from typing import List, Optional
from uuid import UUID
from src.domain.models.buyer_request import BuyerRequest
from src.domain.repositories.buyer_request_repository import BuyerRequestRepository
from src.domain.services.buyer_request_service_interface import IBuyerRequestService
from src.infrastructure.utils.logs import app_log

class BuyerRequestService(IBuyerRequestService):
    def __init__(self, repository: BuyerRequestRepository):
        self.repository = repository

    async def create_request(self, request: BuyerRequest) -> BuyerRequest:
        try:
            return await self.repository.create_request(request)
        except Exception as e:
            app_log.error(f"Error creating buyer request: {e}")
            raise

    async def get_request_by_id(self, request_id: UUID) -> Optional[BuyerRequest]:
        try:
            return await self.repository.get_request_by_id(request_id)
        except Exception as e:
            app_log.error(f"Error fetching buyer request {request_id}: {e}")
            raise

    async def get_all_requests(self) -> List[BuyerRequest]:
        try:
            return await self.repository.get_all_requests()
        except Exception as e:
            app_log.error(f"Error fetching all buyer requests: {e}")
            raise

    async def get_requests_by_buyer(self, buyer_id: UUID) -> List[BuyerRequest]:
        try:
            return await self.repository.get_requests_by_buyer(buyer_id)
        except Exception as e:
            app_log.error(f"Error fetching requests for buyer {buyer_id}: {e}")
            raise

    async def update_request(self, request: BuyerRequest) -> BuyerRequest:
        try:
            return await self.repository.update_request(request)
        except Exception as e:
            app_log.error(f"Error updating buyer request {request.id}: {e}")
            raise

    async def delete_requests(self, request_ids: List[UUID]) -> None:
        try:
            await self.repository.delete_requests(request_ids)
        except Exception as e:
            app_log.error(f"Error deleting buyer requests {request_ids}: {e}")
            raise

    async def delete_requests_by_buyer(self, buyer_id: UUID) -> None:
        try:
            await self.repository.delete_requests_by_buyer(buyer_id)
        except Exception as e:
            app_log.error(f"Error deleting all requests for buyer {buyer_id}: {e}")
            raise
