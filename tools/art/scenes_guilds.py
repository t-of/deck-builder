"""収穫祭＆ギルド（cards-guilds.js）の 48 枚の場面データ。書き方は scenes.py の冒頭を見る。
収穫と市と職人の札なので、夜明けの畑・暖かい工房・雪の里・祭りの夜を散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.75):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


SCENES = {
    # ================= 褒賞・賞品 =================
    'coronet': dict(  # 宝の冠: 開いた宝箱の上で、後光を放つ宝石の冠
        light=dict(pool=(112, 90), radius=(150, 100), fall=1.1),
        env=('icon', dict(hz=118, wall='stone', cloth='purple', cloth_gain=0.6)),
        items=[('light_rays', dict(x=112, y=86, n=11, ln=90)), ('chest', dict(x=70, base=150, w=84, h=30, fill='gold')),
               ('royal_crown', dict(x=112, y=96, w=66, h=40, arches=False))]),
    'courser': dict(  # 駿足の馬: 夜明けの野を駆ける馬
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('horse', dict(x=112, base=148, s=1.5, gallop=True, ramp='leather'))]),
    'demesne': dict(  # 直轄地: 金の旗の城と、見渡す限りの麦畑
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN),
        env=_dawn(hz=100, ground='leather'),
        items=[('castle', dict(x=150, base=96, s=0.55, roof='blue', banner='gold')), ('furrows', dict(y0=108)), ('wheat_sheaves', dict(x=30, base=154, n=4))]),
    'turnip': dict(  # 大かぶ: 畑から抜いた、紫の肩の大きなかぶ
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=120, ground='leather'),
        items=[('furrows', dict(y0=128)), ('turnip', dict(x=112, base=150, r=40)), ('spade_stuck', dict(x=180, base=150))]),
    'renown': dict(  # 誉れ: 月桂冠と、旗を下げたラッパ
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=110, wall='stone', cloth='red', cloth_gain=0.7)),
        items=[('candle', dict(x=26, base=106, h=12, r=3)), ('trumpet', dict(x=40, y=60, ang=-12, ln=150, banner='blue')),
               ('laurel', dict(x=112, y=104, r=34))]),
    'goldbag': dict(  # 金の袋: 金の紐で縛った大袋と、こぼれた金貨
        light=dict(pool=(112, 100), radius=(150, 100), halo=(28, 48, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('money_bag', dict(x=100, base=148, r=36))]),
    'crown': dict(  # 金の冠: 赤い座布団の上の、アーチのある王冠
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=86, wall='stone', cloth='blue', cloth_gain=0.6)),
        items=[('candelabra', dict(x=26, base=84, h=26)), ('cushion', dict(x=112, y=130, w=120, ramp='red')), ('royal_crown', dict(x=112, y=118, w=76, h=50))]),
    'steed': dict(  # 愛馬: 馬着を掛けた騎士の馬、城の中庭
        light=dict(pool=(112, 96), radius=(160, 100), fall=1.1, halo=(16, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=20, bh=10)),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=178, top=0, w=28, h=60, ramp='blue', kind='cross')),
               ('horse', dict(x=112, base=150, s=1.45, blanket='blue'))]),
    'guardsman': dict(  # 近衛兵: 斧槍を立て、羽根の兜で門を守る
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(16, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=20, bh=10)),
        items=[('torch', dict(x=16, y=40)), ('doorway', dict(x=180, base=124, w=40, h=78)),
               ('figure', dict(x=104, foot=154, h=114, arms=('hip', 'low'), tunic='red', trim='gold', armor=True, head='helm', cloak='blue', legs_ramp='paper',
                               behind=[(1, ('halberd', {}))])),
               ('plume', dict(x=104, y=40))]),
    'retinue': dict(  # 取り巻き: 胸を張る主と、後ろに控える家来たち
        light=dict(pool=(108, 88), radius=(160, 100), fall=1.1, halo=(16, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('torch', dict(x=16, y=40)),
               ('figure', dict(x=168, foot=140, h=88, facing=-1, arms=('down', 'down'), tunic='green', head='cap', head_ramp='green', legs_ramp='cloth')),
               ('figure', dict(x=196, foot=146, h=92, facing=-1, arms=('chest', 'down'), tunic='blue', head='hood', head_ramp='blue', legs_ramp='cloth')),
               ('figure', dict(x=100, foot=156, h=116, arms=('hip', 'forward'), robe=True, tunic='red', trim='gold', mantle='purple', head='crown', beard='hair'))]),
    'hime': dict(  # 姫君: 宝冠を戴き、花束を抱く姫
        light=dict(pool=(108, 86), radius=(150, 100), halo=(40, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('window_arch', dict(x=22, y=8, w=40, h=76)), ('chandelier', dict(x=150, y=14, r=22, chain_top=0)),
               ('figure', dict(x=118, foot=154, h=108, arms=('chest', 'belly'), robe=True, gown=True, tunic='purple', trim='gold', head='tiara', hair='gold',
                               props=[(0, 'flowers_held', True)]))]),
    # ================= 物と場所 =================
    'smallvillage': dict(  # 里: 雪の積もる小さな里、灯りの窓
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(40, 70, 40, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp=None, stars=10, clouds=((20, 100, 10), (40, 90, 8)))),
        items=[('house', dict(x=6, base=128, w=56, h=30, roof_h=28, roof='wood', windows=[(10, 9, 9, 10, True)], door=(36, 9, 18))),
               ('house', dict(x=120, base=132, w=60, h=32, roof_h=30, roof='wood', gain=0.9, windows=[(10, 9, 9, 10, True), (38, 9, 9, 10, True)])),
               ('snow_roof', dict(x=6, base=128, w=56, h=30, roof_h=28)), ('snow_roof', dict(x=120, base=132, w=60, h=32, roof_h=30)),
               ('tree', dict(x=204, base=128, h=56, kind='pine', gain=0.6, seed=51)),
               ('snow_ground', dict(y0=126)), ('fence', dict(x0=60, x1=120, base=146, h=12)), ('snow', dict(n=90, seed=5))]),
    'chandler': dict(  # ろうそく屋: 吊るした蝋燭の束、浸し鍋、灯した蝋燭の列
        light=dict(pool=(112, 96), radius=(150, 100), halo=(40, 60, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('candle_rack', dict(x0=40, x1=190, y=16)), ('cauldron', dict(x=60, base=154, r=24, brew='paper')),
               ('table', dict(x0=100, x1=210, top=118, legs_to=156)), ('candle_row', dict(x0=112, x1=200, base=116))]),
    'sideshow': dict(  # 見世物小屋: 怪物の絵看板を掲げた天幕
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(36, 40, 40, 0.6)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.65, stars=30)),
        items=[('paper_lantern', dict(x=30, y=40, r=10, ramp='gold', string=0)),
               ('army_tent', dict(x=124, base=136, w=150, h=96, ramp='paper', stripe='purple')),
               ('painted_banner', dict(x=124, y=60))]),
    'clinic': dict(  # 養生所: 寝台、薬の瓶と湯の椀、窓辺の灯
        light=dict(pool=(112, 104), radius=(150, 100), halo=(36, 44, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=116, floor='planks')),
        items=[('window_arch', dict(x=24, y=10, w=30, h=56)), ('bed', dict(x=130, base=150, w=150)),
               ('table', dict(x0=10, x1=56, top=116, legs_to=150)), ('bottle', dict(x=22, base=116, h=12, r=4, ramp='green')),
               ('mortar', dict(x=42, base=116, r=10)), ('candle', dict(x=196, base=104, h=10, r=3))]),
    'notions': dict(  # 小間物屋: 糸巻き・リボン・釦の並ぶ棚
        light=dict(pool=(112, 86), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=140, floor='planks')),
        items=[('lantern', dict(x=20, y=40, hang=0)), ('spools_shelf', dict(x0=40, x1=206, top=20, base=124)), ('scissors', dict(x=112, y=146))]),
    'redo': dict(  # 作り直し: ろくろの上で壺を挽き直す、割れた欠片
        light=dict(pool=(108, 104), radius=(150, 100), halo=(26, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('shelf', dict(x0=120, x1=220, y=44)),
               ('pots', dict(x=138, base=44, n=3)), ('potter_wheel', dict(x=96, base=146))]),
    'square': dict(  # 市の広場: 泉を囲む屋台、夜明けの広場
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=118, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.75)),
        items=[('house', dict(x=-10, base=116, w=60, h=50, roof_h=22, roof='red', gain=0.7, windows=[(12, 12, 8, 9, True), (36, 12, 8, 9, False)])),
               ('house', dict(x=168, base=116, w=60, h=50, roof_h=22, roof='blue', gain=0.6, windows=[(12, 12, 8, 9, True)])),
               ('stall', dict(x0=14, x1=70, top=96, base=150, colors=('red', 'paper'))), ('stall', dict(x0=156, x1=212, top=96, base=150, colors=('green', 'paper'))),
               ('fountain', dict(x=112, base=152, r=34))]),
    'expo': dict(  # 博覧会: 柱廊の台に並ぶ、珍しい品々
        light=dict(pool=(112, 96), radius=(170, 105), halo=(112, 20, 50, 0.5), **WARM),
        env=('room', dict(wall='stone', hz=128, floor='flag')),
        items=[('chandelier', dict(x=112, y=14, r=30, chain_top=0)),
               ('column', dict(x=20, top=0, base=136, r=8)), ('column', dict(x=204, top=0, base=136, r=8, gain=0.8)),
               ('pedestal', dict(x=60, base=140)), ('pedestal', dict(x=112, base=144)), ('pedestal', dict(x=164, base=140)),
               ('globe', dict(x=60, base=112, r=12)), ('big_gem', dict(x=112, y=104, r=14, ramp='blue')), ('goblet', dict(x=164, base=112, s=1.6))]),
    'cornhorn': dict(  # 実りの角: 編んだ角の籠から、果物とパンと葡萄があふれる
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 48, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('cornucopia', dict(x=124, y=114, s=1.5))]),
    'funfair': dict(  # お祭り: 色の帯を張った五月柱と、提灯の夜
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(30, 40, 40, 0.5)),
        env=('night', dict(hz=134, moon=None, ground_ramp='foliage', ground_gain=0.7, stars=30)),
        items=[('lantern_string', dict(y0=10, y1=26, colors=('red', 'gold', 'blue', 'green', 'purple', 'gold'))),
               ('maypole', dict(x=112, base=146, h=116)), ('confetti', dict(area=(10, 30, 214, 130), n=40, seed=9))]),
    'guildhall': dict(  # 商工会: ギルドの紋章旗を下げた木組みの大きな会館
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=('night', dict(hz=134, moon=None, ground_ramp='stone', ground_gain=0.7, stars=20)),
        items=[('house', dict(x=26, base=140, w=150, h=80, roof_h=40, roof='red', windows=[(18, 14, 12, 14, True), (54, 14, 12, 14, True), (90, 14, 12, 14, True), (126, 14, 12, 14, True)],
                              door=(64, 22, 30))),
               ('hang_banner', dict(x=36, top=66, w=18, h=32, ramp='blue', kind='circle')), ('hang_banner', dict(x=148, top=66, w=18, h=32, ramp='green', kind='chevron')),
               ('sign', dict(x=101, y=58, w=34, h=18, emblem='coin')), ('lamp_post', dict(x=200, base=150, h=60))]),
    'countryside': dict(  # 田舎村: 夜明けの丘の風車と、点在する家
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=122),
        items=[('windmill', dict(x=150, base=120, h=76)), ('house', dict(x=20, base=130, w=44, h=26, roof_h=22, roof='wood', windows=[(8, 8, 8, 9, True)])),
               ('fence', dict(x0=0, x1=110, base=150, h=12)), ('haystack', dict(x=196, base=150, r=18))]),
    'tourney': dict(  # 武芸大会: 縞の天幕、旗、槍を立てた台
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=126, ground='foliage'),
        items=[('pavilion', dict(x=46, base=128, w=64, h=70, ramp='red')), ('pavilion', dict(x=178, base=126, w=60, h=66, ramp='blue')),
               ('lance_rack', dict(x=100, base=146)), ('shield_stand', dict(x=146, base=150)), ('fence', dict(x0=0, x1=224, base=158, h=10))]),
    'reaping': dict(  # 取り入れ: 夜明けの麦畑、刈った束と大鎌
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=112, ground='leather'),
        items=[('wheat_field', dict(y0=104)), ('wheat_sheaves', dict(x=36, base=150, n=3)), ('scythe_lean', dict(x=170, base=152))]),
    'gem': dict(  # 逸品: 台に据えた、多面に切った大きな宝石
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=120, wall='stone', cloth='blue', cloth_gain=0.6)),
        items=[('light_rays', dict(x=112, y=96, n=9, ln=80, ramp='green')), ('big_gem', dict(x=112, y=104, r=40, ramp='green'))]),
    # ================= 人物 =================
    'mason': dict(  # 石切り: 膝をつき、槌と鑿で石を割る
        light=dict(pool=(104, 96), radius=(160, 100), **DAWN),
        env=('night', dict(hz=126, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.75)),
        items=[('block', dict(x=10, y=128, w=36, h=20)), ('block', dict(x=134, y=118, w=50, h=30)),
               ('figure', dict(x=86, foot=152, h=106, arms=((1.0, 0.9, 2.6, 0.9), 'raise'), legs='kneel', tunic='leather', apron='paper', head='cap', head_ramp='paper',
                               legs_ramp='cloth', props=[(1, ('hammer', dict(deg=-60, length=2.2)), True), (0, ('chisel', dict(deg=20)), True)])),
               ('rubble', dict(x=150, base=154, n=6, seed=8))]),
    'shoer': dict(  # 蹄鉄屋: 馬の蹄を持ち上げ、蹄鉄を打つ
        light=dict(pool=(104, 96), radius=(160, 100), halo=(16, 60, 50, 0.7), fall=1.1),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('forge', dict(x=-20, y=50, w=48, h=46)), ('horse', dict(x=146, base=148, s=1.25)),
               ('figure', dict(x=74, foot=152, h=100, arms=('reach', 'raise'), legs='crouch', lean=0.15, tunic='blue', apron='leather', head='hair', legs_ramp='cloth',
                               props=[(0, ('hoof', {}), True), (1, ('hammer', dict(deg=-50, length=2.0)), True)]))]),
    'apprentice': dict(  # 見習い魔女: 箒を手に、三角帽の少女と紫の煙
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=('night', dict(hz=126, moon=(30, 22, 12, 0.3), sky_ramp='purple', ground_ramp='foliage', ground_gain=0.6, stars=30)),
        items=[('wisps', dict(pts=[(170, 50), (60, 80)])),
               ('figure', dict(x=108, foot=154, h=100, arms=('lift', 'belly'), robe=True, tunic='purple', head='witch', head_ramp='cloth', hair='red',
                               props=[(1, 'broom', True), (0, ('orb', dict(r=0.5)), True)])),
               ('cat', dict(x=176, base=154, s=1.0, facing=-1))]),
    'counselor': dict(  # 相談役: 玉座のかたわらで、巻物を手に耳打ちする老臣
        light=dict(pool=(108, 88), radius=(150, 100), halo=(112, 22, 40, 0.5), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('throne', dict(x=160, base=126)),
               ('figure', dict(x=90, foot=154, h=110, arms=('present', 'chest'), lean=0.05, robe=True, tunic='blue', mantle='purple', head='coif', head_ramp='blue',
                               beard='paper', props=[(0, ('scroll', dict(length=1.6)), True)]))]),
    'forerunner': dict(  # 先駆け: 松明を掲げて、夜明け前の道を走る
        light=dict(pool=(104, 88), radius=(170, 110), **DAWN),
        env=('night', dict(hz=116, moon=None, sky_ramp='dawn', stars=0, ground_ramp='sand', ground_gain=0.7)),
        items=[('road', dict(x=150, top=116, base=160, w0=6, w1=130, ramp='sand')),
               ('figure', dict(x=100, foot=154, h=110, arms=('lift', 'pull'), legs='stride', lean=0.16, tunic='green', cloak='red', head='hair', legs_ramp='cloth',
                               props=[(0, 'torch_held', True)]))]),
    'farmhand': dict(  # 作男: 熊手で干し草を上げる、納屋の前
        light=dict(pool=(104, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('house', dict(x=140, base=128, w=80, h=50, roof_h=34, roof='red', windows=[], door=(28, 26, 34), timber=True)),
               ('haystack', dict(x=60, base=150, r=26)),
               ('figure', dict(x=110, foot=154, h=110, arms=('reach', 'lift'), tunic='leather', head='hat', head_ramp='sand', legs_ramp='blue',
                               props=[(1, 'pitchfork', True)]))]),
    'huntparty': dict(  # 猟の一行: 角笛を吹き、猟犬を連れて森へ
        light=dict(pool=(104, 88), radius=(160, 105), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=21)),
        items=[('figure', dict(x=84, foot=152, h=110, arms=('lift', 'low'), tunic='green', cloak='red', head='feather', head_ramp='green', legs_ramp='leather',
                               props=[(0, 'hunting_horn', True)], behind=[(1, ('bow', dict(height=3.6)))])),
               ('dog', dict(x=166, base=156, s=1.4, facing=1))]),
    'clown': dict(  # ひょうきん者: 鈴の帽子の道化が、玉を放る
        light=dict(pool=(108, 86), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=176, top=0, w=26, h=56, ramp='gold', kind='chevron')),
               ('figure', dict(x=108, foot=154, h=110, arms=('raise', 'raise'), legs='stride', tunic='red', mantle='gold', head='jester', legs_ramp='purple',
                               props=[(0, 'juggle', True)]))]),
    'breadmaker': dict(  # パン焼き: 窯から木べらでパンを出す
        light=dict(pool=(104, 92), radius=(150, 100), halo=(30, 80, 50, 0.8), fall=1.1, key=0.8),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('bread_oven', dict(x=0, y=54, w=76, h=70)),
               ('figure', dict(x=128, foot=154, h=110, facing=-1, arms=('present', 'aim'), tunic='paper', apron='paper', head='coif', head_ramp='paper', legs_ramp='cloth',
                               props=[(1, ('peel', {}), True)])),
               ('basket', dict(x=196, base=154, w=34, h=12, kind='bread', n=5))]),
    'meatseller': dict(  # 肉売り: 吊るした腿肉と腸詰、肉切り包丁
        light=dict(pool=(108, 92), radius=(150, 100), halo=(30, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('hanging_meats', dict(x0=10, x1=214, y=12)),
               ('figure', dict(x=110, foot=170, h=118, arms=('present', 'lift'), tunic='red', apron='paper', head='hair', beard='hair',
                               props=[(1, 'cleaver', True)])),
               ('table', dict(x0=20, x1=204, top=128, legs_to=160, front=True)), ('roast', dict(x=80, y=126, s=0.9))]),
    'wanderer': dict(  # 渡り職人: 雪の道を、道具袋を担いで行く
        light=dict(pool=(104, 90), radius=(170, 110), fall=1.05),
        env=('night', dict(hz=118, moon=None, ground_ramp=None, stars=10, clouds=((20, 90, 9), (44, 80, 7)))),
        items=[('tree', dict(x=196, base=124, h=70, kind='pine', gain=0.6, seed=52)), ('tree', dict(x=26, base=120, h=56, kind='pine', gain=0.5, seed=53)),
               ('snow_ground', dict(y0=120)),
               ('figure', dict(x=104, foot=154, h=110, arms=('down', 'lift'), legs='stride', tunic='blue', cloak='leather', head='hood', head_ramp='leather', legs_ramp='cloth',
                               props=[(1, ('bindle', {}), True), (0, ('staff', dict(deg=-95, length=3.4, below=1.4)), False)])),
               ('snow', dict(n=100, seed=7))]),
    'stargazer': dict(  # 星読み: 塔の上で望遠鏡を星座へ向ける
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=None),
        env=('battlement', dict(hz=110, moon=None, parapet=(110, 134), stars=60)),
        items=[('constellation', dict(pts=[(150, 20), (170, 30), (186, 18), (200, 36), (176, 48)])),
               ('telescope', dict(x=160, base=134)),
               ('figure', dict(x=84, foot=154, h=110, arms=('forward', 'chest'), robe=True, tunic='blue', head='witch', head_ramp='blue', beard='paper'))]),
    'ferry': dict(  # 渡し舟: 夜明けの川を、竿で舟を進める船頭
        light=dict(pool=(108, 96), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=100, moon=None, sky_ramp='dawn', stars=0)),
        items=[('reeds', dict(xs=(14, 30, 200), base=118)),
               ('figure', dict(x=104, foot=146, h=104, arms=('chest', 'aim'), tunic='leather', head='hat', head_ramp='sand', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=60, length=4.8, below=1.6)), False)])),
               ('boat', dict(x=112, wl=148, w=150)), ('crate', dict(x=140, y=128, w=22, h=16, gain=0.9))]),
    'mugger': dict(  # 辻強盗: 霧の路地で、短剣を手に飛びかかる
        light=dict(pool=(104, 92), radius=(140, 100), fall=1.2, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)),
               ('figure', dict(x=110, foot=154, h=112, facing=-1, arms=('reach', 'raise'), legs='stride', lean=0.18, tunic='cloth', head='hood', head_ramp='cloth',
                               mask='red', cloak='cloth', legs_ramp='cloth', props=[(1, ('dagger', dict(deg=-60)), True)])),
               ('fog', dict(bands=[(140, 10)], gain=0.7))]),
    'duel': dict(  # 果たし合い: 夜明けの野で、剣を打ち合わせる二人
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('figure', dict(x=62, foot=154, h=108, arms=('down', 'aim'), legs='stride', tunic='blue', cloak='paper', head='hair', legs_ramp='cloth',
                               props=[(1, ('sword', dict(deg=-30, length=4.0)), True)])),
               ('figure', dict(x=164, foot=154, h=108, facing=-1, arms=('down', 'aim'), legs='stride', tunic='red', cloak='cloth', head='hair', hair='paper',
                               legs_ramp='cloth', props=[(1, ('sword', dict(deg=-34, length=4.0)), True)])),
               ('sparks', dict(pts=[(112, 54), (116, 50), (108, 48), (118, 58)]))]),
    'diviner': dict(  # 易者: 卓に筮竹と札を並べ、行く末を占う
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(40, 40, 40, 0.5)),
        env=('room', dict(wall='plank', hz=116, floor='planks')),
        items=[('wisps', dict(pts=[(160, 40)])),
               ('figure', dict(x=112, foot=170, h=118, arms=('present', 'present'), robe=True, tunic='purple', head='turban', head_ramp='purple', beard='paper')),
               ('table', dict(x0=20, x1=204, top=126, legs_to=160, front=True, cloth='purple')),
               ('playing_cards', dict(x=70, y=128)), ('candle', dict(x=40, base=126, h=10, r=3)), ('crystal_ball', dict(x=160, base=130, r=12))]),
    'healer': dict(  # 町医者: 薬の瓶と往診の鞄、寝台のそば
        light=dict(pool=(104, 92), radius=(150, 100), halo=(36, 44, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='planks')),
        items=[('window_arch', dict(x=24, y=10, w=30, h=56)), ('bed', dict(x=170, base=150, w=110)),
               ('figure', dict(x=96, foot=154, h=110, arms=('lift', 'low'), robe=True, tunic='cloth', mantle='red', head='hat', head_ramp='cloth', beard='hair',
                               props=[(0, ('held_bottle', dict(ramp='green')), True), (1, ('bag', dict(ramp='leather')), True)]))]),
    'horsedealer': dict(  # 馬喰: 綱で馬を引き、値を言う
        light=dict(pool=(108, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('fence', dict(x0=0, x1=224, base=134, h=14, gain=0.6)),
               ('horse', dict(x=166, base=150, s=1.25, ramp='leather')),
               ('figure', dict(x=58, foot=154, h=108, arms=('belly', 'forward'), tunic='green', cloak='leather', head='hat', head_ramp='leather', legs_ramp='cloth',
                               props=[(1, ('lead_rope', {}), True)]))]),
    'collector': dict(  # 取り立て屋: 戸口で手を突き出し、証文の束を見せる
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(40, 50, 40, 0.6)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.7)),
        items=[('house', dict(x=130, base=136, w=90, h=70, roof_h=30, roof='wood', windows=[(14, 14, 10, 12, False)], door=(48, 18, 32))),
               ('lantern', dict(x=40, y=64, hang=40)),
               ('figure', dict(x=90, foot=154, h=112, arms=('chest', 'forward'), robe=True, tunic='cloth', trim='gold', mantle='red', head='tophat', head_ramp='cloth',
                               props=[(0, 'letter', True)], behind=[(0, ('bag', {}))]))]),
}
