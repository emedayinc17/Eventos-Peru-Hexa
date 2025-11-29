import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_route(method, path, expected_codes, description):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            res = requests.get(url)
        elif method == "PATCH":
            res = requests.patch(url, json={}) 
        elif method == "POST":
            res = requests.post(url, json={})
        
        print(f"Testing {description} [{method} {url}]")
        print(f"  -> Status: {res.status_code}")
        
        if res.status_code in expected_codes:
            print("  -> ✅ PASS (Secured)")
            return True
        else:
            if res.status_code == 200:
                print(f"  -> ❌ FAIL (SECURITY RISK: Got 200 OK, expected {expected_codes})")
            else:
                print(f"  -> ❌ FAIL (Expected {expected_codes}, got {res.status_code})")
            return False
    except Exception as e:
        print(f"  -> ❌ ERROR: {e}")
        return False

print("=== VERIFICACIÓN DE SEGURIDAD DE RUTAS ADMIN ===\n")
print("Nota: Se espera 401 (Unauthorized) o 403 (Forbidden) porque NO enviamos token.")
print("      Si recibimos 200, la ruta es INSEGURA.\n")

# 1. Proveedores Admin List
success_prov = test_route("GET", "/proveedores/v1/admin/proveedores", [401, 403], "Proveedores Admin List")

# 2. IAM Update User
success_iam = test_route("PATCH", "/iam/admin/users/dummy-id", [401, 403], "IAM Update User")

# 3. Contratacion Update Pedido
success_order = test_route("PATCH", "/contratacion/admin/pedidos/dummy-id", [401, 403], "Contratacion Update Pedido")

# 4. Catalogo Create Tipo (Prueba extra)
success_cat = test_route("POST", "/catalogo/v1/admin/tipos", [401, 403], "Catalogo Create Tipo")

print("\n=== RESUMEN DE SEGURIDAD ===")
if success_prov and success_iam and success_order and success_cat:
    print("✅ TODAS LAS RUTAS ADMIN ESTÁN PROTEGIDAS.")
else:
    print("❌ ALGUNAS RUTAS SON INSEGURAS O NO RESPONDEN.")
