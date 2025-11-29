#!/usr/bin/env python3
"""
Simple debugger for catalogo opciones endpoint.
Usage:
  python tools\fetch_opciones_debug.py [SERVICIO_ID] [--gateway]

Defaults to servicio_id 'f40647ce-a748-462b-99c1-ce441a9cf4fa'.
If --gateway is passed, it will call the API Gateway path at http://127.0.0.1:8000/api/catalogo/v1/opciones
Otherwise it calls the catalog service directly at http://127.0.0.1:8020/catalogo/v1/opciones
"""
import sys
import requests
import json
import traceback

DEFAULT_ID = "f40647ce-a748-462b-99c1-ce441a9cf4fa"


def main():
    args = sys.argv[1:]
    servicio_id = DEFAULT_ID
    use_gateway = False
    if args:
        for a in args:
            if a == '--gateway':
                use_gateway = True
            elif a.startswith('--'):
                continue
            else:
                servicio_id = a

    if use_gateway:
        base = 'http://127.0.0.1:8000/api/catalogo/v1/opciones'
    else:
        base = 'http://127.0.0.1:8020/catalogo/v1/opciones'

    params = {'servicio_id': servicio_id}
    headers = {'Accept': 'application/json'}

    print('\nRequest:')
    print('  URL:', base)
    print('  params:', params)
    print('  headers:', headers)

    try:
        r = requests.get(base, params=params, headers=headers, timeout=20)
        print('\nResponse:')
        print('  Status:', r.status_code)
        print('  Reason:', r.reason)
        print('  Headers:')
        for k, v in r.headers.items():
            print('   ', k + ':', v)
        print('\n  Body:')
        ct = r.headers.get('Content-Type','')
        try:
            if 'application/json' in ct:
                j = r.json()
                print(json.dumps(j, indent=2, ensure_ascii=False))
            else:
                print(r.text)
        except Exception as e:
            print('  (failed to parse JSON)', e)
            print(r.text)
    except Exception as e:
        print('\nException while requesting:')
        print(str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
