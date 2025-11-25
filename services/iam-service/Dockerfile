# Dockerfile — IAM Service (FastAPI + Uvicorn)
# Construir desde la raíz del repo:
#   docker build -t iam-service:1.0.0 -f services/iam-service/Dockerfile .

FROM python:3.12-slim

# ===== Configuración base de Python =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# ===== Optimización de Caché: Dependencias primero =====
# Copiamos primero el requirements para aprovechar la caché de Docker
COPY services/iam-service/requirements.txt ./services/iam-service/requirements.txt

# Instalamos dependencias antes de copiar el código fuente
RUN pip install --no-cache-dir -r services/iam-service/requirements.txt

# ===== Copia de código fuente =====
# Copiamos la librería compartida y el código del servicio
COPY libs/shared ./libs/shared
COPY services/iam-service ./services/iam-service

# ===== PYTHONPATH para que funcione ev_shared y el IAM =====
ENV PYTHONPATH=/app/libs/shared:/app/services/iam-service

# ===== Seguridad: Usuario no-root =====
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

# Entramos a la carpeta del servicio IAM
WORKDIR ${APP_HOME}/services/iam-service

# ===== Variables por defecto =====
ENV APP_ENV=prod \
    SERVICE_NAME=iam-service \
    APP_HOST=0.0.0.0 \
    APP_PORT=8010 \
    VAULT_ENABLED=false

# El puerto en el que exponemos el servicio
EXPOSE 8010

# ===== Comando de arranque =====
CMD ["uvicorn", "app.entrypoints.fastapi.main:app", "--host", "0.0.0.0", "--port", "8010"]
