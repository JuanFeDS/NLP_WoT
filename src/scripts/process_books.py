"""Pipeline de procesamiento de libros: extraer, limpiar y dividir libros en capítulos."""
from src.config import settings
from src.core.services.book_loader import BookManager
from src.core.services.text_processor import TextProcessor

from src.config.logger import get_logger

def process_book(file_name: str):
    """Procesa un libro: extrae desde PDF, limpia el texto y divide en capítulos.
    
    Args:
        file_name: Nombre del archivo del libro (sin extensión).
    
    Returns:
        str: Contenido de texto limpio.
    """
    logger = get_logger()
    loader = BookManager()

    # PATHS
    raw_data_dir = settings.RAW_DATA_DIR   
    processed_data_dir = settings.PROCESSED_DATA_DIR

    pdf_path = raw_data_dir / f"{file_name}.pdf"
    txt_path = processed_data_dir / f"{file_name}.txt"

    # Cargar texto desde archivo o construir desde PDF
    try:
        logger.info("Cargando texto desde archivo: %s", txt_path)
        text = loader.load_doc(txt_path)
    except FileNotFoundError:
        logger.info("TXT no encontrado. Construyendo desde PDF: %s", pdf_path)
        doc = loader.build_doc(str(pdf_path))
        loader.save_doc(doc, str(txt_path))
        logger.info("Texto guardado en archivo: %s", txt_path)
        text = loader.load_doc(txt_path)

    # Procesar texto
    processor = TextProcessor()
    clean_text = processor.clean_text(text)
    logger.info("Texto limpiado")

    # Dividir texto por capítulos
    processor.split_by_chapters(clean_text, file_name)
    logger.info("Texto dividido por capítulos")

    return clean_text
