from typing import Dict
from src.application.services.car_listing_service import CarListingService
from src.application.services.listing_service import ListingService
from src.infrastructure.repositories.postgres_car_listing_repository import PostgresCarListingRepository
from src.infrastructure.repositories.postgres_listing_repository import PostgresListingRepository
from src.infrastructure.db.postgres import get_session

# Repositories
from src.infrastructure.repositories.postgres_seller_repository import PostgresSellerRepository
from src.infrastructure.repositories.postgres_buyer_repository import PostgresBuyerRepository
from src.infrastructure.repositories.postgres_buyer_request_repository import PostgresBuyerRequestRepository


# Services
from src.application.services.seller_service import SellerService
from src.application.services.buyer_service import BuyerService
from src.application.services.buyer_request_service import BuyerRequestService


class BotDependencyManager:
    """
    Manages dependencies for the Chat App without relying on FastAPI.
    """
    def __init__(self):
        self.session_gen = None
        self.session = None

    async def __aenter__(self) -> Dict[str, object]:
        # 1. Manually trigger the session generator
        self.session_gen = get_session()
        self.session = await anext(self.session_gen)

        # 2. Initialize Repositories (Passing the session)
        buyer_repo = PostgresBuyerRepository(self.session)
        seller_repo = PostgresSellerRepository(self.session)
        buyer_request_repo = PostgresBuyerRequestRepository(self.session)
        listing_repo = PostgresListingRepository(self.session)
        car_listing_repo = PostgresCarListingRepository(self.session)
        

        # 3. Initialize Services
        buyer_service = BuyerService(buyer_repo)
        seller_service = SellerService(seller_repo)
        buyer_request_service = BuyerRequestService(buyer_request_repo)
        listing_service = ListingService(listing_repo)
        car_listing_service = CarListingService(car_listing_repo)

        

        
        return {
            "buyer_service": buyer_service,
            "seller_service": seller_service,
            "buyer_request_service": buyer_request_service,
            "listing_service": listing_service,
            "car_listing_service": car_listing_service,
        }

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session_gen:
            await self.session_gen.aclose()

def get_bot_deps():
    return BotDependencyManager()