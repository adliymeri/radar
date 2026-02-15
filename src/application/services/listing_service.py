from typing import Optional, List
from uuid import UUID
from src.domain.models.listing import Listing
from src.domain.repositories.listing_repository import ListingRepository
from src.domain.services.listing_service_interface import IListingService
from src.infrastructure.utils.logs import app_log

class ListingService(IListingService):
    def __init__(self, repository: ListingRepository):
        self.repository = repository

    async def create_listing(self, listing: Listing) -> Listing:
        try:
            return await self.repository.create_listing(listing)
        except Exception as e:
            app_log.error(f"Error creating listing: {e}")
            raise

    async def get_listing_by_id(self, listing_id: UUID) -> Optional[Listing]:
        try:
            return await self.repository.get_listing_by_id(listing_id)
        except Exception as e:
            app_log.error(f"Error fetching listing by id {listing_id}: {e}")
            raise

    async def get_all_listings(self) -> List[Listing]:
        try:
            return await self.repository.get_all_listings()
        except Exception as e:
            app_log.error(f"Error fetching all listings: {e}")
            raise

    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        try:
            return await self.repository.get_listings_by_seller(seller_id)
        except Exception as e:
            app_log.error(f"Error fetching listings for seller {seller_id}: {e}")
            raise

    async def update_listing(self, listing: Listing) -> Listing:
        try:
            return await self.repository.update_listing(listing)
        except Exception as e:
            app_log.error(f"Error updating listing {listing.id}: {e}")
            raise

    async def delete_listing(self, listing_id: UUID) -> None:
        try:
            await self.repository.delete_listing(listing_id)
        except Exception as e:
            app_log.error(f"Error deleting listing {listing_id}: {e}")
            raise

    async def delete_listings_by_seller(self, seller_id: UUID) -> None:
        try:
            await self.repository.delete_listings_by_seller(seller_id)
        except Exception as e:
            app_log.error(f"Error deleting listings for seller {seller_id}: {e}")
            raise
