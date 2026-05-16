from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.db.base import Base
from src.domain.models.listing import Listing
import uuid


class ListingORM(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sellers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")
    last_matched_at = Column(TIMESTAMP(timezone=True), nullable=True)

    def to_domain(self) -> Listing:
        """Convert ORM model to domain model"""
        return Listing(
            id=self.id,
            seller_id=self.seller_id,
            type=self.type,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )