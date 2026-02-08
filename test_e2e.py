#!/usr/bin/env python
"""Test E2E del sistema completo"""
import requests
import json
import time

print('=== PRUEBA E2E DEL SISTEMA ===\n')

# 1. Probar endpoint de configuración
print('1. Verificar configuración...')
response = requests.get('http://localhost:8001/api/config', timeout=10)
if response.status_code == 200:
    data = response.json()
    print('✅ Config cargada correctamente')
else:
    print(f'❌ Error en config: {response.status_code}')

# 2. Generar prompt con OpenRouter
print('\n2. Generando prompt con OpenRouter...')
payload = {
    'idea': 'Modelo en estudio con iluminación cinematográfica',
    'style': 'fotografia'
}
response = requests.post('http://localhost:8001/api/prompts-openrouter', json=payload, timeout=30)
if response.status_code == 200:
    data = response.json()
    print('✅ Prompt generado exitosamente')
    print(f"Modelo: {data.get('model_used')}")
    print(f"Prompt ES length: {len(data.get('prompt_es', ''))} characters")
    print(f"Prompt EN length: {len(data.get('prompt_en', '') or '')} characters")
    
    # 3. Guardar como favorito
    print('\n3. Guardando prompt como favorito...')
    fav_payload = {
        'titulo': 'Sesión de fotos en estudio',
        'personaje': 'Modelo profesional',
        'prompt_es': data.get('prompt_es'),
        'prompt_en': data.get('prompt_en', ''),
        'prompt_video': data.get('prompt_video')
    }
    response2 = requests.post('http://localhost:8001/api/save-favorite', json=fav_payload, timeout=10)
    if response2.status_code == 200:
        print('✅ Favorito guardado correctamente')
    else:
        print(f'Warning: Status {response2.status_code}')
        print(f'Response: {response2.text[:200]}')
        
    # 4. Obtener favoritos
    print('\n4. Recuperando favoritos...')
    response3 = requests.get('http://localhost:8001/api/favorites', timeout=10)
    if response3.status_code == 200:
        favorites = response3.json()
        print(f'✅ {len(favorites)} favoritos recuperados')
    else:
        print(f'Warning: {response3.status_code}')
else:
    print(f'❌ Error generando prompt: {response.status_code}')

print('\n=== PRUEBA E2E COMPLETADA ===')
