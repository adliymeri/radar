from typing import List, Optional, Literal
from pydantic import BaseModel


class RealEstateRequestDetailsSchema(BaseModel):
    type: Literal["real_estate"] = "real_estate"
    property_type: Optional[List[str]] = None
    listing_type: Optional[str] = None
    condition: Optional[str] = None
    city: Optional[str] = None
    districts: Optional[List[str]] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_price: float
    max_price: float
    parking: Optional[bool] = None
    elevator: Optional[bool] = None
    furnished: Optional[bool] = None
    balcony: Optional[bool] = None
    min_floor: Optional[int] = None
    max_floor: Optional[int] = None