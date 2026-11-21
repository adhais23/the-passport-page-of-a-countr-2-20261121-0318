#!/usr/bin/env python3
"""Valdoria passport spread — program/v1 entry.

Draws one invented passport spread (Republic of Valdoria) and writes it to
/output/entry.png (PNG, 1024x704, under 1 MiB).

Pure Python 3.13 standard library only: the grading sandbox is
python:3.13-slim, so there is no Pillow, no font files and no network.
Everything is drawn by the small raster engine below, with an embedded
5x7 bitmap font, rendered at 2x supersampling and box-downsampled for
smooth edges.

The country: the Republic of Valdoria, a landlocked alpine republic.
Holder: Elena Maren Voss, born 14 JUN 1990 in Kestrel Falls; passport
issued 12 MAR 2024 in Port Venn, expires 11 MAR 2034. Every stamp on the
visa page is dated after the date of issue, and the telling paperwork
detail is the Northern Marches permit (40 koruna fee stamp).
"""

import math
import os
import struct
import zlib

# ---------------------------------------------------------------------------
# Final image size (must stay <= 1024x1024 and <= 1 MiB).
# ---------------------------------------------------------------------------
OUT_W = 1024
OUT_H = 704
SS = 2  # supersampling factor
W = OUT_W * SS
H = OUT_H * SS

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 characters ('#' = ink).
# Uppercase, digits and the punctuation a passport needs. Passports print
# in capitals, so no lowercase glyphs are required.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "..##.", "..##."),
    ",": (".....", ".....", ".....", ".....", "..##.", "..##.", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", "..##.", "..##.", ".....", "..##.", "..##.", "....."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
}

# Width of one glyph cell (5 px + 1 px gap) at scale 1.
CELL_W = 6
CELL_H = 7


def text_width(text, scale):
    """Pixel width of `text` drawn at `scale` (supersampled canvas units)."""
    return (len(text) * CELL_W - 1) * scale


def draw_glyph(canvas, x, y, ch, scale, color):
    """Draw one glyph with its top-left corner at (x, y)."""
    rows = FONT.get(ch)
    if rows is None:
        return
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell == "#":
                canvas.fill_rect(x + c * scale, y + r * scale,
                                 scale, scale, color)


def draw_text(canvas, x, y, text, scale, color):
    """Draw left-aligned text at (x, y); returns the x just past the text."""
    cx = x
    for ch in text:
        draw_glyph(canvas, cx, y, ch, scale, color)
        cx += CELL_W * scale
    return cx


def draw_text_center(canvas, cx, y, text, scale, color):
    """Draw text centred on x=cx at height y."""
    draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, color)


# ---------------------------------------------------------------------------
# Raster canvas: a flat RGB bytearray with simple filled-shape primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, color=(255, 255, 255)):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, color)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def blend_pixel(self, x, y, color, alpha):
        """Blend `color` over the pixel with opacity alpha (0..1)."""
        if 0 <= x < self.w and 0 <= y < self.h and 0.0 < alpha <= 1.0:
            i = (y * self.w + x) * 3
            self.px[i] = int(color[0] * alpha + self.px[i] * (1.0 - alpha))
            self.px[i + 1] = int(color[1] * alpha + self.px[i + 1] * (1.0 - alpha))
            self.px[i + 2] = int(color[2] * alpha + self.px[i + 2] * (1.0 - alpha))

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def draw_line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line with a square brush of `width`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = width // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, width, width, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)

    def draw_circle(self, cx, cy, r, color, width=1):
        steps = max(24, int(2 * math.pi * r))
        prev = None
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            pt = (cx + int(round(r * math.cos(a))),
                  cy + int(round(r * math.sin(a))))
            if prev is not None:
                self.draw_line(prev[0], prev[1], pt[0], pt[1], color, width)
            prev = pt

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            t = (yy - cy) / ry
            half = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)

    def fill_polygon(self, points, color):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for yy in range(max(0, min(ys)), min(self.h, max(ys)) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[k])), yy,
                               int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1,
                               1, color)


