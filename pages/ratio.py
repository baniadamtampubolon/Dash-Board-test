"""Ratio indicator pages: TPAK, TPT, EPR with shared builder."""

from dash import dcc, html
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from design import PALETTE, SEQ, apply_chart
from data_loader import load_data, filter_data, trend_filter
from components import kpi_card, chart_card, section, fmt_compact, loc


# ══════════════════════════════════════════════════════════════════════════════════
#  HELPER: Reusable ratio page builder
# ══════════════════════════════════════════════════════════════════════════════════
def _ratio_val(data, col):
    """Safely get a single ratio value from filtered data."""
    if data.empty or col not in data.columns:
        return 0.0
    return round(float(data[col].iloc[0]), 2) if len(data) == 1 else round(float(data[col].mean()), 2)


def _build_ratio_page(df, data, year, level, prov, kab, *,
                      ratio_col, title, subtitle, icon, accent, fill_rgba,
                      color_scale, label_short):
    """Build a full ratio dashboard mirroring the AK/PT page composition."""

    v_total  = _ratio_val(data, ratio_col)
    v_lk     = _ratio_val(data, 'jk_lk')
    v_pr     = _ratio_val(data, 'jk_pr')
    v_kota   = _ratio_val(data, 'kls_kota')
    v_desa   = _ratio_val(data, 'kls_desa')

    # ── Age‑group LINE chart ─────────────────────────────────────────────────
    age_m = {
        'ku_1519':'15–19', 'ku_2024':'20–24', 'ku_2529':'25–29',
        'ku_3034':'30–34', 'ku_3539':'35–39', 'ku_4044':'40–44',
        'ku_4549':'45–49', 'ku_5054':'50–54', 'ku_5559':'55–59',
        'ku_6064':'60–64', 'ku_65+':'65+',
    }
    age_vals = [_ratio_val(data, c) for c in age_m]
    age_fig = go.Figure(go.Scatter(
        x=list(age_m.values()), y=age_vals, mode='lines+markers+text',
        line=dict(color=accent, width=3, shape='spline'),
        marker=dict(size=8, color=accent, line=dict(color='#fff', width=1.5)),
        fill='tozeroy', fillcolor=fill_rgba,
        text=[f"{v:.1f}%" for v in age_vals], textposition='top center',
        textfont=dict(size=9, color=accent),
        hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
    ))
    apply_chart(age_fig, height=340, no_legend=True)
    age_fig.update_layout(
        xaxis_title="Kelompok Usia", yaxis_title=f"{label_short} (%)",
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[-0.5, len(age_m) - 0.5]),
    )

    # ── Gender BAR chart ─────────────────────────────────────────────────────
    gen_df = pd.DataFrame({'Gender': ["Laki-laki", "Perempuan"], 'Nilai': [v_lk, v_pr]})
    gen_fig = px.bar(
        gen_df.sort_values('Nilai'), x='Nilai', y='Gender', orientation='h',
        color='Gender', color_discrete_map={"Laki-laki": PALETTE["blue"], "Perempuan": "#F48FB1"},
        text=[f"{v:.2f}%" for v in gen_df.sort_values('Nilai')['Nilai']],
    )
    gen_fig.update_traces(textposition='outside', hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>")
    gen_fig.update_coloraxes(showscale=False)
    apply_chart(gen_fig, height=300, no_legend=True)
    gen_fig.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=10, r=70, t=10, b=10))

    # ── Trend line ───────────────────────────────────────────────────────────
    t = trend_filter(df, level, prov, kab).groupby('thn')[ratio_col].mean().reset_index()
    trend_fig = go.Figure(go.Scatter(
        x=t['thn'], y=t[ratio_col], mode='lines+markers+text',
        line=dict(color=accent, width=3, shape='spline'),
        fill='tozeroy', fillcolor=fill_rgba,
        marker=dict(size=8, color=accent, line=dict(color='#fff', width=1.5)),
        text=[f"{v:.1f}%" for v in t[ratio_col]], textposition='top center',
        textfont=dict(size=10, color=accent),
        hovertemplate=f"Tahun %{{x}}: %{{y:.2f}}%<extra></extra>",
    ))
    apply_chart(trend_fig, height=340)
    trend_fig.update_layout(
        xaxis_title="Tahun", yaxis_title=f"{label_short} (%)",
        hovermode='x unified',
        margin=dict(l=48, r=48, t=48, b=40),
        xaxis=dict(range=[int(t['thn'].min()) - 0.4, int(t['thn'].max()) + 0.4]) if not t.empty else {},
    )

    # ── Education bar ────────────────────────────────────────────────────────
    edu_map = {
        'pd_sd':'SD', 'pd_smp':'SMP', 'pd_smau':'SMA/MA',
        'pd_smak':'SMK', 'pd_dipl':'Diploma', 'pd_univ':'Universitas',
    }
    edu_vals = [_ratio_val(data, c) for c in edu_map]
    edu_fig = px.bar(
        pd.DataFrame({'Pendidikan': list(edu_map.values()), label_short: edu_vals}),
        x='Pendidikan', y=label_short, color=label_short,
        color_continuous_scale=color_scale,
        text=[f"{v:.1f}%" for v in edu_vals],
    )
    edu_fig.update_traces(textposition='outside')
    edu_fig.update_coloraxes(showscale=False)
    apply_chart(edu_fig, height=300)
    edu_fig.update_layout(xaxis_title="", yaxis_title=f"{label_short} (%)", margin=dict(l=10, r=70, t=10, b=20))

    # ── Kota vs Desa BAR chart ───────────────────────────────────────────────
    kd_df = pd.DataFrame({'Wilayah': ["Perkotaan", "Perdesaan"], 'Nilai': [v_kota, v_desa]})
    kd_fig = px.bar(
        kd_df.sort_values('Nilai'), x='Nilai', y='Wilayah', orientation='h',
        color='Wilayah', color_discrete_map={"Perkotaan": PALETTE["sky"], "Perdesaan": PALETTE["gold"]},
        text=[f"{v:.2f}%" for v in kd_df.sort_values('Nilai')['Nilai']],
    )
    kd_fig.update_traces(textposition='outside', hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>")
    kd_fig.update_coloraxes(showscale=False)
    apply_chart(kd_fig, height=300, no_legend=True)
    kd_fig.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=10, r=70, t=10, b=10))

    # ── Assemble page ────────────────────────────────────────────────────────
    return html.Div([
        html.Div(className="page-header", children=[
            html.Span(f"{loc(level,prov,kab)}  ·  {year}", className="page-badge"),
            html.H1(title, className="page-title"),
            html.P(subtitle, className="page-subtitle"),
        ]),
        dbc.Row([
            dbc.Col(kpi_card(icon, label_short, f"{v_total:.2f}%",
                             accent, f"{accent}14"), md=4),
            dbc.Col(kpi_card(DashIconify(icon="ion:male", width=24), f"{label_short} Laki-laki", f"{v_lk:.2f}%",
                             PALETTE["indigo"], f"{PALETTE['indigo']}14"), md=4),
            dbc.Col(kpi_card(DashIconify(icon="ion:female", width=24), f"{label_short} Perempuan", f"{v_pr:.2f}%",
                             "#E91E8C", "#E91E8C14"), md=4),
        ], className="g-3 mb-2"),

        section("Profil Demografis"),
        dbc.Row([
            dbc.Col(chart_card(f"{label_short} per Kelompok Usia",
                               "Distribusi rasio berdasarkan kelompok umur", age_fig), md=8),
            dbc.Col(chart_card("Perbandingan Gender",
                               f"{label_short} laki-laki vs perempuan", gen_fig), md=4),
        ], className="g-3 mb-2"),

        section("Pendidikan & Wilayah"),
        dbc.Row([
            dbc.Col(chart_card(f"{label_short} per Tingkat Pendidikan", "", edu_fig), md=8),
            dbc.Col(chart_card("Perkotaan vs Perdesaan",
                               f"Rasio {label_short} berdasarkan klasifikasi wilayah", kd_fig), md=4),
        ], className="g-3 mb-2"),

        section(f"Tren Historis {label_short}"),
        dbc.Row([
            dbc.Col(chart_card(f"Tren {label_short} 2018–2025",
                               f"Perkembangan historis — {loc(level,prov,kab)}",
                               trend_fig), md=12),
        ], className="g-3"),
    ])


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: TPAK  (rasio dari AK → komposisi mirip render_ak)
# ══════════════════════════════════════════════════════════════════════════════════
def render_tpak(year, level, prov, kab):
    df   = load_data("Database/TPAK-2018-2025-ver2.xlsx")
    data = filter_data(df, year, level, prov, kab)
    return _build_ratio_page(
        df, data, year, level, prov, kab,
        ratio_col='TPAK',
        title="Tingkat Partisipasi Angkatan Kerja (TPAK)",
        subtitle="Persentase angkatan kerja terhadap penduduk usia kerja (AK / PUK)",
        icon=DashIconify(icon="fa-solid:percent", width=20), accent=PALETTE["blue"],
        fill_rgba="rgba(19,83,160,0.08)",
        color_scale=["#DBEAFE", PALETTE["blue"]],
        label_short="TPAK",
    )


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: TPT Rasio  (rasio dari PT → komposisi mirip render_pt)
# ══════════════════════════════════════════════════════════════════════════════════
def render_tpt_rasio(year, level, prov, kab):
    df   = load_data("Database/TPT-2018-2025-ver2.xlsx")
    data = filter_data(df, year, level, prov, kab)
    return _build_ratio_page(
        df, data, year, level, prov, kab,
        ratio_col='TPT',
        title="Tingkat Pengangguran Terbuka (TPT)",
        subtitle="Persentase pengangguran terhadap total angkatan kerja (PT / AK)",
        icon=DashIconify(icon="fa-solid:percent", width=20), accent=PALETTE["red"],
        fill_rgba="rgba(232,69,69,0.08)",
        color_scale=["#FEEBC8", PALETTE["red"]],
        label_short="TPT",
    )


# ══════════════════════════════════════════════════════════════════════════════════
#  PAGE: EPR  (rasio dari PYB → komposisi mirip render_pyb)
# ══════════════════════════════════════════════════════════════════════════════════
def render_epr(year, level, prov, kab):
    df   = load_data("Database/EPR-2018-2025-ver2.xlsx")
    data = filter_data(df, year, level, prov, kab)
    return _build_ratio_page(
        df, data, year, level, prov, kab,
        ratio_col='EPR',
        title="Employment to Population Ratio (EPR)",
        subtitle="Persentase penduduk bekerja terhadap penduduk usia kerja (PYB / PUK)",
        icon=DashIconify(icon="fa-solid:percent", width=20), accent=PALETTE["teal"],
        fill_rgba="rgba(13,158,138,0.08)",
        color_scale=["#E6F4F1", PALETTE["teal"]],
        label_short="EPR",
    )


