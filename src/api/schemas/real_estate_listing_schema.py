from typing import List, Optional, Literal
from pydantic import BaseModel


class RealEstateListingDetailsSchema(BaseModel):
    type: Literal["real_estate"] = "real_estate"
    address: Optional[str] = None
    area: Optional[float] = None
    rooms: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    photos: Optional[List[str]] = None
    link: Optional[str] = None
    description: Optional[str] = None