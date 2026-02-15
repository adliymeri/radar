from typing import List, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.domain.services.seller_service_interface import ISellerService
from src.api.dependency_injection.dependency_injection import get_seller_service
from src.domain.models.seller import Seller

seller_router = APIRouter(
    prefix="/sellers",
    tags=["Sellers"]
)

@seller_router.post("/", response_model=Seller)
async def create_seller(
    seller: Seller,
    service: ISellerService = Depends(get_seller_service)
):
    try:
        return await service.create_seller(seller)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@seller_router.get("/{seller_id}", response_model=Seller)
async def get_seller_by_id(
    seller_id: UUID,
    service: ISellerService = Depends(get_seller_service)
):
    result = await service.get_seller_by_id(seller_id)
    if not result:
        raise HTTPException(status_code=404, detail="Seller not found")
    return result

@seller_router.get("/", response_model=List[Seller])
async def get_all_sellers(
    service: ISellerService = Depends(get_seller_service)
):
    return await service.get_all_sellers()

@seller_router.put("/", response_model=Seller)
async def update_seller(
    seller: Seller,
    service: ISellerService = Depends(get_seller_service)
):
    try:
        return await service.update_seller(seller)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@seller_router.delete("/", response_model=dict)
async def delete_sellers(
    seller_ids: Union[UUID, List[UUID]],
    service: ISellerService = Depends(get_seller_service)
):
    try:
        await service.delete_sellers(seller_ids)
        if isinstance(seller_ids, list):
            count = len(seller_ids)
        else:
            count = 1
        return {"deleted": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
