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
API_URL = "http://127.0.0.1:8020/catalogo/v1/admin/paquetes"
ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Evoluti0n"  # Password actualizado según indicación

# Payload de ejemplo para el create
create_payload = {
    "codigo": "PKG-AUTO-001",
    "nombre": "Paquete Automático Test",
    "moneda": "PEN",
    "items": [
        {"opcion_servicio_id": "op-cater-100", "cantidad": 1},
        {"opcion_servicio_id": "op-dj-4h", "cantidad": 1}
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


def create_paquete(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    print(f"Enviando POST a {API_URL} ...")
    resp = requests.post(API_URL, headers=headers, data=json.dumps(create_payload))
    print(f"Status: {resp.status_code}")
    print("Response:", resp.text)


def main():
    ensure_admin_role()
    token = get_token()
    if token:
        create_paquete(token)
    else:
        print("No se pudo obtener token, abortando test.")

if __name__ == "__main__":
    main()
