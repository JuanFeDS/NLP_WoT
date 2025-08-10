"""_summary_"""
from src.config import settings
from src.data.loader import BookManager
from src.data.preprocessor import TextProcessor

from src.utils.logger.logger import get_logger

def run_character_analysis(file_name: str):
    """Run the character analysis logic
    """
    logger = get_logger()
    loader = BookManager()

    # PATHS
    raw_data_dir = settings.RAW_DATA_DIR   
    processed_data_dir = settings.PROCESSED_DATA_DIR

    pdf_path = raw_data_dir / f"{file_name}.pdf"
    txt_path = processed_data_dir / f"{file_name}.txt"

    try:
        logger.info("Loading text from file: %s", txt_path)
        text = loader.load_doc(txt_path)
    except FileNotFoundError:
        logger.info("TXT not found. Building from PDF: %s", pdf_path)
        doc = loader.build_doc(str(pdf_path))
        loader.save_doc(doc, str(txt_path))
        logger.info("Text saved to file: %s", txt_path)
        text = loader.load_doc(txt_path)

    processor = TextProcessor()
    clean_text = processor.clean_text(text)
    logger.info("Text cleaned")

    processor.split_by_chapters(clean_text, file_name)
    logger.info("Text split by chapters")

    return clean_text
