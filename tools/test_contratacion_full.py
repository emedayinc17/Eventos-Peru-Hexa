import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8040/contratacion"
IAM_URL = "http://127.0.0.1:8010/iam"

def login(email, password):
    try:
        resp = requests.post(f"{IAM_URL}/auth/login", json={"email": email, "password": password})
        if not resp.ok:
            print(f"Login failed for {email}: {resp.text}")
            sys.exit(1)
        return resp.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
        sys.exit(1)

def test_client_flow():
    print("--- Testing Client Flow ---")
    token = login("demo@eventos.pe", "Admin_2025!")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Order
    print("1. Creating Order...")
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
    if not resp.ok:
        print(f"FAILED: Create order. {resp.status_code} {resp.text}")
        return None, None
    
    order_data = resp.json()
    order_id = order_data["id"]
    print(f"SUCCESS: Order created. ID: {order_id}")
    
    # 2. Get Order Details
    print(f"2. Getting Order Details for {order_id}...")
    resp = requests.get(f"{BASE_URL}/pedidos/{order_id}", headers=headers)
    if not resp.ok:
        print(f"FAILED: Get order. {resp.status_code} {resp.text}")
    else:
        print("SUCCESS: Got order details.")
        
    # 3. List My Orders
    print("3. Listing My Orders...")
    resp = requests.get(f"{BASE_URL}/pedidos/mios", headers=headers)
    if not resp.ok:
        print(f"FAILED: List my orders. {resp.status_code} {resp.text}")
    else:
        items = resp.json().get("items", [])
        found = any(item["id"] == order_id for item in items)
        if found:
            print("SUCCESS: Order found in list.")
        else:
            print("FAILED: Order not found in list.")
            
    return order_id, token

def test_admin_flow(order_id, client_token):
    print("\n--- Testing Admin Flow ---")
    token = login("admin@eventos.pe", "Admin_2025!")
    headers = {"Authorization": f"Bearer {token}"}
    client_headers = {"Authorization": f"Bearer {client_token}"}
    
    # 1. List All Orders
    print("1. Listing All Orders (Admin)...")
    resp = requests.get(f"{BASE_URL}/admin/pedidos", headers=headers)
    if not resp.ok:
        print(f"FAILED: List all orders. {resp.status_code} {resp.text}")
    else:
        # The response might be a list or a dict with 'items'
        data = resp.json()
        items = data if isinstance(data, list) else data.get("items", [])
        print(f"SUCCESS: Retrieved {len(items)} orders")
        found = any(item["id"] == order_id for item in items)
        if found:
            print("SUCCESS: Order found in admin list.")
        else:
            print("FAILED: Order not found in admin list.")

    # 2. Update Status
    print(f"2. Updating Status for {order_id}...")
    # Status 1 = CONFIRMADO (assuming 0 is PENDING)
    resp = requests.patch(f"{BASE_URL}/admin/pedidos/{order_id}", json={"estado": 1}, headers=headers)
    if not resp.ok:
        print(f"FAILED: Update status. {resp.status_code} {resp.text}")
    else:
        print("SUCCESS: Status updated.")
        
    # Verify status update using CLIENT token
    print("Verifying status update (as client)...")
    resp = requests.get(f"{BASE_URL}/pedidos/{order_id}", headers=client_headers)
    if resp.ok:
        # Response structure is {"pedido": {...}, "items": [...]}
        data = resp.json()
        status = data["pedido"]["status"]
        if status == 1:
            print("SUCCESS: Status verified as 1.")
        else:
            print(f"FAILED: Status verification. Got {status}")
    else:
        print(f"FAILED: Status verification. {resp.status_code} {resp.text}")

if __name__ == "__main__":
    order_id, client_token = test_client_flow()
    if order_id and client_token:
        try:
            test_admin_flow(order_id, client_token)
        except Exception as e:
            print(f"Admin flow skipped or failed: {e}")
