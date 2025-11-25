# Dockerfile — Proveedores Service (FastAPI + Uvicorn)
# Construir desde la raíz del repo:
#   docker build -t proveedores-service:1.0.0 -f services/proveedores-service/Dockerfile .

FROM python:3.12-slim

# ===== Configuración base de Python =====
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# ===== Optimización de Caché: Dependencias primero =====
# Copiamos primero el requirements para aprovechar la caché de Docker
COPY services/proveedores-service/requirements.txt ./services/proveedores-service/requirements.txt

# Instalamos dependencias antes de copiar el código fuente
RUN pip install --no-cache-dir -r services/proveedores-service/requirements.txt

# ===== Copia de código fuente =====
# Copiamos la librería compartida y el código del servicio
COPY libs/shared ./libs/shared
COPY services/proveedores-service ./services/proveedores-service

# ===== PYTHONPATH para que funcione ev_shared y el servicio =====
ENV PYTHONPATH=/app/libs/shared:/app/services/proveedores-service

# ===== Seguridad: Usuario no-root =====
RUN addgroup --system appgroup && adduser --system --group appuser
USER appuser

# Entramos a la carpeta del servicio
WORKDIR ${APP_HOME}/services/proveedores-service

# ===== Variables por defecto =====
ENV APP_ENV=prod \
    SERVICE_NAME=proveedores-service \
    APP_HOST=0.0.0.0 \
    APP_PORT=8030 \
    VAULT_ENABLED=false

# El puerto en el que exponemos el servicio
EXPOSE 8030

# ===== Comando de arranque =====
CMD ["uvicorn", "app.entrypoints.fastapi.main:app", "--host", "0.0.0.0", "--port", "8030"]
