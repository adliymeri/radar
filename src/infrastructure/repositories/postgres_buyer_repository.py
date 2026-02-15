from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.buyer import Buyer
from src.domain.repositories.buyer_repository import BuyerRepository
from src.infrastructure.db.orm_models.buyer_orm import BuyerORM

class PostgresBuyerRepository(BuyerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _ensure_dict(self, field_data):
        if hasattr(field_data, "model_dump"):
            return field_data.model_dump()
        return field_data

    async def create_buyer(self, buyer: Buyer) -> Buyer:
        buyer_orm = BuyerORM(
            id=buyer.id,
            details=self._ensure_dict(buyer.details),
            payment=self._ensure_dict(buyer.payment),
        )
        self.session.add(buyer_orm)
        await self.session.commit()
        await self.session.refresh(buyer_orm)
        return buyer

    async def get_buyer_by_id(self, buyer_id: UUID) -> Optional[Buyer]:
        result = await self.session.execute(
            select(BuyerORM).where(BuyerORM.id == buyer_id)
        )
        buyer_orm = result.scalar_one_or_none()
        if buyer_orm is None:
            return None
        return Buyer(
            id=buyer_orm.id,
            details=buyer_orm.details,
            payment=buyer_orm.payment,
            created_at=buyer_orm.created_at,
            updated_at=buyer_orm.updated_at,
        )
    
    async def get_buyer_by_chat_id(self, chat_id: str) -> Optional[Buyer]:
        result = await self.session.execute(
            select(BuyerORM).where(BuyerORM.details["chat_id"].astext == str(chat_id))
        )
        buyer_orm = result.scalar_one_or_none()

        if buyer_orm is None:
            return None

        return Buyer(
            id=buyer_orm.id,
            details=buyer_orm.details,
            payment=buyer_orm.payment,
            created_at=buyer_orm.created_at,
            updated_at=buyer_orm.updated_at,
        )

    async def get_all_buyers(self) -> List[Buyer]:
        result = await self.session.execute(select(BuyerORM))
        buyers = [
            Buyer(
                id=row.id,
                details=row.details,
                payment=row.payment,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in result.scalars().all()
        ]
        return buyers

    async def update_buyer(self, buyer: Buyer) -> Buyer:
        await self.session.execute(
            update(BuyerORM)
            .where(BuyerORM.id == buyer.id)
            .values(
                details=buyer.details,
                payment=buyer.payment,
            )
        )
        await self.session.commit()
        return buyer

    async def delete_buyers(self, buyer_ids: Union[UUID, List[UUID]]) -> None:
        if isinstance(buyer_ids, UUID):
            buyer_ids = [buyer_ids]

        await self.session.execute(
            delete(BuyerORM).where(BuyerORM.id.in_(buyer_ids))
        )
        await self.session.commit()
