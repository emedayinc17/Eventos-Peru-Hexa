import os
import pytest
import requests
import re

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def should_run_injection_tests():
    return os.getenv("ALLOW_INJECTION_TESTS", "false").lower() in ("1", "true", "yes")


def _looks_like_sql_error(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    patterns = [
        r"syntax error",
        r"sql",
        r"mysql",
        r"pq:",
        r"sqlite3",
        r"exception",
        r"traceback",
        r"fatal",
        r"error in your sql syntax",
    ]
    return any(re.search(p, t) for p in patterns)


@pytest.mark.parametrize("payload", [
    "' OR '1'='1",
    "' OR 1=1 -- ",
    "' UNION SELECT NULL,NULL -- ",
    "' OR SLEEP(2) -- ",
    '" OR ""="',
])
def test_sql_injection_common_payloads(payload):
    """Envía payloads comunes a endpoints públicos y verifica que no se produzcan
    errores SQL ni respuestas 500. Se salta a menos que ALLOW_INJECTION_TESTS=true.
    """
    if not should_run_injection_tests():
        pytest.skip("Inyección tests deshabilitados. Set ALLOW_INJECTION_TESTS=true para ejecutar")

    endpoints = [
        {"method": "POST", "url": f"{API_BASE}/api/catalogo/tipos-evento/search", "json": {"q": payload}},
        {"method": "GET", "url": f"{API_BASE}/api/catalogo/tipos-evento", "params": {"q": payload}},
        {"method": "GET", "url": f"{API_BASE}/api/proveedores", "params": {"q": payload}},
    ]

    for ep in endpoints:
        try:
            if ep["method"] == "POST":
                r = requests.post(ep["url"], json=ep.get("json"), timeout=8)
            else:
                r = requests.get(ep["url"], params=ep.get("params"), timeout=8)
        except requests.exceptions.RequestException as exc:
            pytest.fail(f"Request failed for {ep['url']}: {exc}")

        # No debe devolver 500
        assert r.status_code != 500, f"Endpoint {ep['url']} devolvió 500 para payload {payload}"

        # El cuerpo no debe contener mensajes de error SQL ni volcado de stack
        body = ""
        try:
            body = r.text
        except Exception:
            body = ""

        assert not _looks_like_sql_error(body), f"Posible error SQL en {ep['url']} respuesta: {body[:300]}"


def test_sql_injection_blind_time_based():
    """Prueba opcional de tipo 'time-based' (muy simple). Se salta por defecto.
    No hace aserciones de explotación, solo comprueba que la API responde y no lanza 500.
    """
    if not should_run_injection_tests():
        pytest.skip("Inyección tests deshabilitados. Set ALLOW_INJECTION_TESTS=true para ejecutar")

    payload = "' OR SLEEP(1) -- "
    url = f"{API_BASE}/api/catalogo/tipos-evento/search"
    try:
        r = requests.post(url, json={"q": payload}, timeout=10)
    except requests.exceptions.RequestException as exc:
        pytest.fail(f"Request failed for {url}: {exc}")

    assert r.status_code != 500
    assert not _looks_like_sql_error(r.text)
