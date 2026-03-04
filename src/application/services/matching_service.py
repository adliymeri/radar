from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.match import Match
from src.domain.services.matching_service_interface import IMatchingService
from src.domain.repositories.match_repository import MatchRepository
from src.infrastructure.db.orm_models.buyer_request_orm import BuyerRequestORM
from src.infrastructure.db.orm_models.car_listing_orm import CarListingORM
from src.infrastructure.db.orm_models.listing_orm import ListingORM
from src.infrastructure.utils.logs import app_log


class MatchingService(IMatchingService):
    def __init__(self, session: AsyncSession, match_repository: MatchRepository):
        self.session = session
        self.match_repository = match_repository

    async def find_matches(self, last_run: Optional[datetime] = None) -> List[Match]:
        """
        Find matches using incremental approach - only check new/updated listings.
        
        Args:
            last_run: Timestamp of last matching cycle. If None, matches all listings.
        """
        matches = []

        # Fetch all active car requests
        result = await self.session.execute(
            select(BuyerRequestORM).where(
                and_(
                    BuyerRequestORM.type == "car",
                    BuyerRequestORM.status == "active"
                )
            )
        )
        requests = result.scalars().all()

        if not requests:
            app_log.info("No active buyer requests found")
            return matches

        # Build incremental filter
        listing_filter = [ListingORM.type == "car"]
        
        if last_run:
            listing_filter.append(
                or_(
                    ListingORM.created_at > last_run,
                    ListingORM.updated_at > last_run,
                    ListingORM.last_matched_at.is_(None)
                )
            )

        # Fetch car listings with incremental filter
        result = await self.session.execute(
            select(CarListingORM, ListingORM).join(
                ListingORM, CarListingORM.listing_id == ListingORM.id
            ).where(and_(*listing_filter))
        )
        listings_data = result.all()

        if not listings_data:
            app_log.info("No new/updated car listings found")
            return matches

        app_log.info(
            f"Incremental matching: {len(requests)} requests against "
            f"{len(listings_data)} new/updated listings"
        )

        # Match each request against filtered listings
        for request_orm in requests:
            matched_count = 0
            
            for car_listing_orm, listing_orm in listings_data:
                if await self.match_repository.match_exists(listing_orm.id, request_orm.id):
                    continue

                if self._quick_filter(request_orm.details, car_listing_orm):
                    if self._detailed_match(request_orm.details, car_listing_orm):
                        match = Match(
                            buyer_id=request_orm.buyer_id,
                            seller_id=listing_orm.seller_id,
                            listing_id=listing_orm.id,
                            request_id=request_orm.id,
                            status="notified",
                        )
                        matches.append(match)
                        matched_count += 1

                        if listing_orm.id not in request_orm.matched_listing_ids:
                            request_orm.matched_listing_ids.append(listing_orm.id)

            if matched_count > 0:
                app_log.info(f"Request {request_orm.id}: {matched_count} new matches")

        # Update last_matched_at for all checked listings
        for _, listing_orm in listings_data:
            listing_orm.last_matched_at = datetime.now(timezone.utc)
        
        await self.session.commit()

        app_log.info(f"Total new matches found: {len(matches)}")
        return matches

    def _quick_filter(self, request_details: dict, listing: CarListingORM) -> bool:
        """Fast pre-filter using database-indexed fields."""
        # Make/Model
        if request_details.get("make") and request_details["make"] != listing.make:
            return False
        if request_details.get("model") and request_details["model"] != listing.model:
            return False

        # Year
        year_min = request_details.get("year_min")
        year_max = request_details.get("year_max")
        if year_min and listing.year and listing.year < year_min:
            return False
        if year_max and listing.year and listing.year > year_max:
            return False

        # Price
        price_min = request_details.get("price_min")
        price_max = request_details.get("price_max")
        if price_min and listing.price and listing.price > price_max:
            return False

        # Mileage
        mileage_max = request_details.get("mileage")
        if mileage_max and listing.mileage and listing.mileage > mileage_max:
            return False

        return True

    def _detailed_match(self, request_details: dict, listing: CarListingORM) -> bool:
        """Detailed matching for non-indexed fields."""
        # Transmission
        transmission_options = request_details.get("transmission", [])
        if transmission_options and listing.transmission not in transmission_options:
            return False

        # Fuel
        fuel_options = request_details.get("fuel", [])
        if fuel_options and listing.fuel_type not in fuel_options:
            return False

        # Drivetrain
        drivetrain_options = request_details.get("drivetrain", [])
        if drivetrain_options and listing.drivetrain not in drivetrain_options:
            return False

        return True

    # ================= CRUD METHODS =================

    async def create_match(self, match: Match) -> Match:
        try:
            return await self.match_repository.create_match(match)
        except Exception as e:
            app_log.error(f"Error creating match: {e}")
            raise

    async def get_match_by_id(self, match_id: UUID) -> Optional[Match]:
        try:
            return await self.match_repository.get_match_by_id(match_id)
        except Exception as e:
            app_log.error(f"Error fetching match {match_id}: {e}")
            raise

    async def mark_as_contacted(self, match_id: UUID) -> None:
        try:
            await self.match_repository.mark_as_contacted(match_id)
        except Exception as e:
            app_log.error(f"Error marking match {match_id} as contacted: {e}")
            raise