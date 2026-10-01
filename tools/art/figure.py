"""人物: 関節の位置（姿勢）を決め、脚・胴・腕・頭を立体として塗る。服・かぶり物・持ち物は差し替え。

単位 u は頭 1 つ分の高さ。立ち姿は 7 頭身（h = 7u）。
腕の姿勢は「右腕（画面の右）」として肩からの (肘 dx, dy, 手 dx, dy) を u で書き、左腕は左右を返して使う。
facing=-1 で全体を左右反転する（光は左上のまま）。
"""
import math

from engine import arc_points, capsule, clamp, ellipse, nrm, poly, rect
from parts import gem

ARMS = {
    'down':     (0.25, 1.35, 0.32, 2.6),
    'hip':      (0.95, 0.95, 0.35, 1.7),
    'raise':    (0.45, -0.95, 0.35, -2.3),
    'lift':     (0.95, 0.15, 1.15, -1.05),   # 手を頭の高さに（灯り・鈴を掲げる）
    'forward':  (1.25, 0.45, 2.45, 0.25),    # 前へ突き出す・指す
    'aim':      (1.3, 0.05, 2.55, -0.1),     # 肩の高さでまっすぐ（弓・剣を構える）
    'present':  (0.4, 1.3, 1.35, 1.15),      # 前腕を前へ（盆・袋を差し出す）
    'chest':    (0.35, 1.3, -0.45, 1.55),    # 胸の前へ（本・巻物を抱える）
    'belly':    (0.3, 1.35, -0.35, 2.05),
    'pull':     (-0.15, 0.85, -0.95, 0.25),  # 弓の弦を引く
    'overhead': (0.55, -0.9, -0.15, -2.0),   # 両手で頭上に（斧）
    'eye':      (0.7, 0.75, -0.55, -0.15),   # 遠眼鏡を目に当てる
    'reach':    (1.0, 1.0, 2.0, 2.0),        # 前下へ手を伸ばす（すり）
    'low':      (0.6, 1.25, 1.1, 2.3),       # 体の横で道具を下げ持つ
}


def _mirror(a):
    return (-a[0], a[1], -a[2], a[3])


class Fig:
    def __init__(self, x, foot, h=92, facing=1, arms=('down', 'down'), legs='stand', lean=0.0):
        self.x, self.foot, self.h, self.f = x, foot, h, facing
        self.u = u = h / 7.0
        drop = {'stand': 0, 'stride': 0.1, 'kneel': 1.75, 'crouch': 1.4}[legs]
        self.legs = legs
        self.lean = lean
        top = foot - h + drop * u
        self.y_head = top + 0.5 * u
        self.y_neck = top + 1.05 * u
        self.y_sh = top + 1.5 * u
        self.y_waist = top + 3.0 * u
        self.y_hip = top + 3.6 * u
        self.arms = (_mirror(ARMS[arms[0]]) if isinstance(arms[0], str) else arms[0],
                     ARMS[arms[1]] if isinstance(arms[1], str) else arms[1])

    # 画面座標: 体の中心からの横 dx（u 単位、facing で反転）と y。前かがみは上ほど前へずらす
    def X(self, dx, y):
        return self.x + self.f * (dx * self.u + self.lean * (self.y_hip - y))

    def joints(self, side):
        """side 0=画面の左腕, 1=右腕（facing=-1 なら入れ替わる）"""
        u = self.u
        sdx = -0.95 if side == 0 else 0.95
        e = self.arms[side]
        sy = self.y_sh + 0.15 * u
        sh = (self.X(sdx, sy), sy)
        el = (self.X(sdx + e[0], sy + e[1] * u), sy + e[1] * u)
        ha = (self.X(sdx + e[2], sy + e[3] * u), sy + e[3] * u)
        return sh, el, ha

    def hand(self, side):
        return self.joints(side)[2]


def _arm(c, fig, side, sleeve, skin='skin', glove=None, gain=1.0):
    u = fig.u
    sh, el, ha = fig.joints(side)
    o = c.obj()
    c.paint(capsule(sh[0], sh[1], el[0], el[1], 0.34 * u, 0.28 * u), sleeve, oid=o, gain=gain)
    o2 = c.obj()
    c.paint(capsule(el[0], el[1], ha[0], ha[1], 0.28 * u, 0.22 * u), sleeve, oid=o2, gain=gain)
    # 袖口（少し広がって暗い）
    t = 0.8
    cx, cy = el[0] + (ha[0] - el[0]) * t, el[1] + (ha[1] - el[1]) * t
    c.paint(capsule(cx, cy, cx + (ha[0] - el[0]) * 0.1, cy + (ha[1] - el[1]) * 0.1, 0.27 * u), sleeve, oid=o2, gain=gain * 0.8)
    c.paint(ellipse(ha[0], ha[1], 0.25 * u, 0.27 * u), glove or skin, gain=1.1)


