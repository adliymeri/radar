from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.buyer import Buyer

class BuyerRepository(ABC):
    """Abstraction for Buyer data persistence."""

    @abstractmethod
    async def create_buyer(self, buyer: Buyer) -> Buyer:
        pass

    @abstractmethod
    async def get_buyer_by_id(self, buyer_id: UUID) -> Optional[Buyer]:
        pass

    @abstractmethod
    async def get_buyer_by_chat_id(self, chat_id: str) -> Optional[Buyer]:
        pass

    @abstractmethod
    async def get_all_buyers(self) -> List[Buyer]:
        pass

    @abstractmethod
    async def update_buyer(self, buyer: Buyer) -> Buyer:
        pass

    @abstractmethod
    async def delete_buyers(self, buyer_ids: Union[UUID, List[UUID]]) -> None:
        pass
