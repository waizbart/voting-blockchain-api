from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.election import ElectionInvite, ElectionInviteCreate, ElectionInviteBulkCreate
from app.services.election_invite_service import ElectionInviteService
from app.controllers.admin import get_current_admin
from app.db.config import SessionLocal

router = APIRouter(prefix="/elections")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/{election_id}/invites", response_model=ElectionInvite, status_code=status.HTTP_201_CREATED)
def create_invite(
    election_id: int,
    invite: ElectionInviteCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Create a single invite for an election.
    Only admin users can create invites.
    """
    service = ElectionInviteService(db)
    return service.create_invite(election_id, invite)


@router.post("/{election_id}/invites/bulk", response_model=List[ElectionInvite], status_code=status.HTTP_201_CREATED)
def create_bulk_invites(
    election_id: int,
    bulk_data: ElectionInviteBulkCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Create multiple invites for an election.
    Only admin users can create invites.
    """
    service = ElectionInviteService(db)
    return service.create_bulk_invites(election_id, bulk_data)


@router.get("/{election_id}/invites", response_model=List[ElectionInvite])
def get_election_invites(
    election_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Get all invites for an election.
    Only admin users can view invites.
    """
    service = ElectionInviteService(db)
    return service.get_election_invites(election_id)


@router.post("/invites/{code}/validate", status_code=status.HTTP_200_OK)
def validate_invite(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Validate if an invite is valid for use.
    This endpoint is public and can be used to check if an invite is valid before voting.
    """
    service = ElectionInviteService(db)
    is_valid = service.validate_invite(code)
    return {"valid": is_valid}


@router.post("/invites/{code}/use", response_model=ElectionInvite)
def use_invite(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Mark an invite as used.
    This endpoint should be called when a user votes using the invite.
    """
    service = ElectionInviteService(db)
    return service.use_invite(code)
