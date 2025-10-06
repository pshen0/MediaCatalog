from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status

from app.schemas.media import KindType, MediaCreate, MediaOut, MediaUpdate, StatusType

router = APIRouter()

MEDIA_DB: Dict[str, dict] = {}


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
    obj = payload.model_dump()
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

    update_data = payload.model_dump(exclude_unset=True)
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
