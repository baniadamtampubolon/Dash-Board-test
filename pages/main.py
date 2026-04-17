"""Ringkasan Eksekutif page."""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc, loc_name


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: RINGKASAN EKSEKUTIF
# ══════════════════════════════════════════════════════════════════════════════════
def render_main(year, level, prov, kab):
    df_puk = load_data("Database/PUK-2018-2025-ver2.xlsx")
    df_ak  = load_data("Database/AK-2018-2025-ver2.xlsx")
    df_pt  = load_data("Database/PT-2018-2025-ver2.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025-ver3.xlsx")

    data_puk = filter_data(df_puk, year, level, prov, kab)
    data_ak  = filter_data(df_ak,  year, level, prov, kab)
    data_pt  = filter_data(df_pt,  year, level, prov, kab)
    data_pyb = filter_data(df_pyb, year, level, prov, kab)

    v_puk = int(data_puk['total'].sum())
    v_ak  = int(data_ak['total'].sum())
    v_pyb = int(data_pyb['total'].sum())
    v_pt  = int(data_pt['total'].sum())
    tpr   = round(v_pt / v_ak * 100, 2) if v_ak > 0 else 0
    tpak  = round(v_ak / v_puk * 100, 2) if v_puk > 0 else 0

    name = loc_name(level, prov, kab)

    # ── Funnel chart (Sankey-style as treemap) ───────────────────────────────────
    bak = max(0, v_puk - v_ak)
    funnel_fig = go.Figure(go.Funnel(
        y=["Penduduk Usia Kerja", "Angkatan Kerja", "Penduduk Bekerja"],
        x=[v_puk, v_ak, v_pyb],
        textinfo="value+percent initial",
        texttemplate="%{value:,.0f}<br>(%{percentInitial:.1%})",
        marker=dict(color=[PALETTE["navy"], PALETTE["blue"], PALETTE["teal"]]),
        connector=dict(line=dict(width=1, color=PALETTE["border"])),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} jiwa<extra></extra>",
    ))
    apply_chart(funnel_fig, height=320, no_legend=True)
    funnel_fig.update_layout(title=None, margin=dict(l=80, r=20, t=20, b=20))

    # ── Donut: komposisi AK ──────────────────────────────────────────────────────
    donut_fig = px.pie(
        pd.DataFrame({"k": ["Bekerja", "Menganggur"], "v": [v_pyb, v_pt]}),
        values="v", names="k", hole=0.65,
        color_discrete_sequence=[PALETTE["teal"], PALETTE["red"]],
    )
    donut_fig.update_traces(
        textposition="inside", textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
    )
    apply_chart(donut_fig, height=300, no_legend=False)
    donut_fig.add_annotation(
        text=f"TPT<br><b>{tpr}%</b>", x=0.5, y=0.5,
        font=dict(size=14, color=PALETTE["text"]), showarrow=False,
    )

    # ── Bar: Top sektor ──────────────────────────────────────────────────────────
    lapus_map = {
        'lapus_A': 'Pertanian', 'lapus_B': 'Pertambangan', 'lapus_C': 'Industri',
        'lapus_D': 'Listrik', 'lapus_F': 'Konstruksi', 'lapus_G': 'Perdagangan',
        'lapus_H': 'Transportasi', 'lapus_I': 'Akomodasi', 'lapus_J': 'IT/Kominfo',
        'lapus_P': 'Pendidikan', 'lapus_Q': 'Kesehatan', 'lapus_RSTU': 'Jasa Lainnya',
    }
    lv = [(lapus_map[c], int(data_pyb[c].sum())) for c in lapus_map if c in data_pyb.columns]
    ldf = pd.DataFrame(lv, columns=['Sektor', 'Jumlah']).sort_values('Jumlah').tail(8)
    bar_sektor = px.bar(
        ldf, x='Jumlah', y='Sektor', orientation='h',
        color='Jumlah', color_continuous_scale=["#AED6F1", PALETTE["blue"], PALETTE["navy"]],
        text=[fmt_compact(v) for v in ldf['Jumlah']],
    )
    bar_sektor.update_traces(
        textposition='outside', textfont_size=10,
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    )
    bar_sektor.update_coloraxes(showscale=False)
    apply_chart(bar_sektor, height=360)
    bar_sektor.update_layout(xaxis_title="", yaxis_title="")

    # ── Multi-line trend ──────────────────────────────────────────────────────────
    t_puk = trend_filter(df_puk, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_ak  = trend_filter(df_ak,  level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_pyb = trend_filter(df_pyb, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    t_pt  = trend_filter(df_pt,  level, prov, kab).groupby('thn')['total'].sum().reset_index()

    trend_fig = go.Figure()
    for df_t, name_t, color, dash in [
        (t_puk, "PUK", "#AED6F1", "dot"),
        (t_ak,  "AK",  PALETTE["sky"], "dot"),
        (t_pyb, "Bekerja", PALETTE["blue"], "solid"),
        (t_pt,  "Pengangguran", PALETTE["red"], "solid"),
    ]:
        trend_fig.add_trace(go.Scatter(
            x=df_t['thn'], y=df_t['total'], name=name_t, mode='lines+markers',
            line=dict(color=color, width=2.5 if dash=="solid" else 1.8, dash=dash, shape='spline'),
            marker=dict(size=6, color=color),
            fill='tozeroy' if name_t == "Bekerja" else None,
            fillcolor='rgba(19,83,160,0.06)' if name_t == "Bekerja" else None,
            hovertemplate=f"<b>{name_t}</b>: %{{y:,.0f}}<extra></extra>",
        ))
    apply_chart(trend_fig, height=380)
    trend_fig.update_layout(
        hovermode='x unified',
        xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
    )

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"📍 {loc(level,prov,kab)}  ·  📅 {year}", className="page-badge"),
            html.H1("Ringkasan Eksekutif Ketenagakerjaan", className="page-title"),
            html.P("Gambaran menyeluruh kondisi ketenagakerjaan nasional", className="page-subtitle"),
        ]),

        dbc.Row([
            dbc.Col(kpi_card("👥", "Penduduk Usia Kerja", f"{fmt_compact(v_puk)}",
                             PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=3),
            dbc.Col(kpi_card("💼", "Angkatan Kerja", f"{fmt_compact(v_ak)}  ({tpak:.1f}%)",
                             PALETTE["blue"], f"{PALETTE['blue']}14"), md=3),
            dbc.Col(kpi_card("✅", "Penduduk Bekerja", fmt_compact(v_pyb),
                             PALETTE["teal"], f"{PALETTE['teal']}14"), md=3),
            dbc.Col(kpi_card("❌", "Pengangguran Terbuka", f"{fmt_compact(v_pt)}  (TPT {tpr}%)",
                             PALETTE["red"], f"{PALETTE['red']}14"), md=3),
        ], className="g-3 mb-2"),

        section("Struktur Ketenagakerjaan"),
        dbc.Row([
            dbc.Col(chart_card("Alur Partisipasi Tenaga Kerja",
                               "Dari total penduduk usia kerja hingga yang bekerja",
                               funnel_fig), md=8),
            dbc.Col(chart_card("Komposisi Angkatan Kerja",
                               f"Tingkat Pengangguran Terbuka (TPT): {tpr}%",
                               donut_fig), md=4),
        ], className="g-3 mb-2"),

        section("Penyerapan & Distribusi"),
        dbc.Row([
            dbc.Col(chart_card("Top Sektor Penyerap Tenaga Kerja",
                               "Berdasarkan jumlah penduduk bekerja",
                               bar_sektor), md=6),
            dbc.Col(chart_card(f"Tren Ketenagakerjaan — {loc(level,prov,kab)}",
                               "Data 2018–2025",
                               trend_fig), md=6),
        ], className="g-3 mb-2"),

        html.Div(
            f"Dashboard Ketenagakerjaan Nasional 2018–2025  ·  Kementerian Ketenagakerjaan RI",
            style={"textAlign": "center", "color": PALETTE["muted"],
                   "fontSize": "12px", "marginTop": "40px"},
        ),
    ])

