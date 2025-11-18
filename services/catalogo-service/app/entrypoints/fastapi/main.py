from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router

settings: Settings = load_settings(service_name="catalogo-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

app = FastAPI(title="Catalogo Service", version="0.1.0", docs_url="/docs", redoc_url="/redoc")

# 🔥 AGREGAR CONFIGURACIÓN CORS 🔥
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # Tu frontend
        "http://127.0.0.1:8000",  # También por si usas IP directa
        "http://127.0.0.1:8020",
        "http://localhost:3000",  # Por si usas React en otro puerto
    ],
    allow_credentials=True,
    allow_methods=["*"],  # O especifica: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # O especifica los headers que necesitas
)

# Routers (primary + debug)
app.include_router(build_api_router(settings), prefix="/catalogo")
app.include_router(build_debug_router(settings), prefix="/catalogo/_debug")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)