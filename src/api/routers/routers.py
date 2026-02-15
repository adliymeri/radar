from fastapi import APIRouter
from src.api.controllers.seller_controller import seller_router
from src.api.controllers.buyer_controller import buyer_router
from src.api.controllers.listing_controller import listing_router
from src.api.controllers.buyer_request_controller import buyer_request_router
from src.api.controllers.car_listing_controller import car_listing_router
from src.api.controllers.real_estate_listing_controller import real_estate_listing_router

api_router = APIRouter()
api_router.include_router(seller_router)
api_router.include_router(buyer_router)
api_router.include_router(listing_router)
api_router.include_router(buyer_request_router)
api_router.include_router(car_listing_router)
api_router.include_router(real_estate_listing_router)
