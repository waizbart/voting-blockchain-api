import hashlib
from typing import Dict, Any, List, Tuple

from app.factories.blockchain_factory import BlockchainFactory
from app.strategies.blockchain_provider import BlockchainProvider


class BlockchainService:
    """
    Service for interacting with the blockchain.
    Uses the Strategy Pattern through BlockchainProvider implementations.
    """

    def __init__(self, provider_name: str = "polygon"):
        """
        Initialize the blockchain service with a provider.

        Args:
            provider_name: The name of the blockchain provider to use.
        """
        # Use the factory to get the appropriate provider
        self.provider: BlockchainProvider = BlockchainFactory.get_provider(
            provider_name)

    def register_votes(self, candidate_id: str, votes: int) -> str:
        """
        Register votes for a candidate on the blockchain.
        Returns the transaction hash.
        """
        return self.provider.register_votes(candidate_id, votes)

    def get_total_candidates(self) -> int:
        """
        Get the total number of candidates on the blockchain.
        """
        return self.provider.get_total_candidates()

    def get_candidate(self, candidate_index: int) -> Tuple[str, int]:
        """
        Get a candidate from the blockchain by index.
        Returns a tuple of (candidate_id, votes).
        """
        return self.provider.get_candidate(candidate_index)

    def get_all_candidates(self) -> List[Tuple[int, str, int]]:
        """
        Get all candidates from the blockchain.
        Returns a list of tuples (index, candidate_id, votes).
        """
        return self.provider.get_all_candidates()
