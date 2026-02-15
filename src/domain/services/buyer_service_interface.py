from abc import ABC, abstractmethod
from typing import Optional, List, Union
from uuid import UUID
from src.domain.models.buyer import Buyer

class IBuyerService(ABC):
    """Abstraction for Buyer service logic."""

    @abstractmethod
    async def create_buyer(self, buyer: Buyer) -> Buyer:
        """Create a new buyer."""
        pass

    @abstractmethod
    async def get_buyer_by_id(self, buyer_id: UUID) -> Optional[Buyer]:
        """Fetch a buyer by their ID."""
        pass

    @abstractmethod
    async def get_all_buyers(self) -> List[Buyer]:
        """Fetch all buyers."""
        pass

    @abstractmethod
    async def update_buyer(self, buyer: Buyer) -> Buyer:
        """Update an existing buyer."""
        pass

    @abstractmethod
    async def delete_buyers(self, buyer_ids: Union[UUID, List[UUID]]) -> None:
        """Delete one or multiple buyers."""
        pass
