import requests
IAM='http://127.0.0.1:8010'
CAT='http://127.0.0.1:8020'
admin_email='admin@eventos.pe'
admin_pass='Admin_2025!'
# login
# login with timeout and error handling
try:
    r=requests.post(IAM+'/iam/auth/login',json={'email':admin_email,'password':admin_pass}, timeout=6)
    print('login',r.status_code)
    token = r.json().get('access_token') if r.status_code==200 else None
except Exception as e:
    print('login exception', e)
    token = None
print('token', bool(token))
headers={'Authorization':f'Bearer {token}'}
# call admin create tipo
resp=requests.post(CAT+'/catalogo/v1/admin/tipos', json={'nombre':'PruebaTipo','descripcion':'desc'}, headers=headers)
print('POST /v1/admin/tipos', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('no json', resp.text)
