from sqlalchemy.orm import Session
from app.models.election import ElectionInvite, InviteStatus
from app.schemas.election import ElectionInviteCreate, ElectionInviteBulkCreate
from typing import List, Optional, Union, Dict
from datetime import datetime, timezone, timedelta
import secrets
import string


class ElectionInviteRepository:
    def __init__(self, db: Session):
        self.db = db

    def _generate_invite_code(self) -> str:
        """Generate a unique invite code."""
        alphabet = string.ascii_letters + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            # Check if code already exists
            if not self.db.query(ElectionInvite).filter(ElectionInvite.code == code).first():
                return code

    def create_invite(self, election_id: int, invite_data: Union[ElectionInviteCreate, Dict]) -> ElectionInvite:
        """Create a single invite for an election."""
        # Handle both dictionary and ElectionInviteCreate object
        if isinstance(invite_data, dict):
            expires_at = invite_data["expires_at"]
        else:
            expires_at = invite_data.expires_at

        db_invite = ElectionInvite(
            election_id=election_id,
            code=self._generate_invite_code(),
            expires_at=expires_at,
            status=InviteStatus.PENDING
        )
        self.db.add(db_invite)
        self.db.commit()
        self.db.refresh(db_invite)
        return db_invite

    def create_bulk_invites(self, election_id: int, bulk_data: Union[ElectionInviteBulkCreate, Dict]) -> List[ElectionInvite]:
        """Create multiple invites for an election."""
        # Handle both dictionary and ElectionInviteBulkCreate object
        if isinstance(bulk_data, dict):
            quantity = bulk_data["quantity"]
            expires_at = bulk_data.get("expires_at")
        else:
            quantity = bulk_data.quantity
            expires_at = bulk_data.expires_at

        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        invites = []
        for _ in range(quantity):
            db_invite = ElectionInvite(
                election_id=election_id,
                code=self._generate_invite_code(),
                expires_at=expires_at,
                status=InviteStatus.PENDING
            )
            self.db.add(db_invite)
            invites.append(db_invite)

        self.db.commit()
        for invite in invites:
            self.db.refresh(invite)
        return invites

    def get_invite(self, code: str) -> Optional[ElectionInvite]:
        """Get an invite by its code."""
        return self.db.query(ElectionInvite).filter(ElectionInvite.code == code).first()

    def get_election_invites(self, election_id: int) -> List[ElectionInvite]:
        """Get all invites for an election."""
        return self.db.query(ElectionInvite).filter(ElectionInvite.election_id == election_id).all()

    def use_invite(self, code: str) -> Optional[ElectionInvite]:
        """Mark an invite as used."""
        invite = self.get_invite(code)
        if invite and invite.status == InviteStatus.PENDING:
            invite.status = InviteStatus.USED
            invite.used_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(invite)
        return invite

    def expire_invite(self, code: str) -> Optional[ElectionInvite]:
        """Mark an invite as expired."""
        invite = self.get_invite(code)
        if invite and invite.status == InviteStatus.PENDING:
            invite.status = InviteStatus.EXPIRED
            self.db.commit()
            self.db.refresh(invite)
        return invite

    def validate_invite(self, code: str) -> bool:
        """Validate if an invite is valid for use."""
        invite = self.get_invite(code)
        if not invite:
            return False

        current_time = datetime.now(timezone.utc)

        # Ensure expires_at has timezone info
        expires_at = invite.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return (
            invite.status == InviteStatus.PENDING and
            expires_at > current_time
        )
