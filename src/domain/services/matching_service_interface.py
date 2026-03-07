from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from src.domain.models.match import Match

class IMatchingService(ABC):
    @abstractmethod
    async def find_matches(self, last_run: Optional[datetime] = None) -> List[Match]:
        """Find all new matches between active buyer requests and listings"""
        pass

    @abstractmethod
    async def create_match(self, match: Match) -> Match:
        pass

    @abstractmethod
    async def get_match_by_id(self, match_id: UUID) -> Optional[Match]:
        pass

    @abstractmethod
    async def mark_as_contacted(self, match_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_matches_by_request(self, request_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Match]:
        pass

    @abstractmethod
    async def count_matches_by_request(self, request_id: UUID) -> int:
        pass