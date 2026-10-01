"""同盟（allies）で足した部品: 町と組合の人々の道具、御座船・棟上げ・柵の砦など。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, flame, paper_lantern, window, gem


def bauble(c, x, y, r=30, ramp='blue'):
    """飾り玉: 金の口金と房の付いた硝子の玉。中に光の渦、照りの点。"""
    c.paint(capsule(x, y - r - 30, x, y - r - 6, 0.8), 'gold', gain=1.0)
    c.paint(ellipse(x, y, r, r), ramp, gain=1.05, spec=1.0, shine=8)
    pts = [(x + math.cos(t) * t * r / 14, y + math.sin(t) * t * r / 18) for t in [i * 0.35 for i in range(32)]]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.9), 'gold', emit=0.85, outline=False)
    c.paint(ellipse(x - r * 0.4, y - r * 0.45, r * 0.22, r * 0.14), 'paper', emit=1.0, outline=False)
    c.paint(vcyl(x, y - r - 6, y - r + 2, 7, 2.4), 'gold', spec=0.8, shine=5)
    for j in range(5):
        tx = x - 6 + j * 3
        c.paint(capsule(tx, y + r - 2, tx + (j - 2) * 1.5, y + r + 18, 0.9), 'red', gain=1.1)
    c.paint(ellipse(x, y + r, 4, 3), 'gold', spec=0.6)


def palisade(c, x0, x1, base, h=50, gain=0.9):
    """柵の砦: 先を尖らせた丸太を並べ、横木で縛る。"""
    n = int((x1 - x0) / 9)
    for i in range(n):
        px = x0 + i * 9 + 4
        hh = h * (0.92 + 0.12 * hsh(i, 7))
        c.paint(poly([(px - 4, base), (px - 4, base - hh), (px, base - hh - 7), (px + 4, base - hh), (px + 4, base)],
                     lambda qx, qy, px=px: nrm((qx - px) / 4 * 0.7, 0, 0.8)), 'wood', gain=gain * (0.95 + 0.1 * (i % 2)))
    for yy in (base - h * 0.3, base - h * 0.75):
        c.paint(rect(x0, yy, x1, yy + 3, nrm(0, -0.3, 1)), 'wood', gain=gain * 0.8)


def watchtower(c, x, base, h=110, w=40):
    """物見櫓: 4 本の脚と筋交い、上に板囲いの台と屋根、篝火。"""
    top = base - h
    for sg in (-1, 1):
        c.paint(capsule(x + sg * w * 0.6, base, x + sg * w * 0.38, top + 22, 2.6), 'wood', gain=0.95 if sg < 0 else 0.8)
    for j in range(3):
        y0 = base - j * (h - 22) / 3
        y1 = base - (j + 1) * (h - 22) / 3
        t0, t1 = j / 3, (j + 1) / 3
        c.paint(capsule(x - w * (0.6 - 0.22 * t0), y0, x + w * (0.6 - 0.22 * t1), y1, 1.3), 'wood', gain=0.75)
        c.paint(capsule(x + w * (0.6 - 0.22 * t0), y0, x - w * (0.6 - 0.22 * t1), y1, 1.3), 'wood', gain=0.7)
    c.paint(rect(x - w * 0.55, top + 4, x + w * 0.55, top + 22, lambda px, py: nrm(-0.2, 0, 1)), 'wood', gain=1.05, tex=lambda px, py: -0.12 if int(px) % 6 == 0 else 0)
    flame(c, x - 6, top + 2, 4, 8)
    c.paint(poly([(x - w * 0.7, top - 6), (x + w * 0.7, top - 6), (x, top - 26)], nrm(-0.3, -0.5, 0.8)), 'wood', gain=0.9)
    c.paint(capsule(x - w * 0.5, top - 6, x - w * 0.5, top + 4, 1.2), 'wood', gain=0.9)
    c.paint(capsule(x + w * 0.5, top - 6, x + w * 0.5, top + 4, 1.2), 'wood', gain=0.8)


def timber_frame(c, x, base, w=150, h=80):
    """棟上げの骨組み: 白木の柱と梁、三角の小屋組み、棟に立てた幣。"""
    top = base - h
    for k in range(5):
        px = x - w / 2 + k * w / 4
        c.paint(rect(px - 3, top, px + 3, base, lambda qx, qy, px=px: nrm((qx - px) / 3 * 0.7, 0, 0.8)), 'sand', gain=1.15)
    for yy in (top, top + h * 0.5):
        c.paint(rect(x - w / 2 - 8, yy - 3, x + w / 2 + 8, yy + 3, nrm(0, -0.3, 1)), 'sand', gain=1.05)
    ridge = (x, top - 44)
    for sg in (-1, 1):
        c.paint(capsule(x + sg * (w / 2 + 8), top - 2, ridge[0], ridge[1], 3), 'sand', gain=1.1 if sg < 0 else 0.9)
        c.paint(capsule(x + sg * w / 4, top - 2, x + sg * w / 4, top - 22, 2), 'sand', gain=0.95)
    c.paint(rect(x - 2, ridge[1], x + 2, top, nrm(0, 0, 1)), 'sand', gain=1.0)
    c.paint(capsule(x - 30, ridge[1] + 2, x + 30, ridge[1] + 2, 2.4), 'sand', gain=1.2)
    for j in range(3):
        c.paint(poly([(x - 4 + j * 4, ridge[1] - 2), (x - 1 + j * 4, ridge[1] - 2), (x + j * 4, ridge[1] - 18), (x - 4 + j * 4, ridge[1] - 14)]),
                ('red', 'paper', 'blue')[j], gain=1.1)


def gozabune(c, x, wl, w=180):
    """御座船: 朱塗りの反った船体、二層の屋形と金の飾り、吹き流し。"""
    pts = [(x - w / 2 - 14, wl - 26), (x - w / 2, wl - 18), (x + w / 2 - 6, wl - 18), (x + w / 2 + 10, wl - 30), (x + w / 2 - 4, wl + 2), (x - w / 2 + 12, wl + 2)]
    c.paint(poly(pts, lambda px, py: nrm(-0.15, (py - wl + 8) / 12 * 0.8, 0.7)), 'red', gain=1.0, tex=lambda px, py: -0.12 if int(py - wl) % 6 == 0 else 0)
    c.paint(capsule(x - w / 2 - 14, wl - 26, x + w / 2 + 10, wl - 30, 1.6), 'gold', gain=1.0)
    cx, cw = x - 6, w * 0.5
    c.paint(rect(cx - cw / 2, wl - 50, cx + cw / 2, wl - 18, nrm(-0.15, 0, 1)), 'wood', gain=0.95)
    for j in range(5):
        window(c, cx - cw / 2 + 5 + j * (cw - 10) / 5, wl - 44, (cw - 10) / 5 - 4, 18, lit=True, arch=False)
    for ry, rw, hh in ((wl - 50, cw + 30, 12), (wl - 74, cw * 0.6 + 16, 10)):
        c.paint(poly([(cx - rw / 2, ry), (cx + rw / 2, ry), (cx + rw * 0.34, ry - hh), (cx - rw * 0.34, ry - hh)], nrm(-0.1, -0.6, 0.8)), 'cloth', gain=1.0)
        for sg in (-1, 1):
            c.paint(poly([(cx + sg * rw / 2, ry), (cx + sg * (rw / 2 + 6), ry - 6), (cx + sg * (rw / 2 - 4), ry - 3)]), 'gold', gain=1.0)
    c.paint(rect(cx - cw * 0.28, wl - 74, cx + cw * 0.28, wl - 62, nrm(-0.15, 0, 1)), 'red', gain=0.95)
    c.paint(ellipse(cx, wl - 88, 4, 4), 'gold', spec=0.8)
    mx = x + w / 2 - 18
    c.paint(capsule(mx, wl - 26, mx, wl - 106, 1.4), 'wood', gain=1.0)
    for j, col in enumerate(('red', 'paper', 'blue', 'gold', 'green')):
        y0 = wl - 104 + j * 3
        c.paint(poly([(mx, y0), (mx - 34 - j * 2, y0 + 6 + j * 2), (mx - 30, y0 + 9 + j * 2), (mx, y0 + 3)], lambda px, py: nrm(0, 0.3 * math.sin(px / 4), 0.9)), col, gain=1.0)
    from parts import foam
    foam(c, x - w / 2 + 10, x + w / 2 - 6, wl + 2)


def handshake(c, x, y, s=1.0):
    """結んだ二つの手: 左から青い袖、右から赤い袖、真ん中で握る手と、上に光る印。"""
    k = s
    c.paint(capsule(x - 90 * k, y + 22 * k, x - 24 * k, y + 4 * k, 17 * k, 13 * k), 'blue', gain=1.05)
    c.paint(capsule(x + 90 * k, y + 22 * k, x + 24 * k, y + 8 * k, 17 * k, 13 * k), 'red', gain=1.15)
    c.paint(rect(x - 30 * k, y - 8 * k, x - 22 * k, y + 18 * k, nrm(-0.4, 0, 0.9)), 'paper', gain=0.9)
    c.paint(rect(x + 22 * k, y - 4 * k, x + 30 * k, y + 22 * k, nrm(0.4, 0, 0.9)), 'paper', gain=0.8)
    c.paint(ellipse(x + 8 * k, y + 8 * k, 18 * k, 12 * k), 'skin', gain=0.95)
    c.paint(ellipse(x - 6 * k, y + 2 * k, 18 * k, 12 * k), 'skin', gain=1.15)
    for j in range(4):
        c.paint(capsule(x - 2 * k + j * 5 * k, y - 6 * k, x + 2 * k + j * 5 * k, y + 6 * k, 2.4 * k), 'skin', gain=1.1 - j * 0.03)
    c.paint(capsule(x - 16 * k, y - 4 * k, x - 4 * k, y - 10 * k, 3 * k, 2.4 * k), 'skin', gain=1.2)
    c.brighten(x, y - 46 * k, 40 * k, 30 * k, 0.25)
    for j in range(8):
        a = j * math.pi / 4
        c.paint(capsule(x + math.cos(a) * 8, y - 46 * k + math.sin(a) * 8, x + math.cos(a) * 16, y - 46 * k + math.sin(a) * 16, 1.2), 'gold', emit=0.95, outline=False)
    c.paint(ellipse(x, y - 46 * k, 5, 5), 'gold', emit=1.0, outline=False)


def dress_form(c, x, base, h=110, ramp='purple'):
    """仕立ての胴台: 三脚の台、布を当てて待ち針を打った胴、肩に掛けた巻き尺。"""
    for dx in (-18, 0, 18):
        c.paint(capsule(x, base - 22, x + dx, base, 1.8), 'wood', gain=0.95)
    c.paint(capsule(x, base - 20, x, base - h + 60, 2.4), 'wood', gain=1.0)
    top = base - h
    keys = [(top + 6, 10), (top + 14, 22), (top + 34, 20), (top + 46, 14), (top + 62, 22)]
    pts = [(x - w, y) for y, w in keys] + [(x + w, y) for y, w in reversed(keys)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / 22 * 0.8, 0, 0.7)), 'paper', gain=0.95)
    cl = [(x - 18, top + 30), (x + 22, top + 14), (x + 24, top + 64), (x + 30, top + 92), (x - 8, top + 96), (x - 20, top + 62)]
    c.paint(poly(cl, lambda px, py: nrm(0.3 * math.sin(px / 4), 0, 0.9)), ramp, gain=1.05)
    for j in range(6):
        px, py = x - 14 + hsh(j, 3) * 34, top + 30 + hsh(3, j) * 50
        c.paint(capsule(px, py, px + 3, py - 4, 0.5), 'silver', gain=1.2, outline=False)
        c.dot(int(px + 3), int(py - 4), 'R3')
    pts = [(x - 18, top + 10), (x - 22, top + 30), (x - 20, top + 60), (x - 26, top + 80)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.6), 'gold', gain=1.1, tex=lambda px, py: -0.2 if int(py) % 4 == 0 else 0)
    c.paint(ellipse(x, top + 2, 4, 4), 'wood', gain=1.1)


def pocket_watch(c, x, y, r=34):
    """懐中時計: 金の側と竜頭、白い文字盤に 12 の目盛りと針、蓋の内の歯車。"""
    c.paint(capsule(x, y - r - 4, x - 40, y - r - 30, 1.2), 'gold', gain=0.9)
    c.paint(ellipse(x, y - r - 4, 5, 4), 'gold', spec=0.8)
    c.paint(ellipse(x, y, r + 4, r + 4), 'gold', spec=0.9, shine=5)
    c.paint(ellipse(x, y, r, r, normal=nrm(-0.1, -0.1, 1)), 'paper', gain=1.1)
    for j in range(12):
        a = j * math.pi / 6
        c.paint(capsule(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, 0.9), 'cloth', gain=0.4, outline=False)
    c.paint(capsule(x, y, x + r * 0.15, y - r * 0.6, 1.2), 'cloth', gain=0.35, outline=False)
    c.paint(capsule(x, y, x + r * 0.5, y + r * 0.1, 1.0), 'cloth', gain=0.35, outline=False)
    c.paint(ellipse(x, y, 2.4, 2.4), 'red', gain=1.0)


def kanejaku():
    """大工の曲尺（L の字の金物の物差し）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        f = fig.f
        c.paint(capsule(x, y, x + f * 0.2 * u, y - 2.2 * u, 0.12 * u), 'silver', spec=0.6)
        c.paint(capsule(x + f * 0.2 * u, y - 2.2 * u, x + f * 1.6 * u, y - 2.1 * u, 0.12 * u), 'silver', spec=0.6)
    return draw


