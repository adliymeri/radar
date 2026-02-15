from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.infrastructure.db.base import Base
import uuid

class CarListingORM(Base):
    __tablename__ = "car_listings"

    listing_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer)
    price = Column(Float)
    location = Column(String)
    mileage = Column(Integer)
    color = Column(JSONB)
    transmission = Column(String)
    fuel_type = Column(String)
    drivetrain = Column(String)
    photos = Column(JSONB, default=[])
    link = Column(Text)
    description = Column(Text)