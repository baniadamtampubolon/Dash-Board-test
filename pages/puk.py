"""Penduduk Usia Kerja (PUK) page."""

from dash import dcc, html
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc
from map_helper import build_geomap_layout


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: PUK
# ══════════════════════════════════════════════════════════════════════════════════
def render_puk(year, level, prov, kab):
    df_puk = load_data("Database/PUK-2018-2025-ver2.xlsx")
    df_pt  = load_data("Database/PT-2018-2025-ver2.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025-ver4.xlsx")

    data = filter_data(df_puk, year, level, prov, kab)
    data_pt  = filter_data(df_pt,  year, level, prov, kab)
    data_pyb = filter_data(df_pyb, year, level, prov, kab)

    total = int(data['total'].sum())
    working    = int(data_pyb['total'].sum())
    unemployed = int(data_pt['total'].sum())
    bak        = max(0, total - working - unemployed)
    
    # Rincian BAK
    sekolah = int(data.get('keg_sklh', pd.Series([0])).sum())
    mrt = int(data.get('keg_mrt', pd.Series([0])).sum())
    lainnya = int(data.get('keg_lain', pd.Series([0])).sum())
    # Normalisasi jika total ketiganya tidak sama persis dengan bak (anomali data)
    bak_sum = sekolah + mrt + lainnya
    if bak_sum > 0 and abs(bak_sum - bak) > 0:
        sekolah = int(sekolah / bak_sum * bak)
        mrt = int(mrt / bak_sum * bak)
        lainnya = bak - sekolah - mrt

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
        hovertemplate="<b>%{label}</b><br>%{value:,.2f} jiwa<extra></extra>",
    ))
    gen_fig.add_annotation(text=f"<b>PUK</b><br>Gender", x=0.5, y=0.5,
                           font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(gen_fig, height=300, no_legend=False)

    # ── Kota vs Desa donut ────────────────────────────────────────────────────
    kd_fig = go.Figure(go.Pie(
        labels=["Perkotaan", "Perdesaan"], values=[kota, desa], hole=0.6,
        marker=dict(colors=[PALETTE["sky"], PALETTE["gold"]]),
        textinfo='none', textposition='outside',
        text=[f"Perkotaan<br>{fmt_compact(kota)}", f"Perdesaan<br>{fmt_compact(desa)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.2f} jiwa<extra></extra>",
    ))
    kd_fig.add_annotation(text=f"<b>PUK</b><br>Wilayah", x=0.5, y=0.5,
                          font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(kd_fig, height=300, no_legend=False)

    # ── Status aktivitas donut ────────────────────────────────────────────────
    act_fig = go.Figure(go.Pie(
        labels=["Bekerja", "Pengangguran", "Sekolah", "Mengurus Rumah Tangga", "Lainnya"], 
        values=[working, unemployed, sekolah, mrt, lainnya], 
        hole=0.6,
        marker=dict(colors=[PALETTE["teal"], PALETTE["red"], "#A5D6A7", "#81C784", "#C8E6C9"]),
        textinfo='none', textposition='outside',
        text=[
            f"Bekerja<br>{fmt_compact(working)}", 
            f"Pengangguran<br>{fmt_compact(unemployed)}", 
            f"Sekolah<br>{fmt_compact(sekolah)}",
            f"Mengurus RT<br>{fmt_compact(mrt)}",
            f"Lainnya<br>{fmt_compact(lainnya)}"
        ],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.2f} jiwa<extra></extra>",
    ))
    act_fig.add_annotation(text="<b>Status<br>Aktivitas</b>", x=0.5, y=0.5,
                           font=dict(size=11, color=PALETTE["text"]), showarrow=False)
    apply_chart(act_fig, height=320, no_legend=True)

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
        hovertemplate="<b>%{x}</b><br>%{y:,.2f} jiwa<extra></extra>",
    ))
    apply_chart(age_fig, height=340, no_legend=True)
    age_fig.update_layout(
        xaxis_title="Kelompok Usia", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[-0.5, len(age_m) - 0.5]),
    )

    # ── Education bar chart ───────────────────────────────────────────────────
    edu_map = {'pd_sd':'SD','pd_smp':'SMP','pd_smau':'SMA/MA','pd_smak':'SMK','pd_dipl':'Diploma','pd_univ':'Universitas'}
    edu_vals = [int(data[c].sum()) if c in data.columns else 0 for c in edu_map]
    edu_df = pd.DataFrame({'Pendidikan': list(edu_map.values()), 'Jumlah': edu_vals})
    
    edu_bar = px.bar(
        edu_df.sort_values('Jumlah'), x='Jumlah', y='Pendidikan', orientation='h',
        color='Jumlah', color_continuous_scale=["#DBEAFE", PALETTE["blue"], PALETTE["navy"]],
        text=[fmt_compact(v) for v in edu_df.sort_values('Jumlah')['Jumlah']],
    )
    edu_bar.update_traces(textposition='outside')
    edu_bar.update_coloraxes(showscale=False)
    apply_chart(edu_bar, height=340)
    edu_bar.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=10, r=60, t=10, b=10))

    # ── Trend (full width) ────────────────────────────────────────────────────
    t = trend_filter(df_puk, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    tp = trend_filter(df_pt,  level, prov, kab).groupby('thn')['total'].sum().reset_index()
    ty = trend_filter(df_pyb, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend = go.Figure()
    for dt, nm, cl in [(t, "PUK", "#AED6F1"), (ty, "Bekerja", PALETTE["teal"]), (tp, "Pengangguran", PALETTE["red"])]:
        trend.add_trace(go.Scatter(
            x=dt['thn'], y=dt['total'], name=nm, mode='lines+markers+text',
            line=dict(color=cl, width=3, shape='spline'),
            marker=dict(size=7, color=cl, line=dict(color='#fff', width=1.5)),
            text=[fmt_compact(v) for v in dt['total']], textposition='top center',
            textfont=dict(size=9, color=cl),
            hovertemplate=f"<b>{nm}</b>: %{{y:,.2f}}<extra></extra>",
        ))
    apply_chart(trend, height=340)
    trend.update_layout(
        hovermode='x unified', xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
    )

    map_section, top_bottom_section, rank_section = build_geomap_layout(df_puk, year, level, prov, 'PUK')

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Penduduk Usia Kerja (PUK)", className="page-title"),
            html.P("Distribusi demografis penduduk usia 15 tahun ke atas", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card(DashIconify(icon="fa-solid:users", width=24), "Total PUK",            fmt_compact(total),    PALETTE["blue"],   f"{PALETTE['blue']}14"),  md=3),
            dbc.Col(kpi_card(DashIconify(icon="la:industry-solid", width=26), "Penduduk Bekerja",     fmt_compact(working),  PALETTE["teal"],   f"{PALETTE['teal']}14"),  md=3),
            dbc.Col(kpi_card(DashIconify(icon="fa-solid:frown-open", width=24),  "Pengangguran Terbuka", fmt_compact(unemployed),PALETTE["red"],   f"{PALETTE['red']}14"),   md=3),
            dbc.Col(kpi_card(DashIconify(icon="fa-solid:home", width=24), "Bukan Angkatan Kerja", fmt_compact(bak),      PALETTE["muted"],  "#7A8BAA14"),              md=3),
        ], className="g-3 mb-2"),

        map_section,
        top_bottom_section,

        section("Profil Demografis"),
        dbc.Row([
            dbc.Col(chart_card("Perbandingan Gender", "Jumlah PUK laki-laki vs perempuan", gen_fig), md=4),
            dbc.Col(chart_card("Perkotaan vs Perdesaan", "Jumlah PUK berdasarkan klasifikasi wilayah", kd_fig), md=4),
            dbc.Col(chart_card("Status Aktivitas", "Komposisi kegiatan penduduk usia kerja", act_fig), md=4),
        ], className="g-3 mb-2"),

        section("Kelompok Usia & Pendidikan"),
        dbc.Row([
            dbc.Col(chart_card("PUK per Kelompok Usia", "Distribusi jumlah berdasarkan kelompok umur", age_fig), md=8),
            dbc.Col(chart_card("Tingkat Pendidikan", "Berdasarkan jenjang pendidikan", edu_bar), md=4),
        ], className="g-3 mb-2"),

        section("Tren Historis PUK"),
        dbc.Row([
            dbc.Col(chart_card("Tren PUK 2018–2025",
                               f"Perkembangan historis — {loc(level,prov,kab)}", trend), md=12),
        ], className="g-3"),
        
        rank_section
    ])