def courier_pole():
    """飛脚の担ぎ棒（肩の棒の先に、黒い文箱と小さな幟）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        f = fig.f
        ex, ey = x - f * 2.6 * u, y - 0.6 * u
        c.paint(capsule(x + f * 0.6 * u, y + 0.3 * u, ex, ey, 0.13 * u), 'wood')
        c.paint(rect(ex - 0.8 * u, ey + 0.1 * u, ex + 0.8 * u, ey + 1.3 * u, nrm(-0.3, -0.2, 0.9)), 'cloth', gain=0.8, spec=0.5)
        c.paint(rect(ex - 0.8 * u, ey + 0.6 * u, ex + 0.8 * u, ey + 0.75 * u), 'red', gain=1.0, outline=False)
        c.paint(poly([(ex, ey), (ex - f * 0.1 * u, ey - 1.6 * u), (ex - f * 0.9 * u, ey - 1.3 * u), (ex - f * 0.8 * u, ey - 0.6 * u)]), 'red', gain=1.0)
    return draw


def kagura_bell():
    """神楽鈴（柄の先に鈴の房、五色の布）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y + 0.4 * u, x, y - 1.2 * u, 0.1 * u), 'wood')
        for j in range(3):
            for i in range(3 - j):
                c.paint(ellipse(x + (i - (2 - j) / 2) * 0.32 * u, y - 1.3 * u - j * 0.3 * u, 0.15 * u, 0.15 * u), 'gold', spec=0.7)
        for j, col in enumerate(('red', 'blue', 'paper', 'green', 'gold')):
            c.paint(capsule(x, y + 0.3 * u, x + (j - 2) * 0.2 * u, y + 1.6 * u, 0.07 * u), col, gain=1.1, outline=False)
    return draw


