from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.buyer_request import BuyerRequest
from src.domain.repositories.buyer_request_repository import BuyerRequestRepository
from src.infrastructure.db.orm_models.buyer_request_orm import BuyerRequestORM

class PostgresBuyerRequestRepository(BuyerRequestRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(self, request: BuyerRequest) -> BuyerRequest:
        orm = BuyerRequestORM(
            id=request.id,
            buyer_id=request.buyer_id,
            type=request.type,
            details=request.details,
            status=request.status,
            matched_listing_id=request.matched_listing.id if request.matched_listing else None
        )
        self.session.add(orm)
        await self.session.commit()
        await self.session.refresh(orm)
        return request

    async def get_request_by_id(self, request_id: UUID) -> Optional[BuyerRequest]:
        result = await self.session.execute(select(BuyerRequestORM).where(BuyerRequestORM.id == request_id))
        orm = result.scalar_one_or_none()
        if not orm:
            return None
        return BuyerRequest(
            id=orm.id,
            buyer_id=orm.buyer_id,
            type=orm.type,
            details=orm.details,
            status=orm.status,
            matched_listing=None,  # optional: load listing separately
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    async def get_all_requests(self) -> List[BuyerRequest]:
        result = await self.session.execute(select(BuyerRequestORM))
        return [
            BuyerRequest(
                id=orm.id,
                buyer_id=orm.buyer_id,
                type=orm.type,
                details=orm.details,
                status=orm.status,
                matched_listing=None,
                created_at=orm.created_at,
                updated_at=orm.updated_at
            )
            for orm in result.scalars().all()
        ]

    async def get_requests_by_buyer(self, buyer_id: UUID) -> List[BuyerRequest]:
        result = await self.session.execute(select(BuyerRequestORM).where(BuyerRequestORM.buyer_id == buyer_id))
        return [
            BuyerRequest(
                id=orm.id,
                buyer_id=orm.buyer_id,
                type=orm.type,
                details=orm.details,
                status=orm.status,
                matched_listing=None,
                created_at=orm.created_at,
                updated_at=orm.updated_at
            )
            for orm in result.scalars().all()
        ]

    async def update_request(self, request: BuyerRequest) -> BuyerRequest:
        await self.session.execute(
            update(BuyerRequestORM)
            .where(BuyerRequestORM.id == request.id)
            .values(
                type=request.type,
                details=request.details,
                status=request.status,
                matched_listing_id=request.matched_listing.id if request.matched_listing else None
            )
        )
        await self.session.commit()
        return request

    async def delete_requests(self, request_ids: Union[UUID, List[UUID]]) -> None:
        if isinstance(request_ids, UUID):
            request_ids = [request_ids]
        await self.session.execute(delete(BuyerRequestORM).where(BuyerRequestORM.id.in_(request_ids)))
        await self.session.commit()

    async def delete_requests_by_buyer(self, buyer_id: UUID) -> None:
        await self.session.execute(
            delete(BuyerRequestORM).where(BuyerRequestORM.buyer_id == buyer_id)
        )
        await self.session.commit()
