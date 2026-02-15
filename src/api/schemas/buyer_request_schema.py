from datetime import datetime
from uuid import UUID
from typing import Optional, List, Union, Annotated
from pydantic import BaseModel, ConfigDict, Field
from src.api.schemas.car_listing_schema import CarListingDetailsSchema
from src.api.schemas.real_estate_listing_schema import RealEstateListingDetailsSchema

BuyerRequestDetailsSchema = Annotated[
    Union[CarListingDetailsSchema, RealEstateListingDetailsSchema],
    Field(discriminator="type")
]

class BuyerRequestCreateRequest(BaseModel):
    buyer_id: UUID
    type: str
    details: BuyerRequestDetailsSchema


class BuyerRequestUpdateRequest(BaseModel):
    type: Optional[str] = None
    details: Optional[BuyerRequestDetailsSchema] = None
    status: Optional[str] = None


class BuyerRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    buyer_id: UUID
    type: str
    details: dict
    status: str
    matched_listing: Optional[dict] = None
    created_at: datetime
    updated_at: datetime