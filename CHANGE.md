# Historial de Cambios - NLP_WoT

### [Fecha del cambio: 2026-08-25]

**Archivo(s) Modificado(s):**
- `src/core/pipelines/` (eliminado)
- `src/analysis/sentiment/aggregator.py` (eliminado, sin uso)
- `src/analysis/sentiment/__init__.py` (modificado)
- `src/scripts/analyze_sentiment.py` (nuevo)
- `src/scripts/build_report.py` (nuevo)
- `src/scripts/visualize_emotions.py` (eliminado, migrado a `build_report.py`)
- `notebooks/05.sentiment_baseline.ipynb` (eliminado)
- `notebooks/` (carpeta eliminada)
- `docs/notebook_conventions.md` (eliminado)
- `docs/roadmap_nlp_wot.md` (modificado)
- `README.md` (modificado)

**Tipo de cambio:** Refactor - Simplificación de arquitectura y migración notebooks → reporte HTML

**Descripción del cambio:**

1. **Simplificación de la capa de pipelines:**
   - `SentimentPipeline` (clase, único punto de invocación) reemplazada por `analyze_book()`, función simple en `src/scripts/analyze_sentiment.py`, siguiendo el mismo patrón que `process_books.py`.
   - Eliminado `SentimentAggregator`: se instanciaba pero ningún método se llamaba en ningún lugar del repo.
   - Eliminada la carpeta `src/core/pipelines/`; todo el código ejecutable vive ahora en `src/scripts/`.

2. **Migración de notebooks a reportes HTML:**
   - `notebooks/05.sentiment_baseline.ipynb` estaba desactualizado (columnas obsoletas tras el cambio a métricas híbridas) y su función de exploración manual ya no aporta valor con el flujo actual.
   - Nuevo `src/scripts/build_report.py::build_report()`: genera un único HTML consolidado por libro, en `data/outputs/sentiment/reportes/<libro>_reporte.html`.
   - Descubre automáticamente los modelos de emoción disponibles a partir de los CSV existentes, sin hardcodear nombres de modelo.
   - Diseño editorial (tipografía Newsreader/Public Sans/IBM Plex Mono, paleta por emoción, tiles de resumen, paneles de capítulo con barras apiladas, tabla y concordancia entre modelos) adoptado a partir de un reporte de referencia generado por otra sesión de Claude Code sobre los mismos datos piloto; generalizado para funcionar con cualquier libro/capítulos/N modelos en vez de contenido curado a mano.
   - `visualize_emotions.py` (raíz) absorbido por `build_report.py` y eliminado como script suelto.

3. **Documentación:**
   - `docs/notebook_conventions.md` eliminado (ya no aplica).
   - `docs/roadmap_nlp_wot.md`: Milestones 2, 4 y 5 actualizados para reflejar reportes HTML en vez de notebooks.
   - `README.md`: quitada la carpeta `notebooks/` de la estructura del proyecto.

**Impacto:**
- Menos capas de abstracción sin uso real (pipeline-clase, aggregator).
- Flujo de análisis reproducible sin depender de Jupyter: `analyze_book()` → `build_report()`.
- Prueba de humo (`build_report('WoT_01', ...)`) ejecutada contra datos reales existentes: genera correctamente las 5 secciones esperadas.

**Autor:**
- Claude (Sonnet 5), coordinado con otra sesión de Claude Code trabajando en paralelo sobre la eliminación de VADER.

---

### [Fecha del cambio: 2026-03-14 11:12]

**Archivo(s) Modificado(s):**
- `src/analysis/sentiment/emotion_detector.py` (modificado)
- `src/analysis/character/name_cleaner.py` (nuevo)
- `src/analysis/character/pov_detector.py` (nuevo)
- `src/analysis/sentiment/emotional_segmenter.py` (nuevo)
- `src/core/pipelines/sentiment_pipeline.py` (modificado)
- `src/analysis/character/__init__.py` (modificado)

**Tipo de cambio:** Feature - Mejoras de calidad Milestone 2

**Descripción del cambio:**

1. **Análisis por oraciones con agregación ponderada**:
   - Divide capítulo en oraciones con spaCy
   - Clasifica cada oración individualmente
   - Excluye oraciones con neutral > 70%
   - Promedia scores de oraciones no-neutrales
   - Resultado: neutral bajó de 82% a 30% (-51.6 puntos)
   - Emoción dominante ahora detecta sorpresa, tristeza, ira

2. **Limpieza de nombres detectados (NameCleaner)**:
   - Filtra verbos comunes (había, era, voy, etc.)
   - Filtra palabras comunes (aquella, este, cual, etc.)
   - Valida con spaCy POS tagging (PROPN)
   - Separa nombres con conjunciones (Y, y, e)
   - Resultado: 50 → 37 personajes (-13 falsos positivos)

