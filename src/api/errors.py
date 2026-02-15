from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.domain.exceptions.buyer import BuyerAlreadyExistsError


def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(BuyerAlreadyExistsError)
    async def buyer_already_exists_handler(request: Request, exc: BuyerAlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(exc),
                "error_code": "BUYER_ALREADY_EXISTS"
            }
        )
