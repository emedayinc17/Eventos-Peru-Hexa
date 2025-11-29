"""
Script para probar la creación de un tipo de evento via API
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8000/api/catalogo/v1/admin/tipos"
LOGIN_URL = "http://localhost:8000/api/iam/v1/auth/login"

# 1. Login como admin
print("1. Haciendo login como admin...")
login_response = requests.post(LOGIN_URL, json={
    "email": "admin@eventos.pe",
    "password": "Evoluti0n"
})

if login_response.status_code != 200:
    print(f"❌ Error en login: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login exitoso. Token obtenido.")

# 2. Crear tipo de evento con descripción
print("\n2. Creando tipo de evento...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "nombre": "Test Automatizado",
    "descripcion": "Este es un test automatizado para verificar que se guarda la descripción"
}

create_response = requests.post(API_URL, json=data, headers=headers)

if create_response.status_code == 201:
    print(f"✅ Tipo de evento creado exitosamente!")
    print(f"   Respuesta: {json.dumps(create_response.json(), indent=2)}")
    tipo_id = create_response.json().get("id")
else:
    print(f"❌ Error al crear: {create_response.status_code}")
    print(create_response.text)
    exit(1)

# 3. Verificar en la base de datos
print("\n3. Verificando en la base de datos...")
import pymysql

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'app_catalogo',
    'password': 'Catalogo_2025',
    'database': 'ev_catalogo',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("""
        SELECT id, nombre, descripcion, status
        FROM tipo_evento
        WHERE id = %s
    """, (tipo_id,))
    
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Registro encontrado en la BD:")
        print(f"   ID: {result['id']}")
        print(f"   Nombre: {result['nombre']}")
        print(f"   Descripción: {result['descripcion']}")
        print(f"   Status: {result['status']}")
        
        if result['descripcion']:
            print("\n🎉 ¡ÉXITO! La descripción se guardó correctamente.")
        else:
            print("\n❌ FALLO: La descripción está vacía en la BD.")
    else:
        print(f"❌ No se encontró el registro con ID {tipo_id} en la BD")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error al verificar BD: {e}")
