"""夜想曲（nocturne）で足した部品: 恵み・呪詛の情景、精霊と怪物、家宝。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import (UP, block, chest, coin, flame, gem, goblet, rocks, skull, stone_wall, wheel, window, flower, haystack, tree)


def sun(c, x, y, r=22):
    """昇る日: 白金の芯から橙へ、まわりに淡い暈。"""
    c.paint(ellipse(x, y, r, r), 'fire', emit=lambda px, py, n: 1.0 - math.hypot(px - x, py - y) / r * 0.5, outline=False)
    c.brighten(x, y, r * 4, r * 3, 0.25)


def will_o_wisp(c, x, y, r=5, ramp='blue'):
    """鬼火: 尾を引いて揺れる光の玉。"""
    c.brighten(x, y, r * 9, r * 9, 0.09)
    for k in range(5, -1, -1):
        t = k / 5
        c.paint(ellipse(x - t * 8, y + t * 10 + math.sin(t * 5) * 3, r * (1 - t * 0.7), r * (1 - t * 0.7)), ramp, emit=1.0 - t * 0.25, outline=False)
    c.paint(ellipse(x - r * 0.25, y - r * 0.25, r * 0.4, r * 0.4), 'paper', emit=1.0, outline=False)


def imp(c, x, base, s=1.0, ramp='red'):
    """小悪魔: 丸い体、角、蝙蝠の羽、尖った尾、光る目。"""
    k = s
    for sg in (-1, 1):
        pts = [(x + sg * 6 * k, base - 30 * k), (x + sg * 30 * k, base - 46 * k), (x + sg * 26 * k, base - 30 * k), (x + sg * 32 * k, base - 22 * k), (x + sg * 10 * k, base - 22 * k)]
        c.paint(poly(pts, nrm(sg * 0.2, -0.2, 0.9)), 'purple', gain=0.8)
    pts = [(x + 8 * k, base - 6 * k), (x + 22 * k, base - 2 * k), (x + 30 * k, base - 12 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.2 * k), ramp, gain=0.9)
    c.paint(poly([(pts[-1][0], pts[-1][1] - 4 * k), (pts[-1][0] + 6 * k, pts[-1][1]), (pts[-1][0], pts[-1][1] + 3 * k)]), ramp, gain=1.0)
    c.paint(ellipse(x, base - 16 * k, 12 * k, 14 * k), ramp, gain=1.0, spec=0.2)
    c.paint(ellipse(x, base - 34 * k, 10 * k, 9 * k), ramp, gain=1.05)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 6 * k, base - 40 * k, x + sg * 10 * k, base - 50 * k, 2 * k, 0.6 * k), 'paper', gain=1.0)
        c.paint(ellipse(x + sg * 4 * k, base - 35 * k, 2.2 * k, 1.6 * k), 'gold', emit=1.0, outline=False)
        c.paint(capsule(x + sg * 6 * k, base - 4 * k, x + sg * 8 * k, base, 2 * k), ramp, gain=0.85)
    for j in range(3):
        c.dot(int(x - 3 * k + j * 3 * k), int(base - 29 * k), 'S3')


def fairy_wings(c, x, y, s=1.0):
    """妖精の羽（透ける 4 枚）。"""
    k = s
    for sg in (-1, 1):
        for big, (dx, dy, rx, ry) in enumerate(((22, -14, 18, 12), (16, 10, 12, 8))):
            pix = [(px, py, n) for px, py, n in ellipse(x + sg * dx * k, y + dy * k, rx * k, ry * k) if (px + py) % 2 == 0]
            c.paint(pix, 'water', emit=0.75, outline=False)
    c.brighten(x, y, 50 * k, 40 * k, 0.2)


def goat(c, x, base, s=1.0, facing=1, ramp='paper', kid=True):
    """山羊（子山羊）: 細い脚、短い角、あごひげ、立った尾。"""
    k = s
    f = facing
    X = lambda dx: x + f * -dx * k
    by = base - 22 * k
    for hx, fx, g in ((-10, -11, 0.75), (10, 11, 0.8)):
        c.paint(capsule(X(hx), by + 4 * k, X(fx), base, 2.2 * k, 1.4 * k), ramp, gain=g)
    c.paint(ellipse(x, by, 15 * k, 8 * k), ramp, gain=1.0, tex=lambda px, py: -0.06 if (int(px) + int(py)) % 3 == 0 else 0)
    c.paint(capsule(X(12), by - 2 * k, X(16), by - 14 * k, 4 * k, 3.4 * k), ramp, gain=1.05)
    c.paint(capsule(X(16), by - 15 * k, X(23), by - 11 * k, 3.4 * k, 2 * k), ramp, gain=1.1)
    for dx in (14, 17):
        c.paint(capsule(X(dx), by - 18 * k, X(dx - 6), by - 22 * k, 1.1 * k, 0.5 * k), 'leather', gain=1.0)
    c.paint(poly([(X(13), by - 17 * k), (X(9), by - 18 * k), (X(12), by - 14 * k)]), ramp, gain=0.9)
    c.paint(capsule(X(21), by - 9 * k, X(21), by - 5 * k, 1 * k), ramp, gain=0.9)
    c.dot(int(X(18)), int(by - 15 * k), 'N0')
    c.paint(capsule(X(-14), by - 4 * k, X(-17), by - 9 * k, 1.4 * k), ramp, gain=1.0)
    for hx, fx, g in ((-14, -15, 1.0), (14, 15, 1.05)):
        c.paint(capsule(X(hx), by + 4 * k, X(fx), base, 2.2 * k, 1.4 * k), ramp, gain=g)
        c.paint(ellipse(X(fx), base, 1.8 * k, 1.2 * k), 'hair', gain=0.8)


def sheep(c, x, base, s=1.0, facing=1):
    """羊: もこもこの毛（丸の重なり）、黒い顔と脚。"""
    k = s
    f = facing
    for dx in (-8, 8):
        c.paint(capsule(x + dx * k, base - 8 * k, x + dx * k, base, 1.8 * k), 'cloth', gain=0.6)
    for j, (dx, dy) in enumerate(((-8, -14), (0, -18), (8, -14), (-4, -10), (6, -9), (-11, -9), (12, -10))):
        c.paint(ellipse(x + dx * k, base + dy * k, 7 * k, 6 * k), 'paper', gain=1.0 + 0.04 * (j % 3), spec=0.1)
    c.paint(ellipse(x + f * 15 * k, base - 16 * k, 4.5 * k, 5 * k), 'cloth', gain=0.6)
    c.dot(int(x + f * 17 * k), int(base - 17 * k), 'S2')


def bats(c, pts):
    """蝙蝠の群れ（翼を広げた影）。"""
    for k, (x, y, s) in enumerate(pts):
        for sg in (-1, 1):
            p = [(x, y), (x + sg * 6 * s, y - 4 * s), (x + sg * 12 * s, y - 2 * s), (x + sg * 10 * s, y + 2 * s), (x + sg * 6 * s, y), (x + sg * 3 * s, y + 3 * s)]
            c.paint(poly(p, nrm(0, -0.3, 0.9)), 'cloth', gain=0.55)
        c.paint(ellipse(x, y, 2.4 * s, 3 * s), 'cloth', gain=0.6)


def locust_swarm(c, x, y, n=60, w=90, h=40, seed=0):
    for k in range(n):
        px = int(x + (hsh(k, seed) - 0.5) * 2 * w)
        py = int(y + (hsh(seed, k) - 0.5) * 2 * h * (1 - abs(px - x) / w * 0.5))
        c.dot(px, py, 'E1')
        c.dot(px + 1, py, 'G2' if k % 3 else 'E2')
        if k % 4 == 0:
            c.dot(px, py - 1, 'S1')


def oil_lamp(c, x, base, s=1.0):
    """願いの灯: 金の油差し形のランプ、注ぎ口の炎、立ちのぼる光の煙。"""
    k = s
    c.paint(ellipse(x, base - 10 * k, 30 * k, 12 * k), 'gold', spec=0.8, shine=5)
    c.paint(poly([(x + 20 * k, base - 14 * k), (x + 52 * k, base - 22 * k), (x + 52 * k, base - 18 * k), (x + 22 * k, base - 6 * k)], nrm(-0.2, -0.4, 0.9)), 'gold', spec=0.7)
    pts = arc_points(x - 32 * k, base - 10 * k, 9 * k, -math.pi / 2, math.pi / 2, 10)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2 * k), 'gold', gain=0.9)
    c.paint(ellipse(x, base - 22 * k, 10 * k, 5 * k), 'gold', gain=1.1, spec=0.6)
    c.paint(ellipse(x, base - 28 * k, 3 * k, 3 * k), 'gold', spec=0.7)
    flame(c, x + 54 * k, base - 28 * k, 3 * k, 6 * k)
    for t in range(14):
        tt = t / 13
        c.paint(ellipse(x + 54 * k - tt * 30 + math.sin(tt * 6) * 8, base - 36 * k - tt * 70, 4 + tt * 8, 3 + tt * 5), 'blue', emit=0.7 - tt * 0.35, outline=False, dither=True)


def cradle(c, x, base, w=80):
    """揺りかご: 弧の脚、木の籠、布、中で光る赤子。"""
    pts = arc_points(x, base - 40, w / 2 + 10, math.pi * 0.2, math.pi * 0.8, 14)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.2), 'wood', gain=0.9)
    c.paint(ellipse(x, base - 22, w / 2, 16, clip=lambda px, py: py >= base - 26), 'wood', gain=1.0, tex=lambda px, py: -0.1 if int(px) % 5 == 0 else 0)
    c.paint(ellipse(x, base - 26, w / 2 - 4, 6), 'paper', gain=1.0)
    c.paint(ellipse(x - 10, base - 30, 7, 6), 'skin', gain=1.1)
    c.brighten(x - 10, base - 30, 40, 26, 0.3)
    for k in range(6):
        c.dot(int(x - 30 + hsh(k, 1) * 60), int(base - 50 - hsh(1, k) * 30), 'G6')


def dogu(c, x, base, s=1.0):
    """土偶: 大きな遮光器の目、模様の刻まれた太い体と脚。"""
    k = s
    c.paint(capsule(x - 12 * k, base - 26 * k, x - 16 * k, base, 7 * k, 8 * k), 'copper', gain=0.9)
    c.paint(capsule(x + 12 * k, base - 26 * k, x + 16 * k, base, 7 * k, 8 * k), 'copper', gain=0.8)
    c.paint(ellipse(x, base - 46 * k, 22 * k, 24 * k), 'copper', gain=1.0, tex=lambda px, py: -0.1 if (int((px - x) / (3 * k)) + int((py - base) / (3 * k))) % 4 == 0 else 0)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 20 * k, base - 56 * k, x + sg * 32 * k, base - 46 * k, 6 * k, 5 * k), 'copper', gain=0.95)
    c.paint(ellipse(x, base - 84 * k, 18 * k, 16 * k), 'copper', gain=1.05)
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 8 * k, base - 84 * k, 7 * k, 4 * k), 'copper', gain=0.55)
        c.paint(rect(x + sg * 8 * k - 6 * k, base - 84.5 * k, x + sg * 8 * k + 6 * k, base - 83.5 * k), 'copper', gain=1.2, outline=False)
    c.paint(ellipse(x, base - 98 * k, 12 * k, 5 * k), 'copper', gain=1.1)


def sarcophagus(c, x, base, w=110, h=34):
    """石の棺: 蓋に横たわる像の浮き彫り、まわりの供え物。"""
    d = 16
    c.paint(poly([(x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2 + d, base - h - d * 0.6), (x - w / 2 + d, base - h - d * 0.6)], UP), 'stone', gain=1.1)
    c.paint(poly([(x + w / 2, base), (x + w / 2 + d, base - d * 0.6), (x + w / 2 + d, base - h - d * 0.6), (x + w / 2, base - h)], nrm(0.85, 0, 0.5)), 'stone', gain=0.7)
    o = c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.2, 0, 1)), 'stone', gain=0.95)
    for k in range(5):
        c.paint(rect(x - w / 2 + 8 + k * (w - 16) / 4 - 3, base - h + 6, x - w / 2 + 8 + k * (w - 16) / 4 + 3, base - 6), 'stone', oid=o, gain=0.6, outline=False)
    c.paint(capsule(x - w / 2 + d * 0.6 + 14, base - h - d * 0.35, x + w / 2 + d * 0.4 - 16, base - h - d * 0.35, 5), 'stone', gain=1.2)
    c.paint(ellipse(x - w / 2 + d * 0.6 + 10, base - h - d * 0.35, 6, 5), 'stone', gain=1.25)


def shimenawa_tree(c, x, base, h=130):
    """鎮守の森の神木: 太い幹に注連縄と紙垂。"""
    tree(c, x, base, h, kind='oak', gain=0.9, seed=99)
    c.paint(capsule(x - 18, base - 46, x + 20, base - 44, 3.4), 'sand', gain=1.1, tex=lambda px, py: -0.12 if int(px - py) % 4 == 0 else 0)
    for dx in (-10, 4, 16):
        for j in range(3):
            c.paint(rect(x + dx - 2 + (j % 2) * 3, base - 42 + j * 4, x + dx + 2 + (j % 2) * 3, base - 38 + j * 4), 'paper', gain=1.15, outline=False)


def holed_coin(c, x, y, r=34):
    """福銭: 四角い穴の大きな銭、赤い紐の房。"""
    c.paint(ellipse(x, y, r, r), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x, y, r * 0.85, r * 0.85), 'gold', gain=0.85)
    c.paint(rect(x - r * 0.2, y - r * 0.2, x + r * 0.2, y + r * 0.2), 'stone', emit=0.05, outline=False)
    for k, (dx, dy) in enumerate(((0, -0.55), (0.55, 0), (0, 0.55), (-0.55, 0))):
        c.paint(rect(x + dx * r - 3, y + dy * r - 3, x + dx * r + 3, y + dy * r + 3), 'gold', gain=1.15, outline=False)
    c.paint(capsule(x, y - r * 0.2, x - 4, y - r - 30, 1.2), 'red', gain=1.0)
    c.paint(poly([(x - 6, y + r), (x + 6, y + r), (x + 8, y + r + 20), (x - 8, y + r + 20)], lambda px, py: nrm(0.4 * math.sin(px), 0, 0.9)), 'red', gain=1.0)


def skeleton_rise(c, x, base):
    """土から這い出る骸骨（頭・肋・腕）。"""
    skull(c, x, base - 34, 1.1)
    for k in range(4):
        c.paint(capsule(x - 10, base - 20 + k * 4, x + 10, base - 20 + k * 4, 1.2), 'paper', gain=0.9)
    c.paint(capsule(x, base - 22, x, base, 1.6), 'paper', gain=0.9)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 10, base - 20, x + sg * 22, base - 40, 1.4), 'paper', gain=0.95)
        for j in range(3):
            c.paint(capsule(x + sg * 22, base - 40, x + sg * (22 + j * 2), base - 46, 0.6), 'paper', gain=1.0, outline=False)
    c.paint(ellipse(x, base + 2, 40, 6), 'leather', gain=0.6)


def shoe_last(c, x, base):
    """靴型にかけた靴、横に糸と錐。"""
    c.paint(capsule(x, base - 60, x, base - 24, 3), 'wood', gain=0.9)
    c.paint(capsule(x - 20, base - 70, x + 18, base - 66, 7, 5), 'leather', gain=1.1, spec=0.3)
    c.paint(ellipse(x - 18, base - 72, 8, 9), 'leather', gain=1.15)
    c.paint(rect(x - 26, base - 63, x + 22, base - 61), 'cloth', gain=0.7, outline=False)
    c.paint(ellipse(x, base - 22, 12, 4), 'wood', gain=0.9)


def shooting_star(c, x, y):
    for k in range(20):
        t = k / 19
        c.paint(ellipse(x + t * 90, y - t * 40, 3 - t * 2.4, 2 - t * 1.6), 'paper', emit=1.0 - t * 0.6, outline=False)
    c.paint(ellipse(x, y, 4, 4), 'gold', emit=1.0, outline=False)
    c.brighten(x, y, 30, 30, 0.25)


def rain_cloud(c, x, y, w=70):
    for k in range(5):
        c.paint(ellipse(x - w / 2 + k * w / 4, y - (6 if k in (1, 3) else 0), w / 5, w / 7), 'stone', gain=0.75)
    for k in range(18):
        rx = x - w / 2 + hsh(k, 4) * w
        ry = y + 8 + hsh(4, k) * 40
        c.paint(capsule(rx, ry, rx - 2, ry + 5, 0.4), 'water', emit=0.5, outline=False)


def spiral_dizzy(c, x, y, r=16, ramp='purple'):
    pts = [(x + math.cos(t) * t * r / 12, y + math.sin(t) * t * r / 24) for t in [i * 0.3 for i in range(40)]]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.8), ramp, emit=0.85, outline=False)


def grasping_hands(c, pts):
    """闇から伸びる影の手。"""
    for x, y, ang in pts:
        a = math.radians(ang)
        ex, ey = x + math.cos(a) * 60, y + math.sin(a) * 60
        c.paint(capsule(x, y, ex, ey, 6, 3), 'purple', emit=0.12, outline=False)
        for j in range(4):
            fa = a + (j - 1.5) * 0.3
            c.paint(capsule(ex, ey, ex + math.cos(fa) * 12, ey + math.sin(fa) * 12, 1.6, 0.8), 'purple', emit=0.14, outline=False)


def gohei():
    """お祓いの幣（棒の先に紙垂）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x + fig.f * 0.6 * u, y - 2.6 * u
        c.paint(capsule(x, y + 0.6 * u, tx, ty, 0.12 * u), 'wood')
        for j in range(4):
            sx = tx + (j - 1.5) * 0.35 * u
            c.paint(poly([(sx - 0.2 * u, ty), (sx + 0.2 * u, ty), (sx + 0.3 * u, ty + 1.4 * u), (sx - 0.1 * u, ty + 1.1 * u)]), 'paper', gain=1.2)
    return draw


