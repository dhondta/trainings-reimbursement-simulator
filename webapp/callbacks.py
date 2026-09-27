"""The dashboard's business-logic callbacks: CSV upload/presets, the departure-date slider, chart/card generation,
language switching, and course-table editing. Sign-in related callbacks live in auth.py instead."""
from __future__ import annotations

import base64
import binascii
from decimal import Decimal
from pathlib import Path

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html, no_update

from simulator import REPAYMENT_MONTHS, add_months, build_period_status_timeline, build_rendement_periods, \
                      calculate_reimbursement, determine_triggering_courses, load_courses, money

from . import config
from .auth import session_dir
from .helpers import date_at, final_rendement_completion_day, info_card, load_preset_rows, presets_for_session, \
                     rows_to_courses, rows_to_csv, slider_marks, slider_max_months, split_at_departure, status_at_date, \
                     timeline_horizon, value_card
from .instance import app
from .strings import STRINGS


@app.callback(Output("preset-dropdown", "options"), Output("preset-dropdown", "value"),
              Output("upload-error", "children"), Input("csv-upload", "contents"),
              State("csv-upload", "filename"), State("lang-selector", "value"), prevent_initial_call=True)
def handle_csv_upload(contents, filename, lang):
    t = STRINGS[lang]
    if contents is None:
        return no_update, no_update, no_update
    try:
        _header, encoded = contents.split(",", 1)
        raw_bytes = base64.b64decode(encoded)
    except (ValueError, binascii.Error) as exc:
        return no_update, no_update, t["upload_error"].format(error=exc)
    # Sanitize filename (strip any directory components), save into this user's own session folder, and never overwrite
    #  one of their existing uploads (number the file instead) - a name that only collides with a bundled preset is
    #  fine, it will simply shadow it for this user.
    safe_name = Path(filename or "custom.csv").name
    if not safe_name.lower().endswith(".csv"):
        safe_name += ".csv"
    stem, suffix = Path(safe_name).stem, Path(safe_name).suffix
    user_dir = session_dir()
    if user_dir is None:
        return no_update, no_update, t["auth_required"]
    dest = user_dir / safe_name
    n = 1
    while dest.exists():
        dest = user_dir / f"{stem} ({n}){suffix}"
        n += 1
    dest.write_bytes(raw_bytes)
    try:
        load_courses(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        return no_update, no_update, t["upload_error"].format(error=exc)
    presets = presets_for_session()
    return [{"label": name, "value": name} for name in presets], dest.name, ""


@app.callback(Output("csv-download", "data"), Input("export-btn", "n_clicks"), State("courses-table", "data"),
              State("preset-dropdown", "value"), prevent_initial_call=True)
def export_csv(_n_clicks, rows, preset_name):
    # Named after the loaded preset when there is one, so exporting then re-uploading an edited set reads naturally.
    filename = Path(preset_name).name if preset_name else "courses.csv"
    return dcc.send_string(rows_to_csv(rows or []), filename)


@app.callback(Output("courses-table", "data", allow_duplicate=True), Output("courses-table", "selected_rows"),
              Output("reorder-error", "children"), Input("move-up-btn", "n_clicks"),
              Input("move-down-btn", "n_clicks"), State("courses-table", "data"),
              State("courses-table", "selected_rows"), State("lang-selector", "value"), prevent_initial_call=True)
def reorder_table(up_clicks, down_clicks, rows, selected_rows, lang):
    trigger = dash.callback_context.triggered_id
    rows = list(rows or [])
    if not selected_rows:
        return no_update, no_update, STRINGS[lang]["move_no_selection"]
    i = selected_rows[0]
    if trigger == "move-up-btn" and i > 0:
        rows[i - 1], rows[i] = rows[i], rows[i - 1]
        i -= 1
    elif trigger == "move-down-btn" and i < len(rows) - 1:
        rows[i + 1], rows[i] = rows[i], rows[i + 1]
        i += 1
    else:
        return no_update, no_update, ""
    return rows, [i], ""


@app.callback(Output("departure-date-label", "children"), Input("departure-slider", "value"))
def show_departure_date(slider_value):
    return date_at(slider_value).strftime("%d/%m/%Y")


@app.callback(Output("courses-error", "children"), Output("final-rendement-date-card", "children"),
              Output("total-reimbursement-card", "children"), Output("reimbursement-bar", "figure"),
              Output("rendement-timeline", "figure"), Output("rendement-rate-card", "children"),
              Output("law-application", "children"), Input("courses-table", "data"),
              Input("departure-slider", "value"), Input("lang-selector", "value"))
def update_charts(rows, slider_value, lang):
    t = STRINGS[lang]
    departure_date = date_at(slider_value)
    departure_str = departure_date.strftime("%d/%m/%Y")
    courses, errors = rows_to_courses(rows or [], lang=lang)
    error_text = "\n".join(errors)
    empty_bar = go.Figure()
    empty_bar.update_layout(title=t["bar_title_default"])
    empty_timeline = go.Figure()
    empty_timeline.update_layout(title=t["timeline_title_default"])
    empty_rate_card = info_card(t["rate_label"], t["rate_none"])
    if not courses:
        no_course_card = info_card(t["final_date_label"], t["no_valid_courses"])
        return (
            error_text,
            no_course_card,
            info_card(t["total_label"].format(date=departure_str), t["no_valid_courses"]),
            empty_bar,
            empty_timeline,
            empty_rate_card,
            html.Div(t["no_valid_courses"], style={"color": "#777"}),
        )
    triggering_courses, _audit = determine_triggering_courses(courses)
    periods = build_rendement_periods(triggering_courses)
    if not periods:
        empty_bar.update_layout(title=t["bar_title_none"])
        return (
            error_text,
            info_card(t["final_date_label"], t["final_date_none"]),
            value_card(t["total_label"].format(date=departure_str), "0.00 €"),
            empty_bar,
            empty_timeline,
            empty_rate_card,
            html.Div(t["final_date_none"], style={"color": "#777"}),
        )
    total, details = calculate_reimbursement(periods, departure_date)
    # --------------------------------------------------------
    # Vertical bar chart: degressive reimbursement per course
    codes = [d["course"] for d in details]
    amounts = [float(d["reimbursement"]) for d in details]
    # The y-axis upper bound is fixed to the amounts at the earliest reachable departure date (slider index 0), not the
    #  currently selected one: since reimbursement only ever decreases as the departure date advances, that is always
    #  the largest a bar can be, so the axis no longer rescales as the slider moves.
    _, details_at_start = calculate_reimbursement(build_rendement_periods(triggering_courses), date_at(0))
    max_amount = max((d["reimbursement"] for d in details_at_start), default=Decimal("0"))
    y_upper = float(max_amount) * 1.15 if max_amount > 0 else 1.0
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=codes,
                y=amounts,
                text=[f"{a:,.2f} €" for a in amounts],
                textposition="outside",
                marker_color="#2E86AB",
            )
        ]
    )
    bar_fig.update_layout(
        title=t["bar_title"].format(date=departure_date.strftime("%d/%m/%Y")),
        xaxis_title=t["xaxis_course"],
        yaxis_title=t["yaxis_amount"],
        yaxis_range=[0, y_upper],
        margin={"t": 60},
    )
    # --------------------------------------------------------
    # Horizontal bar chart: rendement periods, as accurate month-by-month runs of "served" / "suspended" (a more recent
    #  course's period took priority). Each period stays suspended until every more recent one has itself fully
    #  completed its 24 months, so the timeline is built out to a horizon far past the selected departure date - not
    #  capped at it - to let that chain of suspensions fully unwind into the pyramid of real completion dates.
    # Plotly plots a numeric bar "length" against a date axis as a duration in MILLISECONDS from `base`. The length must
    #  therefore be converted to an actual calendar span (in ms) between the real start/end dates of each run, not
    #  passed as a raw month count.
    timeline_fig = go.Figure()
    horizon = timeline_horizon(periods)
    timeline_by_course = build_period_status_timeline(periods, horizon)
    display_timeline_by_course = {code: split_at_departure(runs, departure_date) \
                                  for code, runs in timeline_by_course.items()}
    for d in details:
        for run in display_timeline_by_course.get(d["course"], []):
            status = run["status"]
            status_label = t[status].lower()
            timeline_fig.add_trace(
                go.Bar(
                    y=[d["course"]],
                    x=[(run["end"] - run["start"]).days * config.MS_PER_DAY],
                    base=[run["start"].isoformat()],
                    orientation="h",
                    name=t[status],
                    marker_color=config.STATUS_COLORS[status],
                    showlegend=False,
                    customdata=[[run["start"].strftime("%d/%m/%Y"), run["end"].strftime("%d/%m/%Y")]],
                    hovertemplate=(
                        f"%{{y}} - {status_label}<br>"
                        "%{customdata[0]} → %{customdata[1]}<extra></extra>"
                    ),
                )
            )
    timeline_fig.update_layout(
        title=t["timeline_title"],
        xaxis_title=t["xaxis_date"],
        yaxis_title=t["yaxis_course"],
        barmode="stack",
        margin={"t": 60},
    )
    timeline_fig.update_xaxes(type="date")
    departure_iso = departure_date.isoformat()
    timeline_fig.add_shape(
        type="line",
        x0=departure_iso,
        x1=departure_iso,
        y0=0,
        y1=1,
        yref="paper",
        line={"dash": "dash", "color": "black"},
    )
    timeline_fig.add_annotation(
        x=departure_iso,
        y=1,
        yref="paper",
        text=t["departure_marker"],
        showarrow=False,
        yanchor="bottom",
    )
    # Legend proxies (since individual bar traces have showlegend=False). Always shown, even if a status has no bar this
    #  run (e.g. no "remaining" left once the departure date is past the final rendement end date), so the legend stays
    #  stable across the slider.
    for status in ("served", "suspended", "remaining"):
        timeline_fig.add_trace(go.Bar(y=[None], x=[None], marker_color=config.STATUS_COLORS[status], name=t[status]))
    total_card = value_card(t["total_label"].format(date=departure_str), f"{total:.2f} €")
    final_date = final_rendement_completion_day(periods)
    final_date_card = value_card(t["final_date_label"], final_date.strftime("%d/%m/%Y") if final_date else "-")
    # Rendement rate: amount served during the month right after the slider's departure date, i.e. the course actively
    #  accruing rendement that month in the full (unsplit) pyramid.
    next_month = add_months(departure_date, 1)
    price_by_code = {d["course"]: d["cost"] for d in details}
    active_code = None
    for code, runs in timeline_by_course.items():
        for run in runs:
            if run["status"] == "served" and run["start"] <= next_month < run["end"]:
                active_code = code
                break
        if active_code:
            break
    if active_code is None:
        rate_card = info_card(t["rate_label"], t["rate_none"])
    else:
        amount = money(price_by_code[active_code] / Decimal(REPAYMENT_MONTHS))
        pct = (amount / total * 100) if total > 0 else Decimal("0.00")

        rate_card = value_card(
            t["rate_label"],
            f"{amount:.2f} €",
            html.Div(
                t["rate_detail"].format(code=active_code, month=next_month.strftime("%m/%Y")),
                style={"marginTop": "4px"},
            ),
            html.Div(t["rate_pct"].format(pct=f"{pct:.2f}"), style={"color": "#777", "fontSize": "13px"}),
        )
    # --------------------------------------------------------
    # Dynamic explanation: how the four criteria listed under the title concretely apply to this simulation, with
    #  the actual numbers behind this departure date.
    n_owing = sum(1 for d in details if d["months_remaining"] > 0)
    n_active = sum(1 for d in details if status_at_date(timeline_by_course[d["course"]], departure_date) == "served")
    capped_rows = [d for d in details if d["months_forgiven"] > 0]
    if capped_rows:
        forgiven_amount = money(sum(
            (d["cost"] * Decimal(d["months_forgiven"]) / Decimal(REPAYMENT_MONTHS) for d in capped_rows),
            Decimal("0.00"),
        ))
        cap_explanation = t["explanation_cap_some"].format(n_capped=len(capped_rows), amount=f"{forgiven_amount:.2f}")
    else:
        cap_explanation = t["explanation_cap_none"]
    law_application = html.Div([
        html.Div(t["explanation_title"], style={"fontWeight": "bold", "marginBottom": "8px"}),
        html.Ol(
            [
                html.Li(t["explanation_threshold"].format(
                    n_triggering=len(triggering_courses), n_total=len(courses),
                    codes=", ".join(c.code for c in triggering_courses),
                )),
                html.Li(t["explanation_rendement"].format(date=departure_str, n_owing=n_owing, total=f"{total:.2f}")),
                html.Li(t["explanation_priority"].format(
                    date=departure_str, n_active=n_active, n_suspended=len(details) - n_active,
                )),
                html.Li(cap_explanation),
            ],
            style={"fontSize": "13px", "color": "#555"},
        ),
    ])
    return error_text, final_date_card, total_card, bar_fig, timeline_fig, rate_card, law_application


