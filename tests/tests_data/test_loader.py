"""Unit tests for the BookLoader class."""
import sys
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

project_root = str(Path(__file__).parent.parent.parent)  # Sube hasta la raíz del proyecto
sys.path.insert(0, project_root)

import fitz
import pytest

from src.data.loader import BookManager


class TestBookLoader:
    """Test suite for the BookLoader class."""

    @pytest.fixture
    def loader(self):
        """Fixture to create a BookLoader instance."""
        return BookManager()

    # Pruebas de build_doc
    # Prueba de que se construya el documento con éxito
    def test_build_doc_success(self, loader, tmp_path):
        """Test that the document is built successfully."""

        # Preparamos el entorno
        test_pdf = tmp_path / 'test.pdf'
        test_pdf.write_bytes(b'%PDF-1.4\n')  # Encabezado PDF básico
        
        # Mockeamos fitz.open para no depender de PyMuPDF real
        mock_doc = MagicMock(spec=fitz.Document)
        with patch('src.data.loader.fitz.open', return_value=mock_doc) as mock_open:
            result = loader.build_doc(str(test_pdf))
            
            # Verificaciones
            mock_open.assert_called_once_with(str(test_pdf))
            assert result is mock_doc

    def test_build_doc_failure_file_not_found(self, loader, tmp_path):

        # Definimos una ruta que no existe
        non_existent_file = tmp_path / "non_existent.pdf"

        # Verificamos que el archivo no existe
        assert not non_existent_file.exists()

        # Verificamos que se lance FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.build_doc(str(non_existent_file))

        # Verificamos que el mensaje de error sea el correcto
        assert f"PDF file not found: {non_existent_file}" in str(exc_info.value)



    # Prueba de que el documento no se genera porque en la ruta no hay archivo
    # Prueba de que el documento no se genera por otra razón

    # Pruebas de load_text
    # Prueba de que se cargue el texto con éxito
    # Prueba de que el texto no se cargue porque en la ruta no hay archivo
    # Prueba de que el texto no se cargue por otra razón

    # Pruebas de save_text
    # Prueba de que se guarde el texto con éxito
    # Prueba de que el texto no se guarde por tema de permisos
    # Prueba de que el texto no se guarde por problemas de sistema


