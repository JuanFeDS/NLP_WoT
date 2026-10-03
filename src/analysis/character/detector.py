"""Detector de personajes usando NER con spaCy."""
from collections import Counter
from typing import List, Dict

import spacy

from src.config.logger import get_logger

class CharacterDetector:
    """Detecta personajes en texto usando Named Entity Recognition."""

    def __init__(
        self, 
        model_name: str = "es_core_news_lg", 
        min_frequency: int = 2
    ):
        """Inicializa el detector de personajes.
        
        Args:
            model_name: Nombre del modelo spaCy a usar
            min_frequency: Frecuencia mínima para considerar un personaje válido
        """
        self.logger = get_logger(__name__)
        self.min_frequency = min_frequency

        try:
            self.nlp = spacy.load(model_name)
            self.logger.info(
                "Modelo spaCy %s cargado exitosamente", 
                model_name
            )
        except OSError:
            self.logger.error("Modelo '%s' no encontrado", model_name)
            raise
    
    def detect_characters(self, text: str) -> List[Dict[str, any]]:
        """Detecta personajes en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de diccionarios con personajes detectados:
            [{name: str, count: int, positions: list}, ...]
        """
        if not text or not text.strip():
            self.logger.warning("Texto vacío proporcionado")
            return []

        doc = self.nlp(text)

        # Extraer entidades PERSON
        person_entities = [
            ent.text.strip() for ent in doc.ents 
            if ent.label_ == "PER"
        ]

        # Normalizar nombres (capitalizar correctamente)
        normalized_names = [self._normalize_name(name) for name in person_entities]

        # Contar frecuencias
        name_counts = Counter(normalized_names)

        # Filtrar por frecuencia mínima
        characters = []
        for name, count in name_counts.items():
            if count >= self.min_frequency:
                # Encontrar posiciones de este personaje
                positions = [
                    i for i, n in enumerate(normalized_names) 
                    if n == name
                ]

                characters.append({
                    'name': name,
                    'count': count,
                    'positions': positions,
                    'confidence': min(1.0, count / 10.0)  # Heurística simple
                })

        # Ordenar por frecuencia descendente
        characters.sort(key=lambda x: x['count'], reverse=True)

        self.logger.debug(
            "Detectados %d personajes"
            "(de %d únicos)",
            len(characters),
            len(name_counts)
        )
        
        return characters
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza un nombre de personaje.
        
        Args:
            name: Nombre a normalizar
            
        Returns:
            Nombre normalizado
        """
        # Eliminar espacios extras
        name = ' '.join(name.split())

        # Capitalizar cada palabra
        name = ' '.join(word.capitalize() for word in name.split())

        return name
