#!/usr/bin/env python3
"""news-image-20261127 v1 — "Friday 27 November 2026" early edition.

Fresh renderer written for this bounty day (27 Nov 2026). Applies the
lessons of the 25/26 Nov audits + final Round 4 audit:
  * giant date headline = largest element on the page
  * 32 stories (3 leads + 9 illustrated cards + 20 ALSO ON, 2 columns)
  * solid colour trust chips on every lead/card; colour squares on ALSO ON
  * map block ~38% of content width, numbered pins 1-12
  * date check = boxed panel with HOW SURE legend + LEFT OUT list
  * WHY IT MATTERS under each lead; hero art carries data in the picture
  * region ribbon with coloured chips + counts near the top
  * 300px legibility test required before submit (see thumb300.png)
Style: editorial broadsheet, cream paper, ink, one muted red.
Deterministic: no timestamps, no randomness, fixed font paths.
1024x1024 RGB, saved as output/entry.png; <= 1 MiB target.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28
CW = W - 2 * M
PAPER = (245, 240, 225)
INK = (26, 26, 26)
RED = (166, 25, 46)
MUTED = (95, 89, 77)
FAINT = (120, 114, 100)
LAND = (227, 217, 190)
SEA = (214, 227, 231)
BLUE = (47, 93, 107)
GOLD = (146, 106, 0)
GREEN = (27, 120, 60)      # OFFICIAL chip
CBLUE = (30, 90, 160)      # CONFIRMED chip
ORANGE = (198, 108, 0)     # REPORTED chip
CREED = (178, 32, 32)      # CLAIM chip
PURPLE = (110, 60, 150)    # ONGOING chip

CHIP_FILL = {"OFFICIAL": GREEN, "CONFIRMED": CBLUE, "REPORTED": ORANGE,
             "CLAIM": CREED, "ONGOING": PURPLE}

FD = "/usr/share/fonts/truetype"
SERIF_BLACK = f"{FD}/noto/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FD}/noto/NotoSerif-Bold.ttf"
SERIF = f"{FD}/noto/NotoSerif-Regular.ttf"
SERIF_IT = f"{FD}/noto/NotoSerif-Italic.ttf"
SANS = f"{FD}/dejavu/DejaVuSans.ttf"
SANS_B = f"{FD}/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit(draw, text, fnt, max_w, max_lines, what):
    lines = wrap(draw, text, fnt, max_w)
    assert len(lines) <= max_lines, f"{what}: {len(lines)} lines > {max_lines}: {lines}"
    return lines


def rule(draw, x, y, w, fill=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


def small_caps(draw, text, x, y, size=8, fill=MUTED, fnt=None):
    f = fnt or font(SANS_B, size)
    draw.text((x, y), text.upper(), font=f, fill=fill)
    return draw.textlength(text.upper(), font=f)


def chip(draw, x, y, label):
    """Solid colour trust chip; returns width used."""
    f = font(SANS_B, 8)
    w = draw.textlength(label, font=f) + 10
    draw.rectangle([x, y, x + w, y + 12], fill=CHIP_FILL[label])
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def chip_square(draw, x, y, label, s=8):
    draw.rectangle([x, y, x + s, y + s], fill=CHIP_FILL[label])


# ---------------------------------------------------------------- data
LEADS = [
    dict(num=1, region="EAST ASIA", trust="CONFIRMED",
         head="Asia edges up on Black Friday as Nikkei climbs",
         body="Nikkei +0.4% to 57,754 in early Tokyo trade; banks and trading houses lead. Kospi +13.70 to 4,711.",
         why="WHY IT MATTERS — The AI sell-off pauses as dip buyers return.",
         src="WSJ  ·  YONHAP INFOMAX", art="chart"),
    dict(num=2, region="NORTH AMERICA", trust="CONFIRMED",
         head="Thanksgiving storms leave 900,000+ in the dark",
         body="Severe weather snarls air travel across the US on the holiday; roofs torn off, streets under water.",
         why="WHY IT MATTERS — Peak travel day meets peak storm.",
         src="BBC", art="storm"),
    dict(num=3, region="GLOBAL", trust="CONFIRMED",
         head="Trump says he pressed Putin in China to end aggression",
         body="Trump says he urged Putin to pull back \u2018all military aggression\u2019 in Europe; he also spoke to NATO chief Rutte.",
         why="WHY IT MATTERS — Washington tests Beijing as go-between.",
         src="MULTIPLE OUTLETS", art="diplomacy"),
]

CARDS = [
    dict(num=4, region="MIDDLE EAST", trust="REPORTED",
         head="Katz warns Gaza operation may displace 1,000,000",
         body="Israel\u2019s defence minister warns of a coming operation in Gaza.",
         src="ISRAELI MEDIA", art="gaza", banner="1,000,000 AT RISK"),
    dict(num=5, region="EUROPE", trust="REPORTED",
         head="Zelensky warns of a \u2018massive\u2019 Russian strike soon",
         body="Kyiv says Moscow is readying a large-scale attack as winter nears.",
         src="UKRAINIAN OUTLETS", art="kyiv", banner="\u2018MASSIVE\u2019 STRIKE"),
    dict(num=6, region="EAST ASIA", trust="CLAIM",
         head="Kim escalates nuclear drive after spurning Trump",
         body="Pyongyang vows wider nuclear arms; Kyiv says its aid to Russia is cut.",
         src="KCNA  ·  UKR INTEL", art="pyongyang", banner="NUCLEAR DRIVE"),
    dict(num=7, region="OCEANIA", trust="CONFIRMED",
         head="New Zealand 77-1 at lunch, 2nd Test v India",
         body="Day one in Christchurch: India won the toss and chose to field.",
         src="REUTERS", art="cricket", banner="77-1 AT LUNCH"),
    dict(num=8, region="SOUTH ASIA", trust="REPORTED",
         head="Four dead, 17 missing as Karachi building falls",
         body="A six-storey building collapsed; rescuers search the rubble.",
         src="PAKISTANI MEDIA", art="karachi", banner="4 DEAD \u00b7 17 MISSING"),
    dict(num=9, region="SE ASIA", trust="CONFIRMED",
         head="Nine hurt, three critically, in Bangkok refinery blast",
         body="An explosion at an oil refinery injures nine workers.",
         src="BBC", art="bangkok", banner="9 INJURED"),
    dict(num=10, region="EUROPE", trust="CONFIRMED",
         head="Diesel tanker capsizes near Ibiza; one killed",
         body="A tanker carrying up to 7,000 tonnes of diesel went down off Ibiza.",
         src="BBC", art="ibiza", banner="7,000 TONNES"),
    dict(num=11, region="EUROPE", trust="OFFICIAL",
         head="UK car output +4.8% in October to 64,141",
         body="SMMT: car making recovers after last year\u2019s cyber halt at JLR.",
         src="REUTERS  ·  SMMT", art="auto", banner="+4.8% IN OCTOBER"),
    dict(num=12, region="SE ASIA", trust="CONFIRMED",
         head="Duterte ICC trial set to start on Monday",
         body="Families seek justice as the ex-president faces 85 murder counts.",
         src="REUTERS", art="icc", banner="TRIAL MON 30 NOV"),
]

# (num, headline, source, trust)
ALSO = [
    (13, "Black Friday: cautious shoppers; holiday sales seen +4.2% to $1tn", "REUTERS", "CONFIRMED"),
    (14, "Michigan State beats Arkansas 70-67 on Thanksgiving Day", "REUTERS", "CONFIRMED"),
    (15, "Sandpapergate forum will not assign blame to anyone", "REUTERS", "CONFIRMED"),
    (16, "Serbia sets presidential election for 27 December", "AGGREGATOR", "REPORTED"),
    (17, "Hong Kong marks 1 year since tower fire that killed 168", "AGGREGATOR", "REPORTED"),
    (18, "China launches new batch of Earth-observation satellites", "AGGREGATOR", "REPORTED"),
    (19, "UN trade agency backs Palestinian economic recovery, aid", "UNCTAD", "OFFICIAL"),
    (20, "Lithuania detains 5 suspected of working with VGTRK", "AGGREGATOR", "REPORTED"),
    (21, "Iraq sentences 8 French IS militants to life in prison", "AGGREGATOR", "REPORTED"),
    (22, "US hails Syria over Captagon seizures, Iranian arms haul", "AGGREGATOR", "REPORTED"),
    (23, "Kenya: KWS officers convicted over fisherman Brian Odhiambo", "DAILY NATION", "CONFIRMED"),
    (24, "India: Cessna crash in Hyderabad injures two; food labels ordered", "DECCAN CHRONICLE", "CONFIRMED"),
    (25, "Bangladesh garment workers tear-gassed in wage protest", "AGGREGATOR", "REPORTED"),
    (26, "ECB picks Pablo Hern\u00e1ndez de Cos as next top official", "AGGREGATOR", "REPORTED"),
    (27, "Trump, NATO chief Rutte talk Ukraine, Iran, funding", "AGGREGATOR", "REPORTED"),
    (28, "Taylor, longtime Duran Duran guitarist, dies aged 65", "AGGREGATOR", "REPORTED"),
    (29, "US Army controlled blast of explosives in Iowa a \u2018huge success\u2019", "BBC", "CONFIRMED"),
    (30, "Fireball steals show at Thanksgiving drone display in Indiana", "BBC", "CONFIRMED"),
    (31, "Kushner urges Israel to drop \u2018permanent war mindset\u2019", "AGGREGATOR", "REPORTED"),
    (32, "Iraq chief judge to convene dialogue on Erbil\u2013Baghdad rows", "AGGREGATOR", "REPORTED"),
]

NUMBERS = [
    ("57,754", "Nikkei 225, +0.4%\nearly Friday (WSJ)"),
    ("4,711", "Kospi close, +13.70\nin Friday memo (Yonhap)"),
    ("$83.68", "WTI crude, closed\n(Yonhap memo)"),
    ("900,000+", "without power in US\nThanksgiving storms (BBC)"),
    ("4 + 17", "dead and missing\nin Karachi collapse"),
    ("168", "killed in Hong Kong\ntower fire, 1 year on"),
]

TIMELINE = [
    ("00:06", "Reuters: UK car output +4.8% in October"),
    ("00:15", "WSJ: Nikkei +0.4% in early Tokyo trade"),
    ("00:17", "Gaza drone strike kills three; ECB picks de Cos"),
    ("00:20", "Reuters: NZ 77-1 at lunch v India"),
    ("00:38", "Zelensky warns of \u2018massive\u2019 Russian strike"),
    ("00:54", "Karachi collapse: 4 dead, 17 missing"),
]

REGIONS = [
    ("EUROPE", 8, CBLUE), ("MIDDLE EAST", 6, CREED), ("N. AMERICA", 5, (0, 120, 120)),
    ("EAST ASIA", 4, GOLD), ("SOUTH ASIA", 3, PURPLE), ("SE ASIA", 2, GREEN),
    ("OCEANIA", 2, (30, 60, 120)), ("AFRICA", 1, (140, 90, 40)), ("GLOBAL", 1, MUTED),
]

PINS = [
    (1, 139.69, 35.68, 0, -4),    # Tokyo
    (2, -77.0, 39.0, 0, 0),      # Washington DC (storms)
    (3, 116.40, 39.90, 0, -4),   # Beijing
    (4, 34.45, 31.50, 0, 0),     # Gaza
    (5, 30.52, 50.45, 0, -4),    # Kyiv
    (6, 125.75, 39.03, 0, 0),    # Pyongyang
    (7, 172.64, -43.53, 0, 0),   # Christchurch
    (8, 67.00, 24.86, 0, 0),     # Karachi
    (9, 100.50, 13.75, 0, 0),    # Bangkok
    (10, 1.42, 38.98, 0, -6),    # Ibiza
    (11, -0.12, 51.50, 0, -8),   # London
    (12, 4.32, 52.08, 0, -4),    # The Hague (ICC)
]

# coarse schematic continents (lon, lat) — drawn fresh, simplified
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-105, 72), (-90, 74), (-82, 73), (-76, 62),
     (-65, 60), (-60, 52), (-65, 45), (-70, 42), (-75, 35), (-81, 31), (-84, 30),
     (-90, 29), (-97, 26), (-97, 22), (-105, 20), (-95, 16), (-86, 13), (-83, 9),
     (-90, 14), (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-124, 40),
     (-125, 49), (-135, 58), (-150, 60), (-165, 60), (-168, 66)],
    [(-80, 9), (-77, 7), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-70, -52),
     (-73, -44), (-73, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 0), (-80, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70), (40, 68),
     (45, 68), (50, 69), (55, 68), (60, 69), (68, 73), (75, 72), (80, 73),
     (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 70), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 59),
     (142, 55), (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
     (122, 28), (115, 22), (110, 20), (108, 12), (105, 9), (100, 7), (98, 12),
     (95, 16), (92, 21), (89, 22), (86, 20), (80, 13), (77, 8), (75, 15),
     (72, 20), (68, 23), (62, 25), (57, 26), (52, 28), (50, 30), (48, 30),
     (44, 29), (40, 32), (36, 36), (30, 36), (26, 38), (23, 36), (20, 40),
     (18, 42), (14, 45), (10, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37), (-10, 36)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 21),
     (43, 12), (48, 11), (51, 12), (44, 2), (41, -2), (40, -10), (40, -18),
     (36, -26), (32, -29), (28, -33), (20, -35), (18, -32), (15, -27),
     (12, -18), (13, -12), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
]


# ---------------------------------------------------------------- art
def art_chart(d, x, y, w, h):
    """Hero 1: Asia markets bar chart with real Friday values."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    d.text((x + 8, y + 4), "ASIA OPENS HIGHER — % CHANGE, FRI", font=font(SANS_B, 7), fill=MUTED)
    bars = [("NIKKEI", 0.4, "+0.4%"), ("KOSPI", 0.3, "+0.3%"), ("KOSDAQ", 0.8, "+0.8%")]
    base = y + h - 20
    bw = 46
    gap = (w - 3 * bw - 16) / 4
    for i, (lab, v, txt) in enumerate(bars):
        bx = x + 8 + gap + i * (bw + gap)
        bh = max(6, (h - 40) * v / 0.8)
        d.rectangle([bx, base - bh, bx + bw, base], fill=RED if i == 0 else INK)
        d.text((bx, base - bh - 11), txt, font=font(SANS_B, 8), fill=INK)
        d.text((bx, base + 4), lab, font=font(SANS_B, 7), fill=MUTED)
    d.line([(x + 6, base), (x + w - 6, base)], fill=INK, width=1)