# ---------------------------------------------------------------------------
# Stamp layer: a small RGBA buffer that can be rotated and stamped onto the
# main canvas, so border-control stamps look hand-applied, not grid-aligned.
# ---------------------------------------------------------------------------
class Layer:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.a = bytearray(w * h)  # 0 = transparent, 255 = opaque

    def set_pixel(self, x, y, color, alpha=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = y * self.w + x
            j = i * 3
            self.px[j] = color[0]
            self.px[j + 1] = color[1]
            self.px[j + 2] = color[2]
            self.a[i] = alpha

    def fill_rect(self, x, y, w, h, color, alpha=255):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.set_pixel(xx, yy, color, alpha)

    def draw_line(self, x0, y0, x1, y1, color, width=1, alpha=255):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = width // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, width, width, color, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def draw_circle(self, cx, cy, r, color, width=1, alpha=255):
        steps = max(24, int(2 * math.pi * r))
        prev = None
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            pt = (cx + int(round(r * math.cos(a))),
                  cy + int(round(r * math.sin(a))))
            if prev is not None:
                self.draw_line(prev[0], prev[1], pt[0], pt[1], color, width, alpha)
            prev = pt

    def draw_text(self, x, y, text, scale, color, alpha=235):
        cx = x
        for ch in text:
            rows = FONT.get(ch)
            if rows:
                for r, row in enumerate(rows):
                    for c, cell in enumerate(row):
                        if cell == "#":
                            self.fill_rect(cx + c * scale, y + r * scale,
                                           scale, scale, color, alpha)
            cx += CELL_W * scale

    def draw_text_center(self, cx, y, text, scale, color, alpha=235):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color, alpha)

    def paste_rotated(self, canvas, cx, cy, angle_deg, opacity=0.85):
        """Paste this layer centred at (cx, cy), rotated by angle_deg."""
        ang = math.radians(angle_deg)
        ca, sa = math.cos(ang), math.sin(ang)
        hw, hh = self.w / 2.0, self.h / 2.0
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rot = [(x * ca - y * sa, x * sa + y * ca) for x, y in corners]
        min_x = int(cx + min(p[0] for p in rot)) - 1
        max_x = int(cx + max(p[0] for p in rot)) + 1
        min_y = int(cy + min(p[1] for p in rot)) - 1
        max_y = int(cy + max(p[1] for p in rot)) + 1
        for yy in range(max(0, min_y), min(canvas.h, max_y + 1)):
            for xx in range(max(0, min_x), min(canvas.w, max_x + 1)):
                dx, dy = xx - cx, yy - cy
                sx = dx * ca + dy * sa + hw
                sy = -dx * sa + dy * ca + hh
                ix, iy = int(sx), int(sy)
                if 0 <= ix < self.w and 0 <= iy < self.h:
                    al = self.a[iy * self.w + ix] / 255.0 * opacity
                    if al > 0.01:
                        j = (iy * self.w + ix) * 3
                        canvas.blend_pixel(
                            xx, yy,
                            (self.px[j], self.px[j + 1], self.px[j + 2]), al)


# ---------------------------------------------------------------------------
# PNG output: minimal encoder (truecolour, filter 0, zlib).
# ---------------------------------------------------------------------------
def write_png(path, rgb, w, h):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)


def downsample(canvas):
    """Box-average the 2x supersampled canvas to the final size."""
    out = bytearray(OUT_W * OUT_H * 3)
    for y in range(OUT_H):
        for x in range(OUT_W):
            r = g = b = 0
            for dy in range(SS):
                for dx in range(SS):
                    i = ((y * SS + dy) * W + (x * SS + dx)) * 3
                    r += canvas.px[i]
                    g += canvas.px[i + 1]
                    b += canvas.px[i + 2]
            o = (y * OUT_W + x) * 3
            n = SS * SS
            out[o] = r // n
            out[o + 1] = g // n
            out[o + 2] = b // n
    return out


