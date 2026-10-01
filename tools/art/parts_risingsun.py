"""昇る日（risingsun）で足した部品: 狐・狸・蛇、かご、茶店の傘と床几、桜、金継ぎの椀、三方・重箱、千本鳥居。
動物は facing=1 で頭が右。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, flame, paper_lantern, window, gem, tree, coin


def fox(c, x, base, s=1.0, facing=1, ramp='copper', sit=True):
    """化け狐（座った横向き）: 細い脚、白い胸、尖った耳と鼻づら、大きくふくらむ尾、細い金の目。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    for i in range(10):  # 尾（体の後ろから上へ巻き、先が白い）
        t = i / 9
        px = X(-12 - 22 * math.sin(t * 1.9))
        py = base - 4 * k - t * 26 * k
        r = (3.5 + 4 * math.sin(t * math.pi * 0.9)) * k
        c.paint(ellipse(px, py, r, r, normal=nrm(-0.35, -0.45, 0.8)), 'paper' if t > 0.82 else ramp, gain=1.0)
    c.paint(ellipse(X(-4), base - 12 * k, 13 * k, 12 * k), ramp, gain=1.0)
    c.paint(capsule(X(4), base - 14 * k, X(8), base - 34 * k, 7 * k, 5.4 * k), ramp, gain=1.05)
    c.paint(ellipse(X(9), base - 22 * k, 4.4 * k, 9 * k), 'paper', gain=1.05, outline=False)
    for dx, g in ((2, 0.85), (8, 1.05)):
        c.paint(capsule(X(dx), base - 16 * k, X(dx + 1), base - 1, 2 * k, 1.6 * k), ramp, gain=g)
        c.paint(ellipse(X(dx + 1.5), base - 1 * k, 2.4 * k, 1.4 * k), 'cloth', gain=0.6)
    c.paint(ellipse(X(10), base - 40 * k, 7 * k, 6.5 * k), ramp, gain=1.1)
    c.paint(poly([(X(13), base - 43 * k), (X(25), base - 37 * k), (X(14), base - 35 * k)], nrm(0.1, -0.3, 0.9)), ramp, gain=1.15)
    c.paint(poly([(X(14), base - 36 * k), (X(24), base - 37 * k), (X(14), base - 34 * k)]), 'paper', gain=1.0)
    c.dot(int(X(25)), int(base - 37 * k), 'N0')
    for dx, g in ((5, 0.9), (11, 1.1)):
        c.paint(poly([(X(dx - 3), base - 44 * k), (X(dx + 3), base - 45 * k), (X(dx), base - 54 * k)], nrm(-0.3, -0.4, 0.8)), ramp, gain=g)
        c.paint(poly([(X(dx - 1.4), base - 45 * k), (X(dx + 1.4), base - 45.5 * k), (X(dx), base - 51 * k)]), 'cloth', gain=0.5, outline=False)
    c.paint(capsule(X(12), base - 41 * k, X(16), base - 42 * k, 0.8 * k), 'gold', emit=1.0, outline=False)


