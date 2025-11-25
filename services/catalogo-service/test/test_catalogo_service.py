import pytest
import requests
import os

# Configuration
# The service mounts the router at /catalogo
BASE_URL = os.getenv("CATALOGO_URL", "http://127.0.0.1:8020/catalogo")

# Test Data
# Using the seed package ID from bootstrap.sql mentioned in validate_frontend_endpoints.py
SEED_PACKAGE_ID = "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0"

def test_health_check():
    """Verify the service is running."""
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_list_tipos_evento():
    """Verify listing event types."""
    resp = requests.get(f"{BASE_URL}/v1/catalogo/tipos")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Assuming there's at least one type seeded
    if len(data) > 0:
        assert "id" in data[0]
        assert "nombre" in data[0]

def test_list_servicios():
    """Verify listing services."""
    resp = requests.get(f"{BASE_URL}/v1/catalogo/servicios")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "nombre" in data[0]

def test_list_paquetes():
    """Verify listing packages."""
    resp = requests.get(f"{BASE_URL}/v1/catalogo/paquetes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "nombre" in data[0]
        assert "monto_total" in data[0]

def test_get_paquete_detalle():
    """Verify retrieving package details."""
    resp = requests.get(f"{BASE_URL}/v1/catalogo/paquetes/{SEED_PACKAGE_ID}")
    # If the seed data is not present, this might fail with 404, 
    # but in a controlled test env it should be there.
    if resp.status_code == 404:
        pytest.skip(f"Seed package {SEED_PACKAGE_ID} not found")
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == SEED_PACKAGE_ID
    assert "items" in data
    assert isinstance(data["items"], list)

def test_list_opciones_requires_service_id():
    """Verify listing options requires service_id."""
    resp = requests.get(f"{BASE_URL}/v1/catalogo/opciones")
    # FastAPI usually returns 422 for missing required query params
    assert resp.status_code == 422

def test_list_opciones_valid():
    """Verify listing options for a valid service."""
    # First get a service ID
    resp_serv = requests.get(f"{BASE_URL}/v1/catalogo/servicios")
    if resp_serv.status_code == 200 and len(resp_serv.json()) > 0:
        service_id = resp_serv.json()[0]["id"]
        resp = requests.get(f"{BASE_URL}/v1/catalogo/opciones?servicio_id={service_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
    else:
        pytest.skip("No services available to test options")
