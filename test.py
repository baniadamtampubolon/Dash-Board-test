"""
Dashboard Ketenagakerjaan Nasional — Kementerian Ketenagakerjaan RI
Rewritten from Streamlit to Dash for stability, performance, and richer visuals.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ─── App Init ────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dashboard Ketenagakerjaan | Kemnaker RI"
server = app.server


# ─── Data Loader ─────────────────────────────────────────────────────────────────
_cache = {}

def load_data(path: str) -> pd.DataFrame:
    if path in _cache:
        return _cache[path]
    df = pd.read_excel(path)
    df['thn'] = df['thn'].astype(int)
    df['lvl_wil'] = df['lvl_wil'].astype(str).str.lower()
    df['nm_prov']   = df['nm_prov'].fillna('NASIONAL')
    df['nm_kabkot'] = df['nm_kabkot'].fillna('-')

    # Normalize all column names to lowercase for consistent lookup
    df.columns = [c.strip() for c in df.columns]

    text_cols = {'thn', 'lvl_wil', 'kd_prov', 'nm_prov', 'kd_kabkot', 'nm_kabkot'}
    for col in df.columns:
        if col not in text_cols:
            # Handle both comma and period as decimal separator
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Detect total column — check both uppercase and lowercase variants
    _total_candidates = ['PUK', 'AK', 'PYB', 'PT', 'TPAK', 'TPT', 'EPR',
                         'puk', 'ak', 'pyb', 'pt', 'tpak', 'tpt', 'epr']
    for tc in _total_candidates:
        if tc in df.columns:
            df['total'] = df[tc].astype(float)
            break

    # Also assign jk_lk / jk_pr from lowercase variants if needed
    for _lk in ['jk_lk', 'JK_LK']:
        if _lk in df.columns and _lk != 'jk_lk':
            df['jk_lk'] = df[_lk]
    for _pr in ['jk_pr', 'JK_PR']:
        if _pr in df.columns and _pr != 'jk_pr':
            df['jk_pr'] = df[_pr]

    if 'total' not in df.columns and 'jk_lk' in df.columns and 'jk_pr' in df.columns:
        df['total'] = df['jk_lk'] + df['jk_pr']

    _cache[path] = df
    return df


def filter_data(df, year, level, prov=None, kabkot=None):
    d = df[df['thn'] == year]
    if level == 'nasional':
        return d[d['lvl_wil'] == 'nasional']
    elif level == 'provinsi':
        return d[(d['lvl_wil'] == 'provinsi') & (d['nm_prov'] == prov)]
    elif level == 'kabupaten':
        return d[(d['lvl_wil'].isin(['kabupaten', 'kota'])) & (d['nm_kabkot'] == kabkot)]
    return d


def fmt_compact(val):
    if val >= 1_000_000:
        v = val / 1_000_000
        return f"{v:.1f}M" if v % 1 else f"{int(v)}M"
    elif val >= 1_000:
        v = val / 1_000
        return f"{v:.1f}K" if v % 1 else f"{int(v)}K"
    return f"{val:,.0f}"


# ─── Design Tokens ───────────────────────────────────────────────────────────────
PALETTE = {
    "navy":    "#0A1628",
    "blue":    "#1353A0",
    "sky":     "#2E86DE",
    "teal":    "#0D9E8A",
    "indigo":  "#3D4FB5",
    "gold":    "#F5A623",
    "red":     "#E84545",
    "bg":      "#F4F6FB",
    "surface": "#FFFFFF",
    "border":  "#E2E8F3",
    "muted":   "#7A8BAA",
    "text":    "#0D1B2E",
    "text2":   "#4A5568",
}

SEQ = [PALETTE["navy"], PALETTE["blue"], PALETTE["sky"], PALETTE["teal"],
       "#64B5F6", "#90CAF9", "#BBDEFB"]

CHART = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=PALETTE["text"], size=12),
    margin=dict(l=12, r=12, t=48, b=12),
    hoverlabel=dict(bgcolor=PALETTE["surface"], font_size=12, bordercolor=PALETTE["border"]),
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.28,
        xanchor="center", x=0.5,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11),
    ),
    xaxis=dict(gridcolor="#EEF1F8", showline=False, tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#EEF1F8", showline=False, tickfont=dict(size=11)),
    barcornerradius=6,
)


def apply_chart(fig, height=None, no_legend=False):
    kw = dict(CHART)
    if height:
        kw["height"] = height
    if no_legend:
        kw["showlegend"] = False
    fig.update_layout(**kw)
    return fig


# ─── Static data for filters (always PUK as geo reference) ───────────────────────
try:
    _GEO = load_data("Database/PUK-2018-2025-ver2.xlsx")
    _YEARS = sorted(_GEO['thn'].unique(), reverse=True)
    _PROV_DF = (
        _GEO[_GEO['nm_prov'] != 'NASIONAL'][['kd_prov', 'nm_prov']]
        .drop_duplicates().sort_values('kd_prov')
    )
    _PROV_LIST = _PROV_DF['nm_prov'].tolist()
    DATA_AVAILABLE = True
except Exception:
    _YEARS = list(range(2018, 2026))
    _PROV_LIST = []
    DATA_AVAILABLE = False


# ─── CSS ─────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = f"""
* {{ box-sizing: border-box; }}
body {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: {PALETTE["bg"]};
    color: {PALETTE["text"]};
    margin: 0;
}}

/* ── Sidebar ── */
.sidebar {{
    width: 260px;
    min-height: 100vh;
    background: linear-gradient(160deg, {PALETTE["navy"]} 0%, #102040 100%);
    position: fixed;
    left: 0; top: 0;
    display: flex;
    flex-direction: column;
    padding: 0;
    z-index: 100;
    box-shadow: 4px 0 24px rgba(0,0,0,0.18);
}}
.sidebar-logo {{
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.sidebar-logo h2 {{
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    margin: 10px 0 2px;
    letter-spacing: -0.2px;
    line-height: 1.3;
}}
.sidebar-logo p {{
    color: rgba(255,255,255,0.45);
    font-size: 11px;
    margin: 0;
}}
.sidebar-section {{
    padding: 20px 20px 0;
}}
.sidebar-label {{
    color: rgba(255,255,255,0.35);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.sidebar-nav {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-bottom: 20px;
}}
.nav-btn {{
    background: none;
    border: none;
    color: rgba(255,255,255,0.6);
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    text-align: left;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.18s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.nav-btn:hover {{ background: rgba(255,255,255,0.08); color: #fff; }}
.nav-btn.active {{
    background: rgba(46,134,222,0.25);
    color: #fff;
    font-weight: 600;
    border-left: 3px solid {PALETTE["sky"]};
}}
.sidebar-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 4px 20px 16px;
}}
.filter-label {{
    color: rgba(255,255,255,0.5);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-bottom: 6px;
    display: block;
}}
.Select-control, .Select-menu-outer {{
    border-radius: 8px !important;
}}

/* ── Main content ── */
.main-content {{
    margin-left: 260px;
    padding: 32px 32px 48px;
    min-height: 100vh;
}}

/* ── Page Header ── */
.page-header {{
    margin-bottom: 28px;
}}
.page-title {{
    font-size: 26px;
    font-weight: 800;
    color: {PALETTE["text"]};
    margin: 0 0 4px;
    letter-spacing: -0.5px;
}}
.page-subtitle {{
    font-size: 13.5px;
    color: {PALETTE["muted"]};
    margin: 0;
    font-weight: 400;
}}
.page-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {PALETTE["blue"]}18;
    color: {PALETTE["blue"]};
    border: 1px solid {PALETTE["blue"]}30;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}}

/* ── KPI Cards ── */
.kpi-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 16px;
    padding: 22px 20px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, {PALETTE["blue"]});
    border-radius: 16px 16px 0 0;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(19, 83, 160, 0.1);
}}
.kpi-icon {{
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 14px;
    background: var(--icon-bg, {PALETTE["blue"]}12);
}}
.kpi-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: {PALETTE["muted"]};
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: {PALETTE["text"]};
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -1px;
    line-height: 1;
}}
.kpi-delta {{
    font-size: 12px;
    color: {PALETTE["teal"]};
    margin-top: 6px;
    font-weight: 500;
}}

