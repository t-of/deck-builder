"""動物園（menagerie）で足した部品: 「ならい」の動物たち、駒と馬の道具、そり・窯・くず鉄。
動物はどれも facing=1 で頭が右（X(dx) の dx>0 が頭の側）。光は左上なので、主役の動物は左向き（facing=-1）にすることが多い。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, coin, flame, horse, wheel, chain, fence, window


def _fur(step=3, amt=0.07):
    return lambda px, py: -amt if (int(px) * 2 + int(py) * 3) % (step * 2 + 1) == 0 else 0


def monkey2(c, x, y, s=1.0):
    """手長猿（作り直し）: 胸と腰の 2 つのふくらみ、肘で曲がる 2 節の長い腕で綱をつかみ、片手を伸ばす。
    膝を曲げた 2 節の脚、毛の面の中に肌色の顔。(x, y) は頭の中心。"""
    k = s
    hx, hy = x, y
    fur = _fur()
    # 奥の脚（暗い）
    c.paint(capsule(hx + 5 * k, hy + 27 * k, hx + 14 * k, hy + 33 * k, 3.2 * k, 2.6 * k), 'leather', gain=0.75, tex=fur)
    c.paint(capsule(hx + 14 * k, hy + 33 * k, hx + 11 * k, hy + 43 * k, 2.4 * k, 1.8 * k), 'leather', gain=0.75)
    c.paint(ellipse(hx + 13 * k, hy + 44 * k, 3 * k, 1.8 * k), 'skin', gain=0.8)
    # 伸ばす腕（奥）
    c.paint(capsule(hx + 6 * k, hy + 8 * k, hx + 17 * k, hy + 12 * k, 3.0 * k, 2.6 * k), 'leather', gain=0.85, tex=fur)
    c.paint(capsule(hx + 17 * k, hy + 12 * k, hx + 30 * k, hy + 5 * k, 2.5 * k, 2.0 * k), 'leather', gain=0.85, tex=fur)
    c.paint(ellipse(hx + 32 * k, hy + 4 * k, 3 * k, 2.6 * k), 'skin', gain=1.05)
    # 胴: 胸と腰
    o = c.obj()
    c.paint(ellipse(hx + 1 * k, hy + 13 * k, 8.5 * k, 9 * k), 'leather', oid=o, gain=1.0, tex=fur)
    c.paint(ellipse(hx + 2 * k, hy + 23 * k, 7.5 * k, 7.5 * k), 'leather', oid=o, gain=0.95, tex=fur)
    c.paint(ellipse(hx + 2.5 * k, hy + 17 * k, 4 * k, 7 * k), 'sand', oid=o, gain=0.85, outline=False)
    # 手前の脚
    c.paint(capsule(hx - 2 * k, hy + 27 * k, hx - 11 * k, hy + 31 * k, 3.4 * k, 2.8 * k), 'leather', gain=1.0, tex=fur)
    c.paint(capsule(hx - 11 * k, hy + 31 * k, hx - 8 * k, hy + 42 * k, 2.6 * k, 2.0 * k), 'leather', gain=1.0)
    c.paint(ellipse(hx - 9 * k, hy + 43 * k, 3.2 * k, 2 * k), 'skin', gain=1.0)
    # 尾のない手長猿。綱をつかむ腕（手前、頭の上へ）
    c.paint(capsule(hx - 6 * k, hy + 7 * k, hx - 10 * k, hy - 12 * k, 3.0 * k, 2.6 * k), 'leather', gain=1.1, tex=fur)
    c.paint(capsule(hx - 10 * k, hy - 12 * k, hx - 5 * k, hy - 30 * k, 2.5 * k, 2.0 * k), 'leather', gain=1.15, tex=fur)
    c.paint(ellipse(hx - 5 * k, hy - 31 * k, 3 * k, 3 * k), 'skin', gain=1.15)
    # 頭: 毛の面、肌色の顔、眉の張り、目と鼻の穴、耳
    for sg in (-1, 1):
        c.paint(ellipse(hx + sg * 7 * k, hy + 1 * k, 1.8 * k, 2.2 * k), 'skin', gain=0.85)
    c.paint(ellipse(hx, hy, 7.5 * k, 7.5 * k), 'leather', gain=1.1, tex=fur)
    c.paint(ellipse(hx + 1.2 * k, hy + 1.4 * k, 5.4 * k, 5.2 * k), 'hair', gain=0.9, outline=False)
    c.paint(ellipse(hx + 1.2 * k, hy + 1.6 * k, 4 * k, 4.4 * k), 'skin', gain=0.9, outline=False)
    c.paint(ellipse(hx + 1.2 * k, hy + 3.4 * k, 2.6 * k, 2 * k), 'skin', gain=1.05, outline=False)
    c.paint(rect(hx - 2.6 * k, hy - 1.2 * k, hx + 5 * k, hy - 0.2 * k), 'hair', gain=0.8, outline=False)
    for ex in (-1, 3.2):
        c.dot(int(hx + ex * k), int(hy + 0.4 * k), 'N0')
        c.dot(int(hx + ex * k), int(hy - 0.2 * k), 'G3')
    c.dot(int(hx + 1.2 * k), int(hy + 2.6 * k), 'G0')
    c.paint(capsule(hx - 0.6 * k, hy + 4.4 * k, hx + 3 * k, hy + 4.4 * k, 0.4 * k), 'hair', gain=0.6, outline=False)


def owl(c, x, base, s=1.0):
    """梟（正面）: 卵形の胴に羽の模様、顔の円盤、大きな金の目、耳の房、たたんだ翼、枝をつかむ爪。"""
    k = s
    fur = lambda px, py: -0.09 if (int(px) + (int(py) // 3) * 2) % 5 == 0 and int(py) % 3 == 0 else 0
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 15 * k, base - 26 * k, 9 * k, 22 * k), 'wood', gain=0.8 if sg > 0 else 0.95,
                tex=lambda px, py: -0.1 if int(py) % 4 == 0 else 0)
    c.paint(ellipse(x, base - 28 * k, 19 * k, 26 * k), 'leather', gain=1.05, tex=fur)
    c.paint(ellipse(x, base - 20 * k, 12 * k, 15 * k), 'sand', gain=1.0, tex=fur)
    c.paint(ellipse(x, base - 54 * k, 18 * k, 15 * k), 'leather', gain=1.05, tex=fur)
    for sg in (-1, 1):
        c.paint(poly([(x + sg * 8 * k, base - 64 * k), (x + sg * 16 * k, base - 64 * k), (x + sg * 18 * k, base - 76 * k)], nrm(sg * 0.2, -0.4, 0.8)), 'leather', gain=1.0)
        ex = x + sg * 7.5 * k
        c.paint(ellipse(ex, base - 54 * k, 8 * k, 8 * k), 'sand', gain=1.15)
        c.paint(ellipse(ex, base - 54 * k, 4.6 * k, 4.6 * k), 'gold', emit=0.95, outline=False)
        c.paint(ellipse(ex, base - 54 * k, 2.2 * k, 2.4 * k), 'stone', emit=0.02, outline=False)
        c.dot(int(ex - 1.5 * k), int(base - 56 * k), 'G6')
    c.paint(poly([(x - 2.4 * k, base - 50 * k), (x + 2.4 * k, base - 50 * k), (x, base - 43 * k)], nrm(-0.3, -0.2, 0.9)), 'gold', gain=0.85)
    for sg in (-1, 1):
        for j in range(3):
            c.paint(capsule(x + sg * (4 + j * 3) * k, base - 3 * k, x + sg * (3 + j * 3.5) * k, base + 2 * k, 1 * k), 'gold', gain=0.9, outline=False)


def frog(c, x, base, s=1.0):
    """蛙（正面寄り）: 平たい体、頭の上の 2 つの目玉、白い喉、折りたたんだ後脚と前脚。"""
    k = s
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 18 * k, base - 7 * k, 12 * k, 8 * k), 'green', gain=0.85 if sg > 0 else 1.0)
        c.paint(capsule(x + sg * 26 * k, base - 2 * k, x + sg * 36 * k, base, 2.4 * k, 2.8 * k), 'green', gain=0.9)
    c.paint(ellipse(x, base - 12 * k, 20 * k, 13 * k), 'green', gain=1.05, spec=0.3,
            tex=lambda px, py: -0.12 if hsh(int(px) // 3, int(py) // 3, 5) < 0.12 else 0)
    c.paint(ellipse(x, base - 6 * k, 11 * k, 6 * k), 'sand', gain=1.0)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 9 * k, base - 8 * k, x + sg * 11 * k, base, 2.4 * k, 2 * k), 'green', gain=1.0)
        c.paint(ellipse(x + sg * 12 * k, base, 3.6 * k, 1.6 * k), 'green', gain=1.1)
        ex = x + sg * 10 * k
        c.paint(ellipse(ex, base - 24 * k, 6 * k, 6 * k), 'green', gain=1.1)
        c.paint(ellipse(ex, base - 25 * k, 3.8 * k, 3.6 * k), 'gold', emit=0.9, outline=False)
        c.paint(rect(ex - 3 * k, base - 25.5 * k, ex + 3 * k, base - 24.5 * k), 'stone', emit=0.02, outline=False)
        c.dot(int(ex - 1.5 * k), int(base - 27 * k), 'G6')
    c.paint(capsule(x - 10 * k, base - 15 * k, x + 10 * k, base - 15 * k, 0.6 * k), 'green', gain=0.4, outline=False)


def lily_pad(c, x, y, r=30, flower=True):
    """睡蓮の葉（切れ込みのある円）と、桃色の花。"""
    c.paint(ellipse(x, y, r, r * 0.32, normal=UP, clip=lambda px, py: not (px > x and abs(py - y) < (px - x) * 0.25)), 'green', gain=0.95,
            tex=lambda px, py: -0.08 if int(math.atan2(py - y, (px - x) * 0.32) * 5) % 2 == 0 else 0)
    if flower:
        fx, fy = x - r * 0.6, y - 2
        for j in range(7):
            a = math.pi + j * math.pi / 6
            c.paint(ellipse(fx + math.cos(a) * 5, fy + math.sin(a) * 4 - 3, 3.4, 5), 'purple', gain=1.3)
        c.paint(ellipse(fx, fy - 4, 2.4, 2), 'gold', gain=1.2)


def mole(c, x, base, s=1.0):
    """土竜: 盛り土から顔を出す。黒い毛の体、桃色の尖った鼻、大きな鋤の手。"""
    k = s
    c.paint(ellipse(x, base - 6 * k, 44 * k, 16 * k, clip=lambda px, py: py < base), 'leather', gain=0.85,
            tex=lambda px, py: -0.12 if hsh(int(px) // 2, int(py) // 2, 9) < 0.18 else 0)
    c.paint(ellipse(x, base - 30 * k, 17 * k, 22 * k), 'cloth', gain=0.95, spec=0.25, tex=_fur(2, 0.06))
    c.paint(capsule(x + 4 * k, base - 40 * k, x + 18 * k, base - 46 * k, 7 * k, 2.6 * k), 'cloth', gain=1.0)
    c.paint(ellipse(x + 20 * k, base - 46 * k, 3.4 * k, 3 * k), 'copper', gain=1.25)
    c.dot(int(x + 9 * k), int(base - 47 * k), 'S2')
    for sg in (-1, 1):
        hx = x + sg * 20 * k
        c.paint(ellipse(hx, base - 16 * k, 8 * k, 7 * k), 'copper', gain=1.15 if sg < 0 else 0.95)
        for j in range(5):
            a = math.radians(-60 + j * 30)
            c.paint(capsule(hx + sg * 6 * k * math.cos(a), base - 16 * k + 6 * k * math.sin(a), hx + sg * 11 * k * math.cos(a), base - 16 * k + 10 * k * math.sin(a), 1.1 * k, 0.5 * k), 'paper', gain=1.05)
    for j in range(8):
        c.paint(ellipse(x - 50 * k + hsh(j, 2) * 100 * k, base - hsh(2, j) * 4, 2.5 * k, 1.8 * k), 'leather', gain=1.0)


def mouse(c, x, base, s=1.0, facing=1, ramp='silver', ear=1.0):
    """鼠（小）: 丸い胴、大きな丸い耳、尖った鼻と髭、長く巻く尾。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    pts = [(X(-12), base - 6 * k), (X(-24), base - 2 * k), (X(-34), base - 8 * k), (X(-40), base - 18 * k), (X(-36), base - 24 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.3 * k, 1.0 * k), 'copper', gain=1.0)
    c.paint(ellipse(X(-2), base - 11 * k, 14 * k, 11 * k), ramp, gain=0.85, tex=_fur(2, 0.05))
    c.paint(ellipse(X(12), base - 14 * k, 8 * k, 7 * k), ramp, gain=0.95)
    c.paint(poly([(X(16), base - 19 * k), (X(25), base - 12 * k), (X(16), base - 9 * k)], nrm(0.1, -0.3, 0.9)), ramp, gain=1.0)
    c.paint(ellipse(X(25), base - 12 * k, 1.8 * k, 1.6 * k), 'copper', gain=1.3)
    c.paint(ellipse(X(8), base - 18 * k - 6 * k * ear, 6 * k * ear, 6.5 * k * ear), ramp, gain=0.9)
    c.paint(ellipse(X(8.5), base - 18 * k - 6 * k * ear, 3.8 * k * ear, 4.2 * k * ear), 'copper', gain=1.2, outline=False)
    c.dot(int(X(16)), int(base - 16 * k), 'N0')
    c.dot(int(X(15.5)), int(base - 17 * k), 'S3')
    for dy in (-1, 1):
        c.paint(capsule(X(24), base - 12 * k, X(32), base - 12 * k + dy * 3 * k, 0.3 * k), 'paper', emit=0.6, outline=False)
    for dx in (-8, 6):
        c.paint(ellipse(X(dx), base - 1 * k, 3 * k, 1.6 * k), 'copper', gain=1.1)


