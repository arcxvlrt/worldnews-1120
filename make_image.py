"""Render entry.png: the world news of Friday 20 November 2026 on one 1024x1024 page.

Deterministic: fixed fonts, fixed layout, no clock or randomness. Needs Pillow.
Run: python make_image.py  (writes entry.png next to this file)
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
S = 2  # supersampling factor; everything below is in 1024-px units
W = H = 1024
M = 32  # outer margin

BG = (10, 12, 17)
CARD = (24, 28, 37)
WHITE = (255, 255, 255)
SOFT = (214, 220, 230)
MUTED = (160, 168, 182)
RED = (255, 77, 77)

LEAD = {
    "tag": "RUSSIA vs NATO  ·  OVERNIGHT 19–20 NOV",
    "head": "RUSSIAN MISSILE CRASHES IN POLAND",
    "facts": [
        "Poland: 2 missiles and 1 drone crossed its airspace; a Kh-101 hit a field in Lublin region",
        "Same night, Russian strikes on Ukraine kill 8",
        "Putin rules out ceasefire talks after Crimean Bridge attacks",
    ],
    "icon": "missile",
    "color": RED,
}

STORIES = [
    {"tag": "IRAN WAR", "head": "US SENATE REJECTS IRAN WAR-POWERS BID",
     "facts": ["51–48 vote (Thu)", "Pentagon: war cost tops $48B", "Tanker ablaze in Hormuz"],
     "icon": "ship", "color": (255, 166, 61)},
    {"tag": "MYANMAR", "head": "UN COURT RULES MYANMAR GENOCIDE",
     "facts": ["ICJ rules 9–6 on Rohingya (Thu)", "UK expels Myanmar’s defence attaché"],
     "icon": "scales", "color": (122, 167, 255)},
    {"tag": "APEC · SHENZHEN", "head": "FIRST XI–TRUMP–PUTIN SUMMIT",
     "facts": ["Three-way talks (Thu)", "“Declaration toward Peace” on cutting nuclear risk"],
     "icon": "summit", "color": (255, 210, 63)},
    {"tag": "COP31 · ANTALYA", "head": "CLIMATE DRAFT DROPS FOSSIL FUELS",
     "facts": ["Slimmed-down text cuts every mention", "Activists condemn it"],
     "icon": "thermo", "color": (110, 230, 90)},
    {"tag": "ESTONIA", "head": "ESTONIA TO SHUT RUSSIA BORDER",
     "facts": ["Closed for at least 6 months", "Moscow vows a response"],
     "icon": "barrier", "color": (190, 145, 255)},
    {"tag": "ITALY", "head": "GENERAL STRIKE GRIPS ITALY",
     "facts": ["Nationwide walkout", "Protests in several cities"],
     "icon": "megaphone", "color": (255, 122, 182)},
]

FOOTER = ("(Thu) = happened Thu 19 Nov, reported Fri 20 Nov.   Sources: Democracy Now!, Just Security, "
          "Anadolu Agency, Wikipedia Current events")


def font(name, size):
    return ImageFont.truetype(str(ROOT / "fonts" / name), size * S)


F_KICK = font("BarlowCondensed-Bold.ttf", 22)
F_DATE = font("BarlowCondensed-ExtraBold.ttf", 76)
F_LEAD = font("BarlowCondensed-ExtraBold.ttf", 60)
F_HEAD = font("BarlowCondensed-ExtraBold.ttf", 31)
F_TAG = font("BarlowCondensed-Bold.ttf", 21)
F_FACT = font("Barlow-Medium.ttf", 18)
F_LFACT = font("Barlow-Medium.ttf", 21)
F_FOOT = font("Barlow-Medium.ttf", 16)


def sc(*v):
    return [round(x * S) for x in v]


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= width * S:
            cur = trial
        else:
            assert cur, f"word too wide: {word}"
            lines.append(cur)
            cur = word
    return lines + [cur]


def text_lines(d, x, y, text, fnt, width, fill, lh, max_lines):
    lines = wrap(d, text, fnt, width)
    assert len(lines) <= max_lines, f"too many lines ({len(lines)}): {text}"
    for i, line in enumerate(lines):
        d.text(sc(x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(lines) * lh


def facts(d, x, y, items, fnt, width, color, lh, gap, max_lines):
    used = 0
    for item in items:
        d.rectangle(sc(x, y + lh * 0.42, x + 6, y + lh * 0.42 + 6), fill=color)
        n = len(wrap(d, item, fnt, width - 16))
        used += n
        y = text_lines(d, x + 16, y, item, fnt, width - 16, SOFT, lh, n) + gap
    assert used <= max_lines, f"facts need {used} lines: {items}"
    return y


def rot(points, deg, cx, cy):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + px * c - py * s, cy + px * s + py * c) for px, py in points]


def poly(d, pts, fill):
    d.polygon([round(v * S) for p in pts for v in p], fill=fill)


def icon(d, kind, cx, cy, r, col):
    lw = max(2, round(r * 0.09)) * S
    if kind == "missile":
        for k in (1.0, 0.66, 0.32):
            d.ellipse(sc(cx - r * k, cy - r * k, cx + r * k, cy + r * k), outline=col, width=lw)
        star = [((0.36 if j % 2 else 0.17) * r * math.cos(math.radians(j * 30)),
                 (0.36 if j % 2 else 0.17) * r * math.sin(math.radians(j * 30))) for j in range(12)]
        poly(d, [(cx + x, cy + y) for x, y in star], (255, 210, 63))
        body = [(-1.15, -0.13), (-0.42, -0.13), (-0.2, 0), (-0.42, 0.13), (-1.15, 0.13)]
        fin_a = [(-1.0, -0.12), (-1.25, -0.4), (-1.12, -0.4), (-0.78, -0.12)]
        fin_b = [(x, -y) for x, y in fin_a]
        for shape in (body, fin_a, fin_b):
            poly(d, rot([(x * r, y * r) for x, y in shape], 40, cx, cy), WHITE)
    elif kind == "ship":
        poly(d, [(cx - r, cy + 0.15 * r), (cx + r, cy + 0.15 * r), (cx + 0.7 * r, cy + 0.6 * r),
                 (cx - 0.8 * r, cy + 0.6 * r)], WHITE)
        d.rectangle(sc(cx + 0.35 * r, cy - 0.25 * r, cx + 0.75 * r, cy + 0.15 * r), fill=WHITE)
        fx = cx - 0.3 * r
        for k, c in ((1.0, RED), (0.55, (255, 210, 63))):
            poly(d, [(fx - 0.42 * k * r, cy + 0.12 * r), (fx - 0.3 * k * r, cy - 0.45 * k * r),
                     (fx, cy - 1.05 * k * r + 0.1 * r), (fx + 0.3 * k * r, cy - 0.45 * k * r),
                     (fx + 0.42 * k * r, cy + 0.12 * r)], c)
        d.line(sc(cx - r, cy + 0.85 * r, cx + r, cy + 0.85 * r), fill=col, width=lw)
    elif kind == "scales":
        d.line(sc(cx, cy - 0.85 * r, cx, cy + 0.75 * r), fill=WHITE, width=lw)
        d.line(sc(cx - 0.8 * r, cy - 0.6 * r, cx + 0.8 * r, cy - 0.6 * r), fill=WHITE, width=lw)
        d.rectangle(sc(cx - 0.45 * r, cy + 0.7 * r, cx + 0.45 * r, cy + 0.85 * r), fill=WHITE)
        for sx in (-0.8, 0.8):
            px = cx + sx * r
            d.line(sc(px, cy - 0.6 * r, px - 0.3 * r, cy + 0.15 * r), fill=col, width=lw // 2)
            d.line(sc(px, cy - 0.6 * r, px + 0.3 * r, cy + 0.15 * r), fill=col, width=lw // 2)
            d.chord(sc(px - 0.35 * r, cy - 0.15 * r, px + 0.35 * r, cy + 0.45 * r), 0, 180, fill=col)
    elif kind == "summit":
        for dx, big in ((-0.62, False), (0.62, False), (0, True)):
            k = 1.15 if big else 0.9
            hx, hy = cx + dx * r, cy - 0.35 * r * (1.1 if big else 0.8)
            d.ellipse(sc(hx - 0.22 * r * k, hy - 0.22 * r * k, hx + 0.22 * r * k, hy + 0.22 * r * k),
                      fill=WHITE if big else col)
            d.chord(sc(hx - 0.42 * r * k, hy + 0.28 * r, hx + 0.42 * r * k, hy + 1.2 * r * k), 180, 360,
                    fill=WHITE if big else col)
        d.line(sc(cx - r, cy + 0.75 * r, cx + r, cy + 0.75 * r), fill=col, width=lw)
    elif kind == "thermo":
        d.rounded_rectangle(sc(cx - 0.18 * r, cy - 0.9 * r, cx + 0.18 * r, cy + 0.4 * r),
                            radius=0.18 * r * S, outline=WHITE, width=lw)
        d.ellipse(sc(cx - 0.36 * r, cy + 0.25 * r, cx + 0.36 * r, cy + 0.95 * r), fill=RED)
        d.rectangle(sc(cx - 0.07 * r, cy - 0.35 * r, cx + 0.07 * r, cy + 0.4 * r), fill=RED)
        for i in range(3):
            ty = cy - 0.7 * r + i * 0.3 * r
            d.line(sc(cx + 0.3 * r, ty, cx + 0.55 * r, ty), fill=col, width=lw // 2)
    elif kind == "barrier":
        d.rectangle(sc(cx - 0.95 * r, cy - 0.5 * r, cx - 0.7 * r, cy + 0.85 * r), fill=WHITE)
        d.rectangle(sc(cx + 0.7 * r, cy + 0.05 * r, cx + 0.95 * r, cy + 0.85 * r), fill=WHITE)
        y0, y1 = cy - 0.3 * r, cy + 0.05 * r
        d.rectangle(sc(cx - 0.7 * r, y0, cx + 0.95 * r, y1), fill=WHITE)
        x = cx - 0.6 * r
        while x < cx + 0.85 * r:
            poly(d, [(x, y1), (x + 0.18 * r, y0), (x + 0.36 * r, y0), (x + 0.18 * r, y1)], RED)
            x += 0.42 * r
        d.line(sc(cx - r, cy + 0.85 * r, cx + r, cy + 0.85 * r), fill=col, width=lw)
    elif kind == "globe":
        d.ellipse(sc(cx - r, cy - r, cx + r, cy + r), outline=col, width=lw)
        for k in (0.35, 0.72):
            d.ellipse(sc(cx - k * r, cy - r, cx + k * r, cy + r), outline=col, width=lw // 2)
        for k in (-0.5, 0, 0.5):
            hw = r * math.sqrt(1 - k * k)
            d.line(sc(cx - hw, cy + k * r, cx + hw, cy + k * r), fill=col, width=lw // 2)
    elif kind == "megaphone":
        poly(d, [(cx - 0.75 * r, cy - 0.2 * r), (cx + 0.25 * r, cy - 0.65 * r),
                 (cx + 0.25 * r, cy + 0.65 * r), (cx - 0.75 * r, cy + 0.2 * r)], WHITE)
        d.rectangle(sc(cx - 0.95 * r, cy - 0.22 * r, cx - 0.75 * r, cy + 0.22 * r), fill=WHITE)
        d.line(sc(cx - 0.55 * r, cy + 0.2 * r, cx - 0.4 * r, cy + 0.75 * r), fill=WHITE, width=lw)
        for k in (0.45, 0.8):
            d.arc(sc(cx + 0.3 * r - k * r, cy - k * r, cx + 0.3 * r + k * r, cy + k * r), -40, 40,
                  fill=col, width=lw)


def render():
    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle(sc(0, 0, W, 8), fill=RED)
    d.text(sc(M, 26), "THE WORLD IN ONE PAGE", font=F_KICK, fill=RED)
    d.text(sc(M, 44), "FRIDAY 20 NOVEMBER 2026", font=F_DATE, fill=WHITE)
    icon(d, "globe", W - M - 52, 82, 50, MUTED)
    d.line(sc(M, 140, W - M, 140), fill=MUTED, width=S)

    # Lead story
    top, bottom = 156, 462
    d.rounded_rectangle(sc(M, top, W - M, bottom), radius=14 * S, fill=CARD)
    d.rectangle(sc(M, top + 14, M + 6, bottom - 14), fill=RED)
    icon(d, "missile", M + 130, (top + bottom) / 2, 88, RED)
    x, width = M + 260, W - M - 24 - (M + 260)
    d.text(sc(x, top + 20), LEAD["tag"], font=F_TAG, fill=RED)
    y = text_lines(d, x, top + 46, LEAD["head"], F_LEAD, width, WHITE, 58, 2) + 10
    y = facts(d, x, y, LEAD["facts"], F_LFACT, width, RED, 27, 4, 4)
    assert y <= bottom - 8, f"lead overflow {y}"

    # Six smaller stories, 3 x 2
    gap, cols = 16, 3
    cw = (W - 2 * M - gap * (cols - 1)) / cols
    gy, ch = 476, 232
    for i, st in enumerate(STORIES):
        cx0 = M + (i % cols) * (cw + gap)
        cy0 = gy + (i // cols) * (ch + gap)
        col = st["color"]
        d.rounded_rectangle(sc(cx0, cy0, cx0 + cw, cy0 + ch), radius=12 * S, fill=CARD)
        d.rectangle(sc(cx0 + 12, cy0, cx0 + cw - 12, cy0 + 5), fill=col)
        icon(d, st["icon"], cx0 + 42, cy0 + 42, 24, col)
        d.text(sc(cx0 + 80, cy0 + 29), st["tag"], font=F_TAG, fill=col)
        y = text_lines(d, cx0 + 16, cy0 + 74, st["head"], F_HEAD, cw - 32, WHITE, 31, 2) + 12
        y = facts(d, cx0 + 16, y, st["facts"], F_FACT, cw - 32, col, 23, 2, 3)
        assert y <= cy0 + ch - 6, f"card {i} overflow {y}"

    # Footer
    fy = gy + 2 * ch + gap + 12
    y = text_lines(d, M, fy, FOOTER, F_FOOT, W - 2 * M, MUTED, 19, 2)
    assert y <= H - 8, f"footer overflow {y}"

    out = img.resize((W, H), Image.LANCZOS)
    out = out.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out.save(ROOT / "entry.png", optimize=True)


if __name__ == "__main__":
    render()
