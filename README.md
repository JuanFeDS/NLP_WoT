# 📚 Análisis de Texto - The Wheel of Time (WoT)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Este proyecto implementa técnicas de Procesamiento de Lenguaje Natural (NLP) para analizar los libros de ***The Wheel of Time***. El sistema permite cargar documentos en formato PDF o TXT, procesar el texto y realizar diversos análisis sobre el contenido.

## 🚀 Características

- **Carga de documentos**: Soporte para archivos PDF y TXT
- **Preprocesamiento de texto**: Limpieza y normalización de texto
- **Análisis de personajes**: Extracción y análisis de personajes en los textos
- **Estructura modular**: Código organizado siguiendo buenas prácticas de desarrollo

## 📦 Requisitos

- Python 3.10 o superior
- Poetry (gestor de dependencias)

## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd NLP_WoT
   ```

2. Instala Poetry si no lo tienes:
   ```bash
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

   # Linux/macOS
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Instala las dependencias del proyecto:
   ```bash
   poetry install
   ```

   Esto creará automáticamente un entorno virtual y instalará todas las dependencias necesarias.

## 🚀 Uso

1. Coloca tus archivos PDF en el directorio `data/Raw/`
2. Configura variables de entorno (opcional) creando `.env` (ver ejemplo abajo)
3. Ejecuta desde `run.py`:
   - Procesar todos los libros detectados (por defecto):
     ```bash
     poetry run python run.py
     ```
   - Procesar un libro específico:
     ```bash
     poetry run python run.py --book WoT_08
     ```
   - Procesar todos explícitamente:
     ```bash
     poetry run python run.py --all-books
     ```
   - Override de normalización ASCII en runtime:
     ```bash
     poetry run python run.py --ascii-norm false
     ```

   **Nota**: También puedes activar el entorno virtual de Poetry y ejecutar directamente:
   ```bash
   poetry shell
   python run.py
   ```

## 📁 Estructura del Proyecto

```
NLP_WoT/
├── data/               # Directorio para los datos
│   ├── Raw/           # Archivos PDF originales
│   └── Processed/     # Archivos de texto procesados
├── scripts/           # Scripts ejecutables
├── src/               # Código fuente del proyecto
│   ├── config/       # Configuraciones
│   ├── data/         # Módulos de carga de datos
│   ├── character_analysis/  # Análisis de personajes
│   └── utils/        # Utilidades varias
└── tests/             # Pruebas unitarias
```

---

## ⚙️ Variables de entorno (.env)

El módulo `src/config/settings.py` carga automáticamente `.env` en la raíz si existe. Puedes usar `.env.example` como base.

Variables soportadas:
- `ENV`: entorno actual (por defecto `development`).
- `RAW_DATA_DIR`: ruta a PDF de entrada (por defecto `./data/Raw`).
- `PROCESSED_DATA_DIR`: ruta para TXT intermedios (por defecto `./data/processed`).
- `CLEAN_DATA_DIR`: ruta para capítulos generados (por defecto `./data/clean`).
- `NORMALIZE_TO_ASCII`: `true/false` para normalización a ASCII (por defecto `true`).

Ejemplo rápido:
```env
ENV=development
RAW_DATA_DIR=./data/Raw
PROCESSED_DATA_DIR=./data/processed
CLEAN_DATA_DIR=./data/clean
NORMALIZE_TO_ASCII=true
```

<div align="center">
Hecho con ❤️ para la comunidad de The Wheel of Time
</div>
