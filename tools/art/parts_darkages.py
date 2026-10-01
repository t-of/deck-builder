"""暗黒時代（darkages）で足した部品。描き方は parts.py と同じ（形と向きとランプだけ渡す）。"""
import math

from engine import FLAT, H, W, arc_points, capsule, ellipse, hsh, nrm, poly, rect, vcyl
from parts import (UP, barrel, block, books_row, chest, coin, crate, flame, gem, goblet, house, lantern,
                   rocks, rubble, skull, stone_wall, wheel, window)


def broken_column(c, x, base, h=70, r=9, gain=1.0):
    """折れた円柱: 斜めに欠けた上端、足もとに落ちた柱頭。"""
    top = base - h
    pix = []
    for y in range(int(top - 8), int(base)):
        for xx in range(int(x - r), int(x + r) + 1):
            u = (xx + 0.5 - x) / r
            if abs(u) <= 1 and y >= top + u * 8 + (3 if int(xx) % 5 == 0 else 0):
                pix.append((xx, y, nrm(u, 0, math.sqrt(max(0, 1 - u * u)))))
    c.paint(pix, 'stone', gain=gain, tex=lambda px, py: -0.08 if int(px - x + r) % 4 == 0 else 0)
    c.paint(rect(x - r - 4, base - 5, x + r + 5, base, UP), 'stone', gain=gain * 0.95)
    block(c, x + r + 8, base - 10, 22, 10, gain=0.9)


def weeds(c, x, base, n=6, h=16, ramp='foliage'):
    for k in range(n):
        dx = (k - n / 2) * 3
        c.paint(capsule(x + dx, base, x + dx * 1.6 + math.sin(k) * 3, base - h * (0.6 + 0.4 * hsh(k, int(x))), 0.8), ramp, gain=0.9 + 0.1 * (k % 2), outline=False)


def broken_beams(c, x0, x1, top, bottom, w=7):
    """崩れた坑口: 片方の柱が傾き、梁が落ちかけ、岩がふさぐ。"""
    c.paint(rect(x0 + w, top, x1 - w, bottom), 'stone', emit=0.03, outline=False)
    c.paint(capsule(x0 + w / 2, bottom, x0 + w / 2 + 6, top, w / 2), 'wood', gain=0.95)
    c.paint(capsule(x1 - w / 2, bottom, x1 - w / 2 - 22, top + 18, w / 2), 'wood', gain=0.8)
    c.paint(capsule(x0 - 6, top - 2, x1 - 10, top + 26, w / 2), 'wood', gain=1.0)
    rocks(c, [((x0 + x1) / 2 + 6, bottom, (x1 - x0) * 0.8, (bottom - top) * 0.55), ((x0 + x1) / 2 - 20, bottom, 40, 22)], gain=0.85)


def burnt_shelf(c, x0, x1, top, bottom):
    """焼けた書棚: 焦げた板と本、ところどころに残り火。"""
    c.paint(rect(x0, top, x1, bottom), 'wood', gain=0.25, outline=False)
    for i, y in enumerate(range(int(top) + 28, int(bottom), 28)):
        c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.6, 0.8)), 'wood', gain=0.55)
        books_row(c, x0 + 2, x1 - 2 - (30 if i == 1 else 0), y, hmin=8, hmax=18, seed=30 + i, gain=0.28)
    for x in (x0, x1 - 5):
        c.paint(rect(x, top, x + 5, bottom, nrm(-0.3, 0, 0.95)), 'wood', gain=0.5)
    embers(c, [(x0 + 20, top + 50), (x1 - 30, top + 80), (x0 + 50, bottom - 6), (x0 + 110, top + 52), (x1 - 60, bottom - 34)])


def embers(c, pts):
    """残り火（赤い点と小さな炎）。"""
    for x, y in pts:
        flame(c, x, y - 4, 2, 4)
        for k in range(4):
            c.dot(int(x - 6 + hsh(k, int(x)) * 12), int(y + 2 + hsh(int(y), k) * 3), 'R3' if k % 2 else 'G4')


