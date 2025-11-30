FROM python:3.12-slim

WORKDIR /app

# Install service requirements (use the service folder path like other services)
COPY services/gateway-service/requirements.txt ./services/gateway-service/requirements.txt
RUN pip install --no-cache-dir -r services/gateway-service/requirements.txt

# Copy shared libs and gateway source
COPY libs/shared ./libs/shared
COPY gateway ./gateway

# Ensure python can import shared libs
ENV PYTHONPATH=/app/libs/shared:/app/gateway

RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app/gateway

# Run as non-root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