def _legs(c, fig, cloth, boots):
    u, f = fig.u, fig.f
    y0 = fig.y_hip
    foot = fig.foot
    if fig.legs in ('stand', 'stride'):
        spread = 0.42 if fig.legs == 'stand' else 0.75
        for s in (-1, 1):
            hx = fig.X(s * 0.38, y0)
            kx = fig.X(s * (0.4 + spread * 0.3), y0 + 1.9 * u)
            fx = fig.X(s * spread, foot) if fig.legs == 'stand' else fig.x + f * s * spread * u
            c.paint(capsule(hx, y0, kx, y0 + 1.9 * u, 0.48 * u, 0.38 * u), cloth)
            c.paint(capsule(kx, y0 + 1.9 * u, fx, foot - 0.6 * u, 0.38 * u, 0.3 * u), cloth)
            c.paint(capsule(fx, foot - 1.1 * u, fx, foot - 0.25 * u, 0.36 * u), boots)
            c.paint(ellipse(fx + f * 0.25 * u, foot - 0.18 * u, 0.55 * u, 0.25 * u), boots)
    else:
        # 片膝をつく（kneel）／しゃがむ（crouch）: 前の脚は膝を立て、後ろの脚は膝を地面に
        front = 1
        hx = fig.X(0.2, y0)
        kx = fig.X(front * 1.6, y0)
        ky = y0 - 0.2 * u
        c.paint(capsule(fig.X(-0.4, y0), y0, fig.X(-0.9, foot - 0.3 * u), foot - 0.3 * u, 0.48 * u, 0.4 * u), cloth)
        c.paint(capsule(fig.X(-0.9, foot - 0.3 * u), foot - 0.3 * u, fig.X(-2.3, foot - 0.25 * u), foot - 0.25 * u, 0.36 * u, 0.3 * u), boots)
        c.paint(capsule(hx, y0, kx, ky, 0.5 * u, 0.42 * u), cloth)
        c.paint(capsule(kx, ky, kx + f * 0.2 * u, foot - 0.5 * u, 0.4 * u, 0.32 * u), cloth)
        c.paint(capsule(kx + f * 0.2 * u, foot - 1.0 * u, kx + f * 0.2 * u, foot - 0.25 * u, 0.36 * u), boots)
        c.paint(ellipse(kx + f * 0.55 * u, foot - 0.2 * u, 0.6 * u, 0.25 * u), boots)


def _body_poly(fig, keys):
    """keys: [(y, 半幅 u)]。前かがみに合わせた左右の輪郭を返す。"""
    left = [(fig.X(-w, y), y) for y, w in keys]
    right = [(fig.X(w, y), y) for y, w in reversed(keys)]
    return left + right


