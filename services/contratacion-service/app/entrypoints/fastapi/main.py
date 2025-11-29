# created by emeday 2025 - corrected hex alignment
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 AÑADE ESTO
from fastapi.openapi.utils import get_openapi
from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router

settings: Settings = load_settings(service_name="contratacion-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

docs_url = f"{settings.BASE_PATH}/docs" if getattr(settings, "BASE_PATH", "") else "/docs"
redoc_url = f"{settings.BASE_PATH}/redoc" if getattr(settings, "BASE_PATH", "") else "/redoc"
openapi_url = f"{settings.BASE_PATH}/openapi.json" if getattr(settings, "BASE_PATH", "") else "/openapi.json"

app = FastAPI(title="Contratacion Service", version="0.1.0", docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url)

# 🔥 CORS ABIERTO (solo desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),      # <--- IMPORTANTE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# Register routers without an extra '/contratacion' prefix because
# the router definitions already include their full paths (e.g. '/v1/contratacion/...').
app.include_router(build_api_router(settings))
app.include_router(build_debug_router(settings))

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)