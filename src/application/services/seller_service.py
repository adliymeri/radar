from typing import List, Optional, Union
from uuid import UUID
from src.domain.exceptions.seller import SellerAlreadyExistsError
from src.domain.models.seller import Seller
from src.domain.repositories.seller_repository import SellerRepository
from src.domain.services.seller_service_interface import ISellerService
from src.infrastructure.utils.logs import app_log  

class SellerService(ISellerService):
    def __init__(self, repository: SellerRepository):
        self.repository = repository

    async def create_seller(self, seller: Seller) -> Seller:
        existing = await self.repository.get_seller_by_chat_id(seller.details["chat_id"])
        if existing:
            raise SellerAlreadyExistsError(seller.details["chat_id"])
        try:
            return await self.repository.create_seller(seller)
        except Exception as e:
            app_log.error(f"Error creating seller: {e}")
            raise

    async def get_seller_by_id(self, seller_id: UUID) -> Optional[Seller]:
        try:
            return await self.repository.get_seller_by_id(seller_id)
        except Exception as e:
            app_log.error(f"Error fetching seller by id {seller_id}: {e}")
            raise
    
    async def get_seller_by_chat_id(self, chat_id: str) -> Optional[Seller]:
        try:
            return await self.repository.get_seller_by_chat_id(chat_id)
        except Exception as e:
            app_log.error(f"Error fetching seller by chat_id {chat_id}: {e}")
            raise

    async def get_all_sellers(self) -> List[Seller]:
        try:
            return await self.repository.get_all_sellers()
        except Exception as e:
            app_log.error(f"Error fetching all sellers: {e}")
            raise

    async def update_seller(self, seller: Seller) -> Seller:
        try:
            return await self.repository.update_seller(seller)
        except Exception as e:
            app_log.error(f"Error updating seller {seller.id}: {e}")
            raise

    async def delete_sellers(self, seller_ids: Union[UUID, List[UUID]]) -> None:
        try:
            await self.repository.delete_sellers(seller_ids)
        except Exception as e:
            app_log.error(f"Error deleting seller(s) {seller_ids}: {e}")
            raise
