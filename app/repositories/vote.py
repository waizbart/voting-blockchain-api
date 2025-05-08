from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.vote import Vote
from app.models.election import Election, Candidate, ElectionInvite
from typing import List, Optional, Dict, Any, Tuple


class VoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_vote(self, election_id: int, candidate_id: int, invite_id: int) -> Vote:
        """Create a new vote record."""
        db_vote = Vote(
            election_id=election_id,
            candidate_id=candidate_id,
            invite_id=invite_id
        )
        self.db.add(db_vote)
        self.db.commit()
        self.db.refresh(db_vote)
        return db_vote

    def update_transaction_hash(self, vote_id: int, transaction_hash: str) -> Optional[Vote]:
        """Update the blockchain transaction hash for a vote."""
        db_vote = self.db.query(Vote).filter(Vote.id == vote_id).first()
        if db_vote:
            db_vote.transaction_hash = transaction_hash
            self.db.commit()
            self.db.refresh(db_vote)
        return db_vote

    def get_vote_by_invite_id(self, invite_id: int) -> Optional[Vote]:
        """Get a vote by its invite ID."""
        return self.db.query(Vote).filter(Vote.invite_id == invite_id).first()

    def get_election_vote_count(self, election_id: int) -> int:
        """Get the total number of votes for an election."""
        return self.db.query(Vote).filter(Vote.election_id == election_id).count()

    def get_candidate_vote_count(self, candidate_id: int) -> int:
        """Get the number of votes for a specific candidate."""
        return self.db.query(Vote).filter(Vote.candidate_id == candidate_id).count()

    def get_election_results(self, election_id: int) -> List[Tuple[int, str, int]]:
        """Get the voting results for an election."""
        results = (
            self.db.query(
                Candidate.id,
                Candidate.name,
                func.count(Vote.id).label('vote_count')
            )
            .outerjoin(Vote, Vote.candidate_id == Candidate.id)
            .filter(Candidate.election_id == election_id)
            .group_by(Candidate.id, Candidate.name)
            .all()
        )
        return results
