""" The page shell (serve_layout) and the two top-level views it swaps between: the signed-in main dashboard
(render_main_view) and, via auth.render_login_view, whichever login form matches config.AUTH_METHOD."""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Input, Output, dash_table, dcc, html

from . import config
from .auth import render_login_view, signed_in_identity
from .helpers import icon_label, load_preset_rows, presets_for_session, slider_marks
from .instance import app
from .strings import STRINGS

# Plotly's toolbar only on hover (it would otherwise overlap the charts' titles on narrower screens), without its logo.
GRAPH_CONFIG = {"displayModeBar": "hover", "displaylogo": False}


def render_main_view(identity: str | None):
    # Computed fresh per page load (inside the visitor's own request context), so each user's dropdown and initial table
    #  already reflect their own previously uploaded CSVs, not just the bundled presets.
    presets = presets_for_session()
    default_rows = load_preset_rows(config.DEFAULT_PRESET_NAME, presets) if config.DEFAULT_PRESET_NAME in presets \
        else []
    # Basic Auth credentials are cached by the browser, not by our session cookie, so there is no server-side way to
    #  make "Sign out" actually sign the visitor out - hide the button rather than offer something that won't work.
    can_sign_out = identity and config.AUTH_METHOD != "basic"
    t = STRINGS[config.DEFAULT_LANG]
    navbar = dbc.Navbar(
        dbc.Container([
            html.Span(t["app_title"], id="app-title", className="navbar-brand text-wrap fw-semibold"),
            html.Div(
                className="d-flex align-items-center gap-2 ms-auto",
                children=[
                    html.Span(f"Signed in as {identity}" if identity else "Local mode - session management disabled",
                              className="small text-white-50 me-2 d-none d-lg-inline"),
                    html.Span(t["language_label"], id="language-label", className="small text-white-50"),
                    dbc.RadioItems(
                        id="lang-selector",
                        options=config.LANGUAGE_OPTIONS,
                        value=config.DEFAULT_LANG,
                        class_name="lang-toggle d-flex",
                        input_class_name="btn-check",
                        label_class_name="btn btn-sm btn-outline-light",
                        label_checked_class_name="active",
                    ),
                    *([dbc.Button(icon_label("box-arrow-right", "Sign out"), id="logout-btn", n_clicks=0, size="sm",
                                  color="light", outline=True, class_name="ms-2")] if can_sign_out else []),
                ],
            ),
        ]),
        color="primary",
        dark=True,
        class_name="mb-4 shadow-sm",
    )
    law_summary = dbc.Card(
        dbc.CardBody(html.Ul([html.Li(c) for c in t["law_criteria"]], id="law-summary",
                             className="mb-0 small text-muted fst-italic")),
        class_name="mb-4 shadow-sm",
        style={"borderLeft": f"4px solid {config.THEME_COLORS['info']}"},
    )
    courses = dbc.Card(
        dbc.CardBody([
            html.Div(
                className="d-flex flex-wrap align-items-center gap-2 mb-3",
                children=[
                    html.Label(t["load_label"], id="load-label", className="fw-semibold me-1"),
                    dcc.Dropdown(
                        id="preset-dropdown",
                        options=[{"label": name, "value": name} for name in presets],
                        placeholder=t["preset_placeholder"],
                        style={"width": "260px"},
                    ),
                    dcc.Upload(
                        id="csv-upload",
                        children=dbc.Button(icon_label("upload", t["browse_label"]), id="browse-btn",
                                            color="primary"),
                        accept=".csv",
                        multiple=False,
                    ),
                    dbc.Button(icon_label("download", t["export_label"]), id="export-btn", n_clicks=0,
                               color="primary", outline=True),
                    dcc.Download(id="csv-download"),
                    dbc.Button(icon_label("file-earmark-pdf", t["export_pdf_label"]), id="export-pdf-btn", n_clicks=0,
                               color="primary", outline=True),
                    dcc.Download(id="pdf-download"),
                    dbc.Button(icon_label("plus-lg", t["add_row"]), id="add-row-btn", n_clicks=0,
                               color="primary", outline=True),
                ],
            ),
            html.Div(id="upload-error", className="text-danger small mb-2"),
            html.Div(id="export-error", className="text-danger small mb-2"),
            dash_table.DataTable(
                id="courses-table",
                columns=[
                    {"name": t["col_course"], "id": "Course", "type": "text"},
                    {"name": t["col_price"], "id": "Price", "type": "text"},
                    {"name": t["col_end_date"], "id": "End Date", "type": "text"},
                ],
                data=default_rows,
                editable=True,
                row_deletable=True,
                style_table={"overflowX": "auto"},
                style_cell={"padding": "8px 12px", "textAlign": "left",
                            "border": f"1px solid {config.THEME_COLORS['border']}"},
                style_header={"fontWeight": "600", "backgroundColor": config.THEME_COLORS["light"]},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#FCFCFD"},
                    {"if": {"state": "active"}, "backgroundColor": "rgba(52, 152, 219, 0.08)",
                     "border": f"1px solid {config.THEME_COLORS['info']}"},
                ],
            ),
            html.Div(id="courses-error", className="text-danger small mt-2", style={"whiteSpace": "pre-line"}),
        ]),
        class_name="mb-4 shadow-sm",
    )
    departure = dbc.Card(
        dbc.CardBody([
            html.Div(
                className="d-flex align-items-baseline gap-3 mb-2",
                children=[
                    html.Label(t["departure_label"], id="departure-label", className="fw-semibold"),
                    html.Span(id="departure-date-label", className="fs-4 fw-bold text-primary"),
                ],
            ),
            dcc.Slider(
                id="departure-slider",
                min=0,
                max=config.FALLBACK_SLIDER_MONTHS,
                step=1,
                value=0,
                marks=slider_marks(0, config.FALLBACK_SLIDER_MONTHS),
                tooltip={"placement": "bottom", "always_visible": False},
                allow_direct_input=False,  # the raw month index would mean nothing to users (the date is shown above)
            ),
        ]),
        class_name="mb-4 shadow-sm",
    )
    # The metric cards' column is sized (xl=3 / lg=4, full width below) to keep the rendement period's dates on a single
    #  line (see update_charts).
    def metric_card(card_id):
        return dbc.Card(dbc.CardBody(id=card_id), class_name="text-center shadow-sm")
    charts = dbc.Row(
        class_name="g-3 mb-4",
        children=[
            dbc.Col(dbc.Card(dcc.Graph(id="reimbursement-bar", config=GRAPH_CONFIG), body=True,
                             class_name="h-100 shadow-sm"), xl=9, lg=8),
            dbc.Col(
                html.Div(
                    className="d-flex flex-column justify-content-center gap-3 h-100",
                    children=[metric_card("rendement-period-card"), metric_card("total-reimbursement-card"),
                              metric_card("rendement-rate-card")],
                ),
                xl=3, lg=4,
            ),
        ],
    )
    return html.Div([
        navbar,
        dbc.Container([
            law_summary,
            courses,
            departure,
            charts,
            dbc.Card(dcc.Graph(id="rendement-timeline", config=GRAPH_CONFIG), body=True, class_name="mb-4 shadow-sm"),
            dbc.Card(dbc.CardBody(id="law-application"), class_name="mb-4 shadow-sm"),
        ]),
    ])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(_pathname):
    if config.LOCAL_MODE:
        return render_main_view(None)
    identity = signed_in_identity()
    return render_main_view(identity) if identity else render_login_view()


def serve_layout():
    # A stable shell: only its content (page-content) changes, driven by render_page below, so the login and main
    #  views can be swapped in reactively without a full browser reload.
    #  Each view lays out its own Bootstrap container (the main view's navbar spans the full width).
    return html.Div(
        className="bg-body-tertiary min-vh-100",
        children=[
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
        ],
    )
app.layout = serve_layout

