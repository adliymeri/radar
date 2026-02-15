from sqlalchemy import Column, Text, Numeric, Integer, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
import uuid

class RealEstateListingORM(Base):
    __tablename__ = "real_estate_listings"

    listing_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(Text, nullable=False)
    area = Column(Numeric, nullable=True)
    rooms = Column(Integer, nullable=True)
    price = Column(Numeric, nullable=True)
    location = Column(Text, nullable=True)
    photos = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    link = Column(Text, nullable=True)
    description = Column(Text, nullable=True)