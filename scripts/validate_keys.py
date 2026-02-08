import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
from models import ModelConfig
from api_integration import APIIntegration

if __name__ == '__main__':
    print('ModelConfig keys configured:')
    print(ModelConfig.validate_keys())
    print('\nRunning API integration validation (this will attempt network calls)...')
    ai = APIIntegration()
    results = ai.validate_apis()
    print('\nAPI validation results:')
    print(results)
