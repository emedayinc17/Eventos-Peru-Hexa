"""Test automático basado en OpenAPI: intenta invocar las operaciones listadas.

Uso: python tools/test_openapi_endpoints.py

Precaución: para métodos no-GET se envía un cuerpo mínimo `{}`. Evita operaciones destructivas en entornos reales.
"""
import requests
import os
import json

SERVICES = [
    ('iam', os.getenv('IAM_ROOT', 'http://127.0.0.1:8010')),
    ('catalogo', os.getenv('CATALOGO_ROOT', 'http://127.0.0.1:8020')),
    ('proveedores', os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030')),
    ('contratacion', os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040')),
]

TOKEN = None

def get_token():
    global TOKEN
    if TOKEN:
        return TOKEN
    iam = [s for s in SERVICES if s[0]=='iam']
    if not iam:
        return None
    root = iam[0][1]
    try:
        r = requests.post(root + '/iam/auth/login', json={
            'email': os.getenv('TEST_CLIENT_EMAIL','demo@eventos.pe'),
            'password': os.getenv('TEST_CLIENT_PASSWORD','Admin_2025!')
        }, timeout=6)
        if r.status_code==200:
            data=r.json()
            TOKEN = data.get('access_token') or data.get('token') or data.get('accessToken')
            return TOKEN
    except Exception:
        return None

def try_request(root, method, path, need_auth=False):
    url = root.rstrip('/') + path
    headers = {}
    if need_auth:
        t = get_token()
        if t:
            headers['Authorization'] = f'Bearer {t}'
    try:
        if method.lower() == 'get':
            r = requests.get(url, headers=headers, timeout=10)
        elif method.lower() in ('post','put','patch','delete'):
            r = requests.request(method.upper(), url, headers=headers, json={}, timeout=12)
        else:
            r = requests.request(method.upper(), url, headers=headers, timeout=10)
        try:
            body = r.json()
        except Exception:
            body = r.text[:300]
        return r.status_code, body
    except Exception as e:
        return 'error', str(e)

def main():
    print('Iniciando test basado en OpenAPI de servicios...')
    summary = []
    for name, root in SERVICES:
        openapi_url = root.rstrip('/') + '/openapi.json'
        print(f'\n== {name} ({root}) ==')
        try:
            r = requests.get(openapi_url, timeout=6)
            if r.status_code != 200:
                print(' openapi.json no disponible ->', r.status_code)
                summary.append((name, 'openapi_missing', r.status_code))
                continue
            spec = r.json()
        except Exception as e:
            print(' error al obtener openapi.json', e)
            summary.append((name, 'openapi_error', str(e)))
            continue

        paths = spec.get('paths', {})
        for path, ops in paths.items():
            for method, meta in ops.items():
                # determine if security required by operation
                need_auth = False
                if meta.get('security'):
                    need_auth = True
                status, body = try_request(root, method, path, need_auth=need_auth)
                print(f' {method.upper():6} {path:40} -> {status}')
                summary.append((name, method.upper(), path, status))

    print('\nResumen breve:')
    for item in summary:
        print(' -', item)


if __name__ == '__main__':
    main()
