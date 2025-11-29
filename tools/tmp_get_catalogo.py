import requests
URL='http://localhost:8020/catalogo/v1/paquetes/pkg-matr-0001'
try:
    r=requests.get(URL, timeout=5)
    print('GET', URL, r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    print('error', e)
