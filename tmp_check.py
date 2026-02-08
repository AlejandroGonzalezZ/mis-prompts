import requests, json
r = requests.post('http://localhost:8001/api/generate-prompts', json={'idea':'Prueba fallback endpoint','style':'fotografia','personajes':['ninguno']}, timeout=30)
print('Status', r.status_code)
print('model_info:', r.json().get('model_info'))
print(json.dumps(r.json(), indent=2)[:1000])
