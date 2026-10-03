"""Analiza sentimiento, emociones y personajes de un libro, capítulo por capítulo."""
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from tqdm import tqdm

from src.config.logger import get_logger
from src.analysis.character import CharacterDetector, CharacterMatcher, POVDetector
from src.analysis.character.name_cleaner import NameCleaner
from src.analysis.sentiment import EmotionDetector, RadarBuilder

MODELOS_EMOCION_POR_DEFECTO = [
    "finiteautomata/beto-emotion-analysis",
    "pysentimiento/robertuito-emotion-analysis",
]


def analyze_book(
    libro_id: str,
    reference_csv: str,
    clean_dir: Path,
    output_dir: Path,
    emotion_models: Optional[List[str]] = None,
    max_chapters: Optional[int] = None,
) -> Dict:
    """Analiza sentimiento, emociones y personajes de un libro completo.

    Args:
        libro_id: ID del libro (ej: 'WoT_01').
        reference_csv: Ruta al dataset de personajes de referencia.
        clean_dir: Directorio con capítulos limpios.
        output_dir: Directorio de salida.
        emotion_models: Modelos de emociones a usar (por defecto BETO y RoBERTuito).
        max_chapters: Número máximo de capítulos a procesar (None = todos).

    Returns:
        Resumen del procesamiento con rutas de los outputs generados.
    """
    logger = get_logger(__name__)
    emotion_models = emotion_models or MODELOS_EMOCION_POR_DEFECTO

    char_detector = CharacterDetector()
    char_matcher = CharacterMatcher(reference_csv)
    pov_detector = POVDetector()
    name_cleaner = NameCleaner()
    radar_builder = RadarBuilder()

    book_dir = clean_dir / libro_id
    if not book_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {book_dir}")

    chapter_files = sorted(book_dir.glob("*.json"))
    if max_chapters:
        chapter_files = chapter_files[:max_chapters]
        logger.info("Limitando a %s capítulos", max_chapters)

    logger.info("Encontrados %s capítulos", len(chapter_files))

    results_by_model = {}

    for model_name in emotion_models:
        logger.info("Procesando con modelo: %s", model_name)
        emotion_detector = EmotionDetector(model_name)
        model_key = model_name.split("/")[-1]

        results = []
        new_characters = []

        for chapter_file in tqdm(chapter_files, desc=f"Capítulos ({model_name})"):
            try:
                with open(chapter_file, "r", encoding="utf-8") as f:
                    chapter_data = json.load(f)

                content = chapter_data.get("content", "")
                if not content or not content.strip():
                    logger.warning("Capítulo vacío: %s", chapter_file.name)
                    continue

                detected_chars = char_detector.detect_characters(content)
                cleaned_chars = name_cleaner.clean_detected_names(detected_chars, source_text=content)
                unified_chars = name_cleaner.unify_names(cleaned_chars)
                char_matches = char_matcher.match_to_reference(unified_chars)

                # El detector de POV busca el nombre como substring literal
                # dentro de las oraciones, asi que necesita la forma tal como
                # aparece en el texto (detected_name), no el nombre canonico
                # del dataset de referencia (que casi nunca aparece completo)
                known_chars = [m["detected_name"] for m in char_matches if m["detected_name"]]
                detected_to_canonical = {
                    m["detected_name"]: m["matched_name"] for m in char_matches
                }
                pov_character = (
                    pov_detector.detect_pov(content, known_chars) if known_chars else None
                )
                if pov_character:
                    pov_character = "|".join(
                        detected_to_canonical.get(name, name)
                        for name in pov_character.split("|")
                    )
                else:
                    pov_character = char_matcher.identify_pov(char_matches)

                for match in char_matches:
                    if match["source"] == "ner" and match["count"] >= 3:
                        new_characters.append({
                            "libro_id": libro_id,
                            "capitulo": chapter_data.get("chapter_number", 0),
                            "nombre_detectado": match["detected_name"],
                            "frecuencia": match["count"],
                            "validation_status": "pending",
                        })

                emotions_full = emotion_detector.detect_emotions(
                    content, use_segmentation=False
                )
                emotions_emotional = emotion_detector.detect_emotions(
                    content, use_segmentation=True
                )

                personajes_lista = [c["name"] for c in unified_chars[:10]]

                results.append({
                    "libro_id": libro_id,
                    "numero_capitulo": chapter_data.get("chapter_number", 0),
                    "titulo_capitulo": chapter_data.get("title", "Sin título"),
                    "titulo_libro": chapter_data.get("book_title", libro_id),
                    "personaje_pov": pov_character,
                    "personajes_detectados": len(unified_chars),
                    "lista_personajes": "|".join(personajes_lista),
                    "score_alegria_full": emotions_full["alegria"],
                    "score_tristeza_full": emotions_full["tristeza"],
                    "score_ira_full": emotions_full["ira"],
                    "score_miedo_full": emotions_full["miedo"],
                    "score_sorpresa_full": emotions_full["sorpresa"],
                    "score_disgusto_full": emotions_full["disgusto"],
                    "score_neutral_full": emotions_full["neutral"],
                    "emocion_dominante_full": emotions_full["emocion_dominante"],
                    "confianza_emocion_full": emotions_full["confianza"],
                    "score_alegria_emotional": emotions_emotional["alegria"],
                    "score_tristeza_emotional": emotions_emotional["tristeza"],
                    "score_ira_emotional": emotions_emotional["ira"],
                    "score_miedo_emotional": emotions_emotional["miedo"],
                    "score_sorpresa_emotional": emotions_emotional["sorpresa"],
                    "score_disgusto_emotional": emotions_emotional["disgusto"],
                    "score_neutral_emotional": emotions_emotional["neutral"],
                    "emocion_dominante_emotional": emotions_emotional["emocion_dominante"],
                    "confianza_emocion_emotional": emotions_emotional["confianza"],
                    "modelo": model_key,
                })
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error procesando %s: %s", chapter_file.name, e)

        results_by_model[model_key] = {"results": results, "new_characters": new_characters}

    return _save_results(libro_id, results_by_model, output_dir, radar_builder)


