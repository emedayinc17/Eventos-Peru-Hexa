"""
Obtener token de admin y decodificar payload JWT para mostrar claims.

Uso:
  python .\tools\decode_admin_token.py

Variables opcionales de entorno:
  TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD
"""
import os
import sys
import json
import base64
import requests

def b64url_decode(inp: str) -> bytes:
    s = inp.encode('utf-8')
    # add padding
    rem = len(s) % 4
    if rem:
        s += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(s)

def main():
    email = os.environ.get('TEST_ADMIN_EMAIL', 'admin@eventos.pe')
    password = os.environ.get('TEST_ADMIN_PASSWORD', 'Evoluti0n')
    login_url = 'http://localhost:5173/api/iam/auth/login'
    print(f'Logging in as {email} -> {login_url}')
    try:
        r = requests.post(login_url, json={'email': email, 'password': password}, timeout=8)
    except Exception as e:
        print('Error connecting to login endpoint:', e)
        sys.exit(2)
    print('Status:', r.status_code)
    try:
        data = r.json()
    except Exception:
        print('Non-JSON response:', r.text)
        sys.exit(3)
    token = data.get('access_token') or data.get('token')
    if not token:
        print('No access_token in login response:', json.dumps(data, indent=2))
        sys.exit(4)
    print('Token length:', len(token))

    # Decode JWT payload
    parts = token.split('.')
    if len(parts) < 2:
        print('Token not in JWT format')
        sys.exit(5)
    payload_b = b64url_decode(parts[1])
    try:
        payload = json.loads(payload_b.decode('utf-8'))
    except Exception as e:
        print('Error decoding payload:', e)
        print(payload_b)
        sys.exit(6)

    print('\nDecoded JWT payload:')
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    role = payload.get('role') or payload.get('rol') or payload.get('role'.upper()) or payload.get('rol'.upper())
    print('\nDetected role claim value:', repr(role))
    if isinstance(role, str) and role.lower() == 'admin':
        print('-> Usuario es ADMIN (case-insensitive match)')
    else:
        print('-> Usuario NO es ADMIN según claim; revisar claims')

if __name__ == '__main__':
    main()
