import requests
import pytest

API_BASE = "http://localhost:8000"


def test_list_tipos_evento(token, api_base):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{api_base}/api/catalogo/tipos-evento", headers=headers)
    assert r.status_code == 200


def test_list_proveedores(token, api_base):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{api_base}/api/proveedores", headers=headers)
    assert r.status_code == 200
