from typing import TypedDict, List, Optional

class CarListingDetails(TypedDict, total=False):
    make: str
    model: str
    year: Optional[int]
    price: Optional[float]
    location: Optional[str]
    mileage: Optional[int]
    color: Optional[List[str]]
    transmission: Optional[str]
    fuel_type: Optional[str]
    drivetrain: Optional[str]
    photos: Optional[List[str]]
    link: Optional[str]
    description: Optional[str]
