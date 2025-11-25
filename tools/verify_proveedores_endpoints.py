"""
Simple script de verificación para endpoints del servicio Proveedores.
Uso: configurar variables de entorno opcionales y ejecutar:
  python tools\verify_proveedores_endpoints.py

Lo que verifica:
- GET /proveedores/health
- GET /proveedores/v1/proveedores/disponibles?servicio_id=...&fecha=...
- POST /proveedores/internal/holds (requiere X-Service-Token)
- PATCH /proveedores/internal/holds/{hold_id}/confirm
- DELETE /proveedores/internal/holds/{hold_id}

Nota: este script asume que los servicios están corriendo localmente.
"""

import os
import sys
import httpx
from datetime import datetime, timedelta

PROVEEDORES_BASE = os.getenv('PROVEEDORES_SERVICE_URL', 'http://127.0.0.1:8030/proveedores')
INTERNAL_TOKEN = os.getenv('INTERNAL_SERVICE_TOKEN', 'dev-internal-token-change-in-production')

SAMPLE_SERVICIO_ID = os.getenv('SAMPLE_SERVICIO_ID', '77777777-7777-7777-7777-777777777777')
SAMPLE_FECHA = os.getenv('SAMPLE_FECHA', datetime.now().date().isoformat())

print('Proveedores base:', PROVEEDORES_BASE)

client = httpx.Client(timeout=10.0)

try:
    print('1) Health...')
    r = client.get(f"{PROVEEDORES_BASE}/health")
    print(r.status_code, r.text)

    print('\n2) Buscar disponibles (public)')
    params = {'servicio_id': SAMPLE_SERVICIO_ID, 'fecha': SAMPLE_FECHA, 'limit': 5}
    r = client.get(f"{PROVEEDORES_BASE}/v1/proveedores/disponibles", params=params)
    print(r.status_code)
    try:
        data = r.json()
        print('Encontrados:', len(data))
        if data:
            print('Primer proveedor:', data[0])
    except Exception as e:
        print('No JSON:', r.text)

    print('\n3) Crear hold (interno)')
    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=4)
    hold_payload = {
        'proveedor_id': os.getenv('SAMPLE_PROVEEDOR_ID', 'ccccccc0-cccc-cccc-cccc-ccccccccccc0'),
        'opcion_servicio_id': SAMPLE_SERVICIO_ID,
        'inicio': start.isoformat(),
        'fin': end.isoformat(),
        'ttl_min': 30,
        'correlation_id': f"test-{int(datetime.now().timestamp())}",
        'created_by': 'verify-script'
    }
    headers = {'X-Service-Token': INTERNAL_TOKEN, 'Content-Type': 'application/json'}
    r = client.post(f"{PROVEEDORES_BASE}/internal/holds", json=hold_payload, headers=headers)
    print('status', r.status_code)
    if r.status_code == 201:
        hold = r.json()
        print('Hold creado:', hold)

        hold_id = hold.get('id')
        print('\n4) Confirmar hold')
        r = client.patch(f"{PROVEEDORES_BASE}/internal/holds/{hold_id}/confirm", headers={'X-Service-Token': INTERNAL_TOKEN})
        print('confirm status', r.status_code, r.text)

        print('\n5) Liberar hold')
        r = client.delete(f"{PROVEEDORES_BASE}/internal/holds/{hold_id}", headers={'X-Service-Token': INTERNAL_TOKEN})
        print('liberar status', r.status_code)
    else:
        print('No se pudo crear hold:', r.status_code, r.text)

except Exception as e:
    print('Error durante verificación:', e)
finally:
    client.close()

print('\nVerificación completada. Ajusta env vars si es necesario.')
