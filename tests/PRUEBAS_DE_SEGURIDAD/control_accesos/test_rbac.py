import os
import pytest
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


@pytest.mark.parametrize("path", ["/admin/users", "/admin/config"])
def test_admin_paths_forbidden_for_cliente(path, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}{path}", headers=headers)
    assert r.status_code in (401, 403)


def test_expired_token_returns_401(api_base):
    # Token manipulado (payload modificado) — este test asume que el sistema
    # valida firmas correctamente y responderá 401.
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.payload"
    headers = {"Authorization": f"Bearer {fake_token}"}
    r = requests.get(f"{api_base}/api/iam/me", headers=headers)
    assert r.status_code == 401


def test_admin_access_allowed_if_admin_creds_present(api_base):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_email or not admin_password:
        pytest.skip("No hay credenciales ADMIN en variables de entorno; omitiendo test de acceso ADMIN")

    # Obtener token de admin
    resp = requests.post(f"{api_base}/api/iam/login", json={"email": admin_email, "password": admin_password})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{api_base}/admin/users", headers=headers)
    assert r.status_code in (200, 204)
