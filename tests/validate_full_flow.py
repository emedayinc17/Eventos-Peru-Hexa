import requests
import json
import sys
import time

# --- CONFIGURACIÓN ---
BASE_URLS = {
    "iam": "http://localhost:8010/iam",
    "catalogo": "http://localhost:8020/catalogo",
    "proveedores": "http://localhost:8030/proveedores",
    "contratacion": "http://localhost:8040/contratacion"
}

# Credenciales
ADMIN_USER = {"email": "demo@eventos.pe", "password": "Admin_2025!"}
# Usaremos el script2.sql para obtener un cliente aleatorio o crearemos uno si falla
CLIENT_USER = {"email": "cliente_test@eventos.pe", "password": "Client_2025!", "nombre": "Cliente Test"}

def print_header(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def print_step(msg):
    print(f" -> {msg}")

def print_result(status, msg):
    color = "\033[92m" if status == "OK" else "\033[91m"
    reset = "\033[0m"
    print(f"    [{color}{status}{reset}] {msg}")

def login(email, password, role_name):
    url = f"{BASE_URLS['iam']}/auth/login"
    try:
        r = requests.post(url, json={"email": email, "password": password})
        if r.status_code == 200:
            token = r.json().get("access_token")
            print_result("OK", f"Login exitoso como {role_name} ({email})")
            return token
        else:
            print_result("FAIL", f"Login fallido como {role_name}: {r.status_code} - {r.text}")
            return None
    except Exception as e:
        print_result("FAIL", f"Error de conexión en login: {e}")
        return None

def register_client_if_needed():
    # Intentar login primero
    token = login(CLIENT_USER["email"], CLIENT_USER["password"], "CLIENTE (Check)")
    if token:
        return token

    # Si falla, registrar
    print_step("Registrando nuevo cliente de prueba...")
    url = f"{BASE_URLS['iam']}/auth/register"
    payload = {
        "email": CLIENT_USER["email"],
        "password": CLIENT_USER["password"],
        "nombre": CLIENT_USER["nombre"],
        "telefono": "+51 999 888 777"
    }
    r = requests.post(url, json=payload)
    if r.status_code in [200, 201]:
        print_result("OK", "Cliente registrado correctamente")
        return login(CLIENT_USER["email"], CLIENT_USER["password"], "CLIENTE")
    else:
        print_result("FAIL", f"No se pudo registrar cliente: {r.text}")
        return None

# --- FLUJOS DE PRUEBA ---

def test_admin_flow(token):
    headers = {"Authorization": f"Bearer {token}"}
    print_header("FLUJO ADMINISTRADOR")

    # 1. IAM: Listar usuarios
    print_step("IAM: Listar usuarios (solo admin)")
    r = requests.get(f"{BASE_URLS['iam']}/admin/users", headers=headers)
    if r.status_code == 200:
        users = r.json()
        print_result("OK", f"Usuarios listados: {len(users)} encontrados")
    else:
        print_result("FAIL", f"Error listando usuarios: {r.status_code}")

    # 2. PROVEEDORES: Crear proveedor (Endpoint no encontrado en router público/interno, saltando...)
    print_step("PROVEEDORES: Crear nuevo proveedor (SALTADO - Endpoint no expuesto)")
    prov_id = None

    # 3. CATALOGO: Crear servicio (si existe endpoint de escritura, asumimos que sí por ser admin)
    # Nota: Ajustar según tu API real. Si no hay endpoint de escritura expuesto, saltamos.
    
    return prov_id

def test_client_flow(token, prov_id_created_by_admin):
    headers = {"Authorization": f"Bearer {token}"}
    print_header("FLUJO CLIENTE")

    # 1. CATALOGO: Listar tipos de evento (Público/Autenticado)
    print_step("CATALOGO: Buscar tipos de evento")
    r = requests.get(f"{BASE_URLS['catalogo']}/v1/catalogo/tipos", headers=headers)
    tipo_evento_id = None
    if r.status_code == 200:
        types = r.json()
        print_result("OK", f"Tipos de evento encontrados: {len(types)}")
        if types:
            tipo_evento_id = types[0]['id']
            print_step(f"Seleccionado Tipo Evento: {types[0]['nombre']}")
    else:
        # Fallback a endpoint alternativo si /types no existe
        print_result("WARN", f"Endpoint /v1/catalogo/tipos falló ({r.status_code}), probando /servicios...")
    
    # 2. CATALOGO: Listar servicios
    print_step("CATALOGO: Listar servicios")
    r = requests.get(f"{BASE_URLS['catalogo']}/v1/catalogo/servicios", headers=headers)
    servicio_id = None
    if r.status_code == 200:
        services = r.json()
        print_result("OK", f"Servicios encontrados: {len(services)}")
        if services:
            servicio_id = services[0]['id']
    else:
        print_result("FAIL", f"Error listando servicios: {r.status_code}")

    # 3. CONTRATACION: Crear Pedido (Cotización)
    if tipo_evento_id and servicio_id:
        print_step("CONTRATACION: Crear Pedido Custom")
        pedido_payload = {
            "tipo_evento_id": tipo_evento_id,
            "items": [
                {
                    "opcion_servicio_id": servicio_id,
                    "cantidad": 1
                }
            ],
            "fecha_evento": "2025-12-25",
            "hora_inicio": "18:00",
            "hora_fin": "23:00",
            "num_personas": 50,
            "ubicacion": "Lima Test"
        }
        r = requests.post(f"{BASE_URLS['contratacion']}/pedidos", json=pedido_payload, headers=headers)
        pedido_id = None
        if r.status_code in [200, 201]:
            pedido_data = r.json()
            pedido_id = pedido_data.get("id")
            print_result("OK", f"Pedido creado exitosamente. ID: {pedido_id}")
        else:
            print_result("FAIL", f"Error creando pedido: {r.status_code} - {r.text}")
            
        # 4. CONTRATACION: Consultar mis pedidos
        print_step("CONTRATACION: Listar mis pedidos")
        r = requests.get(f"{BASE_URLS['contratacion']}/pedidos/mios", headers=headers)
        if r.status_code == 200:
            mis_pedidos = r.json().get("items", [])
            found = any(p['id'] == pedido_id for p in mis_pedidos) if pedido_id else False
            print_result("OK", f"Pedidos listados: {len(mis_pedidos)}. Pedido reciente encontrado: {found}")
        else:
            print_result("FAIL", f"Error listando pedidos: {r.status_code}")
    else:
        print_result("WARN", "No se pudo crear pedido: falta tipo_evento_id o servicio_id")

def main():
    print("Iniciando Validación Integral de Endpoints...")
    
    # 1. Validar Admin
    admin_token = login(ADMIN_USER["email"], ADMIN_USER["password"], "ADMIN")
    prov_id = None
    if admin_token:
        prov_id = test_admin_flow(admin_token)
    else:
        print("CRITICAL: No se pudo loguear como Admin. Abortando pruebas de admin.")

    # 2. Validar Cliente
    client_token = register_client_if_needed()
    if client_token:
        test_client_flow(client_token, prov_id)
    else:
        print("CRITICAL: No se pudo obtener token de Cliente. Abortando pruebas de cliente.")

if __name__ == "__main__":
    main()
