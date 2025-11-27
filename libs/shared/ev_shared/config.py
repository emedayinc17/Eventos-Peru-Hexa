
"""
ev_shared.config
-----------------
Carga de configuración para servicios (local .env y listo para extender a Vault).
Synopsis: created by emeday 2025
"""
from __future__ import annotations
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

# Determine env_file path for Settings (opt-in).
# If EV_SETTINGS_ENV_FILE is set, use it; otherwise default to '.env'.
_env_file = os.getenv("EV_SETTINGS_ENV_FILE", ".env")

class Settings(BaseSettings):
    # Identidad del servicio
    SERVICE_NAME: str = Field(default="service")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8010)

    # DB (MySQL)
    DB_HOST: str = Field(default="127.0.0.1")
    DB_PORT: int = Field(default=3306)
    DB_USER: str = Field(default="root")
    DB_PASS: str = Field(default="")
    DB_NAME: str = Field(default="mysql")

    # JWT
    JWT_SECRET: str = Field(default="dev-secret")
    JWT_ALG: str = Field(default="HS256")
    JWT_EXPIRES_MIN: int = Field(default=60)

    # Service-to-Service Communication
    INTERNAL_SERVICE_TOKEN: str = Field(default="dev-internal-token-change-in-production")
    PROVEEDORES_SERVICE_URL: str = Field(default="http://127.0.0.1:8030/proveedores")
    CATALOGO_SERVICE_URL: str = Field(default="http://127.0.0.1:8020/catalogo")
    CONTRATACION_SERVICE_URL: str = Field(default="http://127.0.0.1:8040/contratacion")

    # Vault (placeholder para despliegue)
    VAULT_ENABLED: bool = Field(default=False)
    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500", description="Comma separated list of allowed origins")

    model_config = SettingsConfigDict(env_file=_env_file, env_file_encoding='utf-8', extra='ignore')

    @property
    def DATABASE_URL(self) -> str:
        # mysql+pymysql://user:pass@host:port/dbname
        from urllib.parse import quote_plus
        p = quote_plus(self.DB_PASS or "")
        return f"mysql+pymysql://{self.DB_USER}:{p}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

def load_settings(service_name: str|None=None) -> Settings:
    s = Settings()
    if service_name:
        s.SERVICE_NAME = service_name
    return s
