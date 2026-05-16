from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.listing import Listing
from src.domain.repositories.listing_repository import ListingRepository
from src.infrastructure.db.orm_models.listing_orm import ListingORM
from src.infrastructure.utils.logs import app_log

class PostgresListingRepository(ListingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_listing(self, listing: Listing) -> Listing:
        listing_orm = ListingORM(
            id=listing.id,
            seller_id=listing.seller_id,
            type=listing.type
        )
        self.session.add(listing_orm)
        await self.session.commit()
        await self.session.refresh(listing_orm)
        return listing

    async def get_listing_by_id(self, listing_id: UUID) -> Optional[Listing]:
        result = await self.session.execute(
            select(ListingORM).where(ListingORM.id == listing_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return Listing(
            id=orm.id,
            seller_id=orm.seller_id,
            type=orm.type,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    async def get_all_listings(self) -> List[Listing]:
        result = await self.session.execute(select(ListingORM))
        listings = []
        for orm in result.scalars().all():
            listings.append(
                Listing(
                    id=orm.id,
                    seller_id=orm.seller_id,
                    type=orm.type,
                    created_at=orm.created_at,
                    updated_at=orm.updated_at
                )
            )
        return listings
    
    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        result = await self.session.execute(
            select(ListingORM).where(ListingORM.seller_id == seller_id)
        )
        listings = []
        for row in result.scalars().all():
            # map to domain model
            listings.append(
                Listing(
                    id=row.id,
                    seller_id=row.seller_id,
                    type=row.type,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
            )
        return listings

    async def update_listing(self, listing: Listing) -> Listing:
        await self.session.execute(
            update(ListingORM)
            .where(ListingORM.id == listing.id)
            .values(
                type=listing.type,
            )
        )
        await self.session.commit()
        return listing

    async def delete_listing(self, listing_id: UUID) -> None:
        await self.session.execute(
            delete(ListingORM).where(ListingORM.id == listing_id)
        )
        await self.session.commit()

    async def delete_listings_by_seller(self, seller_id: UUID) -> None:
        """Delete all listings belonging to a seller."""
        await self.session.execute(
            delete(ListingORM).where(ListingORM.seller_id == seller_id)
        )
        await self.session.commit()
    
    async def get_listings_by_seller(self, seller_id: UUID) -> List[Listing]:
        """Get all listings for a seller"""
        result = await self.session.execute(
            select(ListingORM)
            .where(ListingORM.seller_id == seller_id)
            .order_by(ListingORM.created_at.desc())
        )
        listing_orms = result.scalars().all()
        return [listing_orm.to_domain() for listing_orm in listing_orms]

    async def delete_listing(self, listing_id: UUID) -> None:
        """Delete a listing"""
        result = await self.session.execute(
            select(ListingORM).where(ListingORM.id == listing_id)
        )
        listing_orm = result.scalar_one_or_none()
        
        if not listing_orm:
            raise ValueError(f"Listing {listing_id} not found")
        
        await self.session.delete(listing_orm)
        await self.session.commit()