def pages(c, pts):
    """散らばった紙。"""
    for k, (x, y) in enumerate(pts):
        a = hsh(k, 3) * 1.2 - 0.6
        dx, dy = math.cos(a) * 7, math.sin(a) * 3
        c.paint(poly([(x - dx, y - dy - 3), (x + dx, y + dy - 3), (x + dx + 1, y + dy + 3), (x - dx + 1, y - dy + 3)], UP), 'paper', gain=1.0)


def smoke_column(c, x, y, h=60):
    for k in range(10):
        t = k / 9
        c.paint(ellipse(x + math.sin(t * 5) * 8, y - t * h, 6 + t * 10, 5 + t * 6), 'stone', emit=0.32 - t * 0.12, outline=False, dither=True)


def torn_awning(c, x0, x1, y, colors=('red', 'paper')):
    """破れて垂れた日よけ。"""
    stripe = 8
    o = c.obj()
    for px, py, n in poly([(x0, y), (x1, y), (x1 - 10, y + 22), (x0 + 30, y + 10), (x0 + 6, y + 26)], nrm(0, -0.4, 0.9)):
        c.paint([(px, py, n)], colors[int((px - x0) // stripe) % 2], oid=o, gain=0.75)
    for x in (x0 + 4, x1 - 6):
        c.paint(rect(x, y, x + 3, y + 70), 'wood', gain=0.8)


def ruined_house(c, x, base, w=60, h=40, roof='wood', gain=0.8, smoke=False):
    """荒れた家: 屋根に穴、割れた窓、傾いた戸。"""
    house(c, x, base, w, h, roof_h=w * 0.5, roof=roof, gain=gain, windows=[(8, 10, 8, 9, False), (w - 16, 10, 8, 9, False)], timber=True)
    hx, hy = x + w * 0.62, base - h - w * 0.2
    c.paint(poly([(hx - 10, hy), (hx + 8, hy - 4), (hx + 12, hy + 10), (hx - 4, hy + 12)]), 'stone', emit=0.03, outline=False)
    for k in range(4):
        c.paint(capsule(hx - 8 + k * 5, hy - 2, hx - 6 + k * 5, hy + 10, 0.8), 'wood', gain=0.7)
    c.paint(poly([(x + w * 0.4, base), (x + w * 0.4 + 12, base - 2), (x + w * 0.4 + 16, base - 24), (x + w * 0.4 + 4, base - 22)], nrm(-0.3, 0, 1)), 'wood', gain=0.7)
    if smoke:
        smoke_column(c, x + w * 0.6, base - h - w * 0.4)


def shack(c, x, base, w=80, h=50):
    """掘っ立て小屋: 継ぎはぎの板、傾いた片流れの屋根、灯のひとつ窓。"""
    pts = [(x - w / 2, base), (x + w / 2, base), (x + w / 2, base - h * 0.8), (x - w / 2, base - h)]
    o = c.paint(poly(pts, nrm(-0.25, 0, 1)), 'wood', gain=0.9, tex=lambda px, py: -0.12 if int(px - x) % 9 == 0 else (-0.05 if int(py) % 13 == 0 else 0))
    for k, (dx, dy, ww, hh, col) in enumerate(((-30, -30, 14, 10, 'leather'), (12, -18, 16, 12, 'wood'), (-8, -14, 10, 8, 'cloth'))):
        c.paint(rect(x + dx, base + dy, x + dx + ww, base + dy + hh, nrm(-0.2, 0, 1)), col, oid=o, gain=0.8, outline=False)
    c.paint(poly([(x - w / 2 - 8, base - h - 2), (x + w / 2 + 8, base - h * 0.8 - 2), (x + w / 2 + 8, base - h * 0.8 + 4), (x - w / 2 - 8, base - h + 4)], nrm(-0.1, -0.6, 0.8)), 'cloth', gain=0.9,
            tex=lambda px, py: -0.1 if int(px) % 7 == 0 else 0)
    window(c, x + 6, base - h * 0.6, 10, 9, True, oid=o)
    c.paint(rect(x - 20, base - 30, x - 6, base), 'wood', oid=o, gain=0.6, outline=False)


def crypt(c, x, base, w=90, h=70):
    """墓所: 半ば埋まった石の霊廟、下りの階段、扉の奥の灯。"""
    stone_wall(c, int(base - h), int(base), x0=int(x - w / 2), x1=int(x + w / 2), bw=12, bh=7, gain=0.9, seed=31)
    c.paint(poly([(x - w / 2 - 6, base - h), (x + w / 2 + 6, base - h), (x, base - h - 24)], nrm(-0.2, -0.5, 0.8)), 'stone', gain=1.0)
    pts = [(x - 14, base), (x - 14, base - 30)] + arc_points(x, base - 30, 14, math.pi, 2 * math.pi, 10) + [(x + 14, base)]
    c.paint(poly(pts), 'fire', emit=lambda px, py, n: 0.35 - (base - py) / 60, outline=False)
    for k in range(4):
        c.paint(rect(x - 16 - k * 4, base + k * 4, x + 16 + k * 4, base + 4 + k * 4, UP), 'stone', gain=1.0 - k * 0.08)
    skull(c, x, base - h - 10, 0.8)


def gravestones(c, pts, gain=0.8):
    for x, base, w, h in pts:
        pts2 = [(x - w / 2, base), (x - w / 2, base - h + w / 2)] + arc_points(x, base - h + w / 2, w / 2, math.pi, 2 * math.pi, 10) + [(x + w / 2, base)]
        o = c.paint(poly(pts2, nrm(-0.2, -0.1, 1)), 'stone', gain=gain)
        c.paint(rect(x - 1, base - h + 6, x + 1, base - h + h * 0.7), 'stone', oid=o, gain=gain * 0.5, outline=False)
        c.paint(rect(x - w * 0.3, base - h + 11, x + w * 0.3, base - h + 13), 'stone', oid=o, gain=gain * 0.5, outline=False)


def loot_sack(c, x, base):
    """ぶんどり品: 口の開いた袋から、杯・首飾り・金貨・燭台がこぼれる。"""
    c.paint(ellipse(x, base - 28, 36, 28), 'leather', gain=0.95, tex=lambda px, py: -0.1 if (int(px) + int(py) * 2) % 9 == 0 else 0)
    c.paint(ellipse(x - 14, base - 40, 14, 12), 'leather', gain=1.05)
    c.paint(ellipse(x + 6, base - 54, 22, 8), 'leather', gain=1.1)
    c.paint(ellipse(x + 6, base - 56, 18, 6), 'stone', emit=0.05, outline=False)
    goblet(c, x + 4, base - 50, s=1.6)
    for k in range(9):
        coin(c, x + 30 + k * 7 - (k % 3) * 4, base - 2 - (k % 3) * 4, 6, 'gold', stamp=('crown', 'star')[k % 2])
    for px, py in arc_points(x - 40, base - 12, 12, 0.2, math.pi - 0.2, 9):
        c.dot(int(px), int(py), 'G5')
    gem(c, x - 40, base - 2, 4, 'red')
    gem(c, x + 50, base - 22, 4, 'blue')


def skull_wall(c, x0, x1, top, bottom):
    """骨の間: 壁一面に積んだ髑髏と大腿骨の列。"""
    c.paint(rect(x0, top, x1, bottom), 'stone', emit=0.03, outline=False)
    row = 0
    y = top + 8
    while y < bottom:
        if row % 2 == 0:
            for x in range(int(x0) + 8, int(x1), 16):
                skull(c, x, y, 0.75, gain=0.95)
            y += 15
        else:
            for x in range(int(x0), int(x1), 9):
                c.paint(capsule(x, y - 2, x + 8, y + 1, 1.6), 'paper', gain=0.85)
            y += 6
        row += 1


def market_cross(c, x, base):
    """市の十字碑: 段の上に立つ石の柱と十字。"""
    for k in range(3):
        w = 40 - k * 10
        c.paint(rect(x - w / 2, base - 6 - k * 6, x + w / 2, base - k * 6, UP), 'stone', gain=1.05 - k * 0.05)
    c.paint(capsule(x, base - 18, x, base - 84, 4, 3), 'stone', gain=1.0)
    c.paint(capsule(x - 14, base - 72, x + 14, base - 72, 3), 'stone', gain=1.05)


def clutter(c, x, base):
    """がらくた: 壊れた椅子、額縁、古い箱、巻いた絨毯、壺。"""
    c.paint(capsule(x - 70, base - 2, x - 20, base - 10, 6, flat=0.2), 'red', gain=0.8)
    chest(c, x - 30, base, 42, 22, open_=False, band='silver', lock=False)
    frame = (x + 20, base - 70, 44, 56)
    fx, fy, fw, fh = frame
    c.paint(rect(fx, fy, fx + fw, fy + fh, nrm(-0.2, 0, 1)), 'gold', gain=0.8, spec=0.4)
    c.paint(rect(fx + 5, fy + 5, fx + fw - 5, fy + fh - 5), 'green', gain=0.55)
    c.paint(ellipse(fx + fw / 2, fy + fh / 2 + 4, 8, 12), 'leather', gain=0.6, outline=False)
    c.paint(rect(x + 76, base - 34, x + 80, base), 'wood', gain=0.8)
    c.paint(rect(x + 70, base - 18, x + 96, base - 14, UP), 'wood', gain=0.9)
    c.paint(capsule(x + 92, base - 16, x + 102, base - 2, 1.6), 'wood', gain=0.7)
    c.paint(ellipse(x - 80, base - 30, 9, 11), 'copper', gain=0.8, spec=0.4)


def weapon_rack(c, x0, x1, top, base):
    """武具蔵の壁: 槍・剣の立て掛け、盾の列。"""
    c.paint(rect(x0, base - 8, x1, base - 4, UP), 'wood', gain=1.0)
    c.paint(rect(x0, top + 6, x1, top + 10, nrm(0, -0.4, 0.9)), 'wood', gain=1.0)
    n = int((x1 - x0) / 14)
    for k in range(n):
        x = x0 + 7 + k * 14
        if k % 3 == 0:
            c.paint(capsule(x, base - 6, x, top - 6, 1.3), 'wood', gain=0.95)
            c.paint(poly([(x - 3, top - 4), (x + 3, top - 4), (x, top - 16)]), 'silver', spec=0.6)
        else:
            lean = 5
            c.paint(poly([(x - 3, base - 30), (x + 3, base - 30), (x + 2 + lean, top + 16), (x + lean, top + 8), (x - 2 + lean, top + 16)], nrm(-0.4, 0, 0.9)), 'silver', gain=0.7, spec=0.5, shine=6)
            c.paint(capsule(x - 7, base - 30, x + 7, base - 30, 1.8), 'gold', spec=0.5)
            c.paint(capsule(x, base - 30, x - lean * 0.4, base - 14, 1.6), 'leather', gain=0.9)
            c.paint(ellipse(x - lean * 0.45, base - 12, 2.6, 2.6), 'gold', spec=0.6)


def shield_row(c, x0, x1, y, ramps=('red', 'blue', 'green', 'gold')):
    n = int((x1 - x0) / 34)
    for k in range(n):
        x = x0 + 17 + k * 34
        w, h = 14, 20
        pts = [(x - w, y - h * 0.4), (x + w, y - h * 0.4), (x + w, y + 3), (x, y + h * 0.7), (x - w, y + 3)]
        c.paint(poly(pts, lambda px, py, x=x: nrm((px - x) / w * 0.5, 0, 0.85)), 'silver', gain=0.85, spec=0.5)
        c.paint(poly([(x - w + 3, y - h * 0.4 + 3), (x + w - 3, y - h * 0.4 + 3), (x + w - 3, y + 2), (x, y + h * 0.7 - 4), (x - w + 3, y + 2)]), ramps[k % len(ramps)], gain=0.95)


def shrouds(c, x, y, n=3):
    """荷台に積んだ布包み。"""
    for k in range(n):
        c.paint(capsule(x - 34 + k * 4, y - k * 9, x + 34 - k * 3, y - k * 9 - 2, 6), 'paper', gain=0.75 - k * 0.05,
                tex=lambda px, py: -0.08 if int(px) % 9 == 0 else 0)
        c.paint(rect(x - 20 + k * 3, y - k * 9 - 6, x - 18 + k * 3, y - k * 9 + 5), 'leather', gain=0.8, outline=False)


def flat_cart(c, x, base, w=90):
    """荷台だけの車（二輪）と引き棒。"""
    c.paint(rect(x - w / 2, base - 26, x + w / 2, base - 18, nrm(-0.2, -0.3, 0.9)), 'wood', gain=0.95)
    wheel(c, x - w * 0.15, base - 12, r=13)
    c.paint(capsule(x + w / 2, base - 22, x + w / 2 + 34, base - 14, 1.5), 'wood', gain=0.9)
    c.paint(capsule(x + w / 2, base - 18, x + w / 2 + 34, base - 10, 1.5), 'wood', gain=0.8)


def house_fire(c, x, base, w=70, h=44):
    """燃える家: 屋根から上がる炎、窓の火、煙。"""
    house(c, x, base, w, h, roof_h=w * 0.5, roof='wood', gain=0.7, windows=[(10, 10, 9, 10, True), (w - 19, 10, 9, 10, True)])
    for k in range(7):
        flame(c, x + 6 + k * w / 7, base - h - 6 - (k % 3) * 8, 5 + (k % 2) * 2, 12 + (k % 3) * 4)
    smoke_column(c, x + w * 0.5, base - h - 30, h=50)


def grain_sacks(c, x, base):
    for k, (dx, dy, r) in enumerate(((-40, 0, 20), (0, 0, 22), (40, 0, 20), (-20, -26, 18), (20, -28, 18))):
        c.paint(ellipse(x + dx, base - r * 0.9 + dy, r, r * 0.9), 'paper', gain=0.8 + 0.05 * (k % 2),
                tex=lambda px, py: -0.06 if (int(px) * 3 + int(py)) % 11 == 0 else 0)
    for k in range(10):
        c.dot(int(x - 50 + k * 10), int(base - 2), 'G4')


def deer(c, x, base, s=1.0, facing=1):
    """鹿（横から）: 細い脚、白い尻、枝角。"""
    k = s
    f = facing
    X = lambda dx: x + f * -dx * k
    by = base - 30 * k
    for (hx, fx), g in (((-12, -14), 0.75), ((12, 13), 0.8), ((-16, -18), 1.0), ((14, 16), 1.05)):
        c.paint(capsule(X(hx), by + 4 * k, X(fx), base, 2.4 * k, 1.2 * k), 'leather', gain=g)
    c.paint(ellipse(x, by, 18 * k, 9 * k), 'leather', gain=1.0)
    c.paint(ellipse(X(-16), by - 1 * k, 4 * k, 5 * k), 'paper', gain=0.9)
    c.paint(capsule(X(14), by - 2 * k, X(20), by - 18 * k, 4 * k, 3 * k), 'leather', gain=1.05)
    c.paint(capsule(X(20), by - 20 * k, X(28), by - 16 * k, 3.4 * k, 2 * k), 'leather', gain=1.1)
    c.dot(int(X(22)), int(by - 20 * k), 'N0')
    for sgn in (-1, 1):
        ax, ay = X(19 + sgn * 1.5), by - 23 * k
        tips = [(ax, ay), (X(19 + sgn * 6), by - 34 * k), (X(19 + sgn * 4), by - 42 * k)]
        for a, b in zip(tips, tips[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.9 * k), 'paper', gain=0.9)
        c.paint(capsule(tips[1][0], tips[1][1], X(19 + sgn * 11), by - 38 * k, 0.8 * k), 'paper', gain=0.9)


def bedrolls(c, pts):
    for x, y, col in pts:
        c.paint(capsule(x - 18, y, x + 18, y, 5, flat=0.2), col, gain=0.85)
        c.paint(ellipse(x - 18, y, 3, 5, normal=nrm(-0.8, 0, 0.6)), col, gain=0.7)


def offering_altar(c, x, base):
    """供物台: 石の台に、果物の盛り皿、杯、蝋燭、香の煙。"""
    c.paint(rect(x - 54, base - 34, x + 54, base, nrm(-0.2, 0, 1)), 'stone', gain=1.0, tex=lambda px, py: -0.08 if int(py) % 8 == 0 else 0)
    c.paint(rect(x - 60, base - 40, x + 60, base - 34, UP), 'stone', gain=1.15)
    c.paint(rect(x - 54, base - 34, x + 54, base - 22, lambda px, py: nrm(0.3 * math.sin(px / 4), 0, 1)), 'red', gain=0.9)
    c.paint(ellipse(x, base - 42, 22, 5), 'gold', spec=0.6)
    for k, (dx, col) in enumerate(((-12, 'red'), (0, 'green'), (12, 'red'), (-6, 'gold'), (6, 'purple'))):
        c.paint(ellipse(x + dx, base - 48 - (k // 3) * 8, 6, 5.5), col, gain=1.05, spec=0.4)
    goblet(c, x - 38, base - 40, s=1.3)
    for dx in (-52, 52):
        c.paint(vcyl(x + dx, base - 58, base - 40, 3, 1.2), 'paper', gain=1.2, add=0.1)
        flame(c, x + dx, base - 62, 2, 4)
    smoke_column(c, x + 34, base - 46, h=40)


def forger_table(c, x, y):
    """贋金づくりの卓: 鋳型、鉛色の偽金と本物の金貨、拡大鏡、やすり。"""
    c.paint(rect(x - 30, y - 10, x + 10, y + 4, nrm(-0.2, -0.4, 0.9)), 'stone', gain=0.9)
    for k in range(3):
        c.paint(ellipse(x - 20 + k * 12, y - 4, 4.5, 2.5), 'stone', emit=0.08, outline=False)
    for k in range(4):
        coin(c, x + 30 + k * 12, y + 8 - (k % 2) * 4, 6, 'silver' if k % 2 else 'gold', stamp='crown', gain=0.6 if k % 2 else 1.0)
    c.paint(ellipse(x - 60, y + 4, 10, 10), 'gold', spec=0.6)
    c.paint(ellipse(x - 60, y + 4, 7, 7), 'water', emit=0.5, outline=False)
    c.paint(capsule(x - 52, y + 12, x - 42, y + 22, 1.6), 'wood', gain=1.0)
    c.paint(capsule(x + 10, y + 20, x + 60, y + 14, 1.4), 'silver', spec=0.6)


def lute():
    """リュート（胸に抱えて弾く）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = fig.X(0.2, fig.y_waist), fig.y_waist - 0.2 * u
        c.paint(ellipse(x, y, 1.2 * u, 1.0 * u), 'wood', gain=1.2, spec=0.4)
        c.paint(ellipse(x, y, 0.3 * u, 0.3 * u), 'stone', emit=0.05, outline=False)
        nx, ny = x + fig.f * 2.6 * u, y - 1.6 * u
        c.paint(capsule(x + fig.f * 0.8 * u, y - 0.5 * u, nx, ny, 0.2 * u), 'wood', gain=1.0)
        c.paint(capsule(nx, ny, nx + fig.f * 0.4 * u, ny + 0.4 * u, 0.25 * u), 'wood', gain=0.8)
        c.paint(capsule(x - fig.f * 0.6 * u, y + 0.3 * u, nx, ny, 0.3), 'paper', gain=0.9, outline=False)
    return draw


def drum():
    def draw(c, fig, hand):
        u = fig.u
        x, y = fig.X(0.2, fig.y_waist), fig.y_waist + 0.4 * u
        c.paint(vcyl(x, y - 0.6 * u, y + 0.8 * u, 1.2 * u, 0.4 * u), 'red', gain=1.0, tex=lambda px, py: -0.12 if int(px + py) % 4 == 0 else 0)
        c.paint(ellipse(x, y - 0.6 * u, 1.2 * u, 0.4 * u, normal=UP), 'paper', gain=1.1)
        c.paint(capsule(hand[0], hand[1], hand[0] + 0.4 * u, hand[1] - 0.8 * u, 0.1 * u), 'wood', gain=1.1)
    return draw


def bowl():
    """物乞いの木の椀（銅貨入り）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.4 * u, hand[1] - 0.2 * u
        c.paint(ellipse(x, y, 1.0 * u, 0.6 * u, clip=lambda px, py: py >= y - 0.1 * u), 'wood', gain=1.1)
        c.paint(ellipse(x, y - 0.1 * u, 1.0 * u, 0.25 * u), 'wood', gain=0.6)
        coin(c, x - 0.3 * u, y - 0.2 * u, 0.3 * u, 'copper', tilt=0.5, stamp='pip')
    return draw


def big_sword():
    """肩に担いだ両手剣。"""
    def draw(c, fig, hand):
        u = fig.u
        f = fig.f
        x, y = hand
        tip = (x - f * 4.6 * u, y - 2.4 * u)
        c.paint(capsule(x + f * 0.8 * u, y + 0.5 * u, x, y, 0.16 * u), 'leather')
        c.paint(capsule(x - f * 0.2 * u + 0.5 * u * 0, y - 0.6 * u, x + 0.4 * u, y + 0.6 * u, 0.18 * u), 'gold', spec=0.5)
        c.paint(capsule(x, y, tip[0], tip[1], 0.32 * u, 0.12 * u), 'silver', spec=0.8, shine=5)
    return draw


def mirror_stand(c, x, base, h=90):
    """姿見: 金の枠の鏡に、ぼんやり映る別の顔。"""
    c.paint(capsule(x - 14, base, x, base - 10, 1.4), 'gold', gain=0.9)
    c.paint(capsule(x + 14, base, x, base - 10, 1.4), 'gold', gain=0.8)
    c.paint(ellipse(x, base - h / 2 - 8, 24, h / 2), 'gold', spec=0.6)
    c.paint(ellipse(x, base - h / 2 - 8, 19, h / 2 - 5), 'water', emit=lambda px, py, n: 0.35 + (0.2 if px - x < -(py - base) * 0.1 - 6 else 0))
    c.paint(ellipse(x, base - h / 2 - 16, 7, 9), 'purple', emit=0.45, outline=False)


def ransacked(c):
    """荒らされた部屋の床: 倒れた椅子、開いた引き出し、散らばった紙と硬貨。"""
    chest(c, 120, 152, 52, 24, open_=True, fill=None)
    c.paint(capsule(40, 150, 76, 132, 2.2), 'wood', gain=0.9)
    c.paint(rect(50, 136, 76, 140, nrm(0.3, -0.6, 0.7)), 'wood', gain=1.0)
    c.paint(capsule(60, 150, 64, 138, 1.6), 'wood', gain=0.8)
    pages(c, [(30, 156), (90, 158), (178, 150), (196, 156), (150, 146)])
    for k in range(4):
        coin(c, 170 + k * 8, 140 - k * 2, 4, 'silver', stamp='tower')


PROPS = {'lute': lute, 'drum': drum, 'bowl': bowl, 'big_sword': big_sword}


def rain(c, n=120, seed=0):
    """雨の筋（斜めの短い線、決まった位置）。"""
    for k in range(n):
        x = int(hsh(k, seed, 3) * W)
        y = int(hsh(seed, k, 4) * H)
        c.dot(x, y, 'S1')
        c.dot(x - 1, y + 1, 'S1')
        c.dot(x - 2, y + 2, 'N4')


def nails_box(c, x, base):
    c.paint(rect(x - 16, base - 10, x + 16, base, nrm(-0.2, 0, 1)), 'wood', gain=1.0)
    for k in range(12):
        c.dot(int(x - 13 + (k % 6) * 5), int(base - 11 - k // 6), 'S2')


def hinges(c, x, base):
    for k in range(3):
        c.paint(rect(x - 8 + k * 4, base - 14 + k * 2, x + 10 + k * 4, base - 10 + k * 2, nrm(-0.2, -0.4, 0.9)), 'silver', gain=0.9, spec=0.5)


def sword_stuck(c, x, base):
    """地に突き立てた剣。"""
    c.paint(poly([(x - 2, base - 30), (x + 2, base - 30), (x + 2, base - 4), (x, base + 2), (x - 2, base - 4)], nrm(-0.4, 0, 0.9)), 'silver', spec=0.8)
    c.paint(capsule(x - 8, base - 30, x + 8, base - 30, 1.5), 'gold', spec=0.5)
    c.paint(capsule(x, base - 30, x, base - 42, 1.4), 'leather')
    c.paint(ellipse(x, base - 43, 2, 2), 'gold', spec=0.6)


def clutter_cart(c, x, y):
    """荷台に積んだがらくた。"""
    chest(c, x - 40, y + 4, 30, 16, open_=False, band='silver', lock=False)
    c.paint(ellipse(x + 8, y - 4, 9, 11), 'copper', gain=0.9, spec=0.4)
    c.paint(rect(x + 20, y - 26, x + 44, y + 4, nrm(-0.2, 0, 1)), 'gold', gain=0.75, spec=0.3)
    c.paint(rect(x + 24, y - 22, x + 40, y), 'blue', gain=0.6)
    c.paint(capsule(x - 30, y - 10, x + 10, y - 30, 1.4), 'wood', gain=0.9)
    c.paint(ellipse(x - 6, y - 14, 6, 4), 'red', gain=0.8)


def big_rat(c, x, base, s=1.6, facing=1):
    """どぶネズミ（大きめ）: 丸い背、尖った鼻、細い尾。"""
    k, f = s, facing
    c.paint(capsule(x - f * 9 * k, base - 3 * k, x - f * 24 * k, base - 1, 0.8 * k, 0.4 * k), 'red', gain=0.6, outline=False)
    c.paint(ellipse(x, base - 6 * k, 10 * k, 6 * k), 'cloth', gain=0.75)
    c.paint(poly([(x + f * 6 * k, base - 10 * k), (x + f * 16 * k, base - 5 * k), (x + f * 7 * k, base - 2 * k)], nrm(-0.2, -0.4, 0.8)), 'cloth', gain=0.85)
    c.paint(ellipse(x + f * 6 * k, base - 11 * k, 2.4 * k, 2.4 * k), 'red', gain=0.6)
    c.dot(int(x + f * 11 * k), int(base - 7 * k), 'R3')
    c.dot(int(x + f * 16 * k), int(base - 5 * k), 'P3')


def forger_table_big(c, x, y):
    """贋金づくりの卓（大きめ）: 鋳型、偽金と本物、拡大鏡。"""
    c.paint(rect(x - 60, y - 16, x + 4, y + 6, nrm(-0.2, -0.4, 0.9)), 'stone', gain=0.95)
    for i in range(4):
        c.paint(ellipse(x - 48 + i * 15, y - 6, 6, 3.5), 'stone', emit=0.06, outline=False)
        if i < 2:
            c.paint(ellipse(x - 48 + i * 15, y - 6, 4.5, 2.5), 'fire', emit=0.7, outline=False)
    for i in range(5):
        coin(c, x + 20 + i * 15, y + 14 - (i % 2) * 6, 9, 'gold' if i % 2 == 0 else 'silver', stamp='crown', gain=1.0 if i % 2 == 0 else 0.55)
    c.paint(ellipse(x - 86, y + 10, 14, 14), 'gold', spec=0.6)
    c.paint(ellipse(x - 86, y + 10, 10, 10), 'water', emit=0.5, outline=False)
    c.paint(capsule(x - 76, y + 22, x - 62, y + 34, 2.2), 'wood', gain=1.0)
