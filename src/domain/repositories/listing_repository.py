from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.models.listing import Listing

class ListingRepository(ABC):
    """Abstraction for Listing data persistence."""

    @abstractmethod
    async def create_listing(self, listing: Listing) -> Listing:
        """Create a new listing."""
        pass

    @abstractmethod
    async def get_listing_by_id(self, listing_id: UUID) -> Optional[Listing]:
        pass

    @abstractmethod
    async def get_all_listings(self) -> List[Listing]:
        pass

    @abstractmethod
    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        """Fetch all listings for a given seller."""
        pass

    @abstractmethod
    async def update_listing(self, listing: Listing) -> Listing:
        pass

    @abstractmethod
    async def delete_listing(self, listing_id: UUID) -> None:
        """Delete a listing by ID."""
        pass

    @abstractmethod
    async def delete_listings_by_seller(self, seller_id: UUID) -> None:
        """Delete all listings for a specific seller."""
        pass
