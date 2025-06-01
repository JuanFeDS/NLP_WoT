"""Unit tests for the BookLoader class."""
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

# Add parent directory to path for local imports
sys.path.append(str(Path(__file__).parent.parent))
from src.data.loader import BookLoader

# Test constants
TEST_PDF_PATH = "test_document.pdf"
TEST_TXT_PATH = "test_document.txt"
TEST_CONTENT = "This is a test content."
TEST_DIR = "/test/directory"

class TestBookLoader:
    """Test suite for the BookLoader class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.loader = BookLoader()

    @patch('src.data.loader.fitz.open')
    @patch('src.data.loader.Path')
    def test_build_doc_success(self, mock_path, mock_fitz_open):
        """Test successful PDF document loading."""
        # Configurar mocks
        mock_path.return_value.is_file.return_value = True
        mock_doc = MagicMock()
        mock_fitz_open.return_value = mock_doc

        # Ejecutar
        result = self.loader.build_doc(TEST_PDF_PATH)

        # Verificar
        mock_path.return_value.is_file.assert_called_once()
        mock_fitz_open.assert_called_once_with(TEST_PDF_PATH)
        assert result == mock_doc

    @patch('src.data.loader.Path')
    def test_build_doc_raises_file_not_found(self, mock_path):
        """Test build_doc raises FileNotFoundError when file doesn't exist."""
        mock_path.return_value.is_file.return_value = False

        with pytest.raises(FileNotFoundError):
            self.loader.build_doc("nonexistent.pdf")

    @patch('builtins.open', new_callable=mock_open, read_data=TEST_CONTENT)
    def test_load_text_returns_file_content(self, mock_file):
        """Test load_text returns the content of the text file."""
        result = self.loader.load_text(TEST_TXT_PATH)

        mock_file.assert_called_once_with(
            TEST_TXT_PATH, 'r', encoding='utf-8'
        )
        assert result == TEST_CONTENT

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_text_raises_file_not_found(self, mock_open):
        """Test load_text raises FileNotFoundError for non-existent files."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_text("nonexistent.txt")
        mock_open.assert_called_once_with("nonexistent.txt", 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    @patch('src.data.loader.Path')
    def test_save_text_writes_document_to_file(self, mock_path, mock_file):
        """Test save_text correctly writes document content to file."""
        mock_doc = MagicMock()
        page1 = MagicMock()
        page1.get_text.return_value = "Page 1 content\n"
        page2 = MagicMock()
        page2.get_text.return_value = "Page 2 content\n"
        mock_doc.__iter__.return_value = [page1, page2]

        self.loader.save_text(mock_doc, TEST_TXT_PATH)

        mock_path.return_value.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        mock_file.assert_called_once_with(
            TEST_TXT_PATH, 'w', encoding='utf-8'
        )
        file_handle = mock_file()
        assert file_handle.write.call_count == 2  # One write per page

    @patch('builtins.open', side_effect=PermissionError)
    @patch('src.data.loader.Path')
    def test_save_text_raises_permission_error(self, mock_path, mock_open):
        """Test save_text raises PermissionError for write-protected locations."""
        # Configurar mocks
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content\n"
        mock_doc.__iter__.return_value = [mock_page]
        
        protected_path = f"{TEST_DIR}/protected/test.txt"

        # Ejecutar y verificar
        with pytest.raises(PermissionError):
            self.loader.save_text(mock_doc, protected_path)
            
        # Verificar que se intentó crear el directorio
        mock_path.return_value.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('builtins.open', side_effect=OSError)
    @patch('src.data.loader.Path')
    def test_save_text_raises_os_error(self, mock_path, mock_open):
        """Test save_text propagates OSError for file system issues."""
        # Configurar mocks
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content\n"
        mock_doc.__iter__.return_value = [mock_page]
        
        invalid_path = f"{TEST_DIR}/invalid/test.txt"

        # Ejecutar y verificar
        with pytest.raises(OSError):
            self.loader.save_text(mock_doc, invalid_path)
            
        # Verificar que se intentó crear el directorio
        mock_path.return_value.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
