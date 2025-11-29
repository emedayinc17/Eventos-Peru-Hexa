import requests, json
VITE = 'http://localhost:5173'
GATEWAY = 'http://localhost:8000'
IAM_LOGIN = f"{GATEWAY}/api/iam/auth/login"
VITE_CONTR_POST = f"{VITE}/api/contratacion/pedidos"
creds = {"email":"test.cliente@eventos.pe","password":"test123"}

print('1) Login via gateway:', IAM_LOGIN)
r = requests.post(IAM_LOGIN, json=creds, timeout=10)
print('IAM status:', r.status_code)
try:
    print('IAM resp:', json.dumps(r.json(), indent=2, ensure_ascii=False))
except Exception:
    print('IAM resp text:', r.text)

if r.status_code == 200:
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    sample = {
        "tipo_evento_id": "11111111-1111-1111-1111-111111111111",
        "paquete_id": "pkg-matr-0001",
        "fecha_evento": "2025-12-01",
        "num_personas": 100,
        "hora_inicio": "18:00:00",
        "hora_fin": "22:00:00",
        "ubicacion": "Lugar de prueba"
    }
    print('\n2) POST to Vite dev server (should be proxied):', VITE_CONTR_POST)
    try:
        r2 = requests.post(VITE_CONTR_POST, json=sample, headers=headers, timeout=10)
        print('Vite POST status:', r2.status_code)
        try:
            print('Vite resp:', json.dumps(r2.json(), indent=2, ensure_ascii=False))
        except Exception:
            print('Vite resp text:', r2.text)
    except Exception as e:
        print('Error posting to Vite dev server:', e)
else:
    print('Login failed; aborting test')
