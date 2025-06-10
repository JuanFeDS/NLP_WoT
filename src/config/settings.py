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
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", BASE_DIR / "models"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", BASE_DIR / "logs"))

# Books
books = os.listdir(DATA_DIR / "Raw")
books = [book for book in books if book.endswith(".pdf")]
books = [book.split(".")[0] for book in books]
