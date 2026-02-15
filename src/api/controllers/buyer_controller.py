from typing import List, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.buyer_schema import BuyerCreateRequest, BuyerUpdateRequest, BuyerResponse
from src.domain.services.buyer_service_interface import IBuyerService
from src.api.dependency_injection.dependency_injection import get_buyer_service
from src.domain.models.buyer import Buyer


buyer_router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"]
)


@buyer_router.post("/", response_model=BuyerResponse)
async def create_buyer(
    payload: BuyerCreateRequest,
    service: IBuyerService = Depends(get_buyer_service)
):
    try:
        new_buyer = Buyer(
            details=payload.details.model_dump(),
            payment=payload.payment.model_dump(exclude_none=True),
        )
        return await service.create_buyer(new_buyer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@buyer_router.get("/{buyer_id}", response_model=BuyerResponse)
async def get_buyer_by_id(
    buyer_id: UUID,
    service: IBuyerService = Depends(get_buyer_service)
):
    result = await service.get_buyer_by_id(buyer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return result


@buyer_router.get("/", response_model=List[BuyerResponse])
async def get_all_buyers(
    service: IBuyerService = Depends(get_buyer_service)
):
    return await service.get_all_buyers()


@buyer_router.put("/{buyer_id}", response_model=BuyerResponse)
async def update_buyer(
    buyer_id: UUID,
    payload: BuyerUpdateRequest,
    service: IBuyerService = Depends(get_buyer_service)
):
    try:
        existing = await service.get_buyer_by_id(buyer_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Buyer not found")

        if payload.details is not None:
            existing.details = payload.details.model_dump()
        if payload.payment is not None:
            existing.payment = payload.payment.model_dump(exclude_none=True)

        return await service.update_buyer(existing)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@buyer_router.delete("/", response_model=dict)
async def delete_buyers(
    buyer_ids: Union[UUID, List[UUID]],
    service: IBuyerService = Depends(get_buyer_service)
):
    try:
        await service.delete_buyers(buyer_ids)
        count = len(buyer_ids) if isinstance(buyer_ids, list) else 1
        return {"deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))