"""_summary_"""
import sys
sys.path.append('./')

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
    data_dir = settings.DATA_DIR
    # file_name = str(input('Enter the file name (without extension): '))

    pdf_path = f'{data_dir}/Raw/{file_name}.pdf'
    txt_path = f'{data_dir}/Processed/{file_name}.txt'

    try:
        logger.info("Loading text from file: %s", txt_path)
        text = loader.load_doc(txt_path)
    except FileNotFoundError:
        logger.info("PDF file not found: %s", pdf_path)
        doc = loader.build_doc(pdf_path)
        loader.save_doc(doc, txt_path)
        logger.info("Text saved to file: %s", txt_path)
        text = loader.load_doc(txt_path)

    processor = TextProcessor()
    clean_text = processor.clean_text(text)
    logger.info("Text cleaned")

    return clean_text
