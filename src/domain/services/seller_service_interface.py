from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID
from src.domain.models.seller import Seller

class ISellerService(ABC):
    @abstractmethod
    async def create_seller(self, seller: Seller) -> Seller:
        pass

    @abstractmethod
    async def get_seller_by_id(self, seller_id: UUID) -> Optional[Seller]:
        pass

    @abstractmethod
    async def get_all_sellers(self) -> List[Seller]:
        pass

    @abstractmethod
    async def update_seller(self, seller: Seller) -> Seller:
        pass

    @abstractmethod
    async def delete_sellers(self, seller_ids: Union[UUID, List[UUID]]) -> None:
        pass

    @abstractmethod
    async def update_seller(self, seller: Seller) -> Seller:
        """Update seller"""
        pass
