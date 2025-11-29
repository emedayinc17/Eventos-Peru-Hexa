import requests, subprocess, json

print('Checking contratacion service HTTP health on http://localhost:8040/contratacion/health')
try:
    r = requests.get('http://localhost:8040/contratacion/health', timeout=3)
    print('HTTP status:', r.status_code)
    try:
        print('Body:', json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print('Body text:', r.text)
except Exception as e:
    print('HTTP check failed:', e)

print('\nChecking port 8040 listeners using netstat')
try:
    out = subprocess.check_output(['netstat', '-ano'], universal_newlines=True)
    lines = [l for l in out.splitlines() if ':8040' in l]
    if not lines:
        print('No netstat lines found for :8040')
    else:
        for l in lines:
            print(l)
            # Try to extract PID
            parts = l.split()
            pid = parts[-1]
            print(' -> PID:', pid)
            # Try to get process name via tasklist
            try:
                tl = subprocess.check_output(['tasklist', '/FI', f'PID eq {pid}'], universal_newlines=True)
                print(tl)
            except Exception as e:
                print('tasklist error:', e)
except Exception as e:
    print('netstat failed:', e)
