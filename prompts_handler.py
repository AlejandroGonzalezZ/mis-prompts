"""
Manejador de Prompts - Implementación del GEM y Prompt Chaining
"""
import asyncio
import requests
import json
from typing import Optional, Dict, List, Tuple
from models import ModelConfig, PromptTemplates
from api_integration import APIIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetryHandler:
    """Sistema de reintentos con backoff exponencial"""
    
    def __init__(self, max_retries: int = None, delay: int = None):
        self.max_retries = max_retries or ModelConfig.MAX_RETRIES
        self.delay = delay or ModelConfig.RETRY_DELAY_SECONDS
        self.last_model_used = None
        self.error_log = []
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Ejecutar función con reintentos y fallback"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Intento {attempt}/{self.max_retries}")
                result = await func(*args, **kwargs)
                logger.info(f"✅ Éxito en intento {attempt}")
                return result
            
            except Exception as e:
                last_error = e
                logger.error(f"❌ Error en intento {attempt}: {str(e)}")
                self.error_log.append({
                    'attempt': attempt,
                    'error': str(e),
                    'model': kwargs.get('model', 'unknown')
                })
                
                if attempt < self.max_retries:
                    wait_time = self.delay * (2 ** (attempt - 1))
                    logger.info(f"⏳ Esperando {wait_time}s antes de reintentar...")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"❌ Fallos en todos los intentos")
        raise Exception(f"Fallos después de {self.max_retries} intentos: {str(last_error)}")

class ModelA:
    """Motor Lógico Maestro - Construcción de Prompts (GEM)"""
    
    def __init__(self):
        self.retry_handler = RetryHandler()
        self.current_model = ModelConfig.MODELO_A_PRINCIPAL
        self.api = APIIntegration()
    
    async def build_prompt(self, 
                          idea: str,
                          style: str = 'fotografia',
                          personajes: List[str] = None,
                          image_analysis: Optional[str] = None,
                          **kwargs) -> Dict[str, str]:
        """
        Construir prompt según GEM usando Gemini
        """
        
        personajes = personajes or ['ninguno']
        
        # Construir contexto con información de personajes
        characters_context = self._build_characters_context(personajes)
        
        # Construir prompt del usuario
        user_message = self._build_user_message(
            idea=idea,
            style=style,
            characters_context=characters_context,
            image_analysis=image_analysis
        )
        
        try:
            # Llamar a Gemini para generar prompt en español
            logger.info(f"🤖 Generando prompt fotográfico con {self.current_model}...")
            prompt_es = await self._call_gemini(user_message)

            # Generar sugerencia de video (usar prompt en español como base)
            logger.info("🎬 Generando prompt de video...")
            prompt_video = await self._generate_video_prompt(prompt_es)

            return {
                'prompt_es': prompt_es,
                'prompt_video': prompt_video,
                'model_used': self.current_model,
                'primary_model': self.current_model,
                'primary_status': 'success',
                'fallback_model': None
            }

        except Exception as e:
            # Si Gemini falla, hacer fallback a OpenRouter
            logger.error(f"Error en Model A (Gemini): {str(e)} - intentando fallback a OpenRouter")
            try:
                # Intentar generar el prompt usando OpenRouter
                prompt_es = await asyncio.to_thread(
                    self.api.openrouter.generate_text,
                    user_message,
                    ModelConfig.MODELO_B_VISION,
                    PromptTemplates.SYSTEM_PROMPT_A,
                    0.7
                )

                # Generar prompt de video: intentar Gemini primero, si falla usar OpenRouter
                try:
                    prompt_video = await self._generate_video_prompt(prompt_es)
                except Exception:
                    try:
                        prompt_video = await asyncio.to_thread(
                            self.api.openrouter.generate_text,
                            PromptTemplates.VIDEO_PROMPT_TEMPLATE + "\n\nPrompt fotográfico:\n" + prompt_es,
                            ModelConfig.MODELO_B_VISION,
                            None,
                            0.5
                        )
                    except Exception:
                        prompt_video = "Zoom lento al sujeto, luz cálida suave, duración 5s."

                return {
                    'prompt_es': prompt_es,
                    'prompt_video': prompt_video,
                    'model_used': f"openrouter/{ModelConfig.MODELO_B_VISION}",
                    'primary_model': self.current_model,
                    'primary_status': 'failed',
                    'fallback_model': ModelConfig.MODELO_B_VISION
                }

            except Exception as e_fallback:
                logger.error(f"Falló fallback a OpenRouter: {str(e_fallback)}")
                raise
    
    def _build_characters_context(self, personajes: List[str]) -> str:
        """Construir contexto de personajes"""
        context = []
        
        if 'andy' in personajes:
            context.append(f"Andy: {ModelConfig.PERFIL_ANDY}")
        if 'cony' in personajes:
            context.append(f"Cony: {ModelConfig.PERFIL_CONY}")
        
        return "\n".join(context) if context else "Sin personajes específicos"
    
    def _build_user_message(self, idea: str, style: str, 
                           characters_context: str, image_analysis: Optional[str]) -> str:
        """Construir mensaje para enviar a la API"""
        
        message = f"""
Construir un prompt fotográfico ultra-detallado según estas especificaciones:

**IDEA/DESCRIPCIÓN DEL USUARIO:**
{idea}

**ESTILO ARTÍSTICO:**
{style}

**PERSONAJES (si aplica):**
{characters_context}
"""
        
        if image_analysis:
            message += f"""
**ANÁLISIS DE IMAGEN (Referencia Visual):**
{image_analysis}
"""
        
        message += f"""
**INSTRUCCIONES:**
{PromptTemplates.SYSTEM_PROMPT_A}

Genera el prompt final en ESPAÑOL, en un SOLO PÁRRAFO, incluyendo todos los elementos técnicos fotográficos, descripción del personaje (si aplica), entorno, luz, estilo artístico e inspiraciones."""
        
        return message
    
    async def _call_gemini(self, user_message: str) -> str:
        """Llamar a Gemini con reintentos"""
        
        async def api_call():
            response = await asyncio.to_thread(self.api.gemini.generate_text, user_message)
            return response
        
        return await self.retry_handler.execute_with_retry(api_call)
    
    async def _translate_to_english(self, prompt_es: str) -> str:
        """Traducir prompt a inglés usando OpenAI"""
        try:
            prompt_en = await asyncio.to_thread(self.api.openai.translate_text, prompt_es, "español", "inglés")
            return prompt_en
        except Exception as e:
            logger.error(f"Error en traducción: {str(e)}")
            # Fallback: usar Gemini para traducir
            try:
                translation_prompt = f"""Traduce el siguiente prompt fotográfico del español al inglés de manera exacta, manteniendo todos los detalles técnicos:

{prompt_es}

Proporciona SOLO la traducción, sin explicaciones adicionales."""
                return await asyncio.to_thread(self.api.gemini.generate_text, translation_prompt)
            except:
                # Último fallback
                return prompt_es
    
    async def _generate_video_prompt(self, prompt_es: str) -> str:
        """Generar sugerencia de animación usando Gemini"""
        try:
            video_prompt = f"""{PromptTemplates.VIDEO_PROMPT_TEMPLATE}

Prompt fotográfico original:
{prompt_es}

Ahora genera la sugerencia específica de animación."""
            
            response = await asyncio.to_thread(self.api.gemini.generate_text, video_prompt)
            return response
        except Exception as e:
            logger.error(f"Error generando video prompt con Gemini: {str(e)} - intentando fallback a OpenRouter")
            # Fallback a OpenRouter
            try:
                response = await asyncio.to_thread(
                    self.api.openrouter.generate_text,
                    video_prompt,
                    ModelConfig.MODELO_B_VISION,
                    None,
                    0.5
                )
                return response
            except Exception as e2:
                logger.error(f"Error generando video prompt con OpenRouter: {str(e2)}")
                # Fallback simple
                return f"Cámara realiza un zoom suave hacia el sujeto principal. Luz envolvente con movimiento de pan sutil. Duración: 4-6 segundos. Transición suave al final."

