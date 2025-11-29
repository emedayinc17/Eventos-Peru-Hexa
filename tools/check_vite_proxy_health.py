import requests

def check():
    print('GET gateway /health')
    try:
        r = requests.get('http://localhost:8000/health', timeout=5)
        print(r.status_code, r.text)
    except Exception as e:
        print('Gateway health error:', e)
    print('\nGET via Vite /api/health')
    try:
        r2 = requests.get('http://localhost:5173/api/health', timeout=5)
        print(r2.status_code, r2.text)
    except Exception as e:
        print('Vite /api/health error:', e)
    print('\nGET via Vite /api/contratacion/health')
    try:
        r3 = requests.get('http://localhost:5173/api/contratacion/health', timeout=5)
        print(r3.status_code, r3.text)
    except Exception as e:
        print('Vite /api/contratacion/health error:', e)

if __name__ == '__main__':
    check()
