from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.domain.models.real_estate_listing import RealEstateListing

class IRealEstateListingService(ABC):
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
    async def update_listing(self, listing: RealEstateListing) -> RealEstateListing:
        pass

    @abstractmethod
    async def delete_listings(self, listing_ids: List[UUID]) -> None:
        pass
