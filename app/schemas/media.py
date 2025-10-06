from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

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
