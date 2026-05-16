from datetime import datetime, timezone  # CHANGED: Correct import
from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.seller import Seller
from src.domain.repositories.seller_repository import SellerRepository
from src.infrastructure.db.orm_models.seller_orm import SellerORM


class PostgresSellerRepository(SellerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_seller(self, seller: Seller) -> Seller:
        seller_orm = SellerORM(
            id=seller.id,
            details=seller.details,
            payment=seller.payment,
        )
        self.session.add(seller_orm)
        await self.session.commit()
        await self.session.refresh(seller_orm)
        return seller

    async def get_seller_by_id(self, seller_id: UUID) -> Optional[Seller]:
        result = await self.session.execute(
            select(SellerORM).where(SellerORM.id == seller_id)
        )
        seller_orm = result.scalar_one_or_none()
        if seller_orm is None:
            return None
        return Seller(
            id=seller_orm.id,
            details=seller_orm.details,
            payment=seller_orm.payment,
            created_at=seller_orm.created_at,
            updated_at=seller_orm.updated_at,
        )
    
    async def get_seller_by_chat_id(self, chat_id: str) -> Optional[Seller]:
        result = await self.session.execute(
            select(SellerORM).where(SellerORM.details["chat_id"].astext == str(chat_id))
        )
        seller_orm = result.scalar_one_or_none()
        if seller_orm is None:
            return None
        return Seller(
            id=seller_orm.id,
            details=seller_orm.details,
            payment=seller_orm.payment,
            created_at=seller_orm.created_at,
            updated_at=seller_orm.updated_at,
        )

    async def get_all_sellers(self) -> List[Seller]:
        result = await self.session.execute(select(SellerORM))
        sellers = []
        for row in result.scalars().all():
            sellers.append(
                Seller(
                    id=row.id,
                    details=row.details,
                    payment=row.payment,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
            )
        return sellers

    async def update_seller(self, seller: Seller) -> Seller:
        """Update existing seller"""
        result = await self.session.execute(
            select(SellerORM).where(SellerORM.id == seller.id)
        )
        seller_orm = result.scalar_one_or_none()
        
        if not seller_orm:
            raise ValueError(f"Seller {seller.id} not found")
        
        # Update fields
        seller_orm.details = seller.details
        seller_orm.payment = seller.payment
        seller_orm.updated_at = datetime.now(timezone.utc)  # CHANGED: Correct usage
        
        await self.session.commit()
        await self.session.refresh(seller_orm)
        
        # Return domain model
        return Seller(
            id=seller_orm.id,
            details=seller_orm.details,
            payment=seller_orm.payment,
            created_at=seller_orm.created_at,
            updated_at=seller_orm.updated_at,
        )

    async def delete_sellers(self, seller_ids: Union[UUID, List[UUID]]) -> None:
        if isinstance(seller_ids, UUID):
            seller_ids = [seller_ids]
        await self.session.execute(
            delete(SellerORM).where(SellerORM.id.in_(seller_ids))
        )
        await self.session.commit()