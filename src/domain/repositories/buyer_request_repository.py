from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.buyer_request import BuyerRequest

class BuyerRequestRepository(ABC):
    """Abstraction for BuyerRequest data persistence."""

    @abstractmethod
    async def create_request(self, request: BuyerRequest) -> BuyerRequest:
        pass

    @abstractmethod
    async def get_request_by_id(self, request_id: UUID) -> Optional[BuyerRequest]:
        pass

    @abstractmethod
    async def get_all_requests(self) -> List[BuyerRequest]:
        pass

    @abstractmethod
    async def get_requests_by_buyer(self, buyer_id: UUID) -> List[BuyerRequest]:
        """Fetch all requests for a specific buyer."""
        pass

    @abstractmethod
    async def update_request(self, request: BuyerRequest) -> BuyerRequest:
        pass

    @abstractmethod
    async def delete_requests(self, request_ids: Union[UUID, List[UUID]]) -> None:
        pass

    @abstractmethod
    async def delete_requests_by_buyer(self, buyer_id: UUID) -> None:
        """Delete all buyer requests for a given buyer."""
        pass

