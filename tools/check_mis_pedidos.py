"""
Login as demo client and fetch /api/contratacion/pedidos/mios via Gateway

Usage:
  python .\tools\check_mis_pedidos.py

Env vars:
  TEST_CLIENT_EMAIL (default: demo@eventos.pe)
  TEST_CLIENT_PASSWORD (default: Admin_2025!)
"""
import os
import requests
import json

GATEWAY = os.environ.get('GATEWAY_URL', 'http://localhost:8000')
LOGIN = f"{GATEWAY}/api/iam/auth/login"
MIS_PEDIDOS = f"{GATEWAY}/api/contratacion/pedidos/mios"

EMAIL = os.environ.get('TEST_CLIENT_EMAIL', 'demo@eventos.pe')
PASSWORD = os.environ.get('TEST_CLIENT_PASSWORD', 'Admin_2025!')

def main():
    print('Login as', EMAIL)
    r = requests.post(LOGIN, json={'email': EMAIL, 'password': PASSWORD}, timeout=10)
    print('Login status:', r.status_code)
    try:
        print('Login resp:', json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print('Login resp text:', r.text)
    if r.status_code != 200:
        return 1
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    print('\nFetching mis pedidos...')
    r2 = requests.get(MIS_PEDIDOS, headers=headers, timeout=10)
    print('Status:', r2.status_code)
    try:
        print('Body:', json.dumps(r2.json(), indent=2, ensure_ascii=False))
    except Exception:
        print('Body text:', r2.text)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
