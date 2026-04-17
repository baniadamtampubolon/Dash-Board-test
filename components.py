"""
Reusable UI components: KPI cards, chart cards, section labels, sidebar.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc

from design import PALETTE, CUSTOM_CSS
from data_loader import _YEARS, _PROV_LIST


def fmt_compact(val):
    if val >= 1_000_000:
        v = val / 1_000_000
        return f"{v:.1f}M" if v % 1 else f"{int(v)}M"
    elif val >= 1_000:
        v = val / 1_000
        return f"{v:.1f}K" if v % 1 else f"{int(v)}K"
    return f"{val:,.0f}"



# ─── Sidebar ─────────────────────────────────────────────────────────────────────
def make_sidebar():
    return html.Div(className="sidebar", children=[
        html.Div(className="sidebar-logo", children=[
            html.Img(src="/assets/kemnaker-logo.png",
                     style={"width": "210px", "height": "210px", "objectFit": "contain",
                            "borderRadius": "10px"}),
            html.H2("Dashboard Ketenagakerjaan"),
            html.P("Kementerian Ketenagakerjaan RI"),
        ]),

        html.Div(className="sidebar-section", children=[
            html.Div("Menu Utama", className="sidebar-label"),
            html.Div(className="sidebar-nav", children=[
                html.Button(["📊 ", "Ringkasan Eksekutif"], id="nav-main", className="nav-btn active", n_clicks=0),
                html.Button(["🗺️ ", "Peta Sebaran"],        id="nav-geomap", className="nav-btn", n_clicks=0),
                html.Button(["👥 ", "Penduduk Usia Kerja"], id="nav-puk",  className="nav-btn", n_clicks=0),
                html.Button(["💼 ", "Angkatan Kerja"],       id="nav-ak",   className="nav-btn", n_clicks=0),
                html.Button(["❌ ", "Pengangguran Terbuka"], id="nav-pt",   className="nav-btn", n_clicks=0),
                html.Button(["✅ ", "Penduduk Bekerja"],     id="nav-pyb",  className="nav-btn", n_clicks=0),
            ]),
        ]),

        html.Div(className="sidebar-section", style={"paddingTop": "10px"}, children=[
            html.Div("Indikator Rasio", className="sidebar-label"),
            html.Div(className="sidebar-nav", children=[
                html.Button(["📈 ", "TPAK"], id="nav-tpak", className="nav-btn", n_clicks=0),
                html.Button(["📉 ", "TPT"], id="nav-tpt_rasio", className="nav-btn", n_clicks=0),
                html.Button(["📊 ", "EPR"], id="nav-epr", className="nav-btn", n_clicks=0),
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



# ─── Helpers ─────────────────────────────────────────────────────────────────────
def loc_name(level, prov, kab):
    if level == "provinsi":   return prov or "—"
    if level == "kabupaten":  return kab  or "—"
    return "Indonesia"


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



def loc(level, prov, kab):
    if level == "provinsi":  return prov or "—"
    if level == "kabupaten": return kab  or "—"
    return "Indonesia"
