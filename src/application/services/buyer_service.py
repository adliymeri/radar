from typing import Optional, List, Union
from uuid import UUID
from src.domain.exceptions.buyer import BuyerAlreadyExistsError
from src.domain.models.buyer import Buyer
from src.domain.repositories.buyer_repository import BuyerRepository
from src.domain.services.buyer_service_interface import IBuyerService
from src.infrastructure.utils.logs import app_log  

class BuyerService(IBuyerService):
    def __init__(self, repository: BuyerRepository):
        self.repository = repository

    async def create_buyer(self, buyer: Buyer) -> Buyer:
        existing_buyer = await self.repository.get_buyer_by_chat_id(buyer.details["chat_id"])
        
        if existing_buyer:
            app_log.warning(f"Conflict: Chat ID {buyer.details['chat_id']} already exists.")
            raise BuyerAlreadyExistsError(buyer.details["chat_id"])
        
        try:
            return await self.repository.create_buyer(buyer)
        except Exception as e:
            app_log.error(f"Infrastructure Error in create_buyer: {e}")
            raise

    async def get_buyer_by_id(self, buyer_id: UUID) -> Optional[Buyer]:
        try:
            return await self.repository.get_buyer_by_id(buyer_id)
        except Exception as e:
            app_log.error(f"Error fetching buyer by id {buyer_id}: {e}")
            raise

    async def get_buyer_by_chat_id(self, chat_id: str) -> Optional[Buyer]:
        try:
            return await self.repository.get_buyer_by_chat_id(chat_id)
        except Exception as e:
            app_log.error(f"Error fetching buyer by chat_id {chat_id}: {e}")
            raise

    async def get_all_buyers(self) -> List[Buyer]:
        try:
            return await self.repository.get_all_buyers()
        except Exception as e:
            app_log.error(f"Error fetching all buyers: {e}")
            raise

    async def update_buyer(self, buyer: Buyer) -> Buyer:
        try:
            return await self.repository.update_buyer(buyer)
        except Exception as e:
            app_log.error(f"Error updating buyer {buyer.id}: {e}")
            raise

    async def delete_buyers(self, buyer_ids: Union[UUID, List[UUID]]) -> None:
        try:
            await self.repository.delete_buyers(buyer_ids)
        except Exception as e:
            app_log.error(f"Error deleting buyer(s) {buyer_ids}: {e}")
            raise
