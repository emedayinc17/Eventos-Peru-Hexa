import os
import pytest
import requests
from datetime import date

IAM_URL = os.getenv("IAM_URL", "http://127.0.0.1:8010/iam")
CATALOGO_URL = os.getenv("CATALOGO_URL", "http://127.0.0.1:8020/catalogo")
PROVEEDORES_URL = os.getenv("PROVEEDORES_URL", "http://127.0.0.1:8030/proveedores")
CONTRATACION_URL = os.getenv("CONTRATACION_URL", "http://127.0.0.1:8040/contratacion")

CLIENT_EMAIL = os.getenv("TEST_CLIENT_EMAIL", "demo@eventos.pe")
CLIENT_PASSWORD = os.getenv("TEST_CLIENT_PASSWORD", "Admin_2025!")
SEED_PACKAGE_ID = os.getenv("SEED_PACKAGE_ID", "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0")
TEST_SERVICE_ID = os.getenv("TEST_SERVICE_ID", "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa")


def maybe_skip():
    """Skip E2E unless E2E_RUN=1 to avoid accidental network calls."""
    if os.getenv("E2E_RUN", "0") != "1":
        pytest.skip("E2E tests disabled. Set E2E_RUN=1 to enable.")


@pytest.fixture(scope="session")
def token():
    maybe_skip()
    url = f"{IAM_URL}/auth/login"
    resp = requests.post(url, json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}, timeout=10)
    assert resp.status_code == 200, f"IAM login failed {resp.status_code}: {resp.text}"
    data = resp.json()
    token = data.get("access_token") or data.get("token") or data.get("accessToken")
    assert token, "IAM response missing access token"
    return token


def test_catalogo_package_available():
    maybe_skip()
    # nota: CATALOGO_URL ya incluye el prefijo /catalogo
    url = f"{CATALOGO_URL}/v1/paquetes/{SEED_PACKAGE_ID}"
    resp = requests.get(url, timeout=10)
    # package may be absent depending on DB seed; just verify reachable or 404
    assert resp.status_code in (200, 404), f"Catalogo returned unexpected {resp.status_code}: {resp.text}"


def test_proveedores_disponibles():
    maybe_skip()
    today = date.today().isoformat()
    url = f"{PROVEEDORES_URL}/v1/proveedores/disponibles"
    params = {"servicio_id": TEST_SERVICE_ID, "fecha": today}
    resp = requests.get(url, params=params, timeout=10)
    assert resp.status_code == 200, f"Proveedores returned {resp.status_code}: {resp.text}"
    items = resp.json()
    # allow both list or object-wrapped responses
    assert isinstance(items, (list, dict)), "Proveedores response unexpected type"


def test_create_pedido_flow(token):
    maybe_skip()
    url = f"{CONTRATACION_URL}/pedidos"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "paquete_id": SEED_PACKAGE_ID,
        "tipo_evento_id": "22222222-2222-2222-2222-222222222222",
        "fecha_evento": "2025-12-25",
        "hora_inicio": "18:00:00",
        "hora_fin": "22:00:00",
        "num_personas": 100,
        "ubicacion": "Lima, Peru"
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    # If package is not present the service may return 400/404 — test allows fallback
    assert resp.status_code in (200, 201, 400, 404), f"Crear pedido unexpected {resp.status_code}: {resp.text}"
    if resp.status_code in (200, 201):
        data = resp.json()
        assert isinstance(data, dict), "Crear pedido did not return a JSON object"
        assert data.get("id") or data.get("pedido"), "Created order missing id"
        return

    # Fallback: intentar crear un pedido custom usando opciones disponibles
    # 1) listar tipos
    tipos_url = f"{CATALOGO_URL}/v1/tipos-evento"
    r_t = requests.get(tipos_url, timeout=10)
    assert r_t.status_code == 200, f"List tipos failed: {r_t.status_code} {r_t.text}"
    tipos = r_t.json()
    tipo_id = None
    if isinstance(tipos, list) and tipos:
        tipo_id = tipos[0].get("id")

    # 2) listar servicios por tipo si existe tipo
    servicio_id = TEST_SERVICE_ID
    if tipo_id:
        servicios_url = f"{CATALOGO_URL}/v1/servicios"
        r_s = requests.get(servicios_url, params={"tipo_evento_id": tipo_id}, timeout=10)
        if r_s.status_code == 200:
            servs = r_s.json()
            if isinstance(servs, list) and servs:
                servicio_id = servs[0].get("id") or servicio_id

    # 3) listar opciones para servicio
    opciones_url = f"{CATALOGO_URL}/v1/opciones-servicio"
    r_o = requests.get(opciones_url, params={"servicio_id": servicio_id}, timeout=10)
    assert r_o.status_code == 200, f"List opciones failed: {r_o.status_code} {r_o.text}"
    opciones = r_o.json()
    assert isinstance(opciones, list), "Opciones response unexpected"
    assert opciones, "No opciones available for test service"
    opcion = opciones[0]

    # 4) crear pedido custom
    payload_custom = {
        "tipo_evento_id": tipo_id or "22222222-2222-2222-2222-222222222222",
        "items": [{"opcion_servicio_id": opcion.get("id"), "cantidad": 2}],
        "fecha_evento": "2025-12-25",
        "hora_inicio": "18:00:00",
        "num_personas": 10,
        "ubicacion": "Lima"
    }
    r_create = requests.post(url, json=payload_custom, headers=headers, timeout=15)
    assert r_create.status_code in (200, 201), f"Crear pedido custom failed: {r_create.status_code} {r_create.text}"
    data2 = r_create.json()
    assert isinstance(data2, dict) and (data2.get("id") or data2.get("pedido")), "Custom order missing id"
