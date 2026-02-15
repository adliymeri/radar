from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional

@dataclass
class CarListing:
    listing_id: UUID = field(default_factory=uuid4)
    make: str = ""
    model: str = ""
    year: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    mileage: Optional[int] = None
    color: Optional[List[str]] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    drivetrain: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    link: Optional[str] = None
    description: Optional[str] = None