def cheese(c, x, base, w=40, h=24):
    """穴のあいた三角のチーズ。"""
    pts = [(x - w / 2, base), (x + w / 2, base), (x + w / 2, base - h * 0.7), (x - w / 2, base - h * 0.2)]
    o = c.paint(poly(pts, nrm(-0.2, 0, 1)), 'gold', gain=1.0)
    c.paint(poly([(x - w / 2, base - h * 0.2), (x + w / 2, base - h * 0.7), (x + w / 2 - 8, base - h), (x - w / 2 - 6, base - h * 0.32)], nrm(-0.2, -0.8, 0.5)), 'gold', gain=1.2)
    for hx, hy, r in ((x - 8, base - 6, 3), (x + 6, base - 10, 4), (x + 14, base - 4, 2.4)):
        c.paint(ellipse(hx, hy, r, r * 0.9), 'gold', oid=o, gain=0.6, outline=False)


def mule(c, x, base, s=1.0, facing=1, ramp='leather', packs=True):
    """騾馬: 馬の体に長い耳、背に振り分けの荷。horse と同じ向き（facing=1 で頭が左）。"""
    horse(c, x, base, s=s, ramp=ramp, facing=facing)
    k = s
    X = lambda dx: x + facing * -dx * k
    by = base - 44 * k
    for dx, g in ((27, 0.85), (31, 1.05)):
        c.paint(poly([(X(dx), by - 36 * k), (X(dx + 4), by - 37 * k), (X(dx - 3), by - 58 * k)], nrm(-0.3, -0.4, 0.8)), ramp, gain=g)
    if packs:
        c.paint(poly([(X(16), by - 10 * k), (X(-16), by - 10 * k), (X(-18), by + 4 * k), (X(18), by + 4 * k)], nrm(0, -0.2, 1)), 'red', gain=0.95)
        c.paint(rect(min(X(12), X(-12)), by - 26 * k, max(X(12), X(-12)), by - 10 * k, nrm(-0.3, -0.4, 0.9)), 'paper', gain=1.0,
                tex=lambda px, py: -0.12 if int(py) % 6 == 0 else 0)
        c.paint(capsule(X(0), by - 26 * k, X(0), by + 4 * k, 1.2 * k), 'leather', gain=0.8)
        c.paint(ellipse(X(-2), by + 8 * k, 8 * k, 9 * k), 'leather', gain=1.0)


