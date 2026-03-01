from typing import Union
from src.domain.types.car_request_types import CarRequestDetails
from src.domain.types.real_estate_listing_types import RealEstateListingDetails

class BuyerRequestCarDetails(CarRequestDetails):
    pass

class BuyerRequestRealEstateDetails(RealEstateListingDetails):
    pass

BuyerRequestDetails = Union[BuyerRequestCarDetails, BuyerRequestRealEstateDetails]
