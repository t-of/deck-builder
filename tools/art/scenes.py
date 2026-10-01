"""場面データ: カードごとに「どこで・何を・どの光で」だけを書く。描き方は parts / figure が共通で持つ。

各場面は dict:
  light: Light の引数（光だまりの中心 pool・半径 radius・見えている灯りの halo など）
  env:   背景の組み立て（ENVS の名前と引数）
  items: 奥から順に置く部品 [(部品の名前, 引数)]。'figure' は人物（figure.figure の引数）。
"""
import math

import figure as F
import parts as P
from engine import Light, capsule, ellipse, nrm, poly, rect


# ================= 背景の組み立て =================

def env_room(c, wall='stone', hz=100, floor='table', floor_ramp='wood', wall_gain=1.0, floor_gain=1.0, bw=18, bh=9):
    if wall == 'stone':
        P.stone_wall(c, 0, hz, bw=bw, bh=bh, gain=0.8 * wall_gain)
    elif wall == 'plank':
        P.plank_wall(c, 0, hz, gain=0.8 * wall_gain)
    elif wall == 'shoji':
        from parts_renaissance import shoji_wall
        shoji_wall(c, 0, hz, gain=0.8 * wall_gain)
    if floor == 'table':
        P.table_top(c, hz, floor_ramp, gain=floor_gain)
    elif floor == 'flag':
        P.flag_floor(c, hz, gain=0.85 * floor_gain)
    elif floor == 'planks':
        P.table_top(c, hz, 'wood', gain=0.8 * floor_gain, edge=False)


def env_night(c, hz=110, moon=(40, 32, 11), hills=(), ground_ramp='foliage', ground_gain=0.75, stars=26, wave=2.0, sky_ramp='night',
              clouds=((46, 70, 8), (70, 90, 7))):
    P.sky(c, hz + 10, ramp=sky_ramp, stars=stars, glow=moon is not None, clouds=clouds)
    if moon:
        P.moon(c, *moon)
    for i, (base, amp, gain, dep, seed) in enumerate(hills):
        P.hills(c, base, amp, gain=gain, depth=dep, seed=seed)
    if ground_ramp:
        P.ground(c, hz, ground_ramp, gain=ground_gain, wave=wave)


def env_forest(c, hz=118, moon=(36, 24, 10), seed=0, ground_gain=0.8):
    """夜の森: 奥ほど暗く寒い幹の列を 3 層、手前に草地。"""
    P.sky(c, hz, stars=14)
    if moon:
        P.moon(c, *moon)
    for layer, (n, gain, dep, w0) in enumerate(((9, 0.5, 0.8, 4), (7, 0.65, 0.55, 6), (4, 0.8, 0.25, 9))):
        for i in range(n):
            x = (i + 0.5 + (P.hsh(i, layer, seed) - 0.5) * 0.6) * 224 / n
            w = w0 * (0.8 + P.hsh(layer, i) * 0.5)
            if moon and abs(x - moon[0]) < moon[2] + w and layer == 0:
                continue
            c.paint(rect(x - w / 2, 0, x + w / 2, hz + 4 + layer * 3, lambda px, py, x=x, w=w: nrm((px - x) / w * 1.6, 0, 0.8)),
                    'wood', gain=gain, depth=dep, tex=lambda px, py: -0.05 if (py + px * 7) % 13 == 0 else 0)
        P.ground(c, hz - 6 + layer * 5, 'foliage', gain=0.45 + layer * 0.15, depth=0.6 - layer * 0.25, seed=seed + layer, tufts=layer == 2)
    canopy = []
    for x in range(224):
        b = 14 + 8 * math.sin(x / 13 + seed) + 5 * math.sin(x / 5.3)
        for y in range(0, int(b)):
            canopy.append((x, y, nrm(0, 0.5, 0.8)))
    c.paint(canopy, 'foliage', gain=0.5, outline=False, dither=True, tex=lambda px, py: -0.06 if (px * 3 + py * 5) % 7 == 0 else 0)


def env_battlement(c, hz=104, moon=(34, 26, 11), parapet=(92, 126), stars=24, far=True):
    """城壁の上: 夜空と遠い山、奥の胸壁、足もとの石畳。"""
    P.sky(c, hz, stars=stars, glow=moon is not None)
    if moon:
        P.moon(c, *moon)
    if far:
        P.hills(c, hz - 6, 12, gain=0.4, depth=0.7, seed=4)
    P.crenel_wall(c, 0, 224, parapet[0], parapet[1], merlon=14, gap=10, gain=0.85)
    P.flag_floor(c, parapet[1], gain=0.85)


def env_cave(c, hz=126, ramp='stone', gain=0.8, seed=0):
    P.rock_wall(c, 0, hz, ramp=ramp, gain=gain, seed=seed)
    P.ground(c, hz, 'stone', gain=0.75, wave=2.5, seed=seed, tufts=False)


def env_pass(c, hz=120, moon=(36, 24, 11)):
    """峠: 夜空、重なる山の稜線、岩の道。"""
    P.sky(c, hz, stars=30)
    if moon:
        P.moon(c, *moon)
    P.hills(c, 92, 40, gain=0.45, depth=0.75, seed=2, freq=1.4)
    P.hills(c, 110, 30, gain=0.55, depth=0.5, seed=6, freq=1.1)
    P.ground(c, hz, 'stone', gain=0.8, wave=4.0, seed=3, tufts=False)


def env_icon(c, hz=106, wall='stone', cloth='red', cloth_gain=0.8):
    """アイコン用: 暗い壁と、布を掛けた台。主役 1 つを真ん中に置く。"""
    if wall == 'stone':
        P.stone_wall(c, 0, hz, gain=0.7)
    else:
        P.plank_wall(c, 0, hz, gain=0.7)
    pix = [(x, y, P.UP) for y in range(hz, 160) for x in range(224)]
    c.paint(pix, cloth, gain=cloth_gain, dither=True, outline=False,
            tex=lambda px, py: -0.06 if int(px + 4 * math.sin(py / 5.0)) % 18 == 0 else 0)


def env_coast(c, hz=86, shore=None, moon=(40, 26, 11), sky_ramp='night', stars=30, clouds=((40, 80, 7),), sea_gain=1.0):
    """海辺: 夜空、水平線までの海（月の下に光の道）、手前に砂浜（shore を渡したとき）。"""
    P.sky(c, hz + 2, ramp=sky_ramp, stars=stars, glow=moon is not None, clouds=clouds)
    if moon:
        P.moon(c, *moon)
    P.sea(c, hz, gain=sea_gain, moon_x=moon[0] if moon else None)
    if shore is not None:
        P.beach(c, shore)


