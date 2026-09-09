#!/usr/bin/env python3
"""
make_ascii_svg.py

Reads prepped-source.png (grayscale, white background) and writes
avi-ascii.svg: a monochrome ASCII portrait that "types" itself in,
row by row, via SMIL animation. Prints once and freezes (no loop).

GitHub renders <img>-embedded SVGs' SMIL/CSS animation, but strips
<script>, so everything here is pure SVG/SMIL -- no JS.
"""
from PIL import Image

IN_PATH = "prepped-source.png"
OUT_PATH = "avi-ascii.svg"

COLS = 100
ROWS = 53

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.0
FILL_COLOR = "#c9d1d9"   # single light-gray fill -- monochrome on purpose

ROW_STAGGER = 0.05       # seconds between each row starting its wipe
ROW_DURATION = 0.35      # seconds for a single row to wipe in


def image_to_ascii_grid(path, cols, rows):
    img = Image.open(path).convert("L")
    img = img.resize((cols, rows), Image.LANCZOS)
    pixels = list(img.getdata())

    ramp_len = len(RAMP)
    grid = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black .. 255=white
            # invert: bright -> low density index, dark -> high density index
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        grid.append("".join(row_chars))
    return grid


def xml_escape(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(grid):
    width = COLS * CHAR_W
    height = ROWS * LINE_H + 10

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="{FONT_SIZE}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="transparent"/>')

    for r, row in enumerate(grid):
        row_escaped = "".join(xml_escape(ch) for ch in row)
        row_width = COLS * CHAR_W
        y = (r + 1) * LINE_H
        start_time = r * ROW_STAGGER

        clip_id = f"clip{r}"
        # Clip rect wipes from width 0 -> full row width, revealing text L->R
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y - LINE_H:.1f}" width="0" height="{LINE_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{row_width:.1f}" '
            f'begin="{start_time:.2f}s" dur="{ROW_DURATION}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1"/>'
            f'</rect>'
            f'</clipPath>'
        )
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y:.1f}" fill="{FILL_COLOR}" xml:space="preserve">'
            f'{row_escaped}</text>'
            f'</g>'
        )
        # small block "cursor" riding the wipe edge
        cursor_w, cursor_h = CHAR_W * 0.9, LINE_H * 0.8
        parts.append(
            f'<rect x="0" y="{y - LINE_H * 0.85:.1f}" width="{cursor_w:.1f}" '
            f'height="{cursor_h:.1f}" fill="{FILL_COLOR}" opacity="0.85">'
            f'<animate attributeName="x" from="0" to="{row_width:.1f}" '
            f'begin="{start_time:.2f}s" dur="{ROW_DURATION}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1"/>'
            f'<animate attributeName="opacity" from="0.85" to="0" '
            f'begin="{start_time + ROW_DURATION:.2f}s" dur="0.15s" fill="freeze"/>'
            f'</rect>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    grid = image_to_ascii_grid(IN_PATH, COLS, ROWS)
    svg = build_svg(grid)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    main()
