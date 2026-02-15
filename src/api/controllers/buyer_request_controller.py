from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.buyer_request_schema import (
    BuyerRequestCreateRequest,
    BuyerRequestUpdateRequest,
    BuyerRequestResponse,
)
from src.domain.models.buyer_request import BuyerRequest
from src.domain.services.buyer_request_service_interface import IBuyerRequestService
from src.api.dependency_injection.dependency_injection import get_buyer_request_service


buyer_request_router = APIRouter(
    prefix="/buyer-requests",
    tags=["Buyer Requests"]
)


@buyer_request_router.post("/", response_model=BuyerRequestResponse)
async def create_buyer_request(
    request: BuyerRequestCreateRequest,
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    try:
        domain_request = BuyerRequest(
            buyer_id=request.buyer_id,
            type=request.type,
            details=request.details.model_dump(),
        )
        return await service.create_request(domain_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@buyer_request_router.get("/{request_id}", response_model=BuyerRequestResponse)
async def get_buyer_request_by_id(
    request_id: UUID,
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    result = await service.get_request_by_id(request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Buyer request not found")
    return result


@buyer_request_router.get("/", response_model=List[BuyerRequestResponse])
async def get_all_buyer_requests(
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    return await service.get_all_requests()


@buyer_request_router.get("/buyer/{buyer_id}", response_model=List[BuyerRequestResponse])
async def get_requests_by_buyer(
    buyer_id: UUID,
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    return await service.get_requests_by_buyer(buyer_id)


@buyer_request_router.put("/{request_id}", response_model=BuyerRequestResponse)
async def update_buyer_request(
    request_id: UUID,
    request: BuyerRequestUpdateRequest,
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    try:
        existing = await service.get_request_by_id(request_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Buyer request not found")

        if request.type is not None:
            existing.type = request.type
        if request.details is not None:
            existing.details = request.details.model_dump()
        if request.status is not None:
            existing.status = request.status

        return await service.update_request(existing)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@buyer_request_router.delete("/", response_model=dict)
async def delete_buyer_requests(
    request_ids: List[UUID],
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    try:
        await service.delete_requests(request_ids)
        return {"deleted": len(request_ids)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@buyer_request_router.delete("/buyer/{buyer_id}", response_model=dict)
async def delete_requests_by_buyer(
    buyer_id: UUID,
    service: IBuyerRequestService = Depends(get_buyer_request_service)
):
    try:
        await service.delete_requests_by_buyer(buyer_id)
        return {"deleted_for_buyer": str(buyer_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
