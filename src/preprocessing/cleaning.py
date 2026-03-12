"""Helpers de limpieza para preprocesamiento de texto."""
import re
import unicodedata


def clean_text(text: str, normalize_to_ascii: bool, logger) -> str:
    """Limpia texto crudo y opcionalmente normaliza a ASCII.

    - Elimina marcas de agua como 'www.lectulandia.com - Página N'.
    - Opcionalmente normaliza a ASCII (NFKD -> ascii-encode -> utf-8 decode).
    """
    logger.debug("Iniciando limpieza de texto")

    try:
        # Normalizar caracteres de control comunes y saltos de línea
        clean = text.replace("\r\n", "\n").replace("\r", "\n")
        clean = clean.replace("\x0c", "\n\n")  # form feed -> línea en blanco

        # Eliminar marcas de agua de sitios web
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