@app.callback(Output("departure-slider", "max"), Output("departure-slider", "marks"),
              Output("departure-slider", "value"), Input("courses-table", "data"), State("departure-slider", "value"))
def update_slider_range(rows, current_value):
    courses, _errors = rows_to_courses(rows or [])
    triggering_courses, _audit = determine_triggering_courses(courses)
    periods = build_rendement_periods(triggering_courses)
    max_months = slider_max_months(periods)
    return max_months, slider_marks(max_months), min(current_value or 0, max_months)


@app.callback(Output("language-label", "children"), Output("app-title", "children"), Output("law-summary", "children"),
              Output("load-label", "children"), Output("preset-dropdown", "placeholder"),
              Output("browse-btn", "children"), Output("export-btn", "children"), Output("add-row-btn", "children"), Output("move-up-btn", "children"),
              Output("move-down-btn", "children"), Output("courses-table", "columns"),
              Output("departure-label", "children"), Input("lang-selector", "value"))
def update_static_labels(lang):
    t = STRINGS[lang]
    columns = [
        {"name": t["col_course"], "id": "Course", "type": "text"},
        {"name": t["col_price"], "id": "Price", "type": "text"},
        {"name": t["col_end_date"], "id": "End Date", "type": "text"},
    ]
    law_criteria = [html.Li(c) for c in t["law_criteria"]]
    return t["language_label"], t["app_title"], law_criteria, t["load_label"], t["preset_placeholder"], \
           t["browse_label"], t["export_label"], t["add_row"], t["move_up_label"], t["move_down_label"], columns, \
           t["departure_label"]


@app.callback(Output("courses-table", "data"), Input("preset-dropdown", "value"), Input("add-row-btn", "n_clicks"),
              State("courses-table", "data"), prevent_initial_call=True)
def update_table(preset_name, n_clicks, current_rows):
    trigger = dash.callback_context.triggered_id
    if trigger == "preset-dropdown" and preset_name:
        return load_preset_rows(preset_name, presets_for_session())
    if trigger == "add-row-btn":
        return (current_rows or []) + [dict(config.EMPTY_ROW)]
    return current_rows