def _body_normal(fig, keys, folds=0.0, fold_from=None, phase=0.0):
    u = fig.u

    def hw(y):
        for (y0, w0), (y1, w1) in zip(keys, keys[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / ((y1 - y0) or 1)
                return (w0 + (w1 - w0) * t) * u
        return keys[-1][1] * u

    def n(x, y):
        cx = fig.X(0, y)
        w = hw(y) or 1
        k = clamp((x + 0.5 - cx) / w, -1, 1)
        nx = k * 0.85
        if folds and fold_from is not None and y > fold_from:
            t = clamp((y - fold_from) / (2.5 * u))
            nx += folds * t * math.sin((x - cx) / u * 2.4 + phase + y * 0.05)
        return nrm(nx, -0.05, math.sqrt(max(0.05, 1 - k * k)))
    return n


def figure(c, x, foot, h=92, facing=1, arms=('down', 'down'), legs='stand', lean=0.0,
           tunic='red', robe=False, cloak=None, legs_ramp='cloth', boots='leather', skin='skin',
           head='hood', head_ramp=None, belt='leather', trim=None, armor=False, apron=None,
           mantle=None, props=(), behind=(), hair='hair', mask=None, young=False, gown=False, beard=None):
    """props: [(腕 0/1, 持ち物の関数, 前に描くか)]。持ち物の関数は (c, fig, 手の位置) を受ける。
    behind: 体より奥に描く持ち物（槍の柄など）。"""
    fig = Fig(x, foot, h, facing, arms, legs, lean)
    u = fig.u
    c.cel = 3
    hem = foot - 0.2 * u if robe else fig.y_hip + 1.25 * u
    if young:
        pass
    sh_w = 1.0
    # ---- 外套（背中側） ----
    if cloak:
        ck = [(fig.y_neck, 0.7), (fig.y_sh + 0.2 * u, 1.35), (fig.y_waist, 1.45), (foot - 0.9 * u, 1.95)]
        if legs in ('kneel', 'crouch'):
            ck[-1] = (foot - 0.3 * u, 2.3)
        c.paint(poly(_body_poly(fig, ck), _body_normal(fig, ck, 0.5, fig.y_sh, 1.0)), cloak, gain=0.8)
    for side, fn in behind:
        fn(c, fig, fig.hand(side))
    # ---- 脚 ----
    if not robe:
        _legs(c, fig, legs_ramp, boots)
    # ---- 胴 ----
    keys = [(fig.y_neck + 0.1 * u, 0.55), (fig.y_sh, sh_w), (fig.y_sh + 0.8 * u, 0.95), (fig.y_waist, 0.72),
            (fig.y_hip, 0.85), (hem, 1.25 if not robe else 1.5)]
    if gown:  # 細い胴と、裾へ大きく広がるドレス
        keys = [(fig.y_neck + 0.1 * u, 0.5), (fig.y_sh, 0.9), (fig.y_sh + 0.8 * u, 0.8), (fig.y_waist, 0.55),
                (fig.y_hip, 1.1), (hem, 2.3)]
    if robe and legs in ('kneel', 'crouch'):
        keys[-1] = (foot - 0.1 * u, 2.0)
    body = c.paint(poly(_body_poly(fig, keys), _body_normal(fig, keys, 0.45, fig.y_waist, 0.5)), tunic)
    if armor:
        ak = [(fig.y_sh - 0.05 * u, 0.9), (fig.y_sh + 0.9 * u, 0.88), (fig.y_waist + 0.2 * u, 0.7)]
        ao = c.paint(poly(_body_poly(fig, ak), _body_normal(fig, ak)), 'silver', spec=0.4, shine=6, gain=0.6)
        rx_ = fig.X(0.1, fig.y_sh)
        c.paint(rect(rx_, fig.y_sh + 0.2 * u, rx_ + 1, fig.y_waist), 'silver', oid=ao, gain=0.95, outline=False)
        wy = fig.y_waist + 0.05 * u
        c.paint(poly(_body_poly(fig, [(wy, 0.72), (wy + 0.3 * u, 0.78)])), 'silver', oid=ao, gain=0.55, outline=False)
    if apron:
        ap = [(fig.y_sh + 0.9 * u, 0.6), (fig.y_waist, 0.66), (hem - 0.2 * u, 0.95)]
        c.paint(poly(_body_poly(fig, ap), _body_normal(fig, ap, 0.3, fig.y_waist)), apron, oid=body)
    if mantle:
        mk = [(fig.y_neck, 0.6), (fig.y_sh, 1.15), (fig.y_sh + 1.0 * u, 1.05)]
        c.paint(poly(_body_poly(fig, mk), _body_normal(fig, mk)), mantle)
    if belt:
        by = fig.y_waist + 0.1 * u
        bk = [(by, 0.74), (by + 0.32 * u, 0.76)]
        c.paint(poly(_body_poly(fig, bk), _body_normal(fig, bk)), belt, oid=body, gain=0.9)
        c.paint(rect(fig.X(0.05, by) - 1, by, fig.X(0.05, by) + 2, by + 0.32 * u + 1), 'gold', oid=body, gain=1.1)
    if trim:
        tk = [(hem - 0.3 * u, 1.22 if not robe else 1.45), (hem, 1.25 if not robe else 1.5)]
        if not (robe and legs in ('kneel', 'crouch')):
            c.paint(poly(_body_poly(fig, tk), _body_normal(fig, tk)), trim, oid=body)
    # ---- 頭 ----
    hx, hy = fig.X(0.05, fig.y_head), fig.y_head
    c.paint(capsule(fig.X(0, fig.y_neck - 0.2 * u), fig.y_neck - 0.2 * u, fig.X(0, fig.y_neck + 0.2 * u), fig.y_neck + 0.2 * u, 0.28 * u), skin, gain=0.75)
    _head(c, fig, hx, hy, head, head_ramp or tunic, skin, hair, mask, beard)
    # ---- 腕と持ち物 ----
    for side in (0, 1):
        sh = fig.joints(side)[0]
        c.paint(ellipse(sh[0], sh[1] + 0.05 * u, 0.42 * u, 0.4 * u), 'silver' if armor else (mantle or tunic), gain=0.85 if armor else 1.0,
                spec=0.4 if armor else 0)
    for side in (0, 1):
        for ps, fn, front in props:
            if ps == side and not front:
                fn(c, fig, fig.hand(side))
        _arm(c, fig, side, tunic if not armor else tunic, skin)
        for ps, fn, front in props:
            if ps == side and front:
                fn(c, fig, fig.hand(side))
    c.cel = 0
    return fig


def _head(c, fig, hx, hy, kind, ramp, skin, hair, mask, beard=None):
    u, f = fig.u, fig.f
    rx, ry = 0.4 * u, 0.5 * u
    if kind == 'hood':
        c.paint(ellipse(hx - f * 0.08 * u, hy - 0.05 * u, rx * 1.45, ry * 1.25), ramp, gain=0.95)
        o = c.obj()
        c.paint(ellipse(hx + f * 0.1 * u, hy + 0.12 * u, rx * 0.82, ry * 0.85), skin, oid=o, gain=0.8)
        # フードの縁の影（顔の上部）
        c.paint(ellipse(hx + f * 0.1 * u, hy - 0.42 * u, rx * 0.8, ry * 0.2), ramp, oid=o, gain=0.6, outline=False)
        if mask:
            c.paint(rect(hx - rx * 0.9, hy + 0.15 * u, hx + rx * 1.0, hy + 0.55 * u), mask, oid=o, gain=0.9, outline=False)
        else:
            c.dot(int(hx + f * 0.28 * u), int(hy), 'G0')
        return
    if kind in ('long', 'tiara'):
        # 肩まで流れる長い髪（頭の後ろ）
        c.paint(poly([(hx - rx * 1.15, hy - 0.2 * u), (hx + rx * 1.15, hy - 0.2 * u), (hx + rx * 1.3, hy + 1.3 * u), (hx - rx * 1.3, hy + 1.3 * u)],
                     lambda px, py: nrm((px - hx) / rx * 0.5, 0, 0.85)), hair)
    c.paint(ellipse(hx, hy, rx, ry), skin)
    eye = (int(hx + f * 0.25 * u), int(hy - 0.02 * u))
    if kind in ('long', 'tiara'):
        c.paint(ellipse(hx - f * 0.05 * u, hy - 0.25 * u, rx * 1.12, ry * 0.7, clip=lambda x, y: y < hy - 0.2 * u), hair)
        c.dot(*eye, 'G0')
        if kind == 'tiara':
            ty = hy - 0.5 * u
            c.paint(poly([(hx - rx * 0.8, ty + 2), (hx + rx * 0.8, ty + 2), (hx + rx * 0.4, ty - 1), (hx, ty - 0.35 * u), (hx - rx * 0.4, ty - 1)]), 'gold', spec=0.7)
            c.dot(int(hx), int(ty - 1), 'R3')
    if kind in ('hair', 'cap', 'feather', 'hat', 'helm', 'crown', 'coif', 'mitre', 'tophat', 'turban'):
        if kind not in ('helm', 'turban'):
            c.paint(ellipse(hx - f * 0.12 * u, hy - 0.22 * u, rx * 1.08, ry * 0.75,
                            clip=lambda x, y: y < hy - 0.24 * u or ((x - hx) * f < -0.14 * u and y < hy + 0.3 * u)), hair)
        c.dot(*eye, 'G0')
    if mask:
        c.paint(rect(hx - rx, hy + 0.12 * u, hx + rx + 1, hy + 0.55 * u), mask, outline=False)
    if kind in ('cap', 'feather'):
        c.paint(ellipse(hx - f * 0.1 * u, hy - 0.42 * u, rx * 1.15, ry * 0.5,
                        clip=lambda x, y: y < hy - 0.25 * u), ramp)
        if kind == 'feather':
            c.paint(capsule(hx - f * 0.3 * u, hy - 0.6 * u, hx - f * 1.1 * u, hy - 1.3 * u, 0.12 * u, 0.04 * u), 'red', gain=1.1)
    elif kind == 'hat':
        c.paint(ellipse(hx, hy - 0.42 * u, rx * 2.0, ry * 0.28), ramp)
        c.paint(ellipse(hx, hy - 0.68 * u, rx * 1.0, ry * 0.6, clip=lambda x, y: y < hy - 0.48 * u), ramp)
        c.paint(rect(hx - rx, hy - 0.6 * u, hx + rx, hy - 0.5 * u), 'gold', outline=False)
    elif kind == 'helm':
        c.paint(ellipse(hx, hy - 0.15 * u, rx * 1.12, ry * 0.95, clip=lambda x, y: y < hy + 0.0 * u), 'silver', spec=0.6, shine=6)
        c.paint(rect(hx + f * 0.18 * u - 1, hy - 0.2 * u, hx + f * 0.18 * u + 1, hy + 0.35 * u), 'silver', outline=False)
        c.paint(rect(hx - rx * 1.12, hy - 0.05 * u, hx + rx * 1.12, hy + 0.08 * u), 'silver', gain=0.8, outline=False)
        c.dot(*eye, 'N0')
    elif kind == 'crown':
        cy = hy - 0.55 * u
        c.paint(rect(hx - rx, cy, hx + rx, cy + 0.25 * u), 'gold', spec=0.5)
        for k in (-1, 0, 1):
            px = hx + k * rx * 0.75
            c.paint(poly([(px - 1.5, cy), (px + 1.5, cy), (px, cy - 0.35 * u)]), 'gold', spec=0.5)
    elif kind == 'mitre':
        pts = [(hx - rx * 0.95, hy - 0.4 * u), (hx + rx * 0.95, hy - 0.4 * u), (hx + rx * 0.7, hy - 1.2 * u), (hx, hy - 1.6 * u), (hx - rx * 0.7, hy - 1.2 * u)]
        o = c.paint(poly(pts, lambda x, y: nrm((x - hx) / rx * 0.6, -0.2, 0.8)), ramp)
        c.paint(rect(hx - rx * 0.95, hy - 0.55 * u, hx + rx * 0.95, hy - 0.4 * u), 'gold', oid=o, outline=False)
        c.paint(rect(hx - 1, hy - 1.5 * u, hx + 1, hy - 0.55 * u), 'gold', oid=o, outline=False)
    elif kind == 'tophat':
        c.paint(ellipse(hx, hy - 0.45 * u, rx * 1.7, ry * 0.25), ramp)
        c.paint(rect(hx - rx * 0.85, hy - 1.35 * u, hx + rx * 0.85, hy - 0.45 * u, lambda x, y: nrm((x - hx) / rx * 0.8, 0, 0.7)), ramp)
        c.paint(rect(hx - rx * 0.85, hy - 0.65 * u, hx + rx * 0.85, hy - 0.5 * u), 'red', outline=False)
    elif kind == 'turban':
        c.paint(ellipse(hx - f * 0.05 * u, hy - 0.4 * u, rx * 1.3, ry * 0.75, clip=lambda x, y: y < hy - 0.15 * u), ramp,
                tex=lambda x, y: -0.08 if int(x - y * 0.6) % 4 == 0 else 0)
        gem(c, hx + f * 0.1 * u, hy - 0.45 * u, 0.18 * u, 'red')
    if beard:
        c.paint(ellipse(hx + f * 0.05 * u, hy + 0.35 * u, rx * 0.85, ry * 0.65, clip=lambda x, y: y > hy + 0.12 * u), beard)
    if kind == 'coif':
        c.paint(ellipse(hx - f * 0.05 * u, hy - 0.1 * u, rx * 1.2, ry * 1.1,
                        clip=lambda x, y: not ((x - hx - f * 0.08 * u) ** 2 / (rx * 0.75) ** 2 + (y - hy - 0.12 * u) ** 2 / (ry * 0.72) ** 2 < 1)), ramp)


# ================= 持ち物 =================
# どれも (c, fig, 手) を受け取る関数を返す。角度は度、0 が右、-90 が真上（facing で左右反転）

def _dir(fig, deg):
    a = math.radians(deg)
    return math.cos(a) * fig.f, math.sin(a)


def staff(deg=-90, length=5.0, ramp='wood', top=None, below=1.2):
    def draw(c, fig, hand):
        dx, dy = _dir(fig, deg)
        u = fig.u
        x0, y0 = hand[0] - dx * below * u, hand[1] - dy * below * u
        x1, y1 = hand[0] + dx * length * u, hand[1] + dy * length * u
        c.paint(capsule(x0, y0, x1, y1, 0.17 * u), ramp)
        if top == 'spear':
            c.paint(poly([(x1 - 0.3 * u, y1 + 0.2 * u), (x1 + 0.3 * u, y1 + 0.2 * u), (x1 + dx * 1.2 * u, y1 + dy * 1.2 * u)]),
                    'silver', spec=0.6, shine=5, gain=1.1)
        elif top == 'knob':
            c.paint(ellipse(x1, y1, 0.42 * u, 0.42 * u), 'gold', spec=0.7, shine=5)
        elif top == 'lantern':
            from parts import lantern
            c.paint(capsule(x1, y1, x1 + fig.f * 1.0 * u, y1, 0.13 * u), 'wood')
            lantern(c, x1 + fig.f * 1.0 * u, y1 + 1.0 * u, s=u / 13 * 0.9, hang=y1)
        elif top == 'crook':
            pts = [(x1 + fig.f * 0.6 * u * (1 - math.cos(t)), y1 - 0.6 * u * math.sin(t)) for t in [i * 0.5 for i in range(7)]]
            for a, b in zip(pts, pts[1:]):
                c.paint(capsule(a[0], a[1], b[0], b[1], 0.17 * u), ramp)
    return draw


def sword(deg=-60, length=4.4, ramp='silver'):
    def draw(c, fig, hand):
        u = fig.u
        dx, dy = _dir(fig, deg)
        px, py = -dy, dx
        o = c.obj()
        tip = (hand[0] + dx * length * u, hand[1] + dy * length * u)
        base = (hand[0] + dx * 0.5 * u, hand[1] + dy * 0.5 * u)
        w = 0.24 * u
        pts = [(base[0] + px * w, base[1] + py * w), (tip[0] - dx * 0.6 * u + px * w * 0.7, tip[1] - dy * 0.6 * u + py * w * 0.7), tip,
               (tip[0] - dx * 0.6 * u - px * w * 0.7, tip[1] - dy * 0.6 * u - py * w * 0.7), (base[0] - px * w, base[1] - py * w)]
        c.paint(poly(pts, lambda x, y: nrm(-0.5 if (x - base[0]) * px + (y - base[1]) * py > 0 else 0.4, -0.5, 0.7)),
                ramp, oid=o, spec=0.8, shine=5, gain=1.05)
        c.paint(capsule(base[0] + px * 0.7 * u, base[1] + py * 0.7 * u, base[0] - px * 0.7 * u, base[1] - py * 0.7 * u, 0.17 * u), 'gold', spec=0.5)
        c.paint(capsule(hand[0] - dx * 0.5 * u, hand[1] - dy * 0.5 * u, base[0], base[1], 0.15 * u), 'leather')
        c.paint(ellipse(hand[0] - dx * 0.6 * u, hand[1] - dy * 0.6 * u, 0.22 * u, 0.22 * u), 'gold', spec=0.5)
    return draw


def axe(deg=-100, length=3.8):
    def draw(c, fig, hand):
        u = fig.u
        dx, dy = _dir(fig, deg)
        x0, y0 = hand[0] - dx * 0.6 * u, hand[1] - dy * 0.6 * u
        x1, y1 = hand[0] + dx * length * u, hand[1] + dy * length * u
        c.paint(capsule(x0, y0, x1, y1, 0.18 * u), 'wood')
        px, py = -dy * fig.f, dx * fig.f
        hx, hy = x1 - dx * 0.5 * u, y1 - dy * 0.5 * u
        s = fig.f
        pts = [(hx, hy), (hx + dx * 0.6 * u, hy + dy * 0.6 * u), (hx + dx * 0.9 * u + s * 1.3 * u * -dy, hy + dy * 0.9 * u + s * 1.3 * u * dx),
               (hx - dx * 0.5 * u + s * 1.4 * u * -dy, hy - dy * 0.5 * u + s * 1.4 * u * dx), (hx - dx * 0.2 * u, hy - dy * 0.2 * u)]
        c.paint(poly(pts, nrm(-0.4, -0.5, 0.75)), 'silver', spec=0.7, shine=5)
    return draw


def hammer(deg=-70, length=2.6, big=False):
    def draw(c, fig, hand):
        u = fig.u
        dx, dy = _dir(fig, deg)
        x1, y1 = hand[0] + dx * length * u, hand[1] + dy * length * u
        c.paint(capsule(hand[0] - dx * 0.5 * u, hand[1] - dy * 0.5 * u, x1, y1, 0.16 * u), 'wood')
        px, py = -dy, dx
        hw = (0.9 if big else 0.6) * u
        c.paint(capsule(x1 + px * hw, y1 + py * hw, x1 - px * hw, y1 - py * hw, (0.38 if big else 0.3) * u, flat=0.4), 'silver', spec=0.6, shine=5, gain=0.95)
    return draw


def bow(height=4.2):
    def draw(c, fig, hand):
        u = fig.u
        f = fig.f
        r = height * u / 2
        pts = [(hand[0] - f * (r * 0.55) * (1 - math.cos(t)) + f * 0.2 * u, hand[1] + r * math.sin(t)) for t in
               [(-1.3 + 2.6 * i / 14) for i in range(15)]]
        for a, b in zip(pts, pts[1:]):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.17 * u), 'wood', gain=1.05)
        top, bot = pts[0], pts[-1]
        string_x = fig.hand(0 if f == 1 else 1)  # 引き手
        sx = fig.joints(0)[2]
        for (a, b) in ((top, sx), (sx, bot)):
            c.paint(capsule(a[0], a[1], b[0], b[1], 0.35), 'paper', gain=0.9, outline=False)
        c.paint(capsule(sx[0], sx[1], hand[0] + f * 0.8 * u, hand[1] - 0.05 * u, 0.12 * u), 'wood', gain=1.1)
        c.paint(poly([(hand[0] + f * 0.8 * u, hand[1] - 0.35 * u), (hand[0] + f * 0.8 * u, hand[1] + 0.25 * u), (hand[0] + f * 1.4 * u, hand[1] - 0.05 * u)]), 'silver', spec=0.6)
    return draw


