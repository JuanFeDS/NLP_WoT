"""Ejecuta el pipeline de procesamiento de libros"""
from src.scripts.process_books import process_book
from src.config import settings

from src.config.logger import get_logger

def run():
    """Ejecuta el pipeline de procesamiento de libros"""
    logger = get_logger()
    # Asegurar que los directorios de salida existen
    settings.ensure_output_dirs()

    # Obtener libros disponibles desde RAW_DATA_DIR
    books = settings.list_books()

    for book in books:
        logger.info("Procesando libro: %s", book)
        _ = process_book(book)

if __name__ == "__main__":
    run()
