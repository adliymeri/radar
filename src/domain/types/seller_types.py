from typing import TypedDict, Optional

class SellerDetails(TypedDict):
    name: str
    mobile_phone: str
    telegram_handle: str
    chat_id: str
    email: str
    website: Optional[str]

class PaymentDetails(TypedDict, total=False):
    status: str
    plan: str
    last_paid_at: Optional[str]  # ISO string
    expires_at: Optional[str]
    payment_method: Optional[str]
