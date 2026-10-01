"""部品: 背景・灯り・硬貨・建物・道具・家具・動植物。
どれも engine の形を組み合わせ、光は Canvas の Light から受ける（部品が自分で明るさを決めない）。
"""
import math

from engine import (FLAT, H, W, arc_points, capsule, clamp, ellipse, hsh, nrm, poly, rect, vcyl)

UP = nrm(0, -1, 0.45)       # 上を向いた面（卓・床）
FRONT = FLAT


# ================= 背景 =================

def stone_wall(c, y0=0, y1=H, bw=18, bh=9, ramp='stone', gain=1.0, depth=0.0, x0=0, x1=W, seed=0):
    """石積みの壁。石ごとにふくらみ（枕の形）を持たせ、左上の光で上・左の縁が明るく、下・右の縁が暗くなる。
    いくつかの石は角が欠け、ひびが入る（どれが欠けるかは石の位置から決まる）。"""
    def normal(x, y):
        row = (y - y0) // bh
        off = (hsh(row, seed) * 0.5 + (row % 2) * 0.5) * bw
        lx = (x + off) % bw
        ly = (y - y0) % bh
        if ly == 0 or lx < 1:
            return None
        col = int((x + off) // bw)
        t = hsh(row, col, seed)
        if t < 0.1 and lx + ly < 4:  # 欠けた角
            return None
        if 0.1 <= t < 0.17 and abs((lx - 3) - (ly - 1) * 1.6) < 0.6:  # ひび
            return None
        if ly == 1:
            return nrm(0, -0.7, 0.7)
        if lx < 2:
            return nrm(-0.7, 0, 0.7)
        if ly == bh - 1:
            return nrm(0, 0.6, 0.8)
        if lx >= bw - 1:
            return nrm(0.6, 0, 0.8)
        u = (lx / bw - 0.5) * 0.5 + (t - 0.5) * 0.2
        v = (ly / bh - 0.5) * 0.5 + (hsh(col, row, 7 + seed) - 0.5) * 0.2
        return nrm(u, v, 1)

    pix_stone, pix_mortar = [], []
    y0, y1, x0, x1 = int(y0), int(y1), int(x0), int(x1)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            n = normal(x, y)
            (pix_mortar if n is None else pix_stone).append((x, y, n or FLAT))
    o = c.obj()
    c.paint(pix_mortar, ramp, oid=o, gain=gain * 0.5, dither=True, outline=False, depth=depth)
    c.paint(pix_stone, ramp, oid=o, gain=gain, dither=True, outline=False, depth=depth)
    return o


def plank_wall(c, y0=0, y1=H, pw=13, ramp='wood', gain=0.9, depth=0.0, seed=0):
    """縦板の壁。板の境目は暗く、木目は板ごとに決まった波線。"""
    pix, seams = [], []
    for y in range(max(0, y0), min(H, y1)):
        for x in range(W):
            p = x // pw
            lx = x % pw
            if lx == 0:
                seams.append((x, y, FLAT))
                continue
            u = (lx - pw / 2) / (pw / 2)
            n = nrm(u * 0.06, 0, 1)
            pix.append((x, y, n))

    def grain(x, y):
        p = x // pw
        g = (x + 2.2 * math.sin(y / (9 + 3 * hsh(p, seed)) + p * 1.7)) % 5
        knot = math.hypot(x - (p * pw + pw * hsh(p, 3)), (y - 160 * hsh(p, 9))) < 2.2
        return (-0.05 if g < 1 else 0.0) - (0.08 if knot else 0.0)

    o = c.obj()
    c.paint(seams, ramp, oid=o, gain=gain * 0.45, outline=False, depth=depth, dither=True)
    c.paint(pix, ramp, oid=o, gain=gain, tex=grain, dither=True, outline=False, depth=depth)
    return o


def table_top(c, y0, ramp='wood', gain=1.0, x0=0, x1=W, seed=0, edge=True):
    """手前へ伸びる卓の天板。板目は横、奥ほど細い。手前の縁に面取りの照り。"""
    pix = []
    for y in range(int(y0), H):
        for x in range(int(x0), int(x1)):
            pix.append((x, y, UP))
    depthy = lambda y: (y - y0 + 1)

    def tex(x, y):
        t = math.log(depthy(y)) * 3.2
        f = t - math.floor(t)
        if f < 0.12 * (1 + 2 / depthy(y)):
            return -0.12
        g = (x * 0.9 + 4 * math.sin(x / 23 + math.floor(t) * 2.1) + math.floor(t) * 17) % 11
        return -0.04 if g < 1.2 else 0.0
    o = c.paint(pix, ramp, gain=gain, tex=tex, dither=True, outline=False)
    if edge:
        c.paint(rect(x0, y0, x1, y0 + 1, nrm(0, -1, 0.2)), ramp, oid=o, gain=gain * 1.15, outline=False)
    return o


def flag_floor(c, y0, ramp='stone', gain=0.85, depth=0.0):
    """石畳の床。奥へすぼまる目地。"""
    pix = []
    vx = W * 0.45
    for y in range(int(y0), H):
        d = y - y0 + 1
        for x in range(W):
            t = math.log(d) * 2.6
            row = math.floor(t)
            f = t - row
            u = (x - vx) / d * 9 + row * 0.5
            seam = f < 0.1 or (u - math.floor(u)) < 0.08 * (1 + 8 / d)
            n = UP if not seam else FLAT
            pix.append((x, y, n, seam))
    o = c.obj()
    c.paint([(x, y, n) for x, y, n, s in pix if s], ramp, oid=o, gain=gain * 0.45, outline=False, dither=True, depth=depth)
    c.paint([(x, y, n) for x, y, n, s in pix if not s], ramp, oid=o, gain=gain, outline=False, dither=True, depth=depth)
    return o


def ground(c, y0, ramp='foliage', gain=0.8, wave=2.0, seed=0, depth=0.0, tufts=True):
    """草地。上の縁がゆるく波打ち、草の房が決まった間隔で立つ。"""
    pix = []
    for x in range(W):
        top = y0 + wave * math.sin(x / 19 + seed) + wave * 0.6 * math.sin(x / 7.3 + seed * 2)
        for y in range(max(0, int(top)), H):
            pix.append((x, y, nrm(0.15 * math.cos(x / 19 + seed), -1, 0.6)))

    def tex(x, y):
        if not tufts:
            return 0
        k = (x * 3 + (y // 4) * 7) % 13
        return 0.06 if k == 0 and (y % 4) < 2 else (-0.05 if k == 6 else 0)
    return c.paint(pix, ramp, gain=gain, tex=tex, dither=True, outline=False, depth=depth)


def sky(c, y1=H, ramp='night', top=0.05, horizon=0.32, stars=26, moon=None, glow=True, clouds=()):
    """夜空。地平に向かって明るく、月のまわりは光だまり（Light の halo）で明るむ。"""
    pix = [(x, y, FLAT) for y in range(0, int(y1)) for x in range(W)]
    lt = c.light

    def emit(x, y, n):
        t = y / max(1, y1)
        return top + (horizon - top) * t ** 1.6 + (lt.glow(x, y) * 0.9 if glow else 0) + lt.att(x, y) * 0.08
    o = c.paint(pix, ramp, emit=emit, dither=True, outline=False)
    if clouds:
        for k, (cy, cw, ch) in enumerate(clouds):
            cx = W * (0.25 + 0.5 * hsh(k, 11))
            for j in range(5):
                bx = cx + (j - 2) * cw * 0.3
                by = cy + (abs(j - 2) * ch * 0.25)
                c.paint(ellipse(bx, by, cw * 0.28, ch * (0.6 - abs(j - 2) * 0.1)), ramp, oid=o,
                        emit=lambda px, py, n, by=by: emit(px, py, n) + 0.06 + (0.08 if py < by - 1 and n[0] < 0.2 else -0.02), dither=True, outline=False)
    rng = c.rng
    for _ in range(stars):
        x, y = rng.randrange(W), rng.randrange(int(y1 * 0.7))
        if c.light.glow(x, y) < 0.05:
            c.dot(x, y, 'S1' if rng.random() < 0.7 else 'S2')
    return o


def moon(c, x, y, r=11, phase=0.0):
    """月。紙のランプで発光させ、海の模様。phase > 0 で右下から欠ける（0.5 ほどで三日月）。"""
    def emit(px, py, n):
        u, v = (px + 0.5 - x) / r, (py + 0.5 - y) / r
        m = 0.92 - 0.25 * (u + v) * 0.5
        if hsh(int(u * 4 + 9), int(v * 4 + 9)) < 0.25:
            m -= 0.12
        return m
    clip = (lambda px, py: (px + 0.5 - x - r * phase * 1.6) ** 2 + (py + 0.5 - y - r * phase * 0.8) ** 2 > (r * 1.05) ** 2) if phase else None
    o = c.paint(ellipse(x, y, r, r, clip=clip), 'paper', emit=emit, outline=False)
    return o


def hills(c, base, amp, ramp='night', gain=0.5, depth=0.6, seed=0, freq=1.0):
    pix = []
    for x in range(W):
        top = base - amp * (0.6 + 0.4 * math.sin(x / (31 / freq) + seed)) * (0.7 + 0.3 * math.sin(x / (13 / freq) + seed * 3))
        for y in range(max(0, int(top)), H):
            pix.append((x, y, nrm(-0.3 * math.cos(x / (31 / freq) + seed), -0.6, 0.7)))
    return c.paint(pix, ramp, gain=gain, depth=depth, outline=False, dither=True)


def vignette(c, strength=0.55):
    """四隅をなだらかに暗く（画素の明るさに掛ける。段は最後に丸める）。"""
    for y in range(H):
        for x in range(W):
            u = (x + 0.5) / W * 2 - 1
            v = (y + 0.5) / H * 2 - 1
            d = clamp((u * u * 0.7 + v * v * 0.8) - 0.55) / 0.95
            i = y * W + x
            c.L[i] *= 1 - strength * d * d


# ================= 灯り =================

def candle(c, x, base, h=14, r=3, holder=True):
    """燭台の蝋燭。炎は発光、蝋は光源のすぐ下なので上が明るい。"""
    if holder:
        c.paint(ellipse(x, base + 1, r + 5, 2.2), 'gold', gain=1.1)
        c.paint(capsule(x, base - 1, x, base + 1, r + 1), 'gold')
    c.paint(vcyl(x, base - h, base, r, r * 0.4), 'paper', gain=1.25, add=0.15)
    c.paint(capsule(x, base - h - 1, x, base - h - 3, 0.6), 'stone', emit=0.2, outline=False)
    flame(c, x, base - h - 5, 2.6, 5)


def flame(c, x, y, rx=3, ry=6):
    """炎: 外は橙、芯は白金。発光なので光に左右されない。"""
    def emit(px, py, n):
        u, v = (px + 0.5 - x) / rx, (py + 0.5 - y) / ry
        d = math.sqrt(u * u + max(0, v) ** 2 * 1.0 + min(0, v) ** 2 * 0.6)
        return clamp(1.05 - d * 0.75)
    pts = [(x, y - ry * 1.4), (x + rx, y), (x + rx * 0.7, y + ry * 0.6), (x, y + ry * 0.8),
           (x - rx * 0.7, y + ry * 0.6), (x - rx, y)]
    c.paint(poly(pts), 'fire', emit=emit, outline=False)


def lantern(c, x, y, s=1.0, hang=None):
    """吊りランタン。鉄の枠と、内側の灯り。hang: 吊るす鎖の上端の y。"""
    if hang is not None:
        c.paint(rect(x, hang, x + 1, y - 9 * s), 'silver', gain=0.8, outline=False)
    c.paint(capsule(x - 5 * s, y - 8 * s, x + 5 * s, y - 8 * s, 1.5 * s), 'silver')
    c.paint(poly([(x - 4 * s, y - 9 * s), (x + 4 * s, y - 9 * s), (x, y - 13 * s)]), 'silver', gain=0.9)
    o = c.obj()

    def emit(px, py, n):
        return clamp(1.0 - math.hypot(px + 0.5 - x, py + 0.5 - y) / (7 * s))
    c.paint(rect(x - 5 * s, y - 7 * s, x + 5 * s + 1, y + 7 * s), 'fire', oid=o, emit=emit)
    for bx in (x - 5 * s, x - 0.5, x + 5 * s):
        c.paint(rect(bx, y - 7 * s, bx + 1, y + 7 * s), 'silver', gain=0.7, outline=False)
    c.paint(rect(x - 6 * s, y + 7 * s, x + 6 * s + 1, y + 9 * s), 'silver')
    flame(c, x, y + 1, 1.6 * s, 3 * s)


def arched_window(c, x, y, w, h, panes=True, glow='moon'):
    """尖頭アーチの窓。外の月明かりで発光し、桟で区切る。"""
    pts = [(x, y + h), (x, y + w * 0.6)] + arc_points(x + w / 2, y + w * 0.6, w / 2, math.pi, 2 * math.pi, 16) + [(x + w, y + h)]
    c.paint(poly([(px - 2, py - (2 if py < y + w else 0)) for px, py in pts]), 'stone', gain=1.0)
    ramp = 'water' if glow == 'moon' else 'fire'

    def emit(px, py, n):
        return clamp(0.95 - (py - y) / h * 0.45 - abs(px - x - w / 2) / w * 0.3)
    o = c.paint(poly(pts), ramp, emit=emit, dither=True)
    if panes:
        c.paint(rect(x + w / 2, y, x + w / 2 + 1, y + h), 'stone', oid=o, gain=0.5, outline=False)
        for yy in range(int(y + w * 0.6), int(y + h), 7):
            c.paint(rect(x, yy, x + w, yy + 1), 'stone', oid=o, gain=0.5, outline=False)
    return o


def wall_torch(c, x, y):
    c.paint(capsule(x, y + 10, x + 1, y, 1.6, 2.2), 'wood')
    c.paint(capsule(x - 3, y + 2, x + 4, y + 2, 1.2), 'silver')
    flame(c, x + 0.5, y - 5, 3.5, 7)


# ================= 硬貨 =================

METAL = {'gold': 'gold', 'silver': 'silver', 'copper': 'copper'}


def _motif(kind, u, v):
    """硬貨の刻印（-1〜1 の座標で、浮き出ている所が True）。"""
    if kind == 'crown':
        if -0.42 < v < -0.05 and abs(u) < 0.45:
            if v > -0.18:
                return True
            return any(abs(u - p) < 0.09 for p in (-0.36, 0.0, 0.36)) and v > -0.42 + abs(u) * 0.2
        return 0.05 < v < 0.18 and abs(u) < 0.4
    if kind == 'tower':
        if abs(u) < 0.22 and -0.3 < v < 0.38:
            return True
        return -0.45 < v < -0.3 and abs(u) < 0.32 and (int((u + 0.32) / 0.16) % 2 == 0)
    if kind == 'star':
        a = math.atan2(v, u)
        r = math.hypot(u, v)
        return r < 0.2 + 0.25 * max(0, math.cos(a * 5 + math.pi / 2)) ** 3
    if kind == 'pip':
        return math.hypot(u, v) < 0.24
    return False


def coin(c, cx, cy, r, metal='gold', tilt=0.5, stamp='crown', glint=True, rot=0.0, gain=1.0):
    """1 枚の硬貨。上を向いた面（縁が盛り上がり、真ん中に刻印）と、手前に見える厚み。
    面の明るさは光から 1 度だけ求め、縁・溝・刻印はそこからの決まった段の差で描く（小さくても形が崩れない）。"""
    ramp = METAL[metal]
    ry = r * tilt
    t = max(1.5, r * 0.22)
    o = c.obj()
    lt = c.light
    base = min(0.8, lt.lum(cx, cy, nrm(rot * 0.3, -0.85, 0.5), 0.4, 6)) * gain
    edge = list(ellipse(cx, cy + t, r, ry))
    for y in range(int(cy), int(cy + t) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if abs(x + 0.5 - cx) <= r:
                edge.append((x, y, FLAT))

    def edge_l(x, y, n):
        u = (x + 0.5 - cx) / r
        reed = -0.07 if (metal != 'copper' and x % 2 == 0) else 0.0
        return base - 0.3 - 0.12 * u + reed
    c.paint(edge, ramp, oid=o, emit=edge_l)

    def face_l(x, y, n):
        u = (x + 0.5 - cx) / r
        v = (y + 0.5 - cy) / ry
        d = math.sqrt(u * u + v * v)
        side = -(u * 0.7 + v * 0.7)  # 左上が +、右下が -
        if d > 0.8:
            return base + 0.16 * side + (0.04 if side > 0.3 else -0.08)
        if d > 0.68:
            return base - 0.14 - 0.06 * side
        m = _motif(stamp, u / 0.68, v / 0.68)
        f = base + 0.05 * side
        if m:
            if not _motif(stamp, (u - 0.12) / 0.68, (v - 0.2) / 0.68):
                return f + 0.14
            if not _motif(stamp, (u + 0.12) / 0.68, (v + 0.2) / 0.68):
                return f - 0.16
            return f + 0.03
        return f
    c.paint(ellipse(cx, cy, r, ry), ramp, oid=o, emit=face_l)
    if glint and lt.att(cx, cy) > 0.3:
        hi = 'S3' if metal == 'silver' else 'G6'
        gx, gy = int(cx - r * 0.62), int(cy - ry * 0.62)
        c.dot(gx, gy, hi)
        if r >= 7:
            c.dot(gx + 1, gy - 0, hi)
            c.dot(gx + 2, gy - 1 if ry > 5 else gy, hi)
    return o


def coin_stack(c, cx, base, r, n, metal='gold', tilt=0.5, stamp='crown', seed=0, lean=0.0):
    """積んだ硬貨。下から 1 枚ずつ重ね、少しずつずらす。"""
    t = max(1.5, r * 0.22)
    for i in range(n):
        dx = (hsh(i, seed) - 0.5) * 1.6 + lean * i
        coin(c, cx + dx, base - i * (t + 1) - t, r, metal, tilt, stamp, glint=(i == n - 1))


def coin_pile(c, cx, base, w, h, metal='gold', r=7, count=40, seed=0, stamps=('crown', 'star', 'tower')):
    """山盛りの硬貨。山の形の中に奥から手前へ並べる（奥ほど上・小さく見えるように）。"""
    rng = __import__('random').Random(f'pile{seed}{metal}')
    pts = []
    tries = 0
    while len(pts) < count and tries < count * 40:
        tries += 1
        u = rng.uniform(-1, 1)
        top = base - h * math.sqrt(max(0, 1 - u * u))
        y = rng.uniform(top, base)
        x = cx + u * w
        if all(math.hypot(x - px, (y - py) * 2.2) > r * 1.1 for px, py, _ in pts):
            pts.append((x, y, rng.random()))
    pts.sort(key=lambda p: p[1])
    for x, y, q in pts:
        rr = r * (0.85 + 0.3 * q)
        coin(c, x, y, rr, metal, tilt=0.42 + 0.2 * q, stamp=stamps[int(q * 97) % len(stamps)],
             rot=(q - 0.5), glint=q > 0.55)


def gem(c, x, y, r, ramp='red'):
    """カットした宝石。上の面は明るく、下の切子は暗い。照りを 1 点。"""
    o = c.obj()
    top = [(x - r, y), (x - r * 0.5, y - r * 0.6), (x + r * 0.5, y - r * 0.6), (x + r, y)]
    bottom = [(x - r, y), (x + r, y), (x, y + r)]
    c.paint(poly(top, nrm(-0.2, -0.8, 0.6)), ramp, oid=o, gain=1.15, add=0.1)
    c.paint(poly([(x - r, y), (x, y), (x, y + r)], nrm(-0.5, 0.2, 0.8)), ramp, oid=o, gain=1.0)
    c.paint(poly([(x, y), (x + r, y), (x, y + r)], nrm(0.7, 0.3, 0.6)), ramp, oid=o, gain=0.9)
    c.dot(int(x - r * 0.3), int(y - r * 0.35), 'G6')
    return o


# ================= 建物 =================

def window(c, x, y, w, h, lit=True, oid=None, arch=False):
    """窓。灯りがついていれば内から発光（上ほど明るい）、桟で 4 つに区切る。"""
    if arch:
        pts = [(x, y + h), (x, y + w / 2)] + arc_points(x + w / 2, y + w / 2, w / 2, math.pi, 2 * math.pi, 8) + [(x + w, y + h)]
        pix = list(poly(pts))
    else:
        pix = list(rect(x, y, x + w, y + h))
    if lit:
        o = c.paint(pix, 'fire', oid=oid, emit=lambda px, py, n: 0.82 - (py - y) / h * 0.35, outline=False)
    else:
        o = c.paint(pix, 'night', oid=oid, emit=0.12, outline=False)
    if w >= 4:
        c.paint(rect(x + w // 2, y, x + w // 2 + 1, y + h), 'wood', oid=oid, emit=0.2, outline=False)
    if h >= 5:
        c.paint(rect(x, y + h // 2, x + w, y + h // 2 + 1), 'wood', oid=oid, emit=0.2, outline=False)
    return o


def house(c, x, base, w, h, depth=None, roof_h=None, wall='paper', roof='wood', windows=(), door=None,
          timber=True, chimney=None, gain=1.0, dep=0.0, roof_gain=1.0):
    """切妻の家（正面に破風）。正面は光を受け、右の側壁は影、右の屋根は中くらい。
    windows: 正面の左上からの (dx, dy, w, h, 灯り)。"""
    d = depth if depth is not None else w * 0.55
    rh = roof_h if roof_h is not None else w * 0.55
    sk = d * 0.45
    o = c.obj()
    if chimney:
        cx = x + w + d * chimney
        c.paint(rect(cx, base - h - rh - sk * chimney + 2, cx + 4, base - h - sk * chimney), 'stone', oid=o, gain=gain, depth=dep)
    # 側壁と屋根（奥）
    side = [(x + w, base), (x + w + d, base - sk), (x + w + d, base - h - sk), (x + w, base - h)]
    c.paint(poly(side, nrm(0.85, 0, 0.5)), wall, oid=o, gain=gain, depth=dep)
    apex = (x + w / 2, base - h - rh)
    rpts = [apex, (apex[0] + d, apex[1] - sk), (x + w + d + 2, base - h - sk + 2), (x + w + 2, base - h + 2)]
    c.paint(poly(rpts, nrm(0.45, -0.75, 0.5)), roof, oid=o, gain=gain * roof_gain, depth=dep,
            tex=lambda px, py: -0.07 if (px + 2 * py) % 6 == 0 else 0)
    # 正面
    front = [(x, base), (x + w, base), (x + w, base - h), apex, (x, base - h)]
    plaster = (lambda px, py: -0.03 if hsh(int(px) // 5, int(py) // 4, 3) < 0.15 else 0) if wall == 'paper' else (
        lambda px, py: -0.08 if (int(py - base) % 6 == 0 or (int(px - x) + (int(py - base) // 6) * 5) % 10 == 0) else 0)
    fo = c.paint(poly(front, nrm(-0.25, -0.05, 0.95)), wall, gain=gain, depth=dep, tex=plaster)
    if timber:
        for bx in (x, x + w - 1.5):
            c.paint(rect(bx, base - h, bx + 1.5, base), 'wood', oid=fo, gain=gain * 0.9, depth=dep, outline=False)
        c.paint(rect(x, base - h, x + w, base - h + 1.5), 'wood', oid=fo, gain=gain * 0.9, depth=dep, outline=False)
        c.paint(rect(x, base - h * 0.5, x + w, base - h * 0.5 + 1), 'wood', oid=fo, gain=gain * 0.8, depth=dep, outline=False)
        for s in (-1, 1):
            c.paint(capsule(apex[0], apex[1] + 2, apex[0] + s * w * 0.45, base - h, 0.7), 'wood', oid=fo, gain=gain * 0.9, depth=dep, outline=False)
        if w >= 40:
            c.paint(capsule(x + 1, base - h * 0.5, x + w * 0.22, base - 1, 0.7), 'wood', oid=fo, gain=gain * 0.85, depth=dep, outline=False)
            c.paint(capsule(x + w - 1, base - h * 0.5, x + w * 0.78, base - 1, 0.7), 'wood', oid=fo, gain=gain * 0.85, depth=dep, outline=False)
            c.paint(rect(x + w / 2, apex[1] + 4, x + w / 2 + 1.5, base - h), 'wood', oid=fo, gain=gain * 0.85, depth=dep, outline=False)
    # 破風の縁（屋根の厚み）
    c.paint(capsule(apex[0], apex[1] - 1, x - 2, base - h + 2, 1.3), roof, gain=gain * 1.1 * roof_gain, depth=dep)
    c.paint(capsule(apex[0], apex[1] - 1, x + w + 2, base - h + 2, 1.3), roof, gain=gain * 0.9 * roof_gain, depth=dep)
    for wx, wy, ww, wh, lit in windows:
        window(c, x + wx, base - h + wy, ww, wh, lit, oid=fo)
    if door:
        dx, dw, dh = door
        c.paint(rect(x + dx, base - dh, x + dx + dw, base), 'wood', oid=fo, gain=gain * 0.75, depth=dep, outline=False)
    return fo


def tower(c, x, base, w, h, roof='blue', roof_h=None, crenel=False, windows=(), gain=1.0, dep=0.0, ramp='stone'):
    """丸い塔。円柱の陰（左が明るい）に、円錐の屋根か胸壁。"""
    r = w / 2
    cx = x + r
    o = c.paint(vcyl(cx, base - h, base, r, r * 0.3, top=False), ramp, gain=gain, depth=dep,
                tex=lambda px, py: -0.08 if (py % 7 == 0 or (px + (py // 7) * 3) % 9 == 0) else 0)
    if crenel:
        for k in range(-2, 3):
            mx = cx + k * r * 0.45
            c.paint(rect(mx - r * 0.16, base - h - 4, mx + r * 0.16, base - h + 1), ramp, oid=o, gain=gain * 0.95, depth=dep)
    elif roof:
        rh = roof_h or w * 1.2
        pts = [(cx - r - 2, base - h + 1), (cx + r + 2, base - h + 1), (cx, base - h - rh)]
        c.paint(poly(pts, lambda px, py: nrm((px - cx) / (r + 2) * 0.9, -0.4, 0.6)), roof, gain=gain, depth=dep)
    for wx, wy, ww, wh in windows:
        window(c, cx + wx, base - h + wy, ww, wh, True, oid=o, arch=True)
    return o


def crenel_wall(c, x0, x1, top, bottom, merlon=8, gap=6, ramp='stone', gain=1.0, dep=0.0):
    """胸壁つきの石垣（城壁）。凹凸の上面は光を受けて明るい。"""
    o = stone_wall(c, top, bottom, x0=x0, x1=x1, ramp=ramp, gain=gain, depth=dep, bw=14, bh=7, seed=3)
    for i in range(int(x0), int(x1), merlon + gap):
        stone_wall(c, top - 7, top, x0=i, x1=min(int(x1), i + merlon), ramp=ramp, gain=gain, depth=dep, bw=14, bh=7, seed=4)
        c.paint(rect(i, top - 8, min(x1, i + merlon), top - 6, UP), ramp, gain=gain * 1.1, depth=dep)
    c.paint(rect(x0, top - 1, x1, top + 1, UP), ramp, oid=o, gain=gain * 1.05, depth=dep, outline=False)
    return o


# ================= 木・草花 =================

def tree(c, x, base, h, kind='oak', ramp='foliage', gain=1.0, dep=0.0, seed=0):
    import random as _r
    rng = _r.Random(f'tree{seed}{x}')
    if kind == 'pine':
        c.paint(capsule(x, base, x, base - h * 0.3, h * 0.04), 'wood', gain=gain, depth=dep)
        for k in range(4):
            yb = base - h * (0.18 + k * 0.2)
            ww = h * (0.32 - k * 0.06)
            c.paint(poly([(x - ww, yb), (x + ww, yb), (x, yb - h * 0.34)], lambda px, py: nrm((px - x) / ww * 0.7, -0.3, 0.7)), ramp, gain=gain, depth=dep)
        return
    if kind == 'dead':
        def branch(x0, y0, ang, ln, w, d):
            x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
            c.paint(capsule(x0, y0, x1, y1, w, w * 0.65), 'wood' if ramp == 'foliage' else ramp, gain=gain, depth=dep)
            if d > 0:
                branch(x1, y1, ang - 0.5 - rng.random() * 0.3, ln * 0.7, w * 0.65, d - 1)
                branch(x1, y1, ang + 0.45 + rng.random() * 0.3, ln * 0.65, w * 0.65, d - 1)
        branch(x, base, -math.pi / 2, h * 0.38, h * 0.05, 4)
        return
    c.paint(capsule(x, base, x + h * 0.02, base - h * 0.5, h * 0.06, h * 0.04), 'wood', gain=gain, depth=dep)
    blobs = []
    for k in range(9):
        a = rng.random() * math.pi * 2
        rr = rng.random() * 0.22
        blobs.append((x + math.cos(a) * h * rr * 1.2, base - h * 0.66 + math.sin(a) * h * rr * 0.8, h * (0.16 + rng.random() * 0.1)))
    blobs.sort(key=lambda b: -b[0] - b[1])
    o = c.obj()
    for bx, by, br in blobs:
        c.paint(ellipse(bx, by, br, br * 0.85), ramp, oid=o, gain=gain, depth=dep, outline=False,
                tex=lambda px, py: (-0.06 if (px * 2 + py * 3) % 7 == 0 else 0))


def flower(c, x, y, r, ramp='red', stem=6, gain=1.05):
    c.paint(capsule(x, y, x + 0.5, y + stem, 0.6), 'foliage', gain=1.0, outline=False)
    c.paint(ellipse(x + 2, y + stem * 0.55, 1.8, 0.9), 'foliage', outline=False)
    o = c.obj()
    for k in range(5):
        a = k / 5 * math.pi * 2 - math.pi / 2
        c.paint(ellipse(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.45, r * 0.55, r * 0.45), ramp, oid=o, gain=gain)
    c.paint(ellipse(x, y, r * 0.35, r * 0.3), 'gold', oid=o, gain=1.2)


# ================= 家具・道具 =================

def barrel(c, x, base, r, h, lying=False, gain=1.0):
    """樽。胴がふくらみ、たがは鉄。lying=True で横倒し（鏡板が手前）。"""
    if lying:
        o = c.obj()
        for px, py, n in ellipse(x, base - r, h / 2, r):
            pass
        body = list(capsule(x - h / 2 + r * 0.3, base - r, x + h / 2 - r * 0.3, base - r, r, flat=0.0))
        c.paint([(px, py, nrm(n[0] * 0.3, n[1], n[2])) for px, py, n in body], 'wood', oid=o, gain=gain,
                tex=lambda px, py: -0.1 if int(py - base) % 4 == 0 else 0)
        for k in (-0.3, 0.3):
            hx = x + k * h
            c.paint(rect(hx, base - 2 * r + 1, hx + 2, base), 'silver', oid=o, gain=gain * 0.8, outline=False)
        fo = c.paint(ellipse(x - h / 2 + r * 0.3, base - r, r * 0.45, r * 0.98, normal=nrm(-0.8, -0.1, 0.55)), 'wood', gain=gain * 1.05,
                     tex=lambda px, py: -0.12 if int(py) % 4 == 0 else 0)
        c.paint(ellipse(x - h / 2 + r * 0.3, base - r, r * 0.12, r * 0.18), 'silver', oid=fo, gain=gain * 0.6)
        return o
    top = base - h
    pix = []
    for y in range(int(top), int(base)):
        t = (y - top) / h
        rr = r * (0.86 + 0.14 * math.sin(t * math.pi))
        for xx in range(int(x - rr), int(x + rr) + 1):
            u = (xx + 0.5 - x) / rr
            if abs(u) <= 1:
                pix.append((xx, y, nrm(u, (t - 0.5) * 0.4, math.sqrt(max(0, 1 - u * u)))))
    o = c.paint(pix, 'wood', gain=gain, tex=lambda px, py: -0.1 if int(px - x) % 5 == 0 else 0)
    for t in (0.12, 0.85):
        yy = top + h * t
        c.paint([(px, py, n) for px, py, n in pix if yy <= py < yy + 2], 'silver', oid=o, gain=gain * 0.85, outline=False)
    c.paint(ellipse(x, top, r * 0.86, r * 0.28, normal=UP), 'wood', gain=gain * 1.1,
            tex=lambda px, py: -0.12 if int(px) % 4 == 0 else 0)
    return o


def crate(c, x, y, w, h, gain=1.0):
    """木箱。正面と上面、斜めの補強板。"""
    d = w * 0.35
    o = c.paint(poly([(x, y), (x + d, y - d * 0.5), (x + w + d, y - d * 0.5), (x + w, y)], UP), 'wood', gain=gain * 1.1)
    c.paint(poly([(x + w, y), (x + w + d, y - d * 0.5), (x + w + d, y + h - d * 0.5), (x + w, y + h)], nrm(0.8, 0, 0.5)), 'wood', oid=o, gain=gain * 0.8)
    f = c.paint(rect(x, y, x + w, y + h, nrm(-0.2, 0, 1)), 'wood', gain=gain,
                tex=lambda px, py: -0.1 if int(py - y) % 5 == 0 else 0)
    c.paint(rect(x, y, x + 2, y + h), 'wood', oid=f, gain=gain * 1.2, outline=False)
    c.paint(rect(x + w - 2, y, x + w, y + h), 'wood', oid=f, gain=gain * 0.8, outline=False)
    c.paint(capsule(x + 2, y + h - 2, x + w - 2, y + 2, 1.2), 'wood', oid=f, gain=gain * 1.15, outline=False)
    return f


def sack(c, x, base, r, ramp='paper', gain=0.85):
    o = c.paint(ellipse(x, base - r * 0.9, r, r * 0.95), ramp, gain=gain)
    c.paint(poly([(x - r * 0.35, base - r * 1.7), (x + r * 0.35, base - r * 1.7), (x + r * 0.5, base - r * 2.2), (x - r * 0.5, base - r * 2.2)]), ramp, gain=gain)
    c.paint(rect(x - r * 0.4, base - r * 1.8, x + r * 0.4, base - r * 1.65), 'leather', outline=False)
    return o


def table(c, x0, x1, top, legs_to, ramp='wood', cloth=None, gain=1.0, thick=4, front=False):
    """卓。天板（上面は光を受ける）と手前の厚み、脚。cloth: 卓掛けのランプ。"""
    d = 10
    c.paint(capsule(x0 + 4, top + thick, x0 + 4, legs_to, 2.2), ramp, gain=gain * 0.9)
    c.paint(capsule(x1 - 4, top + thick, x1 - 4, legs_to, 2.2), ramp, gain=gain * 0.75)
    o = c.paint(poly([(x0, top), (x0 + d, top - d * 0.6), (x1 + d * 0.3, top - d * 0.6), (x1, top)], UP), ramp, gain=gain,
                tex=lambda px, py: -0.06 if (px + 3 * py) % 11 == 0 else 0)
    c.paint(rect(x0, top, x1, top + thick, nrm(0, 0.2, 1)), ramp, gain=gain * 0.85)
    if front:
        c.paint(rect(x0 + 2, top + thick, x1 - 2, legs_to, nrm(-0.1, 0, 1)), ramp, gain=gain * 0.7,
                tex=lambda px, py: -0.1 if int(px - x0) % 14 == 0 else (-0.04 if int(py - top) % 9 == 0 else 0))
    if cloth:
        pts = [(x0 - 1, top - 1), (x1 + 1, top - 1), (x1 + 2, top + 14), (x0 - 2, top + 14)]
        c.paint(poly(pts, lambda px, py: nrm(0.35 * math.sin(px / 3.5), 0.1, 0.9)), cloth, gain=gain)
        c.paint(rect(x0 - 2, top + 13, x1 + 2, top + 15), 'gold', outline=False, gain=gain)
    return o


def candelabra(c, x, base, h=26, arms=1):
    c.paint(ellipse(x, base, 6, 2), 'gold', spec=0.6)
    c.paint(capsule(x, base, x, base - h, 1.4, 1.0), 'gold', spec=0.6, shine=5)
    tips = [(x, base - h)]
    if arms:
        for s in (-1, 1):
            pts = arc_points(x + s * 5, base - h + 5, 5, math.pi if s > 0 else 0, math.pi / 2 if s > 0 else math.pi / 2, 6)
            c.paint(capsule(x, base - h + 6, x + s * 9, base - h + 6, 1.0), 'gold', spec=0.5)
            c.paint(capsule(x + s * 9, base - h + 6, x + s * 9, base - h + 1, 1.0), 'gold', spec=0.5)
            tips.append((x + s * 9, base - h + 1))
    for tx, ty in tips:
        c.paint(ellipse(tx, ty, 2.6, 1), 'gold')
        c.paint(vcyl(tx, ty - 7, ty - 1, 1.5, 0.6), 'paper', gain=1.3, add=0.15)
        flame(c, tx, ty - 10, 1.8, 3.5)


def goblet(c, x, base, s=1.0, ramp='gold', wine=True):
    c.paint(ellipse(x, base, 4 * s, 1.4 * s), ramp, spec=0.6)
    c.paint(capsule(x, base, x, base - 6 * s, 0.9 * s), ramp, spec=0.6)
    c.paint(ellipse(x, base - 9 * s, 4 * s, 4 * s, clip=lambda px, py: py >= base - 10 * s), ramp, spec=0.8, shine=5)
    c.paint(ellipse(x, base - 10 * s, 4 * s, 1.3 * s), 'red' if wine else ramp, gain=0.75)


def skull(c, x, y, s=1.0, ramp='paper', gain=1.0):
    o = c.paint(ellipse(x, y, 8 * s, 7 * s), ramp, gain=gain)
    c.paint(ellipse(x + 0.5 * s, y + 6 * s, 5 * s, 3.5 * s), ramp, gain=gain * 0.92)
    for ex in (-3.3, 3.3):
        c.paint(ellipse(x + ex * s, y + 1 * s, 2.3 * s, 2.0 * s), 'stone', oid=o, emit=0.05, outline=False)
    c.paint(poly([(x - 0.8 * s, y + 4.2 * s), (x + 0.8 * s, y + 4.2 * s), (x, y + 2.8 * s)]), 'stone', oid=o, emit=0.08, outline=False)
    for tx in range(-3, 4, 2):
        c.paint(rect(x + tx * s, y + 7 * s, x + tx * s + 1, y + 8.5 * s), 'stone', emit=0.08, outline=False)
    return o


def book_closed(c, x, y, w, h, t, ramp='red', gain=1.0):
    """卓に寝かせた本。表紙と、手前の小口（白い頁）。"""
    o = c.paint(poly([(x, y), (x + w, y), (x + w + t, y - t), (x + t, y - t)], UP), ramp, gain=gain)
    c.paint(rect(x, y, x + w, y + h, nrm(0, 0.2, 1)), 'paper', gain=gain * 0.9,
            tex=lambda px, py: -0.06 if int(py) % 2 == 0 else 0)
    c.paint(rect(x, y + h - 1, x + w, y + h + 1), ramp, gain=gain * 0.8)
    return o


def chest(c, x, base, w, h, open_=True, fill='gold', ramp='wood', band='gold', gain=1.0, lock=True):
    """宝箱。正面・右の側面・蓋。open_ なら蓋は後ろへ開き、中から硬貨が盛り上がる。"""
    d = w * 0.28
    sk = d * 0.5
    top = base - h
    if open_:
        lid = [(x + d * 0.2, top - sk), (x + w + d, top - sk), (x + w + d * 0.8, top - sk - h * 0.9), (x + d * 0.1, top - sk - h * 0.85)]
        c.paint(poly(lid, nrm(-0.5, -0.2, 1)), ramp, gain=gain * 0.95,
                tex=lambda px, py: -0.1 if int(px - x) % 9 == 0 else 0)
        c.paint(poly([(x + d * 0.1, top - sk - h * 0.85), (x + w + d * 0.8, top - sk - h * 0.9), (x + w + d * 0.75, top - sk - h * 1.05), (x + d * 0.1, top - sk - h * 1.0)], nrm(-0.2, -0.8, 0.5)), band, gain=gain, spec=0.4)
        inner = [(x, top), (x + d, top - sk), (x + w + d, top - sk), (x + w, top)]
        c.paint(poly(inner, UP), ramp, gain=0.3)
        if fill:
            coin_pile(c, x + w / 2 + d / 2, top + 1, w * 0.52, h * 0.55, fill, r=w * 0.1, count=22, seed=7)
    else:
        c.paint(poly([(x, top), (x + d, top - sk), (x + w + d, top - sk), (x + w, top)], UP), ramp, gain=gain * 1.05,
                tex=lambda px, py: -0.1 if int(px - x) % 8 == 0 else 0)
    c.paint(poly([(x + w, base), (x + w + d, base - sk), (x + w + d, top - sk), (x + w, top)], nrm(0.85, 0, 0.5)), ramp, gain=gain * 0.8)
    f = c.paint(rect(x, top, x + w, base, lambda px, py: nrm(-0.2 + (px - x) / w * 0.5, 0.05, 1)), ramp, gain=gain * 0.85,
                tex=lambda px, py: -0.1 if int(py - top) % 7 == 0 else (-0.04 if int(px - x) % 11 == 0 else 0))
    for bx in (x + w * 0.12, x + w * 0.82):
        c.paint(rect(bx, top, bx + w * 0.07, base), band, oid=f, gain=gain * 0.95, spec=0.4, outline=False)
    c.paint(rect(x, top, x + w, top + 2), band, oid=f, gain=gain, spec=0.4, outline=False)
    c.paint(rect(x, base - 2, x + w, base), band, oid=f, gain=gain * 0.8, outline=False)
    if lock:
        lx = x + w / 2
        c.paint(rect(lx - 3, top + 1, lx + 4, top + 10), band, gain=gain * 1.05, spec=0.6)
        c.paint(rect(lx, top + 4, lx + 1, top + 8), 'stone', emit=0.03, outline=False)
    return f


def castle(c, x, base, s=1.0, roof='blue', banner='red'):
    """丘の上の城。中央の天守、左右の丸塔、城壁と門。窓に灯り。"""
    k = s
    tower(c, x - 52 * k, base - 6, 16 * k, 46 * k, roof=roof, gain=0.8, windows=[(-2, 14, 4, 6)])
    tower(c, x + 38 * k, base - 6, 16 * k, 50 * k, roof=roof, gain=0.7, windows=[(-2, 16, 4, 6)])
    # 天守（正面＋右の側面）
    kx0, kx1, ktop = x - 22 * k, x + 18 * k, base - 72 * k
    c.paint(poly([(kx1, base - 10), (kx1 + 10 * k, base - 15), (kx1 + 10 * k, ktop - 5), (kx1, ktop)], nrm(0.85, 0, 0.5)), 'stone', gain=0.85,
            tex=lambda px, py: -0.08 if int(py) % 7 == 0 else 0)
    keep = P_stone_rect(c, kx0, ktop, kx1, base - 10)
    for i in range(int(kx0), int(kx1), 8):
        c.paint(rect(i, ktop - 5, i + 5, ktop + 1, nrm(-0.2, -0.3, 0.9)), 'stone', gain=1.0)
    for wx, wy in ((kx0 + 7, ktop + 12), (kx0 + 25, ktop + 12), (kx0 + 16, ktop + 30)):
        window(c, wx, wy, 5, 8, True, oid=keep, arch=True)
    tower(c, x - 30 * k, base - 2, 14 * k, 38 * k, roof=roof, gain=0.95, windows=[(-2, 12, 4, 6)])
    tower(c, x + 24 * k, base - 2, 14 * k, 34 * k, roof=roof, gain=0.8)
    # 天守の上の旗
    c.paint(rect(x - 2, ktop - 26, x - 1, ktop - 5), 'wood', gain=0.9)
    c.paint(poly([(x - 1, ktop - 26), (x + 13, ktop - 23), (x - 1, ktop - 19)], nrm(-0.3, 0, 1)), banner, gain=1.0)
    # 城壁と門
    crenel_wall(c, x - 46 * k, x + 40 * k, base - 20, base + 2, merlon=6, gap=4, gain=0.9)
    gx = x - 4
    c.paint(poly([(gx - 8, base + 2), (gx - 8, base - 9)] + arc_points(gx, base - 9, 8, math.pi, 2 * math.pi, 8) + [(gx + 8, base + 2)]),
            'fire', emit=lambda px, py, n: 0.55 - (py - base + 17) * 0.015, outline=False)
    for k2 in range(-6, 7, 3):
        c.paint(rect(gx + k2, base - 16, gx + k2 + 1, base + 2), 'stone', emit=0.08, outline=False)


def P_stone_rect(c, x0, y0, x1, y1, gain=1.0):
    return stone_wall(c, int(y0), int(y1), x0=int(x0), x1=int(x1), bw=10, bh=6, gain=gain, seed=5)


def grave(c, x, base, w=34, h=46):
    """墓石。上が丸い石板、ひび、右の厚み。"""
    d = 6
    pts = [(x - w / 2, base), (x - w / 2, base - h + w / 2)] + arc_points(x, base - h + w / 2, w / 2, math.pi, 2 * math.pi, 14) + [(x + w / 2, base)]
    c.paint(poly([(px + d, py - d * 0.5) for px, py in pts], nrm(0.8, -0.1, 0.5)), 'stone', gain=0.6)
    o = c.paint(poly(pts, lambda px, py: nrm(-0.15, -0.1, 1)), 'stone', gain=1.0,
                tex=lambda px, py: (-0.05 if (px * 7 + py * 3) % 17 == 0 else 0))
    crack = [(x + 4, base - h + 6), (x + 1, base - h + 14), (x + 5, base - h + 20), (x + 2, base - h + 30)]
    for a, b in zip(crack, crack[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'stone', oid=o, emit=0.05, outline=False)
    c.paint(rect(x - 8, base - h + 22, x + 8, base - h + 24), 'stone', oid=o, gain=0.45, outline=False)
    c.paint(rect(x - 1, base - h + 14, x + 1, base - h + 36), 'stone', oid=o, gain=0.45, outline=False)


def wisp_candle(c, x, base):
    """災いの灯: 溶けた蝋燭と紫の炎。"""
    c.paint(vcyl(x, base - 12, base, 4, 1.4), 'paper', gain=0.9)
    c.paint(capsule(x + 3, base - 11, x + 4, base - 5, 1.1), 'paper', gain=0.8)

    def emit(px, py, n):
        return max(0.0, 1.05 - math.hypot(px + 0.5 - x, (py + 0.5 - base + 19) * 0.6) / 5)
    pts = [(x, base - 32), (x + 4, base - 20), (x + 2, base - 14), (x - 2, base - 14), (x - 4, base - 20)]
    c.paint(poly(pts), 'purple', emit=emit, outline=False)


def wisps(c, pts):
    """漂う紫の煙。決まった波の帯を、段を落としながら重ねる。"""
    for i, (x, y) in enumerate(pts):
        for k in range(14):
            t = k / 13
            px = x + math.sin(t * 5 + i) * 7 - t * 20
            py = y + t * 26
            c.paint(ellipse(px, py, 7 - t * 4, 3.5 - t * 1.5), 'purple', emit=0.5 - t * 0.3, outline=False, dither=True)


# ================= 室内の小物 =================

def shelf(c, x0, x1, y, gain=0.9):
    c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.6, 0.8)), 'wood', gain=gain)
    for bx in (x0 + 4, x1 - 6):
        c.paint(poly([(bx, y + 3), (bx + 2, y + 3), (bx + 2, y + 10), (bx, y + 6)]), 'wood', gain=gain * 0.8)


def books_row(c, x0, x1, base, hmin=12, hmax=20, seed=0, gain=1.0, lean_last=True):
    """棚に並んだ本の背。色は宝石のランプを順に、高さは決まった揺らぎ。"""
    ramps = ['red', 'blue', 'green', 'leather', 'purple', 'red', 'wood', 'blue']
    x = x0
    i = 0
    while x < x1 - 3:
        w = 3 + int(hsh(i, seed) * 3)
        h = hmin + int(hsh(seed, i, 3) * (hmax - hmin))
        r = ramps[int(hsh(i, seed, 5) * len(ramps))]
        o = c.paint(rect(x, base - h, min(x + w, x1), base, lambda px, py: nrm(((px - x) / max(1, w) - 0.5) * 1.2, 0, 0.8)), r, gain=gain)
        if h > 13:
            c.paint(rect(x, base - h + 3, min(x + w, x1), base - h + 4), 'gold', oid=o, gain=gain * 0.9, outline=False)
            c.paint(rect(x, base - 5, min(x + w, x1), base - 4), 'gold', oid=o, gain=gain * 0.8, outline=False)
        x += w
        i += 1


def bottle(c, x, base, h=14, r=4, ramp='green', glow=False):
    """ガラス瓶。中の液は色のランプ、ガラスの照りは白い 1 本線。"""
    body = list(ellipse(x, base - r, r, r)) + list(rect(x - r, base - h * 0.55, x + r + 1, base - r))
    if glow:
        o = c.paint(body, ramp, emit=lambda px, py, n: 0.9 - (py - (base - h * 0.55)) / h * 0.4 - max(0, px - x) * 0.04)
    else:
        o = c.paint(body, ramp, gain=1.0, spec=0.6, shine=6)
    c.paint(rect(x - r * 0.35, base - h, x + r * 0.35 + 1, base - h * 0.55), 'silver', gain=0.75)
    c.paint(rect(x - r * 0.45, base - h - 2, x + r * 0.45 + 1, base - h), 'wood', gain=0.9)
    c.paint(rect(x - r + 1, base - h * 0.5, x - r + 2, base - r), 'paper', oid=o, emit=0.9, outline=False)
    return o


def flask(c, x, y, r, ramp='green', neck=10):
    """丸底フラスコ（発光する液）。"""
    def emit(px, py, n):
        if py < y - r * 0.15:
            return 0.25
        return 0.95 - math.hypot(px - x + r * 0.3, py - y) / r * 0.45
    o = c.paint(ellipse(x, y, r, r), ramp, emit=emit)
    c.paint(rect(x - 2, y - r - neck, x + 3, y - r + 2), 'silver', gain=0.8)
    c.paint(ellipse(x - r * 0.45, y - r * 0.4, 1.5, 2.5), 'silver', oid=o, emit=1.0, outline=False)
    for k in range(4):
        bx, by = x - r * 0.3 + hsh(k, 1) * r * 0.8, y + r * 0.2 - k * r * 0.18
        c.paint(ellipse(bx, by, 1.3, 1.3), ramp, oid=o, emit=1.0, outline=False)
    return o


def burner(c, x, base):
    c.paint(rect(x - 6, base - 7, x + 7, base, nrm(-0.3, 0, 1)), 'silver', gain=0.7, spec=0.4)
    c.paint(rect(x - 7, base - 8, x + 8, base - 6), 'silver', gain=0.9)
    flame(c, x, base - 13, 3, 5)


def anvil(c, x, base, s=1.0):
    """金床（横から）: 台座・くびれ・天板、左へ細く伸びる角。天板の上面は光を受ける。"""
    k = s
    c.paint(poly([(x - 16 * k, base), (x + 18 * k, base), (x + 12 * k, base - 6 * k), (x - 10 * k, base - 6 * k)], nrm(-0.2, -0.2, 1)), 'silver', gain=0.7)
    c.paint(poly([(x - 8 * k, base - 6 * k), (x + 10 * k, base - 6 * k), (x + 7 * k, base - 15 * k), (x - 5 * k, base - 15 * k)], nrm(-0.2, 0, 1)), 'silver', gain=0.62)
    body = [(x - 12 * k, base - 15 * k), (x + 24 * k, base - 15 * k), (x + 24 * k, base - 24 * k), (x - 12 * k, base - 24 * k),
            (x - 22 * k, base - 23 * k), (x - 34 * k, base - 24.5 * k), (x - 22 * k, base - 19 * k)]
    o = c.paint(poly(body, nrm(-0.2, 0.1, 1)), 'silver', gain=0.8, spec=0.3)
    c.paint(poly([(x - 34 * k, base - 24.5 * k), (x - 12 * k, base - 26.5 * k), (x + 24 * k, base - 26.5 * k), (x + 24 * k, base - 24 * k), (x - 12 * k, base - 24 * k)], UP),
            'silver', oid=o, gain=1.05, spec=0.8, shine=4)
    c.paint(rect(x + 14 * k, base - 25 * k, x + 17 * k, base - 22 * k), 'stone', oid=o, emit=0.08, outline=False)


def forge(c, x, y, w, h):
    """炉: 煉瓦の口の中で火が燃え、口のまわりが照らされる。"""
    stone_wall(c, y, y + h, x0=x, x1=x + w, bw=8, bh=5, ramp='red', gain=0.9, seed=9)
    mx, my, mw, mh = x + w * 0.18, y + h * 0.35, w * 0.64, h * 0.5
    pts = [(mx, my + mh), (mx, my + mw * 0.4)] + arc_points(mx + mw / 2, my + mw * 0.4, mw / 2, math.pi, 2 * math.pi, 12) + [(mx + mw, my + mh)]

    def emit(px, py, n):
        return 1.0 - (my + mh - py) / mh * 0.55 + (0.12 if (px * 3 + py) % 7 < 2 and py > my + mh * 0.5 else 0)
    c.paint(poly(pts), 'fire', emit=emit)
    for k in range(5):
        flame(c, mx + mw * (0.15 + k * 0.17), my + mh * 0.72, 2.5, 6 + 3 * hsh(k, 4))
    c.paint(rect(x - 3, y + h, x + w + 3, y + h + 4, UP), 'stone', gain=1.0)
    hood = [(x - 6, y), (x + w + 6, y), (x + w * 0.7, y - 24), (x + w * 0.3, y - 24)]
    c.paint(poly(hood, nrm(-0.2, 0.2, 1)), 'stone', gain=0.6)


def sparks(c, pts):
    for x, y in pts:
        c.dot(x, y, 'G5')
        c.dot(x + 1, y + 1, 'R3')


def tool_rack(c, x0, x1, y, tools=('saw', 'hammer', 'pliers', 'axe', 'saw2'), s=1.0):
    """壁の道具掛け: 横木に、のこぎり・金槌・やっとこを掛ける。"""
    c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.5, 0.85)), 'wood', gain=0.9)
    step = (x1 - x0) / (len(tools) + 0.5)
    for i, t in enumerate(tools):
        tx = x0 + step * (i + 0.75)
        c.dot(int(tx), int(y + 1 * s), 'G4')
        if t.startswith('saw'):
            L = (26 if t == 'saw' else 20) * s
            c.paint(poly([(tx - 3 * s, y + 8 * s), (tx + 4 * s, y + 8 * s), (tx + 6 * s, y + 8 * s + L), (tx - 4 * s, y + 8 * s + L)], nrm(-0.3, 0, 0.9)), 'silver', gain=0.95, spec=0.5)
            for k in range(int(L / 2)):
                c.dot(int(tx + 4 * s + k * 2 * s / L * 2), int(y + 9 * s + k * 2), 'N2')
            c.paint(rect(tx - 4 * s, y + 2 * s, tx + 5 * s, y + 9 * s), 'wood', gain=1.0)
        elif t == 'hammer':
            c.paint(capsule(tx, y + 3 * s, tx, y + 26 * s, 1.4 * s), 'wood')
            c.paint(capsule(tx - 5 * s, y + 24 * s, tx + 5 * s, y + 24 * s, 2.6 * s, flat=0.4), 'silver', spec=0.6)
        elif t == 'pliers':
            c.paint(capsule(tx - 1 * s, y + 3 * s, tx - 3 * s, y + 22 * s, 1.0 * s), 'silver', spec=0.5)
            c.paint(capsule(tx + 1 * s, y + 3 * s, tx + 3 * s, y + 22 * s, 1.0 * s), 'silver', gain=0.85)
        elif t == 'axe':
            c.paint(capsule(tx, y + 3 * s, tx, y + 28 * s, 1.3 * s), 'wood')
            c.paint(poly([(tx, y + 5 * s), (tx + 8 * s, y + 3 * s), (tx + 9 * s, y + 13 * s), (tx, y + 11 * s)], nrm(-0.3, -0.3, 0.9)), 'silver', spec=0.6)
        elif t == 'tongs':
            c.paint(capsule(tx - 1 * s, y + 3 * s, tx - 4 * s, y + 30 * s, 1.0 * s), 'silver', gain=0.85, spec=0.5)
            c.paint(capsule(tx + 1 * s, y + 3 * s, tx + 4 * s, y + 30 * s, 1.0 * s), 'silver', gain=0.75)
        elif t == 'coil':
            c.paint(ellipse(tx, y + 12 * s, 7 * s, 8 * s), 'leather', gain=0.9)
            c.paint(ellipse(tx, y + 12 * s, 3.5 * s, 4 * s), 'stone', emit=0.06, outline=False)


def plank(c, x0, y0, x1, y1, w=3):
    c.paint(capsule(x0, y0, x1, y1, w, flat=0.5), 'wood', gain=1.0, tex=lambda px, py: -0.06 if (px + py) % 5 == 0 else 0)


def balance(c, x, base, h=40, tilt=4, left='copper', right='gold', s=1.0):
    """天秤。片方に銅貨、もう片方に金貨。tilt: 傾き（左が下がる）。"""
    c.paint(ellipse(x, base, 12 * s, 3.5 * s), 'gold', spec=0.5)
    c.paint(capsule(x, base, x, base - h, 1.6 * s), 'gold', spec=0.6, shine=5)
    c.paint(ellipse(x, base - h - 2 * s, 2.6 * s, 2.6 * s), 'gold', spec=0.7)
    bx0, by0, bx1, by1 = x - 26 * s, base - h + tilt, x + 26 * s, base - h - tilt
    c.paint(capsule(bx0, by0, bx1, by1, 1.3 * s), 'gold', spec=0.6)
    for px, py, metal, n in ((bx0, by0, left, 4), (bx1, by1, right, 2)):
        for sg in (-1, 1):
            c.paint(capsule(px, py, px + sg * 8 * s, py + 17 * s, 0.6), 'gold', gain=0.9, outline=False)
        for k in range(n):
            coin(c, px + (k % 2) * 2 - 1, py + 15 * s - k * 2.4 * s, 5.5 * s, metal, tilt=0.45, stamp='pip', glint=(k == n - 1))
        c.paint(ellipse(px, py + 18 * s, 10 * s, 3 * s, clip=lambda qx, qy, py=py: qy >= py + 17.5 * s), 'gold', spec=0.6)


def awning(c, x0, x1, y, depth=12, colors=('red', 'paper'), stripe=8, scallop=True):
    """縞の日よけ。手前に向かって垂れ、縁は波形。"""
    pts = [(x0, y), (x1, y), (x1 + 4, y + depth), (x0 - 4, y + depth)]
    o = c.obj()
    for px, py, n in poly(pts, nrm(0, -0.5, 0.85)):
        t = (px - x0 + (py - y) * 0.3) // stripe
        c.paint([(px, py, n)], colors[int(t) % 2], oid=o, gain=1.0)
    if scallop:
        for sx in range(int(x0 - 4), int(x1 + 4), stripe):
            col = colors[int((sx - x0 + depth * 0.3) // stripe) % 2]
            c.paint(ellipse(sx + stripe / 2, y + depth, stripe / 2, 3, clip=lambda qx, qy: qy >= y + depth), col, oid=o, gain=0.85)
    return o


def paper_lantern(c, x, y, r=6, ramp='red', glow=True, string=None):
    """提灯（紙の丸い灯籠）。横の骨が段の線になり、内から光る。"""
    if string is not None:
        c.paint(rect(x, string, x + 1, y - r * 1.2), 'wood', gain=0.6, outline=False)
    c.paint(rect(x - r * 0.5, y - r * 1.25, x + r * 0.5 + 1, y - r * 0.95), 'wood', gain=0.8)
    c.paint(rect(x - r * 0.5, y + r * 0.95, x + r * 0.5 + 1, y + r * 1.25), 'wood', gain=0.8)

    def emit(px, py, n):
        rib = -0.18 if int(py - y + r) % max(2, int(r / 2.5)) == 0 else 0
        return 0.92 - math.hypot(px + 0.5 - x + r * 0.25, (py + 0.5 - y) * 0.9) / r * 0.42 + rib
    if glow:
        return c.paint(ellipse(x, y, r, r * 1.05), ramp, emit=emit)
    return c.paint(ellipse(x, y, r, r * 1.05), ramp)


def basket(c, x, base, w, h, fill='red', n=6, kind='apple'):
    """編みかご。中に果物・パン・魚。"""
    o = c.obj()
    for k in range(n):
        fx = x - w * 0.38 + (k % 4) * w * 0.25 + (k // 4) * w * 0.12
        fy = base - h + 1 - (k // 4) * 4
        if kind == 'apple':
            c.paint(ellipse(fx, fy, 4, 3.6), fill, spec=0.5)
            c.dot(int(fx), int(fy - 4), 'G1')
        elif kind == 'bread':
            c.paint(ellipse(fx, fy, 6, 3.3), 'wood', gain=1.4, spec=0.2)
            c.paint(rect(fx - 1, fy - 2, fx, fy + 1), 'wood', gain=0.8, outline=False)
        elif kind == 'fish':
            c.paint(ellipse(fx, fy, 6, 2.2), 'silver', spec=0.6)
            c.paint(poly([(fx + 5, fy), (fx + 9, fy - 3), (fx + 9, fy + 3)]), 'silver', gain=0.8)
        elif kind == 'cabbage':
            c.paint(ellipse(fx, fy, 5, 4.5), 'green', gain=1.05)
    pts = [(x - w / 2, base - h), (x + w / 2, base - h), (x + w * 0.42, base), (x - w * 0.42, base)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 1.2, 0, 0.8)), 'wood', gain=1.25,
            tex=lambda px, py: -0.1 if (px + (py // 3) * 2) % 4 == 0 or py % 3 == 0 else 0)
    c.paint(rect(x - w / 2 - 1, base - h - 1, x + w / 2 + 1, base - h + 2), 'wood', gain=1.3)
    return o


def rock_wall(c, y0=0, y1=H, ramp='stone', gain=0.8, seed=0, cell=16):
    """岩肌（坑道・洞窟）。大きさの違う岩の塊が、それぞれ左上を向いた面を持つ。"""
    pix = []
    for y in range(int(y0), int(y1)):
        for x in range(W):
            gx, gy = x / cell, y / (cell * 0.7)
            best, best2, bi = 9, 9, None
            ix, iy = int(gx), int(gy)
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    cx_, cy_ = ix + ox, iy + oy
                    px_ = cx_ + hsh(cx_, cy_, seed)
                    py_ = cy_ + hsh(cy_, cx_, seed + 1)
                    d = (gx - px_) ** 2 + (gy - py_) ** 2
                    if d < best:
                        best2, best, bi = best, d, (cx_, cy_, px_, py_)
                    elif d < best2:
                        best2 = d
            cx_, cy_, px_, py_ = bi
            edge = math.sqrt(best2) - math.sqrt(best)
            if edge < 0.07:
                pix.append((x, y, None))
                continue
            dx, dy = gx - px_, gy - py_
            n = nrm(dx * 1.3 + (hsh(cx_, cy_, 9) - 0.5) * 0.5, dy * 1.3, 0.8)
            pix.append((x, y, n))
    o = c.obj()
    c.paint([(x, y, FLAT) for x, y, n in pix if n is None], ramp, oid=o, gain=gain * 0.35, dither=True, outline=False)
    c.paint([(x, y, n) for x, y, n in pix if n is not None], ramp, oid=o, gain=gain, dither=True, outline=False)
    return o


def beam_frame(c, x0, x1, top, bottom, w=6):
    """坑道の支え木（左右の柱と梁）。"""
    for x in (x0, x1 - w):
        c.paint(rect(x, top, x + w, bottom, lambda px, py, x=x: nrm(((px - x) / w - 0.5) * 1.4, 0, 0.8)), 'wood', gain=0.95,
                tex=lambda px, py: -0.07 if (py + px * 3) % 9 == 0 else 0)
    c.paint(rect(x0 - 4, top - w, x1 + 4, top, lambda px, py: nrm(0, ((py - top + w) / w - 0.5) * 1.4, 0.8)), 'wood', gain=1.0,
            tex=lambda px, py: -0.07 if (px + py * 3) % 11 == 0 else 0)


def cart(c, x, base, w=44, h=20, ore='gold'):
    """鉱車。鉄の箱に鉱石が盛られ、金の筋が光る。"""
    for wx in (x - w * 0.3, x + w * 0.3):
        c.paint(ellipse(wx, base - 5, 5.5, 5.5), 'silver', gain=0.7, spec=0.4)
        c.paint(ellipse(wx, base - 5, 2, 2), 'silver', gain=1.0)
    top = base - 8 - h
    pts = [(x - w / 2 - 3, top), (x + w / 2 + 3, top), (x + w / 2, base - 8), (x - w / 2, base - 8)]
    c.paint(poly(pts, nrm(-0.25, 0.05, 1)), 'silver', gain=0.8, spec=0.3,
            tex=lambda px, py: -0.12 if int(px - x) % 11 == 0 else 0)
    for k in range(9):
        rx = x - w * 0.42 + k * w * 0.105
        ry = top - 3 - 4 * math.sin(k / 8 * math.pi)
        c.paint(ellipse(rx, ry, 6, 4.5), 'stone', gain=1.0)
        if k % 3 == 1:
            c.dot(int(rx - 1), int(ry - 1), 'G5')
            c.dot(int(rx), int(ry - 1), 'G4')
    c.paint(rect(x - w / 2 - 4, top - 1, x + w / 2 + 4, top + 2), 'silver', gain=1.0, spec=0.4)


def pickaxe(c, x, y, ang=-60, length=38):
    a = math.radians(ang)
    x1, y1 = x + math.cos(a) * length, y + math.sin(a) * length
    c.paint(capsule(x, y, x1, y1, 1.7), 'wood')
    px, py = -math.sin(a), math.cos(a)
    pts = [(x1 + px * 14, y1 + py * 14 + 3), (x1 + px * 4, y1 + py * 4 - 2), (x1 - px * 4, y1 - py * 4 - 2), (x1 - px * 14, y1 - py * 14 + 3),
           (x1 - px * 4, y1 - py * 4 + 1), (x1 + px * 4, y1 + py * 4 + 1)]
    c.paint(poly(pts, nrm(-0.3, -0.6, 0.7)), 'silver', spec=0.6)


def vein(c, pts, ramp='gold'):
    """岩に走る金の筋。"""
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.3), ramp, gain=1.25, spec=0.7, shine=4, outline=False)
    for x, y in pts[1:-1]:
        c.dot(int(x), int(y) - 1, 'G6')


def water(c, y0, ramp='water', gain=0.8, ripple=5):
    """堀の水面。横の波の帯と、光の映り込み（光だまりの真下が明るい）。"""
    pix = [(x, y, FLAT) for y in range(int(y0), H) for x in range(W)]
    lt = c.light

    def emit(x, y, n):
        band = math.sin(y * 1.3 + math.sin(x / 9 + y) * 1.5)
        refl = lt.att(lt.cx + (x - lt.cx) * 1.6, y0 - (y - y0) * 0.6) * 0.5
        g = lt.glow(x, y0 - (y - y0)) * 0.9
        return (0.16 + refl + g) * gain + (0.08 if band > 0.75 else -0.04 if band < -0.6 else 0)
    return c.paint(pix, ramp, emit=emit, dither=True, outline=False)


def drawbridge_gate(c, x, base, w=40, h=50):
    """城門: 石のアーチに落とし格子、手前に跳ね橋。"""
    pts = [(x - w / 2, base), (x - w / 2, base - h + w / 2)] + arc_points(x, base - h + w / 2, w / 2, math.pi, 2 * math.pi, 12) + [(x + w / 2, base)]
    c.paint(poly([(px + (3 if px > x else -3), py - 3) for px, py in pts]), 'stone', gain=1.15)
    c.paint(poly(pts), 'stone', emit=0.05)
    inner = [(x - w / 2 + 3, base), (x - w / 2 + 3, base - h + w / 2)] + arc_points(x, base - h + w / 2, w / 2 - 3, math.pi, 2 * math.pi, 12) + [(x + w / 2 - 3, base)]
    o = c.paint(poly(inner), 'fire', emit=lambda px, py, n: 0.45 - (base - py) / h * 0.3)
    for gx in range(int(x - w / 2 + 5), int(x + w / 2 - 3), 5):
        c.paint(rect(gx, base - h, gx + 2, base - 4), 'silver', oid=o, gain=0.6, outline=False)
    for gy in range(int(base - h + 8), int(base - 4), 7):
        c.paint(rect(x - w / 2 + 3, gy, x + w / 2 - 3, gy + 1), 'silver', oid=o, gain=0.5, outline=False)


def well(c, x, base, r=16):
    c.paint(vcyl(x, base - 14, base, r, r * 0.35), 'stone', gain=1.0,
            tex=lambda px, py: -0.1 if (py % 5 == 0 or (px + (py // 5) * 4) % 8 == 0) else 0)
    c.paint(ellipse(x, base - 14, r * 0.8, r * 0.26), 'water', emit=0.12)
    for s in (-1, 1):
        c.paint(rect(x + s * (r - 2) - 1.5, base - 44, x + s * (r - 2) + 1.5, base - 12), 'wood', gain=0.95 if s < 0 else 0.7)
    c.paint(poly([(x - r - 6, base - 40), (x + r + 6, base - 40), (x, base - 54)], nrm(-0.2, -0.6, 0.7)), 'wood', gain=1.0)
    c.paint(capsule(x - r + 2, base - 34, x + r - 2, base - 34, 1.4), 'wood', gain=0.9)
    c.paint(rect(x, base - 34, x + 1, base - 22), 'paper', gain=0.7, outline=False)
    c.paint(rect(x - 3, base - 22, x + 4, base - 16, nrm(-0.3, 0, 1)), 'wood', gain=1.0)


def fence(c, x0, x1, base, h=14, gain=0.8):
    for x in range(int(x0), int(x1), 9):
        c.paint(poly([(x, base), (x + 4, base), (x + 4, base - h), (x + 2, base - h - 3), (x, base - h)], nrm(-0.3, 0, 1)), 'wood', gain=gain)
    for yy in (base - h * 0.75, base - h * 0.35):
        c.paint(rect(x0, yy, x1, yy + 2), 'wood', gain=gain * 0.9)


def scaffold(c, x0, x1, top, base):
    """足場: 縦の丸太、横の板、筋かい。"""
    xs = [x0, (x0 + x1) / 2, x1]
    for x in xs:
        c.paint(capsule(x, base, x, top, 1.8), 'wood', gain=1.0)
    for yy in (top + 14, top + (base - top) * 0.55):
        c.paint(rect(x0 - 4, yy, x1 + 4, yy + 3, nrm(0, -0.6, 0.8)), 'wood', gain=1.05)
    for a, b in ((xs[0], xs[1]), (xs[1], xs[2])):
        c.paint(capsule(a, base - 2, b, top + (base - top) * 0.58, 1.0), 'wood', gain=0.8)


def block(c, x, y, w, h, gain=1.0):
    """切り石 1 つ（正面と上面と右側面）。"""
    d = w * 0.3
    c.paint(poly([(x, y), (x + d, y - d * 0.55), (x + w + d, y - d * 0.55), (x + w, y)], UP), 'stone', gain=gain * 1.1)
    c.paint(poly([(x + w, y), (x + w + d, y - d * 0.55), (x + w + d, y + h - d * 0.55), (x + w, y + h)], nrm(0.85, 0, 0.5)), 'stone', gain=gain * 0.8)
    return c.paint(rect(x, y, x + w, y + h, nrm(-0.2, 0, 1)), 'stone', gain=gain,
                   tex=lambda px, py: -0.05 if (px * 5 + py * 3) % 13 == 0 else 0)


def rope(c, x0, y0, x1, y1):
    c.paint(capsule(x0, y0, x1, y1, 0.7), 'paper', gain=0.75, outline=False)


def pulley(c, x, y):
    c.paint(ellipse(x, y, 5, 5), 'wood', gain=1.0)
    c.paint(ellipse(x, y, 1.6, 1.6), 'silver', gain=1.1)


def roast(c, x, y, s=1.0):
    """皿の上の丸焼き。"""
    c.paint(ellipse(x, y + 4 * s, 22 * s, 6 * s), 'silver', spec=0.6, gain=1.0)
    c.paint(ellipse(x, y - 4 * s, 15 * s, 9 * s), 'copper', spec=0.4, shine=5, gain=1.05)
    c.paint(ellipse(x - 13 * s, y - 2 * s, 6 * s, 4 * s), 'copper', spec=0.4)
    for s2 in (-1, 1):
        c.paint(capsule(x + 12 * s, y - 2 * s + s2 * 3, x + 20 * s, y - 6 * s + s2 * 2, 2.2 * s, 1.6 * s), 'copper', gain=0.95)
        c.paint(ellipse(x + 21 * s, y - 6 * s + s2 * 2, 1.8 * s, 1.8 * s), 'paper', gain=1.1)
    c.paint(ellipse(x - 20 * s, y + 3 * s, 3, 2.5), 'green')
    c.paint(ellipse(x + 18 * s, y + 4 * s, 3, 2.5), 'red', spec=0.4)


def ladder(c, x, top, base, w=14):
    for s in (0, w):
        c.paint(capsule(x + s, base, x + s + 4, top, 1.4), 'wood', gain=1.0 if s == 0 else 0.8)
    for yy in range(int(top + 6), int(base), 10):
        t = (yy - top) / (base - top)
        c.paint(capsule(x + 4 * (1 - t), yy, x + w + 4 * (1 - t), yy, 1.1), 'wood', gain=0.9)


def lectern(c, x, base, h=30):
    c.paint(rect(x - 3, base - h, x + 3, base, lambda px, py: nrm((px - x) / 3 * 0.8, 0, 0.7)), 'wood', gain=0.9)
    c.paint(ellipse(x, base, 10, 2.5), 'wood', gain=0.8)
    c.paint(poly([(x - 16, base - h - 2), (x + 16, base - h - 8), (x + 16, base - h - 4), (x - 16, base - h + 2)], UP), 'wood', gain=1.0)


def open_book(c, x, y, w=14, h=9):
    c.paint(poly([(x - w, y - 2), (x, y), (x, y + h), (x - w, y + h - 2)], nrm(-0.3, -0.6, 0.7)), 'paper', gain=1.15)
    c.paint(poly([(x, y), (x + w, y - 2), (x + w, y + h - 2), (x, y + h)], nrm(0.2, -0.6, 0.7)), 'paper', gain=1.0)
    for k in range(1, 4):
        yy = y + k * h / 4.5
        c.paint(rect(x - w + 3, yy - 1, x - 2, yy), 'paper', gain=0.55, outline=False)
        c.paint(rect(x + 2, yy - 1, x + w - 3, yy), 'paper', gain=0.5, outline=False)


def hang_banner(c, x, top, w, h, ramp='red', emblem='gold', kind='circle'):
    """梁から下がる旗（燕尾の下端）。"""
    pts = [(x, top), (x + w, top), (x + w, top + h), (x + w / 2, top + h - w * 0.4), (x, top + h)]
    o = c.paint(poly(pts, lambda px, py: nrm(0.4 * math.sin((px - x) / w * 6.3), 0, 0.9)), ramp, gain=1.0)
    c.paint(rect(x - 2, top - 2, x + w + 2, top + 1), 'wood', gain=1.0)
    cx, cy = x + w / 2, top + h * 0.38
    if kind == 'circle':
        c.paint(ellipse(cx, cy, w * 0.26, w * 0.26), emblem, oid=o, spec=0.4)
    elif kind == 'cross':
        c.paint(rect(cx - 1, cy - w * 0.3, cx + 1, cy + w * 0.3), emblem, oid=o, outline=False)
        c.paint(rect(cx - w * 0.3, cy - 1, cx + w * 0.3, cy + 1), emblem, oid=o, outline=False)
    elif kind == 'chevron':
        c.paint(poly([(cx - w * 0.3, cy + 3), (cx, cy - 4), (cx + w * 0.3, cy + 3), (cx + w * 0.3, cy + 6), (cx, cy - 1), (cx - w * 0.3, cy + 6)]), emblem, oid=o, outline=False)
    c.paint(rect(x, top + h * 0.75, x + w, top + h * 0.75 + 2, nrm(0, 0, 1)), emblem, oid=o, gain=0.8, outline=False,
            )
    return o


def chair(c, x, base, s=1.0, gain=0.8):
    c.paint(rect(x - 6 * s, base - 30 * s, x - 3 * s, base), 'wood', gain=gain)
    c.paint(rect(x + 4 * s, base - 14 * s, x + 7 * s, base), 'wood', gain=gain * 0.8)
    c.paint(rect(x - 6 * s, base - 16 * s, x + 7 * s, base - 13 * s, UP), 'wood', gain=gain * 1.1)


def logs(c, x, base, n=3, r=6):
    """積んだ丸太（小口が手前、年輪）。"""
    k = 0
    for row in range(n):
        for i in range(n - row):
            cx = x + i * r * 2.1 + row * r * 1.05
            cy = base - r - row * r * 1.75
            c.paint(ellipse(cx, cy, r, r, normal=nrm(-0.3, -0.1, 0.95)), 'wood', gain=1.35,
                    tex=lambda px, py, cx=cx, cy=cy: -0.1 if int(math.hypot(px - cx, py - cy)) % 2 == 0 else 0)
            c.paint(ellipse(cx, cy, 1.2, 1.2), 'wood', gain=0.8, outline=False)
            k += 1


def stump(c, x, base, r=16, h=12, log=True):
    c.paint(vcyl(x, base - h, base, r, r * 0.33), 'wood', gain=0.9, tex=lambda px, py: -0.08 if int(px) % 4 == 0 else 0)
    c.paint(ellipse(x, base - h, r * 0.95, r * 0.3, normal=UP), 'wood', gain=1.3,
            tex=lambda px, py: -0.1 if int(math.hypot((px - x) / 3, (py - base + h))) % 2 == 0 else 0)
    if log:
        c.paint(vcyl(x + 2, base - h - 16, base - h, 6, 2.2), 'wood', gain=1.0)
        c.paint(ellipse(x + 2, base - h - 16, 6, 2.2, normal=UP), 'wood', gain=1.35)


def railing(c, x0, x1, top, base, gain=0.9):
    """物見台の手すり（丸太の柵）。"""
    c.paint(rect(x0, top, x1, top + 4, nrm(0, -0.6, 0.8)), 'wood', gain=gain * 1.1)
    for x in range(int(x0) + 3, int(x1), 12):
        c.paint(rect(x, top + 4, x + 3, base, nrm(-0.3, 0, 1)), 'wood', gain=gain)
    c.paint(rect(x0, base - 5, x1, base, nrm(0, -0.3, 1)), 'wood', gain=gain * 0.9)
    for k in range(3):
        c.paint(capsule(x0 + 5 + k * 40, base - 5, x0 + 40 + k * 40, top + 5, 1.2), 'wood', gain=gain * 0.8)


def doorway(c, x, base, w=34, h=58, lit=True):
    pts = [(x - w / 2, base), (x - w / 2, base - h + w / 2)] + arc_points(x, base - h + w / 2, w / 2, math.pi, 2 * math.pi, 12) + [(x + w / 2, base)]
    c.paint(poly([(px + (3 if px > x else -3), py - 3) for px, py in pts]), 'stone', gain=1.1)
    c.paint(poly(pts), 'wood', gain=0.8, tex=lambda px, py: -0.1 if int(px - x + w) % 6 == 0 else 0)
    for yy in (base - h * 0.75, base - h * 0.3):
        c.paint(rect(x - w / 2, yy, x + w / 2, yy + 2), 'silver', gain=0.7, outline=False)
    c.paint(ellipse(x + w * 0.3, base - h * 0.45, 2, 2), 'gold', spec=0.6)


def cobweb(c, x, y, r=16):
    """隅の蜘蛛の巣。細い線だけ（光の中でだけ見える）。"""
    for k in range(5):
        a = math.pi / 2 * k / 4
        c.paint(capsule(x, y, x + math.cos(a) * r, y + math.sin(a) * r, 0.35), 'stone', gain=1.3, outline=False)
    for rr in (r * 0.4, r * 0.7):
        pts = arc_points(x, y, rr, 0, math.pi / 2, 4)
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.35), 'stone', gain=1.2, outline=False)


# ================= アイコン（ルネサンスの「もの」）の主役 =================

def nobori(c, x, top, base, w=30, ramp='red', emblem='gold'):
    """のぼり旗: 竿に縦長の布、上に横木、布の端に乳（ちち）。"""
    c.paint(capsule(x, base, x, top - 6, 2.0), 'wood', gain=1.0)
    c.paint(capsule(x, top, x + w + 2, top, 1.5), 'wood', gain=1.0)
    c.paint(ellipse(x, top - 7, 2.6, 2.6), 'gold', spec=0.7)
    ch = base - top - 18
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x + w + math.sin(t * 6) * 2.5, top + 2 + ch * t))
    pts += [(x + 2, top + 2 + ch), (x + 2, top + 2)]
    o = c.paint(poly(pts, lambda px, py: nrm(-0.3 + 0.4 * math.sin((py - top) / ch * 6 + 1.5), 0, 0.85)), ramp, gain=1.0)
    for k in range(6):
        yy = top + 4 + k * ch / 5.2
        c.paint(rect(x - 1, yy, x + 5, yy + 2), 'paper', gain=0.9)
    ex = x + 2 + w / 2
    c.paint(ellipse(ex, top + ch * 0.28, w * 0.32, w * 0.32), emblem, oid=o, spec=0.4)
    c.paint(ellipse(ex, top + ch * 0.28, w * 0.18, w * 0.18), ramp, oid=o, gain=0.9, outline=False)
    for k in range(3):
        yy = top + ch * (0.52 + k * 0.13)
        c.paint(rect(ex - w * 0.25, yy, ex + w * 0.25, yy + 3), emblem, oid=o, gain=0.95, outline=False)
    c.paint(rect(x + 2, top + ch - 6, x + w, top + ch - 3), emblem, oid=o, gain=0.8, outline=False)


def conch(c, x, y, s=1.0):
    """法螺貝: 左に大きく開いた口（内は桃色）、右へ細る渦の段、先に真鍮の吹き口、紐と房。"""
    k = s
    x0, y0, x1, y1 = x - 34 * k, y + 2 * k, x + 46 * k, y - 10 * k
    o = c.obj()
    steps = 40
    for i in range(steps, -1, -1):
        t = i / steps
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = 4 * k + 22 * k * (1 - t) ** 0.9
        ridge = (t * 6) % 1 < 0.22 and t > 0.45

        def tex(px, py, cx=cx, cy=cy, r=r, t=t):
            band = int((px - cx + (py - cy) * 0.6) / (3.5 * k)) % 3 == 0 and py > cy - r * 0.2 and t < 0.5
            return -0.12 if band else 0
        c.paint(ellipse(cx, cy, r * 0.55, r), 'paper', oid=o, gain=0.55 if ridge else 1.05, spec=0.3, shine=6, tex=tex)
    for t in (0.18, 0.3, 0.42):
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = 4 * k + 22 * k * (1 - t) ** 0.9
        c.paint(poly([(cx - 3 * k, cy - r + 2), (cx + 3 * k, cy - r + 2), (cx + 1 * k, cy - r - 6 * k)], nrm(-0.4, -0.6, 0.6)), 'paper', gain=1.1)
    c.paint(ellipse(x0 - 6 * k, y0 + 6 * k, 9 * k, 22 * k), 'paper', gain=1.2)
    c.paint(ellipse(x0 - 5 * k, y0 + 6 * k, 6.5 * k, 19 * k, normal=nrm(0.6, 0.1, 0.8)), 'red', gain=1.15)
    c.paint(ellipse(x0 + 1 * k, y0 + 4 * k, 6 * k, 18 * k), 'paper', gain=0.9,
            tex=lambda px, py: -0.12 if int((py - y0) / (3.5 * k)) % 3 == 0 else 0)
    c.paint(capsule(x1 - 2 * k, y1, x1 + 12 * k, y1 - 2 * k, 3.5 * k, 2.5 * k), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x1 + 12 * k, y1 - 2 * k, 1.5 * k, 3 * k), 'gold', gain=0.6)
    pts = [(x1 - 4 * k, y1 + 3 * k), (x + 30 * k, y + 22 * k), (x + 12 * k, y + 30 * k)]
    for a2, b2 in zip(pts, pts[1:]):
        c.paint(capsule(a2[0], a2[1], b2[0], b2[1], 1.3), 'red', gain=0.95)
    tx, ty = pts[-1]
    c.paint(ellipse(tx, ty, 3, 3), 'gold', spec=0.5)
    c.paint(poly([(tx - 3, ty + 2), (tx + 3, ty + 2), (tx + 5, ty + 16), (tx - 5, ty + 16)], lambda px, py: nrm(0.5 * math.sin(px * 1.3), 0, 0.85)), 'red', gain=1.0)


def key(c, x, y, s=1.0, ang=-20):
    """大きな鍵: 透かしの輪、軸、歯。真鍮の照り。"""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    k = s
    bx, by = x - dx * 44 * k, y - dy * 44 * k
    c.paint(ellipse(bx, by, 20 * k, 20 * k), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(bx, by, 11 * k, 11 * k), 'stone', emit=0.0, outline=False)
    for i in range(4):
        aa = i * math.pi / 2 + math.pi / 4
        c.paint(ellipse(bx + math.cos(aa) * 11 * k, by + math.sin(aa) * 11 * k, 4.5 * k, 4.5 * k), 'gold', gain=1.0, spec=0.6)
    c.paint(ellipse(bx, by, 4 * k, 4 * k), 'gold', spec=0.6)
    ex, ey = x + dx * 46 * k, y + dy * 46 * k
    c.paint(capsule(bx + dx * 18 * k, by + dy * 18 * k, ex, ey, 4.2 * k), 'gold', spec=0.8, shine=5)
    for t in (0.0, 0.08):
        cx_, cy_ = bx + dx * (22 + t * 100) * k, by + dy * (22 + t * 100) * k
        c.paint(capsule(cx_ + px * 7 * k, cy_ + py * 7 * k, cx_ - px * 7 * k, cy_ - py * 7 * k, 2.4 * k), 'gold', spec=0.6)
    for i, (t, ln) in enumerate(((0.8, 14), (0.9, 9), (1.0, 16))):
        cx_, cy_ = x + dx * 46 * k * t - dx * 6 * k * i, y + dy * 46 * k * t - dy * 6 * k * i
        q = [(cx_ - dx * 3 * k, cy_ - dy * 3 * k), (cx_ + dx * 3 * k, cy_ + dy * 3 * k),
             (cx_ + dx * 3 * k + px * ln * k, cy_ + dy * 3 * k + py * ln * k), (cx_ - dx * 3 * k + px * ln * k, cy_ - dy * 3 * k + py * ln * k)]
        c.paint(poly(q, nrm(0.2, 0.3, 0.9)), 'gold', gain=0.9, spec=0.5)
    c.paint(capsule(bx - dx * 18 * k, by - dy * 18 * k, bx - dx * 30 * k + px * 6, by - dy * 30 * k + py * 6, 1.2), 'red', gain=0.9)
    c.paint(ellipse(bx - dx * 32 * k + px * 8, by - dy * 32 * k + py * 8, 4, 6), 'red', gain=1.0)


# ================= 場面ごとの小さな組み物 =================

def niche(c, x, top, w, h):
    """祭壇の奥の壁龕: 尖頭アーチの窪み（奥は暗い）と、金の円窓。"""
    pts = [(x - w / 2, top + h), (x - w / 2, top + w / 2)] + arc_points(x, top + w / 2, w / 2, math.pi, 2 * math.pi, 14) + [(x + w / 2, top + h)]
    c.paint(poly([(px + (3 if px > x else -3), py - 3) for px, py in pts]), 'stone', gain=1.1)
    c.paint(poly(pts, nrm(0.5, 0.3, 0.8)), 'stone', gain=0.45)
    c.paint(ellipse(x, top + w * 0.45, w * 0.26, w * 0.26), 'gold', gain=0.9, spec=0.4)
    c.paint(ellipse(x, top + w * 0.45, w * 0.17, w * 0.17), 'blue', emit=0.55, outline=False)
    for k in range(6):
        a = k * math.pi / 3
        c.paint(capsule(x, top + w * 0.45, x + math.cos(a) * w * 0.17, top + w * 0.45 + math.sin(a) * w * 0.17, 0.6), 'gold', gain=0.8, outline=False)


def saw_on_bench(c, x, y):
    c.paint(poly([(x - 30, y - 4), (x + 8, y - 6), (x + 8, y + 2), (x - 30, y + 1)], nrm(-0.2, -0.7, 0.7)), 'silver', spec=0.6)
    for k in range(19):
        c.dot(int(x - 30 + k * 2), int(y + 1 - k * 0.05), 'N3')
    c.paint(poly([(x + 6, y - 9), (x + 20, y - 10), (x + 20, y + 3), (x + 6, y + 3)], nrm(-0.2, -0.5, 0.8)), 'wood', gain=1.1)
    c.paint(ellipse(x + 14, y - 3, 3, 3), 'wood', gain=0.4, outline=False)


def mallet(c, x, y):
    c.paint(capsule(x, y, x - 26, y + 6, 1.6), 'wood', gain=1.0)
    c.paint(capsule(x + 1, y - 7, x + 3, y + 7, 5, flat=0.4), 'wood', gain=1.25)


def shavings(c, pts):
    for x, y in pts:
        c.paint(ellipse(x, y, 4, 1.6, clip=lambda px, py, y=y: py <= y), 'wood', gain=1.5, outline=False)
        c.paint(ellipse(x, y + 0.5, 2, 0.8), 'wood', gain=0.9, outline=False)


def flowers(c, rows):
    """花畑: 奥の列は小さく暗く、手前ほど大きく明るい。色は決まった順に巡る。"""
    ramps = ['red', 'gold', 'blue', 'purple', 'red', 'paper']
    for ri, (y, r, step) in enumerate(rows):
        i = 0
        x = -step / 2 + hsh(ri, 1) * step
        while x < W + step:
            fx = x + (hsh(i, ri) - 0.5) * step * 0.6
            fy = y + (hsh(ri, i) - 0.5) * r * 2
            flower(c, fx, fy, r, ramps[(i * 3 + ri) % len(ramps)], stem=r * 2.5, gain=1.0 + ri * 0.15)
            x += step
            i += 1


def necklace(c, x, y):
    pts = arc_points(x, y - 6, 12, 0.2, math.pi - 0.2, 10)
    for px, py in pts:
        c.paint(ellipse(px, py, 1.6, 1.6), 'gold', spec=0.6, outline=False)
    gem(c, x, y + 7, 3.5, 'green')


def ruin_wall(c, x0, x1, base):
    """積みかけの石壁: 上の縁が段々に欠けている。"""
    for i, x in enumerate(range(int(x0), int(x1), 12)):
        top = base - 34 - 22 * math.sin((x - x0) / (x1 - x0) * math.pi * 0.9) + (6 if i % 2 else 0)
        stone_wall(c, int(top), int(base), x0=x, x1=min(int(x1), x + 12), bw=12, bh=7, gain=0.95, seed=6 + (i % 2))


def crane(c, x, top, hook):
    """足場の上の滑車と綱。"""
    c.paint(capsule(x - 34, top, x + 16, top, 2), 'wood', gain=1.0)
    pulley(c, hook[0], top + 4)
    rope(c, hook[0] - 3, top + 4, hook[0] - 3, hook[1])
    rope(c, hook[0] + 3, top + 4, x + 20, top + 40)
    c.paint(capsule(hook[0] - 3, hook[1], hook[0] - 8, hook[1] + 4, 0.8), 'silver')
    c.paint(capsule(hook[0] - 3, hook[1], hook[0] + 10, hook[1] + 4, 0.8), 'silver')


def hot_bar(c, x0, x1, y):
    """金床の上の赤く焼けた鉄。発光し、芯ほど白い。"""
    c.paint(capsule(x0, y, x1, y - 2, 3.0),
            'fire', emit=lambda px, py, n: 0.95 - abs(py - y + 1) * 0.12 - abs(px - (x0 + x1) / 2) / (x1 - x0) * 0.5)
    c.paint(capsule(x1, y - 2, x1 + 34, y - 10, 1.6), 'silver', gain=0.9, spec=0.5)
    c.paint(capsule(x1, y - 1, x1 + 34, y - 6, 1.6), 'silver', gain=0.75)


def hammer_rest(c, x, y):
    """金床に立てかけた槌。"""
    c.paint(capsule(x, y, x + 26, y + 34, 1.6), 'wood', gain=0.95)
    c.paint(capsule(x - 5, y + 3, x + 4, y - 4, 3, flat=0.4), 'silver', gain=0.75, spec=0.5)


def beam(c, y):
    c.paint(rect(0, y, W, y + 7, lambda px, py: nrm(0, (py - y - 3.5) / 3.5 * 0.7, 0.7)), 'wood', gain=0.9,
            tex=lambda px, py: -0.06 if (px + py * 4) % 13 == 0 else 0)


def tent(c, x, base, w, h):
    pts = [(x - w / 2, base), (x, base - h), (x + w / 2, base)]
    o = c.obj()
    for px, py, n in poly(pts, lambda px, py: nrm((px - x) / w * 1.4, -0.2, 0.8)):
        col = 'blue' if int((px - x) / 7 + 50) % 2 else 'paper'
        c.paint([(px, py, n)], col, oid=o, gain=0.6)
    c.paint(poly([(x - 4, base), (x, base - h * 0.6), (x + 4, base)]), 'fire', emit=0.5, outline=False)


def stall(c, x0, x1, top, base, colors=('red', 'paper'), counter='table'):
    """屋台: 2 本の柱、縞の日よけ、台。"""
    for x in (x0 + 4, x1 - 6):
        c.paint(rect(x, top, x + 3, base, nrm(-0.3, 0, 1)), 'wood', gain=0.95)
    awning(c, x0, x1, top, depth=14, colors=colors)
    ctop = base - 30
    if counter == 'crates':
        for i, x in enumerate(range(int(x0), int(x1) - 20, 36)):
            crate(c, x + 4, ctop + 4, 30, 24, gain=0.85)
    else:
        table(c, x0 + 6, x1 - 6, ctop, base, cloth=colors[0])


def lantern_string(c, y0, y1, colors):
    """店先に渡した綱と、ぶら下がる提灯の列。"""
    n = len(colors)
    pts = [(x, y0 + (y1 - y0) * math.sin(x / W * math.pi)) for x in range(0, W + 1, 4)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.5), 'wood', gain=0.6, outline=False)
    for i, col in enumerate(colors):
        x = (i + 0.5) * W / n
        y = y0 + (y1 - y0) * math.sin(x / W * math.pi)
        paper_lantern(c, x, y + 9, 5.5, col, string=y)


def mask(c, x, y, ramp='gold'):
    """祭りの面。"""
    o = c.paint(ellipse(x, y, 7, 8), ramp, spec=0.5)
    for ex in (-3, 3):
        c.paint(ellipse(x + ex, y - 1, 1.8, 1.3), 'stone', oid=o, emit=0.05, outline=False)
    c.paint(rect(x - 2, y + 4, x + 3, y + 5), 'red', oid=o, gain=1.0, outline=False)


def tube(c, pts):
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.0), 'silver', gain=0.85, spec=0.5)
        c.paint(capsule(a[0], a[1] - 1, b[0], b[1] - 1, 0.5), 'silver', emit=0.95, outline=False)


def bookcase(c, x0, x1, top, bottom):
    """壁一面の書棚: 棚板ごとに本の背と、巻物の差し込み口。"""
    c.paint(rect(x0, top, x1, bottom, nrm(0, 0, 1)), 'wood', gain=0.35, outline=False, dither=True)
    rows = list(range(int(top) + 26, int(bottom), 28))
    for i, y in enumerate(rows):
        c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.6, 0.8)), 'wood', gain=1.0)
        if i % 2 == 1:
            books_row(c, x0 + 2, x0 + (x1 - x0) * 0.55, y, hmin=14, hmax=22, seed=i * 3)
            for k in range(6):
                sx = x0 + (x1 - x0) * 0.58 + k * 14
                c.paint(ellipse(sx, y - 6, 5, 5, normal=nrm(-0.4, -0.2, 0.9)), 'paper', gain=1.0)
                c.paint(ellipse(sx, y - 6, 1.6, 1.6), 'paper', gain=0.5, outline=False)
        else:
            books_row(c, x0 + 2, x1 - 2, y, hmin=14, hmax=22, seed=i * 3 + 1)
    for x in (x0, x0 + (x1 - x0) / 2 - 2, x1 - 5):
        c.paint(rect(x, top, x + 5, bottom, nrm(-0.3, 0, 0.95)), 'wood', gain=0.9)


def scrolls(c, x, base):
    for i, (dx, dy, ln) in enumerate(((0, 0, 26), (-6, -6, 22), (6, -8, 24), (0, -13, 20))):
        c.paint(capsule(x + dx - ln / 2, base + dy, x + dx + ln / 2, base + dy - 3, 3.0), 'paper', gain=1.05)
        c.paint(ellipse(x + dx - ln / 2, base + dy, 2.4, 3, normal=nrm(-0.8, 0, 0.6)), 'paper', gain=0.85)
        c.paint(rect(x + dx - 1, base + dy - 4, x + dx + 1, base + dy + 2), 'red', gain=0.9, outline=False)


def tunnel(c, x0, x1, top, bottom):
    """坑道の奥: 支え木の内側は闇。奥にもう 1 組、小さく暗い支え木を置いて深さを出す。"""
    c.paint(rect(x0, top, x1, bottom), 'stone', emit=lambda px, py, n: 0.02 + 0.05 * (abs(px - (x0 + x1) / 2) / (x1 - x0) * 2) ** 2, outline=False)
    cx, cy = (x0 + x1) / 2, (top + bottom) / 2 + 8
    for k, sc in enumerate((0.55, 0.3)):
        w, h = (x1 - x0) * sc, (bottom - top) * sc
        g = 0.35 - k * 0.15
        for xx in (cx - w / 2, cx + w / 2 - 3):
            c.paint(rect(xx, cy - h / 2, xx + 3, cy + h / 2), 'wood', gain=g, outline=False)
        c.paint(rect(cx - w / 2 - 2, cy - h / 2 - 3, cx + w / 2 + 2, cy - h / 2), 'wood', gain=g, outline=False)


def rails(c, y):
    for yy in (y - 1, y + 5):
        pass
    for k in range(-6, 7):
        x = 112 + k * 20
        c.paint(rect(x - 6, y, x + 6, y + 3, UP), 'wood', gain=0.8)
    c.paint(rect(0, y - 1, W, y + 1), 'silver', gain=1.0, spec=0.5)
    c.paint(rect(0, y + 5, W, y + 7), 'silver', gain=0.9, spec=0.5)


def plate(c, x, y):
    c.paint(ellipse(x, y, 13, 4.2), 'silver', spec=0.6)
    c.paint(ellipse(x, y, 8, 2.6), 'silver', gain=0.75)


def bag_on_floor(c, x, base):
    c.paint(ellipse(x, base - 9, 12, 10), 'leather', gain=1.0)
    c.paint(poly([(x - 4, base - 18), (x + 4, base - 18), (x + 7, base - 24), (x - 7, base - 24)]), 'leather', gain=0.95)
    c.paint(rect(x - 5, base - 20, x + 5, base - 18), 'gold', outline=False)
    coin(c, x + 15, base - 2, 6, 'gold', stamp='crown')
    coin(c, x - 14, base, 5, 'gold', stamp='star')


def keyring(c, x, y):
    c.paint(ellipse(x, y, 4, 4), 'gold', spec=0.6)
    c.paint(ellipse(x, y, 2, 2), 'stone', emit=0.05, outline=False)
    for k, (dx, ln) in enumerate(((-3, 10), (0, 13), (3, 9))):
        c.paint(capsule(x + dx, y + 3, x + dx * 2, y + 3 + ln, 0.9), 'gold', spec=0.6)
        c.paint(rect(x + dx * 2, y + ln, x + dx * 2 + 3, y + ln + 2), 'gold', gain=0.9)


def statue(c, x, base):
    """彫りかけの石像: 台座、粗い石塊から上半身が現れている。"""
    block(c, x - 20, base - 16, 40, 16, gain=0.95)
    c.paint(poly([(x - 16, base - 16), (x + 16, base - 16), (x + 12, base - 50), (x - 12, base - 50)], lambda px, py: nrm((px - x) / 16 * 0.8, 0, 0.7)), 'stone', gain=1.1,
            tex=lambda px, py: -0.08 if (px * 3 + py * 7) % 11 == 0 and py > base - 34 else 0)
    c.paint(ellipse(x, base - 58, 7, 8), 'stone', gain=1.15)
    c.paint(capsule(x - 10, base - 48, x + 10, base - 48, 4), 'stone', gain=1.1)
    c.paint(capsule(x - 12, base - 46, x - 14, base - 30, 3), 'stone', gain=1.05)


def far_lights(c, pts):
    for x, y in pts:
        c.dot(x, y, 'G5')
        c.dot(x + 1, y, 'G4')


def eave(c, y, h):
    """軒（提灯を吊る）。"""
    c.paint(rect(0, y, W, y + h, lambda px, py: nrm(0, 0.6, 0.8)), 'wood', gain=0.7,
            tex=lambda px, py: -0.1 if int(px) % 10 == 0 else 0)
    c.paint(rect(0, y + h, W, y + h + 3, nrm(0, 0.3, 1)), 'wood', gain=0.9)


def lantern_mark(c, x, y):
    """提灯の胴に書いた丸紋（二重の輪）。"""
    c.paint(ellipse(x, y + 2, 14, 14), 'stone', emit=0.1, outline=False)
    c.paint(ellipse(x, y + 2, 11, 11), 'red', emit=0.8, outline=False)
    c.paint(ellipse(x, y + 2, 7, 7), 'stone', emit=0.1, outline=False)
    c.paint(ellipse(x, y + 2, 4, 4), 'red', emit=0.8, outline=False)


def lamp_post(c, x, base, h=70):
    """街灯: 木の柱と腕木、吊りランタン。"""
    c.paint(capsule(x, base, x, base - h, 2.0), 'wood', gain=0.9)
    c.paint(capsule(x, base - h + 2, x + 14, base - h + 2, 1.4), 'wood', gain=0.9)
    lantern(c, x + 12, base - h + 18, s=1.0, hang=base - h + 3)


def brazier(c, x, base):
    """篝火の鉄の鉢（三脚の上で炎が上がる）。"""
    for dx in (-7, 0, 7):
        c.paint(capsule(x + dx * 0.4, base - 16, x + dx, base, 1.1), 'silver', gain=0.7)
    c.paint(ellipse(x, base - 18, 11, 6, clip=lambda px, py: py >= base - 19), 'silver', gain=0.8, spec=0.4)
    for k in range(4):
        flame(c, x - 6 + k * 4, base - 24 - 3 * hsh(k, 2), 3, 7 + 2 * hsh(k, 5))


def vise(c, x, top):
    """作業台の端の万力。"""
    c.paint(rect(x - 8, top - 14, x + 8, top, nrm(-0.3, 0, 1)), 'silver', gain=0.8, spec=0.4)
    c.paint(rect(x - 10, top - 18, x + 10, top - 13, nrm(0, -0.6, 0.8)), 'silver', gain=1.0, spec=0.5)
    c.paint(capsule(x - 14, top - 8, x + 14, top - 8, 1.3), 'silver', gain=1.0, spec=0.6)
    c.paint(ellipse(x - 14, top - 8, 2, 2), 'silver', gain=1.1)


# ================= 陰謀（intrigue）で足した部品 =================

def clothesline(c, x0, x1, y, cloths=('paper', 'blue', 'red', 'paper')):
    """物干し綱と、干した布。"""
    pts = [(x, y + 6 * math.sin((x - x0) / (x1 - x0) * math.pi)) for x in range(int(x0), int(x1) + 1, 3)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.5), 'paper', gain=0.6, outline=False)
    n = len(cloths)
    for i, col in enumerate(cloths):
        cx = x0 + (i + 0.6) * (x1 - x0) / (n + 0.2)
        cy = y + 6 * math.sin((cx - x0) / (x1 - x0) * math.pi)
        w, h = 14 + 4 * hsh(i, 2), 18 + 8 * hsh(i, 3)
        c.paint(poly([(cx - w / 2, cy), (cx + w / 2, cy), (cx + w / 2 + 1, cy + h), (cx - w / 2 - 1, cy + h - 3)],
                     lambda px, py, cx=cx: nrm(0.4 * math.sin((px - cx) / 3), 0, 0.9)), col, gain=0.95)
        for px in (cx - w / 2 + 2, cx + w / 2 - 2):
            c.paint(rect(px, cy - 2, px + 1.5, cy + 2), 'wood', gain=1.1, outline=False)


def fountain(c, x, base, r=40):
    """石の泉: 円い水盤、中の柱と上の受け皿、落ちる水、底の硬貨。"""
    c.paint(vcyl(x, base - 16, base, r, r * 0.3), 'stone', gain=1.0,
            tex=lambda px, py: -0.08 if (py % 6 == 0 or (px + (py // 6) * 7) % 13 == 0) else 0)
    c.paint(ellipse(x, base - 16, r, r * 0.3, normal=UP), 'stone', gain=1.15)
    lt = c.light
    c.paint(ellipse(x, base - 16, r - 4, r * 0.3 - 3), 'water',
            emit=lambda px, py, n: 0.35 + 0.3 * lt.att(px, py) + (0.12 if (py + int(px / 6)) % 4 == 0 else 0))
    for k, (dx, dy) in enumerate(((-14, -14), (6, -12), (16, -17), (-4, -19))):
        coin(c, x + dx, base + dy, 3.2, 'gold' if k % 2 == 0 else 'silver', tilt=0.4, stamp='pip')
    c.paint(capsule(x, base - 18, x, base - 52, 4, 3), 'stone', gain=1.0)
    c.paint(ellipse(x, base - 54, 16, 5, clip=lambda px, py: py >= base - 55), 'stone', gain=1.05)
    c.paint(ellipse(x, base - 56, 15, 3.5), 'water', emit=0.6)
    c.paint(ellipse(x, base - 62, 3, 6), 'stone', gain=1.1)
    for s in (-1, 1):
        pts = [(x + s * (14 + t * 10), base - 54 + t * t * 34) for t in [i / 8 for i in range(9)]]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.3), 'water', emit=0.75, outline=False)
    pts = [(x + math.sin(t * 6) * 0.6, base - 68 - t * 6) for t in [i / 5 for i in range(6)]]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.0), 'water', emit=0.85, outline=False)


def cliff(c, x0, x1, top, side=1, ramp='stone', gain=0.85):
    """崖: 岩の塊が段々に積み、縁は光を受ける。side=1 なら右へ落ちる。"""
    pts = [(x0, H), (x0, top)]
    for k in range(7):
        t = k / 6
        x = x0 + (x1 - x0) * t
        pts.append((x, top + (t ** 2) * 10 + (3 if k % 2 else 0)))
    pts += [(x1, top + 20), (x1 - side * 6, H)]
    o = c.paint(poly(pts, lambda px, py: nrm(0.3 * math.sin(px / 5 + py / 9) - 0.2, 0.2 * math.cos(py / 6), 0.8)), ramp, gain=gain,
                tex=lambda px, py: -0.1 if (int(px + py * 0.6) % 11 == 0) else 0)
    c.paint(rect(x0, top - 1, x1 - (x1 - x0) * 0.3, top + 2, UP), 'foliage', oid=o, gain=0.9, outline=False)


def rope_bridge(c, x0, y0, x1, y1, sag=22):
    """吊り橋: 両岸の柱、垂れた 2 本の綱、板。"""
    def at(t, lift=0):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * math.sin(t * math.pi) - lift
    for x, y in ((x0, y0), (x1, y1)):
        c.paint(capsule(x, y + 2, x, y - 20, 2.0), 'wood', gain=1.0)
        c.paint(ellipse(x, y - 21, 2.5, 2), 'wood', gain=1.2)
    n = 26
    for i in range(n):
        t = (i + 0.5) / n
        px, py = at(t)
        c.paint(rect(px - 3, py - 1, px + 3, py + 2, UP), 'wood', gain=1.1 - 0.3 * (i % 2))
    for lift in (0, 16):
        pts = [at(i / 30, lift) for i in range(31)]
        if lift:
            pts = [(x, y - 18 + sag * 0.15 * math.sin(i / 30 * math.pi)) for i, (x, y) in enumerate([at(i / 30) for i in range(31)])]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.7), 'paper', gain=0.75, outline=False)
        if lift:
            for i in range(0, 31, 3):
                a, b = pts[i], at(i / 30)
                c.paint(capsule(a[0], a[1], b[0], b[1], 0.4), 'paper', gain=0.6, outline=False)


def crucible_pour(c, x, y, s=1.0):
    """鎖で吊った坩堝（丸い鉄の壺）を左へ傾け、口から溶けた金属を型へ注ぐ。"""
    k = s
    c.paint(rect(x + 4, 0, x + 5, y - 20 * k), 'silver', gain=0.7, outline=False)
    c.paint(capsule(x - 14 * k, y - 8 * k, x + 4, y - 20 * k, 1.0 * k), 'silver', gain=0.8)
    c.paint(capsule(x + 18 * k, y - 4 * k, x + 4, y - 20 * k, 1.0 * k), 'silver', gain=0.7)
    c.paint(ellipse(x + 2 * k, y + 6 * k, 18 * k, 15 * k), 'silver', gain=0.55, spec=0.3)
    # 傾いた口（左が下がる）: 縁は熱で赤く、中は溶けた金属
    lip = [(x - 18 * k, y - 4 * k), (x + 14 * k, y - 12 * k), (x + 16 * k, y - 6 * k), (x - 14 * k, y + 3 * k)]
    c.paint(poly(lip), 'fire', emit=lambda px, py, n: 0.82 - (px - x + 18 * k) / (34 * k) * 0.3)
    c.paint(capsule(x - 18 * k, y - 4 * k, x + 14 * k, y - 12 * k, 1.2 * k), 'red', emit=0.75, outline=False)
    pts = [(x - 18 * k, y - 2 * k), (x - 24 * k, y + 8 * k), (x - 26 * k, y + 24 * k), (x - 26 * k, y + 40 * k)]
    for a2, b2 in zip(pts, pts[1:]):
        c.paint(capsule(a2[0], a2[1], b2[0], b2[1], 2.2 * k, 1.8 * k), 'fire', emit=0.72, outline=False)
        c.paint(capsule(a2[0] - 0.5, a2[1], b2[0] - 0.5, b2[1], 0.6 * k), 'fire', emit=0.95, outline=False)


def molds(c, x0, y, n=3, w=26):
    for i in range(n):
        x = x0 + i * (w + 6)
        c.paint(poly([(x, y), (x + w, y), (x + w + 6, y - 5), (x + 6, y - 5)], UP), 'stone', gain=1.0)
        c.paint(rect(x, y, x + w, y + 8, nrm(-0.1, 0.1, 1)), 'stone', gain=0.75)
        glow = 0.9 if i == 0 else (0.55 if i == 1 else 0)
        if glow:
            c.paint(poly([(x + 4, y - 1), (x + w - 2, y - 1), (x + w + 2, y - 4), (x + 8, y - 4)]), 'fire', emit=glow, outline=False)
        else:
            c.paint(poly([(x + 4, y - 1), (x + w - 2, y - 1), (x + w + 2, y - 4), (x + 8, y - 4)], UP), 'gold', gain=1.0, spec=0.6)


def waterwheel(c, x, y, r=30, spokes=8):
    """水車: 外輪、輻、水受けの板、軸。右から落ちる水。"""
    pts = arc_points(x, y, r, 0, math.pi * 2, 40)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.0), 'wood', gain=1.0)
    pts = arc_points(x, y, r * 0.6, 0, math.pi * 2, 30)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.0), 'wood', gain=0.9)
    for k in range(spokes):
        a = k / spokes * math.pi * 2 + 0.2
        c.paint(capsule(x, y, x + math.cos(a) * r, y + math.sin(a) * r, 1.3), 'wood', gain=0.95)
    for k in range(spokes * 2):
        a = k / (spokes * 2) * math.pi * 2
        ox, oy = math.cos(a), math.sin(a)
        c.paint(capsule(x + ox * r, y + oy * r, x + ox * (r + 6), y + oy * (r + 6), 2.0, flat=0.5), 'wood', gain=1.1)
    c.paint(ellipse(x, y, 4.5, 4.5), 'silver', gain=1.0, spec=0.5)
    for k in range(3):
        xx = x + r * 0.7 + k * 3
        c.paint(capsule(xx, y - r - 4, xx + 2, y + r * 0.5, 1.4), 'water', emit=0.75 - k * 0.12, outline=False)


def stream(c, y0, y1):
    """小川（帯状の水面）。"""
    lt = c.light
    pix = [(x, y, FLAT) for y in range(int(y0), int(y1)) for x in range(W)]
    c.paint(pix, 'water', emit=lambda x, y, n: 0.2 + 0.4 * lt.att(x, y) + (0.1 if math.sin(y * 1.7 + math.sin(x / 7) * 2) > 0.7 else 0),
            dither=True, outline=False)


def headframe(c, x, base, h=70):
    """坑口の櫓: 木の脚 2 本、筋かい、頂の滑車、垂れる綱。"""
    for s in (-1, 1):
        c.paint(capsule(x + s * 20, base, x + s * 5, base - h, 2.2), 'wood', gain=1.0 if s < 0 else 0.8)
    for k in range(3):
        y = base - h * (0.25 + k * 0.25)
        w = 20 - (20 - 5) * (0.25 + k * 0.25)
        c.paint(capsule(x - w, y, x + w, y, 1.4), 'wood', gain=0.9)
    c.paint(capsule(x - 18, base - 4, x + 12, base - h * 0.7, 1.0), 'wood', gain=0.75)
    c.paint(ellipse(x, base - h - 2, 8, 8), 'wood', gain=1.1)
    c.paint(ellipse(x, base - h - 2, 2, 2), 'silver', gain=1.1)
    c.paint(rect(x + 7, base - h, x + 8, base - 12), 'paper', gain=0.6, outline=False)


def secret_door(c, x, base, w=46, h=80):
    """隠し戸: 壁の書棚がずれて開き、奥に下りの石段と松明の灯。"""
    top = base - h
    c.paint(rect(x, top, x + w, base), 'stone', emit=0.04, outline=False)
    for k in range(7):
        sy = top + 30 + k * 7
        sx = x + 6 + k * 3
        c.paint(rect(sx, sy, x + w - 2, sy + 3, UP), 'stone', gain=1.0, add=0.1 - k * 0.04)
        c.paint(rect(sx, sy + 3, x + w - 2, sy + 7, nrm(0, 0.3, 1)), 'stone', gain=0.6, add=0.06 - k * 0.03)
    c.paint(ellipse(x + w - 10, top + 22, 9, 12), 'fire', emit=lambda px, py, n: 0.6 - math.hypot(px - x - w + 10, py - top - 22) / 18, outline=False)
    flame(c, x + w - 10, top + 18, 2.5, 5)
    # 回り戸の書棚（手前へ斜めに開く）
    pts = [(x - 4, top - 2), (x - 30, top + 8), (x - 30, base + 6), (x - 4, base)]
    c.paint(poly(pts, nrm(-0.6, 0, 0.8)), 'wood', gain=0.95)
    for k in range(4):
        yy = top + 6 + k * 20
        c.paint(poly([(x - 6, yy), (x - 28, yy + 8), (x - 28, yy + 10), (x - 6, yy + 2)], UP), 'wood', gain=1.1)
        for j in range(5):
            bx = x - 9 - j * 4
            col = ('red', 'blue', 'green', 'leather', 'purple')[(j + k) % 5]
            c.paint(rect(bx - 2, yy - 13 + j * 1.6, bx + 1, yy + 1 + j * 1.6), col, gain=0.9, outline=False)


def column(c, x, top, base, r=7, ramp='stone', gain=1.0):
    """円柱（柱頭と礎盤つき）。"""
    c.paint(vcyl(x, top + 6, base - 4, r, r * 0.3, top=False), ramp, gain=gain,
            tex=lambda px, py: -0.07 if int(px - x + r) % 4 == 0 else 0)
    c.paint(rect(x - r - 3, top, x + r + 4, top + 6, nrm(-0.2, -0.3, 0.9)), ramp, gain=gain * 1.05)
    c.paint(rect(x - r - 3, base - 4, x + r + 4, base, nrm(-0.2, -0.3, 0.9)), ramp, gain=gain * 0.95)


def palace(c, x, base, w=150, h=56, wings=True, gain=1.0, dep=0.0, cols=6, lit=True):
    """館（左右対称）: 中央の破風と柱廊、両翼、並ぶ窓。"""
    x0 = x - w / 2
    if wings:
        for s in (-1, 1):
            wx = x + s * w * 0.32 - w * 0.18
            stone_wall(c, int(base - h * 0.8), int(base), x0=int(wx), x1=int(wx + w * 0.36), bw=10, bh=6, gain=gain * 0.9, depth=dep, seed=8)
            c.paint(poly([(wx - 2, base - h * 0.8), (wx + w * 0.36 + 2, base - h * 0.8), (wx + w * 0.33, base - h * 0.8 - 12), (wx + w * 0.03, base - h * 0.8 - 12)],
                         nrm(-0.1, -0.7, 0.6)), 'blue', gain=gain * 0.8, depth=dep)
            for k in range(3):
                for row in range(2):
                    window(c, wx + 6 + k * w * 0.11, base - h * 0.7 + row * h * 0.34, 6, 9, lit and (k + row) % 3 != 1, arch=True)
    cx0, cx1 = x - w * 0.2, x + w * 0.2
    stone_wall(c, int(base - h), int(base), x0=int(cx0), x1=int(cx1), bw=10, bh=6, gain=gain, depth=dep, seed=9)
    c.paint(poly([(cx0 - 4, base - h), (cx1 + 4, base - h), (x, base - h - 22)], nrm(-0.2, -0.5, 0.8)), 'stone', gain=gain * 1.1, depth=dep)
    c.paint(ellipse(x, base - h - 8, 4, 4), 'gold', spec=0.6)
    c.paint(rect(cx0 - 4, base - h - 1, cx1 + 4, base - h + 3, UP), 'stone', gain=gain * 1.15, depth=dep)
    for k in range(cols):
        px = cx0 + 4 + k * (cx1 - cx0 - 8) / (cols - 1)
        window(c, px - 3, base - h + 8, 6, 10, lit, arch=True) if k not in (0, cols - 1) else None
    for k in range(cols):
        px = cx0 + 4 + k * (cx1 - cx0 - 8) / (cols - 1)
        column(c, px, base - h * 0.55, base, r=2.6, gain=gain * 1.1)
    c.paint(rect(cx0 - 2, base - h * 0.55 - 2, cx1 + 2, base - h * 0.55 + 1, UP), 'stone', gain=gain * 1.1)
    c.paint(rect(x - 6, base - 20, x + 6, base), 'fire', emit=0.7, outline=False)
    for k in range(3):
        c.paint(rect(cx0 - 6 - k * 4, base + k * 3, cx1 + 6 + k * 4, base + 3 + k * 3, UP), 'stone', gain=gain * (1.1 - k * 0.1))


def hedge(c, x0, x1, base, h=10, gain=0.8):
    """刈り込んだ生垣（上面が光を受ける）。"""
    c.paint(rect(x0, base - h, x1, base, lambda px, py: nrm(0.15 * math.sin(px / 3), -0.6 if py < base - h + 3 else 0, 0.8)), 'foliage', gain=gain,
            tex=lambda px, py: -0.07 if (px * 3 + py * 5) % 7 == 0 else 0)


def topiary(c, x, base, h=24):
    c.paint(rect(x - 1, base - 6, x + 2, base), 'wood', gain=0.9)
    c.paint(ellipse(x, base - 6 - h * 0.35, h * 0.28, h * 0.36), 'foliage', gain=0.95)
    c.paint(ellipse(x, base - 6 - h * 0.85, h * 0.18, h * 0.22), 'foliage', gain=1.0)


def throne(c, x, base, ramp='red'):
    """玉座: 高い背もたれ（赤い布張り・金の縁）と肘掛け、段。"""
    for k in range(2):
        c.paint(rect(x - 30 + k * 6, base - 6 + k * 3 - 6, x + 30 - k * 6, base - 3 + k * 3, UP), 'stone', gain=1.0 - k * 0.1)
    c.paint(rect(x - 18, base - 70, x + 18, base - 26, nrm(-0.2, 0, 1)), 'gold', gain=0.9, spec=0.5)
    c.paint(poly([(x - 18, base - 70), (x + 18, base - 70), (x, base - 84)], nrm(-0.2, -0.4, 0.9)), 'gold', gain=1.0, spec=0.6)
    c.paint(rect(x - 13, base - 66, x + 13, base - 30, lambda px, py: nrm(0.2 * math.sin((px - x) / 4), 0, 1)), ramp, gain=0.95)
    c.paint(rect(x - 22, base - 30, x + 22, base - 22, UP), ramp, gain=1.05)
    c.paint(rect(x - 22, base - 22, x + 22, base - 9, nrm(-0.1, 0, 1)), 'gold', gain=0.8)
    for s in (-1, 1):
        c.paint(rect(x + s * 24 - 4, base - 40, x + s * 24 + 4, base - 9, nrm(s * 0.5, 0, 0.8)), 'gold', gain=0.85, spec=0.4)
        c.paint(ellipse(x + s * 24, base - 41, 5, 3), 'gold', spec=0.6)
    gem(c, x, base - 76, 3.5, 'red')


def carpet(c, x, top, base, w0=14, w1=60, ramp='red'):
    """奥へ伸びる絨毯（手前ほど幅広）と、金の縁取り。"""
    pts = [(x - w0 / 2, top), (x + w0 / 2, top), (x + w1 / 2, base), (x - w1 / 2, base)]
    o = c.paint(poly(pts, UP), ramp, gain=1.0, tex=lambda px, py: -0.06 if int(py) % 7 == 0 else 0)
    for s in (-1, 1):
        c.paint(capsule(x + s * w0 / 2 * 0.85, top, x + s * w1 / 2 * 0.85, base, 0.8), 'gold', oid=o, gain=1.0, outline=False)


def chandelier(c, x, y, r=26, chain_top=0):
    c.paint(rect(x, chain_top, x + 1, y), 'gold', gain=0.7, outline=False)
    c.paint(ellipse(x, y, r, r * 0.25, clip=lambda px, py: py >= y), 'gold', gain=0.9, spec=0.6)
    for k in range(5):
        cx = x - r + k * r * 0.5
        c.paint(vcyl(cx, y - 7, y - 1, 1.4, 0.5), 'paper', gain=1.2, add=0.15)
        flame(c, cx, y - 10, 1.6, 3.2)


def cell_bars(c, x0, x1, top, base, gap=9):
    """牢の鉄格子（奥は闇、横桟 2 本）。"""
    c.paint(rect(x0, top, x1, base), 'stone', emit=0.03, outline=False)
    for x in range(int(x0) + 3, int(x1), gap):
        c.paint(capsule(x, top, x, base, 1.5), 'silver', gain=0.85, spec=0.5)
    for y in (top + 8, base - 16):
        c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.4, 0.9)), 'silver', gain=0.8, spec=0.4)


