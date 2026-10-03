"""Matcher de personajes contra dataset de referencia."""
import pandas as pd
from difflib import SequenceMatcher
from typing import List, Dict, Optional
from src.config.logger import get_logger


class CharacterMatcher:
    """Vincula personajes detectados con dataset de referencia."""
    
    def __init__(self, reference_csv: str, fuzzy_threshold: float = 0.85):
        """Inicializa el matcher.
        
        Args:
            reference_csv: Ruta al archivo CSV de referencia
            fuzzy_threshold: Umbral de similitud para fuzzy matching (0-1)
        """
        self.logger = get_logger(__name__)
        self.fuzzy_threshold = fuzzy_threshold
        
        try:
            self.reference_df = pd.read_csv(reference_csv)
            self.logger.info(
                f"Dataset de referencia cargado: {len(self.reference_df)} personajes"
            )
        except Exception as e:
            self.logger.error(f"Error cargando dataset de referencia: {e}")
            raise
        
        # Crear diccionario de aliases para búsqueda rápida
        self._build_alias_dict()
    
    def _build_alias_dict(self):
        """Construye diccionario de nombres y aliases."""
        self.alias_dict = {}
        
        for _, row in self.reference_df.iterrows():
            name = row['name']
            
            # Agregar nombre principal
            self.alias_dict[name.lower()] = name
            
            # Agregar aliases si existen
            if pd.notna(row['aliases']):
                aliases = str(row['aliases']).split(';')
                for alias in aliases:
                    alias = alias.strip()
                    if alias:
                        self.alias_dict[alias.lower()] = name
    
    def match_to_reference(
        self, 
        detected_characters: List[Dict]
    ) -> List[Dict]:
        """Vincula personajes detectados con dataset de referencia.
        
        Args:
            detected_characters: Lista de personajes detectados por NER
            
        Returns:
            Lista de matches con información adicional
        """
        matches = []
        
        for char in detected_characters:
            detected_name = char['name']
            match_result = self._find_match(detected_name)
            
            matches.append({
                'detected_name': detected_name,
                'matched_name': match_result['matched_name'],
                'match_type': match_result['match_type'],
                'confidence': match_result['confidence'],
                'count': char['count'],
                'source': match_result['source']
            })
        
        return matches
    
    def _find_match(self, detected_name: str) -> Dict:
        """Busca match para un nombre detectado.
        
        Args:
            detected_name: Nombre detectado por NER
            
        Returns:
            Diccionario con información del match
        """
        detected_lower = detected_name.lower()
        
        # 1. Match exacto por nombre
        if detected_lower in self.alias_dict:
            return {
                'matched_name': self.alias_dict[detected_lower],
                'match_type': 'exact',
                'confidence': 1.0,
                'source': 'manual'
            }
        
        # 2. Fuzzy matching
        best_match = None
        best_score = 0.0
        
        for alias_lower, ref_name in self.alias_dict.items():
            score = SequenceMatcher(None, detected_lower, alias_lower).ratio()
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = ref_name
        
        if best_match:
            return {
                'matched_name': best_match,
                'match_type': 'fuzzy',
                'confidence': best_score,
                'source': 'manual'
            }
        
        # 3. No match - nuevo candidato
        return {
            'matched_name': detected_name,
            'match_type': 'new',
            'confidence': 0.5,
            'source': 'ner'
        }
    
    def identify_pov(
        self, 
        character_matches: List[Dict]
    ) -> Optional[str]:
        """Identifica el personaje POV del capítulo.
        
        Estrategia: Personaje más mencionado del dataset de referencia,
        priorizando personajes con is_pov=True.
        
        Args:
            character_matches: Lista de personajes matcheados
            
        Returns:
            Nombre del personaje POV o None
        """
        if not character_matches:
            return None
        
        # Filtrar solo personajes conocidos (source='manual')
        known_chars = [
            char for char in character_matches 
            if char['source'] == 'manual'
        ]
        
        if not known_chars:
            self.logger.warning("No se encontraron personajes conocidos")
            return None
        
        # Obtener información de is_pov del dataset
        pov_chars = []
        non_pov_chars = []
        
        for char in known_chars:
            ref_row = self.reference_df[
                self.reference_df['name'] == char['matched_name']
            ]
            
            if not ref_row.empty:
                is_pov = ref_row.iloc[0]['is_pov']
                if is_pov:
                    pov_chars.append(char)
                else:
                    non_pov_chars.append(char)
        
        # Priorizar personajes POV
        candidates = pov_chars if pov_chars else non_pov_chars
        
        if not candidates:
            return None
        
        # Seleccionar el más mencionado
        pov_character = max(candidates, key=lambda x: x['count'])
        
        self.logger.info(
            f"POV identificado: {pov_character['matched_name']} "
            f"({pov_character['count']} menciones)"
        )
        
        return pov_character['matched_name']
