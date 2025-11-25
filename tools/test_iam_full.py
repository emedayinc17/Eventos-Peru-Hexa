import requests
import uuid
import sys

IAM_URL = "http://127.0.0.1:8010/iam"

def print_step(msg):
    print(f"\n--- {msg} ---")

def test_health():
    print_step("Testing Health Check")
    try:
        r = requests.get(f"{IAM_URL}/health")
        if r.status_code == 200:
            print("SUCCESS: Health check passed.")
        else:
            print(f"FAILURE: Health check failed. Status: {r.status_code}, Body: {r.text}")
            sys.exit(1)
    except Exception as e:
        print(f"FAILURE: Connection error: {e}")
        sys.exit(1)

def test_login(email, password, expected_role=None):
    print_step(f"Testing Login for {email}")
    payload = {"email": email, "password": password}
    r = requests.post(f"{IAM_URL}/auth/login", json=payload)
    
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token")
        role = data.get("role")
        print(f"SUCCESS: Login successful. Role: {role}")
        
        if expected_role and role != expected_role:
            print(f"WARNING: Expected role {expected_role}, got {role}")
            
        return token
    else:
        print(f"FAILURE: Login failed. Status: {r.status_code}, Body: {r.text}")
        return None

def test_me(token):
    print_step("Testing /me Endpoint")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{IAM_URL}/me", headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        print(f"SUCCESS: Got profile for {data.get('email')} ({data.get('role')})")
    else:
        print(f"FAILURE: /me failed. Status: {r.status_code}, Body: {r.text}")

def test_admin_users(token):
    print_step("Testing Admin List Users")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{IAM_URL}/admin/users", headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        print(f"SUCCESS: Retrieved {len(data)} users.")
    elif r.status_code == 403:
        print("SUCCESS: Access denied as expected (if testing non-admin).")
    else:
        print(f"FAILURE: Admin list failed. Status: {r.status_code}, Body: {r.text}")

def test_register():
    print_step("Testing Registration")
    random_id = str(uuid.uuid4())[:8]
    email = f"test_{random_id}@eventos.pe"
    password = "TestPassword123!"
    payload = {
        "email": email,
        "password": password,
        "nombre": f"Test User {random_id}",
        "telefono": "+51 900 000 000"
    }
    
    r = requests.post(f"{IAM_URL}/auth/register", json=payload)
    
    if r.status_code == 200:
        print(f"SUCCESS: Registered user {email}")
        return email, password
    else:
        print(f"FAILURE: Registration failed. Status: {r.status_code}, Body: {r.text}")
        return None, None

def main():
    test_health()
    
    # 1. Test Admin Login
    admin_token = test_login("admin@eventos.pe", "Admin_2025!", expected_role="ADMIN")
    if admin_token:
        test_me(admin_token)
        test_admin_users(admin_token)
    
    # 2. Test Client Login (Demo)
    client_token = test_login("demo@eventos.pe", "Admin_2025!", expected_role="CLIENTE")
    if client_token:
        test_me(client_token)
        # Verify client cannot access admin endpoint
        print_step("Testing Client Access to Admin Endpoint")
        headers = {"Authorization": f"Bearer {client_token}"}
        r = requests.get(f"{IAM_URL}/admin/users", headers=headers)
        if r.status_code == 403:
            print("SUCCESS: Client correctly denied access to admin endpoint.")
        else:
            print(f"FAILURE: Client should get 403, got {r.status_code}")

    # 3. Test Registration
    new_email, new_pass = test_register()
    if new_email:
        # Login with new user
        test_login(new_email, new_pass, expected_role="CLIENTE")

if __name__ == "__main__":
    main()
