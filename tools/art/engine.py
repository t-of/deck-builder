"""絵の土台: 光の当て方、形の塗り方、仕上げ（段への丸め・ディザ・輪郭・パレット PNG）。

画素ごとに「どのランプか」と「明るさ L（0〜1）」を持ち、最後に L をランプの段に丸める。
明るさは場面に 1 つだけの光（Light）から決まる。形の向き（法線）と、光だまりの中心からの距離で段が変わる。
"""
import math
import random

from PIL import Image

from palette import INDEX, NAMES, RAMPS, RGB

W, H = 224, 160
DITHER_BAND = 0.1  # 段の境目から ±この幅だけ市松にする（それ以外はベタ）


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def nrm(x, y, z):
    l = math.sqrt(x * x + y * y + z * z) or 1.0
    return (x / l, y / l, z / l)


def hsh(*a):
    """座標などから決まる 0〜1 の値（乱数の代わり。何度動かしても同じ）。"""
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
        h ^= h >> 13
        h = (h * 0x5bd1e995) & 0xffffffff
        h ^= h >> 15
    return h / 0xffffffff


class Light:
    """左上の光 1 つ。dir は面から光への向き（画面の y は下向き、z は手前）。
    pool: 光だまりの中心と半径。halo: 見えている灯り（燭台・窓など）のまわりの明るみ。"""

    def __init__(self, pool=(96, 64), radius=(120, 90), amb=0.06, flat=0.4, key=0.72,
                 bounce=0.16, dir=(-0.55, -0.62, 0.56), halo=None, fall=1.25):
        self.cx, self.cy = pool
        self.rx, self.ry = radius[0] * 1.1, radius[1] * 1.1
        self.amb, self.flat, self.key, self.bounce, self.fall = amb, flat, key, bounce, fall
        self.dir = nrm(*dir)
        self.bdir = nrm(0.7, 0.45, 0.3)  # 影の側の反射光（右下の卓から返る光）
        self.halo = halo  # (x, y, 半径, 強さ)
        self.half = nrm(self.dir[0], self.dir[1], self.dir[2] + 1)  # 金属の照り（視線は手前から）

    def att(self, x, y):
        d2 = ((x - self.cx) / self.rx) ** 2 + ((y - self.cy) / self.ry) ** 2
        return math.exp(-d2 * 1.9 * self.fall)

    def glow(self, x, y):
        if not self.halo:
            return 0.0
        hx, hy, r, s = self.halo
        d = math.hypot(x - hx, y - hy) / r
        return s * clamp(1 - d) ** 2

    def lum(self, x, y, n, spec=0.0, shine=10, cel=0):
        a = self.att(x, y)
        d = self.dir
        lam = n[0] * d[0] + n[1] * d[1] + n[2] * d[2]
        if cel:
            lam = round(lam * cel) / cel  # 人物は面を 3 段に割る（ぬるい丸みを出さない）
        L = self.amb + a * (self.flat + self.key * max(0.0, lam))
        if spec:
            h = self.half
            L += spec * (0.25 + 0.75 * a) * max(0.0, n[0] * h[0] + n[1] * h[1] + n[2] * h[2]) ** shine
        if lam < 0.3:
            b = self.bdir
            L += self.bounce * max(0.0, n[0] * b[0] + n[1] * b[1] + n[2] * b[2]) * (0.35 + 0.65 * a)
        return L + self.glow(x, y) * 0.6


FLAT = (0.0, 0.0, 1.0)


class Canvas:
    def __init__(self, light, seed):
        self.light = light
        self.rng = random.Random(seed)
        n = W * H
        self.ramp = ['stone'] * n
        self.L = [0.0] * n
        self.oid = [0] * n
        self.dith = [True] * n
        self.line = [False] * n
        self.fixed = [None] * n
        self._oid = 0
        self.cel = 0

    # ---- 塗る ----
    def obj(self):
        self._oid += 1
        return self._oid

    def paint(self, pix, ramp, oid=None, gain=1.0, add=0.0, dither=False, outline=True,
              tex=None, depth=0.0, emit=None, lit=None, spec=0.0, shine=10):
        """pix: (x, y, 法線) の並び。emit を渡すと光を無視してその明るさ（関数か値）で塗る。
        depth: 0 が手前、1 に近いほど奥（暗く沈む）。"""
        if oid is None:
            oid = self.obj()
        light = lit or self.light
        for x, y, n in pix:
            if not (0 <= x < W and 0 <= y < H):
                continue
            i = y * W + x
            if emit is not None:
                L = emit(x, y, n) if callable(emit) else emit
            else:
                L = light.lum(x + 0.5, y + 0.5, n, spec, shine, self.cel) * gain + add
            if tex:
                L += tex(x, y)
            if depth:
                L = L * (1 - 0.55 * depth)
            self.ramp[i] = ramp
            self.L[i] = L
            self.oid[i] = oid
            self.dith[i] = dither
            self.line[i] = outline
            self.fixed[i] = None
        return oid

    def dot(self, x, y, color, oid=None):
        """決まった 1 色の点（宝石の照り・星など）。"""
        if 0 <= x < W and 0 <= y < H:
            i = y * W + x
            self.fixed[i] = INDEX[color]
            if oid is not None:
                self.oid[i] = oid

    def get_oid(self, x, y):
        return self.oid[y * W + x] if 0 <= x < W and 0 <= y < H else -1

    # ---- 仕上げ ----
    def indices(self):
        out = [0] * (W * H)
        step = [0] * (W * H)
        for y in range(H):
            for x in range(W):
                i = y * W + x
                r = RAMPS[self.ramp[i]]
                f = clamp(self.L[i]) * (len(r) - 1)
                k = int(f)
                fr = f - k
                if self.dith[i] and abs(fr - 0.5) < DITHER_BAND:
                    k += (x + y) & 1
                else:
                    k = int(f + 0.5)
                step[i] = min(k, len(r) - 1)
        # 輪郭: 手前の物の縁（奥の物と接する画素）を、その物の色の暗い段で描く。真っ黒にはしない。
        for y in range(H):
            for x in range(W):
                i = y * W + x
                if not self.line[i]:
                    continue
                o = self.oid[i]
                edge = False
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = self.get_oid(x + dx, y + dy)
                    if 0 <= q < o:
                        edge = True
                        break
                if edge:
                    k = step[i]
                    n = len(RAMPS[self.ramp[i]])
                    # 光の側の縁は 1 段だけ落とし、影の側は闇の 1 つ上の段にする（選択輪郭）
                    step[i] = k - 1 if k >= n * 0.62 else min(k, 1)
        for i in range(W * H):
            if self.fixed[i] is not None:
                out[i] = self.fixed[i]
            else:
                out[i] = INDEX[RAMPS[self.ramp[i]][max(0, step[i])]]
        return out

    def image(self):
        im = Image.new('P', (W, H))
        flat = []
        for c in RGB:
            flat.extend(c)
        im.putpalette(flat)
        im.putdata(self.indices())
        return im.resize((W * 2, H * 2), Image.NEAREST)

    def save(self, path):
        self.image().save(path, optimize=True)