def tanuki(c, x, base, s=1.0):
    """化け狸（置物の姿）: 笠をかぶり、丸い腹、徳利と通い帳を下げ、目のまわりが黒い。"""
    k = s
    c.paint(ellipse(x, base - 4 * k, 34 * k, 6 * k), 'stone', emit=0.06, outline=False)
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 14 * k, base - 6 * k, 9 * k, 6 * k), 'leather', gain=0.9)
    c.paint(capsule(x + 24 * k, base - 10 * k, x + 36 * k, base - 4 * k, 6 * k, 4 * k), 'leather', gain=0.8)
    c.paint(ellipse(x, base - 30 * k, 28 * k, 26 * k), 'leather', gain=1.0, tex=lambda px, py: -0.06 if (int(px) * 2 + int(py) * 3) % 7 == 0 else 0)
    c.paint(ellipse(x + 2 * k, base - 24 * k, 18 * k, 18 * k), 'sand', gain=1.1, spec=0.25)
    c.paint(ellipse(x, base - 66 * k, 17 * k, 15 * k), 'leather', gain=1.05)
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 7 * k, base - 66 * k, 6 * k, 4.6 * k), 'cloth', gain=0.45)
        c.paint(ellipse(x + sg * 7 * k, base - 66 * k, 2 * k, 2 * k), 'paper', emit=0.9, outline=False)
        c.dot(int(x + sg * 7 * k), int(base - 66 * k), 'N0')
    c.paint(ellipse(x, base - 59 * k, 6 * k, 4 * k), 'sand', gain=1.15)
    c.dot(int(x), int(base - 61 * k), 'N0')
    c.paint(poly([(x - 34 * k, base - 76 * k), (x + 34 * k, base - 76 * k), (x, base - 96 * k)], lambda px, py: nrm((px - x) / (34 * k) * 0.3, -0.7, 0.6)), 'sand', gain=1.0,
            tex=lambda px, py: -0.1 if int(px - x) % 5 == 0 else 0)
    c.paint(capsule(x - 26 * k, base - 44 * k, x - 32 * k, base - 22 * k, 4 * k), 'leather', gain=1.0)
    c.paint(ellipse(x - 34 * k, base - 18 * k, 7 * k, 9 * k), 'paper', gain=1.0, spec=0.4)
    c.paint(capsule(x - 34 * k, base - 30 * k, x - 34 * k, base - 27 * k, 2.6 * k), 'paper', gain=1.0)
    c.paint(rect(x - 38 * k, base - 20 * k, x - 30 * k, base - 16 * k), 'red', gain=1.0, outline=False)
    c.paint(capsule(x + 26 * k, base - 44 * k, x + 30 * k, base - 26 * k, 4 * k), 'leather', gain=0.9)
    c.paint(rect(x + 24 * k, base - 28 * k, x + 38 * k, base - 12 * k, nrm(0.2, 0, 1)), 'paper', gain=0.9)


def snake(c, x, base, s=1.0, ramp='green'):
    """蛇: 籠から S の字に鎌首をもたげ、広げた頸と、ちろりと出す舌。"""
    k = s
    pts = [(x - math.sin(t * 4.2) * 12 * k * (1 - t * 0.3), base - t * 70 * k) for t in [i / 18 for i in range(19)]]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        r = (5 - i * 0.12) * k
        c.paint(capsule(a[0], a[1], b[0], b[1], r, r), ramp, gain=1.05 + 0.01 * i, spec=0.4, shine=6,
                tex=lambda px, py: -0.14 if (int(px) + int(py)) % 4 == 0 else 0)
    hx, hy = pts[-1]
    c.paint(ellipse(hx, hy + 6 * k, 10 * k, 9 * k), ramp, gain=0.95)
    c.paint(ellipse(hx, hy + 6 * k, 5 * k, 6 * k), 'sand', gain=1.0, outline=False)
    c.paint(ellipse(hx + 2 * k, hy - 2 * k, 6 * k, 4.4 * k), ramp, gain=1.15)
    c.dot(int(hx + 4 * k), int(hy - 3 * k), 'G5')
    c.paint(capsule(hx + 8 * k, hy - 1 * k, hx + 13 * k, hy, 0.4 * k), 'red', gain=1.2, outline=False)


