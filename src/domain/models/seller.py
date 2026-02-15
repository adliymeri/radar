from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List
from src.domain.models.listing import Listing
from src.domain.types.seller_types import SellerDetails, PaymentDetails

@dataclass
class Seller:
    id: UUID = field(default_factory=uuid4)
    details: SellerDetails = field(default_factory=dict)
    payment: PaymentDetails = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    listings: List["Listing"] = field(default_factory=list)  # one-to-many relationship
