# Proveedores Service - Hexagonal Architecture
from fastapi import FastAPI
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router_public import build_public_router
from .router_internal import build_internal_router
from fastapi.middleware.cors import CORSMiddleware

settings: Settings = load_settings(service_name="proveedores-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

docs_url = f"{settings.BASE_PATH}/docs" if getattr(settings, "BASE_PATH", "") else "/docs"
redoc_url = f"{settings.BASE_PATH}/redoc" if getattr(settings, "BASE_PATH", "") else "/redoc"
openapi_url = f"{settings.BASE_PATH}/openapi.json" if getattr(settings, "BASE_PATH", "") else "/openapi.json"

app = FastAPI(
    title="Proveedores Service",
    version="0.1.0",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

origins = settings.CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (public + internal + debug)
app.include_router(build_public_router(settings), prefix="/proveedores")
app.include_router(build_internal_router(settings), prefix="/proveedores")
app.include_router(build_debug_router(settings), prefix="/proveedores")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s",
             settings.SERVICE_NAME,
             settings.APP_HOST,
             settings.APP_PORT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.entrypoints.fastapi.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
