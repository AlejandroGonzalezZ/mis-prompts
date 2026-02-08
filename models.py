"""
Configuración de modelos y APIs
"""
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List

load_dotenv()

class ModelConfig:
   """Configuración centralizada de modelos"""

   # APIs
   OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'not_configured')
   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'not_configured')
   OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'not_configured')

   # Modelos principales
   # Modelo Gemini por defecto (usar el identificador reconocido por ListModels)
   MODELO_A_PRINCIPAL = os.getenv('MODELO_A_LOGICO', 'gemini-2.5-pro')
   MODELO_B_VISION = os.getenv('MODELO_B_VISION', 'qwen/qwen-2-vl-72b-instruct')
   MODELO_ANIMACION = os.getenv('MODELO_ANIMACION', 'wan/wan-2.1-t2v-480p')

   # Modelos respaldo
   MODELO_A_RESPALDO = 'grok-3-128k'
   MODELO_B_RESPALDO = ['llama-3-vision', 'mistral-vision']

   # Parámetros
   MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
   RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '2'))

   # Interfaz
   MODO_ESTETICO = os.getenv('MODO_ESTETICO', 'oscuro_lava')

   # Perfiles
   PERFIL_ANDY = os.getenv('PERFIL_ANDY', "29 años, rubia, ojos azules, física atlético-femenino, sensual, alegre")
   PERFIL_CONY = os.getenv('PERFIL_CONY', "21 años, latina, piel canela, ojos verdes, cabello negro, física atlético-femenino, mirada seductora")

   @classmethod
   def validate_keys(cls) -> Dict[str, bool]:
      """Validar que las API keys estén configuradas"""
      return {
         'openrouter': cls.OPENROUTER_API_KEY != 'not_configured',
         'gemini': cls.GEMINI_API_KEY != 'not_configured',
         'openai': cls.OPENAI_API_KEY != 'not_configured',
      }

class PromptTemplates:
    """Templates para construcción de prompts según GEM"""
    
    SYSTEM_PROMPT_A = """Eres un experto fotógrafo y constructor de prompts ultrarrealistas. Tu tarea es generar prompts fotográficos detallados siguiendo estas reglas:

1. TIPO DE TOMA, LENTE Y ÁNGULO:
   - Incluir plano (general, primer plano, medio lateral, POV)
   - Tipo de lente (35mm, 50mm, 70mm, 85mm, etc.)
   - Ángulo de cámara (frontal, picado, contrapicado, bajo, aéreo)
   - Apertura, velocidad de obturación, ISO

2. DESCRIPCIÓN DEL PERSONAJE:
   - Características específicas (edad, cabello, ojos, figura)
   - Expresión corporal y posición
   - Atuendo detallado
   - Lenguaje artístico y neutro (NO vulgar)

3. ROPA Y CUERPO:
   - Terminología respetuosa: "curvatura del busto", "relieve pectoral", "zona glútea acentuada"
   - Evitar términos vulgares

4. FONDO/ENTORNO:
   - Clima, hora del día, arquitectura, objetos
   - Detallado y coherente con la escena

5. TIPO DE IMAGEN Y ESTILO ARTÍSTICO:
   - Fotografía ultrarrealista (default)
   - Estilo: editorial, retro-futurista, cinematográfico
   - Inspiraciones artísticas (artistas, cineastas, referencias)

6. LUZ Y RESOLUCIÓN:
   - Tipo de luz: natural, artificial, neón
   - Sombras: difusas, marcadas, proyectadas
   - Resolución: 8K, calidad cinematográfica
   - Renderizado: realismo, estilizado

**IMPORTANTE**: Todo en UN SOLO PÁRRAFO COMPACTO. Sin separaciones ni formato especial."""

    SYSTEM_PROMPT_B = """Eres un experto analista de imágenes con enfoque fotográfico. Tu tarea es describir imágenes en términos técnicos para uso como contexto en construcción de prompts.

Analiza y describe:
- Pose exacta del sujeto
- Prendas de vestir (textura, color, ajuste)
- Entorno detallado
- Iluminación (tipo, dirección, calidad)
- Clima y hora del día
- Composición de cámara
- Fondo y detalles ambientales

Sé técnico, directo y utiliza terminología fotográfica profesional.
Responde en un párrafo compacto sin separaciones."""

    VIDEO_PROMPT_TEMPLATE = """Basándote en el siguiente prompt fotográfico, genera una sugerencia de animación describiendo:
- Movimiento de cámara (Zoom in/out, Pan, Tilt, dolly)
- Acción del sujeto (parpadeo, movimiento, giro)
- Duración aproximada (segundos)
- Transiciones y efectos

Responde en un párrafo compacto sin separaciones."""