def book(w=1.6, h=1.2, ramp='red', open_=False):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] - fig.f * 0.3 * u, hand[1] - 0.2 * u
        if open_:
            c.paint(poly([(x - w * u, y - h * u * 0.4), (x, y - h * u * 0.2), (x, y + h * u * 0.6), (x - w * u, y + h * u * 0.4)], nrm(-0.3, -0.5, 0.8)), 'paper', gain=1.1)
            c.paint(poly([(x, y - h * u * 0.2), (x + w * u, y - h * u * 0.4), (x + w * u, y + h * u * 0.4), (x, y + h * u * 0.6)], nrm(0.3, -0.5, 0.8)), 'paper')
            for k in range(1, 4):
                yy = y - h * u * 0.25 + k * h * u * 0.2
                c.paint(rect(x - w * u * 0.8, yy, x - 2, yy + 1), 'paper', gain=0.6, outline=False)
                c.paint(rect(x + 2, yy, x + w * u * 0.8, yy + 1), 'paper', gain=0.55, outline=False)
            return
        c.paint(rect(x - w * u / 2, y - h * u / 2, x + w * u / 2, y + h * u / 2, nrm(-0.2, -0.3, 0.9)), ramp)
        c.paint(rect(x + w * u / 2 - 1, y - h * u / 2 + 1, x + w * u / 2 + 1, y + h * u / 2 - 1), 'paper', gain=1.0, outline=False)
        c.paint(rect(x - w * u / 2 + 2, y - 1, x + w * u / 2 - 2, y + 1), 'gold', outline=False)
    return draw


