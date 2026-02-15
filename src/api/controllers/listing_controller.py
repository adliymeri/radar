from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.domain.services.listing_service_interface import IListingService
from src.api.dependency_injection.dependency_injection import get_listing_service
from src.domain.models.listing import Listing

listing_router = APIRouter(
    prefix="/listings",
    tags=["Listings"]
)

@listing_router.post("/", response_model=Listing)
async def create_listing(
    listing: Listing,
    service: IListingService = Depends(get_listing_service)
):
    try:
        return await service.create_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@listing_router.get("/{listing_id}", response_model=Listing)
async def get_listing_by_id(
    listing_id: UUID,
    service: IListingService = Depends(get_listing_service)
):
    result = await service.get_listing_by_id(listing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")
    return result

@listing_router.get("/", response_model=List[Listing])
async def get_all_listings(
    service: IListingService = Depends(get_listing_service)
):
    return await service.get_all_listings()

@listing_router.get("/seller/{seller_id}", response_model=List[Listing])
async def get_listings_by_seller(
    seller_id: UUID,
    service: IListingService = Depends(get_listing_service)
):
    return await service.get_listings_by_seller(seller_id)

@listing_router.put("/", response_model=Listing)
async def update_listing(
    listing: Listing,
    service: IListingService = Depends(get_listing_service)
):
    try:
        return await service.update_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@listing_router.delete("/{listing_id}", response_model=dict)
async def delete_listing(
    listing_id: UUID,
    service: IListingService = Depends(get_listing_service)
):
    try:
        await service.delete_listing(listing_id)
        return {"deleted": str(listing_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@listing_router.delete("/seller/{seller_id}", response_model=dict)
async def delete_listings_by_seller(
    seller_id: UUID,
    service: IListingService = Depends(get_listing_service)
):
    try:
        await service.delete_listings_by_seller(seller_id)
        return {"deleted_for_seller": str(seller_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
