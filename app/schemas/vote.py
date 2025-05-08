from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class VoteBase(BaseModel):
    candidate_id: int = Field(..., description="ID do candidato escolhido")
    invite_code: str = Field(...,
                             description="Código do convite usado para votar")


class VoteCreate(VoteBase):
    pass


class Vote(BaseModel):
    id: int
    election_id: int
    candidate_id: int
    invite_id: int
    transaction_hash: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VoteCount(BaseModel):
    candidate_id: int
    candidate_name: str
    vote_count: int


class ElectionResults(BaseModel):
    election_id: int
    election_title: str
    total_votes: int
    candidate_results: list[VoteCount]
