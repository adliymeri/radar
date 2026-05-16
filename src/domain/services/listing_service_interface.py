from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.models.listing import Listing

class IListingService(ABC):
    @abstractmethod
    async def create_listing(self, listing: Listing) -> Listing:
        pass

    @abstractmethod
    async def get_listing_by_id(self, listing_id: UUID) -> Optional[Listing]:
        pass

    @abstractmethod
    async def get_all_listings(self) -> List[Listing]:
        pass

    @abstractmethod
    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        pass

    @abstractmethod
    async def update_listing(self, listing: Listing) -> Listing:
        pass

    @abstractmethod
    async def delete_listing(self, listing_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_listings_by_seller(self, seller_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        """Get all listings for a seller"""
        pass
    
    @abstractmethod
    async def delete_listing(self, listing_id: UUID) -> None:
        """Delete a listing"""
        pass