def bone_staff():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, fig.foot - 0.2 * u, x, y - 2.0 * u, 0.15 * u), 'paper', gain=0.8)
        skull(c, x, y - 2.6 * u, u / 18)
    return draw


def cape_collar():
    """吸血鬼の立て襟の外套（体より奥に描く）。"""
    def draw(c, fig, hand):
        u = fig.u
        for sg in (-1, 1):
            c.paint(poly([(fig.X(sg * 0.6, fig.y_neck), fig.y_neck), (fig.X(sg * 1.3, fig.y_head), fig.y_head - 0.4 * u), (fig.X(sg * 1.2, fig.y_sh), fig.y_sh)],
                         nrm(sg * 0.4, -0.2, 0.9)), 'red', gain=0.9)
    return draw


def sack_back():
    def draw(c, fig, hand):
        u = fig.u
        c.paint(ellipse(fig.X(-1.2, fig.y_sh), fig.y_sh + 0.6 * u, 1.6 * u, 1.4 * u), 'paper', gain=0.8)
    return draw


PROPS = {'gohei': gohei, 'bone_staff': bone_staff, 'cape_collar': cape_collar, 'sack_back': sack_back}


def peaks(c):
    """雪をいただく峰（奥ほど寒く暗い）。"""
    for k, (x, h, w, g) in enumerate(((60, 90, 90, 0.6), (150, 110, 100, 0.75), (100, 70, 120, 0.9))):
        base = 150
        pts = [(x - w, base), (x - w * 0.2, base - h + 10), (x, base - h), (x + w * 0.3, base - h + 14), (x + w, base)]
        c.paint(poly(pts, lambda px, py, x=x: nrm(-0.6 if px < x else 0.5, -0.3, 0.7)), 'stone', gain=g)
        cap = [(x - w * 0.3, base - h + 22), (x - w * 0.2, base - h + 10), (x, base - h), (x + w * 0.3, base - h + 14), (x + w * 0.36, base - h + 26), (x + 4, base - h + 18)]
        c.paint(poly(cap, lambda px, py, x=x: nrm(-0.6 if px < x else 0.5, -0.3, 0.7)), 'silver', gain=g * 1.2)


