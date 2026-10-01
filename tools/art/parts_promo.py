"""プロモ（promo）で足した部品: 鳥の巣の隠し財布、蒸し風呂の小屋、氷の穴、焼け石。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, coin, window


def nest(c, x, y, r=46):
    """鳥の巣: 小枝を編んだ椀の中に、卵と口の開いた財布と金貨。"""
    c.paint(ellipse(x, y, r, r * 0.45, clip=lambda px, py: py > y - r * 0.15), 'wood', gain=0.95,
            tex=lambda px, py: -0.16 if int(px * 0.7 + py * 1.3) % 4 == 0 or int(px * 0.9 - py * 1.1) % 5 == 0 else 0)
    c.paint(ellipse(x, y - r * 0.12, r * 0.8, r * 0.2), 'wood', gain=0.45, outline=False)
    for dx in (-0.45, -0.2):
        c.paint(ellipse(x + dx * r, y - r * 0.2, r * 0.13, r * 0.17), 'paper', gain=1.1, spec=0.3)
    c.paint(ellipse(x + r * 0.2, y - r * 0.22, r * 0.3, r * 0.22), 'red', gain=0.95)
    c.paint(ellipse(x + r * 0.28, y - r * 0.38, r * 0.18, r * 0.07), 'stone', emit=0.04, outline=False)
    for j in range(4):
        coin(c, x + r * (0.18 + j * 0.1), y - r * (0.42 + (j % 2) * 0.06), r * 0.1, metal='gold', tilt=0.5, stamp='star' if j % 2 else 'crown')
    for j in range(7):
        a = math.pi * (0.1 + 0.8 * hsh(j, 3))
        c.paint(capsule(x - math.cos(a) * r, y + r * 0.1, x - math.cos(a) * r * 1.2, y + r * 0.1 + (hsh(3, j) - 0.5) * 20, 0.8), 'wood', gain=0.9, outline=False)


def sauna_hut(c, x, base, w=90, h=50):
    """蒸し風呂の小屋: 丸太の小屋、雪をのせた屋根、煙突から立つ湯気、灯の窓。"""
    from parts_menagerie import log_cabin
    log_cabin(c, x, base, w=w, h=h, antlers=False)
    c.paint(capsule(x + w * 0.25, base - h - 6, x + w * 0.25, base - h - 34, 4), 'stone', gain=0.8)
    for j in range(6):
        t = j / 5
        c.paint(ellipse(x + w * 0.25 - t * 14 + math.sin(t * 5) * 4, base - h - 40 - t * 40, 5 + t * 6, 4 + t * 4), 'paper', emit=0.7 - t * 0.3, outline=False, dither=True)


def ice_hole(c, x, y, rx=50, ry=12):
    """凍った湖に開けた四角い氷の穴、縁の氷の塊と、黒い水。"""
    c.paint(rect(x - rx, y - ry, x + rx, y + ry, UP), 'water', emit=0.12, outline=False)
    c.paint(rect(x - rx + 4, y - ry + 2, x + rx - 4, y + ry - 2, UP), 'water', emit=lambda px, py, n: 0.4 + 0.2 * c.light.att(px, py) + (0.2 if math.sin(px * 0.5 + py) > 0.8 else 0), outline=False)
    for j in range(8):
        bx = x - rx - 6 + hsh(j, 5) * (rx * 2 + 12)
        by = y + (ry + 4) * (1 if j % 2 else -1)
        c.paint(poly([(bx - 6, by + 3), (bx + 6, by + 3), (bx + 3, by - 4), (bx - 4, by - 3)], nrm(-0.3, -0.5, 0.8)), 'silver', gain=1.1, spec=0.6)
    c.paint(capsule(x + rx - 6, y - ry - 30, x + rx - 6, y - ry, 1.4), 'wood', gain=0.9)
    for j in range(3):
        c.paint(capsule(x + rx - 12 + j * 3, y - ry, x + rx - 6, y - ry - 30, 0.6), 'wood', gain=0.8, outline=False)


def hot_stones(c, x, base, r=30):
    """蒸し風呂の焼け石: 鉄の籠に積んだ赤く光る石と、柄杓と木の桶。"""
    c.paint(rect(x - r, base - r * 0.9, x + r, base, nrm(-0.2, 0, 1)), 'stone', gain=0.7, spec=0.4)
    for j in range(9):
        sx = x + (hsh(j, 1) - 0.5) * r * 1.6
        sy = base - r * 0.9 - hsh(1, j) * r * 0.5
        c.paint(ellipse(sx, sy, 7, 5), 'stone', gain=0.9)
        c.paint(ellipse(sx, sy + 1, 4, 2), 'fire', emit=0.7, outline=False)
    c.brighten(x, base - r, r * 2, r * 1.4, 0.2)
    c.paint(capsule(x + r + 6, base - 4, x + r + 30, base - 40, 1.6), 'wood', gain=1.0)
    c.paint(ellipse(x + r + 6, base - 4, 6, 3), 'wood', gain=1.1)


def steam_cloud(c, pts):
    """湯気: 白く透ける丸の重なり（発光・市松）。"""
    for j, (x, y) in enumerate(pts):
        for k in range(4):
            px, py = x + (hsh(j, k) - 0.5) * 16, y - k * 6
            c.paint(ellipse(px, py, 9 - k, 7 - k), 'paper', emit=0.75 - k * 0.08, outline=False, dither=True)


PROPS = {}
