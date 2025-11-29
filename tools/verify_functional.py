import requests
import sys
import json

BASE_URL = "http://localhost:8000/api"

# Credenciales probables de admin
ADMIN_EMAIL = "admin@colegio.com"
ADMIN_PASS = "Admin123!"

def get_admin_token():
    url = f"{BASE_URL}/iam/auth/login"
    try:
        res = requests.post(url, json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        if res.status_code == 200:
            token = res.json().get("access_token")
            print(f"✅ Login Admin exitoso. Token obtenido.")
            return token
        else:
            print(f"⚠️ Login Admin falló ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        print(f"❌ Error conectando a IAM: {e}")
        return None

def test_endpoint(method, path, token=None, body=None, expected_codes=[200], description=""):
    url = f"{BASE_URL}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            res = requests.get(url, headers=headers)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=body)
        elif method == "PATCH":
            res = requests.patch(url, headers=headers, json=body)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers)
            
        print(f"Testing {description} [{method} {url}]")
        print(f"  -> Status: {res.status_code}")
        
        if res.status_code in expected_codes:
            print("  -> ✅ PASS")
            return True, res
        else:
            print(f"  -> ❌ FAIL (Expected {expected_codes}, got {res.status_code})")
            print(f"  -> Response: {res.text[:200]}")
            return False, res
    except Exception as e:
        print(f"  -> ❌ ERROR: {e}")
        return False, None

print("=== VERIFICACIÓN FUNCIONAL COMPLETA ===\n")

# 1. Login
token = get_admin_token()
if not token:
    print("\n⚠️ No se pudo obtener token de admin. Se omitirán pruebas autenticadas.")
    print("   (Verifica si el usuario admin existe o las credenciales son correctas)")

# 2. Catalogo Público
print("\n--- Catálogo Público ---")
test_endpoint("GET", "/catalogo/v1/tipos", expected_codes=[200], description="Listar Tipos Evento")
test_endpoint("GET", "/catalogo/v1/servicios", expected_codes=[200], description="Listar Servicios (Todos)")

# 3. Proveedores Admin (Requiere Token)
if token:
    print("\n--- Proveedores Admin ---")
    # Listar
    test_endpoint("GET", "/proveedores/v1/admin/proveedores", token=token, expected_codes=[200], description="Listar Proveedores (Admin)")
    
    # Crear Proveedor Dummy
    prov_data = {
        "nombre": "Proveedor Test Auto",
        "email": "test@prov.com",
        "telefono": "999888777"
    }
    success, res = test_endpoint("POST", "/proveedores/v1/admin/proveedores", token=token, body=prov_data, expected_codes=[201], description="Crear Proveedor")
    if success:
        prov_id = res.json().get("id")
        print(f"   -> Proveedor creado con ID: {prov_id}")
        # Eliminar
        if prov_id:
            test_endpoint("DELETE", f"/proveedores/v1/admin/proveedores/{prov_id}", token=token, expected_codes=[204], description="Eliminar Proveedor")

# 4. Servicios Admin (Requiere Token)
if token:
    print("\n--- Servicios Admin ---")
    # Crear Servicio Dummy (necesita un tipo_evento_id válido)
    # Primero obtenemos un tipo
    s, r = test_endpoint("GET", "/catalogo/v1/tipos", expected_codes=[200], description="Obtener Tipos para crear servicio")
    if s and len(r.json()) > 0:
        tipo_id = r.json()[0]["id"]
        serv_data = {
            "nombre": "Servicio Test Auto",
            "descripcion": "Test description",
            "tipo_evento_id": tipo_id,
            "precio_unitario": 100.0,
            "categoria": "OTROS",
            "disponible": True
        }
        success, res = test_endpoint("POST", "/catalogo/v1/admin/servicios", token=token, body=serv_data, expected_codes=[201], description="Crear Servicio")
        if success:
            serv_id = res.json().get("id")
            print(f"   -> Servicio creado con ID: {serv_id}")
            # Eliminar
            if serv_id:
                test_endpoint("DELETE", f"/catalogo/v1/admin/servicios/{serv_id}", token=token, expected_codes=[204], description="Eliminar Servicio")

print("\n=== FIN DEL TEST ===")
