"""
Design tokens, palette, chart configuration, and CSS for the dashboard.
"""

# ─── Design Tokens ───────────────────────────────────────────────────────────────
PALETTE = {
    "navy":    "#0A1628",
    "blue":    "#1353A0",
    "sky":     "#2E86DE",
    "teal":    "#0D9E8A",
    "indigo":  "#3D4FB5",
    "gold":    "#F5A623",
    "red":     "#E84545",
    "bg":      "#F4F6FB",
    "surface": "#FFFFFF",
    "border":  "#E2E8F3",
    "muted":   "#7A8BAA",
    "text":    "#0D1B2E",
    "text2":   "#4A5568",
}

SEQ = [PALETTE["navy"], PALETTE["blue"], PALETTE["sky"], PALETTE["teal"],
       "#64B5F6", "#90CAF9", "#BBDEFB"]

CHART = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=PALETTE["text"], size=12),
    margin=dict(l=12, r=12, t=48, b=12),
    hoverlabel=dict(bgcolor=PALETTE["surface"], font_size=12, bordercolor=PALETTE["border"]),
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.28,
        xanchor="center", x=0.5,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11),
    ),
    xaxis=dict(gridcolor="#EEF1F8", showline=False, tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#EEF1F8", showline=False, tickfont=dict(size=11)),
    barcornerradius=6,
)


def apply_chart(fig, height=None, no_legend=False):
    kw = dict(CHART)
    if height:
        kw["height"] = height
    if no_legend:
        kw["showlegend"] = False
    fig.update_layout(**kw)
    return fig


# ─── Static data for filters (always PUK as geo reference) ───────────────────────
try:
    _GEO = load_data("Database/PUK-2018-2025-ver2.xlsx")
    _YEARS = sorted(_GEO['thn'].unique(), reverse=True)
    _PROV_DF = (
        _GEO[_GEO['nm_prov'] != 'NASIONAL'][['kd_prov', 'nm_prov']]
        .drop_duplicates().sort_values('kd_prov')
    )
    _PROV_LIST = _PROV_DF['nm_prov'].tolist()
    DATA_AVAILABLE = True
except Exception:
    _YEARS = list(range(2018, 2026))
    _PROV_LIST = []
    DATA_AVAILABLE = False


# ─── CSS ─────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = f"""
* {{ box-sizing: border-box; }}
body {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: {PALETTE["bg"]};
    color: {PALETTE["text"]};
    margin: 0;
}}

/* ── Sidebar ── */
.sidebar {{
    width: 260px;
    min-height: 100vh;
    max-height: 100vh;
    overflow-y: auto;
    background: linear-gradient(160deg, {PALETTE["navy"]} 0%, #102040 100%);
    position: fixed;
    left: 0; top: 0;
    display: flex;
    flex-direction: column;
    padding: 0;
    z-index: 100;
    box-shadow: 4px 0 24px rgba(0,0,0,0.18);
}}
.sidebar-logo {{
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.sidebar-logo h2 {{
    color: #fff;
    font-size: 15px;
    font-weight: 700;
    margin: 10px 0 2px;
    letter-spacing: -0.2px;
    line-height: 1.3;
}}
.sidebar-logo p {{
    color: rgba(255,255,255,0.45);
    font-size: 11px;
    margin: 0;
}}
.sidebar-section {{
    padding: 20px 20px 0;
}}
.sidebar-label {{
    color: rgba(255,255,255,0.35);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.sidebar-nav {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-bottom: 20px;
}}
.nav-btn {{
    background: none;
    border: none;
    color: rgba(255,255,255,0.6);
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    text-align: left;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.18s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.nav-btn:hover {{ background: rgba(255,255,255,0.08); color: #fff; }}
.nav-btn.active {{
    background: rgba(46,134,222,0.25);
    color: #fff;
    font-weight: 600;
    border-left: 3px solid {PALETTE["sky"]};
}}
.sidebar-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 4px 20px 16px;
}}
.filter-label {{
    color: rgba(255,255,255,0.5);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-bottom: 6px;
    display: block;
}}
.Select-control, .Select-menu-outer {{
    border-radius: 8px !important;
}}

/* ── Main content ── */
.main-content {{
    margin-left: 260px;
    padding: 32px 32px 48px;
    min-height: 100vh;
}}

/* ── Page Header ── */
.page-header {{
    margin-bottom: 28px;
}}
.page-title {{
    font-size: 26px;
    font-weight: 800;
    color: {PALETTE["text"]};
    margin: 0 0 4px;
    letter-spacing: -0.5px;
}}
.page-subtitle {{
    font-size: 13.5px;
    color: {PALETTE["muted"]};
    margin: 0;
    font-weight: 400;
}}
.page-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {PALETTE["blue"]}18;
    color: {PALETTE["blue"]};
    border: 1px solid {PALETTE["blue"]}30;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}}

/* ── KPI Cards ── */
.kpi-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 16px;
    padding: 22px 20px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, {PALETTE["blue"]});
    border-radius: 16px 16px 0 0;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(19, 83, 160, 0.1);
}}
.kpi-icon {{
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    margin-bottom: 14px;
    background: var(--icon-bg, {PALETTE["blue"]}12);
}}
.kpi-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: {PALETTE["muted"]};
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: {PALETTE["text"]};
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -1px;
    line-height: 1;
}}
.kpi-delta {{
    font-size: 12px;
    color: {PALETTE["teal"]};
    margin-top: 6px;
    font-weight: 500;
}}

/* ── Chart Card ── */
.chart-card {{
    background: {PALETTE["surface"]};
    border: 1px solid {PALETTE["border"]};
    border-radius: 16px;
    padding: 4px 4px 0;
    height: 100%;
}}
.chart-card-title {{
    font-size: 13.5px;
    font-weight: 700;
    color: {PALETTE["text"]};
    padding: 18px 20px 0;
    letter-spacing: -0.2px;
}}
.chart-card-sub {{
    font-size: 11.5px;
    color: {PALETTE["muted"]};
    padding: 2px 20px 0;
    font-weight: 400;
}}

/* ── Section ── */
.section-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {PALETTE["muted"]};
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {PALETTE["border"]};
}}

/* ── Dash dropdown/select overrides ── */
.dash-dropdown .Select-control {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: white !important;
}}
.dash-dropdown .Select-value-label {{ color: rgba(255,255,255,0.85) !important; font-size: 12px; }}
.dash-dropdown .Select-placeholder {{ color: rgba(255,255,255,0.4) !important; font-size: 12px; }}
.dash-dropdown .Select-arrow {{ border-top-color: rgba(255,255,255,0.4) !important; }}

.radio-group .form-check-input {{ accent-color: {PALETTE["sky"]}; }}
.radio-group .form-check-label {{
    color: rgba(255,255,255,0.65);
    font-size: 12.5px;
    cursor: pointer;
}}
.radio-group .form-check-input:checked + .form-check-label {{ color: #fff; font-weight: 600; }}

/* Loading overlay */
._dash-loading-callback {{ opacity: 0.6; }}
"""