def otter(c, x, y, s=1.0):
    """川獺: 水に仰向けに浮かび、胸の上で貝を抱える。茶の毛、薄い腹、髭の頭、太い尾。"""
    k = s
    c.paint(capsule(x + 26 * k, y + 2 * k, x + 46 * k, y + 6 * k, 5 * k, 2.4 * k), 'leather', gain=0.85)
    c.paint(ellipse(x + 4 * k, y, 30 * k, 11 * k), 'leather', gain=1.0, spec=0.25, tex=_fur(3, 0.06))
    c.paint(ellipse(x + 2 * k, y - 4 * k, 20 * k, 6 * k), 'sand', gain=1.05, outline=False)
    c.paint(ellipse(x - 30 * k, y - 8 * k, 13 * k, 12 * k), 'leather', gain=1.05, tex=_fur(3, 0.05))
    c.paint(ellipse(x - 33 * k, y - 4 * k, 7 * k, 6 * k), 'sand', gain=1.15)
    c.paint(ellipse(x - 34 * k, y - 6 * k, 2 * k, 1.6 * k), 'cloth', gain=0.4)
    c.dot(int(x - 27 * k), int(y - 10 * k), 'N0')
    c.paint(ellipse(x - 22 * k, y - 15 * k, 2.4 * k, 2 * k), 'leather', gain=0.9)
    for dy in (-1, 1):
        c.paint(capsule(x - 36 * k, y - 4 * k, x - 44 * k, y - 4 * k + dy * 3 * k, 0.3 * k), 'paper', emit=0.6, outline=False)
    from parts import shell
    for dx in (-10, 4):
        c.paint(capsule(x + dx * k, y - 9 * k, x - 3 * k + dx * 0.4 * k, y - 15 * k, 3.4 * k, 3 * k), 'leather', gain=1.1)
    shell(c, int(x - 3 * k), int(y - 18 * k), 7 * k)
    for dx in (14, 22):
        c.paint(ellipse(x + dx * k, y - 9 * k, 3.4 * k, 2.6 * k), 'leather', gain=1.0)
    for j in range(3):
        rx = 40 * k + j * 10
        c.paint(ellipse(x, y + 6 * k, rx, 3 + j, clip=lambda px, py, rx=rx, j=j: abs(((px + 0.5 - x) / rx) ** 2 + ((py + 0.5 - y - 6 * k) / (3 + j)) ** 2 - 0.85) < 0.15),
                'water', emit=0.75 - j * 0.12, outline=False)