def river(c, y0):
    """谷をうねって手前へ広がる川。"""
    lt = c.light
    pix = []
    for y in range(int(y0), H):
        t = (y - y0) / (H - y0)
        cx = 112 + 50 * math.sin(t * 3.2)
        w = 6 + 70 * t
        for x in range(int(cx - w / 2), int(cx + w / 2)):
            pix.append((x, y, FLAT))
    c.paint(pix, 'water', emit=lambda x, y, n: 0.3 + 0.35 * lt.att(x, y) + (0.12 if math.sin(y * 1.4 + x * 0.2) > 0.7 else 0), dither=True, outline=False)


def wind_streaks(c):
    for k in range(7):
        y = 30 + k * 13
        x0 = hsh(k, 2) * 120
        pts = [(x0 + t * 100, y + math.sin(t * 6 + k) * 4) for t in [i / 10 for i in range(11)]]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'paper', emit=0.55, outline=False)


def leaves(c, n=20):
    for k in range(n):
        x = int(hsh(k, 9) * W)
        y = int(20 + hsh(9, k) * 110)
        c.paint(ellipse(x, y, 2.6, 1.4), ('green', 'gold', 'red')[k % 3], gain=1.0, outline=False)


def green_eyes(c, x, y):
    for ex in (-20, 20):
        c.paint(ellipse(x + ex, y, 10, 5), 'green', emit=1.0, outline=False)
        c.paint(ellipse(x + ex, y, 2, 4.5), 'stone', emit=0.05, outline=False)


