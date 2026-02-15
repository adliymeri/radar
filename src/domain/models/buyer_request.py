from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from src.domain.types.buyer_request_types import BuyerRequestDetails
from src.domain.models.listing import Listing

@dataclass
class BuyerRequest:
    id: UUID = field(default_factory=uuid4)
    buyer_id: UUID = field(default_factory=uuid4)
    type: str = ""  # 'car', 'real_estate', etc.
    details: BuyerRequestDetails = field(default_factory=dict)
    status: str = "pending"
    matched_listing: Optional[Listing] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
