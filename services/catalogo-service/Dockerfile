# Dockerfile — Catalogo Service (FastAPI + Uvicorn)
# Construir desde la raíz del repo:
#   docker build -t catalogo-service:1.0.0 -f services/catalogo-service/Dockerfile .

FROM python:3.12-slim

# ===== Configuración base de Python =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# ===== Copia de código necesario =====
# Solo copiamos la librería compartida y el servicio de catálogo
# Estructura esperada dentro del contenedor:
#   /app/libs/shared/ev_shared/...
#   /app/services/catalogo-service/app/...
COPY libs/shared ./libs/shared
COPY services/catalogo-service ./services/catalogo-service

# ===== PYTHONPATH para que funcione ev_shared y el servicio de catálogo =====
ENV PYTHONPATH=/app/libs/shared:/app/services/catalogo-service

# Entramos a la carpeta del servicio de catálogo
WORKDIR ${APP_HOME}/services/catalogo-service

# ===== Instalación de dependencias =====
# Usa el requirements.txt propio del catalogo-service
RUN pip install --no-cache-dir -r requirements.txt

# ===== Variables por defecto (se sobreescriben en K8s/Vault) =====
# Aquí solo ponemos defaults seguros; en Kubernetes las reemplazas
# con ConfigMap/Secret + Vault.
# Valores por defecto — se sobreescriben en K8s/Secrets
ENV APP_ENV=prod \
    SERVICE_NAME=catalogo-service \
    APP_HOST=0.0.0.0 \
    APP_PORT=8020 \
    VAULT_ENABLED=false

# El puerto en el que exponemos el servicio
# Puerto por defecto del servicio de catálogo
EXPOSE 8020

# ===== Comando de arranque =====
# Igual que tu run.bat pero para contenedor
CMD ["uvicorn", "app.entrypoints.fastapi.main:app", "--host", "0.0.0.0", "--port", "8020"]
