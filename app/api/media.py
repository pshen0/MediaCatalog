from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, field_validator

router = APIRouter()

MEDIA_DB: Dict[str, dict] = {}

KindType = Literal["movie", "course"]
StatusType = Literal["planned", "watching", "completed"]


class MediaBase(BaseModel):
    title: str = Field(..., min_length=1)
    kind: KindType
    year: int
    status: StatusType

    @field_validator("year")
    def year_must_be_reasonable(cls, v: int) -> int:
        current = datetime.now().year
        if v < 1900 or v > current + 1:
            raise ValueError(f"year must be between 1900 and {current + 1}")
        return v


class MediaCreate(MediaBase):
    pass


class MediaUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[KindType] = None
    year: Optional[int] = None
    status: Optional[StatusType] = None

    @field_validator("year")
    def year_must_be_reasonable(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        current = datetime.now().year
        if v < 1900 or v > current + 1:
            raise ValueError(f"year must be between 1900 and {current + 1}")
        return v


class MediaOut(MediaBase):
    id: str
    owner_id: str


def get_current_user(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header required (simulated auth)",
        )
    return {"id": str(x_user_id), "username": f"user_{x_user_id}"}


# --- Endpoints ---


@router.post("/", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
def create_media(payload: MediaCreate, user=Depends(get_current_user)):
    new_id = str(uuid4())
    obj = payload.dict()
    obj.update({"id": new_id, "owner_id": user["id"]})
    MEDIA_DB[new_id] = obj
    return obj


@router.get("/", response_model=List[MediaOut])
def list_media(
    kind: Optional[KindType] = Query(None),
    status: Optional[StatusType] = Query(None),
    user=Depends(get_current_user),
):
    results = []
    for m in MEDIA_DB.values():
        if m["owner_id"] != user["id"]:
            continue
        if kind is not None and m["kind"] != kind:
            continue
        if status is not None and m["status"] != status:
            continue
        results.append(m)
    return results


@router.get("/{media_id}", response_model=MediaOut)
def get_media(media_id: str, user=Depends(get_current_user)):
    m = MEDIA_DB.get(media_id)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media not found"
        )
    if m["owner_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return m


@router.put("/{media_id}", response_model=MediaOut)
def update_media(media_id: str, payload: MediaUpdate, user=Depends(get_current_user)):
    m = MEDIA_DB.get(media_id)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media not found"
        )
    if m["owner_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    update_data = payload.dict(exclude_unset=True)
    if update_data:
        m.update(update_data)
        MEDIA_DB[media_id] = m
    return m


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(media_id: str, user=Depends(get_current_user)):
    m = MEDIA_DB.get(media_id)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media not found"
        )
    if m["owner_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    del MEDIA_DB[media_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