ENVS = {'coast': env_coast, 'room': env_room, 'night': env_night, 'forest': env_forest, 'battlement': env_battlement,
        'cave': env_cave, 'pass': env_pass, 'icon': env_icon}


# ================= 一枚絵の部品の組み合わせ =================

def gems_at(c, pts):
    for x, y, r, ramp in pts:
        P.gem(c, x, y, r, ramp)


PARTS = {n: f for n, f in vars(P).items() if callable(f) and not n.startswith('_')}
PARTS.update({
    'torch': P.wall_torch, 'window_arch': P.arched_window, 'stack': P.coin_stack, 'pile': P.coin_pile,
    'gems': gems_at, 'wall': P.crenel_wall, 'book': P.book_closed, 'figure': F.figure, 'floor': P.table_top,
})

PROPS = {name: getattr(F, name) for name in (
    'staff', 'sword', 'axe', 'hammer', 'bow', 'book', 'scroll', 'bag', 'bell', 'tray', 'orb', 'held_lantern',
    'spyglass', 'shield', 'banner', 'quill', 'dagger', 'chisel', 'held_map', 'held_coin', 'quiver',
    'club', 'held_keys', 'held_candelabra', 'parcel', 'letter', 'fan', 'mask_stick', 'pot', 'rod')}
PROPS.update({name: getattr(P, name) for name in ('spade', 'cutlass', 'cane', 'casket', 'pearl', 'coil_held',
                                                  'pitchfork', 'torch_held', 'tray_strap', 'held_bottle', 'crook_staff',
                                                  'basket_held', 'held_flask', 'mortar_held',
                                                  'bindle', 'held_dividers', 'held_wheel', 'silver_plate', 'toolbox',
                                                  'scythe', 'broom', 'cleaver', 'hunting_horn', 'peel', 'juggle', 'halberd', 'flowers_held',
                                                  'lead_rope', 'hoof')})


def _prop(spec):
    if isinstance(spec, str):
        return PROPS[spec]()
    name, kw = spec
    return PROPS[name](**kw)


# ================= カードごとの場面 =================

