# created by emeday 2025 - corrected hex alignment
from fastapi import FastAPI
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router
from fastapi.middleware.cors import CORSMiddleware

settings: Settings = load_settings(service_name="proveedores-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

app = FastAPI(
    title="Proveedores Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

origins = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8080",
    "http://localhost:63343",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (primary + debug)
app.include_router(build_api_router(settings), prefix="/proveedores")
app.include_router(build_debug_router(settings), prefix="/proveedores/_debug")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s",
             settings.SERVICE_NAME,
             settings.APP_HOST,
             settings.APP_PORT)
