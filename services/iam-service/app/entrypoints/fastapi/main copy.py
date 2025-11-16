"""
IAM FastAPI main
----------------
- Carga Settings (.env)
- Registra router de API y de debug
Synopsis: created by emeday 2025
"""
from fastapi import FastAPI
from ev_shared import load_settings, get_logger
from .router import build_api_router
from ev_shared.http_debug import build_debug_router
from fastapi.middleware.cors import CORSMiddleware

settings = load_settings(service_name="iam-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

BASE_PATH = "/iam"   # si luego lo quieres desde settings, lo cambiamos

app = FastAPI(
    title="IAM Service",
    version="0.1.0",
    docs_url=f"{BASE_PATH}/docs",            # /iam/docs
    openapi_url=f"{BASE_PATH}/openapi.json", # /iam/openapi.json
    redoc_url=f"{BASE_PATH}/redoc",          # opcional
)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(build_debug_router(settings), prefix=BASE_PATH)
app.include_router(build_api_router(settings), prefix=BASE_PATH)

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)

@app.get(f"{BASE_PATH}/health")
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
