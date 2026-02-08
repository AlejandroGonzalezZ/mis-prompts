"""
Manejador de CSV - Gestión de Favoritos/Prompts Guardados
"""
import csv
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVHandler:
    """Gestor de base de datos CSV para favoritos"""
    
    CSV_FILE = 'Nuevos-Prompt.csv'
    COLUMNS = ['ID', 'Título', 'Personaje', 'Prompt_ES', 'Prompt_EN', 'Prompt_Video', 'Fecha_Creacion']
    
    def __init__(self):
        self.file_path = self.CSV_FILE
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Asegurar que el archivo CSV existe con las columnas correctas"""
        if not os.path.exists(self.file_path):
            # Crear CSV nuevo
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
                writer.writeheader()
            logger.info(f"✅ CSV creado: {self.file_path}")
        else:
            logger.info(f"✅ CSV verificado: {self.file_path}")
    
    def _read_csv(self) -> List[Dict]:
        """Leer todos los registros del CSV"""
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader) if reader else []
        except Exception as e:
            logger.error(f"Error al leer CSV: {str(e)}")
            return []
    
    def _write_csv(self, data: List[Dict]):
        """Escribir datos al CSV"""
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            logger.error(f"Error al escribir CSV: {str(e)}")
            raise
    
    def add_prompt(self, 
                   titulo: str,
                   personaje: str,
                   prompt_es: str,
                   prompt_video: str,
                   prompt_en: Optional[str] = None) -> Dict:
        """
        Agregar nuevo prompt a favoritos
        """
        try:
            data = self._read_csv()
            
            # Generar ID único (basado en timestamp)
            new_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Crear nuevo registro
            new_record = {
                'ID': new_id,
                'Título': titulo,
                'Personaje': personaje,
                'Prompt_ES': prompt_es,
                'Prompt_EN': prompt_en or '',
                'Prompt_Video': prompt_video,
                'Fecha_Creacion': datetime.now().isoformat()
            }
            
            data.append(new_record)
            self._write_csv(data)
            
            logger.info(f"✅ Prompt guardado con ID: {new_id}")
            
            return {
                'success': True,
                'id': new_id,
                'message': 'Prompt guardado en favoritos'
            }
        
        except Exception as e:
            logger.error(f"Error al guardar prompt: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_prompts(self) -> List[Dict]:
        """Obtener todos los prompts guardados"""
        return self._read_csv()
    
    def search_prompts(self, query: str) -> List[Dict]:
        """
        Buscar prompts por palabra clave
        Busca en todas las columnas de texto
        """
        try:
            data = self._read_csv()
            query_lower = query.lower()
            
            results = []
            for record in data:
                # Buscar en todos los campos
                for value in record.values():
                    if value and query_lower in str(value).lower():
                        results.append(record)
                        break
            
            logger.info(f"🔍 Búsqueda '{query}': {len(results)} resultado(s)")
            return results
        
        except Exception as e:
            logger.error(f"Error al buscar prompts: {str(e)}")
            return []
    
    def delete_prompt(self, prompt_id: str) -> Dict:
        """Eliminar un prompt por ID"""
        try:
            data = self._read_csv()
            
            # Filtrar (mantener todos excepto el ID a eliminar)
            original_len = len(data)
            data = [record for record in data if record.get('ID') != prompt_id]
            
            if len(data) == original_len:
                return {
                    'success': False,
                    'error': 'Prompt no encontrado'
                }
            
            self._write_csv(data)
            logger.info(f"✅ Prompt eliminado: {prompt_id}")
            
            return {
                'success': True,
                'message': 'Prompt eliminado'
            }
        
        except Exception as e:
            logger.error(f"Error al eliminar prompt: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict]:
        """Obtener un prompt específico por ID"""
        try:
            data = self._read_csv()
            
            for record in data:
                if record.get('ID') == prompt_id:
                    return record
            
            return None
        
        except Exception as e:
            logger.error(f"Error al obtener prompt: {str(e)}")
            return None
    
    def update_prompt(self, 
                     prompt_id: str,
                     titulo: Optional[str] = None,
                     personaje: Optional[str] = None,
                     prompt_es: Optional[str] = None,
                     prompt_en: Optional[str] = None,
                     prompt_video: Optional[str] = None) -> Dict:
        """Actualizar un prompt existente"""
        try:
            data = self._read_csv()
            
            # Encontrar el índice
            idx = None
            for i, record in enumerate(data):
                if record.get('ID') == prompt_id:
                    idx = i
                    break
            
            if idx is None:
                return {'success': False, 'error': 'Prompt no encontrado'}
            
            # Actualizar solo los campos proporcionados
            if titulo:
                data[idx]['Título'] = titulo
            if personaje:
                data[idx]['Personaje'] = personaje
            if prompt_es:
                data[idx]['Prompt_ES'] = prompt_es
            if prompt_en:
                data[idx]['Prompt_EN'] = prompt_en
            if prompt_video:
                data[idx]['Prompt_Video'] = prompt_video
            
            self._write_csv(data)
            logger.info(f"✅ Prompt actualizado: {prompt_id}")
            
            return {
                'success': True,
                'message': 'Prompt actualizado'
            }
        
        except Exception as e:
            logger.error(f"Error al actualizar prompt: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_json(self, output_file: str = 'favoritos.json') -> Dict:
        """Exportar todos los prompts a JSON"""
        try:
            data = self._read_csv()
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exportado a JSON: {output_file}")
            
            return {
                'success': True,
                'file': output_file
            }
        
        except Exception as e:
            logger.error(f"Error al exportar: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del CSV"""
        try:
            data = self._read_csv()
            
            # Contar personajes
            personajes_count = {}
            for record in data:
                personaje = record.get('Personaje', 'desconocido')
                personajes_count[personaje] = personajes_count.get(personaje, 0) + 1
            
            # Última fecha
            ultima_fecha = None
            if data:
                ultima_fecha = data[-1].get('Fecha_Creacion')
            
            return {
                'total_prompts': len(data),
                'personajes': personajes_count,
                'fecha_ultima_actualizacion': ultima_fecha
            }
        
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {}
