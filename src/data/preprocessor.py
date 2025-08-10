"""Preprocessor module for cleaning the text data."""
import re
from pathlib import Path

from src.config import settings

from src.utils.logger.logger import get_logger

from src.data.preprocessing.cleaning import clean_text as _clean_text
from src.data.preprocessing.chapters import (
    get_chapter_matches as _get_chapter_matches,
    infer_title as _infer_title,
    sanitize_title as _sanitize_title,
    write_chapter as _write_chapter,
    diagnose_candidate_headers as _diagnose_candidate_headers,
)

class TextProcessor:
    """Class to process and clean text data."""

    def __init__(self):
        self.logger = get_logger()

    def clean_text(self, text: str) -> str:
        """Limpia y normaliza el texto eliminando caracteres no deseados.

        - Elimina menciones de páginas web específicas (ej: lectulandia.com)
        - Opcionalmente normaliza caracteres Unicode a su forma más cercana en ASCII
        - Elimina múltiples espacios en blanco
        - Elimina espacios al inicio y final del texto

        Args:
            text (str): Texto de entrada a limpiar.

        Returns:
            str: Texto limpio.
        """
        # Validación de texto vacío
        if not text.strip():
            error_msg = (
                "El texto de entrada está vacío o solo contiene espacios en blanco"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Delegar a helper de limpieza para mantener este script corto y claro
        return _clean_text(text, settings.NORMALIZE_TO_ASCII, self.logger)

    def split_by_chapters(self, text: str, file_name: str) -> None:
        """Separa el texto por capítulos y los guarda en archivos individuales.

        Args:
            text (str): Texto de entrada a dividir en capítulos.
            file_name (str): Nombre base para los archivos de salida.
        """
        # Validación de texto vacío
        if not text.strip():
            error_msg = (
                "El texto de entrada está vacío o solo contiene espacios en blanco"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info("Iniciando división por capítulos")

        # Resolver matches con orden de prioridad (delegado)
        matches, pattern_used = _get_chapter_matches(text)
        if matches:
            self.logger.debug("Patrón '%s' detectado para capítulos", pattern_used)

        # Buscar inicio del glosario si existe
        glosary_match = re.search(r"(?i)glosario", text)

        # Crear directorio de salida
        output_dir = Path(settings.CLEAN_DATA_DIR) / file_name
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("Guardando capítulos en: %s", output_dir)

        if not matches:
            _diagnose_candidate_headers(text, self.logger)
            # Fallback: guardar texto completo como un único capítulo
            output_file = output_dir / "01.texto_completo.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text.strip())
            self.logger.warning(
                "No se detectaron capítulos. Guardado como un único archivo: %s",
                output_file,
            )
            return

        # Procesar cada capítulo
        for i, match in enumerate(matches):
            try:
                # Calcular índices de inicio y fin
                start_idx = match.start()
                end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)

                # Ajustar fin si hay glosario
                if glosary_match and end_idx > glosary_match.start():
                    end_idx = glosary_match.start()

                # Obtener contenido y título
                chapter_content = text[start_idx:end_idx].strip()
                if not chapter_content:
                    self.logger.warning("Contenido vacío para el capítulo %d", i + 1)
                    continue

                # Preparar nombre del archivo
                chapter_num = i + 1
                # Título
                title_group = _infer_title(text, match, end_idx)
                safe_title = _sanitize_title(title_group) or f"capitulo_{chapter_num:02d}"

                # Crear archivo
                file_num = f"{chapter_num:02d}"
                output_file = output_dir / f"{file_num}.{safe_title}.txt"

                # Escribir archivo
                if _write_chapter(output_file, chapter_content, self.logger):
                    self.logger.info("Capítulo %d guardado: %s", chapter_num, output_file)
                else:
                    self.logger.error("¡Atención! Archivo vacío: %s", output_file)

            except Exception as error:
                self.logger.error(
                    "Error procesando capítulo %d: %s",
                    chapter_num,
                    str(error),
                    exc_info=True,
                )
                continue

        self.logger.info("Procesados %d capítulos correctamente", len(matches))
