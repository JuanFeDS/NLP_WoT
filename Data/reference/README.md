# Reference Data

Esta carpeta contiene datos de referencia para el análisis NLP de The Wheel of Time.

## Archivos Esperados

### `characters.csv`
Lista de personajes principales y secundarios con metadata.

**Columnas sugeridas:**
- `name`: Nombre del personaje
- `aliases`: Alias o nombres alternativos (separados por `;`)
- `affiliation`: Afiliación (Aes Sedai, Two Rivers, etc.)
- `gender`: Género
- `first_appearance_book`: Número del libro donde aparece por primera vez
- `is_pov`: Si tiene capítulos POV (True/False)
- `importance`: Nivel de importancia (main, secondary, minor)

### `pov_patterns.json`
Patrones y reglas para identificar POV de capítulos.

### `locations.csv`
Ubicaciones importantes en la saga (opcional, para análisis geográfico).

## Estrategia de Expansión del Dataset

### Dataset Semilla (Manual)
El archivo `characters.csv` inicia con ~20 personajes principales curados manualmente:
- Personajes POV confirmados de The Wheel of Time
- Personajes secundarios críticos para la trama
- Metadata validada contra fuentes canónicas

**Campos para estrategia evolutiva:**
- `source`: `manual` (curado) o `ner` (detectado automáticamente)
- `validation_status`: `validated`, `pending`, `rejected`
- `notes`: Información contextual adicional

### Expansión Automática (NER - Milestone 3)
En fases posteriores, el dataset se expandirá usando Named Entity Recognition:

1. **Extracción con spaCy NER**
   - Detectar entidades PERSON en capítulos procesados
   - Filtrar por frecuencia de aparición (umbral mínimo)
   - Generar candidatos automáticos para validación

2. **Validación y Refinamiento**
   - Nuevos candidatos con `source=ner` y `validation_status=pending`
   - Revisión manual para confirmar/rechazar
   - Actualización de aliases y metadata

3. **Criterios de Calidad**
   - Mínimo 5 menciones en el corpus para considerar candidato
   - Validación cruzada con diccionario de nombres conocidos
   - Detección de variantes ortográficas y títulos

### Mantenimiento
- Revisar periódicamente candidatos pendientes
- Actualizar aliases cuando se detecten nuevas variantes
- Marcar como `rejected` falsos positivos del NER

## Uso

Estos archivos son utilizados por:
- `src/analysis/character/detector.py` - Detección de personajes
- `src/analysis/character/pov_classifier.py` - Clasificación de POV
- `src/core/pipelines/character_pipeline.py` - Pipeline de análisis