def snake_basket(c, x, base, r=24):
    """蛇遣いの籠（編み目の壺形、蓋を脇に）。"""
    c.paint(ellipse(x, base - r * 0.8, r, r * 0.9, clip=lambda px, py: py > base - r * 1.4), 'sand', gain=1.0,
            tex=lambda px, py: -0.15 if (int(px) // 3 + int(py) // 3) % 2 == 0 else 0)
    c.paint(ellipse(x, base - r * 1.4, r * 0.75, r * 0.2), 'sand', gain=1.15)
    c.paint(ellipse(x, base - r * 1.4, r * 0.55, r * 0.12), 'stone', emit=0.04, outline=False)
    c.paint(ellipse(x + r * 1.6, base - 3, r * 0.7, r * 0.22), 'sand', gain=0.9)


def kago(c, x, base, w=70, h=50):
    """かご（駕籠）: 屋根の付いた箱の乗り物、簾の窓、上を通る長い担ぎ棒。"""
    top = base - h
    c.paint(capsule(x - w - 30, top - 8, x + w + 30, top - 8, 3), 'wood', gain=1.05)
    c.paint(rect(x - w / 2, top, x + w / 2, base, nrm(-0.2, 0, 1)), 'cloth', gain=0.8, spec=0.5)
    c.paint(rect(x - w / 2 + 8, top + 8, x + w / 2 - 8, base - 12, nrm(-0.1, 0, 1)), 'sand', gain=1.0,
            tex=lambda px, py: -0.18 if int(py) % 3 == 0 else 0)
    c.paint(rect(x - w / 2, base - 8, x + w / 2, base - 4), 'gold', gain=1.0, outline=False)
    c.paint(poly([(x - w / 2 - 8, top + 2), (x + w / 2 + 8, top + 2), (x + w / 2 - 6, top - 12), (x - w / 2 + 6, top - 12)], nrm(-0.1, -0.6, 0.8)), 'cloth', gain=1.0)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * w * 0.3, top - 8, x + sg * w * 0.3, top, 1.4), 'gold', gain=1.0)


def parasol(c, x, base, h=110, r=56, ramp='red'):
    """野点の傘: 太い竹の柄と、骨の見える朱の大きな傘。"""
    c.paint(capsule(x, base, x, base - h + 6, 2.2), 'sand', gain=1.0)
    top = base - h
    pts = [(x - r, top + 26), (x - r * 0.5, top + 8), (x, top), (x + r * 0.5, top + 8), (x + r, top + 26)]
    pix = poly(pts + [(x + r, top + 28), (x - r, top + 28)], lambda px, py: nrm((px - x) / r * 0.5, -0.6, 0.7))
    o = c.paint(pix, ramp, gain=1.0)
    for j in range(9):
        t = j / 8
        ex = x - r + t * 2 * r
        c.paint(capsule(x, top + 1, ex, top + 26 - 18 * (1 - abs(t - 0.5) * 2) * 0, 0.6), ramp, oid=o, gain=0.75, outline=False)
    c.paint(ellipse(x, top, 3, 2), 'gold', gain=1.0)


def red_bench(c, x, base, w=100):
    """茶店の床几: 赤い毛氈を敷いた縁台と、湯呑と団子の皿。"""
    for dx in (-w / 2 + 8, w / 2 - 8):
        c.paint(rect(x + dx - 2, base - 18, x + dx + 2, base, nrm(-0.2, 0, 1)), 'wood', gain=0.85)
    c.paint(rect(x - w / 2, base - 24, x + w / 2, base - 18, nrm(0, -0.4, 0.9)), 'red', gain=1.05)
    c.paint(rect(x - w / 2, base - 18, x + w / 2, base - 14, nrm(0, 0.3, 1)), 'red', gain=0.7)
    c.paint(vcyl(x + 20, base - 32, base - 24, 4, 1.4), 'paper', gain=1.05)
    c.paint(ellipse(x - 14, base - 25, 12, 3), 'paper', gain=1.0)
    for j, col in enumerate(('red', 'paper', 'green')):
        c.paint(ellipse(x - 20 + j * 6, base - 29, 2.8, 2.6), col, gain=1.15)
    c.paint(capsule(x - 26, base - 29, x - 4, base - 29, 0.5), 'wood', gain=1.0, outline=False)


