import pytest
import requests
import os
import uuid
from datetime import datetime

# Configuration
BASE_URL = os.getenv("CONTRATACION_URL", "http://127.0.0.1:8040/contratacion")
IAM_URL = os.getenv("IAM_URL", "http://127.0.0.1:8010/iam")

# Test Data
CLIENT_EMAIL = "demo@eventos.pe"
CLIENT_PASSWORD = "Admin_2025!"
ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Admin_2025!"

@pytest.fixture(scope="session")
def client_token():
    """Get a valid JWT token for a client user."""
    try:
        resp = requests.post(f"{IAM_URL}/auth/login", json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD})
        resp.raise_for_status()
        return resp.json()["access_token"]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to login as client: {e}")

@pytest.fixture(scope="session")
def admin_token():
    """Get a valid JWT token for an admin user."""
    try:
        resp = requests.post(f"{IAM_URL}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        resp.raise_for_status()
        return resp.json()["access_token"]
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to login as admin: {e}")

@pytest.fixture(scope="session")
def created_order(client_token):
    """Create an order and return its ID."""
    headers = {"Authorization": f"Bearer {client_token}"}
    payload = {
        "paquete_id": "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0",
        "tipo_evento_id": "22222222-2222-2222-2222-222222222222",
        "fecha_evento": "2025-12-25",
        "hora_inicio": "18:00:00",
        "hora_fin": "22:00:00",
        "num_personas": 100,
        "ubicacion": "Lima, Peru"
    }
    resp = requests.post(f"{BASE_URL}/pedidos", json=payload, headers=headers)
    assert resp.status_code in [200, 201], f"Failed to create order: {resp.text}"
    data = resp.json()
    assert "id" in data
    return data["id"]

def test_health_check():
    """Verify the service is running."""
    # Assuming there is a health check or root endpoint, if not we can skip or check a public endpoint
    # Based on previous context, maybe just check if the service responds
    pass # Contratacion service might not have a dedicated health endpoint exposed at root without auth in the same way, 
         # but let's assume it's up if we can run other tests. 
         # Or we can try a GET to a known endpoint that might return 401, proving it's up.
    resp = requests.get(f"{BASE_URL}/pedidos/mios") # Should be 401
    assert resp.status_code in [401, 403, 200], "Service is not reachable or behaving unexpectedly"

def test_create_order(created_order):
    """Verify order creation (covered by fixture, but good to have explicit test)."""
    assert created_order is not None

def test_get_order_details(client_token, created_order):
    """Verify retrieving order details."""
    headers = {"Authorization": f"Bearer {client_token}"}
    resp = requests.get(f"{BASE_URL}/pedidos/{created_order}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # Structure might be {"pedido": {...}, "items": [...]} or just the order object
    # Based on previous script: resp.json()
    # And previous script checked data["pedido"]["status"] in verification
    # Let's just check ID match
    if "pedido" in data:
        assert data["pedido"]["id"] == created_order
    else:
        assert data["id"] == created_order

def test_list_my_orders(client_token, created_order):
    """Verify the created order appears in the user's list."""
    headers = {"Authorization": f"Bearer {client_token}"}
    resp = requests.get(f"{BASE_URL}/pedidos/mios", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", []) if isinstance(data, dict) else data
    found = any(item["id"] == created_order for item in items)
    assert found, "Created order not found in 'my orders' list"

def test_admin_list_orders(admin_token, created_order):
    """Verify admin can see the order."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/admin/pedidos", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", []) if isinstance(data, dict) else data
    found = any(item["id"] == created_order for item in items)
    assert found, "Created order not found in admin list"

def test_admin_update_status(admin_token, client_token, created_order):
    """Verify admin can update order status and client sees the change."""
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_client = {"Authorization": f"Bearer {client_token}"}
    
    # Update to CONFIRMADO (1)
    new_status = 1
    resp = requests.patch(
        f"{BASE_URL}/admin/pedidos/{created_order}", 
        json={"estado": new_status}, 
        headers=headers_admin
    )
    assert resp.status_code == 200, f"Admin failed to update status: {resp.text}"
    
    # Verify as client
    resp = requests.get(f"{BASE_URL}/pedidos/{created_order}", headers=headers_client)
    assert resp.status_code == 200
    data = resp.json()
    
    # Handle response structure variation
    current_status = data["pedido"]["status"] if "pedido" in data else data["status"]
    assert current_status == new_status, f"Status not updated. Expected {new_status}, got {current_status}"