3. **Unificación de nombres**:
   - Elimina títulos (Lady, Lord, Maese)
   - Combina variantes del mismo personaje

4. **POV detector mejorado (POVDetector)**:
   - Análisis de verbos de percepción, pensamiento y emoción
   - Scoring ponderado por tipo de verbo
   - Soporte para múltiples POVs por capítulo (threshold 25%)
   - Resultado: detecta Rand, Tam|Rand según capítulo

5. **Métricas híbridas en CSV**:
   - `_full`: análisis de texto completo (tono general)
   - `_emotional`: análisis por oraciones (emociones de personajes)
   - Nueva columna `lista_personajes` con top 10

**Resultados (BETO, 5 capítulos WoT_01):**

| Métrica | Full | Emotional |
|---------|------|-----------|
| Neutral | 81.9% | 30.2% |
| Sorpresa | 5.8% | 25.1% |
| Ira | 7.3% | 15.3% |
| Tristeza | 3.4% | 12.5% |
| Miedo | 0.7% | 11.7% |
| Alegría | 0.7% | 3.9% |

### [Fecha del cambio: 2026-03-13 23:58]

**Archivo(s) Modificado(s):**
- `src/analysis/character/detector.py` (nuevo)
- `src/analysis/character/matcher.py` (nuevo)
- `src/analysis/sentiment/analyzer.py` (nuevo)
- `src/analysis/sentiment/emotion_detector.py` (nuevo)
- `src/analysis/sentiment/aggregator.py` (nuevo)
- `src/analysis/sentiment/radar_builder.py` (nuevo)
- `src/core/pipelines/sentiment_pipeline.py` (nuevo)
- `notebooks/05.sentiment_baseline.ipynb` (nuevo)

**Tipo de cambio:** Feature - Milestone 2 completado

**Descripción del cambio:**
Implementación completa del pipeline de análisis de sentimiento y detección de emociones:

1. **Detección de Personajes con NER (spaCy)**:
   - Detector de entidades PERSON usando `es_core_news_lg`
   - Matching contra dataset de referencia con fuzzy matching
   - Identificación automática de POV por frecuencia de menciones
   - Detección de 50 nuevos candidatos de personajes

2. **Análisis de Sentimiento**:
   - Polaridad con VADER (baseline)
   - Scores: positivo/negativo/neutral

3. **Detección de Emociones**:
   - Modelos: BETO y RoBERTuito emotion analysis
   - 6 emociones de Ekman + neutral
   - Truncation automático según límites del modelo (BETO: 450 tokens, RoBERTuito: 100 tokens)

4. **Outputs Generados**:
   - CSVs de polaridad y emociones por capítulo
   - JSON de radar charts (global, por personaje, temporal)
   - CSV de nuevos personajes detectados

5. **Resultados Iniciales (5 capítulos de WoT_01)**:
   - Personaje POV dominante: Matrim Cauthon (4/5 capítulos)
   - Emoción dominante: Neutral (~82% en ambos modelos)
   - BETO detecta más ira y sorpresa
   - RoBERTuito detecta más tristeza

**Impacto:**
- ✅ Milestone 2 completado
- Pipeline end-to-end funcional
- Base para análisis comparativo de personajes
- Preparado para escalar a 53 capítulos completos

**Próximos pasos:**
- Validar POV identificados manualmente
- Decidir modelo final (BETO vs RoBERTuito)
- Procesar libro completo
- Milestone 3: Tracking de arcos narrativos

### [Fecha del cambio: 2026-03-13 22:40]

**Archivo(s) Modificado(s):**  
- `pyproject.toml` (nuevo)
- `poetry.lock` (nuevo)
- `data/reference/characters.csv` (nuevo)
- `data/reference/README.md`
- `docs/data_formats.md` (nuevo)
- `docs/notebook_conventions.md` (nuevo)
- `docs/roadmap_nlp_wot.md`
- `.gitignore`
- `README.md`

**Tipo de cambio:**  
- Completación de Milestone 1
- Migración a Poetry
- Creación de documentación base

**Descripción del cambio:**  

**1. Migración a Poetry:**
- Creado `pyproject.toml` con todas las dependencias del proyecto
- Actualizado requisito de Python a 3.10+ (compatibilidad con networkx 3.2+)
- Generado `poetry.lock` para reproducibilidad
- Eliminado `requirements.txt` (reemplazado por Poetry)
- Actualizado README con instrucciones de Poetry

**2. Dataset de Personajes:**
- Creado `data/reference/characters.csv` con 20 personajes semilla de The Wheel of Time
- Incluye campos para estrategia evolutiva: `source`, `validation_status`, `notes`
- Personajes POV principales y secundarios importantes
- Documentada estrategia de expansión con NER en `data/reference/README.md`

