import requests
import json

# Login
login_url = "http://localhost:8010/iam/auth/login"
login_payload = {"email": "cliente_test@eventos.pe", "password": "Client_2025!"}

print("=== LOGIN ===")
r = requests.post(login_url, json=login_payload)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    token = r.json()["access_token"]
    print(f"Token obtenido: {token[:50]}...")
else:
    print(f"Error: {r.text}")
    exit(1)

# Crear pedido
headers = {"Authorization": f"Bearer {token}"}
pedido_url = "http://localhost:8040/contratacion/pedidos"
pedido_payload = {
    "tipo_evento_id": "44444444-1111-1111-1111-111111111111",  # Quinceañeros del script2
    "items": [
        {
            "opcion_servicio_id": "77777777-7777-7777-7777-777777777777",  # Del bootstrap
            "cantidad": 1
        }
    ],
    "fecha_evento": "2025-12-25",
    "hora_inicio": "18:00",
    "hora_fin": "23:00",
    "num_personas": 50,
    "ubicacion": "Lima Test"
}

print("\n=== CREAR PEDIDO ===")
print(f"Payload: {json.dumps(pedido_payload, indent=2)}")
r = requests.post(pedido_url, json=pedido_payload, headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code in [200, 201]:
    print("\n✅ PEDIDO CREADO EXITOSAMENTE!")
    print(json.dumps(r.json(), indent=2))
else:
    print("\n❌ ERROR AL CREAR PEDIDO")
