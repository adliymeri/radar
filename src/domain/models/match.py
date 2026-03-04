from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class Match:
    id: UUID = field(default_factory=uuid4)
    buyer_id: UUID = field(default_factory=uuid4)
    seller_id: UUID = field(default_factory=uuid4)
    listing_id: UUID = field(default_factory=uuid4)
    request_id: UUID = field(default_factory=uuid4)
    status: str = "notified"  # 'notified', 'contacted', 'rejected'
    notified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    contacted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))