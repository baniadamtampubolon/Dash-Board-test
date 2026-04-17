"""Peta Sebaran (Choropleth Map) page."""

from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, load_geojson, _PROV_NAME_TO_GEO, DATA_AVAILABLE
from components import kpi_card, chart_card, section, fmt_compact, loc


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: PETA SEBARAN (GeoMap Choropleth)
# ══════════════════════════════════════════════════════════════════════════════════
_GEOMAP_INDICATORS = {
    'PUK':  {'file': 'Database/PUK-2018-2025-ver2.xlsx',  'col': 'total', 'label': 'Penduduk Usia Kerja',       'unit': 'jiwa',  'is_ratio': False},
    'AK':   {'file': 'Database/AK-2018-2025-ver2.xlsx',   'col': 'total', 'label': 'Angkatan Kerja',            'unit': 'jiwa',  'is_ratio': False},
    'PYB':  {'file': 'Database/PYB-2018-2025-ver3.xlsx',  'col': 'total', 'label': 'Penduduk Bekerja',          'unit': 'jiwa',  'is_ratio': False},
    'PT':   {'file': 'Database/PT-2018-2025-ver2.xlsx',   'col': 'total', 'label': 'Pengangguran Terbuka',      'unit': 'jiwa',  'is_ratio': False},
    'TPAK': {'file': 'Database/TPAK-2018-2025-ver2.xlsx', 'col': 'TPAK',  'label': 'Tingkat Partisipasi AK',    'unit': '%',     'is_ratio': True},
    'TPT':  {'file': 'Database/TPT-2018-2025-ver2.xlsx',  'col': 'TPT',   'label': 'Tingkat Pengangguran',      'unit': '%',     'is_ratio': True},
    'EPR':  {'file': 'Database/EPR-2018-2025-ver2.xlsx',  'col': 'EPR',   'label': 'Employment to Pop. Ratio',  'unit': '%',     'is_ratio': True},
}

def render_geomap(year, level, prov, kab):
    """Peta Sebaran page — always shows ALL provinces regardless of sidebar filter."""
    indicator_options = [
        {'label': f"{k} — {v['label']}", 'value': k}
        for k, v in _GEOMAP_INDICATORS.items()
    ]
    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📅 {year}", className="page-badge"),
            html.H1("Peta Sebaran Ketenagakerjaan", className="page-title"),
            html.P("Distribusi indikator ketenagakerjaan per provinsi di seluruh Indonesia", className="page-subtitle"),
        ]),

        # Inline indicator selector
        dbc.Row([
            dbc.Col([
                html.Span("Pilih Indikator", className="filter-label",
                          style={"color": PALETTE["text"], "fontSize": "13px", "fontWeight": "600"}),
                dcc.Dropdown(
                    id="geomap-indicator",
                    options=indicator_options,
                    value="PUK",
                    clearable=False,
                    style={"marginTop": "6px"},
                ),
            ], md=4),
        ], className="mb-4"),

        # Content rendered by callback
        html.Div(id="geomap-content"),
    ])




