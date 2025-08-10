"""Settings module"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables desde un archivo .env si existe
BASE_DIR = Path(__file__).resolve().parents[2]
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# === ENTORNO ===
ENV = os.getenv("ENV", "development")

# === BASE PATHS ===
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR") or (BASE_DIR / "data" / "Raw"))
PROCESSED_DATA_DIR = Path(os.getenv("PROCESSED_DATA_DIR") or (BASE_DIR / "data" / "processed"))
CLEAN_DATA_DIR = Path(os.getenv("CLEAN_DATA_DIR") or (BASE_DIR / "data" / "clean"))

# === PREPROCESAMIENTO ===
def _to_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}

NORMALIZE_TO_ASCII = _to_bool(os.getenv("NORMALIZE_TO_ASCII", "true"), True)

def ensure_output_dirs() -> None:
    """Crea los directorios de salida si no existen."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

def list_books(extensions=("pdf",)) -> list[str]:
    """Lista libros en RAW_DATA_DIR devolviendo nombres sin extensión.

    Args:
        extensions: Extensiones a considerar (sin punto). Por defecto solo 'pdf'.

    Returns:
        Lista ordenada de nombres de archivo (sin extensión).

    Raises:
        FileNotFoundError: Si RAW_DATA_DIR no existe.
        NotADirectoryError: Si RAW_DATA_DIR no es un directorio.
    """
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"RAW_DATA_DIR no existe: {RAW_DATA_DIR}")
    if not RAW_DATA_DIR.is_dir():
        raise NotADirectoryError(f"RAW_DATA_DIR no es un directorio: {RAW_DATA_DIR}")

    exts = {ext.lower().lstrip('.') for ext in extensions}
    files = [p for p in RAW_DATA_DIR.iterdir() if p.is_file() and p.suffix.lower().lstrip('.') in exts]
    return sorted({p.stem for p in files})
