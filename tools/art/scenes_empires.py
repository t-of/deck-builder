"""帝国（cards-empires.js）の 76 枚の場面データ。書き方は scenes.py の冒頭を見る。
札 29・上下 2 種の山 5・城 8・イベント 13・ランドマーク 21。城と名所の札なので、夜明けの遠景と夕暮れを多めに、
城は 1 枚ずつ荒れ方・飾り・大きさで描き分ける。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


SCENES = {
    # ================= 上下 2 種の山 =================
    'p_settlers': dict(  # 入植者／にぎわう村: 荷車で着いた入植者と、灯のあふれる村
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(40, 70, 40, 0.5)),
        env=_night(moon=None),
        items=[('house', dict(x=110, base=124, w=50, h=32, roof_h=24, roof='red', windows=[(8, 9, 8, 9, True), (32, 9, 8, 9, True)])),
               ('house', dict(x=166, base=128, w=50, h=30, roof_h=22, roof='wood', gain=0.85, windows=[(8, 9, 8, 9, True)])),
               ('lantern_string', dict(y0=40, y1=56, colors=('gold', 'red', 'gold'))), ('wagon', dict(x=56, base=152, w=74))]),
    'p_catapult': dict(  # 石弓／石ころ: 投石機と、その前の石ころの山
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=128),
        items=[('trebuchet', dict(x=96, base=146, s=1.0)), ('pebble_pile', dict(x=176, base=152, w=34))]),
    'p_patrician': dict(  # 名士／大商店: 大商店の前に立つ名士
        light=dict(pool=(104, 92), radius=(170, 105), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=_night(moon=None, ground='stone'),
        items=[('palace', dict(x=150, base=124, w=120, h=46, wings=False)), ('sign', dict(x=150, y=50, w=40, h=16, emblem='coin')),
               ('figure', dict(x=62, foot=154, h=110, arms=('chest', 'low'), robe=True, tunic='paper', trim='gold', mantle='purple', head='hair', face=True,
                               props=[(0, 'letter', True)]))]),
    'p_encampment': dict(  # 野営／戦利の品: 天幕の前に積んだ戦利の箱
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(80, 130, 50, 0.6)),
        env=_night(moon=None, gain=0.5),
        items=[('army_tent', dict(x=150, base=132, w=100, h=70, stripe='red')), ('campfire', dict(x=70, base=150)), ('chest', dict(x=110, base=152, w=50, h=22, fill='gold'))]),
    'p_gladiator': dict(  # 闘士／一財産: 闘技場の砂に立つ闘士と、金の山
        light=dict(pool=(104, 100), radius=(170, 110), **DAWN),
        env=('night', dict(hz=110, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('arena', dict(y0=120)), ('pile', dict(cx=172, base=154, w=36, h=18, metal='gold', r=7, count=14, seed=12)),
               ('figure', dict(x=90, foot=154, h=110, arms=('down', 'lift'), tunic='red', armor=True, head='crest', legs_ramp='leather', props=[(1, 'trident', True)]))]),
    # ================= 札 =================
    'colonist': dict(  # 入植者: 斧と包みで、新しい土地の小屋の前に立つ
        light=dict(pool=(104, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('hut', dict(x=170, base=132, w=56, h=30)), ('stump', dict(x=130, base=154, r=12, h=8, log=False)),
               ('figure', dict(x=80, foot=154, h=110, arms=('down', 'lift'), tunic='leather', cloak='green', head='hat', head_ramp='leather', legs_ramp='cloth',
                               props=[(1, ('bindle', {}), True), (0, ('axe', dict(deg=100, length=2.2)), True)]))]),
    'busyvillage': dict(  # にぎわう村: 提灯と灯の窓、夜の広場の人だかり
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(40, 70, 40, 0.5)),
        env=_night(moon=None, ground='stone'),
        items=[('house', dict(x=-6, base=124, w=60, h=40, roof_h=24, roof='red', windows=[(10, 10, 9, 10, True), (36, 10, 9, 10, True)])),
               ('house', dict(x=160, base=124, w=64, h=44, roof_h=24, roof='wood', windows=[(10, 10, 9, 10, True), (40, 10, 9, 10, True)])),
               ('house', dict(x=70, base=114, w=70, h=34, roof_h=20, roof='red', gain=0.6, windows=[(10, 8, 7, 8, True), (30, 8, 7, 8, True), (50, 8, 7, 8, True)])),
               ('lantern_string', dict(y0=24, y1=40, colors=('red', 'gold', 'blue', 'gold', 'red'))),
               ('figure', dict(x=90, foot=154, h=80, arms=('down', 'raise'), tunic='green', head='cap', head_ramp='red')),
               ('figure', dict(x=140, foot=156, h=84, facing=-1, arms=('belly', 'down'), robe=True, gown=True, tunic='blue', head='long', hair='hair'))]),
    'trebuchet': dict(  # 石弓: 夕暮れの丘に据えた投石機
        light=dict(pool=(112, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=130),
        items=[('trebuchet', dict(x=112, base=148, s=1.3)), ('pebble_pile', dict(x=40, base=154, w=24))]),
    'pebbles': dict(  # 石ころ: 石ころの山のなかに光る銀貨
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1),
        env=_dawn(hz=110, ground='stone'),
        items=[('pebble_pile', dict(x=112, base=150, w=70)), ('coin', dict(cx=124, cy=124, r=11, metal='silver', stamp='tower', tilt=0.7))]),
    'notable': dict(  # 名士: 月桂樹の冠、巻物を持つ衣の人
        light=dict(pool=(104, 86), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('column', dict(x=180, top=0, base=136, r=10)), ('torch', dict(x=16, y=40)),
               ('figure', dict(x=100, foot=154, h=112, arms=('chest', 'present'), robe=True, tunic='paper', trim='gold', mantle='red', head='hair', hair='paper', face=True,
                               props=[(0, 'letter', True)])),
               ('laurel', dict(x=104, y=50, r=9))]),
    'emporium': dict(  # 大商店: 天井まで品の並ぶ大きな店の中
        light=dict(pool=(112, 92), radius=(160, 100), halo=(112, 20, 50, 0.5), **WARM),
        env=('room', dict(wall='plank', hz=130, floor='planks')),
        items=[('chandelier', dict(x=112, y=10, r=24, chain_top=0)), ('spools_shelf', dict(x0=10, x1=100, top=20, base=124)), ('curio_shelf', dict(x0=120, x1=214, top=20, base=124)),
               ('table', dict(x0=40, x1=190, top=130, legs_to=160, front=True, cloth='red')), ('goblet', dict(x=90, base=132, s=1.2)), ('bottle', dict(x=150, base=132, h=12, r=4, ramp='green'))]),
    'bivouac': dict(  # 野営: 星空の下、焚き火を囲む寝床
        light=dict(pool=(112, 108), radius=(150, 100), fall=1.1, halo=(112, 140, 60, 0.7)),
        env=_night(moon=None, gain=0.5, stars=60),
        items=[('army_tent', dict(x=180, base=128, w=70, h=50, stripe='blue')), ('campfire', dict(x=112, base=148)),
               ('bedrolls', dict(pts=[(50, 150, 'red'), (170, 156, 'green')])), ('sword_stuck', dict(x=36, base=140))]),
    'spoil': dict(  # 戦利の品: 兜と盾と金の山
        light=dict(pool=(112, 104), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=110, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('shield_row', dict(x0=40, x1=190, y=50)), ('pile', dict(cx=112, base=152, w=54, h=24, metal='gold', r=9, count=20, seed=13)),
               ('helmet_floor', dict(x=50, base=150)), ('sword_stuck', dict(x=186, base=150))]),
    'fightman': dict(  # 闘士: 闘技場で網と三叉槍を構える
        light=dict(pool=(104, 100), radius=(170, 110), **DAWN),
        env=('night', dict(hz=110, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('arena', dict(y0=120)),
               ('figure', dict(x=108, foot=154, h=112, arms=('low', 'lift'), legs='stride', tunic='red', armor=False, head='crest', legs_ramp='leather',
                               props=[(1, 'trident', True), (0, 'net_held', True)]))]),
    'fortune': dict(  # 一財産: 宝物庫にあふれる金、王冠と宝石
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.0, halo=(26, 38, 50, 0.6), key=0.8),
        env=('room', dict(wall='stone', hz=80, floor='table')),
        items=[('candelabra', dict(x=26, base=78, h=30)),
               ('chest', dict(x=40, base=104, w=60, h=26, fill='gold')), ('chest', dict(x=130, base=100, w=64, h=26, fill='gold')),
               ('pile', dict(cx=112, base=156, w=100, h=40, metal='gold', r=11, count=50, seed=14)),
               ('royal_crown', dict(x=150, y=124, w=40, h=26, arches=False)),
               ('gems', dict(pts=[(60, 138, 5, 'red'), (90, 128, 4, 'blue'), (186, 140, 5, 'green'), (110, 118, 4, 'purple')]))]),
    'castles': dict(  # 城々: 山の上に重なる、大小の城
        light=dict(pool=(112, 80), radius=(180, 120), **DAWN),
        env=_dawn(hz=140, hills=((110, 30, 0.6, 0.4, 3), (130, 16, 0.7, 0.2, 7))),
        items=[('castle', dict(x=60, base=104, s=0.5, roof='red')), ('castle', dict(x=170, base=94, s=0.6, roof='blue')), ('castle', dict(x=112, base=132, s=0.8, roof='red'))]),
    'chariot': dict(  # 馬車競べ: 砂を蹴立てて駆ける二輪の戦車
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=110, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('arena', dict(y0=120)), ('chariot', dict(x=160, base=152)), ('horse', dict(x=78, base=150, s=1.1, gallop=True, ramp='paper'))]),
    'temptress': dict(  # 魔性の女: 紫の灯で、杯を差し出すドレスの女
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(40, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('wisps', dict(pts=[(170, 40), (40, 80)])),
               ('figure', dict(x=110, foot=154, h=112, arms=('belly', 'present'), robe=True, gown=True, tunic='purple', trim='gold', head='long', hair='red', face=True,
                               props=[(1, 'trophy', True)]))]),
    'vegmarket': dict(  # 野菜市: かごに盛った菜、かぶ、人参
        light=dict(pool=(112, 104), radius=(170, 105), **DAWN),
        env=_dawn(hz=112, ground='stone'),
        items=[('stall', dict(x0=24, x1=200, top=56, base=150, colors=('green', 'paper'), counter='crates')),
               ('basket', dict(x=50, base=124, w=30, h=10, kind='cabbage', n=6)), ('basket', dict(x=86, base=124, w=30, h=10, kind='apple', fill='copper', n=8)),
               ('basket', dict(x=122, base=124, w=30, h=10, kind='cabbage', n=5)), ('basket', dict(x=158, base=124, w=30, h=10, kind='apple', fill='red', n=8)),
               ('turnip', dict(x=200, base=154, r=14))]),
    'mechanic': dict(  # 技師: 歯車の機械を、鉄の鍵で締める
        light=dict(pool=(104, 96), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('gears', dict(x=164, y=80)), ('automaton', dict(x=180, base=154, s=1.0)),
               ('figure', dict(x=84, foot=154, h=110, arms=('belly', 'forward'), tunic='blue', apron='leather', head='cap', head_ramp='cloth', legs_ramp='cloth',
                               props=[(1, 'wrench', True)]))]),
    'oblation': dict(  # 捧げ物: 社の火鉢に、膝をついて椀を捧げる
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(150, 100, 60, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('brazier', dict(x=160, base=140)), ('smoke_column', dict(x=160, y=96)),
               ('figure', dict(x=90, foot=152, h=100, arms=('present', 'present'), legs='kneel', lean=0.08, robe=True, tunic='paper', head='hood', head_ramp='paper',
                               props=[(1, 'bowl', True)]))]),
    'shrine': dict(  # お社: 夕暮れの鳥居と、石灯籠の灯
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='stone', hills=((100, 20, 0.5, 0.5, 6),)),
        items=[('tree', dict(x=20, base=124, h=80, kind='pine', gain=0.6, seed=81)), ('tree', dict(x=206, base=124, h=86, kind='pine', gain=0.6, seed=82)),
               ('wayside_shrine', dict(x=112, base=118)), ('torii', dict(x=112, base=152, w=130, h=110))]),
    'villa': dict(  # 別荘: 柱廊のある館と、刈り込んだ庭
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN),
        env=_dawn(hz=120),
        items=[('palace', dict(x=112, base=118, w=150, h=46, wings=True)), ('hedge', dict(x0=0, x1=90, base=140, h=10)), ('hedge', dict(x0=134, x1=224, base=140, h=10)),
               ('topiary', dict(x=40, base=156, h=24)), ('topiary', dict(x=184, base=156, h=24)), ('fountain', dict(x=112, base=158, r=22))]),
    'archivist': dict(  # 書庫番: 梯子の上で、巻物を棚に収める
        light=dict(pool=(108, 90), radius=(150, 100), halo=(30, 60, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=130, floor='planks')),
        items=[('bookcase', dict(x0=0, x1=224, top=0, bottom=130)), ('ladder', dict(x=104, top=20, base=150, w=18)),
               ('figure', dict(x=150, foot=150, h=104, facing=-1, arms=('raise', 'chest'), robe=True, tunic='green', head='coif', head_ramp='green',
                               props=[(1, ('scroll', dict(length=1.2)), True)])), ('candle', dict(x=36, base=152, h=10, r=3))]),
    'principal': dict(  # 元金: 金の山と、赤い字の借金の帳面
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('stack', dict(cx=70, base=146, r=13, n=9, metal='gold', seed=81)),
               ('stack', dict(cx=104, base=150, r=13, n=6, metal='gold', seed=82)), ('doc', dict(x=164, y=124, w=70, h=50)), ('debt_tokens', dict(pts=[(150, 150), (176, 152), (196, 146)]))]),
    'luckycharm': dict(  # 縁起物: 金の蹄鉄と四つ葉
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=110, wall='plank', cloth='green', cloth_gain=0.6)),
        items=[('horseshoe', dict(x=100, y=80, r=30)), ('clover', dict(x=160, y=120, r=16)), ('coin', dict(cx=60, cy=140, r=8, metal='gold'))]),
    'scepter': dict(  # 玉冠: 座布団に載せた宝石の笏
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=86, wall='stone', cloth='blue', cloth_gain=0.6)),
        items=[('candelabra', dict(x=26, base=84, h=26)), ('cushion', dict(x=112, y=130, w=140, ramp='purple')), ('scepter', dict(x0=56, y0=134, x1=166, y1=100))]),
    'meetinghall': dict(  # 寄り合い所: 長椅子の並ぶ板の間と、正面の演台
        light=dict(pool=(112, 92), radius=(160, 100), halo=(112, 30, 40, 0.5), **WARM),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('hang_banner', dict(x=96, top=0, w=32, h=60, ramp='blue', kind='circle')),
               ('figure', dict(x=112, foot=128, h=92, arms=('chest', 'raise'), robe=True, tunic='blue', mantle='gold', head='hat', head_ramp='cloth', beard='paper')),
               ('lectern', dict(x=112, base=132, h=24)), ('benches', dict(y0=136)),
               ('figure', dict(x=40, foot=170, h=96, facing=1, arms=('belly', 'chest'), tunic='green', head='cap', head_ramp='green')),
               ('figure', dict(x=186, foot=172, h=96, facing=-1, arms=('belly', 'raise'), tunic='red', head='hair'))]),
    'gardener': dict(  # 植木屋: 鋏で生垣の形を整える
        light=dict(pool=(104, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=118),
        items=[('topiary', dict(x=166, base=152, h=60)), ('hedge', dict(x0=0, x1=224, base=128, h=14)),
               ('figure', dict(x=90, foot=154, h=108, arms=('belly', 'aim'), tunic='green', apron='leather', head='hat', head_ramp='sand', legs_ramp='cloth', props=[(1, 'shears', True)]))]),
    'hoplite': dict(  # 重装兵: 鶏冠の兜、円い盾と長槍
        light=dict(pool=(104, 88), radius=(170, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('figure', dict(x=108, foot=154, h=114, arms=('forward', 'aim'), legs='stride', tunic='red', armor=True, head='crest', cloak='red', legs_ramp='leather',
                               props=[(0, ('round_shield', {}), True), (1, ('staff', dict(deg=-10, length=4.2, top='spear', below=2.4)), True)]))]),
    'wildchase': dict(  # 狩り立て: 森を逃げる鹿と、追う猟犬
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=51)),
        items=[('deer', dict(x=150, base=148, s=1.4, facing=1)), ('dog', dict(x=60, base=156, s=1.3, facing=1)), ('dog', dict(x=20, base=150, s=1.0, facing=1, ramp='paper'))]),
    'townblock': dict(  # 町並み: 背の高い家が隙間なく並ぶ一画
        light=dict(pool=(112, 96), radius=(170, 105), **DAWN),
        env=_dawn(hz=134, ground='stone'),
        items=[('house', dict(x=-4, base=140, w=46, h=90, roof_h=18, roof='red', windows=[(8, 12, 7, 9, True), (26, 12, 7, 9, False), (8, 40, 7, 9, True), (26, 64, 7, 9, True)])),
               ('house', dict(x=42, base=140, w=44, h=80, roof_h=16, roof='blue', gain=0.85, windows=[(8, 12, 7, 9, False), (26, 36, 7, 9, True), (8, 58, 7, 9, True)])),
               ('house', dict(x=88, base=140, w=48, h=96, roof_h=18, roof='red', windows=[(8, 14, 7, 9, True), (28, 14, 7, 9, True), (8, 46, 7, 9, False), (28, 72, 7, 9, True)])),
               ('house', dict(x=138, base=140, w=44, h=84, roof_h=16, roof='wood', gain=0.8, windows=[(8, 12, 7, 9, True), (26, 44, 7, 9, True)])),
               ('house', dict(x=184, base=140, w=46, h=92, roof_h=18, roof='blue', gain=0.7, windows=[(8, 14, 7, 9, True), (26, 50, 7, 9, False)]))]),
    'overking': dict(  # 覇王: 玉座に座す、王冠のひげの王
        light=dict(pool=(112, 84), radius=(150, 100), halo=(112, 20, 60, 0.4), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('carpet', dict(x=112, top=124, base=160, w0=40, w1=110)), ('throne', dict(x=112, base=132)),
               ('figure', dict(x=112, foot=148, h=108, arms=('present', 'low'), robe=True, tunic='red', trim='gold', mantle='purple', head='crown', beard='hair', face=True,
                               props=[(1, ('staff', dict(deg=-92, length=3.4, below=1.0, top='knob')), True)])),
               ('column', dict(x=20, top=0, base=136, r=9)), ('column', dict(x=204, top=0, base=136, r=9, gain=0.8))]),
    'royalsmith': dict(  # 御用鍛冶: 王家の旗の下、金床で槌を振るう
        light=dict(pool=(104, 96), radius=(150, 100), halo=(16, 70, 50, 0.8), fall=1.1, key=0.8),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('forge', dict(x=-20, y=50, w=50, h=50)), ('hang_banner', dict(x=176, top=0, w=28, h=60, ramp='purple', kind='circle')),
               ('anvil', dict(x=150, base=152, s=1.2)), ('hot_bar', dict(x0=132, x1=160, y=118)),
               ('figure', dict(x=84, foot=154, h=110, arms=('belly', 'raise'), tunic='red', apron='leather', head='hair', beard='hair', legs_ramp='cloth',
                               props=[(1, ('hammer', dict(deg=-40, length=2.2)), True)]))]),
    # ================= 城 8 種 =================
    'c_humble': dict(  # あばら城: 屋根の落ちた、小さな石の塔ひとつ
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('tower', dict(x=88, base=136, w=40, h=70, roof=None, crenel=True, windows=[(-2, 22, 5, 8)])), ('rubble', dict(x=120, base=146, n=8, seed=31)),
               ('fence', dict(x0=120, x1=200, base=146, h=12, gain=0.6))]),
    'c_crumbling': dict(  # 朽ちた城: 蔦の這う、崩れかけた城壁
        light=dict(pool=(112, 92), radius=(170, 110), fall=1.05),
        env=_night(moon=(36, 24, 10, 0.4)),
        items=[('ruin_wall', dict(x0=30, x1=200, base=134)), ('tower', dict(x=150, base=134, w=36, h=80, roof=None, crenel=True)), ('ivy', dict(x0=30, x1=200, top=70, base=134))]),
    'c_small': dict(  # こぢんまり城: 小さくまとまった、旗の立つ城
        light=dict(pool=(112, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('castle', dict(x=112, base=124, s=0.75, roof='blue', banner='red'))]),
    'c_haunted': dict(  # 亡霊の城: 紫の夜に、亡霊の舞う城
        light=dict(pool=(112, 90), radius=(160, 105), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=('night', dict(hz=124, moon=(40, 30, 14), sky_ramp='purple', ground_ramp='stone', ground_gain=0.5, stars=20)),
        items=[('castle', dict(x=120, base=120, s=0.9, roof='purple', banner='paper')), ('ghosts', dict(pts=[(60, 70), (180, 54), (150, 96)])),
               ('tree', dict(x=26, base=128, h=70, kind='dead', ramp='cloth', gain=0.6, seed=83))]),
    'c_opulent': dict(  # きらびやか城: 金の屋根と、灯のあふれる窓
        light=dict(pool=(112, 86), radius=(170, 110), fall=1.0),
        env=_night(moon=None, gain=0.6),
        items=[('castle', dict(x=112, base=124, s=1.0, roof='gold', banner='purple')), ('lantern_string', dict(y0=10, y1=22, colors=('gold', 'gold', 'gold')))]),
    'c_sprawling': dict(  # だだっ広い城: 横に長く広がる城壁と塔の列
        light=dict(pool=(112, 90), radius=(190, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('wall', dict(x0=0, x1=224, top=90, bottom=130, merlon=8, gap=6)),
               ('tower', dict(x=4, base=130, w=26, h=66, roof='red')), ('tower', dict(x=60, base=130, w=26, h=58, roof='red', gain=0.9)),
               ('tower', dict(x=120, base=130, w=30, h=76, roof='red', windows=[(-2, 26, 4, 7)])), ('tower', dict(x=176, base=130, w=26, h=60, roof='red', gain=0.85))]),
    'c_grand': dict(  # 堂々たる城: 丘を覆う、大きな天守と塔
        light=dict(pool=(112, 80), radius=(180, 110), **DAWN),
        env=_dawn(hz=140, hills=((120, 20, 0.6, 0.3, 4),)),
        items=[('castle', dict(x=112, base=126, s=1.25, roof='blue', banner='gold'))]),
    'c_king': dict(  # 王の城: 王冠の旗を掲げた、夜明けの大城
        light=dict(pool=(112, 76), radius=(180, 120), **DAWN),
        env=_dawn(hz=140, hills=((122, 24, 0.6, 0.3, 5),)),
        items=[('light_rays', dict(x=112, y=30, n=13, ln=110)), ('castle', dict(x=112, base=126, s=1.3, roof='red', banner='gold')),
               ('royal_crown', dict(x=112, y=24, w=26, h=16, arches=False))]),
    # ================= イベント =================
    'e_promote': dict(  # 出世: 跪く者の肩に、王が剣を当てる
        light=dict(pool=(112, 90), radius=(160, 100), halo=(112, 20, 60, 0.4), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('hang_banner', dict(x=20, top=0, w=28, h=60, ramp='red', kind='circle')),
               ('figure', dict(x=150, foot=154, h=112, facing=-1, arms=('down', 'aim'), robe=True, tunic='red', mantle='purple', head='crown', beard='hair', face=True,
                               props=[(1, ('sword', dict(deg=20, length=3.8)), True)])),
               ('figure', dict(x=70, foot=154, h=100, arms=('chest', 'chest'), legs='kneel', tunic='blue', armor=True, head='hair', legs_ramp='silver'))]),
    'e_dig': dict(  # 掘り下げ: 掘った穴の底に光る銀
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=110, ground='leather'),
        items=[('dug_hole', dict(x=104, y=138)), ('coin', dict(cx=100, cy=138, r=9, metal='silver', stamp='tower')), ('spade_stuck', dict(x=170, base=146))]),
    'e_levy': dict(  # 年貢: 卓の銭の山ごとに置かれた、赤い借金の札
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=92, floor='table')),
        items=[('candle', dict(x=28, base=90, h=12, r=3)), ('book', dict(x=150, y=110, w=50, h=4, t=12, ramp='red')),
               ('stack', dict(cx=50, base=146, r=10, n=4, metal='copper', stamp='pip', seed=83)), ('stack', dict(cx=96, base=148, r=10, n=5, metal='silver', stamp='tower', seed=84)),
               ('stack', dict(cx=140, base=150, r=10, n=3, metal='gold', seed=85)), ('debt_tokens', dict(pts=[(52, 118), (98, 112), (142, 128), (182, 146)]))]),
    'e_feast': dict(  # 祝い膳: 野の卓に並ぶ料理と銅貨
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=96, ground='foliage'),
        items=[('table', dict(x0=10, x1=214, top=114, legs_to=158, cloth='red')), ('roast', dict(x=112, y=108, s=1.2)), ('goblet', dict(x=50, base=112, s=1.2)),
               ('basket', dict(x=180, base=112, w=28, h=10, kind='bread', n=4)), ('coin', dict(cx=80, cy=112, r=6, metal='copper', stamp='pip')), ('coin', dict(cx=150, cy=114, r=6, metal='copper', stamp='star'))]),
    'e_marriage': dict(  # 祝言: 花のアーチの下に並ぶ二人
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('flower_arch', dict(x=112, base=152)),
               ('figure', dict(x=90, foot=154, h=104, arms=('down', 'belly'), tunic='blue', trim='gold', cloak='blue', head='hair', legs_ramp='paper')),
               ('figure', dict(x=134, foot=154, h=98, facing=-1, arms=('down', 'belly'), robe=True, gown=True, tunic='paper', trim='gold', head='tiara', hair='gold',
                               props=[(1, 'flowers_held', True)]))]),
    'e_rite': dict(  # 祭祀: 蝋燭の輪の中で、紫の災いが立ちのぼる
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 120, 50, 0.4)),
        env=('room', dict(wall='stone', hz=100, floor='flag')),
        items=[('rune_circle', dict(x=112, y=130, rx=86, ry=20, ramp='purple')), ('candle_ring', dict(x=112, y=130)), ('wisps', dict(pts=[(112, 100), (90, 90), (134, 94)])),
               ('skull', dict(x=112, y=128, s=1.2))]),
    'e_scorch': dict(  # 焦土: 燃え広がる畑と、黒い煙
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.05, halo=(112, 120, 80, 0.6)),
        env=('night', dict(hz=110, moon=None, ground_ramp='leather', ground_gain=0.5, stars=0, clouds=((20, 110, 12),))),
        items=[('furrows', dict(y0=118)), ('fire_line', dict(y=120)), ('smoke_column', dict(x=60, y=100, h=80)), ('smoke_column', dict(x=170, y=96, h=80)),
               ('ruined_house', dict(x=150, base=116, w=50, h=28, gain=0.5))]),
    'e_luck': dict(  # 思わぬ幸運: 草むらに落ちていた金貨 3 枚と四つ葉
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=96, ground='foliage', gain=0.8),
        items=[('coin', dict(cx=80, cy=130, r=14, metal='gold', stamp='crown')), ('coin', dict(cx=120, cy=140, r=14, metal='gold', stamp='star')),
               ('coin', dict(cx=160, cy=128, r=14, metal='gold', stamp='tower')), ('clover', dict(x=50, y=146, r=12)), ('flowers', dict(rows=[(112, 3.0, 26)]))]),
    'e_warcry': dict(  # 勝ちどき: 旗の下で剣を突き上げ、声を上げる兵
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('figure', dict(x=50, foot=148, h=96, arms=('down', 'raise'), tunic='blue', armor=True, head='helm', props=[(1, ('sword', dict(deg=-88, length=3.4)), True)])),
               ('figure', dict(x=170, foot=148, h=96, facing=-1, arms=('down', 'raise'), tunic='green', armor=True, head='helm', props=[(1, ('staff', dict(deg=-92, length=4.0, top='spear', below=1.6)), True)])),
               ('figure', dict(x=112, foot=156, h=112, arms=('raise', 'raise'), tunic='red', armor=True, head='crest', cloak='red', face=True,
                               props=[(1, ('sword', dict(deg=-90, length=3.8)), True), (0, ('banner', dict(ramp='red', deg=-92, length=3.0, flag=(2.0, 1.6))), True)]))]),
    'e_subdue': dict(  # 平定: 落とした砦に旗を立てる騎士
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='stone'),
        items=[('ruin_wall', dict(x0=120, x1=224, base=130)),
               ('figure', dict(x=90, foot=154, h=110, arms=('lift', 'low'), tunic='blue', armor=True, head='helm', cloak='blue', legs_ramp='silver',
                               props=[(0, ('banner', dict(ramp='blue', deg=-92, length=4.0, flag=(2.4, 1.8))), True)])),
               ('stack', dict(cx=180, base=152, r=9, n=4, metal='silver', stamp='tower', seed=86))]),
    'e_absorb': dict(  # 取り込み: 卓の上で、紫の渦が札を呑み込む
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1),
        env=('room', dict(wall='stone', hz=100, floor='table', floor_ramp='purple', floor_gain=0.6)),
        items=[('vortex', dict(x=112, y=124, r=80)), ('pages', dict(pts=[(60, 110), (170, 120), (140, 146), (80, 140)]))]),
    'e_alms2': dict(  # 喜捨: 僧が、物乞いの椀にパンを入れる
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('lantern', dict(x=26, y=44, hang=0)),
               ('figure', dict(x=150, foot=154, h=110, facing=-1, arms=('down', 'present'), robe=True, tunic='leather', head='hood', head_ramp='leather', face=True,
                               props=[(1, ('peel', {}), False)])),
               ('figure', dict(x=70, foot=154, h=96, arms=('present', 'chest'), legs='crouch', tunic='cloth', head='hood', head_ramp='cloth', props=[(0, 'bowl', True)]))]),
    'e_unify': dict(  # 天下統一: 壁の国の地図を、ひとつの旗が覆う
        light=dict(pool=(112, 90), radius=(160, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=140, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('wall_map', dict(x0=40, y0=14, x1=200, y1=120)), ('banner_pole', dict(x=150, base=136)),
               ('royal_crown', dict(x=100, y=134, w=30, h=20, arches=False))]),
    # ================= ランドマーク =================
    'l_canal': dict(  # 用水路: 石の岸の間を流れる水と、木の水門
        light=dict(pool=(112, 110), radius=(170, 110), **DAWN),
        env=_dawn(hz=96),
        items=[('lock_canal', dict(y0=96)), ('house', dict(x=0, base=96, w=40, h=22, roof_h=16, roof='red', gain=0.6, windows=[(8, 6, 6, 6, True)]))]),
    'l_ring': dict(  # 土俵: 吊り屋根の下の、俵の輪
        light=dict(pool=(112, 104), radius=(150, 100), halo=(112, 30, 40, 0.5), **WARM),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('dohyo', dict(x=112, base=152, w=170))]),
    'l_banditden': dict(  # 賊の隠れ里: 岩陰の松明と、粗末な小屋
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(40, 60, 40, 0.6)),
        env=('cave', dict(hz=130, seed=55)),
        items=[('torch', dict(x=40, y=60)), ('shack', dict(x=130, base=136, w=100, h=56)), ('campfire', dict(x=60, base=154, s=0.8)), ('poster', dict(x=196, y=80))]),
    'l_hall': dict(  # 会所: 提灯を下げた、木組みの集会の館
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(60, 70, 40, 0.5)),
        env=_night(moon=None, ground='stone'),
        items=[('house', dict(x=22, base=140, w=160, h=70, roof_h=36, roof='wood', windows=[(18, 14, 12, 14, True), (60, 14, 12, 14, True), (102, 14, 12, 14, True), (140, 14, 12, 14, True)], door=(70, 22, 30))),
               ('paper_lantern', dict(x=60, y=104, r=8, ramp='red', string=86)), ('paper_lantern', dict(x=146, y=104, r=8, ramp='red', string=86))]),
    'l_bathhouse': dict(  # 湯屋: 暖簾の下の湯船から立つ湯気
        light=dict(pool=(112, 100), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('noren', dict(x0=40, x1=184, y=0, ramp='blue')), ('wood_tub', dict(x=112, base=150, w=150, h=30)), ('steam', dict(pts=[(70, 110), (112, 104), (154, 110)])),
               ('lantern', dict(x=20, y=50, hang=26))]),
    'l_battleground': dict(  # 古戦場: 夕暮れの野に刺さったままの剣と槍、倒れた旗
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=110, ground='leather'),
        items=[('battlefield', dict(y0=104)), ('raven', dict(x=150, y=100, s=1.2, facing=-1))]),
    'l_arcade': dict(  # 回廊: 奥へ続く列柱とアーチ
        light=dict(pool=(112, 96), radius=(160, 105), **DAWN),
        env=('room', dict(wall='stone', hz=140, floor='flag')),
        items=[('arcade_arches', dict(x0=0, x1=224, top=20, base=150, n=5))]),
    'l_ruinedtemple': dict(  # 荒れ寺: 草に覆われた、屋根の崩れた堂
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05),
        env=_night(moon=(36, 24, 11, 0.4)),
        items=[('palace', dict(x=112, base=128, w=110, h=50, wings=False, lit=False, gain=0.75)), ('broken_column', dict(x=40, base=140, h=60, r=8)),
               ('ivy', dict(x0=60, x1=170, top=80, base=128)), ('weeds', dict(x=112, base=152, n=12, h=20))]),
    'l_fountain': dict(  # 泉水: 広場の大きな泉、底の銅貨
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=104, ground='stone'),
        items=[('fountain', dict(x=112, base=150, r=60)), ('stack', dict(cx=30, base=152, r=8, n=4, metal='copper', stamp='pip', seed=87))]),
    'l_donjon': dict(  # 天守: 夜明けの空に高くそびえる天守の塔
        light=dict(pool=(112, 80), radius=(170, 110), **DAWN),
        env=_dawn(hz=140, hills=((128, 14, 0.6, 0.3, 4),)),
        items=[('tower', dict(x=82, base=146, w=60, h=130, roof='blue', roof_h=34, windows=[(-3, 30, 6, 10), (-3, 60, 6, 10), (-3, 90, 6, 10)])),
               ('wall', dict(x0=0, x1=224, top=126, bottom=150, merlon=8, gap=6))]),
    'l_maze': dict(  # 迷路: 生垣の迷路を見下ろす
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=60, ground=None),
        items=[('hedge_maze', dict(x0=10, y0=62, x1=214, y1=156))]),
    'l_pass': dict(  # 関所越え: 山あいの道をふさぐ関の門
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=('pass', dict(hz=128, moon=None)),
        items=[('road', dict(x=112, top=110, base=160, w0=12, w1=90, ramp='stone')), ('great_gate', dict(x=112, base=136, w=130, h=90))]),
    'l_treasury': dict(  # 宝物殿: 柱の間に並ぶ宝箱
        light=dict(pool=(112, 100), radius=(170, 105), halo=(112, 20, 60, 0.4), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('column', dict(x=20, top=0, base=136, r=9)), ('column', dict(x=204, top=0, base=136, r=9, gain=0.8)),
               ('chest', dict(x=40, base=134, w=40, h=20, fill='gold')), ('chest', dict(x=96, base=132, w=40, h=20, fill='silver')), ('chest', dict(x=150, base=134, w=40, h=20, fill='copper')),
               ('chest', dict(x=60, base=158, w=46, h=22, open_=False, band='gold')), ('chest', dict(x=130, base=158, w=46, h=22, open_=False, band='silver'))]),
    'l_pillar': dict(  # 石柱: 夜明けの丘に立つ、一本の高い石柱
        light=dict(pool=(112, 80), radius=(170, 110), **DAWN),
        env=_dawn(hz=130),
        items=[('obelisk', dict(x=112, base=148, w=30, h=120))]),
    'l_fruitfield': dict(  # 果物畑: 実のなる木の並ぶ果樹園
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=110),
        items=[('fruit_tree', dict(x=40, base=124, h=60, fruit='red')), ('fruit_tree', dict(x=112, base=120, h=56, fruit='gold')), ('fruit_tree', dict(x=184, base=124, h=60, fruit='red')),
               ('fruit_tree', dict(x=76, base=152, h=76, fruit='gold')), ('fruit_tree', dict(x=156, base=154, h=80, fruit='red')), ('basket', dict(x=112, base=156, w=30, h=10, kind='apple', fill='red', n=8))]),
    'l_palace': dict(  # 御殿: 夕暮れに灯のともる、両翼の御殿
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN),
        env=_dawn(hz=130, ground='stone'),
        items=[('palace', dict(x=112, base=126, w=210, h=64, wings=True)), ('carpet', dict(x=112, top=130, base=160, w0=20, w1=80, ramp='stone'))]),
    'l_mound': dict(  # 塚: 草の盛り土と石の入口
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05),
        env=_night(moon=(36, 24, 11), gain=0.55),
        items=[('burial_mound', dict(x=112, base=146, w=190, h=60)), ('standing_stone', dict(x=24, base=150, w=18, h=40, rune=False)),
               ('standing_stone', dict(x=200, base=150, w=18, h=36, rune=False))]),
    'l_tower': dict(  # 高楼: 反った屋根の重なる高い楼閣
        light=dict(pool=(112, 80), radius=(170, 110), **DAWN),
        env=_dawn(hz=146, ground='stone'),
        items=[('pagoda', dict(x=112, base=154, levels=4, w=70)), ('tree', dict(x=24, base=150, h=70, kind='pine', gain=0.6, seed=84))]),
    'l_gate': dict(  # 大門: 二重の屋根と大きな扉、門の提灯
        light=dict(pool=(112, 96), radius=(170, 105), **DAWN),
        env=_dawn(hz=144, ground='stone'),
        items=[('great_gate', dict(x=112, base=152, w=190, h=130))]),
    'l_wall': dict(  # 城壁: 地平まで続く長い城壁
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=120, hills=((110, 20, 0.6, 0.4, 2),)),
        items=[('long_wall', dict(y_top=60, y_base=150))]),
    'l_lair': dict(  # 獣の巣: 骨の散らばる洞の奥に光る目
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.15),
        env=('cave', dict(hz=134, seed=57)),
        items=[('cave_mouth', dict(x=112, base=134, w=130, h=100)), ('beast_eyes', dict(x=112, y=80)), ('skull', dict(x=60, y=146, s=1.0)),
               ('bones', dict(pts=[(100, 152), (150, 148), (176, 156)]))]),
}
