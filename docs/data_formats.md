# Formatos de Datos - NLP WoT

Este documento especifica los formatos estándar para todos los outputs de análisis del proyecto.

## 1. Análisis de Sentimiento y Emociones

### Estructura de Directorios

```
data/outputs/sentiment/
├── emociones/
│   ├── por_capitulo/
│   │   ├── WoT_01_emociones.csv
│   │   └── ...
│   ├── por_libro/
│   │   └── WoT_01_emociones_agregadas.csv
│   └── radar/
│       ├── WoT_01_radar_data.json
│       └── ...
└── metadata.json
```

> Se eliminó la polaridad baseline con VADER: su léxico es en inglés y no reconoce el texto en español (en la práctica, ~0.4% de las palabras del corpus), y aplicado a capítulos completos su score compuesto satura al extremo negativo sin importar el contenido real. La detección de emociones (BETO/RoBERTuito) es la métrica vigente.

### Schema: Detección de Emociones Específicas

**Archivo:** `emociones/por_capitulo/{libro_id}_emociones.csv`

Basado en las **6 emociones de Ekman** + neutral:
- `alegria` (joy)
- `tristeza` (sadness)
- `ira` (anger)
- `miedo` (fear)
- `sorpresa` (surprise)
- `disgusto` (disgust)
- `neutral`

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `libro_id` | string | Identificador del libro | `WoT_01` |
| `numero_capitulo` | int | Número de capítulo | `1` |
| `titulo_capitulo` | string | Título del capítulo | `Un camino solitario` |
| `emocion_dominante` | string | Emoción con mayor score | `miedo` |
| `score_alegria` | float | Probabilidad de alegría (0-1) | `0.12` |
| `score_tristeza` | float | Probabilidad de tristeza (0-1) | `0.18` |
| `score_ira` | float | Probabilidad de ira (0-1) | `0.08` |
| `score_miedo` | float | Probabilidad de miedo (0-1) | `0.35` |
| `score_sorpresa` | float | Probabilidad de sorpresa (0-1) | `0.15` |
| `score_disgusto` | float | Probabilidad de disgusto (0-1) | `0.05` |
| `score_neutral` | float | Probabilidad de neutral (0-1) | `0.07` |
| `modelo` | string | Modelo usado | `beto-emotion`, `robertuito-emotion` |
| `confianza` | float | Confianza del modelo (0-1) | `0.85` |
| `timestamp` | datetime | Fecha de análisis | `2026-03-13T22:30:00Z` |
| `personaje_pov` | string | Personaje POV (opcional) | `Rand al'Thor` |

**Ejemplo CSV:**
```csv
libro_id,numero_capitulo,titulo_capitulo,emocion_dominante,score_alegria,score_tristeza,score_ira,score_miedo,score_sorpresa,score_disgusto,score_neutral,modelo,confianza,timestamp,personaje_pov
WoT_01,1,Un camino solitario,miedo,0.12,0.18,0.08,0.35,0.15,0.05,0.07,beto-emotion,0.85,2026-03-13T22:30:00Z,Rand al'Thor
WoT_01,2,Forasteros,ira,0.10,0.22,0.38,0.15,0.08,0.04,0.03,beto-emotion,0.82,2026-03-13T22:30:00Z,Rand al'Thor
```

### Schema: Emociones Agregadas por Libro

