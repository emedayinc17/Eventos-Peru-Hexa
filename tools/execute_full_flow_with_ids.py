"""Ejecuta flujo completo usando los IDs de prueba definidos en `db/script2.sql`.

Flujo:
 - Login CLIENTE
 - Listar opciones en `catalogo` para `TEST_SERVICE_ID`
 - Listar proveedores disponibles para `TEST_SERVICE_ID`
 - Crear pedido custom en `contratacion` usando `TEST_OPTION_ID`
 - Listar `pedidos/mios` y buscar el pedido creado

Configurable vía variables de entorno:
  TEST_SERVICE_ID, TEST_OPTION_ID, TEST_PROVIDER_ID
  IAM_ROOT, CATALOGO_ROOT, PROVEEDORES_ROOT, CONTRATACION_ROOT
  TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD

"""
import os
import requests
from datetime import date
import time

IAM = os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')
CATALOGO = os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')
PROVEEDORES = os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')
CONTRATACION = os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')

TEST_SERVICE_ID = os.getenv('TEST_SERVICE_ID', 'aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa')
TEST_OPTION_ID = os.getenv('TEST_OPTION_ID', 'bbbbbbbb-2222-3333-4444-bbbbbbbbbbbb')
TEST_PROVIDER_ID = os.getenv('TEST_PROVIDER_ID', 'cccccccc-3333-4444-5555-cccccccccccc')

CLIENT_EMAIL = os.getenv('TEST_CLIENT_EMAIL', 'demo@eventos.pe')
CLIENT_PASSWORD = os.getenv('TEST_CLIENT_PASSWORD', 'Admin_2025!')


def login(email, password):
    url = IAM.rstrip('/') + '/iam/auth/login'
    r = requests.post(url, json={'email': email, 'password': password}, timeout=10)
    if r.status_code != 200:
        print('Login failed', r.status_code, r.text)
        return None
    data = r.json()
    token = data.get('access_token') or data.get('token') or data.get('accessToken')
    return token


def list_opciones(servicio_id):
    # Path según openapi del servicio: /catalogo/v1/catalogo/opciones
    url = CATALOGO.rstrip('/') + f'/catalogo/v1/catalogo/opciones'
    r = requests.get(url, params={'servicio_id': servicio_id}, timeout=10)
    print('List opciones', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def proveedores_disponibles(servicio_id):
    url = PROVEEDORES.rstrip('/') + f'/proveedores/v1/proveedores/disponibles'
    r = requests.get(url, params={'servicio_id': servicio_id, 'fecha': date.today().isoformat()}, timeout=10)
    print('Proveedores disponibles', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def crear_pedido_custom(token, opcion_id):
    url = CONTRATACION.rstrip('/') + '/contratacion/pedidos'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        'tipo_evento_id': '44444444-1111-1111-1111-111111111111',
        'items': [{'opcion_servicio_id': opcion_id, 'cantidad': 1}],
        'fecha_evento': (date.today()).isoformat(),
        'hora_inicio': '18:00:00',
        'num_personas': 10,
        'ubicacion': 'Lima'
    }
    r = requests.post(url, json=payload, headers=headers, timeout=15)
    print('Crear pedido custom', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def listar_pedidos_mios(token):
    url = CONTRATACION.rstrip('/') + '/contratacion/pedidos/mios'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, timeout=10)
    print('List pedidos/mios', r.status_code)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text


def main():
    print('Usando IDs de prueba:')
    print(' TEST_SERVICE_ID=', TEST_SERVICE_ID)
    print(' TEST_OPTION_ID=', TEST_OPTION_ID)
    print(' TEST_PROVIDER_ID=', TEST_PROVIDER_ID)

    token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    if not token:
        print('No se pudo autenticar cliente; abortando')
        return
    print('Token cliente OK len', len(token))

    # 1) listar opciones por servicio
    status, opciones = list_opciones(TEST_SERVICE_ID)
    if status == 200 and isinstance(opciones, list) and opciones:
        print('Opciones encontradas:', len(opciones))
        opcion_id = opciones[0].get('id') if isinstance(opciones[0], dict) else None
    else:
        print('No se obtuvieron opciones desde catalogo, usando TEST_OPTION_ID')
        opcion_id = TEST_OPTION_ID

    # 2) proveedores disponibles
    status_p, provs = proveedores_disponibles(TEST_SERVICE_ID)
    if status_p == 200:
        print('Proveedores disponibles response type', type(provs))
    else:
        print('Proveedores no listados o error; status', status_p)

    # 3) crear pedido custom con opcion_id
    status_c, created = crear_pedido_custom(token, opcion_id)
    print('Crear pedido response:', status_c, created)
    if status_c in (200,201):
        pedido_id = created.get('id') or created.get('pedido') or created.get('data', {}).get('id')
        print('Pedido creado:', pedido_id)
    else:
        print('Creación falla o no hubo creación. Intentaremos listar pedidos/mios para ver actividad')

    # 4) listar pedidos/mios
    time.sleep(1)
    st, pedidos = listar_pedidos_mios(token)
    print('Pedidos/mios type:', type(pedidos))
    if st == 200:
        if isinstance(pedidos, list):
            print('Número de pedidos del cliente:', len(pedidos))
        elif isinstance(pedidos, dict):
            print('Pedidos/mios dict keys:', list(pedidos.keys()))
    else:
        print('No se pudo listar pedidos:', st)


if __name__ == '__main__':
    main()
