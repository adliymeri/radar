from enum import Enum


class PropertyType(str, Enum):
    APARTMENT = "Apartment"
    HOUSE = "House"
    VILLA = "Villa"
    LAND = "Land"
    COMMERCIAL = "Commercial"
    STUDIO = "Studio"


class ListingType(str, Enum):
    SALE = "Sale"
    RENT = "Rent"


class PropertyCondition(str, Enum):
    NEW_CONSTRUCTION = "New Construction"
    OLD_CONSTRUCTION = "Old Construction"
    