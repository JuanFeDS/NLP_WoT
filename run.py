from scripts.run_character_analysis import run_character_analysis
from src.config import settings

from src.utils.logger.logger import get_logger

def run():
    logger = get_logger()
    books = settings.books
    
    for book in books:
        logger.info("Running character analysis for book: %s", book)
        _ = run_character_analysis(book)

if __name__ == "__main__":
    run()
