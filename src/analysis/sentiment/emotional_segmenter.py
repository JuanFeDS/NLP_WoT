"""Extractor de segmentos emocionales del texto."""
import re
from typing import List, Dict
import spacy
from src.config.logger import get_logger


class EmotionalSegmenter:
    """Extrae segmentos con carga emocional del texto."""
    
    EMOTIONAL_KEYWORDS = [
        # Miedo y ansiedad
        'miedo', 'temor', 'terror', 'pánico', 'asustado', 'aterrado',
        'nervioso', 'ansioso', 'preocupado', 'angustiado', 'inquieto',
        'temblor', 'temblar', 'estremec', 'sobresalt',
        # Alegría y placer
        'alegría', 'feliz', 'contento', 'dichoso', 'gozo', 'sonri',
        'risa', 'reir', 'júbilo', 'regocij', 'satisf', 'plac',
        # Tristeza y dolor
        'tristeza', 'triste', 'melancólico', 'deprimido', 'afligido',
        'llor', 'lágrim', 'solloz', 'pena', 'dolor', 'sufr',
        'desesper', 'desconsuelo', 'abatid', 'desalent',
        # Ira y frustración
        'ira', 'enojo', 'rabia', 'furia', 'enfadado', 'furioso',
        'frustrad', 'irritad', 'molest', 'indignac', 'cólera',
        'grit', 'rugid', 'bramid',
        # Sorpresa y asombro
        'sorpresa', 'asombro', 'sorprendido', 'asombrado',
        'impresion', 'estupefact', 'maravill', 'incredulid',
        # Disgusto y rechazo
        'disgusto', 'asco', 'repugnancia', 'repulsión',
        'náusea', 'aversión', 'desprecio',
        # Emociones complejas
        'amor', 'odio', 'esperanza', 'desesperación',
        'confus', 'duda', 'incertidumbr', 'desconfianz',
        'culpa', 'vergüenza', 'arrepent', 'remordimient',
        'orgullo', 'humillac', 'envidia', 'celos',
        # Estados emocionales
        'tensión', 'alivio', 'calma', 'paz', 'tranquil',
        'agitac', 'perturbac', 'desasosieg',
        'determinac', 'resoluc', 'valentía', 'cobardía',
        # Descriptores físicos de emoción
        'corazón', 'palpita', 'latid', 'respirac', 'suspir',
        'palidec', 'rubor', 'sudor', 'escalofrí',
        'puño', 'apret', 'tens', 'relaj'
    ]
    
    def __init__(self, nlp=None):
        """Inicializa el segmentador.
        
        Args:
            nlp: Modelo spaCy (opcional, se carga si no se proporciona)
        """
        self.logger = get_logger(__name__)
        self.nlp = nlp or spacy.load('es_core_news_lg')
    
    def extract_by_emotional_sentences(
        self, 
        text: str, 
        min_confidence: float = 0.3
    ) -> List[str]:
        """Extrae oraciones que contienen palabras emocionales.
        
        Args:
            text: Texto completo
            min_confidence: Umbral mínimo (no usado por ahora)
            
        Returns:
            Lista de oraciones con carga emocional
        """
        doc = self.nlp(text)
        emotional_sentences = []
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in self.EMOTIONAL_KEYWORDS):
                emotional_sentences.append(sent.text.strip())
        
        self.logger.debug(
            f"Extraídas {len(emotional_sentences)} oraciones emocionales "
            f"de {len(list(doc.sents))} totales"
        )
        
        return emotional_sentences
    
    def extract_character_windows(
        self, 
        text: str, 
        character_names: List[str],
        window_size: int = 100
    ) -> List[str]:
        """Extrae ventanas de texto alrededor de menciones de personajes.
        
        Args:
            text: Texto completo
            character_names: Lista de nombres de personajes
            window_size: Palabras antes/después de cada mención
            
        Returns:
            Lista de fragmentos de texto
        """
        windows = []
        words = text.split()
        
        for i, word in enumerate(words):
            for char_name in character_names:
                if char_name.lower() in word.lower():
                    start = max(0, i - window_size)
                    end = min(len(words), i + window_size + 1)
                    window = ' '.join(words[start:end])
                    windows.append(window)
                    break
        
        self.logger.debug(
            f"Extraídas {len(windows)} ventanas alrededor de personajes"
        )
        
        return windows
    
    def extract_emotional_paragraphs(
        self,
        text: str,
        min_emotional_density: float = 0.02
    ) -> List[str]:
        """Extrae párrafos con densidad emocional mínima.
        
        Args:
            text: Texto completo
            min_emotional_density: Proporción mínima de palabras emocionales
            
        Returns:
            Lista de párrafos emocionales
        """
        paragraphs = text.split('\n\n')
        emotional_paragraphs = []
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            words = para.lower().split()
            if not words:
                continue
            
            emotional_words = sum(
                1 for word in words 
                if any(kw in word for kw in self.EMOTIONAL_KEYWORDS)
            )
            
            density = emotional_words / len(words)
            
            if density >= min_emotional_density:
                emotional_paragraphs.append(para.strip())
        
        self.logger.debug(
            f"Extraídos {len(emotional_paragraphs)} párrafos emocionales "
            f"de {len(paragraphs)} totales"
        )
        
        return emotional_paragraphs
    
    def combine_segments(self, segments: List[str], max_length: int = 3000) -> str:
        """Combina segmentos hasta alcanzar longitud máxima.
        
        Args:
            segments: Lista de segmentos de texto
            max_length: Longitud máxima en caracteres
            
        Returns:
            Texto combinado
        """
        combined = []
        current_length = 0
        
        for segment in segments:
            if current_length + len(segment) > max_length:
                break
            combined.append(segment)
            current_length += len(segment) + 1
        
        return ' '.join(combined)
