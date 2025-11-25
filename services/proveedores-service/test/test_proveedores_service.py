import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta, date

# Configuration
BASE_URL = os.getenv("PROVEEDORES_URL", "http://127.0.0.1:8030/proveedores")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "dev-internal-token-change-in-production")

def test_health_check():
    """Verify the service is running."""
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_buscar_disponibles():
    """Verify searching for available providers."""
    today = date.today().isoformat()
    # servicio_id is likely required. Using a dummy UUID.
    # If the service validates existence, this might return 404 or empty list.
    # If it just filters, it should return 200 with empty list.
    params = {
        "servicio_id": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa", 
        "fecha": today, 
        "limit": 5
    }
    resp = requests.get(f"{BASE_URL}/v1/proveedores/disponibles", params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # We might not have data, but the call should succeed

def test_internal_hold_lifecycle():
    """Verify the internal hold lifecycle (Create -> Get -> Confirm -> Release)."""
    headers = {"X-Service-Token": INTERNAL_TOKEN}
    
    # 1. Create Hold
    start = (datetime.now() + timedelta(hours=24)).isoformat()
    end = (datetime.now() + timedelta(hours=28)).isoformat()
    correlation_id = str(uuid.uuid4())
    
    payload = {
        "proveedor_id": "cccccccc-3333-4444-5555-cccccccccccc", # Using a seed provider ID if possible, or random
        "opcion_servicio_id": "dddddddd-4444-5555-6666-dddddddddddd",
        "inicio": start,
        "fin": end,
        "ttl_min": 30,
        "correlation_id": correlation_id,
        "created_by": "test-suite"
    }
    
    # Note: If the provider doesn't exist, this might fail depending on validation.
    # However, the service might just create the hold record without checking foreign keys 
    # if it's a microservice with loose coupling (or if the DB has the seed data).
    # Let's try.
    
    resp = requests.post(f"{BASE_URL}/internal/holds", json=payload, headers=headers)
    
    # If 404 (Provider not found) or 400, we handle it. 
    # Assuming seed data exists (bootstrap.sql).
    if resp.status_code == 404:
        pytest.skip("Seed provider not found, skipping hold test")
        
    assert resp.status_code in [200, 201], f"Failed to create hold: {resp.text}"
    hold_data = resp.json()
    hold_id = hold_data["id"]
    assert hold_id
    
    # 2. Get Hold
    resp = requests.get(f"{BASE_URL}/internal/holds/{hold_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == hold_id
    
    # 3. Confirm Hold
    resp = requests.patch(f"{BASE_URL}/internal/holds/{hold_id}/confirm", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == 1 # CONFIRMED
    
    # 4. Release Hold (Clean up)
    resp = requests.delete(f"{BASE_URL}/internal/holds/{hold_id}", headers=headers)
    assert resp.status_code == 204
