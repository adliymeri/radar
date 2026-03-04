from typing import List
from uuid import UUID
from sqlalchemy import select, and_
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

    async def find_matches(self) -> List[Match]:
        """
        Find all new matches between active buyer requests and car listings.
        This is the core matching algorithm.
        """
        matches = []

        # Fetch all active car requests
        result = await self.session.execute(
            select(BuyerRequestORM).where(
                and_(
                    BuyerRequestORM.type == "car",
                    BuyerRequestORM.status == "pending"
                )
            )
        )
        requests = result.scalars().all()

        if not requests:
            app_log.info("No active buyer requests found")
            return matches

        # Fetch all car listings with their base listing data
        result = await self.session.execute(
            select(CarListingORM, ListingORM).join(
                ListingORM, CarListingORM.listing_id == ListingORM.id
            )
        )
        listings_data = result.all()

        if not listings_data:
            app_log.info("No car listings found")
            return matches

        app_log.info(f"Checking {len(requests)} requests against {len(listings_data)} listings")

        # Match each request against each listing
        for request_orm in requests:
            for car_listing_orm, listing_orm in listings_data:
                # Skip if already matched
                if await self.match_repository.match_exists(listing_orm.id, request_orm.id):
                    continue

                # Perform matching logic
                if self._is_match(request_orm.details, car_listing_orm):
                    match = Match(
                        buyer_id=request_orm.buyer_id,
                        seller_id=listing_orm.seller_id,
                        listing_id=listing_orm.id,
                        request_id=request_orm.id,
                        status="notified",
                    )
                    matches.append(match)
                    app_log.info(
                        f"Match found: Request {request_orm.id} <-> Listing {listing_orm.id}"
                    )

        app_log.info(f"Total matches found: {len(matches)}")
        return matches

    def _is_match(self, request_details: dict, listing: CarListingORM) -> bool:
        """
        Core matching logic - checks if listing satisfies request criteria.
        Designed to be field-agnostic - add new fields to enums and they work automatically.
        """
        # Make/Model - exact match required
        if request_details.get("make") and request_details["make"] != listing.make:
            return False
        if request_details.get("model") and request_details["model"] != listing.model:
            return False

        # Year - range check
        year_min = request_details.get("year_min")
        year_max = request_details.get("year_max")
        if year_min and listing.year and listing.year < year_min:
            return False
        if year_max and listing.year and listing.year > year_max:
            return False

        # Price - range check
        price_min = request_details.get("price_min")
        price_max = request_details.get("price_max")
        if price_min and listing.price and listing.price < price_min:
            return False
        if price_max and listing.price and listing.price > price_max:
            return False

        # Mileage - max check
        mileage_max = request_details.get("mileage")
        if mileage_max and listing.mileage and listing.mileage > mileage_max:
            return False

        # Transmission - array check (listing value must be in request array)
        transmission_options = request_details.get("transmission", [])
        if transmission_options and listing.transmission not in transmission_options:
            return False

        # Fuel - array check
        fuel_options = request_details.get("fuel", [])
        if fuel_options and listing.fuel_type not in fuel_options:
            return False

        # Drivetrain - array check
        drivetrain_options = request_details.get("drivetrain", [])
        if drivetrain_options and listing.drivetrain not in drivetrain_options:
            return False

        # All checks passed
        return True

    async def create_match(self, match: Match) -> Match:
        return await self.match_repository.create_match(match)

    async def mark_as_contacted(self, match_id: UUID) -> None:
        await self.match_repository.mark_as_contacted(match_id)