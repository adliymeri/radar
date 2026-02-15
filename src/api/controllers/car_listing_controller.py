from typing import List, Union, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.domain.services.car_listing_service_interface import ICarListingService
from src.api.dependency_injection.dependency_injection import get_car_listing_service
from src.domain.models.car_listing import CarListing

car_listing_router = APIRouter(
    prefix="/car-listings",
    tags=["Car Listings"]
)

@car_listing_router.post("/", response_model=CarListing)
async def create_car_listing(
    listing: CarListing,
    service: ICarListingService = Depends(get_car_listing_service)
):
    try:
        return await service.create_car_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@car_listing_router.get("/{listing_id}", response_model=CarListing)
async def get_car_listing_by_id(
    listing_id: UUID,
    service: ICarListingService = Depends(get_car_listing_service)
):
    result = await service.get_car_listing_by_id(listing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Car listing not found")
    return result

@car_listing_router.get("/", response_model=List[CarListing])
async def get_all_car_listings(
    service: ICarListingService = Depends(get_car_listing_service)
):
    return await service.get_all_car_listings()

@car_listing_router.put("/", response_model=CarListing)
async def update_car_listing(
    listing: CarListing,
    service: ICarListingService = Depends(get_car_listing_service)
):
    try:
        return await service.update_car_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@car_listing_router.delete("/", response_model=dict)
async def delete_car_listings(
    listing_ids: Union[UUID, List[UUID]],
    service: ICarListingService = Depends(get_car_listing_service)
):
    try:
        await service.delete_car_listings(listing_ids)
        if isinstance(listing_ids, list):
            count = len(listing_ids)
        else:
            count = 1
        return {"deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
