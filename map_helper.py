import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import plotly.express as px
import plotly.graph_objects as go

from design import PALETTE, apply_chart
from components import kpi_card, section, fmt_compact
from data_loader import load_geojson, load_geojson_kabkot, _PROV_NAME_TO_GEO, _PROV_NAME_TO_GEO_KABKOT, _KABKOT_NAME_TO_GEO, _PROV_BOUNDS, expand_bounds, center_zoom_from_bounds

_GEOMAP_INDICATORS = {
    'PUK':  {'label': 'Penduduk Usia Kerja',       'unit': 'jiwa',  'is_ratio': False, 'col': 'total'},
    'AK':   {'label': 'Angkatan Kerja',            'unit': 'jiwa',  'is_ratio': False, 'col': 'total'},
    'PYB':  {'label': 'Penduduk Bekerja',          'unit': 'jiwa',  'is_ratio': False, 'col': 'total'},
    'PT':   {'label': 'Pengangguran Terbuka',      'unit': 'jiwa',  'is_ratio': False, 'col': 'total'},
    'TPAK': {'label': 'Tingkat Partisipasi AK',    'unit': '%',     'is_ratio': True,  'col': 'TPAK'},
    'TPT':  {'label': 'Tingkat Pengangguran',      'unit': '%',     'is_ratio': True,  'col': 'TPT'},
    'EPR':  {'label': 'Employment to Pop. Ratio',  'unit': '%',     'is_ratio': True,  'col': 'EPR'},
}

