import requests
import sys
import time
import json

# Configuration
SERVICES = {
    "iam": "http://localhost:8010/iam",
    "catalogo": "http://localhost:8020/catalogo",
    "proveedores": "http://localhost:8030/proveedores",
    "contratacion": "http://localhost:8040/contratacion"
}

CREDENTIALS = {
    "email": "demo@eventos.pe",
    "password": "Admin_2025!" # Default from bootstrap.sql
}

def print_status(service, status, message=""):
    color = "\033[92m" if status == "OK" else "\033[91m"
    reset = "\033[0m"
    print(f"[{service.upper()}] {color}{status}{reset} {message}")

def check_health(name, url):
    try:
        # Try /health endpoint first
        health_url = f"{url}/health"
        r = requests.get(health_url, timeout=2)
        if r.status_code == 200:
            print_status(name, "OK", "Health check passed")
            return True
        else:
            print_status(name, "FAIL", f"Health check returned {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status(name, "FAIL", "Connection refused (Service not running?)")
        return False
    except Exception as e:
        print_status(name, "FAIL", str(e))
        return False

def test_login(base_url):
    print(f"\nTesting Login on {base_url}...")
    login_url = f"{base_url}/auth/login"
    try:
        payload = {
            "email": CREDENTIALS["email"],
            "password": CREDENTIALS["password"]
        }
        r = requests.post(login_url, json=payload, timeout=5)
        if r.status_code == 200:
            token = r.json().get("access_token")
            print_status("LOGIN", "OK", "Authentication successful")
            return token
        elif r.status_code == 500:
             print_status("LOGIN", "FAIL", "Internal Server Error (Check Database Connection)")
             return None
        else:
            print_status("LOGIN", "FAIL", f"Status {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print_status("LOGIN", "FAIL", str(e))
        return None

def main():
    print("=== SYSTEM VALIDATION STARTED ===\n")
    
    # 1. Check Health of all services
    all_health_ok = True
    for name, url in SERVICES.items():
        if not check_health(name, url):
            all_health_ok = False
    
    if not all_health_ok:
        print("\nCRITICAL: Some services are not healthy. Aborting integration tests.")
        # We continue to try login just in case IAM is the only one working
    
    # 2. Test Login (IAM)
    token = test_login(SERVICES["iam"])
    
    if not token:
        print("\nCRITICAL: Login failed. Cannot proceed with authenticated tests.")
        sys.exit(1)
        
    print(f"\nToken received: {token[:10]}...")
    
    # 3. Test Protected Endpoints (Basic)
    headers = {"Authorization": f"Bearer {token}"}
    
    # IAM: Me
    try:
        r = requests.get(f"{SERVICES['iam']}/me", headers=headers)
        if r.status_code == 200:
            print_status("IAM /me", "OK", f"User: {r.json().get('email')}")
        else:
            print_status("IAM /me", "FAIL", str(r.status_code))
    except:
        pass

    # Catalogo: List Types
    try:
        r = requests.get(f"{SERVICES['catalogo']}/tipos-evento", headers=headers) # Guessing endpoint
        if r.status_code == 200:
            print_status("CATALOGO /tipos", "OK", f"Found {len(r.json())} types")
        elif r.status_code == 404:
             # Try another common path
             r = requests.get(f"{SERVICES['catalogo']}/public/tipos", headers=headers)
             if r.status_code == 200:
                 print_status("CATALOGO /public/tipos", "OK", f"Found {len(r.json())} types")
             else:
                 print_status("CATALOGO", "WARN", "Could not find types endpoint")
        else:
            print_status("CATALOGO", "FAIL", str(r.status_code))
    except Exception as e:
        print_status("CATALOGO", "FAIL", str(e))

    print("\n=== VALIDATION COMPLETE ===")

if __name__ == "__main__":
    main()