def trapdoor(c, x, y, w=60, d=22):
    """床の落とし戸: 開いた戸板、下の暗がり、梯子、奥の宝箱の照り。"""
    pts = [(x - w / 2, y), (x + w / 2, y), (x + w / 2 + 8, y + d), (x - w / 2 - 8, y + d)]
    c.paint(poly(pts), 'stone', emit=lambda px, py, n: 0.02 + (py - y) / d * 0.08, outline=False)
    coin(c, x + 12, y + d * 0.7, 5, 'gold', stamp='crown')
    coin(c, x + 22, y + d * 0.75, 4.5, 'gold', stamp='star')
    for s in (0, 14):
        c.paint(capsule(x - 16 + s, y + d, x - 12 + s, y - 6, 1.3), 'wood', gain=1.0)
    for k in range(3):
        yy = y + 2 + k * 7
        c.paint(capsule(x - 15, yy, x + 1, yy, 1.0), 'wood', gain=0.95)
    lid = [(x - w / 2, y), (x + w / 2, y), (x + w / 2 - 6, y - 34), (x - w / 2 + 6, y - 34)]
    c.paint(poly(lid, nrm(-0.2, 0.3, 1)), 'wood', gain=0.95, tex=lambda px, py: -0.1 if int(px - x) % 10 == 0 else 0)
    c.paint(ellipse(x, y - 20, 4, 4), 'silver', gain=0.9)
    c.paint(ellipse(x, y - 20, 2.4, 2.4), 'stone', emit=0.05, outline=False)


