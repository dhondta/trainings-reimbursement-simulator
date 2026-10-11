"""The PDF report of the reimbursement plan (the "Export PDF" button): the simulation displayed on the dashboard for the
selected departure date - key figures, threshold test, reimbursement per course, both charts and the explanation of the
law's criteria - laid out with ReportLab, in the dashboard's current language. The charts are drawn natively (not
exported from Plotly), so that no headless browser is needed server-side."""
from __future__ import annotations

import io
import math
from datetime import date
from decimal import Decimal
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Group, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, \
                               TableStyle

from simulator import active_rendement, build_period_status_timeline, calculate_reimbursement, \
                      determine_triggering_courses, money

from . import config
from .helpers import cut_off_runs, detail_status, explanation_items, final_rendement_completion_day, \
                     inactivity_runs, rendement_periods, rows_to_courses, split_at_departure, timeline_horizon, \
                     with_forgiven_runs
from .strings import STRINGS

FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"
MARGIN = 18 * mm
PAGE_WIDTH, PAGE_HEIGHT = A4
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
COLORS = {name: colors.HexColor(value) for name, value in config.THEME_COLORS.items()}
STATUS_COLORS = {name: colors.HexColor(value) for name, value in config.STATUS_COLORS.items()}
LAPSED = STATUS_COLORS["lapsed"]  # Drawn hatched (see _hatched).


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["BodyText"], fontName=FONT, fontSize=9, leading=12,
                          textColor=COLORS["body"])
    return {
        'title': ParagraphStyle("title", parent=base["Title"], fontName=FONT_BOLD, fontSize=18, leading=22,
                                textColor=COLORS["primary"], alignment=0, spaceAfter=4),
        'subtitle': ParagraphStyle("subtitle", parent=body, textColor=COLORS["secondary"]),
        'h2': ParagraphStyle("h2", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=12, leading=15,
                             textColor=COLORS["primary"], spaceBefore=12, spaceAfter=6),
        'h3': ParagraphStyle("h3", parent=body, fontName=FONT_BOLD, spaceBefore=6, spaceAfter=4),
        'body': body,
        'small': ParagraphStyle("small", parent=body, fontSize=8, leading=10),
        'muted': ParagraphStyle("muted", parent=body, textColor=COLORS["secondary"]),
        'error': ParagraphStyle("error", parent=body, fontSize=8, leading=10, textColor=COLORS["danger"]),
        'th': ParagraphStyle("th", parent=body, fontName=FONT_BOLD, fontSize=8, leading=10),
        'td': ParagraphStyle("td", parent=body, fontSize=8, leading=10),
        'card_label': ParagraphStyle("card_label", parent=body, fontName=FONT_BOLD, textColor=COLORS["secondary"],
                                     alignment=TA_CENTER),
        'card_value': ParagraphStyle("card_value", parent=body, fontName=FONT_BOLD, fontSize=14, leading=18,
                                     textColor=COLORS["primary"], alignment=TA_CENTER),
        'card_detail': ParagraphStyle("card_detail", parent=body, fontSize=8, leading=10, alignment=TA_CENTER,
                                      textColor=COLORS["secondary"]),
    }


