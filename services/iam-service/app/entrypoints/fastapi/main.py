from fastapi import FastAPI
from ev_shared import load_settings, get_logger
from .router import build_api_router
from ev_shared.http_debug import build_debug_router
from fastapi.middleware.cors import CORSMiddleware

settings = load_settings(service_name="iam-service")
log = get_logger(__name__, service_name=settings.SERVICE_NAME)

# 👉 Deja FastAPI SIN docs_url ni openapi_url personalizados
#    Así SIEMPRE expone:
#    - /docs
#    - /openapi.json
app = FastAPI(
    title="IAM Service",
    version="0.1.0",
)

# origins = settings.CORS_ORIGINS.split(",")
origins = ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
print(f"DEBUG CORS ORIGINS HARDCODED: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👉 Los routers con prefix /iam (como tenías cuando todo funcionaba)
app.include_router(build_debug_router(settings), prefix="/iam")
app.include_router(build_api_router(settings), prefix="/iam")

@app.on_event("startup")
async def on_startup():
    log.info("Starting %s on %s:%s",
             settings.SERVICE_NAME,
             settings.APP_HOST,
             settings.APP_PORT)

# Health externo
@app.get("/iam/health")
def health_iam():
    return {"status": "ok", "service": settings.SERVICE_NAME}
