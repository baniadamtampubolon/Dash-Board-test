"""Ringkasan Eksekutif page."""

from dash import dcc, html
from dash_iconify import DashIconify
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

    # ── Icicle Chart (Struktur Ketenagakerjaan) ──────────────────────────────────
    v_sklh = int(data_puk['keg_sklh'].sum()) if 'keg_sklh' in data_puk.columns else 0
    v_mrt = int(data_puk['keg_mrt'].sum()) if 'keg_mrt' in data_puk.columns else 0
    v_lain = int(data_puk['keg_lain'].sum()) if 'keg_lain' in data_puk.columns else 0

    val_ak = v_pyb + v_pt
    val_bak = v_sklh + v_mrt + v_lain
    # Jika data BAK tidak lengkap, fallback ke nilai total BAK:
    if val_bak == 0:
        val_bak = max(0, v_puk - val_ak)
        v_lain = val_bak
    
    val_puk = val_ak + val_bak

    # ── Custom HTML Icicle Chart (Struktur Ketenagakerjaan) ────────────────────
    custom_icicle = html.Div(className="icicle-container", children=[
        # Baris 1: PUK
        html.Div(className="icicle-row", children=[
            html.Div(className="icicle-box", style={"backgroundColor": "#0097A7", "flex": 1}, children=[
                html.Div("PUK", className="icicle-title"),
                html.Div(fmt_compact(val_puk), className="icicle-value")
            ])
        ]),
        # Baris 2: AK & BAK
        html.Div(className="icicle-row", children=[
            html.Div(className="icicle-box", style={"backgroundColor": "#4F86F7", "flex": val_ak}, children=[
                html.Div("AK", className="icicle-title"),
                html.Div(fmt_compact(val_ak), className="icicle-value"),
                html.Div(f"({val_ak/val_puk:.1%})", className="icicle-percent") if val_puk else None
            ]),
            html.Div(className="icicle-box", style={"backgroundColor": "#F97316", "flex": val_bak}, children=[
                html.Div("BAK", className="icicle-title"),
                html.Div(fmt_compact(val_bak), className="icicle-value"),
                html.Div(f"({val_bak/val_puk:.1%})", className="icicle-percent") if val_puk else None
            ])
        ]),
        # Baris 3: Rincian AK & BAK
        html.Div(className="icicle-row", children=[
            html.Div(className="icicle-subrow", style={"flex": val_ak}, children=[
                html.Div(className="icicle-box", style={"backgroundColor": "#10B981", "flex": v_pyb}, children=[
                    html.Div("PYB", className="icicle-title"),
                    html.Div(fmt_compact(v_pyb), className="icicle-value")
                ]),
                html.Div(className="icicle-box", style={"backgroundColor": "#EF4444", "flex": v_pt}, children=[
                    html.Div("PT", className="icicle-title"),
                    html.Div(fmt_compact(v_pt), className="icicle-value")
                ]),
            ]),
            html.Div(className="icicle-subrow", style={"flex": val_bak}, children=[
                html.Div(className="icicle-box", style={"backgroundColor": "#9CA3AF", "flex": v_sklh}, children=[
                    html.Div("Sekolah", className="icicle-title"),
                    html.Div(fmt_compact(v_sklh), className="icicle-value")
                ]),
                html.Div(className="icicle-box", style={"backgroundColor": "#9CA3AF", "flex": v_mrt}, children=[
                    html.Div("MRT", className="icicle-title"),
                    html.Div(fmt_compact(v_mrt), className="icicle-value")
                ]),
                html.Div(className="icicle-box", style={"backgroundColor": "#9CA3AF", "flex": v_lain}, children=[
                    html.Div("Lainnya", className="icicle-title"),
                    html.Div(fmt_compact(v_lain), className="icicle-value")
                ]),
            ])
        ])
    ])

    # ── Donut: komposisi AK ──────────────────────────────────────────────────────
    donut_fig = go.Figure(go.Pie(
        labels=["Bekerja", "Pengangguran"], values=[v_pyb, v_pt], hole=0.65,
        marker=dict(colors=[PALETTE["teal"], PALETTE["red"]]),
        textinfo='none', textposition='outside',
        text=[f"Bekerja<br>{fmt_compact(v_pyb)}", f"Pengangguran<br>{fmt_compact(v_pt)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<extra></extra>",
    ))
    donut_fig.add_annotation(
        text=f"TPT<br><b>{tpr}%</b>", x=0.5, y=0.5,
        font=dict(size=14, color=PALETTE["text"]), showarrow=False,
    )
    apply_chart(donut_fig, height=360, no_legend=True)

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

    # ── Historical Table ─────────────────────────────────────────────────────────
    years = sorted(df_puk['thn'].unique())
    t_puk_full = trend_filter(df_puk, level, prov, kab).groupby('thn').sum(numeric_only=True).reset_index()
    
    def get_yearly_dict(df, val_col='total'):
        if df.empty or val_col not in df.columns: return {y: 0 for y in years}
        return dict(zip(df['thn'], df[val_col]))

    y_puk = get_yearly_dict(t_puk_full, 'total')
    y_ak  = get_yearly_dict(t_ak, 'total')
    y_pyb = get_yearly_dict(t_pyb, 'total')
    y_pt  = get_yearly_dict(t_pt, 'total')
    y_sklh = get_yearly_dict(t_puk_full, 'keg_sklh')
    y_mrt  = get_yearly_dict(t_puk_full, 'keg_mrt')
    y_lain = get_yearly_dict(t_puk_full, 'keg_lain')
    
    y_bak = {y: max(0, y_puk.get(y,0) - y_ak.get(y,0)) for y in years}
    y_tpak = {y: (y_ak.get(y,0) / y_puk.get(y,0) * 100) if y_puk.get(y,0) > 0 else 0 for y in years}
    y_tpt  = {y: (y_pt.get(y,0) / y_ak.get(y,0) * 100) if y_ak.get(y,0) > 0 else 0 for y in years}
    y_epr  = {y: (y_pyb.get(y,0) / y_puk.get(y,0) * 100) if y_puk.get(y,0) > 0 else 0 for y in years}

    def fmt_n(v): return f"{v:,.0f}" if v > 0 else "-"
    def fmt_p(v): return f"{v:.1f}%" if v > 0 else "-"

    table_header = [
        html.Thead([
            html.Tr([
                html.Th("KEGIATAN", rowSpan=2, className="align-middle text-center", style={"width": "22%"}),
                html.Th("TAHUN", colSpan=len(years), className="text-center")
            ]),
            html.Tr([html.Th(str(y), className="text-center") for y in years])
        ], className="hist-thead")
    ]
    
    row_defs = [
        ("PENDUDUK USIA KERJA", y_puk, fmt_n, "hist-parent"),
        ("ANGKATAN KERJA", y_ak, fmt_n, "hist-parent"),
        ("BEKERJA", y_pyb, fmt_n, "hist-child"),
        ("PENGANGGUR", y_pt, fmt_n, "hist-child"),
        ("BUKAN ANGKATAN KERJA", y_bak, fmt_n, "hist-parent"),
        ("SEKOLAH", y_sklh, fmt_n, "hist-child"),
        ("MENGURUS RUMAH TANGGA", y_mrt, fmt_n, "hist-child"),
        ("LAINNYA", y_lain, fmt_n, "hist-child"),
        ("TPAK (%)", y_tpak, fmt_p, "hist-ratio"),
        ("TPT (%)", y_tpt, fmt_p, "hist-ratio"),
        ("EPR (%)", y_epr, fmt_p, "hist-ratio"),
    ]
    
    table_body = []
    for label, ddict, ffunc, cls in row_defs:
        tds = [html.Td(label, className=f"hist-label {cls}")]
        for y in years:
            tds.append(html.Td(ffunc(ddict.get(y, 0)), className=f"hist-val {cls} text-end"))
        table_body.append(html.Tr(tds))
        
    hist_table = dbc.Table(
        table_header + [html.Tbody(table_body)],
        bordered=True, hover=True, responsive=True,
        className="historical-table"
    )

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Ringkasan Eksekutif Ketenagakerjaan", className="page-title"),
            html.P("Gambaran menyeluruh kondisi ketenagakerjaan nasional", className="page-subtitle"),
        ]),

        dbc.Row([
            dbc.Col(kpi_card(DashIconify(icon="fa-solid:users", width=24), "Penduduk Usia Kerja", f"{fmt_compact(v_puk)}",
                             PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=3),
            dbc.Col(kpi_card(DashIconify(icon="mdi:briefcase", width=24), "Angkatan Kerja", f"{fmt_compact(v_ak)}  ({tpak:.1f}%)",
                             PALETTE["blue"], f"{PALETTE['blue']}14"), md=3),
            dbc.Col(kpi_card(DashIconify(icon="la:industry-solid", width=26), "Penduduk Bekerja", fmt_compact(v_pyb),
                             PALETTE["teal"], f"{PALETTE['teal']}14"), md=3),
            dbc.Col(kpi_card(DashIconify(icon="fa-solid:frown-open", width=24), "Pengangguran Terbuka", f"{fmt_compact(v_pt)}  (TPT {tpr}%)",
                             PALETTE["red"], f"{PALETTE['red']}14"), md=3),
        ], className="g-3 mb-2"),

        section("Struktur Ketenagakerjaan"),
        dbc.Row([
            dbc.Col(html.Div(className="chart-card", children=[
                html.Div("Alur Partisipasi Tenaga Kerja", className="chart-card-title"),
                html.Div("Dari total penduduk usia kerja hingga yang bekerja", className="chart-card-sub"),
                custom_icicle
            ]), md=12),
        ], className="g-3 mb-2"),

        section("Penyerapan & Komposisi"),
        dbc.Row([
            dbc.Col(chart_card("Top Sektor Penyerap Tenaga Kerja",
                               "Berdasarkan jumlah penduduk bekerja",
                               bar_sektor), md=8),
            dbc.Col(chart_card("Komposisi Angkatan Kerja",
                               f"Tingkat Pengangguran Terbuka (TPT): {tpr}%",
                               donut_fig), md=4),
        ], className="g-3 mb-2"),

        section("Dinamika & Tren"),
        dbc.Row([
            dbc.Col(chart_card(f"Tren Ketenagakerjaan — {loc(level,prov,kab)}",
                               "Data 2018–2025",
                               trend_fig), md=12),
        ], className="g-3 mb-2"),

        section("Rekapitulasi Data Historis"),
        dbc.Row([
            dbc.Col(html.Div(className="chart-card", style={"padding": "16px 20px"}, children=[
                hist_table
            ]), md=12),
        ], className="g-3 mb-4"),

        html.Div(
            f"Dashboard Ketenagakerjaan Nasional 2018–2025  ·  Kementerian Ketenagakerjaan RI",
            style={"textAlign": "center", "color": PALETTE["muted"],
                   "fontSize": "12px", "marginTop": "40px"},
        ),
    ])

