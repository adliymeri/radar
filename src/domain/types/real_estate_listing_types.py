from typing import TypedDict, List, Optional

class RealEstateListingDetails(TypedDict, total=False):
    address: str
    area: Optional[float]
    rooms: Optional[int]
    price: Optional[float]
    location: Optional[str]
    photos: Optional[List[str]]
    link: Optional[str]
    description: Optional[str]