def jinmaku(c, x0, x1, top, base, crest='gold'):
    """陣幕: 杭に張った白と黒の横縞の幕、真ん中に丸い家紋。"""
    n = int((x1 - x0) / 40) + 1
    for i in range(n):
        px = x0 + i * (x1 - x0) / (n - 1)
        c.paint(capsule(px, top - 6, px, base, 1.6), 'wood', gain=0.9)
    h = base - top
    pix_w, pix_k = [], []
    for y in range(int(top), int(base - 6)):
        for x in range(int(x0), int(x1)):
            sag = 3 * math.sin((x - x0) / (x1 - x0) * math.pi * (n - 1)) ** 2
            if y < top + sag:
                continue
            band = int((y - top - sag) / (h / 5))
            (pix_k if band % 2 == 1 else pix_w).append((x, y, nrm(0.25 * math.sin(x / 5), 0, 0.9)))
    o = c.obj()
    c.paint(pix_w, 'paper', oid=o, gain=0.95)
    c.paint(pix_k, 'cloth', oid=o, gain=0.6)
    cx, cy = (x0 + x1) / 2, top + h * 0.45
    c.paint(ellipse(cx, cy, 16, 16), crest, oid=o, gain=1.0, spec=0.3, outline=False)
    c.paint(ellipse(cx, cy, 11, 11), 'paper', oid=o, gain=0.95, outline=False)
    for j in range(3):
        a = j * 2 * math.pi / 3 - math.pi / 2
        c.paint(ellipse(cx + math.cos(a) * 5, cy + math.sin(a) * 5, 4, 4), crest, oid=o, gain=0.9, outline=False)


PROPS = {'kanejaku': kanejaku, 'courier_pole': courier_pole, 'kagura_bell': kagura_bell}
