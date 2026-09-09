#!/usr/bin/env python3
"""
render_heatmap_svg.py

Reads data/contributions.json and draws the classic 53-week x 7-day
contribution calendar as rounded, colored boxes. Reveals once with a
diagonal, line-after-line slide-down (plays on load, then freezes --
no looping). Adds a Less->More legend and a stats footer.

Output: contrib-heatmap.svg (width 860, matching the two README
columns: 370 + 490 = 860, so edges line up).
"""
import json

IN_PATH = "data/contributions.json"
OUT_PATH = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

CELL = 11
GAP = 3
LEFT_PAD = 30      # room for day labels
TOP_PAD = 40        # room for month labels
BOTTOM_PAD = 46      # room for legend + stats footer
WIDTH = 860
BG = "#0d1117"
TEXT_COLOR = "#7d8590"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

COL_STAGGER = 0.03
ROW_STAGGER = 0.015
DUR = 0.35


def level_to_color(level):
    level = max(0, min(5, level))
    return PALETTE[level]


def build_weeks(days):
    """Group days into weeks (columns) the way GitHub's calendar does:
    each column is a week starting Sunday."""
    if not days:
        return []

    by_date = {d["date"]: d for d in days}
    dates = sorted(by_date.keys())
    first = dates[0]
    last = dates[-1]

    import datetime as dt
    start = dt.date.fromisoformat(first)
    end = dt.date.fromisoformat(last)

    # back up 'start' to the previous Sunday so weeks align
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cur_week = []
    d = start
    while d <= end:
        key = d.isoformat()
        entry = by_date.get(key, {"date": key, "level": 0, "count": 0})
        cur_week.append(entry)
        if d.weekday() == 5:  # Saturday -> close out the week
            weeks.append(cur_week)
            cur_week = []
        d += dt.timedelta(days=1)
    if cur_week:
        weeks.append(cur_week)

    return weeks


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    with open(IN_PATH) as f:
        data = json.load(f)

    days = data.get("days", [])
    stats = data.get("stats", {})
    username = data.get("username", "")

    weeks = build_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}" rx="8"/>')

    # day-of-week labels (Mon, Wed, Fri)
    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for dow, label in day_labels.items():
        y = TOP_PAD + dow * (CELL + GAP) + CELL - 1
        parts.append(
            f'<text x="{LEFT_PAD - 8}" y="{y}" text-anchor="end" '
            f'fill="{TEXT_COLOR}" font-size="9">{label}</text>'
        )

    # month labels: mark the first week column whose first day falls in
    # a new month
    last_month = None
    for wi, week in enumerate(weeks):
        first_day = week[0]["date"]
        month = int(first_day[5:7])
        if month != last_month:
            x = LEFT_PAD + wi * (CELL + GAP)
            parts.append(
                f'<text x="{x}" y="{TOP_PAD - 8}" fill="{TEXT_COLOR}" '
                f'font-size="9">{MONTH_NAMES[month - 1]}</text>'
            )
            last_month = month

    # boxes
    for wi, week in enumerate(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        for di, day in enumerate(week):
            y = TOP_PAD + di * (CELL + GAP)
            color = level_to_color(day["level"])
            begin = wi * COL_STAGGER + di * ROW_STAGGER
            title = f'{day["count"]} contributions on {day["date"]}'
            parts.append(
                f'<rect x="{x}" y="{y - 8}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<title>{esc(title)}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.3f}s" dur="{DUR}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y-8}" to="{y}" '
                f'begin="{begin:.3f}s" dur="{DUR}s" fill="freeze" '
                f'calcMode="spline" keySplines="0.3 0 0.2 1"/>'
                f'</rect>'
            )

    # legend: Less -> More
    legend_y = height - BOTTOM_PAD + 24
    legend_x = LEFT_PAD
    parts.append(
        f'<text x="{legend_x}" y="{legend_y + 8}" fill="{TEXT_COLOR}" '
        f'font-size="10">Less</text>'
    )
    lx = legend_x + 30
    for color in PALETTE:
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}"/>'
        )
        lx += CELL + GAP
    parts.append(
        f'<text x="{lx + 4}" y="{legend_y + 8}" fill="{TEXT_COLOR}" '
        f'font-size="10">More</text>'
    )

    # stats footer
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = f"{total:,} contributions in the last year · streak {streak}d · longest {longest}d"
    parts.append(
        f'<text x="{WIDTH - LEFT_PAD}" y="{legend_y + 8}" text-anchor="end" '
        f'fill="{TEXT_COLOR}" font-size="10">{esc(footer)}</text>'
    )

    parts.append('</svg>')

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH}: {n_weeks} weeks, total={total}")


if __name__ == "__main__":
    main()
