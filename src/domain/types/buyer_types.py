from typing import TypedDict, Optional

class BuyerDetails(TypedDict):
    name: str
    surname: str
    mobile_phone: str
    telegram_handle: str
    chat_id: str
    email: str

class BuyerPaymentDetails(TypedDict, total=False):
    status: str
    plan: str
    last_paid_at: Optional[str]
    expires_at: Optional[str]
    payment_method: Optional[str]
