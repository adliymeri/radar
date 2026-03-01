from typing import TypedDict, List, Optional

class CarRequestDetails(TypedDict, total=False):
    make: str
    model: str
    year_min: Optional[int]
    year_max: Optional[int]
    price_min: Optional[float]
    price_max: Optional[float]
    mileage: Optional[int]  # max mileage
    transmission: Optional[List[str]]  # array
    fuel: Optional[List[str]]  # array
    drivetrain: Optional[List[str]]  # array