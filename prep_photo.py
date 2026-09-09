#!/usr/bin/env python3
"""
prep_photo.py <source-photo.jpg>

Prepares a photo for ASCII conversion:
  1. Remove the background with rembg so only the subject remains.
  2. Boost local contrast with CLAHE so a flatly-lit face gets real
     highlights and shadows (flat lighting -> unreadable ASCII blob).
  3. Composite onto pure white, so the background maps to the blank
     end of the ASCII ramp (white -> space character).

Output: prepped-source.png (grayscale, ready for make_ascii_svg.py)
Run this once per photo -- it doesn't need to be part of the daily
automation.
"""
import sys
import io

import numpy as np
import cv2
from PIL import Image
from rembg import remove

OUT_PATH = "prepped-source.png"


def main():
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = sys.argv[1]

    with open(src_path, "rb") as f:
        input_bytes = f.read()

    # 1. Remove background -> RGBA PNG bytes
    result_bytes = remove(input_bytes)
    rgba = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # 2. Composite onto pure white using the alpha mask
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. Convert to grayscale, then apply CLAHE for local contrast
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrast_boosted = clahe.apply(gray)

    # Re-flatten background to pure white: anything that was background
    # (fully white before CLAHE) can get slightly perturbed by CLAHE, so
    # snap near-white pixels back to 255 using the original alpha mask.
    alpha = np.array(rgba)[:, :, 3]
    contrast_boosted = np.where(alpha < 10, 255, contrast_boosted).astype(np.uint8)

    out_img = Image.fromarray(contrast_boosted, mode="L")
    out_img.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({out_img.size[0]}x{out_img.size[1]})")


if __name__ == "__main__":
    main()
