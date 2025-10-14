
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

settings = load_settings(service_name="iam-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

app = FastAPI(title="IAM Service", version="0.1.0")

# Routers
app.include_router(build_debug_router(settings), prefix="/iam")
app.include_router(build_api_router(settings), prefix="/iam")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)

@app.get("/iam/health")
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
