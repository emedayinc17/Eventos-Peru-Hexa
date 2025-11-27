import requests
import json

IAM_URL = "http://localhost:8010/iam"

def ensure_client_user():
    email = "cliente@eventos.pe"
    password = "Cliente_2025!"
    nombre = "Cliente Demo"
    
    # Try to login first to see if exists
    try:
        print(f"Checking if {email} exists...")
        resp = requests.post(f"{IAM_URL}/auth/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            print("User already exists and credentials work.")
            return
    except:
        pass

    # Register if not login success (assuming it doesn't exist or wrong pass, but we'll try register)
    print(f"Registering {email}...")
    payload = {
        "nombre": nombre,
        "email": email,
        "password": password
    }
    
    try:
        resp = requests.post(f"{IAM_URL}/auth/register", json=payload)
        if resp.status_code == 200:
            print("Client user created successfully.")
        elif resp.status_code == 409: # Conflict
             print("User exists (409).")
        else:
            print(f"Failed to create user: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_client_user()
