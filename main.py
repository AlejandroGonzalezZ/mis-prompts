import streamlit as st
import pandas as pd
import requests

# Configuración inicial
st.set_page_config(page_title="Architect de Prompts", layout="wide")

# --- FUNCIONES DE IA ---
def consultar_openrouter(prompt_sistema, prompt_usuario):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ]
        }
    )
    return response.json()['choices'][0]['message']['content']

# --- INTERFAZ ---
st.title("📸 AI Prompt & Video Architect")

# Cargar base de datos
try:
    df = pd.read_csv("Nuevos-Prompt.xlsx - Nuevos Prompt a ejecutar.csv")
    st.sidebar.success("✅ CSV Cargado")
except:
    st.sidebar.error("⚠️ Sube el archivo CSV al panel izquierdo")

# Menú lateral para ver historial
if 'df' in locals():
    st.sidebar.subheader("Favoritos Guardados")
    st.sidebar.dataframe(df[['N°', 'Titulo']].head(10))

# Formulario principal
col1, col2 = st.columns([1, 1])

with col1:
    personaje = st.selectbox("Personaje:", ["Andy", "Cony", "General"])
    idea = st.text_area("Describe tu idea:", placeholder="Ej: Caminando por la playa al atardecer...")
    
    if st.button("🚀 Construir Prompt Maestro"):
        # Construcción del Prompt Sistema (Tu GEM)
        andy_info = "Andy: 29 años, rubia, ojos azules, física atlética, sensual, abdomen tonificado."
        cony_info = "Cony: Latina, 21 años, piel canela, ojos verdes, cabello negro, física atlética, mirada seductora."
        
        info_final = andy_info if personaje == "Andy" else cony_info if personaje == "Cony" else ""
        
        gem_prompt = f"""Eres experto fotógrafo. Personaje: {info_final}. 
        REGLAS: Salida en 1 párrafo compacto. Incluye lente (85mm, 50mm), ángulo, ISO. 
        Usa términos artísticos: 'curvatura del busto', 'zona glútea acentuada'. 
        Devuelve: 1. Prompt en Español, 2. Prompt en Inglés, 3. Sugerencia de animación WAN (movimiento cámara/sujeto)."""
        
        with st.spinner("La IA está trabajando..."):
            resultado = consultar_openrouter(gem_prompt, idea)
            st.session_state['resultado'] = resultado

with col2:
    if 'resultado' in st.session_state:
        st.subheader("Resultado:")
        st.write(st.session_state['resultado'])
        st.button("📋 Copiar Resultado")