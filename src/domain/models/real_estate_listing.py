from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional

@dataclass
class RealEstateListing:
    listing_id: UUID = field(default_factory=uuid4)
    address: str = ""
    area: Optional[float] = None
    rooms: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    link: Optional[str] = None
    description: Optional[str] = None
