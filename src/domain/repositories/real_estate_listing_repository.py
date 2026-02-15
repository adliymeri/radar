from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID
from src.domain.models.real_estate_listing import RealEstateListing

class RealEstateListingRepository(ABC):
    @abstractmethod
    async def create_listing(self, listing: RealEstateListing) -> RealEstateListing:
        pass

    @abstractmethod
    async def get_listing_by_id(self, listing_id: UUID) -> Optional[RealEstateListing]:
        pass

    @abstractmethod
    async def get_all_listings(self) -> List[RealEstateListing]:
        pass

    @abstractmethod
    async def get_listings_by_seller(self, seller_id: UUID) -> List[RealEstateListing]:
        pass

    @abstractmethod
    async def update_listing(self, listing: RealEstateListing) -> RealEstateListing:
        pass

    @abstractmethod
    async def delete_listing(self, listing_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_listings(self, listing_ids: Union[UUID, List[UUID]]) -> None:
        """Delete single or multiple listings."""
        pass
