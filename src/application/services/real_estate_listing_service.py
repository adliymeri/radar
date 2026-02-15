from src.infrastructure.utils.logs import app_log
from typing import List, Optional
from uuid import UUID
from src.domain.models.real_estate_listing import RealEstateListing
from src.domain.repositories.real_estate_listing_repository import RealEstateListingRepository
from src.domain.services.real_estate_listing_service_interface import IRealEstateListingService

class RealEstateListingService(IRealEstateListingService):
    def __init__(self, repository: RealEstateListingRepository):
        self.repository = repository

    async def create_listing(self, listing: RealEstateListing) -> RealEstateListing:
        try:
            return await self.repository.create_listing(listing)
        except Exception as e:
            app_log.error(f"Error creating real estate listing: {e}")
            raise

    async def get_listing_by_id(self, listing_id: UUID) -> Optional[RealEstateListing]:
        try:
            return await self.repository.get_listing_by_id(listing_id)
        except Exception as e:
            app_log.error(f"Error fetching real estate listing {listing_id}: {e}")
            raise

    async def get_all_listings(self) -> List[RealEstateListing]:
        try:
            return await self.repository.get_all_listings()
        except Exception as e:
            app_log.error(f"Error fetching all real estate listings: {e}")
            raise

    async def update_listing(self, listing: RealEstateListing) -> RealEstateListing:
        try:
            return await self.repository.update_listing(listing)
        except Exception as e:
            app_log.error(f"Error updating real estate listing {listing.listing_id}: {e}")
            raise

    async def delete_listings(self, listing_ids: List[UUID]) -> None:
        try:
            await self.repository.delete_listings(listing_ids)
        except Exception as e:
            app_log.error(f"Error deleting real estate listings {listing_ids}: {e}")
            raise
