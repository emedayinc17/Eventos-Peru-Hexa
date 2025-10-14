
"""
ev_shared.config
-----------------
Carga de configuración para servicios (local .env y listo para extender a Vault).
Synopsis: created by emeday 2025
"""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

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

    # Vault (placeholder para despliegue)
    VAULT_ENABLED: bool = Field(default=False)
    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

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
