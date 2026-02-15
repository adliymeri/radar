from typing import Dict, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.postgres import get_session

# Repositories
from src.domain.repositories.seller_repository import SellerRepository
from src.infrastructure.repositories.postgres_seller_repository import PostgresSellerRepository

from src.domain.repositories.buyer_repository import BuyerRepository
from src.infrastructure.repositories.postgres_buyer_repository import PostgresBuyerRepository

from src.domain.repositories.listing_repository import ListingRepository
from src.infrastructure.repositories.postgres_listing_repository import PostgresListingRepository

from src.domain.repositories.buyer_request_repository import BuyerRequestRepository
from src.infrastructure.repositories.postgres_buyer_request_repository import PostgresBuyerRequestRepository

from src.domain.repositories.car_listing_repository import CarListingRepository
from src.infrastructure.repositories.postgres_car_listing_repository import PostgresCarListingRepository

from src.domain.repositories.real_estate_listing_repository import RealEstateListingRepository
from src.infrastructure.repositories.postgres_real_estate_listing_repository import PostgresRealEstateListingRepository

# Services
from src.domain.services.seller_service_interface import ISellerService
from src.application.services.seller_service import SellerService

from src.domain.services.buyer_service_interface import IBuyerService
from src.application.services.buyer_service import BuyerService

from src.domain.services.listing_service_interface import IListingService
from src.application.services.listing_service import ListingService

from src.domain.services.buyer_request_service_interface import IBuyerRequestService
from src.application.services.buyer_request_service import BuyerRequestService

from src.domain.services.car_listing_service_interface import ICarListingService
from src.application.services.car_listing_service import CarListingService

from src.domain.services.real_estate_listing_service_interface import IRealEstateListingService
from src.application.services.real_estate_listing_service import RealEstateListingService


# ================================
# Async Dependency Initialization
# ================================
async def init_dependencies(session: AsyncSession) -> Dict[str, object]:
    """
    Initialize all repositories and services with a given AsyncSession.
    This ensures proper per-request session scoping.
    """
    # Repositories
    seller_repo: SellerRepository = PostgresSellerRepository(session)
    buyer_repo: BuyerRepository = PostgresBuyerRepository(session)
    listing_repo: ListingRepository = PostgresListingRepository(session)
    buyer_request_repo: BuyerRequestRepository = PostgresBuyerRequestRepository(session)
    car_listing_repo: CarListingRepository = PostgresCarListingRepository(session)
    real_estate_repo: RealEstateListingRepository = PostgresRealEstateListingRepository(session)

    # Services
    seller_service: ISellerService = SellerService(seller_repo)
    buyer_service: IBuyerService = BuyerService(buyer_repo)
    listing_service: IListingService = ListingService(listing_repo)
    buyer_request_service: IBuyerRequestService = BuyerRequestService(buyer_request_repo)
    car_listing_service: ICarListingService = CarListingService(car_listing_repo)
    real_estate_service: IRealEstateListingService = RealEstateListingService(real_estate_repo)

    return {
        "seller_service": seller_service,
        "buyer_service": buyer_service,
        "listing_service": listing_service,
        "buyer_request_service": buyer_request_service,
        "car_listing_service": car_listing_service,
        "real_estate_service": real_estate_service,
    }


# ================================
# FastAPI Dependency Factories
# ================================
async def get_dependencies() -> AsyncGenerator[Dict[str, object], None]:
    async for session in get_session():  
        deps = await init_dependencies(session)
        yield deps

async def get_seller_service(deps: Dict[str, object] = Depends(get_dependencies)) -> ISellerService:
    return deps["seller_service"]


async def get_buyer_service(deps: Dict[str, object] = Depends(get_dependencies)) -> IBuyerService:
    return deps["buyer_service"]


async def get_listing_service(deps: Dict[str, object] = Depends(get_dependencies)) -> IListingService:
    return deps["listing_service"]


async def get_buyer_request_service(deps: Dict[str, object] = Depends(get_dependencies)) -> IBuyerRequestService:
    return deps["buyer_request_service"]


async def get_car_listing_service(deps: Dict[str, object] = Depends(get_dependencies)) -> ICarListingService:
    return deps["car_listing_service"]


async def get_real_estate_listing_service(deps: Dict[str, object] = Depends(get_dependencies)) -> IRealEstateListingService:
    return deps["real_estate_service"]
