from typing import Union
from src.domain.types.car_listing_types import CarListingDetails
from src.domain.types.real_estate_listing_types import RealEstateListingDetails

class BuyerRequestCarDetails(CarListingDetails):
    pass

class BuyerRequestRealEstateDetails(RealEstateListingDetails):
    pass

BuyerRequestDetails = Union[BuyerRequestCarDetails, BuyerRequestRealEstateDetails]
