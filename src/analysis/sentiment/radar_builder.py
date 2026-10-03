"""Constructor de datos para radar charts de emociones."""
import pandas as pd
import json
from typing import Dict, List
from pathlib import Path
from src.config.logger import get_logger


class RadarBuilder:
    """Construye datos para visualización con radar charts."""
    
    def __init__(self):
        """Inicializa el constructor de radar charts."""
        self.logger = get_logger(__name__)
        self.emotion_keys = [
            'alegria', 'tristeza', 'ira', 'miedo', 'sorpresa', 'disgusto'
        ]
    
    def build_global_radar(
        self, 
        df: pd.DataFrame, 
        libro_id: str,
        titulo: str
    ) -> Dict:
        """Construye datos de radar global del libro.
        
        Args:
            df: DataFrame con emociones por capítulo
            libro_id: ID del libro
            titulo: Título del libro
            
        Returns:
            Diccionario con datos para radar chart
        """
        if df.empty:
            self.logger.warning("DataFrame vacío")
            return {}
        
        # Calcular promedios globales
        emotion_cols = [f'score_{em}' for em in self.emotion_keys]
        emotion_means = {}
        
        for em, col in zip(self.emotion_keys, emotion_cols):
            if col in df.columns:
                emotion_means[em] = float(df[col].mean())
            else:
                emotion_means[em] = 0.0
        
        radar_data = {
            'libro_id': libro_id,
            'titulo': titulo,
            'timestamp': pd.Timestamp.now().isoformat(),
            'modelo': df['modelo'].iloc[0] if 'modelo' in df.columns else 'unknown',
            'emociones_globales': emotion_means
        }
        
        self.logger.info(f"Radar global construido para {libro_id}")
        
        return radar_data
    
    def build_character_radar(
        self, 
        df: pd.DataFrame, 
        personaje: str
    ) -> Dict:
        """Construye datos de radar para un personaje específico.
        
        Args:
            df: DataFrame con emociones por capítulo
            personaje: Nombre del personaje
            
        Returns:
            Diccionario con datos para radar chart del personaje
        """
        if df.empty or 'personaje_pov' not in df.columns:
            self.logger.warning("DataFrame vacío o sin columna personaje_pov")
            return {}
        
        # Filtrar capítulos del personaje
        df_char = df[df['personaje_pov'] == personaje]
        
        if df_char.empty:
            self.logger.warning(f"No hay capítulos para {personaje}")
            return {}
        
        # Calcular promedios
        emotion_cols = [f'score_{em}' for em in self.emotion_keys]
        emotion_means = {}
        
        for em, col in zip(self.emotion_keys, emotion_cols):
            if col in df_char.columns:
                emotion_means[em] = float(df_char[col].mean())
            else:
                emotion_means[em] = 0.0
        
        radar_data = {
            'personaje': personaje,
            'capitulos_pov': len(df_char),
            'emociones': emotion_means
        }
        
        self.logger.debug(f"Radar construido para {personaje}")
        
        return radar_data
    
    def build_temporal_radar(
        self, 
        df: pd.DataFrame, 
        ranges: List[tuple]
    ) -> List[Dict]:
        """Construye datos de radar para evolución temporal.
        
        Args:
            df: DataFrame con emociones por capítulo
            ranges: Lista de tuplas (inicio, fin) de rangos de capítulos
            
        Returns:
            Lista de diccionarios con datos por rango temporal
        """
        if df.empty:
            self.logger.warning("DataFrame vacío")
            return []
        
        temporal_data = []
        
        for start, end in ranges:
            df_range = df[
                (df['numero_capitulo'] >= start) & 
                (df['numero_capitulo'] <= end)
            ]
            
            if df_range.empty:
                continue
            
            emotion_cols = [f'score_{em}' for em in self.emotion_keys]
            emotion_means = {}
            
            for em, col in zip(self.emotion_keys, emotion_cols):
                if col in df_range.columns:
                    emotion_means[em] = float(df_range[col].mean())
                else:
                    emotion_means[em] = 0.0
            
            temporal_data.append({
                'rango_capitulos': f'{start}-{end}',
                'emociones': emotion_means
            })
        
        self.logger.info(f"Radar temporal construido: {len(temporal_data)} rangos")
        
        return temporal_data
    
    def build_complete_radar(
        self,
        df: pd.DataFrame,
        libro_id: str,
        titulo: str,
        output_path: Path
    ) -> Dict:
        """Construye radar completo (global + personajes + temporal).
        
        Args:
            df: DataFrame con emociones por capítulo
            libro_id: ID del libro
            titulo: Título del libro
            output_path: Ruta donde guardar el JSON
            
        Returns:
            Diccionario completo con todos los radars
        """
        # Radar global
        radar_data = self.build_global_radar(df, libro_id, titulo)
        
        # Radars por personaje
        if 'personaje_pov' in df.columns:
            personajes = df['personaje_pov'].dropna().unique()
            radar_data['por_personaje'] = [
                self.build_character_radar(df, personaje)
                for personaje in personajes
            ]
        else:
            radar_data['por_personaje'] = []
        
        # Radar temporal (dividir en rangos)
        total_caps = df['numero_capitulo'].max()
        if total_caps > 10:
            # Dividir en 3 rangos
            step = total_caps // 3
            ranges = [
                (1, step),
                (step + 1, step * 2),
                (step * 2 + 1, total_caps)
            ]
        else:
            # Un solo rango
            ranges = [(1, total_caps)]
        
        radar_data['evolucion_temporal'] = self.build_temporal_radar(df, ranges)
        
        # Guardar JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(radar_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Radar completo guardado en {output_path}")
        
        return radar_data
