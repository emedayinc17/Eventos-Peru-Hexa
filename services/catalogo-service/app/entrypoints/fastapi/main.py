from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Ensure `ev_shared` package from repo `libs/shared` is on sys.path when running locally
repo_file = Path(__file__).resolve()
for parent in repo_file.parents:
    candidate = parent / 'libs' / 'shared'
    if candidate.exists():
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ev_shared.config import load_settings, Settings
from ev_shared.logger import get_logger
from ev_shared.http_debug import build_debug_router
from .router import build_api_router
from fastapi.responses import RedirectResponse, JSONResponse
import sqlalchemy

settings: Settings = load_settings(service_name="catalogo-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

docs_url = f"{settings.BASE_PATH}/docs" if getattr(settings, "BASE_PATH", "") else "/docs"
redoc_url = f"{settings.BASE_PATH}/redoc" if getattr(settings, "BASE_PATH", "") else "/redoc"
openapi_url = f"{settings.BASE_PATH}/openapi.json" if getattr(settings, "BASE_PATH", "") else "/openapi.json"

app = FastAPI(title="Catalogo Service", version="0.1.0", docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url)


# Map DB operational errors to a clearer HTTP response
@app.exception_handler(sqlalchemy.exc.OperationalError)
async def _handle_db_operational_error(request, exc: sqlalchemy.exc.OperationalError):
    # Do not expose full SQL or credentials; return sanitized message
    msg = str(exc).split('\n')[0]
    return JSONResponse(status_code=503, content={"code": "DB_ERROR", "message": "Database operational error: " + msg})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (primary + debug)
app.include_router(build_api_router(settings), prefix="/catalogo")
app.include_router(build_debug_router(settings), prefix="/catalogo")

@app.get("/catalogo/health")
def health_catalogo():
    return {"status": "ok", "service": settings.SERVICE_NAME}


# Si `BASE_PATH` está configurado (p. ej. "/catalogo"), exponer atajos
# desde la raíz para facilitar acceso a docs/openapi:
if getattr(settings, "BASE_PATH", ""):
    base = settings.BASE_PATH.rstrip('/')

    @app.get("/docs")
    def _redirect_docs():
        return RedirectResponse(url=f"{base}/docs")

    @app.get("/redoc")
    def _redirect_redoc():
        return RedirectResponse(url=f"{base}/redoc")

    @app.get("/openapi.json")
    def _redirect_openapi():
        return RedirectResponse(url=f"{base}/openapi.json")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s", settings.SERVICE_NAME, settings.APP_HOST, settings.APP_PORT)