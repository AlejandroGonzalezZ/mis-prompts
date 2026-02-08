import os, sys, json
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from models import ModelConfig
import requests

url = 'https://openrouter.ai/api/v1/chat/completions'
headers = {'Authorization': f'Bearer {ModelConfig.OPENROUTER_API_KEY}', 'Content-Type': 'application/json'}
model = ModelConfig.MODELO_B_VISION
# Normalize model id - mantener prefijo para OpenRouter
if ':' in model:
    model = model.split(':',1)[0]

payload = {
    'model': model,
    'messages': [{'role':'user','content':'Hola prueba'}],
    'temperature': 0.2,
    'max_tokens': 50
}
print('POST', url)
try:
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    print('Status:', r.status_code)
    print('Headers:', r.headers)
    text = r.text
    print('Body len:', len(text))
    print('Body preview:\n', text[:2000])
except Exception as e:
    print('ERROR', e)
