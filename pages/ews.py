"""Early Warning System (EWS) — Top 10 daerah per kategori dengan 3 mode chart."""

from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, apply_chart
from data_loader import load_data, load_geojson, _PROV_NAME_TO_GEO, DATA_AVAILABLE
from components import section, fmt_compact


# ══════════════════════════════════════════════════════════════════════════════════
#  EWS Indicator Configs
# ══════════════════════════════════════════════════════════════════════════════════
_EWS_INDICATORS = [
    {
        'id': 'putus_asa', 'name': 'Penganggur Putus Asa', 'icon': '😔',
        'file': 'Database/PT-2018-2025-ver2.xlsx', 'col': 'kat_pa',
        'unit': 'jiwa', 'is_ratio': False, 'compute': None,
        'color': PALETTE['red'], 'desc': 'PT — Kategori: Putus Asa', 'sort_asc': False,
    },
    {
        'id': 'pencari_kerja', 'name': 'Penganggur Pencari Kerja', 'icon': '🔍',
        'file': 'Database/PT-2018-2025-ver2.xlsx', 'col': 'kat_mp',
        'unit': 'jiwa', 'is_ratio': False, 'compute': None,
        'color': PALETTE['gold'], 'desc': 'PT — Kategori: Mencari Pekerjaan', 'sort_asc': False,
    },
    {
        'id': 'pekerja_keluarga', 'name': 'Pekerja Keluarga/Tak Dibayar', 'icon': '🏠',
        'file': 'Database/PYB-2018-2025-ver3.xlsx', 'col': 'sta_7',
        'unit': 'jiwa', 'is_ratio': False, 'compute': None,
        'color': PALETTE['gold'], 'desc': 'PYB — Status: Pekerja Keluarga/Tak Dibayar', 'sort_asc': False,
    },
    {
        'id': 'gender_gap', 'name': 'Gender Gap TPAK', 'icon': '⚤',
        'file': 'Database/TPAK-2018-2025-ver2.xlsx', 'col': 'gender_gap',
        'unit': 'pp', 'is_ratio': True, 'compute': 'gender_gap',
        'color': '#9B59B6', 'desc': 'TPAK Laki-laki − TPAK Perempuan', 'sort_asc': False,
    },
    {
        'id': 'kualitas_pendidikan', 'name': 'Kualitas Pendidikan (SD)', 'icon': '📚',
        'file': 'Database/PUK-2018-2025-ver2.xlsx', 'col': 'prop_sd',
        'unit': '%', 'is_ratio': True, 'compute': 'prop_sd',
        'color': PALETTE['indigo'], 'desc': 'PUK — Proporsi PUK SD per Total PUK', 'sort_asc': False,
    },
    {
        'id': 'pengangguran_terdidik', 'name': 'Pengangguran Terdidik', 'icon': '🎓',
        'file': 'Database/PT-2018-2025-ver2.xlsx', 'col': 'prop_univ',
        'unit': '%', 'is_ratio': True, 'compute': 'prop_univ',
        'color': PALETTE['blue'], 'desc': 'PT — Proporsi PT Universitas per Total PT', 'sort_asc': False,
    },
    {
        'id': 'partisipasi_perempuan', 'name': 'Partisipasi Perempuan', 'icon': '👩',
        'file': 'Database/TPAK-2018-2025-ver2.xlsx', 'col': 'jk_pr',
        'unit': '%', 'is_ratio': True, 'compute': None,
        'color': '#E91E8C', 'desc': 'TPAK — Jenis Kelamin: Perempuan', 'sort_asc': True,
    },
    {
        'id': 'partisipasi_muda', 'name': 'Partisipasi Pekerja Muda', 'icon': '🧑',
        'file': 'Database/TPAK-2018-2025-ver2.xlsx', 'col': 'ku_1519',
        'unit': '%', 'is_ratio': True, 'compute': None,
        'color': PALETTE['sky'], 'desc': 'TPAK — Golongan Umur: 15–19', 'sort_asc': True,
    },
    {
        'id': 'tpt', 'name': 'Tingkat Pengangguran Terbuka', 'icon': '📉',
        'file': 'Database/TPT-2018-2025-ver2.xlsx', 'col': 'TPT',
        'unit': '%', 'is_ratio': True, 'compute': None,
        'color': PALETTE['red'], 'desc': 'TPT — Rasio pengangguran terhadap AK', 'sort_asc': False,
    },
    {
        'id': 'epr', 'name': 'Employment to Population Ratio', 'icon': '📊',
        'file': 'Database/EPR-2018-2025-ver2.xlsx', 'col': 'EPR',
        'unit': '%', 'is_ratio': True, 'compute': None,
        'color': PALETTE['teal'], 'desc': 'EPR — Rasio penduduk bekerja terhadap PUK', 'sort_asc': True,
    },
]


