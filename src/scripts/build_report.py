"""Genera un reporte HTML editorial con el análisis de emociones de un libro.

El diseño (tipografía, paleta, componentes) reutiliza clases CSS pensadas para que
`conclusiones` pueda incluir bloques `<div class="callout">...</div>` o
`<ul class="pending">...</ul>` con la interpretación cualitativa del análisis.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.config.logger import get_logger

EMOCIONES = ['alegria', 'tristeza', 'ira', 'miedo', 'sorpresa', 'disgusto', 'neutral']
EMOTION_LABELS = {
    'alegria': 'Alegría', 'tristeza': 'Tristeza', 'ira': 'Ira', 'miedo': 'Miedo',
    'sorpresa': 'Sorpresa', 'disgusto': 'Disgusto', 'neutral': 'Neutral',
}


def build_report(libro_id: str, output_dir: Path, conclusiones: str = "") -> Path:
    """Genera el reporte HTML de un libro a partir de los CSV que produce analyze_book().

    Args:
        libro_id: ID del libro (ej: 'WoT_01').
        output_dir: Directorio de salida usado por analyze_book (contiene sentiment/emociones/...).
        conclusiones: HTML con la interpretación de resultados (opcional). Puede usar las
            clases `.callout`, `.evidence-pair`/`.evidence-box` o `ul.pending` del sistema
            de diseño para resaltar hallazgos.

    Returns:
        Ruta del archivo HTML generado.
    """
    logger = get_logger(__name__)

    emociones_dir = output_dir / "sentiment" / "emociones" / "por_capitulo"
    dataframes = _load_model_dataframes(libro_id, emociones_dir)
    if not dataframes:
        raise FileNotFoundError(
            f"No se encontraron CSVs de emociones para {libro_id} en {emociones_dir}"
        )

    model_keys = sorted(dataframes)
    primary_model = model_keys[0]
    df_primary = dataframes[primary_model]
    titulo_libro = (
        _safe(df_primary['titulo_libro'].iloc[0], libro_id) if not df_primary.empty else libro_id
    )

    reportes_dir = output_dir / "sentiment" / "reportes"
    reportes_dir.mkdir(parents=True, exist_ok=True)
    report_path = reportes_dir / f"{libro_id}_reporte.html"

    html = _render_report(
        libro_id, titulo_libro, dataframes, model_keys, primary_model, conclusiones
    )
    report_path.write_text(html, encoding='utf-8')

    logger.info("Reporte guardado en %s", report_path)

    return report_path


def _safe(value, default: str = '—') -> str:
    """Devuelve `default` si `value` es NaN/None, o el valor como string."""
    return default if pd.isna(value) else str(value)


def _load_model_dataframes(libro_id: str, emociones_dir: Path) -> Dict[str, pd.DataFrame]:
    """Carga los CSV de emociones disponibles para un libro, uno por modelo."""
    dataframes = {}
    for csv_file in sorted(emociones_dir.glob(f"{libro_id}_*_emociones.csv")):
        model_key = csv_file.stem.removeprefix(f"{libro_id}_").removesuffix("_emociones")
        dataframes[model_key] = pd.read_csv(csv_file)
    return dataframes


def _compute_tiles(
    dataframes: Dict[str, pd.DataFrame], model_keys: List[str], primary_model: str
) -> List[Dict[str, str]]:
    """Métricas de resumen ejecutivo, calculadas a partir de los datos (sin narrativa)."""
    df = dataframes[primary_model]

    full_neutral = df['score_neutral_full'].mean() * 100
    emo_neutral = df['score_neutral_emotional'].mean() * 100

    tiles = [
        {'value': str(len(df)), 'label': f'Capítulos analizados con {primary_model}'},
        {
            'value': f'{full_neutral:.0f}% → {emo_neutral:.0f}%',
            'label': f'Neutral promedio ({primary_model}): texto completo vs. por oración',
        },
    ]

    if len(model_keys) > 1:
        secondary_model = model_keys[1]
        df_secondary = dataframes[secondary_model]
        n = min(len(df), len(df_secondary))
        coincide = (
            df['emocion_dominante_emotional'].values[:n]
            == df_secondary['emocion_dominante_emotional'].values[:n]
        )
        discrepancias = n - int(coincide.sum())
        tiles.append({
            'value': f'{discrepancias} / {n}',
            'label': f'Capítulos donde {primary_model} y {secondary_model} '
                     'eligen una emoción dominante distinta',
        })

    personajes = set()
    for lista in df['lista_personajes'].dropna():
        personajes.update(p for p in str(lista).split('|') if p)
    tiles.append({
        'value': str(len(personajes)),
        'label': 'Personajes distintos detectados en los capítulos analizados',
    })

    return tiles


def _stack_bar(row: pd.Series, suffix: str) -> str:
    """Barra apilada (una franja por emoción) para la fila de un capítulo."""
    segments = []
    for emocion in EMOCIONES:
        pct = row[f'score_{emocion}_{suffix}'] * 100
        segments.append(
            f'<div class="stack-seg" style="width:{pct:.4f}%;background:var(--em-{emocion});" '
            f'title="{EMOTION_LABELS[emocion]}: {pct:.1f}%"></div>'
        )
    return f'<div class="stack-bar">{"".join(segments)}</div>'


def _render_legend() -> str:
    items = ''.join(
        f'<span class="legend-item"><span class="legend-swatch" '
        f'style="background:var(--em-{e})"></span>{EMOTION_LABELS[e]}</span>'
        for e in EMOCIONES
    )
    return f'<div class="legend">{items}</div>'


def _render_chapter_panels(df: pd.DataFrame) -> str:
    """Un panel por capítulo: título, POV, barras FULL/EMOTIONAL y emociones dominantes."""
    panels = []
    for _, row in df.iterrows():
        pov = _safe(row.get('personaje_pov')).replace('|', ' · ')
        dom_full = row['emocion_dominante_full']
        dom_emo = row['emocion_dominante_emotional']
        panels.append(f"""
        <div class="chapter-panel">
          <div class="chapter-head">
            <div class="chapter-title-group">
              <span class="chapter-num">Cap. {int(row['numero_capitulo']):02d}</span>
              <span class="chapter-title">{row['titulo_capitulo']}</span>
            </div>
            <span class="chapter-pov">POV <b>{pov}</b></span>
          </div>
          <div class="bar-rows">
            <div class="bar-row">
              <span class="bar-row-label">Completo</span>{_stack_bar(row, 'full')}
            </div>
            <div class="bar-row">
              <span class="bar-row-label">Por oración</span>{_stack_bar(row, 'emotional')}
            </div>
          </div>
          <div class="dom-line">
            <span>Dominante completo:
              <span class="dom-emotion">{EMOTION_LABELS.get(dom_full, dom_full)}</span></span>
            <span>Dominante por oración:
              <span class="dom-emotion">{EMOTION_LABELS.get(dom_emo, dom_emo)}</span></span>
            <span>Neutral: {row['score_neutral_full'] * 100:.0f}%
              → {row['score_neutral_emotional'] * 100:.0f}%</span>
          </div>
        </div>
        """)
    return ''.join(panels)


def _render_tabla(dataframes: Dict[str, pd.DataFrame], model_keys: List[str]) -> str:
    """Tabla capítulo por capítulo con la emoción dominante de cada modelo."""
    primary = dataframes[model_keys[0]]
    headers = ['Cap.', 'Título', 'POV', 'Personajes'] + model_keys
    if len(model_keys) > 1:
        headers.append('¿Coinciden?')

    rows_html = []
    for idx in range(len(primary)):
        row_primary = primary.iloc[idx]
        cells = [
            f'<td class="mono">{int(row_primary["numero_capitulo"]):02d}</td>',
            f'<td class="emph">{row_primary["titulo_capitulo"]}</td>',
            f'<td class="mono">{_safe(row_primary.get("personaje_pov")).replace("|", " · ")}</td>',
            f'<td class="mono">{row_primary["personajes_detectados"]}</td>',
        ]
        dominantes = []
        for model_key in model_keys:
            df_model = dataframes[model_key]
            if idx < len(df_model):
                dom = df_model.iloc[idx]['emocion_dominante_emotional']
                dominantes.append(dom)
                cells.append(f'<td>{EMOTION_LABELS.get(dom, dom)}</td>')
            else:
                cells.append('<td>—</td>')
        if len(model_keys) > 1:
            coincide = len(set(dominantes)) == 1
            css_class = 'agree-yes' if coincide else 'agree-no'
            texto = 'Sí' if coincide else 'No'
            cells.append(f'<td class="{css_class}">{texto}</td>')
        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    thead = ''.join(f'<th>{h}</th>' for h in headers)
    return (
        '<div class="table-wrap"><table>'
        f'<thead><tr>{thead}</tr></thead><tbody>{"".join(rows_html)}</tbody>'
        '</table></div>'
    )


def _render_concordancia(dataframes: Dict[str, pd.DataFrame], model_keys: List[str]) -> str:
    """Correlación por emoción entre los dos primeros modelos disponibles (EMOTIONAL)."""
    df_a = dataframes[model_keys[0]]
    df_b = dataframes[model_keys[1]]
    n = min(len(df_a), len(df_b))

    correlaciones = {}
    for emocion in EMOCIONES:
        if emocion == 'neutral' or n < 2:
            continue
        serie_a = pd.Series(df_a[f'score_{emocion}_emotional'].values[:n])
        serie_b = pd.Series(df_b[f'score_{emocion}_emotional'].values[:n])
        correlaciones[emocion] = serie_a.corr(serie_b)

    filas = []
    for emocion, corr in sorted(
        correlaciones.items(), key=lambda kv: (kv[1] if pd.notna(kv[1]) else -1), reverse=True
    ):
        valor = f'{corr:.2f}' if pd.notna(corr) else 's/d'
        pct = max(min(corr, 1.0), 0.0) * 100 if pd.notna(corr) else 0
        filas.append(f"""
        <div class="conc-row">
          <span class="conc-label">{EMOTION_LABELS[emocion]}</span>
          <span class="conc-track"><span class="conc-fill" style="width:{pct:.0f}%;background:var(--em-{emocion});"></span></span>
          <span class="conc-value">{valor}</span>
        </div>
        """)
    return f'<div class="conc-list">{"".join(filas)}</div>'


def _render_char_pills(df: pd.DataFrame, top_n: int = 14) -> str:
    """Los personajes más frecuentes detectados, como pills con su conteo de capítulos."""
    counter: Dict[str, int] = {}
    for lista in df['lista_personajes'].dropna():
        for nombre in str(lista).split('|'):
            nombre = nombre.strip()
            if nombre:
                counter[nombre] = counter.get(nombre, 0) + 1

    top = sorted(counter.items(), key=lambda kv: -kv[1])[:top_n]
    pills = ''.join(
        f'<span class="char-pill">{nombre} <b>· {count}</b></span>' for nombre, count in top
    )
    return f'<div class="char-pills">{pills}</div>'


def _render_report(
    libro_id: str,
    titulo_libro: str,
    dataframes: Dict[str, pd.DataFrame],
    model_keys: List[str],
    primary_model: str,
    conclusiones: str,
) -> str:
    """Arma el HTML completo: masthead, secciones numeradas y footer."""
    df_primary = dataframes[primary_model]
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
    n_capitulos = len(df_primary)
    cap_min = int(df_primary['numero_capitulo'].min())
    cap_max = int(df_primary['numero_capitulo'].max())

    sections: List[str] = []
    section_num = 0

    def add_section(titulo: str, body: str, extra_class: str = "") -> None:
        nonlocal section_num
        section_num += 1
        cls = f' class="{extra_class}"' if extra_class else ""
        sections.append(
            f'<section{cls}><div class="section-head">'
            f'<span class="section-num">{section_num:02d}</span><h2>{titulo}</h2></div>'
            f'{body}</section>'
        )

    tiles_html = ''.join(
        f'<div class="tile"><div class="tile-value">{t["value"]}</div>'
        f'<div class="tile-label">{t["label"]}</div></div>'
        for t in _compute_tiles(dataframes, model_keys, primary_model)
    )
    add_section('Resumen ejecutivo', f'<div class="tiles">{tiles_html}</div>')

    if conclusiones:
        add_section('Conclusiones', conclusiones, extra_class='prose')

    add_section(
        'Evolución de emociones por capítulo',
        _render_legend() + f'<div class="chapters">{_render_chapter_panels(df_primary)}</div>',
    )

    if len(model_keys) > 1:
        add_section(
            f'Concordancia entre modelos ({" vs. ".join(model_keys)})',
            _render_concordancia(dataframes, model_keys),
        )

    add_section('Capítulo por capítulo', _render_tabla(dataframes, model_keys))
    add_section('Personajes detectados', _render_char_pills(df_primary), extra_class='prose')

    meta_row = (
        f'<span><b>Corpus:</b> {libro_id}, cap. {cap_min}–{cap_max} ({n_capitulos} analizados)</span>'
        f'<span><b>Modelos:</b> {" · ".join(model_keys)}</span>'
        f'<span><b>Generado:</b> {fecha}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte de Emociones · {libro_id}</title>
{_CSS}
</head>
<body>
<div class="page">
  <header class="masthead">
    <span class="eyebrow">NLP_WoT · Análisis de emociones</span>
    <h1 class="title">{titulo_libro}</h1>
    <p class="dek">Sentimiento y emociones detectadas capítulo a capítulo en <em>{titulo_libro}</em> ({libro_id}).</p>
    <div class="meta-row">{meta_row}</div>
  </header>
  {''.join(sections)}
  <footer>Generado a partir de data/outputs/sentiment/ · {libro_id} · {n_capitulos} capítulos</footer>
</div>
</body>
</html>"""


