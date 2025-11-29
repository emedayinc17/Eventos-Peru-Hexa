import os
import pytest
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def should_run_injection_tests():
    return os.getenv("ALLOW_INJECTION_TESTS", "false").lower() in ("1", "true", "yes")


def test_sql_injection_safe():
    if not should_run_injection_tests():
        pytest.skip("Inyección tests deshabilitados. Set ALLOW_INJECTION_TESTS=true para ejecutar")

    payloads = ["' OR '1'='1", "' UNION SELECT username, password FROM users -- "]
    for p in payloads:
        r = requests.post(f"{API_BASE}/api/catalogo/tipos-evento/search", json={"q": p})
        # Esperar que no devuelva 500 ni datos sensibles
        assert r.status_code != 500


def test_path_traversal_protected():
    if not should_run_injection_tests():
        pytest.skip("Inyección tests deshabilitados. Set ALLOW_INJECTION_TESTS=true para ejecutar")

    # Intento simple de path traversal; la API debería bloquearlo (400/404/403)
    r = requests.get(f"{API_BASE}/static/../../etc/passwd")
    assert r.status_code in (400, 403, 404)
