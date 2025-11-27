import requests
from datetime import datetime, timedelta
import json

# Configuración
IAM_URL = "http://127.0.0.1:8010/iam"
CONTRATACION_URL = "http://127.0.0.1:8040/contratacion"
ADMIN_EMAIL = "admin@eventos.pe"
ADMIN_PASSWORD = "Evoluti0n"
PROVIDER_ID = "cccccccc-3333-4444-5555-cccccccccccc"
OPTION_ID = "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb"

# 1. Login admin
print("=== LOGIN ADMIN ===\n")
login_response = requests.post(
    f"{IAM_URL}/auth/login",
    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
)
print(f"Status: {login_response.status_code}")
if login_response.status_code != 200:
    print(f"Error: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token obtenido\n")

# 2. Crear pedido de prueba
print("=== CREAR PEDIDO ===\n")
fecha_evento = (datetime.now() + timedelta(days=45)).date().isoformat()
pedido_payload = {
    "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
    "fecha_evento": fecha_evento,
    "hora_inicio": "19:00:00",
    "hora_fin": "23:00:00",
    "num_personas": 100,
    "ubicacion": "Lima Centro",
    "items": [
        {
            "opcion_servicio_id": OPTION_ID,
            "nombre_servicio": "Opcion Prueba Verificacion",
            "cantidad": 1,
            "precio_unitario": 1500.00
        }
    ]
}

pedido_response = requests.post(
    f"{CONTRATACION_URL}/pedidos",
    json=pedido_payload,
    headers=headers
)
print(f"Status: {pedido_response.status_code}")
if pedido_response.status_code != 201:
    print(f"Error: {pedido_response.text}")
    exit(1)

pedido = pedido_response.json()
pedido_id = pedido["id"]
print(f"✅ Pedido creado: {pedido_id}")
print(f"Items: {pedido.get('items', 'N/A')}\n")

# 3. Obtener items del pedido
print("=== OBTENER ITEMS DEL PEDIDO ===\n")
items_response = requests.get(
    f"{CONTRATACION_URL}/admin/pedidos/{pedido_id}",
    headers=headers
)
print(f"Status: {items_response.status_code}")
if items_response.status_code != 200:
    print(f"Error: {items_response.text}")
    exit(1)

pedido_detalle = items_response.json()
print(f"Pedido detalle: {json.dumps(pedido_detalle, indent=2, ensure_ascii=False)}\n")

if not pedido_detalle.get("items"):
    print("❌ Pedido sin items")
    exit(1)

item_id = pedido_detalle["items"][0]["id"] if isinstance(pedido_detalle["items"], list) else None
if not item_id:
    print("❌ No se pudo obtener item_id")
    exit(1)

print(f"✅ Item ID: {item_id}\n")

# 4. Cambiar a APROBADO
print("=== CAMBIAR A APROBADO ===\n")
# Primero COTIZADO
cotizado_response = requests.patch(
    f"{CONTRATACION_URL}/admin/pedidos/{pedido_id}",
    json={"estado": 1},  # COTIZADO
    headers=headers
)
print(f"COTIZADO Status: {cotizado_response.status_code}")

# Luego APROBADO
estado_response = requests.patch(
    f"{CONTRATACION_URL}/admin/pedidos/{pedido_id}",
    json={"estado": 2},  # APROBADO
    headers=headers
)
print(f"APROBADO Status: {estado_response.status_code}")
if estado_response.status_code == 200:
    print(f"✅ Pedido APROBADO\n")
else:
    print(f"❌ Error cambiando estado: {estado_response.text}\n")
    exit(1)

# 5. Asignar proveedor
print("=== ASIGNAR PROVEEDOR ===\n")
inicio = datetime.fromisoformat(fecha_evento + "T19:00:00")
fin = inicio + timedelta(hours=4)

asignar_payload = {
    "proveedor_id": PROVIDER_ID,
    "item_pedido_id": item_id,
    "opcion_servicio_id": OPTION_ID,
    "fecha_inicio": inicio.isoformat(),
    "fecha_fin": fin.isoformat(),
    "monto": 1500.0,
    "notas": "Test asignación"
}

print(f"Payload: {json.dumps(asignar_payload, indent=2)}\n")

asignar_response = requests.post(
    f"{CONTRATACION_URL}/admin/pedidos/{pedido_id}/asignar-proveedor",
    json=asignar_payload,
    headers=headers
)

print(f"Status: {asignar_response.status_code}")
print(f"Response: {asignar_response.text}\n")

if asignar_response.status_code == 200:
    print(f"✅ Proveedor asignado exitosamente")
    print(f"Reserva: {json.dumps(asignar_response.json(), indent=2, ensure_ascii=False)}")
else:
    print(f"❌ Error asignando proveedor")
    try:
        print(f"Detalle: {json.dumps(asignar_response.json(), indent=2, ensure_ascii=False)}")
    except:
        pass
