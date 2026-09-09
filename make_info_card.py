#!/usr/bin/env python3
"""
make_info_card.py

Hand-authored neofetch-style SVG panel: title bar + colored key/value
rows. Each line fades + slides in on a short stagger. Set STATIC=1 to
emit a frozen (already fully drawn) frame -- handy for local Quick Look
previews where SMIL doesn't animate.

    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
"""
import os

OUT_PATH = "info-card.svg"

WIDTH = 490
HEIGHT = 424

# ---- EDIT ME: this is the story the numbers in the heatmap can't tell ----
USERNAME = "dhaminiteen08"
TITLE = f"{USERNAME}@github"

ROWS = [
    ("Now", "Building things that click", "#39d353"),
    ("Prev", "Add your last role / focus here", "#26a641"),
    ("Stack", "Python · TypeScript · React · SQL", "#69f0a0"),
    ("Highlights", "Add a project or two worth bragging about", "#39d353"),
    ("Learning", "Whatever's next", "#26a641"),
]

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BAR = "#161b22"
KEY_COLOR = "#7d8590"
VAL_COLOR = "#c9d1d9"
FONT = "Menlo, Consolas, monospace"

ROW_START_Y = 70
ROW_H = 60
STAGGER = 0.35
DUR = 0.5


def esc(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main():
    static = os.environ.get("STATIC") == "1"

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # title bar
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="36" rx="10" fill="{TITLE_BAR}"/>')
    parts.append(f'<rect x="0.5" y="26.5" width="{WIDTH-1}" height="10" fill="{TITLE_BAR}"/>')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{22 + i*18}" cy="18.5" r="6" fill="{c}"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="23" text-anchor="middle" fill="{VAL_COLOR}" '
        f'font-size="13">{esc(TITLE)}</text>'
    )

    for i, (key, val, accent) in enumerate(ROWS):
        y = ROW_START_Y + i * ROW_H
        begin = i * STAGGER

        if static:
            opacity_attr = 'opacity="1"'
            transform = ""
            anim_opacity = ""
            anim_transform = ""
        else:
            opacity_attr = 'opacity="0"'
            transform = 'transform="translate(-14,0)"'
            anim_opacity = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.2f}s" dur="{DUR}s" fill="freeze"/>'
            )
            anim_transform = (
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-14 0" to="0 0" begin="{begin:.2f}s" dur="{DUR}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1"/>'
            )

        parts.append(f'<g {opacity_attr} {transform}>')
        parts.append(anim_opacity)
        parts.append(anim_transform)
        parts.append(f'<circle cx="26" cy="{y - 5}" r="4" fill="{accent}"/>')
        parts.append(
            f'<text x="42" y="{y}" fill="{KEY_COLOR}" font-size="14">{esc(key)}</text>'
        )
        parts.append(
            f'<text x="150" y="{y}" fill="{VAL_COLOR}" font-size="14">{esc(val)}</text>'
        )
        parts.append('</g>')

    parts.append('</svg>')

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote {OUT_PATH}" + (" (static frame)" if static else ""))


if __name__ == "__main__":
    main()