def scroll(length=2.4):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(rect(x - 0.6 * u, y, x + 0.6 * u, y + length * u, nrm(-0.2, 0, 1)), 'paper', gain=1.1)
        for k in range(4):
            yy = y + (0.5 + k * 0.45) * u
            c.paint(rect(x - 0.4 * u, yy, x + 0.4 * u, yy + 1), 'paper', gain=0.55, outline=False)
        c.paint(capsule(x - 0.75 * u, y, x + 0.75 * u, y, 0.25 * u), 'paper', gain=0.95)
        c.paint(capsule(x - 0.75 * u, y + length * u, x + 0.75 * u, y + length * u, 0.25 * u), 'paper', gain=0.85)
    return draw


def bag(ramp='leather', coins=True, r=0.75):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] + 0.25 * u
        c.paint(ellipse(x, y + r * 1.25 * u, r * u * 1.05, r * u * 1.15), ramp, gain=1.05)
        c.paint(poly([(x - 0.3 * u, y + 0.3 * u), (x + 0.3 * u, y + 0.3 * u), (x + 0.5 * u, y - 0.25 * u), (x - 0.5 * u, y - 0.25 * u)]), ramp)
        c.paint(rect(x - 0.38 * u, y + 0.2 * u, x + 0.38 * u, y + 0.4 * u), 'gold', outline=False)
    return draw


