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

    def _to_domain(self, orm_obj: RealEstateListingORM) -> RealEstateListing:
        return RealEstateListing(
            listing_id=orm_obj.listing_id,
            property_type=orm_obj.property_type,
            listing_type=orm_obj.listing_type,
            condition=orm_obj.condition,
            city=orm_obj.city,
            district=orm_obj.district,
            address=orm_obj.address,
            area=float(orm_obj.area) if orm_obj.area else 0.0,
            bedrooms=orm_obj.bedrooms,
            bathrooms=orm_obj.bathrooms,
            floor=orm_obj.floor,
            price=float(orm_obj.price) if orm_obj.price else 0.0,
            parking=orm_obj.parking,
            elevator=orm_obj.elevator,
            furnished=orm_obj.furnished,
            balcony=orm_obj.balcony,
            photos=orm_obj.photos or [],
            link=orm_obj.link,
            description=orm_obj.description,
        )

    async def create_listing(self, listing: RealEstateListing) -> RealEstateListing:
        listing_orm = RealEstateListingORM(
            listing_id=listing.listing_id,
            property_type=listing.property_type,
            listing_type=listing.listing_type,
            condition=listing.condition,
            city=listing.city,
            district=listing.district,
            address=listing.address,
            area=listing.area,
            bedrooms=listing.bedrooms,
            bathrooms=listing.bathrooms,
            floor=listing.floor,
            price=listing.price,
            parking=listing.parking,
            elevator=listing.elevator,
            furnished=listing.furnished,
            balcony=listing.balcony,
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
        return self._to_domain(orm_obj)

    async def get_all_listings(self) -> List[RealEstateListing]:
        result = await self.session.execute(select(RealEstateListingORM))
        return [self._to_domain(row) for row in result.scalars().all()]

    async def update_listing(self, listing: RealEstateListing) -> RealEstateListing:
        await self.session.execute(
            update(RealEstateListingORM)
            .where(RealEstateListingORM.listing_id == listing.listing_id)
            .values(
                property_type=listing.property_type,
                listing_type=listing.listing_type,
                condition=listing.condition,
                city=listing.city,
                district=listing.district,
                address=listing.address,
                area=listing.area,
                bedrooms=listing.bedrooms,
                bathrooms=listing.bathrooms,
                floor=listing.floor,
                price=listing.price,
                parking=listing.parking,
                elevator=listing.elevator,
                furnished=listing.furnished,
                balcony=listing.balcony,
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

    async def get_listings_by_seller(self, seller_id: UUID) -> List[RealEstateListing]:
        from src.infrastructure.db.orm_models.listing_orm import ListingORM
        
        result = await self.session.execute(
            select(RealEstateListingORM)
            .join(ListingORM, ListingORM.id == RealEstateListingORM.listing_id)
            .where(ListingORM.seller_id == seller_id)
        )
        return [self._to_domain(row) for row in result.scalars().all()]