# 📚 Análisis de Texto - The Wheel of Time (WoT)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Este proyecto implementa técnicas de Procesamiento de Lenguaje Natural (NLP) para analizar los libros de ***The Wheel of Time***. El sistema permite cargar documentos en formato PDF o TXT, procesar el texto y realizar diversos análisis sobre el contenido.

## 🚀 Características

- **Carga de documentos**: Soporte para archivos PDF y TXT
- **Preprocesamiento de texto**: Limpieza y normalización de texto
- **Análisis de personajes**: Extracción y análisis de personajes en los textos
- **Estructura modular**: Código organizado siguiendo buenas prácticas de desarrollo

## 📦 Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd NLP_WoT
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uso

1. Coloca tus archivos PDF en el directorio `data/Raw/`
2. Ejecuta el análisis:
   ```bash
   python run.py
   ```
3. Sigue las instrucciones en pantalla

## 📁 Estructura del Proyecto

```
NLP_WoT/
├── data/               # Directorio para los datos
│   ├── Raw/           # Archivos PDF originales
│   └── Processed/     # Archivos de texto procesados
├── notebooks/         # Jupyter notebooks para análisis exploratorio
├── scripts/           # Scripts ejecutables
├── src/               # Código fuente del proyecto
│   ├── config/       # Configuraciones
│   ├── data/         # Módulos de carga de datos
│   ├── character_analysis/  # Análisis de personajes
│   └── utils/        # Utilidades varias
└── tests/             # Pruebas unitarias
```

---

<div align="center">
Hecho con ❤️ para la comunidad de The Wheel of Time
</div>
