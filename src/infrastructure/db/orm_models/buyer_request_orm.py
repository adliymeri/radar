from sqlalchemy import Column, TIMESTAMP, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
import uuid

class BuyerRequestORM(Base):
    __tablename__ = "buyer_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    details = Column(JSONB, nullable=False)  # was JSON
    status = Column(String(50), nullable=False, server_default=text("'pending'"))
    matched_listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))