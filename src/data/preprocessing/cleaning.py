"""Cleaning helpers for text preprocessing."""
import re
import unicodedata
from typing import Optional


def clean_text(text: str, normalize_to_ascii: bool, logger) -> str:
    """Clean raw text and optionally normalize to ASCII.

    - Removes watermarks like 'www.lectulandia.com - Página N'.
    - Optionally normalizes to ASCII (NFKD -> ascii-encode -> utf-8 decode).
    """
    logger.debug("Iniciando limpieza de texto")

    try:
        # Normalize common control characters and newlines
        clean = text.replace("\r\n", "\n").replace("\r", "\n")
        clean = clean.replace("\x0c", "\n\n")  # form feed -> blank line

        # Remove site/page watermarks
        clean = re.sub(r"www\.lectulandia\.com\s*-\s*Página\s*\d+", "", clean)

        if normalize_to_ascii:
            try:
                clean = unicodedata.normalize("NFKD", clean)
                clean = clean.encode("ascii", "ignore").decode("utf-8")
            except UnicodeError as ue:
                error_msg = f"Error al normalizar el texto a ASCII: {str(ue)}"
                logger.error(error_msg, exc_info=True)
                raise UnicodeError(error_msg) from ue

        logger.info("Texto limpiado exitosamente")
        return clean

    except Exception as e:
        error_msg = f"Error inesperado al limpiar el texto: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise
