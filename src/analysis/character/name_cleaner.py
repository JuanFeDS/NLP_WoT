"""Limpiador de nombres detectados para filtrar falsos positivos."""
import re
import spacy
from typing import List, Dict, Optional
from src.config.logger import get_logger


class NameCleaner:
    """Filtra falsos positivos en detección de nombres."""
    
    COMMON_VERBS = {
        'habia', 'había', 'habian', 'habían', 'era', 'eran', 'fue', 'fueron',
        'voy', 'vas', 'va', 'vamos', 'van', 'iba', 'ibas', 'iban',
        'dijo', 'decia', 'decía', 'hizo', 'hacia', 'hacía',
        'parecia', 'parecía', 'parecian', 'parecían',
        'tenia', 'tenía', 'tenian', 'tenían',
        'podia', 'podía', 'podian', 'podían',
        'debia', 'debía', 'debian', 'debían',
        'queria', 'quería', 'querian', 'querían',
        'sabia', 'sabía', 'sabian', 'sabían',
        'veia', 'veía', 'veian', 'veían',
        'oia', 'oía', 'oian', 'oían',
        'creia', 'creía', 'creian', 'creían'
    }
    
    COMMON_WORDS = {
        'aquella', 'aquellas', 'aquello', 'aquel', 'aquellos',
        'esta', 'está', 'estas', 'están', 'este', 'estos',
        'esa', 'esas', 'ese', 'esos',
        'cual', 'cuales', 'cuando', 'donde', 'como', 'cómo',
        'quien', 'quién', 'quienes', 'quiénes',
        'todo', 'todos', 'toda', 'todas',
        'otro', 'otros', 'otra', 'otras',
        'mismo', 'misma', 'mismos', 'mismas',
        'tal', 'tales', 'tanto', 'tantos',
        'cada', 'varios', 'varias', 'ambos', 'ambas',
        'nadie', 'nada', 'algo', 'alguien',
        'señor', 'señora', 'señorita', 'don', 'doña',
        'lady', 'lord', 'sir', 'maese', 'maestro'
    }
    
    TITLES = {
        'señor', 'señora', 'señorita', 'don', 'doña',
        'lady', 'lord', 'sir', 'maese', 'maestro', 'maestra',
        'rey', 'reina', 'principe', 'princesa',
        'duque', 'duquesa', 'conde', 'condesa',
        'capitan', 'capitán', 'general', 'comandante'
    }
    
    def __init__(self, nlp=None):
        """Inicializa el limpiador.
        
        Args:
            nlp: Modelo spaCy (opcional)
        """
        self.logger = get_logger(__name__)
        self.nlp = nlp or spacy.load('es_core_news_lg')
    
    def split_conjunctions(self, detected_chars: List[Dict]) -> List[Dict]:
        """Separa nombres unidos por conjunciones (Y, y, e).
        
        Args:
            detected_chars: Lista de personajes detectados
            
        Returns:
            Lista con nombres separados
        """
        split_chars = []
        
        for char in detected_chars:
            name = char['name']
            
            # Buscar conjunciones en el nombre
            if ' Y ' in name or ' y ' in name or ' e ' in name:
                # Separar por conjunciones
                parts = name.replace(' Y ', '|').replace(' y ', '|').replace(' e ', '|').split('|')
                
                # Crear entrada para cada parte
                for part in parts:
                    part = part.strip()
                    if part:
                        split_chars.append({
                            'name': part,
                            'count': char['count']  # Mantener el mismo conteo
                        })
                
                self.logger.debug("Separado '%s' -> %s", name, parts)
            else:
                split_chars.append(char)
        
        return split_chars
    
    def _find_context_sentence(self, name: str, source_text: str) -> Optional[str]:
        """Busca la oración del texto original donde aparece el nombre.

        Se busca con la capitalización real del texto (no la forzada por el
        detector) para no sesgar el POS tagging hacia nombre propio solo por
        estar en mayúscula.

        Args:
            name: Nombre candidato a buscar
            source_text: Texto original del capítulo

        Returns:
            Oración (ventana de contexto) donde aparece, o None si no se encuentra
        """
        match = re.search(re.escape(name), source_text, re.IGNORECASE)
        if not match:
            return None

        window_start = max(0, match.start() - 80)
        window_end = min(len(source_text), match.end() + 80)
        window = source_text[window_start:window_end]

        # Recortar a limites de oracion (punto o salto de linea) si hay uno cerca
        start_cut = max(window.rfind('. ', 0, match.start() - window_start), window.rfind('\n', 0, match.start() - window_start))
        end_cut = window.find('. ', match.end() - window_start)

        sentence = window[start_cut + 2 if start_cut != -1 else 0 : end_cut + 1 if end_cut != -1 else len(window)]
        return sentence.strip()

    def clean_detected_names(
        self, detected_chars: List[Dict], source_text: Optional[str] = None
    ) -> List[Dict]:
        """Limpia lista de personajes detectados eliminando falsos positivos.

        Args:
            detected_chars: Lista de personajes detectados por NER
            source_text: Texto original del capítulo. Si se provee, el filtro
                de nombre propio evalúa la palabra en su contexto real de
                oración en vez de aislada, para detectar casos como "tejón"
                (sustantivo común que el NER etiquetó como PERSON y que,
                aislado y forzado a mayúscula, spaCy vuelve a taggear PROPN)

        Returns:
            Lista filtrada de personajes válidos
        """
        # Primero separar nombres con conjunciones
        split_chars = self.split_conjunctions(detected_chars)
        
        cleaned = []
        removed_count = 0
        
        for char in split_chars:
            name = char['name']
            name_lower = name.lower().strip()
            
            # Filtro 1: Eliminar verbos comunes
            if name_lower in self.COMMON_VERBS:
                self.logger.debug("Filtrado verbo: '%s'", name)
                removed_count += 1
                continue
            
            # Filtro 2: Eliminar palabras comunes
            if name_lower in self.COMMON_WORDS:
                self.logger.debug("Filtrado palabra com\u00fan: '%s'", name)
                removed_count += 1
                continue
            
            # Filtro 3: Eliminar nombres muy cortos (1-2 letras)
            if len(name) <= 2:
                self.logger.debug("Filtrado nombre corto: '%s'", name)
                removed_count += 1
                continue
            
            # Filtro 4: Verificar que contenga al menos una letra mayúscula
            if not any(c.isupper() for c in name):
                self.logger.debug("Filtrado sin may\u00fasculas: '%s'", name)
                removed_count += 1
                continue
            
            # Filtro 5: Verificar con spaCy que sea realmente un nombre propio.
            # Se evalua en el contexto real de la oracion (con la
            # capitalizacion original del texto) cuando hay source_text
            # disponible, en vez de la palabra aislada y forzada a mayuscula,
            # que sesga a spaCy hacia PROPN incluso para sustantivos comunes.
            context = self._find_context_sentence(name, source_text) if source_text else None
            doc = self.nlp(context) if context else self.nlp(name)
            name_tokens_lower = {w.lower() for w in name.split()}
            relevant_tokens = [t for t in doc if t.text.lower() in name_tokens_lower]
            tokens_to_check = relevant_tokens or doc
            is_proper_noun = any(token.pos_ == 'PROPN' for token in tokens_to_check)

            if not is_proper_noun:
                self.logger.debug("Filtrado no es nombre propio: '%s'", name)
                removed_count += 1
                continue
            
            cleaned.append(char)
        
        self.logger.info(
            "Limpieza completada: %d v\u00e1lidos, %d filtrados",
            len(cleaned), removed_count
        )
        
        return cleaned
    
    def normalize_name(self, name: str) -> str:
        """Normaliza un nombre eliminando títulos y estandarizando.
        
        Args:
            name: Nombre a normalizar
            
        Returns:
            Nombre normalizado
        """
        # Eliminar títulos al inicio
        parts = name.split()
        
        if len(parts) > 1 and parts[0].lower() in self.TITLES:
            name = ' '.join(parts[1:])
        
        # Capitalizar correctamente
        name = name.strip()
        
        return name
    
    def unify_names(self, detected_chars: List[Dict]) -> List[Dict]:
        """Unifica variantes del mismo nombre.
        
        Ejemplos:
        - "Lady Moraine" -> "Moraine"
        - "Moraine Sedai" -> "Moraine"
        
        Args:
            detected_chars: Lista de personajes detectados
            
        Returns:
            Lista con nombres unificados
        """
        name_map = {}
        unified = []
        
        for char in detected_chars:
            original_name = char['name']
            normalized = self.normalize_name(original_name)
            
            # Buscar si ya existe una variante de este nombre
            base_name = normalized.split()[0] if normalized else normalized
            
            if base_name in name_map:
                # Incrementar contador de la variante existente
                existing_char = name_map[base_name]
                existing_char['count'] += char['count']
                
                # Mantener el nombre más largo (más específico)
                if len(normalized) > len(existing_char['name']):
                    existing_char['name'] = normalized
                    existing_char['original_name'] = original_name
                
                self.logger.debug(
                    "Unificado '%s' -> '%s'",
                    original_name, existing_char['name']
                )
            else:
                # Nuevo nombre base
                char_copy = char.copy()
                char_copy['name'] = normalized
                char_copy['original_name'] = original_name
                name_map[base_name] = char_copy
                unified.append(char_copy)
        
        self.logger.info(
            "Unificaci\u00f3n completada: %d -> %d nombres",
            len(detected_chars), len(unified)
        )
        
        return unified
