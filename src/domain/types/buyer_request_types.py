from typing import Union
from src.domain.types.car_request_types import CarRequestDetails
from src.domain.types.real_estate_request_types import RealEstateRequestDetails

class BuyerRequestCarDetails(CarRequestDetails):
    pass

class BuyerRequestRealEstateDetails(RealEstateRequestDetails):
    pass

BuyerRequestDetails = Union[BuyerRequestCarDetails, BuyerRequestRealEstateDetails]
