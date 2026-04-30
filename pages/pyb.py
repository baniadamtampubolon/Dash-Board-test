"""Penduduk yang Bekerja (PYB) page."""

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
#  PAGE: PYB
# ══════════════════════════════════════════════════════════════════════════════════
def render_pyb(year, level, prov, kab):
    df = load_data("Database/PYB-2018-2025-ver4.xlsx")
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
    gen_fig.add_annotation(text=f"<b>PYB</b><br>Gender", x=0.5, y=0.5,
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
    kd_fig.add_annotation(text=f"<b>PYB</b><br>Wilayah", x=0.5, y=0.5,
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
        line=dict(color=PALETTE["teal"], width=3, shape='spline'),
        marker=dict(size=8, color=PALETTE["teal"], line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor='rgba(13,158,138,0.08)',
        text=[fmt_compact(v) for v in age_vals], textposition='top center',
        textfont=dict(size=9, color=PALETTE["teal"]),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} jiwa<extra></extra>",
    ))
    apply_chart(age_fig, height=340, no_legend=True)
    age_fig.update_layout(
        xaxis_title="Kelompok Usia", yaxis_title="Jumlah Jiwa",
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[-0.5, len(age_m) - 0.5]),
    )

    # ── Sektor treemap ────────────────────────────────────────────────────────
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

    # ── Status pekerjaan donut ────────────────────────────────────────────────
    sta_map = {
        'sta_1':'Berusaha Sendiri','sta_2':'Buruh Tdk Tetap','sta_3':'Buruh Tetap',
        'sta_4':'Karyawan','sta_5':'Bebas (Tani)','sta_6':'Bebas (Non-Tani)','sta_7':'Keluarga',
    }
    sv = [int(data[c].sum()) if c in data.columns else 0 for c in sta_map]
    sta_fig = go.Figure(go.Pie(
        labels=list(sta_map.values()), values=sv, hole=0.6,
        marker=dict(colors=[PALETTE["blue"], PALETTE["sky"], PALETTE["teal"], PALETTE["indigo"], PALETTE["gold"], PALETTE["red"], PALETTE["muted"]]),
        textinfo='none', textposition='outside',
        text=[f"{l}<br>{fmt_compact(v)}" for l, v in zip(sta_map.values(), sv)],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<extra></extra>",
    ))
    sta_fig.add_annotation(text="<b>Status<br>Pekerjaan</b>", x=0.5, y=0.5,
                           font=dict(size=12, color=PALETTE["text"]), showarrow=False)
    apply_chart(sta_fig, height=360, no_legend=True)
    sta_fig.update_layout(margin=dict(l=60, r=60, t=20, b=20))

    # ── Formal vs Informal ───────────────────────────────────────────────────
    v_formal = int(data['sta_3'].sum() + data['sta_4'].sum()) if ('sta_3' in data.columns and 'sta_4' in data.columns) else 0
    v_informal = max(0, total - v_formal)
    formal_fig = go.Figure(go.Pie(
        labels=['Formal', 'Informal'], values=[v_formal, v_informal], hole=0.6,
        marker=dict(colors=[PALETTE["teal"], PALETTE["gold"]]),
        textinfo='none', textposition='outside',
        text=[f"Formal<br>{fmt_compact(v_formal)}", f"Informal<br>{fmt_compact(v_informal)}"],
        texttemplate="%{text}",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} jiwa<br>%{percent}<extra></extra>",
    ))
    formal_fig.add_annotation(text="<b>Pekerja</b>", x=0.5, y=0.5,
                           font=dict(size=14, color=PALETTE["text"]), showarrow=False)
    apply_chart(formal_fig, height=360, no_legend=True)
    formal_fig.update_layout(margin=dict(l=60, r=60, t=20, b=20))

    # ── Jabatan horizontal ────────────────────────────────────────────────────
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

    # ── Jam kerja ─────────────────────────────────────────────────────────────
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

    # ── Trend (full width) ────────────────────────────────────────────────────
    t = trend_filter(df, level, prov, kab).groupby('thn')['total'].sum().reset_index()
    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t['total'], mode='lines+markers+text',
        line=dict(color=PALETTE["teal"], width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(13,158,138,0.08)',
        marker=dict(size=8, color=PALETTE["teal"], line=dict(color='#fff', width=1.5)),
        text=[fmt_compact(v) for v in t['total']], textposition='top center',
        textfont=dict(size=10, color=PALETTE["teal"]),
        hovertemplate="Tahun %{x}: %{y:,.0f}<extra></extra>",
    ))
    apply_chart(trend_fig, height=340)
    trend_fig.update_layout(
        xaxis_title="Tahun", yaxis_title="Jumlah Jiwa",
        hovermode='x unified',
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[int(t['thn'].min()) - 0.4, int(t['thn'].max()) + 0.4]) if not t.empty else {},
    )

    map_section, top_bottom_section, rank_section = build_geomap_layout(df, year, level, prov, 'PYB')

    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1("Penduduk yang Bekerja (PYB)", className="page-title"),
            html.P("Analisis mendalam profil pekerjaan, sektor, dan jabatan", className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card(DashIconify(icon="la:industry-solid", width=26), "Total Penduduk Bekerja", fmt_compact(total),
                             PALETTE["teal"], f"{PALETTE['teal']}14"), md=4),
            dbc.Col(kpi_card(DashIconify(icon="mdi:factory", width=24), "Sektor Terbesar",
                             ldf.sort_values('Jumlah').iloc[-1]['Sektor'] if not ldf.empty else "—",
                             PALETTE["blue"], f"{PALETTE['blue']}14"), md=4),
            dbc.Col(kpi_card(DashIconify(icon="lucide:clock-8", width=24), "Pekerja >48 jam/minggu",
                             fmt_compact(jmv[-1]) if jmv else "—",
                             PALETTE["gold"], f"{PALETTE['gold']}14"), md=4),
        ], className="g-3 mb-2"),

        map_section,
        top_bottom_section,

        section("Profil Demografis"),
        dbc.Row([
            dbc.Col(chart_card("Perbandingan Gender", "Jumlah PYB laki-laki vs perempuan", gen_fig), md=4),
            dbc.Col(chart_card("Perkotaan vs Perdesaan", "Jumlah PYB berdasarkan klasifikasi wilayah", kd_fig), md=4),
            dbc.Col(chart_card("PYB per Kelompok Usia", "Distribusi jumlah berdasarkan umur", age_fig), md=4),
        ], className="g-3 mb-2"),

        section("Distribusi Sektor & Status"),
        dbc.Row([
            dbc.Col(chart_card("Lapangan Usaha (Treemap)", "Proporsi berdasarkan sektor pekerjaan", sektor_tree), md=12),
        ], className="g-3 mb-2"),
        dbc.Row([
            dbc.Col(chart_card("Status Pekerjaan Utama", "Berdasarkan 7 klasifikasi BPS", sta_fig), md=6),
            dbc.Col(chart_card("Pekerja Formal vs Informal", "Formal: Buruh Tetap + Karyawan", formal_fig), md=6),
        ], className="g-3 mb-2"),

        section("Jabatan & Jam Kerja"),
        dbc.Row([
            dbc.Col(chart_card("Distribusi Jabatan / Jenis Pekerjaan", "", jab_fig), md=6),
            dbc.Col(chart_card("Jam Kerja per Minggu", "Distribusi durasi kerja per minggu", jam_fig), md=6),
        ], className="g-3 mb-2"),

        section("Tren Historis Penduduk Bekerja"),
        dbc.Row([
            dbc.Col(chart_card("Tren PYB 2018–2025",
                               f"Perkembangan historis — {loc(level,prov,kab)}", trend_fig), md=12),
        ], className="g-3"),
        
        rank_section
    ])
