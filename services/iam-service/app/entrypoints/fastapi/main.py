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

# 👇 Sin BASE_PATH aquí: las rutas internas serán "/auth/login", "/health", etc.
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
# 👇 IMPORTANTE: sin prefix="/iam". El "/iam" lo añade el Ingress sólo por fuera
app.include_router(build_debug_router(settings))       # quedará /_debug/env
app.include_router(build_api_router(settings))         # quedará /auth/login, /admin/...

@app.on_event("startup")
async def on_startup():
    log.info(
        "Starting %s on %s:%s",
        settings.SERVICE_NAME,
        settings.APP_HOST,
        settings.APP_PORT,
    )

# Health "externo" (si lo estabas usando)
@app.get("/iam/health")
def health_iam():
    return {"status": "ok", "service": settings.SERVICE_NAME}
    
# 👇 Health sin "/iam"
@app.get("/health")
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
