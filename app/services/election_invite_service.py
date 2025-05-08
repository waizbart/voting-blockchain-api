from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from app.repositories.election_invite import ElectionInviteRepository
from app.repositories.election import ElectionRepository
from app.schemas.election import ElectionInviteCreate, ElectionInviteBulkCreate, ElectionInvite
from fastapi import HTTPException


class ElectionInviteService:
    def __init__(self, db: Session):
        self.repository = ElectionInviteRepository(db)
        self.election_repository = ElectionRepository(db)

    def create_invite(self, election_id: int, invite_data: ElectionInviteCreate) -> ElectionInvite:
        """Create a single invite for an election."""
        # Verify if election exists and is active
        election = self.election_repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )

        if not election.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot create invites for inactive election"
            )

        # Convert dates to UTC timezone-aware
        current_time = datetime.now(timezone.utc)
        expires_at = invite_data.expires_at.replace(
            tzinfo=timezone.utc) if invite_data.expires_at.tzinfo is None else invite_data.expires_at
        election_end_date = election.end_date.replace(
            tzinfo=timezone.utc) if election.end_date.tzinfo is None else election.end_date

        # Validate expiration date
        if expires_at <= current_time:
            raise HTTPException(
                status_code=400,
                detail="Expiration date must be in the future"
            )

        if expires_at > election_end_date:
            raise HTTPException(
                status_code=400,
                detail="Expiration date cannot be after election end date"
            )

        # Update invite data with timezone-aware datetime
        invite_dict = invite_data.dict()
        invite_dict["expires_at"] = expires_at

        return self.repository.create_invite(election_id, invite_dict)

    def create_bulk_invites(self, election_id: int, bulk_data: ElectionInviteBulkCreate) -> List[ElectionInvite]:
        """Create multiple invites for an election."""
        # Verify if election exists and is active
        election = self.election_repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )

        if not election.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot create invites for inactive election"
            )

        # Convert dates to UTC timezone-aware
        current_time = datetime.now(timezone.utc)
        election_end_date = election.end_date.replace(
            tzinfo=timezone.utc) if election.end_date.tzinfo is None else election.end_date

        # Validate expiration date if provided
        if bulk_data.expires_at:
            expires_at = bulk_data.expires_at.replace(
                tzinfo=timezone.utc) if bulk_data.expires_at.tzinfo is None else bulk_data.expires_at

            if expires_at <= current_time:
                raise HTTPException(
                    status_code=400,
                    detail="Expiration date must be in the future"
                )

            if expires_at > election_end_date:
                raise HTTPException(
                    status_code=400,
                    detail="Expiration date cannot be after election end date"
                )

            # Update bulk data with timezone-aware datetime
            bulk_dict = bulk_data.dict()
            bulk_dict["expires_at"] = expires_at
            return self.repository.create_bulk_invites(election_id, bulk_dict)

        return self.repository.create_bulk_invites(election_id, bulk_data)

    def get_election_invites(self, election_id: int) -> List[ElectionInvite]:
        """Get all invites for an election."""
        # Verify if election exists
        election = self.election_repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Election not found"
            )

        return self.repository.get_election_invites(election_id)

    def validate_invite(self, code: str) -> bool:
        """Validate if an invite is valid for use."""
        invite = self.repository.get_invite(code)
        if not invite:
            raise HTTPException(
                status_code=404,
                detail="Invite not found"
            )

        # Check if election is active
        election = self.election_repository.get_election(invite.election_id)
        if not election or not election.is_active:
            raise HTTPException(
                status_code=400,
                detail="Election is not active"
            )

        # Convert dates to UTC timezone-aware
        current_time = datetime.now(timezone.utc)
        election_start_date = election.start_date.replace(
            tzinfo=timezone.utc) if election.start_date.tzinfo is None else election.start_date
        election_end_date = election.end_date.replace(
            tzinfo=timezone.utc) if election.end_date.tzinfo is None else election.end_date

        # Check if election is in progress
        if current_time < election_start_date:
            raise HTTPException(
                status_code=400,
                detail="Election has not started yet"
            )

        if current_time > election_end_date:
            raise HTTPException(
                status_code=400,
                detail="Election has ended"
            )

        return self.repository.validate_invite(code)

    def use_invite(self, code: str) -> ElectionInvite:
        """Mark an invite as used."""
        if not self.validate_invite(code):
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired invite"
            )

        invite = self.repository.use_invite(code)
        if not invite:
            raise HTTPException(
                status_code=400,
                detail="Failed to use invite"
            )

        return invite
