from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.config import SessionLocal
from app.schemas.vote import VoteCreate, Vote, ElectionResults
from app.services.vote_service import VoteService
from app.controllers.admin import get_current_admin
from typing import List

router = APIRouter(prefix="/elections")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/vote", response_model=Vote, status_code=status.HTTP_201_CREATED)
def create_vote(
    vote_data: VoteCreate,
    db: Session = Depends(get_db)
):
    """
    Cast a vote for a candidate using an invite code.
    This endpoint is public and can be used by anyone with a valid invite code.
    """
    service = VoteService(db)
    return service.create_vote(vote_data)


@router.get("/{election_id}/results", response_model=ElectionResults)
def get_election_results(
    election_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the voting results for an election.
    This endpoint is public and shows the current results.
    """
    service = VoteService(db)
    return service.get_election_results(election_id)


@router.get("/{election_id}/admin-results", response_model=ElectionResults)
def get_admin_election_results(
    election_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Get the voting results for an election (admin version).
    Only admin users can access this endpoint.
    Functionally identical to the public endpoint, but requires admin authentication.
    """
    service = VoteService(db)
    return service.get_election_results(election_id)
