from typing import List, Optional, Literal
from pydantic import BaseModel


class CarListingDetailsSchema(BaseModel):
    type: Literal["car"] = "car"
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    mileage: Optional[int] = None
    color: Optional[List[str]] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    drivetrain: Optional[str] = None
    photos: Optional[List[str]] = None
    link: Optional[str] = None
    description: Optional[str] = None