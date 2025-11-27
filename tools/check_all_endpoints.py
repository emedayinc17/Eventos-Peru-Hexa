"""Smoke test: comprobar endpoints de los 4 servicios.

Uso:
  python tools/check_all_endpoints.py

Lee variables de entorno para URLs y credenciales:
  IAM_URL, CATALOGO_URL, PROVEEDORES_URL, CONTRATACION_URL
  TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD

Imprime un resumen con método, ruta y status code. Intenta autenticación Bearer cuando procede.
"""
import os
import requests
import json
from datetime import date

IAM_URL = os.getenv("IAM_URL", "http://127.0.0.1:8010/iam")
CATALOGO_URL = os.getenv("CATALOGO_URL", "http://127.0.0.1:8020/catalogo")
PROVEEDORES_URL = os.getenv("PROVEEDORES_URL", "http://127.0.0.1:8030/proveedores")
CONTRATACION_URL = os.getenv("CONTRATACION_URL", "http://127.0.0.1:8040/contratacion")

CLIENT_EMAIL = os.getenv("TEST_CLIENT_EMAIL", "demo@eventos.pe")
CLIENT_PASSWORD = os.getenv("TEST_CLIENT_PASSWORD", "Admin_2025!")


def try_login():
    url = f"{IAM_URL}/auth/login"
    try:
        resp = requests.post(url, json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}, timeout=8)
    except Exception as e:
        return None, f"conn_error: {e}"
    if resp.status_code != 200:
        return None, f"status_{resp.status_code}"
    try:
        data = resp.json()
        token = data.get("access_token") or data.get("token") or data.get("accessToken")
        return token, None
    except Exception as e:
        return None, f"json_error: {e}"


def main():
    print("Iniciando smoke test de endpoints...\n")
    token, err = try_login()
    if token:
        print(f"IAM login OK, token len={len(token)}")
    else:
        print(f"IAM login falló: {err}")

    headers_auth = {"Authorization": f"Bearer {token}"} if token else {}

    checks = [
        ("GET", f"{IAM_URL}/health", False, None, None),
        ("POST", f"{IAM_URL}/auth/login", False, {"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}, None),
        ("GET", f"{IAM_URL}/me", True, None, None),

        ("GET", f"{CATALOGO_URL}/health", False, None, None),
        ("GET", f"{CATALOGO_URL}/v1/tipos-evento", False, None, None),
        ("GET", f"{CATALOGO_URL}/v1/servicios", False, None, {"tipo_evento_id": None}),
        ("GET", f"{CATALOGO_URL}/v1/opciones-servicio", False, None, {"servicio_id": None}),
        ("GET", f"{CATALOGO_URL}/v1/paquetes", False, None, None),

        ("GET", f"{PROVEEDORES_URL}/health", False, None, None),
        ("GET", f"{PROVEEDORES_URL}/v1/proveedores/disponibles", False, None, {"servicio_id": None, "fecha": date.today().isoformat()}),
        ("POST", f"{PROVEEDORES_URL}/internal/holds", True, {"pedido_id": "test", "item_id": "i1", "proveedor_id": "p1", "inicio": "2025-12-25T18:00:00", "fin": "2025-12-25T20:00:00"}, None),

        ("GET", f"{CONTRATACION_URL}/health", False, None, None),
        ("POST", f"{CONTRATACION_URL}/pedidos", True, {"paquete_id": None}, None),
        ("GET", f"{CONTRATACION_URL}/pedidos/mios", True, None, None),
    ]

    results = []
    for method, url, need_auth, data, params in checks:
        h = headers_auth.copy() if need_auth else {}
        try:
            if method == "GET":
                r = requests.get(url, headers=h, params=params, timeout=10)
            elif method == "POST":
                r = requests.post(url, headers=h, json=data, params=params, timeout=12)
            else:
                r = None
            status = r.status_code if r is not None else 'NA'
            try:
                body = r.json() if r is not None else None
            except Exception:
                body = r.text if r is not None else None
            print(f"{method} {url} -> {status}")
            results.append((method, url, status, body))
        except Exception as e:
            print(f"{method} {url} -> ERROR {e}")
            results.append((method, url, 'error', str(e)))

    # resumen simple
    print("\nResumen:")
    for m, u, s, b in results:
        print(f"- {m} {u} => {s}")


if __name__ == '__main__':
    main()