def register_geomap_callbacks(app):
    @app.callback(
        Output("geomap-content", "children"),
        Input("geomap-indicator", "value"),
        Input("dd-year", "value"),
    )
    def update_geomap(indicator, year):
        if not indicator or not DATA_AVAILABLE:
            return html.Div("Memuat data…")
    
        cfg = _GEOMAP_INDICATORS[indicator]
        df = load_data(cfg['file'])
        geojson = load_geojson()
    
        # Get province-level data for the selected year
        prov_data = df[(df['thn'] == year) & (df['lvl_wil'].str.lower() == 'provinsi')].copy()
    
        col = cfg['col']
        if col not in prov_data.columns:
            return html.Div(f"Kolom '{col}' tidak ditemukan dalam dataset.")
    
        if cfg['is_ratio']:
            prov_data['value'] = prov_data[col].apply(lambda x: round(float(x), 2))
        else:
            prov_data['value'] = pd.to_numeric(prov_data[col], errors='coerce').fillna(0).astype(int)
    
        # Map province names to GeoJSON names
        prov_data['geo_name'] = prov_data['nm_prov'].map(
            lambda x: _PROV_NAME_TO_GEO.get(x, x)
        )
    
        # ── Choropleth Map ────────────────────────────────────────────────────────
        if cfg['is_ratio']:
            hover_tmpl = "<b>%{customdata[0]}</b><br>" + f"{indicator}: " + "%{z:.2f}%<extra></extra>"
            color_scale = [[0, "#E3EDF9"], [0.35, "#90CAF9"], [0.65, PALETTE["sky"]], [1, PALETTE["navy"]]]
            fmt_val = lambda v: f"{v:.2f}%"
        else:
            hover_tmpl = "<b>%{customdata[0]}</b><br>" + f"{cfg['label']}: " + "%{z:,.0f} jiwa<extra></extra>"
            color_scale = [[0, "#E6F4F1"], [0.3, "#64B5F6"], [0.6, PALETTE["blue"]], [1, PALETTE["navy"]]]
            fmt_val = lambda v: fmt_compact(v)
    
        map_fig = go.Figure(go.Choroplethmap(
            geojson=geojson,
            locations=prov_data['geo_name'],
            featureidkey="properties.PROVINSI",
            z=prov_data['value'],
            colorscale=color_scale,
            marker=dict(line=dict(width=0.8, color="#FFFFFF")),
            hovertemplate=hover_tmpl,
            customdata=prov_data[['nm_prov']].values,
            colorbar=dict(
                title=dict(text=f"{indicator} ({cfg['unit']})", font=dict(size=12)),
                thickness=14, len=0.6, x=0.98,
                tickfont=dict(size=10),
            ),
        ))
    
        map_fig.update_layout(
            map=dict(
                style="white-bg",
                center=dict(lat=-2.5, lon=118),
                zoom=3.4,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans, sans-serif"),
        )
    
        # ── Top 3 & Bottom 3 ─────────────────────────────────────────────────────
        sorted_prov = prov_data.sort_values('value', ascending=False)
        top3 = sorted_prov.head(3)
        bot3 = sorted_prov.tail(3).sort_values('value', ascending=True)
    
        top_cards = []
        top_icons  = ["🥇", "🥈", "🥉"]
        top_colors = [PALETTE["teal"], PALETTE["blue"], PALETTE["indigo"]]
        for i, (_, row) in enumerate(top3.iterrows()):
            top_cards.append(
                dbc.Col(kpi_card(top_icons[i], row['nm_prov'], fmt_val(row['value']),
                                 top_colors[i], f"{top_colors[i]}14"), md=2)
            )
    
        bot_cards = []
        bot_icons  = ["⚠️", "⚠️", "⚠️"]
        for i, (_, row) in enumerate(bot3.iterrows()):
            bot_cards.append(
                dbc.Col(kpi_card(bot_icons[i], row['nm_prov'], fmt_val(row['value']),
                                 PALETTE["gold"], f"{PALETTE['gold']}14"), md=2)
            )
    
        # ── Province ranking bar chart ────────────────────────────────────────────
        rank_df = prov_data.sort_values('value', ascending=True)
    
        bar_fig = px.bar(
            rank_df, x='value', y='nm_prov', orientation='h',
            color='value', color_continuous_scale=[PALETTE["sky"], PALETTE["blue"], PALETTE["navy"]],
            text=[fmt_val(v) for v in rank_df['value']],
        )
        bar_fig.update_traces(
            textposition='outside', textfont_size=9,
            hovertemplate="<b>%{y}</b><br>" + f"{indicator}: " + "%{x:,.0f}<extra></extra>" if not cfg['is_ratio']
            else "<b>%{y}</b><br>" + f"{indicator}: " + "%{x:.2f}%<extra></extra>",
        )
        bar_fig.update_coloraxes(showscale=False)
        apply_chart(bar_fig, height=max(600, len(rank_df) * 22))
        bar_fig.update_layout(
            xaxis_title=f"{indicator} ({cfg['unit']})", yaxis_title="",
            margin=dict(l=12, r=60, t=12, b=40),
        )
    
        return html.Div([
            # Map
            html.Div(className="chart-card", style={"marginBottom": "20px"}, children=[
                html.Div(f"Peta {cfg['label']} per Provinsi", className="chart-card-title"),
                html.Div(f"Tahun {year} — Semua provinsi di Indonesia", className="chart-card-sub"),
                dcc.Graph(figure=map_fig, config={"displayModeBar": False, "scrollZoom": True},
                          style={"borderRadius": "0 0 16px 16px"}),
            ]),
    
            # Top / Bottom KPIs
            section("Top & Bottom Provinsi"),
            dbc.Row([
                dbc.Col(html.Div("🏆 Tertinggi", style={
                    "fontSize": "12px", "fontWeight": "700", "color": PALETTE["teal"],
                    "marginBottom": "8px", "letterSpacing": "0.5px"}), md=6),
                dbc.Col(html.Div("📉 Terendah", style={
                    "fontSize": "12px", "fontWeight": "700", "color": PALETTE["gold"],
                    "marginBottom": "8px", "letterSpacing": "0.5px"}), md=6),
            ]),
            dbc.Row(top_cards + bot_cards, className="g-3 mb-3"),
    
            # Ranking bar
            section("Ranking Seluruh Provinsi"),
            html.Div(className="chart-card", children=[
                html.Div(f"Ranking {cfg['label']} — {year}", className="chart-card-title"),
                html.Div("38 provinsi diurutkan dari terendah ke tertinggi", className="chart-card-sub"),
                dcc.Graph(figure=bar_fig, config={"displayModeBar": False},
                          style={"borderRadius": "0 0 16px 16px"}),
            ]),
        ])
    
    
