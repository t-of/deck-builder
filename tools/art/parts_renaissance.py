"""ルネサンス（renaissance）で足した部品: 和の商いと学芸、プロジェクトの建物。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import UP, flame, paper_lantern, wheel, window, stone_wall


def koban_coin(c, x, y, w=22, h=34, tilt=1.0, gain=1.0):
    """小判: 縦長の楕円の金、横に細い筋（茣蓙目）、上下に刻印。tilt < 1 で寝かせる。"""
    ry = h / 2 * tilt
    o = c.paint(ellipse(x, y, w / 2, ry), 'gold', gain=gain, spec=0.7, shine=6,
                tex=lambda px, py: -0.14 if int((py - y) / max(1.0, tilt * 2.0)) % 2 == 0 else 0)
    c.paint(ellipse(x, y, w / 2 - 2, ry - 2 * tilt, normal=nrm(-0.15, -0.2, 0.95),
                    clip=lambda px, py: ((px + 0.5 - x) / (w / 2 - 2)) ** 2 + ((py + 0.5 - y) / (ry - 2 * tilt)) ** 2 > 0.82),
            'gold', oid=o, gain=gain * 0.8, outline=False)
    for dy in (-0.55, 0.55):
        c.paint(rect(x - w * 0.14, y + dy * ry - 2 * tilt, x + w * 0.14, y + dy * ry + 2 * tilt), 'gold', oid=o, gain=gain * 0.55, outline=False)
    c.dot(int(x - w * 0.22), int(y - ry * 0.5), 'G6')


def makiwara(c, x, base, h=74):
    """試し斬りの巻藁: 台の杭に藁の束、縄の巻き、斜めに切れた上端。"""
    c.paint(rect(x - 16, base - 6, x + 16, base, UP), 'wood', gain=0.8)
    c.paint(capsule(x, base - 4, x, base - h * 0.4, 3), 'wood', gain=0.8)
    pts = [(x - 11, base - 8), (x + 11, base - 8), (x + 11, base - h + 6), (x - 11, base - h - 4)]
    o = c.paint(poly(pts, lambda px, py: nrm((px - x) / 11 * 0.9, 0, 0.6)), 'sand', gain=1.15,
                tex=lambda px, py: -0.1 if int(px * 1.7) % 3 == 0 else 0)
    c.paint(poly([(x - 11, base - h - 4), (x + 11, base - h + 6), (x + 9, base - h + 9), (x - 11, base - h)], nrm(-0.3, -0.7, 0.6)), 'gold', oid=o, gain=1.05, outline=False)
    for k in range(3):
        yy = base - 18 - k * (h - 30) / 2.2
        c.paint(rect(x - 11, yy, x + 11, yy + 3, lambda px, py: nrm((px - x) / 11 * 0.9, 0, 0.6)), 'leather', oid=o, gain=0.9, outline=False)
    for k in range(5):  # 切り口から舞う藁くず
        c.paint(capsule(x + 16 + k * 7, base - h - 2 + hsh(k, 7) * 14, x + 19 + k * 7, base - h + 1 + hsh(k, 7) * 14, 0.7), 'gold', gain=1.2, outline=False)


def bonsai(c, x, base, s=1.0, pot=True):
    """盆栽: 浅い角鉢、うねる幹、平たい葉の雲を 4 つ。pot=False で鉢なしの松（舞台の背景）。"""
    k = s
    if pot:
        c.paint(poly([(x - 34 * k, base - 12 * k), (x + 34 * k, base - 12 * k), (x + 28 * k, base), (x - 28 * k, base)], nrm(-0.2, 0, 1)), 'blue', gain=0.9, spec=0.3)
        c.paint(rect(x - 36 * k, base - 15 * k, x + 36 * k, base - 11 * k, UP), 'blue', gain=1.1)
        c.paint(ellipse(x, base - 15 * k, 32 * k, 3 * k), 'leather', gain=0.6, outline=False)
    trunk = [(x - 2 * k, base - 14 * k), (x + 10 * k, base - 30 * k), (x - 8 * k, base - 46 * k), (x + 4 * k, base - 62 * k), (x - 4 * k, base - 76 * k)]
    for i, (a, b) in enumerate(zip(trunk, trunk[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], (6 - i * 1.2) * k, (5 - i * 1.2) * k), 'wood', gain=1.1,
                tex=lambda px, py: -0.08 if int(px + py * 0.5) % 4 == 0 else 0)
    c.paint(capsule(x + 8 * k, base - 34 * k, x + 30 * k, base - 40 * k, 2.4 * k, 1.6 * k), 'wood', gain=1.0)
    c.paint(capsule(x - 6 * k, base - 50 * k, x - 28 * k, base - 56 * k, 2.4 * k, 1.6 * k), 'wood', gain=1.0)
    for px, py, rx, ry in ((32, -44, 18, 8), (-30, -60, 20, 8), (6, -80, 22, 10), (16, -64, 12, 6)):
        for j in range(3):
            c.paint(ellipse(x + (px + (j - 1) * rx * 0.5) * k, base + (py - (1 - abs(j - 1)) * 3) * k, rx * 0.6 * k, ry * k), 'foliage', gain=1.15 + 0.05 * j,
                    tex=lambda qx, qy: -0.08 if (int(qx) * 3 + int(qy) * 5) % 7 == 0 else 0)


def kokeshi(c, x, base, s=1.0, ramp='red'):
    """こけし: 木の筒の胴に花の帯、丸い頭に黒髪と細い目。"""
    k = s
    o = c.paint(vcyl(x, base - 54 * k, base, 15 * k, 4 * k), 'wood', gain=1.25)
    for j, yy in enumerate((-48, -30, -12)):
        c.paint(rect(x - 15 * k, base + yy * k, x + 15 * k, base + (yy + 6) * k, lambda px, py: nrm((px - x) / (15 * k), 0, 0.8)), ramp, oid=o, gain=1.0, outline=False)
    for j in range(3):
        fx = x + (j - 1) * 8 * k
        c.paint(ellipse(fx, base - 21 * k, 3 * k, 3 * k), 'red' if j != 1 else 'green', oid=o, gain=1.1, outline=False)
    c.paint(ellipse(x, base - 72 * k, 19 * k, 18 * k), 'paper', gain=1.1)
    c.paint(ellipse(x, base - 80 * k, 19 * k, 12 * k, clip=lambda px, py: py < base - 76 * k or abs(px - x) > 13 * k), 'hair', gain=0.9)
    c.paint(ellipse(x, base - 89 * k, 6 * k, 3 * k), ramp, gain=1.0)
    for ex in (-6, 6):
        c.paint(capsule(x + (ex - 2.5) * k, base - 70 * k, x + (ex + 2.5) * k, base - 70 * k, 0.6 * k), 'hair', gain=0.4, outline=False)
    c.paint(ellipse(x, base - 62 * k, 2 * k, 1.2 * k), 'red', gain=1.0, outline=False)


def spice_heaps(c, x, base, s=1.0):
    """香辛料の山: 木の鉢に盛った 5 色の円錐（赤・金・銅・緑・紫）。"""
    k = s
    spots = ((-62, -16, 'red'), (0, -20, 'gold'), (62, -16, 'copper'), (-32, 4, 'green'), (32, 4, 'purple'))
    for dx, dy, ramp in spots:
        bx, by = x + dx * k, base + dy * k
        c.paint(ellipse(bx, by, 24 * k, 9 * k, clip=lambda px, py, by=by: py >= by - 2 * k), 'wood', gain=0.95)
        c.paint(poly([(bx - 22 * k, by - 2 * k), (bx + 22 * k, by - 2 * k), (bx + 2 * k, by - 26 * k), (bx - 2 * k, by - 26 * k)],
                     lambda px, py, bx=bx: nrm((px - bx) / (22 * k) * 0.9, -0.35, 0.7)), ramp, gain=1.1,
                tex=lambda px, py: -0.06 if (int(px) * 7 + int(py) * 3) % 5 == 0 else 0)
        c.paint(ellipse(bx, by - 2 * k, 22 * k, 5 * k, clip=lambda px, py, by=by: py >= by - 2 * k), ramp, gain=0.95, outline=False)


def magnifier(c, x, y, r=16, ang=40):
    """虫眼鏡: 金の輪、青く光るレンズ、木の柄。"""
    a = math.radians(ang)
    c.paint(capsule(x + math.cos(a) * r, y + math.sin(a) * r, x + math.cos(a) * (r + 26), y + math.sin(a) * (r + 26), 3.2, 2.6), 'wood', gain=1.0)
    c.paint(ellipse(x, y, r + 3, r + 3), 'gold', spec=0.8, shine=5)
    c.paint(ellipse(x, y, r, r), 'water', emit=lambda px, py, n: 0.55 + 0.25 * (1 - math.hypot(px - x + r * 0.4, py - y + r * 0.4) / (r * 1.6)), outline=False)
    c.paint(ellipse(x - r * 0.4, y - r * 0.4, r * 0.25, r * 0.15), 'paper', emit=1.0, outline=False)


def kimono_rack(c, x, base, w=150, h=110, ramp='red', pattern='gold'):
    """衣桁に掛けた着物: 鳥居形の木の枠、袖を広げた着物、金の模様と帯。"""
    for sg in (-1, 1):
        c.paint(rect(x + sg * w / 2 - 3, base - h, x + sg * w / 2 + 3, base, nrm(sg * -0.2, 0, 1)), 'wood', gain=0.9)
        c.paint(rect(x + sg * w / 2 - 12, base - 6, x + sg * w / 2 + 12, base, UP), 'wood', gain=0.8)
    c.paint(capsule(x - w / 2 - 10, base - h + 2, x + w / 2 + 10, base - h + 2, 3), 'wood', gain=1.05)
    top = base - h + 6
    sl = [(x - w / 2 + 4, top), (x + w / 2 - 4, top), (x + w / 2 - 4, top + 40), (x + 26, top + 44), (x + 28, base - 10), (x - 28, base - 10), (x - 26, top + 44), (x - w / 2 + 4, top + 40)]
    pat = lambda px, py: (0.12 if (int(px * 0.37 + py * 0.21) % 9 == 0 and int(py) % 3 == 0) else 0)
    o = c.paint(poly(sl, lambda px, py: nrm((px - x) / w * 0.6 + 0.25 * math.sin(px / 9), 0, 0.85)), ramp, gain=1.05, tex=pat)
    c.paint(poly([(x - 4, top), (x + 4, top), (x + 12, base - 10), (x + 2, base - 10)], nrm(0.4, 0, 0.9)), ramp, oid=o, gain=0.7, outline=False)
    c.paint(rect(x - 27, top + 46, x + 27, top + 58, lambda px, py: nrm((px - x) / 40, 0, 0.9)), pattern, oid=o, gain=0.95, spec=0.3, outline=False)
    for k in range(9):
        px = x - w / 2 + 16 + hsh(k, 3) * (w - 32)
        py = top + 8 + hsh(3, k) * 30
        c.paint(ellipse(px, py, 3, 3), pattern, gain=1.1, outline=False)
        c.dot(int(px), int(py), 'G6')


def temple_hall(c, x, base, w=176, h=46):
    """大伽藍の本堂: 石の基壇、朱の柱と白壁、反りの大屋根、金の鴟尾。"""
    c.paint(poly([(x - w / 2 - 8, base), (x + w / 2 + 8, base), (x + w / 2, base - 10), (x - w / 2, base - 10)], nrm(0, -0.4, 0.9)), 'stone', gain=0.9)
    top = base - 10 - h
    c.paint(rect(x - w / 2 + 8, top, x + w / 2 - 8, base - 10, nrm(-0.1, 0, 1)), 'paper', gain=0.85)
    n = 7
    for k in range(n + 1):
        px = x - w / 2 + 8 + k * (w - 16) / n
        c.paint(rect(px - 3, top, px + 3, base - 10, lambda qx, qy, px=px: nrm((qx - px) / 3 * 0.7, 0, 0.8)), 'red', gain=1.0)
        if k < n and k in (2, 3, 4):
            window(c, px + 6, top + 10, (w - 16) / n - 12, h - 18, lit=True, arch=False)
    c.paint(rect(x - w / 2 + 4, top - 6, x + w / 2 - 4, top, nrm(0, 0.3, 1)), 'red', gain=0.8)
    pts = [(x - w / 2 - 28, top - 4), (x - w / 2 - 14, top - 10), (x - w * 0.3, top - 34), (x + w * 0.3, top - 34), (x + w / 2 + 14, top - 10), (x + w / 2 + 28, top - 4), (x + w / 2, top - 6), (x - w / 2, top - 6)]
    c.paint(poly(pts, lambda px, py: nrm(0, -0.55, 0.8)), 'cloth', gain=1.0, tex=lambda px, py: -0.08 if int(px) % 5 == 0 else 0)
    c.paint(capsule(x - w * 0.3, top - 34, x + w * 0.3, top - 34, 2.4), 'cloth', gain=1.2)
    for sg in (-1, 1):
        sx = x + sg * w * 0.3
        c.paint(poly([(sx, top - 34), (sx - sg * 6, top - 46), (sx - sg * 2, top - 36)]), 'gold', spec=0.7)


def dashi(c, x, base, s=1.0):
    """祭りの山車: 大きな木の車輪、朱の幕と金の房、二層の屋根、提灯、頂の飾り。"""
    k = s
    for dx in (-40, 40):
        wheel(c, x + dx * k, base - 16 * k, 16 * k)
    c.paint(rect(x - 54 * k, base - 36 * k, x + 54 * k, base - 26 * k, nrm(0, -0.2, 1)), 'wood', gain=0.9)
    c.paint(rect(x - 48 * k, base - 76 * k, x + 48 * k, base - 36 * k, lambda px, py: nrm(0.2 * math.sin(px / 4), 0, 0.9)), 'red', gain=1.0)
    for j in range(5):
        tx = x - 40 * k + j * 20 * k
        c.paint(capsule(tx, base - 76 * k, tx, base - 54 * k, 1.6 * k), 'gold', gain=1.1)
        c.paint(ellipse(tx, base - 52 * k, 2.6 * k, 3 * k), 'gold', spec=0.6)
    c.paint(rect(x - 30 * k, base - 100 * k, x + 30 * k, base - 80 * k, nrm(-0.1, 0, 1)), 'wood', gain=1.0)
    window(c, x - 20 * k, base - 96 * k, 40 * k, 12 * k, lit=True, arch=False)
    for ry, rw in ((base - 78 * k, 120 * k), (base - 100 * k, 80 * k)):
        c.paint(poly([(x - rw / 2, ry), (x + rw / 2, ry), (x + rw * 0.36, ry - 12 * k), (x - rw * 0.36, ry - 12 * k)], nrm(-0.1, -0.6, 0.8)), 'cloth', gain=0.95)
        for sg in (-1, 1):
            c.paint(poly([(x + sg * rw / 2, ry), (x + sg * (rw / 2 + 6 * k), ry - 6 * k), (x + sg * (rw / 2 - 4 * k), ry - 3 * k)]), 'cloth', gain=1.0)
    c.paint(capsule(x, base - 112 * k, x, base - 128 * k, 1.6 * k), 'gold', spec=0.6)
    c.paint(ellipse(x, base - 130 * k, 5 * k, 5 * k), 'gold', spec=0.8)
    for dx in (-56, 56):
        paper_lantern(c, x + dx * k, base - 70 * k, 6 * k, 'fire', string=base - 78 * k)


def sewer_tunnel(c, x, top, base, w=180):
    """下水の暗渠: 奥へ続く煉瓦のアーチ、真ん中の水路、両側の歩み板。"""
    for i in range(6, -1, -1):
        t = i / 6
        s = 1 - t * 0.78
        ww, hh = w * s, (base - top) * s
        cy = base - (base - top) * 0.22 * t - hh
        bot = base - (base - top) * 0.3 * t
        pts = [(x - ww / 2, bot), (x - ww / 2, cy + ww / 2)] + arc_points(x, cy + ww / 2, ww / 2, math.pi, 2 * math.pi, 16) + [(x + ww / 2, bot)]
        g = 0.95 - t * 0.55
        c.paint(poly(pts, lambda px, py: nrm(0, 0.2, 1)), 'stone', gain=g, depth=t * 0.7,
                tex=lambda px, py: -0.12 if (int(py) % 6 == 0 or (int(px) + (int(py) // 6) * 5) % 11 == 0) else 0)
        inner = ww - 10 * s
        pts2 = [(x - inner / 2, bot)] + [(x - inner / 2, cy + ww / 2)] + arc_points(x, cy + ww / 2, inner / 2, math.pi, 2 * math.pi, 16) + [(x + inner / 2, bot)]
        c.paint(poly(pts2), 'stone', gain=0.3 + (1 - t) * 0.08, depth=0.5, outline=False)
    lt = c.light
    pix = []
    for y in range(int(base - (base - top) * 0.3), H):
        tt = (y - (base - (base - top) * 0.3)) / (H - (base - (base - top) * 0.3))
        hw = 8 + tt * 40
        for px in range(int(x - hw), int(x + hw)):
            pix.append((px, y, FLAT))
    c.paint(pix, 'water', emit=lambda px, py, n: 0.25 + 0.4 * lt.att(px, py) + (0.12 if math.sin(py * 1.3 + px * 0.15) > 0.75 else 0), dither=True, outline=False)


def star_map(c, x, y, rx=86, ry=44):
    """星の地図: 卓に広げた丸い天図（同心円と目盛り、星と星座の線、縁の飾り）。"""
    c.paint(rect(x - rx - 10, y - ry - 8, x + rx + 10, y + ry + 8, UP), 'paper', gain=0.85, tex=lambda px, py: -0.05 if (int(px) + int(py) * 3) % 17 == 0 else 0)
    o = c.paint(ellipse(x, y, rx, ry, normal=UP), 'blue', gain=0.75)
    for f in (0.66, 0.33):
        pts = arc_points(x, y, 1, 0, 2 * math.pi, 40)
        pts = [(x + (px - x) * rx * f, y + (py - y) * ry * f) for px, py in pts]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.4), 'gold', oid=o, emit=0.55, outline=False)
    for k in range(12):
        a = k * math.pi / 6
        c.paint(capsule(x + math.cos(a) * rx * 0.9, y + math.sin(a) * ry * 0.9, x + math.cos(a) * rx, y + math.sin(a) * ry, 0.6), 'gold', oid=o, emit=0.7, outline=False)
    stars = [(x - 50, y - 14), (x - 30, y - 24), (x - 10, y - 12), (x + 6, y - 26), (x + 30, y - 6), (x + 52, y - 18), (x + 20, y + 18), (x - 24, y + 16), (x - 56, y + 8)]
    for a, b in zip(stars[:6], stars[1:6]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.4), 'paper', oid=o, emit=0.7, outline=False)
    c.paint(capsule(stars[6][0], stars[6][1], stars[4][0], stars[4][1], 0.4), 'paper', oid=o, emit=0.7, outline=False)
    c.paint(capsule(stars[7][0], stars[7][1], stars[8][0], stars[8][1], 0.4), 'paper', oid=o, emit=0.7, outline=False)
    for i, (sx, sy) in enumerate(stars):
        c.paint(ellipse(sx, sy, 2.2, 1.6), 'gold', oid=o, emit=1.0, outline=False)
        c.dot(int(sx), int(sy), 'G6')
    for k in range(30):
        c.dot(int(x + (hsh(k, 8) - 0.5) * rx * 1.6), int(y + (hsh(8, k) - 0.5) * ry * 1.6), 'S2')


def rice_bales(c, x, base, rows=(3, 2, 1), r=12, ln=40):
    """米俵の山: 藁の俵を横に寝かせて積み、縄の帯を 3 本。"""
    for j, n in enumerate(rows):
        for i in range(n):
            bx = x + (i - (n - 1) / 2) * (r * 2 + 2) + j * 3
            by = base - r - j * (r * 1.7)
            o = c.paint(ellipse(bx, by, r, r), 'sand', gain=1.1, tex=lambda px, py: -0.08 if int(px * 1.3 + py) % 3 == 0 else 0)
            c.paint(ellipse(bx, by, r * 0.62, r * 0.62, normal=nrm(-0.3, -0.3, 0.9)), 'gold', oid=o, gain=0.85, outline=False)
            for a in (0.2, 1.4, 2.6, 3.8, 5.0):
                c.dot(int(bx + math.cos(a) * r * 0.85), int(by + math.sin(a) * r * 0.85), 'G1')


def kura(c, x, base, w=90, h=60):
    """土蔵: 白い漆喰の壁、黒い腰壁のなまこ格子、厚い瓦屋根、小さな窓と鉄の扉。"""
    c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.25, 0, 1)), 'paper', gain=0.95)
    c.paint(rect(x - w / 2, base - h * 0.36, x + w / 2, base, nrm(-0.25, 0, 1)), 'cloth', gain=0.7,
            tex=lambda px, py: 0.25 if (int(px - x) + int(py)) % 8 == 0 or (int(px - x) - int(py)) % 8 == 0 else 0)
    c.paint(rect(x - 12, base - h * 0.62, x + 12, base, nrm(-0.2, 0, 1)), 'cloth', gain=0.55)
    c.paint(rect(x - 10, base - h * 0.6, x - 1, base, nrm(-0.2, 0, 1)), 'silver', gain=0.6, spec=0.3)
    window(c, x + w * 0.22, base - h * 0.85, 10, 9, lit=True, arch=False)
    pts = [(x - w / 2 - 14, base - h + 2), (x + w / 2 + 14, base - h + 2), (x + w / 2 - 6, base - h - 24), (x - w / 2 + 6, base - h - 24)]
    c.paint(poly(pts, nrm(-0.1, -0.6, 0.8)), 'cloth', gain=1.0, tex=lambda px, py: -0.1 if int(px) % 5 == 0 else 0)
    c.paint(capsule(x - w / 2 + 2, base - h - 26, x + w / 2 - 2, base - h - 26, 4), 'cloth', gain=1.1)


def kabuki_stage(c, x0, x1, top, base, pulled=0.42):
    """芝居小屋の舞台: 檜の床、黒・柿・萌黄の縦縞の定式幕（左へ引き寄せ）、奥に松の背景、上に提灯の列。"""
    c.paint(rect(x0, top, x1, base - 18, nrm(0, 0, 1)), 'gold', gain=0.55)
    bonsai(c, (x0 + x1) / 2 + 40, base - 6, s=1.0, pot=False)
    c.paint(rect(x0 - 6, base - 18, x1 + 6, base, UP), 'wood', gain=1.2, tex=lambda px, py: -0.1 if int(px) % 14 == 0 else 0)
    c.paint(rect(x0 - 6, base, x1 + 6, base + 6, nrm(0, 0.2, 1)), 'wood', gain=0.75)
    cw = (x1 - x0) * pulled
    cols = ('cloth', 'copper', 'green')
    pix_cols = {}
    for px in range(int(x0), int(x0 + cw)):
        k = int((px - x0) / 10) % 3
        pix_cols.setdefault(cols[k], []).extend((px, py, nrm(0.35 * math.sin((px - x0) / 3.2), 0, 0.9)) for py in range(int(top), int(base - 18 + 4 * math.sin(px / 7))))
    o = c.obj()
    for ramp, pix in pix_cols.items():
        c.paint(pix, ramp, oid=o, gain=1.0 if ramp != 'cloth' else 1.3)
    c.paint(rect(x0 - 10, top - 14, x1 + 10, top, nrm(0, 0.2, 1)), 'red', gain=0.9)
    for k in range(7):
        lx = x0 + 12 + k * (x1 - x0 - 24) / 6
        paper_lantern(c, lx, top - 6, 5, 'fire', glow=False, string=top - 14)


def strip_fields(c, y0):
    """畑まわしの畑: 奥へすぼまる畝の帯を、麦・菜・休み地・豆で塗り分ける。"""
    crops = ('gold', 'foliage', 'leather', 'green', 'gold', 'leather', 'foliage')
    n = len(crops)
    groups = {}
    for y in range(int(y0), H):
        t = (y - y0) / (H - y0)
        sc = 0.25 + 0.75 * t
        for x in range(W):
            u = (x - 112) / sc / 224 + 0.5
            if 0 <= u < 1:
                groups.setdefault(int(u * n), []).append((x, y, nrm(0.3 * math.sin((x - 112) / sc * 0.9), -0.5, 0.8)))
    for k, pix in sorted(groups.items()):
        ramp = crops[k]
        c.paint(pix, ramp, gain=0.95 if ramp != 'leather' else 0.8, dither=True, outline=False,
                tex=lambda px, py: -0.08 if int(py) % 3 == 0 else 0)


def tenshu(c, x, base, s=1.0):
    """山城の天守: 反りのある石垣、白壁の 3 層、黒い屋根と破風、金の鯱。"""
    k = s
    sw = 74 * k
    pts = [(x - sw, base)]
    for t in [i / 8 for i in range(9)]:
        pts.append((x - sw + (sw - 54 * k) * (t ** 2), base - t * 34 * k))
    pts += [(x + 54 * k - (sw - 54 * k) * 0, base - 34 * k)]
    pts += [(x + sw - (sw - 54 * k) * (t ** 2), base - t * 34 * k) for t in [i / 8 for i in range(8, -1, -1)]]
    c.paint(poly(pts, lambda px, py: nrm(-0.5 if px < x else 0.45, -0.25, 0.8)), 'stone', gain=1.0,
            tex=lambda px, py: -0.12 if (int(py) % 6 == 0 or (int(px) + (int(py) // 6) * 7) % 13 == 0) else 0)
    y = base - 34 * k
    for j, (ww, hh) in enumerate(((100, 26), (76, 22), (52, 22))):
        ww, hh = ww * k, hh * k
        c.paint(rect(x - ww / 2, y - hh, x + ww / 2, y, lambda px, py: nrm(-0.3 if px < x else 0.25, 0, 0.9)), 'paper', gain=1.0)
        for wx in range(-1, 2):
            window(c, x + wx * ww * 0.28 - 3 * k, y - hh + 7 * k, 6 * k, 7 * k, lit=(wx + j) % 2 == 0, arch=False)
        rw = ww + 26 * k
        ry = y - hh
        c.paint(poly([(x - rw / 2, ry + 3 * k), (x - rw / 2 + 6 * k, ry - 2 * k), (x + rw / 2 - 6 * k, ry - 2 * k), (x + rw / 2, ry + 3 * k),
                      (x + ww * 0.36, ry - 10 * k), (x - ww * 0.36, ry - 10 * k)], nrm(-0.05, -0.6, 0.8)), 'cloth', gain=1.0)
        c.paint(poly([(x - 12 * k, ry - 6 * k), (x + 12 * k, ry - 6 * k), (x, ry - 18 * k)], nrm(-0.3, -0.4, 0.8)), 'paper', gain=0.9)
        c.paint(poly([(x - 14 * k, ry - 5 * k), (x, ry - 20 * k), (x + 14 * k, ry - 5 * k), (x + 12 * k, ry - 5 * k), (x, ry - 17 * k), (x - 12 * k, ry - 5 * k)]), 'cloth', gain=1.1)
        y = ry - 8 * k
    c.paint(poly([(x - 30 * k, y + 2 * k), (x + 30 * k, y + 2 * k), (x + 16 * k, y - 12 * k), (x - 16 * k, y - 12 * k)], nrm(-0.05, -0.6, 0.8)), 'cloth', gain=1.05)
    for sg in (-1, 1):
        sx = x + sg * 16 * k
        c.paint(poly([(sx, y - 12 * k), (sx + sg * 2 * k, y - 22 * k), (sx - sg * 4 * k, y - 16 * k)]), 'gold', spec=0.8)


def saihai():
    """采配: 短い柄の先に、細く裂いた紙の房。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x + fig.f * 0.5 * u, y - 1.3 * u
        c.paint(capsule(x, y + 0.5 * u, tx, ty, 0.14 * u), 'wood', gain=1.0)
        c.paint(ellipse(tx, ty, 0.2 * u, 0.2 * u), 'gold', spec=0.6)
        for j in range(9):
            a = math.radians(-160 + j * 18)
            ln = (1.4 + 0.3 * hsh(j, 2)) * u
            ex, ey = tx + math.cos(a) * ln * 0.5 * fig.f, ty - math.sin(a) * 0.2 * u + ln * 0.75
            c.paint(capsule(tx, ty, ex, ey, 0.14 * u, 0.08 * u), 'paper', gain=1.2)
    return draw


