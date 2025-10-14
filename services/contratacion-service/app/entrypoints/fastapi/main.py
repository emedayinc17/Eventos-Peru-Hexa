# created by emeday 2025 - corrected hex alignment
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi  # 👈 añade esto
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router  # Asegúrate que router.py exporte esta función

settings: Settings = load_settings(service_name="contratacion-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

app = FastAPI(title="Contratacion Service", version="0.1.0", docs_url="/docs", redoc_url="/redoc")

# 👉 Esquema de seguridad Bearer para Swagger (Authorize)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    comps = schema.setdefault("components", {}).setdefault("securitySchemes", {})
    comps["HTTPBearer"] = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi  # 👈 activa el esquema en OpenAPI

# Routers (primary + debug)
app.include_router(build_api_router(settings), prefix="/contratacion")
app.include_router(build_debug_router(settings), prefix="/contratacion/_debug")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)
