from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.domain.services.real_estate_listing_service_interface import IRealEstateListingService
from src.api.dependency_injection.dependency_injection import get_real_estate_listing_service
from src.domain.models.real_estate_listing import RealEstateListing

real_estate_listing_router = APIRouter(
    prefix="/real-estate-listings",
    tags=["Real Estate Listings"]
)

@real_estate_listing_router.post("/", response_model=RealEstateListing)
async def create_real_estate_listing(
    listing: RealEstateListing,
    service: IRealEstateListingService = Depends(get_real_estate_listing_service)
):
    try:
        return await service.create_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@real_estate_listing_router.get("/{listing_id}", response_model=RealEstateListing)
async def get_real_estate_listing_by_id(
    listing_id: UUID,
    service: IRealEstateListingService = Depends(get_real_estate_listing_service)
):
    result = await service.get_listing_by_id(listing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Real estate listing not found")
    return result

@real_estate_listing_router.get("/", response_model=List[RealEstateListing])
async def get_all_real_estate_listings(
    service: IRealEstateListingService = Depends(get_real_estate_listing_service)
):
    return await service.get_all_listings()

@real_estate_listing_router.put("/", response_model=RealEstateListing)
async def update_real_estate_listing(
    listing: RealEstateListing,
    service: IRealEstateListingService = Depends(get_real_estate_listing_service)
):
    try:
        return await service.update_listing(listing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@real_estate_listing_router.delete("/", response_model=dict)
async def delete_real_estate_listings(
    listing_ids: List[UUID],
    service: IRealEstateListingService = Depends(get_real_estate_listing_service)
):
    try:
        await service.delete_listings(listing_ids)
        return {"deleted": len(listing_ids)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