# ══════════════════════════════════════════════════════════════════════════════════
#  Data Helpers
# ══════════════════════════════════════════════════════════════════════════════════
def _get_all_regions(cfg, year, level, prov):
    """Get ALL region data for a given indicator (not just top 10)."""
    df = load_data(cfg['file'])

    if level == 'nasional':
        sub = df[(df['thn'] == year) & (df['lvl_wil'] == 'provinsi')].copy()
        name_col = 'nm_prov'
    else:
        sub = df[(df['thn'] == year) &
                 (df['lvl_wil'].isin(['kabupaten', 'kota'])) &
                 (df['nm_prov'] == prov)].copy()
        name_col = 'nm_kabkot'

    if sub.empty:
        return pd.DataFrame(columns=['region', 'value', 'geo_name'])

    compute = cfg['compute']
    if compute == 'gender_gap':
        sub['value'] = sub['jk_lk'].astype(float) - sub['jk_pr'].astype(float)
    elif compute == 'prop_sd':
        total_col = 'PUK' if 'PUK' in sub.columns else 'total'
        sub['value'] = (pd.to_numeric(sub['pd_sd'], errors='coerce') /
                        pd.to_numeric(sub[total_col], errors='coerce') * 100)
    elif compute == 'prop_univ':
        total_col = 'PT' if 'PT' in sub.columns else 'total'
        sub['value'] = (pd.to_numeric(sub['pd_univ'], errors='coerce') /
                        pd.to_numeric(sub[total_col], errors='coerce') * 100)
    else:
        sub['value'] = pd.to_numeric(sub[cfg['col']], errors='coerce')

    sub['value'] = sub['value'].fillna(0).round(2)

    result = sub[[name_col, 'value']].copy()
    result.columns = ['region', 'value']

    # Add geo_name for map mode (province level only)
    if level == 'nasional' and name_col == 'nm_prov':
        result['geo_name'] = result['region'].map(lambda x: _PROV_NAME_TO_GEO.get(x, x))
    else:
        result['geo_name'] = result['region']

    return result


def _get_top10(all_data, sort_asc):
    """Extract top 10 from all data."""
    top = all_data.sort_values('value', ascending=sort_asc).head(10)
    return top.sort_values('value', ascending=not sort_asc)


# ══════════════════════════════════════════════════════════════════════════════════
#  Chart Builders
# ══════════════════════════════════════════════════════════════════════════════════
def _make_bar(cfg, top10, show_pct=False):
    """Horizontal bar chart for top 10."""
    if top10.empty:
        return go.Figure()

    # If user wants percentage AND the indicator is NOT already a ratio,
    # convert absolute values to share-of-total percentages.
    plot_data = top10.copy()
    if show_pct and not cfg['is_ratio']:
        total = plot_data['value'].sum()
        if total > 0:
            plot_data['value'] = (plot_data['value'] / total * 100).round(2)
        text_vals = [f"{v:.2f}%" for v in plot_data['value']]
        hover = "<b>%{y}</b><br>" + f"{cfg['name']}: " + "%{x:.2f}%<extra></extra>"
    elif cfg['is_ratio']:
        text_vals = [f"{v:.2f}%" for v in plot_data['value']]
        hover = "<b>%{y}</b><br>" + f"{cfg['name']}: " + "%{x:.2f}%<extra></extra>"
    else:
        text_vals = [fmt_compact(v) for v in plot_data['value']]
        hover = "<b>%{y}</b><br>" + f"{cfg['name']}: " + "%{x:,.0f}<extra></extra>"

    fig = px.bar(plot_data, x='value', y='region', orientation='h',
                 text=text_vals, color='value', 
                 color_continuous_scale=[[0, "#F8FAFC"], [1, cfg['color']]])
    fig.update_coloraxes(showscale=False)
    fig.update_traces(textposition='outside', textfont_size=11,
                      hovertemplate=hover, marker_line_width=0)
    apply_chart(fig, height=320)
    fig.update_layout(xaxis_title="", yaxis_title="",
                      margin=dict(l=8, r=50, t=8, b=24), showlegend=False)
    return fig


