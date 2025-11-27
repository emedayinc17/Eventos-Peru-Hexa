from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router

settings: Settings = load_settings(service_name="catalogo-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

docs_url = f"{settings.BASE_PATH}/docs" if getattr(settings, "BASE_PATH", "") else "/docs"
redoc_url = f"{settings.BASE_PATH}/redoc" if getattr(settings, "BASE_PATH", "") else "/redoc"

app = FastAPI(title="Catalogo Service", version="0.1.0", docs_url=docs_url, redoc_url=redoc_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (primary + debug)
app.include_router(build_api_router(settings), prefix="/catalogo")
app.include_router(build_debug_router(settings), prefix="/catalogo/_debug")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)