def art_storm(d, x, y, w, h):
    """Hero 2: schematic US with storm swirls + outage callout."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=1)
    us = [(0.06, 0.28), (0.10, 0.14), (0.30, 0.10), (0.55, 0.12), (0.80, 0.16),
          (0.94, 0.28), (0.90, 0.45), (0.82, 0.55), (0.70, 0.62), (0.55, 0.78),
          (0.40, 0.85), (0.25, 0.80), (0.12, 0.65), (0.05, 0.45), (0.06, 0.28)]
    d.polygon([(x + px * w, y + py * h) for px, py in us], fill=LAND, outline=INK)
    # storm swirls over the east
    for (cx, cy, r) in [(0.72, 0.38, 13), (0.58, 0.30, 10), (0.84, 0.52, 9)]:
        px, py = x + cx * w, y + cy * h
        d.arc([px - r, py - r, px + r, py + r], 20, 300, fill=BLUE, width=3)
        d.arc([px - r // 2, py - r // 2, px + r // 2, py + r // 2], 200, 120, fill=BLUE, width=2)
    d.text((x + 6, y + 4), "THANKSGIVING", font=font(SANS_B, 7), fill=BLUE)
    bx, by = x + 6, y + h - 24
    d.rectangle([bx, by, bx + 168, by + 18], fill=INK)
    d.text((bx + 6, by + 4), "900,000+ WITHOUT POWER", font=font(SANS_B, 8), fill=PAPER)


def art_diplomacy(d, x, y, w, h):
    """Hero 3: Beijing-Moscow-Washington triangle with the quote."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    nodes = [(0.22, 0.25, "BEIJING"), (0.78, 0.22, "MOSCOW"), (0.50, 0.34, "WASHINGTON")]
    pts = []
    for (px, py, lab) in nodes:
        cx, cy = x + px * w, y + py * h
        pts.append((cx, cy))
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED, outline=PAPER, width=1)
        d.text((cx - d.textlength(lab, font=font(SANS_B, 7)) / 2, cy + 8),
               lab, font=font(SANS_B, 7), fill=INK)
    for a, b in [(0, 1), (0, 2)]:
        d.line([pts[a], pts[b]], fill=BLUE, width=2)
    # arrowhead on Beijing->Moscow
    d.polygon([(pts[1][0] - 12, pts[1][1] - 4), (pts[1][0] - 12, pts[1][1] + 4),
               (pts[1][0] - 2, pts[1][1])], fill=BLUE)
    d.text((x + 6, y + 4), "SUMMIT WEEK — CHINA", font=font(SANS_B, 7), fill=MUTED)
    bx, by = x + 6, y + h - 18
    d.rectangle([bx, by, bx + 196, by + 14], fill=INK)
    d.text((bx + 6, by + 3), "\u2018PULL BACK ALL AGGRESSION\u2019", font=font(SANS_B, 8), fill=PAPER)


