"""Detector de emociones usando transformers (BETO/RoBERTuito)."""
from transformers import pipeline
from typing import Dict, List
import torch
import spacy
from src.config.logger import get_logger


class EmotionDetector:
    """Detecta emociones específicas usando modelos de transformers."""
    
    # Mapeo de labels en inglés a español
    EMOTION_MAP = {
        'joy': 'alegria',
        'sadness': 'tristeza',
        'anger': 'ira',
        'fear': 'miedo',
        'surprise': 'sorpresa',
        'disgust': 'disgusto',
        'neutral': 'neutral',
        'others': 'neutral'
    }
    
    def __init__(self, model_name: str = "finiteautomata/beto-emotion-analysis"):
        """Inicializa el detector de emociones.
        
        Args:
            model_name: Nombre del modelo de HuggingFace
                - 'finiteautomata/beto-emotion-analysis' (BETO)
                - 'pysentimiento/robertuito-emotion-analysis' (RoBERTuito)
        """
        self.logger = get_logger(__name__)
        self.model_name = model_name
        
        # Configurar max_length según el modelo
        if 'robertuito' in model_name.lower():
            self.max_length = 100  # RoBERTuito tiene límite de 128
        else:
            self.max_length = 450  # BETO tiene límite de 512
        
        # Detectar si hay GPU disponible
        device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if device == 0 else "CPU"
        
        self.logger.info(f"Cargando modelo {model_name} en {device_name}...")
        self.logger.info(f"Max length configurado: {self.max_length} tokens")
        
        try:
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                top_k=None,  # Retornar todas las emociones
                device=device
            )
            self.logger.info(f"Modelo cargado exitosamente")
        except Exception as e:
            self.logger.error(f"Error cargando modelo: {e}")
            raise
    
    def detect_emotions(self, text: str, use_segmentation: bool = False) -> Dict[str, any]:
        """Detecta emociones en el texto.
        
        Args:
            text: Texto a analizar
            use_segmentation: Si True, usa análisis por oraciones con
                agregación ponderada excluyendo neutrales
            
        Returns:
            Diccionario con scores de emociones y emoción dominante
        """
        if not text or not text.strip():
            self.logger.warning("Texto vacío proporcionado")
            return self._empty_result()
        
        if use_segmentation:
            return self._detect_by_sentences(text)
        
        return self._classify_single(text)
    
    def _classify_single(self, text: str) -> Dict[str, any]:
        """Clasifica un solo fragmento de texto.
        
        Args:
            text: Texto a clasificar
            
        Returns:
            Diccionario con scores de emociones
        """
        try:
            results = self.classifier(
                text, 
                truncation=True, 
                max_length=self.max_length
            )[0]
            
            emotion_scores = {}
            for item in results:
                label_en = item['label'].lower()
                label_es = self.EMOTION_MAP.get(label_en, 'neutral')
                emotion_scores[label_es] = item['score']
            
            for emotion_es in self.EMOTION_MAP.values():
                if emotion_es not in emotion_scores:
                    emotion_scores[emotion_es] = 0.0
            
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            return {
                'alegria': emotion_scores.get('alegria', 0.0),
                'tristeza': emotion_scores.get('tristeza', 0.0),
                'ira': emotion_scores.get('ira', 0.0),
                'miedo': emotion_scores.get('miedo', 0.0),
                'sorpresa': emotion_scores.get('sorpresa', 0.0),
                'disgusto': emotion_scores.get('disgusto', 0.0),
                'neutral': emotion_scores.get('neutral', 0.0),
                'emocion_dominante': dominant_emotion[0],
                'confianza': dominant_emotion[1]
            }
            
        except Exception as e:
            self.logger.error(f"Error clasificando texto: {e}", exc_info=True)
            return self._empty_result()
    
    def _detect_by_sentences(self, text: str) -> Dict[str, any]:
        """Analiza emociones oración por oración y agrega resultados.
        
        Estrategia:
        1. Dividir texto en oraciones con spaCy
        2. Clasificar cada oración individualmente
        3. Excluir oraciones donde neutral > 0.7
        4. Promediar scores de oraciones no-neutrales
        
        Args:
            text: Texto completo del capítulo
            
        Returns:
            Diccionario con scores agregados
        """
        nlp = spacy.load('es_core_news_lg', disable=['ner', 'lemmatizer'])
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
        
        self.logger.debug(f"Oraciones a analizar: {len(sentences)}")
        
        if not sentences:
            return self._empty_result()
        
        # Clasificar cada oración
        all_results = []
        non_neutral_results = []
        
        for sent in sentences:
            result = self._classify_single(sent)
            all_results.append(result)
            
            # Filtrar: solo incluir si neutral < 0.7
            if result['neutral'] < 0.7:
                non_neutral_results.append(result)
        
        self.logger.info(
            f"Oraciones totales: {len(all_results)}, "
            f"no-neutrales: {len(non_neutral_results)} "
            f"({len(non_neutral_results)/len(all_results)*100:.0f}%)"
        )
        
        # Si no hay oraciones no-neutrales, usar todas
        target_results = non_neutral_results if non_neutral_results else all_results
        
        # Promediar scores
        emotions = ['alegria', 'tristeza', 'ira', 'miedo', 'sorpresa', 'disgusto', 'neutral']
        avg_scores = {}
        
        for emotion in emotions:
            avg_scores[emotion] = sum(r[emotion] for r in target_results) / len(target_results)
        
        # Encontrar emoción dominante (excluyendo neutral)
        non_neutral_scores = {k: v for k, v in avg_scores.items() if k != 'neutral'}
        dominant = max(non_neutral_scores.items(), key=lambda x: x[1])
        
        return {
            'alegria': avg_scores['alegria'],
            'tristeza': avg_scores['tristeza'],
            'ira': avg_scores['ira'],
            'miedo': avg_scores['miedo'],
            'sorpresa': avg_scores['sorpresa'],
            'disgusto': avg_scores['disgusto'],
            'neutral': avg_scores['neutral'],
            'emocion_dominante': dominant[0],
            'confianza': dominant[1]
        }
    
    def _empty_result(self) -> Dict[str, any]:
        """Retorna resultado vacío."""
        return {
            'alegria': 0.0,
            'tristeza': 0.0,
            'ira': 0.0,
            'miedo': 0.0,
            'sorpresa': 0.0,
            'disgusto': 0.0,
            'neutral': 1.0,
            'emocion_dominante': 'neutral',
            'confianza': 0.0
        }
