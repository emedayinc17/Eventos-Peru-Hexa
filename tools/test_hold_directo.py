import requests
from datetime import datetime, timedelta

# Configuración
PROVEEDORES_URL = "http://127.0.0.1:8030/proveedores"
INTERNAL_TOKEN = "dev-internal-token-change-in-production"
PROVIDER_ID = "cccccccc-3333-4444-5555-cccccccccccc"
OPTION_ID = "bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb"

# Calcular fechas (45 días en el futuro, igual que el test Admin)
fecha_base = datetime.now() + timedelta(days=45)
inicio = fecha_base.replace(hour=19, minute=0, second=0, microsecond=0)
fin = inicio + timedelta(hours=4)

print(f"=== TEST DIRECTO: CREAR HOLD ===\n")
print(f"Proveedor: {PROVIDER_ID}")
print(f"Opción: {OPTION_ID}")
print(f"Inicio: {inicio.isoformat()}")
print(f"Fin: {fin.isoformat()}\n")

# Crear hold
payload = {
    "proveedor_id": PROVIDER_ID,
    "opcion_servicio_id": OPTION_ID,
    "inicio": inicio.isoformat(),
    "fin": fin.isoformat(),
    "ttl_min": 30,
    "correlation_id": f"test-direct-{datetime.now().timestamp()}",
    "created_by": "test-script"
}

headers = {
    "X-Service-Token": INTERNAL_TOKEN,
    "Content-Type": "application/json"
}

try:
    response = requests.post(
        f"{PROVEEDORES_URL}/internal/holds",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    if response.status_code == 201:
        hold_data = response.json()
        hold_id = hold_data["id"]
        print(f"✅ Hold creado exitosamente: {hold_id}")
        
        # Confirmar hold
        print(f"\n=== CONFIRMANDO HOLD {hold_id} ===\n")
        confirm_response = requests.patch(
            f"{PROVEEDORES_URL}/internal/holds/{hold_id}/confirm",
            headers=headers
        )
        
        print(f"Status: {confirm_response.status_code}")
        print(f"Response: {confirm_response.json()}")
        
        if confirm_response.status_code == 200:
            print(f"\n✅ Hold confirmado exitosamente")
        else:
            print(f"\n❌ Error confirmando hold")
    else:
        print(f"❌ Error creando hold")
        
except Exception as e:
    print(f"❌ Excepción: {type(e).__name__}: {e}")
