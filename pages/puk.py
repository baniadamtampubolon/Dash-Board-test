"""Penduduk Usia Kerja (PUK) page."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc


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

