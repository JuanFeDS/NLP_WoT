"""Run the character analysis logic"""
from scripts.run_character_analysis import run_character_analysis
from src.config import settings

from src.utils.logger.logger import get_logger

def run():
    """Run the character analysis logic"""
    logger = get_logger()
    # Ensure output directories exist
    settings.ensure_output_dirs()

    # Get available books from RAW_DATA_DIR
    books = settings.list_books()

    for book in books:
        logger.info("Running character analysis for book: %s", book)
        _ = run_character_analysis(book)

if __name__ == "__main__":
    run()
