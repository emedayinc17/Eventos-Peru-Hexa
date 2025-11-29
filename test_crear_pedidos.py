#!/usr/bin/env python3
"""Test crear pedido con los 3 casos"""
import requests
import json
from datetime import date, timedelta

# Configuración
API_BASE = "http://localhost:8000"
CLIENTE_EMAIL = "cliente@test.com"
CLIENTE_PASSWORD = "Cliente123!"

def login():
    """Autenticar y obtener token"""
    response = requests.post(
        f"{API_BASE}/api/iam/login",
        json={"email": CLIENTE_EMAIL, "password": CLIENTE_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login exitoso")
        return token
    else:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return None

def test_crear_pedido_con_paquete(token):
    """CASO 1: Pedido con paquete"""
    print("\n📦 CASO 1: Pedido con paquete")
    
    fecha_evento = (date.today() + timedelta(days=35)).isoformat()
    
    payload = {
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",  # Matrimonio
        "fecha_evento": fecha_evento,
        "num_personas": 100,
        "hora_inicio": "18:00",
        "hora_fin": "23:00",
        "ubicacion": "Lima, Perú",
        "paquete_id": "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0",  # Premium 100 pax
        "notas": "Pedido de prueba con paquete"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/api/contratacion/pedidos",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200 or response.status_code == 201

def test_crear_pedido_paquete_con_extras(token):
    """CASO 3: Pedido con paquete + servicios adicionales"""
    print("\n📦➕ CASO 3: Pedido con paquete + servicios adicionales")
    
    fecha_evento = (date.today() + timedelta(days=40)).isoformat()
    
    payload = {
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "fecha_evento": fecha_evento,
        "num_personas": 100,
        "hora_inicio": "18:00",
        "hora_fin": "23:00",
        "ubicacion": "Lima, Perú",
        "paquete_id": "bbbbbbb0-bbbb-bbbb-bbbb-bbbbbbbbbbb0",
        "servicios_adicionales": [
            {
                "opcion_servicio_id": "88888888-8888-8888-8888-888888888888",  # DJ Pro 4h
                "cantidad": 1
            }
        ],
        "notas": "Pedido con paquete + DJ adicional"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/api/contratacion/pedidos",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200 or response.status_code == 201

def test_crear_pedido_custom(token):
    """CASO 2: Pedido custom (sin paquete)"""
    print("\n🎨 CASO 2: Pedido custom (sin paquete)")
    
    fecha_evento = (date.today() + timedelta(days=45)).isoformat()
    
    payload = {
        "tipo_evento_id": "22222222-2222-2222-2222-222222222222",  # Cumpleaños
        "fecha_evento": fecha_evento,
        "num_personas": 50,
        "hora_inicio": "15:00",
        "hora_fin": "20:00",
        "ubicacion": "Lima, Perú",
        "items": [
            {
                "opcion_servicio_id": "77777777-7777-7777-7777-777777777777",  # Buffet 100 pax
                "cantidad": 1
            },
            {
                "opcion_servicio_id": "88888888-8888-8888-8888-888888888888",  # DJ Pro 4h
                "cantidad": 1
            }
        ]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/api/contratacion/pedidos",
        json=payload,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200 or response.status_code == 201

def main():
    print("=" * 60)
    print("TEST: Crear Pedidos - 3 Casos")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("\n❌ No se pudo autenticar. Verifica las credenciales.")
        return
    
    # Ejecutar tests
    resultados = []
    
    try:
        resultados.append(("Pedido con paquete", test_crear_pedido_con_paquete(token)))
    except Exception as e:
        print(f"❌ Error: {e}")
        resultados.append(("Pedido con paquete", False))
    
    try:
        resultados.append(("Pedido paquete + extras", test_crear_pedido_paquete_con_extras(token)))
    except Exception as e:
        print(f"❌ Error: {e}")
        resultados.append(("Pedido paquete + extras", False))
    
    try:
        resultados.append(("Pedido custom", test_crear_pedido_custom(token)))
    except Exception as e:
        print(f"❌ Error: {e}")
        resultados.append(("Pedido custom", False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for nombre, exito in resultados:
        estado = "✅" if exito else "❌"
        print(f"{estado} {nombre}")

if __name__ == "__main__":
    main()
