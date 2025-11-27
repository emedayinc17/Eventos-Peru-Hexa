import requests, json
spec = requests.get('http://127.0.0.1:8020/openapi.json').json()
for p in sorted(spec.get('paths',{})):
	if 'tipos' in p:
		print(p)
		print(json.dumps(spec['paths'][p], indent=2))
