import requests, json
import time

print("=" * 60)
print("PRUEBA DE FALLBACK: Gemini → OpenRouter")
print("=" * 60)

time.sleep(2)  # Esperar a que servidor esté listo

payload = {
    'idea': 'Una chica en la playa al atardecer',
    'style': 'fotografia',
    'personajes': ['ninguno']
}

print(f"\n📤 Enviando request a /api/generate-prompts...")
print(f"   Idea: {payload['idea']}")

r = requests.post('http://localhost:8001/api/generate-prompts', json=payload, timeout=60)

print(f"\n📥 Respuesta del servidor:")
print(f"   Status: {r.status_code}")

data = r.json()
print(f"   Success: {data.get('success')}")
print(f"   Model Info: {data.get('model_info')}")
print(f"   Model Used: {data.get('model_used')}")
print(f"   Prompt ES length: {len(data.get('prompt_es', ''))} chars")
print(f"   Prompt EN length: {len(data.get('prompt_en', '') or '')} chars")

if "failed" in str(data.get('model_info', '')).lower() or "fallback" in str(data.get('model_info', '')).lower():
    print(f"\n✅ FALLBACK FUE EJECUTADO - El endpoint capturó el error de Gemini y usó OpenRouter")
else:
    print(f"\n⚠️ No hay indicación de fallback en model_info")

print(f"\n📄 Primeras 150 chars del prompt (ES):")
print(f"   {data.get('prompt_es', '')[:150]}...")
