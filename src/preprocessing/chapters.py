"""Helpers y patrones para dividir capítulos."""
import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional

# Patrones regex
PATTERN_CAPITULO = (
    r"(?im)^\s*(?:cap[ií]tulo)\s+"
    r"(\d{1,3}|[ivxlcdm]{1,7})\s*"
    r"(?:[:\-–—]\s*(.+))?$"
)
# Soporta capítulos con número en palabras sin hardcodear lista (ej: "CAPÍTULO UNO")
# Captura solo el número en palabras (una o dos palabras máximo)
PATTERN_CAPITULO_WORD = (
    r"(?im)^\s*(?:cap[ií]tulo)\s+"
    r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:\s+(?:y\s+)?[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)?)\s*$"
)
# Patrones numéricos: solo líneas que parecen títulos de capítulo (mayúsculas o longitud razonable)
# Evita detectar listas como "1 varita." o "1. Item de lista"
PATTERN_NUMERIC_DOT = r"(?m)^\s*(\d{1,3})\.\s+([A-ZÁÉÍÓÚÜÑ][^\n]{10,})$"
PATTERN_NUMERIC = r"(?m)^\s*(\d{1,3})\s+([A-ZÁÉÍÓÚÜÑ][^\n]{10,})$"


def get_chapter_matches(text: str) -> Tuple[List[re.Match], Optional[str]]:
    """Obtiene coincidencias de capítulos del texto.

    Agrega coincidencias de todos los patrones soportados para manejar estilos mixtos
    dentro del mismo libro. Los resultados se ordenan por posición y se deduplicam
    por índice de inicio.
    """
    patterns = (
        (PATTERN_CAPITULO, "capitulo"),
        (PATTERN_CAPITULO_WORD, "capitulo_word"),
        (PATTERN_NUMERIC_DOT, "numeric_dot"),
        (PATTERN_NUMERIC, "numeric"),
    )
    all_matches: List[re.Match] = []
    used_names: List[str] = []
    for pat, name in patterns:
        found = list(re.finditer(pat, text))
        if found:
            all_matches.extend(found)
            used_names.append(name)
    if not all_matches:
        return [], None
    # Deduplicar por índice de inicio y ordenar
    by_start = {}
    for m in all_matches:
        s = m.start()
        # mantener la primera ocurrencia para una posición de inicio dada
        if s not in by_start:
            by_start[s] = m
    merged = [by_start[k] for k in sorted(by_start.keys())]
    pat_name = used_names[0] if len(set(used_names)) == 1 else "mixed"
    return merged, pat_name


def infer_title(text: str, match: re.Match, end_idx: int) -> str:
    """Infiere el título del texto después de una coincidencia de capítulo."""
    title = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
    if title:
        return title
    after = text[match.end():end_idx]
    for line in after.splitlines():
        s = line.strip()
        if s:
            return s
    return ""


def sanitize_title(title: str) -> str:
    """Sanitiza el título para nombre de archivo."""
    slug = title.strip().replace(" ", "_").lower()
    slug = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in slug)
    return slug[:50]


def write_chapter(path: Path, content: str, logger, metadata: Optional[dict] = None) -> bool:
    """Escribe capítulo a archivo como JSON con metadata opcional.

    La estructura JSON es: {"content": str, ...metadata}
    """
    try:
        # Construir payload con metadata primero para preservar orden de claves en JSON
        payload = {}
        if metadata:
            for k, v in metadata.items():
                payload[k] = v
        # Agregar contenido como última clave
        payload["content"] = content
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return os.path.getsize(path) > 0
    except OSError as e:
        logger.error("Error al escribir %s: %s", path, str(e))
        return False


def diagnose_candidate_headers(text: str, logger) -> None:
    """Diagnostica encabezados candidatos en el texto."""
    try:
        # Buscar líneas que parezcan encabezados de capítulo
        pats = [
            r"(?im)^\s*cap[ií]tulo\s+[^\n]*$",
            r"(?m)^\s*\d{1,3}(?:[\.:]|\s+)[^\n]*$",
        ]
        candidates: list[str] = []
        for p in pats:
            candidates.extend(re.findall(p, text))
        sample = candidates[:20]
        if sample:
            logger.info("Líneas candidatas a encabezado (primeras 20): %s", sample)
    except Exception:
        pass
