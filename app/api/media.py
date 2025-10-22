from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status

from app.core.rfc7807_handler import problem
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
    record_id = str(uuid4())
    obj = payload.model_dump()
    obj.update(
        {
            "id": record_id,
            "record_id": record_id,
            "owner_id": user["id"],
        }
    )
    MEDIA_DB[record_id] = obj
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
        if kind and m["kind"] != kind:
            continue
        if status and m["status"] != status:
            continue
        results.append(m)
    return results


@router.get("/{record_id}", response_model=MediaOut)
def get_media(record_id: str, user=Depends(get_current_user)):
    m = MEDIA_DB.get(record_id)
    if not m:
        return problem(status=404, title="Not Found", detail="Media not found")
    if m["owner_id"] != user["id"]:
        return problem(
            status=403, title="Forbidden", detail="Cannot access others' media"
        )
    return m


@router.put("/{record_id}", response_model=MediaOut)
def update_media(record_id: str, payload: MediaUpdate, user=Depends(get_current_user)):
    m = MEDIA_DB.get(record_id)
    if not m:
        return problem(status=404, title="Not Found", detail="Media not found")
    if m["owner_id"] != user["id"]:
        return problem(
            status=403, title="Forbidden", detail="Cannot modify others' media"
        )

    update_data = payload.model_dump(exclude_unset=True)

    m.update(update_data)
    MEDIA_DB[record_id] = m
    return m


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(record_id: str, user=Depends(get_current_user)):
    m = MEDIA_DB.get(record_id)
    if not m:
        return problem(status=404, title="Not Found", detail="Media not found")
    if m["owner_id"] != user["id"]:
        return problem(
            status=403, title="Forbidden", detail="Cannot delete others' media"
        )
    del MEDIA_DB[record_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