/* ── Chart Card ── */
.chart-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 16px;
    padding: 4px 4px 0;
    height: 100%;
}}
.chart-card-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: {PALETTE["text"]};
    padding: 18px 20px 0;
    letter-spacing: -0.2px;
}}
.chart-card-sub {{
    font-size: 11.5px;
    color: {PALETTE["muted"]};
    padding: 2px 20px 0;
    font-weight: 400;
}}

/* ── Section ── */
.section-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {PALETTE["muted"]};
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {PALETTE["border"]};
}}

/* ── Dash dropdown/select overrides ── */
.dash-dropdown .Select-control {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: white !important;
}}
.dash-dropdown .Select-value-label {{ color: rgba(255,255,255,0.85) !important; font-size: 12px; }}
.dash-dropdown .Select-placeholder {{ color: rgba(255,255,255,0.4) !important; font-size: 12px; }}
.dash-dropdown .Select-arrow {{ border-top-color: rgba(255,255,255,0.4) !important; }}

.radio-group .form-check-input {{ accent-color: {PALETTE["sky"]}; }}
.radio-group .form-check-label {{
    color: rgba(255,255,255,0.65);
    font-size: 12.5px;
    cursor: pointer;
}}
.radio-group .form-check-input:checked + .form-check-label {{ color: #fff; font-weight: 600; }}

/* Loading overlay */
._dash-loading-callback {{ opacity: 0.6; }}
"""


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
def make_sidebar():
    return html.Div(className="sidebar", children=[
        html.Div(className="sidebar-logo", children=[
            html.Div("⚙️", style={"fontSize": "28px"}),
            html.H2("Dashboard Ketenagakerjaan"),
            html.P("Kementerian Ketenagakerjaan RI"),
        ]),

        html.Div(className="sidebar-section", children=[
            html.Div("Data Absolut", className="sidebar-label"),
            html.Div(className="sidebar-nav", children=[
                html.Button(["📊 ", "Ringkasan Eksekutif"], id="nav-main", className="nav-btn active", n_clicks=0),
                html.Button(["👥 ", "Penduduk Usia Kerja"], id="nav-puk",  className="nav-btn", n_clicks=0),
                html.Button(["💼 ", "Angkatan Kerja"],       id="nav-ak",   className="nav-btn", n_clicks=0),
                html.Button(["❌ ", "Pengangguran Terbuka"], id="nav-pt",   className="nav-btn", n_clicks=0),
                html.Button(["✅ ", "Penduduk Bekerja"],     id="nav-pyb",  className="nav-btn", n_clicks=0),
            ]),
            html.Div("Indikator Rasio", className="sidebar-label", style={"marginTop": "8px"}),
            html.Div(className="sidebar-nav", children=[
                html.Button(["📈 ", "TPAK"], id="nav-tpak", className="nav-btn", n_clicks=0),
                html.Button(["📉 ", "TPT"],  id="nav-tpt",  className="nav-btn", n_clicks=0),
                html.Button(["⚖️ ", "EPR"],  id="nav-epr",  className="nav-btn", n_clicks=0),
            ]),
        ]),

        html.Hr(className="sidebar-divider"),

        html.Div(className="sidebar-section", children=[
            html.Div("Filter Wilayah", className="sidebar-label"),

            html.Span("Tahun", className="filter-label"),
            dcc.Dropdown(
                id="dd-year",
                options=[{"label": str(y), "value": y} for y in _YEARS],
                value=_YEARS[0] if _YEARS else 2024,
                clearable=False,
                className="dash-dropdown",
                style={"marginBottom": "14px"},
            ),

            html.Span("Tingkat Wilayah", className="filter-label"),
            dbc.RadioItems(
                id="radio-level",
                options=[
                    {"label": "Nasional",        "value": "nasional"},
                    {"label": "Provinsi",         "value": "provinsi"},
                    {"label": "Kabupaten/Kota",   "value": "kabupaten"},
                ],
                value="nasional",
                className="radio-group",
                style={"marginBottom": "14px"},
            ),

            html.Div(id="prov-container", style={"display": "none"}, children=[
                html.Span("Provinsi", className="filter-label"),
                dcc.Dropdown(
                    id="dd-prov",
                    options=[{"label": p, "value": p} for p in _PROV_LIST],
                    value=_PROV_LIST[0] if _PROV_LIST else None,
                    clearable=False,
                    className="dash-dropdown",
                    style={"marginBottom": "14px"},
                ),
            ]),

            html.Div(id="kab-container", style={"display": "none"}, children=[
                html.Span("Kabupaten/Kota", className="filter-label"),
                dcc.Dropdown(
                    id="dd-kab",
                    options=[],
                    value=None,
                    clearable=False,
                    className="dash-dropdown",
                    style={"marginBottom": "14px"},
                ),
            ]),
        ]),

        html.Div(style={"flex": 1}),
        html.Div(
            "© 2025 Kemnaker RI",
            style={"padding": "20px 24px", "color": "rgba(255,255,255,0.2)",
                   "fontSize": "11px", "borderTop": "1px solid rgba(255,255,255,0.06)"},
        ),
    ])


# ─── Inject CSS via index_string (html.Style does not exist in Dash) ──────────
app.index_string = (
    '<!DOCTYPE html><html><head>'
    '{%metas%}<title>{%title%}</title>{%favicon%}{%css%}'
    '<style>' + CUSTOM_CSS + '</style>'
    '</head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>'
)

# ─── Layout ──────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="store-active-tab", data="main"),

    make_sidebar(),

    html.Div(className="main-content", children=[
        html.Div(id="page-content"),
    ]),
])


# ─── Callbacks: Navigation ────────────────────────────────────────────────────────
@app.callback(
    Output("store-active-tab", "data"),
    Output("nav-main", "className"),
    Output("nav-puk",  "className"),
    Output("nav-ak",   "className"),
    Output("nav-pt",   "className"),
    Output("nav-pyb",  "className"),
    Output("nav-tpak", "className"),
    Output("nav-tpt",  "className"),
    Output("nav-epr",  "className"),
    Input("nav-main", "n_clicks"),
    Input("nav-puk",  "n_clicks"),
    Input("nav-ak",   "n_clicks"),
    Input("nav-pt",   "n_clicks"),
    Input("nav-pyb",  "n_clicks"),
    Input("nav-tpak", "n_clicks"),
    Input("nav-tpt",  "n_clicks"),
    Input("nav-epr",  "n_clicks"),
    prevent_initial_call=True,
)
def update_active_tab(*_):
    triggered = callback_context.triggered_id
    mapping = {
        "nav-main": "main", "nav-puk": "puk", "nav-ak": "ak",
        "nav-pt": "pt", "nav-pyb": "pyb",
        "nav-tpak": "tpak", "nav-tpt": "tpt", "nav-epr": "epr",
    }
    tab = mapping.get(triggered, "main")
    classes = {k: "nav-btn" for k in mapping}
    classes[triggered] = "nav-btn active"
    return (tab,
            classes["nav-main"], classes["nav-puk"], classes["nav-ak"],
            classes["nav-pt"],   classes["nav-pyb"],
            classes["nav-tpak"], classes["nav-tpt"], classes["nav-epr"])


# ─── Callbacks: Filter visibility ────────────────────────────────────────────────
@app.callback(
    Output("prov-container", "style"),
    Output("kab-container",  "style"),
    Input("radio-level", "value"),
)
def toggle_filters(level):
    prov_style = {"display": "block"} if level in ("provinsi", "kabupaten") else {"display": "none"}
    kab_style  = {"display": "block"} if level == "kabupaten" else {"display": "none"}
    return prov_style, kab_style


@app.callback(
    Output("dd-kab", "options"),
    Output("dd-kab", "value"),
    Input("dd-prov", "value"),
)
def update_kabkot(prov):
    if not prov or not DATA_AVAILABLE:
        return [], None
    kab_df = (
        _GEO[(_GEO['nm_prov'] == prov) & (_GEO['nm_kabkot'] != '-')]
        [['kd_kabkot', 'nm_kabkot']].drop_duplicates().sort_values('kd_kabkot')
    )
    opts = [{"label": k, "value": k} for k in kab_df['nm_kabkot']]
    return opts, (opts[0]["value"] if opts else None)


# ─── Callbacks: Page Content ──────────────────────────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    Input("store-active-tab", "data"),
    Input("dd-year",    "value"),
    Input("radio-level","value"),
    Input("dd-prov",    "value"),
    Input("dd-kab",     "value"),
)
def render_page(tab, year, level, prov, kab):
    if not DATA_AVAILABLE:
        return html.Div([
            html.Div(className="page-header", children=[
                html.Span("⚠️ Mode Demo", className="page-badge"),
                html.H1("Data tidak tersedia", className="page-title"),
                html.P(
                    "Letakkan file Excel di folder Database/ lalu jalankan ulang aplikasi. "
                    "Tampilan di bawah adalah contoh mock data.",
                    className="page-subtitle",
                ),
            ]),
            render_demo_page(),
        ])

    if tab == "main":  return render_main(year, level, prov, kab)
    if tab == "puk":   return render_puk(year, level, prov, kab)
    if tab == "ak":    return render_ak(year, level, prov, kab)
    if tab == "pt":    return render_pt(year, level, prov, kab)
    if tab == "pyb":   return render_pyb(year, level, prov, kab)
    if tab == "tpak":  return render_rasio(year, level, prov, kab, "tpak")
    if tab == "tpt":   return render_rasio(year, level, prov, kab, "tpt")
    if tab == "epr":   return render_rasio(year, level, prov, kab, "epr")
    return html.Div("Pilih menu di sidebar.")


# ─── Helpers ─────────────────────────────────────────────────────────────────────
# NOTE: loc() is defined after render_main (line ~781) — alias here for pages that call early
def loc_name(level, prov, kab):
    if level == "provinsi":   return prov or "—"
    if level == "kabupaten":  return kab  or "—"
    return "Indonesia"

loc = loc_name  # single canonical helper, both names work


def kpi_card(icon, label, value, accent=None, icon_bg=None):
    style = {}
    if accent: style["--accent"] = accent
    if icon_bg: style["--icon-bg"] = icon_bg
    return html.Div(className="kpi-card", style=style, children=[
        html.Div(icon, className="kpi-icon"),
        html.Div(label, className="kpi-label"),
        html.Div(value, className="kpi-value"),
    ])


def chart_card(title, sub, figure, height=None):
    graph_style = {}
    if height: graph_style["height"] = height
    return html.Div(className="chart-card", children=[
        html.Div(title, className="chart-card-title"),
        html.Div(sub,   className="chart-card-sub"),
        dcc.Graph(figure=figure, config={"displayModeBar": False},
                  style={"borderRadius": "0 0 16px 16px", **graph_style}),
    ])


def section(label):
    return html.Div(label, className="section-label")


def trend_filter(df, level, prov, kab):
    if level == "nasional":   return df[df['lvl_wil'] == 'nasional']
    if level == "provinsi":   return df[(df['lvl_wil'] == 'provinsi') & (df['nm_prov'] == prov)]
    if level == "kabupaten":  return df[(df['lvl_wil'].isin(['kabupaten','kota'])) & (df['nm_kabkot'] == kab)]
    return df


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: RINGKASAN EKSEKUTIF
# ══════════════════════════════════════════════════════════════════════════════════
def render_main(year, level, prov, kab):
    df_puk = load_data("Database/PUK-2018-2025-ver2.xlsx")
    df_ak  = load_data("Database/AK-2018-2025-ver2.xlsx")
    df_pt  = load_data("Database/PT-2018-2025-ver2.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025-ver3.xlsx")

    data_puk = filter_data(df_puk, year, level, prov, kab)
    data_ak  = filter_data(df_ak,  year, level, prov, kab)
    data_pt  = filter_data(df_pt,  year, level, prov, kab)
    data_pyb = filter_data(df_pyb, year, level, prov, kab)

    v_puk = int(data_puk['total'].sum())
    v_ak  = int(data_ak['total'].sum())
    v_pyb = int(data_pyb['total'].sum())
    v_pt  = int(data_pt['total'].sum())
    tpr   = round(v_pt / v_ak * 100, 2) if v_ak > 0 else 0
    tpak  = round(v_ak / v_puk * 100, 2) if v_puk > 0 else 0

    name = loc_name(level, prov, kab)

    # ── Funnel chart (Sankey-style as treemap) ───────────────────────────────────
    bak = max(0, v_puk - v_ak)
    funnel_fig = go.Figure(go.Funnel(
        y=["Penduduk Usia Kerja", "Angkatan Kerja", "Penduduk Bekerja"],
        x=[v_puk, v_ak, v_pyb],
        textinfo="value+percent initial",
        texttemplate="%{value:,.0f}<br>(%{percentInitial:.1%})",
        marker=dict(color=[PALETTE["navy"], PALETTE["blue"], PALETTE["teal"]]),
        connector=dict(line=dict(width=1, color=PALETTE["border"])),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} jiwa<extra></extra>",
    ))
    apply_chart(funnel_fig, height=320, no_legend=True)
    funnel_fig.update_layout(title=None, margin=dict(l=80, r=20, t=20, b=20))

    # ── Donut: komposisi AK ──────────────────────────────────────────────────────
    donut_fig = px.pie(
        pd.DataFrame({"k": ["Bekerja", "Menganggur"], "v": [v_pyb, v_pt]}),
        values="v", names="k", hole=0.65,
        color_discrete_sequence=[PALETTE["teal"], PALETTE["red"]],
    )
    donut_fig.update_traces(
        textposition="inside", textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    )
    apply_chart(donut_fig, height=300, no_legend=False)
    donut_fig.add_annotation(
        text=f"TPT<br><b>{tpr}%</b>", x=0.5, y=0.5,
        font=dict(size=14, color=PALETTE["text"]), showarrow=False,
    )

    # ── Bar: Top sektor ──────────────────────────────────────────────────────────
    lapus_map = {
        'lapus_A': 'Pertanian', 'lapus_B': 'Pertambangan', 'lapus_C': 'Industri',
        'lapus_D': 'Listrik', 'lapus_F': 'Konstruksi', 'lapus_G': 'Perdagangan',
        'lapus_H': 'Transportasi', 'lapus_I': 'Akomodasi', 'lapus_J': 'IT/Kominfo',
        'lapus_P': 'Pendidikan', 'lapus_Q': 'Kesehatan', 'lapus_RSTU': 'Jasa Lainnya',
    }
    lv = [(lapus_map[c], int(data_pyb[c].sum())) for c in lapus_map if c in data_pyb.columns]
    ldf = pd.DataFrame(lv, columns=['Sektor', 'Jumlah']).sort_values('Jumlah').tail(8)
    bar_sektor = px.bar(
        ldf, x='Jumlah', y='Sektor', orientation='h',
        color='Jumlah', color_continuous_scale=["#AED6F1", PALETTE["blue"], PALETTE["navy"]],
        text=[fmt_compact(v) for v in ldf['Jumlah']],
    )
    bar_sektor.update_traces(
        textposition='outside', textfont_size=10,
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    )
    bar_sektor.update_coloraxes(showscale=False)
    apply_chart(bar_sektor, height=360)
    bar_sektor.update_layout(xaxis_title="", yaxis_title="")

    # ── Multi-line trend ──────────────────────────────────────────────────────────
    t_puk = trend_filter(df_puk, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_ak  = trend_filter(df_ak,  level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_pyb = trend_filter(df_pyb, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_pt  = trend_filter(df_pt,  level, prov, kab).groupby('thn')['total'].sum().reset_index()

    trend_fig = go.Figure()
    for df_t, name_t, color, dash in [
        (t_puk, "PUK", "#AED6F1", "dot"),
        (t_ak,  "AK",  PALETTE["sky"], "dot"),
        (t_pyb, "Bekerja", PALETTE["blue"], "solid"),
        (t_pt,  "Pengangguran", PALETTE["red"], "solid"),
    ]:
        trend_fig.add_trace(go.Scatter(
            x=df_t['thn'], y=df_t['total'], name=name_t, mode='lines+markers',
            line=dict(color=color, width=2.5 if dash=="solid" else 1.8, dash=dash, shape='spline'),
            marker=dict(size=6, color=color),
            fill='tozeroy' if name_t == "Bekerja" else None,
            fillcolor='rgba(19,83,160,0.06)' if name_t == "Bekerja" else None,
            hovertemplate=f"<b>{name_t}</b>: %{{y:,.0f}}<extra></extra>",
        ))
    apply_chart(trend_fig, height=380)
    trend_fig.update_layout(
        hovermode='x unified',
        xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
    )

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  📅 {year}", className="page-badge"),
            html.H1("Ringkasan Eksekutif Ketenagakerjaan", className="page-title"),
            html.P("Gambaran menyeluruh kondisi ketenagakerjaan nasional", className="page-subtitle"),
        ]),

        dbc.Row([
            dbc.Col(kpi_card("👥", "Penduduk Usia Kerja", f"{fmt_compact(v_puk)}",
                             PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=3),
            dbc.Col(kpi_card("💼", "Angkatan Kerja", f"{fmt_compact(v_ak)}  ({tpak:.1f}%)",
                             PALETTE["blue"], f"{PALETTE['blue']}14"), md=3),
            dbc.Col(kpi_card("✅", "Penduduk Bekerja", fmt_compact(v_pyb),
                             PALETTE["teal"], f"{PALETTE['teal']}14"), md=3),
            dbc.Col(kpi_card("❌", "Pengangguran Terbuka", f"{fmt_compact(v_pt)}  (TPT {tpr}%)",
                             PALETTE["red"], f"{PALETTE['red']}14"), md=3),
        ], className="g-3 mb-2"),

        section("Struktur Ketenagakerjaan"),
        dbc.Row([
            dbc.Col(chart_card("Alur Partisipasi Tenaga Kerja",
                               "Dari total penduduk usia kerja hingga yang bekerja",
                               funnel_fig), md=8),
            dbc.Col(chart_card("Komposisi Angkatan Kerja",
                               f"Tingkat Pengangguran Terbuka (TPT): {tpr}%",
                               donut_fig), md=4),
        ], className="g-3 mb-2"),

        section("Penyerapan & Distribusi"),
        dbc.Row([
            dbc.Col(chart_card("Top Sektor Penyerap Tenaga Kerja",
                               "Berdasarkan jumlah penduduk bekerja",
                               bar_sektor), md=6),
            dbc.Col(chart_card(f"Tren Ketenagakerjaan — {loc(level,prov,kab)}",
                               "Data 2018–2025",
                               trend_fig), md=6),
        ], className="g-3 mb-2"),

        html.Div(
            f"Dashboard Ketenagakerjaan Nasional 2018–2025  ·  Kementerian Ketenagakerjaan RI",
            style={"textAlign": "center", "color": PALETTE["muted"],
                   "fontSize": "12px", "marginTop": "40px"},
        ),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: PUK
# ══════════════════════════════════════════════════════════════════════════════════
def render_puk(year, level, prov, kab):
    df_puk = load_data("Database/PUK-2018-2025-ver2.xlsx")
    df_pt  = load_data("Database/PT-2018-2025-ver2.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025-ver3.xlsx")

    data = filter_data(df_puk, year, level, prov, kab)
    data_pt  = filter_data(df_pt,  year, level, prov, kab)
    data_pyb = filter_data(df_pyb, year, level, prov, kab)

    total = int(data['total'].sum())
    working    = int(data_pyb['total'].sum())
    unemployed = int(data_pt['total'].sum())
    bak        = max(0, total - working - unemployed)

    # Age pyramid
    age_m = {c: f for c, f in zip(
        ['ku_1519','ku_2024','ku_2529','ku_3034','ku_3539','ku_4044',
         'ku_4549','ku_5054','ku_5559','ku_6064','ku_65+'],
        ['15–19','20–24','25–29','30–34','35–39','40–44','45–49','50–54','55–59','60–64','65+']
    )}
    lk_vals = [-int(data.get(c, pd.Series([0])).sum()) for c in age_m]
    pr_vals =  [int(data.get(c, pd.Series([0])).sum()) for c in age_m]
    labels  = list(age_m.values())

    pyramid = go.Figure()
    pyramid.add_trace(go.Bar(
        y=labels, x=lk_vals, name="Laki-laki", orientation='h',
        marker_color=PALETTE["blue"],
        hovertemplate="<b>%{y}</b><br>Laki-laki: %{customdata:,.0f}<extra></extra>",
        customdata=[-v for v in lk_vals],
    ))
    pyramid.add_trace(go.Bar(
        y=labels, x=pr_vals, name="Perempuan", orientation='h',
        marker_color="#F48FB1",
        hovertemplate="<b>%{y}</b><br>Perempuan: %{x:,.0f}<extra></extra>",
    ))
    apply_chart(pyramid, height=400)
    pyramid.update_layout(
        barmode='relative', bargap=0.1,
        xaxis=dict(tickformat=',d', title="Jumlah Jiwa",
                   tickvals=[-5000000,-2500000,0,2500000,5000000],
                   ticktext=["5M","2.5M","0","2.5M","5M"]),
        yaxis_title="",
    )

    # Status aktivitas donut
    act_df = pd.DataFrame({
        'Aktivitas': ['Bekerja', 'Pengangguran', 'Bukan Angkatan Kerja'],
        'Jumlah':    [working, unemployed, bak],
    })
    act_fig = px.pie(act_df, values='Jumlah', names='Aktivitas', hole=0.6,
                     color_discrete_sequence=[PALETTE["teal"], PALETTE["red"], PALETTE["muted"]])
    act_fig.update_traces(textposition='inside', textinfo='percent+label')
    apply_chart(act_fig, height=340, no_legend=False)

    # Education treemap
    edu_map = {'pd_sd':'SD','pd_smp':'SMP','pd_smau':'SMA/MA','pd_smak':'SMK','pd_dipl':'Diploma','pd_univ':'Universitas'}
    edu_vals = [int(data[c].sum()) if c in data.columns else 0 for c in edu_map]
    edu_df = pd.DataFrame({'Pendidikan': list(edu_map.values()), 'Jumlah': edu_vals})
    treemap = px.treemap(edu_df, path=['Pendidikan'], values='Jumlah',
                         color='Jumlah', color_continuous_scale=["#E3EDF9", PALETTE["blue"]])
    treemap.update_traces(texttemplate="<b>%{label}</b><br>%{value:,.0f}", hovertemplate="%{label}: %{value:,.0f}<extra></extra>")
    treemap.update_coloraxes(showscale=False)
    apply_chart(treemap, height=340)

    # Trend
    t = trend_filter(df_puk, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    tp = trend_filter(df_pt,  level, prov, kab).groupby('thn')['total'].sum().reset_index()
    ty = trend_filter(df_pyb, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend = go.Figure()
    for dt, nm, cl in [(t, "PUK", "#AED6F1"), (ty, "Bekerja", PALETTE["teal"]), (tp, "Pengangguran", PALETTE["red"])]:
        trend.add_trace(go.Scatter(
            x=dt['thn'], y=dt['total'], name=nm, mode='lines+markers',
            line=dict(color=cl, width=2.5, shape='spline'), marker=dict(size=6),
            hovertemplate=f"<b>{nm}</b>: %{{y:,.0f}}<extra></extra>",
        ))
    apply_chart(trend, height=320)
    trend.update_layout(hovermode='x unified', xaxis_title="Tahun")

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Penduduk Usia Kerja (PUK)", className="page-title"),
            html.P("Distribusi demografis penduduk usia 15 tahun ke atas", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("👥", "Total PUK",            fmt_compact(total),    PALETTE["blue"],   f"{PALETTE['blue']}14"),  md=3),
            dbc.Col(kpi_card("✅", "Penduduk Bekerja",     fmt_compact(working),  PALETTE["teal"],   f"{PALETTE['teal']}14"),  md=3),
            dbc.Col(kpi_card("❌", "Pengangguran Terbuka", fmt_compact(unemployed),PALETTE["red"],   f"{PALETTE['red']}14"),   md=3),
            dbc.Col(kpi_card("🏠", "Bukan Angkatan Kerja", fmt_compact(bak),      PALETTE["muted"],  "#7A8BAA14"),              md=3),
        ], className="g-3 mb-2"),
        section("Profil Demografis"),
        dbc.Row([
            dbc.Col(chart_card("Piramida Usia & Gender", "Distribusi kelompok usia berdasarkan jenis kelamin", pyramid), md=8),
            dbc.Col(chart_card("Status Aktivitas", "Komposisi kegiatan penduduk usia kerja", act_fig), md=4),
        ], className="g-3 mb-2"),
        section("Pendidikan & Tren"),
        dbc.Row([
            dbc.Col(chart_card("Distribusi Tingkat Pendidikan", "Proporsi berdasarkan jenjang pendidikan terakhir", treemap), md=6),
            dbc.Col(chart_card("Tren PUK 2018–2025", f"Perkembangan tahunan — {loc(level,prov,kab)}", trend), md=6),
        ], className="g-3"),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: AK
# ══════════════════════════════════════════════════════════════════════════════════
def render_ak(year, level, prov, kab):
    df = load_data("Database/AK-2018-2025-ver2.xlsx")
    data = filter_data(df, year, level, prov, kab)
    total = int(data['total'].sum())

    lk = int(data.get('jk_lk', pd.Series([0])).sum())
    pr = int(data.get('jk_pr', pd.Series([0])).sum())

    # Age bar
    age_m = {'ku_1519':'15–19','ku_2024':'20–24','ku_2529':'25–29','ku_3034':'30–34',
              'ku_3539':'35–39','ku_4044':'40–44','ku_4549':'45–49','ku_5054':'50–54',
              'ku_5559':'55–59','ku_6064':'60–64','ku_65+':'65+'}
    lk_age = [int(data[c].sum()) if c in data.columns else 0 for c in age_m]
    pr_age = [int(data.get(c.replace('ku_', 'ku_'), pd.Series([0])).sum()) for c in age_m]
    
    age_fig = go.Figure()
    age_fig.add_trace(go.Bar(x=list(age_m.values()), y=lk_age, name="Laki-laki",
                             marker_color=PALETTE["blue"]))
    age_fig.add_trace(go.Bar(x=list(age_m.values()), y=pr_age, name="Perempuan",
                             marker_color="#F48FB1"))
    apply_chart(age_fig, height=340)
    age_fig.update_layout(barmode='group', xaxis_title="", yaxis_title="Jumlah")

    # Gender gauge-like bar
    gen_fig = go.Figure(go.Bar(
        x=["Laki-laki", "Perempuan"], y=[lk, pr],
        marker_color=[PALETTE["blue"], "#F48FB1"],
        text=[f"{fmt_compact(lk)} ({lk/(lk+pr)*100:.1f}%)",
              f"{fmt_compact(pr)} ({pr/(lk+pr)*100:.1f}%)"] if (lk+pr)>0 else ["",""],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    ))
    apply_chart(gen_fig, height=280, no_legend=True)
    gen_fig.update_layout(xaxis_title="", yaxis_title="")

    # Trend
    t = trend_filter(df, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t['total'], mode='lines+markers',
        line=dict(color=PALETTE["blue"], width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(19,83,160,0.08)',
        marker=dict(size=7, color=PALETTE["blue"]),
        hovertemplate="Tahun %{x}: %{y:,.0f}<extra></extra>",
    ))
    apply_chart(trend_fig, height=300)
    trend_fig.update_layout(xaxis_title="Tahun", yaxis_title="Jumlah Jiwa")

    # Education
    edu_map = {'pd_sd':'SD','pd_smp':'SMP','pd_smau':'SMA','pd_smak':'SMK','pd_dipl':'Diploma','pd_univ':'Universitas'}
    edu_vals = [int(data[c].sum()) if c in data.columns else 0 for c in edu_map]
    edu_fig = px.bar(
        pd.DataFrame({'Pendidikan': list(edu_map.values()), 'Jumlah': edu_vals}),
        x='Pendidikan', y='Jumlah', color='Jumlah',
        color_continuous_scale=["#DBEAFE", PALETTE["blue"]],
        text=[fmt_compact(v) for v in edu_vals],
    )
    edu_fig.update_traces(textposition='outside')
    edu_fig.update_coloraxes(showscale=False)
    apply_chart(edu_fig, height=300)
    edu_fig.update_layout(xaxis_title="", yaxis_title="")

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Angkatan Kerja (AK)", className="page-title"),
            html.P("Penduduk yang bekerja atau sedang mencari pekerjaan", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("💼", "Total Angkatan Kerja", fmt_compact(total), PALETTE["blue"], f"{PALETTE['blue']}14"), md=4),
            dbc.Col(kpi_card("👨", "Laki-laki", f"{fmt_compact(lk)} ({lk/(lk+pr)*100:.1f}%)" if (lk+pr)>0 else "—", PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=4),
            dbc.Col(kpi_card("👩", "Perempuan",  f"{fmt_compact(pr)} ({pr/(lk+pr)*100:.1f}%)" if (lk+pr)>0 else "—", "#E91E8C", "#E91E8C14"), md=4),
        ], className="g-3 mb-2"),
        section("Profil Angkatan Kerja"),
        dbc.Row([
            dbc.Col(chart_card("Distribusi Usia per Gender", "", age_fig), md=7),
            dbc.Col(chart_card("Perbandingan Gender", "", gen_fig), md=5),
        ], className="g-3 mb-2"),
        section("Pendidikan & Tren"),
        dbc.Row([
            dbc.Col(chart_card("Tingkat Pendidikan", "", edu_fig), md=6),
            dbc.Col(chart_card("Tren Angkatan Kerja 2018–2025", "", trend_fig), md=6),
        ], className="g-3"),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: PT
# ══════════════════════════════════════════════════════════════════════════════════
def render_pt(year, level, prov, kab):
    df = load_data("Database/PT-2018-2025-ver2.xlsx")
    df_ak = load_data("Database/AK-2018-2025-ver2.xlsx")
    data = filter_data(df, year, level, prov, kab)
    data_ak = filter_data(df_ak, year, level, prov, kab)

    total  = int(data['total'].sum())
    v_ak   = int(data_ak['total'].sum())
    tpr    = round(total / v_ak * 100, 2) if v_ak > 0 else 0

    pt_map  = {'kat_mp':'Mencari Pekerjaan','kat_mu':'Mempersiapkan Usaha','kat_pa':'Putus Asa','kat_bmb':'Diterima Belum Bekerja'}
    pt_vals = [int(data[c].sum()) if c in data.columns else 0 for c in pt_map]
    ptdf    = pd.DataFrame({'Kategori': list(pt_map.values()), 'Jumlah': pt_vals})

    # Horizontal diverging bar for categories
    cat_fig = px.bar(
        ptdf.sort_values('Jumlah'), x='Jumlah', y='Kategori', orientation='h',
        color='Jumlah',
        color_continuous_scale=["#FEEBC8", PALETTE["gold"], PALETTE["red"]],
        text=[fmt_compact(v) for v in ptdf.sort_values('Jumlah')['Jumlah']],
    )
    cat_fig.update_traces(textposition='outside')
    cat_fig.update_coloraxes(showscale=False)
    apply_chart(cat_fig, height=300)
    cat_fig.update_layout(xaxis_title="", yaxis_title="")

    # Sunburst: cat + gender breakdown
    lk_vals = [int(data.get('jk_lk', pd.Series([0])).sum()) // max(1, len(pt_map))] * len(pt_map)
    pr_vals = [int(data.get('jk_pr', pd.Series([0])).sum()) // max(1, len(pt_map))] * len(pt_map)
    sun_labels = ["Pengangguran"] + list(pt_map.values()) * 1
    sun_parents = [""] + ["Pengangguran"] * len(pt_map)
    sun_vals   = [total] + pt_vals
    sun_fig = go.Figure(go.Sunburst(
        labels=sun_labels, parents=sun_parents, values=sun_vals,
        branchvalues='total',
        marker=dict(colors=[PALETTE["red"], PALETTE["navy"], PALETTE["blue"],
                             PALETTE["sky"], PALETTE["gold"]]),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    ))
    apply_chart(sun_fig, height=340, no_legend=True)

    # Trend multi-line
    ts = trend_filter(df, level, prov, kab)
    cols_pt = [c for c in ['total','kat_mp','kat_mu','kat_pa','kat_bmb'] if c in ts.columns]
    ts_g = ts.groupby('thn')[cols_pt].sum().reset_index()
    trend_fig = go.Figure()
    colors_pt = [PALETTE["red"], PALETTE["navy"], PALETTE["blue"], PALETTE["sky"], PALETTE["gold"]]
    labels_pt = ["Total PT", "Mencari Pekerjaan", "Mempersiapkan Usaha", "Putus Asa", "Diterima Belum Bekerja"]
    for col, clr, lbl in zip(cols_pt, colors_pt, labels_pt):
        trend_fig.add_trace(go.Scatter(
            x=ts_g['thn'], y=ts_g[col], name=lbl, mode='lines+markers',
            line=dict(color=clr, width=2.5 if col=='total' else 1.8, shape='spline'),
            marker=dict(size=5),
        ))
    apply_chart(trend_fig, height=360)
    trend_fig.update_layout(hovermode='x unified', xaxis_title="Tahun")

    # Age + gender
    age_m = {'ku_1519':'15–19','ku_2024':'20–24','ku_2529':'25–29','ku_3034':'30–34',
              'ku_3539':'35–39','ku_4044':'40–44','ku_4549':'45–49','ku_5054':'50–54',
              'ku_5559':'55–59','ku_6064':'60–64'}
    age_vals = [int(data[c].sum()) if c in data.columns else 0 for c in age_m]
    age_fig = px.area(
        pd.DataFrame({'Usia': list(age_m.values()), 'Jumlah': age_vals}),
        x='Usia', y='Jumlah', markers=True, color_discrete_sequence=[PALETTE["red"]],
    )
    age_fig.update_traces(
        fillcolor='rgba(232,69,69,0.1)', line_width=2.5,
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    )
    apply_chart(age_fig, height=300)
    age_fig.update_layout(xaxis_title="", yaxis_title="")

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Pengangguran Terbuka (PT)", className="page-title"),
            html.P("Analisis kondisi dan karakteristik pengangguran", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("❌", "Total Pengangguran",    fmt_compact(total), PALETTE["red"],  f"{PALETTE['red']}14"),   md=4),
            dbc.Col(kpi_card("📊", "TPT (Tingkat Pengangguran Terbuka)", f"{tpr}%",              PALETTE["gold"], f"{PALETTE['gold']}14"), md=4),
            dbc.Col(kpi_card("🔍", "Mencari Pekerjaan",
                             fmt_compact(pt_vals[0]) if pt_vals else "—",
                             PALETTE["navy"], f"{PALETTE['navy']}14"), md=4),
        ], className="g-3 mb-2"),
        section("Distribusi Pengangguran"),
        dbc.Row([
            dbc.Col(chart_card("Kategori Pengangguran", "", cat_fig), md=7),
            dbc.Col(chart_card("Proporsi Kategori", "", sun_fig), md=5),
        ], className="g-3 mb-2"),
        section("Usia & Tren"),
        dbc.Row([
            dbc.Col(chart_card("Profil Usia Pengangguran", "", age_fig), md=5),
            dbc.Col(chart_card("Tren Pengangguran 2018–2025", "", trend_fig), md=7),
        ], className="g-3"),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: PYB
# ══════════════════════════════════════════════════════════════════════════════════
def render_pyb(year, level, prov, kab):
    df = load_data("Database/PYB-2018-2025-ver3.xlsx")
    data = filter_data(df, year, level, prov, kab)
    total = int(data['total'].sum())

    # Sektor treemap
    lapus_map = {
        'lapus_A':'Pertanian','lapus_B':'Pertambangan','lapus_C':'Industri Pengolahan',
        'lapus_D':'Listrik & Gas','lapus_E':'Air & Limbah','lapus_F':'Konstruksi',
        'lapus_G':'Perdagangan','lapus_H':'Transportasi','lapus_I':'Akomodasi',
        'lapus_J':'IT/Kominfo','lapus_K':'Keuangan','lapus_L':'Real Estat',
        'lapus_MN':'Jasa Profesional','lapus_O':'Administrasi','lapus_P':'Pendidikan',
        'lapus_Q':'Kesehatan','lapus_RSTU':'Jasa Lainnya',
    }
    lv = [int(data[c].sum()) if c in data.columns else 0 for c in lapus_map]
    ldf = pd.DataFrame({'Sektor': list(lapus_map.values()), 'Jumlah': lv})
    sektor_tree = px.treemap(ldf, path=['Sektor'], values='Jumlah',
                              color='Jumlah', color_continuous_scale=["#DBEAFE", PALETTE["blue"]])
    sektor_tree.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f}",
        hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>",
    )
    sektor_tree.update_coloraxes(showscale=False)
    apply_chart(sektor_tree, height=400)

    # Status pekerjaan
    sta_map = {
        'sta_1':'Berusaha Sendiri','sta_2':'Buruh Tdk Tetap','sta_3':'Buruh Tetap',
        'sta_4':'Karyawan','sta_5':'Bebas (Tani)','sta_6':'Bebas (Non-Tani)','sta_7':'Keluarga',
    }
    sv = [int(data[c].sum()) if c in data.columns else 0 for c in sta_map]
    sdf = pd.DataFrame({'Status': list(sta_map.values()), 'Jumlah': sv})
    sta_fig = px.pie(sdf, values='Jumlah', names='Status', hole=0.55,
                     color_discrete_sequence=SEQ)
    sta_fig.update_traces(textposition='inside', textinfo='percent+label',
                           hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>")
    apply_chart(sta_fig, height=360)

    # Jabatan horizontal
    jab_map = {
        'jab_1':'Manajer','jab_2':'Profesional','jab_3':'Teknisi',
        'jab_4':'Tata Usaha','jab_5':'Jasa & Penjualan',
        'jab_6':'Pekerja Tani','jab_7':'Pengolah','jab_8':'Operator',
        'jab_9':'Kebersihan/Kasar','jab_0':'TNI/POLRI',
    }
    jv = [int(data[c].sum()) if c in data.columns else 0 for c in jab_map]
    jdf = pd.DataFrame({'Jabatan': list(jab_map.values()), 'Jumlah': jv}).sort_values('Jumlah')
    jab_fig = px.bar(jdf, x='Jumlah', y='Jabatan', orientation='h',
                     color='Jumlah', color_continuous_scale=["#DBEAFE", PALETTE["indigo"]],
                     text=[fmt_compact(v) for v in jdf['Jumlah']])
    jab_fig.update_traces(textposition='outside')
    jab_fig.update_coloraxes(showscale=False)
    apply_chart(jab_fig, height=380)
    jab_fig.update_layout(xaxis_title="", yaxis_title="")

    # Jam kerja
    jam_map = {'jam_114':'1–14 jam','jam_1534':'15–34 jam','jam_3540':'35–40 jam',
               'jam_4148':'41–48 jam','jam_>48':'>48 jam'}
    jmv = [int(data[c].sum()) if c in data.columns else 0 for c in jam_map]
    jam_fig = go.Figure(go.Bar(
        x=list(jam_map.values()), y=jmv,
        marker_color=[PALETTE["sky"], PALETTE["teal"], PALETTE["blue"],
                      PALETTE["indigo"], PALETTE["navy"]],
        text=[fmt_compact(v) for v in jmv], textposition='outside',
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    ))
    apply_chart(jam_fig, height=300, no_legend=True)
    jam_fig.update_layout(xaxis_title="", yaxis_title="")

    # Trend
    t = trend_filter(df, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t['total'], mode='lines+markers',
        line=dict(color=PALETTE["teal"], width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(13,158,138,0.08)',
        marker=dict(size=7, color=PALETTE["teal"]),
        hovertemplate="Tahun %{x}: %{y:,.0f}<extra></extra>",
    ))
    apply_chart(trend_fig, height=300)
    trend_fig.update_layout(xaxis_title="Tahun", yaxis_title="Jumlah Jiwa")

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Penduduk yang Bekerja (PYB)", className="page-title"),
            html.P("Analisis mendalam profil pekerjaan, sektor, dan jabatan", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("✅", "Total Penduduk Bekerja", fmt_compact(total),
                             PALETTE["teal"], f"{PALETTE['teal']}14"), md=4),
            dbc.Col(kpi_card("🏭", "Sektor Terbesar",
                             ldf.sort_values('Jumlah').iloc[-1]['Sektor'] if not ldf.empty else "—",
                             PALETTE["blue"], f"{PALETTE['blue']}14"), md=4),
            dbc.Col(kpi_card("⏱️", "Pekerja >48 jam/minggu",
                             fmt_compact(jmv[-1]) if jmv else "—",
                             PALETTE["gold"], f"{PALETTE['gold']}14"), md=4),
        ], className="g-3 mb-2"),
        section("Distribusi Sektor & Status"),
        dbc.Row([
            dbc.Col(chart_card("Lapangan Usaha (Treemap)", "Proporsi berdasarkan sektor pekerjaan", sektor_tree), md=8),
            dbc.Col(chart_card("Status Pekerjaan", "", sta_fig), md=4),
        ], className="g-3 mb-2"),
        section("Jabatan & Jam Kerja"),
        dbc.Row([
            dbc.Col(chart_card("Distribusi Jabatan / Jenis Pekerjaan", "", jab_fig), md=6),
            dbc.Col(html.Div(className="chart-card", children=[
                html.Div("Jam Kerja per Minggu", className="chart-card-title"),
                html.Div("Distribusi durasi kerja per minggu", className="chart-card-sub"),
                dcc.Graph(figure=jam_fig, config={"displayModeBar": False}),
                html.Hr(style={"margin": "0 20px", "borderColor": PALETTE["border"]}),
                html.Div("Tren 2018–2025", className="chart-card-title"),
                dcc.Graph(figure=trend_fig, config={"displayModeBar": False}),
            ]), md=6),
        ], className="g-3"),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: RASIO (TPAK / TPT / EPR) — satu fungsi generik untuk ketiga indikator
# ══════════════════════════════════════════════════════════════════════════════════

_RASIO_CONFIG = {
    "tpak": {
        "file":     "Database/TPAK-2018-2025-ver2.xlsx",
        "title":    "Tingkat Partisipasi Angkatan Kerja (TPAK)",
        "subtitle": "Persentase angkatan kerja terhadap penduduk usia kerja (AK / PUK)",
        "unit":     "TPAK",
        "kpi_icon": "📈",
        "color":    "#1353A0",       # blue
        "fill":     "rgba(19,83,160,0.08)",
        "gradient": ["#DBEAFE", "#1353A0"],
        "icon_bg":  "#1353A014",
        "lk_color": "#3D4FB5",      # indigo
        "pr_color": "#E91E8C",
        "bar_label":"TPAK (%)",
    },
    "tpt": {
        "file":     "Database/TPT-2018-2025-ver2.xlsx",
        "title":    "Tingkat Pengangguran Terbuka (TPT)",
        "subtitle": "Persentase pengangguran terhadap total angkatan kerja (PT / AK)",
        "unit":     "TPT",
        "kpi_icon": "📉",
        "color":    "#E84545",       # red
        "fill":     "rgba(232,69,69,0.08)",
        "gradient": ["#FEEBC8", "#E84545"],
        "icon_bg":  "#E8454514",
        "lk_color": "#3D4FB5",
        "pr_color": "#E91E8C",
        "bar_label":"TPT (%)",
    },
    "epr": {
        "file":     "Database/EPR-2018-2025-ver2.xlsx",
        "title":    "Employment to Population Ratio (EPR)",
        "subtitle": "Persentase penduduk bekerja terhadap penduduk usia kerja (PYB / PUK)",
        "unit":     "EPR",
        "kpi_icon": "⚖️",
        "color":    "#0D9E8A",       # teal
        "fill":     "rgba(13,158,138,0.08)",
        "gradient": ["#E6F4F1", "#0D9E8A"],
        "icon_bg":  "#0D9E8A14",
        "lk_color": "#3D4FB5",
        "pr_color": "#E91E8C",
        "bar_label":"EPR (%)",
    },
}


def render_rasio(year, level, prov, kab, kind: str):
    cfg  = _RASIO_CONFIG[kind]
    df   = load_data(cfg["file"])
    data = filter_data(df, year, level, prov, kab)

    # ── KPI values ───────────────────────────────────────────────────────────────
    # Rasio = persentase; dataset berisi 1 baris per wilayah per tahun.
    # Gunakan .mean() agar aman jika lebih dari 1 baris tersisa setelah filter.
    v_val  = round(float(data['total'].mean()),  2) if not data.empty else 0.0
    lk_val = round(float(data['jk_lk'].mean()), 2) if (not data.empty and 'jk_lk' in data.columns) else 0.0
    pr_val = round(float(data['jk_pr'].mean()), 2) if (not data.empty and 'jk_pr' in data.columns) else 0.0

    # ── Trend line ───────────────────────────────────────────────────────────────
    # Untuk data rasio, gunakan mean() per tahun (bukan sum)
    t = trend_filter(df, level, prov, kab).groupby('thn')['total'].mean().reset_index()
    y_min = max(0.0, float(t['total'].min()) * 0.92) if not t.empty else 0
    y_max = min(100.0, float(t['total'].max()) * 1.06) if not t.empty else 100

    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t['total'],
        mode='lines+markers+text',
        text=[f"{v:.1f}%" for v in t['total']],
        textposition='top center',
        textfont=dict(size=9, color=cfg["color"]),
        line=dict(color=cfg["color"], width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=cfg["fill"],
        marker=dict(size=7, color=cfg["color"], line=dict(color="#fff", width=1.5)),
        hovertemplate=f"Tahun %{{x}}<br>{cfg['unit']}: %{{y:.2f}}%<extra></extra>",
    ))
    apply_chart(trend_fig, height=300)
    trend_fig.update_layout(
        xaxis_title="Tahun",
        yaxis=dict(
            title="Persentase (%)",
            ticksuffix="%",
            gridcolor="#EEF1F8",
            range=[y_min, y_max],
        ),
        showlegend=False,
    )

    # ── Gender comparison bar ─────────────────────────────────────────────────────
    gender_fig = go.Figure()
    gender_fig.add_trace(go.Bar(
        x=["Laki-laki", "Perempuan"],
        y=[lk_val, pr_val],
        marker_color=[PALETTE["indigo"], "#E91E8C"],
        text=[f"{lk_val:.2f}%", f"{pr_val:.2f}%"],
        textposition='outside',
        textfont=dict(size=12, color=PALETTE["text"]),
        hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
        width=0.45,
    ))
    apply_chart(gender_fig, height=260, no_legend=True)
    gender_fig.update_layout(
        xaxis_title="",
        yaxis=dict(title="Persentase (%)", ticksuffix="%", gridcolor="#EEF1F8"),
        bargap=0.4,
    )

    # ── Gender trend (lk vs pr) ───────────────────────────────────────────────────
    t_all      = trend_filter(df, level, prov, kab)
    has_gender = 'jk_lk' in t_all.columns and 'jk_pr' in t_all.columns
    gender_trend_fig = go.Figure()
    if has_gender and not t_all.empty:
        tg = t_all.groupby('thn')[['jk_lk', 'jk_pr']].mean().reset_index()
        all_vals  = pd.concat([tg['jk_lk'], tg['jk_pr']])
        gt_y_min  = max(0.0, float(all_vals.min()) * 0.92)
        gt_y_max  = min(100.0, float(all_vals.max()) * 1.06)
        gender_trend_fig.add_trace(go.Scatter(
            x=tg['thn'], y=tg['jk_lk'], name="Laki-laki",
            mode='lines+markers',
            line=dict(color=PALETTE["indigo"], width=2.5, shape='spline'),
            marker=dict(size=6),
            hovertemplate="Laki-laki %{x}: %{y:.2f}%<extra></extra>",
        ))
        gender_trend_fig.add_trace(go.Scatter(
            x=tg['thn'], y=tg['jk_pr'], name="Perempuan",
            mode='lines+markers',
            line=dict(color="#E91E8C", width=2.5, shape='spline', dash='dash'),
            marker=dict(size=6),
            hovertemplate="Perempuan %{x}: %{y:.2f}%<extra></extra>",
        ))
    else:
        gt_y_min, gt_y_max = 0, 100
    apply_chart(gender_trend_fig, height=260)
    gender_trend_fig.update_layout(
        hovermode='x unified',
        xaxis_title="Tahun",
        yaxis=dict(
            title="Persentase (%)",
            ticksuffix="%",
            gridcolor="#EEF1F8",
            range=[gt_y_min, gt_y_max] if has_gender else [0, 100],
        ),
    )

    # ── Regional bar (wilayah) ────────────────────────────────────────────────────
    if level == 'nasional':
        reg_df   = df[(df['thn'] == year) & (df['lvl_wil'] == 'provinsi')].copy()
        name_col  = 'nm_prov'
        reg_title = "Perbandingan Antar Provinsi"
        reg_sub   = f"15 provinsi dengan {cfg['unit']} tertinggi"
    elif level == 'provinsi':
        reg_df   = df[
            (df['thn'] == year) &
            (df['lvl_wil'].isin(['kabupaten', 'kota'])) &
            (df['nm_prov'] == prov)
        ].copy()
        name_col  = 'nm_kabkot'
        reg_title = f"Perbandingan Kabupaten/Kota — {prov}"
        reg_sub   = f"15 wilayah dengan {cfg['unit']} tertinggi di {prov}"
    else:
        # level == kabupaten: tampilkan semua kabkot di provinsi yang sama sebagai konteks
        reg_df   = df[
            (df['thn'] == year) &
            (df['lvl_wil'].isin(['kabupaten', 'kota'])) &
            (df['nm_prov'] == prov)
        ].copy()
        name_col  = 'nm_kabkot'
        reg_title = f"Konteks Kabupaten/Kota — {prov}"
        reg_sub   = f"Semua wilayah di {prov}" if prov else "Semua kabupaten/kota"

    if not reg_df.empty and name_col in reg_df.columns and 'total' in reg_df.columns:
        reg_df = reg_df[[name_col, 'total']].dropna().sort_values('total').tail(15)
        bar_fig = px.bar(
            reg_df, x='total', y=name_col, orientation='h',
            color='total',
            color_continuous_scale=cfg["gradient"],
            text=[f"{v:.1f}%" for v in reg_df['total']],
        )
        bar_fig.update_traces(
            textposition='outside',
            hovertemplate=f"<b>%{{y}}</b><br>{cfg['unit']}: %{{x:.2f}}%<extra></extra>",
        )
        bar_fig.update_coloraxes(showscale=False)
        apply_chart(bar_fig, height=420)
        bar_fig.update_layout(
            xaxis=dict(title=cfg["bar_label"], ticksuffix="%"),
            yaxis_title="",
        )
    else:
        bar_fig = go.Figure()
        bar_fig.add_annotation(
            text="Data wilayah tidak tersedia untuk filter ini",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=13, color=PALETTE["muted"]),
        )
        apply_chart(bar_fig, height=420)

    # ── Gauge: nilai saat ini vs tahun sebelumnya ─────────────────────────────────
    # Ambil nilai tahun sebelumnya dari trend untuk delta (selisih poin persentase)
    t_sorted     = t.sort_values('thn')
    prev_year_df = t_sorted[t_sorted['thn'] < year]
    ref_val      = float(prev_year_df['total'].iloc[-1]) if not prev_year_df.empty else v_val

    # Batas gauge dinamis: selalu mulai dari 0, atas = max(100, nilai + 10%)
    gauge_max = 100.0

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(v_val, 2),
        number=dict(suffix="%", font=dict(size=36, color=cfg["color"]), valueformat=".2f"),
        delta=dict(
            reference=ref_val,
            relative=False,
            suffix=" pp",
            valueformat="+.2f",
            increasing=dict(color=PALETTE["teal"]),
            decreasing=dict(color=PALETTE["red"]),
        ),
        gauge=dict(
            axis=dict(
                range=[0, gauge_max],
                ticksuffix="%",
                tickfont=dict(size=10),
                nticks=6,
            ),
            bar=dict(color=cfg["color"], thickness=0.28),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0,               gauge_max * 0.33], color="#F4F6FB"),
                dict(range=[gauge_max * 0.33, gauge_max * 0.66], color="#E8EEF8"),
                dict(range=[gauge_max * 0.66, gauge_max],        color="#D6E4F5"),
            ],
            threshold=dict(
                line=dict(color=cfg["color"], width=3),
                thickness=0.75,
                value=round(v_val, 2),
            ),
        ),
        title=dict(
            text="{} — {}  <span style='font-size:11px;color:{}'>vs {}</span>".format(
                cfg["unit"], year, PALETTE["muted"], year - 1
            ),
            font=dict(size=13, color=PALETTE["muted"]),
        ),
        domain=dict(x=[0, 1], y=[0, 1]),
    ))
    apply_chart(gauge_fig, height=280, no_legend=True)
    gauge_fig.update_layout(margin=dict(l=24, r=24, t=48, b=16))

    # ── Layout ────────────────────────────────────────────────────────────────────
    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level, prov, kab)}  ·  {year}", className="page-badge"),
            html.H1(cfg["title"], className="page-title"),
            html.P(cfg["subtitle"], className="page-subtitle"),
        ]),

        # Row 1: KPI cards
        dbc.Row([
            dbc.Col(kpi_card(
                cfg["kpi_icon"], cfg["unit"],
                f"{v_val:.2f}%",
                cfg["color"], cfg["icon_bg"],
            ), md=4),
            dbc.Col(kpi_card(
                "👨", f"{cfg['unit']} Laki-laki",
                f"{lk_val:.2f}%",
                PALETTE["indigo"], f"{PALETTE['indigo']}14",
            ), md=4),
            dbc.Col(kpi_card(
                "👩", f"{cfg['unit']} Perempuan",
                f"{pr_val:.2f}%",
                "#E91E8C", "#E91E8C14",
            ), md=4),
        ], className="g-3 mb-2"),

        section("Indikator & Perbandingan Gender"),
        dbc.Row([
            dbc.Col(chart_card(
                f"Gauge {cfg['unit']}",
                f"Nilai {cfg['unit']} tahun {year} vs tahun sebelumnya",
                gauge_fig,
            ), md=4),
            dbc.Col(chart_card(
                "Perbandingan Gender",
                f"{cfg['unit']} laki-laki vs perempuan",
                gender_fig,
            ), md=4),
            dbc.Col(chart_card(
                "Tren Gender 2018–2025",
                "Perkembangan tahunan per jenis kelamin",
                gender_trend_fig,
            ), md=4),
        ], className="g-3 mb-2"),

        section("Analisis Spasial & Tren Historis"),
        dbc.Row([
            dbc.Col(chart_card(reg_title, reg_sub, bar_fig), md=7),
            dbc.Col(chart_card(
                f"Tren {cfg['unit']} 2018–2025",
                f"Perkembangan historis — {loc(level, prov, kab)}",
                trend_fig,
            ), md=5),
        ], className="g-3"),
    ])



def render_demo_page():
    np.random.seed(42)
    years = list(range(2018, 2026))
    puk  = [130e6 + i*2e6 + np.random.randn()*1e6 for i in range(8)]
    ak   = [80e6  + i*1.5e6 + np.random.randn()*0.5e6 for i in range(8)]
    pyb  = [75e6  + i*1.4e6 + np.random.randn()*0.5e6 for i in range(8)]
    pt   = [8e6   - i*0.2e6 + np.random.randn()*0.3e6 for i in range(8)]

    trend_fig = go.Figure()
    for vals, nm, cl in [(puk,"PUK","#AED6F1"),(ak,"AK",PALETTE["sky"]),
                          (pyb,"Bekerja",PALETTE["teal"]),(pt,"Pengangguran",PALETTE["red"])]:
        trend_fig.add_trace(go.Scatter(
            x=years, y=vals, name=nm, mode='lines+markers',
            line=dict(color=cl, width=2.5, shape='spline'), marker=dict(size=6),
        ))
    apply_chart(trend_fig, height=380)
    trend_fig.update_layout(title="Demo: Tren Ketenagakerjaan 2018–2025", hovermode='x unified')

    sektor = ['Pertanian','Industri','Perdagangan','Konstruksi','Jasa','Transportasi','Pendidikan','Kesehatan']
    vals   = [40e6, 18e6, 25e6, 8e6, 12e6, 6e6, 5e6, 4e6]
    bar_fig = px.bar(
        pd.DataFrame({'Sektor': sektor, 'Jumlah': vals}).sort_values('Jumlah'),
        x='Jumlah', y='Sektor', orientation='h',
        color='Jumlah', color_continuous_scale=["#DBEAFE", PALETTE["blue"]],
        text=[fmt_compact(v) for v in sorted(vals)],
    )
    bar_fig.update_traces(textposition='outside')
    bar_fig.update_coloraxes(showscale=False)
    apply_chart(bar_fig, height=340)

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card("👥", "Penduduk Usia Kerja", "138.5M", PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=3),
            dbc.Col(kpi_card("💼", "Angkatan Kerja",       "91.2M", PALETTE["blue"],   f"{PALETTE['blue']}14"),   md=3),
            dbc.Col(kpi_card("✅", "Penduduk Bekerja",     "85.8M", PALETTE["teal"],   f"{PALETTE['teal']}14"),   md=3),
            dbc.Col(kpi_card("❌", "Pengangguran",          "5.4M (5.9%)", PALETTE["red"], f"{PALETTE['red']}14"), md=3),
        ], className="g-3 mb-4"),
        dbc.Row([
            dbc.Col(chart_card("Demo: Tren Ketenagakerjaan", "(data mock)", trend_fig), md=7),
            dbc.Col(chart_card("Demo: Top Sektor", "(data mock)", bar_fig), md=5),
        ], className="g-3"),
    ])


if __name__ == "__main__":
    # host='0.0.0.0' allows access from other devices on your local network
    app.run(debug=True, host='0.0.0.0', port=8060)