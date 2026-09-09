#!/usr/bin/env python3
"""
fetch_contributions.py

Pulls the public contribution calendar fragment GitHub itself uses on
profile pages -- no GraphQL API, no personal access token needed:

    https://github.com/users/<username>/contributions

Parses the day cells with BeautifulSoup and writes data/contributions.json
with raw days plus derived stats (current streak, longest streak, best
day, monthly totals, total).
"""
import json
import sys
from datetime import date, datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "dhaminiteen08"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = "data/contributions.json"


def fetch_html(username):
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td> with data-date + data-level,
    # or an <rect>/<td> with class "ContributionCalendar-day".
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # fallback selector in case markup changes
        cells = soup.find_all(attrs={"data-date": True})

    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        level = int(level) if level is not None else 0

        # tooltip text usually holds the count, e.g. "3 contributions on ..."
        count = 0
        tooltip_id = cell.get("id")
        tooltip = None
        if tooltip_id:
            tooltip = soup.find("tool-tip", attrs={"for": tooltip_id})
        if tooltip and tooltip.text:
            first_tok = tooltip.text.strip().split(" ")[0]
            if first_tok.isdigit():
                count = int(first_tok)
            elif first_tok.lower() == "no":
                count = 0

        days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    # current streak: consecutive days with count > 0, ending at the
    # most recent day that already has data
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch_html(username)
    days = parse_days(html)

    if not days:
        print(
            "WARNING: parsed 0 contribution days -- GitHub may have changed "
            "its markup. Check the CSS selectors in this script.",
            file=sys.stderr,
        )

    stats = compute_stats(days)
    out = {"username": username, "days": days, "stats": stats}

    import os
    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {OUT_PATH}: {len(days)} days, {stats['total']} total contributions")


if __name__ == "__main__":
    main()
