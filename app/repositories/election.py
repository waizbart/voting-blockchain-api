from sqlalchemy.orm import Session
from app.models.election import Election, Candidate
from app.schemas.election import ElectionCreate, CandidateCreate
from typing import List, Optional, Union, Dict
from datetime import datetime


class ElectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_election(self, election: Union[ElectionCreate, Dict]) -> Election:
        # Handle both dictionary and ElectionCreate object
        if isinstance(election, dict):
            title = election["title"]
            description = election.get("description")
            start_date = election["start_date"]
            end_date = election["end_date"]
            is_active = election.get("is_active", True)
            candidates = election.get("candidates", [])
        else:
            title = election.title
            description = election.description
            start_date = election.start_date
            end_date = election.end_date
            is_active = election.is_active
            candidates = election.candidates

        db_election = Election(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )
        self.db.add(db_election)
        self.db.flush()

        for candidate in candidates:
            if isinstance(candidate, dict):
                name = candidate["name"]
                description = candidate.get("description")
            else:
                name = candidate.name
                description = candidate.description

            db_candidate = Candidate(
                name=name,
                description=description,
                election_id=db_election.id
            )
            self.db.add(db_candidate)

        self.db.commit()
        self.db.refresh(db_election)
        return db_election

    def get_election(self, election_id: int) -> Optional[Election]:
        return self.db.query(Election).filter(Election.id == election_id).first()

    def get_elections(self, skip: int = 0, limit: int = 100) -> List[Election]:
        return self.db.query(Election).offset(skip).limit(limit).all()

    def get_active_elections(self) -> List[Election]:
        current_time = datetime.utcnow()
        return self.db.query(Election).filter(
            Election.is_active == True,
            Election.start_date <= current_time,
            Election.end_date >= current_time
        ).all()

    def update_election(self, election_id: int, election_data: dict) -> Optional[Election]:
        db_election = self.get_election(election_id)
        if db_election:
            for key, value in election_data.items():
                setattr(db_election, key, value)
            self.db.commit()
            self.db.refresh(db_election)
        return db_election

    def delete_election(self, election_id: int) -> bool:
        db_election = self.get_election(election_id)
        if db_election:
            self.db.delete(db_election)
            self.db.commit()
            return True
        return False
