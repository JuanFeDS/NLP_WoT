"""Módulo para cargar y procesar archivos de documentos."""
import logging
from pathlib import Path

import fitz

# Inicializar logger para este módulo
logger = logging.getLogger(__name__)

class BookManager:
    """Clase para procesar archivos PDF y extraer su contenido de texto."""

    def __init__(self) -> None:
        """Inicializa la instancia de BookLoader."""

    def build_doc(self, pdf_path: str) -> fitz.Document:
        """Carga el archivo PDF y devuelve su objeto Document.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            fitz.Document: El documento PDF cargado.

        Raises:
            FileNotFoundError: Si el archivo PDF no se encuentra.
            Exception: Para otros errores de carga de PDF.
        """
        try:
            if not Path(pdf_path).is_file():
                error_msg = f"Archivo PDF no encontrado: {pdf_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            logger.info("Cargando documento PDF: %s", pdf_path)
            doc = fitz.open(pdf_path)
            logger.debug("Documento PDF cargado exitosamente con %d páginas", len(doc))
            return doc

        except Exception as e:
            logger.error(
                "Problema al cargar el documento PDF %s: %s", 
                pdf_path, str(e))
            raise


    def save_doc(self, doc: fitz.Document, file_path: str) -> None:
        """Guarda el contenido de texto en un archivo.

        Args:
            doc: El objeto documento a guardar.
            file_path: La ruta donde se guardará el contenido de texto.

        Raises:
            PermissionError: Si no hay permisos de escritura para el directorio de salida.
            OSError: Para otros errores relacionados con el sistema de archivos.
        """
        try:
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info("Guardando contenido del documento en: %s", file_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                for _, page in enumerate(doc, 1):
                    text = page.get_text()
                    file.write(text)

            logger.debug(
                "Documento guardado con %d páginas en %s",
                len(doc), file_path)

        except PermissionError as e:
            error_msg = f"Permiso denegado al escribir en {file_path}"
            logger.error("%s: %s", error_msg, str(e))
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"Error al guardar el documento en {file_path}"
            logger.error("%s: %s", error_msg, str(e))
            raise
        finally:
            # Asegurar que el documento PDF se cierra correctamente
            try:
                if hasattr(doc, "close"):
                    doc.close()
            except Exception as e:
                logger.debug("Error al cerrar el documento PDF: %s", e)

    def load_doc(self, file_path: str) -> str:
        """Carga contenido de texto desde un archivo.

        Args:
            file_path: Ruta al archivo de texto.

        Returns:
            str: El contenido del archivo de texto.
        """

        try:
            logger.debug("Cargando texto desde archivo: %s", file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.debug(
                "Texto cargado exitosamente con %d caracteres desde %s", 
                len(text), file_path)

            return text
        except FileNotFoundError as e:
            error_msg = f"Archivo no encontrado: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg) from e
        except Exception as e:
            error_msg = f"Error al cargar el texto desde {file_path}: {str(e)}"
            logger.error(error_msg)
            raise