def build_geomap_layout(df, year, level, prov, indicator_key):
    """
    Build the GeoMap layout consisting of Top/Bottom KPI cards, Choropleth map, and ranking bar chart.
    `df` should be the raw (unfiltered) dataframe containing all regions for the given metric.
    """
    cfg = _GEOMAP_INDICATORS[indicator_key]
    col = cfg['col']

    if level == 'nasional':
        prov_data = df[(df['thn'] == year) & (df['lvl_wil'].str.lower() == 'provinsi')].copy()
        geojson = load_geojson()
        feature_key = "properties.PROVINSI"
        name_col = 'nm_prov'
        sub_label = "Provinsi"
        scope_label = "Indonesia"
    else:
        prov_data = df[(df['thn'] == year) & 
                       (df['lvl_wil'].str.lower().isin(['kabupaten', 'kota'])) & 
                       (df['nm_prov'] == prov)].copy()
        full_geojson = load_geojson_kabkot()
        geo_prov = _PROV_NAME_TO_GEO_KABKOT.get(prov, prov)
        filtered_features = [
            f for f in full_geojson['features']
            if f['properties'].get('NAME_1', '') == geo_prov
        ]
        geojson = {
            "type": "FeatureCollection",
            "features": filtered_features
        }
        feature_key = "properties.NAME_2"
        name_col = 'nm_kabkot'
        sub_label = "Kabupaten/Kota"
        scope_label = prov

    if prov_data.empty or col not in prov_data.columns:
        return html.Div(f"Data {sub_label.lower()} untuk {indicator_key} pada tahun {year} tidak tersedia.", className="p-4 text-center text-muted"), None, None

    if cfg['is_ratio']:
        prov_data['value'] = prov_data[col].apply(lambda x: round(float(x), 2))
    else:
        prov_data['value'] = pd.to_numeric(prov_data[col], errors='coerce').fillna(0).astype(int)

    if level == 'nasional':
        prov_data['geo_name'] = prov_data[name_col].map(lambda x: _PROV_NAME_TO_GEO.get(x, x))
    else:
        prov_data['geo_name'] = prov_data[name_col].map(lambda x: _KABKOT_NAME_TO_GEO.get(x, x))

    # ── Choropleth Map ────────────────────────────────────────────────────────
    if cfg['is_ratio']:
        hover_tmpl = "<b>%{customdata[0]}</b><br>" + f"{indicator_key}: " + "%{z:.2f}%<extra></extra>"
        color_scale = [[0, "#E3EDF9"], [0.35, "#90CAF9"], [0.65, PALETTE["sky"]], [1, PALETTE["navy"]]]
        fmt_val = lambda v: f"{v:.2f}%"
    else:
        hover_tmpl = "<b>%{customdata[0]}</b><br>" + f"{cfg['label']}: " + "%{z:,.2f} jiwa<extra></extra>"
        color_scale = [[0, "#E6F4F1"], [0.3, "#64B5F6"], [0.6, PALETTE["blue"]], [1, PALETTE["navy"]]]
        fmt_val = lambda v: fmt_compact(v)

    map_fig = go.Figure(go.Choroplethmap(
        geojson=geojson,
        locations=prov_data['geo_name'],
        featureidkey=feature_key,
        z=prov_data['value'],
        colorscale=color_scale,
        marker=dict(line=dict(width=0.8, color="#FFFFFF")),
        hovertemplate=hover_tmpl,
        customdata=prov_data[[name_col]].values,
        colorbar=dict(
            title=dict(text=f"{indicator_key} ({cfg['unit']})", font=dict(size=12)),
            thickness=14, len=0.6, x=0.98,
            tickfont=dict(size=10),
        ),
    ))

    if level == 'nasional':
        map_center = dict(lat=-2.5, lon=118)
        map_zoom = 4
    else:
        map_center, map_zoom = center_zoom_from_bounds(geo_prov)
        map_zoom = map_zoom + 1

    map_fig.update_layout(
        map=dict(
            style="white-bg",
            center=map_center,
            zoom=map_zoom,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        hoverlabel=dict(bgcolor=PALETTE["navy"], font=dict(color="white"), bordercolor=PALETTE["navy"]),
    )

    # ── Top 3 & Bottom 3 ─────────────────────────────────────────────────────
    sorted_prov = prov_data.sort_values('value', ascending=False)
    top3 = sorted_prov.head(3)
    bot3 = sorted_prov.tail(3).sort_values('value', ascending=True)

    top_cards = []
    top_icons  = [
        DashIconify(icon="fa-solid:trophy", width=24),
        DashIconify(icon="fa-solid:medal", width=24),
        DashIconify(icon="fa-solid:award", width=24)
    ]
    top_colors = [PALETTE["teal"], PALETTE["blue"], PALETTE["indigo"]]
    for i, (_, row) in enumerate(top3.iterrows()):
        icon_with_rank = html.Div([top_icons[i], html.Span(f"#{i+1}", style={"marginLeft": "8px", "fontSize": "16px", "fontWeight": "800"})], style={"display": "flex", "alignItems": "center"})
        top_cards.append(
            dbc.Col(kpi_card(icon_with_rank, row[name_col], fmt_val(row['value']),
                             top_colors[i], f"{top_colors[i]}14"), md=2)
        )

    bot_cards = []
    bot_icons  = [
        DashIconify(icon="ph:warning-fill", width=24),
        DashIconify(icon="ph:warning-fill", width=24),
        DashIconify(icon="ph:warning-fill", width=24)
    ]
    for i, (_, row) in enumerate(bot3.iterrows()):
        icon_with_rank = html.Div([bot_icons[i], html.Span(f"#{i+1}", style={"marginLeft": "8px", "fontSize": "16px", "fontWeight": "800"})], style={"display": "flex", "alignItems": "center"})
        bot_cards.append(
            dbc.Col(kpi_card(icon_with_rank, row[name_col], fmt_val(row['value']),
                             PALETTE["gold"], f"{PALETTE['gold']}14"), md=2)
        )

    # ── Province ranking bar chart ────────────────────────────────────────────
    rank_df = prov_data.sort_values('value', ascending=True)

    bar_fig = px.bar(
        rank_df, x='value', y=name_col, orientation='h',
        color='value', color_continuous_scale=[PALETTE["sky"], PALETTE["blue"], PALETTE["navy"]],
        text=[fmt_val(v) for v in rank_df['value']],
    )
    bar_fig.update_traces(
        textposition='outside', textfont_size=9,
        hovertemplate="<b>%{y}</b><br>" + f"{indicator_key}: " + "%{x:,.2f}<extra></extra>" if not cfg['is_ratio']
        else "<b>%{y}</b><br>" + f"{indicator_key}: " + "%{x:.2f}%<extra></extra>",
    )
    bar_fig.update_coloraxes(showscale=False)
    apply_chart(bar_fig, height=max(600, len(rank_df) * 22))
    bar_fig.update_layout(
        xaxis_title=f"{indicator_key} ({cfg['unit']})", yaxis_title="",
        margin=dict(l=12, r=60, t=12, b=40),
    )

    map_section = html.Div([
        section("Peta Choropleth"),
        html.Div(className="chart-card", style={"marginBottom": "20px"}, children=[
            html.Div(f"Peta {cfg['label']} per {sub_label}", className="chart-card-title"),
            html.Div(f"Tahun {year} — Sebaran di {scope_label}", className="chart-card-sub"),
            dcc.Graph(figure=map_fig, config={"displayModeBar": "hover", "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"], "scrollZoom": True},
                      style={"borderRadius": "0 0 16px 16px"}),
        ])
    ], style={"marginTop": "32px"})

    top_bottom_section = html.Div([
        section(f"Top & Bottom {sub_label}"),
        dbc.Row([
            dbc.Col(html.Div([DashIconify(icon="lucide:trending-up", width=16, style={"marginRight": "6px", "marginBottom": "2px"}), "Tertinggi"], style={
                "fontSize": "12px", "fontWeight": "700", "color": PALETTE["teal"],
                "marginBottom": "8px", "letterSpacing": "0.5px", "display": "flex", "alignItems": "center"}), md=6),
            dbc.Col(html.Div([DashIconify(icon="lucide:trending-down", width=16, style={"marginRight": "6px", "marginBottom": "2px"}), "Terendah"], style={
                "fontSize": "12px", "fontWeight": "700", "color": PALETTE["gold"],
                "marginBottom": "8px", "letterSpacing": "0.5px", "display": "flex", "alignItems": "center"}), md=6),
        ]),
        dbc.Row(top_cards + bot_cards, className="g-3 mb-3"),
    ])

    rank_section = html.Div([
        section(f"Ranking Seluruh {sub_label}"),
        html.Div(className="chart-card", children=[
            html.Div(f"Ranking {cfg['label']} — {year}", className="chart-card-title"),
            html.Div(f"Urutan daerah di {scope_label} dari terendah ke tertinggi", className="chart-card-sub"),
            dcc.Graph(figure=bar_fig, config={"displayModeBar": False},
                      style={"borderRadius": "0 0 16px 16px"}),
        ]),
    ], style={"marginTop": "32px"})

    return map_section, top_bottom_section, rank_section
