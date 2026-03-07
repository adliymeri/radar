from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.models.match import Match

class MatchRepository(ABC):
    @abstractmethod
    async def create_match(self, match: Match) -> Match:
        pass

    @abstractmethod
    async def get_match_by_id(self, match_id: UUID) -> Optional[Match]:
        pass

    @abstractmethod
    async def get_matches_by_buyer(self, buyer_id: UUID) -> List[Match]:
        pass

    @abstractmethod
    async def get_matches_by_seller(self, seller_id: UUID) -> List[Match]:
        pass

    @abstractmethod
    async def match_exists(self, listing_id: UUID, request_id: UUID) -> bool:
        pass

    @abstractmethod
    async def update_match(self, match: Match) -> Match:
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