def art_card(d, x, y, w, h, kind, banner):
    d.rectangle([x, y, x + w, y + h], fill=SEA if kind in ("ibiza",) else PAPER,
                outline=INK, width=1)
    cx, cy = x + w / 2, y + h / 2
    if kind == "gaza":
        d.polygon([(cx, y + 6), (cx + 16, y + 34), (cx - 16, y + 34)], fill=CREED, outline=INK)
        d.text((cx - 3, y + 16), "!", font=font(SANS_B, 12), fill=PAPER)
        d.text((cx + 20, y + 18), "GAZA", font=font(SANS_B, 8), fill=INK)
    elif kind == "kyiv":
        for r in (6, 10, 14):
            d.arc([cx - r, cy - 2 - r, cx + r, cy - 2 + r], 200, 340, fill=RED, width=2)
        d.ellipse([cx - 4, cy - 6, cx + 4, cy + 2], fill=RED)
    elif kind == "pyongyang":
        for r in (7, 12, 17):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=1)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
        d.text((cx + 20, cy - 4), "N. KOREA", font=font(SANS_B, 7), fill=INK)
    elif kind == "cricket":
        d.line([(cx - 24, cy + 12), (cx + 10, cy - 14)], fill=(139, 69, 19), width=5)
        d.ellipse([cx + 10, cy - 18, cx + 22, cy - 6], fill=CREED, outline=INK, width=1)
        d.text((x + 6, y + 4), "CHRISTCHURCH", font=font(SANS_B, 7), fill=INK)
    elif kind == "karachi":
        d.polygon([(x + 22, y + 8), (x + 62, y + 8), (x + 58, y + h - 8), (x + 26, y + h - 8)],
                  fill=LAND, outline=INK, width=2)
        d.line([(x + 22, y + 8), (x + 40, y + h - 8)], fill=RED, width=2)
        for i in range(3):
            d.rectangle([x + 30 + i * 9, y + 14, x + 36 + i * 9, y + 20], fill=INK)
        d.text((x + 70, y + 14), "6 STOREYS", font=font(SANS_B, 7), fill=INK)
    elif kind == "bangkok":
        d.polygon([(cx, y + 6), (cx + 12, y + 22), (cx + 6, y + 30), (cx + 14, y + 38),
                   (cx, y + h - 6), (cx - 14, y + 38), (cx - 6, y + 30), (cx - 12, y + 22)],
                  fill=ORANGE, outline=CREED)
        d.text((cx + 18, y + 16), "REFINERY", font=font(SANS_B, 7), fill=INK)
    elif kind == "ibiza":
        d.polygon([(x + 20, y + 26), (x + w - 20, y + 26), (x + w - 34, y + 38),
                   (x + 34, y + 38)], fill=INK)
        d.rectangle([x + 40, y + 12, x + 62, y + 26], fill=RED, outline=INK, width=1)
    elif kind == "auto":
        d.polygon([(x + 140, y + 22), (x + 160, y + 12), (x + 200, y + 12), (x + 220, y + 20),
                   (x + 232, y + 24), (x + 232, y + 28), (x + 140, y + 28)], fill=RED, outline=INK)
        d.ellipse([x + 154, y + 26, x + 166, y + 36], fill=INK)
        d.ellipse([x + 204, y + 26, x + 216, y + 36], fill=INK)
        d.text((x + 238, y + 14), "UK", font=font(SANS_B, 9), fill=INK)
    elif kind == "icc":
        d.line([(cx, y + 8), (cx, y + 36)], fill=INK, width=2)
        d.line([(cx - 20, y + 12), (cx + 20, y + 12)], fill=INK, width=2)
        d.arc([cx - 26, y + 12, cx - 14, y + 26], 0, 180, fill=GOLD, width=2)
        d.arc([cx + 14, y + 12, cx + 26, y + 26], 0, 180, fill=GOLD, width=2)
        d.line([(cx - 24, y + 34), (cx + 24, y + 34)], fill=INK, width=2)
        d.text((cx + 28, y + 16), "THE HAGUE", font=font(SANS_B, 7), fill=INK)
    bw = d.textlength(banner, font=font(SANS_B, 8)) + 12
    bx, by = x + 6, y + h - 19
    d.rectangle([bx, by, bx + bw, by + 14], fill=INK)
    d.text((bx + 6, by + 3), banner, font=font(SANS_B, 8), fill=PAPER)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8
    # top bar
    small_caps(d, "Friday 27 November 2026  ·  Early edition  ·  All times UTC unless stated",
               M, y, size=9, fill=INK)
    r = d.textlength("32 STORIES  ·  9 REGIONS", font=font(SANS_B, 9))
    d.text((W - M - r, y), "32 STORIES  ·  9 REGIONS", font=font(SANS_B, 9), fill=INK)
    y = 26
    rule(d, M, y, CW, width=2)
    # masthead (small) + GIANT date headline
    mf = font(SERIF_BLACK, 20)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(t, font=mf)) / 2, 30), t, font=mf, fill=INK)
    df = font(SERIF_BLACK, 52)
    dt = "Friday 27 November 2026"
    d.text(((W - d.textlength(dt, font=df)) / 2, 54), dt, font=df, fill=RED)
    # sub-headline
    sf = font(SERIF_IT, 14)
    sub = ("Asia climbs into Black Friday, Thanksgiving storms cut power to 900,000+ \u2014 "
           "and Trump presses Putin in China.")
    d.text(((W - d.textlength(sub, font=sf)) / 2, 120), sub, font=sf, fill=INK)
    # region ribbon
    ry = 138
    rx = M
    for (name, n, col) in REGIONS:
        lab = f"{name} {n}"
        f = font(SANS_B, 8)
        w = d.textlength(lab, font=f) + 16
        d.rounded_rectangle([rx, ry, rx + w, ry + 15], radius=7, fill=col)
        d.text((rx + 8, ry + 3), lab, font=f, fill=(255, 255, 255))
        rx += w + 6
    assert rx <= W - M, f"region ribbon overflows: {rx}"
    rule(d, M, 160, CW, width=1)

    # ---- Day in Numbers
    y = 166
    small_caps(d, "The day in numbers", M, y, size=9, fill=RED)
    y = 180
    colw = CW / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = M + i * colw
        nf = font(SERIF_BOLD, 25)
        d.text((cx, y), num, font=nf, fill=INK)
        for j, ln in enumerate(lab.split("\n")):
            d.text((cx, y + 29 + j * 10), ln, font=font(SANS, 8), fill=MUTED)
        if i:
            d.line([(cx - 7, y + 2), (cx - 7, y + 44)], fill=FAINT, width=1)
    rule(d, M, 228, CW, width=1)

    # ---- Timeline (first hour of Friday UTC)
    y = 234
    small_caps(d, "Timeline \u2014 UTC  ·  first hour", M, y, size=9, fill=RED)
    tw = (CW - 200) / 6
    for i, (tm, txt) in enumerate(TIMELINE):
        tx = M + 200 + i * tw
        d.text((tx, y), tm, font=font(SANS_B, 9), fill=RED)
        lines = fit(d, txt, font(SANS, 8), tw - 8, 2, f"timeline {tm}")
        draw_lines(d, lines, tx, y + 12, font(SANS, 8), INK, 10)
    rule(d, M, 272, CW, width=1)

    # ---- Leads
    hy, hh = 278, 160
    hw = (CW - 2 * 14) / 3
    for i, ld in enumerate(LEADS):
        hx = M + i * (hw + 14)
        d.text((hx, hy), str(ld["num"]), font=font(SERIF_BOLD, 13), fill=RED)
        cw_ = chip(d, hx + 16, hy + 1, ld["trust"])
        small_caps(d, ld["region"], hx + 16 + cw_ + 6, hy + 3, size=8)
        lines = fit(d, ld["head"], font(SERIF_BOLD, 16), hw, 2, f"lead {ld['num']}")
        draw_lines(d, lines, hx, hy + 17, font(SERIF_BOLD, 16), INK, 19)
        ay = hy + 17 + len(lines) * 19 + 4
        ah = 52
        if ld["art"] == "chart":
            art_chart(d, hx, ay, hw, ah)
        elif ld["art"] == "storm":
            art_storm(d, hx, ay, hw, ah)
        else:
            art_diplomacy(d, hx, ay, hw, ah)
        by = ay + ah + 5
        blines = fit(d, ld["body"], font(SANS, 9), hw, 2, f"lead body {ld['num']}")
        draw_lines(d, blines, hx, by, font(SANS, 9), INK, 11)
        wy = by + len(blines) * 11 + 3
        wlines = fit(d, ld["why"], font(SANS_B, 8), hw, 1, f"lead why {ld['num']}")
        draw_lines(d, wlines, hx, wy, font(SANS_B, 8), RED, 10)
        small_caps(d, ld["src"], hx, wy + 11, size=7)
        assert wy + 18 <= hy + hh, f"lead {ld['num']} overflows"
    rule(d, M, hy + hh + 6, CW, width=1)

    # ---- Cards (3 rows x 3)
    cw = (CW - 2 * 12) / 3
    ch = 108
    for row in range(3):
        cy0 = 452 + row * (ch + 6)
        for col in range(3):
            c = CARDS[row * 3 + col]
            cx = M + col * (cw + 12)
            rule(d, cx, cy0, cw, fill=INK, width=2)
            d.text((cx, cy0 + 4), str(c["num"]), font=font(SERIF_BOLD, 11), fill=RED)
            cw_ = chip(d, cx + 15, cy0 + 5, c["trust"])
            small_caps(d, c["region"], cx + 15 + cw_ + 6, cy0 + 7, size=7)
            lines = fit(d, c["head"], font(SERIF_BOLD, 12), cw, 2, f"card {c['num']}")
            draw_lines(d, lines, cx, cy0 + 19, font(SERIF_BOLD, 12), INK, 13)
            ay = cy0 + 19 + len(lines) * 13 + 3
            ah = 38
            art_card(d, cx, ay, cw, ah, c["art"], c["banner"])
            by = ay + ah + 3
            blines = fit(d, c["body"], font(SANS, 8), cw, 1, f"card body {c['num']}")
            draw_lines(d, blines, cx, by, font(SANS, 8), INK, 10)
            small_caps(d, c["src"], cx, cy0 + ch - 7, size=7)
    rule(d, M, 452 + 3 * ch + 2 * 6 + 4, CW, width=1)

    # ---- Bottom: map (left, ~38% wide) + ALSO ON (right, 2 cols)
    by0 = 452 + 3 * ch + 2 * 6 + 12
    map_w = 372
    small_caps(d, "Where it happened", M, by0, size=9, fill=RED)
    mx0, mx1 = M, M + map_w
    map_top, map_h = by0 + 14, 92
    lon2x = lambda lon: mx0 + (lon + 170) / 360 * (mx1 - mx0)
    lat2y = lambda lat: map_top + (75 - lat) / 140 * map_h
    for poly in CONTINENTS:
        d.polygon([(lon2x(lo), lat2y(la)) for lo, la in poly], fill=LAND, outline=INK)
    d.text((mx0 + 60, map_top + 62), "ATLANTIC", font=font(SANS_B, 7), fill=BLUE)
    d.text((mx0 + 300, map_top + 66), "PACIFIC", font=font(SANS_B, 7), fill=BLUE)
    for (n, lo, la, dx, dy) in PINS:
        px, py = lon2x(lo) + dx, lat2y(la) + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=PAPER, width=1)
        tw_ = d.textlength(str(n), font=font(SANS_B, 8))
        d.text((px - tw_ / 2, py - 6), str(n), font=font(SANS_B, 8), fill=PAPER)
    small_caps(d, "12 featured stories  ·  numbered pins  ·  schematic, not to scale",
               M, map_top + map_h + 4, size=7)

    ax0 = M + map_w + 16
    aw = W - M - ax0
    small_caps(d, "Also on Friday 27 November", ax0, by0, size=9, fill=RED)
    colw2 = aw / 2
    for i, (n, head, src, trust) in enumerate(ALSO):
        col, r = divmod(i, 10)
        ax = ax0 + col * colw2
        ay = by0 + 14 + r * 11
        chip_square(d, ax, ay + 1, trust)
        d.text((ax + 11, ay), str(n), font=font(SANS_B, 9), fill=RED)
        hf = font(SANS, 9)
        srcw = d.textlength("  " + src, font=font(SANS_B, 7))
        max_hw = colw2 - 30 - srcw
        hh_ = head
        while d.textlength(hh_, font=hf) > max_hw and len(hh_) > 10:
            hh_ = hh_[:-1]
        if hh_ != head:
            hh_ = hh_.rstrip() + "\u2026"
        d.text((ax + 28, ay), hh_, font=hf, fill=INK)
        d.text((ax + 28 + d.textlength(hh_, font=hf) + 4, ay), src,
               font=font(SANS_B, 7), fill=MUTED)
    rule(d, M, by0 + 14 + 10 * 11 + 4, CW, width=1)

    # ---- DATE CHECK (boxed panel)
    dy = by0 + 14 + 10 * 11 + 10
    d.rectangle([M, dy, W - M, dy + 62], outline=RED, width=2)
    small_caps(d, "Date check \u2014 these are NOT 27 November (left out on purpose)",
               M + 8, dy + 5, size=9, fill=RED)
    dc = ("Kuwait drone strike kills 2 Italians (26 Nov)  \u00b7  Tankers hit mines off Hormuz (25 Nov)  \u00b7  "
          "Cairo fuel-tanker fire kills 31 (26 Nov)  \u00b7  Macy\u2019s parade postponed (26 Nov)  \u00b7  "
          "UK\u2013EU treaties published (26 Nov)  \u00b7  FedEx jet off runway, Miami (26 Nov)  \u00b7  "
          "Champions League results (25 Nov).   NOT YET: Macy\u2019s parade Sat 28 Nov  \u00b7  Spain election "
          "Sun 29 Nov  \u00b7  Duterte trial Mon 30 Nov  \u00b7  OPEC+ Sun 29 Nov.")
    dlines = fit(d, dc, font(SANS, 8), CW - 16, 3, "date check")
    draw_lines(d, dlines, M + 8, dy + 19, font(SANS, 8), INK, 10)
    leg = ("HOW SURE:  OFFICIAL = named authority  \u00b7  CONFIRMED = verified by a named outlet  \u00b7  "
           "REPORTED = reported, not officially confirmed  \u00b7  CLAIM = one side\u2019s claim.")
    flines = fit(d, leg, font(SANS, 7), CW - 16, 1, "how sure")
    draw_lines(d, flines, M + 8, dy + 19 + len(dlines) * 10 + 2, font(SANS, 7), MUTED, 9)

    # ---- Footer
    fy = dy + 62 + 6
    foot = ("Sources: Reuters, BBC, WSJ, Yonhap Infomax, SMMT, UNCTAD, KCNA, national front pages \u2014 "
            "full list in SOURCES.md.  Schematic map, not to scale.  Early edition: built from reports "
            "dated Friday 27 November 2026 (see timeline).")
    flines = fit(d, foot, font(SANS, 7), CW, 2, "footer")
    draw_lines(d, flines, M, fy, font(SANS, 7), MUTED, 9)
    assert fy + len(flines) * 9 <= H - 4, f"footer overflows: {fy}"
    return img


def main():
    img = build()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "entry.png")
    img.save(out, optimize=True)
    data = open(out, "rb").read()
    print(out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("size", img.size, img.mode)
    # 300px legibility proof
    thumb = img.resize((300, 300), Image.LANCZOS)
    tpath = os.path.join(outdir, "thumb300.png")
    thumb.save(tpath, optimize=True)
    print(tpath, os.path.getsize(tpath), "bytes")


if __name__ == "__main__":
    main()
