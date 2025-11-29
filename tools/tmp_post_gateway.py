import requests, json
GATEWAY='http://localhost:8000'
creds={'email':'test.cliente@eventos.pe','password':'test123'}
try:
    r=requests.post(GATEWAY+'/api/iam/auth/login',json=creds,timeout=10)
    print('login', r.status_code)
    if r.status_code==200:
        t=r.json().get('access_token')
        headers={'Authorization':f'Bearer {t}','Content-Type':'application/json'}
        payload={
          "tipo_evento_id":"11111111-1111-1111-1111-111111111111",
          "paquete_id":"pkg-matr-0001",
          "fecha_evento":"2025-12-01",
          "num_personas":100,
          "hora_inicio":"18:00:00",
          "hora_fin":"22:00:00",
          "ubicacion":"Lugar de prueba"
        }
        r2=requests.post(GATEWAY+'/api/contratacion/pedidos',json=payload,headers=headers,timeout=10)
        print('post', r2.status_code)
        try:
            print(json.dumps(r2.json(),indent=2,ensure_ascii=False))
        except Exception:
            print(r2.text)
    else:
        print('login failed', r.text)
except Exception as e:
    print('error', e)
