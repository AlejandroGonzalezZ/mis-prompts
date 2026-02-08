import requests, json
r = requests.post('http://localhost:8001/api/generate-prompts', json={'idea':'Prueba UI fallback','style':'fotografia','personajes':['ninguno']}, timeout=60)
print('Status', r.status_code)
print('model_info:', r.json().get('model_info'))
print('model_used:', r.json().get('model_used'))
print('keys:', list(r.json().keys()))
