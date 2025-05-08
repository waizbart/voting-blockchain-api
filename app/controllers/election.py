from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.controllers.admin import get_current_admin, Admin
from app.schemas.election import Election, ElectionCreate
from app.services.election_service import ElectionService
from app.db.config import SessionLocal

router = APIRouter(prefix="/elections")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Election, status_code=status.HTTP_201_CREATED)
def create_election(
    election: ElectionCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Create a new election with candidates.
    Only admin users can create elections.
    """
    service = ElectionService(db)
    return service.create_election(election)


@router.get("/", response_model=List[Election])
def get_elections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all elections.
    """
    service = ElectionService(db)
    return service.get_elections(skip, limit)


@router.get("/active", response_model=List[Election])
def get_active_elections(
    db: Session = Depends(get_db)
):
    """
    Get all active elections (current time is between start_date and end_date).
    """
    service = ElectionService(db)
    return service.get_active_elections()


@router.get("/{election_id}", response_model=Election)
def get_election(
    election_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific election by ID.
    """
    service = ElectionService(db)
    return service.get_election(election_id)


@router.put("/{election_id}", response_model=Election)
def update_election(
    election_id: int,
    election: ElectionCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Update an election.
    Only admin users can update elections.
    """
    service = ElectionService(db)
    return service.update_election(election_id, election.dict())


@router.delete("/{election_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_election(
    election_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """
    Delete an election.
    Only admin users can delete elections.
    Elections that have already started cannot be deleted.
    """
    service = ElectionService(db)
    service.delete_election(election_id)
    return None
