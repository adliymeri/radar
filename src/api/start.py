from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from src.api.errors import setup_exception_handlers
from src.api.routers.routers import api_router
from src.infrastructure.db.postgres import shutdown_db
from src.infrastructure.utils.logs import setup_logging, app_log

setup_logging("api_logs")
app_log.info("Initializing API server...")

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_log.info("API lifespan started")  # logs when app starts
    yield
    app_log.info("Shutting down Postgres connections for API server")
    await shutdown_db()

app = FastAPI(
    title="Radar",
    description="APIs for Radar",
    openapi_url="/swagger/openapi.json",
    docs_url="/swagger/docs",
    redoc_url="/swagger/redoc",
    version="0.1.0",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(api_router, prefix="/api")

app_log.info("FastAPI app created successfully")

if __name__ == "__main__":
    app_log.info("Starting Uvicorn server on http://0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        log_level="info"
    )
