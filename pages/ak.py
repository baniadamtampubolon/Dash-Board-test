"""Angkatan Kerja (AK) page."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc


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

