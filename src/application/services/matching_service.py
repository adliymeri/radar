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
from src.infrastructure.db.orm_models.real_estate_listing_orm import RealEstateListingORM
from src.infrastructure.db.orm_models.listing_orm import ListingORM
from src.infrastructure.utils.logs import app_log


class MatchingService(IMatchingService):
    def __init__(self, session: AsyncSession, match_repository: MatchRepository):
        self.session = session
        self.match_repository = match_repository

    async def find_matches(self, last_run: Optional[datetime] = None) -> List[Match]:
        matches = []

        # Run car matching
        car_matches = await self._find_car_matches(last_run)
        matches.extend(car_matches)

        # Run real estate matching
        real_estate_matches = await self._find_real_estate_matches(last_run)
        matches.extend(real_estate_matches)

        app_log.info(f"Total new matches found: {len(matches)} (cars: {len(car_matches)}, real_estate: {len(real_estate_matches)})")
        return matches

    # ================= CAR MATCHING =================

    async def _find_car_matches(self, last_run: Optional[datetime] = None) -> List[Match]:
        matches = []

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
            app_log.info("No active car buyer requests found")
            return matches

        listing_filter = [ListingORM.type == "car"]

        if last_run:
            listing_filter.append(
                or_(
                    ListingORM.created_at > last_run,
                    ListingORM.updated_at > last_run,
                    ListingORM.last_matched_at.is_(None),
                    ListingORM.last_matched_at < last_run
                )
            )

        result = await self.session.execute(
            select(CarListingORM, ListingORM).join(
                ListingORM, CarListingORM.listing_id == ListingORM.id
            ).where(and_(*listing_filter))
        )
        listings_data = result.all()

        if not listings_data:
            app_log.info("No new/updated car listings found")
            return matches

        # Load existing matches
        existing_matches = await self._load_existing_matches(
            [r.id for r in requests],
            [listing_orm.id for _, listing_orm in listings_data]
        )

        app_log.info(
            f"Car matching: {len(requests)} requests against "
            f"{len(listings_data)} new/updated listings"
        )

        for request_orm in requests:
            matched_count = 0

            for car_listing_orm, listing_orm in listings_data:
                if (listing_orm.id, request_orm.id) in existing_matches:
                    continue

                if self._car_quick_filter(request_orm.details, car_listing_orm):
                    if self._car_detailed_match(request_orm.details, car_listing_orm):
                        match = Match(
                            buyer_id=request_orm.buyer_id,
                            seller_id=listing_orm.seller_id,
                            listing_id=listing_orm.id,
                            request_id=request_orm.id,
                            status="notified",
                        )
                        matches.append(match)
                        matched_count += 1

                        if request_orm.matched_listing_ids is None:
                            request_orm.matched_listing_ids = []

                        if listing_orm.id not in request_orm.matched_listing_ids:
                            request_orm.matched_listing_ids.append(listing_orm.id)

                        existing_matches.add((listing_orm.id, request_orm.id))

            if matched_count > 0:
                app_log.info(f"Car request {request_orm.id}: {matched_count} new matches")

        for _, listing_orm in listings_data:
            listing_orm.last_matched_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.commit()

        return matches

    def _car_quick_filter(self, request_details: dict, listing: CarListingORM) -> bool:
        if request_details.get("make") and request_details["make"] != listing.make:
            return False
        if request_details.get("model") and request_details["model"] != listing.model:
            return False

        year_min = request_details.get("year_min")
        year_max = request_details.get("year_max")
        if year_min and listing.year and listing.year < year_min:
            return False
        if year_max and listing.year and listing.year > year_max:
            return False

        price_min = request_details.get("price_min")
        price_max = request_details.get("price_max")
        if price_min and listing.price and listing.price < price_min:
            return False
        if price_max and listing.price and listing.price > price_max:
            return False

        mileage_max = request_details.get("mileage")
        if mileage_max and listing.mileage and listing.mileage > mileage_max:
            return False

        return True

    def _car_detailed_match(self, request_details: dict, listing: CarListingORM) -> bool:
        transmission_options = request_details.get("transmission", [])
        if transmission_options and listing.transmission not in transmission_options:
            return False

        fuel_options = request_details.get("fuel", [])
        if fuel_options and listing.fuel_type not in fuel_options:
            return False

        drivetrain_options = request_details.get("drivetrain", [])
        if drivetrain_options and listing.drivetrain not in drivetrain_options:
            return False

        return True

    # ================= REAL ESTATE MATCHING =================

    async def _find_real_estate_matches(self, last_run: Optional[datetime] = None) -> List[Match]:
        matches = []

        result = await self.session.execute(
            select(BuyerRequestORM).where(
                and_(
                    BuyerRequestORM.type == "real_estate",
                    BuyerRequestORM.status == "active"
                )
            )
        )
        requests = result.scalars().all()

        if not requests:
            app_log.info("No active real estate buyer requests found")
            return matches

        listing_filter = [ListingORM.type == "real_estate"]

        if last_run:
            listing_filter.append(
                or_(
                    ListingORM.created_at > last_run,
                    ListingORM.updated_at > last_run,
                    ListingORM.last_matched_at.is_(None),
                    ListingORM.last_matched_at < last_run
                )
            )

        result = await self.session.execute(
            select(RealEstateListingORM, ListingORM).join(
                ListingORM, RealEstateListingORM.listing_id == ListingORM.id
            ).where(and_(*listing_filter))
        )
        listings_data = result.all()

        if not listings_data:
            app_log.info("No new/updated real estate listings found")
            return matches

        existing_matches = await self._load_existing_matches(
            [r.id for r in requests],
            [listing_orm.id for _, listing_orm in listings_data]
        )

        app_log.info(
            f"Real estate matching: {len(requests)} requests against "
            f"{len(listings_data)} new/updated listings"
        )

        for request_orm in requests:
            matched_count = 0

            for re_listing_orm, listing_orm in listings_data:
                if (listing_orm.id, request_orm.id) in existing_matches:
                    continue

                if self._real_estate_match(request_orm.details, re_listing_orm):
                    match = Match(
                        buyer_id=request_orm.buyer_id,
                        seller_id=listing_orm.seller_id,
                        listing_id=listing_orm.id,
                        request_id=request_orm.id,
                        status="notified",
                    )
                    matches.append(match)
                    matched_count += 1

                    if request_orm.matched_listing_ids is None:
                        request_orm.matched_listing_ids = []

                    if listing_orm.id not in request_orm.matched_listing_ids:
                        request_orm.matched_listing_ids.append(listing_orm.id)

                    existing_matches.add((listing_orm.id, request_orm.id))

            if matched_count > 0:
                app_log.info(f"Real estate request {request_orm.id}: {matched_count} new matches")

        for _, listing_orm in listings_data:
            listing_orm.last_matched_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.commit()

        return matches

    def _real_estate_match(self, request_details: dict, listing: RealEstateListingORM) -> bool:
        """Match real estate listing against buyer request"""

        # Property type (buyer can select multiple)
        property_types = request_details.get("property_type", [])
        if property_types and listing.property_type not in property_types:
            return False

        # Listing type (sale/rent)
        listing_type = request_details.get("listing_type")
        if listing_type and listing.listing_type != listing_type:
            return False

        # Condition
        condition = request_details.get("condition")
        if condition and listing.condition != condition:
            return False

        # City (must match)
        if request_details.get("city") and listing.city != request_details["city"]:
            return False

        # Districts (if buyer specified, listing must be in one)
        districts = request_details.get("districts")
        if districts and listing.district not in districts:
            return False

        # Price range
        min_price = request_details.get("min_price")
        max_price = request_details.get("max_price")
        if min_price and listing.price and float(listing.price) < min_price:
            return False
        if max_price and listing.price and float(listing.price) > max_price:
            return False

        # Area range
        min_area = request_details.get("min_area")
        max_area = request_details.get("max_area")
        if min_area and listing.area and float(listing.area) < min_area:
            return False
        if max_area and listing.area and float(listing.area) > max_area:
            return False

        # Bedrooms range
        min_bedrooms = request_details.get("min_bedrooms")
        max_bedrooms = request_details.get("max_bedrooms")
        if min_bedrooms and listing.bedrooms and listing.bedrooms < min_bedrooms:
            return False
        if max_bedrooms and listing.bedrooms and listing.bedrooms > max_bedrooms:
            return False

        # Floor range
        min_floor = request_details.get("min_floor")
        max_floor = request_details.get("max_floor")
        if min_floor is not None and listing.floor is not None and listing.floor < min_floor:
            return False
        if max_floor is not None and listing.floor is not None and listing.floor > max_floor:
            return False

        # Boolean filters (buyer True = must have, None = don't care)
        if request_details.get("parking") is True and listing.parking is False:
            return False
        if request_details.get("elevator") is True and listing.elevator is False:
            return False
        if request_details.get("furnished") is True and listing.furnished is False:
            return False
        if request_details.get("balcony") is True and listing.balcony is False:
            return False

        return True

    # ================= SHARED HELPERS =================

    async def _load_existing_matches(self, request_ids: list, listing_ids: list) -> set:
        from src.infrastructure.db.orm_models.match_orm import MatchORM
        result = await self.session.execute(
            select(MatchORM.listing_id, MatchORM.request_id).where(
                and_(
                    MatchORM.request_id.in_(request_ids),
                    MatchORM.listing_id.in_(listing_ids)
                )
            )
        )
        existing = set((row[0], row[1]) for row in result.all())
        app_log.info(f"Loaded {len(existing)} existing matches into memory")
        return existing

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

    async def get_matches_by_request(self, request_id: UUID, limit: Optional[int] = None, offset: int = 0) -> List[Match]:
        try:
            return await self.match_repository.get_matches_by_request(request_id, limit, offset)
        except Exception as e:
            app_log.error(f"Error fetching matches for request {request_id}: {e}")
            raise

    async def count_matches_by_request(self, request_id: UUID) -> int:
        try:
            return await self.match_repository.count_matches_by_request(request_id)
        except Exception as e:
            app_log.error(f"Error counting matches for request {request_id}: {e}")
            raise