#!/usr/bin/env python3
"""Draw a broadsheet summing up Thursday 26 November 2026 (v3, font fix).

Layout follows the user's reference image (masthead, stats bar, 3 heroes
+ 10 small cards, timeline, map with pins 1-13, AND ALSO list 14-36,
DATE CHECK box, footer) with original drawn illustrations - no pixels
copied from the reference. The thin region colour bar from v3 is dropped:
it crowded the stats row and added nothing legible.

FONT FIX (this revision): the v3 font was a 5x7 bitmap (7px glyphs at
scale 1) - unreadable at thumbnail size and strained at full size. It
is replaced by a NEW bold bitmap font: 8px wide x 14px tall per glyph,
2px stems, open counters, I with top/bottom bars (distinct from 1,
which has a flag and a base), O round (distinct from slashed 0).
Minimum text on the page is scale 1 of this font = 14px tall glyphs;
headlines are scale 2 (28px), the masthead scale 3 (42px). To make
room, every text was shortened - hero bodies to ~10 words, small-card
bodies to ~8 words, AND ALSO items to headline + source only, DATE
CHECK entries to name + date only. Words were cut, never the font
shrunk to fit them. Facts, dates, numbers, sources and status badges
are unchanged from v3 (see NEWS.md).

Pure Python 3.13 standard library, deterministic: no network, no files
read, no timestamps, so two runs produce identical bytes.

COMPLIANCE: the bounty gate allows at most 1024 by 1024 pixels and
1 MiB, so this renders at exactly 1024x1024 PNG. A "high-resolution"
image above 1024px would be rejected (Valid=0); 16:9 would only be
1024x576 and 4:5 only 819x1024, both smaller than the square.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (22, 22, 22)
NAVY = (20, 38, 74)
GOLD = (198, 158, 40)
RED = (172, 32, 32)
TEAL = (18, 110, 105)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
RULE = (190, 182, 160)
MUTED = (90, 86, 76)
OCEAN = (226, 236, 234)
LAND = (150, 178, 165)
SKY = (38, 58, 92)
SKY2 = (70, 110, 140)

# ---------------------------------------------------------------- font ----
# NEW bold bitmap font: each glyph is 8 wide x 14 tall, '#' on, '.' off.
# Ink sits on rows 1-11 (rows 0 and 12-13 are clear, except the tails of
# ',' and ';' which reach row 13). Stems are 2px thick. I has top and
# bottom bars; 1 has a flag and a base; O is plain; 0 carries a slash.
# All page text is set in capitals (Canvas.text uppercases).
FONT = {
    "A": ("........",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".######.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........"),
    "B": ("........",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".#####..",
          "........",
          "........",
          "........"),
    "C": ("........",
          "..####..",
          ".##..##.",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "D": ("........",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".#####..",
          "........",
          "........",
          "........"),
    "E": ("........",
          ".######.",
          ".##.....",
          ".##.....",
          ".##.....",
          ".#####..",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".######.",
          "........",
          "........",
          "........"),
    "F": ("........",
          ".######.",
          ".##.....",
          ".##.....",
          ".##.....",
          ".#####..",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          "........",
          "........",
          "........"),
    "G": ("........",
          "..####..",
          ".##..##.",
          ".##.....",
          ".##.....",
          ".##.###.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "H": ("........",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".######.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........"),
    "I": ("........",
          ".######.",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          ".######.",
          "........",
          "........",
          "........"),
    "J": ("........",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          ".##.##..",
          ".##.##..",
          "..###...",
          "........",
          "........",
          "........"),
    "K": ("........",
          ".##..##.",
          ".##..##.",
          ".##.##..",
          ".####...",
          ".###....",
          ".####...",
          ".##.##..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "L": ("........",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".######.",
          "........",
          "........",
          "........"),
    "M": ("........",
          ".##..##.",
          ".###.##.",
          ".##.###.",
          ".##.###.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "N": ("........",
          ".##..##.",
          ".###.##.",
          ".####.#.",
          ".##.###.",
          ".##.###.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "O": ("........",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "P": ("........",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".#####..",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".##.....",
          "........",
          "........",
          "........"),
    "Q": ("........",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##.###.",
          ".##..##.",
          "..####..",
          "....##..",
          "........",
          "........"),
    "R": ("........",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".#####..",
          ".####...",
          ".##.##..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "S": ("........",
          "..####..",
          ".##..##.",
          ".##.....",
          ".##.....",
          "..###...",
          "....##..",
          "....##..",
          "....##..",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "T": ("........",
          ".######.",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "........",
          "........",
          "........"),
    "U": ("........",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "V": ("........",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "...##...",
          "...##...",
          "........",
          "........",
          "........"),
    "W": ("........",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##.###.",
          ".##.###.",
          ".##.###.",
          ".###.##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "X": ("........",
          ".##..##.",
          ".##..##.",
          "..####..",
          "...##...",
          "...##...",
          "...##...",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "Y": ("........",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "........",
          "........",
          "........"),
    "Z": ("........",
          ".######.",
          "....##..",
          "....##..",
          "...##...",
          "...##...",
          "..##....",
          "..##....",
          ".##.....",
          ".##.....",
          ".######.",
          "........",
          "........",
          "........"),
    "0": ("........",
          "..####..",
          ".##..##.",
          ".##.###.",
          ".###.##.",
          ".##.##..",
          ".##.##..",
          ".###.##.",
          ".##.###.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "1": ("........",
          "...##...",
          "..###...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          "...##...",
          ".######.",
          "........",
          "........",
          "........"),
    "2": ("........",
          "..####..",
          ".##..##.",
          "....##..",
          "....##..",
          "...##...",
          "..##....",
          ".##.....",
          ".##.....",
          ".##.....",
          ".######.",
          "........",
          "........",
          "........"),
    "3": ("........",
          "..####..",
          ".##..##.",
          "....##..",
          "....##..",
          "..###...",
          "....##..",
          "....##..",
          "....##..",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "4": ("........",
          "....##..",
          "...###..",
          "..##.##.",
          "..##.##.",
          ".##..##.",
          ".######.",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "........",
          "........",
          "........"),
    "5": ("........",
          ".######.",
          ".##.....",
          ".##.....",
          ".#####..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "6": ("........",
          "..####..",
          ".##.....",
          ".##.....",
          ".##.....",
          ".#####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "7": ("........",
          ".######.",
          "....##..",
          "....##..",
          "...##...",
          "...##...",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "........",
          "........",
          "........"),
    "8": ("........",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..####..",
          "........",
          "........",
          "........"),
    "9": ("........",
          "..####..",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          ".##..##.",
          "..#####.",
          "....##..",
          "....##..",
          "....##..",
          "..####..",
          "........",
          "........",
          "........"),
    " ": ("........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........"),
    ".": ("........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "..##....",
          "..##....",
          "........",
          "........"),
    ",": ("........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "..##....",
          "..##....",
          "..##....",
          ".#......"),
    "-": ("........",
          "........",
          "........",
          "........",
          "........",
          "..####..",
          "..####..",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........"),
    ":": ("........",
          "........",
          "........",
          "..##....",
          "..##....",
          "........",
          "........",
          "........",
          "..##....",
          "..##....",
          "........",
          "........",
          "........",
          "........"),
    ";": ("........",
          "........",
          "........",
          "..##....",
          "..##....",
          "........",
          "........",
          "........",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          ".#......",
          "........"),
    "!": ("........",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "........",
          "..##....",
          "..##....",
          "........",
          "........"),
    "?": ("........",
          "..####..",
          ".##..##.",
          "....##..",
          "....##..",
          "...##...",
          "...##...",
          "........",
          "...##...",
          "...##...",
          "........",
          "........",
          "........",
          "........"),
    "/": ("........",
          "....##..",
          "....##..",
          "...##...",
          "...##...",
          "..##....",
          "..##....",
          ".##.....",
          ".##.....",
          "##......",
          "........",
          "........",
          "........",
          "........"),
    "%": ("........",
          ".##..##.",
          ".##.##..",
          "...##...",
          "..##....",
          "..##....",
          ".##.....",
          ".##.##..",
          ".##..##.",
          "........",
          "........",
          "........",
          "........",
          "........"),
    "(": ("........",
          "....##..",
          "...##...",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "..##....",
          "...##...",
          "....##..",
          "........",
          "........",
          "........"),
    ")": ("........",
          "..##....",
          "...##...",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "....##..",
          "...##...",
          "..##....",
          "........",
          "........",
          "........"),
    "+": ("........",
          "........",
          "........",
          "...##...",
          "...##...",
          ".######.",
          ".######.",
          "...##...",
          "...##...",
          "........",
          "........",
          "........",
          "........",
          "........"),
    "&": ("........",
          "..###...",
          ".##.##..",
          ".##.##..",
          "..##....",
          ".####...",
          ".##.##..",
          ".##.##..",
          ".##.##..",
          "..##.##.",
          ".##..##.",
          "........",
          "........",
          "........"),
    "'": ("........",
          "..##....",
          "..##....",
          ".##.....",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........"),
    "$": ("........",
          "...##...",
          "..####..",
          ".##.##..",
          ".##.....",
          "..###...",
          "....##..",
          ".##.##..",
          ".####...",
          "...##...",
          "...##...",
          "........",
          "........",
          "........"),
    "=": ("........",
          "........",
          "........",
          "........",
          ".######.",
          ".######.",
          "........",
          "........",
          ".######.",
          ".######.",
          "........",
          "........",
          "........",
          "........"),
    "*": ("........",
          "........",
          "........",
          ".##..##.",
          "..####..",
          ".######.",
          "..####..",
          ".##..##.",
          "........",
          "........",
          "........",
          "........",
          "........",
          "........"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    if not text:
        return 0
    return len(text) * 9 * scale - scale


def wrap(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, color)
                elif not fill and abs(d - r * r) <= r:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ys = sorted([y0, y1, y2])
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by) or y == ys[2]:
                    t = (y - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT["?"])
            for row in range(14):
                for col in range(8):
                    if glyph[row][col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 9 * scale
        return cx

    def text_center(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)

    def text_center_in(self, x, w, y, s, scale, color):
        self.text(x + (w - text_width(s, scale)) // 2, y, s, scale, color)

# -------------------------------------------------------------- art ------
# Original pictograms, drawn from shapes into a box (x, y, w, h).
# Only the parade / india / chess branches are used (heroes 1-3); the
# rest are kept for completeness. In-art text is kept to a minimum and
# sized to fit its label bar at the new 14px font.
def draw_art(cv, x, y, w, h, kind):
    cx, cy = x + w // 2, y + h // 2
    if kind == "parade":  # night sky, buildings, parade balloon
        cv.rect(x, y, w, h, SKY)
        for bx, bh in ((4, 34), (26, 52), (52, 40), (78, 58), (104, 30),
                       (128, 48), (154, 36), (180, 54), (206, 32),
                       (232, 46), (258, 38), (284, 52)):
            cv.rect(x + bx, y + h - bh, 20, bh, (16, 24, 44))
            for wy in range(y + h - bh + 6, y + h - 6, 10):
                cv.rect(x + bx + 5, wy, 4, 5, GOLD)
                cv.rect(x + bx + 12, wy, 4, 5, GOLD)
        cv.circle(cx - 40, y + 22, 22, WHITE, fill=True)
        cv.circle(cx - 40, y + 22, 22, (200, 40, 40), fill=False)
        cv.rect(cx - 46, y + 46, 12, 8, RED)
        cv.rect(x + 8, y + h - 18, 200, 16, RED)
        cv.text(x + 14, y + h - 16, "POSTPONED TO SATURDAY", 1, WHITE)
        cv.circle(x + w - 22, y + 16, 12, GOLD, fill=True)
    elif kind == "india":  # saffron sky, candles, flag
        cv.rect(x, y, w, h, (222, 150, 70))
        cv.rect(x, y + h - 26, w, 26, (120, 70, 30))
        for i in range(7):
            fx = x + 18 + i * 38
            cv.rect(fx, y + h - 52, 6, 26, WHITE)
            cv.triangle(fx + 3, y + h - 62, fx - 2, y + h - 52,
                        fx + 8, y + h - 52, GOLD)
        cv.rect(x + w - 92, y + 10, 80, 12, (255, 140, 40))
        cv.rect(x + w - 92, y + 22, 80, 12, WHITE)
        cv.rect(x + w - 92, y + 34, 80, 12, (20, 120, 60))
        cv.circle(x + w - 52, y + 28, 5, NAVY, fill=False)
        cv.rect(x + 100, y + 8, 80, 16, NAVY)
        cv.text(x + 104, y + 11, "18 YEARS", 1, WHITE)
    elif kind == "chess":  # board, clocks, score
        cv.rect(x, y, w, h, (40, 60, 40))
        bs = 18
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0:
                    cv.rect(x + 14 + c * bs, y + 12 + r * bs, bs, bs, WHITE)
                else:
                    cv.rect(x + 14 + c * bs, y + 12 + r * bs, bs, bs,
                            (30, 30, 30))
        cv.circle(x + 30, y + 28, 7, NAVY, fill=True)
        cv.circle(x + 62, y + 62, 7, WHITE, fill=True)
        cv.rect(x + w - 150, y + 14, 64, 34, WHITE)
        cv.rect(x + w - 76, y + 14, 64, 34, WHITE)
        cv.text(x + w - 138, y + 24, "1:32", 1, INK)
        cv.text(x + w - 64, y + 24, "1:32", 1, INK)
        cv.rect(x + w - 150, y + 50, 140, 14, RED)
        cv.text(x + w - 94, y + 52, "1-1", 1, WHITE)
        cv.rect(x + w - 150, y + 68, 60, 12, GOLD)
        cv.text(x + w - 146, y + 69, "GAME 3", 1, NAVY)
    elif kind == "eu":  # blue, circle of stars
        cv.rect(x, y, w, h, (30, 60, 130))
        for i in range(8):
            import math as _m
            a = i * _m.pi / 4
            sx = int(cx + 52 * _m.cos(a))
            sy = int(cy - 8 + 30 * _m.sin(a))
            cv.circle(sx, sy, 4, GOLD, fill=True)
        cv.circle(cx, cy - 8, 20, GOLD, fill=False)
        cv.circle(cx, cy - 8, 15, GOLD, fill=False)
        cv.rect(x + 10, y + h - 20, w - 20, 14, WHITE)
        cv.text(x + 16, y + h - 17, "BRUSSELS SUMMIT", 1, NAVY)
    elif kind == "mine":  # hills, shaft, helmet
        cv.rect(x, y, w, h, (150, 190, 160))
        cv.triangle(x, y + h, x + w // 2, y + 20, x + w, y + h, (90, 130, 90))
        cv.rect(x + w // 2 - 14, y + 34, 28, h - 34, (60, 45, 30))
        cv.rect(x + w // 2 - 22, y + 34, 44, 8, NAVY)
        cv.circle(cx, y + 22, 12, GOLD, fill=True)
        cv.rect(cx - 16, y + 22, 32, 4, GOLD)
        for i in range(3):
            cv.circle(x + 24 + i * 30, y + h - 14, 6, WHITE, fill=True)
    elif kind == "nuke":  # flag, rocket
        cv.rect(x, y, w, h, (90, 30, 30))
        cv.rect(x + 16, y + 12, 70, 14, RED)
        cv.rect(x + 16, y + 26, 70, 14, WHITE)
        cv.rect(x + 16, y + 40, 70, 14, (30, 60, 160))
        cv.circle(x + 51, y + 33, 6, RED, fill=True)
        cv.triangle(cx + 40, y + h - 8, cx + 62, y + h - 8, cx + 51, y + 30,
                    WHITE)
        cv.circle(cx + 51, y + 34, 5, RED, fill=True)
    elif kind == "jets":  # sky, jet, burst
        cv.rect(x, y, w, h, SKY2)
        cv.triangle(x + 40, cy - 6, x + w - 30, cy - 2, x + 40, cy + 8, WHITE)
        cv.triangle(x + 90, cy - 16, x + 130, cy - 2, x + 90, cy + 4, WHITE)
        cv.triangle(x + 90, cy + 2, x + 130, cy + 4, x + 90, cy + 16, WHITE)
        cv.circle(x + w - 44, y + 22, 12, GOLD, fill=True)
        cv.circle(x + w - 44, y + 22, 6, RED, fill=True)
    elif kind == "power":  # courthouse, lightning
        cv.rect(x, y, w, h, (210, 200, 170))
        for i in range(4):
            cv.rect(x + 24 + i * 62, y + 30, 16, h - 60, WHITE)
        cv.triangle(x + 10, y + 8, x + w - 10, y + 8, cx, y + 30, NAVY)
        cv.rect(x + 16, y + h - 34, w - 32, 8, NAVY)
        cv.triangle(cx + 60, y + 14, cx + 44, y + 44, cx + 62, y + 44, GOLD)
        cv.triangle(cx + 56, y + 44, cx + 72, y + 44, cx + 54, y + 74, GOLD)
    elif kind == "spain":  # ballot box, flag
        cv.rect(x, y, w, h, (200, 40, 40))
        cv.rect(x + 16, y + 16, 90, 12, (255, 200, 40))
        cv.rect(x + 16, y + 28, 90, 12, RED)
        cv.rect(x + 16, y + 40, 90, 12, (255, 200, 40))
        cv.rect(cx - 10, y + 62, 90, 34, WHITE)
        cv.rect(cx - 10, y + 62, 90, 6, NAVY)
        cv.rect(cx + 30, y + 44, 8, 20, NAVY)
    elif kind == "bok":  # coin up, bars
        cv.rect(x, y, w, h, (30, 90, 90))
        cv.circle(cx, cy + 6, 30, GOLD, fill=False)
        cv.circle(cx, cy + 6, 24, GOLD, fill=False)
        cv.text(cx - 18, cy, "3.25%", 1, GOLD)
        cv.triangle(cx + 34, y + 12, cx + 22, y + 30, cx + 46, y + 30, WHITE)
        cv.rect(cx + 32, y + 30, 4, 18, WHITE)
        cv.rect(x + 12, y + h - 22, 16, 14, WHITE)
        cv.rect(x + 34, y + h - 30, 16, 22, WHITE)
        cv.rect(x + 56, y + h - 38, 16, 30, GOLD)
    elif kind == "sanaa":  # skyline, blast
        cv.rect(x, y, w, h, (60, 40, 50))
        for bx, bh in ((10, 40), (40, 62), (76, 48), (112, 70), (150, 44),
                       (188, 58), (226, 40), (262, 52)):
            cv.rect(x + bx, y + h - bh - 14, 30, bh, (20, 20, 30))
        cv.circle(cx + 60, y + 24, 14, GOLD, fill=True)
        cv.circle(cx + 60, y + 24, 7, RED, fill=True)
        cv.circle(cx - 70, y + 30, 16, TEAL, fill=False)
    elif kind == "checkpoint":  # barrier, alert
        cv.rect(x, y, w, h, (180, 160, 120))
        cv.rect(x + 20, y + h // 2 - 6, w - 40, 12, RED)
        cv.rect(x + 20, y + h // 2 - 6, 24, 12, WHITE)
        cv.rect(x + w - 44, y + h // 2 - 6, 24, 12, WHITE)
        cv.triangle(cx, y + 10, cx - 22, y + 44, cx + 22, y + 44, GOLD)
        cv.text(cx - 4, y + 24, "!", 1, NAVY)
    elif kind == "zambia":  # placard, scales
        cv.rect(x, y, w, h, (40, 110, 60))
        cv.rect(x + 30, y + 16, 120, 44, WHITE)
        cv.vline(cx, y + 60, 30, WHITE)
        cv.hline(cx - 30, y + 62, 60, WHITE)
        cv.circle(cx - 26, y + 74, 8, GOLD, fill=True)
        cv.circle(cx + 26, y + 74, 8, GOLD, fill=True)


# Small pictogram for the 10 small cards: one motif per kind, drawn in a
# 44x44 box centred in the art panel (never wider than the card).
def draw_mini(cv, x, y, kind, color):
    cx, cy = x + 22, y + 22
    if kind == "eu":
        cv.circle(cx, cy, 16, color, fill=False)
        cv.circle(cx, cy, 11, color, fill=False)
        cv.text(cx - 9, cy - 7, "45", 1, color)
    elif kind == "mine":
        cv.triangle(cx - 20, y + 40, cx, y + 6, cx + 20, y + 40, color)
        cv.rect(cx - 4, y + 14, 8, 26, NAVY)
        cv.circle(cx, y + 10, 6, GOLD, fill=True)
    elif kind == "nuke":
        cv.rect(cx - 20, y + 4, 26, 10, RED)
        cv.rect(cx - 20, y + 14, 26, 10, WHITE)
        cv.triangle(cx + 12, y + 38, cx + 20, y + 38, cx + 16, y + 10, color)
    elif kind == "jets":
        cv.triangle(cx - 20, cy - 4, cx + 18, cy, cx - 20, cy + 6, color)
        cv.triangle(cx - 2, cy - 12, cx + 12, cy, cx - 2, cy + 4, color)
        cv.circle(cx + 14, y + 8, 5, GOLD, fill=True)
    elif kind == "power":
        for i in range(3):
            cv.rect(cx - 18 + i * 14, y + 12, 6, 22, color)
        cv.triangle(cx + 8, y + 6, cx - 2, y + 22, cx + 8, y + 22, GOLD)
        cv.triangle(cx + 4, y + 22, cx + 14, y + 22, cx + 4, y + 38, GOLD)
    elif kind == "spain":
        cv.rect(cx - 18, y + 14, 36, 20, color)
        cv.rect(cx - 18, y + 14, 36, 5, NAVY)
        cv.rect(cx - 3, y + 6, 6, 10, NAVY)
    elif kind == "bok":
        cv.circle(cx, cy + 4, 15, color, fill=False)
        cv.circle(cx, cy + 4, 11, color, fill=False)
        cv.triangle(cx, y + 2, cx - 7, y + 12, cx + 7, y + 12, color)
    elif kind == "sanaa":
        for bx, bh in ((-20, 18), (-6, 26), (8, 20)):
            cv.rect(cx + bx, y + 40 - bh, 12, bh, color)
        cv.circle(cx + 12, y + 10, 7, GOLD, fill=True)
        cv.circle(cx + 12, y + 10, 3, RED, fill=True)
    elif kind == "checkpoint":
        cv.rect(cx - 20, cy - 4, 40, 8, RED)
        cv.rect(cx - 20, cy - 4, 10, 8, WHITE)
        cv.triangle(cx, y + 2, cx - 10, y + 16, cx + 10, y + 16, GOLD)
    elif kind == "zambia":
        cv.rect(cx - 18, y + 6, 36, 18, WHITE)
        cv.text(cx - 9, y + 10, "NO", 1, RED)
        cv.vline(cx, y + 26, 14, color)
        cv.hline(cx - 14, y + 28, 28, color)
        cv.circle(cx - 12, y + 36, 4, GOLD, fill=True)
        cv.circle(cx + 12, y + 36, 4, GOLD, fill=True)

# -------------------------------------------------------------- data -----
# Heroes: (no, headline, body, source, badge, art, region, field)
# Headlines shortened to fit 2 lines at scale 2 (28px); bodies to ~10
# words. Facts, numbers, sources and badges are unchanged from v3.
HEROES = [
    (1, "MACY'S 100TH PARADE POSTPONED",
     "NOR'EASTER BRINGS 60 MPH GUSTS; PARADE MOVES TO SATURDAY.",
     "AP", "REPORTED", "parade", "NORTH AMERICA", "DISASTER"),
    (2, "INDIA MARKS 18 YEARS SINCE 26/11",
     "TRIBUTES MARK 26/11 MUMBAI ATTACKS; 77 YEARS OF CONSTITUTION.",
     "PTI", "CONFIRMED", "india", "SOUTH ASIA", "POLITICS"),
    (3, "GUKESH MEETS SINDAROV IN GAME 3",
     "LEVEL AFTER TWO DRAWS; GAME 3 IN GENEVA TODAY.",
     "FIDE", "ONGOING", "chess", "SOUTH ASIA", "SPORT"),
    (4, "EU LEADERS CLASH OVER 45BN LOAN",
     "BRUSSELS DEBATES EUR 45BN UKRAINE LOAN.",
     "DAILY SUMMARY OF", "REPORTED", "eu", "EUROPE", "POLITICS"),
    (5, "13 MINERS TRAPPED IN FLOOD",
     "RESCUERS PUMP TWO SHAFTS 100M DEEP.",
     "DAILY SUMMARY OF", "REPORTED", "mine", "SE ASIA & OCEANIA",
     "DISASTER"),
    (6, "KIM WIDENS TACTICAL NUKES",
     "KIM: TACTICAL NUKES ACROSS MORE DOMAINS.",
     "KCNA", "REPORTED", "nuke", "EAST ASIA", "CONFLICT"),
    (7, "UKRAINE HITS FIVE JETS",
     "THREE MIG-31 AND TWO SU-34 HIT.",
     "UKR GENERAL STAFF", "REPORTED", "jets", "EUROPE", "CONFLICT"),
    (8, "PUERTO RICO AXES LUMA DEAL",
     "COURT VOTES 5-4; ONE YEAR FOR SUCCESSOR.",
     "DAILY SUMMARY OF", "REPORTED", "power", "NORTH AMERICA", "POLITICS"),
    (9, "SPAIN HEADS TO SNAP VOTE",
     "ELECTIONS 29 NOV; PEOPLE'S PARTY LEADS.",
     "DAILY SUMMARY OF", "REPORTED", "spain", "EUROPE", "POLITICS"),
    (10, "BANK OF KOREA RAISES RATE",
     "KEY RATE UP 25BP TO 3.25%.",
     "YONHAP", "CONFIRMED", "bok", "EAST ASIA", "ECONOMY"),
    (11, "BLAST HITS SANAA",
     "BLAST HITS SANAA; MISSILES INTERCEPTED.",
     "DAILY SUMMARY OF", "REPORTED", "sanaa", "MIDDLE EAST", "CONFLICT"),
    (12, "ISIL ATTACK KILLS TWO IN HASAKAH",
     "SUICIDE ATTACK KILLS TWO, WOUNDS FIVE.",
     "AL JAZEERA", "REPORTED", "checkpoint", "MIDDLE EAST", "CONFLICT"),
    (13, "ZAMBIA BANS TERM-LIMIT PROTEST",
     "BAN ON PROTEST OVER TERM LIMITS.",
     "DAILY SUMMARY OF", "REPORTED", "zambia", "AFRICA", "POLITICS"),
]

# Also: (no, headline, source, region, field). Headlines shortened so
# "NN. HEADLINE - SOURCE" fits one line in a 324px column at 14px text.
ALSO = [
    (14, "EU BUDGET MEET", "TAGESSCHAU", "EUROPE", "POLITICS"),
    (15, "TUBE STRIKE", "DAILY SUMMARY OF", "EUROPE", "POLITICS"),
    (16, "ASIAN STOCKS REBOUND", "CNBC", "EAST ASIA", "ECONOMY"),
    (17, "KING TIDES FLOOD", "GUARDIAN", "NORTH AMERICA", "DISASTER"),
    (18, "213 INDIANS DEAD", "THE HINDU", "SOUTH ASIA", "DISASTER"),
    (19, "BRAZIL ENVOY RECALL", "MERCOPRESS", "SOUTH AMERICA", "POLITICS"),
    (20, "HASINA RETURN ROW", "THE HINDU", "SOUTH ASIA", "POLITICS"),
    (21, "KURD OIL RULING", "AL JAZEERA", "MIDDLE EAST", "POLITICS"),
    (22, "2035 TARGET MISSED", "GUARDIAN", "SE ASIA & OCEANIA", "CLIMATE"),
    (23, "6 HOMES LOST IN FIRE", "GUARDIAN", "SE ASIA & OCEANIA",
     "DISASTER"),
    (24, "SOMALIA TROOPS WITHDRAW", "BBC", "AFRICA", "CONFLICT"),
    (25, "RED SEA LAKES", "SCIENCEDAILY", "WORLD & SCIENCE", "SCIENCE"),
    (26, "UK REFUGEES TO ESWATINI", "BBC", "AFRICA", "MIGRATION"),
    (27, "FAMINE RISK FALLS", "ALLAFRICA", "AFRICA", "DISASTER"),
    (28, "RAMSAY TO HOST TOP GEAR", "BBC", "EUROPE", "CULTURE"),
    (29, "LONDON FALLING WINS", "GUARDIAN", "EUROPE", "CULTURE"),
    (30, "ASTRONAUT BABY FROM ORBIT", "BBC", "NORTH AMERICA", "SCIENCE"),
    (31, "TOP K-POP STARS RANKED", "YONHAP", "EAST ASIA", "CULTURE"),
    (32, "BEALE RETURNS TO WALLABIES", "ABC", "SE ASIA & OCEANIA", "SPORT"),
    (33, "BRIGNONE RETIRES", "CBC", "EUROPE", "SPORT"),
    (34, "PIG KIDNEY OFF DIALYSIS", "CBC", "NORTH AMERICA", "HEALTH"),
    (35, "DEALER LINKED TO GANGS", "BBC", "EUROPE", "JUSTICE"),
    (36, "DR CONGO QUERIES THREATS", "BBC", "AFRICA", "POLITICS"),
]

# Verified first-report times on 26 Nov 2026 UTC (dailysummaryof.com).
TIMELINE = [
    (0.00, "00:00 SANAA"),
    (0.38, "00:23 SPAIN"),
    (1.00, "01:00 LUMA"),
    (1.65, "01:39 JETS"),
    (2.05, "02:03 NUKES"),
    (5.23, "05:14 MINERS"),
    (5.73, "05:44 EU LOAN"),
]

# DATE CHECK box: stories that are NOT 26 November (item, correct date).
# Entries shortened to name + date only; shown in red, no X prefix.
DATE_CHECK = [
    ("RAS TANURA", "25 NOV"),
    ("HORMUZ MINES", "24 NOV"),
    ("GAZA CHIEF", "24 NOV"),
    ("BLYSK LASER", "25 NOV"),
    ("RUSSIA STRIKES", "25 NOV"),
    ("US TARIFFS", "25 NOV"),
    ("BANGLA WAGE", "25 NOV"),
    ("SHENZHOU-24", "25 NOV"),
    ("SOLOMON PACT", "25 NOV"),
    ("HUANG RETURNS", "24 NOV"),
    ("COP31 NO PACT", "22 NOV"),
    ("DRONES LIBYA", "22 NOV"),
    ("BELGIUM STRIKE", "23 NOV"),
    ("ABU NAHAL", "24 NOV"),
    ("SHENZHEN", "17 NOV"),
    ("UNRWA WORKER", "23 NOV"),
    ("RUSSIA PLAN", "25 NOV"),
]

# Map pin positions (panel-local) for heroes 1-13.
MAP_PINS = [
    (58, 38), (226, 50), (168, 38), (148, 24), (256, 70), (282, 30),
    (198, 24), (90, 56), (138, 46), (298, 50), (202, 70), (186, 52),
    (172, 86),
]

STANDFIRST = ("NOR'EASTER GROUNDS MACY'S PARADE; INDIA MARKS 26/11; "
              "GUKESH PLAYS GAME 3.")

SRC_SHORT = {"DAILY SUMMARY OF": "DAILY SUMMARY",
             "UKR GENERAL STAFF": "UKR STAFF"}

# -------------------------------------------------------------- layout ----
def draw_hero_card(cv, x, y, w, h, hero):
    no, headline, body, source, badge, art, region, field = hero
    cv.rect(x, y, w, h, CARD)
    cv.hline(x, y + h - 1, w, RULE)
    cv.vline(x, y, h, RULE)
    cv.vline(x + w - 1, y, h, RULE)
    cv.hline(x, y, w, RULE)
    draw_art(cv, x + 1, y + 1, w - 2, 86, art)
    cv.circle(x + 16, y + 16, 11, RED, fill=True)
    cv.text(x + 12, y + 9, str(no), 1, WHITE)
    hy = y + 94
    for line in wrap(headline, w - 16, 2)[:2]:
        cv.text(x + 8, hy, line, 2, INK)
        hy += 30
    by = y + 158
    for line in wrap(body, w - 16, 1)[:2]:
        cv.text(x + 8, by, line, 1, INK)
        by += 16
    src = SRC_SHORT.get(source, source)
    cv.text(x + 8, y + 192, "SOURCE: " + src, 1, INK)
    bw = text_width(badge, 1) + 10
    cv.rect(x + w - bw - 8, y + 189, bw, 16, NAVY)
    cv.text(x + w - bw - 3, y + 191, badge, 1, WHITE)


def draw_small_card(cv, x, y, w, h, hero):
    no, headline, body, source, badge, art, region, field = hero
    cv.rect(x, y, w, h, CARD)
    cv.hline(x, y + h - 1, w, RULE)
    cv.vline(x, y, h, RULE)
    cv.vline(x + w - 1, y, h, RULE)
    cv.hline(x, y, w, RULE)
    cv.rect(x + 1, y + 1, w - 2, 52, (232, 238, 236))
    # pictogram sits in the clear middle gap between the number circle
    # (left) and the status badge (right) so nothing overlaps it
    draw_mini(cv, x + 44, y + 4, art, NAVY)
    cv.circle(x + 12, y + 12, 9, RED, fill=True)
    cv.text(x + 9 if no < 10 else x + 6, y + 5, str(no), 1, WHITE)
    bw = text_width(badge, 1) + 8
    cv.rect(x + w - bw - 6, y + 5, bw, 16, NAVY)
    cv.text(x + w - bw - 2, y + 6, badge, 1, WHITE)
    hy = y + 58
    for line in wrap(headline, w - 12, 1)[:2]:
        cv.text(x + 6, hy, line, 1, INK)
        hy += 15
    by = y + 90
    for line in wrap(body, w - 12, 1)[:2]:
        cv.text(x + 6, by, line, 1, INK)
        by += 15
    src = SRC_SHORT.get(source, source)
    cv.text(x + 6, y + 120, src, 1, INK)


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, OCEAN)
    cv.hline(x, y + h - 1, w, RULE)
    cv.vline(x, y, h, RULE)
    cv.vline(x + w - 1, y, h, RULE)
    cv.hline(x, y, w, RULE)
    cv.text(x + 8, y + 6, "WHERE IT HAPPENED - PINS 1-13", 1, INK)
    # simple clean continents (panel-local blobs)
    cv.rect(x + 14, y + 26, 84, 24, LAND)
    cv.triangle(x + 14, y + 26, x + 56, y + 16, x + 98, y + 26, LAND)
    cv.rect(x + 66, y + 56, 30, 22, LAND)
    cv.triangle(x + 66, y + 78, x + 96, y + 78, x + 81, y + 100, LAND)
    cv.rect(x + 148, y + 24, 30, 16, LAND)
    cv.rect(x + 148, y + 44, 34, 30, LAND)
    cv.triangle(x + 148, y + 74, x + 182, y + 74, x + 165, y + 96, LAND)
    cv.rect(x + 186, y + 22, 104, 30, LAND)
    cv.triangle(x + 236, y + 48, x + 268, y + 48, x + 252, y + 78, LAND)
    cv.rect(x + 268, y + 76, 30, 10, LAND)
    for i, (mx, my) in enumerate(MAP_PINS):
        cv.circle(x + mx, y + my, 10, RED, fill=True)
        cv.circle(x + mx, y + my, 10, WHITE, fill=False)
        n = str(i + 1)
        cv.text(x + mx - 4 if i + 1 < 10 else x + mx - 8, y + my - 7, n, 1,
                WHITE)


def draw_timeline(cv, x, y, w):
    cv.text(x, y, "THE DAY IN UTC", 1, INK)
    line_y = y + 22
    x0, x1 = x + 10, x + w - 10
    cv.hline(x0, line_y, x1 - x0, NAVY)
    for hour in (6, 12, 18, 24):
        tx = x0 + int((x1 - x0) * hour / 24)
        cv.vline(tx, line_y - 4, 9, NAVY)
        cv.text(tx - 9, y + 8, "%02d" % hour, 1, INK)
    for hour, _label in TIMELINE:
        dx = x0 + int((x1 - x0) * hour / 24)
        cv.circle(dx, line_y, 4, RED, fill=True)
    legend = " - ".join(lbl for _h, lbl in TIMELINE)
    cv.text(x, line_y + 10, legend, 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    sources = set(h[3] for h in HEROES) | set(a[2] for a in ALSO)
    fields = set(h[7] for h in HEROES) | set(a[4] for a in ALSO)
    # masthead (scale 3 = 42px glyphs, the largest on the page)
    cv.text_center(6, "THE WORLD IN ONE DAY", 3, INK)
    cv.hline(12, 52, W - 24, INK)
    cv.text_center(58, "THURSDAY 26 NOVEMBER 2026", 2, INK)
    cv.text_center(90, STANDFIRST, 1, INK)
    # stats bar (numbers scale 2 = 28px, words scale 1 = 14px)
    stats = [("36", "STORIES"), ("9", "REGIONS"),
             (str(len(sources)), "SOURCES - %d FIELDS" % len(fields))]
    for i, (num, word) in enumerate(stats):
        bx = 12 + i * 336
        cv.rect(bx, 112, 328, 30, CARD)
        cv.hline(bx, 112 + 29, 328, RULE)
        cv.vline(bx, 112, 30, RULE)
        cv.vline(bx + 327, 112, 30, RULE)
        cv.hline(bx, 112, 328, RULE)
        total = text_width(num, 2) + 6 + text_width(word, 1)
        tx = bx + (328 - total) // 2
        tx = cv.text(tx, 113, num, 2, RED)
        cv.text(tx + 6, 120, word, 1, INK)
    # hero row (1-3)
    for i, hero in enumerate(HEROES[:3]):
        draw_hero_card(cv, 12 + i * 336, 148, 328, 210, hero)
    # small cards (4-13): two rows of five
    for i, hero in enumerate(HEROES[3:]):
        cx = 12 + (i % 5) * 204
        cy = 364 + (i // 5) * 142
        draw_small_card(cv, cx, cy, 196, 136, hero)
    # timeline
    draw_timeline(cv, 24, 648, 976)
    # AND ALSO list (14-36): three columns, one line per story
    ax, ay, aw = 12, 700, 1000
    cv.text(ax, ay, "AND ALSO - STORIES 14-36", 1, INK)
    cv.hline(ax, ay + 14, aw, RULE)
    cols = [ALSO[:8], ALSO[8:16], ALSO[16:]]
    for ci, col in enumerate(cols):
        lx = ax + ci * 338
        ly = ay + 22
        for no, text, source, _reg, _f in col:
            cv.text(lx, ly, "%d. %s - %s" % (no, text, source), 1, INK)
            ly += 15
    # bottom: map + date check box
    draw_map(cv, 12, 844, 330, 118)
    dx, dy, dw = 350, 844, 662
    cv.rect(dx, dy, dw, 118, CARD)
    cv.rect(dx, dy, dw, 3, RED)
    cv.hline(dx, dy + 117, dw, RULE)
    cv.vline(dx, dy, 118, RULE)
    cv.vline(dx + dw - 1, dy, 118, RULE)
    cv.text(dx + 12, dy + 8, "DATE CHECK - THESE ARE NOT 26 NOVEMBER", 1,
            RED)
    third = (len(DATE_CHECK) + 2) // 3
    for ci, col in enumerate([DATE_CHECK[:third],
                             DATE_CHECK[third:2 * third],
                             DATE_CHECK[2 * third:]]):
        lx = dx + 12 + ci * 216
        ly = dy + 26
        for item, date in col:
            cv.text(lx, ly, item + " - " + date, 1, RED)
            ly += 15
    # footer: claim, how-sure key, scenes note (all 14px, near-black ink)
    fy = 968
    cv.hline(24, fy, W - 48, NAVY)
    cv.text(24, fy + 6,
            "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON "
            "26 NOVEMBER 2026.", 1, INK)
    cv.text(24, fy + 20,
            "HOW SURE: OFFICIAL = GOVERNMENT - CONFIRMED = TWO SOURCES - "
            "CLAIM = ONE SIDE - ONGOING = UNFOLDING.", 1, INK)
    cv.text(24, fy + 34,
            "SCENES ARE DRAWN ILLUSTRATIONS, NOT PHOTOGRAPHS.", 1, INK)
    return cv


# -------------------------------------------------------------- png --------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