**3. Documentación de Formatos de Datos:**
- Creado `docs/data_formats.md` con especificaciones completas
- Schemas para análisis de sentimiento (por capítulo y por libro)
- Schemas para análisis de personajes (detecciones, co-ocurrencias, POV)
- Schemas para evolución temporal
- Todos los formatos en español

**4. Convenciones de Notebooks:**
- Creado `docs/notebook_conventions.md` con estándares del proyecto
- Nomenclatura por fases (01-09)
- Template estándar de estructura interna
- Convenciones de código, visualización y documentación
- Checklist pre-commit

**5. Actualización de Roadmap:**
- Marcado Milestone 1 como completado en `docs/roadmap_nlp_wot.md`
- Actualizada sección de Stack Técnico con Poetry
- Definidos próximos pasos para Milestone 2 (Sentiment Analysis)
- Actualizada fecha de estado

**6. Ajustes en .gitignore:**
- Agregada excepción para permitir `data/reference/*.csv`
- Mantiene exclusión de otros archivos CSV

**Impacto:**
- Milestone 1 completado al 100%
- Base sólida para implementar Milestone 2 (Sentiment Analysis)
- Documentación técnica completa y en español
- Gestión de dependencias moderna con Poetry
- Dataset de personajes listo para expansión con NER

**Autor:**  
- Windsurf IA

---

### [Fecha del cambio: 2026-03-11 22:30]

**Archivo(s) Modificado(s):**  
- Estructura completa del proyecto
- notebooks/ (eliminados 3, renombrado 1)
- scripts/ (renombrado run_character_analysis.py → process_books.py)
- src/ (reorganización completa)
- requirements.txt
- .gitignore
- data/ (nueva estructura de outputs)

**Tipo de cambio:**  
- Refactorización mayor
- Limpieza de código
- Preparación para roadmap NLP

**Descripción del cambio:**  

**1. Limpieza de archivos obsoletos:**
- Eliminados notebooks antiguos: `01.Lectura_Data.ipynb`, `02.NLP_Basico.ipynb`, `04.Wordcloud.ipynb` (funcionalidad migrada a módulos).
- Eliminado `evaluacion.md` (obsoleto).
- Eliminado `.coverage` (debe estar en .gitignore).
- Eliminadas carpetas vacías: `src/character_analysis/`, `assets/`.

**2. Reorganización de estructura:**
- Consolidado logger en `src/config/logging.py` (eliminado duplicado de `src/utils/`).
- Movido `src/data/loader.py` → `src/core/services/book_loader.py`.
- Movido `src/data/preprocessor.py` → `src/core/services/text_processor.py`.
- Movido `src/data/preprocessing/*` → `src/preprocessing/` (nivel superior).
- Eliminadas carpetas `src/data/` y `src/utils/` (obsoletas).
- Renombrado `notebooks/03.Sentimental_Analysis.ipynb` → `notebooks/05.Sentiment_Analysis_Exploration.ipynb`.

**3. Refactorización de scripts:**
- Renombrado `scripts/run_character_analysis.py` → `scripts/process_books.py`.
- Renombrada función `run_character_analysis()` → `process_book()`.
- Actualizado `run.py` para reflejar nuevos nombres.
- Mejorada documentación de funciones con docstrings completos.

**4. Actualización de dependencias:**
- Expandido `requirements.txt` con stack NLP completo:
  - spaCy, transformers, torch (NLP avanzado)
  - vaderSentiment, TextBlob (análisis de sentimiento)
  - pandas, numpy (procesamiento de datos)
  - plotly, matplotlib, seaborn, wordcloud, networkx (visualización)
  - tqdm, pytest (utilidades)

**5. Estructura de datos:**
- Creadas carpetas: `data/outputs/`, `data/outputs/sentiment/`, `data/outputs/characters/`, `data/outputs/evolution/`, `data/reference/`.
- Añadidos README.md en `data/reference/` y `data/outputs/` con especificaciones.
- Actualizado `.gitignore` para excluir `data/outputs/` y archivos de coverage.

**6. Documentación:**
- Creado `docs/roadmap_nlp_wot.md` con plan maestro del proyecto (5 milestones).
- Creada carpeta `docs/` para documentación técnica.

**7. Actualización de imports:**
- Todos los módulos actualizados para usar nuevas rutas:
  - `src.config.logging` (logger)
  - `src.core.services.book_loader` (BookManager)
  - `src.core.services.text_processor` (TextProcessor)
  - `src.preprocessing.cleaning` y `src.preprocessing.chapters` (helpers)
- Tests actualizados en `tests/tests_data/test_loader.py`.

**Impacto:**
- Proyecto limpio y listo para implementar roadmap NLP.
- Estructura modular y escalable.
- Eliminada deuda técnica (duplicados, archivos obsoletos).
- Base sólida para análisis de sentimiento, detección de personajes y visualizaciones.

**Autor:**  
- Windsurf IA

---

**Estado:** Proyecto reorganizado y preparado para Milestone 1 del roadmap NLP.
