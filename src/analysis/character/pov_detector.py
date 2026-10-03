"""Detector de personaje POV usando análisis lingüístico."""
import spacy
from typing import Dict, List, Optional
from collections import Counter
from src.config.logger import get_logger


class POVDetector:
    """Detecta el personaje POV de un capítulo usando análisis híbrido."""
    
    PERCEPTION_VERBS = [
        'ver', 'vio', 'veía', 'mirar', 'miró', 'miraba',
        'escuchar', 'escuchó', 'escuchaba', 'oír', 'oyó', 'oía',
        'sentir', 'sintió', 'sentía', 'notar', 'notó', 'notaba',
        'observar', 'observó', 'observaba', 'percibir', 'percibió', 'percibía'
    ]
    
    THOUGHT_VERBS = [
        'pensar', 'pensó', 'pensaba', 'creer', 'creía', 'creyó',
        'saber', 'sabía', 'supo', 'recordar', 'recordó', 'recordaba',
        'imaginar', 'imaginó', 'imaginaba', 'suponer', 'supuso', 'suponía',
        'considerar', 'consideró', 'consideraba', 'preguntarse', 'preguntó'
    ]
    
    EMOTION_VERBS = [
        'temer', 'temió', 'temía', 'esperar', 'esperó', 'esperaba',
        'desear', 'deseó', 'deseaba', 'querer', 'quiso', 'quería',
        'odiar', 'odió', 'odiaba', 'amar', 'amó', 'amaba',
        'preocuparse', 'preocupó', 'preocupaba'
    ]
    
    def __init__(self, nlp=None):
        """Inicializa el detector de POV.
        
        Args:
            nlp: Modelo spaCy (opcional)
        """
        self.logger = get_logger(__name__)
        self.nlp = nlp or spacy.load('es_core_news_lg')
    
    def detect_pov(
        self, 
        text: str, 
        candidate_characters: List[str],
        threshold_percentage: float = 0.25
    ) -> Optional[str]:
        """Detecta el personaje POV usando análisis híbrido.
        
        Retorna múltiples POVs si están dentro del threshold de diferencia.
        
        Args:
            text: Texto del capítulo
            candidate_characters: Lista de personajes detectados
            threshold_percentage: % de diferencia para considerar múltiples POVs
            
        Returns:
            Nombre del personaje POV o múltiples separados por '|'
        """
        if not candidate_characters:
            self.logger.warning("No hay personajes candidatos para POV")
            return None
        
        doc = self.nlp(text)
        
        scores = Counter()
        
        for char in candidate_characters:
            score = 0
            score += self._score_perception_subject(doc, char) * 3.0
            score += self._score_thought_subject(doc, char) * 4.0
            score += self._score_emotion_subject(doc, char) * 2.5
            score += self._score_pronoun_proximity(doc, char) * 1.5
            
            scores[char] = score
            
            self.logger.debug(f"POV score para '{char}': {score:.2f}")
        
        if not scores:
            return None
        
        # Obtener top POVs
        top_povs = scores.most_common(3)
        
        if not top_povs or top_povs[0][1] < 5.0:
            self.logger.warning(
                f"Score de POV muy bajo ({top_povs[0][1] if top_povs else 0:.2f})"
            )
            return None
        
        # Verificar si hay múltiples POVs cercanos
        primary_pov = top_povs[0][0]
        primary_score = top_povs[0][1]
        
        multiple_povs = [primary_pov]
        
        for char, score in top_povs[1:]:
            # Si el score está dentro del threshold, agregar como POV compartido
            if score >= primary_score * (1 - threshold_percentage):
                multiple_povs.append(char)
                self.logger.info(
                    f"POV compartido detectado: '{char}' "
                    f"(score: {score:.2f}, {score/primary_score:.1%} del principal)"
                )
        
        result = '|'.join(multiple_povs)
        
        if len(multiple_povs) > 1:
            self.logger.info(f"Múltiples POVs detectados: {result}")
        else:
            self.logger.info(f"POV único detectado: '{primary_pov}' (score: {primary_score:.2f})")
        
        return result
    
    def _score_perception_subject(self, doc, character: str) -> float:
        """Cuenta veces que el personaje es sujeto de verbos de percepción."""
        score = 0.0
        char_lower = character.lower()
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            if char_lower not in sent_text:
                continue
            
            for token in sent:
                if token.pos_ == 'VERB' and token.lemma_ in self.PERCEPTION_VERBS:
                    for child in token.children:
                        if child.dep_ == 'nsubj' and char_lower in child.text.lower():
                            score += 1.0
                            break
        
        return score
    
    def _score_thought_subject(self, doc, character: str) -> float:
        """Cuenta veces que el personaje es sujeto de verbos de pensamiento."""
        score = 0.0
        char_lower = character.lower()
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            if char_lower not in sent_text:
                continue
            
            for token in sent:
                if token.pos_ == 'VERB' and token.lemma_ in self.THOUGHT_VERBS:
                    for child in token.children:
                        if child.dep_ == 'nsubj' and char_lower in child.text.lower():
                            score += 1.0
                            break
        
        return score
    
    def _score_emotion_subject(self, doc, character: str) -> float:
        """Cuenta veces que el personaje es sujeto de verbos emocionales."""
        score = 0.0
        char_lower = character.lower()
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            if char_lower not in sent_text:
                continue
            
            for token in sent:
                if token.pos_ == 'VERB' and token.lemma_ in self.EMOTION_VERBS:
                    for child in token.children:
                        if child.dep_ == 'nsubj' and char_lower in child.text.lower():
                            score += 1.0
                            break
        
        return score
    
    def _score_pronoun_proximity(self, doc, character: str) -> float:
        """Cuenta pronombres de tercera persona cerca del personaje."""
        score = 0.0
        char_lower = character.lower()
        
        pronouns_3rd = ['él', 'ella', 'le', 'lo', 'la']
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            if char_lower not in sent_text:
                continue
            
            for pronoun in pronouns_3rd:
                if pronoun in sent_text:
                    score += 0.5
        
        return score
