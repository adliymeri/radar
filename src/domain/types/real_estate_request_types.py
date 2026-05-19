from typing import TypedDict, List, Optional
from src.domain.enums.real_estate_enums import ListingType, PropertyCondition, PropertyType


class RealEstateRequestDetails(TypedDict, total=False):
    """Real estate search criteria for buyer requests"""
    
    # Property info
    property_type: List[PropertyType]
    listing_type: ListingType
    condition: Optional[PropertyCondition]
    
    # Location
    city: str
    districts: Optional[List[str]]
    
    # Size Range
    min_area: Optional[float]
    max_area: Optional[float]
    
    # Room Range
    min_bedrooms: Optional[int]
    max_bedrooms: Optional[int]
    
    # Price Range (required, always in EUR)
    min_price: float
    max_price: float
    
    # Boolean Filters
    parking: Optional[bool]
    elevator: Optional[bool]
    furnished: Optional[bool]
    balcony: Optional[bool]
    
    # Floor Range
    min_floor: Optional[int]
    max_floor: Optional[int]