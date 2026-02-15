from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.db.base import Base
import uuid

class ListingORM(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sellers.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    type = Column(String(50), nullable=False)  # 'car', 'real_estate', 'other'
    created_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP(timezone=True), server_default="CURRENT_TIMESTAMP")
