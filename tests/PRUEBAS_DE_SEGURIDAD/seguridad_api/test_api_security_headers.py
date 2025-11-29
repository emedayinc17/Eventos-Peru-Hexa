import os
import requests
import pytest

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def test_cors_allows_authorized_origin():
    headers = {"Origin": "http://localhost:3000"}
    r = requests.options(f"{API_BASE}/api/contratacion/pedidos", headers=headers)
    # Puede devolver 200 o 204 dependiendo del servidor
    assert r.status_code in (200, 204)
    assert "Access-Control-Allow-Origin" in r.headers and r.headers.get("Access-Control-Allow-Origin") in ("*", "http://localhost:3000")


def test_security_headers_present():
    r = requests.get(f"{API_BASE}/")
    # Verificar algunos headers de seguridad típicos
    expected = ["X-Frame-Options", "Content-Security-Policy", "Referrer-Policy", "Strict-Transport-Security"]
    missing = [h for h in expected if h not in r.headers]
    # Falla si faltan headers críticos
    assert len(missing) == 0, f"Faltan headers de seguridad: {missing}"
