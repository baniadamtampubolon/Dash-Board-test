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

    lk = int(data.get('jk_lk', pd.Series([0])).sum())
    pr = int(data.get('jk_pr', pd.Series([0])).sum())
    kota = int(data.get('kls_kota', pd.Series([0])).sum())
    desa = int(data.get('kls_desa', pd.Series([0])).sum())

    # ── Kategori PT bar ──────────────────────────────────────────────────────
    pt_map  = {'kat_mp':'Mencari Pekerjaan','kat_mu':'Mempersiapkan Usaha','kat_pa':'Putus Asa','kat_bmb':'Diterima Belum Bekerja'}
    pt_vals = [int(data[c].sum()) if c in data.columns else 0 for c in pt_map]
    ptdf    = pd.DataFrame({'Kategori': list(pt_map.values()), 'Jumlah': pt_vals})

    cat_fig = px.bar(
        ptdf.sort_values('Jumlah'), x='Jumlah', y='Kategori', orientation='h',
        color='Jumlah', color_continuous_scale=["#FEEBC8", PALETTE["gold"], PALETTE["red"]],
        text=[fmt_compact(v) for v in ptdf.sort_values('Jumlah')['Jumlah']],
    )
    cat_fig.update_traces(textposition='outside')
    cat_fig.update_coloraxes(showscale=False)
    apply_chart(cat_fig, height=300)
    cat_fig.update_layout(xaxis_title="", yaxis_title="")

    # ── Gender donut ──────────────────────────────────────────────────────────
    gen_fig = go.Figure(go.Pie(
        labels=["Laki-laki", "Perempuan"], values=[lk, pr], hole=0.6,
        marker=dict(colors=[PALETTE["blue"], "#F48FB1"]),
        textinfo='none', textposition='outside',
        text=[f"Laki-laki<br>{fmt_compact(lk)}", f"Perempuan<br>{fmt_compact(pr)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<extra></extra>",
    ))
    gen_fig.add_annotation(text=f"<b>PT</b><br>Gender", x=0.5, y=0.5,
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
    kd_fig.add_annotation(text=f"<b>PT</b><br>Wilayah", x=0.5, y=0.5,
                          font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(kd_fig, height=300, no_legend=False)

    # ── Age line chart (jumlah) ───────────────────────────────────────────────
    age_m = {
        'ku_1519':'15–19','ku_2024':'20–24','ku_2529':'25–29','ku_3034':'30–34',
        'ku_3539':'35–39','ku_4044':'40–44','ku_4549':'45–49','ku_5054':'50–54',
        'ku_5559':'55–59','ku_6064':'60–64',
    }
    age_vals = [int(data[c].sum()) if c in data.columns else 0 for c in age_m]
    age_fig = go.Figure(go.Scatter(
        x=list(age_m.values()), y=age_vals, mode='lines+markers+text',
        line=dict(color=PALETTE["red"], width=3, shape='spline'),
        marker=dict(size=8, color=PALETTE["red"], line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor='rgba(232,69,69,0.08)',
        text=[fmt_compact(v) for v in age_vals], textposition='top center',
        textfont=dict(size=9, color=PALETTE["red"]),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} jiwa<extra></extra>",
    ))
    apply_chart(age_fig, height=340, no_legend=True)
    age_fig.update_layout(
        xaxis_title="Kelompok Usia", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[-0.5, len(age_m) - 0.5]),
    )

    # ── Sunburst proporsi kategori ────────────────────────────────────────────
    sun_labels = ["Pengangguran"] + list(pt_map.values())
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

    # ── Trend (full width) ────────────────────────────────────────────────────
    ts = trend_filter(df, level, prov, kab)
    cols_pt = [c for c in ['total','kat_mp','kat_mu','kat_pa','kat_bmb'] if c in ts.columns]
    ts_g = ts.groupby('thn')[cols_pt].sum().reset_index()
    trend_fig = go.Figure()
    colors_pt = [PALETTE["red"], PALETTE["navy"], PALETTE["blue"], PALETTE["sky"], PALETTE["gold"]]
    labels_pt = ["Total PT", "Mencari Pekerjaan", "Mempersiapkan Usaha", "Putus Asa", "Diterima Belum Bekerja"]
    for col, clr, lbl in zip(cols_pt, colors_pt, labels_pt):
        trend_fig.add_trace(go.Scatter(
            x=ts_g['thn'], y=ts_g[col], name=lbl, mode='lines+markers',
            line=dict(color=clr, width=3 if col=='total' else 2, shape='spline'),
            marker=dict(size=6, color=clr, line=dict(color='#fff', width=1)),
            hovertemplate=f"<b>{lbl}</b>: %{{y:,.0f}}<extra></extra>",
        ))
    apply_chart(trend_fig, height=340)
    trend_fig.update_layout(
        hovermode='x unified', xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
    )

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Pengangguran Terbuka (PT)", className="page-title"),
            html.P("Analisis kondisi dan karakteristik pengangguran", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card("PT", "Total Pengangguran",    fmt_compact(total), PALETTE["red"],  f"{PALETTE['red']}14"),   md=4),
            dbc.Col(kpi_card("%",  "TPT", f"{tpr}%", PALETTE["gold"], f"{PALETTE['gold']}14"), md=4),
            dbc.Col(kpi_card("MP", "Mencari Pekerjaan",
                             fmt_compact(pt_vals[0]) if pt_vals else "—",
                             PALETTE["navy"], f"{PALETTE['navy']}14"), md=4),
        ], className="g-3 mb-2"),

        section("Distribusi Pengangguran"),
        dbc.Row([
            dbc.Col(chart_card("Kategori Pengangguran", "Berdasarkan alasan menganggur", cat_fig), md=4),
            dbc.Col(chart_card("Perbandingan Gender", "Jumlah PT laki-laki vs perempuan", gen_fig), md=4),
            dbc.Col(chart_card("Perkotaan vs Perdesaan", "Jumlah PT berdasarkan klasifikasi wilayah", kd_fig), md=4),
        ], className="g-3 mb-2"),

        section("Profil Usia & Proporsi"),
        dbc.Row([
            dbc.Col(chart_card("PT per Kelompok Usia", "Distribusi jumlah berdasarkan kelompok umur", age_fig), md=8),
            dbc.Col(chart_card("Proporsi Kategori", "Breakdown pengangguran", sun_fig), md=4),
        ], className="g-3 mb-2"),

        section("Tren Historis Pengangguran"),
        dbc.Row([
            dbc.Col(chart_card("Tren Pengangguran 2018–2025",
                               f"Perkembangan historis — {loc(level,prov,kab)}", trend_fig), md=12),
        ], className="g-3"),
    ])
