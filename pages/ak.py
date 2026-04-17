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
    kota = int(data.get('kls_kota', pd.Series([0])).sum())
    desa = int(data.get('kls_desa', pd.Series([0])).sum())

    # ── Gender donut ──────────────────────────────────────────────────────────
    gen_fig = go.Figure(go.Pie(
        labels=["Laki-laki", "Perempuan"], values=[lk, pr], hole=0.6,
        marker=dict(colors=[PALETTE["blue"], "#F48FB1"]),
        textinfo='none', textposition='outside',
        text=[f"Laki-laki<br>{fmt_compact(lk)}", f"Perempuan<br>{fmt_compact(pr)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<extra></extra>",
    ))
    gen_fig.add_annotation(text=f"<b>AK</b><br>Gender", x=0.5, y=0.5,
                           font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(gen_fig, height=300, no_legend=False)

    # ── Kota vs Desa donut ────────────────────────────────────────────────────
    kd_fig = go.Figure(go.Pie(
        labels=["Perkotaan", "Perdesaan"], values=[kota, desa], hole=0.6,
        marker=dict(colors=[PALETTE["sky"], PALETTE["gold"]]),
        textinfo='none', textposition='outside',
        text=[f"Perkotaan<br>{fmt_compact(kota)}", f"Perdesaan<br>{fmt_compact(desa)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<extra></extra>",
    ))
    kd_fig.add_annotation(text=f"<b>AK</b><br>Wilayah", x=0.5, y=0.5,
                          font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(kd_fig, height=300, no_legend=False)

    # ── Age line chart (jumlah) ───────────────────────────────────────────────
    age_m = {
        'ku_1519':'15–19','ku_2024':'20–24','ku_2529':'25–29','ku_3034':'30–34',
        'ku_3539':'35–39','ku_4044':'40–44','ku_4549':'45–49','ku_5054':'50–54',
        'ku_5559':'55–59','ku_6064':'60–64','ku_65+':'65+',
    }
    age_vals = [int(data[c].sum()) if c in data.columns else 0 for c in age_m]
    age_fig = go.Figure(go.Scatter(
        x=list(age_m.values()), y=age_vals, mode='lines+markers+text',
        line=dict(color=PALETTE["blue"], width=3, shape='spline'),
        marker=dict(size=8, color=PALETTE["blue"], line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor='rgba(19,83,160,0.08)',
        text=[fmt_compact(v) for v in age_vals], textposition='top center',
        textfont=dict(size=9, color=PALETTE["blue"]),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} jiwa<extra></extra>",
    ))
    apply_chart(age_fig, height=340, no_legend=True)
    age_fig.update_layout(
        xaxis_title="Kelompok Usia", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[-0.5, len(age_m) - 0.5]),
    )

    # ── Education bar ─────────────────────────────────────────────────────────
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

    # ── Trend (full width) ────────────────────────────────────────────────────
    t = trend_filter(df, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t['total'], mode='lines+markers+text',
        line=dict(color=PALETTE["blue"], width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(19,83,160,0.08)',
        marker=dict(size=8, color=PALETTE["blue"], line=dict(color='#fff', width=1.5)),
        text=[fmt_compact(v) for v in t['total']], textposition='top center',
        textfont=dict(size=10, color=PALETTE["blue"]),
        hovertemplate="Tahun %{x}: %{y:,.0f}<extra></extra>",
    ))
    apply_chart(trend_fig, height=340)
    trend_fig.update_layout(
        xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
        hovermode='x unified',
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[int(t['thn'].min()) - 0.4, int(t['thn'].max()) + 0.4]) if not t.empty else {},
    )

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
            dbc.Col(chart_card("Perbandingan Gender", "Jumlah AK laki-laki vs perempuan", gen_fig), md=4),
            dbc.Col(chart_card("Perkotaan vs Perdesaan", "Jumlah AK berdasarkan klasifikasi wilayah", kd_fig), md=4),
            dbc.Col(chart_card("Tingkat Pendidikan", "Distribusi berdasarkan jenjang pendidikan", edu_fig), md=4),
        ], className="g-3 mb-2"),

        section("Kelompok Usia"),
        dbc.Row([
            dbc.Col(chart_card("AK per Kelompok Usia", "Distribusi jumlah berdasarkan kelompok umur", age_fig), md=12),
        ], className="g-3 mb-2"),

        section("Tren Historis Angkatan Kerja"),
        dbc.Row([
            dbc.Col(chart_card("Tren Angkatan Kerja 2018–2025",
                               f"Perkembangan historis — {loc(level,prov,kab)}", trend_fig), md=12),
        ], className="g-3"),
    ])