def toll_gate(c, x, base, length=110):
    """関所の遮断棒（紅白）と、柱、銭箱。"""
    c.paint(rect(x - 4, base - 40, x + 4, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0)
    c.paint(ellipse(x, base - 30, 5, 5), 'silver', gain=1.0)
    for k in range(10):
        x0 = x + k * length / 10
        c.paint(capsule(x0, base - 30, x0 + length / 10, base - 30, 2.4, flat=0.2), 'red' if k % 2 == 0 else 'paper', gain=1.05)
    c.paint(capsule(x - 2, base - 30, x - 26, base - 30, 3, flat=0.2), 'stone', gain=0.9)
    c.paint(rect(x + length - 3, base - 30, x + length, base), 'wood', gain=0.8)


def coin_box(c, x, base):
    o = c.paint(rect(x - 12, base - 16, x + 12, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0)
    c.paint(poly([(x - 12, base - 16), (x + 12, base - 16), (x + 16, base - 20), (x - 8, base - 20)], UP), 'wood', gain=1.2)
    c.paint(rect(x - 5, base - 19, x + 6, base - 17), 'stone', emit=0.05, outline=False)
    c.paint(rect(x - 12, base - 9, x + 12, base - 7), 'silver', oid=o, gain=0.8, outline=False)
    coin(c, x + 2, base - 24, 4, 'silver', tilt=0.95, stamp='tower')


def tripod(c, x, base, h=44):
    """測量の三脚と、上の望遠の器械。"""
    for dx in (-12, 2, 12):
        c.paint(capsule(x, base - h, x + dx, base, 1.2), 'wood', gain=0.95 if dx < 0 else 0.8)
    c.paint(rect(x - 6, base - h - 3, x + 7, base - h + 1, UP), 'gold', spec=0.6)
    c.paint(capsule(x - 9, base - h - 7, x + 10, base - h - 9, 2.6, 2.0), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x, base - h - 5, 3, 2), 'gold', gain=0.8)


def cups_game(c, x, y):
    """伏せた 3 つの椀と、1 つから覗く玉（いかさまの賭け）。"""
    for k, dx in enumerate((-26, 0, 26)):
        cx = x + dx
        lift = 6 if k == 2 else 0
        c.paint(poly([(cx - 9, y - lift), (cx + 9, y - lift), (cx + 6, y - 16 - lift), (cx - 6, y - 16 - lift)],
                     lambda px, py, cx=cx: nrm((px - cx) / 9 * 0.8, -0.1, 0.7)), 'leather', gain=1.1)
        c.paint(ellipse(cx, y - 16 - lift, 6, 2), 'leather', gain=1.3)
        if lift:
            c.paint(ellipse(cx, y + 1, 3, 3), 'red', spec=0.6)


def chess_board(c, x, y, w=56):
    """卓の上の盤（奥へ傾いた市松）と、いくつかの駒。"""
    d = w * 0.4
    for i in range(8):
        for j in range(4):
            t0, t1 = j / 4, (j + 1) / 4
            def pt(u, t):
                return (x - w / 2 + d * 0.3 * t + u * (w - d * 0.6 * t), y - d * t)
            q = [pt(i / 8, t0), pt((i + 1) / 8, t0), pt((i + 1) / 8, t1), pt(i / 8, t1)]
            c.paint(poly(q, UP), 'paper' if (i + j) % 2 == 0 else 'wood', gain=0.85 if (i + j) % 2 == 0 else 1.0, outline=False)
    for px, py, col, tall in ((x - 14, y - 6, 'paper', 12), (x + 4, y - 12, 'wood', 10), (x + 16, y - 4, 'paper', 8), (x - 4, y - 2, 'wood', 14)):
        c.paint(vcyl(px, py - tall, py, 2.6, 1.0), col, gain=1.2 if col == 'paper' else 1.4, spec=0.4)
        c.paint(ellipse(px, py - tall - 2, 2.6, 2.6), col, gain=1.2 if col == 'paper' else 1.4, spec=0.4)


def sign(c, x, y, w=36, h=18, ramp='wood', emblem='coin'):
    """吊り看板。"""
    c.paint(capsule(x - w / 2 - 6, y - 10, x + w / 2 + 2, y - 10, 1.5), 'silver', gain=0.8)
    for s in (-1, 1):
        c.paint(rect(x + s * w * 0.35, y - 10, x + s * w * 0.35 + 1, y), 'silver', gain=0.7, outline=False)
    o = c.paint(rect(x - w / 2, y, x + w / 2, y + h, nrm(-0.2, 0, 1)), ramp, gain=1.0)
    if emblem == 'coin':
        coin(c, x, y + h / 2, h * 0.35, 'gold', tilt=0.95)
    elif emblem == 'scale':
        c.paint(rect(x - 1, y + 3, x + 1, y + h - 3), 'gold', oid=o, outline=False)
        c.paint(rect(x - 10, y + 5, x + 10, y + 6), 'gold', oid=o, outline=False)


def pots(c, x, base, n=3):
    for k in range(n):
        px = x + k * 18
        r = 8 - k
        c.paint(ellipse(px, base - r, r, r * 0.85, clip=lambda qx, qy, b=base - r: qy >= b - r * 0.4), 'copper', spec=0.6, shine=5)
        c.paint(ellipse(px, base - r * 1.4, r, r * 0.3), 'copper', gain=0.55)
        c.paint(capsule(px + r, base - r * 1.3, px + r + 6, base - r * 1.6, 0.9), 'silver', gain=0.85)


def rubble(c, x, base, n=8, seed=0):
    for k in range(n):
        rx = x + (hsh(k, seed) - 0.5) * 50
        ry = base - hsh(seed, k) * 6
        r = 2 + hsh(k, 5, seed) * 4
        c.paint(poly([(rx - r, ry), (rx - r * 0.3, ry - r), (rx + r, ry - r * 0.6), (rx + r * 0.8, ry)], nrm(-0.4, -0.6, 0.7)), 'stone', gain=1.0)


def broken_wall(c, x0, x1, base, top=40, seed=1):
    """壊されかけの壁: 中ほどに穴が開き、石が飛ぶ。"""
    stone_wall(c, int(top), int(base), x0=int(x0), x1=int(x1), bw=14, bh=8, gain=0.95, seed=seed)
    cx, cy = (x0 + x1) / 2 + 6, (top + base) / 2 + 6
    pts = []
    for k in range(12):
        a = k / 12 * math.pi * 2
        rr = 18 + 8 * hsh(k, seed)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9))
    c.paint(poly(pts), 'stone', emit=0.03, outline=False)
    for k in range(6):
        a = -0.9 - k * 0.35
        d = 26 + k * 6
        bx, by = cx + math.cos(a) * d - 40, cy + math.sin(a) * d * 0.7
        r = 3 + hsh(k, 3) * 3
        c.paint(poly([(bx - r, by), (bx, by - r), (bx + r, by - r * 0.3), (bx + r * 0.5, by + r)], nrm(-0.4, -0.5, 0.7)), 'stone', gain=1.1)


