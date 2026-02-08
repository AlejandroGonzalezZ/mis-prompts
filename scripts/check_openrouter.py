import sys
import os
import requests

# Ensure project root is on sys.path regardless of invocation cwd
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from models import ModelConfig

candidates=[
    'https://openrouter.io/api/v1/chat/completions',
    'https://openrouter.ai/v1/chat/completions',
    'https://api.openrouter.ai/v1/chat/completions',
    'https://api.openrouter.ai/api/v1/chat/completions'
]
headers={'Authorization': f'Bearer {ModelConfig.OPENROUTER_API_KEY}'}
for u in candidates:
    try:
        r=requests.options(u, headers=headers, timeout=10)
        print(u, r.status_code, r.headers.get('Allow'))
    except Exception as e:
        print(u, 'ERR', e)