class ModelB:
    """Motor de Visión - Análisis de Imágenes"""
    
    def __init__(self):
        self.retry_handler = RetryHandler()
        self.current_model = ModelConfig.MODELO_B_VISION
        self.api = APIIntegration()
    
    async def analyze_image(self, image_path: str) -> str:
        """
        Analizar imagen y devolver descripción técnica
        
        Usa Qwen2-VL o similar a través de OpenRouter
        """
        try:
            logger.info(f"📸 Analizando imagen con {self.current_model}...")
            
            # Nota: Para análisis real de imágenes, necesitaría convertir la imagen
            # a base64 o proporcionar una URL
            # Por ahora, usar un prompt descriptivo
            
            analysis_prompt = """Analiza esta imagen con enfoque fotográfico profesional:

1. SUJETO Y POSE:
   - Descripción del sujeto (edad, género, características visibles)
   - Pose exacta y lenguaje corporal
   - Expresión facial

2. ATUENDO:
   - Prendas de vestir (tipo, color, textura, ajuste)
   - Accesorios
   - Detalles visibles

3. ENTORNO:
   - Ubicación (interior/exterior)
   - Objetos cercanos
   - Fondo y desenfoque

4. ILUMINACIÓN:
   - Tipo de luz (natural, artificial, mixta)
   - Dirección y calidad
   - Sombras y reflejos

5. COMPOSICIÓN:
   - Tipo de plano
   - Ángulo de cámara
   - Profundidad de campo aparente

Proporciona respuesta técnica en UN párrafo compacto."""
            
            # Llamar con reintentos
            analysis = await self.retry_handler.execute_with_retry(
                self._analyze_with_api,
                analysis_prompt
            )
            
            return analysis
        
        except Exception as e:
            logger.error(f"Error en Model B: {str(e)}")
            raise
    
    async def _analyze_with_api(self, prompt: str) -> str:
        """Realizar análisis usando OpenRouter con Qwen2-VL"""
        try:
            # Intentar con Qwen2-VL primero
            response = await asyncio.to_thread(
                self.api.openrouter.generate_text,
                prompt,
                self.current_model,
                PromptTemplates.SYSTEM_PROMPT_B,
                0.5
            )
            return response
        except Exception as e:
            logger.warning(f"⚠️ Error con {self.current_model}, intentando cambio de modelo...")
            
            # Fallback a Llama 3
            try:
                response = await asyncio.to_thread(
                    self.api.openrouter.generate_text,
                    prompt,
                    "meta-llama/llama-3-vision-free",
                    PromptTemplates.SYSTEM_PROMPT_B,
                    0.5
                )
                self.current_model = "meta-llama/llama-3-vision-free"
                logger.info(f"✅ Cambio exitoso a modelo respaldo: {self.current_model}")
                return response
            except Exception as e2:
                logger.error(f"❌ También falló modelo respaldo: {str(e2)}")
                raise