def ox(c, x, base, s=1.0, facing=1, ramp='wood', yoke=False):
    """牛: 重い胴と肩のこぶ、短い太い脚、下げた頭、横に張る角、房のある尾。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    by = base - 40 * k

    def leg(hx, fx, g):
        c.paint(capsule(X(hx), by + 4 * k, X(hx + 1), by + 22 * k, 5 * k, 3.6 * k), ramp, gain=g)
        c.paint(capsule(X(hx + 1), by + 22 * k, X(fx), base - 2 * k, 3.4 * k, 3 * k), ramp, gain=g)
        c.paint(ellipse(X(fx), base - 1 * k, 3.6 * k, 2 * k), 'hair', gain=0.7)
    leg(-24, -24, 0.7)
    leg(20, 21, 0.72)
    pts = [(X(-32), by - 8 * k), (X(-38), by + 8 * k), (X(-38), by + 22 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.6 * k), ramp, gain=0.9)
    c.paint(ellipse(X(-38), by + 25 * k, 2.6 * k, 4 * k), 'hair', gain=0.9)
    o = c.obj()
    c.paint(ellipse(X(-18), by, 18 * k, 17 * k), ramp, oid=o, gain=0.95)
    c.paint(ellipse(X(0), by + 2 * k, 26 * k, 16 * k), ramp, oid=o, gain=1.0)
    c.paint(ellipse(X(18), by - 3 * k, 17 * k, 19 * k), ramp, oid=o, gain=1.05)
    c.paint(ellipse(X(14), by - 18 * k, 12 * k, 7 * k), ramp, oid=o, gain=1.1)
    c.paint(ellipse(X(20), by + 14 * k, 9 * k, 7 * k), ramp, gain=0.85)  # 喉の垂れ
    c.paint(poly([(X(28), by - 14 * k), (X(42), by - 10 * k), (X(50), by + 8 * k), (X(44), by + 14 * k), (X(34), by + 10 * k), (X(28), by)],
                 lambda px, py: nrm(-0.2 * f, -0.4, 0.85)), ramp, gain=1.1)
    c.paint(ellipse(X(47), by + 11 * k, 5 * k, 4 * k), 'leather', gain=0.95)
    c.dot(int(X(48)), int(by + 11 * k), 'N0')
    c.dot(int(X(38)), int(by - 6 * k), 'N0')
    c.paint(ellipse(X(32), by - 12 * k, 3 * k, 2 * k), ramp, gain=0.9)
    pts = [(X(34), by - 12 * k), (X(28), by - 20 * k), (X(30), by - 28 * k), (X(36), by - 30 * k)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (2.2 - i * 0.6) * k, (1.6 - i * 0.6) * k), 'paper', gain=1.15)
    pts = [(X(40), by - 12 * k), (X(48), by - 18 * k), (X(50), by - 26 * k)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (2.0 - i * 0.7) * k, (1.4 - i * 0.6) * k), 'paper', gain=0.95)
    if yoke:
        c.paint(capsule(X(18), by - 24 * k, X(30), by - 20 * k, 3 * k), 'wood', gain=1.1)
    leg(-16, -17, 1.0)
    leg(14, 15, 1.05)


def pig(c, x, base, s=1.0, facing=1):
    """豚: 丸い桃色の胴、平たい鼻、垂れた耳、巻いた尾、短い脚。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    by = base - 22 * k
    for dx, g in ((-14, 0.75), (12, 0.78)):
        c.paint(capsule(X(dx), by + 6 * k, X(dx), base - 1, 3.4 * k, 2.6 * k), 'copper', gain=g)
    pts = [(X(-28), by - 4 * k), (X(-34), by - 8 * k), (X(-36), by - 2 * k), (X(-32), by)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.0 * k), 'copper', gain=1.1)
    c.paint(ellipse(X(-2), by, 28 * k, 17 * k), 'copper', gain=1.15, spec=0.15)
    c.paint(ellipse(X(24), by - 4 * k, 12 * k, 12 * k), 'copper', gain=1.2)
    c.paint(ellipse(X(34), by - 2 * k, 4 * k, 5 * k), 'copper', gain=1.05)
    for dy in (-2, 1.5):
        c.dot(int(X(35)), int(by - 2 * k + dy * k), 'R1')
    c.dot(int(X(27)), int(by - 9 * k), 'N0')
    for dx, g in ((18, 0.95), (24, 1.15)):
        c.paint(poly([(X(dx - 4), by - 14 * k), (X(dx + 5), by - 14 * k), (X(dx + 6), by - 6 * k)], nrm(0.2, -0.4, 0.8)), 'copper', gain=g)
    for dx, g in ((-20, 1.0), (16, 1.05)):
        c.paint(capsule(X(dx), by + 8 * k, X(dx), base - 1, 3.6 * k, 2.8 * k), 'copper', gain=g)
        c.paint(ellipse(X(dx), base - 1, 3 * k, 1.6 * k), 'hair', gain=0.8)