def bell():
    """手鈴: 手が柄を握り、鈴の口は下へ広がる。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1]
        c.paint(capsule(x, y - 0.3 * u, x, y + 0.7 * u, 0.2 * u), 'wood')
        y0 = y + 0.6 * u
        pts = [(x - 0.35 * u, y0), (x + 0.35 * u, y0), (x + 0.6 * u, y0 + 1.0 * u), (x + 1.05 * u, y0 + 1.5 * u),
               (x - 1.05 * u, y0 + 1.5 * u), (x - 0.6 * u, y0 + 1.0 * u)]
        c.paint(poly(pts, lambda px, py: nrm((px - x) / u * 0.8, -0.1, 0.7)), 'gold', spec=0.8, shine=5)
        c.paint(ellipse(x, y0 + 1.5 * u, 1.05 * u, 0.28 * u), 'gold', gain=0.55)
        c.paint(ellipse(x + 0.2 * u, y0 + 1.75 * u, 0.25 * u, 0.25 * u), 'gold', gain=0.9)
    return draw


def held_coin(metal='silver', r=0.6):
    def draw(c, fig, hand):
        from parts import coin
        u = fig.u
        coin(c, hand[0], hand[1] - 0.55 * u, r * u, metal, tilt=0.95, stamp='tower')
    return draw


def tray():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.2 * u, hand[1] - 0.2 * u
        c.paint(ellipse(x, y, 1.7 * u, 0.42 * u, normal=lambda px, py, a, b: nrm(a * 0.3, -0.85, 0.5)), 'silver', spec=0.6, shine=5)
        c.paint(ellipse(x, y + 0.15 * u, 1.7 * u, 0.3 * u, clip=lambda px, py: py > y + 0.1 * u), 'silver', gain=0.6)
        # 杯と果物
        gx = x - fig.f * 0.5 * u
        c.paint(capsule(gx, y - 0.2 * u, gx, y - 0.8 * u, 0.12 * u), 'gold')
        c.paint(ellipse(gx, y - 1.3 * u, 0.45 * u, 0.55 * u, clip=lambda px, py: py > y - 1.5 * u), 'gold', spec=0.7, shine=5)
        c.paint(ellipse(gx, y - 1.5 * u, 0.45 * u, 0.16 * u), 'red', gain=0.7)
        c.paint(ellipse(x + fig.f * 0.6 * u, y - 0.45 * u, 0.45 * u, 0.42 * u), 'red', spec=0.4)
        c.paint(ellipse(x + fig.f * 1.15 * u, y - 0.35 * u, 0.35 * u, 0.33 * u), 'green', spec=0.3)
    return draw


def orb(r=0.75, ramp='purple'):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] - r * 1.3 * u

        def emit(px, py, n):
            d = math.hypot(px + 0.5 - x + r * 0.3 * u, py + 0.5 - y + r * 0.3 * u) / (r * u * 1.3)
            return clamp(1.05 - d * 0.8)
        c.paint(ellipse(x, y, r * u, r * u), ramp, emit=emit)
    return draw


def held_lantern(hang=0.6):
    from parts import lantern

    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] + hang * u + 9 * u / 13
        c.paint(capsule(hand[0], hand[1], x, y - 12 * u / 13, 0.6), 'silver', outline=False)
        lantern(c, x, y, s=u / 13 * 0.95)
    return draw


def spyglass(length=2.4):
    def draw(c, fig, hand):
        u = fig.u
        f = fig.f
        x, y = hand
        x1 = x + f * length * u
        y1 = y - 0.35 * u
        c.paint(capsule(x - f * 0.3 * u, y + 0.05 * u, x1, y1, 0.15 * u, 0.2 * u, flat=0.2), 'gold', spec=0.6, shine=5)
        mx, my = (x + x1) / 2, (y + y1) / 2
        c.paint(capsule(mx, my - 0.17 * u, mx, my + 0.17 * u, 0.12 * u), 'gold', gain=0.7)
        c.paint(capsule(x1 - f * 0.25 * u, y1 + 0.02 * u, x1, y1, 0.26 * u), 'gold', spec=0.6, gain=0.9)
    return draw


def shield(ramp='blue', emblem='gold'):
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] - 0.3 * u
        w, h = 1.25 * u, 1.9 * u
        pts = [(x - w, y - h * 0.55), (x + w, y - h * 0.55), (x + w, y), (x, y + h * 0.65), (x - w, y)]
        nf = lambda px, py: nrm((px - x) / w * 0.5, (py - y) / h * 0.3, 0.85)
        c.paint(poly(pts, nf), 'gold', spec=0.5)
        inner = [(x - w + 2, y - h * 0.55 + 2), (x + w - 2, y - h * 0.55 + 2), (x + w - 2, y), (x, y + h * 0.65 - 3), (x - w + 2, y)]
        o = c.paint(poly(inner, nf), ramp)
        c.paint(rect(x - 1, y - h * 0.4, x + 1, y + h * 0.4), emblem, oid=o, outline=False)
        c.paint(rect(x - w * 0.6, y - h * 0.15, x + w * 0.6, y - h * 0.15 + 2), emblem, oid=o, outline=False)
    return draw


def banner(ramp='red', deg=-95, length=6.0, flag=(2.2, 1.8), emblem='gold'):
    def draw(c, fig, hand):
        u = fig.u
        f = fig.f
        dx, dy = _dir(fig, deg)
        x0, y0 = hand[0] - dx * 1.2 * u, hand[1] - dy * 1.2 * u
        x1, y1 = hand[0] + dx * length * u, hand[1] + dy * length * u
        fw, fh = flag[0] * u, flag[1] * u
        top = y1 + 0.3 * u
        pts = []
        for i in range(9):
            t = i / 8
            pts.append((x1 + f * fw * t, top + math.sin(t * 5) * 0.25 * u))
        for i in range(8, -1, -1):
            t = i / 8
            pts.append((x1 + f * fw * t, top + fh + math.sin(t * 5 + 0.6) * 0.25 * u - (0.6 * u if 0.35 < t < 0.65 and i % 8 else 0)))
        wave = lambda px, py: nrm(0.55 * math.cos((px - x1) * f / fw * 5), -0.1, 0.8)
        o = c.paint(poly(pts, wave), ramp)
        ex, ey = x1 + f * fw * 0.45, top + fh * 0.42
        c.paint(ellipse(ex, ey, 0.38 * u, 0.38 * u), emblem, oid=o, spec=0.4)
        c.paint(capsule(x0, y0, x1, y1 - 0.3 * u, 0.17 * u), 'wood')
        c.paint(ellipse(x1, y1 - 0.4 * u, 0.28 * u, 0.28 * u), 'gold', spec=0.6)
    return draw


def quill():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        c.paint(capsule(x, y, x - fig.f * 0.5 * u, y - 1.6 * u, 0.2 * u, 0.05 * u), 'paper', gain=1.1)
    return draw


def dagger(deg=60):
    return sword(deg=deg, length=1.9)


def chisel(deg=-150):
    def draw(c, fig, hand):
        u = fig.u
        dx, dy = _dir(fig, deg)
        c.paint(capsule(hand[0] - dx * 0.4 * u, hand[1] - dy * 0.4 * u, hand[0] + dx * 0.4 * u, hand[1] + dy * 0.4 * u, 0.17 * u), 'wood')
        c.paint(capsule(hand[0] + dx * 0.4 * u, hand[1] + dy * 0.4 * u, hand[0] + dx * 1.5 * u, hand[1] + dy * 1.5 * u, 0.12 * u), 'silver', spec=0.6)
    return draw


def held_map():
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        pts = [(x - 1.4 * u, y - 0.7 * u), (x + 0.4 * u, y - 0.9 * u), (x + 0.5 * u, y + 0.6 * u), (x - 1.3 * u, y + 0.8 * u)]
        o = c.paint(poly(pts, nrm(-0.2, -0.3, 0.9)), 'paper', gain=1.05)
        c.paint(capsule(x - 1.0 * u, y + 0.3 * u, x - 0.1 * u, y - 0.4 * u, 0.5), 'red', oid=o, outline=False, gain=1.1)
    return draw


def quiver():
    """背中の矢筒（体より奥に描く）。"""
    def draw(c, fig, hand):
        u = fig.u
        x = fig.X(-0.6, fig.y_sh)
        c.paint(capsule(x - fig.f * 0.4 * u, fig.y_sh - 0.4 * u, x + fig.f * 0.6 * u, fig.y_waist, 0.45 * u), 'leather', gain=0.9)
        for k in range(3):
            c.paint(capsule(x - fig.f * (0.4 + k * 0.15) * u, fig.y_sh - 0.4 * u, x - fig.f * (0.7 + k * 0.2) * u, fig.y_sh - 1.2 * u, 0.12 * u), 'paper', gain=1.0)
    return draw


def club():
    """棍棒: 先の太い木の棒。"""
    def draw(c, fig, hand):
        u = fig.u
        dx, dy = _dir(fig, -70)
        x1, y1 = hand[0] + dx * 2.8 * u, hand[1] + dy * 2.8 * u
        c.paint(capsule(hand[0] - dx * 0.4 * u, hand[1] - dy * 0.4 * u, x1, y1, 0.16 * u, 0.42 * u), 'wood', gain=1.0)
        c.dot(int(x1 - 1), int(y1 - 1), 'G4')
    return draw


def held_keys():
    def draw(c, fig, hand):
        from parts import keyring
        keyring(c, hand[0], hand[1] + 0.3 * fig.u)
    return draw


def held_candelabra():
    def draw(c, fig, hand):
        from parts import candelabra
        candelabra(c, hand[0], hand[1] + 0.3 * fig.u, h=1.6 * fig.u)
    return draw


def parcel():
    """紐をかけた包み。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0], hand[1] - 0.3 * u
        o = c.paint(rect(x - 0.9 * u, y - 0.8 * u, x + 0.9 * u, y + 0.5 * u, nrm(-0.3, -0.2, 0.9)), 'paper', gain=0.9)
        c.paint(rect(x - 0.9 * u, y - 0.2 * u, x + 0.9 * u, y - 0.2 * u + 1.5), 'red', oid=o, outline=False)
        c.paint(rect(x - 0.75, y - 0.8 * u, x + 0.75, y + 0.5 * u), 'red', oid=o, outline=False)
    return draw