_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,500&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F0F1F5;
    --surface: #FFFFFF;
    --surface-alt: #F7F7FA;
    --ink: #1B1D24;
    --ink-soft: #565A68;
    --ink-faint: #8A8D99;
    --border: #DADCE3;
    --border-soft: #E7E8EE;
    --accent: #5B4B8A;
    --accent-strong: #453569;
    --accent-soft: #ECE8F7;
    --warn: #A6531F;
    --warn-soft: #FBEEE3;
    --warn-border: #E7C6A6;
    --em-alegria: #AD8619;
    --em-tristeza: #3E6D9C;
    --em-ira: #B23A3A;
    --em-miedo: #2F6E6E;
    --em-sorpresa: #C06B2C;
    --em-disgusto: #5C7A4A;
    --em-neutral: #9A9DAA;
    --shadow-card: 0 1px 2px rgba(27,29,36,0.04), 0 1px 12px rgba(27,29,36,0.05);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #16171C; --surface: #1E2028; --surface-alt: #25272F;
      --ink: #E7E8ED; --ink-soft: #A6A9B7; --ink-faint: #6E7180;
      --border: #34363F; --border-soft: #2A2C34;
      --accent: #A392D1; --accent-strong: #C1B4E3; --accent-soft: #2A2440;
      --warn: #E3A574; --warn-soft: #332318; --warn-border: #5A3F26;
      --em-alegria: #DEBD5A; --em-tristeza: #74A2CE; --em-ira: #DD7C7C;
      --em-miedo: #5CA6A6; --em-sorpresa: #E0975C; --em-disgusto: #93B87C; --em-neutral: #9297A6;
      --shadow-card: 0 1px 2px rgba(0,0,0,0.3), 0 1px 16px rgba(0,0,0,0.25);
    }
  }
  :root[data-theme="dark"] {
    --bg: #16171C; --surface: #1E2028; --surface-alt: #25272F;
    --ink: #E7E8ED; --ink-soft: #A6A9B7; --ink-faint: #6E7180;
    --border: #34363F; --border-soft: #2A2C34;
    --accent: #A392D1; --accent-strong: #C1B4E3; --accent-soft: #2A2440;
    --warn: #E3A574; --warn-soft: #332318; --warn-border: #5A3F26;
    --em-alegria: #DEBD5A; --em-tristeza: #74A2CE; --em-ira: #DD7C7C;
    --em-miedo: #5CA6A6; --em-sorpresa: #E0975C; --em-disgusto: #93B87C; --em-neutral: #9297A6;
    --shadow-card: 0 1px 2px rgba(0,0,0,0.3), 0 1px 16px rgba(0,0,0,0.25);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: "Public Sans", -apple-system, "Segoe UI", sans-serif;
    font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased;
  }
  ::selection { background: var(--accent-soft); color: var(--ink); }
  .page { max-width: 980px; margin: 0 auto; padding: 56px 24px 96px; }
  .prose { max-width: 700px; }
  h1, h2, h3 { font-family: "Newsreader", Georgia, serif; text-wrap: balance; color: var(--ink); margin: 0; }
  .eyebrow {
    font-family: "IBM Plex Mono", monospace; font-size: 12px; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--accent); font-weight: 500;
  }
  header.masthead {
    display: flex; flex-direction: column; gap: 14px;
    padding-bottom: 40px; margin-bottom: 40px; border-bottom: 1px solid var(--border);
  }
  h1.title { font-size: clamp(2.1rem, 4vw, 2.9rem); font-weight: 500; line-height: 1.12; }
  .dek { max-width: 620px; color: var(--ink-soft); font-size: 1.05rem; line-height: 1.6; }
  .meta-row {
    display: flex; flex-wrap: wrap; gap: 24px; margin-top: 6px;
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px; color: var(--ink-faint);
  }
  .meta-row b { color: var(--ink-soft); font-weight: 600; }
  section { margin-bottom: 64px; }
  section:last-of-type { margin-bottom: 32px; }
  .section-head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; }
  .section-head h2 { font-size: 1.5rem; font-weight: 500; }
  .section-num {
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px;
    color: var(--ink-faint); font-variant-numeric: tabular-nums;
  }
  p { color: var(--ink-soft); }
  strong { color: var(--ink); font-weight: 600; }
  .tiles {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
    background: var(--border); border: 1px solid var(--border);
    border-radius: 10px; overflow: hidden;
  }
  @media (max-width: 760px) { .tiles { grid-template-columns: repeat(2, 1fr); } }
  .tile { background: var(--surface); padding: 22px 20px; display: flex; flex-direction: column; gap: 6px; }
  .tile.warn-tile { background: var(--warn-soft); }
  .tile-value {
    font-family: "IBM Plex Mono", monospace; font-size: 1.5rem; font-weight: 600;
    font-variant-numeric: tabular-nums; color: var(--ink); letter-spacing: -0.01em;
  }
  .tile.warn-tile .tile-value { color: var(--warn); }
  .tile-label { font-size: 12.5px; color: var(--ink-soft); line-height: 1.4; }
  .callout {
    border: 1px solid var(--warn-border); background: var(--warn-soft); border-radius: 10px;
    padding: 24px 26px; display: flex; flex-direction: column; gap: 14px;
  }
  .callout-tag {
    font-family: "IBM Plex Mono", monospace; font-size: 11.5px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--warn); font-weight: 600;
  }
  .callout h3 { font-size: 1.25rem; font-weight: 500; }
  .callout p { color: var(--ink-soft); }
  .callout code {
    font-family: "IBM Plex Mono", monospace; font-size: 0.88em; background: var(--surface);
    border: 1px solid var(--warn-border); border-radius: 4px; padding: 1px 6px;
  }
  .evidence-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 4px; }
  @media (max-width: 640px) { .evidence-pair { grid-template-columns: 1fr; } }
  .evidence-box { background: var(--surface); border: 1px solid var(--warn-border); border-radius: 8px; padding: 14px 16px; }
  .evidence-box .ev-label {
    font-family: "IBM Plex Mono", monospace; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.06em; color: var(--ink-faint); margin-bottom: 6px;
  }
  .evidence-box .ev-text { font-family: "IBM Plex Mono", monospace; font-size: 13px; color: var(--ink-soft); }
  .evidence-box .ev-score {
    font-family: "IBM Plex Mono", monospace; font-size: 1.3rem; font-weight: 600;
    color: var(--ink); margin-top: 8px; font-variant-numeric: tabular-nums;
  }
  .chapters { display: flex; flex-direction: column; gap: 14px; }
  .chapter-panel {
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    padding: 20px 22px; box-shadow: var(--shadow-card);
  }
  .chapter-head {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
  }
  .chapter-title-group { display: flex; align-items: baseline; gap: 10px; }
  .chapter-num { font-family: "IBM Plex Mono", monospace; font-size: 12.5px; color: var(--ink-faint); }
  .chapter-title { font-family: "Newsreader", serif; font-size: 1.1rem; font-weight: 500; color: var(--ink); }
  .chapter-pov { font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-soft); }
  .chapter-pov b { color: var(--accent); font-weight: 600; }
  .bar-rows { display: flex; flex-direction: column; gap: 8px; }
  .bar-row { display: grid; grid-template-columns: 92px 1fr; gap: 12px; align-items: center; }
  .bar-row-label {
    font-family: "IBM Plex Mono", monospace; font-size: 11.5px; color: var(--ink-faint);
    text-transform: uppercase; letter-spacing: 0.04em;
  }
  .stack-bar { display: flex; height: 22px; border-radius: 4px; overflow: hidden; background: var(--surface-alt); }
  .stack-seg { height: 100%; min-width: 0; }
  .dom-line {
    margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--border-soft);
    display: flex; gap: 20px; flex-wrap: wrap; font-size: 13px; color: var(--ink-soft);
  }
  .dom-line .dom-emotion { color: var(--ink); font-weight: 600; }
  .legend {
    display: flex; flex-wrap: wrap; gap: 14px 20px; margin-bottom: 18px;
    font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-soft);
  }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-swatch { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
  .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; }
  table { border-collapse: collapse; width: 100%; min-width: 720px; background: var(--surface); }
  thead th {
    text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-faint); font-weight: 500;
    padding: 12px 16px; background: var(--surface-alt); border-bottom: 1px solid var(--border); white-space: nowrap;
  }
  tbody td { padding: 13px 16px; border-bottom: 1px solid var(--border-soft); font-size: 13.5px; color: var(--ink-soft); vertical-align: top; }
  tbody tr:last-child td { border-bottom: none; }
  td.emph { color: var(--ink); font-weight: 500; }
  td.mono { font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }
  .agree-yes { color: var(--em-disgusto); font-weight: 600; }
  .agree-no { color: var(--warn); font-weight: 600; }
  .conc-list { display: flex; flex-direction: column; gap: 12px; }
  .conc-row { display: grid; grid-template-columns: 110px 1fr 56px; gap: 14px; align-items: center; }
  .conc-label { font-size: 13.5px; color: var(--ink); font-weight: 500; }
  .conc-track { height: 10px; background: var(--surface-alt); border-radius: 5px; overflow: hidden; border: 1px solid var(--border-soft); }
  .conc-fill { height: 100%; background: var(--accent); border-radius: 5px; }
  .conc-value { font-family: "IBM Plex Mono", monospace; font-size: 13px; font-variant-numeric: tabular-nums; color: var(--ink-soft); text-align: right; }
  .char-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
  .char-pill {
    font-family: "IBM Plex Mono", monospace; font-size: 12px; background: var(--surface-alt);
    border: 1px solid var(--border-soft); border-radius: 20px; padding: 4px 12px; color: var(--ink-soft);
  }
  .char-pill b { color: var(--ink); font-weight: 600; }
  ul.pending { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 10px; }
  ul.pending li {
    display: flex; gap: 12px; padding: 14px 16px; background: var(--surface);
    border: 1px solid var(--border); border-radius: 8px; font-size: 14px; color: var(--ink-soft);
  }
  ul.pending li::before { content: "→"; color: var(--accent); font-weight: 600; flex-shrink: 0; }
  ul.pending b { color: var(--ink); }
  footer {
    margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border);
    font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-faint);
  }
  @media (prefers-reduced-motion: no-preference) { .chapter-panel, .tile { transition: box-shadow 0.15s ease; } }
</style>
"""
