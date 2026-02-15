from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.buyer_request import BuyerRequest

class IBuyerRequestService(ABC):
    """Abstraction for BuyerRequest business logic."""

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
    async def update_request(self, request: BuyerRequest) -> BuyerRequest:
        pass

    @abstractmethod
    async def delete_requests(self, request_ids: Union[UUID, List[UUID]]) -> None:
        pass

    @abstractmethod
    async def delete_requests_by_buyer(self, buyer_id: UUID) -> None:
        pass
