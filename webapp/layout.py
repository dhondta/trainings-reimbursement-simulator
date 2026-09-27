""" The page shell (serve_layout) and the two top-level views it swaps between: the signed-in main dashboard
(render_main_view) and, via auth.render_login_view, whichever login form matches config.AUTH_METHOD."""
from __future__ import annotations

from dash import Input, Output, dash_table, dcc, html

from . import config
from .auth import render_login_view, signed_in_identity
from .helpers import load_preset_rows, presets_for_session, slider_marks
from .instance import app
from .strings import STRINGS


def render_main_view(identity: str | None):
    # Computed fresh per page load (inside the visitor's own request context), so each user's dropdown and initial table
    #  already reflect their own previously uploaded CSVs, not just the bundled presets.
    presets = presets_for_session()
    default_rows = load_preset_rows(config.DEFAULT_PRESET_NAME, presets) if config.DEFAULT_PRESET_NAME in presets \
        else []
    # Basic Auth credentials are cached by the browser, not by our session cookie, so there is no server-side way to
    #  make "Sign out" actually sign the visitor out - hide the button rather than offer something that won't work.
    can_sign_out = identity and config.AUTH_METHOD != "basic"
    return html.Div(
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                children=[
                    html.Span(f"Signed in as {identity}" if identity else "Local mode - session management disabled",
                              style={"color": "#555", "fontSize": "13px"}),
                    html.Div(
                        style={"display": "flex", "gap": "8px", "alignItems": "center"},
                        children=[
                            html.Label(STRINGS[config.DEFAULT_LANG]["language_label"], id="language-label"),
                            dcc.RadioItems(
                                id="lang-selector",
                                options=config.LANGUAGE_OPTIONS,
                                value=config.DEFAULT_LANG,
                                inline=True,
                                labelStyle={"marginRight": "12px"},
                            ),
                            *([html.Button("Sign out", id="logout-btn", n_clicks=0)] if can_sign_out else []),
                        ],
                    ),
                ],
            ),
            html.H2(STRINGS[config.DEFAULT_LANG]["app_title"], id="app-title"),
            html.Ul(
                [html.Li(c) for c in STRINGS[config.DEFAULT_LANG]["law_criteria"]],
                id="law-summary",
                style={
                    "color": "#555",
                    "fontSize": "13px",
                    "fontStyle": "italic",
                    "borderLeft": "3px solid #ddd",
                    "paddingLeft": "28px",
                    "margin": "0 0 20px 0",
                },
            ),
            html.Div(
                style={"display": "flex", "gap": "12px", "alignItems": "center", "marginBottom": "8px"},
                children=[
                    html.Label(STRINGS[config.DEFAULT_LANG]["load_label"], id="load-label"),
                    dcc.Dropdown(
                        id="preset-dropdown",
                        options=[{"label": name, "value": name} for name in presets],
                        placeholder=STRINGS[config.DEFAULT_LANG]["preset_placeholder"],
                        style={"width": "260px"},
                    ),
                    dcc.Upload(
                        id="csv-upload",
                        children=html.Button(STRINGS[config.DEFAULT_LANG]["browse_label"], id="browse-btn"),
                        accept=".csv",
                        multiple=False,
                    ),
                    html.Button(STRINGS[config.DEFAULT_LANG]["export_label"], id="export-btn", n_clicks=0),
                    dcc.Download(id="csv-download"),
                    html.Button(STRINGS[config.DEFAULT_LANG]["add_row"], id="add-row-btn", n_clicks=0),
                    html.Button(STRINGS[config.DEFAULT_LANG]["move_up_label"], id="move-up-btn", n_clicks=0),
                    html.Button(STRINGS[config.DEFAULT_LANG]["move_down_label"], id="move-down-btn", n_clicks=0),
                ],
            ),
            html.Div(id="upload-error", style={"color": "crimson", "marginBottom": "8px"}),
            html.Div(id="reorder-error", style={"color": "crimson", "marginBottom": "8px"}),
            dash_table.DataTable(
                id="courses-table",
                columns=[
                    {"name": STRINGS[config.DEFAULT_LANG]["col_course"], "id": "Course", "type": "text"},
                    {"name": STRINGS[config.DEFAULT_LANG]["col_price"], "id": "Price", "type": "text"},
                    {"name": STRINGS[config.DEFAULT_LANG]["col_end_date"], "id": "End Date", "type": "text"},
                ],
                data=default_rows,
                editable=True,
                row_deletable=True,
                row_selectable="single",
                selected_rows=[],
                style_table={"marginBottom": "16px"},
                style_cell={"padding": "6px", "textAlign": "left"},
                style_header={"fontWeight": "bold"},
            ),
            html.Div(id="courses-error", style={"color": "crimson", "whiteSpace": "pre-line", "marginBottom": "12px"}),
            html.Hr(),
            html.Label(STRINGS[config.DEFAULT_LANG]["departure_label"], id="departure-label"),
            html.Div(id="departure-date-label", style={"fontWeight": "bold", "margin": "8px 0"}),
            dcc.Slider(
                id="departure-slider",
                min=0,
                max=config.FALLBACK_SLIDER_MONTHS,
                step=1,
                value=0,
                marks=slider_marks(config.FALLBACK_SLIDER_MONTHS),
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            html.Div(
                style={"display": "flex", "gap": "16px", "alignItems": "stretch", "marginTop": "20px"},
                children=[
                    dcc.Graph(id="reimbursement-bar", style={"flex": "3", "minWidth": "0"}),
                    html.Div(
                        style={
                            "flex": "1",
                            "minWidth": "180px",
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "16px",
                            "justifyContent": "center",
                        },
                        children=[
                            html.Div(id="final-rendement-date-card", style=config.CARD_STYLE),
                            html.Div(id="total-reimbursement-card", style=config.CARD_STYLE),
                            html.Div(id="rendement-rate-card", style=config.CARD_STYLE),
                        ],
                    ),
                ],
            ),
            dcc.Graph(id="rendement-timeline"),
            html.Div(id="law-application", style={"marginTop": "12px"}),
        ],
    )


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(_pathname):
    if config.LOCAL_MODE:
        return render_main_view(None)
    identity = signed_in_identity()
    return render_main_view(identity) if identity else render_login_view()


def serve_layout():
    # A stable shell: only its content (page-content) changes, driven by render_page below, so the login and main
    #  views can be swapped in reactively without a full browser reload.
    return html.Div(
        style={"fontFamily": "Arial, sans-serif", "maxWidth": "1100px", "margin": "0 auto", "padding": "24px"},
        children=[
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
        ],
    )
app.layout = serve_layout

