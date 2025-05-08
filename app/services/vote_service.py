from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.vote import VoteRepository
from app.repositories.election_invite import ElectionInviteRepository
from app.repositories.election import ElectionRepository
from app.schemas.vote import VoteCreate, Vote, VoteCount, ElectionResults
from fastapi import HTTPException
from app.services.blockchain_service import BlockchainService


class VoteService:
    def __init__(self, db: Session):
        self.vote_repository = VoteRepository(db)
        self.invite_repository = ElectionInviteRepository(db)
        self.election_repository = ElectionRepository(db)
        self.blockchain_service = BlockchainService()
        self.db = db

    def create_vote(self, vote_data: VoteCreate) -> Vote:
        """Create a new vote using an invite code."""
        # Validate invite
        invite = self.invite_repository.get_invite(vote_data.invite_code)
        if not invite:
            raise HTTPException(
                status_code=404,
                detail="Convite não encontrado"
            )

        # Check if invite is valid (not used and not expired)
        if not self.invite_repository.validate_invite(vote_data.invite_code):
            raise HTTPException(
                status_code=400,
                detail="Convite inválido ou expirado"
            )

        # Check if election exists and is active
        election = self.election_repository.get_election(invite.election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Eleição não encontrada"
            )

        if not election.is_active:
            raise HTTPException(
                status_code=400,
                detail="Esta eleição não está ativa"
            )

        # Check if election is in progress
        current_time = datetime.now(timezone.utc)
        election_start = election.start_date.replace(
            tzinfo=timezone.utc) if election.start_date.tzinfo is None else election.start_date
        election_end = election.end_date.replace(
            tzinfo=timezone.utc) if election.end_date.tzinfo is None else election.end_date

        if current_time < election_start:
            raise HTTPException(
                status_code=400,
                detail="Esta eleição ainda não começou"
            )

        if current_time > election_end:
            raise HTTPException(
                status_code=400,
                detail="Esta eleição já terminou"
            )

        # Check if candidate exists and belongs to the election
        candidate = next(
            (c for c in election.candidates if c.id == vote_data.candidate_id),
            None
        )
        if not candidate:
            raise HTTPException(
                status_code=404,
                detail="Candidato não encontrado nesta eleição"
            )

        # Check if invite has already been used for voting
        existing_vote = self.vote_repository.get_vote_by_invite_id(invite.id)
        if existing_vote:
            raise HTTPException(
                status_code=400,
                detail="Este convite já foi usado para votar"
            )

        # Mark invite as used
        used_invite = self.invite_repository.use_invite(vote_data.invite_code)
        if not used_invite:
            raise HTTPException(
                status_code=400,
                detail="Erro ao processar o convite"
            )

        # Create vote
        vote = self.vote_repository.create_vote(
            election_id=election.id,
            candidate_id=vote_data.candidate_id,
            invite_id=invite.id
        )

        # Register vote on blockchain
        try:
            candidate_id_str = str(vote_data.candidate_id)
            # Since we only record one vote at a time, set votes=1
            tx_hash = self.blockchain_service.register_votes(
                candidate_id_str, 1)
            # Store transaction hash if needed
            # vote.blockchain_tx = tx_hash
            # self.vote_repository.update_vote(vote)
        except Exception as e:
            # Log the error but don't fail the operation
            print(f"Error registering vote on blockchain: {e}")
            # Could implement a retry mechanism or queue for failed blockchain operations

        return vote

    def get_election_results(self, election_id: int) -> ElectionResults:
        """Get the voting results for an election."""
        # Check if election exists
        election = self.election_repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Eleição não encontrada"
            )

        # Get results from database
        db_results = self.vote_repository.get_election_results(election_id)

        # Format results
        candidate_results = [
            VoteCount(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                vote_count=vote_count
            )
            for candidate_id, candidate_name, vote_count in db_results
        ]

        # Attempt to get blockchain results for verification
        blockchain_results = {}
        try:
            all_candidates = self.blockchain_service.get_all_candidates()
            for _, candidate_id, votes in all_candidates:
                blockchain_results[candidate_id] = votes

            # You could compare blockchain_results with database results
            # and handle any discrepancies here
        except Exception as e:
            # Log the error but don't fail the operation
            print(f"Error fetching blockchain results: {e}")

        # Calculate total votes
        total_votes = sum(result.vote_count for result in candidate_results)

        return ElectionResults(
            election_id=election.id,
            election_title=election.title,
            total_votes=total_votes,
            candidate_results=candidate_results
        )

    def sync_results_with_blockchain(self, election_id: int) -> None:
        """
        Sync election results with blockchain.
        This could be run as a scheduled job or manually triggered.
        """
        # Check if election exists
        election = self.election_repository.get_election(election_id)
        if not election:
            raise HTTPException(
                status_code=404,
                detail="Eleição não encontrada"
            )

        # Get results from database
        db_results = self.vote_repository.get_election_results(election_id)

        # Register totals on blockchain
        for candidate_id, _, vote_count in db_results:
            try:
                candidate_id_str = str(candidate_id)
                self.blockchain_service.register_votes(
                    candidate_id_str, vote_count)
            except Exception as e:
                print(
                    f"Error syncing candidate {candidate_id} to blockchain: {e}")
                # Continue with other candidates even if one fails
