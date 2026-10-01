"""冒険（adventures）で足した部品。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import (UP, barrel, block, chest, coin, flame, gem, goblet, rocks, skull, stone_wall, wheel, window, horse, bottle, doc)


def tankard(c, x, base, s=1.0):
    """酒場の木のジョッキ（泡つき）。"""
    k = s
    c.paint(vcyl(x, base - 22 * k, base, 9 * k, 3 * k), 'wood', gain=1.1, tex=lambda px, py: -0.12 if int(px) % 4 == 0 else 0)
    for y in (base - 18 * k, base - 5 * k):
        c.paint(rect(x - 9 * k, y, x + 9 * k + 1, y + 2 * k), 'silver', gain=0.9, outline=False)
    c.paint(ellipse(x, base - 23 * k, 9.5 * k, 4 * k), 'paper', gain=1.2)
    c.paint(ellipse(x - 3 * k, base - 25 * k, 5 * k, 3 * k), 'paper', gain=1.3)
    pts = arc_points(x + 11 * k, base - 12 * k, 6 * k, -math.pi / 2, math.pi / 2, 8)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.6 * k), 'wood', gain=0.9)


def standing_stone(c, x, base, w=44, h=96, rune=True):
    """立石: 荒い縦長の石、光る護りの印。"""
    pts = [(x - w / 2, base), (x - w / 2 + 4, base - h * 0.6), (x - w / 4, base - h), (x + w / 3, base - h + 6), (x + w / 2, base - h * 0.5), (x + w / 2 - 2, base)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 0.9 - 0.15, -0.1, 0.9)), 'stone', gain=1.0, tex=lambda px, py: -0.06 if (int(px) * 5 + int(py) * 3) % 17 == 0 else 0)
    if rune:
        cy = base - h * 0.55
        for a, b in (((x - 8, cy - 12), (x, cy + 12)), ((x + 8, cy - 12), (x, cy + 12)), ((x - 10, cy - 2), (x + 10, cy - 2))):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.4), 'blue', emit=0.95, outline=False)
        c.brighten(x, cy, 30, 34, 0.25)


def wall_chains(c, x, top, n=2):
    for k in range(n):
        cx = x + k * 30
        for j in range(8):
            y = top + j * 6
            if j % 2 == 0:
                c.paint(ellipse(cx, y, 2, 3.5), 'silver', gain=0.8, spec=0.5)
            else:
                c.paint(ellipse(cx, y, 3.5, 2), 'silver', gain=0.7)
        c.paint(ellipse(cx, top + 52, 6, 4), 'silver', gain=0.9, spec=0.5)


def light_beam(c, x0, y0, x1, y1, w0=8, w1=30, ramp='water'):
    """窓から差し込む光の筋（市松で透ける）。"""
    pts = [(x0 - w0 / 2, y0), (x0 + w0 / 2, y0), (x1 + w1 / 2, y1), (x1 - w1 / 2, y1)]
    pix = [(px, py, n) for px, py, n in poly(pts) if (px + py) % 2 == 0]
    c.paint(pix, ramp, emit=0.5, outline=False)


def backpack(c, x, base):
    """背負い袋（巻いた寝具をのせ、締め革つき）。"""
    c.paint(rect(x - 20, base - 44, x + 20, base, lambda px, py: nrm((px - x) / 20 * 0.7, 0, 0.8)), 'leather', gain=1.0)
    c.paint(ellipse(x, base - 44, 20, 6), 'leather', gain=1.1)
    c.paint(capsule(x - 22, base - 50, x + 22, base - 50, 6, flat=0.2), 'red', gain=0.9)
    for dx in (-10, 10):
        c.paint(rect(x + dx - 2, base - 44, x + dx + 2, base), 'wood', gain=0.8, outline=False)
        c.paint(rect(x + dx - 2, base - 24, x + dx + 2, base - 21), 'gold', gain=1.0, outline=False)
    c.paint(rect(x - 14, base - 20, x + 14, base - 8, nrm(-0.2, 0, 1)), 'leather', gain=0.85)


def waterskin(c, x, base):
    c.paint(ellipse(x, base - 12, 10, 12), 'leather', gain=1.1, spec=0.3)
    c.paint(capsule(x, base - 24, x + 2, base - 30, 2.4), 'wood', gain=1.0)
    c.paint(capsule(x - 10, base - 20, x + 20, base - 40, 0.6), 'leather', gain=0.8, outline=False)


def easel(c, x, base, w=60, h=50):
    """画架: 3 本脚の台に、壺を描いた絵。"""
    for dx in (-w / 2 + 6, w / 2 - 6, 0):
        c.paint(capsule(x, base - h - 30, x + dx * 1.2, base, 1.6), 'wood', gain=0.95 if dx <= 0 else 0.8)
    o = c.paint(rect(x - w / 2, base - h - 26, x + w / 2, base - 26, nrm(-0.2, 0, 1)), 'paper', gain=1.0)
    c.paint(rect(x - w / 2 - 2, base - 26, x + w / 2 + 2, base - 22, UP), 'wood', gain=1.0)
    cx, cy = x, base - h / 2 - 26
    c.paint(ellipse(cx, cy + 6, 12, 14), 'copper', oid=o, gain=0.9, outline=False)
    c.paint(rect(cx - 5, cy - 14, cx + 6, cy - 6), 'copper', oid=o, gain=0.9, outline=False)


def vase(c, x, base, s=1.0):
    k = s
    c.paint(ellipse(x, base - 16 * k, 14 * k, 16 * k), 'copper', gain=1.0, spec=0.5)
    c.paint(capsule(x, base - 30 * k, x, base - 40 * k, 6 * k, 5 * k), 'copper', gain=1.05, spec=0.5)
    c.paint(ellipse(x, base - 42 * k, 7 * k, 2.4 * k), 'copper', gain=0.6)


def gears(c, x, y):
    """からくりの歯車（大小の噛み合い）と、ぜんまい。"""
    for gx, gy, r, n in ((x, y, 22, 12), (x + 30, y - 16, 13, 8), (x - 26, y + 18, 11, 7)):
        pts = []
        for i in range(n * 2):
            a = i / (n * 2) * math.pi * 2
            rr = r if i % 2 == 0 else r * 0.8
            pts.append((gx + math.cos(a) * rr, gy + math.sin(a) * rr))
        c.paint(poly(pts, nrm(-0.3, -0.3, 0.9)), 'gold', gain=0.95, spec=0.6)
        c.paint(ellipse(gx, gy, r * 0.5, r * 0.5), 'gold', gain=0.6)
        c.paint(ellipse(gx, gy, r * 0.18, r * 0.18), 'silver', gain=1.0)
    pts = [(x + 50 + math.cos(t) * t * 1.6, y + 14 + math.sin(t) * t * 1.6) for t in [i * 0.4 for i in range(20)]]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.7), 'silver', gain=0.95, outline=False)


def automaton(c, x, base, s=1.0):
    """小さな機械人形（球の関節、ねじ巻き）。"""
    k = s
    c.paint(rect(x - 10 * k, base - 50 * k, x + 10 * k, base - 22 * k, lambda px, py: nrm((px - x) / (10 * k) * 0.8, 0, 0.7)), 'gold', gain=0.9, spec=0.5)
    c.paint(ellipse(x, base - 58 * k, 8 * k, 8 * k), 'gold', gain=1.0, spec=0.6)
    for ex in (-3, 3):
        c.paint(ellipse(x + ex * k, base - 59 * k, 1.6 * k, 1.6 * k), 'blue', emit=0.95, outline=False)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 11 * k, base - 46 * k, x + sg * 16 * k, base - 30 * k, 2.4 * k), 'silver', gain=0.9)
        c.paint(capsule(x + sg * 5 * k, base - 22 * k, x + sg * 6 * k, base, 2.6 * k), 'silver', gain=0.85)
    c.paint(capsule(x + 10 * k, base - 38 * k, x + 18 * k, base - 38 * k, 1.2 * k), 'silver', gain=1.0)
    c.paint(capsule(x + 18 * k, base - 43 * k, x + 18 * k, base - 33 * k, 1.2 * k), 'silver', gain=1.0)


def bog(c, y0):
    """沼: 濁った緑の水面、泡、葦。"""
    lt = c.light
    pix = [(x, y, FLAT) for y in range(int(y0), H) for x in range(W)]
    c.paint(pix, 'green', emit=lambda x, y, n: 0.12 + 0.3 * lt.att(x, y) + (0.07 if math.sin(y * 1.6 + math.sin(x / 8) * 2) > 0.7 else 0), dither=True, outline=False)
    for k in range(8):
        c.paint(ellipse(20 + k * 27, y0 + 10 + (k % 3) * 9, 2.4, 1.6), 'green', emit=0.6, outline=False)


def bog_monster(c, x, base, s=1.0):
    """沼の魔物: 泥から盛り上がる体、垂れる藻、光る目、伸びる腕。"""
    k = s
    c.paint(ellipse(x, base - 30 * k, 40 * k, 42 * k, clip=lambda px, py: py <= base), 'green', gain=0.6, spec=0.2,
            tex=lambda px, py: -0.1 if (int(px) * 3 + int(py)) % 7 == 0 else 0)
    for sg in (-1, 1):
        pts = [(x + sg * 30 * k, base - 40 * k), (x + sg * 54 * k, base - 56 * k), (x + sg * 64 * k, base - 40 * k)]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 7 * k, 5 * k), 'green', gain=0.55)
        for j in range(3):
            c.paint(capsule(pts[-1][0], pts[-1][1], pts[-1][0] + sg * (4 + j * 3) * k, pts[-1][1] + (8 - j * 6) * k, 1.6 * k), 'green', gain=0.5)
    for ex in (-12, 12):
        c.paint(ellipse(x + ex * k, base - 48 * k, 5 * k, 3.4 * k), 'gold', emit=1.0, outline=False)
    for j in range(7):
        sx = x - 30 * k + j * 10 * k
        c.paint(capsule(sx, base - 56 * k + abs(j - 3) * 6 * k, sx + 2, base - 30 * k + j % 2 * 6, 1.4 * k), 'foliage', gain=0.8, outline=False)
    c.paint(ellipse(x, base - 30 * k, 16 * k, 5 * k), 'stone', emit=0.05, outline=False)


def idol(c, x, base):
    """古の宝: 台座の上の黄金の像（座った姿）、額の紅玉、まわりの光。"""
    block(c, x - 30, base - 16, 60, 16, gain=0.95)
    c.paint(ellipse(x, base - 30, 22, 14), 'gold', gain=1.0, spec=0.7, shine=5)
    c.paint(capsule(x, base - 36, x, base - 60, 13, 10), 'gold', gain=1.0, spec=0.7, shine=5)
    c.paint(ellipse(x, base - 74, 11, 12), 'gold', gain=1.05, spec=0.7)
    c.paint(poly([(x - 12, base - 80), (x + 12, base - 80), (x, base - 98)], nrm(-0.3, -0.4, 0.8)), 'gold', gain=1.0, spec=0.6)
    for ex in (-4, 4):
        c.dot(int(x + ex), int(base - 75), 'G1')
    gem(c, x, base - 82, 3, 'red')
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 12, base - 54, x + sg * 6, base - 38, 3.6), 'gold', gain=0.9, spec=0.5)
    c.brighten(x, base - 54, 56, 60, 0.18)


def coach(c, x, base, w=90, h=50):
    """お召し馬車: 金の飾りの箱型、窓の灯、大きな後輪。"""
    wheel(c, x - w * 0.3, base - 14, r=14)
    wheel(c, x + w * 0.32, base - 18, r=18)
    pts = [(x - w / 2 + 6, base - 22), (x + w / 2 - 4, base - 22), (x + w / 2, base - h), (x + w / 2 - 10, base - h - 10), (x - w / 2 + 14, base - h - 10), (x - w / 2, base - h)]
    o = c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 0.8 - 0.1, -0.1, 0.9)), 'red', gain=1.0)
    window(c, x - 16, base - h + 2, 14, 14, True, oid=o)
    window(c, x + 6, base - h + 2, 14, 14, True, oid=o)
    c.paint(rect(x - w / 2, base - h - 12, x + w / 2, base - h - 8, nrm(0, -0.5, 0.8)), 'gold', gain=1.0, spec=0.6)
    for dx in (-w / 2 + 4, 0, w / 2 - 4):
        c.paint(ellipse(x + dx, base - h - 14, 3, 3), 'gold', spec=0.7)
    c.paint(rect(x - w / 2 + 6, base - 26, x + w / 2 - 4, base - 22), 'gold', gain=0.9, outline=False)
    c.paint(capsule(x - w / 2, base - 26, x - w / 2 - 40, base - 20, 1.6), 'wood', gain=0.9)


def target(c, x, y, r=34):
    """的: 藁の円に色の輪、刺さった矢。"""
    c.paint(capsule(x - 16, y + r, x - 6, y + 20, 2), 'wood', gain=0.9)
    c.paint(capsule(x + 16, y + r, x + 6, y + 20, 2), 'wood', gain=0.8)
    for k, (rr, col) in enumerate(((r, 'sand'), (r * 0.8, 'red'), (r * 0.6, 'paper'), (r * 0.4, 'blue'), (r * 0.2, 'gold'))):
        c.paint(ellipse(x, y, rr, rr * 0.95), col, gain=1.0 if k else 0.9, tex=(lambda px, py: -0.08 if int(px + py) % 4 == 0 else 0) if k == 0 else None)
    for dx, dy in ((4, -3), (-10, 8), (14, 12)):
        c.paint(capsule(x + dx, y + dy, x + dx + 18, y + dy - 10, 0.8), 'wood', gain=1.1)
        c.paint(poly([(x + dx + 18, y + dy - 10), (x + dx + 24, y + dy - 16), (x + dx + 22, y + dy - 8)]), 'red', gain=1.0)


def bonfire(c, x, base, s=1.0):
    """どんど焼き: 組んだ竹と藁の大きな火、舞う火の粉。"""
    k = s
    for i in range(7):
        a = -math.pi / 2 + (i - 3) * 0.16
        c.paint(capsule(x + (i - 3) * 6 * k, base, x + math.cos(a) * 70 * k * 0.25, base - 80 * k, 1.8 * k), 'green' if i % 2 else 'sand', gain=0.7)
    for i, (dx, rx, ry) in enumerate(((-24, 8, 18), (22, 9, 22), (-10, 11, 30), (12, 10, 34), (0, 14, 44))):
        flame(c, x + dx * k, base - ry * 0.7 * k, rx * k, ry * k)
    for i in range(16):
        c.dot(int(x - 40 * k + hsh(i, 7) * 80 * k), int(base - 70 * k - hsh(7, i) * 60 * k), 'G5' if i % 2 else 'R3')


def picnic(c, x, y):
    """遠出の野の昼餉: 格子の敷布、かご、パン、杯。"""
    pts = [(x - 60, y - 14), (x + 54, y - 18), (x + 66, y + 14), (x - 70, y + 18)]
    o = c.paint(poly(pts, UP), 'red', gain=1.0, tex=lambda px, py: -0.15 if (int(px) // 8 + int(py) // 5) % 2 == 0 else 0)
    from parts import basket
    basket(c, x - 20, y + 4, 30, 12, kind='bread', n=4)
    goblet(c, x + 26, y + 6, s=1.2, ramp='silver')
    c.paint(ellipse(x + 44, y + 2, 6, 5), 'red', spec=0.4)


def dummy(c, x, base):
    """稽古の藁人形（十字の木組みに藁の胴と頭）。"""
    c.paint(capsule(x, base, x, base - 80, 2.4), 'wood', gain=1.0)
    c.paint(capsule(x - 30, base - 60, x + 30, base - 60, 2.2), 'wood', gain=1.0)
    c.paint(ellipse(x, base - 52, 16, 22), 'sand', gain=1.0, tex=lambda px, py: -0.1 if int(px - py * 0.3) % 3 == 0 else 0)
    c.paint(ellipse(x, base - 84, 9, 10), 'sand', gain=1.05, tex=lambda px, py: -0.1 if int(px + py) % 3 == 0 else 0)
    for y in (base - 64, base - 40):
        c.paint(rect(x - 16, y, x + 16, y + 2), 'red', gain=0.9, outline=False)
    c.paint(capsule(x + 20, base - 30, x + 44, base - 4, 1.8), 'wood', gain=1.1)


def beast_shadow(c, x, base):
    """壁に映る獣の影（狼の形、暗く透ける）。"""
    pts = [(x - 40, base), (x - 36, base - 40), (x - 20, base - 56), (x - 8, base - 70), (x - 2, base - 92), (x + 6, base - 76), (x + 14, base - 92), (x + 18, base - 74),
           (x + 34, base - 70), (x + 44, base - 62), (x + 30, base - 54), (x + 24, base - 40), (x + 30, base)]
    pix = [(px, py, n) for px, py, n in poly(pts) if (px + py) % 2 == 0]
    c.paint(pix, 'purple', emit=0.08, outline=False)
    for ex in (8, 20):
        c.paint(ellipse(x + ex, base - 76, 2.4, 1.4), 'gold', emit=1.0, outline=False)


def treasure_chest_glow(c, x, base):
    chest(c, x - 32, base, 64, 30, fill='gold')
    c.brighten(x, base - 40, 50, 30, 0.25)


def hoe():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x + fig.f * 0.6 * u, fig.foot - 0.6 * u
        c.paint(capsule(x - fig.f * 0.6 * u, y - 2.2 * u, tx, ty, 0.13 * u), 'wood')
        c.paint(poly([(tx, ty - 0.3 * u), (tx + fig.f * 1.2 * u, ty), (tx + fig.f * 1.1 * u, ty + 0.5 * u), (tx, ty + 0.2 * u)], nrm(-0.3, -0.3, 0.9)), 'silver', spec=0.5)
    return draw


def trophy():
    def draw(c, fig, hand):
        goblet(c, hand[0], hand[1] - 0.1 * fig.u, s=fig.u / 9)
    return draw


def broken_sword():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        dx, dy = fig.f * 0.5, 0.86
        c.paint(capsule(x, y, x + dx * 1.8 * u, y + dy * 1.8 * u, 0.22 * u, 0.2 * u), 'silver', gain=0.8, spec=0.5)
        c.paint(capsule(x - fig.f * 0.6 * u, y - 0.2 * u, x + fig.f * 0.6 * u, y + 0.2 * u, 0.13 * u), 'gold', spec=0.5)
    return draw


def katana(deg=-60, length=4.4):
    def draw(c, fig, hand):
        u = fig.u
        a = math.radians(deg)
        dx, dy = math.cos(a) * fig.f, math.sin(a)
        x, y = hand
        pts = [(x + dx * t * length * u - dy * 0.0 + (-dy) * (t * t) * 0.6 * u * 0, y + dy * t * length * u + (t * t) * 0.5 * u * abs(dx)) for t in [i / 8 for i in range(9)]]
        for i, (p, q) in enumerate(zip(pts, pts[1:])):
            c.paint(capsule(p[0], p[1], q[0], q[1], 0.16 * u * (1 - i / 12)), 'silver', spec=0.8, shine=5)
        c.paint(capsule(x - dx * 1.0 * u, y - dy * 1.0 * u, x, y, 0.15 * u), 'red', gain=0.9)
        c.paint(ellipse(x + dx * 0.1 * u, y + dy * 0.1 * u, 0.3 * u, 0.3 * u), 'gold', spec=0.6)
    return draw


PROPS = {'hoe': hoe, 'trophy': trophy, 'broken_sword': broken_sword, 'katana': katana}


def bowl_floor(c, x, base):
    c.paint(ellipse(x, base - 4, 10, 6, clip=lambda px, py: py >= base - 5), 'wood', gain=1.0)
    c.paint(ellipse(x, base - 5, 10, 2.6), 'wood', gain=0.5)


def bowls_row(c, x, base):
    for k in range(3):
        bowl_floor(c, x + k * 18, base - (k % 2) * 3)


def parcel_big(c, x, base, w=60, h=40):
    o = c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.3, -0.1, 1)), 'paper', gain=0.9)
    c.paint(poly([(x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2 + 10, base - h - 7), (x - w / 2 + 10, base - h - 7)], UP), 'paper', gain=1.05)
    c.paint(rect(x - w / 2, base - h / 2 - 1, x + w / 2, base - h / 2 + 2), 'red', oid=o, gain=1.0, outline=False)
    c.paint(rect(x - 1, base - h, x + 2, base), 'red', oid=o, gain=1.0, outline=False)


def tag(c, x, y):
    c.paint(capsule(x - 18, y - 8, x, y, 0.5), 'paper', gain=0.6, outline=False)
    c.paint(poly([(x, y - 4), (x + 18, y - 4), (x + 18, y + 6), (x, y + 6), (x - 4, y + 1)], nrm(-0.2, 0, 1)), 'paper', gain=1.15)
    c.paint(rect(x + 3, y, x + 15, y + 1), 'red', gain=1.0, outline=False)


def ghost_city(c, x, base):
    """幻の都: 淡く発光する塔と円屋根の影（輪郭はほとんど消えている）。"""
    for k, (dx, w, h, kind) in enumerate(((-80, 18, 50, 0), (-52, 22, 76, 1), (-20, 26, 60, 2), (10, 30, 96, 0), (44, 22, 70, 1), (72, 18, 54, 2))):
        bx = x + dx
        e = 0.5 - abs(dx) / 400
        c.paint(rect(bx, base - h, bx + w, base), 'water', emit=lambda px, py, n, e=e, bx=bx: e + (0.12 if px - bx < 3 else 0), outline=False)
        if kind == 0:
            c.paint(poly([(bx - 2, base - h), (bx + w + 2, base - h), (bx + w / 2, base - h - w * 1.2)]), 'water', emit=e + 0.1, outline=False)
        elif kind == 1:
            c.paint(ellipse(bx + w / 2, base - h, w / 2, w / 2, clip=lambda px, py, b=base - h: py <= b), 'water', emit=e + 0.08, outline=False)
        for j in range(int(h / 12)):
            c.dot(int(bx + w / 2), int(base - h + 6 + j * 12), 'S3')


def blueprint(c, x, y, w=150, h=60):
    """図面: 青い紙に白い線の間取り、印の駒。"""
    pts = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2 - 4), (x + w / 2 + 6, y + h / 2), (x - w / 2 - 6, y + h / 2 + 4)]
    o = c.paint(poly(pts, UP), 'blue', gain=0.95)
    for a, b in (((x - 50, y - 18), (x + 40, y - 20)), ((x + 40, y - 20), (x + 44, y + 18)), ((x + 44, y + 18), (x - 54, y + 20)), ((x - 54, y + 20), (x - 50, y - 18)),
                 ((x - 6, y - 19), (x - 6, y + 19)), ((x - 6, y), (x + 42, y - 1))):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'paper', oid=o, emit=0.75, outline=False)
    for px, py, col in ((x - 30, y - 4, 'red'), (x + 20, y + 10, 'gold'), (x + 24, y - 12, 'green')):
        c.paint(vcyl(px, py - 8, py, 3, 1.2), col, gain=1.1, spec=0.4)


def route_line(c, x0, y0, x1, y1):
    for t in range(0, 20, 2):
        a, b = t / 20, (t + 1) / 20
        c.paint(capsule(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b, 0.8), 'gold', emit=0.8, outline=False)


def cloth_bolts(c, x, base):
    for k, col in enumerate(('red', 'blue', 'green')):
        c.paint(capsule(x - 30 + k * 4, base - 8 - k * 10, x + 30 + k * 4, base - 8 - k * 10, 5, flat=0.2), col, gain=1.0)
        c.paint(ellipse(x - 30 + k * 4, base - 8 - k * 10, 2.4, 5, normal=nrm(-0.8, 0, 0.6)), col, gain=0.8)


def glow_scroll(c, x, y):
    c.paint(rect(x - 30, y - 8, x + 30, y + 8, nrm(-0.2, -0.3, 0.9)), 'paper', gain=1.15)
    for sx in (x - 32, x + 32):
        c.paint(capsule(sx, y - 11, sx, y + 11, 3), 'red', gain=1.0)
    for k in range(3):
        c.paint(rect(x - 22, y - 4 + k * 3, x + 22, y - 3 + k * 3), 'leather', gain=0.6, outline=False)
    c.brighten(x, y, 60, 40, 0.3)


def katana_flat(c, x, y):
    """床に置いた鞘入りの刀。"""
    c.paint(capsule(x - 40, y, x + 30, y - 4, 2.2), 'cloth', gain=0.9, spec=0.4)
    c.paint(capsule(x + 30, y - 4, x + 48, y - 5, 2.0), 'red', gain=0.9)
    c.paint(ellipse(x + 30, y - 4, 2.4, 3.2), 'gold', spec=0.6)