def confetti(c, area, n=40, seed=0):
    x0, y0, x1, y1 = area
    cols = ('R3', 'G5', 'B3', 'E3', 'P3')
    for k in range(n):
        x = int(x0 + hsh(k, seed) * (x1 - x0))
        y = int(y0 + hsh(seed, k, 1) * (y1 - y0))
        c.dot(x, y, cols[k % len(cols)])
        if k % 3 == 0:
            c.dot(x + 1, y, cols[k % len(cols)])


def gem_bench(c, x, y, s=1.0):
    """宝石の手直し: 台の上の万力に挟んだ石、やすり、拡大鏡、削り粉、仕上がった石。"""
    if s != 1.0:
        return _gem_bench_scaled(c, x, y, s)
    c.paint(rect(x - 6, y - 12, x + 6, y, nrm(-0.3, 0, 1)), 'silver', gain=0.8, spec=0.4)
    c.paint(rect(x - 10, y - 15, x + 10, y - 11, UP), 'silver', gain=1.0, spec=0.5)
    gem(c, x, y - 21, 7, 'green')
    c.paint(capsule(x + 18, y - 4, x + 52, y - 10, 1.6), 'silver', gain=0.95, spec=0.6)
    c.paint(capsule(x + 46, y - 9, x + 56, y - 11, 2, 2), 'wood', gain=1.0)
    c.paint(ellipse(x - 34, y - 6, 9, 9), 'gold', spec=0.6)
    c.paint(ellipse(x - 34, y - 6, 6.5, 6.5), 'water', emit=lambda px, py, n: 0.45 + (0.35 if px - py < x - 34 - (y - 6) - 2 else 0), outline=False)
    c.paint(capsule(x - 28, y, x - 18, y + 8, 1.6), 'wood', gain=1.0)
    for k in range(6):
        c.dot(int(x - 8 + k * 3), int(y + 3 + (k % 2)), 'E3')
    gem(c, x + 30, y + 6, 5, 'red')
    gem(c, x + 44, y + 8, 4, 'blue')


def roof_ridge(c, y, ramp='wood'):
    """手前いっぱいの屋根（瓦の段が奥へ並ぶ）。人物はこの上に乗る。"""
    pix = [(x, yy, nrm(0, -0.8, 0.6)) for yy in range(int(y), H) for x in range(W)]
    c.paint(pix, ramp, gain=0.9, dither=True, outline=False,
            tex=lambda px, py: -0.12 if int(py - y) % 6 == 0 else (-0.05 if (int(px) + (int(py - y) // 6) * 5) % 10 == 0 else 0))
    c.paint(rect(0, y - 2, W, y + 1, UP), ramp, gain=1.15)


def letter_fly(c, x, y):
    """風に舞う 1 枚の書き付け。"""
    c.paint(poly([(x, y), (x + 12, y - 4), (x + 14, y + 6), (x + 2, y + 9)], nrm(-0.3, -0.4, 0.8)), 'paper', gain=1.1)
    for k in range(3):
        c.paint(rect(x + 3, y + 1 + k * 2.5, x + 11, y + 2 + k * 2.5), 'paper', gain=0.6, outline=False)


def swap_arrows(c, x, y):
    """すり替えの印: 向き合う 2 本の金の矢。"""
    for s, yy in ((1, y), (-1, y + 10)):
        c.paint(capsule(x - 18, yy, x + 18, yy, 1.4), 'gold', gain=1.0, spec=0.5)
        tx = x + 18 * s
        c.paint(poly([(tx, yy - 5), (tx + 7 * s, yy), (tx, yy + 5)]), 'gold', gain=1.1, spec=0.5)


def gate_bars(c, x0, x1, top, base):
    """鉄の門扉（先の尖った金の飾り）。"""
    for x in range(int(x0) + 2, int(x1), 8):
        c.paint(capsule(x, base, x, top + 4, 1.2), 'silver', gain=0.7, spec=0.4)
        c.paint(poly([(x - 2, top + 5), (x + 2, top + 5), (x, top - 2)]), 'gold', gain=1.0, spec=0.6)
    for y in (top + 12, base - 10):
        c.paint(rect(x0, y, x1, y + 2), 'silver', gain=0.7, spec=0.4)


def held_map_flat(c, x, y):
    """卓に広げた地図（道筋の赤い線と印）。"""
    c.paint(poly([(x - 30, y - 6), (x + 26, y - 9), (x + 30, y + 10), (x - 32, y + 12)], UP), 'paper', gain=1.05,
            tex=lambda px, py: -0.06 if (px + py * 3) % 13 == 0 else 0)
    pts = [(x - 22, y + 6), (x - 8, y), (x + 4, y + 4), (x + 18, y - 3)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'red', gain=1.1, outline=False)
    c.paint(ellipse(x + 18, y - 3, 2.5, 1.5), 'red', gain=1.2)


def necklace_on(c, x, y):
    """胸元の首飾り（金の粒と紅玉）。"""
    for px, py in arc_points(x, y - 6, 8, 0.4, math.pi - 0.4, 8):
        c.dot(int(px), int(py), 'G5')
    gem(c, x, y + 3, 2.5, 'red')


def _gem_bench_scaled(c, x, y, k):
    c.paint(rect(x - 6 * k, y - 12 * k, x + 6 * k, y, nrm(-0.3, 0, 1)), 'silver', gain=0.8, spec=0.4)
    c.paint(rect(x - 10 * k, y - 15 * k, x + 10 * k, y - 11 * k, UP), 'silver', gain=1.0, spec=0.5)
    gem(c, x, y - 21 * k, 7 * k, 'green')
    c.paint(capsule(x + 18 * k, y - 4 * k, x + 52 * k, y - 10 * k, 1.6 * k), 'silver', gain=0.95, spec=0.6)
    c.paint(capsule(x + 46 * k, y - 9 * k, x + 58 * k, y - 11 * k, 2 * k), 'wood', gain=1.0)
    lx, ly = x - 36 * k, y - 8 * k
    c.paint(ellipse(lx, ly, 9 * k, 9 * k), 'gold', spec=0.6)
    c.paint(ellipse(lx, ly, 6.5 * k, 6.5 * k), 'water', emit=lambda px, py, n: 0.45 + (0.35 if (px - lx) + (py - ly) < -2 else 0), outline=False)
    c.paint(capsule(lx + 6 * k, ly + 6 * k, lx + 16 * k, ly + 14 * k, 1.6 * k), 'wood', gain=1.0)
    for i in range(8):
        c.dot(int(x - 10 * k + i * 3), int(y + 3 + (i % 2)), 'E3')
    gem(c, x + 30 * k, y + 8 * k, 5 * k, 'red')
    gem(c, x + 50 * k, y + 10 * k, 4 * k, 'blue')


def table_cloth(c, y, ramp='purple'):
    """卓に広げた布（手前いっぱい）。"""
    pix = [(x, yy, UP) for yy in range(int(y), H) for x in range(W)]
    c.paint(pix, ramp, gain=0.75, dither=True, outline=False,
            tex=lambda px, py: -0.06 if int(px + 4 * math.sin(py / 5.0)) % 18 == 0 else 0)


# ================= 海辺（seaside）で足した部品 =================

def sea(c, y0, y1=H, gain=1.0, moon_x=None):
    """沖へ続く海: 奥ほど細い波の帯、光だまりの下と月の下に光の道。"""
    lt = c.light
    pix = [(x, y, FLAT) for y in range(int(y0), int(y1)) for x in range(W)]

    def emit(x, y, n):
        d = y - y0 + 1
        band = math.sin(math.log(d) * 9 + math.sin(x / (6 + d * 0.3)) * 1.8)
        L = (0.14 + 0.35 * lt.att(x, y) + lt.glow(x, y0 - d * 0.3) * 0.9) * gain
        if moon_x is not None and abs(x - moon_x + (hsh(int(y), 3) - 0.5) * d * 0.2) < 2 + d * 0.12 and band > 0.55:
            L += 0.4
        return L + (0.08 if band > 0.7 else -0.04 if band < -0.6 else 0)
    return c.paint(pix, 'water', emit=emit, dither=True, outline=False)


def beach(c, y0, wave=2.0, gain=0.85, seed=0):
    """砂浜: 波打ち際の白い泡の線と、ゆるい起伏。"""
    pix = []
    for x in range(W):
        top = y0 + wave * math.sin(x / 23 + seed) + 1.2 * math.sin(x / 9 + seed)
        for y in range(max(0, int(top)), H):
            pix.append((x, y, nrm(0.1 * math.cos(x / 23), -1, 0.6)))
    o = c.paint(pix, 'sand', gain=gain, dither=True, outline=False,
                tex=lambda px, py: -0.05 if (px * 3 + py * 7) % 17 == 0 else 0)
    for x in range(W):
        top = y0 + wave * math.sin(x / 23 + seed) + 1.2 * math.sin(x / 9 + seed)
        if (x // 5) % 3 != 2:
            c.dot(x, int(top), 'S2')
    return o


def ship(c, x, wl, s=1.0, sails='paper', hull='wood', masts=2, flag='red', kind='merchant', gain=1.0, dep=0.0):
    """帆船（横から）: 船首は左、船尾楼は右。マストに張った帆、旗、灯のともる窓。
    kind: merchant（交易船）/ pirate（私掠船・赤い帆と髑髏の旗）/ ghost（霧の船・灯なし）。"""
    k = s
    L = 120 * k
    x0, x1 = x - L / 2, x + L / 2
    hull_pts = [(x0 - 6 * k, wl - 22 * k), (x1 - 8 * k, wl - 24 * k), (x1, wl - 40 * k), (x1 + 6 * k, wl - 40 * k), (x1 + 4 * k, wl - 20 * k),
                (x1 - 6 * k, wl + 4 * k), (x0 + 20 * k, wl + 6 * k), (x0 + 4 * k, wl - 6 * k)]
    # マストと帆（船体より奥）
    mx = [x - 30 * k, x + 14 * k, x + 50 * k][:masts] if masts > 1 else [x]
    for i, m in enumerate(mx):
        top = wl - (110 - i * 8) * k
        c.paint(capsule(m, wl - 20 * k, m, top, 1.6 * k), 'wood', gain=gain * 0.95, depth=dep)
        for j, (yy, ww, hh) in enumerate(((top + 14 * k, 26 * k, 26 * k), (top + 44 * k, 32 * k, 30 * k))):
            if kind == 'longship' and j == 0:
                continue
            pts = [(m - ww, yy), (m + ww, yy), (m + ww + 4 * k, yy + hh), (m - ww + 4 * k, yy + hh)]
            col = sails
            wave = lambda px, py, m=m, ww=ww: nrm(0.5 * math.sin((px - m) / ww * 2.6) - 0.15, -0.1, 0.8)
            if kind == 'longship':
                o = c.obj()
                for px, py, n in poly(pts, wave):
                    c.paint([(px, py, n)], 'red' if int((px - m + ww) / (7 * k)) % 2 == 0 else 'paper', oid=o, gain=gain, depth=dep)
            else:
                c.paint(poly(pts, wave), col, gain=gain, depth=dep)
            c.paint(capsule(m - ww - 2, yy, m + ww + 2, yy, 1.1 * k), 'wood', gain=gain, depth=dep)
        if kind != 'longship':
            fl = 'stone' if kind == 'pirate' else flag
            c.paint(poly([(m, top), (m + 16 * k, top + 3 * k), (m, top + 7 * k)], nrm(-0.3, 0, 1)), fl, gain=gain * (0.6 if kind == 'pirate' else 1.0), depth=dep)
            if kind == 'pirate':
                c.dot(int(m + 5 * k), int(top + 3 * k), 'S3')
    # 帆綱
    c.paint(capsule(x0 - 30 * k, wl - 34 * k, mx[0], wl - 104 * k, 0.5), 'paper', gain=0.55, outline=False, depth=dep)
    c.paint(capsule(x0 - 6 * k, wl - 22 * k, x0 - 36 * k, wl - 32 * k, 1.4 * k), 'wood', gain=gain, depth=dep)
    o = c.paint(poly(hull_pts, lambda px, py: nrm(-0.15, (py - wl + 10 * k) / (30 * k) * 0.9, 0.7)), hull, gain=gain, depth=dep,
                tex=lambda px, py: -0.1 if int(py - wl) % int(max(2, 5 * k)) == 0 else 0)
    c.paint(capsule(x0 - 4 * k, wl - 23 * k, x1 - 6 * k, wl - 25 * k, 1.4 * k), 'gold' if kind != 'ghost' else hull, gain=gain * 0.9, depth=dep, outline=False)
    if kind != 'ghost':
        for i in range(6):
            px = x0 + 22 * k + i * 14 * k
            c.paint(rect(px, wl - 14 * k, px + 4 * k, wl - 10 * k), 'stone', oid=o, emit=0.05, outline=False)
        for i in range(2):
            window(c, x1 - 10 * k + i * 6 * k, wl - 36 * k, 4 * k, 5 * k, True, oid=o)
    if kind == 'longship':
        for i in range(7):
            px = x0 + 16 * k + i * 14 * k
            c.paint(ellipse(px, wl - 20 * k, 5 * k, 5 * k), ('red', 'gold', 'blue')[i % 3], gain=gain, spec=0.3, depth=dep)
            c.paint(capsule(px + 2, wl - 14 * k, px - 10 * k, wl + 8 * k, 0.9 * k), 'wood', gain=gain * 0.9, depth=dep)
    return o


def foam(c, x0, x1, y):
    """船や岩の根もとに立つ白い波頭。"""
    for x in range(int(x0), int(x1)):
        if (x // 3) % 4 != 3:
            c.dot(x, int(y + math.sin(x / 4) * 1.2), 'S2')
            if x % 5 == 0:
                c.dot(x, int(y + 1 + math.sin(x / 4) * 1.2), 'S1')


def boat(c, x, wl, w=50, ramp='wood', gain=1.0, oars=False):
    """小舟（横から）。"""
    pts = [(x - w / 2, wl - 10), (x + w / 2, wl - 10), (x + w / 2 - 6, wl + 2), (x - w / 2 + 8, wl + 2)]
    o = c.paint(poly(pts, lambda px, py: nrm(-0.15, (py - wl + 4) / 8 * 0.8, 0.7)), ramp, gain=gain,
                tex=lambda px, py: -0.1 if int(py - wl) % 4 == 0 else 0)
    c.paint(capsule(x - w / 2, wl - 10, x + w / 2, wl - 10, 1.2), ramp, gain=gain * 1.2)
    if oars:
        c.paint(capsule(x - 6, wl - 12, x - 26, wl + 6, 1.0), 'wood', gain=gain * 0.9)
    foam(c, x - w / 2 + 6, x + w / 2 - 4, wl + 2)
    return o


def dock(c, y, x0=0, x1=W, posts=True):
    """手前の桟橋の板（横板が奥へ）と杭。"""
    pix = [(x, yy, UP) for yy in range(int(y), H) for x in range(int(x0), int(x1))]
    c.paint(pix, 'wood', gain=0.95, dither=True, outline=False,
            tex=lambda px, py: -0.12 if int(px - x0) % 12 == 0 else (-0.04 if (px + py * 3) % 11 == 0 else 0))
    if posts:
        for px in (x0 + 6, x1 - 10):
            c.paint(vcyl(px + 2, y - 10, y + 6, 4, 1.5), 'wood', gain=1.0)


def long_pier(c, x, y0, y1, w0=10, w1=80):
    """沖へ伸びる長い桟橋（遠近）。杭が等間隔に立つ。"""
    pts = [(x - w0 / 2, y0), (x + w0 / 2, y0), (x + w1 / 2, y1), (x - w1 / 2, y1)]
    c.paint(poly(pts, UP), 'wood', gain=1.0, tex=lambda px, py: -0.1 if int(math.log(max(1, py - y0 + 2)) * 9) % 2 == 0 else 0)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = y0 + (y1 - y0) * t
        ww = (w0 + (w1 - w0) * t) / 2
        r = 1 + 3 * t
        for s in (-1, 1):
            c.paint(vcyl(x + s * ww, yy - 6 - 10 * t, yy + 4 * t, r, r * 0.4), 'wood', gain=1.0 if s < 0 else 0.8)


def nets(c, x0, x1, top, base):
    """干した網（菱目の線）と浮き。"""
    for k in range(int((x1 - x0) / 6) + 1):
        xx = x0 + k * 6
        c.paint(capsule(xx, top, xx + 10, base, 0.4), 'paper', gain=0.6, outline=False)
        c.paint(capsule(xx + 10, top, xx, base, 0.4), 'paper', gain=0.55, outline=False)
    c.paint(capsule(x0 - 2, top, x1 + 2, top, 1.2), 'wood', gain=1.0)
    for k in range(4):
        c.paint(ellipse(x0 + 8 + k * (x1 - x0 - 16) / 3, base - 2, 3, 3), 'red', gain=1.0, spec=0.4)


def fish_rack(c, x, base, w=60):
    """魚を干す竿掛け。"""
    for s in (0, w):
        c.paint(capsule(x + s, base, x + s, base - 40, 1.6), 'wood', gain=0.95)
    c.paint(capsule(x - 3, base - 38, x + w + 3, base - 38, 1.4), 'wood', gain=1.0)
    for k in range(6):
        fx = x + 6 + k * (w - 12) / 5
        c.paint(rect(fx, base - 38, fx + 1, base - 33), 'paper', gain=0.6, outline=False)
        c.paint(ellipse(fx, base - 25, 2.6, 7), 'silver', spec=0.6)
        c.paint(poly([(fx - 3, base - 17), (fx + 3, base - 17), (fx, base - 20)]), 'silver', gain=0.8)


def palm(c, x, base, h=60, lean=0.25):
    """椰子の木: しなる幹の節と、垂れる葉。"""
    pts = [(x + lean * h * (t ** 1.5), base - h * t) for t in [i / 10 for i in range(11)]]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], 3.0 - i * 0.12), 'wood', gain=1.0 if i % 2 else 0.85)
    tx, ty = pts[-1]
    for k in range(7):
        a = -math.pi + k * math.pi / 6
        fp = [(tx + math.cos(a) * h * 0.4 * t, ty + math.sin(a) * h * 0.18 * t + (t ** 2) * h * 0.18) for t in [i / 6 for i in range(7)]]
        for j, (p, q) in enumerate(zip(fp, fp[1:])):
            c.paint(capsule(p[0], p[1], q[0], q[1], 2.6 - j * 0.35), 'foliage', gain=1.0)
    c.paint(ellipse(tx, ty + 3, 3, 3), 'leather', gain=0.9)


def hut(c, x, base, w=34, h=20):
    """草葺きの小屋。"""
    c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.3, 0, 1)), 'wood', gain=0.9,
            tex=lambda px, py: -0.08 if int(px) % 5 == 0 else 0)
    c.paint(poly([(x - w / 2 - 6, base - h + 2), (x + w / 2 + 6, base - h + 2), (x, base - h - 18)],
                 lambda px, py: nrm((px - x) / w * 0.8, -0.4, 0.7)), 'sand', gain=1.0,
            tex=lambda px, py: -0.1 if (int(px) + int(py)) % 4 == 0 else 0)
    window(c, x - 4, base - h + 6, 7, 7, True)


