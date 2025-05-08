from abc import ABC, abstractmethod
from typing import Tuple, Any, List


class BlockchainProvider(ABC):
    """
    Abstract base class for blockchain providers.
    Defines the strategy interface for interacting with different blockchains.
    """

    @abstractmethod
    def register_votes(self, candidate_id: str, votes: int) -> str:
        """
        Register votes for a candidate on the blockchain.

        Args:
            candidate_id: The ID of the candidate.
            votes: The number of votes to register.

        Returns:
            The transaction hash.
        """
        pass

    @abstractmethod
    def get_total_candidates(self) -> int:
        """
        Get the total number of candidates on the blockchain.

        Returns:
            The total number of candidates.
        """
        pass

    @abstractmethod
    def get_candidate(self, candidate_index: int) -> Tuple[str, int]:
        """
        Get a candidate from the blockchain by index.

        Args:
            candidate_index: The index of the candidate to get.

        Returns:
            A tuple of (candidate_id, votes).
        """
        pass

    @abstractmethod
    def get_all_candidates(self) -> List[Tuple[int, str, int]]:
        """
        Get all candidates from the blockchain.

        Args:
            None

        Returns:
            A list of tuples (index, candidate_id, votes).
        """
        pass
