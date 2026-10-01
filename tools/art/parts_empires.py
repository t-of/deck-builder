"""帝国（empires）で足した部品。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import (UP, block, castle, chest, coin, coin_stack, column, crenel_wall, flame, gem, goblet, hedge, rocks, skull,
                   stone_wall, tower, tree, wheel, window, horse, paper_lantern, flower)
from parts_darkages import smoke_column


def trebuchet(c, x, base, s=1.0):
    """投石機: 三角の脚、長い腕、重りの箱、投げ袋。"""
    k = s
    for dx in (-30, 30):
        c.paint(capsule(x + dx * k, base, x, base - 70 * k, 3 * k), 'wood', gain=1.0 if dx < 0 else 0.8)
    c.paint(capsule(x - 34 * k, base - 2, x + 34 * k, base - 2, 3 * k), 'wood', gain=0.9)
    ax, ay = x, base - 70 * k
    c.paint(capsule(ax - 60 * k, ay - 40 * k, ax + 26 * k, ay + 16 * k, 2.6 * k, 3.6 * k), 'wood', gain=1.05)
    c.paint(rect(ax + 18 * k, ay + 16 * k, ax + 40 * k, ay + 38 * k, nrm(-0.2, 0, 1)), 'wood', gain=0.85, tex=lambda px, py: -0.1 if int(py) % 5 == 0 else 0)
    c.paint(capsule(ax - 60 * k, ay - 40 * k, ax - 66 * k, ay - 16 * k, 0.6), 'paper', gain=0.6, outline=False)
    c.paint(ellipse(ax - 66 * k, ay - 12 * k, 6 * k, 6 * k), 'stone', gain=1.0)
    c.paint(ellipse(ax, ay, 4 * k, 4 * k), 'silver', gain=1.0)
    for dx in (-24, 24):
        wheel(c, x + dx * k, base - 8 * k, r=8 * k)


def pebble_pile(c, x, base, w=60):
    """石ころの山（丸い小石が積もる）。"""
    for k in range(40):
        u = (hsh(k, 3) - 0.5) * 2
        h = (1 - u * u) * 26
        px = x + u * w
        py = base - hsh(3, k) * h
        r = 3 + hsh(k, 9) * 3
        c.paint(ellipse(px, py, r * 1.2, r), 'stone', gain=0.9 + 0.2 * hsh(k, 1), spec=0.2)


def arena(c, y0, x0=0, x1=W):
    """闘技場: 半円の観客席の段、砂の床、柵。"""
    for k in range(5):
        top = y0 - 60 + k * 12
        c.paint(rect(x0, top, x1, top + 12, nrm(0, -0.3 - k * 0.05, 1)), 'stone', gain=0.55 + k * 0.08, dither=True, outline=False,
                tex=lambda px, py: -0.1 if int(px) % 14 == 0 else 0)
        for j in range(int(W / 10)):
            if hsh(j, k, 5) < 0.4:
                c.dot(int(j * 10 + 4), int(top + 4), ('R2', 'B2', 'G4', 'E2')[j % 4])
    for k in range(int(W / 28) + 1):
        column(c, k * 28, y0 - 20, y0, r=3, gain=0.8)
    c.paint(rect(x0, y0, x1, H, UP), 'sand', gain=0.9, dither=True, outline=False)


def chariot(c, x, base):
    """二輪の戦車: 車輪、弧の囲い、引き棒。"""
    wheel(c, x, base - 16, r=16)
    pts = [(x - 20, base - 18), (x + 18, base - 18), (x + 22, base - 46), (x + 6, base - 50), (x - 4, base - 38)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / 20 * 0.6, -0.2, 0.8)), 'red', gain=1.0)
    c.paint(capsule(x - 20, base - 18, x + 22, base - 46, 1.4), 'gold', gain=1.0, spec=0.5, outline=False)
    c.paint(capsule(x - 20, base - 22, x - 70, base - 30, 1.6), 'wood', gain=0.9)


def torii(c, x, base, w=110, h=100, ramp='red'):
    """お社の鳥居（2 本柱、2 本の横木、反った笠木）。"""
    for sg in (-1, 1):
        c.paint(vcyl(x + sg * w * 0.36, base - h, base, 5, 1.6, top=False), ramp, gain=1.0 if sg < 0 else 0.85)
    c.paint(rect(x - w * 0.42, base - h * 0.78, x + w * 0.42, base - h * 0.72, nrm(0, -0.3, 1)), ramp, gain=0.95)
    pts = [(x - w / 2 - 6, base - h - 6), (x, base - h - 2), (x + w / 2 + 6, base - h - 6), (x + w / 2 + 4, base - h + 2), (x, base - h + 4), (x - w / 2 - 4, base - h + 2)]
    c.paint(poly(pts, nrm(0, -0.4, 0.9)), 'cloth', gain=0.8)
    c.paint(rect(x - w / 2, base - h + 4, x + w / 2, base - h + 10, nrm(0, 0, 1)), ramp, gain=1.0)


def hedge_maze(c, x0, y0, x1, y1):
    """生垣の迷路（上から斜めに見る）: 通路は砂、垣は緑。"""
    cols, rows = 9, 6
    cw, rh = (x1 - x0) / cols, (y1 - y0) / rows
    c.paint(rect(x0, y0, x1, y1, UP), 'sand', gain=0.8, outline=False)
    for i in range(cols + 1):
        for j in range(rows + 1):
            x, y = x0 + i * cw, y0 + j * rh
            if j < rows and (hsh(i, j, 3) < 0.55 or i in (0, cols)):
                c.paint(rect(x - 2, y, x + 3, y + rh + 2, nrm(-0.2, -0.6, 0.7)), 'foliage', gain=0.9 + 0.1 * (j / rows))
            if i < cols and (hsh(j, i, 4) < 0.5 or j in (0, rows)):
                c.paint(rect(x, y - 2, x + cw + 2, y + 3, nrm(0, -0.8, 0.6)), 'foliage', gain=0.95 + 0.1 * (j / rows))


def dohyo(c, x, base, w=150):
    """土俵: 盛り土の台、俵の円、吊り屋根。"""
    c.paint(poly([(x - w / 2, base), (x + w / 2, base), (x + w / 2 - 14, base - 22), (x - w / 2 + 14, base - 22)], nrm(-0.1, -0.3, 0.9)), 'sand', gain=0.9)
    c.paint(ellipse(x, base - 22, w / 2 - 14, 14, normal=UP), 'sand', gain=1.1)
    pts = arc_points(x, base - 22, 1, 0, math.pi * 2, 40)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(x + (a[0] - x) * (w / 2 - 26), base - 22 + (a[1] - base + 22) * 10, x + (b[0] - x) * (w / 2 - 26), base - 22 + (b[1] - base + 22) * 10, 1.6), 'paper', gain=1.0)
    rt = base - 120
    c.paint(poly([(x - w / 2 - 6, rt + 18), (x + w / 2 + 6, rt + 18), (x + w * 0.3, rt), (x - w * 0.3, rt)], nrm(-0.1, -0.6, 0.8)), 'wood', gain=0.9)
    for k, col in enumerate(('blue', 'red', 'paper', 'stone')):
        px = x - w / 2 + 10 + k * (w - 20) / 3
        c.paint(capsule(px, rt + 18, px, rt + 34, 3), col, gain=1.0)


def steam(c, pts):
    for x, y in pts:
        for k in range(6):
            t = k / 5
            c.paint(ellipse(x + math.sin(t * 4) * 6, y - t * 30, 5 + t * 6, 4 + t * 3), 'paper', emit=0.5 - t * 0.2, outline=False, dither=True)


def wood_tub(c, x, base, w=100, h=26):
    c.paint(rect(x - w / 2, base - h, x + w / 2, base, lambda px, py: nrm((px - x) / w * 0.6, 0, 0.9)), 'wood', gain=1.0, tex=lambda px, py: -0.12 if int(px) % 6 == 0 else 0)
    c.paint(ellipse(x, base - h, w / 2, 7), 'wood', gain=1.1)
    c.paint(ellipse(x, base - h, w / 2 - 4, 5), 'water', emit=0.55)
    for y in (base - h + 6, base - 6):
        c.paint(rect(x - w / 2, y, x + w / 2, y + 2), 'silver', gain=0.8, outline=False)


def noren(c, x0, x1, y, ramp='blue'):
    n = 4
    w = (x1 - x0) / n
    for k in range(n):
        o = c.paint(rect(x0 + k * w + 1, y, x0 + (k + 1) * w - 1, y + 26, lambda px, py: nrm(0.2 * math.sin(px / 3), 0, 1)), ramp, gain=1.0)
    c.paint(ellipse((x0 + x1) / 2, y + 12, 6, 6), 'paper', gain=1.2, outline=False)


def battlefield(c, y0):
    """古戦場: 地に刺さった剣と槍、倒れた旗、兜、髑髏。"""
    for k, (x, ang) in enumerate(((30, -80), (70, -100), (130, -70), (176, -95), (206, -110))):
        a = math.radians(ang)
        c.paint(capsule(x, y0 + 30, x + math.cos(a) * 34, y0 + 30 + math.sin(a) * 34, 1.2), 'silver' if k % 2 else 'wood', gain=0.85)
        c.paint(capsule(x + math.cos(a) * 20 - 5, y0 + 30 + math.sin(a) * 20, x + math.cos(a) * 20 + 5, y0 + 30 + math.sin(a) * 20, 1.2), 'gold', gain=0.8)
    c.paint(capsule(100, y0 + 40, 150, y0 + 20, 1.4), 'wood', gain=0.8)
    c.paint(poly([(150, y0 + 20), (176, y0 + 30), (170, y0 + 44), (146, y0 + 34)], nrm(0.2, -0.5, 0.8)), 'red', gain=0.8)
    skull(c, 90, y0 + 46, 0.9)
    c.paint(ellipse(56, y0 + 50, 9, 6, clip=lambda px, py: py < y0 + 52), 'silver', gain=0.8, spec=0.5)


def arcade_arches(c, x0, x1, top, base, n=5):
    """回廊: 列柱とアーチが奥へ並ぶ（手前ほど大きい）。"""
    for k in range(n - 1, -1, -1):
        t = k / (n - 1)
        s = 1 - t * 0.6
        cx = x0 + (x1 - x0) * (0.5 + 0.35 * (1 - t))
        h = (base - top) * s
        w = 60 * s
        b = base - (1 - s) * 30
        g = 0.55 + 0.45 * s
        column(c, cx - w / 2, b - h, b, r=5 * s, gain=g)
        column(c, cx + w / 2, b - h, b, r=5 * s, gain=g)
        pts = arc_points(cx, b - h + w / 2, w / 2, math.pi, 2 * math.pi, 12)
        for a2, b2 in zip(pts, pts[1:]):
            c.paint(capsule(a2[0], a2[1], b2[0], b2[1], 4 * s), 'stone', gain=g)


def obelisk(c, x, base, w=26, h=120):
    pts = [(x - w / 2, base), (x + w / 2, base), (x + w * 0.36, base - h), (x, base - h - 14), (x - w * 0.36, base - h)]
    o = c.paint(poly(pts, lambda px, py: nrm(-0.2 if px < x else 0.6, -0.1, 0.9)), 'stone', gain=1.05, tex=lambda px, py: -0.04 if (int(px) * 3 + int(py)) % 13 == 0 else 0)
    for k in range(6):
        y = base - h + 18 + k * 14
        c.paint(rect(x - 5, y, x + 5, y + 6), 'gold', oid=o, gain=0.9, outline=False)
    block(c, x - w / 2 - 12, base - 12, w + 24, 12, gain=0.95)


def burial_mound(c, x, base, w=170, h=50):
    """塚: 草の盛り土、石の入口、まわりの立石。"""
    pts = [(x - w / 2, base)] + [(x - w / 2 + w * t, base - h * math.sin(t * math.pi) ** 0.7) for t in [i / 20 for i in range(1, 20)]] + [(x + w / 2, base)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 1.2, -0.7, 0.6)), 'foliage', gain=0.85, dither=True)
    c.paint(rect(x - 12, base - 24, x + 12, base), 'stone', emit=0.05, outline=False)
    block(c, x - 18, base - 30, 36, 6, gain=1.0)
    for dx in (-14, 12):
        c.paint(rect(x + dx, base - 24, x + dx + 3, base), 'stone', gain=0.95)


def pagoda(c, x, base, levels=4, w=60):
    """高楼: 段ごとに反った屋根の重なる塔。"""
    y = base
    for k in range(levels):
        ww = w * (1 - k * 0.16)
        hh = 26 - k * 2
        c.paint(rect(x - ww * 0.36, y - hh, x + ww * 0.36, y, lambda px, py: nrm((px - x) / ww * 1.2, 0, 0.8)), 'red', gain=0.9)
        window(c, x - 4, y - hh + 6, 8, 10, True, arch=False)
        pts = [(x - ww / 2 - 6, y - hh + 2), (x + ww / 2 + 6, y - hh + 2), (x + ww * 0.36, y - hh - 8), (x - ww * 0.36, y - hh - 8)]
        c.paint(poly(pts, nrm(-0.1, -0.6, 0.8)), 'cloth', gain=0.85)
        y -= hh + 8
    c.paint(capsule(x, y + 2, x, y - 18, 1.4), 'gold', spec=0.6)


def great_gate(c, x, base, w=150, h=110):
    """大門: 二層の屋根、大きな扉、門の灯。"""
    stone_wall(c, int(base - h * 0.6), int(base), x0=int(x - w / 2), x1=int(x + w / 2), bw=14, bh=8, gain=0.9, seed=41)
    pts = [(x - 26, base), (x - 26, base - 50)] + arc_points(x, base - 50, 26, math.pi, 2 * math.pi, 12) + [(x + 26, base)]
    c.paint(poly(pts), 'wood', gain=0.85, tex=lambda px, py: -0.12 if int(px - x) % 8 == 0 else 0)
    c.paint(rect(x - 1, base - 76, x + 1, base), 'stone', emit=0.05, outline=False)
    for ry, rw in ((base - h * 0.6, w + 20), (base - h * 0.85, w * 0.7)):
        c.paint(poly([(x - rw / 2, ry), (x + rw / 2, ry), (x + rw * 0.38, ry - 18), (x - rw * 0.38, ry - 18)], nrm(-0.1, -0.6, 0.8)), 'blue', gain=0.9)
    c.paint(rect(x - w * 0.3, base - h * 0.85, x + w * 0.3, base - h * 0.6, nrm(-0.2, 0, 1)), 'red', gain=0.9)
    for dx in (-40, 40):
        paper_lantern(c, x + dx, base - h * 0.5, 7, 'gold', string=base - h * 0.6)


def long_wall(c, y_top, y_base):
    """城壁が左手前から右奥へ続く（遠近で低く細る）。"""
    segs = 7
    for k in range(segs - 1, -1, -1):
        t = k / (segs - 1)
        s = 1 - t * 0.75
        x0 = 0 + t * 180
        w = 70 * s
        top = y_base - (y_base - y_top) * s - t * 34
        bot = y_base - t * 40
        crenel_wall(c, x0, x0 + w + 2, top, bot, merlon=max(3, int(8 * s)), gap=max(2, int(5 * s)), gain=0.5 + 0.5 * s)
        if k % 2 == 0:
            tower(c, x0 + w - 8 * s, bot, 18 * s, (bot - top) * 1.5, roof=None, crenel=True, gain=0.5 + 0.5 * s)


def fruit_tree(c, x, base, h=70, fruit='red'):
    tree(c, x, base, h, kind='oak', gain=0.9, seed=int(x))
    for k in range(9):
        a = hsh(k, int(x)) * math.pi * 2
        r = hsh(int(x), k) * h * 0.24
        c.paint(ellipse(x + math.cos(a) * r * 1.2, base - h * 0.66 + math.sin(a) * r * 0.8, 2.6, 2.6), fruit, gain=1.1, spec=0.5)


def vortex(c, x, y, r=60, ramp='purple'):
    """取り込みの渦（腕の巻く光、中心は闇）。"""
    for arm in range(3):
        pts = [(x + math.cos(t + arm * 2.1) * t * r / 7, y + math.sin(t + arm * 2.1) * t * r / 14) for t in [i * 0.25 for i in range(29)]]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1 + i * 0.12), ramp, emit=0.85 - i * 0.02, outline=False)
    c.paint(ellipse(x, y, 8, 4), 'stone', emit=0.02, outline=False)


def clover(c, x, y, r=14):
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        cx, cy = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
        c.paint(ellipse(cx, cy, r * 0.5, r * 0.5), 'green', gain=1.05, spec=0.3)
        c.paint(capsule(x, y, cx, cy, 0.6), 'green', gain=0.7, outline=False)
    c.paint(capsule(x, y, x + 4, y + r * 1.4, 1.2), 'green', gain=0.9)


def horseshoe(c, x, y, r=24):
    pts = arc_points(x, y, r, math.pi * 0.85, math.pi * 2.15, 20)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 5), 'gold', spec=0.7, shine=5)
    for t in (0.15, 0.35, 0.65, 0.85):
        px, py = pts[int(t * (len(pts) - 1))]
        c.paint(ellipse(px, py, 1.4, 1.4), 'stone', emit=0.05, outline=False)


def scepter(c, x0, y0, x1, y1):
    c.paint(capsule(x0, y0, x1, y1, 3), 'gold', spec=0.7, shine=5)
    for t in (0.2, 0.5, 0.8):
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        c.paint(ellipse(cx, cy, 4.5, 4.5), 'gold', spec=0.7)
    c.paint(ellipse(x1, y1, 10, 10), 'gold', spec=0.7)
    gem(c, x1, y1 - 2, 6, 'red')
    c.paint(rect(x1 - 1, y1 - 20, x1 + 1, y1 - 9), 'gold', gain=1.1)
    c.paint(rect(x1 - 5, y1 - 17, x1 + 5, y1 - 15), 'gold', gain=1.1)


def ghosts(c, pts):
    """亡霊（下が尾のように細る白い影）。"""
    for x, y in pts:
        pts2 = [(x - 8, y), (x - 9, y - 12)] + arc_points(x, y - 12, 9, math.pi, 2 * math.pi, 10) + [(x + 9, y - 12), (x + 8, y), (x + 4, y + 10), (x, y + 4), (x - 4, y + 12)]
        pix = [(px, py, n) for px, py, n in poly(pts2) if (px + py) % 2 == 0 or py < y - 6]
        c.paint(pix, 'paper', emit=0.6, outline=False)
        for ex in (-3, 3):
            c.dot(int(x + ex), int(y - 14), 'N0')


def ivy(c, x0, x1, top, base):
    for k in range(int((x1 - x0) / 6)):
        x = x0 + k * 6 + hsh(k, 3) * 4
        ln = (base - top) * (0.3 + 0.6 * hsh(3, k))
        for j in range(int(ln / 5)):
            c.paint(ellipse(x + math.sin(j) * 2, base - j * 5, 2.4, 2), 'foliage', gain=0.9 + 0.1 * (j % 2), outline=False)


def debt_tokens(c, pts):
    """借金の札（赤い丸札）。"""
    for x, y in pts:
        c.paint(ellipse(x, y, 8, 6), 'red', gain=1.0, spec=0.3)
        c.paint(ellipse(x, y - 1, 5, 3), 'red', gain=0.7, outline=False)


def lock_canal(c, y0):
    """用水路の水門: 石の岸の間の水、木の門扉。"""
    lt = c.light
    pts = [(80, y0), (144, y0), (200, H), (24, H)]
    c.paint(poly(pts), 'water', emit=lambda px, py, n: 0.25 + 0.35 * lt.att(px, py) + (0.08 if math.sin(py * 1.3) > 0.7 else 0), dither=True)
    for sg, xs in ((-1, (80, 24)), (1, (144, 200))):
        q = [(xs[0], y0), (xs[0] + sg * 70, y0), (xs[1] + sg * 80, H), (xs[1], H)]
        c.paint(poly(q, UP), 'stone', gain=0.9, tex=lambda px, py: -0.1 if int(py) % 8 == 0 else 0)
    c.paint(rect(84, y0 + 20, 140, y0 + 28, nrm(0, -0.3, 1)), 'wood', gain=1.0)
    c.paint(rect(70, y0 + 28, 154, y0 + 44, nrm(-0.2, 0, 1)), 'wood', gain=0.85, tex=lambda px, py: -0.1 if int(px) % 8 == 0 else 0)


def trident():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        top = y - 4.6 * u
        c.paint(capsule(x, y + 2.0 * u, x, top, 0.13 * u), 'wood')
        for dx in (-0.5, 0, 0.5):
            c.paint(capsule(x + dx * u, top, x + dx * u, top - 1.2 * u, 0.1 * u), 'silver', spec=0.6)
        c.paint(capsule(x - 0.5 * u, top, x + 0.5 * u, top, 0.1 * u), 'silver')
    return draw


def round_shield(ramp='gold'):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(ellipse(x, y - 0.4 * u, 1.6 * u, 1.6 * u), ramp, spec=0.6, shine=5)
        c.paint(ellipse(x, y - 0.4 * u, 1.2 * u, 1.2 * u), 'red', gain=0.9)
        c.paint(ellipse(x, y - 0.4 * u, 0.35 * u, 0.35 * u), ramp, spec=0.7)
    return draw


def shears():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        for sg in (-1, 1):
            c.paint(capsule(x, y, x + fig.f * 2.0 * u, y - (1.0 + sg * 0.25) * u, 0.12 * u), 'silver', spec=0.6)
        c.paint(capsule(x - fig.f * 0.8 * u, y + 0.3 * u, x, y, 0.15 * u), 'wood')
    return draw


def wrench():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x + fig.f * 1.6 * u, y - 1.2 * u
        c.paint(capsule(x, y, tx, ty, 0.15 * u), 'silver', spec=0.6)
        c.paint(ellipse(tx, ty, 0.4 * u, 0.4 * u), 'silver', gain=0.9, spec=0.5)
        c.paint(ellipse(tx + fig.f * 0.2 * u, ty - 0.2 * u, 0.18 * u, 0.18 * u), 'stone', emit=0.05, outline=False)
    return draw


def net_held():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        for k in range(5):
            c.paint(capsule(x, y, x - fig.f * (0.6 + k * 0.3) * u, fig.foot - 0.4 * u, 0.3), 'paper', gain=0.7, outline=False)
        for j in range(3):
            yy = y + (j + 1) * (fig.foot - y) / 4
            c.paint(capsule(x - fig.f * 0.3 * u, yy, x - fig.f * 1.8 * u, yy, 0.3), 'paper', gain=0.6, outline=False)
    return draw


PROPS = {'trident': trident, 'round_shield': round_shield, 'shears': shears, 'wrench': wrench, 'net_held': net_held}


def helmet_floor(c, x, base):
    c.paint(ellipse(x, base - 8, 13, 12, clip=lambda px, py: py <= base - 2), 'silver', gain=0.9, spec=0.6)
    c.paint(rect(x - 13, base - 4, x + 13, base), 'silver', gain=0.7)
    c.paint(ellipse(x - 2, base - 22, 8, 4), 'red', gain=0.9)


def benches(c, y0):
    for k in range(3):
        y = y0 + k * 9
        w = 140 + k * 30
        c.paint(rect(112 - w / 2, y, 112 + w / 2, y + 3, UP), 'wood', gain=1.0 + k * 0.05)
        c.paint(rect(112 - w / 2, y + 3, 112 + w / 2, y + 6, nrm(0, 0.2, 1)), 'wood', gain=0.7)


def flower_arch(c, x, base, w=100, h=110):
    for sg in (-1, 1):
        c.paint(capsule(x + sg * w / 2, base, x + sg * w / 2, base - h * 0.6, 2), 'wood', gain=0.9)
    pts = arc_points(x, base - h * 0.6, w / 2, math.pi, 2 * math.pi, 18)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2), 'wood', gain=0.9)
    for k, (px, py) in enumerate(pts + [(x - w / 2, base - h * 0.6 + j * 10) for j in range(6)] + [(x + w / 2, base - h * 0.6 + j * 10) for j in range(6)]):
        flower(c, px, py, 3.4, ('red', 'paper', 'gold', 'purple')[k % 4], stem=0)


def candle_ring(c, x, y, rx=70, ry=16, n=8):
    from parts import candle
    for k in range(n):
        a = k / n * math.pi * 2
        cx, cy = x + math.cos(a) * rx, y + math.sin(a) * ry
        if math.sin(a) < 0:
            candle(c, cx, cy, h=8, r=2, holder=False)
    for k in range(n):
        a = k / n * math.pi * 2
        cx, cy = x + math.cos(a) * rx, y + math.sin(a) * ry
        if math.sin(a) >= 0:
            candle(c, cx, cy, h=10, r=2.5, holder=False)


def fire_line(c, y):
    for k in range(9):
        x = 10 + k * 25 + hsh(k, 3) * 8
        ry = 8 + 14 * hsh(k, 4)
        flame(c, x, y - ry * 0.6, 4 + ry * 0.3, ry)


def beast_eyes(c, x, y):
    for ex in (-14, 14):
        c.paint(ellipse(x + ex, y, 6, 3.5), 'gold', emit=1.0, outline=False)
        c.paint(ellipse(x + ex, y, 1.5, 3), 'stone', emit=0.05, outline=False)


def bones(c, pts):
    for k, (x, y) in enumerate(pts):
        a = hsh(k, 7) * 2 - 1
        c.paint(capsule(x - 10, y + a * 3, x + 10, y - a * 3, 1.6), 'paper', gain=0.9)
        for sx in (x - 10, x + 10):
            c.paint(ellipse(sx, y + (a * 3 if sx < x else -a * 3), 2.4, 2.4), 'paper', gain=0.95)