def letter():
    """封をした書状（赤い封蝋）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.3 * u, hand[1] - 0.4 * u
        c.paint(rect(x - 0.9 * u, y - 0.55 * u, x + 0.9 * u, y + 0.55 * u, nrm(-0.3, -0.2, 0.9)), 'paper', gain=1.1)
        c.paint(capsule(x - 0.9 * u, y - 0.55 * u, x, y + 0.1 * u, 0.5), 'paper', gain=0.7, outline=False)
        c.paint(capsule(x + 0.9 * u, y - 0.55 * u, x, y + 0.1 * u, 0.5), 'paper', gain=0.7, outline=False)
        c.paint(ellipse(x, y + 0.1 * u, 0.3 * u, 0.3 * u), 'red', gain=1.1, spec=0.4)
    return draw


def fan(ramp='red'):
    """扇（開いた扇の骨が放射に）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        pts = [(x, y)] + arc_points(x, y, 1.5 * u, -math.pi * 0.95, -math.pi * 0.45, 10)
        o = c.paint(poly(pts, nrm(-0.3, -0.3, 0.9)), ramp, gain=1.05)
        for a in [-math.pi * (0.92 - k * 0.09) for k in range(6)]:
            c.paint(capsule(x, y, x + math.cos(a) * 1.4 * u, y + math.sin(a) * 1.4 * u, 0.4), 'gold', oid=o, gain=0.8, outline=False)
    return draw


