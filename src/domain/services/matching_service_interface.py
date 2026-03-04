from abc import ABC, abstractmethod
from typing import List
from src.domain.models.match import Match

class IMatchingService(ABC):
    @abstractmethod
    async def find_matches(self) -> List[Match]:
        """Find all new matches between active buyer requests and listings"""
        pass

    @abstractmethod
    async def create_match(self, match: Match) -> Match:
        pass

    @abstractmethod
    async def mark_as_contacted(self, match_id) -> None:
        pass