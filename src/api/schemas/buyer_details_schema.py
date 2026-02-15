from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

class BuyerDetailsSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
    mobile_phone: str
    telegram_handle: str
    chat_id: str


class BuyerPaymentDetailsSchema(BaseModel):
    status: Optional[Literal["active", "inactive", "expired"]] = None
    plan: Optional[Literal["monthly", "yearly"]] = None
    last_paid_at: Optional[str] = None
    expires_at: Optional[str] = None
    payment_method: Optional[str] = None