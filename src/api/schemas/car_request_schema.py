from typing import List, Optional, Literal
from pydantic import BaseModel

class CarRequestDetailsSchema(BaseModel):
    type: Literal["car"] = "car"
    make: Optional[str] = None
    model: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    mileage: Optional[int] = None
    transmission: Optional[List[str]] = None
    fuel: Optional[List[str]] = None
    drivetrain: Optional[List[str]] = None