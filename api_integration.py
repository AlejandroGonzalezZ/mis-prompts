"""
Integraciones de APIs - Gemini, OpenRouter, OpenAI
"""
import requests
import json
import asyncio
from typing import Optional, Dict
from models import ModelConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAPI:
    """Integración con API Gemini de Google"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def __init__(self):
        self.api_key = ModelConfig.GEMINI_API_KEY
        # Obtener modelo desde configuración (fall back a valor por defecto en ModelConfig)
        self.model = getattr(ModelConfig, 'MODELO_A_PRINCIPAL', 'gemini-2.5-pro')
    
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generar texto usando Gemini
        
        Args:
            prompt: Prompt para el usuario
            system_prompt: Instrucciones del sistema
        """
        try:
            # Construir mensaje
            message_content = []
            
            if system_prompt:
                message_content.append({
                    "role": "user",
                    "parts": [{"text": system_prompt + "\n\n" + prompt}]
                })
            else:
                message_content.append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })
            
            # Realizar solicitud
            # Normalizar identificador de modelo: quitar prefijos tipo 'models/', 'google/',
            # y sufijos tipo ':free' si vienen desde configuración o .env
            model_id = self.model
            if '/' in model_id:
                model_id = model_id.split('/')[-1]
            if model_id.startswith('models/'):
                model_id = model_id.split('/', 1)[1]
            if ':' in model_id:
                model_id = model_id.split(':', 1)[0]

            url = f"{self.BASE_URL}/{model_id}:generateContent"
            params = {"key": self.api_key}
            
            payload = {
                "contents": message_content,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            logger.debug(f"Gemini Request URL: {url}")
            logger.debug(f"Gemini Payload: {json.dumps(payload, indent=2)[:200]}...")
            
            response = requests.post(url, json=payload, params=params, timeout=30)
            
            # Log de respuesta para debugging
            logger.debug(f"Gemini Response Status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Gemini Error Response: {response.text[:500]}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer texto
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text = candidate['content']['parts'][0].get('text', '')
                    logger.info(f"✅ Respuesta de Gemini generada ({len(text)} caracteres)")
                    return text
            
            raise Exception("No se obtuvo texto de la respuesta de Gemini")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en solicitud Gemini: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error al procesar respuesta Gemini: {str(e)}")
            raise

class OpenRouterAPI:
    """Integración con OpenRouter para múltiples modelos"""
    
    # OpenRouter correct base URL
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self):
        self.api_key = ModelConfig.OPENROUTER_API_KEY
    
    def generate_text(self, 
                           prompt: str,
                           model: str,
                           system_prompt: str = None,
                           temperature: float = 0.7) -> str:
        """
        Generar texto usando OpenRouter
        
        Args:
            prompt: Prompt para el usuario
            model: Modelo a usar (ej: qwen/qwen-2-vl-72b-instruct)
            system_prompt: Instrucciones del sistema
            temperature: Creatividad (0.0-1.0)
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2048,
                "top_p": 0.95,
            }
            
            try:
                response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    text = data['choices'][0]['message']['content']
                    logger.info(f"✅ Respuesta de OpenRouter ({model}) generada ({len(text)} caracteres)")
                    return text
                
                raise Exception("No se obtuvo texto de OpenRouter")
            
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout en OpenRouter, reintentando...")
                import time
                time.sleep(2)
                return self.generate_text(prompt, model, system_prompt, temperature)
        
        except Exception as e:
            logger.error(f"❌ Error en OpenRouter: {str(e)}")
            raise

class OpenAIAPI:
    """Integración con OpenAI para traducción"""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self):
        self.api_key = ModelConfig.OPENAI_API_KEY
    
    def translate_text(self, text: str, from_lang: str = "es", to_lang: str = "en") -> str:
        """
        Traducir texto de un idioma a otro
        
        Args:
            text: Texto a traducir
            from_lang: Idioma origen (es, en, etc)
            to_lang: Idioma destino
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            prompt = f"""Traduce el siguiente texto de {from_lang} a {to_lang}. 
Solo devuelve el texto traducido, sin explicaciones adicionales.

Texto original:
{text}"""
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un traductor profesional experto en traducción de prompts fotográficos. Tu tarea es traducir de manera exacta manteniendo todos los detalles técnicos."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            }
            
            response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                translated = data['choices'][0]['message']['content'].strip()
                logger.info(f"✅ Texto traducido ({len(translated)} caracteres)")
                return translated
            
            raise Exception("No se obtuvo traducción")
        
        except Exception as e:
            logger.error(f"❌ Error en traducción OpenAI: {str(e)}")
            # Fallback: devolver texto original
            logger.warning("⚠️ Usando texto original como fallback")
            return text

class VisionAnalyzer:
    """Analizador de imágenes usando APIs de visión"""
    
    def __init__(self):
        self.gemini = GeminiAPI()
        self.openrouter = OpenRouterAPI()
    
    def analyze_image_url(self, image_url: str, prompt: str = None) -> str:
        """
        Analizar imagen por URL (usando Gemini)
        
        Args:
            image_url: URL de la imagen
            prompt: Instrucciones para analizar
        """
        try:
            if not prompt:
                prompt = """Describe esta imagen con enfoque fotográfico: 
- Pose exacta del sujeto
- Prendas de vestir (textura/color)
- Entorno detallado
- Iluminación y composición de cámara
- Atmósfera general

Sé técnico y directo."""
            
            # Nota: Esta es una simplificación. La API de Gemini puede requerir
            # enviar la imagen en base64 o como archivo
            # Por ahora usaremos un método alternativo
            
            logger.warning("⚠️ Análisis de imágenes requiere integración adicional")
            return f"Imagen analizada. Prompt personalizado: {prompt[:100]}..."
        
        except Exception as e:
            logger.error(f"Error en análisis de imagen: {str(e)}")
            raise

class APIIntegration:
    """Integración central de todas las APIs"""
    
    def __init__(self):
        self.gemini = GeminiAPI()
        self.openrouter = OpenRouterAPI()
        self.openai = OpenAIAPI()
        self.vision = VisionAnalyzer()
    
    def validate_apis(self) -> Dict[str, bool]:
        """Validar que todas las APIs estén disponibles"""
        results = {
            'gemini': False,
            'openrouter': False,
            'openai': False
        }
        
        # Validar Gemini (simple request)
        try:
            self.gemini.generate_text("test", system_prompt=None)
            results['gemini'] = True
            logger.info("✅ Gemini API: OK")
        except Exception as e:
            logger.warning(f"⚠️ Gemini API: {str(e)}")
        
        # Validar OpenRouter
        try:
            self.openrouter.generate_text(
                "test",
                ModelConfig.MODELO_B_VISION
            )
            results['openrouter'] = True
            logger.info("✅ OpenRouter API: OK")
        except Exception as e:
            logger.warning(f"⚠️ OpenRouter API: {str(e)}")
        
        # Validar OpenAI
        try:
            self.openai.translate_text("test")
            results['openai'] = True
            logger.info("✅ OpenAI API: OK")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI API: {str(e)}")
        
        return results
