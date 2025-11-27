import requests

services = [
    ('catalogo','http://127.0.0.1:8020/catalogo'),
    ('proveedores','http://127.0.0.1:8030/proveedores'),
]

for name, base in services:
    url = base + '/openapi.json'
    try:
        r = requests.get(url, timeout=5)
        print(name, r.status_code)
        if r.status_code == 200:
            data = r.json()
            paths = list(data.get('paths', {}).keys())
            print('  rutas:', len(paths))
            for p in paths[:50]:
                print('   ', p)
        else:
            print('  body:', r.text[:400])
    except Exception as e:
        print(name, 'error', e)