**Archivo:** `emociones/por_libro/{libro_id}_emociones_agregadas.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `libro_id` | string | Identificador del libro |
| `titulo_libro` | string | Título completo |
| `promedio_alegria` | float | Promedio de alegría |
| `promedio_tristeza` | float | Promedio de tristeza |
| `promedio_ira` | float | Promedio de ira |
| `promedio_miedo` | float | Promedio de miedo |
| `promedio_sorpresa` | float | Promedio de sorpresa |
| `promedio_disgusto` | float | Promedio de disgusto |
| `promedio_neutral` | float | Promedio de neutral |
| `emocion_dominante_libro` | string | Emoción más frecuente |
| `capitulos_analizados` | int | Total de capítulos |
| `modelo` | string | Modelo usado |
| `timestamp` | datetime | Fecha de análisis |

### Schema: Datos para Radar Chart

**Archivo:** `emociones/radar/{libro_id}_radar_data.json`

Formato optimizado para visualización con radar/spider charts:

```json
{
  "libro_id": "WoT_01",
  "titulo": "El Ojo del Mundo",
  "timestamp": "2026-03-13T22:30:00Z",
  "modelo": "beto-emotion",
  "emociones_globales": {
    "alegria": 0.15,
    "tristeza": 0.22,
    "ira": 0.18,
    "miedo": 0.25,
    "sorpresa": 0.12,
    "disgusto": 0.08
  },
  "por_personaje": [
    {
      "personaje": "Rand al'Thor",
      "capitulos_pov": 25,
      "emociones": {
        "alegria": 0.12,
        "tristeza": 0.28,
        "ira": 0.15,
        "miedo": 0.30,
        "sorpresa": 0.10,
        "disgusto": 0.05
      }
    },
    {
      "personaje": "Matrim Cauthon",
      "capitulos_pov": 8,
      "emociones": {
        "alegria": 0.25,
        "tristeza": 0.10,
        "ira": 0.20,
        "miedo": 0.15,
        "sorpresa": 0.22,
        "disgusto": 0.08
      }
    }
  ],
  "evolucion_temporal": [
    {
      "rango_capitulos": "1-10",
      "emociones": {
        "alegria": 0.18,
        "tristeza": 0.15,
        "ira": 0.12,
        "miedo": 0.28,
        "sorpresa": 0.20,
        "disgusto": 0.07
      }
    },
    {
      "rango_capitulos": "11-20",
      "emociones": {
        "alegria": 0.14,
        "tristeza": 0.25,
        "ira": 0.22,
        "miedo": 0.20,
        "sorpresa": 0.10,
        "disgusto": 0.09
      }
    }
  ]
}
```

### Schema: Resumen por Libro

**Archivo:** `resumen_libros.csv`

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `libro_id` | string | Identificador del libro | `WoT_01` |
| `titulo_libro` | string | Título completo | `El Ojo del Mundo` |
| `sentimiento_promedio` | float | Promedio de sentimiento | `0.12` |
| `varianza_sentimiento` | float | Varianza del sentimiento | `0.34` |
| `capitulos_analizados` | int | Número de capítulos | `53` |
| `palabras_totales` | int | Total de palabras | `305420` |
| `modelo` | string | Modelo usado | `vader` |
| `timestamp` | datetime | Fecha de análisis | `2026-03-13T22:30:00Z` |

### Metadata del Análisis

**Archivo:** `metadata.json`

```json
{
  "version": "1.0",
  "fecha_generacion": "2026-03-13T22:30:00Z",
  "modelos_usados": ["vader", "textblob"],
  "configuracion": {
    "idioma": "es",
    "normalizacion_ascii": true,
    "umbral_neutral": 0.05
  },
  "estadisticas": {
    "total_libros": 3,
    "total_capitulos": 123,
    "total_palabras": 850000
  }
}
```

## 2. Análisis de Personajes

### Estructura de Directorios

```
data/outputs/characters/
├── detecciones/
│   ├── WoT_01_personajes.csv
│   └── ...
├── co_ocurrencias/
│   ├── WoT_01_red.csv
│   └── ...
├── pov/
│   ├── WoT_01_pov.csv
│   └── ...
└── metadata.json
```

### Schema: Detecciones de Personajes

**Archivo:** `{libro_id}_personajes.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `libro_id` | string | Identificador del libro |
| `numero_capitulo` | int | Número de capítulo |
| `personaje` | string | Nombre del personaje |
| `menciones` | int | Número de menciones |
| `primera_mencion` | int | Posición de primera mención |
| `ultima_mencion` | int | Posición de última mención |
| `confianza_ner` | float | Confianza del NER (0-1) |

### Schema: Co-ocurrencias

**Archivo:** `{libro_id}_red.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `personaje_a` | string | Primer personaje |
| `personaje_b` | string | Segundo personaje |
| `co_ocurrencias` | int | Número de co-ocurrencias |
| `capitulos_compartidos` | int | Capítulos donde aparecen juntos |
| `peso` | float | Peso de la relación (normalizado) |

### Schema: Clasificación POV

**Archivo:** `{libro_id}_pov.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `libro_id` | string | Identificador del libro |
| `numero_capitulo` | int | Número de capítulo |
| `titulo_capitulo` | string | Título del capítulo |
| `personaje_pov` | string | Personaje POV detectado |
| `confianza` | float | Confianza de la clasificación |
| `metodo` | string | Método usado (`patron`, `ml`, `manual`) |

## 3. Evolución Temporal

### Schema: Evolución de Sentimiento

**Archivo:** `evolucion_sentimiento.csv`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `libro_id` | string | Identificador del libro |
| `numero_capitulo` | int | Número de capítulo |
| `posicion_relativa` | float | Posición en el libro (0-1) |
| `sentimiento` | float | Score de sentimiento |
| `personaje_pov` | string | Personaje POV |
| `media_movil_5` | float | Media móvil de 5 capítulos |

## 4. Convenciones Generales

### Nombres de Archivos
- Usar snake_case: `resumen_libros.csv`
- Incluir identificador de libro cuando aplique: `WoT_01_capitulos.csv`
- Usar extensión apropiada: `.csv` para datos tabulares, `.json` para metadata

### Encoding
- Todos los archivos CSV: UTF-8 con BOM
- Separador: coma (`,`)
- Quote character: comillas dobles (`"`)

### Fechas y Timestamps
- Formato ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`
- Zona horaria: UTC

### Valores Nulos
- CSV: campo vacío o `NA`
- JSON: `null`

### Idioma
- Todos los campos y valores en español
- Etiquetas de sentimiento: `positivo`, `negativo`, `neutral`
- Nombres de personajes: mantener forma original (inglés)

## 5. Validación

Cada output debe incluir:
1. Timestamp de generación
2. Versión del formato
3. Modelo/método usado
4. Parámetros de configuración relevantes

Los archivos deben validarse contra estos schemas antes de ser considerados finales.
