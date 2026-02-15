from typing import Optional, List, Union
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.car_listing import CarListing
from src.domain.repositories.car_listing_repository import CarListingRepository
from src.infrastructure.db.orm_models.car_listing_orm import CarListingORM

class PostgresCarListingRepository(CarListingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_car_listing(self, listing: CarListing) -> CarListing:
        listing_orm = CarListingORM(
            listing_id=listing.listing_id,
            make=listing.make,
            model=listing.model,
            year=listing.year,
            price=listing.price,
            location=listing.location,
            mileage=listing.mileage,
            color=listing.color,
            transmission=listing.transmission,
            fuel_type=listing.fuel_type,
            drivetrain=listing.drivetrain,
            photos=listing.photos,
            link=listing.link,
            description=listing.description,
        )
        self.session.add(listing_orm)
        await self.session.commit()
        await self.session.refresh(listing_orm)
        return listing

    async def get_car_listing_by_id(self, listing_id: UUID) -> Optional[CarListing]:
        result = await self.session.execute(
            select(CarListingORM).where(CarListingORM.listing_id == listing_id)
        )
        listing_orm = result.scalar_one_or_none()
        if not listing_orm:
            return None
        return CarListing(
            listing_id=listing_orm.listing_id,
            make=listing_orm.make,
            model=listing_orm.model,
            year=listing_orm.year,
            price=listing_orm.price,
            location=listing_orm.location,
            mileage=listing_orm.mileage,
            color=listing_orm.color,
            transmission=listing_orm.transmission,
            fuel_type=listing_orm.fuel_type,
            drivetrain=listing_orm.drivetrain,
            photos=listing_orm.photos,
            link=listing_orm.link,
            description=listing_orm.description,
        )

    async def get_all_car_listings(self) -> List[CarListing]:
        result = await self.session.execute(select(CarListingORM))
        listings = []
        for row in result.scalars().all():
            listings.append(
                CarListing(
                    listing_id=row.listing_id,
                    make=row.make,
                    model=row.model,
                    year=row.year,
                    price=row.price,
                    location=row.location,
                    mileage=row.mileage,
                    color=row.color,
                    transmission=row.transmission,
                    fuel_type=row.fuel_type,
                    drivetrain=row.drivetrain,
                    photos=row.photos,
                    link=row.link,
                    description=row.description,
                )
            )
        return listings

    async def update_car_listing(self, listing: CarListing) -> CarListing:
        await self.session.execute(
            update(CarListingORM)
            .where(CarListingORM.listing_id == listing.listing_id)
            .values(
                make=listing.make,
                model=listing.model,
                year=listing.year,
                price=listing.price,
                location=listing.location,
                mileage=listing.mileage,
                color=listing.color,
                transmission=listing.transmission,
                fuel_type=listing.fuel_type,
                drivetrain=listing.drivetrain,
                photos=listing.photos,
                link=listing.link,
                description=listing.description,
            )
        )
        await self.session.commit()
        return listing

    async def delete_car_listings(self, listing_ids: Union[UUID, List[UUID]]) -> None:
        if isinstance(listing_ids, UUID):
            listing_ids = [listing_ids]
        await self.session.execute(delete(CarListingORM).where(CarListingORM.listing_id.in_(listing_ids)))
        await self.session.commit()
