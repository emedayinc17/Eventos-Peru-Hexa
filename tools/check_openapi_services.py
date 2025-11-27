import requests, os, json

ROOTS = {
    'proveedores': os.getenv('PROVEEDORES_ROOT', 'http://127.0.0.1:8030'),
    'contratacion': os.getenv('CONTRATACION_ROOT', 'http://127.0.0.1:8040'),
}

services = list(ROOTS.items())

for name, root in services:
    print('\n== Checking', name, root)
    tried = []
    # try plain /openapi.json
    for path in ['/openapi.json', f'/{name}/openapi.json', f'/{name}/v1/openapi.json']:
        url = root.rstrip('/') + path
        tried.append(url)
        try:
            r = requests.get(url, timeout=4)
            print(url, '->', r.status_code)
            if r.status_code == 200:
                try:
                    spec = r.json()
                    print('  paths count:', len(spec.get('paths', {})))
                    # print first 5 paths
                    for p in list(spec.get('paths', {}))[:10]:
                        print('   ', p)
                except Exception as e:
                    print('  ok but invalid json:', e)
                break
        except Exception as e:
            print(url, '-> error:', e)
    else:
        print('Tried urls:', tried)

print('\nDone')
