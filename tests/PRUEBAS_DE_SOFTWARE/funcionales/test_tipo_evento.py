import requests
from datetime import date, timedelta

API_BASE = "http://localhost:8000"


def test_crud_tipo_evento():
    # login
    resp = requests.post(f"{API_BASE}/api/iam/login", json={"email": "cliente@test.com", "password": "Cliente123!"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # CREATE
    payload = {"nombre": "Test Tipo Evento", "slug": "test-tipo-evento"}
    r = requests.post(f"{API_BASE}/api/catalogo/tipos-evento", json=payload, headers=headers)
    assert r.status_code in (200, 201)
    created = r.json()
    tipo_id = created.get("id")

    # READ
    r2 = requests.get(f"{API_BASE}/api/catalogo/tipos-evento/{tipo_id}", headers=headers)
    assert r2.status_code == 200

    # LIST
    r3 = requests.get(f"{API_BASE}/api/catalogo/tipos-evento", headers=headers)
    assert r3.status_code == 200

    # DELETE (cleanup)
    r4 = requests.delete(f"{API_BASE}/api/catalogo/tipos-evento/{tipo_id}", headers=headers)
    assert r4.status_code in (200, 204, 202)
