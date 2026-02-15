from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List
from src.domain.types.buyer_types import BuyerDetails, BuyerPaymentDetails
from src.domain.models.buyer_request import BuyerRequest

@dataclass
class Buyer:
    id: UUID = field(default_factory=uuid4)
    details: BuyerDetails = field(default_factory=dict)
    payment: BuyerPaymentDetails = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    requests: List[BuyerRequest] = field(default_factory=list)  # one-to-many relationship
