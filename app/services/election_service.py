from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.election import ElectionRepository
from app.schemas.election import ElectionCreate, Election
from fastapi import HTTPException


class ElectionService:
    def __init__(self, db: Session):
        self.repository = ElectionRepository(db)

    def create_election(self, election: ElectionCreate) -> Election:
        # Convert dates to UTC timezone-aware
        current_time = datetime.now(timezone.utc)
        start_date = election.start_date.replace(tzinfo=timezone.utc)
        end_date = election.end_date.replace(tzinfo=timezone.utc)

        # Validate dates
        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )

        if start_date < current_time:
            raise HTTPException(
                status_code=400,
                detail="Start date must be in the future"
            )

        # Validate candidates
        if not election.candidates:
            raise HTTPException(
                status_code=400,
                detail="At least one candidate is required"
            )

        if len(election.candidates) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two candidates are required"
            )

        # Update election dates with timezone-aware datetimes
        election_dict = election.dict()
        election_dict["start_date"] = start_date
        election_dict["end_date"] = end_date

        return self.repository.create_election(election_dict)

    def get_election(self, election_id: int) -> Optional[Election]:
        election = self.repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )
        return election

    def get_elections(self, skip: int = 0, limit: int = 100) -> List[Election]:
        return self.repository.get_elections(skip, limit)

    def get_active_elections(self) -> List[Election]:
        return self.repository.get_active_elections()

    def update_election(self, election_id: int, election_data: dict) -> Election:
        election = self.repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )

        # Validate dates if they are being updated
        if "start_date" in election_data and "end_date" in election_data:
            start_date = election_data["start_date"].replace(
                tzinfo=timezone.utc)
            end_date = election_data["end_date"].replace(tzinfo=timezone.utc)

            if start_date >= end_date:
                raise HTTPException(
                    status_code=400,
                    detail="End date must be after start date"
                )

            election_data["start_date"] = start_date
            election_data["end_date"] = end_date

        updated_election = self.repository.update_election(
            election_id, election_data)
        if not updated_election:
            raise HTTPException(
                status_code=400,
                detail="Failed to update election"
            )
        return updated_election

    def delete_election(self, election_id: int) -> bool:
        election = self.repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )

        current_time = datetime.now(timezone.utc)
        if election.start_date.replace(tzinfo=timezone.utc) <= current_time:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete an election that has already started"
            )

        return self.repository.delete_election(election_id)
