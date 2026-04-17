"""Demo page (mock data when no database available)."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from design import PALETTE, SEQ, apply_chart
from components import kpi_card, chart_card, section, fmt_compact


# ══════════════════════════════════════════════════════════════════════════════════
#  DEMO PAGE (no data)
# ══════════════════════════════════════════════════════════════════════════════════
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