def held_abacus():
    """手に提げた算盤。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        from parts import abacus
        abacus(c, x + fig.f * 0.8 * u, y + 0.2 * u, w=2.6 * u, h=1.5 * u)
    return draw


def barge(c, x, wl, w=170, h=20):
    """荷船: 平底の深い船体、舷の縁、船尾の竿。"""
    pts = [(x - w / 2 - 8, wl - h), (x + w / 2 + 4, wl - h), (x + w / 2 - 8, wl + 3), (x - w / 2 + 10, wl + 3)]
    c.paint(poly(pts, lambda px, py: nrm(-0.15, (py - wl + h / 2) / h * 0.9, 0.7)), 'wood', gain=1.0,
            tex=lambda px, py: -0.1 if int(py - wl) % 5 == 0 else 0)
    c.paint(capsule(x - w / 2 - 8, wl - h, x + w / 2 + 4, wl - h, 1.8), 'wood', gain=1.25)
    c.paint(capsule(x + w / 2 - 10, wl - h - 4, x + w / 2 + 26, wl - h - 70, 1.3), 'wood', gain=0.9)
    from parts import foam
    foam(c, x - w / 2 + 6, x + w / 2 - 4, wl + 3)


def dagger_stuck(c, x, base, s=1.0):
    """卓に突き立てた短刀（斜めに刺さる刃、鍔、柄巻き）。"""
    k = s
    tip = (x, base)
    top = (x - 10 * k, base - 40 * k)
    c.paint(capsule(tip[0], tip[1], top[0], top[1], 1.0 * k, 3.2 * k), 'silver', spec=0.9, shine=5)
    c.paint(capsule(top[0] - 8 * k, top[1] + 2 * k, top[0] + 8 * k, top[1] - 2 * k, 2 * k), 'gold', spec=0.6)
    end = (x - 15 * k, base - 64 * k)
    c.paint(capsule(top[0], top[1], end[0], end[1], 3 * k), 'red', gain=0.9, tex=lambda px, py: -0.15 if int(py) % 3 == 0 else 0)
    c.paint(ellipse(end[0], end[1], 3.4 * k, 3.4 * k), 'gold', spec=0.6)
    c.paint(ellipse(x + 3, base + 1, 8 * k, 2 * k), 'stone', emit=0.05, outline=False)


PROPS = {'saihai': saihai, 'held_abacus': held_abacus}


def shoji_wall(c, y0=0, y1=H, gain=0.8):
    """障子の壁: 和紙の面に細い木の桟、太い柱が 3 本。"""
    paper, wood = [], []
    for y in range(int(y0), int(y1)):
        for x in range(W):
            if x % 74 < 6:
                continue
            (wood if (x % 74) % 17 == 6 or y % 15 == 0 else paper).append((x, y, FLAT))
    c.paint(paper, 'paper', gain=gain * 0.85, dither=True, outline=False, depth=0.15)
    c.paint(wood, 'wood', gain=gain * 0.9, dither=True, outline=False)
    for k in range(4):
        x = k * 74
        c.paint(rect(x, y0, x + 6, y1, lambda px, py, x=x: nrm((px - x - 3) / 3 * 0.7, 0, 0.8)), 'wood', gain=gain)
