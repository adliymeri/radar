from sqlalchemy import Column, Text, Numeric, Integer, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
import uuid


class RealEstateListingORM(Base):
    __tablename__ = "real_estate_listings"

    listing_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_type = Column(Text, nullable=False)
    listing_type = Column(Text, nullable=False)
    condition = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    district = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    area = Column(Numeric, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    parking = Column(Boolean, nullable=False, default=False)
    elevator = Column(Boolean, nullable=False, default=False)
    furnished = Column(Boolean, nullable=False, default=False)
    balcony = Column(Boolean, nullable=False, default=False)
    photos = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    link = Column(Text, nullable=True)
    description = Column(Text, nullable=True)