"""Chapter splitting helpers and patterns."""
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

# Regex patterns
PATTERN_CAPITULO = (
    r"(?im)^\s*(?:cap[ií]tulo)\s+"
    r"(\d{1,3}|[ivxlcdm]{1,7})\s*"
    r"(?:[:\-–—]\s*(.+))?$"
)
# Soporta capítulos con número en palabras sin hardcodear lista (e.g. "CAPÍTULO UNO Título")
# Captura cualquier token alfabético como número en palabras y, opcionalmente, un título inline.
PATTERN_CAPITULO_WORD = (
    r"(?im)^\s*(?:cap[ií]tulo)\s+"
    r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:\s+(?:y\s+)?[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*)\s*"
    r"(?:[:\-–—]\s*)?(.+)?$"
)
PATTERN_NUMERIC_DOT = r"(?m)^\s*(\d{1,3})\.\s+([^\n]+)$"
PATTERN_NUMERIC = r"(?m)^\s*(\d{1,3})\s+([^\n]+)$"


def get_chapter_matches(text: str) -> Tuple[List[re.Match], Optional[str]]:
    """Get chapter matches from text.

    Aggregates matches from all supported patterns to handle mixed styles
    within the same book. Results are sorted by position and deduplicated
    by start index.
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
    # Deduplicate by start index and sort
    by_start = {}
    for m in all_matches:
        s = m.start()
        # keep the first occurrence for a given start position
        if s not in by_start:
            by_start[s] = m
    merged = [by_start[k] for k in sorted(by_start.keys())]
    pat_name = used_names[0] if len(set(used_names)) == 1 else "mixed"
    return merged, pat_name


def infer_title(text: str, match: re.Match, end_idx: int) -> str:
    """Infer title from text after a chapter match."""
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
    """Sanitize title for filename."""
    slug = title.strip().replace(" ", "_").lower()
    slug = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in slug)
    return slug[:50]


def write_chapter(path: Path, content: str, logger) -> bool:
    """Write chapter to file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.getsize(path) > 0
    except OSError as e:
        logger.error("Error al escribir %s: %s", path, str(e))
        return False


def diagnose_candidate_headers(text: str, logger) -> None:
    """Diagnose candidate headers in text."""
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
