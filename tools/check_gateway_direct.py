import requests

try:
    r = requests.get('http://localhost:8000/api/contratacion/health', timeout=5)
    print('Status', r.status_code)
    print(r.text)
except Exception as e:
    print('Error', e)
