from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from src.domain.models.car_listing import CarListing
from src.domain.models.real_estate_listing import RealEstateListing

@dataclass
class Listing:
    id: UUID = field(default_factory=uuid4)
    seller_id: UUID = field(default_factory=uuid4)
    type: str = ""  # 'car', 'real_estate', 'other'
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    car: Optional[CarListing] = None
    real_estate: Optional[RealEstateListing] = None