def island(c, x, wl, w=110, h=26):
    """海に浮かぶ小島（岩の縁、草の頂）。"""
    pts = [(x - w / 2, wl + 2)] + [(x - w / 2 + w * t, wl - h * math.sin(t * math.pi) ** 0.7 - (3 if 0.3 < t < 0.5 else 0)) for t in [i / 12 for i in range(1, 12)]] + [(x + w / 2, wl + 2)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 1.2, -0.6, 0.7)), 'sand', gain=0.95)
    gpts = [(x - w * 0.36 + w * 0.72 * t, wl - h * math.sin((0.14 + 0.72 * t) * math.pi) ** 0.7 - 2) for t in [i / 10 for i in range(11)]]
    c.paint(poly(gpts + [(x + w * 0.3, wl - h * 0.5), (x - w * 0.3, wl - h * 0.5)], nrm(-0.2, -0.8, 0.6)), 'foliage', gain=0.9)
    foam(c, x - w / 2, x + w / 2, wl + 2)


def beacon_tower(c, x, base, h=60):
    """岬のかがり火台: 石の塔の上で大きな火が燃える。"""
    c.paint(poly([(x - 16, base), (x + 16, base), (x + 11, base - h), (x - 11, base - h)], lambda px, py: nrm((px - x) / 16 * 0.8, 0, 0.7)), 'stone', gain=1.0,
            tex=lambda px, py: -0.1 if (int(py) % 7 == 0 or (int(px) + (int(py) // 7) * 5) % 9 == 0) else 0)
    c.paint(ellipse(x, base - h, 17, 6, clip=lambda px, py: py >= base - h - 1), 'silver', gain=0.8, spec=0.4)
    for k in range(6):
        flame(c, x - 12 + k * 5, base - h - 10 - 6 * hsh(k, 7), 4.2, 10 + 5 * hsh(k, 3))
    flame(c, x, base - h - 22, 6, 14)


def monkey(c, x, y, s=1.0):
    """手長猿: 長い腕で綱にぶら下がり、片手を伸ばす。"""
    k = s
    hx, hy = x, y
    c.paint(capsule(hx - 4 * k, hy - 30 * k, hx - 2 * k, hy - 4 * k, 2.2 * k, 2.6 * k), 'leather', gain=1.0)
    c.paint(capsule(hx + 2 * k, hy - 4 * k, hx + 26 * k, hy + 2 * k, 2.6 * k, 2.0 * k), 'leather', gain=0.9)
    c.paint(ellipse(hx + 28 * k, hy + 2 * k, 2.6 * k, 2.4 * k), 'leather', gain=1.2)
    c.paint(ellipse(hx + 1 * k, hy + 14 * k, 8 * k, 12 * k), 'leather', gain=1.0)
    c.paint(capsule(hx - 4 * k, hy + 22 * k, hx - 10 * k, hy + 38 * k, 2.4 * k), 'leather', gain=0.95)
    c.paint(capsule(hx + 6 * k, hy + 22 * k, hx + 12 * k, hy + 36 * k, 2.4 * k), 'leather', gain=0.8)
    pts = [(hx + 6 * k, hy + 22 * k), (hx + 18 * k, hy + 30 * k), (hx + 22 * k, hy + 22 * k), (hx + 18 * k, hy + 16 * k)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.2 * k), 'leather', gain=0.9)
    c.paint(ellipse(hx, hy - 2 * k, 7 * k, 7 * k), 'leather', gain=1.05)
    c.paint(ellipse(hx + 1.5 * k, hy, 4.5 * k, 4 * k), 'skin', gain=1.1)
    for ex in (-1.6, 2.4):
        c.dot(int(hx + ex * k), int(hy - 1 * k), 'N0')
    c.paint(ellipse(hx - 4 * k, hy - 31 * k, 2.4 * k, 2.4 * k), 'leather', gain=1.2)


def horse(c, x, base, s=1.0, ramp='leather', facing=1, blanket=None, gallop=False):
    """馬（横から、顔は左）。胴は胸・腹・尻の 3 つのふくらみ、脚は腿と脛の 2 節で膝が曲がり、
    首は弓なりの面、頭は額から鼻先へ細る。たてがみと尾は毛の束。gallop で駆け足の脚。"""
    k = s
    f = facing
    X = lambda dx: x + f * -dx * k  # dx>0 で頭の側
    by = base - 44 * k

    def leg(hip, knee, fet, g, r0=4.2):
        hx, hy = X(hip[0]), by + hip[1] * k
        kx, ky = X(knee[0]), by + knee[1] * k
        fx, fy = X(fet[0]), by + fet[1] * k
        c.paint(capsule(hx, hy, kx, ky, r0 * k, 2.4 * k), ramp, gain=g)
        c.paint(capsule(kx, ky, fx, fy, 2.2 * k, 1.7 * k), ramp, gain=g)
        c.paint(ellipse(fx - f * 0.8 * k, fy + 1.4 * k, 2.6 * k, 1.8 * k), 'hair', gain=0.8)
    foot = 43
    if gallop:
        back = [((-16, 4), (-30, 22), (-44, 34)), ((-20, 4), (-22, 24), (-34, 40))]
        front = [((18, 4), (34, 10), (30, 24)), ((14, 4), (26, 22), (14, 36))]
    else:
        back = [((-16, 4), (-22, 24), (-19, foot)), ((-22, 4), (-26, 24), (-24, foot))]
        front = [((18, 4), (19, 24), (19, foot)), ((13, 4), (14, 24), (12, foot))]
    leg(*back[0], 0.7)
    leg(*front[0], 0.75)
    # 尾（毛の束が流れる）
    for i in range(4):
        sway = (i - 1.5) * 1.6
        pts = [(X(-28), by - 4 * k)] + [(X(-30 - t * 10 - (8 * t if gallop else 0)), by - 4 * k + t * (28 if not gallop else 16) * k + sway * t * k) for t in (0.33, 0.66, 1.0)]
        for a2, b2 in zip(pts, pts[1:]):
            c.paint(capsule(a2[0], a2[1], b2[0], b2[1], 2.0 * k, 1.2 * k), 'hair', gain=0.9 + 0.05 * i, outline=False)
    o = c.obj()
    c.paint(ellipse(X(-18), by - 2 * k, 13 * k, 13 * k), ramp, oid=o, gain=0.95)
    c.paint(ellipse(X(0), by, 24 * k, 12 * k), ramp, oid=o, gain=1.0)
    c.paint(ellipse(X(17), by - 1 * k, 11 * k, 12.5 * k), ramp, oid=o, gain=1.05)
    # 首（弓なりの面）と頭
    neck = [(X(10), by - 6 * k), (X(18), by - 26 * k), (X(26), by - 36 * k), (X(32), by - 34 * k), (X(30), by - 24 * k), (X(27), by + 2 * k)]
    c.paint(poly(neck, lambda px, py: nrm(-0.25, -0.35, 0.85)), ramp, gain=1.05)
    head = [(X(28), by - 38 * k), (X(34), by - 39 * k), (X(46), by - 26 * k), (X(47), by - 21 * k), (X(42), by - 19 * k), (X(30), by - 26 * k)]
    c.paint(poly(head, lambda px, py: nrm(-0.2, -0.4, 0.85)), ramp, gain=1.1)
    c.paint(ellipse(X(31), by - 28 * k, 3.5 * k, 3.2 * k), ramp, gain=1.0, outline=False)
    for dx in (28, 31):
        c.paint(poly([(X(dx), by - 37 * k), (X(dx + 3), by - 38 * k), (X(dx + 1), by - 45 * k)], nrm(-0.3, -0.4, 0.8)), ramp, gain=1.0)
    c.dot(int(X(35)), int(by - 33 * k), 'N0')
    c.dot(int(X(45)), int(by - 22 * k), 'N0')
    for i in range(7):
        t = i / 6
        mx, my = X(26 - t * 14), by - (37 - t * 30) * k
        c.paint(capsule(mx, my, mx + f * (3 + 3 * t) * k, my + (4 + 2 * t) * k, 1.6 * k, 0.8 * k), 'hair', gain=1.0, outline=False)
    if blanket:  # 馬着（金の縁の布）
        c.paint(poly([(X(22), by - 10 * k), (X(-22), by - 10 * k), (X(-26), by + 12 * k), (X(26), by + 12 * k)],
                     lambda px, py: nrm(0.3 * math.sin(px / 3), 0, 0.9)), blanket, gain=1.0)
        c.paint(rect(min(X(26), X(-26)), by + 10 * k, max(X(26), X(-26)), by + 13 * k), 'gold', gain=1.0, outline=False)
    leg(*back[1], 1.0)
    leg(*front[1], 1.05)


def wagon(c, x, base, w=70, cover='paper'):
    """幌つきの荷馬車（大きな車輪 2 つ）。"""
    c.paint(rect(x - w / 2, base - 30, x + w / 2, base - 16, nrm(-0.2, 0, 1)), 'wood', gain=1.0,
            tex=lambda px, py: -0.1 if int(py) % 4 == 0 else 0)
    pts = [(x - w / 2 + 2, base - 30)] + arc_points(x, base - 30, w / 2 - 2, math.pi, 2 * math.pi, 14)[1:-1] + [(x + w / 2 - 2, base - 30)]
    pts = [(px, base - 30 - (base - 30 - py) * 0.8) for px, py in pts]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 1.2, -0.4, 0.7)), cover, gain=0.95,
            tex=lambda px, py: -0.07 if int(px - x) % 12 == 0 else 0)
    for wx in (x - w * 0.3, x + w * 0.3):
        pts = arc_points(wx, base - 12, 12, 0, math.pi * 2, 20)
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.4), 'wood', gain=1.0)
        for kk in range(6):
            a = kk * math.pi / 3
            c.paint(capsule(wx, base - 12, wx + math.cos(a) * 12, base - 12 + math.sin(a) * 12, 0.8), 'wood', gain=0.85)
        c.paint(ellipse(wx, base - 12, 2.4, 2.4), 'silver', gain=1.0)


def compass_rose(c, x, y, r=40):
    """羅針盤: 真鍮の枠、文字盤の方位の星、北を指す紅の針、ガラスの照り。"""
    c.paint(ellipse(x, y + 4, r + 4, (r + 4) * 0.72), 'gold', gain=0.6)
    c.paint(ellipse(x, y, r + 4, (r + 4) * 0.72), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x, y, r, r * 0.72, normal=UP), 'paper', gain=1.0)
    for kk in range(8):
        a = kk * math.pi / 4 - math.pi / 2
        ln = r * (0.85 if kk % 2 == 0 else 0.5)
        tip = (x + math.cos(a) * ln, y + math.sin(a) * ln * 0.72)
        side = (a + math.pi / 2)
        w = r * 0.1
        for sgn, g in ((1, 0.9), (-1, 0.55)):
            c.paint(poly([(x, y), tip, (x + math.cos(side) * w * sgn, y + math.sin(side) * w * sgn * 0.72)]), 'leather', gain=g, outline=False)
    c.paint(poly([(x - 3, y), (x + 3, y), (x, y - r * 0.8 * 0.72)]), 'red', gain=1.2, outline=False)
    c.paint(poly([(x - 3, y), (x + 3, y), (x, y + r * 0.8 * 0.72)]), 'silver', gain=1.0, outline=False)
    c.paint(ellipse(x, y, 3, 2.4), 'gold', spec=0.7)
    for kk in range(4):
        a = -2.4 + kk * 0.12
        c.dot(int(x + math.cos(a) * r * 0.75), int(y + math.sin(a) * r * 0.75 * 0.72), 'S3')


def sea_chart(c, x, y, w=150, h=56):
    """海図: 卓の上に広げた紙、海岸線、点線の航路、方位の印。"""
    pts = [(x - w / 2, y - h / 2), (x + w / 2 - 4, y - h / 2 - 3), (x + w / 2 + 6, y + h / 2), (x - w / 2 - 6, y + h / 2 + 2)]
    c.paint(poly(pts, UP), 'paper', gain=1.05, tex=lambda px, py: -0.05 if (px * 2 + py * 5) % 19 == 0 else 0)
    coast = [(x - w / 2 + 6, y - 8), (x - w / 4, y - 14), (x - w / 6, y - 2), (x - w / 3, y + 14), (x - w / 2 + 4, y + 18)]
    for a, b in zip(coast, coast[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.8), 'leather', gain=1.0, outline=False)
    island_pts = [(x + w / 5, y - 10), (x + w / 4 + 10, y - 12), (x + w / 4 + 14, y - 2), (x + w / 5, y)]
    c.paint(poly(island_pts), 'sand', gain=0.7, outline=False)
    route = [(x - w / 6 + 4, y + 2), (x, y + 12), (x + w / 6, y + 4), (x + w / 4, y - 4)]
    for a, b in zip(route, route[1:]):
        for t in range(0, 10, 2):
            t0, t1 = t / 10, (t + 1) / 10
            c.paint(capsule(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0, a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1, 0.7), 'red', gain=1.1, outline=False)
    rx, ry = x + w / 3, y + h / 4
    for kk in range(4):
        a = kk * math.pi / 2
        c.paint(capsule(rx, ry, rx + math.cos(a) * 8, ry + math.sin(a) * 6, 0.7), 'leather', gain=0.9, outline=False)


def dividers(c, x, y, ln=40):
    """測りの両脚器（真鍮の 2 本脚）。"""
    c.paint(capsule(x, y - ln, x - 12, y, 1.2), 'gold', spec=0.7)
    c.paint(capsule(x, y - ln, x + 10, y + 2, 1.2), 'gold', gain=0.85, spec=0.6)
    c.paint(ellipse(x, y - ln, 2.6, 2.6), 'gold', spec=0.7)


def map_pieces(c, x, y):
    """破れた宝の絵図 2 枚: 合わせ目がぎざぎざ、点線の道と赤い ✕。"""
    jag = [(x + (3 if i % 2 else -1), y - 30 + i * 6) for i in range(11)]
    left = [(x - 54, y - 28), (x - 4, y - 32)] + jag + [(x - 2, y + 30), (x - 56, y + 28)]
    right = [(x + 8, y - 34), (x + 58, y - 30), (x + 60, y + 30), (x + 6, y + 28)] + [(px + 8, py - 2) for px, py in reversed(jag)]
    for pts, g in ((left, 1.05), (right, 0.95)):
        c.paint(poly(pts, nrm(-0.2, -0.5, 0.8)), 'paper', gain=g, tex=lambda px, py: -0.06 if (px + py * 3) % 13 == 0 else 0)
    route = [(x - 40, y + 18), (x - 24, y + 4), (x - 10, y + 10), (x + 14, y - 2), (x + 32, y - 10)]
    for a2, b2 in zip(route, route[1:]):
        for t in range(0, 10, 3):
            t0, t1 = t / 10, (t + 1.5) / 10
            c.paint(capsule(a2[0] + (b2[0] - a2[0]) * t0, a2[1] + (b2[1] - a2[1]) * t0, a2[0] + (b2[0] - a2[0]) * t1, a2[1] + (b2[1] - a2[1]) * t1, 0.7),
                    'leather', gain=0.9, outline=False)
    cx, cy = x + 38, y - 12
    c.paint(capsule(cx - 6, cy - 6, cx + 6, cy + 6, 1.6), 'red', gain=1.2, outline=False)
    c.paint(capsule(cx - 6, cy + 6, cx + 6, cy - 6, 1.6), 'red', gain=1.2, outline=False)
    c.paint(capsule(x - 46, y - 18, x - 30, y - 18, 3.5), 'leather', gain=0.8)


def barricade(c, x, base, w=140):
    """通せんぼ: 交差した杭の柵（先が尖る）と、積んだ木箱。"""
    c.paint(capsule(x - w / 2, base - 18, x + w / 2, base - 18, 3, flat=0.3), 'wood', gain=1.0)
    for kk in range(7):
        px = x - w / 2 + 10 + kk * (w - 20) / 6
        for s in (-1, 1):
            tip = (px + s * 14, base - 44)
            c.paint(capsule(px - s * 10, base, tip[0], tip[1], 2.2, 1.5), 'wood', gain=1.0 if s < 0 else 0.8)
            c.paint(poly([(tip[0] - 2, tip[1] + 2), (tip[0] + 2, tip[1] + 2), (tip[0] + s * 3, tip[1] - 5)]), 'silver', gain=1.0, spec=0.5)


def starfish(c, x, y, r=8, ramp='red'):
    pts = []
    for kk in range(10):
        a = kk * math.pi / 5 - math.pi / 2
        rr = r if kk % 2 == 0 else r * 0.42
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7))
    c.paint(poly(pts, lambda px, py: nrm((px - x) / r * 0.6, (py - y) / r * 0.6, 0.8)), ramp, gain=1.1)


def crab(c, x, y, s=1.0):
    k = s
    for sgn in (-1, 1):
        for i in range(3):
            c.paint(capsule(x + sgn * 6 * k, y + i * 2 * k, x + sgn * 13 * k, y + 4 * k + i * 3 * k, 0.9 * k), 'red', gain=0.85)
        c.paint(capsule(x + sgn * 7 * k, y - 3 * k, x + sgn * 13 * k, y - 10 * k, 1.3 * k), 'red', gain=1.0)
        c.paint(ellipse(x + sgn * 14 * k, y - 12 * k, 3.2 * k, 2.6 * k), 'red', gain=1.1, spec=0.4)
    c.paint(ellipse(x, y, 9 * k, 6 * k), 'red', gain=1.05, spec=0.4)
    for sgn in (-1, 1):
        c.dot(int(x + sgn * 3 * k), int(y - 6 * k), 'N0')


def shell(c, x, y, r=5):
    pts = [(x, y + r * 0.6)] + arc_points(x, y, r, math.pi * 1.05, math.pi * 1.95, 8)
    c.paint(poly(pts, nrm(-0.3, -0.5, 0.8)), 'paper', gain=1.1)
    for kk in range(4):
        a = math.pi * (1.15 + kk * 0.23)
        c.paint(capsule(x, y + r * 0.6, x + math.cos(a) * r, y + math.sin(a) * r, 0.4), 'leather', gain=0.8, outline=False)


def rocks(c, pts, ramp='stone', gain=0.9):
    """岩の塊（左上の面が明るい）。pts: (x, 底, 幅, 高さ)"""
    for x, base, w, h in pts:
        poly_pts = [(x - w / 2, base), (x - w * 0.42, base - h * 0.6), (x - w * 0.15, base - h), (x + w * 0.25, base - h * 0.9), (x + w / 2, base - h * 0.3), (x + w * 0.45, base)]
        c.paint(poly(poly_pts, lambda px, py, x=x, w=w, h=h, b=base: nrm((px - x) / w * 1.0 - 0.2, (py - b + h * 0.6) / h * 0.9, 0.7)), ramp, gain=gain,
                tex=lambda px, py: -0.08 if (px * 5 + py * 3) % 11 == 0 else 0)


def seaweed(c, x, base, h=24):
    for kk in range(3):
        pts = [(x + kk * 4 + math.sin(t * 5 + kk) * 3, base - h * t) for t in [i / 8 for i in range(9)]]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.2), 'foliage', gain=1.0, outline=False)


def tide_pool(c, x, y, rx=70, ry=16):
    """岩に囲まれた潮だまり（澄んだ水と底の砂）。"""
    lt = c.light
    c.paint(ellipse(x, y, rx, ry), 'water', emit=lambda px, py, n: 0.3 + 0.35 * lt.att(px, py) + (0.12 if (int(px / 5) + int(py)) % 5 == 0 else 0))


def vault_door(c, x, base, w=70, h=96):
    """金蔵の扉: 開いた厚い鉄扉（鋲・輪のハンドル）、奥の棚に金の山。"""
    top = base - h
    c.paint(rect(x - w / 2 - 6, top - 6, x + w / 2 + 6, base, nrm(-0.2, 0, 1)), 'stone', gain=1.0)
    c.paint(rect(x - w / 2, top, x + w / 2, base), 'stone', emit=0.08, outline=False)
    for row in range(3):
        y = top + 26 + row * 28
        c.paint(rect(x - w / 2, y, x + w / 2, y + 3, UP), 'wood', gain=0.9)
        for kk in range(4):
            coin_stack(c, x - w / 2 + 10 + kk * 16, y, 6, 3 + (kk + row) % 3, 'gold', seed=row * 4 + kk)
    pts = [(x + w / 2, top), (x + w / 2 + 40, top + 10), (x + w / 2 + 40, base + 4), (x + w / 2, base)]
    o = c.paint(poly(pts, nrm(0.6, 0, 0.8)), 'silver', gain=0.75, spec=0.3)
    for yy in range(int(top + 8), int(base), 10):
        for xx in (x + w / 2 + 6, x + w / 2 + 34):
            c.dot(int(xx), int(yy + (xx - x - w / 2) * 0.25), 'S2')
    hx, hy = x + w / 2 + 22, top + h * 0.5
    pts = arc_points(hx, hy, 9, 0, math.pi * 2, 16)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.4), 'gold', spec=0.6)


def sea_fort(c, x, base):
    """海の出城: 岩の上の円い砦、旗、灯の窓。"""
    rocks(c, [(x, base + 6, 120, 26), (x - 50, base + 8, 50, 16), (x + 52, base + 8, 46, 14)], gain=0.85)
    crenel_wall(c, x - 46, x + 46, base - 34, base - 4, merlon=6, gap=4, gain=0.9)
    tower(c, x - 18, base - 20, 36, 70, roof=None, crenel=True, windows=[(-2, 18, 4, 7), (-2, 40, 4, 7)])
    c.paint(rect(x - 1, base - 108, x, base - 92), 'wood', gain=0.9)
    c.paint(poly([(x, base - 108), (x + 14, base - 105), (x, base - 101)], nrm(-0.3, 0, 1)), 'blue', gain=1.0)
    foam(c, x - 70, x + 80, base + 6)


def wall_map(c, x0, y0, x1, y1):
    """壁に掛けた沿岸の地図と、刺した印のピン。"""
    c.paint(rect(x0, y0, x1, y1, nrm(-0.1, 0, 1)), 'paper', gain=1.0, tex=lambda px, py: -0.05 if (px * 3 + py) % 17 == 0 else 0)
    coast = [(x0 + 6, y0 + 8), (x0 + (x1 - x0) * 0.3, y0 + 18), (x0 + (x1 - x0) * 0.45, y0 + 10), (x0 + (x1 - x0) * 0.6, y1 - 12), (x1 - 6, y1 - 6)]
    for a, b in zip(coast, coast[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.9), 'leather', gain=0.9, outline=False)
    c.paint(poly([(x0, y0 + 20)] + coast[1:4] + [(x0 + (x1 - x0) * 0.4, y1), (x0, y1)]), 'water', emit=0.35, outline=False)
    for kk, (px, py, col) in enumerate(((0.25, 0.4, 'R3'), (0.52, 0.55, 'B3'), (0.7, 0.35, 'R3'), (0.38, 0.75, 'G5'))):
        xx, yy = int(x0 + (x1 - x0) * px), int(y0 + (y1 - y0) * py)
        c.dot(xx, yy, col)
        c.dot(xx + 1, yy, col)
        c.dot(xx, yy + 1, 'N1')
    for xx in (x0, x1):
        c.paint(ellipse(xx, y0 - 1, 2, 2), 'gold', spec=0.5)


def mermaid_tail(c, x, y, ramp='green'):
    """水から上がる人魚の尾びれ。"""
    pts = [(x, y + 10), (x + 6, y - 6), (x + 10, y - 18)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 5, 3), ramp, gain=1.0, spec=0.4)
    tx, ty = pts[-1]
    c.paint(poly([(tx, ty), (tx - 12, ty - 12), (tx - 2, ty - 6), (tx + 4, ty - 16), (tx + 14, ty - 8)], nrm(-0.3, -0.4, 0.8)), ramp, gain=1.1, spec=0.4)


def tub(c, x, wl, r=14):
    """海女の浮き桶。"""
    c.paint(vcyl(x, wl - 10, wl, r, r * 0.3), 'wood', gain=1.0, tex=lambda px, py: -0.1 if int(px) % 4 == 0 else 0)
    c.paint(ellipse(x, wl - 10, r * 0.85, r * 0.25), 'wood', gain=0.5)
    shell(c, x - 3, wl - 12, 4)
    foam(c, x - r, x + r, wl)


def notice(c, x, top, w=50, h=58):
    """差し止めの触れ書き: 柱に打ちつけた紙、赤い大きな封印、交差した鎖。"""
    c.paint(rect(x - 3, top - 10, x + 3, H, nrm(-0.3, 0, 1)), 'wood', gain=0.95)
    o = c.paint(rect(x - w / 2, top, x + w / 2, top + h, nrm(-0.2, 0, 1)), 'paper', gain=1.1)
    for kk in range(6):
        yy = top + 8 + kk * 6
        c.paint(rect(x - w / 2 + 6, yy, x + w / 2 - 6, yy + 1.5), 'paper', oid=o, gain=0.55, outline=False)
    c.paint(ellipse(x + 8, top + h - 12, 9, 9), 'red', gain=1.05, spec=0.4)
    c.paint(ellipse(x + 8, top + h - 12, 5, 5), 'red', gain=0.75, outline=False)
    for xx in (x - w / 2 + 3, x + w / 2 - 3):
        c.paint(ellipse(xx, top + 3, 1.6, 1.6), 'silver', gain=1.0)


def chain(c, x0, y0, x1, y1, r=3):
    """鉄の鎖（輪を交互の向きで）。"""
    n = int(math.hypot(x1 - x0, y1 - y0) / (r * 1.6))
    for i in range(n + 1):
        t = i / max(1, n)
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if i % 2 == 0:
            c.paint(ellipse(cx, cy, r * 1.2, r * 0.7), 'silver', gain=0.9, spec=0.5)
            c.paint(ellipse(cx, cy, r * 0.5, r * 0.25), 'stone', emit=0.06, outline=False)
        else:
            c.paint(ellipse(cx, cy, r * 0.5, r * 0.9), 'silver', gain=0.75, spec=0.4)


def fog(c, bands, gain=1.0):
    """霧の帯（市松で透ける）。bands: (y, 厚さ)"""
    for y, th in bands:
        pix = []
        for x in range(W):
            yy = y + 3 * math.sin(x / 17 + y)
            for py in range(int(yy - th / 2), int(yy + th / 2)):
                d = abs(py - yy) / (th / 2)
                if d < 0.55 or (x + py) % 2 == 0:
                    pix.append((x, py, FLAT))
        c.paint(pix, 'stone', emit=0.42 * gain, outline=False)


def cave_mouth(c, x, base, w=90, h=80):
    """海食洞の口（暗い奥）。"""
    pts = [(x - w / 2, base)] + [(x - w / 2 + w * t, base - h * math.sin(t * math.pi) ** 0.6 - (6 if 0.4 < t < 0.6 else 0)) for t in [i / 14 for i in range(1, 14)]] + [(x + w / 2, base)]
    c.paint(poly(pts), 'stone', emit=lambda px, py, n: 0.03 + 0.04 * abs(px - x) / w, outline=False)


def spade():
    """鋤（柄の先に鉄の刃）。手で握る持ち物。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y - 1.5 * u, x + fig.f * 0.6 * u, y + 3.6 * u, 0.15 * u), 'wood')
        bx, by = x + fig.f * 0.7 * u, y + 3.8 * u
        c.paint(poly([(bx - 0.6 * u, by - 0.4 * u), (bx + 0.6 * u, by - 0.4 * u), (bx + 0.5 * u, by + 0.9 * u), (bx, by + 1.2 * u), (bx - 0.5 * u, by + 0.9 * u)],
                     nrm(-0.3, -0.2, 0.9)), 'silver', spec=0.6)
    return draw


def cutlass():
    """反りのある短い船刀。"""
    def draw(c, fig, hand):
        u = fig.u
        f = fig.f
        x, y = hand
        pts = [(x + f * (0.4 + t * 2.6) * u, y - (t * 2.4 + (t ** 2) * -0.6) * u) for t in [i / 8 for i in range(9)]]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.24 * u * (1 - i / 10)), 'silver', spec=0.8, shine=5, gain=1.05)
        c.paint(ellipse(x + f * 0.3 * u, y - 0.2 * u, 0.45 * u, 0.3 * u), 'gold', spec=0.6)
    return draw


def cane():
    """曲がった杖（老婆）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y - 0.3 * u, x + fig.f * 0.3 * u, fig.foot, 0.16 * u), 'wood')
        c.paint(capsule(x, y - 0.3 * u, x - fig.f * 0.5 * u, y - 0.6 * u, 0.16 * u), 'wood')
    return draw


def casket():
    """両手で捧げる小箱（贈り物）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.5 * u, hand[1] - 0.6 * u
        chest(c, x - 1.0 * u, y + 0.6 * u, 2.0 * u, 1.0 * u, open_=False, band='gold', lock=False)
        gem(c, x, y - 0.2 * u, 0.3 * u, 'red')
    return draw


def pearl():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] - 0.5 * u
        shell(c, x, y + 0.2 * u, 0.6 * u)
        c.paint(ellipse(x, y - 0.1 * u, 0.25 * u, 0.25 * u), 'paper', gain=1.3, spec=0.8)
    return draw


def ship_model(c, x, y):
    """卓に置いた船の模型。"""
    ship(c, x, y, s=0.28)


def smoke(c, pts):
    """砲の煙（丸い塊を重ね、段で落とす）。"""
    for i, (x, y) in enumerate(pts):
        for k in range(5):
            c.paint(ellipse(x + k * 4 - 8, y - k * 2 + (k % 2) * 3, 8 - k * 0.6, 6 - k * 0.5), 'stone', emit=0.5 - k * 0.05, outline=False, dither=True)


def ship_rail(c, y):
    """手前いっぱいの船べり（手すりと柱）。"""
    c.paint(rect(0, y, W, H, nrm(0, -0.2, 1)), 'wood', gain=0.8, tex=lambda px, py: -0.1 if int(py - y) % 6 == 0 else 0)
    c.paint(rect(0, y - 4, W, y, UP), 'wood', gain=1.1)
    for x in range(8, W, 30):
        c.paint(ellipse(x, y + 10, 2.6, 2.6), 'silver', gain=0.9)


def mast(c, x, top, base):
    c.paint(capsule(x, base, x, top, 4.5, 3.5), 'wood', gain=1.0)
    c.paint(capsule(x - 30, top + 20, x + 30, top + 20, 2), 'wood', gain=0.9)
    for dx in (-24, 24):
        c.paint(capsule(x, top + 4, x + dx, base, 0.6), 'paper', gain=0.6, outline=False)


def harness(c, x0, y0, x1, y1):
    c.paint(capsule(x0, y0, x1, y1, 1.2), 'leather', gain=1.0)
    c.paint(capsule(x0, y0 + 6, x1, y1 + 6, 1.2), 'wood', gain=0.9)


def furrows(c, y0):
    """起こした畝の筋（奥ほど細い）。"""
    for k in range(5):
        y = y0 + k * (4 + k * 1.5)
        c.paint(rect(0, y, W, y + 1 + k * 0.4, nrm(0, -0.8, 0.6)), 'leather', gain=1.1, outline=False)


def flag_pole(c, x, base, ramp='blue'):
    c.paint(capsule(x, base, x, base - 70, 1.5), 'wood', gain=1.0)
    pts = [(x, base - 70)] + [(x + 30 * t, base - 70 + 3 * math.sin(t * 5)) for t in [i / 6 for i in range(1, 7)]] + \
          [(x + 30 * t, base - 52 + 3 * math.sin(t * 5 + 0.7)) for t in [i / 6 for i in range(6, 0, -1)]] + [(x, base - 52)]
    o = c.paint(poly(pts, lambda px, py: nrm(0.5 * math.cos((px - x) / 30 * 5), 0, 0.85)), ramp, gain=1.0)
    c.paint(ellipse(x + 14, base - 61, 3.5, 3.5), 'gold', oid=o, spec=0.4)


def coil_held():
    """肩に担いだ綱の束。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] - fig.f * 0.4 * u, hand[1] + 0.6 * u
        for k in range(3):
            pts = arc_points(x, y, (1.1 - k * 0.2) * u, 0, math.pi * 2, 18)
            for a, b in zip(pts, pts[1:]):
                c.paint(capsule(a[0], a[1], b[0], b[1], 0.2 * u), 'paper', gain=0.95 - k * 0.1)
    return draw


# ================= 繁栄（prosperity）で足した部品 =================

def snow(c, n=70, seed=0, area=(0, 0, W, H)):
    """降る雪（決まった位置の白い点。大きい粒は 2×2）。"""
    x0, y0, x1, y1 = area
    for k in range(n):
        x = int(x0 + hsh(k, seed, 1) * (x1 - x0))
        y = int(y0 + hsh(seed, k, 2) * (y1 - y0))
        c.dot(x, y, 'S3' if k % 3 else 'S2')
        if k % 5 == 0:
            c.dot(x + 1, y, 'S2')
            c.dot(x, y + 1, 'S2')


