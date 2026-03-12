"""
Módulo de configuración para logging de la aplicación.

Este módulo configura un sistema de logging centralizado que puede ser importado
y usado en toda la aplicación. Configura handlers de consola y archivo
con formato y niveles de log apropiados.
"""
import os
from datetime import datetime
from typing import Optional

import logging
from logging.handlers import RotatingFileHandler

# Constantes
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - %(name)s - %(funcName)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5

# Asegurar que el directorio de logs existe
LOG_DIR = 'log'

os.makedirs(LOG_DIR, exist_ok=True)

# Crear logger personalizado
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Crear formateador
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

try:
    # Console handler (muestra WARNING y superiores)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    # File handler (muestra DEBUG y superiores, rota al alcanzar MAX_LOG_SIZE)
    log_file = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

except Exception as e:
    logging.error("Error al configurar handlers de logging: %s", e)
    raise

# Agregar handlers al logger
if not logger.handlers:  # Evitar agregar handlers múltiples veces
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger. Si es None, devuelve el root logger.
    
    Returns:
        Instancia de logger configurada.
    """
    return logging.getLogger(name)
