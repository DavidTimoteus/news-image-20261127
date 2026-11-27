[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/DavidTimoteus/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/DavidTimoteus/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# news-image-20261127 — v1

**Bounty:** make.fun `news-image-20261127` — "Sum up 27 November's
world news in one image"
**File:** `entry.png` — 1024×1024 RGB, 193,355 bytes (≤1 MiB)
**SHA-256:** `dc42d90959f810190af226c17d9d8b14279e8955660c6f049718caa0c7ccdf86`
**Build:** `python3 render_image.py` (100% code-drawn Pillow, no AI
image generation). Deterministic: rendered 2×, byte-identical.
**Status:** v1 — early edition of Friday 27 November 2026.

## The day in one line

Asia's markets edge up, Thanksgiving storms cut power to 900,000+ —
and Trump presses Putin in China.

## Contents

- `main.py` — entrypoint (stdlib only): copies `entry.png` to
  `/output/entry.png`
- `render_image.py` — fresh renderer for this day (broadsheet style)
- `entry.png` — the v1 image
- `RESEARCH.md` — story list, region counts, numbers, timeline,
  left-out list, honest limits of this early build
- `SOURCES.md` — per-story verification (outlet + date/time) for
  all 32 stories; zero fictional sources
- `DESIGN_NOTES.md` — how each audit lesson was applied, and the
  defects found + fixed during visual QA

## Numbers

- **32 stories** (3 leads + 9 illustrated cards + 20 also-on),
  **9 regions**: Europe 8 · Middle East 6 · N. America 5 ·
  East Asia 4 · South Asia 3 · SE Asia 2 · Oceania 2 · Africa 1 ·
  Global 1.
- **3 leads:** Asia markets up (Nikkei +0.4%); Thanksgiving
  storms (900,000+ without power); Trump pressed Putin in China.
- 6 numbers + 6-point UTC timeline (first hour of Friday) +
  world map with 12 numbered pins + boxed date-check panel.
- Trust chips on every featured story (green OFFICIAL, blue
  CONFIRMED, orange REPORTED, red CLAIM); ALSO ON in 2 columns.

## Early-edition honesty

This v1 was built from reports available ~00:40–02:00 UTC on
27 Nov (timeline = first hour of Friday UTC, plus Asia-Pacific
Friday-morning editions). Two ALSO ON items (Iowa Army blast,
Indiana drone fireball) are dated from the BBC 27 Nov 00:18 UTC
front-page edition rather than a standalone timestamp — see
RESEARCH.md "Risks". Nothing in the image is invented: every
story names its outlet and first-report date in SOURCES.md.