def snow_ground(c, y0, wave=2.0, seed=0):
    """雪の積もった地面（青みの影と、光の側の白）。"""
    pix = []
    for x in range(W):
        top = y0 + wave * math.sin(x / 21 + seed) + 0.8 * math.sin(x / 7 + seed)
        for y in range(max(0, int(top)), H):
            pix.append((x, y, nrm(0.2 * math.cos(x / 21 + seed), -1, 0.6)))
    return c.paint(pix, 'silver', gain=0.9, dither=True, outline=False, tex=lambda px, py: -0.04 if (px * 3 + py * 7) % 19 == 0 else 0)


def snow_cap(c, x0, x1, y, h=3):
    """屋根・塀の上の雪。"""
    c.paint(rect(x0 - 1, y - h, x1 + 1, y + 1, UP), 'silver', gain=1.15, outline=False)


def velvet_case(c, x, y, w=150, h=70, ramp='purple'):
    """内張りの天鵞絨が見える開いた箱（宝飾品の入れ物）。"""
    c.paint(poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2 - 10, y - h / 2 - 34), (x - w / 2 + 10, y - h / 2 - 34)], nrm(-0.2, 0.3, 1)), 'leather', gain=0.85)
    c.paint(poly([(x - w / 2 + 6, y - h / 2 - 2), (x + w / 2 - 6, y - h / 2 - 2), (x + w / 2 - 14, y - h / 2 - 30), (x - w / 2 + 14, y - h / 2 - 30)], nrm(-0.2, 0.3, 1)), ramp, gain=0.8)
    c.paint(rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, nrm(-0.2, 0, 1)), 'leather', gain=0.9)
    c.paint(poly([(x - w / 2 + 6, y - h / 2 + 4), (x + w / 2 - 6, y - h / 2 + 4), (x + w / 2 - 10, y - h / 2 + 18), (x - w / 2 + 10, y - h / 2 + 18)], UP), ramp, gain=1.0)
    c.paint(rect(x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 2), 'gold', gain=1.0, spec=0.5, outline=False)


def skyline(c, x0, x1, base, gain=0.6, seed=0, lit=True, dep=0.4):
    """遠い街並み: 高さの違う塔と屋根、灯の点。"""
    x = x0
    k = 0
    while x < x1:
        w = 10 + hsh(k, seed) * 16
        h = 18 + hsh(seed, k) * 34
        kind = int(hsh(k, seed, 3) * 3)
        c.paint(rect(x, base - h, x + w, base, nrm(-0.3, 0, 1)), 'stone', gain=gain, depth=dep)
        if kind == 0:
            c.paint(poly([(x - 1, base - h), (x + w + 1, base - h), (x + w / 2, base - h - w * 0.9)], nrm(-0.3, -0.5, 0.8)), 'blue', gain=gain, depth=dep)
        elif kind == 1:
            for m in range(int(x), int(x + w), 4):
                c.paint(rect(m, base - h - 3, m + 2, base - h), 'stone', gain=gain, depth=dep)
        else:
            c.paint(ellipse(x + w / 2, base - h, w / 2, w / 2, clip=lambda px, py, b=base - h: py <= b), 'gold', gain=gain * 0.9, depth=dep)
        if lit:
            for j in range(int(h / 9)):
                if hsh(k, j, seed) < 0.55:
                    c.dot(int(x + 2 + hsh(j, k) * (w - 4)), int(base - h + 5 + j * 8), 'G4')
        x += w + 1
        k += 1


def stele(c, x, base, w=40, h=96):
    """石碑: 上が丸い縦長の石、刻んだ文字の列、台石。"""
    block(c, x - w / 2 - 10, base - 12, w + 20, 12, gain=0.95)
    top = base - 12 - h
    pts = [(x - w / 2, base - 12), (x - w / 2, top + w / 2)] + arc_points(x, top + w / 2, w / 2, math.pi, 2 * math.pi, 14) + [(x + w / 2, base - 12)]
    c.paint(poly([(px + 5, py - 3) for px, py in pts], nrm(0.8, -0.1, 0.5)), 'stone', gain=0.6)
    o = c.paint(poly(pts, lambda px, py: nrm(-0.15, -0.1, 1)), 'stone', gain=1.05, tex=lambda px, py: -0.04 if (px * 7 + py * 3) % 17 == 0 else 0)
    for col in range(3):
        cx = x - w / 2 + 9 + col * (w - 18) / 2
        for row in range(9):
            yy = top + 18 + row * 8
            if hsh(col, row) < 0.85:
                c.paint(rect(cx - 2, yy, cx + 3, yy + 4), 'stone', oid=o, gain=0.45, outline=False)
    c.paint(ellipse(x, top + 10, 5, 5), 'gold', oid=o, gain=0.9, spec=0.5)


def sprout_pot(c, x, base):
    """種銭: 鉢の土に埋めた銭から芽が出る。"""
    c.paint(poly([(x - 22, base - 30), (x + 22, base - 30), (x + 16, base), (x - 16, base)], lambda px, py: nrm((px - x) / 22 * 0.8, 0, 0.7)), 'copper', gain=0.9,
            tex=lambda px, py: -0.08 if int(py) % 9 == 0 else 0)
    c.paint(ellipse(x, base - 30, 22, 5), 'copper', gain=1.05)
    c.paint(ellipse(x, base - 30, 19, 4), 'leather', gain=0.55)
    for k, dx in enumerate((-10, 4, 12)):
        coin(c, x + dx, base - 32 + (k % 2), 4.5, 'copper', tilt=0.5, stamp='pip')
    pts = [(x - 1, base - 32), (x + 1, base - 46), (x - 2, base - 60)]
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.2), 'green', gain=1.0)
    for s, yy in ((-1, -52), (1, -58)):
        c.paint(ellipse(x + s * 9, base + yy, 9, 4), 'green', gain=1.05, spec=0.3)
    coin(c, x, base - 66, 6, 'gold', tilt=0.95, stamp='crown')


def cushion(c, x, y, w=90, ramp='red'):
    """宝を載せる房つきの座布団。"""
    c.paint(ellipse(x, y, w / 2, w * 0.16), ramp, gain=1.0, spec=0.2)
    c.paint(ellipse(x, y + w * 0.08, w / 2, w * 0.14, clip=lambda px, py: py > y + 2), ramp, gain=0.75)
    for s in (-1, 1):
        tx = x + s * w / 2
        c.paint(ellipse(tx, y + 2, 3, 3), 'gold', spec=0.5)
        c.paint(poly([(tx - 2, y + 4), (tx + 2, y + 4), (tx + 3, y + 14), (tx - 3, y + 14)], nrm(0.2, 0, 1)), 'gold', gain=0.9)


def diadem(c, x, y, w=70):
    """髪飾り: 金の弧に並ぶ尖り、中央に大きな紅玉、宝石の粒。"""
    pts = arc_points(x, y + 18, w / 2, math.pi * 1.1, math.pi * 1.9, 16)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.4), 'gold', spec=0.8, shine=5)
    for i, (px, py) in enumerate(pts[1:-1:2]):
        hgt = 12 if i == 3 else 7
        c.paint(poly([(px - 3, py + 1), (px + 3, py + 1), (px, py - hgt)], nrm(-0.3, -0.4, 0.9)), 'gold', spec=0.7)
        if i != 3:
            gem(c, px, py - 2, 2.2, ('blue', 'green', 'red')[i % 3])
    gem(c, x, y - 2, 6, 'red')


def screw_press(c, x, base):
    """貨幣の打ち出し機: 太い枠、ねじ棒、上の横棒の両端の重り、台の下に打ち出された硬貨。"""
    c.paint(rect(x - 36, base - 16, x + 36, base, nrm(-0.2, -0.2, 1)), 'stone', gain=0.9)
    for s in (-1, 1):
        c.paint(rect(x + s * 26 - 5, base - 92, x + s * 26 + 5, base - 16, nrm(s * 0.4, 0, 0.9)), 'silver', gain=0.75, spec=0.4)
    c.paint(rect(x - 34, base - 100, x + 34, base - 88, nrm(0, -0.5, 0.8)), 'silver', gain=0.85, spec=0.4)
    for k in range(10):
        yy = base - 98 + k * 6
        c.paint(capsule(x - 4, yy, x + 4, yy + 3, 1.5), 'silver', gain=1.0 if k % 2 else 0.8, spec=0.5)
    c.paint(capsule(x - 52, base - 104, x + 52, base - 104, 2.2), 'silver', gain=0.9, spec=0.5)
    for s in (-1, 1):
        c.paint(ellipse(x + s * 54, base - 104, 7, 7), 'silver', gain=0.9, spec=0.6)
    c.paint(rect(x - 8, base - 40, x + 8, base - 30, nrm(-0.2, 0, 1)), 'silver', gain=1.0, spec=0.5)
    coin(c, x, base - 22, 8, 'gold', tilt=0.4)


def drawers(c, x0, y0, cols=6, rows=5, w=22, h=18, open_at=(2, 2)):
    """貸し金庫の小引き出しの壁。1 つだけ開いて中に金。"""
    for i in range(cols):
        for j in range(rows):
            x, y = x0 + i * w, y0 + j * h
            o = c.paint(rect(x + 1, y + 1, x + w - 1, y + h - 1, nrm(-0.2, -0.1, 1)), 'wood', gain=0.95)
            if (i, j) == open_at:
                c.paint(rect(x + 2, y + 2, x + w - 2, y + h - 2), 'stone', oid=o, emit=0.04, outline=False)
                c.paint(poly([(x - 4, y + h - 2), (x + w + 4, y + h - 2), (x + w + 1, y + h + 8), (x - 1, y + h + 8)], UP), 'wood', gain=1.1)
                coin(c, x + w / 2 - 3, y + h - 2, 4, 'gold', stamp='crown')
                coin(c, x + w / 2 + 4, y + h, 4, 'gold', stamp='star')
            else:
                c.paint(ellipse(x + w / 2, y + h / 2, 2.2, 1.6), 'gold', oid=o, gain=1.0, spec=0.5)
                c.paint(rect(x + w / 2 - 0.5, y + h / 2 + 2, x + w / 2 + 1, y + h / 2 + 4), 'stone', oid=o, emit=0.04, outline=False)


def curio_shelf(c, x0, x1, top, base):
    """蒐集棚: 段の上に髑髏、巻貝、宝石、鳥の剥製、瓶、小箱。"""
    c.paint(rect(x0, top, x1, base, nrm(0, 0, 1)), 'wood', gain=0.35, outline=False)
    rows = [top + 34, top + 68, base - 2]
    for y in rows:
        c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.6, 0.8)), 'wood', gain=1.0)
    w = x1 - x0
    skull(c, x0 + w * 0.2, rows[0] - 9, 0.9)
    shell(c, x0 + w * 0.45, rows[0] - 6, 8)
    gem(c, x0 + w * 0.68, rows[0] - 6, 5, 'blue')
    bottle(c, x0 + w * 0.85, rows[0], h=18, r=5, ramp='green')
    bird(c, x0 + w * 0.25, rows[1])
    chest(c, x0 + w * 0.5, rows[1], 24, 14, open_=False, band='gold')
    coin_stack(c, x0 + w * 0.85, rows[1], 6, 4, 'gold')
    starfish(c, x0 + w * 0.2, rows[2] - 6, 8, 'red')
    globe(c, x0 + w * 0.55, rows[2])
    bottle(c, x0 + w * 0.85, rows[2], h=14, r=6, ramp='purple')
    for x in (x0, x1 - 4):
        c.paint(rect(x, top, x + 4, base, nrm(-0.3, 0, 0.95)), 'wood', gain=0.9)


def bird(c, x, base):
    """止まり木の鳥の剥製。"""
    c.paint(rect(x - 1, base - 6, x + 1, base), 'wood', gain=0.9)
    c.paint(ellipse(x, base - 14, 7, 6), 'blue', gain=1.0)
    c.paint(ellipse(x + 5, base - 20, 4, 4), 'blue', gain=1.1)
    c.paint(poly([(x + 8, base - 21), (x + 13, base - 20), (x + 8, base - 18)]), 'gold', gain=1.0)
    c.paint(poly([(x - 6, base - 13), (x - 14, base - 8), (x - 6, base - 9)]), 'blue', gain=0.8)
    c.dot(int(x + 6), int(base - 21), 'N0')


def globe(c, x, base, r=12):
    c.paint(capsule(x, base, x, base - 6, 2), 'gold')
    c.paint(ellipse(x, base - r - 6, r, r), 'water', gain=1.0, spec=0.4)
    c.paint(ellipse(x - 3, base - r - 8, r * 0.45, r * 0.3), 'green', gain=0.9, outline=False)
    c.paint(ellipse(x + 4, base - r - 2, r * 0.3, r * 0.25), 'sand', gain=0.9, outline=False)
    pts = arc_points(x, base - r - 6, r + 2, math.pi * 0.6, math.pi * 1.9, 14)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.8), 'gold', gain=0.9, outline=False)


def crystal_ball(c, x, base, r=34, ramp='blue'):
    """占い玉: 金の台座の上の水晶。中に渦の幻が光り、表面に窓の照り。"""
    c.paint(poly([(x - 26, base), (x + 26, base), (x + 16, base - 14), (x - 16, base - 14)], lambda px, py: nrm((px - x) / 26 * 0.7, -0.2, 0.8)), 'gold', spec=0.6)
    for s in (-1, 1):
        c.paint(capsule(x + s * 14, base - 14, x + s * 22, base - 26, 2.2), 'gold', spec=0.6)
    cy = base - 14 - r
    def emit(px, py, n):
        d = math.hypot(px - x, py - cy) / r
        a = math.atan2(py - cy, px - x)
        swirl = 0.15 * math.sin(a * 3 + d * 9)
        return 0.25 + 0.55 * (1 - d) + swirl
    c.paint(ellipse(x, cy, r, r), ramp, emit=emit)
    c.paint(ellipse(x - r * 0.4, cy - r * 0.45, r * 0.18, r * 0.12), 'paper', emit=1.0, outline=False)
    c.dot(int(x - r * 0.15), int(cy - r * 0.62), 'S3')


def war_chest(c, x, base):
    """軍資金: 金のあふれる箱に、交差した剣と軍旗。"""
    c.paint(capsule(x - 60, base - 10, x + 30, base - 96, 1.5), 'wood', gain=1.0)
    c.paint(poly([(x + 30, base - 96), (x + 66, base - 90), (x + 30, base - 74)], nrm(-0.3, 0, 1)), 'red', gain=1.0)
    for s in (-1, 1):
        tip = (x + s * 54, base - 82)
        c.paint(capsule(x - s * 34, base - 18, tip[0], tip[1], 2.0, 1.0), 'silver', spec=0.8, shine=5)
        c.paint(capsule(x - s * 26 + s * -6, base - 28, x - s * 26 + s * 6, base - 20, 1.4), 'gold', spec=0.5)
    chest(c, x - 40, base, 80, 34, fill='gold')


def loose_brick(c, x, y, s=1.0):
    """石壁から抜いた石の穴に隠した銭と小袋、床に置いた抜き石。"""
    k = s
    c.paint(rect(x - 16 * k, y - 9 * k, x + 16 * k, y + 9 * k), 'stone', emit=0.04, outline=False)
    c.paint(rect(x - 16 * k, y - 9 * k, x + 16 * k, y - 7 * k), 'stone', emit=0.12, outline=False)
    c.paint(ellipse(x + 8 * k, y + 2 * k, 6 * k, 6 * k), 'leather', gain=1.0)
    for i in range(5):
        coin(c, x - 12 * k + i * 5 * k, y + 7 * k - (i % 2) * 2 * k, 4 * k, 'gold', stamp=('crown', 'star')[i % 2], tilt=0.5)
    block(c, x + 30 * k, y + 34 * k, 30 * k, 16 * k, gain=1.0)
    for i in range(3):
        coin(c, x - 30 * k + i * 12 * k, y + 50 * k, 4 * k, 'gold', stamp='pip', tilt=0.5)


def abacus(c, x, y, w=60, h=34):
    """算盤: 木の枠、横棒、珠。"""
    c.paint(rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, nrm(-0.2, -0.3, 0.9)), 'wood', gain=1.0)
    c.paint(rect(x - w / 2 + 3, y - h / 2 + 3, x + w / 2 - 3, y + h / 2 - 3), 'wood', gain=0.4, outline=False)
    c.paint(rect(x - w / 2 + 3, y - h / 2 + 10, x + w / 2 - 3, y - h / 2 + 12), 'wood', gain=1.0)
    n = 8
    for i in range(n):
        bx = x - w / 2 + 6 + i * (w - 12) / (n - 1)
        c.paint(rect(bx, y - h / 2 + 3, bx + 1, y + h / 2 - 3), 'silver', gain=0.6, outline=False)
        c.paint(ellipse(bx + 0.5, y - h / 2 + 7 - (2 if i % 3 == 0 else 0), 3, 2), 'red', gain=1.0)
        for j in range(4):
            up = 1 if (i + j) % 3 == 0 else 0
            c.paint(ellipse(bx + 0.5, y - h / 2 + 16 + j * 4 - up * 2, 3, 1.8), 'wood', gain=1.3)


def signpost(c, x, base, arrows=(('red', -1, 0), ('blue', 1, 1), ('paper', -1, 2))):
    """道しるべ: 柱に、別々の方を指す板。"""
    c.paint(capsule(x, base, x, base - 76, 2.4), 'wood', gain=1.0)
    for col, d, i in arrows:
        y = base - 70 + i * 16
        pts = [(x, y), (x + d * 36, y), (x + d * 44, y + 5), (x + d * 36, y + 10), (x, y + 10)]
        c.paint(poly(pts, nrm(-0.2 * d, -0.2, 0.95)), col, gain=1.0)
        c.paint(rect(x + d * 8, y + 4, x + d * 30, y + 5), 'wood', gain=0.6, outline=False)


def road(c, x, top, base, w0=8, w1=110, ramp='stone'):
    """奥へ細くなる道。轍の 2 本線。"""
    pts = [(x - w0 / 2, top), (x + w0 / 2, top), (x + w1 / 2, base), (x - w1 / 2, base)]
    c.paint(poly(pts, UP), ramp, gain=0.95, dither=True, tex=lambda px, py: -0.06 if (int(px) * 3 + int(py) * 5) % 13 == 0 else 0)
    for s in (-0.25, 0.25):
        c.paint(capsule(x + s * w0, top, x + s * w1, base, 0.6), ramp, gain=0.6, outline=False)


def amulet(c, x, y, r=26):
    """お守り: 紐で下げた円い札、中に翠玉、まわりに淡い光。"""
    c.paint(capsule(x - 30, 0, x, y - r, 1.0), 'red', gain=0.9)
    c.paint(capsule(x + 30, 0, x, y - r, 1.0), 'red', gain=0.8)
    c.paint(ellipse(x, y, r + 8, r + 8), 'green', emit=lambda px, py, n: 0.35 - math.hypot(px - x, py - y) / (r + 8) * 0.3, outline=False, dither=True)
    c.paint(ellipse(x, y, r, r), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x, y, r * 0.75, r * 0.75), 'gold', gain=0.65)
    for k in range(8):
        a = k * math.pi / 4
        c.paint(capsule(x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55, x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72, 1.0), 'gold', gain=1.1, outline=False)
    gem(c, x, y, r * 0.4, 'green')
    c.paint(poly([(x - 6, y + r), (x + 6, y + r), (x + 4, y + r + 20), (x - 4, y + r + 20)], lambda px, py: nrm(0.4 * math.sin(px * 1.2), 0, 0.9)), 'red', gain=1.0)


def wax_seal(c, x, y, r=26):
    """御印: 押した赤い封蝋（紋の浮き出し）と、金の柄の印章。"""
    c.paint(ellipse(x, y + 2, r + 4, (r + 4) * 0.8), 'red', gain=0.7)
    c.paint(ellipse(x, y, r, r * 0.8), 'red', gain=1.05, spec=0.5)
    c.paint(ellipse(x, y, r * 0.65, r * 0.52), 'red', gain=0.8)
    for kk, (dx, dy) in enumerate(((0, -8), (-7, 4), (7, 4))):
        c.paint(poly([(x + dx - 4, y + dy + 3), (x + dx + 4, y + dy + 3), (x + dx, y + dy - 5)], nrm(-0.4, -0.5, 0.8)), 'red', gain=1.2)
    sx, sy = x + r + 30, y - 10
    c.paint(capsule(sx, sy + 20, sx + 4, sy - 34, 4, 3), 'wood', gain=1.0, spec=0.3)
    c.paint(ellipse(sx + 4, sy - 38, 6, 6), 'gold', spec=0.7)
    c.paint(vcyl(sx, sy + 20, sy + 30, 9, 3), 'gold', spec=0.7)


def dice(c, x, y, s=14, pips=5, rot=0):
    """骰子（さいころ）: 上の面・正面・右の面、目の数。"""
    d = s * 0.5
    c.paint(poly([(x, y), (x + s, y), (x + s + d, y - d * 0.7), (x + d, y - d * 0.7)], UP), 'paper', gain=1.2)
    c.paint(poly([(x + s, y), (x + s + d, y - d * 0.7), (x + s + d, y + s - d * 0.7), (x + s, y + s)], nrm(0.85, 0, 0.5)), 'paper', gain=0.8)
    o = c.paint(rect(x, y, x + s, y + s, nrm(-0.2, 0, 1)), 'paper', gain=1.0)
    spots = {1: [(0.5, 0.5)], 2: [(0.25, 0.25), (0.75, 0.75)], 3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
             4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)], 5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
             6: [(0.25, 0.2), (0.75, 0.2), (0.25, 0.5), (0.75, 0.5), (0.25, 0.8), (0.75, 0.8)]}[pips]
    for px, py in spots:
        c.paint(ellipse(x + px * s, y + py * s, s * 0.09, s * 0.09), 'red' if pips == 1 else 'stone', oid=o, emit=0.1 if pips != 1 else 0.6, outline=False)


def playing_cards(c, x, y):
    for k, (dx, dy, col) in enumerate(((0, 0, 'red'), (14, -4, 'stone'), (28, 2, 'red'))):
        pts = [(x + dx, y + dy), (x + dx + 16, y + dy - 3), (x + dx + 20, y + dy + 18), (x + dx + 4, y + dy + 21)]
        o = c.paint(poly(pts, UP), 'paper', gain=1.1)
        c.paint(ellipse(x + dx + 10, y + dy + 9, 3, 3), col, oid=o, emit=0.55 if col == 'red' else 0.1, outline=False)


def doc(c, x, y, w=110, h=80, seal=True, lines=7, sign=True):
    """証文（借用書）: 紙、文字の行、署名の線、赤い封蝋。"""
    pts = [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2 - 4), (x + w / 2 + 6, y + h / 2), (x - w / 2 - 4, y + h / 2 + 4)]
    o = c.paint(poly(pts, nrm(-0.2, -0.4, 0.9)), 'paper', gain=1.05, tex=lambda px, py: -0.04 if (px * 3 + py * 7) % 23 == 0 else 0)
    for k in range(lines):
        yy = y - h / 2 + 10 + k * 7
        ln = w * (0.8 if k % 3 else 0.6)
        c.paint(rect(x - w / 2 + 8, yy, x - w / 2 + 8 + ln, yy + 1.5), 'leather', oid=o, gain=0.7, outline=False)
    if sign:
        pts2 = [(x + 4, y + h / 2 - 10), (x + 12, y + h / 2 - 16), (x + 20, y + h / 2 - 8), (x + 30, y + h / 2 - 14), (x + 40, y + h / 2 - 9)]
        for a, b in zip(pts2, pts2[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'stone', oid=o, emit=0.1, outline=False)
    if seal:
        c.paint(ellipse(x - w / 2 + 20, y + h / 2 - 12, 9, 8), 'red', gain=1.05, spec=0.5)
        c.paint(poly([(x - w / 2 + 16, y + h / 2 - 6), (x - w / 2 + 20, y + h / 2 + 10), (x - w / 2 + 24, y + h / 2 - 6)]), 'red', gain=0.8)


def bottles_row(c, x0, x1, base, ramps=('green', 'red', 'blue', 'purple', 'gold'), seed=0):
    x = x0
    k = 0
    while x < x1 - 6:
        r = 3 + int(hsh(k, seed) * 3)
        h = 10 + int(hsh(seed, k) * 8)
        bottle(c, x + r, base, h=h, r=r, ramp=ramps[k % len(ramps)])
        x += r * 2 + 3
        k += 1


def round_table(c, x, y, rx=90, ry=22, cloth='red'):
    """円卓（手前の縁と卓掛け）。"""
    c.paint(ellipse(x, y + 8, rx, ry, clip=lambda px, py: py > y), cloth, gain=0.8,
            tex=lambda px, py: -0.06 if int(px) % 8 == 0 else 0)
    c.paint(ellipse(x, y, rx, ry, normal=UP), 'wood', gain=1.0)
    c.paint(rect(x - rx, y, x + rx, y + 10, lambda px, py: nrm(0.3 * math.sin((px - x) / 4), 0.1, 0.9)), cloth, gain=0.9)
    c.paint(rect(x - rx, y + 9, x + rx, y + 11), 'gold', gain=0.9, outline=False)


def pitchfork():
    """熊手（群衆の持ち物）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y + 2 * u, x, y - 3.2 * u, 0.13 * u), 'wood')
        for dx in (-0.4, 0, 0.4):
            c.paint(capsule(x + dx * u, y - 3.2 * u, x + dx * u, y - 4.2 * u, 0.09 * u), 'silver', gain=1.0)
        c.paint(capsule(x - 0.4 * u, y - 3.2 * u, x + 0.4 * u, y - 3.2 * u, 0.09 * u), 'silver')
    return draw


def torch_held():
    """手に掲げた松明。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y + 1.2 * u, x, y - 1.4 * u, 0.15 * u, 0.22 * u), 'wood')
        flame(c, x, y - 2.0 * u, 0.5 * u, 0.9 * u)
    return draw


def tray_strap():
    """首から下げた売り台（小間物と瓶）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = fig.X(0, fig.y_waist), fig.y_waist + 0.2 * u
        w = 2.4 * u
        for s in (-1, 1):
            c.paint(capsule(fig.X(s * 0.4, fig.y_neck), fig.y_neck, x + s * w * 0.9, y, 0.5), 'leather', gain=0.8, outline=False)
        c.paint(poly([(x - w, y), (x + w, y), (x + w + 0.5 * u, y - 0.6 * u), (x - w + 0.5 * u, y - 0.6 * u)], UP), 'wood', gain=1.1)
        c.paint(rect(x - w, y, x + w, y + 0.6 * u, nrm(-0.1, 0, 1)), 'wood', gain=0.85)
        for k, col in enumerate(('red', 'blue', 'green', 'gold')):
            bottle(c, x - w + 0.6 * u + k * 1.2 * u, y - 0.3 * u, h=0.9 * u, r=0.25 * u, ramp=col)
    return draw


def held_bottle(ramp='green'):
    def draw(c, fig, hand):
        u = fig.u
        bottle(c, hand[0], hand[1] + 0.3 * u, h=1.6 * u, r=0.45 * u, ramp=ramp)
    return draw


def crook_staff():
    """高僧の牧杖（先が渦に巻く金の杖）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        top = y - 3.5 * u
        c.paint(capsule(x, fig.foot - 0.2 * u, x, top, 0.15 * u), 'gold', spec=0.6)
        pts = [(x + fig.f * 0.6 * u * (1 - math.cos(t)), top - 0.6 * u * math.sin(t)) for t in [i * 0.45 for i in range(9)]]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.15 * u), 'gold', spec=0.6)
    return draw


def quill_flat(c, x, y):
    """卓に置いた羽根ペン。"""
    c.paint(capsule(x - 24, y + 10, x + 10, y - 6, 2.8, 0.6), 'paper', gain=1.1)
    c.paint(capsule(x - 30, y + 13, x - 22, y + 9, 0.8), 'stone', emit=0.1, outline=False)


def seal_on(c, x, y):
    """箱に貼った封の札と赤い封蝋。"""
    c.paint(rect(x - 12, y - 18, x + 12, y + 18, nrm(-0.2, 0, 1)), 'paper', gain=1.05)
    for k in range(3):
        c.paint(rect(x - 7, y - 12 + k * 5, x + 7, y - 11 + k * 5), 'stone', emit=0.1, outline=False)
    c.paint(ellipse(x, y + 8, 7, 6), 'red', gain=1.1, spec=0.5)


def bell_hang(c, x, y):
    """櫓に吊った半鐘。"""
    c.paint(rect(x, y - 14, x + 1, y), 'silver', gain=0.7, outline=False)
    pts = [(x - 5, y), (x + 6, y), (x + 9, y + 12), (x + 11, y + 16), (x - 10, y + 16), (x - 8, y + 12)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / 10 * 0.8, -0.1, 0.7)), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x, y + 16, 10.5, 2.4), 'gold', gain=0.55)


def frame(c, x0, x1, base, h):
    """建て増しの木組み（柱・梁・筋かい・棟木）。"""
    for x in (x0, (x0 + x1) / 2, x1):
        c.paint(rect(x - 2, base - h, x + 2, base), 'wood', gain=1.05)
    for y in (base - h, base - h / 2):
        c.paint(rect(x0 - 2, y - 2, x1 + 2, y + 2), 'wood', gain=1.0)
    c.paint(capsule(x0, base, (x0 + x1) / 2, base - h / 2, 1.3), 'wood', gain=0.9)
    apex = ((x0 + x1) / 2, base - h - 30)
    for x in (x0, x1):
        c.paint(capsule(x, base - h, apex[0], apex[1], 1.8), 'wood', gain=1.0 if x == x0 else 0.8)


def melting_pot(c, x, y):
    """炉の中の坩堝: 中で金属が煮え立つ。"""
    c.paint(ellipse(x, y + 8, 30, 20, clip=lambda px, py: py >= y), 'stone', gain=0.75, spec=0.3)
    c.paint(ellipse(x, y, 30, 8), 'stone', gain=0.9)
    c.paint(ellipse(x, y, 26, 6), 'fire', emit=lambda px, py, n: 0.85 + (0.12 if (int(px) + int(py) * 3) % 7 == 0 else 0))
    for k in range(3):
        c.paint(ellipse(x - 10 + k * 10, y - 1, 2.5, 1.5), 'fire', emit=1.0, outline=False)


def falling(c, x, y):
    """坩堝へ落ちていく杯と硬貨。"""
    goblet(c, x - 14, y + 6, s=0.9, wine=False)
    coin(c, x + 10, y - 2, 5, 'gold', tilt=0.9)
    coin(c, x + 2, y + 18, 4, 'copper', tilt=0.7, stamp='pip')


def tally_sticks(c, x, y):
    """刻み目を入れた勘定木の束。"""
    for k in range(6):
        x0, y0 = x - 40 + k * 3, y + 20 - k * 2
        c.paint(capsule(x0, y0, x0 + 70, y0 - 16, 2.4, flat=0.3), 'wood', gain=1.3 - k * 0.04)
        for j in range(8):
            t = 0.1 + j * 0.1
            c.dot(int(x0 + 70 * t), int(y0 - 16 * t - 1), 'G1')
    c.paint(capsule(x - 6, y + 22, x + 8, y - 4, 1.4), 'red', gain=1.0)


def floating_coins(c, x, y):
    """宙に浮かぶ硬貨の弧。"""
    for k in range(7):
        a = math.pi * (0.1 + k * 0.13)
        cx, cy = x + math.cos(a) * 46, y + 40 - math.sin(a) * 30
        coin(c, cx, cy, 5, ('gold', 'silver', 'copper')[k % 3], tilt=0.6 + 0.3 * math.sin(k), stamp='pip')


# ================= 錬金術（alchemy）で足した部品 =================

def rune_circle(c, x, y, rx=80, ry=24, ramp='purple'):
    """床に描いた変成の陣: 二重の輪と、輪の上の文字、中の星形。発光。"""
    for rr, e in ((1.0, 0.8), (0.82, 0.65)):
        pts = arc_points(x, y, 1, 0, math.pi * 2, 48)
        pts = [(x + (px - x) * rx * rr, y + (py - y) * ry * rr) for px, py in pts]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.9), ramp, emit=e, outline=False)
    for k in range(5):
        a0 = -math.pi / 2 + k * 4 * math.pi / 5
        a1 = a0 + 4 * math.pi / 5
        c.paint(capsule(x + math.cos(a0) * rx * 0.8, y + math.sin(a0) * ry * 0.8, x + math.cos(a1) * rx * 0.8, y + math.sin(a1) * ry * 0.8, 0.7), ramp, emit=0.6, outline=False)
    for k in range(16):
        a = k / 16 * math.pi * 2
        px, py = x + math.cos(a) * rx * 0.91, y + math.sin(a) * ry * 0.91
        c.dot(int(px), int(py), 'P3' if ramp == 'purple' else 'G5')
        c.dot(int(px + 1), int(py - 1), 'P3' if ramp == 'purple' else 'G5')


def half_gold_goblet(c, x, base, s=2.0):
    """半分は鉛色、半分は金に変わりかけの杯。"""
    goblet(c, x, base, s=s, ramp='stone', wine=False)
    o = c.obj()
    for px, py, n in ellipse(x, base - 9 * s, 4 * s, 4 * s, clip=lambda qx, qy: qy >= base - 10 * s and qx < x):
        c.paint([(px, py, n)], 'gold', oid=o, spec=0.8, shine=5)
    c.paint(rect(x - 4 * s, base - 10 * s, x, base - 9 * s), 'gold', gain=1.2, outline=False)
    for k in range(8):
        a = k * math.pi / 4
        c.dot(int(x + math.cos(a) * 9 * s), int(base - 8 * s + math.sin(a) * 7 * s), 'G6')


def trellis(c, x0, x1, top, base):
    """ぶどう棚: 柱と横木、絡む蔓、葉、紫の房。"""
    for x in range(int(x0), int(x1) + 1, 40):
        c.paint(rect(x - 2, top, x + 2, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0)
    for y in (top, top + 30):
        c.paint(rect(x0 - 4, y - 2, x1 + 4, y + 1, UP), 'wood', gain=1.0)
    for k in range(int((x1 - x0) / 8)):
        x = x0 + k * 8 + 4
        y = top + 6 + 6 * math.sin(k * 1.3)
        c.paint(ellipse(x, y, 6, 4), 'foliage', gain=1.0 + 0.1 * (k % 2))
    for k in range(int((x1 - x0) / 26)):
        gx = x0 + 14 + k * 26
        gy = top + 14 + (k % 2) * 8
        for r_, cnt in enumerate((4, 3, 2, 1)):  # 房: 上の段ほど粒が多い
            for i in range(cnt):
                c.paint(ellipse(gx + (i - (cnt - 1) / 2) * 3.6, gy + r_ * 3.2, 2.0, 2.0), 'purple', gain=1.15, spec=0.5)
        c.paint(capsule(gx, gy - 4, gx, gy - 1, 0.6), 'wood', gain=0.9, outline=False)


def mortar(c, x, base, r=16):
    """乳鉢と乳棒。"""
    c.paint(ellipse(x, base - r * 0.5, r, r * 0.75, clip=lambda px, py: py >= base - r * 0.8), 'stone', gain=1.05, spec=0.2)
    c.paint(ellipse(x, base - r * 0.8, r, r * 0.25), 'stone', gain=1.15)
    c.paint(ellipse(x, base - r * 0.8, r * 0.8, r * 0.17), 'green', gain=0.75)
    c.paint(capsule(x + 2, base - r * 0.8, x + r * 1.1, base - r * 2.2, 2.2, 3.2), 'stone', gain=1.1)


def scrying_pool(c, x, y, rx=70, ry=20):
    """のぞき水鏡: 石の縁の水盤、水面に映る目と淡い光。"""
    c.paint(ellipse(x, y + 8, rx + 8, ry + 10), 'stone', gain=0.75)
    c.paint(ellipse(x, y, rx + 8, ry + 6, normal=UP), 'stone', gain=1.05, tex=lambda px, py: -0.08 if int(math.atan2(py - y, (px - x) / 3) * 8) % 2 == 0 else 0)
    c.paint(ellipse(x, y, rx, ry), 'water', emit=lambda px, py, n: 0.4 + 0.35 * (1 - math.hypot((px - x) / rx, (py - y) / ry)) + (0.08 if int(math.hypot((px - x) / 2, py - y)) % 5 == 0 else 0))
    c.paint(ellipse(x, y, 16, 6), 'paper', emit=0.85, outline=False)
    c.paint(ellipse(x, y, 7, 5), 'purple', emit=0.6, outline=False)
    c.paint(ellipse(x, y, 3, 3), 'stone', emit=0.05, outline=False)


def slate(c, x, y, w=80, h=54):
    """石板の黒板: 白墨で描いた円と星と式。"""
    c.paint(rect(x - w / 2 - 4, y - h / 2 - 4, x + w / 2 + 4, y + h / 2 + 4, nrm(-0.2, -0.2, 1)), 'wood', gain=1.0)
    o = c.paint(rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), 'stone', emit=0.16, outline=False)
    pts = arc_points(x - 14, y - 2, 14, 0, math.pi * 2, 20)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.5), 'paper', oid=o, emit=0.75, outline=False)
    for k in range(3):
        a0 = -math.pi / 2 + k * 2 * math.pi / 3
        a1 = a0 + 2 * math.pi / 3
        c.paint(capsule(x - 14 + math.cos(a0) * 14, y - 2 + math.sin(a0) * 14, x - 14 + math.cos(a1) * 14, y - 2 + math.sin(a1) * 14, 0.5), 'paper', oid=o, emit=0.7, outline=False)
    for k in range(4):
        yy = y - h / 2 + 10 + k * 9
        c.paint(rect(x + 6, yy, x + w / 2 - 6 - (k % 2) * 8, yy + 1.2), 'paper', oid=o, emit=0.6, outline=False)


