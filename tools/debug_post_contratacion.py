import requests, json
GATEWAY = 'http://localhost:8000'
IAM_LOGIN = f"{GATEWAY}/api/iam/auth/login"
CONTR_POST = f"{GATEWAY}/api/contratacion/pedidos"
creds = {"email":"demo@eventos.pe","password":"Admin_2025!"}
print('1) POST', IAM_LOGIN)
r = requests.post(IAM_LOGIN, json=creds, timeout=10)
print('IAM status:', r.status_code)
try:
    print('IAM resp:', r.json())
except Exception as e:
    print('IAM resp text:', r.text)
if r.status_code==200:
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type':'application/json'}
    sample = {
        "items":[{"opcion_servicio_id":1,"cantidad":1}],
        "tipo_evento_id":1,
        "num_personas":10,
        "fecha_evento":"2025-12-01",
        "hora_inicio":"18:00",
        "hora_fin":"22:00",
        "ubicacion":"Lugar de prueba"
    }
    print('\n2) POST', CONTR_POST, 'with Authorization header')
    r2 = requests.post(CONTR_POST, json=sample, headers=headers, timeout=10)
    print('Contr status:', r2.status_code)
    try:
        print('Contr resp:', json.dumps(r2.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print('Contr resp text:', r2.text)
else:
    print('Skipping contratacion POST due to failed login')
