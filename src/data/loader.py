"""Module for loading and processing document files."""
import logging
from pathlib import Path

import fitz

# Initialize logger for this module
logger = logging.getLogger(__name__)

class BookManager:
    """Class to process PDF files and extract their text content."""

    def __init__(self) -> None:
        """Initialize the BookLoader instance."""

    def build_doc(self, pdf_path: str) -> fitz.Document:
        """Load the PDF file and return its Document object.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            fitz.Document: The loaded PDF document.

        Raises:
            FileNotFoundError: If the PDF file is not found.
            Exception: For other PDF loading errors.
        """
        try:
            if not Path(pdf_path).is_file():
                error_msg = f"PDF file not found: {pdf_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            logger.info("Loading PDF document: %s", pdf_path)
            doc = fitz.open(pdf_path)
            logger.debug("Successfully loaded PDF with %d pages", len(doc))
            return doc

        except Exception as e:
            logger.error("Failed to load PDF %s: %s", pdf_path, str(e), exc_info=True)
            raise


    def save_doc(self, doc: fitz.Document, file_path: str) -> None:
        """Save the text content to a file.

        Args:
            doc: The document object to save.
            file_path: The path where the text content will be saved.

        Raises:
            PermissionError: If there's no write permission for the output directory.
            OSError: For other file system related errors.
        """
        try:
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info("Saving document text to: %s", file_path)
            with open(file_path, 'w', encoding='utf-8') as file:
                for _, page in enumerate(doc, 1):
                    text = page.get_text()
                    file.write(text)

            logger.debug(
                "Successfully saved document with %d pages to %s",
                len(doc), file_path)

        except PermissionError as e:
            error_msg = f"Permission denied when writing to {file_path}"
            logger.error("%s: %s", error_msg, str(e))
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"Failed to save document to {file_path}"
            logger.error("%s: %s", error_msg, str(e))
            raise

    def load_doc(self, file_path: str) -> str:
        """Load text content from a file.

        Args:
            file_path: Path to the text file.

        Returns:
            str: The content of the text file.
        """

        try:
            logger.debug("Loading text from file: %s", file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.debug("Successfully loaded %d characters from %s", len(text), file_path)
            
            return text
        except FileNotFoundError as e:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load text from {file_path}: {str(e)}"
            logger.error(error_msg)
            raise