def hourglass(c, x, base, h=34):
    for yy in (base - h, base):
        c.paint(rect(x - 11, yy - 3, x + 11, yy + 1, UP), 'wood', gain=1.0)
    for s in (-1, 1):
        c.paint(capsule(x + s * 9, base - h, x + s * 9, base, 1.2), 'wood', gain=0.9)
    for top in (True, False):
        y0, y1 = (base - h + 1, base - h / 2) if top else (base - h / 2, base - 3)
        pts = [(x - 7, y0), (x + 7, y0), (x + 1, base - h / 2), (x - 1, base - h / 2)] if top else [(x - 1, base - h / 2), (x + 1, base - h / 2), (x + 7, y1), (x - 7, y1)]
        c.paint(poly(pts, nrm(-0.3, 0, 0.9)), 'silver', gain=0.75, spec=0.5)
    c.paint(poly([(x - 4, base - h + 8), (x + 4, base - h + 8), (x, base - h / 2)]), 'sand', gain=1.2, outline=False)
    c.paint(poly([(x - 6, base - 3), (x + 6, base - 3), (x, base - 10)]), 'sand', gain=1.2, outline=False)
    c.paint(rect(x, base - h / 2, x + 1, base - 8), 'sand', gain=1.2, outline=False)


def cat(c, x, base, s=1.0, facing=1):
    """黒猫（座った横向き）: 丸い背、三角の耳、巻いた尾、光る金の目。"""
    k = s
    f = facing
    c.paint(capsule(x - f * 14 * k, base - 4 * k, x - f * 26 * k, base - 24 * k, 2.4 * k, 1.6 * k), 'cloth', gain=0.5)
    c.paint(ellipse(x - f * 2 * k, base - 16 * k, 14 * k, 16 * k), 'cloth', gain=0.55)
    c.paint(ellipse(x + f * 8 * k, base - 36 * k, 9 * k, 8 * k), 'cloth', gain=0.6)
    for dx in (2, 13):
        c.paint(poly([(x + f * (dx - 1) * k, base - 40 * k), (x + f * (dx + 5) * k, base - 41 * k), (x + f * (dx + 1) * k, base - 50 * k)], nrm(-0.3, -0.4, 0.8)), 'cloth', gain=0.65)
    for dx in (5, 12):
        c.paint(ellipse(x + f * dx * k, base - 37 * k, 1.8 * k, 1.4 * k), 'gold', emit=1.0, outline=False)
        c.dot(int(x + f * dx * k), int(base - 37 * k), 'N0')
    c.paint(capsule(x + f * 6 * k, base - 20 * k, x + f * 8 * k, base - 1, 2.2 * k), 'cloth', gain=0.6)


def crystal_cluster(c, x, base, s=1.0, ramp='blue'):
    """秘石: 台の上に、光る結晶が束になって伸びる。"""
    k = s
    block(c, x - 30 * k, base - 12 * k, 60 * k, 12 * k, gain=0.9)
    shards = [(-14, 30, -0.35), (0, 52, 0.0), (14, 36, 0.3), (-26, 18, -0.6), (26, 20, 0.55)]
    for dx, h, lean in sorted(shards, key=lambda t: t[1]):
        bx = x + dx * k
        tip = (bx + lean * h * k * 0.6, base - 12 * k - h * k)
        w = 5 * k
        def emit(px, py, n, bx=bx, tip=tip):
            return 0.5 + 0.45 * ((base - 12 * k - py) / (base - 12 * k - tip[1] + 1)) + (0.12 if px < (bx + tip[0]) / 2 else -0.06)
        c.paint(poly([(bx - w, base - 12 * k), (bx + w, base - 12 * k), (tip[0] + w * 0.4, tip[1] + 6 * k), tip, (tip[0] - w * 0.4, tip[1] + 6 * k)]), ramp, emit=emit)


def marionette(c, x, top, base):
    """乗っ取り: 上から伸びる手と十字の操り木、糸に吊られた人形。"""
    for s in (-1, 1):
        c.paint(capsule(x + s * 70, 0, x + s * 36, 22, 9, 6), 'cloth', gain=0.9)
        c.paint(ellipse(x + s * 32, 26, 7, 6), 'skin', gain=1.05)
        for j in range(3):
            c.paint(capsule(x + s * (28 - j * 4), 28, x + s * (24 - j * 5), 36, 1.6), 'skin', gain=1.0)
    c.paint(capsule(x - 30, 34, x + 30, 34, 2.0), 'wood', gain=1.1)
    c.paint(capsule(x, 22, x, 48, 2.0), 'wood', gain=1.0)
    fig_top = top
    pts = {'head': (x, fig_top + 8), 'lh': (x - 22, fig_top + 34), 'rh': (x + 24, fig_top + 26), 'lf': (x - 10, base), 'rf': (x + 12, base - 6)}
    for (sx, sy), key in (((x - 30, 34), 'lh'), ((x + 30, 34), 'rh'), ((x, 48), 'head'), ((x - 22, 34), 'lf'), ((x + 22, 34), 'rf')):
        tx, ty = pts[key]
        c.paint(capsule(sx, sy, tx, ty, 0.35), 'paper', gain=0.9, outline=False)
    hx, hy = pts['head']
    c.paint(capsule(x, hy + 8, x, hy + 34, 7, 6), 'red', gain=1.0)
    for key in ('lh', 'rh'):
        c.paint(capsule(x + (-6 if key == 'lh' else 6), hy + 12, pts[key][0], pts[key][1], 2.4), 'red', gain=0.95)
        c.paint(ellipse(pts[key][0], pts[key][1], 2.4, 2.4), 'wood', gain=1.3)
    for key in ('lf', 'rf'):
        c.paint(capsule(x + (-3 if key == 'lf' else 3), hy + 34, pts[key][0], pts[key][1], 2.6), 'blue', gain=0.95)
    c.paint(ellipse(hx, hy, 6.5, 7), 'wood', gain=1.35)
    c.paint(ellipse(hx, hy - 6, 6, 3), 'gold', gain=1.0, spec=0.5)
    for ex in (-2, 2):
        c.dot(int(hx + ex), int(hy), 'N0')


def big_potion(c, x, base, ramp='blue'):
    """霊薬の大瓶: 栓、首の封の紐、光る液、ラベル。"""
    r = 30
    cy = base - r
    c.paint(ellipse(x, cy, r, r), ramp, emit=lambda px, py, n: (0.25 if py < cy - r * 0.35 else 0.95 - math.hypot(px - x + r * 0.3, py - cy) / r * 0.45))
    c.paint(rect(x - 6, cy - r - 24, x + 7, cy - r + 4, nrm(-0.3, 0, 1)), 'silver', gain=0.8, spec=0.5)
    c.paint(rect(x - 8, cy - r - 30, x + 9, cy - r - 22, nrm(-0.3, -0.3, 0.9)), 'wood', gain=1.1)
    c.paint(rect(x - 7, cy - r - 8, x + 8, cy - r - 5), 'red', gain=1.0, outline=False)
    c.paint(rect(x - 16, cy + 2, x + 16, cy + 16, nrm(-0.2, 0, 1)), 'paper', gain=1.1)
    c.paint(rect(x - 11, cy + 8, x + 11, cy + 9), 'leather', gain=0.8, outline=False)
    c.paint(ellipse(x - r * 0.5, cy - r * 0.15, 3, 8), 'paper', emit=1.0, outline=False)
    for k in range(5):
        c.paint(ellipse(x - 10 + hsh(k, 4) * 20, cy - 4 - k * 4, 1.6, 1.6), ramp, emit=1.0, outline=False)


def basket_held():
    """腕に下げたかご（摘んだ草）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] + 1.0 * u
        c.paint(ellipse(x, y - 0.9 * u, 1.3 * u, 1.2 * u, clip=lambda px, py: py <= y - 0.6 * u), 'wood', gain=1.1, outline=False)
        for k in range(5):
            c.paint(ellipse(x - 1.0 * u + k * 0.5 * u, y - 0.2 * u - (k % 2) * 0.3 * u, 0.4 * u, 0.5 * u), 'green', gain=1.1)
        basket(c, x, y + 0.9 * u, 2.4 * u, 1.0 * u, n=0)
    return draw


def held_flask(ramp='green'):
    def draw(c, fig, hand):
        u = fig.u
        flask(c, hand[0], hand[1] - 1.0 * u, 0.8 * u, ramp, neck=0.7 * u)
    return draw


def mortar_held():
    def draw(c, fig, hand):
        mortar(c, hand[0] + fig.f * 0.6 * fig.u, hand[1] + 1.0 * fig.u, r=0.9 * fig.u)
    return draw


def chimney(c, x, base, w=16, h=30):
    c.paint(rect(x - w / 2, base - h, x + w / 2, base, nrm(-0.3, 0, 1)), 'red', gain=0.8, tex=lambda px, py: -0.1 if int(py) % 5 == 0 else 0)
    c.paint(rect(x - w / 2 - 2, base - h - 3, x + w / 2 + 2, base - h, UP), 'red', gain=1.0)


def rune_mark(c, x, y):
    """胸に刻んで光る文字。"""
    for a, b in (((x - 5, y - 6), (x + 5, y - 6)), ((x, y - 6), (x, y + 6)), ((x - 5, y + 6), (x + 5, y + 2))):
        c.paint(capsule(a[0], a[1], b[0], b[1], 1.0), 'gold', emit=1.0, outline=False)


# ================= 異郷（hinterlands）で足した部品 =================

def dog(c, x, base, s=1.0, facing=1, ramp='leather', sit=True):
    """犬（座って吠える横向き）: 胸、前脚、頭と口吻、立った耳、尾。"""
    k = s
    f = facing
    X = lambda dx: x + f * dx * k
    c.paint(capsule(X(-16), base - 10 * k, X(-26), base - 22 * k, 2.2 * k, 1.4 * k), ramp, gain=0.85)
    c.paint(ellipse(X(-8), base - 12 * k, 13 * k, 11 * k), ramp, gain=0.9)
    c.paint(capsule(X(2), base - 14 * k, X(6), base - 34 * k, 7 * k, 6 * k), ramp, gain=1.0)
    c.paint(capsule(X(4), base - 14 * k, X(6), base - 1, 2.6 * k, 2.2 * k), ramp, gain=1.05)
    c.paint(capsule(X(-2), base - 12 * k, X(-1), base - 1, 2.6 * k, 2.2 * k), ramp, gain=0.8)
    c.paint(ellipse(X(8), base - 40 * k, 7 * k, 6.5 * k), ramp, gain=1.05)
    c.paint(capsule(X(10), base - 38 * k, X(19), base - 36 * k, 3.6 * k, 2.6 * k), ramp, gain=1.1)
    c.dot(int(X(20)), int(base - 37 * k), 'N0')
    c.paint(capsule(X(17), base - 34 * k, X(12), base - 32 * k, 1.2 * k), 'red', gain=1.0, outline=False)
    for dx in (3, 9):
        c.paint(poly([(X(dx - 2), base - 44 * k), (X(dx + 3), base - 44 * k), (X(dx), base - 53 * k)], nrm(-0.3, -0.4, 0.8)), ramp, gain=1.0)
    c.dot(int(X(11)), int(base - 42 * k), 'N0')
    c.paint(ellipse(X(4), base - 30 * k, 6 * k, 2.4 * k), 'red', gain=0.9)
    c.dot(int(X(4)), int(base - 28 * k), 'G5')


def raven(c, x, y, s=1.0, facing=1):
    """鴉（とまっている横向き）。"""
    k = s
    f = facing
    c.paint(ellipse(x, y, 10 * k, 7 * k), 'cloth', gain=0.6, spec=0.3)
    c.paint(ellipse(x + f * 9 * k, y - 6 * k, 5 * k, 5 * k), 'cloth', gain=0.65)
    c.paint(poly([(x + f * 13 * k, y - 7 * k), (x + f * 20 * k, y - 5 * k), (x + f * 13 * k, y - 4 * k)]), 'stone', gain=1.1)
    c.paint(poly([(x - f * 8 * k, y - 2 * k), (x - f * 20 * k, y + 2 * k), (x - f * 8 * k, y + 4 * k)]), 'cloth', gain=0.55)
    c.dot(int(x + f * 10 * k), int(y - 7 * k), 'G5')
    for dx in (-2, 2):
        c.paint(capsule(x + dx * k, y + 6 * k, x + dx * k, y + 10 * k, 0.6 * k), 'gold', gain=0.8, outline=False)


def camel(c, x, base, s=1.0, facing=1, ramp='sand', load='red'):
    """駱駝（横から）: 長い首、背のこぶ、荷の布。"""
    k = s
    f = facing
    X = lambda dx: x - f * dx * k
    for dx, g in ((14, 0.75), (-14, 0.75)):
        c.paint(capsule(X(dx + 2), base - 34 * k, X(dx + 3), base - 1, 3.6 * k, 2.4 * k), ramp, gain=g)
    c.paint(ellipse(x, base - 40 * k, 24 * k, 13 * k), ramp, gain=0.95)
    c.paint(ellipse(X(-2), base - 50 * k, 12 * k, 10 * k, clip=lambda px, py: py < base - 44 * k), ramp, gain=1.0)
    c.paint(poly([(X(-12), base - 54 * k), (X(10), base - 54 * k), (X(12), base - 36 * k), (X(-14), base - 36 * k)],
                 lambda px, py: nrm(0.3 * math.sin(px / 3), 0, 0.9)), load, gain=1.0)
    c.paint(capsule(X(18), base - 40 * k, X(30), base - 56 * k, 5.6 * k, 4 * k), ramp, gain=1.0)
    c.paint(capsule(X(30), base - 58 * k, X(38), base - 55 * k, 4.4 * k, 3.2 * k), ramp, gain=1.05)
    c.dot(int(X(32)), int(base - 59 * k), 'N0')
    for dx, g in ((16, 1.0), (-12, 0.95)):
        c.paint(capsule(X(dx), base - 34 * k, X(dx - 1), base - 1, 3.8 * k, 2.6 * k), ramp, gain=g)


def dunes(c, y0, ramp='sand', gain=0.85):
    """砂丘（ゆるい稜線が重なる）。"""
    for i, (yy, amp, g) in enumerate(((y0, 10, 0.6), (y0 + 14, 12, 0.8), (y0 + 30, 8, 1.0))):
        pix = []
        for x in range(W):
            top = yy - amp * math.sin(x / (40 + i * 10) + i * 2) ** 2
            for y in range(max(0, int(top)), H):
                pix.append((x, y, nrm(0.6 * math.cos(x / (40 + i * 10) + i * 2), -0.7, 0.6)))
        c.paint(pix, ramp, gain=gain * g, dither=True, outline=False)


def wheel(c, x, y, r=22, gain=1.0):
    """木の車輪（輪・輻・こしき）。"""
    pts = arc_points(x, y, r, 0, math.pi * 2, 28)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 2.4), 'wood', gain=gain)
    pts = arc_points(x, y, r + 1.5, 0, math.pi * 2, 28)
    for a, b in zip(pts, pts[1:]):
        c.paint(capsule(a[0], a[1], b[0], b[1], 0.8), 'silver', gain=gain * 0.8, outline=False)
    for kk in range(10):
        a = kk * math.pi / 5
        c.paint(capsule(x, y, x + math.cos(a) * r, y + math.sin(a) * r, 1.3), 'wood', gain=gain * 0.95)
    c.paint(ellipse(x, y, 4.5, 4.5), 'wood', gain=gain * 1.2)


def loom(c, x, base, w=110, h=100):
    """機織り機: 木の枠、縦糸、織りかけの模様の布、梭。"""
    x0, x1, top = x - w / 2, x + w / 2, base - h
    for xx in (x0, x1):
        c.paint(rect(xx - 3, top, xx + 3, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0)
    for yy in (top, top + h * 0.55, base - 12):
        c.paint(rect(x0 - 4, yy - 3, x1 + 4, yy + 2, nrm(0, -0.4, 0.9)), 'wood', gain=1.05)
    for i in range(int(w / 3)):
        xx = x0 + 4 + i * 3
        c.paint(rect(xx, top + 2, xx + 1, top + h * 0.55), 'paper', gain=0.7, outline=False)
    cloth_top = top + h * 0.55
    o = c.obj()
    for py in range(int(cloth_top), int(base - 14)):
        for px in range(int(x0 + 4), int(x1 - 3)):
            band = int((py - cloth_top) / 6) % 4
            diamond = (abs((px - x) % 16 - 8) + abs((py - cloth_top) % 12 - 6)) < 5
            col = ('red', 'gold', 'blue', 'red')[band] if not diamond else 'paper'
            c.paint([(px, py, nrm(0, 0, 1))], col, oid=o, gain=0.9, outline=False)
    c.paint(capsule(x - 20, cloth_top - 6, x + 26, cloth_top - 8, 2.4, 1.2), 'wood', gain=1.3)


def cauldron(c, x, base, r=34, brew='purple'):
    """煮え鍋: 薪の火の上の黒い大鍋、泡立つ中身。"""
    for kk in range(4):
        c.paint(capsule(x - 30 + kk * 18, base, x - 20 + kk * 14, base - 8, 2.6), 'wood', gain=0.9)
    for kk in range(5):
        flame(c, x - 24 + kk * 12, base - 8 - 3 * hsh(kk, 9), 4, 8)
    c.paint(ellipse(x, base - r * 0.9, r, r * 0.75, clip=lambda px, py: py >= base - r * 1.3), 'silver', gain=0.5, spec=0.4)
    c.paint(ellipse(x, base - r * 1.3, r, r * 0.25), 'silver', gain=0.75)
    c.paint(ellipse(x, base - r * 1.3, r * 0.85, r * 0.18), brew, emit=lambda px, py, n: 0.7 + (0.2 if (int(px) + int(py) * 2) % 9 == 0 else 0))
    for kk in range(5):
        bx = x - r * 0.6 + kk * r * 0.3
        c.paint(ellipse(bx, base - r * 1.4 - (kk % 2) * 3, 2.5, 2.5), brew, emit=0.95, outline=False)
    for s in (-1, 1):
        c.paint(ellipse(x + s * r * 0.95, base - r * 1.2, 3.5, 4.5), 'silver', gain=0.7)


def campfire(c, x, base, s=1.0):
    k = s
    for kk in range(3):
        c.paint(capsule(x - 14 * k, base - kk * 2, x + 14 * k, base - 6 * k + kk * 4, 2.4 * k), 'wood', gain=0.8)
    for kk in range(4):
        flame(c, x - 7 * k + kk * 5 * k, base - 8 * k - 3 * hsh(kk, 1), 4 * k, 9 * k + 2 * hsh(kk, 2))
    flame(c, x, base - 16 * k, 5 * k, 12 * k)
    for kk in range(7):
        a = kk / 7 * math.pi * 2
        c.paint(ellipse(x + math.cos(a) * 18 * k, base + 2 + math.sin(a) * 4 * k, 3.5 * k, 2.5 * k), 'stone', gain=0.9)


def army_tent(c, x, base, w=100, h=70, ramp='paper', stripe='red'):
    """幕営: 尖った屋根の大きな天幕、入口の垂れ幕が開き中に灯。"""
    pts = [(x - w / 2, base), (x - w * 0.3, base - h * 0.6), (x, base - h), (x + w * 0.3, base - h * 0.6), (x + w / 2, base)]
    o = c.obj()
    for px, py, n in poly(pts, lambda px, py: nrm((px - x) / w * 1.4, -0.2, 0.8)):
        col = stripe if int((px - x) / 10 + 50) % 3 == 0 else ramp
        c.paint([(px, py, n)], col, oid=o, gain=0.95)
    c.paint(poly([(x - 10, base), (x, base - h * 0.5), (x + 10, base)]), 'fire', emit=0.6, outline=False)
    c.paint(poly([(x - 10, base), (x, base - h * 0.5), (x - 18, base)], nrm(-0.5, 0, 0.8)), ramp, gain=1.1)
    c.paint(capsule(x, base - h, x, base - h - 16, 1.2), 'wood', gain=1.0)
    c.paint(poly([(x, base - h - 16), (x + 14, base - h - 13), (x, base - h - 10)], nrm(-0.3, 0, 1)), stripe, gain=1.0)
    for s in (-1, 1):
        c.paint(capsule(x + s * w * 0.3, base - h * 0.6, x + s * (w / 2 + 16), base + 2, 0.5), 'paper', gain=0.6, outline=False)


def wayside_shrine(c, x, base):
    """辻の祠: 石の台に小さな屋根、中に蝋燭の灯。"""
    c.paint(rect(x - 8, base - 40, x + 8, base, nrm(-0.3, 0, 1)), 'stone', gain=1.0, tex=lambda px, py: -0.08 if int(py) % 6 == 0 else 0)
    c.paint(rect(x - 12, base - 62, x + 12, base - 40, nrm(-0.2, 0, 1)), 'stone', gain=1.0)
    c.paint(rect(x - 7, base - 58, x + 7, base - 44), 'fire', emit=0.55, outline=False)
    candle(c, x, base - 44, h=7, r=2, holder=False)
    c.paint(poly([(x - 18, base - 62), (x + 18, base - 62), (x, base - 76)], nrm(-0.2, -0.6, 0.8)), 'wood', gain=1.0)


def pyrite_rock(c, x, base, s=1.0):
    """黄鉄鉱: 岩から突き出た金色の立方体の結晶（にせ金）。"""
    rocks(c, [(x, base, 150 * s, 50 * s)], gain=0.85)
    cubes = [(-30, -30, 14), (-8, -40, 18), (16, -30, 15), (34, -22, 11), (-44, -18, 10), (4, -18, 12)]
    for dx, dy, sz in sorted(cubes, key=lambda t: t[1]):
        cx, cy, z = x + dx * s, base + dy * s, sz * s
        d = z * 0.45
        c.paint(poly([(cx, cy), (cx + z, cy), (cx + z + d, cy - d * 0.7), (cx + d, cy - d * 0.7)], UP), 'gold', gain=1.1, spec=0.8, shine=4)
        c.paint(poly([(cx + z, cy), (cx + z + d, cy - d * 0.7), (cx + z + d, cy + z - d * 0.7), (cx + z, cy + z)], nrm(0.85, 0, 0.5)), 'gold', gain=0.75, spec=0.4)
        o = c.paint(rect(cx, cy, cx + z, cy + z, nrm(-0.3, 0, 1)), 'gold', gain=0.95, spec=0.6, shine=5)
        for yy in range(int(cy + 3), int(cy + z), 4):
            c.paint(rect(cx + 1, yy, cx + z - 1, yy + 1), 'gold', oid=o, gain=0.7, outline=False)


def roots(c, x, ground_y):
    """地面の断面: 木の根が広がり、根もとに埋めた手紙の筒。"""
    c.paint(rect(0, ground_y, W, H, nrm(0, 0, 1)), 'leather', gain=0.55, dither=True, outline=False,
            tex=lambda px, py: -0.06 if (px * 5 + py * 3) % 13 == 0 else 0)
    c.paint(rect(0, ground_y - 2, W, ground_y + 1, UP), 'foliage', gain=0.9, outline=False)

    def branch(x0, y0, ang, ln, w, d):
        x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
        c.paint(capsule(x0, y0, x1, y1, w, w * 0.6), 'wood', gain=1.0)
        if d > 0:
            branch(x1, y1, ang - 0.45, ln * 0.7, w * 0.6, d - 1)
            branch(x1, y1, ang + 0.4, ln * 0.65, w * 0.6, d - 1)
    for ang in (0.5, 1.2, 1.9, 2.6):
        branch(x, ground_y, ang, 26, 4, 3)
    c.paint(capsule(x - 5, ground_y + 44, x + 18, ground_y + 38, 4), 'paper', gain=1.1)
    c.paint(rect(x + 4, ground_y + 36, x + 7, ground_y + 46), 'red', gain=1.0, outline=False)


def arch_bridge(c, x, top, w=160, span=80, ramp='stone'):
    """石の太鼓橋（下をくぐる道）。"""
    thick = 18
    pts = [(x - w / 2, top), (x + w / 2, top), (x + w / 2, H), (x + span / 2, H)] + \
          arc_points(x, top + thick + span * 0.45, span / 2, 0, -math.pi, 18)[1:] + [(x - span / 2, H), (x - w / 2, H)]
    c.paint(poly(pts, nrm(-0.2, 0, 1)), ramp, gain=1.0, tex=lambda px, py: -0.1 if (int(py) % 8 == 0 or (int(px) + (int(py) // 8) * 6) % 14 == 0) else 0)
    c.paint(rect(x - w / 2 - 2, top - 6, x + w / 2 + 2, top, UP), ramp, gain=1.15)


def rug(c, x, y, w=170, d=40, ramp='red'):
    """地べたに敷いた絨毯（縁取りと菱の模様）。"""
    pts = [(x - w / 2 + 14, y - d), (x + w / 2 - 14, y - d), (x + w / 2, y), (x - w / 2, y)]
    o = c.paint(poly(pts, UP), ramp, gain=0.9, tex=lambda px, py: -0.1 if (abs(int(px - x) % 20 - 10) + abs(int(py - y) % 10 - 5)) < 3 else 0)
    for t in (0.06, 0.94):
        c.paint(capsule(x - w / 2 + 14 * t, y - d * t, x + w / 2 - 14 * t, y - d * t, 0.8), 'gold', oid=o, gain=1.0, outline=False)


def haystack(c, x, base, r=24):
    c.paint(ellipse(x, base - r * 0.7, r, r * 0.95, clip=lambda px, py: py <= base), 'sand', gain=1.0,
            tex=lambda px, py: -0.1 if (int(px - py * 0.4) % 4 == 0) else 0)
    c.paint(capsule(x, base - r * 1.6, x, base - r * 1.8, 1.2), 'wood', gain=0.9)


def tracks(c, pts, ramp='stone'):
    """獣の足あと（4 つの指と掌の点）。"""
    for x, y in pts:
        c.paint(ellipse(x, y, 3.6, 2.4), ramp, gain=0.35, outline=False)
        for dx in (-3.5, -1.2, 1.2, 3.5):
            c.paint(ellipse(x + dx, y - 3.6, 1.1, 1.1), ramp, gain=0.35, outline=False)


def mushrooms(c, x, base, n=3):
    for kk in range(n):
        mx = x + kk * 9
        h = 8 + kk * 3
        c.paint(rect(mx - 1.5, base - h, mx + 1.5, base), 'paper', gain=0.9)
        c.paint(ellipse(mx, base - h, 6 - kk * 0.5, 3.5, clip=lambda px, py, b=base - h: py <= b + 1), 'red', gain=1.1, spec=0.3)
        c.dot(int(mx - 2), int(base - h - 1), 'S3')


def poster(c, x, y, w=30, h=40):
    """手配書（顔の絵と赤い字）。"""
    o = c.paint(rect(x - w / 2, y, x + w / 2, y + h, nrm(-0.2, 0, 1)), 'paper', gain=1.05)
    c.paint(ellipse(x, y + 16, 7, 8), 'leather', oid=o, gain=0.7, outline=False)
    c.paint(rect(x - 10, y + 4, x + 10, y + 7), 'red', oid=o, gain=1.0, outline=False)
    c.paint(rect(x - 10, y + h - 9, x + 10, y + h - 7), 'leather', oid=o, gain=0.6, outline=False)
    c.dot(int(x), int(y + 1), 'S2')


def gatehouse_roof(c, x, base, w=90, h=60):
    """村の木の門（屋根つきの冠木門）。"""
    for s in (-1, 1):
        c.paint(rect(x + s * w / 2 - 4, base - h, x + s * w / 2 + 4, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0 if s < 0 else 0.8)
    c.paint(rect(x - w / 2 - 8, base - h - 4, x + w / 2 + 8, base - h + 4, nrm(0, -0.3, 1)), 'wood', gain=1.05)
    c.paint(poly([(x - w / 2 - 16, base - h - 4), (x + w / 2 + 16, base - h - 4), (x + w / 2, base - h - 20), (x - w / 2, base - h - 20)],
                 nrm(-0.1, -0.7, 0.6)), 'red', gain=0.95, tex=lambda px, py: -0.1 if int(px) % 6 == 0 else 0)
    paper_lantern(c, x - 20, base - h + 14, 6, 'gold', string=base - h + 4)
    paper_lantern(c, x + 20, base - h + 14, 6, 'gold', string=base - h + 4)


def bindle():
    """肩に担いだ棒の先の包み（流れ者）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x - fig.f * 2.4 * u, y - 2.0 * u
        c.paint(capsule(x + fig.f * 0.4 * u, y + 0.3 * u, tx, ty, 0.13 * u), 'wood')
        c.paint(ellipse(tx, ty + 0.6 * u, 0.9 * u, 0.85 * u), 'red', gain=1.0, tex=lambda px, py: -0.1 if (int(px) + int(py)) % 4 == 0 else 0)
    return draw


def held_dividers():
    def draw(c, fig, hand):
        u = fig.u
        dividers(c, hand[0], hand[1] + 1.8 * u, ln=2.0 * u)
    return draw


def held_wheel():
    def draw(c, fig, hand):
        wheel(c, hand[0] + fig.f * 1.6 * fig.u, hand[1] + 0.4 * fig.u, r=1.7 * fig.u)
    return draw


def silver_plate():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.4 * u, hand[1] - 1.0 * u
        c.paint(ellipse(x, y, 1.3 * u, 1.3 * u), 'silver', spec=0.8, shine=5)
        c.paint(ellipse(x, y, 0.8 * u, 0.8 * u), 'silver', gain=0.8)
    return draw


def road_cross(c, y, ramp='sand'):
    """横に交わる道（左右の奥へ細る）。"""
    pts = [(0, y - 6), (W, y - 6), (W, y + 8), (0, y + 8)]
    c.paint(poly(pts, UP), ramp, gain=0.9, dither=True)


def terraces(c, y0):
    """段に均した斜面: 段ごとの土の面と、石積みの縁。"""
    for k in range(4):
        top = y0 + k * 16
        c.paint(rect(0, top, W, top + 10, UP), 'leather', gain=0.85 + k * 0.05, dither=True, outline=False,
                tex=lambda px, py: -0.06 if (px * 3 + py) % 11 == 0 else 0)
        stone_wall(c, int(top + 10), int(top + 16), bw=10, bh=6, gain=0.85, seed=20 + k)


def wheelbarrow(c, x, base):
    wheel(c, x - 20, base - 9, r=9)
    c.paint(poly([(x - 30, base - 30), (x + 18, base - 32), (x + 10, base - 14), (x - 22, base - 12)], nrm(-0.2, 0, 1)), 'wood', gain=1.0)
    c.paint(ellipse(x - 6, base - 31, 22, 5), 'leather', gain=0.8)
    for s in (0, 6):
        c.paint(capsule(x + 14, base - 22 + s, x + 40, base - 14 + s, 1.4), 'wood', gain=0.9)
    c.paint(capsule(x + 8, base - 14, x + 10, base, 1.4), 'wood', gain=0.8)


def spade_stuck(c, x, base):
    """土に突き立てた鋤。"""
    c.paint(capsule(x, base - 4, x + 6, base - 50, 1.6), 'wood', gain=1.0)
    c.paint(capsule(x + 1, base - 52, x + 11, base - 50, 1.6), 'wood', gain=1.0)
    c.paint(poly([(x - 6, base - 6), (x + 6, base - 6), (x + 5, base + 6), (x, base + 9), (x - 5, base + 6)], nrm(-0.3, -0.2, 0.9)), 'silver', spec=0.6)


def cascade(c, x, y0, y1):
    """岩の割れ目から落ちる水。"""
    for k in range(4):
        xx = x - 6 + k * 4
        c.paint(capsule(xx, y0, xx + (k - 1.5) * 2, y1, 1.6), 'water', emit=0.75 - k * 0.06, outline=False)
    for k in range(10):
        c.dot(int(x - 12 + hsh(k, 7) * 24), int(y1 - 2 + hsh(7, k) * 6), 'S3')


def foliage_top(c, y):
    """橋の上の草むら。"""
    pix = [(x, yy, nrm(0, -0.6, 0.8)) for x in range(W) for yy in range(int(y - 3 - 2 * math.sin(x / 5)), int(y + 4))]
    c.paint(pix, 'foliage', gain=0.8, outline=False, dither=True)


def reeds(c, xs, base):
    for x in xs:
        for k in range(5):
            dx = (k - 2) * 2.5
            c.paint(capsule(x + dx, base, x + dx * 2, base - 24 - k % 3 * 6, 0.7), 'foliage', gain=0.9, outline=False)
        c.paint(capsule(x, base - 30, x, base - 38, 1.6), 'leather', gain=1.0)


def horse_head(c, x, y, ramp='leather', s=1.0):
    """仕切り戸から突き出た馬の頭と首（正面寄り）。"""
    c.paint(capsule(x - 4 * s, y + 36 * s, x, y + 4 * s, 12 * s, 9 * s), ramp, gain=0.95)
    c.paint(capsule(x, y + 4 * s, x + 12 * s, y + 24 * s, 9 * s, 6 * s), ramp, gain=1.05)
    for sg in (-1, 1):
        c.paint(poly([(x + (sg * 4 - 3) * s, y - 4 * s), (x + (sg * 4 + 3) * s, y - 4 * s), (x + sg * 4 * s, y - 14 * s)], nrm(-0.3, -0.4, 0.8)), ramp, gain=1.0)
    for i in range(6):
        c.paint(capsule(x - 8 * s, y - 2 * s + i * 6 * s, x - 12 * s, y + 2 * s + i * 6 * s, 1.8 * s), 'hair', gain=1.0, outline=False)
    c.dot(int(x + 4 * s), int(y + 6 * s), 'N0')
    c.paint(ellipse(x + 12 * s, y + 26 * s, 2, 1.5), 'hair', gain=0.6, outline=False)
    c.paint(rect(x - 4 * s, y + 12 * s, x + 12 * s, y + 14 * s), 'red', gain=0.9, outline=False)


def stall_door(c, x0, x1, top, base):
    """馬房の仕切り戸（板と斜めの補強）。"""
    c.paint(rect(x0, top, x1, base, nrm(-0.2, 0, 1)), 'wood', gain=0.95, tex=lambda px, py: -0.1 if int(px - x0) % 10 == 0 else 0)
    c.paint(rect(x0 - 2, top - 4, x1 + 2, top, UP), 'wood', gain=1.15)
    c.paint(capsule(x0 + 4, base - 4, x1 - 4, top + 4, 2), 'wood', gain=1.1, outline=False)


def pitch_lean(c, x, base):
    c.paint(capsule(x, base, x + 10, base - 80, 1.4), 'wood', gain=0.9)
    for dx in (-3, 0, 3):
        c.paint(capsule(x + 10 + dx, base - 80, x + 11 + dx, base - 92, 0.8), 'silver', gain=0.9)


def charms(c, x0, x1, y):
    """軒から下がるまじないの品（骨・羽・小さな袋・輪）。"""
    n = 6
    for k in range(n):
        x = x0 + k * (x1 - x0) / (n - 1)
        ln = 8 + (k % 3) * 5
        c.paint(rect(x, y, x + 1, y + ln), 'paper', gain=0.6, outline=False)
        kind = k % 4
        if kind == 0:
            c.paint(capsule(x - 3, y + ln + 3, x + 3, y + ln + 3, 1.2), 'paper', gain=1.1)
        elif kind == 1:
            c.paint(capsule(x, y + ln, x - 1, y + ln + 8, 1.6, 0.4), 'red', gain=1.0)
        elif kind == 2:
            c.paint(ellipse(x, y + ln + 3, 3, 3.5), 'leather', gain=1.0)
        else:
            pts = arc_points(x, y + ln + 4, 3.5, 0, math.pi * 2, 10)
            for a, b in zip(pts, pts[1:]):
                c.paint(capsule(a[0], a[1], b[0], b[1], 0.6), 'gold', gain=1.0, outline=False)


