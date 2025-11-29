import requests
from datetime import date, timedelta

API_BASE = "http://localhost:8000"


def login():
    resp = requests.post(f"{API_BASE}/api/iam/login", json={"email": "cliente@test.com", "password": "Cliente123!"})
    resp.raise_for_status()
    return resp.json().get("access_token")


def test_e2e_crear_pedido():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}

    # 1) Crear tipo de evento
    tipo_payload = {"nombre": "E2E Tipo Evento", "slug": "e2e-tipo"}
    r_tipo = requests.post(f"{API_BASE}/api/catalogo/tipos-evento", json=tipo_payload, headers=headers)
    assert r_tipo.status_code in (200, 201)
    tipo_id = r_tipo.json().get("id")

    # 2) Crear paquete mínimo (si endpoint disponible)
    paquete_payload = {"nombre": "E2E Paquete", "tipo_evento_id": tipo_id, "items": []}
    r_paquete = requests.post(f"{API_BASE}/api/proveedores/paquetes", json=paquete_payload, headers=headers)
    assert r_paquete.status_code in (200, 201)
    paquete_id = r_paquete.json().get("id")

    # 3) Crear pedido usando paquete
    fecha_evento = (date.today() + timedelta(days=60)).isoformat()
    pedido_payload = {
        "tipo_evento_id": tipo_id,
        "fecha_evento": fecha_evento,
        "num_personas": 20,
        "paquete_id": paquete_id,
    }
    r_pedido = requests.post(f"{API_BASE}/api/contratacion/pedidos", json=pedido_payload, headers=headers)
    assert r_pedido.status_code in (200, 201)
