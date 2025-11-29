"""
Run automated validation for admin orders page and routing.

Steps performed:
 - Authenticate against IAM (`/api/iam/auth/login`) using admin credentials
 - Check health endpoints (Vite proxy -> Gateway, Gateway, Contratacion service)
 - Request admin orders list via Vite proxy, Gateway and direct service
 - Print concise diagnostics (status, server header, body snippet)

Usage (PowerShell):
    python .\tools\run_admin_validation.py

Environment variables (optional):
    TEST_ADMIN_EMAIL (default: 'admin@eventos.pe')
    TEST_ADMIN_PASSWORD (default: 'Evoluti0n')

Requires `requests` package: `pip install requests`
"""
from __future__ import annotations
import json
import os
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
    # print full body if short, else first 1200 chars
    text = resp.text or ''
    if len(text) <= 1200:
        print('Body:\n', text)
    else:
        print('Body (first 1200 chars):\n', text[:1200])


def do_get(url: str, token: str | None = None, timeout: float = 8.0) -> Tuple[int, str]:
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    print(f"\nGET {url}")
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        pretty_print(r)
        return r.status_code, r.text
    except requests.RequestException as exc:
        print('ERROR:', repr(exc))
        return 0, str(exc)


def do_post(url: str, payload: dict, token: str | None = None, timeout: float = 10.0) -> Tuple[int, str]:
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    print(f"\nPOST {url}")
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
        pretty_print(r)
        return r.status_code, r.text
    except requests.RequestException as exc:
        print('ERROR:', repr(exc))
        return 0, str(exc)


def login(iam_login_url: str, email: str, password: str) -> str | None:
    print(f"Logging in as {email} -> {iam_login_url}")
    try:
        resp = requests.post(iam_login_url, json={"email": email, "password": password}, timeout=8.0)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} -> {resp.text}")
            return None
        data = resp.json()
        token = data.get('access_token') or data.get('token') or data.get('accessToken')
        if not token:
            print('Login response did not contain access_token field. Response JSON:')
            print(json.dumps(data, indent=2))
            return None
        print('Login succeeded, token acquired (length {})'.format(len(token)))
        return token
    except requests.RequestException as exc:
        print('Login request error:', repr(exc))
        return None


def main() -> int:
    admin_email = os.environ.get('TEST_ADMIN_EMAIL', 'admin@eventos.pe')
    admin_password = os.environ.get('TEST_ADMIN_PASSWORD', 'Evoluti0n')

    # URLs
    vite_base = 'http://localhost:5173'
    gateway_base = 'http://localhost:8000'
    contratacion_base = 'http://localhost:8040'

    iam_login_url = f"{vite_base}/api/iam/auth/login"

    token = login(iam_login_url, admin_email, admin_password)
    if not token:
        print('\nERROR: Unable to login as admin; aborting further checks.')
        return 2

    # Health checks
    print('\n== Health checks ==')
    do_get(f"{vite_base}/api/health", token=None)
    do_get(f"{gateway_base}/health", token=None)
    do_get(f"{contratacion_base}/health", token=None)
    do_get(f"{contratacion_base}/v1/contratacion/health", token=None)

    # Admin pedidos list via different paths
    print('\n== Admin pedidos list checks ==')
    paths = [
        (f"{vite_base}/api/contratacion/admin/pedidos", 'Vite proxy -> admin/pedidos'),
        (f"{gateway_base}/api/contratacion/admin/pedidos", 'Gateway -> admin/pedidos'),
        (f"{contratacion_base}/admin/pedidos", 'Service direct -> /admin/pedidos'),
        (f"{contratacion_base}/v1/contratacion/admin/pedidos", 'Service direct -> /v1/contratacion/admin/pedidos'),
    ]

    results = {}
    for url, label in paths:
        print(f"\n-- {label} ({url}) --")
        status, body = do_get(url, token=token)
        results[url] = (status, body)

    # Optionally attempt a POST create attempt (non-admin create endpoint)
    print('\n== Optional: attempt client create pedido (will likely require more fields) ==')
    test_payload = {
        "fecha_evento": "2025-12-15",
        "hora_inicio": "18:00:00",
        "hora_fin": "20:00:00",
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "ubicacion": "Pruebas automáticas",
        "items": [
            {"nombre_servicio": "Servicio prueba", "cantidad": 1, "precio_unitario": 100.0, "tipo_item": "SERVICIO"}
        ]
    }

    # POST via Gateway (will be proxied and must include Authorization)
    post_status, post_body = do_post(f"{gateway_base}/api/contratacion/pedidos", test_payload, token=token)

    print('\nSummary:')
    for url, (s, b) in results.items():
        print(f"{url} -> {s}")
    print(f"POST to {gateway_base}/api/contratacion/pedidos -> {post_status}")

    # Decide return code: 0 if at least one admin list returned 200, else 3
    ok = any(s == 200 for s, _ in results.values())
    if ok:
        print('\nValidation finished: some admin endpoints returned 200. Check output above for details.')
        return 0
    else:
        print('\nValidation failed: no admin list endpoint returned 200. See details above.')
        return 3


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
