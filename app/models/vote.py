from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.config import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    invite_id = Column(Integer, ForeignKey(
        "election_invites.id"), nullable=False)

    # Campo que armazenará o hash da transação na blockchain
    transaction_hash = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    election = relationship("Election", foreign_keys=[election_id])
    candidate = relationship("Candidate", foreign_keys=[candidate_id])
    invite = relationship("ElectionInvite", foreign_keys=[invite_id])
