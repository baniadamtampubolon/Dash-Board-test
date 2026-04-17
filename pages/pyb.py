"""Penduduk yang Bekerja (PYB) page."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc


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

