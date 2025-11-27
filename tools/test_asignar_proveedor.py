"""
Test mínimo para asignación de proveedor
"""
import requests
from datetime import datetime, timedelta, date

IAM = 'http://127.0.0.1:8010'
CONTRATACION = 'http://127.0.0.1:8040'

ADMIN_EMAIL = 'admin@eventos.pe'
ADMIN_PASSWORD = 'Admin_2025!'

TEST_TIPO_EVENTO_ID = '44444444-1111-1111-1111-111111111111'
TEST_OPTION_ID = 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb'
TEST_PROVIDER_ID = 'cccccccc-3333-4444-5555-cccccccccccc'

# Login
print('Login admin...')
r = requests.post(f'{IAM}/iam/auth/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
admin_token = r.json()['access_token']
print(f'✅ Token obtenido')

# Crear pedido
print('\nCreando pedido...')
fecha_evento = (date.today() + timedelta(days=45)).isoformat()
pedido_data = {
    'tipo_evento_id': TEST_TIPO_EVENTO_ID,
    'items': [{'opcion_servicio_id': TEST_OPTION_ID, 'cantidad': 2}],
    'fecha_evento': fecha_evento,
    'hora_inicio': '19:00:00',
    'num_personas': 200,
    'ubicacion': 'Cusco, Perú'
}

r = requests.post(f'{CONTRATACION}/contratacion/pedidos', 
                  headers={'Authorization': f'Bearer {admin_token}'},
                  json=pedido_data)
pedido_id = r.json()['id']
print(f'✅ Pedido creado: {pedido_id}')

# Cambiar a COTIZADO
print('\nCambiando a COTIZADO...')
r = requests.patch(f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'estado': 1})
print(f'✅ Estado: {r.status_code}')

# Cambiar a APROBADO
print('\nCambiando a APROBADO...')
r = requests.patch(f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={'estado': 2})
print(f'✅ Estado: {r.status_code}')

# Obtener item_pedido_id
print('\nObteniendo item_pedido_id...')
r = requests.get(f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}',
                 headers={'Authorization': f'Bearer {admin_token}'})
items = r.json()['items']
item_pedido_id = items[0]['id']
print(f'✅ Item ID: {item_pedido_id}')

# Asignar proveedor
print('\nAsignando proveedor...')
fecha_inicio = datetime.fromisoformat(fecha_evento + 'T19:00:00')
fecha_fin = fecha_inicio + timedelta(hours=4)

asignar_data = {
    'proveedor_id': TEST_PROVIDER_ID,
    'item_pedido_id': item_pedido_id,
    'opcion_servicio_id': TEST_OPTION_ID,
    'fecha_inicio': fecha_inicio.isoformat(),
    'fecha_fin': fecha_fin.isoformat(),
    'monto': 1500.0,
    'hold_id': None
}

print(f'Payload: {asignar_data}')

try:
    r = requests.post(f'{CONTRATACION}/contratacion/admin/pedidos/{pedido_id}/asignar-proveedor',
                      headers={'Authorization': f'Bearer {admin_token}'},
                      json=asignar_data,
                      timeout=10)
    print(f'\nStatus: {r.status_code}')
    print(f'Response: {r.json()}')
    print('\n✅ Asignación exitosa!')
except Exception as e:
    print(f'\n❌ Error: {e}')
    try:
        print(f'Response text: {r.text}')
    except:
        pass