def _make_map(cfg, all_data, year):
    """Choropleth map for all provinces."""
    if all_data.empty:
        return go.Figure()

    geojson = load_geojson()
    color_scale = [[0, "#E3EDF9"], [0.35, "#90CAF9"], [0.65, cfg['color']], [1, PALETTE["navy"]]]

    if cfg['is_ratio']:
        hover = "<b>%{customdata[0]}</b><br>" + f"{cfg['name']}: " + "%{z:.2f}%<extra></extra>"
    else:
        hover = "<b>%{customdata[0]}</b><br>" + f"{cfg['name']}: " + "%{z:,.0f}<extra></extra>"

    fig = go.Figure(go.Choroplethmap(
        geojson=geojson,
        locations=all_data['geo_name'],
        featureidkey="properties.PROVINSI",
        z=all_data['value'],
        colorscale=color_scale,
        marker=dict(line=dict(width=0.6, color="#FFFFFF")),
        hovertemplate=hover,
        customdata=all_data[['region']].values,
        colorbar=dict(
            title=dict(text=f"{cfg['unit']}", font=dict(size=10)),
            thickness=10, len=0.5, x=0.98, tickfont=dict(size=9),
        ),
    ))
    fig.update_layout(
        map=dict(style="white-bg", center=dict(lat=-2.5, lon=118), zoom=3.2),
        margin=dict(l=0, r=0, t=0, b=0), height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
    )
    return fig


def _make_treemap(cfg, all_data):
    """Treemap for all regions."""
    if all_data.empty:
        return go.Figure()

    tree_data = all_data.copy()
    # Treemap needs positive values
    tree_data['abs_value'] = tree_data['value'].abs()
    tree_data = tree_data[tree_data['abs_value'] > 0]

    if tree_data.empty:
        return go.Figure()

    if cfg['is_ratio']:
        text_vals = [f"{v:.2f}%" for v in tree_data['value']]
    else:
        text_vals = [fmt_compact(v) for v in tree_data['value']]

    fig = px.treemap(
        tree_data, path=['region'], values='abs_value',
        color='value',
        color_continuous_scale=[[0, "#E3EDF9"], [0.5, cfg['color']], [1, PALETTE["navy"]]],
        custom_data=['region', 'value'],
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[1]}",
        hovertemplate="<b>%{customdata[0]}</b><br>" + f"{cfg['name']}: " +
                      "%{customdata[1]:,.0f}<extra></extra>" if not cfg['is_ratio']
        else "<b>%{customdata[0]}</b><br>" + f"{cfg['name']}: " +
             "%{customdata[1]:.2f}%<extra></extra>",
        textfont=dict(size=11),
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        margin=dict(l=2, r=2, t=2, b=2), height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
    )
    return fig