def _data_table(header: list[str], rows: list[list], col_widths: list[float], styles: dict, numeric_cols=(),
                total_row: bool = False) -> Table:
    """ A zebra-striped table with a repeated header; numeric columns are right-aligned, and the last row is set in
     bold when it is a total. """
    right = ParagraphStyle("td_right", parent=styles["td"], alignment=2)
    def cell(value, col, bold=False):
        return Paragraph(f"<b>{escape(value)}</b>" if bold else escape(value),
                         right if col in numeric_cols else styles["td"])
    data = [[Paragraph(escape(h), styles["th"]) for h in header]]
    data += [[cell(v, col, bold=total_row and i == len(rows) - 1) for col, v in enumerate(row)]
             for i, row in enumerate(rows)]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["light"]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, COLORS["primary"]),
        ("GRID", (0, 0), (-1, -1), 0.25, COLORS["border"]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(2, len(data), 2):
        commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FCFCFD")))
    if total_row:
        commands.append(("LINEABOVE", (0, -1), (-1, -1), 0.8, COLORS["primary"]))
    table.setStyle(TableStyle(commands))
    return table


def _thousands(value: float, t: dict) -> str:
    """ A whole amount with the language's thousands separator (e.g. 7,750 / 7 750 / 7.750). """
    return f"{value:,.0f}".replace(",", t["thousands_sep"])


def _legend(drawing: Drawing, right: float, y: float, items: list[tuple[str, colors.Color]]) -> None:
    """ A one-line legend (colored square + label per item, hatched for "lapsed"), right-aligned on `right`. """
    widths = [10 + stringWidth(label, FONT, 7) + 10 for label, _color in items]
    x = right - sum(widths)
    for (label, color), w in zip(items, widths):
        if color is LAPSED:
            _hatched(drawing, x, y, 7, 7)
        else:
            drawing.add(Rect(x, y, 7, 7, fillColor=color, strokeColor=None))
        drawing.add(String(x + 10, y + 1, label, fontName=FONT, fontSize=7, fillColor=COLORS["body"]))
        x += w


def _hatched(drawing: Drawing, x: float, y: float, width: float, height: float, step: float = 3) -> None:
    """ A rectangle hatched with diagonal lines, for the months a period would still have been suspended once
     forgiven ("lapsed" - see helpers.with_forgiven_runs). """
    drawing.add(Rect(x, y, width, height, fillColor=colors.HexColor(config.HATCH_BACKGROUND), strokeColor=None))
    k = -height
    while k < width:
        # The line (x + k + s, y + s), for s in [0, height], within the rectangle's width.
        s0, s1 = max(0.0, -k), min(height, width - k)
        if s0 < s1:
            drawing.add(Line(x + k + s0, y + s0, x + k + s1, y + s1, strokeColor=LAPSED, strokeWidth=0.6))
        k += step


def _nice_step(span: float, n_ticks: int = 5) -> float:
    """ A round tick step (1, 2 or 5 times a power of ten) giving about n_ticks ticks over span. """
    raw = span / n_ticks
    magnitude = 10 ** math.floor(math.log10(raw))
    return next(m * magnitude for m in (1, 2, 5, 10) if m * magnitude >= raw)


def _bar_chart(t: dict, details: list[dict], width: float) -> Drawing:
    """ The degressive amount per course, as on the dashboard: red for an amount still owed, grey for an amount
     forgiven once the clause expired, and green for a zero amount because the period was fully served (label only). A
     course not yet taken is left blank. The y-axis goes up to the largest course price, like the dashboard's. """
    statuses = [detail_status(d) for d in details]
    amounts = [float(money(d["amount_forgiven"]) if s == "expired" else d["reimbursement"])
               for d, s in zip(details, statuses)]
    codes = [d["course"] for d in details]
    slot = (width - 60) / max(len(details), 1)
    rotate = any(stringWidth(code, FONT, 7) > slot - 2 for code in codes)
    bottom = 12 + (max(stringWidth(code, FONT, 7) for code in codes) * 0.71 if rotate else 10)
    height, left, top = 160 + bottom, 50, 20
    plot_w, plot_h = width - left - 10, height - bottom - top
    drawing = Drawing(width, height)
    max_cost = float(max((d["cost"] for d in details), default=Decimal("0")))
    y_upper = max_cost * 1.15 if max_cost > 0 else 1.0
    step = _nice_step(y_upper)
    # Amount labels shrunk just enough to fit their slot, so that neighbouring ones don't overlap on long course lists.
    labels = [f"{_thousands(amount, t)} €" if status else "–" for amount, status in zip(amounts, statuses)]
    label_size = min(6.5, 6.5 * (slot - 2) / max(stringWidth(label, FONT, 6.5) for label in labels))
    def y_at(value):
        return bottom + value / y_upper * plot_h
    tick = 0.0
    while tick <= y_upper:
        drawing.add(Line(left, y_at(tick), left + plot_w, y_at(tick), strokeColor=COLORS["border"], strokeWidth=0.5))
        drawing.add(String(left - 4, y_at(tick) - 2.5, _thousands(tick, t), fontName=FONT, fontSize=7, textAnchor="end",
                           fillColor=COLORS["body"]))
        tick += step
    label = String(0, 0, t["yaxis_amount"], fontName=FONT, fontSize=7, textAnchor="middle", fillColor=COLORS["body"])
    drawing.add(Group(label, transform=(0, 1, -1, 0, 9, bottom + plot_h / 2)))
    for i, (code, amount, status, text) in enumerate(zip(codes, amounts, statuses, labels)):
        center = left + (i + 0.5) * slot
        color = STATUS_COLORS[status] if status else COLORS["secondary"]
        if amount > 0:
            bar_w = min(slot * 0.6, 40)
            drawing.add(Rect(center - bar_w / 2, bottom, bar_w, y_at(amount) - bottom, fillColor=color,
                             strokeColor=None))
        # The label of a forgiven amount is in the darker grey, the lighter one of its bar being hard to read as text.
        drawing.add(String(center, y_at(amount) + 3, text, fontName=FONT, fontSize=label_size, textAnchor="middle",
                           fillColor=COLORS["secondary"] if status == "expired" else color))
        if rotate:
            text = String(0, 0, code, fontName=FONT, fontSize=7, textAnchor="end", fillColor=COLORS["body"])
            drawing.add(Group(text, transform=(0.71, 0.71, -0.71, 0.71, center + 2, bottom - 4)))
        else:
            drawing.add(String(center, bottom - 10, code, fontName=FONT, fontSize=7, textAnchor="middle",
                               fillColor=COLORS["body"]))
    drawing.add(Line(left, bottom, left + plot_w, bottom, strokeColor=COLORS["body"], strokeWidth=0.6))
    _legend(drawing, left + plot_w, height - 10,
            [(t[s], STATUS_COLORS[s]) for s in ("remaining", "expired", "served")])
    return drawing


def _timeline_chart(t: dict, details: list[dict], runs_by_course: dict[str, list[dict]],
                    inactivity_rows: dict[str, list[dict]], departure_date: date, width: float) -> Drawing:
    """ The rendement periods' served / suspended / inactive / remaining runs as a Gantt chart (oldest on top), followed
     by the rows of the periods of non-activity (see inactivity_runs), with the departure date as a dashed line and a
     gridline on every January. """
    row_h, top, bottom = 14, 22, 18
    rows = [(d["course"], runs_by_course.get(d["course"], [])) for d in details] + list(inactivity_rows.items())
    codes = [code for code, _runs in rows]
    left = max(stringWidth(code, FONT, 7) for code in codes) + 8
    plot_w, plot_h = width - left - 10, row_h * len(codes)
    height = top + plot_h + bottom
    drawing = Drawing(width, height)
    runs = [run for _code, row_runs in rows for run in row_runs]
    x0 = min([run["start"] for run in runs] + [departure_date]).toordinal()
    x1 = max([run["end"] for run in runs] + [departure_date]).toordinal()
    def x_at(d: date) -> float:
        return left + (d.toordinal() - x0) / max(x1 - x0, 1) * plot_w
    first_year, last_year = date.fromordinal(x0).year, date.fromordinal(x1).year
    year_step = math.ceil((last_year - first_year + 1) / 15)
    for year in range(first_year + 1, last_year + 1):
        x = x_at(date(year, 1, 1))
        drawing.add(Line(x, bottom, x, bottom + plot_h, strokeColor=COLORS["border"], strokeWidth=0.5))
        if (year - first_year - 1) % year_step == 0:
            drawing.add(String(x, bottom - 10, str(year), fontName=FONT, fontSize=7, textAnchor="middle",
                               fillColor=COLORS["body"]))
    for i, (code, row_runs) in enumerate(rows):
        y = bottom + plot_h - (i + 1) * row_h
        drawing.add(String(left - 4, y + row_h / 2 - 2.5, code, fontName=FONT, fontSize=7, textAnchor="end",
                           fillColor=COLORS["body"]))
        for run in row_runs:
            if run["status"] == "lapsed":
                _hatched(drawing, x_at(run["start"]), y + 2, x_at(run["end"]) - x_at(run["start"]), row_h - 4)
                continue
            drawing.add(Rect(x_at(run["start"]), y + 2, x_at(run["end"]) - x_at(run["start"]), row_h - 4,
                             fillColor=STATUS_COLORS[run["status"]], strokeColor=None))
    drawing.add(Line(left, bottom, left + plot_w, bottom, strokeColor=COLORS["body"], strokeWidth=0.6))
    x = x_at(departure_date)
    drawing.add(Line(x, bottom, x, bottom + plot_h + 4, strokeColor=colors.black, strokeWidth=0.8,
                     strokeDashArray=[3, 2]))
    drawing.add(String(x, bottom + plot_h + 6, t["departure_marker"], fontName=FONT, fontSize=7, textAnchor="middle",
                       fillColor=colors.black))
    inactive = ("inactive",) if any(run["status"] == "inactive" for run in runs) else ()
    shown = {run["status"] for run in runs}
    forgiven = tuple(s for s in ("lapsed", "expired") if s in shown)
    _legend(drawing, left + plot_w, height - 8,
            [(t[s], STATUS_COLORS[s]) for s in ("served", "suspended", *inactive, "remaining", *forgiven)])
    return drawing


def _summary_cards(cards: list[tuple[str, str, list[str]]], styles: dict) -> Table:
    """ The dashboard's metric cards, side by side: (label, value, detail lines) each. """
    cells = [[Paragraph(escape(label), styles["card_label"]), Spacer(1, 3), Paragraph(escape(value),
              styles["card_value"]), *(Paragraph(escape(line), styles["card_detail"]) for line in detail)]
             for label, value, detail in cards]
    table = Table([cells], colWidths=[CONTENT_WIDTH / len(cards)] * len(cards))
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("LINEABOVE", (0, 0), (-1, 0), 2, COLORS["info"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def build_report(rows: list[dict], departure_date: date, lang: str, source: str | None = None,
                 full_schedule: bool = False, cap_mode: str | None = None) -> bytes:
    """ The PDF report (as bytes) of the course-table rows' simulation for a departure on departure_date, with the
     rendement periods' chart as with the dashboard's switch: as they are, or as they would have been without the
     maximum total rendement period (full_schedule), and with the maximum applying as of cap_mode (as chosen in the
     dashboard, the app-wide one by default). """
    t, styles = STRINGS[lang], _styles()
    departure_str, fmt = departure_date.strftime("%d/%m/%Y"), (lambda d: d.strftime("%d/%m/%Y"))
    courses, inactivity, errors = rows_to_courses(rows, lang=lang)
    story = [
        Paragraph(escape(t["report_title"]), styles["title"]),
        Paragraph(escape(t["report_subtitle"].format(date=departure_str, today=fmt(date.today()))),
                  styles["subtitle"]),
    ]
    if source:
        story.append(Paragraph(escape(t["report_source"].format(name=source)), styles["subtitle"]))
    if errors:
        story += [Paragraph(escape(t["report_errors"]), styles["h3"]),
                  *(Paragraph(escape(error), styles["error"]) for error in errors)]
    if not courses:
        story += [Spacer(1, 12), Paragraph(escape(t["no_valid_courses"]), styles["muted"])]
        return _render(story, t, lang)
    triggering_courses, audit = determine_triggering_courses(courses)
    periods = rendement_periods(triggering_courses, inactivity, cap_mode)
    # Summary (as the dashboard's metric cards), then the plan's details.
    story.append(Paragraph(escape(t["report_summary"]), styles["h2"]))
    if not periods:
        story += [_summary_cards([(t["period_label"], "-", [t["final_date_none"]]),
                                  (t["total_label"], "0.00 €", []), (t["rate_label"], "-", [t["rate_none"]])],
                                 styles)]
    else:
        total, details = calculate_reimbursement(periods, departure_date)
        first_start, final_date = min(p.start_date for p in periods), final_rendement_completion_day(periods)
        if (active_now := active_rendement(periods, departure_date)) is None:
            rate_card = (t["rate_label"], "-", [t["rate_none"]])
        else:
            amount = active_now[1]
            pct = (amount / total * 100) if total > 0 else Decimal("0.00")
            month = f"{t['month_abbr'][departure_date.month - 1]} {departure_date:%y}"
            rate_card = (t["rate_label"], f"{amount:.2f} €", [
                t["rate_detail"].format(code=active_now[0].course.code, month=month),
                t["rate_pct"].format(pct=f"{pct:.2f}")])
        story.append(_summary_cards([
            (t["period_label"], f"{fmt(first_start)} - {fmt(final_date) if final_date else '-'}", []),
            (t["total_label"], f"{total:.2f} €", []),
            rate_card,
        ], styles))
    # Threshold test: every course, with its trailing 24-month cumulative cost against the threshold indexed at its end
    #  date (courses ended before the law applied have no test).
    audit_by_course = {id(row["course"]): row for row in audit}
    course_rows = []
    for course in courses:
        row = audit_by_course.get(id(course))
        course_rows.append([course.label, fmt(course.end_date), f"{course.price:.2f}",
                            f"{row['cumulative_cost']:.2f}" if row else "-", f"{row['threshold']:.2f}" if row else "-",
                            (t["yes"] if row["exceeds"] else t["no"]) if row else "-"])
    story += [
        Paragraph(escape(t["report_courses"]), styles["h2"]),
        _data_table([t["col_course"], t["col_end_date"], t["col_price"], t["col_window_cost"], t["col_threshold"],
                     t["col_triggers"]], course_rows, [w * CONTENT_WIDTH for w in (.2, .17, .15, .18, .17, .13)],
                    styles, numeric_cols=(2, 3, 4)),
    ]
    if not periods:
        story += [Spacer(1, 8), Paragraph(escape(t["final_date_none"]), styles["muted"])]
        return _render(story, t, lang)
    # Reimbursement per course at the departure date, with its total.
    detail_rows = []
    for d in details:
        status = detail_status(d)
        detail_rows.append([d["course"], fmt(d["rendement_start"]), f"{d['cost']:.2f}", str(d["required_months"]),
                            str(d["months_served"]), str(d["months_remaining"]), f"{d['reimbursement']:.2f}",
                            t[status] if status else t["not_taken"]])
    detail_rows.append([t["total_row"], "", "", "", "", "", f"{total:.2f}", ""])
    story += [
        Paragraph(escape(t["report_details"].format(date=departure_str)), styles["h2"]),
        _data_table([t["col_course"], t["col_rendement_start"], t["col_price"], t["col_required"], t["col_served"],
                     t["col_months_remaining"], t["col_reimbursement"], t["col_status"]], detail_rows,
                    [w * CONTENT_WIDTH for w in (.12, .12, .11, .115, .115, .115, .13, .175)], styles,
                    numeric_cols=(2, 3, 4, 5, 6), total_row=True),
    ]
    # Charts: the full suspension pyramid, recolored at the departure date (see update_charts).
    horizon = timeline_horizon(periods)
    timeline_by_course = build_period_status_timeline(periods, horizon)
    shown_timeline = (with_forgiven_runs if full_schedule else cut_off_runs)(periods, timeline_by_course)
    display_runs = {code: split_at_departure(runs, departure_date) for code, runs in shown_timeline.items()}
    story += [
        KeepTogether([Paragraph(escape(t["bar_title"].format(date=departure_date.strftime("%d/%m/%y"))),
                                styles["h2"]), _bar_chart(t, details, CONTENT_WIDTH)]),
        KeepTogether([Paragraph(escape(t["timeline_title"]), styles["h2"]),
                      _timeline_chart(t, details, display_runs, inactivity_runs(inactivity), departure_date,
                                      CONTENT_WIDTH)]),
    ]
    # How the law's criteria apply, then the criteria themselves.
    explanation = explanation_items(t, courses, triggering_courses, details, timeline_by_course, departure_date, total,
                                    inactivity, cap_mode, periods)
    story += [
        KeepTogether([Paragraph(escape(t["report_explanation"]), styles["h2"]),
                      ListFlowable([ListItem(Paragraph(escape(item), styles["body"])) for item in explanation],
                                   bulletType="1", bulletFormat="%s.", bulletFontName=FONT,
                                   bulletFontSize=9)]),
        KeepTogether([Paragraph(_linked(t["report_rules"], lang), styles["h2"]),
                      ListFlowable([ListItem(Paragraph(escape(item), styles["body"]), bulletColor=COLORS["body"])
                                    for item in t["law_criteria"]], bulletType="bullet", start="•")]),
    ]
    return _render(story, t, lang)


def _linked(text: str, lang: str) -> str:
    """ text as Paragraph markup, with the mentions of laws as hyperlinks to their official reference. """
    return "".join(f'<a href="{escape(url)}" color="{config.THEME_COLORS["info"]}">{escape(segment)}</a>' if url
                   else escape(segment) for segment, url in config.law_segments(text, lang))


def _render(story: list, t: dict, lang: str) -> bytes:
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(FONT, 7)
        canvas.setFillColor(COLORS["secondary"])
        # The footer is drawn piece by piece, so that the mentions of laws can be made clickable.
        x, y = MARGIN, MARGIN / 2
        for segment, url in config.law_segments(f"{t['app_title']} - {t['app_subtitle']}", lang):
            canvas.drawString(x, y, segment)
            width = stringWidth(segment, FONT, 7)
            if url:
                canvas.linkURL(url, (x, y - 2, x + width, y + 7), relative=1)
            x += width
        canvas.drawRightString(PAGE_WIDTH - MARGIN, MARGIN / 2, t["report_page"].format(n=doc.page))
        canvas.restoreState()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
                            bottomMargin=MARGIN, title=t["report_title"], author=t["app_title"])
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
