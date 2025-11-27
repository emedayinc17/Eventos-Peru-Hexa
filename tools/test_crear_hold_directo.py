#!/usr/bin/env python3
"""Test directo del endpoint interno de crear hold"""
import requests
import json

# Token de servicio
SERVICE_TOKEN = "dev-internal-token-change-in-production"

# Crear hold directamente
url = "http://127.0.0.1:8030/proveedores/internal/holds"
payload = {
    "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc",
    "opcion_servicio_id": "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb",
    "inicio": "2026-01-11T19:00:00",
    "fin": "2026-01-11T23:00:00",
    "ttl_min": 30,
    "correlation_id": "test-direct-hold-12345",
    "created_by": "test-script"
}

print("=== CREAR HOLD (directo) ===")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

response = requests.post(
    url,
    json=payload,
    headers={"X-Service-Token": SERVICE_TOKEN}
)

print(f"Status: {response.status_code}")
try:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except:
    print(f"Response: {response.text}")