def empty_purse(c, x, base):
    c.paint(ellipse(x, base - 14, 30, 16), 'red', gain=0.75, tex=lambda px, py: -0.1 if (int(px) + int(py)) % 5 == 0 else 0)
    c.paint(ellipse(x + 10, base - 26, 18, 6), 'red', gain=0.9)
    c.paint(ellipse(x + 10, base - 26, 14, 4), 'stone', emit=0.04, outline=False)
    c.paint(capsule(x - 20, base - 24, x - 40, base - 40, 0.8), 'gold', gain=0.8, outline=False)
    c.paint(poly([(x - 8, base - 6), (x + 2, base - 4), (x - 2, base + 2)]), 'stone', emit=0.04, outline=False)


def crossed_swords(c, x, y, ln=70):
    for sg in (-1, 1):
        x0, y0 = x - sg * ln / 2, y + 26
        x1, y1 = x + sg * ln / 2, y - 26
        c.paint(capsule(x0, y0, x1, y1, 2.4, 1.0), 'silver', spec=0.8, shine=5)
        gx, gy = x0 + (x1 - x0) * 0.2, y0 + (y1 - y0) * 0.2
        c.paint(capsule(gx - 6, gy - 6 * sg, gx + 6, gy + 6 * sg, 1.6), 'gold', spec=0.5)


