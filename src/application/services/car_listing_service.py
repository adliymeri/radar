from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.car_listing import CarListing
from src.domain.repositories.car_listing_repository import CarListingRepository
from src.domain.services.car_listing_service_interface import ICarListingService
from src.infrastructure.utils.logs import app_log  

class CarListingService(ICarListingService):
    def __init__(self, repository: CarListingRepository):
        self.repository = repository

    async def create_car_listing(self, listing: CarListing) -> CarListing:
        try:
            return await self.repository.create_car_listing(listing)
        except Exception as e:
            app_log.error(f"Error creating car listing: {e}")
            raise

    async def get_car_listing_by_id(self, listing_id: UUID) -> Optional[CarListing]:
        try:
            return await self.repository.get_car_listing_by_id(listing_id)
        except Exception as e:
            app_log.error(f"Error fetching car listing {listing_id}: {e}")
            raise

    async def get_all_car_listings(self) -> List[CarListing]:
        try:
            return await self.repository.get_all_car_listings()
        except Exception as e:
            app_log.error(f"Error fetching all car listings: {e}")
            raise

    async def update_car_listing(self, listing: CarListing) -> CarListing:
        try:
            return await self.repository.update_car_listing(listing)
        except Exception as e:
            app_log.error(f"Error updating car listing {listing.listing_id}: {e}")
            raise

    async def delete_car_listings(self, listing_ids: Union[UUID, List[UUID]]) -> None:
        try:
            await self.repository.delete_car_listings(listing_ids)
        except Exception as e:
            app_log.error(f"Error deleting car listing(s) {listing_ids}: {e}")
            raise
