import subprocess

# Validar y asignar rol ADMIN antes de ejecutar el test
def ensure_admin_role():
    print("Validando rol ADMIN para admin@eventos.pe ...")
    result = subprocess.run([
        'python', 'tools/validate_admin_role.py'
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("[ERROR] No se pudo validar/asignar el rol ADMIN:")
        print(result.stderr)
        exit(1)


import requests
import json

# Configuración
IAM_LOGIN_URL = "http://127.0.0.1:8010/iam/auth/login"
API_URL = "http://127.0.0.1:8020/catalogo/v1/admin/paquetes/pkg-conc-0002"
ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Evoluti0n"  # Password actualizado según indicación

# Payload de ejemplo para el update
update_payload = {
    "nombre": "Paquete Concierto Plus (modificado)",
    "moneda": "PEN",
    "items": [
        {"opcion_servicio_id": "op-sonido-pro", "cantidad": 1},
        {"opcion_servicio_id": "op-luz-basic", "cantidad": 1},
        {"opcion_servicio_id": "op-seg-std", "cantidad": 1}
    ]
}

def get_token():
    login_payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    print(f"Autenticando admin en {IAM_LOGIN_URL} ...")
    resp = requests.post(IAM_LOGIN_URL, json=login_payload)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print("Token obtenido.")
        return token
    else:
        print(f"Error autenticando: {resp.status_code}", resp.text)
        return None

def update_paquete(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    print(f"Enviando PUT a {API_URL} ...")
    resp = requests.put(API_URL, headers=headers, data=json.dumps(update_payload))
    print(f"Status: {resp.status_code}")
    print("Response:", resp.text)

def main():
    ensure_admin_role()
    token = get_token()
    if token:
        update_paquete(token)
    else:
        print("No se pudo obtener token, abortando test.")

if __name__ == "__main__":
    main()
