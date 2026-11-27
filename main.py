#!/usr/bin/env python3
"""Entrypoint for the news-image-20261127 make.fun entry.

Stdlib only. The entry image is rendered at build time by
render_image.py (Pillow, 100% code-drawn) and committed here as
entry.png; this program only places those exact bytes at
/output/entry.png so the grader sees them. No network, no
randomness: two runs write identical bytes.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
TARGET_DIR = "/output"
TARGET = os.path.join(TARGET_DIR, "entry.png")
BLOCK = 32768


def main():
    if not os.path.isfile(SOURCE):
        sys.stderr.write("missing source image: %s\n" % SOURCE)
        return 1
    os.makedirs(TARGET_DIR, exist_ok=True)
    digest = hashlib.sha256()
    total = 0
    with open(SOURCE, "rb") as src, open(TARGET, "wb") as dst:
        while True:
            chunk = src.read(BLOCK)
            if not chunk:
                break
            digest.update(chunk)
            dst.write(chunk)
            total += len(chunk)
    sys.stdout.write(
        "wrote %s (%d bytes, sha256 %s)\n" % (TARGET, total, digest.hexdigest())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
