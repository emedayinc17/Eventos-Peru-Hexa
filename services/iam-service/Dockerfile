# Dockerfile — IAM Service (FastAPI + Uvicorn)
# Construir desde la raíz del repo:
#   docker build -t iam-service:1.0.0 -f services/iam-service/Dockerfile .

FROM python:3.12-slim

# ===== Configuración base de Python =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# ===== Copia de código necesario =====
# Solo copiamos la librería compartida y el servicio IAM
# Estructura esperada:
#   /app/libs/shared/ev_shared/...
#   /app/services/iam-service/app/...
COPY libs/shared ./libs/shared
COPY services/iam-service ./services/iam-service

# ===== PYTHONPATH para que funcione ev_shared y el IAM =====
ENV PYTHONPATH=/app/libs/shared:/app/services/iam-service

# Entramos a la carpeta del servicio IAM
WORKDIR ${APP_HOME}/services/iam-service

# ===== Instalación de dependencias =====
# Usa el requirements.txt propio del iam-service
RUN pip install --no-cache-dir -r requirements.txt

# ===== Variables por defecto (se sobreescriben en K8s/Vault) =====
# Aquí solo ponemos defaults seguros; en Kubernetes las reemplazas
# con ConfigMap/Secret + Vault.
ENV APP_ENV=prod \
    SERVICE_NAME=iam-service \
    APP_HOST=0.0.0.0 \
    APP_PORT=8010 \
    VAULT_ENABLED=false

# El puerto en el que exponemos el servicio
EXPOSE 8010

# ===== Comando de arranque =====
# Igual que tu run.bat pero para contenedor
CMD ["uvicorn", "app.entrypoints.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