def big_ghost(c, x, y, s=1.0):
    from parts_empires import ghosts
    k = s
    pts2 = [(x - 8 * k, y), (x - 9 * k, y - 12 * k)] + arc_points(x, y - 12 * k, 9 * k, math.pi, 2 * math.pi, 14) + [(x + 9 * k, y - 12 * k), (x + 8 * k, y), (x + 4 * k, y + 10 * k), (x, y + 4 * k), (x - 4 * k, y + 12 * k)]
    pix = [(px, py, n) for px, py, n in poly(pts2) if (px + py) % 2 == 0 or py < y - 6 * k]
    c.paint(pix, 'paper', emit=0.62, outline=False)
    for ex in (-3, 3):
        c.paint(ellipse(x + ex * k, y - 14 * k, 1.6 * k, 2.2 * k), 'stone', emit=0.04, outline=False)
    c.paint(ellipse(x, y - 8 * k, 2 * k, 2.6 * k), 'stone', emit=0.04, outline=False)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 8 * k, y - 6 * k, x + sg * 16 * k, y - 14 * k, 2 * k, 1 * k), 'paper', emit=0.55, outline=False)


def hands_cup(c, x, y):
    """椀の形に合わせた両手（袖から差し出す）。"""
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 50, y + 46, x + sg * 16, y + 18, 9, 7), 'blue', gain=0.85)
        c.paint(ellipse(x + sg * 11, y + 14, 12, 8), 'skin', gain=1.1)
        for j in range(3):
            c.paint(capsule(x + sg * (4 + j * 4), y + 8, x + sg * (2 + j * 4), y + 2, 1.6), 'skin', gain=1.15)
