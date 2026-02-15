from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.seller import Seller

class SellerRepository(ABC):
    """Abstraction for Seller data persistence."""

    @abstractmethod
    async def create_seller(self, seller: Seller) -> Seller:
        """Insert a new seller into the database."""
        pass

    @abstractmethod
    async def get_seller_by_id(self, seller_id: UUID) -> Optional[Seller]:
        """Retrieve a seller by their ID."""
        pass

    @abstractmethod
    async def get_all_sellers(self) -> List[Seller]:
        """Get all sellers."""
        pass

    @abstractmethod
    async def update_seller(self, seller: Seller) -> Seller:
        """Update an existing seller."""
        pass

    @abstractmethod
    async def delete_sellers(self, seller_ids: Union[UUID, List[UUID]]) -> None:
        pass

