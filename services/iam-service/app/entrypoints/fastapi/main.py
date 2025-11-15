
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

app = FastAPI(title="IAM Service", version="0.1.0")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # en dev puedes usar ["*"] si quieres
    allow_credentials=True,
    allow_methods=["*"],            # habilita POST/GET/OPTIONS...
    allow_headers=["*"],            # habilita Content-Type, Authorization, etc.
)

# Routers
app.include_router(build_debug_router(settings), prefix="/iam")
app.include_router(build_api_router(settings), prefix="/iam")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)

@app.get("/iam/health")
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