SCENES = {
    # ---- 財宝: 銅 → 銀 → 金で、硬貨の数・積み方・光の強さを上げる ----
    'copper': dict(  # 銅: 粗い板の卓に、すり減った銅貨が数枚と短い山
        light=dict(pool=(112, 116), radius=(150, 100), fall=1.1, halo=(32, 60, 40, 0.55), flat=0.5),
        env=('room', dict(wall='plank', hz=92, floor='table', floor_gain=0.75)),
        items=[
            ('candle', dict(x=32, base=90, h=12, r=4, holder=True)),
            ('sack', dict(x=176, base=112, r=14, ramp='leather', gain=0.85)),
            ('stack', dict(cx=96, base=134, r=16, n=5, metal='copper', stamp='pip', seed=1)),
            ('coin', dict(cx=140, cy=118, r=14, metal='copper', stamp='star', tilt=0.55)),
            ('coin', dict(cx=150, cy=140, r=15, metal='copper', stamp='pip', tilt=0.5, rot=-0.3)),
            ('coin', dict(cx=56, cy=146, r=14, metal='copper', stamp='star', tilt=0.48, rot=0.4)),
        ]),
    'silver': dict(
        light=dict(pool=(108, 118), radius=(160, 105), fall=1.2, halo=(40, 40, 50, 0.5), amb=0.05),
        env=('room', dict(wall='stone', hz=96, floor='table', floor_ramp='stone', floor_gain=0.95)),
        items=[
            ('window_arch', dict(x=22, y=10, w=34, h=62)),
            ('stack', dict(cx=78, base=136, r=13, n=8, metal='silver', stamp='tower', seed=2)),
            ('stack', dict(cx=118, base=124, r=13, n=5, metal='silver', stamp='tower', seed=3)),
            ('stack', dict(cx=160, base=140, r=13, n=3, metal='silver', stamp='tower', seed=4)),
            ('coin', dict(cx=124, cy=148, r=12, metal='silver', stamp='star', tilt=0.5)),
            ('coin', dict(cx=192, cy=126, r=11, metal='silver', stamp='tower', tilt=0.55)),
            ('coin', dict(cx=42, cy=148, r=11, metal='silver', stamp='star', tilt=0.5, rot=0.5)),
        ]),
    'gold': dict(
        light=dict(pool=(112, 118), radius=(165, 115), fall=1.15, halo=(26, 38, 50, 0.6), amb=0.05, key=0.8),
        env=('room', dict(wall='stone', hz=88, floor='table', floor_gain=0.9)),
        items=[
            ('candelabra', dict(x=26, base=84, h=30)),
            ('chest', dict(x=66, base=112, w=86, h=34, fill='gold')),
            ('stack', dict(cx=40, base=136, r=12, n=7, metal='gold', seed=5)),
            ('stack', dict(cx=188, base=128, r=12, n=10, metal='gold', stamp='star', seed=6)),
            ('pile', dict(cx=118, base=150, w=70, h=30, metal='gold', r=11, count=34, seed=1)),
            ('gems', dict(pts=[(150, 122, 5, 'red'), (88, 134, 4, 'blue'), (170, 146, 4, 'green')])),
            ('coin', dict(cx=62, cy=152, r=11, metal='gold', stamp='crown', tilt=0.55)),
            ('coin', dict(cx=200, cy=152, r=10, metal='gold', stamp='star', tilt=0.5)),
        ]),
    # ---- 勝利点: 小屋 → 荘園 → 領地で、建物の大きさと灯りの数を上げる ----
    'estate': dict(
        light=dict(pool=(120, 92), radius=(150, 100), fall=1.2, halo=(46, 30, 44, 0.7), amb=0.05),
        env=('night', dict(hz=118, moon=(46, 30, 12), hills=[(104, 16, 0.55, 0.6, 1)])),
        items=[
            ('tree', dict(x=190, base=124, h=70, kind='oak', gain=0.8, seed=1)),
            ('house', dict(x=72, base=130, w=64, h=38, roof_h=36, wall='paper', roof='wood', chimney=0.5, gain=0.85,
                           windows=[(11, 10, 11, 11, True)], door=(38, 11, 20))),
            ('ground', dict(y0=132, ramp='foliage', gain=0.9, wave=1.2, seed=2)),
            ('fence', dict(x0=150, x1=214, base=146, h=12)),
            ('flower', dict(x=48, y=140, r=4, ramp='gold')), ('flower', dict(x=62, y=146, r=4, ramp='red')), ('flower', dict(x=34, y=150, r=4, ramp='blue')),
        ]),
    'duchy': dict(
        light=dict(pool=(118, 92), radius=(160, 105), fall=1.15, halo=(48, 78, 30, 0.6), amb=0.05),
        env=('night', dict(hz=120, moon=None, hills=[(100, 18, 0.5, 0.6, 3)])),
        items=[
            ('lamp_post', dict(x=36, base=134, h=72)),
            ('tree', dict(x=12, base=124, h=70, kind='pine', gain=0.6, seed=3)),
            ('tree', dict(x=206, base=124, h=74, kind='oak', gain=0.75, seed=4)),
            ('house', dict(x=62, base=128, w=54, h=46, roof_h=26, wall='stone', roof='red', chimney=0.3,
                           windows=[(8, 8, 8, 10, True), (36, 8, 8, 10, True), (8, 28, 8, 10, False), (36, 28, 8, 10, True)],
                           door=(21, 12, 18), timber=False)),
            ('house', dict(x=130, base=128, w=34, h=30, roof_h=20, wall='stone', roof='red', gain=0.85,
                           windows=[(6, 9, 7, 9, True), (21, 9, 7, 9, True)], timber=False)),
            ('ground', dict(y0=130, ramp='foliage', gain=0.85, wave=1.0, seed=5)),
        ]),
    'province': dict(
        light=dict(pool=(120, 70), radius=(165, 110), fall=1.1, halo=(26, 18, 34, 0.6), amb=0.05),
        env=('night', dict(hz=108, moon=(26, 18, 8, 0.45), hills=[(96, 14, 0.45, 0.7, 5)], ground_gain=0.55)),
        items=[
            ('castle', dict(x=112, base=104, s=1.0)),
            ('ground', dict(y0=118, ramp='foliage', gain=0.7, wave=3.0, seed=8)),
            ('house', dict(x=26, base=146, w=24, h=14, roof_h=12, roof='red', gain=0.75, windows=[(5, 4, 5, 5, True)])),
            ('house', dict(x=168, base=150, w=28, h=15, roof_h=13, roof='red', gain=0.75, windows=[(6, 4, 5, 6, True), (17, 4, 5, 6, True)])),
            ('tree', dict(x=200, base=140, h=40, kind='pine', gain=0.6, seed=9)),
            ('tree', dict(x=10, base=150, h=46, kind='pine', gain=0.6, seed=10)),
        ]),
    # ---- 災い: 紫の灯（左上）だけが照らす、髑髏と枯れ木 ----
    'curse': dict(
        light=dict(pool=(110, 90), radius=(130, 95), fall=1.3, halo=(40, 44, 40, 0.6), amb=0.04),
        env=('night', dict(hz=118, moon=None, stars=0, ground_ramp='stone', ground_gain=0.7, wave=3.0, sky_ramp='purple')),
        items=[
            ('tree', dict(x=170, base=124, h=100, kind='dead', ramp='cloth', gain=0.8, seed=11)),
            ('grave', dict(x=104, base=124, w=42, h=58)),
            ('wisp_candle', dict(x=40, base=124)),
            ('skull', dict(x=110, y=128, s=2.0)),
            ('wisps', dict(pts=[(150, 70), (70, 50), (184, 110)])),
        ]),
    # ================= 王国カード: 人物を出さないもの =================
    'warehouse': dict(  # 穴蔵: ランタンひとつの地下蔵に、樽と木箱
        light=dict(pool=(118, 100), radius=(150, 105), fall=1.15, halo=(38, 46, 40, 0.7)),
        env=('room', dict(wall='stone', hz=108, floor='flag', bw=22, bh=11)),
        items=[
            ('lantern', dict(x=38, y=48, hang=0)),
            ('cobweb', dict(x=0, y=0, r=22)),
            ('crate', dict(x=26, y=104, w=32, h=30, gain=0.95)),
            ('crate', dict(x=34, y=82, w=22, h=22, gain=1.0)),
            ('barrel', dict(x=118, base=140, r=17, h=44, lying=True)),
            ('barrel', dict(x=166, base=140, r=17, h=44, lying=True, gain=0.9)),
            ('barrel', dict(x=142, base=108, r=16, h=42, lying=True, gain=1.0)),
            ('sack', dict(x=82, base=146, r=11, gain=0.9)),
            ('sack', dict(x=206, base=150, r=10, gain=0.7)),
        ]),
    'abbey': dict(  # 祈りの庵: 月の窓、祭壇の蝋燭と開いた書
        light=dict(pool=(108, 92), radius=(145, 100), fall=1.2, halo=(36, 36, 44, 0.7)),
        env=('room', dict(wall='stone', hz=114, floor='flag', bw=16, bh=10)),
        items=[
            ('window_arch', dict(x=20, y=8, w=32, h=64)),
            ('niche', dict(x=112, top=18, w=56, h=72)),
            ('table', dict(x0=64, x1=164, top=96, legs_to=128, ramp='stone', cloth='blue')),
            ('candle', dict(x=78, base=94, h=16, r=3)),
            ('candle', dict(x=148, base=94, h=12, r=3)),
            ('open_book', dict(x=112, y=86, w=16, h=8)),
        ]),
    'moat': dict(  # 水濠: 月夜の城壁と城門、堀の水に月が映る
        light=dict(pool=(104, 84), radius=(160, 110), fall=1.1, halo=(52, 20, 40, 0.7)),
        env=('night', dict(hz=98, moon=(52, 20, 11, 0.55), hills=[(70, 10, 0.4, 0.7, 2)], ground_ramp=None)),
        items=[
            ('wall', dict(x0=0, x1=224, top=46, bottom=108, merlon=10, gap=6)),
            ('tower', dict(x=0, base=108, w=30, h=70, roof=None, crenel=True, windows=[(-2, 24, 5, 8)])),
            ('tower', dict(x=180, base=108, w=34, h=80, roof='blue', crenel=False, gain=0.8, windows=[(-2, 30, 5, 8)])),
            ('drawbridge_gate', dict(x=112, base=108, w=40, h=52)),
            ('water', dict(y0=108)),
        ]),
    'village': dict(  # 集落: 灯りのともる家が寄り合い、真ん中に井戸
        light=dict(pool=(112, 96), radius=(160, 100), fall=1.1, halo=(54, 100, 40, 0.5)),
        env=('night', dict(hz=118, moon=None, hills=[(100, 12, 0.45, 0.65, 7)], clouds=((30, 90, 9), (52, 70, 7)))),
        items=[
            ('house', dict(x=4, base=112, w=40, h=26, roof_h=22, roof='red', gain=0.6, windows=[(8, 8, 6, 7, True), (25, 8, 6, 7, True)])),
            ('house', dict(x=138, base=110, w=34, h=24, roof_h=20, roof='wood', gain=0.55, windows=[(12, 8, 7, 7, True)])),
            ('house', dict(x=38, base=126, w=46, h=30, roof_h=26, roof='wood', chimney=0.5, windows=[(8, 8, 8, 9, True), (28, 8, 8, 9, False)], door=(20, 8, 14))),
            ('house', dict(x=152, base=130, w=40, h=28, roof_h=24, roof='red', gain=0.85, windows=[(8, 8, 8, 8, True)], door=(24, 8, 13))),
            ('ground', dict(y0=130, ramp='stone', gain=0.75, wave=0.5, seed=4, tufts=False)),
            ('well', dict(x=114, base=146, r=15)),
            ('fence', dict(x0=0, x1=40, base=156, h=12)),
        ]),
    'workshop': dict(  # 作業場: 壁の道具掛けと、作業台の上の鋸・板
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(30, 44, 40, 0.7)),
        env=('room', dict(wall='plank', hz=100, floor='planks')),
        items=[
            ('lantern', dict(x=30, y=44, hang=0)),
            ('tool_rack', dict(x0=56, x1=216, y=10, tools=('saw', 'hammer', 'pliers', 'axe', 'coil'), s=1.9)),
            ('table', dict(x0=36, x1=196, top=110, legs_to=152)),
            ('plank', dict(x0=60, y0=104, x1=150, y1=100, w=3)),
            ('plank', dict(x0=64, y0=96, x1=140, y1=92, w=2.5)),
            ('saw_on_bench', dict(x=150, y=104)),
            ('mallet', dict(x=96, y=110)),
            ('vise', dict(x=180, top=110)),
            ('shavings', dict(pts=[(70, 112), (120, 113), (170, 111), (178, 114)])),
        ]),
    'meadow': dict(  # 花畑: 月夜の丘に、手前ほど大きい花
        light=dict(pool=(112, 108), radius=(180, 110), fall=1.0, halo=(30, 74, 50, 0.7)),
        env=('night', dict(hz=96, moon=(30, 74, 17), hills=[(82, 10, 0.45, 0.7, 1), (92, 8, 0.55, 0.45, 5)], ground_gain=0.6, wave=2.5)),
        items=[
            ('tree', dict(x=186, base=98, h=44, kind='oak', gain=0.6, seed=3)),
            ('house', dict(x=140, base=92, w=18, h=10, roof_h=9, roof='red', gain=0.5, windows=[(6, 3, 4, 4, True)], timber=False)),
            ('flowers', dict(rows=[(106, 2.6, 18), (122, 4.2, 22), (146, 7.5, 30)])),
            ('far_lights', dict(pts=[(60, 110), (96, 104), (120, 116), (170, 112), (40, 124)])),
        ]),
    'pawnbroker': dict(  # 質屋: 天秤で銅と金を量る。奥の棚に質草
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 72, 34, 0.6)),
        env=('room', dict(wall='plank', hz=100, floor='table')),
        items=[
            ('shelf', dict(x0=60, x1=210, y=46)),
            ('goblet', dict(x=80, base=46, s=1.2, ramp='silver', wine=False)),
            ('bottle', dict(x=104, base=46, h=16, r=4, ramp='blue')),
            ('candelabra', dict(x=140, base=46, h=20, arms=0)),
            ('goblet', dict(x=186, base=46, s=1.0)),
            ('candle', dict(x=28, base=96, h=12, r=3)),
            ('balance', dict(x=112, base=146, h=62, tilt=7, left='copper', right='gold', s=1.45)),
            ('stack', dict(cx=40, base=150, r=12, n=5, metal='copper', stamp='pip', seed=8)),
            ('gems', dict(pts=[(176, 138, 5, 'red'), (188, 148, 4, 'blue')])),
            ('necklace', dict(x=166, y=146)),
        ]),
    'remodel': dict(  # 建て替え: 足場の中で積み直す石壁、滑車で吊った石
        light=dict(pool=(110, 96), radius=(160, 100), fall=1.1, halo=(44, 60, 40, 0.7)),
        env=('night', dict(hz=126, moon=None, ground_ramp='stone', ground_gain=0.7, wave=1.0)),
        items=[
            ('ruin_wall', dict(x0=66, x1=168, base=130)),
            ('scaffold', dict(x0=58, x1=176, top=34, base=132)),
            ('crane', dict(x=150, top=26, hook=(146, 64))),
            ('torch', dict(x=44, y=60)),
            ('block', dict(x=134, y=66, w=22, h=14)),
            ('block', dict(x=20, y=130, w=26, h=16, gain=0.9)),
            ('block', dict(x=176, y=136, w=26, h=16, gain=0.8)),
            ('block', dict(x=34, y=114, w=18, h=14, gain=0.95)),
        ]),
    'smithy': dict(  # 鍛冶場: 左上の炉の火が、金床の赤い鉄を照らす
        light=dict(pool=(96, 100), radius=(150, 100), fall=1.15, halo=(36, 62, 54, 0.9), key=0.8),
        env=('room', dict(wall='stone', hz=112, floor='flag', bw=14, bh=8)),
        items=[
            ('forge', dict(x=6, y=40, w=62, h=56)),
            ('tool_rack', dict(x0=150, x1=220, y=22, tools=('tongs', 'hammer', 'tongs'))),
            ('barrel', dict(x=196, base=140, r=14, h=28, gain=0.7)),
            ('anvil', dict(x=118, base=142, s=1.6)),
            ('hot_bar', dict(x0=96, x1=140, y=104)),
            ('hammer_rest', dict(x=150, y=100)),
            ('sparks', dict(pts=[(110, 92), (124, 86), (102, 80), (136, 94), (118, 74), (96, 96), (130, 70)])),
        ]),
    'assembly': dict(  # 集会所: 梁から下がる旗の列と、長い卓
        light=dict(pool=(112, 96), radius=(160, 100), fall=1.1, halo=(16, 42, 40, 0.7)),
        env=('room', dict(wall='stone', hz=116, floor='flag')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('beam', dict(y=8)),
            ('hang_banner', dict(x=36, top=10, w=22, h=54, ramp='red', kind='circle')),
            ('hang_banner', dict(x=78, top=10, w=22, h=62, ramp='blue', kind='cross')),
            ('hang_banner', dict(x=124, top=10, w=22, h=62, ramp='green', kind='chevron')),
            ('hang_banner', dict(x=166, top=10, w=22, h=54, ramp='purple', kind='circle')),
            ('chair', dict(x=60, base=118)), ('chair', dict(x=96, base=118)), ('chair', dict(x=132, base=118)), ('chair', dict(x=168, base=118)),
            ('table', dict(x0=24, x1=200, top=116, legs_to=156, cloth='red')),
            ('candelabra', dict(x=112, base=112, h=24)),
            ('goblet', dict(x=60, base=114)), ('goblet', dict(x=164, base=114, ramp='silver', wine=True)),
            ('book', dict(x=74, y=112, w=16, h=2, t=6, ramp='blue')),
        ]),
    'fair': dict(  # 夜店: 提灯の連なりと、縞の日よけの屋台
        light=dict(pool=(112, 96), radius=(160, 100), fall=1.1, halo=(26, 50, 40, 0.6)),
        env=('night', dict(hz=120, moon=None, stars=30, ground_ramp='stone', ground_gain=0.7, wave=0.5)),
        items=[
            ('tent', dict(x=168, base=122, w=56, h=60)),
            ('paper_lantern', dict(x=26, y=50, r=11, ramp='gold', string=0)),
            ('stall', dict(x0=40, x1=176, top=58, base=140, colors=('red', 'paper'))),
            ('lantern_string', dict(y0=18, y1=34, colors=('red', 'gold', 'red', 'blue', 'red', 'green', 'red'))),
            ('goblet', dict(x=62, base=118)), ('goblet', dict(x=74, base=118, ramp='silver')),
            ('basket', dict(x=100, base=122, w=22, h=8, kind='apple', fill='red', n=6)),
            ('mask', dict(x=136, y=106, ramp='gold')), ('mask', dict(x=154, y=104, ramp='blue')),
        ]),
    'alembic': dict(  # 錬金室: 炎の上のフラスコが緑に光り、管で別の瓶へ
        light=dict(pool=(104, 98), radius=(150, 100), fall=1.15, halo=(28, 54, 34, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='table', floor_ramp='wood')),
        items=[
            ('shelf', dict(x0=120, x1=220, y=36)),
            ('bottle', dict(x=134, base=36, h=16, r=4, ramp='red')), ('bottle', dict(x=150, base=36, h=12, r=5, ramp='blue')),
            ('bottle', dict(x=168, base=36, h=18, r=4, ramp='purple')), ('bottle', dict(x=186, base=36, h=12, r=4, ramp='green')),
            ('bottle', dict(x=204, base=36, h=15, r=5, ramp='gold')),
            ('shelf', dict(x0=130, x1=220, y=70)),
            ('books_row', dict(x0=134, x1=214, base=70, hmin=11, hmax=18, seed=2)),
            ('candle', dict(x=28, base=62, h=12, r=3)),
            ('shelf', dict(x0=10, x1=48, y=62)),
            ('burner', dict(x=86, base=136)),
            ('flask', dict(x=86, y=106, r=16, ramp='green', neck=12)),
            ('tube', dict(pts=[(88, 76), (100, 66), (150, 96), (164, 112)])),
            ('flask', dict(x=168, y=126, r=10, ramp='green', neck=6)),
            ('skull', dict(x=40, y=134, s=0.9)),
        ]),
    'archive': dict(  # 文書館: 天井まで届く書棚と梯子、手前の書見台
        light=dict(pool=(104, 96), radius=(150, 100), fall=1.15, halo=(32, 70, 34, 0.7)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[
            ('bookcase', dict(x0=0, x1=224, top=0, bottom=124)),
            ('ladder', dict(x=164, top=6, base=128, w=16)),
            ('candelabra', dict(x=32, base=108, h=26)),
            ('lectern', dict(x=100, base=154, h=28)),
            ('open_book', dict(x=100, y=116, w=18, h=9)),
            ('scrolls', dict(x=190, base=152)),
        ]),
    'market': dict(  # 露店: 緑の日よけの下に、りんご・パン・魚・菜
        light=dict(pool=(112, 104), radius=(160, 100), fall=1.1, halo=(30, 52, 34, 0.65)),
        env=('night', dict(hz=118, moon=None, stars=18, ground_ramp='stone', ground_gain=0.7, wave=0.5,
                           hills=[(104, 10, 0.4, 0.7, 3)])),
        items=[
            ('house', dict(x=150, base=110, w=40, h=26, roof_h=20, roof='wood', gain=0.5, windows=[(8, 8, 6, 7, True)])),
            ('stall', dict(x0=34, x1=190, top=50, base=146, colors=('green', 'paper'), counter='crates')),
            ('lantern', dict(x=30, y=64, hang=50)),
            ('basket', dict(x=62, base=124, w=28, h=10, kind='apple', fill='red', n=8)),
            ('basket', dict(x=98, base=124, w=28, h=10, kind='bread', n=5)),
            ('basket', dict(x=134, base=124, w=28, h=10, kind='cabbage', n=5)),
            ('basket', dict(x=168, base=124, w=28, h=10, kind='fish', n=4)),
            ('basket', dict(x=48, base=152, w=30, h=12, kind='apple', fill='gold', n=8)),
            ('sack', dict(x=188, base=156, r=11)),
        ]),
    'mine': dict(  # 鉱脈: 支え木の坑道、岩に金の筋、鉱車とつるはし
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(50, 44, 40, 0.7)),
        env=('cave', dict(hz=132, seed=4)),
        items=[
            ('tunnel', dict(x0=58, x1=166, top=30, bottom=138)),
            ('beam_frame', dict(x0=50, x1=174, top=30, bottom=138, w=8)),
            ('lantern', dict(x=60, y=46, hang=24)),
            ('vein', dict(pts=[(4, 70), (18, 76), (30, 72), (42, 82)])),
            ('vein', dict(pts=[(186, 40), (196, 52), (210, 50), (222, 62)])),
            ('vein', dict(pts=[(184, 100), (198, 96), (206, 108)])),
            ('rails', dict(y=150)),
            ('cart', dict(x=126, base=152, w=50, h=20)),
            ('pickaxe', dict(x=22, y=150, ang=-70, length=44)),
            ('gems', dict(pts=[(200, 146, 4, 'gold'), (40, 128, 3, 'gold')])),
        ]),
    'banquet': dict(  # 晩餐: 燭台の灯で、丸焼きと杯の並ぶ卓
        light=dict(pool=(116, 108), radius=(150, 100), fall=1.15, halo=(30, 46, 44, 0.7)),
        env=('room', dict(wall='stone', hz=96, floor='table', floor_ramp='red', floor_gain=0.8)),
        items=[
            ('hang_banner', dict(x=150, top=0, w=26, h=56, ramp='blue', kind='chevron')),
            ('candelabra', dict(x=34, base=100, h=30)),
            ('roast', dict(x=118, y=118, s=1.5)),
            ('goblet', dict(x=66, base=128, s=1.3)), ('goblet', dict(x=176, base=126, s=1.2, ramp='silver')),
            ('basket', dict(x=192, base=150, w=30, h=10, kind='apple', fill='green', n=6)),
            ('basket', dict(x=46, base=152, w=30, h=10, kind='bread', n=4)),
            ('plate', dict(x=150, y=146)), ('plate', dict(x=90, y=148)),
        ]),
    # ================= 王国カード: 人物 =================
    'crier': dict(  # 呼び込み: 夜の通りで鈴を振り、触れ書きを持つ
        light=dict(pool=(108, 88), radius=(150, 105), fall=1.1, halo=(62, 62, 34, 0.7)),
        env=('night', dict(hz=126, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.5)),
        items=[
            ('house', dict(x=0, base=122, w=44, h=34, roof_h=24, roof='red', gain=0.6, windows=[(10, 10, 7, 8, True), (28, 10, 7, 8, True)])),
            ('house', dict(x=156, base=124, w=44, h=36, roof_h=26, roof='wood', gain=0.55, windows=[(10, 10, 8, 9, True)], door=(26, 9, 15))),
            ('figure', dict(x=110, foot=152, h=112, arms=('hip', 'raise'), tunic='red', cloak='blue', head='feather', head_ramp='blue',
                            legs_ramp='cloth', belt='leather', props=[(1, 'bell', True)])),
            ('lamp_post', dict(x=52, base=140, h=96)),
        ]),
    'moneylender': dict(  # 両替商: 帳場の向こうで銀貨をかざす
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.15, halo=(30, 52, 40, 0.7)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[
            ('shelf', dict(x0=150, x1=220, y=48)),
            ('books_row', dict(x0=154, x1=216, base=48, seed=4)),
            ('shelf', dict(x0=14, x1=50, y=56)),
            ('candle', dict(x=30, base=54, h=12, r=3, holder=True)),
            ('figure', dict(x=108, foot=158, h=112, arms=('chest', 'lift'), robe=True, tunic='green', trim='gold', mantle='red',
                            head='hat', head_ramp='cloth', props=[(1, ('held_coin', dict(metal='silver', r=0.7)), True)])),
            ('table', dict(x0=20, x1=204, top=120, legs_to=160, front=True)),
            ('stack', dict(cx=50, base=124, r=10, n=6, metal='copper', stamp='pip', seed=3)),
            ('stack', dict(cx=160, base=124, r=10, n=4, metal='silver', stamp='tower', seed=4)),
            ('stack', dict(cx=184, base=126, r=10, n=7, metal='silver', stamp='tower', seed=5)),
            ('coin', dict(cx=80, cy=132, r=9, metal='copper', stamp='star')),
        ]),
    'attendant': dict(  # 小姓: 旗の下がる広間で、盆を捧げ持つ少年
        light=dict(pool=(108, 90), radius=(150, 100), fall=1.15, halo=(16, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[
            ('torch', dict(x=16, y=38)),
            ('hang_banner', dict(x=168, top=0, w=26, h=64, ramp='red', kind='circle')),
            ('hang_banner', dict(x=40, top=0, w=22, h=54, ramp='blue', kind='cross')),
            ('figure', dict(x=104, foot=150, h=92, arms=('down', 'present'), tunic='blue', trim='gold', head='feather', head_ramp='red',
                            legs_ramp='red', props=[(1, 'tray', True)])),
        ]),
    'official': dict(  # 徴税官: 台帳を開き、指さして取り立てる
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.15, halo=(18, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=120, floor='flag')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('doorway', dict(x=180, base=120, w=36, h=70)),
            ('chest', dict(x=8, base=148, w=40, h=20, open_=False)),
            ('figure', dict(x=100, foot=152, h=112, arms=('chest', 'forward'), robe=True, tunic='red', trim='gold', mantle='cloth',
                            head='hat', head_ramp='cloth', props=[(0, ('book', dict(open_=True, w=1.5, h=1.3)), True)])),
            ('bag_on_floor', dict(x=150, base=150)),
        ]),
    'hunter': dict(  # 猟師: 夜の森で弓を引き絞る
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.1, halo=(30, 22, 34, 0.7)),
        env=('forest', dict(hz=124, moon=(30, 22, 9), seed=1)),
        items=[
            ('figure', dict(x=90, foot=152, h=110, arms=('pull', 'aim'), legs='stride', tunic='green', head='hood', head_ramp='green',
                            cloak='leather', legs_ramp='leather', props=[(1, 'bow', True)], behind=[(0, ('quiver', {}))])),
        ]),
    'mercenary': dict(  # 自警団: 町の門で盾を構え、剣を振り上げる
        light=dict(pool=(108, 86), radius=(150, 100), fall=1.15, halo=(18, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag', bw=20, bh=10)),
        items=[
            ('torch', dict(x=16, y=40)),
            ('drawbridge_gate', dict(x=176, base=122, w=52, h=84)),
            ('figure', dict(x=104, foot=152, h=112, arms=('forward', 'raise'), legs='stride', tunic='red', armor=True, head='helm',
                            cloak='cloth', legs_ramp='cloth', props=[(1, ('sword', dict(deg=-75, length=4.2)), True), (0, ('shield', dict(ramp='red')), True)])),
        ]),
    'command': dict(  # 号令: 城壁の上で旗を立て、剣で進む先を示す
        light=dict(pool=(104, 84), radius=(150, 100), fall=1.1, halo=(26, 74, 40, 0.8)),
        env=('battlement', dict(hz=100, moon=None, parapet=(98, 132))),
        items=[
            ('brazier', dict(x=26, base=100)),
            ('figure', dict(x=104, foot=154, h=114, arms=('lift', 'aim'), tunic='blue', armor=True, head='helm', cloak='red', legs_ramp='cloth',
                            props=[(1, ('sword', dict(deg=-25, length=4.4)), True),
                                   (0, ('banner', dict(ramp='blue', deg=-92, length=3.0, flag=(2.6, 2.0))), False)])),
        ]),
    'highwayman': dict(  # 峠の盗賊: 覆面で道をふさぎ、剣を突きつける
        light=dict(pool=(112, 84), radius=(150, 100), fall=1.1, halo=(36, 24, 36, 0.7)),
        env=('pass', dict(hz=124, moon=(40, 28, 10, 0.5))),
        items=[
            ('tree', dict(x=200, base=126, h=74, kind='dead', gain=0.7, seed=5)),
            ('figure', dict(x=122, foot=152, h=112, facing=-1, arms=('down', 'aim'), legs='stride', tunic='cloth', head='hood', head_ramp='cloth',
                            mask='red', cloak='red', legs_ramp='cloth', props=[(1, ('sword', dict(deg=-15, length=3.8)), True), (0, ('bag', {}), True)])),
        ]),
    'sentinel': dict(  # 番兵: 城壁の上でランタンを掲げ、槍を立てる
        light=dict(pool=(100, 76), radius=(140, 100), fall=1.15, halo=(64, 44, 40, 0.8)),
        env=('battlement', dict(hz=100, moon=None, parapet=(96, 132), stars=30)),
        items=[
            ('figure', dict(x=112, foot=154, h=112, arms=('lift', 'low'), tunic='blue', armor=True, head='helm', cloak='cloth', legs_ramp='cloth',
                            props=[(0, ('held_lantern', {}), True)], behind=[(1, ('staff', dict(deg=-92, length=5.6, top='spear', below=2.5)))])),
        ]),
    'sorcerer': dict(  # 呪術師: 紫の光の玉を掲げ、災いを呼ぶ
        light=dict(pool=(96, 74), radius=(130, 95), fall=1.25, halo=(62, 30, 40, 0.8)),
        env=('cave', dict(hz=128, ramp='stone', gain=0.75, seed=9)),
        items=[
            ('wisps', dict(pts=[(160, 40), (190, 80), (40, 90)])),
            ('figure', dict(x=112, foot=152, h=112, arms=('lift', 'forward'), robe=True, tunic='purple', trim='gold', head='hood', head_ramp='purple',
                            props=[(0, ('orb', dict(r=0.9)), True)])),
            ('skull', dict(x=184, y=140, s=1.0)),
            ('wisp_candle', dict(x=30, base=150)),
        ]),
    'craftsman': dict(  # 匠: 膝をつき、鑿と槌で像を彫る
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.15, halo=(26, 44, 40, 0.7)),
        env=('room', dict(wall='plank', hz=116, floor='planks')),
        items=[
            ('lantern', dict(x=26, y=46, hang=0)),
            ('tool_rack', dict(x0=110, x1=220, y=16, tools=('saw', 'hammer', 'pliers', 'saw2'))),
            ('statue', dict(x=164, base=150)),
            ('figure', dict(x=86, foot=152, h=108, arms=((1.0, 0.9, 2.6, 0.7), 'raise'), legs='kneel', tunic='red', apron='leather', head='hair',
                            legs_ramp='cloth', props=[(1, ('hammer', dict(deg=-60, length=2.2)), True), (0, ('chisel', dict(deg=0)), True)], facing=1)),
            ('shavings', dict(pts=[(140, 150), (150, 152), (128, 153)])),
        ]),
    'woodsman': dict(  # 薪割り: 森の切り株で、斧を振りかぶる
        light=dict(pool=(108, 88), radius=(150, 100), fall=1.1, halo=(34, 52, 36, 0.7)),
        env=('forest', dict(hz=124, moon=None, seed=4)),
        items=[
            ('lantern', dict(x=34, y=52, hang=12)),
            ('logs', dict(x=10, base=150, n=3, r=7)),
            ('figure', dict(x=100, foot=150, h=110, arms=('overhead', 'overhead'), tunic='leather', head='cap', head_ramp='green',
                            legs_ramp='green', belt='leather', props=[(1, ('axe', dict(deg=-165, length=2.9)), True)])),
            ('stump', dict(x=160, base=154, r=18, h=12)),
        ]),
    'bursar': dict(  # 会計係: 帳簿を両手で開き、腰に鍵束
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.15, halo=(26, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[
            ('shelf', dict(x0=130, x1=222, y=34)), ('books_row', dict(x0=132, x1=220, base=34, seed=7)),
            ('shelf', dict(x0=130, x1=222, y=70)), ('books_row', dict(x0=132, x1=220, base=70, seed=8)),
            ('candelabra', dict(x=26, base=72, h=22, arms=0)), ('shelf', dict(x0=8, x1=46, y=72)),
            ('figure', dict(x=96, foot=152, h=112, arms=('chest', 'chest'), robe=True, tunic='blue', trim='gold', mantle='leather', head='coif',
                            head_ramp='blue', props=[(1, ('book', dict(open_=True, w=1.7, h=1.4)), True)])),
            ('keyring', dict(x=110, y=96)),
            ('chest', dict(x=156, base=150, w=44, h=22, open_=True, fill='silver')),
        ]),
    'scout': dict(  # 物見: 物見台の手すりから遠眼鏡で遠くを見る
        light=dict(pool=(104, 74), radius=(150, 100), fall=1.1, halo=None),
        env=('night', dict(hz=100, moon=None, stars=60, hills=[(86, 12, 0.4, 0.7, 2), (96, 8, 0.5, 0.55, 6)], ground_gain=0.5)),
        items=[
            ('far_lights', dict(pts=[(150, 104), (170, 108), (186, 103), (60, 110), (196, 112)])),
            ('figure', dict(x=96, foot=158, h=114, arms=('down', 'eye'), tunic='green', cloak='cloth', head='cap', head_ramp='leather',
                            props=[(1, ('spyglass', dict(length=2.3)), True)])),
            ('railing', dict(x0=0, x1=224, top=118, base=160)),
        ]),
    'pickpocket': dict(  # すり: 路地にしゃがみ、盗った財布を手に
        light=dict(pool=(104, 92), radius=(140, 100), fall=1.2, halo=(32, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=120, floor='flag', bw=16, bh=8)),
        items=[
            ('lantern', dict(x=32, y=46, hang=0)),
            ('barrel', dict(x=190, base=126, r=16, h=40, gain=0.8)),
            ('crate', dict(x=8, y=116, w=26, h=24, gain=0.8)),
            ('figure', dict(x=110, foot=152, h=108, arms=('reach', 'chest'), legs='crouch', lean=0.18, tunic='purple', head='hood',
                            head_ramp='cloth', mask='cloth', cloak='cloth', legs_ramp='cloth',
                            props=[(1, ('bag', dict(ramp='red')), True), (0, ('dagger', dict(deg=120)), True)])),
            ('coin', dict(cx=170, cy=150, r=7, metal='gold', stamp='crown')),
            ('coin', dict(cx=182, cy=154, r=6, metal='silver', stamp='tower')),
        ]),
    'explorer': dict(  # 宝探し: 洞窟でランタンを掲げ、地図の先の宝箱を見つける
        light=dict(pool=(100, 82), radius=(150, 100), fall=1.15, halo=(58, 44, 40, 0.8)),
        env=('cave', dict(hz=128, seed=2)),
        items=[
            ('figure', dict(x=84, foot=152, h=112, arms=('lift', 'present'), legs='stride', tunic='leather', cloak='green', head='hat', head_ramp='leather',
                            legs_ramp='cloth', props=[(0, ('held_lantern', {}), True), (1, ('held_map', {}), True)])),
            ('chest', dict(x=142, base=150, w=56, h=26, fill='gold')),
            ('coin', dict(cx=134, cy=152, r=7, metal='gold')), ('coin', dict(cx=210, cy=154, r=6, metal='gold', stamp='star')),
        ]),
    # ================= ルネサンスの「もの」（a_*.png） =================
    'a_chest': dict(  # 千両箱: 鉄の帯と錠前の重い箱
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(30, 48, 40, 0.7)),
        env=('icon', dict(hz=104, wall='stone', cloth='red')),
        items=[
            ('candle', dict(x=30, base=100, h=14, r=3)),
            ('chest', dict(x=58, base=140, w=96, h=50, open_=False, band='silver')),
            ('coin', dict(cx=176, cy=144, r=9, metal='gold')), ('coin', dict(cx=40, cy=148, r=8, metal='gold', stamp='star')),
        ]),
    'a_flag': dict(  # のぼり旗: 夜風に立つ縦長の旗
        light=dict(pool=(112, 76), radius=(140, 110), fall=1.1, halo=(36, 26, 40, 0.7)),
        env=('night', dict(hz=134, moon=(36, 26, 10), hills=[(122, 10, 0.45, 0.6, 3)], ground_gain=0.7)),
        items=[
            ('nobori', dict(x=98, top=14, base=150, w=32, ramp='red')),
        ]),
    'a_horn': dict(  # 法螺貝: 布の上の大きな巻貝と房
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=100, wall='plank', cloth='blue')),
        items=[('conch', dict(x=104, y=104, s=1.25))]),
    'a_key': dict(  # 合鍵: 天鵞絨に置いた真鍮の大きな鍵
        light=dict(pool=(112, 92), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=86, wall='stone', cloth='purple', cloth_gain=0.6)),
        items=[('key', dict(x=116, y=106, s=1.25, ang=-18))]),
    'a_lantern': dict(  # 提灯: 夜の軒先に下がる、骨の見える紙の灯
        light=dict(pool=(100, 70), radius=(140, 100), fall=1.15, halo=(110, 76, 60, 0.35)),
        env=('night', dict(hz=140, moon=None, stars=24, ground_ramp='stone', ground_gain=0.6)),
        items=[
            ('eave', dict(y=0, h=16)),
            ('paper_lantern', dict(x=112, y=80, r=34, ramp='fire', string=16)),
        ]),
}


