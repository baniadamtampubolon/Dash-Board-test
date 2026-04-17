"""Pengangguran Terbuka (PT) page."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc


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

