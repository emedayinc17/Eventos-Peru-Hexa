#!/usr/bin/env bash
IMAGE=${1:-}

if [ -z "$IMAGE" ]; then
	echo "Uso: $0 <image:tag>"
	echo "Ejemplo: $0 my-api-image:latest"
	exit 0
fi

if ! command -v trivy >/dev/null 2>&1; then
	echo "trivy no instalado. Instalar siguiendo https://aquasecurity.github.io/trivy/"
	exit 0
fi

echo "Escaneando imagen: $IMAGE (severidades HIGH y CRITICAL)"
trivy image --severity HIGH,CRITICAL --no-progress -q $IMAGE || echo "Trivy returned non-zero status"

