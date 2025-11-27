#!/usr/bin/env python3
"""Integration smoke test across IAM -> Catalogo -> Proveedores -> Contratacion

Usage: python tools/integration_test.py

It logs into IAM, captures a bearer token and performs a few requests against
Catalogo, Proveedores and Contratacion using the token.
"""
import os
import sys
import requests
from datetime import date

IAM_URL = os.getenv("IAM_URL", "http://127.0.0.1:8010/iam")
CATALOGO_URL = os.getenv("CATALOGO_URL", "http://127.0.0.1:8020/catalogo")
PROVEEDORES_URL = os.getenv("PROVEEDORES_URL", "http://127.0.0.1:8030/proveedores")
CONTRATACION_URL = os.getenv("CONTRATACION_URL", "http://127.0.0.1:8040/contratacion")

# Credentials used by the repo tests
CLIENT_EMAIL = os.getenv("TEST_CLIENT_EMAIL", "demo@eventos.pe")
CLIENT_PASSWORD = os.getenv("TEST_CLIENT_PASSWORD", "Admin_2025!")

SEED_PACKAGE_ID = os.getenv("SEED_PACKAGE_ID", "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0")
TEST_SERVICE_ID = os.getenv("TEST_SERVICE_ID", "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa")


def fail(msg: str, code: int = 1):
    print("ERROR:", msg)
    sys.exit(code)


def login(email: str, password: str) -> str:
    url = f"{IAM_URL}/auth/login"
    print(f"-> Logging into IAM at {url} as {email}")
    resp = requests.post(url, json={"email": email, "password": password}, timeout=10)
    if resp.status_code != 200:
        fail(f"IAM login failed ({resp.status_code}): {resp.text}")
    data = resp.json()
    token = data.get("access_token") or data.get("token") or data.get("accessToken")
    if not token:
        fail("IAM login response missing access_token")
    print("-> Obtained access token (truncated):", token[:32])
    return token


def check_catalogo(token: str):
    url = f"{CATALOGO_URL}/v1/catalogo/paquetes/{SEED_PACKAGE_ID}"
    print(f"-> GET Catalogo paquete {SEED_PACKAGE_ID} -> {url}")
    resp = requests.get(url, timeout=10)
    if resp.status_code == 404:
        print("  - Package not found (404) — seed DB may be missing")
        return False, resp.text
    if resp.status_code != 200:
        return False, f"Catalogo returned {resp.status_code}: {resp.text}"
    print("  - Catalogo paquete OK; keys:", list(resp.json().keys()))
    return True, resp.json()


def check_proveedores():
    today = date.today().isoformat()
    url = f"{PROVEEDORES_URL}/v1/proveedores/disponibles"
    params = {"servicio_id": TEST_SERVICE_ID, "fecha": today}
    print(f"-> GET Proveedores disponibles for servicio {TEST_SERVICE_ID} on {today}")
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return False, f"Proveedores returned {resp.status_code}: {resp.text}"
    items = resp.json()
    print(f"  - Found {len(items)} proveedores (first id):", (items[0]["id"] if items else "<none>"))
    return True, items


def create_order(token: str):
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
    print(f"-> POST Contratacion crear pedido -> {url}")
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code not in (200, 201):
        return False, f"Crear pedido failed {resp.status_code}: {resp.text}"
    print("  - Pedido creado; response keys:", list(resp.json().keys()))
    return True, resp.json()


def create_order_custom(token: str, items: list):
    """Intenta crear un pedido custom usando items (cuando paquete no está disponible)."""
    url = f"{CONTRATACION_URL}/pedidos"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # hora_inicio/hora_fin deben estar en formato HH:MM o ISO dependiendo del servicio
    payload = {
        "tipo_evento_id": "22222222-2222-2222-2222-222222222222",
        "items": items,
        "fecha_evento": "2025-12-25",
        "hora_inicio": "18:00:00",
        "hora_fin": "22:00:00",
        "num_personas": 100,
        "ubicacion": "Lima, Peru"
    }

    print(f"-> POST Contratacion crear pedido (custom) -> {url}")
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    if resp.status_code not in (200, 201):
        return False, f"Crear pedido custom failed {resp.status_code}: {resp.text}"
    print("  - Pedido custom creado; response keys:", list(resp.json().keys()))
    return True, resp.json()


def main():
    print("Integration smoke test — IAM -> Catalogo -> Proveedores -> Contratacion")
    print(f"Using endpoints: IAM={IAM_URL}, CATALOGO={CATALOGO_URL}, PROVEEDORES={PROVEEDORES_URL}, CONTRATACION={CONTRATACION_URL}")

    token = login(CLIENT_EMAIL, CLIENT_PASSWORD)

    ok, cat = check_catalogo(token)
    if not ok:
        print("Catalogo check failed:", cat)
    else:
        print("Catalogo paquete OK")

    okp, prov = check_proveedores()
    if not okp:
        print("Proveedores check failed:", prov)
    else:
        print("Proveedores OK")

    okc, order = create_order(token)
    if not okc:
        print("Create order failed:", order)
        # Si falla por paquete no encontrado, intentar crear pedido custom usando items del paquete obtenido
        if isinstance(cat, dict) and cat.get("items"):
            print("Intentando fallback: crear pedido custom usando items del paquete obtenido...")
            items_payload = []
            for it in cat.get("items", []):
                opcion_id = it.get("opcion_servicio_id") or it.get("opcion_id") or it.get("opcion")
                if not opcion_id:
                    continue
                items_payload.append({"opcion_servicio_id": opcion_id, "cantidad": it.get("cantidad", 1)})

            if items_payload:
                okc2, order2 = create_order_custom(token, items_payload)
                if not okc2:
                    print("Fallback create order failed:", order2)
                    sys.exit(3)
                else:
                    print("Fallback create order OK; id:", order2.get("id") or order2.get("pedido", {}).get("id"))
            else:
                print("No se encontraron items válidos para el fallback.")
                sys.exit(2)
        else:
            sys.exit(2)
    else:
        print("Create order OK; id:", order.get("id") or order.get("pedido", {}).get("id"))

    print("All steps completed. If any step failed, check DB seeds and service availability.")


if __name__ == '__main__':
    main()