def _card_header(i, cfg):
    """Reusable card header for all modes."""
    return html.Div(style={"display": "flex", "alignItems": "center", "gap": "8px",
                            "padding": "16px 20px 0"}, children=[
        html.Div([
            html.Div(f"{i+1}. {cfg['name']}", style={
                "fontSize": "15px", "fontWeight": "800", "color": PALETTE["text"]}),
            html.Div(cfg['desc'], style={
                "fontSize": "12px", "color": PALETTE["muted"], "marginTop": "2px"}),
        ]),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: EWS (Layout)
# ══════════════════════════════════════════════════════════════════════════════════
def render_ews(year, level, prov, kab):
    ews_level = level if level in ('nasional', 'provinsi') else 'nasional'
    scope_label = prov if ews_level == 'provinsi' and prov else 'Indonesia'
    sub_label = 'Provinsi' if ews_level == 'nasional' else 'Kabupaten/Kota'

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{scope_label}  ·  {year}", className="page-badge"),
            html.H1("Early Warning System", className="page-title"),
            html.P(
                f"Top 10 {sub_label} per kategori indikator ketenagakerjaan",
                className="page-subtitle",
            ),
        ]),

        # Toggle switch - 3 modes
        html.Div(style={
            "display": "flex", "alignItems": "center", "gap": "16px", "flexWrap": "wrap",
            "marginBottom": "20px",
        }, children=[
            html.Span("Mode Visualisasi", style={
                "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            dbc.RadioItems(
                id="ews-mode",
                options=[
                    {"label": "Bar Chart", "value": "bar"},
                    {"label": "Peta Sebaran", "value": "map"},
                    {"label": "Treemap", "value": "treemap"},
                ],
                value="bar",
                inline=True,
                className="ews-toggle",
            ),
            html.Span("|", style={"color": PALETTE["border"], "fontSize": "18px", "margin": "0 4px"}),
            html.Span("Urutan", style={
                "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            dbc.RadioItems(
                id="ews-sort",
                options=[
                    {"label": "10 Tertinggi", "value": "desc"},
                    {"label": "10 Terendah", "value": "asc"},
                ],
                value="desc",
                inline=True,
                className="ews-toggle",
            ),
            html.Span("|", style={"color": PALETTE["border"], "fontSize": "18px", "margin": "0 4px"}),
            html.Span("Satuan", style={
                "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            dbc.RadioItems(
                id="ews-unit",
                options=[
                    {"label": "Angka", "value": "abs"},
                    {"label": "Persen", "value": "pct"},
                ],
                value="abs",
                inline=True,
                className="ews-toggle",
            ),
        ]),

        # Info banner
        html.Div(style={
            "display": "flex", "gap": "20px", "marginBottom": "20px",
            "padding": "12px 18px",
            "background": PALETTE["surface"],
            "border": f"1px solid {PALETTE['border']}",
            "borderRadius": "12px",
        }, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "6px"}, children=[
                html.Span("📊", style={"fontSize": "14px"}),
                html.Span("10 Indikator", style={
                    "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            ]),
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "6px"}, children=[
                html.Span("🏢", style={"fontSize": "14px"}),
                html.Span(f"Top 10 {sub_label}", style={
                    "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            ]),
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "6px"}, children=[
                html.Span("📍", style={"fontSize": "14px"}),
                html.Span(f"Cakupan: {scope_label}", style={
                    "fontSize": "13px", "fontWeight": "600", "color": PALETTE["text"]}),
            ]),
        ]),

        section("Indikator EWS"),
        html.Div(id="ews-content"),

        html.Div(
            "Early Warning System — Dashboard Ketenagakerjaan · Kemnaker RI",
            style={"textAlign": "center", "color": PALETTE["muted"],
                   "fontSize": "12px", "marginTop": "32px"},
        ),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  Callback Registration
# ══════════════════════════════════════════════════════════════════════════════════
def register_ews_callbacks(app):
    @app.callback(
        Output("ews-content", "children"),
        Input("ews-mode", "value"),
        Input("ews-sort", "value"),
        Input("ews-unit", "value"),
        Input("dd-year", "value"),
        Input("radio-level", "value"),
        Input("dd-prov", "value"),
    )
    def update_ews_content(mode, sort_dir, unit_mode, year, level, prov):
        if not DATA_AVAILABLE:
            return html.Div("Data tidak tersedia.")

        ews_level = level if level in ('nasional', 'provinsi') else 'nasional'
        scope_label = prov if ews_level == 'provinsi' and prov else 'Indonesia'
        sub_label = 'Provinsi' if ews_level == 'nasional' else 'Kabupaten/Kota'
        show_pct = (unit_mode == "pct")

        charts = []
        for i, cfg in enumerate(_EWS_INDICATORS):
            all_data = _get_all_regions(cfg, year, ews_level, prov)

            # Build chart based on mode
            if mode == "bar":
                # Use user-selected sort direction for bar mode
                use_asc = (sort_dir == "asc")
                top10 = _get_top10(all_data, use_asc)
                fig = _make_bar(cfg, top10, show_pct=show_pct)
                sort_word = "Terendah" if use_asc else "Tertinggi"
                sub_text = f"Top 10 {sub_label} {sort_word} — {scope_label} ({year})"
            elif mode == "map":
                if ews_level != 'nasional':
                    # Map only works at national level (provinces)
                    fig = go.Figure()
                    fig.update_layout(
                        height=300, margin=dict(l=0, r=0, t=40, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        annotations=[dict(text="Peta hanya tersedia di tingkat Nasional",
                                         x=0.5, y=0.5, xref="paper", yref="paper",
                                         showarrow=False, font=dict(size=13, color=PALETTE["muted"]))]
                    )
                else:
                    fig = _make_map(cfg, all_data, year)
                sub_text = f"Sebaran {sub_label} — {scope_label} ({year})"
            else:  # treemap
                fig = _make_treemap(cfg, all_data)
                sub_text = f"Proporsi {sub_label} — {scope_label} ({year})"

            card = html.Div(className="chart-card", style={"marginBottom": "4px"}, children=[
                _card_header(i, cfg),
                html.Div(sub_text, style={
                    "fontSize": "11px", "color": PALETTE["muted"],
                    "padding": "4px 18px 0", "fontWeight": "500"}),
                dcc.Graph(figure=fig, config={"displayModeBar": False, "scrollZoom": mode == "map"},
                          style={"borderRadius": "0 0 16px 16px"}),
            ])
            charts.append(card)

        # Arrange in 2 columns × 5 rows
        rows = []
        for r in range(5):
            rows.append(
                dbc.Row([
                    dbc.Col(charts[r * 2], md=6),
                    dbc.Col(charts[r * 2 + 1], md=6),
                ], className="g-3 mb-3")
            )

        return html.Div(rows)
