import requests
import json
import random
import string

# Config
IAM_URL = "http://localhost:8010/iam"

def test_register():
    # Generate random user
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"test_user_{rand_suffix}@example.com"
    password = "SecretPassword123!"
    nombre = f"Test User {rand_suffix}"

    print(f"Intentando registrar usuario: {email}")

    # Payload matching what we fixed in auth-service.js
    # Note: The frontend sends 'nombre', 'email', 'password'
    payload = {
        "nombre": nombre,
        "email": email,
        "password": password
    }

    try:
        print(f"Enviando POST a {IAM_URL}/auth/register...")
        response = requests.post(f"{IAM_URL}/auth/register", json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ ¡Registro EXITOSO!")
            print(f"ID Usuario: {data.get('id')}")
            print(f"Email: {data.get('email')}")
            return True
        else:
            print("\n❌ Registro FALLIDO")
            return False
    except Exception as e:
        print(f"\n❌ Error de Conexión: {e}")
        print("Asegúrate de que el servicio IAM esté corriendo en el puerto 8010.")
        return False

if __name__ == "__main__":
    test_register()
