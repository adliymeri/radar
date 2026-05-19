from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional


@dataclass
class RealEstateListing:
    listing_id: UUID = field(default_factory=uuid4)
    property_type: str = ""
    listing_type: str = ""
    condition: str = ""
    city: str = ""
    district: str = ""
    address: str = ""
    area: float = 0.0
    bedrooms: int = 0
    bathrooms: int = 0
    floor: int = 0
    price: float = 0.0
    parking: bool = False
    elevator: bool = False
    furnished: bool = False
    balcony: bool = False
    photos: List[str] = field(default_factory=list)
    link: Optional[str] = None
    description: Optional[str] = None