from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.models.election import InviteStatus


class CandidateBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CandidateCreate(CandidateBase):
    pass


class Candidate(CandidateBase):
    id: int
    election_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ElectionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: datetime
    end_date: datetime
    is_active: bool = True

    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ElectionCreate(ElectionBase):
    candidates: List[CandidateCreate]


class Election(ElectionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    candidates: List[Candidate]

    class Config:
        from_attributes = True


class ElectionInviteBase(BaseModel):
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ElectionInviteCreate(ElectionInviteBase):
    pass


class ElectionInvite(ElectionInviteBase):
    id: int
    election_id: int
    code: str
    status: InviteStatus
    used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ElectionInviteBulkCreate(BaseModel):
    quantity: int = Field(..., gt=0, le=100)
    expires_at: Optional[datetime] = None

    @validator('expires_at')
    def validate_expires_at(cls, v):
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
