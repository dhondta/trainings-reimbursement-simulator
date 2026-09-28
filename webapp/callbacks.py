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

from simulator import active_rendement, build_period_status_timeline, calculate_reimbursement, \
                      determine_triggering_courses, load_courses, money

from . import config
from .auth import session_dir
from .helpers import date_at, detail_status, explanation_items, final_rendement_completion_day, icon_label, \
                     info_card, load_preset_rows, normalize_rows, presets_for_session, rendement_periods, \
                     rows_to_courses, rows_to_csv, slider_marks, slider_max_months, slider_min_months, \
                     sort_rows_by_date, split_at_departure, timeline_horizon, value_card
from .instance import app
from .report import build_report
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


@app.callback(Output("pdf-download", "data"), Input("export-pdf-btn", "n_clicks"), State("courses-table", "data"),
              State("departure-slider", "value"), State("lang-selector", "value"), State("preset-dropdown", "value"),
              prevent_initial_call=True)
def export_pdf(_n_clicks, rows, slider_value, lang, preset_name):
    # The report covers the simulation as currently displayed: same courses, departure date and language.
    stem = Path(preset_name).stem if preset_name else "courses"
    pdf = build_report(rows or [], date_at(slider_value), lang, source=preset_name)
    return dcc.send_bytes(pdf, f"{stem}-report.pdf")


@app.callback(Output("courses-table", "data", allow_duplicate=True), Input("courses-table", "data_timestamp"),
              State("courses-table", "data"), prevent_initial_call=True)
def tidy_table(_data_timestamp, rows):
    """ After each user edit: reformats prices and dates to the table's canonical format, and re-sorts rows by date.
     data_timestamp only changes on user edits (not when a callback sets the data), so updating it here doesn't loop. """
    rows = rows or []
    tidy_rows = sort_rows_by_date(normalize_rows(rows))
    return no_update if tidy_rows == rows else tidy_rows


@app.callback(Output("departure-date-label", "children"), Input("departure-slider", "value"))
def show_departure_date(slider_value):
    return date_at(slider_value).strftime("%d/%m/%y")


@app.callback(Output("courses-error", "children"), Output("rendement-period-card", "children"),
              Output("total-reimbursement-card", "children"), Output("reimbursement-bar", "figure"),
              Output("rendement-timeline", "figure"), Output("rendement-rate-card", "children"),
              Output("law-application", "children"), Input("courses-table", "data"),
              Input("departure-slider", "value"), Input("lang-selector", "value"))
