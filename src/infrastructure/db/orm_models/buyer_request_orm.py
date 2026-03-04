from sqlalchemy import ARRAY, Column, TIMESTAMP, String, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
from sqlalchemy.ext.mutable import MutableList
import uuid

class BuyerRequestORM(Base):
    __tablename__ = "buyer_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    details = Column(JSONB, nullable=False)  # was JSON
    status = Column(String(50), nullable=False, server_default=text("'pending'"))
    matched_listing_ids = Column(
        MutableList.as_mutable(ARRAY(UUID(as_uuid=True))),
        nullable=False,
        server_default=text("ARRAY[]::UUID[]")
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))