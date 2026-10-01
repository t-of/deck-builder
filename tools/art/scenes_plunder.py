"""略奪（cards-plunder.js）の 71 枚の場面データ。書き方は scenes.py の冒頭を見る。
王国 40・戦利品の山と戦利品 15・イベント 15。海賊と宝の札なので、戦利品は布や砂の上の 1 品を大きく、
王国は船・港・島・洞窟で場所を散らし、夜の海ばかりにならないよう夜明けの浜と船倉の灯を混ぜる。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


def _sea_dawn(hz=96, shore=None):
    return ('coast', dict(hz=hz, shore=shore, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),)))


def _icon(cloth='red', wall='stone', hz=104, gain=0.7):
    return ('icon', dict(hz=hz, wall=wall, cloth=cloth, cloth_gain=gain))


ICON = dict(pool=(112, 98), radius=(150, 100), fall=1.15, halo=(28, 50, 40, 0.6))
HOLD = ('room', dict(wall='plank', hz=124, floor='planks'))  # 船倉

SCENES = {
    # ================= 戦利品 =================
    'loot': dict(  # 戦利品の山: 宝箱からあふれる壺・盃・宝石・刀
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(30, 50, 40, 0.6), key=0.85),
        env=('cave', dict(hz=126, seed=21)),
        items=[('wall_torch', dict(x=24, y=50)), ('amphora', dict(x=184, base=150, s=0.8)), ('chest', dict(x=60, base=146, w=90, h=36, fill='gold')),
               ('half_gold_goblet', dict(x=40, base=154, s=1.6)), ('katana_flat', dict(x=112, y=152)), ('jewel_heap', dict(x=140, base=158, w=60, n=12, seed=3))]),
    'l_amphora': dict(  # 壺: 砂の上の、帯の絵のある素焼きの壺
        light=dict(**ICON), env=_icon('green', 'plank'),
        items=[('candle', dict(x=28, base=100, h=12, r=3)), ('amphora', dict(x=112, base=150, s=1.3))]),
    'l_doubloons': dict(  # 大金貨: 布の上に立てた大きな金貨と、散らばる金貨
        light=dict(**ICON, key=0.85), env=_icon('blue'),
        items=[('coin', dict(cx=112, cy=100, r=40, metal='gold', stamp='crown', tilt=0.95)), ('stack', dict(cx=44, base=150, r=13, n=6, metal='gold', seed=41)),
               ('coin', dict(cx=176, cy=146, r=14, metal='gold', stamp='star', tilt=0.5)), ('coin', dict(cx=150, cy=154, r=11, metal='gold', tilt=0.45))]),
    'l_chalice': dict(  # 尽きない盃: 光をこぼし続ける、宝石の金の盃
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(112, 70, 50, 0.5)), env=_icon('purple', hz=110),
        items=[('light_rays', dict(x=112, y=84, n=11, ln=60)), ('goblet', dict(x=112, base=154, s=7.0, ramp='gold')), ('sparks', dict(pts=[(96, 70), (130, 64), (112, 56)]))]),
    'l_figurehead': dict(  # 船首の像: 舳先に据えた、髪をなびかせる女の木像
        light=dict(pool=(104, 90), radius=(160, 105), **DAWN), env=_sea_dawn(hz=110),
        items=[('figurehead', dict(x=96, y=70, s=1.4))]),
    'l_hammer': dict(  # 金槌: 金床に置いた、金の頭の大きな槌
        light=dict(**ICON), env=('room', dict(wall='stone', hz=104, floor='flag')),
        items=[('wall_torch', dict(x=20, y=40)), ('anvil', dict(x=150, base=154, s=1.0)), ('big_hammer', dict(x=50, y=148, ang=-40, ln=110)), ('sparks', dict(pts=[(150, 108), (170, 102)]))]),
    'l_insignia': dict(  # 記章: 天鵞絨の上の、綬の付いた金の星の章
        light=dict(**ICON), env=_icon('purple', hz=96, gain=0.6),
        items=[('insignia', dict(x=112, y=92, r=34))]),
    'l_jewels': dict(  # 宝石類: 布の上に盛った色とりどりの宝石
        light=dict(**ICON, key=0.85), env=_icon('blue', 'plank'),
        items=[('candle', dict(x=28, base=100, h=12, r=3)), ('jewel_heap', dict(x=112, base=150, w=150, n=34, seed=7)), ('necklace', dict(x=180, y=118))]),
    'l_orb': dict(  # 宝の珠: 十字を頂く金の宝珠
        light=dict(**ICON), env=_icon('red'),
        items=[('cushion', dict(x=112, y=140, w=110, ramp='red')), ('royal_orb', dict(x=112, base=134, r=32))]),
    'l_goat': dict(  # 褒美の山羊: 金の鈴と赤い布を掛けられた白い山羊
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN), env=_dawn(hz=126),
        items=[('goat', dict(x=112, base=152, s=2.0, facing=-1)), ('pavilion', dict(x=196, base=128, w=40, h=40, ramp='red'))]),
    'l_puzzlebox': dict(  # からくり箱: 寄木細工の箱と、半ば開いた引き出し
        light=dict(**ICON), env=_icon('green', 'plank'),
        items=[('candle', dict(x=28, base=100, h=12, r=3)), ('puzzle_box', dict(x=104, base=146, w=110, h=56))]),
    'l_sextant': dict(  # 測角器: 海図の上の真鍮の測角器
        light=dict(**ICON), env=('room', dict(wall='plank', hz=64, floor='table')),
        items=[('sea_chart', dict(x=112, y=122, w=190, h=60)), ('sextant', dict(x=112, y=52, s=1.1))]),
    'l_shield': dict(  # 大盾: 壁に立てかけた、鉄の縁の大きな盾
        light=dict(**ICON), env=('room', dict(wall='stone', hz=130, floor='flag')),
        items=[('wall_torch', dict(x=20, y=40)), ('kite_shield', dict(x=112, y=86, s=1.35, ramp='blue'))]),
    'l_scroll': dict(  # まじないの巻物: 闇に浮かんで光る、封の解けた巻物
        light=dict(pool=(112, 90), radius=(140, 100), fall=1.15, halo=(112, 80, 50, 0.5)), env=_icon('purple', hz=118, gain=0.5),
        items=[('rune_circle', dict(x=112, y=140, rx=70, ry=10, ramp='purple')), ('big_scroll', dict(x=112, y=86, w=120, h=64))]),
    'l_staff': dict(  # 仕込み杖: 漆の鞘から白刃がのぞく杖
        light=dict(**ICON), env=_icon('red', 'plank', hz=96),
        items=[('sword_cane', dict(x=24, y=144, ang=-26, ln=196, r=1.8))]),
    'l_sword': dict(  # 刀: 刀掛けに置いた、抜き身の刀と鞘
        light=dict(**ICON), env=_icon('blue', 'plank', hz=96),
        items=[('big_katana', dict(x=24, y=118, ang=-14, ln=190))]),
    # ================= 王国 40 =================
    'birdcage': dict(  # 鳥かご: 船長室の窓辺に吊るした金の鳥かご
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(30, 40, 40, 0.6)),
        env=HOLD, items=[('window', dict(x=12, y=12, w=40, h=46, lit=True)), ('birdcage', dict(x=118, base=144, h=120, w=64, bird_ramp='red'))]),
    'grotto': dict(  # 岩穴: 海辺の洞窟、奥の青い水たまりと、隠した箱
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.1, halo=(112, 120, 60, 0.4)),
        env=('cave', dict(hz=128, seed=23)),
        items=[('tide_pool', dict(x=112, y=140, rx=80, ry=14)), ('crystal_cluster', dict(x=40, base=134, s=1.0, ramp='blue')), ('chest', dict(x=150, base=132, w=44, h=20, open_=False)),
               ('light_beam', dict(x0=90, y0=0, x1=110, y1=130, w0=8, w1=30, ramp='water'))]),
    'jewelegg': dict(  # 宝玉の卵: 台にのせた、金線と宝石の卵
        light=dict(**ICON), env=_icon('blue', hz=110),
        items=[('jewel_egg', dict(x=112, base=150, r=28))]),
    'search': dict(  # 探り: 夜の浜で、地図とランタンを手に宝のありかを探す
        light=dict(pool=(104, 96), radius=(150, 100), fall=1.1, halo=(66, 70, 40, 0.7)),
        env=('coast', dict(hz=92, shore=118, moon=None)),
        items=[('palm', dict(x=200, base=126, h=70)), ('x_mark', dict(x=160, y=146)),
               ('figure', dict(x=96, foot=156, h=110, arms=('lift', 'present'), lean=0.08, tunic='red', head='bandana', head_ramp='blue', legs_ramp='cloth', face=True,
                               props=[(0, ('held_lantern', {}), True), (1, ('held_map', {}), True)]))]),
    'shaman': dict(  # 祈祷師: 島の焚き火の前で、骨の杖をかざして祈る
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.1, halo=(150, 120, 50, 0.7)),
        env=_night(moon=None, hz=124, ground='sand', gain=0.55),
        items=[('palm', dict(x=24, base=128, h=80)), ('campfire', dict(x=160, base=150, s=1.2)), ('smoke', dict(pts=[(160, 110), (156, 90), (164, 70)])),
               ('figure', dict(x=90, foot=156, h=110, arms=('raise', 'forward'), robe=True, tunic='leather', mantle='red', head='horns', face=True,
                               props=[(0, ('bone_staff', {}), True)]))]),
    'hiddenshrine': dict(  # 奥の宮: 森の奥の苔むした小さな祠と鳥居
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(112, 110, 40, 0.4)),
        env=('forest', dict(hz=124, moon=None, seed=61)),
        items=[('torii', dict(x=112, base=136, w=120, h=90)), ('wayside_shrine', dict(x=112, base=150)), ('paper_lantern', dict(x=60, y=118, r=6, ramp='fire', string=None)),
               ('mushrooms', dict(x=170, base=154))]),
    'lorelei': dict(  # 歌う魔物: 月夜の岩に腰かけ、長い髪で歌う
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=96, moon=(40, 26, 11))),
        items=[('figure', dict(x=124, foot=136, h=100, arms=('lift', 'belly'), tunic='green', gown=True, head='long', hair='gold', face=True)),
               ('rocks', dict(pts=[(124, 168, 160, 50)])), ('foam', dict(x0=0, x1=224, y=128))]),
    'stowaway': dict(  # 潜り込み: 船倉の樽の蓋の下から、のぞく目
        light=dict(pool=(112, 100), radius=(140, 100), fall=1.2, halo=(26, 40, 40, 0.6)),
        env=HOLD, items=[('lantern', dict(x=26, y=40, hang=0)), ('crate', dict(x=160, y=96, w=40, h=40, gain=0.85)), ('sack', dict(x=50, base=150, r=14)),
                         ('stowaway_barrel', dict(x=112, base=152, r=26, h=64))]),
    'taskmaster': dict(  # 親方: 甲板で、腕を組んで鞭を持つ親方
        light=dict(pool=(108, 92), radius=(160, 105), **DAWN),
        env=_sea_dawn(hz=98),
        items=[('mast', dict(x=190, top=0, base=140)), ('ship_rail', dict(y=124)),
               ('figure', dict(x=100, foot=156, h=114, arms=('chest', 'chest'), tunic='blue', head='tricorn', head_ramp='cloth', legs_ramp='cloth', beard='hair', face=True, belt='leather'))]),
    'plenty': dict(  # 実り: 豊穣の角からあふれる果物と麦
        light=dict(**ICON, key=0.85), env=_icon('green', 'plank'),
        items=[('cornucopia', dict(x=112, y=110, s=1.5)), ('wheat_sheaves', dict(x=190, base=150, n=2))]),
    'cabinboy': dict(  # 見習い水夫: 甲板を磨く、頭に布を巻いた少年
        light=dict(pool=(108, 96), radius=(160, 105), **DAWN),
        env=_sea_dawn(hz=98),
        items=[('ship_rail', dict(y=124)), ('bucket', dict(x=170, base=154, r=12, fill='water')),
               ('figure', dict(x=104, foot=154, h=92, arms=('low', 'reach'), lean=0.15, tunic='paper', head='bandana', head_ramp='red', legs_ramp='blue', young=True, face=True,
                               props=[(1, ('broom', {}), True)]))]),
    'meltpot': dict(  # 溶かし鍋: 炉の上で金貨を溶かす坩堝
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 110, 50, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('forge', dict(x=0, y=40, w=50, h=50)), ('campfire', dict(x=120, base=156, s=1.0)), ('cauldron', dict(x=120, base=146, r=36, brew='gold')),
               ('stack', dict(cx=190, base=152, r=11, n=6, metal='gold', seed=43)), ('coin', dict(cx=60, cy=152, r=9, metal='silver'))]),
    'flagship': dict(  # 旗船: 夜明けの海で、大きな旗を掲げた三本帆柱の船
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN), env=_sea_dawn(hz=104),
        items=[('ship', dict(x=40, wl=110, s=0.45, gain=0.7, dep=0.4)), ('ship', dict(x=118, wl=150, s=1.25, masts=3, flag='gold', sails='paper'))]),
    'fortunehunter': dict(  # 財産狙い: 洞窟で、宝箱の中をのぞき込む
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(140, 110, 50, 0.6)),
        env=('cave', dict(hz=128, seed=25)),
        items=[('treasure_chest_glow', dict(x=150, base=152)),
               ('figure', dict(x=80, foot=154, h=108, arms=('reach', 'lift'), lean=0.2, tunic='green', head='tricorn', head_ramp='leather', legs_ramp='cloth', face=True,
                               props=[(1, ('held_lantern', {}), True)]))]),
    'gondola': dict(  # 渡し小舟: 夕暮れの水路を、棹を差して進む細い舟
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=('night', dict(hz=104, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('skyline', dict(x0=0, x1=224, base=104, gain=0.6, seed=19, lit=True)), ('water', dict(y0=104)), ('gondola', dict(x=112, wl=146, w=180)),
               ('figure', dict(x=150, foot=136, h=80, facing=-1, arms=('forward', 'chest'), tunic='paper', head='hat', head_ramp='cloth', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-110, length=4.0, below=3.0)), True)]))]),
    'harborvillage': dict(  # 波止場の村: 桟橋と、灯のともる海辺の家々
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=('coast', dict(hz=108, moon=(30, 20, 8, 0.4))),
        items=[('house', dict(x=0, base=112, w=60, h=34, roof_h=22, roof='red', windows=[(10, 10, 9, 9, True), (36, 10, 9, 9, True)])),
               ('house', dict(x=60, base=108, w=50, h=30, roof_h=20, roof='wood', gain=0.85, windows=[(14, 9, 8, 8, True)])),
               ('house', dict(x=150, base=110, w=74, h=36, roof_h=24, roof='blue', windows=[(10, 10, 9, 9, True), (50, 10, 9, 9, True)], door=(30, 12, 18))),
               ('dock', dict(y=130)), ('boat', dict(x=60, wl=128, w=50))]),
    'landingparty': dict(  # 上陸隊: 夜明けの浜に小舟を着け、剣を手に上がる
        light=dict(pool=(108, 96), radius=(180, 110), **DAWN), env=_sea_dawn(hz=92, shore=118),
        items=[('ship', dict(x=176, wl=96, s=0.5, kind='pirate', gain=0.75, dep=0.3)), ('boat', dict(x=60, wl=124, w=70)),
               ('figure', dict(x=120, foot=156, h=110, arms=('down', 'raise'), legs='stride', tunic='red', head='bandana', head_ramp='paper', legs_ramp='cloth', face=True,
                               props=[(1, ('cutlass', {}), True)]))]),
    'chartmaker': dict(  # 海図描き: 燭台の卓で、羽根ペンで海図を描く
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.15, halo=(30, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('candelabra', dict(x=26, base=76, h=24)), ('shelf', dict(x0=8, x1=46, y=76)), ('globe', dict(x=196, base=110, r=14)),
               ('figure', dict(x=110, foot=158, h=112, arms=('chest', 'present'), robe=True, tunic='blue', mantle='cloth', head='cap', head_ramp='cloth', face=True, beard='paper',
                               props=[(1, 'quill', True)])),
               ('table', dict(x0=20, x1=204, top=124, legs_to=160, front=True)), ('sea_chart', dict(x=118, y=134, w=150, h=24)), ('dividers', dict(x=40, y=132, ln=20))]),
    'maroon': dict(  # 島置き: 椰子が一本の小島に、取り残された男
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN), env=_sea_dawn(hz=94),
        items=[('ship', dict(x=190, wl=98, s=0.35, kind='pirate', gain=0.7, dep=0.4)), ('island', dict(x=112, wl=140, w=150, h=24)), ('palm', dict(x=150, base=128, h=70)),
               ('figure', dict(x=96, foot=134, h=78, arms=('down', 'raise'), tunic='paper', head='hair', legs_ramp='cloth', beard='hair'))]),
    'rope': dict(  # 綱: 甲板に巻いて置いた太い綱と、滑車
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='plank', hz=86, floor='planks')),
        items=[('pulley', dict(x=150, y=28)), ('rope', dict(x0=150, y0=34, x1=150, y1=96)), ('rope_coil', dict(x=100, base=150, r=46))]),
    'swampshacks': dict(  # 湿地の小屋: 霧の沼に杭で建つ板の小屋
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(76, 96, 40, 0.5)),
        env=_night(moon=None, ground=None, hz=118),
        items=[('bog', dict(y0=118)), ('tree', dict(x=196, base=124, h=80, kind='dead', ramp='cloth', gain=0.6, seed=63)),
               ('stilt_shack', dict(x=104, base=146, w=90, h=40, leg=26)), ('reeds', dict(xs=(14, 30, 170, 186), base=152)), ('fog', dict(bands=[(136, 8)], gain=0.7))]),
    'toolbox': dict(  # 道具箱: 作業台に開いた、船大工の道具箱
        light=dict(**ICON), env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('chest', dict(x=56, base=150, w=110, h=34, fill=None, open_=True, band='silver')),
               ('mallet', dict(x=90, y=118)), ('saw_on_bench', dict(x=150, y=112)), ('shavings', dict(pts=[(40, 150), (190, 150)]))]),
    'buriedgold': dict(  # 埋め宝: 夜明けの浜の × 印を掘り出した宝箱と鋤
        light=dict(pool=(112, 110), radius=(170, 110), **DAWN), env=_sea_dawn(hz=86, shore=110),
        items=[('palm', dict(x=30, base=120, h=70)), ('dug_hole', dict(x=112, y=146)), ('chest', dict(x=72, base=150, w=80, h=30, fill='gold')),
               ('spade_stuck', dict(x=180, base=150)), ('x_mark', dict(x=184, y=154, s=0.6))]),
    'crew': dict(  # 船乗りたち: 甲板に並ぶ、頭巾・三角帽・縞の服の水夫
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN), env=_sea_dawn(hz=98),
        items=[('mast', dict(x=112, top=0, base=120)), ('ship_rail', dict(y=124)),
               ('figure', dict(x=52, foot=152, h=98, arms=('hip', 'down'), tunic='blue', head='bandana', head_ramp='red', legs_ramp='cloth', face=True)),
               ('figure', dict(x=172, foot=152, h=100, facing=-1, arms=('hip', 'raise'), tunic='red', head='cap', head_ramp='blue', legs_ramp='cloth', face=True, props=[(1, ('cutlass', {}), True)])),
               ('figure', dict(x=112, foot=158, h=108, arms=('down', 'hip'), tunic='paper', head='tricorn', head_ramp='cloth', legs_ramp='cloth', beard='hair', face=True))]),
    'slasher': dict(  # 人斬り: 月夜の甲板で、二本の曲刀を構える
        light=dict(pool=(112, 92), radius=(140, 100), fall=1.2, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=104, moon=(40, 26, 10, 0.45), sky_ramp='purple')),
        items=[('ship_rail', dict(y=124)),
               ('figure', dict(x=112, foot=156, h=112, facing=-1, arms=('forward', 'raise'), legs='stride', tunic='cloth', head='bandana', head_ramp='red', mask='cloth', legs_ramp='cloth',
                               props=[(1, ('cutlass', {}), True), (0, ('cutlass', {}), True)]))]),
    'enlarge': dict(  # 押し広げ: 足場を組んで建て増す、港の倉
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN), env=_dawn(hz=130, ground='stone'),
        items=[('house', dict(x=30, base=134, w=80, h=44, roof_h=26, roof='red', windows=[(12, 12, 10, 10, True), (50, 12, 10, 10, True)])),
               ('timber_frame', dict(x=158, base=134, w=70, h=44)), ('block', dict(x=150, y=136, w=24, h=14)), ('ladder', dict(x=120, top=80, base=140, w=12))]),
    'statuette': dict(  # 小さな像: 布の上に立つ、宝石の目の金の小像
        light=dict(**ICON), env=_icon('red', hz=110),
        items=[('candle', dict(x=28, base=108, h=12, r=3)), ('pedestal', dict(x=112, base=150, w=50, h=24)), ('idol', dict(x=112, base=126))]),
    'firstmate': dict(  # 副長: 舵輪を握り、前を見すえる副長
        light=dict(pool=(108, 92), radius=(160, 105), **DAWN), env=_sea_dawn(hz=98),
        items=[('ship_rail', dict(y=124)),
               ('figure', dict(x=90, foot=156, h=114, arms=((1.25, 0.45, 2.45, 0.25), 'forward'), tunic='green', cloak='blue', head='tricorn', head_ramp='cloth', legs_ramp='cloth', face=True, beard='hair')),
               ('wheel', dict(x=150, y=104, r=26))]),
    'frigate': dict(  # 快速船: 夜の海を、赤い帆で走る海賊の快速船
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=96, moon=(40, 26, 11))),
        items=[('ship', dict(x=112, wl=148, s=1.15, kind='pirate', masts=2)), ('foam', dict(x0=30, x1=200, y=150))]),
    'miningroad': dict(  # 鉱石道: 山の坑口から伸びる線路と、鉱石を積んだ車
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN), env=_dawn(hz=124, ground='stone', hills=((96, 30, 0.5, 0.6, 4),)),
        items=[('headframe', dict(x=60, base=124, h=80)), ('road', dict(x=150, top=124, base=160, w0=8, w1=90, ramp='leather')), ('rails', dict(y=150)),
               ('cart', dict(x=130, base=152, w=56, h=22, ore='gold'))]),
    'pendant': dict(  # 首飾り: 天鵞絨の胸像に掛けた、大きな青い石の首飾り
        light=dict(**ICON), env=_icon('purple', hz=118, gain=0.6),
        items=[('pendant_big', dict(x=112, y=106, r=22, ramp='blue'))]),
    'pickaxe': dict(  # 採掘具: 岩に突き立てたつるはしと、割れ目の宝石
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(40, 50, 40, 0.6)),
        env=('cave', dict(hz=130, seed=27)),
        items=[('lantern', dict(x=36, y=44, hang=10)), ('vein', dict(pts=[(120, 60), (140, 80), (160, 76), (180, 96)])),
               ('pickaxe', dict(x=110, y=150, ang=-60, length=80)), ('gems', dict(pts=[(150, 84, 6, 'green'), (170, 96, 5, 'red'), (60, 140, 4, 'blue')])), ('rubble', dict(x=160, base=154, n=8))]),
    'pilgrim': dict(  # 遍路: 夜明けの峠道を、杖と笠で行く巡礼
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN), env=('pass', dict(hz=124, moon=None)),
        items=[('sun', dict(x=48, y=92, r=12)), ('wayside_shrine', dict(x=190, base=134)),
               ('figure', dict(x=104, foot=156, h=112, arms=('hip', 'forward'), legs='stride', tunic='paper', robe=True, head='jingasa', head_ramp='sand', face=True,
                               props=[(1, ('staff', dict(deg=-85, length=2.6, below=3.0)), True)]))]),
    'purser': dict(  # 主計長: 船倉の帳場で、帳簿と金庫を守る
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.7)),
        env=HOLD,
        items=[('lantern', dict(x=26, y=40, hang=0)), ('barrel', dict(x=196, base=110, r=16, h=40, lying=True, gain=0.8)),
               ('figure', dict(x=100, foot=158, h=112, arms=('chest', 'chest'), robe=True, tunic='blue', mantle='leather', head='tricorn', head_ramp='cloth', face=True,
                               props=[(1, ('book', dict(open_=True, w=1.6, h=1.3)), True)])),
               ('table', dict(x0=20, x1=204, top=130, legs_to=160, front=True)), ('coin_box', dict(x=168, base=132)), ('stack', dict(cx=48, base=134, r=9, n=5, metal='gold', seed=45))]),
    'silvermine': dict(  # 銀の鉱脈: 坑道の岩に光る銀の筋と、銀を積んだ鉱車
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(50, 44, 40, 0.7)),
        env=('cave', dict(hz=132, seed=29)),
        items=[('beam_frame', dict(x0=40, x1=184, top=24, bottom=138, w=8)), ('lantern', dict(x=56, y=44, hang=18)),
               ('vein', dict(pts=[(70, 60), (100, 74), (130, 66), (160, 84)], ramp='silver')), ('vein', dict(pts=[(80, 100), (110, 112), (140, 104)], ramp='silver')),
               ('rails', dict(y=150)), ('cart', dict(x=124, base=152, w=60, h=22, ore='silver'))]),
    'longship': dict(  # 長船: 夜明けの海を漕ぎ進む、竜頭と縞の帆の長船
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN), env=_sea_dawn(hz=100),
        items=[('ship', dict(x=112, wl=148, s=1.15, kind='longship', masts=1))]),
    'trickster': dict(  # いたずら者: 紫の夜、道化の帽子で災いの札を配る
        light=dict(pool=(112, 92), radius=(150, 100), fall=1.1, halo=(40, 40, 40, 0.5)),
        env=('night', dict(hz=126, moon=None, sky_ramp='purple', stars=20, ground_ramp='stone', ground_gain=0.5, clouds=())),
        items=[('figure', dict(x=108, foot=156, h=112, arms=('lift', 'present'), legs='stride', tunic='purple', head='jester', legs_ramp='red', face=True,
                               props=[(0, ('juggle', {}), True)])),
               ('playing_cards', dict(x=170, y=130)), ('wisps', dict(pts=[(40, 70), (190, 60)]))]),
    'wealthyvillage': dict(  # 裕福な村: 夜明けの港町、金の風見と石の家々
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN), env=_dawn(hz=124, ground='stone', hills=()),
        items=[('house', dict(x=0, base=124, w=60, h=40, roof_h=24, wall='stone', roof='red', timber=False, windows=[(10, 12, 9, 10, True), (38, 12, 9, 10, True)])),
               ('house', dict(x=150, base=124, w=74, h=44, roof_h=26, wall='stone', roof='blue', timber=False, windows=[(10, 12, 9, 10, True), (52, 12, 9, 10, True)], door=(30, 14, 20))),
               ('house', dict(x=64, base=140, w=82, h=48, roof_h=30, wall='paper', roof='red', chimney=0.4, windows=[(10, 12, 10, 11, True), (60, 12, 10, 11, True)], door=(34, 16, 22))),
               ('fountain', dict(x=112, base=158, r=30)), ('coin', dict(cx=40, cy=150, r=8, metal='gold'))]),
    'lootsack': dict(  # 分捕り袋: 口から金貨と宝石がこぼれる革袋
        light=dict(**ICON, key=0.85), env=_icon('blue', 'plank'),
        items=[('candle', dict(x=28, base=100, h=12, r=3)), ('money_bag', dict(x=112, base=150, r=36, ramp='leather')),
               ('jewel_heap', dict(x=170, base=152, w=50, n=8, seed=9)), ('coin', dict(cx=56, cy=150, r=9, metal='gold'))]),
    'kingscache': dict(  # 王の蓄え: 宝物蔵に積まれた、王冠の印の宝箱
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(26, 40, 40, 0.6), key=0.85),
        env=('room', dict(wall='stone', hz=100, floor='flag')),
        items=[('candelabra', dict(x=26, base=96, h=26)), ('chest', dict(x=120, base=118, w=70, h=28, open_=False, band='gold')),
               ('chest', dict(x=40, base=148, w=80, h=32, fill='gold')), ('royal_crown', dict(x=164, y=128, w=50, h=30)), ('pile', dict(cx=180, base=156, w=50, h=12, metal='gold', r=6, count=12, seed=47))]),
    # ================= イベント 15 =================
    'pe_bury': dict(  # 埋め戻し: 月夜の浜で、宝箱を砂に埋める
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=88, shore=112, moon=(40, 26, 10))),
        items=[('palm', dict(x=200, base=118, h=66)), ('dug_hole', dict(x=150, y=146)), ('chest', dict(x=126, base=150, w=46, h=18, open_=False)),
               ('figure', dict(x=76, foot=156, h=106, arms=('reach', 'low'), lean=0.25, tunic='red', head='bandana', head_ramp='blue', legs_ramp='cloth', props=[(1, ('spade', {}), True)]))]),
    'pe_avoid': dict(  # 避け: 嵐の暗礁を、帆をたたんでよける船
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(40, 30, 40, 0.4)),
        env=('coast', dict(hz=96, moon=None, stars=0, clouds=((30, 80, 12), (60, 60, 10)))),
        items=[('rain', dict(n=120, seed=5)), ('ship', dict(x=120, wl=112, s=0.55, sails='paper', gain=0.9)), ('beacon_tower', dict(x=44, base=110, h=60)),
               ('rocks', dict(pts=[(40, 160, 100, 50), (196, 166, 90, 44)])), ('foam', dict(x0=10, x1=214, y=134))]),
    'pe_deliver': dict(  # 届け物: 戸口に置かれた、封蝋の小包
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(40, 60, 40, 0.5)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('doorway', dict(x=112, base=124, w=50, h=88)), ('lantern', dict(x=60, y=44, hang=0)), ('parcel_big', dict(x=112, base=154, w=60, h=36)), ('seal_on', dict(x=112, y=134))]),
    'pe_peril': dict(  # 危うさ: 谷の上の、切れかけた吊り橋
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 30, 40, 0.4)),
        env=('pass', dict(hz=124, moon=(40, 30, 9, 0.5))),
        items=[('cliff', dict(x0=0, x1=60, top=70, side=1)), ('cliff', dict(x0=164, x1=224, top=70, side=-1)), ('rope_bridge', dict(x0=56, y0=72, x1=168, y1=72, sag=26)),
               ('fog', dict(bands=[(140, 10)], gain=0.7))]),
    'pe_rush': dict(  # 急ぎ: 夜明けの甲板を、樽を抱えて駆ける
        light=dict(pool=(108, 96), radius=(170, 110), **DAWN), env=_sea_dawn(hz=98),
        items=[('ship_rail', dict(y=124)),
               ('figure', dict(x=112, foot=156, h=110, arms=('present', 'present'), legs='stride', lean=0.3, tunic='blue', head='bandana', head_ramp='red', legs_ramp='cloth', face=True)),
               ('barrel', dict(x=150, base=120, r=14, h=28)), ('smoke', dict(pts=[(60, 150), (40, 146)]))]),
    'pe_foray': dict(  # 物取り: 夜の村へ忍び込む、袋をかついだ二人
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(40, 70, 40, 0.5)),
        env=_night(moon=None, hz=124, ground='stone', gain=0.55),
        items=[('house', dict(x=130, base=126, w=90, h=44, roof_h=26, roof='wood', windows=[(14, 12, 10, 10, True)])),
               ('figure', dict(x=50, foot=146, h=90, arms=('chest', 'down'), lean=0.2, tunic='cloth', head='hood', head_ramp='cloth', mask='cloth', behind=[(0, ('sack_back', {}))])),
               ('figure', dict(x=100, foot=156, h=108, arms=('reach', 'chest'), legs='crouch', lean=0.15, tunic='purple', head='bandana', head_ramp='cloth', mask='red',
                               props=[(1, ('bag', dict(ramp='red')), True)]))]),
    'pe_launch': dict(  # 船出し: 夜明けに船台を滑り降りる新しい船
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN), env=_sea_dawn(hz=110),
        items=[('slipway', dict(x0=0, x1=200, y=104)), ('ship', dict(x=112, wl=134, s=0.9, flag='blue')), ('foam', dict(x0=60, x1=200, y=138)), ('nobori', dict(x=20, top=40, base=120, w=14, ramp='red'))]),
    'pe_mirror': dict(  # 映し: 宝物を映して二つに見せる、金の枠の姿見
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=126, floor='flag')),
        items=[('candelabra', dict(x=26, base=126, h=26)), ('mirror_stand', dict(x=140, base=156, h=110)), ('goblet', dict(x=82, base=152, s=2.6, ramp='gold'))]),
    'pe_prepare': dict(  # 支度: 船倉で、背負い袋と地図と食料を詰める
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=HOLD, items=[('lantern', dict(x=26, y=40, hang=0)), ('backpack', dict(x=112, base=152)), ('waterskin', dict(x=60, base=152)), ('held_map_flat', dict(x=170, y=144)),
                         ('basket', dict(x=176, base=126, w=28, h=10, kind='bread', n=4))]),
    'pe_scrounge': dict(  # 拾い物: 廃船の残骸の中から、使える物をあさる
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN), env=_sea_dawn(hz=90, shore=112),
        items=[('broken_beams', dict(x0=120, x1=220, top=60, bottom=130)), ('broken_barrel', dict(x=60, base=146)),
               ('figure', dict(x=104, foot=156, h=104, arms=('reach', 'chest'), legs='crouch', lean=0.15, tunic='leather', head='bandana', head_ramp='green', legs_ramp='cloth', face=True)),
               ('coin', dict(cx=150, cy=152, r=6, metal='copper'))]),
    'pe_journey': dict(  # 長旅: 夜明けの海に、遠くの島々へ続く船の跡
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN), env=_sea_dawn(hz=96),
        items=[('island', dict(x=190, wl=98, w=50, h=10)), ('island', dict(x=150, wl=100, w=30, h=8)), ('sun', dict(x=60, y=92, r=12)),
               ('ship', dict(x=120, wl=104, s=0.3, gain=0.8, dep=0.3)), ('ship_rail', dict(y=128)), ('telescope', dict(x=112, base=128))]),
    'pe_maelstrom': dict(  # 大渦: 嵐の海に口を開ける渦と、のまれかける船
        light=dict(pool=(112, 110), radius=(160, 105), fall=1.05, halo=(40, 30, 40, 0.4)),
        env=('coast', dict(hz=70, moon=None, stars=0, clouds=((30, 60, 12),))),
        items=[('vortex', dict(x=112, y=120, r=80, ramp='blue')), ('ship', dict(x=150, wl=110, s=0.5, kind='merchant', gain=0.9))]),
    'pe_looting': dict(  # 荒稼ぎ: 燃える港から、宝箱を担いで逃げる海賊
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.05, halo=(150, 80, 60, 0.6)),
        env=_night(moon=None, hz=124, ground='stone', gain=0.55),
        items=[('house_fire', dict(x=150, base=124, w=80, h=44)), ('smoke_column', dict(x=180, y=40, h=50)),
               ('figure', dict(x=88, foot=156, h=110, arms=('lift', 'lift'), legs='stride', lean=0.1, tunic='red', head='tricorn', head_ramp='cloth', legs_ramp='cloth', face=True)),
               ('chest', dict(x=60, base=78, w=56, h=20, open_=False))]),
    'pe_invasion': dict(  # 侵攻: 夜明けの浜へ押し寄せる、髑髏の旗の船団
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN), env=_sea_dawn(hz=92, shore=132),
        items=[('ship', dict(x=40, wl=100, s=0.45, kind='pirate', gain=0.75, dep=0.3)), ('ship', dict(x=176, wl=98, s=0.55, kind='pirate', gain=0.75, dep=0.3)),
               ('boat', dict(x=60, wl=124, w=60)), ('nobori', dict(x=150, top=70, base=150, w=16, ramp='red')), ('bonfire', dict(x=184, base=150, s=0.5)),
               ('figure', dict(x=112, foot=156, h=104, arms=('down', 'raise'), legs='stride', tunic='red', head='bandana', head_ramp='cloth', legs_ramp='cloth', props=[(1, ('cutlass', {}), True)]))]),
    'pe_prosper': dict(  # 繁盛: 港の市にあふれる、金と銀と銅の山
        light=dict(pool=(112, 104), radius=(160, 105), **WARM, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='plank', hz=90, floor='table')),
        items=[('awning', dict(x0=0, x1=224, y=0, depth=16, colors=('red', 'paper'))), ('chest', dict(x=70, base=124, w=84, h=34, fill='gold')),
               ('pile', dict(cx=60, base=152, w=80, h=46, metal='gold', r=9, count=30, seed=49)), ('pile', dict(cx=124, base=140, w=60, h=36, metal='silver', r=8, count=22, seed=51, stamps=('tower', 'star'))),
               ('pile', dict(cx=180, base=152, w=60, h=34, metal='copper', r=8, count=18, seed=53, stamps=('pip', 'star'))), ('jewel_heap', dict(x=120, base=156, w=30, n=5, seed=11))]),
}
