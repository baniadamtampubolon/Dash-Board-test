"""
Dashboard Ketenagakerjaan Nasional — Kementerian Ketenagakerjaan RI
Rewritten from Streamlit to Dash for stability, performance, and richer visuals.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc

# ─── Local Modules ────────────────────────────────────────────────────────────────
from design import PALETTE, CUSTOM_CSS
from data_loader import DATA_AVAILABLE
from components import make_sidebar

from pages.main   import render_main
from pages.geomap import render_geomap, register_geomap_callbacks
from pages.ews    import render_ews, register_ews_callbacks
from pages.puk    import render_puk
from pages.ak     import render_ak
from pages.pt     import render_pt
from pages.pyb    import render_pyb
from pages.demo   import render_demo_page
from pages.ratio  import render_tpak, render_tpt_rasio, render_epr


# ─── App Init ────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dashboard Ketenagakerjaan | Kemnaker RI"
server = app.server


# ─── Layout ──────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="store-active-tab", data="main"),

    make_sidebar(),

    html.Div(className="main-content", children=[
        html.Div(id="page-content"),
    ]),
])


# ─── Callbacks: Navigation ────────────────────────────────────────────────────────
@app.callback(
    Output("store-active-tab", "data"),
    Output("nav-main",   "className"),
    Output("nav-geomap", "className"),
    Output("nav-ews",    "className"),
    Output("nav-puk",    "className"),
    Output("nav-ak",     "className"),
    Output("nav-pt",     "className"),
    Output("nav-pyb",    "className"),
    Output("nav-tpak",   "className"),
    Output("nav-tpt_rasio", "className"),
    Output("nav-epr",    "className"),
    Input("nav-main",   "n_clicks"),
    Input("nav-geomap", "n_clicks"),
    Input("nav-ews",    "n_clicks"),
    Input("nav-puk",    "n_clicks"),
    Input("nav-ak",     "n_clicks"),
    Input("nav-pt",     "n_clicks"),
    Input("nav-pyb",    "n_clicks"),
    Input("nav-tpak",   "n_clicks"),
    Input("nav-tpt_rasio", "n_clicks"),
    Input("nav-epr",    "n_clicks"),
    prevent_initial_call=True,
)
def update_active_tab(*_):
    triggered = callback_context.triggered_id
    mapping = {
        "nav-main": "main", "nav-geomap": "geomap", "nav-ews": "ews", "nav-puk": "puk",
        "nav-ak": "ak", "nav-pt": "pt", "nav-pyb": "pyb",
        "nav-tpak": "tpak", "nav-tpt_rasio": "tpt_rasio", "nav-epr": "epr",
    }
    tab = mapping.get(triggered, "main")
    classes = {k: "nav-btn" for k in mapping}
    classes[triggered] = "nav-btn active"
    return (tab,
            classes["nav-main"], classes["nav-geomap"], classes["nav-ews"], classes["nav-puk"],
            classes["nav-ak"],   classes["nav-pt"],  classes["nav-pyb"],
            classes["nav-tpak"], classes["nav-tpt_rasio"], classes["nav-epr"])


# ─── Callbacks: Filter visibility ────────────────────────────────────────────────
@app.callback(
    Output("prov-container", "style"),
    Output("kab-container",  "style"),
    Input("radio-level", "value"),
)
def toggle_filters(level):
    prov_style = {"display": "block"} if level in ("provinsi", "kabupaten") else {"display": "none"}
    kab_style  = {"display": "block"} if level == "kabupaten" else {"display": "none"}
    return prov_style, kab_style


@app.callback(
    Output("dd-kab", "options"),
    Output("dd-kab", "value"),
    Input("dd-prov", "value"),
)
def update_kabkot(prov):
    if not prov or not DATA_AVAILABLE:
        return [], None
    from data_loader import _GEO
    kab_df = (
        _GEO[(_GEO['nm_prov'] == prov) & (_GEO['nm_kabkot'] != '-')]
        [['kd_kabkot', 'nm_kabkot']].drop_duplicates().sort_values('kd_kabkot')
    )
    opts = [{"label": k, "value": k} for k in kab_df['nm_kabkot']]
    return opts, (opts[0]["value"] if opts else None)


# ─── Callbacks: Page Content ──────────────────────────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    Input("store-active-tab", "data"),
    Input("dd-year",    "value"),
    Input("radio-level","value"),
    Input("dd-prov",    "value"),
    Input("dd-kab",     "value"),
)
def render_page(tab, year, level, prov, kab):
    if not DATA_AVAILABLE:
        return html.Div([
            html.Div(className="page-header", children=[
                html.Span("⚠️ Mode Demo", className="page-badge"),
                html.H1("Data tidak tersedia", className="page-title"),
                html.P(
                    "Letakkan file Excel di folder Database/ lalu jalankan ulang aplikasi. "
                    "Tampilan di bawah adalah contoh mock data.",
                    className="page-subtitle",
                ),
            ]),
            render_demo_page(),
        ])

    if tab == "main":     return render_main(year, level, prov, kab)
    if tab == "geomap":   return render_geomap(year, level, prov, kab)
    if tab == "ews":      return render_ews(year, level, prov, kab)
    if tab == "puk":      return render_puk(year, level, prov, kab)
    if tab == "ak":       return render_ak(year, level, prov, kab)
    if tab == "pt":       return render_pt(year, level, prov, kab)
    if tab == "pyb":      return render_pyb(year, level, prov, kab)
    if tab == "tpak":     return render_tpak(year, level, prov, kab)
    if tab == "tpt_rasio": return render_tpt_rasio(year, level, prov, kab)
    if tab == "epr":      return render_epr(year, level, prov, kab)
    return html.Div("Pilih menu di sidebar.")


# ─── Register additional callbacks from pages ────────────────────────────────────
register_geomap_callbacks(app)
register_ews_callbacks(app)


if __name__ == "__main__":
    # host='0.0.0.0' allows access from other devices on your local network
    app.run(debug=True, host='0.0.0.0', port=8050)
