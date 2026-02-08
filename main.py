"""
Servidor FastAPI - Estación de Trabajo para Generación de Prompts IA
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging
from prompts_handler import PromptChainOrchestrator
from csv_handler import CSVHandler
from models import ModelConfig
from api_integration import APIIntegration
import uvicorn
import os

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando servidor...")
    logger.info(f"Versión: 1.0.0")
    logger.info(f"Modelo A (Lógico): {ModelConfig.MODELO_A_PRINCIPAL}")
    logger.info(f"Modelo B (Visión): {ModelConfig.MODELO_B_VISION}")
    logger.info("✅ Servidor listo")
    try:
        yield
    finally:
        logger.info("🛑 Apagando servidor...")


app = FastAPI(
    title="Estación de Trabajo IA - Generador de Prompts",
    description="API para generar prompts fotográficos y de animación con IA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: configurar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar módulos
orchestrator = PromptChainOrchestrator()
csv_handler = CSVHandler()
api_integration = APIIntegration()

# ============== MODELOS PYDANTIC ==============

class PromptRequest(BaseModel):
    """Solicitud para generar prompts"""
    idea: str
    style: str = "fotografia"
    personajes: List[str] = ["ninguno"]

class PromptResponse(BaseModel):
    """Respuesta de generación de prompts"""
    prompt_es: str
    prompt_en: Optional[str] = None
    prompt_video: str
    model_used: str
    model_info: Optional[str] = None
    success: bool = True
    message: str = "Prompts generados exitosamente"

class SaveFavoriteRequest(BaseModel):
    """Solicitud para guardar en favoritos"""
    titulo: str
    personaje: str
    prompt_es: str
    prompt_en: Optional[str] = None
    prompt_video: str

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    error: str
    details: Optional[dict] = None

# ============== ENDPOINTS ==============

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz - Health check"""
    keys_valid = ModelConfig.validate_keys()
    
    return {
        "status": "online",
        "version": "1.0.0",
        "message": "Estación de Trabajo IA - Generador de Prompts",
        "keys_configured": keys_valid,
        "ready": all(keys_valid.values())
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para health check rápido"""
    return {
        "status": "healthy",
        "database": "connected",
        "message": "✅ Servidor IA - Estación de Trabajo"
    }

@app.post("/api/debug-prompts", 
          response_model=PromptResponse,
          tags=["Debug"],
          summary="Debug - Generar prompts sin APIs reales")
async def debug_prompts(request: PromptRequest):
    """Endpoint de depuración que devuelve prompts mockificados sin llamar APIs"""
    try:
        logger.info(f"🔧 DEBUG - Idea: {request.idea[:50]}...")
        
        # Respuesta mockeada para testing
        return PromptResponse(
            prompt_es=f"""Fotografía ultrarrealista de {request.idea}. 
Técnica profesional, iluminación cinematográfica, bokeh fino, composición equilibrada, 
saturación natural, contraste suave. Estilo: {request.style}. 
Calidad de retrato profesional, 85mm macro, f/1.8 aperture.""",
            
            prompt_en=f"""Ultrarealistic photograph of {request.idea}. 
Professional technique, cinematic lighting, fine bokeh, balanced composition, 
natural saturation, soft contrast. Style: {request.style}. 
Professional portrait quality, 85mm macro, f/1.8 aperture.""",
            
            prompt_video=f"""Camera slowly zooms in on subject. Warm sunset light with subtle shadow movement. 
Smooth pan from left to right. Duration: 5 seconds. Subject shows gentle emotion transition. 
Fade transition at end. Suitable for WAN 2.2 or Luma AI generation.""",
            
            model_used="debug-mock",
            success=True,
            message="Debug response - APIs not called"
        )
    except Exception as e:
        logger.error(f"Error en debug: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/prompts-openrouter",
          response_model=PromptResponse,
          tags=["Prompts"],
          summary="Generar prompts usando OpenRouter (alternativa)")
async def generate_prompts_openrouter(request: PromptRequest):
    """
    Generar prompts usando OpenRouter con Mistral/Llama
    
    Esta es una alternativa si Gemini no funciona
    """
    try:
        logger.info(f"📝 OpenRouter - Idea: {request.idea[:50]}...")
        
        if not request.idea or len(request.idea.strip()) == 0:
            raise HTTPException(status_code=400, detail="La idea no puede estar vacía")
        
        # Construir prompt para OpenRouter
        prompt = f"""Eres un experto en fotografía profesional y generación de prompts para IA.
        
El usuario quiere que generes un prompt fotográfico detallado.

Idea del usuario: {request.idea}
Estilo: {request.style}

Por favor, genera:
1. Un prompt fotográfico en ESPAÑOL detallado (máximo 200 palabras)
2. La traducción al INGLÉS
3. Una sugerencia de movimiento de cámara para animación

Formato tu respuesta así:
PROMPT_ES:
[aquí el prompt en español]

PROMPT_EN:
[aquí el prompt en inglés]

PROMPT_VIDEO:
[aquí la sugerencia de movimiento]"""

        # Llamar a OpenRouter
        response = api_integration.openrouter.generate_text(
            prompt,
            ModelConfig.MODELO_B_VISION,  # Usar modelo configurado
        )
        
        # Parsear respuesta
        parts = response.split("PROMPT_ES:")
        if len(parts) > 1:
            rest = parts[1]
            
            es_part = rest.split("PROMPT_EN:")[0].strip() if "PROMPT_EN:" in rest else ""
            
            en_part = rest.split("PROMPT_EN:")[1] if "PROMPT_EN:" in rest else ""
            en_part = en_part.split("PROMPT_VIDEO:")[0].strip() if "PROMPT_VIDEO:" in en_part else ""
            
            video_part = en_part
            if "PROMPT_VIDEO:" in rest:
                video_part = rest.split("PROMPT_VIDEO:")[1].strip()
        else:
            es_part = response[:200]
            en_part = response[200:400]
            video_part = response[400:600]
        
        return PromptResponse(
            prompt_es=es_part or response[:150],
            prompt_en=en_part or response[150:300],
            prompt_video=video_part or "Zoom lento al sujeto, luz cálida suave, duración 5s.",
            model_used=f"openrouter/{ModelConfig.MODELO_B_VISION}",
            model_info=f"Primary: OpenRouter ({ModelConfig.MODELO_B_VISION})",
            success=True,
            message="Generado con OpenRouter"
        )
    
    except Exception as e:
        logger.error(f"Error en OpenRouter: {str(e)}")
        # Devolver respuesta de error en lugar de raise exception
        return PromptResponse(
            prompt_es=f"Error generando prompt: {str(e)[:100]}",
            prompt_en=f"Error generating prompt: {str(e)[:100]}",
            prompt_video="Error generando animación",
            model_used="error",
            model_info="Primary: OpenRouter (failed)",
            success=False,
            message=f"Error en OpenRouter: {str(e)[:100]}"
        )

@app.post("/api/prompts-funcional",
          response_model=PromptResponse,
          tags=["Prompts"],
          summary="Generar prompts funcional (mock avanzado)")
async def generate_prompts_funcional(request: PromptRequest):
    """
    Genera prompts de forma funcional usando plantillas avanzadas.
    No requiere llamadas a APIs externas; útil para desarrollo y pruebas.
    """
    try:
        logger.info(f"✨ FUNCIONAL - Idea: {request.idea[:50]}...")

        if not request.idea or len(request.idea.strip()) == 0:
            raise HTTPException(status_code=400, detail="La idea no puede estar vacía")

        # Mapeo de estilos a etiquetas legibles
        style_map = {
            "fotografia": "Fotografía profesional",
            "ilustracion": "Ilustración digital",
            "arte_digital": "Arte digital",
            "acuarela": "Acuarela",
            "default": "Composición visual"
        }
        style_label = style_map.get(request.style, style_map["default"]) 

        # Construcción del prompt en español (más detallado)
        prompt_es = f"""{style_label} de {request.idea}.
Composición cuidada, iluminación cinematográfica, balance cromático, texturas definidas.
Objetivo: transmitir emoción y narrativa visual. Técnicas: profundidad de campo pronunciada,
uso de lente 85mm, apertura amplia (f/1.8-f/2.8), iluminación dorada al atardecer.
Inspira: fotografía editorial y cinematográfica. Mantener tono realista y detallado."""

        # Versión en inglés
        prompt_en = f"""{style_label} of {request.idea}.
Careful composition, cinematic lighting, balanced color grading, defined textures.
Goal: convey emotion and visual narrative. Techniques: pronounced depth of field,
85mm lens, wide aperture (f/1.8-f/2.8), golden hour lighting.
Inspired by editorial and cinematic photography. Keep realistic, rich in detail."""

        # Sugerencia de animación implementable
        prompt_video = f"""Camera: slow dolly-in combined with gentle left-to-right pan.
Lighting: warm golden hour key with soft rim light. Motion: subject breathes and slight head tilt.
Effects: subtle bokeh and light leak, color grade warm with slight teal shadows.
Duration: 6 seconds. Transition: soft dissolve to black. Compatible with Luma/WAN workflows."""

        return PromptResponse(
            prompt_es=prompt_es,
            prompt_en=prompt_en,
            prompt_video=prompt_video,
            model_used="mock-funcional-local",
            success=True,
            message="Generado localmente (mock funcional)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en funcional: {str(e)}")
        return PromptResponse(
            prompt_es="Error generando prompt",
            prompt_en="Error generating prompt",
            prompt_video="Error",
            model_used="error",
            success=False,
            message=f"Error: {str(e)[:100]}"
        )

@app.post("/api/generate-prompts", 
          response_model=PromptResponse,
          tags=["Prompts"],
          summary="Generar prompts fotográficos",
          responses={
              200: {"description": "Prompts generados exitosamente"},
              400: {"description": "Solicitud inválida"},
              500: {"description": "Error del servidor"}
          })
async def generate_prompts(request: PromptRequest):
    """
    Generar prompts fotográficos y de animación
    
    **Parámetros:**
    - `idea` (str): Descripción o idea del usuario
    - `style` (str): Estilo - fotografia, ilustracion, arte_digital, acuarela
    - `personajes` (list): Lista de personajes - andy, cony, ambos, ninguno
    
    **Respuesta:**
    - `prompt_es`: Prompt en español
    - `prompt_en`: Prompt en inglés
    - `prompt_video`: Sugerencia de animación
    """
    try:
        logger.info(f"📝 Solicitud recibida - Idea: {request.idea[:50]}...")
        
        # Validar entrada
        if not request.idea or len(request.idea.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="La idea no puede estar vacía"
            )
        
        # Procesar con el orquestador
        results = await orchestrator.process_request(
            idea=request.idea,
            style=request.style,
            personajes=request.personajes
        )
        
        logger.info("✅ Prompts generados exitosamente")
        
        # Construir información clara de modelos usados (primary/fallback)
        primary = results.get('primary_model')
        pstatus = results.get('primary_status')
        fallback = results.get('fallback_model')
        if primary:
            model_info = f"Primary: {primary} ({pstatus})"
            if fallback:
                model_info += f" — Fallback: {fallback}"
        else:
            model_info = results.get('model_used', 'unknown')

        return PromptResponse(
            prompt_es=results.get('prompt_es', ''),
            prompt_en=results.get('prompt_en', ''),
            prompt_video=results.get('prompt_video', ''),
            model_used=results.get('model_used', 'unknown'),
            model_info=model_info,
            success=True,
            message="Prompts generados exitosamente"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al generar prompts con Gemini: {str(e)}")
        logger.info("⚠️ Ejecutando fallback directo a OpenRouter desde endpoint...")
        try:
            # Fallback directo a OpenRouter sin pasar por ModelA
            prompt = f"""Eres un experto en fotografía profesional y generación de prompts para IA.

El usuario quiere que generes un prompt fotográfico detallado.

Idea del usuario: {request.idea}
Estilo: {request.style}

Por favor, genera:
1. Un prompt fotográfico en ESPAÑOL detallado (máximo 200 palabras)
2. La traducción al INGLÉS
3. Una sugerencia de movimiento de cámara para animación

Formato tu respuesta así:
PROMPT_ES:
[aquí el prompt en español]

PROMPT_EN:
[aquí el prompt en inglés]

PROMPT_VIDEO:
[aquí la sugerencia de movimiento]"""
            
            response = api_integration.openrouter.generate_text(
                prompt,
                ModelConfig.MODELO_B_VISION,
                temperature=0.7
            )
            
            # Parsear respuesta
            parts = response.split("PROMPT_ES:")
            if len(parts) > 1:
                rest = parts[1]
                es_part = rest.split("PROMPT_EN:")[0].strip() if "PROMPT_EN:" in rest else ""
                en_part = rest.split("PROMPT_EN:")[1] if "PROMPT_EN:" in rest else ""
                en_part = en_part.split("PROMPT_VIDEO:")[0].strip() if "PROMPT_VIDEO:" in en_part else ""
                video_part = rest.split("PROMPT_VIDEO:")[1].strip() if "PROMPT_VIDEO:" in rest else "Zoom lento al sujeto, luz cálida suave, duración 5s."
            else:
                es_part = response[:200]
                en_part = response[200:400]
                video_part = response[400:600]
            
            model_info = f"Primary: {ModelConfig.MODELO_A_PRINCIPAL} (failed) — Fallback: {ModelConfig.MODELO_B_VISION}"
            
            logger.info(f"✅ Fallback exitoso a OpenRouter. Model info: {model_info}")
            
            return PromptResponse(
                prompt_es=es_part or response[:150],
                prompt_en=en_part or response[150:300],
                prompt_video=video_part or "Zoom lento al sujeto, luz cálida suave, duración 5s.",
                model_used=f"openrouter/{ModelConfig.MODELO_B_VISION}",
                model_info=model_info,
                success=True,
                message="Generado con fallback OpenRouter"
            )
        except Exception as fallback_e:
            logger.error(f"❌ Falló fallback a OpenRouter: {str(fallback_e)}")
            return PromptResponse(
                prompt_es=f"Error: Fallos en ambos modelos. {str(fallback_e)[:100]}",
                prompt_en=f"Error: Both models failed. {str(fallback_e)[:100]}",
                prompt_video="Error",
                model_used="error",
                success=False,
                message=f"Error: {str(fallback_e)[:150]}"
            )

@app.post("/api/generate-with-image",
          response_model=PromptResponse,
          tags=["Prompts"],
          summary="Generar prompts con imagen de referencia")
async def generate_prompts_with_image(
    idea: str,
    style: str = "fotografia",
    personajes: List[str] = ["ninguno"],
    image: Optional[UploadFile] = File(None)
):
    """
    Generar prompts usando imagen como referencia
    
    El Modelo B analizará la imagen y el Modelo A la usará como contexto
    """
    try:
        logger.info(f"📸 Solicitud con imagen - Idea: {idea[:50]}...")
        
        if not idea or len(idea.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="La idea no puede estar vacía"
            )
        
        # Procesar imagen si existe
        image_bytes = None
        if image:
            image_bytes = await image.read()
            logger.info(f"📷 Imagen cargada: {len(image_bytes)} bytes")
        
        # Procesar solicitud
        results = await orchestrator.process_request(
            idea=idea,
            style=style,
            personajes=personajes,
            image=image_bytes
        )
        
        logger.info("✅ Prompts con imagen generados")
        
        return PromptResponse(
            prompt_es=results.get('prompt_es', ''),
            prompt_en=results.get('prompt_en', ''),
            prompt_video=results.get('prompt_video', ''),
            model_used=results.get('model_used', 'unknown'),
            success=True,
            message="Prompts generados con análisis de imagen"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar: {str(e)}"
        )

@app.post("/api/save-favorite",
          tags=["Favoritos"],
          summary="Guardar prompt en favoritos")
async def save_favorite(request: SaveFavoriteRequest):
    """Guardar un prompt generado en la base de datos de favoritos (CSV)"""
    try:
        logger.info(f"⭐ Guardando favorito: {request.titulo}")
        
        result = csv_handler.add_prompt(
            titulo=request.titulo,
            personaje=request.personaje,
            prompt_es=request.prompt_es,
            prompt_en=request.prompt_en,
            prompt_video=request.prompt_video
        )
        
        if result['success']:
            logger.info(f"✅ Favorito guardado: {result['id']}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error al guardar favorito: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.get("/api/favorites",
         tags=["Favoritos"],
         summary="Obtener todos los favoritos")
async def get_favorites():
    """Obtener lista completa de prompts favoritos"""
    try:
        logger.info("📋 Obteniendo todos los favoritos")
        
        prompts = csv_handler.get_all_prompts()
        
        return {
            'success': True,
            'count': len(prompts),
            'data': prompts
        }
    
    except Exception as e:
        logger.error(f"Error al obtener favoritos: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }

@app.get("/api/favorites/search",
         tags=["Favoritos"],
         summary="Buscar en favoritos")
async def search_favorites(query: str):
    """
    Buscar prompts por palabra clave
    
    **Parámetros:**
    - `query` (str): Palabra clave a buscar
    """
    try:
        if not query or len(query.strip()) == 0:
            return {
                'success': False,
                'error': 'La búsqueda no puede estar vacía',
                'data': []
            }
        
        logger.info(f"🔍 Buscando: {query}")
        
        results = csv_handler.search_prompts(query)
        
        return {
            'success': True,
            'query': query,
            'count': len(results),
            'data': results
        }
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }

@app.get("/api/favorites/{prompt_id}",
         tags=["Favoritos"],
         summary="Obtener un favorito específico")
async def get_favorite(prompt_id: str):
    """Obtener detalles de un prompt por ID"""
    try:
        logger.info(f"📖 Obteniendo prompt: {prompt_id}")
        
        prompt = csv_handler.get_prompt_by_id(prompt_id)
        
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt no encontrado"
            )
        
        return {
            'success': True,
            'data': prompt
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.delete("/api/favorites/{prompt_id}",
            tags=["Favoritos"],
            summary="Eliminar un favorito")
async def delete_favorite(prompt_id: str):
    """Eliminar un prompt de favoritos"""
    try:
        logger.info(f"🗑️ Eliminando prompt: {prompt_id}")
        
        result = csv_handler.delete_prompt(prompt_id)
        
        return result
    
    except Exception as e:
        logger.error(f"Error al eliminar: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.get("/api/favorites/stats",
         tags=["Estadísticas"],
         summary="Obtener estadísticas")
async def get_stats():
    """Obtener estadísticas de prompts guardados"""
    try:
        logger.info("📊 Obteniendo estadísticas")
        
        stats = csv_handler.get_stats()
        
        return {
            'success': True,
            'stats': stats
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.get("/api/config",
         tags=["Configuración"],
         summary="Obtener configuración actual")
async def get_config():
    """Obtener configuración del servidor (sin exponer secrets)"""
    return {
        'modelo_a': ModelConfig.MODELO_A_PRINCIPAL,
        'modelo_b': ModelConfig.MODELO_B_VISION,
        'modelo_animacion': ModelConfig.MODELO_ANIMACION,
        'max_retries': ModelConfig.MAX_RETRIES,
        'retry_delay': ModelConfig.RETRY_DELAY_SECONDS,
        'perfil_andy': ModelConfig.PERFIL_ANDY,
        'perfil_cony': ModelConfig.PERFIL_CONY
    }

# ============== ERROR HANDLERS ==============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador personalizado de excepciones HTTP"""
    return {
        'success': False,
        'error': exc.detail,
        'status_code': exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador general de excepciones"""
    logger.error(f"Excepción no manejada: {str(exc)}")
    return {
        'success': False,
        'error': 'Error interno del servidor',
        'status_code': 500
    }

# ============== STARTUP ==============

# startup/shutdown logs are handled by the `lifespan` context manager above

# ============== MAIN ==============

if __name__ == "__main__":
    # Verificar .env
    if not os.path.exists('.env'):
        logger.warning("⚠️ Archivo .env no encontrado. Usando valores por defecto.")
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
