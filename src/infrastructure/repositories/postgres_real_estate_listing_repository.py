from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Union
from uuid import UUID
from src.domain.models.real_estate_listing import RealEstateListing
from src.domain.repositories.real_estate_listing_repository import RealEstateListingRepository
from src.infrastructure.db.orm_models.real_estate_listing_orm import RealEstateListingORM

class PostgresRealEstateListingRepository(RealEstateListingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_listing(self, listing: RealEstateListing) -> RealEstateListing:
        listing_orm = RealEstateListingORM(
            listing_id=listing.listing_id,
            address=listing.address,
            area=listing.area,
            rooms=listing.rooms,
            price=listing.price,
            location=listing.location,
            photos=listing.photos,
            link=listing.link,
            description=listing.description,
        )
        self.session.add(listing_orm)
        await self.session.commit()
        await self.session.refresh(listing_orm)
        return listing

    async def get_listing_by_id(self, listing_id: UUID) -> Optional[RealEstateListing]:
        result = await self.session.execute(
            select(RealEstateListingORM).where(RealEstateListingORM.listing_id == listing_id)
        )
        orm_obj = result.scalar_one_or_none()
        if not orm_obj:
            return None
        return RealEstateListing(
            listing_id=orm_obj.listing_id,
            address=orm_obj.address,
            area=orm_obj.area,
            rooms=orm_obj.rooms,
            price=orm_obj.price,
            location=orm_obj.location,
            photos=orm_obj.photos,
            link=orm_obj.link,
            description=orm_obj.description,
        )

    async def get_all_listings(self) -> List[RealEstateListing]:
        result = await self.session.execute(select(RealEstateListingORM))
        listings = []
        for row in result.scalars().all():
            listings.append(
                RealEstateListing(
                    listing_id=row.listing_id,
                    address=row.address,
                    area=row.area,
                    rooms=row.rooms,
                    price=row.price,
                    location=row.location,
                    photos=row.photos,
                    link=row.link,
                    description=row.description,
                )
            )
        return listings

    async def get_listings_by_seller(self, seller_id: UUID) -> List[RealEstateListing]:
        # Assuming seller_id is stored in the 'listings' table and joined externally
        # You might need a join query with ListingORM -> RealEstateListingORM
        raise NotImplementedError("Join with listings table needed to fetch by seller")

    async def update_listing(self, listing: RealEstateListing) -> RealEstateListing:
        await self.session.execute(
            update(RealEstateListingORM)
            .where(RealEstateListingORM.listing_id == listing.listing_id)
            .values(
                address=listing.address,
                area=listing.area,
                rooms=listing.rooms,
                price=listing.price,
                location=listing.location,
                photos=listing.photos,
                link=listing.link,
                description=listing.description,
            )
        )
        await self.session.commit()
        return listing

    async def delete_listing(self, listing_id: UUID) -> None:
        await self.delete_listings(listing_id)

    async def delete_listings(self, listing_ids: Union[UUID, List[UUID]]) -> None:
        if not isinstance(listing_ids, list):
            listing_ids = [listing_ids]
        await self.session.execute(
            delete(RealEstateListingORM).where(RealEstateListingORM.listing_id.in_(listing_ids))
        )
        await self.session.commit()
