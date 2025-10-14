
"""
ev_shared.http_debug
--------------------
Router de endpoints de debug comunes.
Synopsis: created by emeday 2025
"""
from fastapi import APIRouter
from sqlalchemy import text
from .config import Settings
from .db import build_engine

def build_debug_router(settings: Settings) -> APIRouter:
    router = APIRouter(tags=["_debug"])

    @router.get("/_debug/env")
    def debug_env():
        # Cuidado de no exponer secretos completos
        return {
            "service": settings.SERVICE_NAME,
            "db_host": settings.DB_HOST,
            "db_name": settings.DB_NAME,
            "app_host": settings.APP_HOST,
            "app_port": settings.APP_PORT,
        }

    @router.get("/_debug/probe")
    def probe():
        return {"ok": True, "service": settings.SERVICE_NAME}

    @router.get("/_debug/db")
    def debug_db():
        engine = build_engine(settings)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return router