def mud_pool(c, x, y, rx=70, ry=12):
    """ぬかるみ: 照りの点のある泥の溜まり。"""
    c.paint(ellipse(x, y, rx, ry, normal=UP), 'leather', gain=0.65, dither=True, outline=False,
            tex=lambda px, py: 0.15 if hsh(int(px) // 2, int(py), 3) < 0.05 else 0)


def seal(c, x, base, s=1.0, facing=1):
    """海豹: 岩の上で頭をもたげる、灰色の滑らかな体、鰭、黒い大きな目と髭。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    c.paint(poly([(X(-40), base - 4 * k), (X(-52), base - 14 * k), (X(-50), base), (X(-36), base)], nrm(0, -0.5, 0.8)), 'silver', gain=0.85)
    pts = [(X(-36), base - 6 * k), (X(-10), base - 18 * k), (X(14), base - 30 * k), (X(22), base - 46 * k)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (9 + i * 3) * k, (12 + i * 1) * k if i < 2 else 9 * k), 'silver', gain=1.0, spec=0.5, shine=6)
    c.paint(ellipse(X(24), base - 50 * k, 10 * k, 9 * k), 'silver', gain=1.05, spec=0.5, shine=6)
    c.paint(ellipse(X(32), base - 47 * k, 5 * k, 4 * k), 'silver', gain=1.1)
    c.paint(ellipse(X(27), base - 53 * k, 2.4 * k, 2.6 * k), 'stone', emit=0.02, outline=False)
    c.dot(int(X(26)), int(base - 54 * k), 'S3')
    c.dot(int(X(36)), int(base - 48 * k), 'N0')
    for dy in (-1, 1):
        c.paint(capsule(X(34), base - 45 * k, X(42), base - 45 * k + dy * 3 * k, 0.3 * k), 'paper', emit=0.65, outline=False)
    c.paint(poly([(X(4), base - 18 * k), (X(14), base - 4 * k), (X(4), base - 2 * k)], nrm(0, -0.3, 0.9)), 'silver', gain=0.9)
    for j in range(5):
        c.dot(int(X(-20 + hsh(j, 4) * 30)), int(base - 14 * k - hsh(4, j) * 14 * k), 'S1')


def squirrel(c, x, base, s=1.0, facing=1):
    """栗鼠: 背を丸めて座り、両手で団栗を持つ。S の字にふくらむ尾、房のある耳。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    pts = [(X(-10), base - 6 * k), (X(-24), base - 14 * k), (X(-28), base - 34 * k), (X(-20), base - 50 * k), (X(-8), base - 56 * k), (X(-2), base - 50 * k)]
    for i in range(14):
        t = i / 13
        j = int(t * (len(pts) - 1) * 0.999)
        ft = t * (len(pts) - 1) - j
        px = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * ft
        py = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * ft
        r = (4.5 + 5 * math.sin(t * math.pi * 0.85)) * k
        c.paint(ellipse(px + (hsh(i, 1) - 0.5) * 2 * k, py, r, r * 0.9, normal=nrm(-0.35, -0.45, 0.8)), 'copper', gain=1.0 - 0.15 * (i % 2 == 1 and t > 0.3),
                tex=lambda qx, qy: -0.1 if (int(qx) * 3 + int(qy)) % 5 == 0 else 0, outline=i == 0)
    c.paint(ellipse(X(4), base - 14 * k, 11 * k, 13 * k), 'copper', gain=1.0, tex=_fur(2, 0.06))
    c.paint(ellipse(X(8), base - 13 * k, 5 * k, 9 * k), 'sand', gain=1.1, outline=False)
    c.paint(ellipse(X(-2), base - 4 * k, 9 * k, 5 * k), 'copper', gain=0.95)
    c.paint(ellipse(X(9), base - 32 * k, 8 * k, 7.5 * k), 'copper', gain=1.1)
    c.paint(ellipse(X(15), base - 30 * k, 4 * k, 3.4 * k), 'copper', gain=1.15)
    c.dot(int(X(18)), int(base - 31 * k), 'N0')
    c.dot(int(X(11)), int(base - 34 * k), 'N0')
    c.dot(int(X(10.5)), int(base - 35 * k), 'S3')
    c.paint(poly([(X(4), base - 37 * k), (X(9), base - 38 * k), (X(5), base - 47 * k)], nrm(-0.3, -0.4, 0.8)), 'copper', gain=1.05)
    c.paint(capsule(X(5), base - 46 * k, X(4), base - 49 * k, 1 * k), 'copper', gain=0.8)
    c.paint(ellipse(X(16), base - 20 * k, 4.4 * k, 5 * k), 'wood', gain=1.2, spec=0.3)
    c.paint(ellipse(X(16), base - 24 * k, 4.8 * k, 2.4 * k), 'leather', gain=0.8, tex=lambda px, py: -0.15 if (int(px) + int(py)) % 2 == 0 else 0)
    for dy in (-20, -17):
        c.paint(ellipse(X(12), base + dy * k, 2.4 * k, 2 * k), 'copper', gain=1.1)


def acorns(c, pts):
    for x, y in pts:
        c.paint(ellipse(x, y, 3, 3.6), 'wood', gain=1.2, spec=0.3)
        c.paint(ellipse(x, y - 3, 3.4, 1.8), 'leather', gain=0.8)


def turtle(c, x, base, s=1.0, facing=1):
    """亀: 甲羅の盛り上がりに六角の甲、縁の板、皺の首と頭、太い脚。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    for dx, g in ((-20, 0.75), (16, 0.78)):
        c.paint(capsule(X(dx), base - 8 * k, X(dx - 2), base - 1, 4.6 * k, 4 * k), 'foliage', gain=g)
    c.paint(capsule(X(22), base - 12 * k, X(36), base - 20 * k, 5 * k, 4.6 * k), 'foliage', gain=1.0, tex=lambda px, py: -0.1 if int(px) % 3 == 0 else 0)
    c.paint(ellipse(X(40), base - 22 * k, 9 * k, 7.5 * k), 'foliage', gain=1.15)
    c.dot(int(X(44)), int(base - 25 * k), 'N0')
    c.paint(capsule(X(42), base - 19 * k, X(46), base - 19 * k, 0.5 * k), 'foliage', gain=0.4, outline=False)
    c.paint(capsule(X(-30), base - 8 * k, X(-38), base - 6 * k, 2.4 * k, 1 * k), 'foliage', gain=0.9)
    c.paint(ellipse(x, base - 10 * k, 34 * k, 7 * k), 'wood', gain=0.9)
    def plates(px, py):
        row = int((py - base + 40 * k) / (9 * k))
        u = (px - x) / (12 * k) + row * 0.5
        return -0.3 if abs(u % 1 - 0.5) > 0.43 or abs(((py - base + 40 * k) / (9 * k)) % 1 - 0.5) > 0.42 else 0
    c.paint(ellipse(x, base - 12 * k, 31 * k, 28 * k, clip=lambda px, py: py < base - 10 * k), 'green', gain=1.05, spec=0.35, shine=6, tex=plates)
    for dx, g in ((-14, 1.0), (14, 1.05)):
        c.paint(capsule(X(dx), base - 8 * k, X(dx + 2), base - 1, 5 * k, 4.4 * k), 'foliage', gain=g)
        for j in range(3):
            c.dot(int(X(dx + 2 + (j - 1) * 2.4)), int(base - 1), 'S2')


def worm(c, x, base, s=1.0):
    """蚯蚓: 土の穴から S の字に身をもたげる、節の輪のある体。"""
    k = s
    pts = [(x + math.sin(t * 3.4) * 14 * k + t * 10 * k, base - t * 62 * k) for t in [i / 16 for i in range(17)]]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        r = (4.4 - i * 0.08) * k
        c.paint(capsule(a[0], a[1], b[0], b[1], r, r), 'copper', gain=1.15 + 0.01 * i, spec=0.4, shine=6,
                tex=lambda px, py: -0.12 if int(py) % 4 == 0 else 0)
    a, b = pts[5], pts[6]
    c.paint(capsule(a[0], a[1], b[0], b[1], 5.4 * k), 'red', gain=1.15)
    c.paint(ellipse(x, base + 1, 14 * k, 4 * k), 'stone', emit=0.04, outline=False)


def butterfly(c, x, y, s=1.0, ramp='blue', open_=1.0):
    """蝶: 上下 2 対の翅に縁の黒と白い点、細い胴と触角。open_ が小さいと翅を立てる。"""
    k = s
    for sg in (-1, 1):
        for (dx, dy, rx, ry) in ((13, -8, 13, 10), (9, 9, 8, 8)):
            cx_, cy_ = x + sg * dx * k * open_, y + dy * k
            c.paint(ellipse(cx_, cy_, rx * k * open_ + 1, ry * k), 'cloth', gain=0.5)
            c.paint(ellipse(cx_ - sg * 1 * k, cy_, (rx - 2.4) * k * open_ + 0.5, (ry - 2.4) * k), ramp, emit=lambda px, py, n: 0.8 + 0.2 * (1 - abs(px - x) / (26 * k)), outline=False)
        c.dot(int(x + sg * 20 * k * open_), int(y - 12 * k), 'S3')
        c.dot(int(x + sg * 16 * k * open_), int(y - 4 * k), 'S3')
        c.paint(capsule(x, y - 12 * k, x + sg * 7 * k, y - 22 * k, 0.4 * k), 'cloth', gain=0.6, outline=False)
        c.dot(int(x + sg * 7 * k), int(y - 22 * k), 'N3')
    c.paint(capsule(x, y - 12 * k, x, y + 12 * k, 1.6 * k, 1.0 * k), 'cloth', gain=0.7)


def falcon(c, x, y, s=1.0, facing=1):
    """鷹（とまった横向き）: 胸の横縞、たたんだ翼の羽先、鉤の嘴、目の下の黒い髭。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    c.paint(poly([(X(-6), y + 14 * k), (X(-14), y + 36 * k), (X(-6), y + 38 * k), (X(0), y + 18 * k)], nrm(-0.2, 0, 0.9)), 'wood', gain=0.85,
            tex=lambda px, py: -0.1 if int(py) % 4 == 0 else 0)
    c.paint(ellipse(X(0), y + 6 * k, 10 * k, 16 * k), 'sand', gain=1.05, tex=lambda px, py: -0.14 if int(py) % 4 == 0 and int(px) % 3 != 0 else 0)
    c.paint(poly([(X(-10), y - 4 * k), (X(4), y - 6 * k), (X(2), y + 16 * k), (X(-10), y + 30 * k), (X(-12), y + 10 * k)], lambda px, py: nrm(-0.3 * f, -0.2, 0.9)), 'wood', gain=1.0,
            tex=lambda px, py: -0.1 if (int(px) + int(py) * 2) % 6 == 0 else 0)
    c.paint(ellipse(X(3), y - 12 * k, 8 * k, 7.5 * k), 'wood', gain=1.05)
    c.paint(ellipse(X(5), y - 9 * k, 4 * k, 4 * k), 'sand', gain=1.15)
    c.paint(capsule(X(5), y - 12 * k, X(6), y - 6 * k, 1 * k), 'cloth', gain=0.5, outline=False)
    c.paint(ellipse(X(6), y - 14 * k, 2.2 * k, 2.2 * k), 'gold', emit=0.95, outline=False)
    c.dot(int(X(6.5)), int(y - 14 * k), 'N0')
    c.paint(poly([(X(9), y - 15 * k), (X(14), y - 12 * k), (X(12), y - 8 * k), (X(9), y - 10 * k)], nrm(0, -0.3, 0.9)), 'gold', gain=0.9)
    for dx in (-3, 3):
        c.paint(capsule(X(dx), y + 20 * k, X(dx), y + 25 * k, 1 * k), 'gold', gain=0.9, outline=False)


def dog_stand(c, x, base, s=1.0, facing=1, ramp='leather', run=False, patch='paper'):
    """犬（立つ・駆ける横向き）: 胸と腰のふくらみ、2 節の脚、口吻と垂れ耳、振り上げた尾、白い胸。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    by = base - 22 * k

    def leg(hip, knee, foot, g):
        c.paint(capsule(X(hip[0]), by + hip[1] * k, X(knee[0]), by + knee[1] * k, 3.2 * k, 2.2 * k), ramp, gain=g)
        c.paint(capsule(X(knee[0]), by + knee[1] * k, X(foot[0]), by + foot[1] * k, 2.0 * k, 1.6 * k), ramp, gain=g)
        c.paint(ellipse(X(foot[0] + 1), by + foot[1] * k + 0.5 * k, 2.4 * k, 1.4 * k), ramp, gain=g * 0.9)
    if run:
        legs = [((-14, 2), (-22, 10), (-30, 16)), ((-12, 2), (-14, 12), (-22, 20)), ((12, 2), (22, 8), (28, 14)), ((10, 2), (18, 12), (16, 20))]
    else:
        legs = [((-14, 2), (-17, 12), (-15, 21)), ((-10, 2), (-11, 12), (-10, 21)), ((12, 2), (13, 12), (13, 21)), ((8, 2), (8, 12), (7, 21))]
    leg(*legs[1], 0.7)
    leg(*legs[3], 0.72)
    pts = [(X(-16), by - 4 * k), (X(-24), by - 12 * k), (X(-28), by - 20 * k)] if not run else [(X(-16), by - 4 * k), (X(-26), by - 8 * k), (X(-34), by - 10 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.4 * k, 1.6 * k), ramp, gain=0.95)
    o = c.obj()
    c.paint(ellipse(X(-10), by, 10 * k, 8 * k), ramp, oid=o, gain=0.95)
    c.paint(ellipse(X(2), by, 14 * k, 8 * k), ramp, oid=o, gain=1.0)
    c.paint(ellipse(X(11), by - 1 * k, 8 * k, 9 * k), ramp, oid=o, gain=1.05)
    c.paint(ellipse(X(14), by + 2 * k, 5 * k, 6 * k), patch, oid=o, gain=1.0, outline=False)
    hy = by - (12 if not run else 6) * k
    c.paint(capsule(X(12), by - 4 * k, X(17), hy, 5 * k, 4.6 * k), ramp, gain=1.05)
    c.paint(ellipse(X(19), hy - 2 * k, 6.5 * k, 6 * k), ramp, gain=1.1)
    c.paint(capsule(X(22), hy, X(30), hy + 1 * k, 3.2 * k, 2.4 * k), ramp, gain=1.1)
    c.paint(capsule(X(23), hy + 2 * k, X(29), hy + 3 * k, 2 * k, 1.6 * k), patch, gain=1.0, outline=False)
    c.dot(int(X(31)), int(hy), 'N0')
    c.dot(int(X(21)), int(hy - 4 * k), 'N0')
    c.paint(poly([(X(15), hy - 6 * k), (X(19), hy - 8 * k), (X(14), hy + 4 * k)], nrm(-0.3, -0.2, 0.9)), ramp, gain=0.8)
    if run:
        c.paint(capsule(X(28), hy + 4 * k, X(26), hy + 8 * k, 1.2 * k), 'red', gain=1.0, outline=False)
    leg(*legs[0], 1.0)
    leg(*legs[2], 1.05)


def sled(c, x, base, w=110):
    """そり: 前の反り上がった 2 本の滑り木、荷台の板、積んだ毛皮と荷。"""
    pts = [(x - w / 2, base)] + [(x + w / 2 - 14 + 14 * math.sin(t * math.pi / 2), base - 18 * (1 - math.cos(t * math.pi / 2)) ** 1 * 1.4) for t in [i / 6 for i in range(7)]]
    for dy, g in ((0, 1.0), (-4, 0.75)):
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1] + dy, b[0], b[1] + dy, 1.8), 'wood', gain=g * 1.1)
    for px in range(int(x - w / 2 + 8), int(x + w / 2 - 14), 18):
        c.paint(rect(px, base - 12, px + 3, base), 'wood', gain=0.9)
    c.paint(rect(x - w / 2 + 2, base - 16, x + w / 2 - 10, base - 11, nrm(0, -0.6, 0.8)), 'wood', gain=1.1)
    c.paint(ellipse(x - 10, base - 24, w * 0.36, 10), 'leather', gain=1.0, tex=_fur(2, 0.08))
    c.paint(rect(x + 8, base - 36, x + 34, base - 16, nrm(-0.2, -0.2, 1)), 'red', gain=0.95)
    c.paint(rect(x + 8, base - 28, x + 34, base - 25), 'gold', gain=1.0, outline=False)


def harness_lines(c, x0, y0, x1, y1):
    """そりと馬をつなぐ引き綱。"""
    for dy in (0, 5):
        c.paint(capsule(x0, y0 + dy, x1, y1 + dy, 0.9), 'leather', gain=1.0)


def scrap_pile(c, x, base, w=150):
    """くず鉄の山: 錆びた車輪、曲がった棒、鍋、鎖、板の切れ端。"""
    c.paint(ellipse(x, base, w / 2, 30, clip=lambda px, py: py <= base), 'copper', gain=0.7, tex=lambda px, py: -0.14 if hsh(int(px) // 3, int(py) // 3, 5) < 0.25 else 0)
    wheel(c, x - 30, base - 34, 22, gain=0.9)
    c.paint(capsule(x - 64, base - 16, x + 10, base - 52, 2.4), 'silver', gain=0.9, spec=0.5)
    c.paint(capsule(x + 20, base - 50, x + 56, base - 10, 2.2), 'copper', gain=1.0)
    c.paint(ellipse(x + 24, base - 26, 18, 11), 'silver', gain=0.85, spec=0.6, shine=6)
    c.paint(ellipse(x + 24, base - 32, 16, 4), 'silver', gain=0.4, outline=False)
    c.paint(capsule(x + 40, base - 30, x + 52, base - 34, 1.6), 'silver', gain=0.8)
    chain(c, x - 50, base - 6, x + 6, base - 10, r=2.4)
    c.paint(poly([(x + 44, base - 2), (x + 70, base - 18), (x + 74, base - 12), (x + 50, base + 2)], nrm(-0.2, -0.4, 0.9)), 'silver', gain=0.75)
    for j in range(10):
        bx = x - w / 2 + 10 + hsh(j, 6) * (w - 20)
        c.paint(ellipse(bx, base - hsh(6, j) * 12, 3, 2), 'copper' if j % 2 else 'silver', gain=1.0)


def coin_jar(c, x, base, s=1.0):
    """蓄えの甕: 床下から掘り出した素焼きの甕、口からあふれる金貨。"""
    k = s
    o = c.paint(ellipse(x, base - 30 * k, 32 * k, 30 * k), 'copper', gain=0.95, spec=0.2,
                tex=lambda px, py: -0.06 if int(py) % 7 == 0 else 0)
    c.paint(rect(x - 16 * k, base - 66 * k, x + 16 * k, base - 56 * k, lambda px, py: nrm((px - x) / (16 * k), 0, 0.8)), 'copper', gain=1.0)
    c.paint(ellipse(x, base - 66 * k, 17 * k, 4 * k), 'copper', gain=1.2)
    c.paint(ellipse(x, base - 66 * k, 13 * k, 2.6 * k), 'stone', emit=0.05, outline=False)
    c.paint(capsule(x - 30 * k, base - 40 * k, x + 30 * k, base - 40 * k, 1.4 * k), 'cloth', oid=o, gain=0.8, outline=False)
    from parts import coin_pile
    coin_pile(c, x, base - 62 * k, 30 * k, 12 * k, metal='gold', r=6 * k, count=16, seed=4)
    for j, (dx, dy) in enumerate(((40, -4), (54, -8), (-44, -2), (30, 4))):
        coin(c, x + dx * k, base + dy * k, 7 * k, metal='gold', stamp=('crown', 'star')[j % 2], tilt=0.5)


def kiln(c, x, base, w=150, h=70):
    """登り窯: 斜面に連なる土の室、焚き口の炎、窓から漏れる火、手前に焼き上がりの壺。"""
    for j in range(3):
        cx = x - w / 2 + 26 + j * (w - 52) / 2
        cy = base - 10 - j * 10
        r = 30 - j * 2
        c.paint(ellipse(cx, cy, r, h * 0.6 - j * 4, clip=lambda px, py, cy=cy: py <= cy), 'copper', gain=0.85 - j * 0.05,
                tex=lambda px, py: -0.08 if (int(px) + int(py) * 2) % 9 == 0 else 0)
        c.paint(ellipse(cx, cy - 10, 5, 4), 'fire', emit=0.85, outline=False)
    mx, my = x - w / 2 + 26, base - 10
    c.paint(poly([(mx - 12, my + 10), (mx - 12, my - 6)] + arc_points(mx, my - 6, 12, math.pi, 2 * math.pi, 8) + [(mx + 12, my + 10)]), 'fire', emit=lambda px, py, n: 0.6 + 0.4 * (py - (my - 18)) / 28, outline=False)
    flame(c, mx, my + 4, 6, 10)
    c.brighten(mx, my, 50, 34, 0.25)
    c.paint(capsule(x + w / 2 - 14, base - 40, x + w / 2 - 14, base - 90, 6, 5), 'copper', gain=0.8)


def bucket(c, x, base, r=12, fill='gold'):
    """木の桶（中に燕麦）。"""
    c.paint(vcyl(x, base - r * 1.4, base, r, r * 0.35), 'wood', gain=1.0, tex=lambda px, py: -0.12 if int(px - x) % 5 == 0 else 0)
    c.paint(ellipse(x, base - r * 1.4, r - 1.5, r * 0.3), fill, gain=1.05, tex=lambda px, py: -0.1 if (int(px) + int(py)) % 2 == 0 else 0)
    for dy in (0.3, 1.0):
        c.paint(rect(x - r, base - r * dy - 1, x + r, base - r * dy + 1), 'silver', gain=0.8, outline=False)


def wanted_poster(c, x, y, w=46, h=60):
    """手配書: 顔の絵と、下に賞金の数字の札。"""
    c.paint(rect(x - w / 2, y, x + w / 2, y + h, nrm(-0.1, 0, 1)), 'paper', gain=1.05, tex=lambda px, py: -0.05 if (int(px) * 3 + int(py)) % 13 == 0 else 0)
    c.paint(ellipse(x, y + h * 0.36, w * 0.24, h * 0.2), 'paper', gain=0.7)
    c.paint(rect(x - w * 0.22, y + h * 0.22, x + w * 0.22, y + h * 0.28), 'cloth', gain=0.5, outline=False)
    for j in range(2):
        c.paint(rect(x - w * 0.35, y + h * (0.66 + j * 0.12), x + w * 0.35, y + h * (0.66 + j * 0.12) + 2), 'cloth', gain=0.5, outline=False)
    coin(c, x, y + h * 0.92, 5, metal='gold', tilt=0.6)
    c.paint(ellipse(x, y + 3, 2, 2), 'red', gain=1.0)


def glove_falcon():
    """手甲にとまらせた鷹（腕を上げた手の上）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(ellipse(x, y, 0.42 * u, 0.36 * u), 'leather', gain=1.0)
        falcon(c, x + fig.f * 0.2 * u, y - 2.1 * u, s=u / 16 * 1.05, facing=fig.f)
    return draw


def fishing_rod(deg=-50, length=6.5):
    """釣り竿と、先から垂れる糸。"""
    def draw(c, fig, hand):
        u = fig.u
        a = math.radians(deg)
        x, y = hand
        tx, ty = x + math.cos(a) * fig.f * length * u, y + math.sin(a) * length * u
        c.paint(capsule(x - math.cos(a) * fig.f * 0.8 * u, y - math.sin(a) * 0.8 * u, tx, ty, 0.14 * u, 0.06 * u), 'wood', gain=1.1)
        c.paint(capsule(tx, ty, tx + fig.f * 0.4 * u, fig.foot + 0.4 * u, 0.04 * u), 'paper', emit=0.7, outline=False)
    return draw


def brush():
    """馬の毛を梳く刷毛。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(rect(x - 0.5 * u, y - 0.25 * u, x + 0.5 * u, y + 0.15 * u, nrm(-0.2, -0.3, 0.9)), 'wood', gain=1.1)
        c.paint(rect(x - 0.45 * u, y + 0.15 * u, x + 0.45 * u, y + 0.4 * u), 'sand', gain=1.0, outline=False)
    return draw


def rider(c, x, base, s=1.2, facing=1, horse_ramp='leather', blanket=None, gallop=False, fig_h=74, props=(), **fig):
    """馬に乗った人: horse（facing=1 で頭が左）の背に、裾の長い衣の人を座らせ、鐙の脚を垂らす。
    fig は figure の引数（服・かぶり物）。props は場面データと同じ書き方。"""
    import figure as F
    import scenes
    k = s
    horse(c, x, base, s=s, ramp=horse_ramp, facing=facing, blanket=blanket, gallop=gallop)
    by = base - 44 * k
    fx = x + facing * 2 * k
    fig.setdefault('robe', True)
    f = F.figure(c, fx, by + 4 * k, h=fig_h, facing=-facing, props=[(sd, scenes._prop(p), fr) for sd, p, fr in props], **fig)
    u = f.u
    lx = fx - facing * 0.6 * u
    c.paint(capsule(lx, f.y_hip, lx - facing * 0.5 * u, by + 14 * k, 0.45 * u, 0.36 * u), fig.get('legs_ramp', 'cloth'), gain=1.0)
    c.paint(capsule(lx - facing * 0.5 * u, by + 12 * k, lx - facing * 0.5 * u, by + 20 * k, 0.4 * u), 'leather', gain=1.0)
    c.paint(ellipse(lx - facing * 0.9 * u, by + 20 * k, 0.6 * u, 0.28 * u), 'leather', gain=1.0)


def log_cabin(c, x, base, w=120, h=50, antlers=True):
    """狩り小屋: 丸太を積んだ壁（端が丸く出る）、板屋根、灯の窓、戸口の上に鹿の角。"""
    n = int(h / 8)
    for j in range(n):
        y = base - 4 - j * 8
        c.paint(capsule(x - w / 2, y, x + w / 2, y, 4), 'wood', gain=0.95 + 0.02 * (j % 2), tex=lambda px, py: -0.08 if int(px) % 9 == 0 else 0)
        for sg in (-1, 1):
            c.paint(ellipse(x + sg * (w / 2 + 2), y, 4, 4, normal=nrm(sg * 0.3, -0.2, 0.9)), 'sand', gain=0.9)
    pts = [(x - w / 2 - 12, base - h + 2), (x + w / 2 + 12, base - h + 2), (x, base - h - 38)]
    c.paint(poly(pts, lambda px, py: nrm(-0.5 if px < x else 0.4, -0.5, 0.7)), 'wood', gain=0.8, tex=lambda px, py: -0.1 if int(px + py) % 6 == 0 else 0)
    window(c, x - w * 0.34, base - h + 14, 16, 14, lit=True, arch=False)
    window(c, x + w * 0.2, base - h + 14, 16, 14, lit=True, arch=False)
    c.paint(rect(x - 10, base - 36, x + 6, base, nrm(-0.2, 0, 1)), 'wood', gain=0.6)
    if antlers:
        ax, ay = x - 2, base - h - 6
        c.paint(ellipse(ax, ay, 4, 4), 'wood', gain=1.0)
        for sg in (-1, 1):
            pts = [(ax + sg * 3, ay - 2), (ax + sg * 10, ay - 10), (ax + sg * 14, ay - 22)]
            for a, b in zip(pts, pts[1:]):
                c.paint(capsule(a[0], a[1], b[0], b[1], 1.2), 'paper', gain=1.0)
            for t in ((ax + sg * 10, ay - 10, ax + sg * 18, ay - 14), (ax + sg * 12, ay - 16, ax + sg * 8, ay - 24)):
                c.paint(capsule(t[0], t[1], t[2], t[3], 0.9), 'paper', gain=1.0)


PROPS = {'glove_falcon': glove_falcon, 'fishing_rod': fishing_rod, 'brush': brush}
