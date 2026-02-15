from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.car_listing import CarListing

class CarListingRepository(ABC):
    """Abstraction for CarListing data persistence."""

    @abstractmethod
    async def create_car_listing(self, listing: CarListing) -> CarListing:
        pass

    @abstractmethod
    async def get_car_listing_by_id(self, listing_id: UUID) -> Optional[CarListing]:
        pass

    @abstractmethod
    async def get_all_car_listings(self) -> List[CarListing]:
        pass

    @abstractmethod
    async def update_car_listing(self, listing: CarListing) -> CarListing:
        pass

    @abstractmethod
    async def delete_car_listings(self, listing_ids: Union[UUID, List[UUID]]) -> None:
        """Delete one or multiple car listings."""
        pass