def update_charts(rows, slider_value, lang):
    t = STRINGS[lang]
    departure_date = date_at(slider_value)
    departure_str = departure_date.strftime("%d/%m/%y")
    courses, errors = rows_to_courses(rows or [], lang=lang)
    error_text = "\n".join(errors)
    empty_bar = go.Figure()
    empty_bar.update_layout(title=t["bar_title_default"])
    empty_timeline = go.Figure()
    empty_timeline.update_layout(title=t["timeline_title_default"])
    empty_rate_card = info_card(t["rate_label"], t["rate_none"])
    if not courses:
        no_course_card = info_card(t["period_label"], t["no_valid_courses"])
        return (
            error_text,
            no_course_card,
            info_card(t["total_label"].format(date=departure_str), t["no_valid_courses"]),
            empty_bar,
            empty_timeline,
            empty_rate_card,
            html.Div(t["no_valid_courses"], className="text-muted"),
        )
    triggering_courses, _audit = determine_triggering_courses(courses)
    periods = rendement_periods(triggering_courses)
    if not periods:
        empty_bar.update_layout(title=t["bar_title_none"])
        return (
            error_text,
            info_card(t["period_label"], t["final_date_none"]),
            value_card(t["total_label"].format(date=departure_str), "0.00 €"),
            empty_bar,
            empty_timeline,
            empty_rate_card,
            html.Div(t["final_date_none"], className="text-muted"),
        )
    total, details = calculate_reimbursement(periods, departure_date)
    # --------------------------------------------------------
    # Vertical bar chart: degressive reimbursement per course, colored like the rendement periods' timeline below: red
    #  for an amount still owed, grey for an amount forgiven once the clause expired (art. 179, §5 - shown as a bar of
    #  that forgiven amount, since the course itself no longer owes anything), and green for a zero amount because the
    #  period was fully served (only its label shows, in green). A course not yet taken at the departure date is left
    #  blank, with a muted label.
    codes = [d["course"] for d in details]
    statuses = [detail_status(d) for d in details]
    amounts = [float(money(d["amount_forgiven"]) if status == "expired" else d["reimbursement"])
               for d, status in zip(details, statuses)]
    colors = [config.STATUS_COLORS[status] if status else config.THEME_COLORS["secondary"] for status in statuses]
    # The y-axis upper bound is fixed to the largest course price, not to the currently selected amounts: the slider
    #  reaches back to the start of every rendement period, where the course is still owed in full, and reimbursement
    #  only ever decreases from there, so that is the largest a bar can be and the axis doesn't rescale as it moves.
    max_amount = max((d["cost"] for d in details), default=Decimal("0"))
    y_upper = float(max_amount) * 1.15 if max_amount > 0 else 1.0
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=codes,
                y=amounts,
                # Labels rounded to the euro so that neighbouring ones don't overlap; the hover shows the exact amount.
                text=[f"{a:,.0f} €" if status else "–" for a, status in zip(amounts, statuses)],
                textposition="outside",
                textfont={"color": colors},
                marker_color=colors,
                customdata=[t[status] if status else "-" for status in statuses],
                hovertemplate="%{x} - %{customdata}<br>%{y:,.2f} €<extra></extra>",
                showlegend=False,
            )
        ]
    )
    # Legend proxies (the bars themselves carry per-course colors), always shown so the legend stays stable.
    for status in ("remaining", "expired", "served"):
        bar_fig.add_trace(go.Bar(x=[None], y=[None], marker_color=config.STATUS_COLORS[status], name=t[status]))
    bar_fig.update_layout(
        title=t["bar_title"].format(date=departure_date.strftime("%d/%m/%y")),
        xaxis_title=t["xaxis_course"],
        yaxis_title=t["yaxis_amount"],
        yaxis_range=[0, y_upper],
        margin={"t": 60},
        # Same label size on every bar (Plotly would otherwise shrink them to fit, except over the zero-height ones).
        uniformtext={"minsize": 9, "mode": "show"},
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
                    customdata=[[run["start"].strftime("%d/%m/%y"), run["end"].strftime("%d/%m/%y")]],
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
    # Rendement period: from the start of the first rendement period to the last day of the final one (following the
    #  full suspension pyramid), on a single line - hence a slightly smaller font, sized to fit the metric cards' column
    #  (see layout.py).
    first_start, final_date = min(p.start_date for p in periods), final_rendement_completion_day(periods)
    period_card = value_card(t["period_label"], [first_start.strftime("%d/%m/%y"), " - ",
                                                 (final_date.strftime("%d/%m/%y") if final_date else "-")],
                             font_size="24px")
    # Rendement rate: amount served during the current month, i.e. the month starting on the slider's departure date
    #  (always the 1st of a month), by the course actively accruing rendement that month in the full (unsplit) pyramid -
    #  at that month's rate, which follows the index when a minimum rendement rate is set.
    current_month = departure_date
    if (active_now := active_rendement(periods, current_month)) is None:
        rate_card = info_card(t["rate_label"], t["rate_none"])
    else:
        active_code, amount = active_now[0].course.code, active_now[1]
        pct = (amount / total * 100) if total > 0 else Decimal("0.00")

        rate_card = value_card(
            t["rate_label"],
            f"{amount:.2f} €",
            html.Div(
                t["rate_detail"].format(code=active_code, month=current_month.strftime("%b %y")),
                className="mt-1",
            ),
            html.Div(t["rate_pct"].format(pct=f"{pct:.2f}"), className="small text-muted"),
        )
    # --------------------------------------------------------
    # Dynamic explanation: how the four criteria listed under the title concretely apply to this simulation, with
    #  the actual numbers behind this departure date.
    explanation = explanation_items(t, courses, triggering_courses, details, timeline_by_course, departure_date, total)
    law_application = html.Div([
        html.Div(t["explanation_title"], className="fw-bold mb-2"),
        html.Ol([html.Li(item) for item in explanation], className="small text-muted mb-0"),
    ])
    return error_text, period_card, total_card, bar_fig, timeline_fig, rate_card, law_application


@app.callback(Output("departure-slider", "min"), Output("departure-slider", "max"),
              Output("departure-slider", "marks"), Output("departure-slider", "value"),
              Input("courses-table", "data"), State("departure-slider", "value"))
def update_slider_range(rows, current_value):
    courses, _errors = rows_to_courses(rows or [])
    triggering_courses, _audit = determine_triggering_courses(courses)
    periods = rendement_periods(triggering_courses)
    min_months, max_months = slider_min_months(periods), slider_max_months(periods)
    value = max(min_months, min(current_value or 0, max_months))
    return min_months, max_months, slider_marks(min_months, max_months), value


@app.callback(Output("language-label", "children"), Output("app-title", "children"), Output("law-summary", "children"),
              Output("load-label", "children"), Output("preset-dropdown", "placeholder"),
              Output("browse-btn", "children"), Output("export-btn", "children"),
              Output("export-pdf-btn", "children"), Output("add-row-btn", "children"),
              Output("courses-table", "columns"), Output("departure-label", "children"),
              Input("lang-selector", "value"))
def update_static_labels(lang):
    t = STRINGS[lang]
    columns = [
        {"name": t["col_course"], "id": "Course", "type": "text"},
        {"name": t["col_price"], "id": "Price", "type": "text"},
        {"name": t["col_end_date"], "id": "End Date", "type": "text"},
    ]
    law_criteria = [html.Li(c) for c in t["law_criteria"]]
    return t["language_label"], t["app_title"], law_criteria, t["load_label"], t["preset_placeholder"], \
           icon_label("upload", t["browse_label"]), icon_label("download", t["export_label"]), \
           icon_label("file-earmark-pdf", t["export_pdf_label"]), icon_label("plus-lg", t["add_row"]), columns, \
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