def comet(c, x, y):
    """ほうき星: 明るい頭と、右下へ伸びる尾。"""
    for k in range(18):
        t = k / 17
        c.paint(ellipse(x + t * 70, y + t * 26, 4 - t * 3, 2.4 - t * 1.6), 'paper', emit=0.95 - t * 0.6, outline=False, dither=True)
    c.paint(ellipse(x, y, 4, 4), 'paper', emit=1.0, outline=False)


def banner_pole(c, x, base):
    c.paint(capsule(x, base, x, base - 80, 1.5), 'wood', gain=1.0)
    c.paint(poly([(x, base - 80), (x - 22, base - 76), (x - 20, base - 52), (x, base - 56)], lambda px, py: nrm(0.4 * math.sin(px / 3), 0, 0.9)), 'blue', gain=1.0)


def dug_hole(c, x, y):
    c.paint(ellipse(x, y, 46, 14), 'leather', emit=0.06, outline=False)
    for k in range(6):
        rx = x + 40 + k * 6
        c.paint(ellipse(rx, y - 4 + (k % 2) * 4, 7, 4), 'leather', gain=0.95)


def mud(c, x, y):
    c.paint(ellipse(x, y, 76, 18), 'leather', gain=0.55, spec=0.3, dither=True)
    c.paint(ellipse(x - 20, y - 2, 30, 6), 'water', emit=0.25, outline=False)


def rat(c, x, base):
    c.paint(ellipse(x, base - 6, 10, 6), 'cloth', gain=0.7)
    c.paint(ellipse(x - 9, base - 8, 5, 4), 'cloth', gain=0.75)
    c.paint(ellipse(x - 8, base - 12, 2, 2), 'red', gain=0.6)
    c.dot(int(x - 11), int(base - 9), 'N0')
    c.paint(capsule(x + 9, base - 4, x + 22, base - 1, 0.7), 'red', gain=0.6, outline=False)


def trail(c, x, top, base):
    """森の奥へ消える細い踏み分け道（うねる）。"""
    pix = []
    for y in range(int(top), H):
        t = (y - top) / (base - top)
        cx = x + 14 * math.sin(t * 4)
        w = 6 + 50 * t
        for xx in range(int(cx - w / 2), int(cx + w / 2)):
            pix.append((xx, y, UP))
    c.paint(pix, 'sand', gain=0.8, dither=True, outline=False)


def trunk(c, x, top, base, w=16):
    c.paint(rect(x - w / 2, top, x + w / 2, base, lambda px, py: nrm((px - x) / w * 1.6, 0, 0.8)), 'wood', gain=0.95,
            tex=lambda px, py: -0.07 if (int(py) + int(px) * 7) % 13 == 0 else 0)


def veil(c, x, y):
    """頭からかけた薄いヴェール（市松で透ける）。"""
    pix = []
    for yy in range(int(y - 8), int(y + 34)):
        w = 12 + (yy - y) * 0.4
        for xx in range(int(x - w), int(x + w)):
            if (xx + yy) % 2 == 0 and abs(xx - x) > 5 + max(0, (yy - y)) * 0.1:
                pix.append((xx, yy, FLAT))
    c.paint(pix, 'paper', emit=0.55, outline=False)


def boots_pair(c, x, base):
    for dx in (0, 14):
        c.paint(capsule(x + dx, base - 18, x + dx, base - 4, 4), 'leather', gain=1.0)
        c.paint(ellipse(x + dx + 4, base - 3, 7, 3), 'leather', gain=0.9)


def broken_barrel(c, x, base):
    """割れた樽: 板が散り、中身がこぼれる。"""
    for k, (dx, ang) in enumerate(((-24, -0.6), (-10, -0.2), (6, 0.3), (20, 0.8))):
        c.paint(capsule(x + dx, base, x + dx + math.sin(ang) * 26, base - math.cos(ang) * 26, 3, flat=0.4), 'wood', gain=1.0 - k * 0.05)
    c.paint(rect(x - 26, base - 18, x + 26, base - 15), 'silver', gain=0.8)
    c.paint(ellipse(x + 10, base + 2, 30, 5), 'red', gain=0.7)


def spice_sacks(c, x, base):
    """口を開けた香料の袋（赤・金・茶・緑の山）。"""
    cols = ('red', 'gold', 'leather', 'green', 'copper')
    for k, col in enumerate(cols):
        sx = x - 84 + k * 42
        c.paint(ellipse(sx, base - 14, 19, 16), 'paper', gain=0.85)
        c.paint(ellipse(sx, base - 26, 17, 6), 'paper', gain=1.0)
        c.paint(ellipse(sx, base - 28, 14, 7, clip=lambda px, py, b=base - 26: py <= b), col, gain=1.1)


def toolbox():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] + 0.6 * u
        c.paint(rect(x - 1.4 * u, y, x + 1.4 * u, y + 1.1 * u, nrm(-0.2, 0, 1)), 'wood', gain=1.0)
        c.paint(capsule(x - 0.6 * u, y - 0.2 * u, x + 0.6 * u, y - 0.2 * u, 0.12 * u), 'wood')
        c.paint(capsule(x - 0.9 * u, y - 0.1 * u, x - 0.4 * u, y - 0.9 * u, 0.12 * u), 'silver', gain=1.0)
    return draw


# ================= 収穫祭＆ギルド（guilds）で足した部品 =================

def royal_crown(c, x, y, w=70, h=44, ramp='gold', arches=True):
    """王冠: 宝石の帯、尖り、上のアーチと十字の玉。"""
    band_y = y
    c.paint(ellipse(x, band_y, w / 2, w * 0.13), ramp, gain=0.7)
    if arches:
        for sg in (-1, 1):
            pts = [(x + sg * w * 0.45 * math.cos(t), band_y - h * 0.9 * math.sin(t)) for t in [i / 10 * math.pi / 2 for i in range(11)]]
            for a, b in zip(pts, pts[1:]):
                c.paint(capsule(a[0], a[1], b[0], b[1], 2.2), ramp, spec=0.7, shine=5)
        c.paint(ellipse(x, band_y - h * 0.5, w * 0.36, h * 0.42, clip=lambda px, py: py < band_y - 4), 'red', gain=0.8)
        c.paint(ellipse(x, band_y - h * 0.95, 4, 4), ramp, spec=0.7)
        c.paint(rect(x - 1, band_y - h * 0.95 - 10, x + 1, band_y - h * 0.95 - 3), ramp, gain=1.1)
        c.paint(rect(x - 4, band_y - h * 0.95 - 8, x + 4, band_y - h * 0.95 - 6), ramp, gain=1.1)
    for k in range(5):
        px = x - w * 0.4 + k * w * 0.2
        c.paint(poly([(px - 5, band_y - 4), (px + 5, band_y - 4), (px, band_y - 18 + (4 if k % 2 else 0))], nrm(-0.3, -0.3, 0.9)), ramp, spec=0.7)
        c.paint(ellipse(px, band_y - 16 + (4 if k % 2 else 0), 2.6, 2.6), ramp, spec=0.8)
    c.paint(rect(x - w / 2, band_y - 6, x + w / 2, band_y + 6, lambda px, py: nrm((px - x) / w * 1.4, 0, 0.8)), ramp, spec=0.7, shine=5)
    for k, col in enumerate(('red', 'blue', 'green', 'blue', 'red')):
        gem(c, x - w * 0.4 + k * w * 0.2, band_y, 3.4, col)


def light_rays(c, x, y, n=9, ln=70, ramp='gold'):
    """後光の筋（市松で透ける細い三角）。"""
    for k in range(n):
        a = -math.pi + (k + 0.5) * math.pi / n
        w = 0.07
        pts = [(x, y), (x + math.cos(a - w) * ln, y + math.sin(a - w) * ln), (x + math.cos(a + w) * ln, y + math.sin(a + w) * ln)]
        pix = [(px, py, n_) for px, py, n_ in poly(pts) if (px + py) % 2 == 0]
        c.paint(pix, ramp, emit=0.55, outline=False)


def laurel(c, x, y, r=34):
    """月桂冠: 円に並ぶ葉と、下で結んだ赤い紐。"""
    for sg in (-1, 1):
        for k in range(9):
            a = math.pi / 2 + sg * (0.35 + k * 0.28)
            px, py = x + math.cos(a) * r, y - math.sin(a) * r * 0.9
            c.paint(ellipse(px, py, 5, 3), 'green', gain=1.0 + 0.1 * (k % 2), spec=0.3)
    c.paint(poly([(x - 4, y + r * 0.9), (x + 4, y + r * 0.9), (x + 10, y + r * 0.9 + 16), (x, y + r * 0.9 + 6), (x - 10, y + r * 0.9 + 16)]), 'red', gain=1.05)


def trumpet(c, x, y, ang=-20, ln=60, banner='blue'):
    """ラッパ（下がる旗つき）。"""
    a = math.radians(ang)
    x1, y1 = x + math.cos(a) * ln, y + math.sin(a) * ln
    c.paint(capsule(x, y, x1, y1, 1.6, 2.6), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x1, y1, 4, 8), 'gold', spec=0.7)
    mx, my = x + math.cos(a) * ln * 0.5, y + math.sin(a) * ln * 0.5
    c.paint(poly([(mx - 12, my), (mx + 12, my - 4), (mx + 12, my + 14), (mx, my + 10), (mx - 12, my + 18)], lambda px, py: nrm(0.3 * math.sin(px / 3), 0, 0.9)), banner, gain=1.0)


def money_bag(c, x, base, r=34, ramp='leather'):
    """金の袋: 金の紐で口を縛った大袋、こぼれる金貨。"""
    c.paint(ellipse(x, base - r, r, r * 0.95), ramp, gain=1.05, spec=0.2)
    c.paint(poly([(x - 10, base - r * 1.85), (x + 10, base - r * 1.85), (x + 18, base - r * 2.3), (x - 18, base - r * 2.3)], nrm(-0.2, -0.5, 0.8)), ramp, gain=1.0)
    c.paint(rect(x - 12, base - r * 1.95, x + 12, base - r * 1.8), 'gold', spec=0.6)
    coin(c, x - 8, base - r * 1.1, r * 0.36, 'gold', tilt=0.95, stamp='crown')
    for k in range(5):
        coin(c, x + r * 0.9 + k * 9, base - 2 - (k % 2) * 3, 6, 'gold', stamp=('star', 'crown')[k % 2])


def cornucopia(c, x, y, s=1.0):
    """実りの角: 巻いた角の籠から、果物とパンと葡萄があふれる。"""
    k = s
    for i in range(16):
        t = i / 15
        cx = x + 50 * k * (1 - t) - 10 * k * math.sin(t * 3)
        cy = y - 20 * k * math.sin(t * math.pi) + 14 * k * t
        r = 4 * k + 22 * k * t
        c.paint(ellipse(cx, cy, r * 0.6, r), 'wood', gain=1.2 - 0.3 * (i % 2), tex=lambda px, py: -0.1 if (px + py) % 4 == 0 else 0)
    ex, ey = x - 10 * k * math.sin(3), y + 14 * k
    c.paint(ellipse(ex - 2 * k, ey, 14 * k, 24 * k), 'wood', gain=1.35)
    c.paint(ellipse(ex - 1 * k, ey, 10 * k, 20 * k), 'wood', gain=0.35, outline=False)
    mx, my = ex - 2 * k, y + 16 * k
    for dx, dy, kind in ((-18, 4, 'apple'), (-6, -12, 'grape'), (-28, -6, 'bread'), (-8, 12, 'apple2'), (-34, 14, 'grape'), (-22, 24, 'pear')):
        px, py = mx + dx * k, my + dy * k
        if kind.startswith('apple'):
            c.paint(ellipse(px, py, 7 * k, 6.5 * k), 'red' if kind == 'apple' else 'green', spec=0.5)
        elif kind == 'grape':
            for r_, cnt in enumerate((3, 2, 1)):
                for j in range(cnt):
                    c.paint(ellipse(px + (j - (cnt - 1) / 2) * 3.6 * k, py + r_ * 3.4 * k, 2.2 * k, 2.2 * k), 'purple', gain=1.15, spec=0.5)
        elif kind == 'bread':
            c.paint(ellipse(px, py, 9 * k, 5 * k), 'wood', gain=1.4, spec=0.2)
        else:
            c.paint(ellipse(px, py, 5 * k, 7 * k), 'gold', spec=0.4)


def turnip(c, x, base, r=40):
    """大かぶ: 白から紫へ変わる丸い根と、大きな葉。"""
    for k, (dx, h) in enumerate(((-18, 50), (0, 62), (18, 48), (-8, 40), (10, 44))):
        c.paint(capsule(x + dx * 0.3, base - r * 1.6, x + dx, base - r * 1.6 - h, 3.2, 1.0), 'green', gain=0.95)
        c.paint(ellipse(x + dx, base - r * 1.6 - h * 0.8, 9, 14), 'green', gain=1.05 + 0.08 * (k % 2), spec=0.2)
    c.paint(ellipse(x, base - r * 0.85, r, r * 0.85), 'paper', gain=1.1, spec=0.3)
    c.paint(ellipse(x, base - r * 1.25, r * 0.85, r * 0.42, clip=lambda px, py: py < base - r * 1.15), 'purple', gain=1.0, spec=0.3)
    c.paint(capsule(x, base - 4, x + 4, base + 6, 2, 0.4), 'paper', gain=0.9)


def windmill(c, x, base, h=80):
    """風車: 石の塔、円錐の屋根、4 枚の羽根。"""
    c.paint(poly([(x - 18, base), (x + 18, base), (x + 12, base - h), (x - 12, base - h)], lambda px, py: nrm((px - x) / 18 * 0.8, 0, 0.7)), 'paper', gain=0.9,
            tex=lambda px, py: -0.06 if int(py) % 8 == 0 else 0)
    c.paint(poly([(x - 15, base - h), (x + 15, base - h), (x, base - h - 20)], nrm(-0.3, -0.5, 0.8)), 'red', gain=0.9)
    window(c, x - 3, base - h * 0.6, 6, 8, True, arch=True)
    c.paint(rect(x - 5, base - 16, x + 5, base), 'wood', gain=0.8)
    hx, hy = x + 2, base - h - 2
    for k in range(4):
        a = k * math.pi / 2 + 0.35
        ex, ey = hx + math.cos(a) * 52, hy + math.sin(a) * 52
        c.paint(capsule(hx, hy, ex, ey, 1.5), 'wood', gain=1.0)
        px, py = -math.sin(a), math.cos(a)
        pts = [(hx + math.cos(a) * 12, hy + math.sin(a) * 12), (ex, ey), (ex + px * 10, ey + py * 10), (hx + math.cos(a) * 12 + px * 10, hy + math.sin(a) * 12 + py * 10)]
        o = c.obj()
        for qx, qy, n in poly(pts, nrm(-0.2, -0.2, 0.9)):
            c.paint([(qx, qy, n)], 'paper' if (qx + qy) % 4 else 'wood', oid=o, gain=0.95)
    c.paint(ellipse(hx, hy, 3.5, 3.5), 'wood', gain=1.2)


def maypole(c, x, base, h=110, ribbons=('red', 'blue', 'gold', 'green', 'purple', 'paper')):
    """五月柱: 柱の頂の花輪から、色の帯が広がる。"""
    c.paint(capsule(x, base, x, base - h, 2.4), 'wood', gain=1.0)
    for k, col in enumerate(ribbons):
        a = math.pi * (0.1 + k * 0.16)
        ex = x + math.cos(a) * 90
        ey = base - 4 + math.sin(a) * 6
        pts = [(x + (ex - x) * t + math.sin(t * 6 + k) * 3, base - h + (ey - base + h) * t) for t in [i / 10 for i in range(11)]]
        for a2, b2 in zip(pts, pts[1:]):
            c.paint(capsule(a2[0], a2[1], b2[0], b2[1], 1.4), col, gain=1.05)
    pts = arc_points(x, base - h + 4, 10, 0, math.pi * 2, 14)
    for px, py in pts:
        c.paint(ellipse(px, py, 3, 2.4), ('green', 'red')[int(px) % 2], gain=1.0)


def potter_wheel(c, x, base):
    """ろくろ: 回る台の上で形を直す壺と、割れた壺の欠片。"""
    c.paint(ellipse(x, base, 34, 8), 'wood', gain=0.8)
    c.paint(rect(x - 34, base - 8, x + 34, base), 'wood', gain=0.75)
    c.paint(ellipse(x, base - 8, 34, 8, normal=UP), 'wood', gain=1.1, tex=lambda px, py: -0.1 if int(math.hypot((px - x) / 4, py - base + 8)) % 2 == 0 else 0)
    c.paint(ellipse(x, base - 26, 20, 17), 'copper', gain=1.0, spec=0.4)
    c.paint(capsule(x, base - 40, x, base - 50, 8, 6), 'copper', gain=1.05, spec=0.4)
    c.paint(ellipse(x, base - 52, 9, 3), 'copper', gain=1.1)
    c.paint(ellipse(x, base - 52, 6, 2), 'copper', gain=0.5)
    for sg in (-1, 1):
        c.paint(ellipse(x + sg * 24, base - 30, 5, 4), 'skin', gain=1.05)
    for k in range(5):
        a = k * 1.3
        sx, sy = x + 60 + k * 9, base + 6 - (k % 2) * 4
        c.paint(poly([(sx, sy), (sx + 8, sy - 3), (sx + 5, sy + 4)], nrm(-0.3, -0.5, 0.8)), 'copper', gain=0.95)


def bread_oven(c, x, y, w=90, h=60):
    """パン窯: 煉瓦の丸い窯の口に火、パンの並ぶ棚。"""
    stone_wall(c, int(y), int(y + h), x0=int(x), x1=int(x + w), bw=8, bh=5, ramp='red', gain=0.85, seed=11)
    mx, my, mw = x + w * 0.2, y + h * 0.35, w * 0.6
    pts = [(mx, y + h), (mx, my + mw * 0.3)] + arc_points(mx + mw / 2, my + mw * 0.3, mw / 2, math.pi, 2 * math.pi, 12) + [(mx + mw, y + h)]
    c.paint(poly(pts), 'fire', emit=lambda px, py, n: 0.95 - (y + h - py) / h * 0.5)
    for k in range(4):
        c.paint(ellipse(mx + 8 + k * (mw - 16) / 3, y + h - 6, 6, 3.5), 'wood', gain=1.3, spec=0.2)


def hanging_meats(c, x0, x1, y):
    c.paint(capsule(x0, y, x1, y, 1.6), 'wood', gain=1.0)
    n = 5
    for k in range(n):
        x = x0 + 10 + k * (x1 - x0 - 20) / (n - 1)
        c.paint(rect(x, y, x + 1, y + 6), 'silver', gain=0.8, outline=False)
        if k % 2 == 0:
            c.paint(ellipse(x, y + 20, 8, 14), 'copper', gain=1.0, spec=0.3)
            c.paint(capsule(x, y + 6, x, y + 10, 2), 'paper', gain=1.0)
        else:
            for j in range(4):
                c.paint(ellipse(x, y + 10 + j * 6, 3, 3.4), 'red', gain=0.95)


def bed(c, x, base, w=120):
    """寝台: 枠、布団、枕、足もとの毛布の折り目。"""
    c.paint(rect(x - w / 2, base - 40, x - w / 2 + 6, base, nrm(-0.3, 0, 1)), 'wood', gain=1.0)
    c.paint(rect(x - w / 2, base - 22, x + w / 2, base - 8, nrm(-0.1, 0, 1)), 'wood', gain=0.9)
    c.paint(rect(x - w / 2 + 4, base - 30, x + w / 2, base - 20, lambda px, py: nrm(0.2 * math.sin(px / 6), -0.5, 0.8)), 'blue', gain=1.0)
    c.paint(ellipse(x - w / 2 + 20, base - 32, 14, 6), 'paper', gain=1.15)
    c.paint(rect(x + w / 4, base - 31, x + w / 2, base - 20), 'red', gain=0.9, tex=lambda px, py: -0.1 if int(px) % 6 == 0 else 0)


def spools_shelf(c, x0, x1, top, base):
    """小間物の棚: 糸巻き、リボンの巻き、釦の箱、鋏。"""
    c.paint(rect(x0, top, x1, base, nrm(0, 0, 1)), 'wood', gain=0.35, outline=False)
    cols = ('red', 'blue', 'gold', 'green', 'purple', 'paper')
    for r, y in enumerate((top + 30, top + 60, base - 2)):
        c.paint(rect(x0, y, x1, y + 3, nrm(0, -0.6, 0.8)), 'wood', gain=1.0)
        for k in range(int((x1 - x0) / 16)):
            sx = x0 + 10 + k * 16
            col = cols[(k + r * 2) % len(cols)]
            if r == 1:
                c.paint(ellipse(sx, y - 7, 6, 7), col, gain=1.05, spec=0.3)
                c.paint(ellipse(sx, y - 7, 2, 2), 'wood', gain=0.8, outline=False)
            else:
                c.paint(rect(sx - 4, y - 14, sx + 4, y - 2, lambda px, py, sx=sx: nrm((px - sx) / 4 * 0.8, 0, 0.7)), col, gain=1.05)
                c.paint(rect(sx - 5, y - 15, sx + 5, y - 13), 'wood', gain=1.1)
                c.paint(rect(sx - 5, y - 3, sx + 5, y - 1), 'wood', gain=1.1)
    for x in (x0, x1 - 4):
        c.paint(rect(x, top, x + 4, base, nrm(-0.3, 0, 0.95)), 'wood', gain=0.9)


def telescope(c, x, base):
    """星を見る大きな望遠鏡（三脚の上）。"""
    for dx in (-16, 4, 16):
        c.paint(capsule(x, base - 44, x + dx, base, 1.4), 'wood', gain=0.9)
    c.paint(capsule(x - 30, base - 30, x + 30, base - 70, 4, 6), 'gold', spec=0.7, shine=5)
    c.paint(ellipse(x + 30, base - 70, 4, 7), 'water', emit=0.6)
    for t in (0.3, 0.6):
        cx, cy = x - 30 + 60 * t, base - 30 - 40 * t
        c.paint(capsule(cx - 2, cy - 3, cx + 2, cy + 3, 5), 'gold', gain=0.8)


def constellation(c, pts):
    for a, b in zip(pts, pts[1:]):
        for t in range(0, 10, 2):
            ax, ay = a[0] + (b[0] - a[0]) * t / 10, a[1] + (b[1] - a[1]) * t / 10
            c.dot(int(ax), int(ay), 'S1')
    for x, y in pts:
        c.dot(x, y, 'S3')
        c.dot(x + 1, y, 'S2')
        c.dot(x, y + 1, 'S2')


def wheat_sheaves(c, x, base, n=3):
    """麦の束（縛った茎と、垂れた穂）。"""
    for k in range(n):
        sx = x + k * 40
        c.paint(poly([(sx - 8, base), (sx + 8, base), (sx + 4, base - 22), (sx - 4, base - 22)], lambda px, py: nrm((px - sx) / 8 * 0.7, 0, 0.8)), 'gold', gain=0.95,
                tex=lambda px, py: -0.1 if int(px) % 2 == 0 else 0)
        for j in range(13):
            dx = (j - 6) * 1.5
            c.paint(capsule(sx + dx * 0.3, base - 20, sx + dx * 2.0, base - 38, 0.9), 'gold', gain=0.75 + (j % 2) * 0.1, outline=False)
            c.paint(ellipse(sx + dx * 2.2, base - 42, 2.0, 4.2), 'gold', gain=0.85 + (j % 3) * 0.08)
        c.paint(rect(sx - 5, base - 20, sx + 5, base - 17), 'leather', gain=1.0)


def pavilion(c, x, base, w=60, h=60, ramp='red'):
    """武芸大会の天幕（丸い屋根と縞の幕）。"""
    o = c.obj()
    for px, py, n in poly([(x - w / 2, base), (x - w / 2, base - h * 0.6), (x + w / 2, base - h * 0.6), (x + w / 2, base)], lambda px, py: nrm((px - x) / w * 1.2, 0, 0.8)):
        c.paint([(px, py, n)], ramp if int((px - x) / 8 + 20) % 2 else 'paper', oid=o, gain=0.95)
    c.paint(poly([(x - w / 2 - 4, base - h * 0.6), (x + w / 2 + 4, base - h * 0.6), (x, base - h)], lambda px, py: nrm((px - x) / w, -0.4, 0.8)), ramp, gain=1.0)
    c.paint(capsule(x, base - h, x, base - h - 14, 1), 'wood')
    c.paint(poly([(x, base - h - 14), (x + 12, base - h - 11), (x, base - h - 8)]), 'gold', gain=1.0)


def lance_rack(c, x, base):
    for k in range(3):
        c.paint(capsule(x + k * 10, base, x + k * 10 + 8, base - 90, 1.6, 1.0), ('red', 'blue', 'paper')[k], gain=1.0)
    c.paint(rect(x - 6, base - 30, x + 34, base - 26, nrm(0, -0.4, 0.9)), 'wood', gain=1.0)


def big_gem(c, x, y, r=40, ramp='green'):
    """逸品: 多面にカットした大きな宝石（台の上）。"""
    c.paint(poly([(x - r * 0.7, y + r * 0.95), (x + r * 0.7, y + r * 0.95), (x + r * 0.5, y + r * 0.75), (x - r * 0.5, y + r * 0.75)], nrm(-0.2, -0.5, 0.8)), 'gold', spec=0.7)
    top = [(x - r, y), (x - r * 0.55, y - r * 0.5), (x + r * 0.55, y - r * 0.5), (x + r, y)]
    c.paint(poly(top, nrm(-0.2, -0.8, 0.6)), ramp, gain=1.15, spec=0.8, shine=4)
    c.paint(poly([(x - r * 0.3, y - r * 0.5), (x + r * 0.3, y - r * 0.5), (x + r * 0.2, y - r * 0.2), (x - r * 0.2, y - r * 0.2)], nrm(-0.1, -0.9, 0.5)), ramp, gain=1.35)
    facets = [((x - r, y), (x - r * 0.4, y), (x, y + r * 0.8), nrm(-0.7, 0.1, 0.7)), ((x - r * 0.4, y), (x + r * 0.4, y), (x, y + r * 0.8), nrm(0, 0.2, 1)),
              ((x + r * 0.4, y), (x + r, y), (x, y + r * 0.8), nrm(0.7, 0.3, 0.6))]
    for a, b, cc, n in facets:
        c.paint(poly([a, b, cc], n), ramp, gain=1.0, spec=0.5)
    for k in range(5):
        c.dot(int(x - r * 0.5 + k * 3), int(y - r * 0.38 - (k % 2)), 'G6')


def scythe():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        tx, ty = x + fig.f * 1.0 * u, y - 3.0 * u
        c.paint(capsule(x - fig.f * 0.6 * u, y + 2.0 * u, tx, ty, 0.14 * u), 'wood')
        pts = [(tx + fig.f * 2.6 * u * t, ty + 1.2 * u * t * t) for t in [i / 8 for i in range(9)]]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.22 * u * (1 - i / 9)), 'silver', spec=0.7)
    return draw


def broom():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        bx, by = x + fig.f * 1.2 * u, fig.foot - 0.4 * u
        c.paint(capsule(x - fig.f * 1.0 * u, y - 2.4 * u, bx, by - 1.2 * u, 0.13 * u), 'wood')
        for k in range(7):
            c.paint(capsule(bx, by - 1.2 * u, bx + fig.f * (k - 3) * 0.25 * u, by + 0.4 * u, 0.12 * u), 'sand', gain=1.0)
    return draw


def cleaver():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y + 0.4 * u, x, y - 0.6 * u, 0.15 * u), 'wood')
        c.paint(rect(x - 0.2 * u, y - 2.0 * u, x + fig.f * 1.2 * u, y - 0.6 * u, nrm(-0.3, -0.2, 0.9)), 'silver', spec=0.8, shine=5)
    return draw


def hunting_horn():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        pts = [(x + fig.f * t * 1.6 * u, y - math.sin(t * 2.5) * 0.9 * u) for t in [i / 8 for i in range(9)]]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.1 * u + i * 0.05 * u), 'gold', spec=0.7)
        ex, ey = pts[-1]
        c.paint(ellipse(ex, ey, 0.3 * u, 0.55 * u), 'gold', spec=0.7)
    return draw


def peel():
    """パン窯の木べら（先にパン）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        ex = x + fig.f * 3.2 * u
        c.paint(capsule(x - fig.f * 0.5 * u, y + 0.2 * u, ex, y - 0.3 * u, 0.13 * u), 'wood')
        c.paint(ellipse(ex + fig.f * 0.6 * u, y - 0.3 * u, 0.9 * u, 0.3 * u), 'wood', gain=1.2)
        c.paint(ellipse(ex + fig.f * 0.6 * u, y - 0.65 * u, 0.7 * u, 0.35 * u), 'wood', gain=1.45, spec=0.2)
    return draw


def juggle():
    """宙に放った 3 つの玉（道化）。"""
    def draw(c, fig, hand):
        u = fig.u
        for k, col in enumerate(('red', 'gold', 'blue')):
            c.paint(ellipse(fig.x + (k - 1) * 1.4 * u, fig.y_head - 1.4 * u - (k % 2) * 0.8 * u, 0.4 * u, 0.4 * u), col, spec=0.6)
    return draw


def halberd():
    """近衛の斧槍。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        top = y - 5.4 * u
        c.paint(capsule(x, fig.foot - 0.1 * u, x, top, 0.14 * u), 'wood')
        c.paint(poly([(x - 0.2 * u, top), (x + 0.2 * u, top), (x, top - 1.2 * u)]), 'silver', spec=0.7)
        c.paint(poly([(x, top + 0.3 * u), (x + fig.f * 1.2 * u, top - 0.1 * u), (x + fig.f * 1.3 * u, top + 1.1 * u), (x, top + 0.9 * u)], nrm(-0.3, -0.2, 0.9)), 'silver', spec=0.7)
        c.paint(poly([(x, top + 0.4 * u), (x - fig.f * 0.6 * u, top + 0.6 * u), (x, top + 0.9 * u)]), 'silver', gain=0.8)
        c.paint(rect(x - 0.4 * u, top + 1.2 * u, x + 0.4 * u, top + 1.4 * u), 'red', outline=False)
    return draw


def flowers_held():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        for k, col in enumerate(('red', 'gold', 'paper', 'blue')):
            c.paint(capsule(x, y, x + (k - 1.5) * 0.3 * u, y - 1.4 * u, 0.06 * u), 'green', outline=False)
            c.paint(ellipse(x + (k - 1.5) * 0.35 * u, y - 1.5 * u - (k % 2) * 0.3 * u, 0.32 * u, 0.3 * u), col, gain=1.1)
    return draw


def lead_rope():
    def draw(c, fig, hand):
        c.paint(capsule(hand[0], hand[1], hand[0] + fig.f * 3.0 * fig.u, hand[1] - 0.6 * fig.u, 0.6), 'leather', gain=1.0, outline=False)
    return draw


def hoof():
    """持ち上げた蹄に打つ蹄鉄。"""
    def draw(c, fig, hand):
        u = fig.u
        c.paint(capsule(hand[0], hand[1], hand[0] + fig.f * 0.8 * u, hand[1] + 0.3 * u, 0.3 * u), 'silver', gain=1.1, spec=0.6)
    return draw


def plume(c, x, y):
    """兜の羽根飾り。"""
    for k in range(5):
        c.paint(capsule(x, y + 6, x - 6 - k * 3, y - 6 - k * 2, 1.6), 'red', gain=1.0 + 0.05 * k, outline=False)


def snow_roof(c, x, base, w, h, roof_h):
    """家（house と同じ寸法）の破風と屋根に積もった雪。"""
    apex = (x + w / 2, base - h - roof_h)
    d = w * 0.55
    sk = d * 0.45
    c.paint(capsule(apex[0], apex[1] - 1, x - 2, base - h + 1, 2.2), 'silver', gain=1.2)
    c.paint(capsule(apex[0], apex[1] - 1, x + w + 2, base - h + 1, 2.2), 'silver', gain=1.05)
    c.paint(poly([apex, (apex[0] + d, apex[1] - sk), (apex[0] + d + 3, apex[1] - sk + 4), (apex[0] + 3, apex[1] + 4)], UP), 'silver', gain=1.1)


def candle_rack(c, x0, x1, y):
    """芯で吊るした蝋燭の束の列。"""
    c.paint(capsule(x0, y, x1, y, 1.6), 'wood', gain=1.0)
    for k in range(int((x1 - x0) / 10)):
        x = x0 + 5 + k * 10
        ln = 22 + (k % 3) * 6
        c.paint(rect(x, y, x + 1, y + 4), 'paper', gain=0.6, outline=False)
        for dx in (-2, 2):
            c.paint(capsule(x + dx, y + 4, x + dx, y + ln, 1.4, 1.0), 'paper', gain=1.2)


def candle_row(c, x0, x1, base):
    for k in range(int((x1 - x0) / 14)):
        x = x0 + 7 + k * 14
        h = 10 + (k % 3) * 4
        c.paint(vcyl(x, base - h, base, 3, 1.2), ('paper', 'red', 'paper', 'blue')[k % 4], gain=1.2, add=0.1)
        flame(c, x, base - h - 4, 1.8, 3.5)


def painted_banner(c, x, y):
    """見世物の絵看板: 二つ首の怪物の絵。"""
    o = c.paint(rect(x - 30, y - 22, x + 30, y + 22, nrm(-0.2, 0, 1)), 'paper', gain=1.0)
    c.paint(rect(x - 30, y - 22, x + 30, y - 18), 'red', oid=o, gain=1.0, outline=False)
    c.paint(ellipse(x, y + 8, 16, 10), 'green', oid=o, gain=1.0, outline=False)
    for dx in (-10, 10):
        c.paint(capsule(x + dx * 0.5, y + 2, x + dx, y - 10, 3), 'green', oid=o, gain=1.05, outline=False)
        c.paint(ellipse(x + dx, y - 12, 4, 3.5), 'green', oid=o, gain=1.1, outline=False)
        c.dot(int(x + dx + 1), int(y - 13), 'R3')


def scissors(c, x, y):
    for sg in (-1, 1):
        c.paint(capsule(x - 20, y + sg * 4, x + 16, y - sg * 2, 1.4), 'silver', spec=0.7)
        pts = arc_points(x - 24, y + sg * 6, 5, 0, math.pi * 2, 12)
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 1.0), 'gold', gain=1.0)


def pedestal(c, x, base, w=34, h=30):
    c.paint(rect(x - w / 2, base - h, x + w / 2, base, lambda px, py: nrm((px - x) / w * 1.2, 0, 0.8)), 'stone', gain=1.05)
    c.paint(rect(x - w / 2 - 4, base - h - 4, x + w / 2 + 4, base - h, UP), 'stone', gain=1.15)
    c.paint(rect(x - w / 2 - 4, base - 4, x + w / 2 + 4, base, UP), 'stone', gain=0.95)


def shield_stand(c, x, base):
    c.paint(capsule(x, base, x, base - 40, 1.4), 'wood', gain=0.9)
    w, h = 18, 26
    y = base - 50
    pts = [(x - w, y - h * 0.4), (x + w, y - h * 0.4), (x + w, y + 4), (x, y + h * 0.7), (x - w, y + 4)]
    c.paint(poly(pts, lambda px, py: nrm((px - x) / w * 0.5, 0, 0.85)), 'gold', spec=0.5)
    c.paint(poly([(x - w + 3, y - h * 0.4 + 3), (x, y - h * 0.4 + 3), (x, y + h * 0.7 - 4), (x - w + 3, y + 3)]), 'red', gain=1.0)
    c.paint(poly([(x, y - h * 0.4 + 3), (x + w - 3, y - h * 0.4 + 3), (x + w - 3, y + 3), (x, y + h * 0.7 - 4)]), 'blue', gain=0.9)


def wheat_field(c, y0):
    """実った麦の畑（穂の列が奥へ細る）。"""
    for row in range(8):
        y = y0 + row * (3 + row * 1.2)
        step = 4 + row
        for k in range(int(W / step) + 1):
            x = k * step + (row % 2) * step / 2
            h = 4 + row * 2
            c.paint(capsule(x, y, x + 0.5, y - h, 0.4 + row * 0.1), 'gold', gain=0.8 + row * 0.04, outline=False)
            c.paint(ellipse(x + 0.5, y - h, 0.8 + row * 0.2, 1.5 + row * 0.35), 'gold', gain=1.0 + row * 0.03, outline=False)


def scythe_lean(c, x, base):
    c.paint(capsule(x, base, x + 10, base - 90, 1.6), 'wood', gain=1.0)
    pts = [(x + 10 - t * 50, base - 90 + t * t * 20) for t in [i / 8 for i in range(9)]]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        c.paint(capsule(a[0], a[1], b[0], b[1], 3.0 * (1 - i / 9) + 0.5), 'silver', spec=0.7)
