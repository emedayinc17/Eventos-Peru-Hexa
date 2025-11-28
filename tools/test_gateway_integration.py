"""
Test de Integración - API Gateway + Microservicios
Prueba el flujo completo a través del Gateway
"""
import requests
import json
from typing import Dict, Any

# Configuración
GATEWAY_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5174"

def print_test(name: str):
    """Imprime el nombre del test"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")

def print_result(success: bool, message: str):
    """Imprime el resultado"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_gateway_health():
    """Test 1: Gateway Health Check"""
    print_test("Gateway Health Check")
    try:
        response = requests.get(f"{GATEWAY_URL}/health")
        data = response.json()
        
        success = (
            response.status_code == 200 and
            data.get("status") == "healthy" and
            len(data.get("services", {})) == 4
        )
        
        print_result(success, f"Gateway health: {data.get('status')}")
        print(f"   Servicios registrados: {len(data.get('services', {}))}")
        for service, url in data.get("services", {}).items():
            print(f"   - {service}: {url}")
        
        return success
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_iam_register():
    """Test 2: Registro de usuario a través del Gateway"""
    print_test("IAM - Registro de Usuario")
    try:
        payload = {
            "email": "gateway_test@test.com",
            "password": "test123",
            "nombre": "Gateway",
            "apellido": "Test",
            "telefono": "987654321"
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/api/iam/auth/register",
            json=payload
        )

        # Mostrar info cruda para depuración si hay fallo
        try:
            data = response.json()
        except Exception:
            data = None

        if response.status_code in (400, 409):
            print_result(True, "Usuario ya existe (esperado en re-ejecuciones)")
            if data:
                print(f"   Response: {data}")
            return True

        success = response.status_code in (200,201)
        print_result(success, f"Usuario registrado: {data.get('email') if isinstance(data, dict) else data}")
        print(f"   Status code: {response.status_code}")
        print(f"   Raw response: {data}")
        return success
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_iam_login() -> Dict[str, Any]:
    """Test 3: Login a través del Gateway"""
    print_test("IAM - Login de Usuario")
    try:
        payload = {
            "email": "gateway_test@test.com",
            "password": "test123"
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/api/iam/auth/login",
            json=payload
        )
        
        data = response.json()
        success = response.status_code == 200 and "access_token" in data
        
        print_result(success, "Login exitoso")
        if success:
            token = data.get("access_token", "")
            print(f"   Token (primeros 50 chars): {token[:50]}...")
            print(f"   Usuario: {data.get('usuario', {}).get('email')}")
            return data
        
        return {}
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return {}

def test_catalogo_tipos_evento(token: str):
    """Test 4: Obtener tipos de evento"""
    print_test("Catálogo - Listar Tipos de Evento")
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Probar diferentes rutas posibles (incluye variantes v1)
        rutas_posibles = [
            "/api/catalogo/v1/tipos-evento",
            "/api/catalogo/v1/tipos",
            "/api/catalogo/tipos-evento",
            "/api/catalogo/tiposevento",
            "/api/catalogo/tipos_evento",
        ]
        
        for ruta in rutas_posibles:
            response = requests.get(f"{GATEWAY_URL}{ruta}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                tipos = data.get("data", []) if isinstance(data, dict) else data
                
                print_result(True, f"Ruta correcta: {ruta}")
                print(f"   Tipos encontrados: {len(tipos)}")
                if tipos:
                    print(f"   Ejemplos:")
                    for tipo in tipos[:3]:
                        nombre = tipo.get("nombre") if isinstance(tipo, dict) else tipo
                        print(f"   - {nombre}")
                return True
        
        print_result(False, "No se encontró ruta válida para tipos de evento")
        return False
        
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_catalogo_paquetes(token: str):
    """Test 5: Obtener paquetes"""
    print_test("Catálogo - Listar Paquetes")
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Intentar rutas v1 primero y luego non-v1
        rutas = ["/api/catalogo/v1/paquetes", "/api/catalogo/paquetes"]
        response = None
        for ruta in rutas:
            response = requests.get(f"{GATEWAY_URL}{ruta}", headers=headers)
            if response.status_code == 200:
                break

        if response and response.status_code == 200:
            data = response.json()
            paquetes = data.get("data", []) if isinstance(data, dict) else data

            print_result(True, "Paquetes obtenidos")
            print(f"   Total: {len(paquetes)}")
            if paquetes:
                print(f"   Ejemplos:")
                for paq in paquetes[:3]:
                    if isinstance(paq, dict):
                        print(f"   - {paq.get('nombre')} (S/ {paq.get('precio_base')})")
            return True
        else:
            status = response.status_code if response else 'no response'
            print_result(False, f"Status: {status}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def test_frontend_accessible():
    """Test 6: Frontend accesible"""
    print_test("Frontend - Página Principal")
    try:
        # Try common Vite ports (5173 default, 5174 alternate)
        frontend_urls = [FRONTEND_URL, "http://localhost:5173"]
        response = None
        frontend_checked = None
        for url in frontend_urls:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200 and "<!doctype html>" in response.text.lower():
                    frontend_checked = url
                    break
            except Exception:
                response = None

        success = bool(response and response.status_code == 200 and "<!doctype html>" in response.text.lower())

        print_result(success, "Frontend cargando correctamente")
        if response:
            print(f"   URL: {frontend_checked}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200 and "<!DOCTYPE html>" not in response.text:
                preview = response.text[:200].replace('\n', ' ')
                print(f"   Nota: el contenido recibido no parece HTML. preview: {preview}...")
        else:
            print(f"   URLs probadas: {frontend_urls}")

        return success
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("PRUEBAS DE INTEGRACIÓN - API GATEWAY")
    print("="*60)
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print("="*60)
    
    results = []
    
    # Test 1: Gateway Health
    results.append(("Gateway Health", test_gateway_health()))
    
    # Test 2: Registro
    results.append(("IAM Register", test_iam_register()))
    
    # Test 3: Login
    login_data = test_iam_login()
    token = login_data.get("access_token", "")
    results.append(("IAM Login", bool(token)))
    
    # Test 4: Catálogo - Tipos
    results.append(("Catálogo Tipos", test_catalogo_tipos_evento(token)))
    
    # Test 5: Catálogo - Paquetes
    results.append(("Catálogo Paquetes", test_catalogo_paquetes(token)))
    
    # Test 6: Frontend
    results.append(("Frontend Accesible", test_frontend_accessible()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests pasaron ({passed*100//total}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\n✅ El API Gateway está funcionando correctamente")
        print("✅ Los microservicios responden correctamente")
        print("✅ El frontend está accesible")
        print("\nPuedes probar el login en: http://localhost:5174")
        print("   Email: gateway_test@test.com")
        print("   Password: test123")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        print("Revisa los logs arriba para más detalles")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
