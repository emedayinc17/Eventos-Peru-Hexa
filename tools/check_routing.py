"""
Temporary script to validate local routing and endpoints for the project.

Usage (PowerShell):
    python .\tools\check_routing.py

The script performs GET checks against the Vite proxy, Gateway and Contratacion
service, then attempts POSTs to the pedidos endpoints (via Vite, Gateway and
direct to service) and prints concise diagnostics for each request.

This is safe read-only (GET) plus a non-destructive POST with a minimal payload
that should either return 401 (auth) or 404/200 depending on routing. It uses
the `requests` package. If not installed, run `pip install requests`.
"""
from __future__ import annotations
import json
import sys
from typing import Tuple

try:
    import requests
except Exception:
    print("Missing dependency: install with `pip install requests`")
    sys.exit(2)


def pretty_print(resp: requests.Response) -> None:
    server = resp.headers.get('server') or resp.headers.get('Server') or ''
    print(f"Status: {resp.status_code}    Server: {server}")
    text = resp.text or ''
    # print a short slice of body to avoid flooding the console
    print('Body:', text[:1000])


def check_get(url: str, timeout: float = 5.0) -> Tuple[int, str]:
    print(f"\nGET {url}")
    try:
        r = requests.get(url, timeout=timeout)
        pretty_print(r)
        return r.status_code, r.text
    except requests.RequestException as exc:
        print("ERROR:", repr(exc))
        return 0, str(exc)


def check_post(url: str, payload: dict, timeout: float = 8.0) -> Tuple[int, str]:
    print(f"\nPOST {url}")
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
        pretty_print(r)
        return r.status_code, r.text
    except requests.RequestException as exc:
        print("ERROR:", repr(exc))
        return 0, str(exc)


def main() -> None:
    # URLs to test
    urls_get = [
        ('Vite proxy (GET)', 'http://localhost:5173/api/health'),
        ('Gateway (GET)', 'http://localhost:8000/health'),
        ('Contratacion root (GET)', 'http://localhost:8040/health'),
        ('Contratacion v1 (GET)', 'http://localhost:8040/v1/contratacion/health'),
    ]

    for label, url in urls_get:
        print(f"== {label} ==")
        check_get(url)

    # Minimal payload for pedidos - aligns with current backend schema
    payload = {
        "fecha_evento": "2025-12-01",
        "hora_inicio": "18:00:00",
        "hora_fin": "20:00:00",
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "ubicacion": "Local de pruebas",
        "items": [
            {"nombre_servicio": "Servicio prueba", "cantidad": 1, "precio_unitario": 100.0, "tipo_item": "SERVICIO"}
        ]
    }

    post_targets = [
        ('Vite proxy -> pedidos', 'http://localhost:5173/api/contratacion/pedidos'),
        ('Gateway -> pedidos', 'http://localhost:8000/api/contratacion/pedidos'),
        ('Contratacion root -> pedidos', 'http://localhost:8040/pedidos'),
        ('Contratacion v1 -> pedidos', 'http://localhost:8040/v1/contratacion/pedidos'),
        ('Service direct maybe alternative path -> /contratacion/pedidos', 'http://localhost:8040/contratacion/pedidos'),
    ]

    for label, url in post_targets:
        print(f"== {label} ==")
        check_post(url, payload)

    print('\nDone. If you see 404 from some targets and 200/401 from others, note which URL returned which status and copy the full response body.')


if __name__ == '__main__':
    main()