def sakura(c, x, base, h=110, seed=0):
    """桜: 黒い幹と枝、薄紅の花の房（紫水晶の明るい段）、散る花びら。"""
    trunk = [(x, base), (x - 6, base - h * 0.35), (x + 4, base - h * 0.55)]
    for a, b in zip(trunk, trunk[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 7, 5), 'wood', gain=0.7)
    for ang, ln in ((-150, 50), (-110, 46), (-70, 50), (-30, 46), (-90, 30)):
        a = math.radians(ang)
        c.paint(capsule(x + 4, base - h * 0.55, x + 4 + math.cos(a) * ln, base - h * 0.55 + math.sin(a) * ln, 3, 1.4), 'wood', gain=0.75)
    for j in range(22):
        px = x + (hsh(j, seed) - 0.5) * h * 1.1
        py = base - h * 0.55 - hsh(seed, j) * h * 0.5 + abs(px - x) * 0.25
        c.paint(ellipse(px, py, 11 + hsh(j, 2) * 6, 8 + hsh(2, j) * 4), 'purple', gain=1.35 + 0.1 * hsh(j, 3),
                tex=lambda qx, qy: 0.1 if (int(qx) * 3 + int(qy) * 2) % 5 == 0 else 0)
    for j in range(14):
        c.dot(int(x - 60 + hsh(j, 9) * 140), int(base - hsh(9, j) * 60), 'P3')


def kintsugi_bowl(c, x, base, r=40):
    """金継ぎの椀: 黒い釉の椀の割れ目を、金の線でつないだもの。"""
    c.paint(ellipse(x, base - 2, r * 0.45, 4), 'cloth', gain=0.6)
    o = c.paint(ellipse(x, base - r * 0.55, r, r * 0.62, clip=lambda px, py: py > base - r * 0.95), 'cloth', gain=0.85, spec=0.7, shine=6)
    c.paint(ellipse(x, base - r * 0.95, r, r * 0.22), 'cloth', gain=1.1, spec=0.5)
    c.paint(ellipse(x, base - r * 0.95, r * 0.9, r * 0.17), 'leather', gain=0.6, outline=False)
    cracks = [[(x - r * 0.7, base - r * 0.9), (x - r * 0.45, base - r * 0.6), (x - r * 0.5, base - r * 0.4), (x - r * 0.2, base - r * 0.15)],
              [(x + r * 0.3, base - r * 0.95), (x + r * 0.35, base - r * 0.7), (x + r * 0.6, base - r * 0.5), (x + r * 0.5, base - r * 0.3)],
              [(x - r * 0.45, base - r * 0.6), (x - r * 0.1, base - r * 0.55), (x + r * 0.35, base - r * 0.7)]]
    for line in cracks:
        for a, b in zip(line, line[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.2), 'gold', oid=o, emit=0.95, outline=False)


def sanbo(c, x, base, w=60):
    """三方の供え物: 白木の台に、盛った米と餅と橙、徳利一対。"""
    c.paint(rect(x - w / 2 + 6, base - 22, x + w / 2 - 6, base, nrm(-0.2, 0, 1)), 'sand', gain=1.15)
    c.paint(ellipse(x, base - 12, 8, 7), 'stone', emit=0.08, outline=False)
    c.paint(rect(x - w / 2, base - 30, x + w / 2, base - 22, nrm(0, -0.4, 0.9)), 'sand', gain=1.25)
    for j, (r, ramp) in enumerate(((16, 'paper'), (13, 'paper'))):
        c.paint(ellipse(x, base - 34 - j * 9, r, 7), ramp, gain=1.15 - j * 0.03)
    c.paint(ellipse(x, base - 54, 7, 6), 'copper', gain=1.25)
    c.paint(capsule(x - 3, base - 60, x + 4, base - 62, 1.5), 'green', gain=1.1)
    for sg in (-1, 1):
        bx = x + sg * (w / 2 + 16)
        c.paint(ellipse(bx, base - 12, 8, 12), 'paper', gain=1.0, spec=0.5)
        c.paint(capsule(bx, base - 22, bx, base - 30, 3), 'paper', gain=1.05)


