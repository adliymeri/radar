from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from src.api.schemas.buyer_details_schema import BuyerDetailsSchema, BuyerPaymentDetailsSchema

class BuyerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    details: dict  
    payment: dict
    created_at: datetime
    updated_at: datetime


class BuyerCreateRequest(BaseModel):
    details: BuyerDetailsSchema
    payment: BuyerPaymentDetailsSchema = BuyerPaymentDetailsSchema()


class BuyerUpdateRequest(BaseModel):
    details: Optional[BuyerDetailsSchema] = None
    payment: Optional[BuyerPaymentDetailsSchema] = None