def mask_stick(ramp='gold'):
    """棒のついた仮面。"""
    def draw(c, fig, hand):
        from parts import mask
        u = fig.u
        c.paint(capsule(hand[0], hand[1] + 0.5 * u, hand[0], hand[1] - 1.2 * u, 0.12 * u), 'wood')
        mask(c, hand[0], hand[1] - 1.8 * u, ramp)
    return draw


def pot(ramp='copper'):
    """手に持つ鍋（修理中）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand[0] + fig.f * 0.9 * u, hand[1]
        c.paint(ellipse(x, y, 1.0 * u, 0.85 * u, clip=lambda px, py: py >= y - 0.3 * u), ramp, spec=0.6, shine=5)
        c.paint(ellipse(x, y - 0.3 * u, 1.0 * u, 0.3 * u), ramp, gain=0.55)
        c.paint(capsule(x - fig.f * 1.0 * u, y - 0.3 * u, hand[0], hand[1], 0.12 * u), 'silver')
    return draw


def rod():
    """測量の目盛り竿（紅白の縞）。"""
    def draw(c, fig, hand):
        u = fig.u
        x, y = hand
        for k in range(8):
            y0 = y - 4.5 * u + k * 0.75 * u
            c.paint(capsule(x, y0, x, y0 + 0.75 * u, 0.17 * u, flat=0.2), 'red' if k % 2 == 0 else 'paper', gain=1.0)
        c.paint(capsule(x, y + 1.5 * u, x, y + 3.6 * u, 0.15 * u), 'wood')
    return draw
