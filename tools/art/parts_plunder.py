"""略奪（plunder）で足した部品: 海賊の船と宝、港と島、駱駝の作り直し。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, coin, flame, gem, window


def camel2(c, x, base, s=1.0, facing=1, ramp='sand', load='red'):
    """駱駝（作り直し。facing=1 で頭が左、parts.camel と同じ向き）: 胸・腹・尻の 3 つのふくらみに一つのこぶ、
    膝の張った 2 節の長い脚と平たい足、前へ伸びてから持ち上がる首、垂れた唇。こぶに房の付いた荷の布。"""
    k = s
    f = facing
    X = lambda dx: x - f * dx * k
    by = base - 48 * k

    def leg(hip, knee, foot, g):
        c.paint(capsule(X(hip), by + 6 * k, X(knee), by + 26 * k, 4.6 * k, 2.6 * k), ramp, gain=g)
        c.paint(ellipse(X(knee), by + 26 * k, 3 * k, 2.6 * k), ramp, gain=g)
        c.paint(capsule(X(knee), by + 26 * k, X(foot), base - 2 * k, 2.2 * k, 1.7 * k), ramp, gain=g)
        c.paint(ellipse(X(foot + 1), base - 1 * k, 3.4 * k, 1.6 * k), ramp, gain=g * 0.85)
    leg(-20, -22, -20, 0.7)
    leg(14, 16, 15, 0.72)
    pts = [(X(-28), by - 2 * k), (X(-32), by + 10 * k), (X(-31), by + 20 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.1 * k), ramp, gain=0.85)
    c.paint(ellipse(X(-31), by + 22 * k, 1.8 * k, 3 * k), 'hair', gain=0.8)
    o = c.obj()
    c.paint(ellipse(X(-18), by, 12 * k, 12 * k), ramp, oid=o, gain=0.95)
    c.paint(ellipse(X(-2), by + 2 * k, 20 * k, 11 * k), ramp, oid=o, gain=1.0)
    c.paint(ellipse(X(12), by, 13 * k, 13 * k), ramp, oid=o, gain=1.05)
    c.paint(ellipse(X(-3), by - 12 * k, 14 * k, 13 * k, clip=lambda px, py: py < by - 4 * k), ramp, oid=o, gain=1.1)
    if load:
        pts = [(X(-15), by - 14 * k), (X(-8), by - 22 * k), (X(4), by - 22 * k), (X(10), by - 14 * k), (X(13), by + 2 * k), (X(-18), by + 2 * k)]
        c.paint(poly(pts, lambda px, py: nrm(0.3 * math.sin(px / 3), -0.2, 0.9)), load, gain=1.0)
        c.paint(capsule(X(-18), by + 2 * k, X(13), by + 2 * k, 1.2 * k), 'gold', gain=1.0)
        for j in range(6):
            tx = X(-16 + j * 5.6)
            c.paint(capsule(tx, by + 3 * k, tx, by + 7 * k, 0.8 * k), 'gold', gain=1.1, outline=False)
    neck = [(X(18), by - 4 * k), (X(26), by - 2 * k), (X(33), by - 12 * k), (X(35), by - 26 * k)]
    for i, (a, b) in enumerate(zip(neck, neck[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (7 - i * 1.4) * k, (5.6 - i * 1.4) * k), ramp, gain=1.05 + 0.03 * i)
    c.paint(capsule(X(34), by - 30 * k, X(46), by - 26 * k, 5 * k, 3.2 * k), ramp, gain=1.12)
    c.paint(ellipse(X(47), by - 23 * k, 3 * k, 2 * k), ramp, gain=0.9)
    c.paint(poly([(X(32), by - 33 * k), (X(35), by - 34 * k), (X(31), by - 38 * k)]), ramp, gain=1.0)
    c.dot(int(X(39)), int(by - 31 * k), 'N0')
    c.dot(int(X(48)), int(by - 27 * k), 'N0')
    leg(-14, -16, -15, 1.0)
    leg(20, 22, 21, 1.05)


def amphora(c, x, base, s=1.0, ramp='copper'):
    """壺（アンフォラ）: 細い首と 2 つの取っ手、ふくらむ胴に黒い帯の絵、尖った底を木の台で支える。"""
    k = s
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 22 * k, base, x + sg * 10 * k, base - 22 * k, 2 * k), 'wood', gain=0.85)
    body = [(x, base - 6 * k)]
    prof = [(0, 0), (0.15, 10), (0.4, 24), (0.62, 26), (0.8, 18), (0.9, 9), (1.0, 8)]
    h = 96 * k
    pts = [(x + w * k, base - 6 * k - t * h) for t, w in prof] + [(x - w * k, base - 6 * k - t * h) for t, w in reversed(prof)]
    o = c.paint(poly(pts, lambda px, py: nrm((px - x) / (26 * k) * 0.9, 0, 0.6)), ramp, gain=1.05, spec=0.25)
    for t0, t1 in ((0.48, 0.54), (0.66, 0.69)):
        c.paint(rect(x - 27 * k, base - 6 * k - t1 * h, x + 27 * k, base - 6 * k - t0 * h), 'cloth', oid=o, gain=0.4, outline=False)
    for j in range(5):
        px = x - 18 * k + j * 9 * k
        c.paint(poly([(px - 3 * k, base - 6 * k - 0.48 * h), (px + 3 * k, base - 6 * k - 0.48 * h), (px, base - 6 * k - 0.38 * h)]), 'cloth', oid=o, gain=0.4, outline=False)
    c.paint(ellipse(x, base - 6 * k - h, 9 * k, 3 * k), ramp, gain=1.2)
    c.paint(ellipse(x, base - 6 * k - h, 6 * k, 1.8 * k), 'stone', emit=0.05, outline=False)
    for sg in (-1, 1):
        pts = arc_points(x + sg * 14 * k, base - 6 * k - 0.86 * h, 8 * k, -math.pi / 2 if sg > 0 else math.pi / 2, math.pi / 2 if sg > 0 else 3 * math.pi / 2, 8)
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.8 * k), ramp, gain=0.95)


def figurehead(c, x, y, s=1.0):
    """船首の像: 反った舳先の木に、髪をなびかせ胸に手を組んだ女の像、金の縁取り。"""
    k = s
    pts = [(x + 70 * k, y + 70 * k), (x + 20 * k, y + 40 * k), (x - 10 * k, y + 10 * k), (x - 26 * k, y - 20 * k)]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (16 - i * 4) * k, (12 - i * 4) * k), 'wood', gain=0.9)
    c.paint(capsule(x + 70 * k, y + 56 * k, x - 20 * k, y - 10 * k, 1.6 * k), 'gold', gain=1.0)
    for j in range(5):
        c.paint(capsule(x + 6 * k, y - 26 * k + j * 3 * k, x + 34 * k + j * 3 * k, y - 22 * k + j * 6 * k, 2.4 * k, 1.2 * k), 'gold', gain=0.85 + 0.04 * j)
    c.paint(ellipse(x - 2 * k, y + 14 * k, 14 * k, 22 * k), 'paper', gain=1.0)
    c.paint(ellipse(x - 4 * k, y - 18 * k, 9 * k, 10 * k), 'paper', gain=1.1)
    c.paint(ellipse(x + 2 * k, y - 24 * k, 9 * k, 6 * k, clip=lambda px, py: py < y - 20 * k), 'gold', gain=0.95)
    c.dot(int(x - 9 * k), int(y - 19 * k), 'N3')
    for sg in (-1, 1):
        c.paint(capsule(x + sg * 10 * k, y, x - sg * 4 * k, y + 8 * k, 3 * k), 'paper', gain=1.05)
    c.paint(poly([(x - 14 * k, y + 30 * k), (x + 14 * k, y + 30 * k), (x + 20 * k, y + 50 * k), (x - 6 * k, y + 54 * k)], nrm(-0.2, 0, 0.9)), 'red', gain=0.95)


def insignia(c, x, y, r=34):
    """記章: 赤い綬の 2 本の垂れ、金の八角の星、真ん中に紅玉。"""
    for sg in (-1, 1):
        c.paint(poly([(x + sg * 4, y - r - 30), (x + sg * 18, y - r - 30), (x + sg * 10, y - r * 0.3), (x, y - r * 0.4)], nrm(sg * 0.2, 0, 0.9)), 'red', gain=1.0)
        c.paint(poly([(x + sg * 8, y + r * 0.6), (x + sg * 20, y + r + 26), (x + sg * 12, y + r + 20), (x + sg * 6, y + r + 30)], nrm(0, 0, 1)), 'blue', gain=0.9)
    pts = []
    for j in range(16):
        a = j * math.pi / 8 - math.pi / 2
        rr = r if j % 2 == 0 else r * 0.62
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.paint(poly(pts, lambda px, py: nrm((px - x) / r * 0.5, (py - y) / r * 0.5, 0.8)), 'gold', spec=0.8, shine=5)
    c.paint(ellipse(x, y, r * 0.42, r * 0.42), 'silver', spec=0.7)
    gem(c, x, y, r * 0.24, 'red')


def royal_orb(c, x, base, r=34):
    """宝の珠: 金の球に十字の帯と宝石、頂に十字。"""
    cy = base - r
    c.paint(ellipse(x, base + 2, r * 0.9, 5), 'stone', emit=0.05, outline=False)
    o = c.paint(ellipse(x, cy, r, r), 'gold', spec=0.9, shine=6)
    c.paint(rect(x - r, cy - 3, x + r, cy + 3, lambda px, py: nrm((px - x) / r, 0, 0.7)), 'gold', oid=o, gain=1.15, outline=False)
    c.paint(rect(x - 3, cy - r, x + 3, cy, lambda px, py: nrm((px - x) / 4 * 0.6, 0, 0.8)), 'gold', oid=o, gain=1.15, outline=False)
    for dx, ramp in ((-0.6, 'blue'), (0, 'red'), (0.6, 'green')):
        gem(c, x + dx * r, cy, 4, ramp)
    c.paint(capsule(x, cy - r, x, cy - r - 22, 3), 'gold', spec=0.7)
    c.paint(capsule(x - 9, cy - r - 14, x + 9, cy - r - 14, 3), 'gold', spec=0.7)
    gem(c, x, cy - r - 24, 3.4, 'red')


def puzzle_box(c, x, base, w=100, h=56):
    """からくり箱: 寄木の市松の面、ずらした板と、半ば開いた引き出し。"""
    d = 20
    c.paint(poly([(x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2 + d, base - h - d * 0.6), (x - w / 2 + d, base - h - d * 0.6)], UP), 'wood', gain=1.2,
            tex=lambda px, py: -0.15 if (int((px - x) / 8) + int((py - base) / 5)) % 2 == 0 else 0)
    c.paint(poly([(x + w / 2, base), (x + w / 2 + d, base - d * 0.6), (x + w / 2 + d, base - h - d * 0.6), (x + w / 2, base - h)], nrm(0.85, 0, 0.5)), 'wood', gain=0.75,
            tex=lambda px, py: -0.12 if int((py - base) / 7) % 2 == 0 else 0)
    o = c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.2, 0, 1)), 'wood', gain=1.0,
                tex=lambda px, py: -0.18 if (int((px - x + 200) / 10) + int((py - base + 200) / 8)) % 2 == 0 else 0)
    c.paint(rect(x - w / 2 + 14, base - h * 0.45, x + 10, base - h * 0.15, nrm(-0.2, -0.3, 1)), 'wood', gain=1.25)
    c.paint(rect(x - w / 2 + 14, base - h * 0.15, x + 10, base - h * 0.08), 'wood', gain=0.6, outline=False)
    c.paint(ellipse(x - w / 2 + 38, base - h * 0.3, 3, 3), 'gold', spec=0.7)
    c.paint(rect(x + w / 2 - 30, base - h + 6, x + w / 2 - 8, base - h + 14), 'gold', oid=o, gain=0.9, outline=False)


def sextant(c, x, y, s=1.0):
    """測角器: 真鍮の扇形の枠と目盛りの弧、振れる腕、小さな望遠鏡と鏡。"""
    k = s
    r = 60 * k
    a0, a1 = math.radians(60), math.radians(120)
    for a in (a0, a1):
        c.paint(capsule(x, y, x + math.cos(a) * r, y + math.sin(a) * r, 2.4 * k), 'gold', spec=0.7)
    pts = arc_points(x, y, r, a0, a1, 16)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 4 * k), 'gold', spec=0.8, shine=5)
    for j in range(13):
        a = a0 + (a1 - a0) * j / 12
        c.paint(capsule(x + math.cos(a) * (r - 3 * k), y + math.sin(a) * (r - 3 * k), x + math.cos(a) * (r + 2 * k), y + math.sin(a) * (r + 2 * k), 0.5), 'stone', emit=0.08, outline=False)
    am = math.radians(98)
    c.paint(capsule(x, y, x + math.cos(am) * (r + 6 * k), y + math.sin(am) * (r + 6 * k), 2 * k), 'silver', spec=0.8)
    c.paint(capsule(x - 30 * k, y + 14 * k, x + 4 * k, y + 14 * k, 4 * k, 3.4 * k), 'cloth', gain=0.9, spec=0.5)
    c.paint(rect(x + 8 * k, y + 4 * k, x + 18 * k, y + 22 * k, nrm(-0.4, -0.2, 0.9)), 'water', emit=0.7)
    c.paint(ellipse(x, y, 5 * k, 5 * k), 'gold', spec=0.8)
    c.paint(capsule(x + 6 * k, y + 40 * k, x + 22 * k, y + 64 * k, 4 * k, 3 * k), 'wood', gain=1.0)


def kite_shield(c, x, y, s=1.0, ramp='blue', emblem='gold'):
    """大盾: 上が平らで下が尖る盾、鉄の縁と鋲、真ん中の獅子の代わりに金の十字と星。"""
    k = s
    pts = [(x - 36 * k, y - 44 * k), (x + 36 * k, y - 44 * k), (x + 34 * k, y + 4 * k), (x + 16 * k, y + 34 * k), (x, y + 48 * k), (x - 16 * k, y + 34 * k), (x - 34 * k, y + 4 * k)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / (36 * k) * 0.6, -0.2, 0.8)), 'silver', spec=0.8, shine=6)
    inner = [(px + (x - px) * 0.12, py + (y - py) * 0.12) for px, py in pts]
    o = c.paint(poly(inner, lambda px, py: nrm((px - x) / (36 * k) * 0.6, -0.2, 0.8)), ramp, gain=1.0, spec=0.2)
    c.paint(rect(x - 4 * k, y - 38 * k, x + 4 * k, y + 38 * k, nrm(-0.2, 0, 1)), emblem, oid=o, gain=1.05, spec=0.5, outline=False)
    c.paint(rect(x - 28 * k, y - 12 * k, x + 28 * k, y - 4 * k, nrm(-0.2, 0, 1)), emblem, oid=o, gain=1.05, spec=0.5, outline=False)
    for px, py in pts[:3] + pts[-2:]:
        c.paint(ellipse(px + (x - px) * 0.06, py + (y - py) * 0.06, 2 * k, 2 * k), 'silver', gain=1.2)


def sword_cane(c, x, y, ang=-30, ln=150, r=1.0):
    """仕込み杖: 漆の鞘と柄が分かれ、間から白刃がのぞく。r で太さを変える。"""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    p = lambda t: (x + dx * ln * t, y + dy * ln * t)
    c.paint(capsule(*p(0), *p(0.48), 3.4 * r, 3.2 * r), 'cloth', gain=0.9, spec=0.6)
    c.paint(capsule(*p(0.47), *p(0.7), 2.2 * r, 1.0 * r), 'silver', spec=1.0, shine=5)
    c.paint(capsule(*p(0.72), *p(1.0), 3.4 * r, 3.4 * r), 'cloth', gain=0.9, spec=0.6)
    c.paint(capsule(*p(0.72), *p(0.76), 3.8 * r), 'gold', spec=0.7)
    c.paint(capsule(*p(0.44), *p(0.47), 3.8 * r), 'gold', spec=0.7)
    c.paint(ellipse(*p(1.0), 4.4 * r, 4.4 * r), 'gold', spec=0.7)


def jewel_heap(c, x, base, w=90, n=26, seed=0):
    """宝石の山: 色とりどりの石を盛り、間に金の鎖。"""
    ramps = ('red', 'blue', 'green', 'purple', 'gold')
    c.paint(ellipse(x, base, w / 2, 16, clip=lambda px, py: py <= base), 'gold', gain=0.75)
    for j in range(n):
        t = hsh(j, seed)
        px = x + (t - 0.5) * w * 0.9
        py = base - 4 - hsh(seed, j) * 22 * (1 - abs(t - 0.5) * 1.6)
        gem(c, px, py, 4 + hsh(j, j) * 4, ramps[j % 5])


def birdcage(c, x, base, h=110, w=60, bird_ramp='gold'):
    """鳥かご: 丸い頂の金の籠、縦の細い桟、止まり木の小鳥、上の吊り輪。"""
    top = base - h
    c.paint(ellipse(x, base - 4, w / 2 + 6, 6), 'wood', gain=0.9)
    pts = arc_points(x, top + w / 2, w / 2, math.pi, 2 * math.pi, 14)
    for j in range(9):
        t = j / 8
        bx = x - w / 2 + t * w
        ty = top + w / 2 - math.sqrt(max(0, (w / 2) ** 2 - (bx - x) ** 2))
        c.paint(capsule(bx, ty, bx, base - 6, 0.8), 'gold', gain=0.95 - 0.2 * (j % 2), outline=False)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.6), 'gold', spec=0.7)
    c.paint(capsule(x - w / 2, base - 8, x + w / 2, base - 8, 2), 'gold', spec=0.6)
    c.paint(capsule(x - w / 2, top + w / 2 + 10, x + w / 2, top + w / 2 + 10, 1.2), 'gold', spec=0.6)
    pts = arc_points(x, top - 6, 6, 0, 2 * math.pi, 12)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.2), 'gold', spec=0.6)
    c.paint(capsule(x - 18, base - 40, x + 18, base - 40, 1.2), 'wood', gain=1.0)
    c.paint(ellipse(x, base - 48, 8, 6), bird_ramp, gain=1.1)
    c.paint(ellipse(x + 6, base - 54, 4.4, 4), bird_ramp, gain=1.15)
    c.paint(poly([(x + 10, base - 55), (x + 14, base - 54), (x + 10, base - 52)]), 'copper', gain=1.2)
    c.paint(poly([(x - 6, base - 48), (x - 16, base - 44), (x - 6, base - 44)]), bird_ramp, gain=0.8)
    c.dot(int(x + 7), int(base - 55), 'N0')


def jewel_egg(c, x, base, r=30):
    """宝玉の卵: 金の脚の台に、格子の金線と宝石をちりばめた卵。"""
    for sg in (-1, 0, 1):
        c.paint(capsule(x, base - 18, x + sg * 16, base, 2), 'gold', spec=0.6)
    cy = base - 20 - r * 1.25
    o = c.paint(ellipse(x, cy, r, r * 1.25), 'red', gain=1.05, spec=0.8, shine=7)
    for j in range(-3, 4):
        c.paint(ellipse(x + j * r * 0.28, cy, max(1.0, r * (1 - abs(j) * 0.28) * 0.08), r * 1.2 * math.sqrt(max(0, 1 - (j * 0.28) ** 2)),
                        clip=lambda px, py: True), 'gold', oid=o, gain=1.1, outline=False)
    for t in (-0.5, 0, 0.5):
        c.paint(ellipse(x, cy + t * r, r * math.sqrt(max(0, 1 - t * t * 0.64)) * 0.98, 1.2), 'gold', oid=o, gain=1.15, outline=False)
    for j in range(6):
        gem(c, x + (hsh(j, 4) - 0.5) * r * 1.2, cy + (hsh(4, j) - 0.5) * r * 1.8, 2.6, ('blue', 'green', 'paper')[j % 3] if j % 3 != 2 else 'blue')
    c.paint(ellipse(x - r * 0.35, cy - r * 0.6, r * 0.15, r * 0.25), 'paper', emit=0.95, outline=False)
    gem(c, x, cy - r * 1.3, 4, 'green')


def rope_coil(c, x, base, r=40):
    """巻いた綱: 甲板に渦に巻いて置いた太い麻縄、垂れた端。"""
    for j in range(6, 0, -1):
        rr = r * j / 6
        pts = arc_points(x, base - 8 - (6 - j) * 2, rr, 0, 2 * math.pi, 28)
        pts = [(px, base - 8 - (6 - j) * 2 + (py - (base - 8 - (6 - j) * 2)) * 0.35) for px, py in pts]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 3.6), 'sand', gain=1.0 + 0.02 * j, tex=lambda px, py: -0.15 if int(px + py) % 3 == 0 else 0)
    c.paint(capsule(x + r, base - 8, x + r + 30, base + 6, 3.6), 'sand', gain=1.05, tex=lambda px, py: -0.15 if int(px + py) % 3 == 0 else 0)


def pendant_big(c, x, y, r=26, ramp='blue'):
    """首飾り: 金の細い鎖の弧と、金の台の大きな雫形の石。"""
    pts = [(x + math.cos(t) * 80, y - 60 + math.sin(t) * 50) for t in [math.pi * (0.05 + 0.9 * i / 20) for i in range(21)]]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.0), 'gold', spec=0.7)
    c.paint(ellipse(x, y + 2, r + 4, r * 1.3 + 4), 'gold', spec=0.8)
    c.paint(poly([(x, y - r * 1.4), (x + r, y), (x, y + r * 1.4), (x - r, y)], lambda px, py: nrm(-0.3 if px < x else 0.3, -0.3 if py < y else 0.3, 0.8)), ramp, gain=1.1, spec=0.9, shine=6)
    c.paint(ellipse(x - r * 0.3, y - r * 0.5, r * 0.15, r * 0.3), 'paper', emit=1.0, outline=False)
    c.paint(ellipse(x, y - r * 1.4 - 4, 4, 4), 'gold', spec=0.7)


def stowaway_barrel(c, x, base, r=26, h=60):
    """潜り込み: 船倉の樽の蓋を少し持ち上げ、のぞく目。"""
    from parts import barrel
    barrel(c, x, base, r, h)
    c.paint(ellipse(x + 4, base - h - 10, r + 2, 6), 'wood', gain=1.1)
    c.paint(ellipse(x, base - h - 3, r - 3, 4), 'stone', emit=0.03, outline=False)
    for ex in (-6, 6):
        c.paint(ellipse(x + ex, base - h - 4, 2.4, 1.6), 'paper', emit=0.9, outline=False)
        c.dot(int(x + ex + 1), int(base - h - 4), 'N0')
    c.paint(capsule(x - r + 2, base - h - 2, x - r - 4, base - h - 10, 2.4), 'skin', gain=1.0)


def gondola(c, x, wl, w=170):
    """渡し小舟（ゴンドラ）: 細長い黒い船、反り上がった舳と艫、舳先の金の飾り。"""
    pts = [(x - w / 2, wl - 30), (x - w / 2 + 16, wl - 8), (x + w / 2 - 20, wl - 8), (x + w / 2, wl - 22), (x + w / 2 - 14, wl + 2), (x - w / 2 + 22, wl + 2)]
    c.paint(poly(pts, lambda px, py: nrm(-0.1, (py - wl + 4) / 8 * 0.7, 0.7)), 'cloth', gain=0.85, spec=0.6)
    c.paint(capsule(x - w / 2 + 16, wl - 8, x + w / 2 - 20, wl - 8, 1.4), 'gold', gain=1.0)
    for j in range(4):
        c.paint(rect(x - w / 2 + 2, wl - 32 + j * 3, x - w / 2 + 12, wl - 31 + j * 3), 'silver', gain=1.2, outline=False)
    c.paint(rect(x - 14, wl - 18, x + 18, wl - 8, nrm(0, -0.4, 0.9)), 'red', gain=1.0)
    from parts import foam
    foam(c, x - w / 2 + 22, x + w / 2 - 14, wl + 2)


def stilt_shack(c, x, base, w=80, h=40, leg=26):
    """湿地の小屋: 水の上に杭で持ち上げた板の小屋、藁屋根、灯の窓、梯子。"""
    for dx in (-w / 2 + 4, -w / 6, w / 6, w / 2 - 4):
        c.paint(capsule(x + dx, base - leg - 4, x + dx, base + 4, 2.4), 'wood', gain=0.85)
    fl = base - leg
    c.paint(rect(x - w / 2 - 6, fl - 4, x + w / 2 + 6, fl, nrm(0, -0.5, 0.9)), 'wood', gain=1.05)
    c.paint(rect(x - w / 2, fl - h, x + w / 2, fl - 4, nrm(-0.2, 0, 1)), 'wood', gain=0.9, tex=lambda px, py: -0.12 if int(px) % 7 == 0 else 0)
    window(c, x - w / 2 + 10, fl - h + 10, 14, 12, lit=True, arch=False)
    c.paint(poly([(x - w / 2 - 12, fl - h + 2), (x + w / 2 + 12, fl - h + 2), (x + 6, fl - h - 30)], lambda px, py: nrm(-0.5 if px < x else 0.4, -0.5, 0.7)), 'sand', gain=0.9,
            tex=lambda px, py: -0.12 if int(px - py * 0.3) % 4 == 0 else 0)
    for j in range(4):
        c.paint(capsule(x + w / 2 + 6, fl + j * 7, x + w / 2 + 14, fl + j * 7, 1), 'wood', gain=1.0)
    c.paint(capsule(x + w / 2 + 6, fl, x + w / 2 + 8, base + 2, 1.2), 'wood', gain=0.9)
    c.paint(capsule(x + w / 2 + 14, fl, x + w / 2 + 16, base + 2, 1.2), 'wood', gain=0.9)


def x_mark(c, x, y, s=1.0):
    """宝の印: 砂に描いた赤い ×。"""
    for sg in (-1, 1):
        c.paint(capsule(x - 14 * s, y - sg * 5 * s, x + 14 * s, y + sg * 5 * s, 2.4 * s), 'red', gain=1.0, outline=False)


def slipway(c, x0, x1, y):
    """船台: 海へ下る斜めの木の滑り道。"""
    c.paint(poly([(x0, y), (x1, y + 30), (x1, y + 40), (x0, y + 14)], nrm(0, -0.5, 0.9)), 'wood', gain=0.95,
            tex=lambda px, py: -0.12 if int(px) % 10 == 0 else 0)


def big_hammer(c, x, y, ang=-35, ln=130):
    """金槌: 革を巻いた長い柄と、金の大きな頭。"""
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
    c.paint(capsule(x, y, ex, ey, 4, 3.4), 'wood', gain=1.0)
    c.paint(capsule(x + math.cos(a) * 6, y + math.sin(a) * 6, x + math.cos(a) * 30, y + math.sin(a) * 30, 4.6), 'leather', gain=0.9, tex=lambda px, py: -0.15 if int(px + py) % 3 == 0 else 0)
    nx, ny = -math.sin(a), math.cos(a)
    hw, hl = 14, 34
    pts = [(ex + nx * hl + math.cos(a) * hw, ey + ny * hl + math.sin(a) * hw), (ex - nx * hl * 0.8 + math.cos(a) * hw, ey - ny * hl * 0.8 + math.sin(a) * hw),
           (ex - nx * hl * 0.8 - math.cos(a) * hw, ey - ny * hl * 0.8 - math.sin(a) * hw), (ex + nx * hl - math.cos(a) * hw, ey + ny * hl - math.sin(a) * hw)]
    c.paint(poly(pts, lambda px, py: nrm(-0.4, -0.5, 0.7)), 'gold', gain=0.8, spec=0.35, shine=5)
    c.paint(capsule(ex - math.cos(a) * hw, ey - math.sin(a) * hw, ex + math.cos(a) * hw, ey + math.sin(a) * hw, 3), 'gold', gain=0.7)


def big_scroll(c, x, y, w=120, h=70):
    """まじないの巻物: 両端の軸に巻かれた紙、紫に光る呪の文字と円。"""
    c.brighten(x, y, w, h, 0.3)
    c.paint(rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, nrm(-0.1, 0, 1)), 'paper', gain=1.1, tex=lambda px, py: -0.05 if (int(px) * 3 + int(py)) % 13 == 0 else 0)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * (w / 2 + 4), y - h / 2 - 6, x + sg * (w / 2 + 4), y + h / 2 + 6, 6), 'paper', gain=1.0)
        for dy in (-1, 1):
            c.paint(ellipse(x + sg * (w / 2 + 4), y + dy * (h / 2 + 8), 4, 3), 'gold', spec=0.7)
    pts = arc_points(x, y, h * 0.32, 0, 2 * math.pi, 24)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.8), 'purple', emit=0.95, outline=False)
    for j in range(5):
        a = j * 2 * math.pi / 5 - math.pi / 2
        b = (j + 2) * 2 * math.pi / 5 - math.pi / 2
        c.paint(capsule(x + math.cos(a) * h * 0.3, y + math.sin(a) * h * 0.3, x + math.cos(b) * h * 0.3, y + math.sin(b) * h * 0.3, 0.7), 'purple', emit=0.95, outline=False)
    for sg in (-1, 1):
        for j in range(4):
            yy = y - h * 0.3 + j * h * 0.2
            c.paint(rect(x + sg * w * 0.28 - 12, yy, x + sg * w * 0.28 + 12, yy + 2), 'purple', emit=0.8, outline=False)


def big_katana(c, x, y, ang=-12, ln=180):
    """刀: 反りのある白い刃、刃文、金の鍔、柄巻きの柄。"""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    hilt = 0.24
    pts = [(x + dx * ln * t - nx * 10 * (t - hilt) ** 2 * 3, y + dy * ln * t - ny * 10 * (t - hilt) ** 2 * 3) for t in [hilt + (1 - hilt) * i / 12 for i in range(13)]]
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(p[0], p[1], q[0], q[1], 3.2 * (1 - i / 16)), 'silver', spec=1.0, shine=5)
        c.paint(capsule(p[0] + nx * 1.5, p[1] + ny * 1.5, q[0] + nx * 1.5, q[1] + ny * 1.5, 0.6), 'paper', emit=0.9, outline=False)
    tx, ty = x + dx * ln * hilt, y + dy * ln * hilt
    c.paint(ellipse(tx, ty, 4, 8), 'gold', spec=0.7)
    c.paint(capsule(x, y, tx, ty, 3.6), 'cloth', gain=0.7, tex=lambda px, py: 0.3 if (int(px) + int(py)) % 4 == 0 else 0)
    c.paint(ellipse(x, y, 3.6, 3.6), 'gold', spec=0.6)


PROPS = {}
