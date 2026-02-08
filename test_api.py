import requests
import json

# Test 1: DEBUG
url = "http://localhost:8001/api/debug-prompts"
payload = {
    "idea": "Mujer sonriendo en la playa al atardecer",
    "style": "fotografia",
    "personajes": ["cony"]
}

print("=" * 70)
print("🧪 TEST 1: ENDPOINT DE DEBUG (Sin APIs reales)")
print("=" * 70)
print("🔄 URL:", url)
print("⏳ Esperando respuesta...")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Prompt ES: {data.get('prompt_es','')[:80]}...")
            print(f"   Modelo: {data.get('model_used')}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: OPENROUTER (Alternativa funcional)
print("\n" + "=" * 70)
print("🧪 TEST 2: ENDPOINT OPENROUTER (Alternativa funcional)")
print("=" * 70)
url_openrouter = "http://localhost:8001/api/prompts-openrouter"
print("🔄 URL:", url_openrouter)
print("⏳ Esperando respuesta (20-40 segundos)...")

try:
    response = requests.post(url_openrouter, json=payload, timeout=120)
    print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 RESPUESTA EXITOSA:")
            print(f"   Prompt ES: {data.get('prompt_es','')[:100]}...")
            print(f"   Prompt EN: {data.get('prompt_en','')[:100]}...")
            print(f"   Modelo: {data.get('model_used')}")
    else:
        print(f"❌ Error ({response.status_code}): {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 3: GEMINI (Requiere API key válida)
print("\n" + "=" * 70)
print("🧪 TEST 3: ENDPOINT GEMINI (Requiere API key válida)")
print("=" * 70)
url_gemini = "http://localhost:8001/api/generate-prompts"
print("🔄 URL:", url_gemini)
print("⚠️ Este endpoint requiere una API key de Gemini válida")
print("⏳ Esperando respuesta (puede fallar)...")

try:
    response = requests.post(url_gemini, json=payload, timeout=120)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ RESPUESTA EXITOSA:")
        print(f"   Modelo: {data['model_used']}")
    else:
        print(f"⚠️ Esperado (API key inválida): {response.status_code}")
except Exception as e:
    print(f"⚠️ Error esperado: {str(e)[:80]}")

# Test 4: PROMPTS FUNCIONAL (Mock avanzado)
print("\n" + "=" * 70)
print("🧪 TEST 4: ENDPOINT PROMPTS FUNCIONAL (Mock avanzado)")
print("=" * 70)
url_func = "http://localhost:8001/api/prompts-funcional"
print("🔄 URL:", url_func)
print("⏳ Esperando respuesta...")

try:
    response = requests.post(url_func, json=payload, timeout=30)
    print(f"✅ Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Prompt ES: {data['prompt_es'][:100]}...")
        print(f"   Modelo: {data['model_used']}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("✅ RECOMENDACIÓN: Usar /api/prompts-openrouter para generación real")
print("=" * 70)