# ---------------------------------------------------------------------------
# Palette (all colours chosen once, so both pages read as one document).
# ---------------------------------------------------------------------------
INK = (28, 38, 44)          # near-black document ink
GOLD = (176, 141, 58)       # Valdorian gold
GOLD_DK = (140, 108, 38)
TEAL = (18, 92, 86)         # Valdorian teal
TEAL_DK = (11, 62, 58)
PAPER_L = (238, 243, 236)   # data page paper
PAPER_R = (243, 238, 224)   # visa page paper
SURFACE = (43, 47, 54)      # dark table the passport lies on
LABEL = (96, 104, 102)      # small-caps field labels
SKIN = (232, 185, 143)
SKIN_SH = (214, 162, 118)
HAIR = (58, 40, 30)
JACKET = (24, 96, 90)
STAMP_BLUE = (38, 84, 160)
STAMP_GREEN = (34, 120, 74)
STAMP_PURPLE = (118, 58, 140)


# ---------------------------------------------------------------------------
# Guilloche: faint wavy arcs and rings that make the paper feel printed.
# ---------------------------------------------------------------------------
def guilloche(canvas, x0, y0, x1, y1, color, step=26, alpha=0.10):
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    max_r = int(math.hypot(x1 - x0, y1 - y0) // 2)
    r = step
    while r < max_r:
        steps = max(48, int(2 * math.pi * r / 3))
        prev = None
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            wob = 3 * math.sin(a * 9 + r / 17.0)
            px = cx + int((r + wob) * math.cos(a))
            py = cy + int((r + wob) * math.sin(a) * 0.72)
            if prev is not None and x0 <= px <= x1 and y0 <= py <= y1:
                canvas.blend_pixel(px, py, color, alpha)
                canvas.blend_pixel(prev[0], prev[1], color, alpha)
            prev = (px, py)
        r += step


# ---------------------------------------------------------------------------
# Coat of arms: a gold eagle above three mountain peaks, inside a ring.
# ---------------------------------------------------------------------------
def coat_of_arms(canvas, cx, cy, r):
    canvas.draw_circle(cx, cy, r, GOLD, 3)
    canvas.draw_circle(cx, cy, r - 6, GOLD, 2)
    # Three mountain peaks.
    base = cy + int(r * 0.52)
    canvas.fill_polygon([
        (cx - int(r * 0.72), base), (cx - int(r * 0.34), cy - int(r * 0.05)),
        (cx - int(r * 0.10), base)], GOLD)
    canvas.fill_polygon([
        (cx - int(r * 0.34), base), (cx, cy - int(r * 0.42)),
        (cx + int(r * 0.34), base)], GOLD)
    canvas.fill_polygon([
        (cx + int(r * 0.10), base), (cx + int(r * 0.34), cy - int(r * 0.05)),
        (cx + int(r * 0.72), base)], GOLD)
    # Snow caps on the peaks.
    canvas.fill_polygon([
        (cx - int(r * 0.40), cy + int(r * 0.02)),
        (cx - int(r * 0.34), cy - int(r * 0.05)),
        (cx - int(r * 0.28), cy + int(r * 0.02))], PAPER_L)
    canvas.fill_polygon([
        (cx - int(r * 0.06), cy - int(r * 0.30)),
        (cx, cy - int(r * 0.42)),
        (cx + int(r * 0.06), cy - int(r * 0.30))], PAPER_L)
    # Eagle: body, spread wings, head with beak.
    ex, ey = cx, cy - int(r * 0.62)
    canvas.fill_ellipse(ex, ey + 6, int(r * 0.10), int(r * 0.20), GOLD_DK)
    canvas.fill_polygon([
        (ex - int(r * 0.08), ey + 2), (ex - int(r * 0.52), ey - int(r * 0.22)),
        (ex - int(r * 0.46), ey + int(r * 0.10)),
        (ex - int(r * 0.10), ey + int(r * 0.16))], GOLD_DK)
    canvas.fill_polygon([
        (ex + int(r * 0.08), ey + 2), (ex + int(r * 0.52), ey - int(r * 0.22)),
        (ex + int(r * 0.46), ey + int(r * 0.10)),
        (ex + int(r * 0.10), ey + int(r * 0.16))], GOLD_DK)
    canvas.fill_circle(ex, ey - 8, int(r * 0.09), GOLD_DK)
    canvas.fill_polygon([
        (ex + int(r * 0.07), ey - 10), (ex + int(r * 0.20), ey - 6),
        (ex + int(r * 0.07), ey - 4)], GOLD_DK)


# ---------------------------------------------------------------------------
# Valdorian flag: teal-white-teal horizontal bands with a gold peak.
# ---------------------------------------------------------------------------
def flag(canvas, x, y, w, h):
    band = h // 3
    canvas.fill_rect(x, y, w, band, TEAL)
    canvas.fill_rect(x, y + band, w, h - 2 * band, (244, 244, 238))
    canvas.fill_rect(x, y + h - band, w, band, TEAL)
    canvas.fill_polygon([
        (x + w // 2 - w // 6, y + h - band),
        (x + w // 2, y + band // 2),
        (x + w // 2 + w // 6, y + h - band)], GOLD)


# ---------------------------------------------------------------------------
# Portrait: a flat, stylised official portrait — dark-haired woman in her
# mid-thirties in a teal jacket, against a pale blue studio background
# with a faint guilloche ring. Drawn, not pasted: it belongs to the page.
# ---------------------------------------------------------------------------
def portrait(canvas, x, y, w, h):
    canvas.fill_rect(x, y, w, h, (207, 221, 230))
    # Studio backdrop: soft ring and mountain silhouette.
    canvas.draw_circle(x + w // 2, y + h // 2, min(w, h) // 2 - 8,
                       (178, 198, 210), 2)
    canvas.fill_polygon([
        (x, y + h), (x + w // 4, y + int(h * 0.62)),
        (x + w // 2, y + h), (x + w * 3 // 4, y + int(h * 0.70)),
        (x + w, y + h)], (186, 204, 214))
    cx = x + w // 2
    # Shoulders / teal jacket with a light collar.
    canvas.fill_polygon([
        (x + int(w * 0.06), y + h), (x + int(w * 0.16), y + int(h * 0.78)),
        (cx - int(w * 0.10), y + int(h * 0.70)),
        (cx + int(w * 0.10), y + int(h * 0.70)),
        (x + int(w * 0.84), y + int(h * 0.78)),
        (x + int(w * 0.94), y + h)], JACKET)
    canvas.fill_polygon([
        (cx - int(w * 0.10), y + int(h * 0.70)),
        (cx, y + int(h * 0.86)), (cx + int(w * 0.10), y + int(h * 0.70))],
        (240, 240, 234))
    # Neck and head.
    canvas.fill_rect(cx - int(w * 0.06), y + int(h * 0.60),
                     int(w * 0.12), int(h * 0.12), SKIN_SH)
    canvas.fill_ellipse(cx, y + int(h * 0.40), int(w * 0.17), int(h * 0.21), SKIN)
    # Hair: dark mass over the crown, falling past the jaw on both sides.
    canvas.fill_ellipse(cx, y + int(h * 0.26), int(w * 0.185), int(h * 0.15), HAIR)
    canvas.fill_rect(cx - int(w * 0.185), y + int(h * 0.22),
                     int(w * 0.055), int(h * 0.30), HAIR)
    canvas.fill_rect(cx + int(w * 0.13), y + int(h * 0.22),
                     int(w * 0.055), int(h * 0.30), HAIR)
    canvas.fill_polygon([
        (cx - int(w * 0.185), y + int(h * 0.24)),
        (cx - int(w * 0.10), y + int(h * 0.13)),
        (cx + int(w * 0.10), y + int(h * 0.13)),
        (cx + int(w * 0.185), y + int(h * 0.24)),
        (cx + int(w * 0.13), y + int(h * 0.30)),
        (cx - int(w * 0.13), y + int(h * 0.30))], HAIR)
    # Face: brows, eyes, nose, mouth — kept minimal and symmetrical.
    ey = y + int(h * 0.38)
    canvas.draw_line(cx - int(w * 0.115), ey - 8, cx - int(w * 0.045), ey - 8,
                     HAIR, 3)
    canvas.draw_line(cx + int(w * 0.045), ey - 8, cx + int(w * 0.115), ey - 8,
                     HAIR, 3)
    canvas.fill_ellipse(cx - int(w * 0.08), ey, 5, 4, INK)
    canvas.fill_ellipse(cx + int(w * 0.08), ey, 5, 4, INK)
    canvas.set_pixel(cx - int(w * 0.08) - 2, ey - 2, (255, 255, 255))
    canvas.set_pixel(cx + int(w * 0.08) - 2, ey - 2, (255, 255, 255))
    canvas.draw_line(cx, ey + 6, cx - 3, ey + 16, SKIN_SH, 3)
    canvas.draw_line(cx - int(w * 0.045), y + int(h * 0.545),
                     cx + int(w * 0.045), y + int(h * 0.545), (168, 92, 84), 4)
    # Soft cheek shading.
    canvas.fill_ellipse(cx - int(w * 0.115), y + int(h * 0.47), 8, 5, (236, 170, 140))
    canvas.fill_ellipse(cx + int(w * 0.115), y + int(h * 0.47), 8, 5, (236, 170, 140))


# ---------------------------------------------------------------------------
# Machine-readable zone (ICAO 9303, two lines of 44 characters).
# ---------------------------------------------------------------------------
_MRZ_VALUES = {}
for _i, _ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    _MRZ_VALUES[_ch] = _i
_MRZ_VALUES["<"] = 0


def mrz_check(text):
    """ICAO check digit for a field: weights 7, 3, 1 repeating."""
    total = 0
    weights = (7, 3, 1)
    for i, ch in enumerate(text):
        total += _MRZ_VALUES[ch] * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<VALVOSS<<ELENA<MAREN"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VD8472916"
    birth = "900614"
    expiry = "340311"
    personal = "<" * 14
    line2 = (doc + mrz_check(doc) + "VAL" + birth + mrz_check(birth) + "F"
             + expiry + mrz_check(expiry) + personal
             + mrz_check(personal))
    body = doc + mrz_check(doc) + "VAL" + birth + mrz_check(birth) + "F" \
        + expiry + mrz_check(expiry) + personal + mrz_check(personal)
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


# ---------------------------------------------------------------------------
# Border-control stamps. Each is drawn on its own layer, then pasted
# rotated, so it looks hand-applied rather than grid-aligned.
# ---------------------------------------------------------------------------
def round_stamp(lines, color, radius):
    """A round stamp: two rings and centred lines of text."""
    size = radius * 2 + 16
    lay = Layer(size, size)
    c = size // 2
    lay.draw_circle(c, c, radius, color, 5)
    lay.draw_circle(c, c, radius - 12, color, 3)
    # Small stars flanking the middle line.
    lay.draw_text(c - 58, c - 42, "*", 3, color)
    lay.draw_text(c + 46, c - 42, "*", 3, color)
    y = c - (len(lines) * 30) // 2
    for i, (text, scale) in enumerate(lines):
        lay.draw_text_center(c, y + i * 30, text, scale, color)
    return lay


def rect_stamp(lines, color, w, h):
    """A rectangular stamp: double border and centred lines of text."""
    lay = Layer(w, h)
    lay.fill_rect(4, 4, w - 8, h - 8, color, 0)  # (keeps the buffer sized)
    for x0, y0, x1, y1 in ((4, 4, w - 5, h - 5), (12, 12, w - 13, h - 13)):
        lay.draw_line(x0, y0, x1, y0, color, 4)
        lay.draw_line(x0, y1, x1, y1, color, 4)
        lay.draw_line(x0, y0, x0, y1, color, 4)
        lay.draw_line(x1, y0, x1, y1, color, 4)
    y = h // 2 - (len(lines) * 30) // 2
    for i, (text, scale) in enumerate(lines):
        lay.draw_text_center(w // 2, y + i * 30, text, scale, color)
    return lay


def field(canvas, x, y, label, value):
    """One bilingual data field: small label above a larger value."""
    draw_text(canvas, x, y, label, 2, LABEL)
    draw_text(canvas, x, y + 24, value, 3, INK)


def build_spread():
    canvas = Canvas(W, H, SURFACE)
    # Soft shadow under the open passport.
    canvas.fill_rect(72, 76, 1928, 1288, (24, 26, 30))
    # Pages: data page left, visa page right, spine in the middle.
    canvas.fill_rect(48, 48, 976, 1312, PAPER_L)
    canvas.fill_rect(1024, 48, 976, 1312, PAPER_R)
    canvas.fill_rect(1012, 48, 24, 1312, (200, 204, 196))
    canvas.draw_line(1024, 48, 1024, 1360, (120, 122, 114), 3)
    guilloche(canvas, 64, 64, 1008, 1344, TEAL)
    guilloche(canvas, 1040, 64, 1984, 1344, (150, 120, 40))

    # ---- Data page ------------------------------------------------------
    coat_of_arms(canvas, 536, 190, 72)
    draw_text_center(canvas, 536, 292, "REPUBLIC OF VALDORIA", 4, TEAL_DK)
    draw_text_center(canvas, 536, 348, "PASSPORT", 5, GOLD_DK)
    canvas.draw_line(120, 420, 952, 420, GOLD, 3)
    canvas.draw_line(120, 430, 952, 430, GOLD, 2)

    # Portrait, framed.
    canvas.fill_rect(88, 452, 256, 296, GOLD)
    portrait(canvas, 96, 460, 240, 280)
    draw_text_center(canvas, 216, 756, "HOLDER / INNEHAVER", 2, LABEL)

    # Data fields to the right of the portrait.
    rows = [
        ("SURNAME / EFTERNAM", "VOSS"),
        ("GIVEN NAMES / FORNAM", "ELENA MAREN"),
        ("NATIONALITY / NASJON", "VALDORIAN"),
        ("DATE OF BIRTH / FODT", "14 JUN 1990"),
        ("PLACE OF BIRTH / FODESTED", "KESTREL FALLS"),
        ("SEX / KJONN", "F"),
    ]
    y = 452
    for label, value in rows:
        field(canvas, 384, y, label, value)
        y += 62
    canvas.draw_line(384, 452 + 6 * 62 - 14, 960, 452 + 6 * 62 - 14,
                     (190, 192, 184), 2)

    # Flag and issue details below the portrait.
    flag(canvas, 96, 852, 150, 78)
    draw_text(canvas, 96, 946, "VALDORIA", 2, LABEL)
    field(canvas, 300, 852, "DOCUMENT NO. / DOKUMENT NR.", "VD 8472916")
    field(canvas, 640, 852, "AUTHORITY / MYNDIGHET", "PORT VENN")
    field(canvas, 300, 962, "DATE OF ISSUE / UTSTEDT", "12 MAR 2024")
    field(canvas, 640, 962, "DATE OF EXPIRY / GYLDIG TIL", "11 MAR 2034")

    # Machine-readable zone (ICAO check digits computed in code).
    canvas.draw_line(96, 1108, 960, 1108, INK, 2)
    line1, line2 = mrz_lines()
    draw_text(canvas, 96, 1130, line1, 3, INK)
    draw_text(canvas, 96, 1180, line2, 3, INK)
    draw_text_center(canvas, 536, 1268,
                     "THIS PASSPORT REMAINS THE PROPERTY OF THE REPUBLIC OF VALDORIA",
                     2, LABEL)

    # ---- Visa page ------------------------------------------------------
    draw_text_center(canvas, 1512, 110, "VISAS", 4, TEAL_DK)
    draw_text_center(canvas, 1512, 158, "VISA / VIZA", 2, LABEL)
    canvas.draw_line(1100, 200, 1924, 200, GOLD, 3)

    # Ostrovik visa sticker (top of the page).
    canvas.fill_rect(1100, 232, 400, 190, (42, 90, 158))
    canvas.fill_rect(1112, 244, 376, 166, (66, 118, 184))
    draw_text_center(canvas, 1300, 258, "VISA", 5, (255, 255, 255))
    draw_text_center(canvas, 1300, 306, "OSTROVIK", 3, (255, 255, 255))
    draw_text_center(canvas, 1300, 338, "SINGLE ENTRY - 30 DAYS", 2,
                     (220, 230, 240))
    draw_text_center(canvas, 1300, 366, "NR OS-8814", 2, (220, 230, 240))
    draw_text_center(canvas, 1300, 390, "ISSUED 28 APR 2025", 2,
                     (220, 230, 240))

    # A small arrival card tucked beside the sticker.
    canvas.fill_rect(1540, 232, 384, 190, (250, 248, 240))
    canvas.draw_line(1552, 244, 1912, 244, (150, 120, 40), 2)
    draw_text(canvas, 1560, 262, "ARRIVAL CARD", 3, INK)
    draw_text(canvas, 1560, 300, "NAME  VOSS, ELENA MAREN", 2, INK)
    draw_text(canvas, 1560, 328, "FLIGHT  OV 214  VIA PORT VENN", 2, INK)
    draw_text(canvas, 1560, 356, "PURPOSE  MOUNTAIN RESEARCH", 2, INK)
    draw_text(canvas, 1560, 384, "STAY  12 DAYS", 2, INK)

    # Stamps — every date after the passport's issue (12 MAR 2024).
    round_stamp([("OSTROVIK", 3), ("ENTRY", 4), ("08 MAY 2025", 3)],
                STAMP_BLUE, 118).paste_rotated(canvas, 1300, 620, -12)
    rect_stamp([("TARNOVIA", 3), ("EXIT", 4), ("21 SEP 2025", 3)],
               STAMP_BLUE, 360, 180).paste_rotated(canvas, 1740, 620, 8)
    round_stamp([("MERIDIAN PORT", 2), ("ENTRY", 4), ("02 FEB 2026", 3)],
                STAMP_GREEN, 118).paste_rotated(canvas, 1300, 1020, -6)
    rect_stamp([("NORTHERN MARCHES", 3), ("PERMIT", 4),
                ("40 KORUNA PAID", 3)], STAMP_PURPLE, 380, 180
               ).paste_rotated(canvas, 1740, 1020, 5)

    # The telling detail: a handwritten-style permit note.
    canvas.draw_line(1100, 1230, 1924, 1230, (150, 120, 40), 2)
    draw_text(canvas, 1100, 1252,
              "RE-ENTRY PERMIT REQUIRED FOR NORTHERN MARCHES",
              3, STAMP_PURPLE)
    draw_text(canvas, 1100, 1290,
              "- BORDER SERVICE, PORT VENN", 2, LABEL)
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_spread()
    rgb = downsample(canvas)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, rgb, OUT_W, OUT_H)
    size = os.path.getsize(path)
    print(f"wrote {path}: {OUT_W}x{OUT_H}, {size} bytes")
    assert size <= 1048576, "entry.png exceeds 1 MiB"


if __name__ == "__main__":
    main()
