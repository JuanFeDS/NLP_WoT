---
title: "Roadmap NLP WoT"
description: "Plan maestro para el análisis NLP de The Wheel of Time"
---

# Roadmap del Proyecto NLP WoT

## 1. Visión General
- **Objetivo**: Analizar la saga *The Wheel of Time* mediante NLP para obtener insights narrativos y emocionales.
- **Resultados esperados**:
  - Tendencias de sentimiento por libro, capítulo y personaje.
  - Red de relaciones entre personajes (co-ocurrencias y POV).
  - Visualizaciones interactivas para portafolio.

## 2. Fases y Entregables

### Milestone 1 · Fundaciones ✅ COMPLETADO
1. ✅ Reorganización de estructura de carpetas (`core/`, `preprocessing/`, `analysis/`).
2. ✅ Migración a Poetry y actualización de dependencias NLP (`pyproject.toml`, `poetry.lock`).
3. ✅ Dataset inicial de personajes en `data/reference/characters.csv` (20 personajes semilla de WoT).
4. ✅ Documentación base en `docs/` (roadmap, formatos de datos).

### Milestone 2 · Sentiment Analysis & Emotion Detection (2-3 semanas)
1. Crear `src/core/pipelines/sentiment_pipeline.py` con pasos:
   - Cargar capítulos limpios.
   - **Polaridad de sentimiento**: VADER (baseline) + BETO sentiment.
   - **Detección de emociones**: BETO/RoBERTuito emotion (6 emociones de Ekman).
   - Persistir resultados en `data/outputs/sentiment/`.
2. Definir módulo `src/analysis/sentiment/` con:
   - `analyzer.py`: wrappers de modelos (VADER, BETO, RoBERTuito).
   - `emotion_detector.py`: detección de emociones específicas (alegría, tristeza, ira, miedo, sorpresa, disgusto).
   - `aggregator.py`: métricas por capítulo/libro/personaje.
   - `radar_builder.py`: generación de datos para radar charts.
3. Exportar datasets CSV/JSON listos para visualización:
   - Polaridad de sentimiento por capítulo y libro.
   - Emociones específicas por capítulo.
   - Datos agregados para radar charts (global, por personaje, evolución temporal).

### Milestone 3 · Character Tracking (2-3 semanas)
1. Implementar `src/analysis/character/detector.py`:
   - spaCy + reglas custom para nombres propios.
   - Diccionario de alias y títulos honoríficos.
2. `pov_classifier.py`: identificar protagonista de cada capítulo.
3. `network_builder.py`: co-ocurrencias (capítulo, ventana móvil, saga completa).
4. Guardar resultados en `data/outputs/characters/`.

### Milestone 4 · Evolución y Visualización (2 semanas)
1. Combinar sentimiento + personajes en `src/analysis/evolution/tracker.py`.
2. Construir visualizaciones (`src/visualization/`):
   - Series temporales (sentimiento vs. capítulo).
   - Heatmaps por libro.
   - Grafos de relaciones (networkx + plotly).
   - Wordclouds temáticas.
3. Generar reporte HTML de storytelling por libro (`src/scripts/build_report.py`).

### Milestone 5 · Portafolio Ready (1 semana)
1. README ampliado con capturas y descripción del proceso.
2. Reporte HTML resumen por libro (tipo "case study").
3. Opcional: mini dashboard (Streamlit/Gradio) para explorar resultados.
4. Publicar resumen en LinkedIn/blog.

## 3. Stack Técnico
- **Gestión de dependencias**: Poetry (Python 3.10+)
- **NLP**: spaCy, transformers (BERT/RoBERTa), VADER, TextBlob.
- **Procesamiento**: pandas, numpy, PyMuPDF, regex.
- **Visualización**: plotly, seaborn, matplotlib, networkx, wordcloud.
- **Infraestructura**: logging centralizado, configuración `.env`, datos en `data/` (Raw/Processed/Clean/Outputs).
- **Idioma de análisis**: Español (outputs, documentación, etiquetas)

## 4. Próximos Pasos (Milestone 2)
1. Implementar pipeline de análisis de sentimiento (`src/core/pipelines/sentiment_pipeline.py`).
2. Crear módulos de análisis en `src/analysis/sentiment/` (analyzer, aggregator).
3. Configurar modelos de sentimiento para español (VADER adaptado, BETO/RoBERTa-es).
4. Generar primeros resultados de sentimiento para WoT_01.
5. Generar reporte HTML exploratorio inicial (`src/scripts/build_report.py`).

## 5. Notas de Implementación
- Mantener scripts < 120 líneas; dividir en módulos si es necesario.
- Documentar cada nueva fase en `CHANGE.md` con fechas y autores.
- Priorizar pruebas unitarias para servicios clave (`BookManager`, `TextProcessor`, pipelines nuevos).
- Utilizar logs con contexto (libro/capítulo/personaje) para facilitar debugging.

---
**Estado:** Milestone 1 completado - actualizado al 13-mar-2026.