# ---- 形（画素と法線の並びを返す） ----

def _bbox(x0, y0, x1, y1):
    return (max(0, int(math.floor(x0))), max(0, int(math.floor(y0))),
            min(W - 1, int(math.ceil(x1))), min(H - 1, int(math.ceil(y1))))


def ellipse(cx, cy, rx, ry, bulge=1.0, normal=None, clip=None):
    """楕円。normal を渡さなければ球の向きで陰がつく。clip(x, y) が False の画素は除く。"""
    bx0, by0, bx1, by1 = _bbox(cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1)
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            u = (x + 0.5 - cx) / rx
            v = (y + 0.5 - cy) / ry
            d = u * u + v * v
            if d > 1 or (clip and not clip(x, y)):
                continue
            if normal:
                n = normal(x, y, u, v) if callable(normal) else normal
            else:
                n = nrm(u * bulge, v * bulge, math.sqrt(max(0.0, 1 - d)))
            yield x, y, n


def _pip(px, py, pts):
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def poly(pts, normal=FLAT, clip=None):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    bx0, by0, bx1, by1 = _bbox(min(xs), min(ys), max(xs), max(ys))
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            if _pip(x + 0.5, y + 0.5, pts) and not (clip and not clip(x, y)):
                yield x, y, (normal(x, y) if callable(normal) else normal)


def rect(x0, y0, x1, y1, normal=FLAT):
    for y in range(max(0, int(y0)), min(H, int(y1))):
        for x in range(max(0, int(x0)), min(W, int(x1))):
            yield x, y, (normal(x, y) if callable(normal) else normal)


def capsule(x0, y0, x1, y1, r0, r1=None, flat=0.0):
    """太さの変わる棒（腕・脚・柄）。断面が丸いので、軸から離れるほど横を向く。"""
    if r1 is None:
        r1 = r0
    R = max(r0, r1)
    bx0, by0, bx1, by1 = _bbox(min(x0, x1) - R - 1, min(y0, y1) - R - 1, max(x0, x1) + R + 1, max(y0, y1) + R + 1)
    dx, dy = x1 - x0, y1 - y0
    ll = dx * dx + dy * dy or 1e-9
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            px, py = x + 0.5, y + 0.5
            t = clamp(((px - x0) * dx + (py - y0) * dy) / ll)
            qx, qy = x0 + dx * t, y0 + dy * t
            r = r0 + (r1 - r0) * t
            ox, oy = px - qx, py - qy
            d = math.hypot(ox, oy)
            if d > r:
                continue
            s = d / r if r else 0
            z = math.sqrt(max(0.0, 1 - s * s)) + flat
            yield x, y, nrm(ox / (r or 1) * (1 - flat), oy / (r or 1) * (1 - flat), z)


def vcyl(cx, y0, y1, rx, ry=None, top=True):
    """立てた円柱（樽・蝋燭・塔・硬貨の山）。上面は楕円で上を向く。"""
    if ry is None:
        ry = rx * 0.35
    body = []
    for x, y, n in ellipse(cx, y1, rx, ry):
        if y >= y1:
            body.append((x, y, nrm((x + 0.5 - cx) / rx, 0.15, math.sqrt(max(0, 1 - ((x + 0.5 - cx) / rx) ** 2)))))
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            u = (x + 0.5 - cx) / rx
            if abs(u) <= 1:
                body.append((x, y, nrm(u, 0.0, math.sqrt(max(0.0, 1 - u * u)))))
    if top:
        for x, y, n in ellipse(cx, y0, rx, ry):
            body.append((x, y, nrm((x + 0.5 - cx) / rx * 0.3, -0.75, 0.6)))
    return body


def arc_points(cx, cy, r, a0, a1, steps=24):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / steps), cy + r * math.sin(a0 + (a1 - a0) * i / steps))
            for i in range(steps + 1)]


def check_palette(path):
    """出力 PNG の全画素がパレットの色か確かめる。"""
    im = Image.open(path).convert('RGB')
    allowed = set(RGB)
    bad = {c for c in im.getdata() if c not in allowed}
    if bad:
        raise SystemExit(f'{path}: パレット外の色 {sorted(bad)[:5]}')
    return True