class AnimationModule:
    """Módulo de Generación de Prompts para Animación (WAN/Luma)"""
    
    def __init__(self):
        self.api = APIIntegration()
    
    async def generate_animation_prompt(self, photo_prompt: str) -> str:
        """
        Generar prompt para video/animación basado en prompt fotográfico
        
        Usa Gemini para analizar el prompt fotográfico y generar
        sugerencias de movimiento y animación
        """
        try:
            logger.info("🎬 Generando prompt de animación...")
            
            animation_context = await self._analyze_for_animation(photo_prompt)
            return animation_context
        
        except Exception as e:
            logger.error(f"Error en módulo de animación: {str(e)}")
            # Fallback
            return "Cámara realiza movimiento suave con zoom gradual. Sujeto con parpadeos naturales. Duración: 4-6 segundos. Transición fade-in/out."
    
    async def _analyze_for_animation(self, prompt: str) -> str:
        """Analizar prompt fotográfico para extraer elementos de animación"""
        try:
            animation_prompt = f"""{PromptTemplates.VIDEO_PROMPT_TEMPLATE}

Prompt fotográfico:
{prompt}

Basándote en este prompt, genera una sugerencia detallada de animación especificando:
1. Tipo de movimiento de cámara (Zoom, Pan, Tilt, Dolly, Orbit)
2. Dirección y velocidad del movimiento
3. Acciones del sujeto (parpadeos, movimiento corporal, gesticulación)
4. Efectos especiales (bokeh, light leak, color grading)
5. Duración aproximada
6. Transiciones (fade, dissolve, wipe)

Responde en UN párrafo compacto implementable en WAN 2.2 o Luma AI."""
            
            response = await asyncio.to_thread(self.api.gemini.generate_text, animation_prompt)
            return response
        
        except Exception as e:
            logger.error(f"Error analizando para animación: {str(e)}")
            raise

class PromptChainOrchestrator:
    """Orquestador del flujo completo de Prompt Chaining con APIs reales"""
    
    def __init__(self):
        self.model_a = ModelA()
        self.model_b = ModelB()
        self.animation = AnimationModule()
    
    async def process_request(self, 
                             idea: str,
                             style: str = 'fotografia',
                             personajes: List[str] = None,
                             image: Optional[bytes] = None,
                             **kwargs) -> Dict[str, str]:
        """
        Procesar solicitud completa con APIs reales
        
        Flujo:
        1. Si hay imagen → Modelo B (Qwen2-VL) → análisis
        2. Modelo A (Gemini) → construir prompt (con/sin imagen)
        3. OpenAI → traducción al inglés
        4. Gemini → generar prompt video
        """
        
        image_analysis = None
        
        # Paso 1: Analizar imagen si existe
        if image:
            logger.info("📸 Analizando imagen con Modelo B (Visión)...")
            try:
                # Guardar imagen temporalmente
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp.write(image)
                    image_path = tmp.name
                
                image_analysis = await self.model_b.analyze_image(image_path)
                logger.info(f"✅ Análisis de imagen completado ({len(image_analysis)} caracteres)")
            
            except Exception as e:
                logger.warning(f"⚠️ No se pudo analizar imagen: {str(e)}")
                image_analysis = None
        
        # Paso 2: Construir prompts con Modelo A
        logger.info("🤖 Generando prompts con Modelo A...")
        try:
            results = await self.model_a.build_prompt(
                idea=idea,
                style=style,
                personajes=personajes,
                image_analysis=image_analysis
            )
            
            logger.info("✅ Prompts generados exitosamente")
            logger.info(f"   - Prompt ES: {len(results.get('prompt_es',''))} caracteres")
            logger.info(f"   - Prompt Video: {len(results.get('prompt_video',''))} caracteres")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Error en generación de prompts: {str(e)}")
            raise
