#!/usr/bin/env python3
"""
fetch_avatar.py

Optional helper: if you don't have a local photo handy, this pulls your
current GitHub avatar (public, no token needed) and saves it as
source-photo.jpg so you can run prep_photo.py on it right away.

You can swap this out later for a better/higher-res photo whenever you like.
"""
import sys
import requests

USERNAME = "dhaminiteen08"
OUT_PATH = "source-photo.jpg"


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    api_url = f"https://api.github.com/users/{username}"
    resp = requests.get(api_url, timeout=15)
    resp.raise_for_status()
    avatar_url = resp.json()["avatar_url"]

    img_resp = requests.get(avatar_url, timeout=15)
    img_resp.raise_for_status()

    with open(OUT_PATH, "wb") as f:
        f.write(img_resp.content)

    print(f"Saved avatar for '{username}' -> {OUT_PATH}")
    print("Tip: a higher-res, well-lit face photo will convert to nicer ASCII "
          "than a small profile thumbnail. Swap the file out anytime.")


if __name__ == "__main__":
    main()
