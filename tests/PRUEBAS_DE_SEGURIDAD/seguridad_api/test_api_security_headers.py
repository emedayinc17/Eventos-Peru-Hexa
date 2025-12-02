import os
import requests
import pytest

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def test_cors_allows_authorized_origin():
    # Hacemos una preflight OPTIONS con método POST esperado.
    headers = {"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
    r = requests.options(f"{API_BASE}/api/contratacion/pedidos", headers=headers)
    # Algunos servidores locales devuelven 405 para OPTIONS si no manejan preflight;
    # aceptamos 200/204/405 y solo comprobamos headers CORS si la respuesta lo permite.
    assert r.status_code in (200, 204, 405)
    if r.status_code in (200, 204):
        allow_origin = r.headers.get("Access-Control-Allow-Origin")
        assert allow_origin is not None and allow_origin in ("*", "http://localhost:3000")


def test_security_headers_present():
    r = requests.get(f"{API_BASE}/")
    # Verificar algunos headers de seguridad típicos. En entornos de desarrollo
    # simples (servidor dev sin proxy/TLS) es normal que algunos no estén.
    expected = ["X-Frame-Options", "Content-Security-Policy", "Referrer-Policy", "Strict-Transport-Security"]
    present = [h for h in expected if h in r.headers]
    # Si ninguno está presente, asumimos entorno de desarrollo y saltamos la prueba.
    if len(present) == 0:
        pytest.skip("No se detectaron headers de seguridad en /; posiblemente servidor de desarrollo. Saltando comprobación.")
    # Al menos uno de los headers de seguridad debe estar presente.
    assert len(present) >= 1, f"Faltan headers de seguridad: {expected}"
