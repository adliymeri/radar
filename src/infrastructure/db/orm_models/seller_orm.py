from sqlalchemy import Column, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
import uuid

class SellerORM(Base):
    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    details = Column(JSONB, nullable=False)
    payment = Column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))