def _save_results(
    libro_id: str,
    results_by_model: Dict,
    output_dir: Path,
    radar_builder: RadarBuilder,
) -> Dict:
    """Guarda los resultados del análisis (CSV de emociones y JSON de radar)."""
    logger = get_logger(__name__)
    summary = {
        "libro_id": libro_id,
        "modelos_procesados": list(results_by_model.keys()),
        "outputs": {},
    }

    for model_key, data in results_by_model.items():
        results = data["results"]
        new_chars = data["new_characters"]

        if not results:
            continue

        df = pd.DataFrame(results)

        emotions_dir = output_dir / "sentiment" / "emociones" / "por_capitulo"
        emotions_dir.mkdir(parents=True, exist_ok=True)
        emotions_file = emotions_dir / f"{libro_id}_{model_key}_emociones.csv"
        df.to_csv(emotions_file, index=False, encoding="utf-8")

        radar_dir = output_dir / "sentiment" / "emociones" / "radar"
        radar_file = radar_dir / f"{libro_id}_{model_key}_radar_data.json"
        titulo = df["titulo_libro"].iloc[0] if not df.empty else libro_id
        radar_builder.build_complete_radar(df, libro_id, titulo, radar_file)

        summary["outputs"][model_key] = {
            "emociones_csv": str(emotions_file),
            "radar_json": str(radar_file),
            "capitulos_procesados": len(results),
        }

        if new_chars:
            chars_dir = output_dir / "characters" / "detecciones"
            chars_dir.mkdir(parents=True, exist_ok=True)
            chars_file = chars_dir / f"{libro_id}_{model_key}_personajes_nuevos.csv"
            pd.DataFrame(new_chars).to_csv(chars_file, index=False, encoding="utf-8")
            summary["outputs"][model_key]["nuevos_personajes"] = len(new_chars)

    metadata_file = output_dir / "sentiment" / "metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info("Resultados guardados en %s", output_dir)

    return summary
