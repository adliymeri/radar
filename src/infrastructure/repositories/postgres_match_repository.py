from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.match import Match
from src.domain.repositories.match_repository import MatchRepository
from src.infrastructure.db.orm_models.match_orm import MatchORM

class PostgresMatchRepository(MatchRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_match(self, match: Match) -> Match:
        match_orm = MatchORM(
            id=match.id,
            buyer_id=match.buyer_id,
            seller_id=match.seller_id,
            listing_id=match.listing_id,
            request_id=match.request_id,
            status=match.status,
            notified_at=match.notified_at,
            contacted_at=match.contacted_at,
        )
        self.session.add(match_orm)
        await self.session.commit()
        await self.session.refresh(match_orm)
        return match

    async def get_match_by_id(self, match_id: UUID) -> Optional[Match]:
        result = await self.session.execute(
            select(MatchORM).where(MatchORM.id == match_id)
        )
        orm = result.scalar_one_or_none()
        if not orm:
            return None
        return Match(
            id=orm.id,
            buyer_id=orm.buyer_id,
            seller_id=orm.seller_id,
            listing_id=orm.listing_id,
            request_id=orm.request_id,
            status=orm.status,
            notified_at=orm.notified_at,
            contacted_at=orm.contacted_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def get_matches_by_buyer(self, buyer_id: UUID) -> List[Match]:
        result = await self.session.execute(
            select(MatchORM).where(MatchORM.buyer_id == buyer_id)
        )
        return [
            Match(
                id=orm.id,
                buyer_id=orm.buyer_id,
                seller_id=orm.seller_id,
                listing_id=orm.listing_id,
                request_id=orm.request_id,
                status=orm.status,
                notified_at=orm.notified_at,
                contacted_at=orm.contacted_at,
                created_at=orm.created_at,
                updated_at=orm.updated_at,
            )
            for orm in result.scalars().all()
        ]

    async def get_matches_by_seller(self, seller_id: UUID) -> List[Match]:
        result = await self.session.execute(
            select(MatchORM).where(MatchORM.seller_id == seller_id)
        )
        return [
            Match(
                id=orm.id,
                buyer_id=orm.buyer_id,
                seller_id=orm.seller_id,
                listing_id=orm.listing_id,
                request_id=orm.request_id,
                status=orm.status,
                notified_at=orm.notified_at,
                contacted_at=orm.contacted_at,
                created_at=orm.created_at,
                updated_at=orm.updated_at,
            )
            for orm in result.scalars().all()
        ]

    async def match_exists(self, listing_id: UUID, request_id: UUID) -> bool:
        result = await self.session.execute(
            select(exists().where(
                (MatchORM.listing_id == listing_id) &
                (MatchORM.request_id == request_id)
            ))
        )
        return result.scalar()

    async def update_match(self, match: Match) -> Match:
        result = await self.session.execute(
            select(MatchORM).where(MatchORM.id == match.id)
        )
        orm = result.scalar_one()
        
        orm.status = match.status
        orm.contacted_at = match.contacted_at
        orm.updated_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        await self.session.refresh(orm)
        return match

    async def mark_as_contacted(self, match_id: UUID) -> None:
        result = await self.session.execute(
            select(MatchORM).where(MatchORM.id == match_id)
        )
        orm = result.scalar_one()
        
        orm.status = "contacted"
        orm.contacted_at = datetime.now(timezone.utc)
        orm.updated_at = datetime.now(timezone.utc)
        
        await self.session.commit()