#!/usr/bin/env python3
"""
Fetch servicios via API Gateway and for each servicio fetch opciones (first 10).
Print servicio id, nombre, first opcion categoria and monto (if any).
"""
import requests
import json

GATEWAY = 'http://127.0.0.1:8000/api'

def main():
    s_url = f"{GATEWAY}/catalogo/v1/servicios"
    try:
        r = requests.get(s_url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print('Failed to fetch servicios:', e)
        return
    try:
        servicios = r.json()
    except Exception:
        servicios = r.text
    # normalize
    if isinstance(servicios, dict) and servicios.get('data'):
        items = servicios['data']
    elif isinstance(servicios, list):
        items = servicios
    elif isinstance(servicios, dict) and servicios.get('items'):
        items = servicios['items']
    else:
        items = []
    print(f'Found {len(items)} servicios, will check up to 10')
    for s in items[:10]:
        sid = s.get('id')
        nombre = s.get('nombre')
        print('\nServicio:', sid, '-', nombre)
        try:
            ro = requests.get(f"{GATEWAY}/catalogo/v1/opciones", params={'servicio_id': sid}, timeout=10)
            if ro.status_code != 200:
                print('  opciones status', ro.status_code, ro.text)
                continue
            opciones = ro.json()
            if isinstance(opciones, dict) and opciones.get('data'):
                ops = opciones['data']
            elif isinstance(opciones, list):
                ops = opciones
            else:
                ops = []
            if not ops:
                print('  no opciones')
                continue
            for i,op in enumerate(ops[:3]):
                detalles = op.get('detalles')
                # detalles may be dict or string
                if isinstance(detalles, str):
                    try:
                        detalles = json.loads(detalles)
                    except Exception:
                        pass
                categoria = detalles.get('categoria') if isinstance(detalles, dict) else detalles
                monto = op.get('monto') or op.get('precio_unitario')
                print(f'  opcion[{i}] id={op.get("id")} categoria={categoria} monto={monto}')
        except Exception as e:
            print('  failed to fetch opciones:', e)

if __name__ == '__main__':
    main()