# 拡張ごとの部品（parts_<拡張>.py）。部品は PARTS に、持ち物は各ファイルの PROPS に入れる
import parts_darkages  # noqa: E402
import parts_adventures  # noqa: E402
import parts_empires  # noqa: E402
import parts_nocturne  # noqa: E402
import parts_renaissance  # noqa: E402

for _mod in (parts_darkages, parts_adventures, parts_empires, parts_nocturne, parts_renaissance):
    PARTS.update({n: f for n, f in vars(_mod).items() if callable(f) and not n.startswith('_') and n not in PARTS and n != 'PROPS'})
    PROPS.update(getattr(_mod, 'PROPS', {}))

import scenes_intrigue  # noqa: E402
import scenes_seaside  # noqa: E402
import scenes_prosperity  # noqa: E402
import scenes_alchemy  # noqa: E402
import scenes_hinterlands  # noqa: E402
import scenes_guilds  # noqa: E402
import scenes_darkages  # noqa: E402
import scenes_adventures  # noqa: E402
import scenes_empires  # noqa: E402
import scenes_nocturne  # noqa: E402
import scenes_renaissance  # noqa: E402

# 拡張ごとの場面の表。build.py と compare_sheet.py は --set でこの名前を受ける
SETS = {'base': SCENES, 'intrigue': scenes_intrigue.SCENES, 'seaside': scenes_seaside.SCENES,
        'prosperity': scenes_prosperity.SCENES, 'alchemy': scenes_alchemy.SCENES,
        'hinterlands': scenes_hinterlands.SCENES, 'guilds': scenes_guilds.SCENES,
        'darkages': scenes_darkages.SCENES, 'adventures': scenes_adventures.SCENES,
        'empires': scenes_empires.SCENES, 'nocturne': scenes_nocturne.SCENES,
        'renaissance': scenes_renaissance.SCENES}
ALL = {k: v for t in SETS.values() for k, v in t.items()}


def render(cid, Canvas):
    s = ALL[cid]
    c = Canvas(Light(**s['light']), cid)
    name, kw = s['env']
    ENVS[name](c, **kw)
    for part, kw in s['items']:
        kw = dict(kw)
        if part == 'figure':
            kw['props'] = [(side, _prop(p), front) for side, p, front in kw.get('props', ())]
            kw['behind'] = [(side, _prop(p)) for side, p in kw.get('behind', ())]
        PARTS[part](c, **kw)
    P.vignette(c, s.get('vignette', 0.5))
    return c