def jubako(c, x, base, w=70, h=22, n=3):
    """重箱: 黒漆と朱の段を重ね、金の蒔絵の線、上の蓋。"""
    for j in range(n):
        y1 = base - j * h
        c.paint(rect(x - w / 2, y1 - h, x + w / 2, y1, nrm(-0.25, 0, 1)), 'cloth' if j % 2 == 0 else 'red', gain=0.8 if j % 2 == 0 else 1.0, spec=0.6, shine=6)
        c.paint(rect(x - w / 2, y1 - 3, x + w / 2, y1 - 1), 'gold', gain=1.0, outline=False)
        c.paint(capsule(x - w * 0.3, y1 - h * 0.5, x + w * 0.1, y1 - h * 0.6, 0.6), 'gold', emit=0.8, outline=False)
    d = 14
    t = base - n * h
    c.paint(poly([(x - w / 2, t), (x + w / 2, t), (x + w / 2 + d, t - d * 0.6), (x - w / 2 + d, t - d * 0.6)], UP), 'cloth', gain=1.1, spec=0.6)
    c.paint(poly([(x + w / 2, base), (x + w / 2 + d, base - d * 0.6), (x + w / 2 + d, t - d * 0.6), (x + w / 2, t)], nrm(0.85, 0, 0.5)), 'cloth', gain=0.55)


def torii_tunnel(c, x, base, n=8):
    """千本鳥居: 奥へ小さくなりながら続く朱の鳥居の列。"""
    from parts_empires import torii
    for j in range(n - 1, -1, -1):
        t = j / (n - 1)
        s = 1 - t * 0.8
        torii(c, x + t * 10, base - t * 40, w=200 * s, h=150 * s, ramp='red')


def tenbin():
    """天秤棒: 肩の棒の両端に、魚を盛った平たい籠を吊る。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        sy = fig.y_sh - 0.1 * u
        cx = fig.x
        c.paint(capsule(cx - 3.4 * u, sy, cx + 3.4 * u, sy - 0.2 * u, 0.13 * u), 'sand', gain=1.1)
        for sg in (-1, 1):
            bx = cx + sg * 3.1 * u
            for dx in (-0.6, 0.6):
                c.paint(capsule(bx, sy, bx + dx * u, sy + 2.4 * u, 0.04 * u), 'sand', gain=0.9, outline=False)
            c.paint(ellipse(bx, sy + 2.6 * u, 1.0 * u, 0.35 * u), 'sand', gain=1.0)
            for j in range(3):
                c.paint(ellipse(bx + (j - 1) * 0.45 * u, sy + 2.3 * u - (j % 2) * 0.15 * u, 0.45 * u, 0.16 * u), 'silver', gain=1.15, spec=0.7)
    return draw


def flute():
    """縦笛（蛇遣いの笛）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y, x + fig.f * 1.2 * u, y + 0.8 * u, 0.12 * u, 0.2 * u), 'wood', gain=1.1)
        c.paint(ellipse(x + fig.f * 1.25 * u, y + 0.85 * u, 0.3 * u, 0.22 * u), 'gold', spec=0.6)
    return draw


def shaku():
    """笏（細長い板）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y + 0.3 * u, x + fig.f * 0.15 * u, y - 1.3 * u, 0.12 * u), 'sand', gain=1.15)
    return draw


def brush_pen():
    """筆。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y, x + fig.f * 0.6 * u, y - 1.0 * u, 0.07 * u), 'wood', gain=1.0)
        c.paint(capsule(x, y, x - fig.f * 0.15 * u, y + 0.3 * u, 0.1 * u, 0.03 * u), 'cloth', gain=0.4)
    return draw


PROPS = {'tenbin': tenbin, 'flute': flute, 'shaku': shaku, 'brush_pen': brush_pen}
