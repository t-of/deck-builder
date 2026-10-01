"""同盟（cards-allies.js）の 31 枚の場面データ。書き方は scenes.py の冒頭を見る。
単独の王国 25 と、4 種が順に重なった山 6。町の衆と組合の人の札が多いので人物を主役に、
宿場・都・砦・船で場所を散らし、夜ばかりにならないよう夜明けと室内の灯を混ぜる。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


SCENES = {
    'trinket': dict(  # 飾り玉: 天鵞絨の台に吊るした、金の口金の硝子玉
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(112, 96, 40, 0.3)),
        env=('icon', dict(hz=118, wall='stone', cloth='purple', cloth_gain=0.65)),
        items=[('candle', dict(x=28, base=116, h=14, r=3)), ('bauble', dict(x=112, y=82, r=32, ramp='blue')),
               ('gems', dict(pts=[(60, 140, 4, 'red'), (170, 144, 4, 'green'), (186, 136, 3, 'gold')]))]),
    'flatterer': dict(  # 太鼓持ち: 扇をかざし、腰を低くしてにじり寄る
        light=dict(pool=(108, 92), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=('room', dict(wall='shoji', hz=120, floor='planks')),
        items=[('paper_lantern', dict(x=30, y=60, r=12, ramp='fire', string=0)),
               ('figure', dict(x=112, foot=154, h=104, arms=('lift', 'present'), lean=0.22, legs='stride', tunic='gold', mantle='red', head='topknot', face=True,
                               props=[(0, ('fan', dict(ramp='red')), True)]))]),
    'importer': dict(  # 舶来商: 波止場の木箱から出した、異国の壺と地球儀と絨毯
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=92, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('ship', dict(x=176, wl=100, s=0.55, gain=0.75, dep=0.3)), ('dock', dict(y=118)),
               ('crate', dict(x=20, y=96, w=36, h=30)), ('rug', dict(x=112, y=140, w=150, d=30, ramp='red')),
               ('vase', dict(x=84, base=138, s=1.3)), ('globe', dict(x=150, base=136, r=16)), ('spice_sacks', dict(x=196, base=144))]),
    'tradecamp': dict(  # 行商の宿営: 夜の野で、幌馬車と天幕のあいだの焚き火
        light=dict(pool=(104, 110), radius=(150, 100), fall=1.1, halo=(96, 128, 50, 0.8)),
        env=_night(moon=None, hz=118, gain=0.55),
        items=[('wagon', dict(x=170, base=140, w=90, cover='paper')), ('tent', dict(x=34, base=124, w=60, h=54)),
               ('campfire', dict(x=100, base=150, s=1.2)), ('sack', dict(x=60, base=154, r=11)), ('crate', dict(x=124, y=132, w=20, h=18, gain=0.9))]),
    'picket': dict(  # 見回り: 夜の柵に沿って、提灯と槍を持って歩く
        light=dict(pool=(108, 88), radius=(150, 100), fall=1.15, halo=(68, 58, 40, 0.8)),
        env=_night(moon=None, hz=126, ground='stone', gain=0.55, stars=30),
        items=[('palisade', dict(x0=0, x1=224, base=128, h=56, gain=0.8)),
               ('figure', dict(x=110, foot=154, h=112, arms=('lift', 'low'), legs='stride', tunic='blue', head='jingasa', head_ramp='cloth', legs_ramp='cloth', belt='red',
                               props=[(0, ('held_lantern', {}), True)], behind=[(1, ('staff', dict(deg=-95, length=5.2, top='spear', below=2.4)))]))]),
    'underling': dict(  # 小者: 屋敷の土間で、箒を手に控える下働き
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(24, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=118, floor='flag')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('barrel', dict(x=190, base=140, r=16, h=36, gain=0.85)), ('bucket', dict(x=160, base=154, r=11, fill='water')),
               ('figure', dict(x=100, foot=154, h=98, arms=('chest', 'low'), lean=0.08, tunic='cloth', apron='paper', head='hair', legs_ramp='cloth', face=True,
                               props=[(1, ('broom', {}), True)]))]),
    'middleman': dict(  # 周旋屋: 帳場で、片手に証文、片手に金貨を差し出す
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('candle', dict(x=28, base=56, h=12, r=3, holder=True)), ('shelf', dict(x0=10, x1=46, y=56)),
               ('figure', dict(x=112, foot=158, h=112, arms=('present', 'present'), robe=True, tunic='green', mantle='leather', head='hat', head_ramp='cloth', face=True,
                               props=[(0, 'letter', True), (1, ('held_coin', dict(metal='gold', r=0.7)), True)])),
               ('table', dict(x0=20, x1=204, top=126, legs_to=160, front=True)),
               ('stack', dict(cx=176, base=130, r=10, n=6, metal='gold', seed=31)), ('parcel_big', dict(x=48, base=130, w=40, h=24))]),
    'masterbuilder': dict(  # 棟梁: 夜明けの棟上げの骨組みを背に、曲尺を掲げる
        light=dict(pool=(108, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=130, ground='sand'),
        items=[('timber_frame', dict(x=140, base=138, w=140, h=72)),
               ('figure', dict(x=72, foot=156, h=112, arms=('hip', 'lift'), tunic='blue', apron='paper', head='topknot', legs_ramp='cloth', face=True, belt='red',
                               props=[(1, ('kanejaku', {}), True)])),
               ('logs', dict(x=176, base=156, n=3, r=6))]),
    'dispatch': dict(  # 飛脚: 夜明けの街道を、文箱を担いで駆ける
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, ground='sand', hills=((106, 14, 0.5, 0.6, 2),)),
        items=[('tree', dict(x=200, base=128, h=70, kind='pine', gain=0.75, seed=51)),
               ('figure', dict(x=108, foot=156, h=110, arms=('forward', 'chest'), legs='stride', lean=0.25, tunic='paper', head='topknot', legs_ramp='skin', boots='paper', belt='red',
                               props=[(1, ('courier_pole', {}), True)]))]),
    'galley': dict(  # 御座船: 夕暮れの海を進む、朱塗りの屋形の船
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=96, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 80, 8),))),
        items=[('sun', dict(x=50, y=92, r=14)), ('gozabune', dict(x=112, wl=146, w=170))]),
    'innkeeper': dict(  # 宿の亭主: 樽の並ぶ酒場で、盆に杯をのせて迎える
        light=dict(pool=(108, 96), radius=(150, 100), **WARM, halo=(24, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('lantern', dict(x=24, y=40, hang=0)), ('barrel', dict(x=176, base=96, r=16, h=40, lying=True)), ('barrel', dict(x=208, base=96, r=16, h=40, lying=True, gain=0.85)),
               ('shelf', dict(x0=150, x1=224, y=60)), ('tankard', dict(x=170, base=60)), ('tankard', dict(x=196, base=60)),
               ('figure', dict(x=100, foot=154, h=112, arms=('down', 'present'), tunic='red', apron='paper', head='hair', legs_ramp='cloth', beard='hair', face=True,
                               props=[(1, 'tray', True)]))]),
    'posttown': dict(  # 宿場町: 夕暮れの街道に、暖簾と提灯の宿が並ぶ
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN, halo=(60, 80, 40, 0.4)),
        env=_dawn(hz=124, ground='sand', hills=()),
        items=[('house', dict(x=0, base=128, w=70, h=44, roof_h=22, wall='paper', roof='wood', timber=True, windows=[(10, 10, 14, 12, True), (44, 10, 14, 12, True)], door=(26, 16, 22))),
               ('house', dict(x=150, base=128, w=74, h=44, roof_h=22, wall='paper', roof='wood', timber=True, windows=[(10, 10, 14, 12, True), (48, 10, 14, 12, True)], door=(30, 16, 22))),
               ('house', dict(x=80, base=112, w=60, h=30, roof_h=18, wall='paper', roof='red', gain=0.65, windows=[(10, 8, 10, 9, True), (40, 8, 10, 9, True)])),
               ('noren', dict(x0=10, x1=60, y=94, ramp='blue')), ('noren', dict(x0=160, x1=214, y=94, ramp='red')),
               ('paper_lantern', dict(x=72, y=90, r=7, ramp='fire', string=84)), ('paper_lantern', dict(x=146, y=90, r=7, ramp='fire', string=84)),
               ('road', dict(x=112, top=112, base=160, w0=20, w1=110, ramp='sand'))]),
    'savage': dict(  # 荒くれ者: 夜の森で、棍棒を振り上げるひげの大男
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(36, 52, 40, 0.6)),
        env=('forest', dict(hz=124, moon=None, seed=53)),
        items=[('torch', dict(x=30, y=56)),
               ('figure', dict(x=112, foot=154, h=114, arms=('forward', 'raise'), legs='stride', tunic='leather', mantle='leather', head='hair', hair='hair', beard='hair', legs_ramp='cloth', face=True,
                               props=[(1, ('club', {}), True)]))]),
    'metropolis': dict(  # 都: 夕暮れの丘から見る、灯のあふれる都と宮殿
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN, halo=(112, 90, 60, 0.3)),
        env=_dawn(hz=116, ground='stone', hills=()),
        items=[('skyline', dict(x0=0, x1=224, base=104, gain=0.55, seed=11, lit=True)), ('palace', dict(x=112, base=124, w=170, h=52)),
               ('tower', dict(x=12, base=128, w=26, h=70, roof='blue', windows=[(-2, 20, 5, 8)])), ('tower', dict(x=186, base=128, w=26, h=78, roof='red', windows=[(-2, 22, 5, 8)])),
               ('far_lights', dict(pts=[(40, 140), (80, 146), (150, 142), (190, 148), (112, 152)]))]),
    'deed': dict(  # 証文: 封蝋を押した証文と、羽根ペンと印
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=70, floor='table')),
        items=[('candle', dict(x=26, base=68, h=12, r=3)), ('doc', dict(x=106, y=114, w=130, h=70, seal=True, lines=6, sign=True)),
               ('quill_flat', dict(x=184, y=120)), ('wax_seal', dict(x=190, y=146, r=12))]),
    'go_between': dict(  # 仲立ち: 青と赤の袖が真ん中で手を結ぶ
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.0, halo=(112, 46, 40, 0.4), amb=0.08, key=0.85),
        env=('icon', dict(hz=130, wall='plank', cloth='green', cloth_gain=0.6)),
        items=[('handshake', dict(x=112, y=104, s=1.35))]),
    'arcade2': dict(  # 商店街: 灯のともる店の並ぶ、夜のアーケード
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=_night(moon=None, hz=138, ground='stone', gain=0.6),
        items=[('house', dict(x=0, base=140, w=74, h=70, roof_h=26, roof='red', timber=True, windows=[(8, 14, 24, 22, True), (42, 14, 24, 22, True), (14, 46, 14, 12, True)])),
               ('house', dict(x=76, base=140, w=72, h=78, roof_h=24, wall='stone', roof='blue', timber=False, windows=[(8, 14, 22, 24, True), (42, 14, 22, 24, True), (28, 50, 14, 12, True)])),
               ('house', dict(x=150, base=140, w=74, h=70, roof_h=26, roof='wood', timber=True, windows=[(8, 14, 24, 22, True), (42, 14, 24, 22, True), (46, 46, 14, 12, True)])),
               ('awning', dict(x0=0, x1=74, y=86, depth=10, colors=('red', 'paper'))), ('awning', dict(x0=76, x1=148, y=80, depth=10, colors=('green', 'paper'))),
               ('awning', dict(x0=150, x1=224, y=86, depth=10, colors=('blue', 'paper'))),
               ('sign', dict(x=38, y=52, w=24, h=12, emblem='coin')), ('sign', dict(x=186, y=52, w=24, h=12, emblem='coin')),
               ('lantern_string', dict(y0=24, y1=36, colors=('red', 'gold', 'blue', 'gold', 'red'))),
               ('basket', dict(x=36, base=144, w=26, h=10, kind='apple', fill='red', n=6)), ('cloth_bolts', dict(x=186, base=150)), ('pots', dict(x=112, base=150, n=3))]),
    'guildhead': dict(  # 組合長: 組合の旗の前に立つ、金の鎖の長
        light=dict(pool=(108, 90), radius=(150, 100), **WARM, halo=(20, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('wall_torch', dict(x=18, y=42)), ('hang_banner', dict(x=150, top=0, w=28, h=70, ramp='blue', kind='chevron')), ('hang_banner', dict(x=190, top=0, w=24, h=60, ramp='gold', kind='circle')),
               ('figure', dict(x=100, foot=156, h=114, arms=('belly', 'present'), robe=True, tunic='blue', trim='gold', mantle='red', head='hat', head_ramp='red', beard='hair', face=True,
                               props=[(1, 'scroll', True)])),
               ('necklace_on', dict(x=100, y=72))]),
    'waylayer': dict(  # 辻斬り: 月夜の辻で、笠の下から刀を抜く
        light=dict(pool=(112, 90), radius=(140, 100), fall=1.2, halo=(40, 26, 40, 0.6)),
        env=_night(moon=(40, 26, 10, 0.45), hz=128, ground='stone', gain=0.5, sky_ramp='purple', stars=16),
        items=[('wayside_shrine', dict(x=186, base=132)),
               ('figure', dict(x=110, foot=156, h=112, facing=-1, arms=('chest', 'forward'), legs='stride', lean=0.1, tunic='cloth', robe=True, mantle='purple', head='jingasa', head_ramp='sand',
                               props=[(1, ('katana', dict(deg=-15, length=4.2)), True)]))]),
    'tracker2': dict(  # 狩りの名手: 雪の森に膝をつき、獣の足跡を読む
        light=dict(pool=(108, 104), radius=(160, 105), fall=1.1, halo=(30, 22, 34, 0.6)),
        env=('forest', dict(hz=118, moon=(30, 22, 9), seed=55)),
        items=[('snow_ground', dict(y0=120)), ('tracks', dict(pts=[(150, 150), (166, 144), (180, 138), (196, 132), (212, 126)])),
               ('figure', dict(x=92, foot=154, h=108, arms=('belly', 'reach'), legs='kneel', tunic='green', cloak='leather', head='hood', head_ramp='green', legs_ramp='leather', face=True,
                               behind=[(0, ('bow', dict(height=4.0)))]))]),
    'modify': dict(  # 作り変え: 仕立て場の胴台に、待ち針で布を当てる
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('spools_shelf', dict(x0=150, x1=222, top=20, base=80)),
               ('dress_form', dict(x=104, base=154, h=118, ramp='purple')), ('scissors', dict(x=168, y=140)), ('cloth_bolts', dict(x=196, base=158))]),
    'skirmisher': dict(  # 斥候兵: 夜明けの草原を駆け、投げ槍を構える
        light=dict(pool=(108, 92), radius=(180, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('weeds', dict(x=30, base=152, n=10, h=20)), ('weeds', dict(x=190, base=150, n=10, h=18)),
               ('figure', dict(x=110, foot=156, h=112, arms=('forward', 'raise'), legs='stride', lean=0.1, tunic='green', head='cap', head_ramp='leather', legs_ramp='leather', belt='leather',
                               props=[(1, ('staff', dict(deg=-160, length=3.8, top='spear', below=1.8)), True), (0, ('round_shield', dict(ramp='red')), True)]))]),
    'specialist': dict(  # 職人肌: 作業台に開いた懐中時計と、拡大鏡と歯車
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=80, floor='table')),
        items=[('candle', dict(x=28, base=78, h=12, r=3)), ('tool_rack', dict(x0=70, x1=210, y=12, tools=('pliers', 'hammer', 'pliers'))),
               ('pocket_watch', dict(x=104, y=116, r=30)), ('gears', dict(x=176, y=132)), ('magnifier', dict(x=50, y=140, r=12, ang=30))]),
    'exchange': dict(  # 差し替え: 卓の上の剣と壺を、回る矢印で取りかえる
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=96, floor='table', floor_ramp='blue', floor_gain=0.7)),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('vase', dict(x=62, base=150, s=1.5)), ('swap_arrows', dict(x=112, y=110)),
               ('goblet', dict(x=166, base=152, s=4.2, ramp='gold'))]),
    'marquess': dict(  # 大殿: 玉座の前に立つ、毛皮の外套の大殿
        light=dict(pool=(108, 90), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('candelabra', dict(x=26, base=82, h=26)), ('shelf', dict(x0=8, x1=46, y=82)), ('throne', dict(x=160, base=128, ramp='red')),
               ('carpet', dict(x=112, top=118, base=160, w0=40, w1=110, ramp='red')),
               ('figure', dict(x=100, foot=156, h=116, arms=('belly', 'lift'), robe=True, tunic='purple', trim='gold', mantle='paper', cloak='red', head='crown', beard='hair', face=True,
                               props=[(1, ('staff', dict(deg=-95, length=2.0, top='knob', below=1.0)), True)]))]),
    # ================= 4 種が順に重なった山（山の札 1 枚と、中の 4 種） =================
    'p_augurs': dict(  # 占い師たち: 夜の社の鳥居と、願い札の下がる縄と灯
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(40, 64, 40, 0.6)),
        env=_night(moon=(40, 26, 9, 0.45), hz=130, ground='sand', gain=0.5),
        items=[('torii', dict(x=112, base=134, w=170, h=112)), ('charms', dict(x0=40, x1=184, y=78)),
               ('paper_lantern', dict(x=56, y=112, r=9, ramp='fire', string=None)), ('paper_lantern', dict(x=168, y=112, r=9, ramp='fire', string=None)),
               ('wayside_shrine', dict(x=112, base=150))]),
    'herbalist2': dict(  # 薬草摘み: 夜明けの森の下草に膝をつき、籠に薬草を摘む
        light=dict(pool=(108, 104), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=57)),
        items=[('weeds', dict(x=150, base=150, n=10, h=22)), ('mushrooms', dict(x=180, base=154)), ('flowers', dict(rows=[(146, 4.0, 18)])),
               ('figure', dict(x=96, foot=154, h=106, arms=('reach', 'present'), legs='kneel', tunic='green', apron='paper', head='hood', head_ramp='leather', legs_ramp='cloth', face=True,
                               props=[(1, 'basket_held', True)]))]),
    'acolyte': dict(  # 神子: 社の板の間で、榊を捧げ持つ白衣の子
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(26, 50, 40, 0.6)),
        env=('room', dict(wall='shoji', hz=118, floor='planks')),
        items=[('candle_row', dict(x0=150, x1=214, base=116)), ('candle', dict(x=30, base=112, h=16, r=3)),
               ('figure', dict(x=104, foot=152, h=90, arms=('present', 'present'), tunic='paper', legs_ramp='blue', boots='paper', head='hair', young=True, face=True, belt='blue',
                               props=[(1, 'flowers_held', True)]))]),
    'shrinemaiden': dict(  # 巫女: 夜の社で、緋袴の巫女が神楽鈴を振る
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(40, 64, 40, 0.6)),
        env=_night(moon=None, hz=128, ground='sand', gain=0.5),
        items=[('torii', dict(x=112, base=130, w=200, h=118)), ('paper_lantern', dict(x=40, y=74, r=8, ramp='fire', string=None)),
               ('figure', dict(x=112, foot=156, h=110, arms=('belly', 'lift'), tunic='paper', legs_ramp='red', boots='paper', head='long', hair='hair', face=True, belt='red',
                               props=[(1, ('kagura_bell', {}), True)]))]),
    'oracle2': dict(  # 託宣者: 香炉の煙の中で、両手を掲げて神託を告げる
        light=dict(pool=(112, 100), radius=(140, 100), fall=1.15, halo=(112, 130, 50, 0.7)),
        env=('room', dict(wall='stone', hz=126, floor='flag', floor_ramp='purple')),
        items=[('smoke', dict(pts=[(112, 120), (100, 96), (118, 74), (104, 50)])),
               ('figure', dict(x=112, foot=150, h=112, arms=('raise', 'raise'), robe=True, tunic='purple', trim='gold', mantle='paper', head='long', hair='paper', face=True)),
               ('brazier', dict(x=112, base=156))]),
    'p_clashes': dict(  # いくさ場: 夕暮れの古戦場に立つ幟と、刺さったままの刀
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, ground='leather', hills=((106, 14, 0.5, 0.6, 3),)),
        items=[('smoke_column', dict(x=170, y=50, h=60)), ('battlefield', dict(y0=126)),
               ('nobori', dict(x=60, top=24, base=140, w=22, ramp='red')), ('nobori', dict(x=150, top=36, base=140, w=18, ramp='blue')),
               ('sword_stuck', dict(x=110, base=152)), ('sword_stuck', dict(x=190, base=150))]),
    'battleplan': dict(  # 軍略: 燭台の卓の盤上に並ぶ駒と、広げた地図
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=74, floor='table')),
        items=[('candelabra', dict(x=28, base=74, h=22)), ('sea_chart', dict(x=150, y=104, w=110, h=40)), ('chess_board', dict(x=96, y=128, w=86)),
               ('dagger_stuck', dict(x=184, base=112, s=0.9))]),
    'archer': dict(  # 弓兵: 夕暮れの戦場で、幟を背に弓を引く
        light=dict(pool=(108, 92), radius=(180, 110), **DAWN),
        env=_dawn(hz=128, ground='leather', hills=((110, 14, 0.5, 0.6, 3),)),
        items=[('smoke_column', dict(x=180, y=60, h=60)), ('nobori', dict(x=176, top=30, base=140, w=18, ramp='red')), ('nobori', dict(x=200, top=40, base=140, w=16, ramp='blue')),
               ('figure', dict(x=92, foot=156, h=112, arms=('pull', 'aim'), legs='stride', tunic='red', armor=True, head='helm', legs_ramp='cloth',
                               props=[(1, 'bow', True)], behind=[(0, ('quiver', {}))]))]),
    'warlord': dict(  # 総大将: 篝火の陣で、鶏冠の兜に赤い外套、刀を掲げる
        light=dict(pool=(108, 88), radius=(160, 105), fall=1.1, halo=(30, 70, 40, 0.7)),
        env=_night(moon=None, hz=128, ground='stone', gain=0.55),
        items=[('brazier', dict(x=28, base=126)), ('jinmaku', dict(x0=100, x1=224, top=56, base=128)),
               ('figure', dict(x=96, foot=156, h=116, arms=('belly', 'raise'), tunic='red', armor=True, head='crest', cloak='red', legs_ramp='cloth', face=True, beard='hair',
                               props=[(1, ('katana', dict(deg=-80, length=4.2)), True)]))]),
    'territory': dict(  # 版図: 壁の大きな地図に、色の旗の留め針
        light=dict(pool=(112, 90), radius=(150, 100), **WARM, halo=(20, 40, 40, 0.5)),
        env=('room', dict(wall='plank', hz=134, floor='planks')),
        items=[('wall_torch', dict(x=16, y=40)), ('wall_map', dict(x0=34, y0=14, x1=210, y1=118)),
               ('gems', dict(pts=[(70, 40, 4, 'red'), (120, 70, 4, 'blue'), (160, 46, 4, 'green'), (184, 96, 4, 'gold'), (90, 96, 4, 'red')])),
               ('globe', dict(x=196, base=154, r=14))]),
    'p_forts': dict(  # 砦の数々: 柵の砦の向こう、山の上の本丸
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 30, 40, 0.5)),
        env=_night(moon=(40, 30, 10, 0.45), hz=130, ground='foliage', gain=0.55, hills=[(96, 30, 0.5, 0.6, 9)]),
        items=[('castle', dict(x=150, base=94, s=0.6)), ('palisade', dict(x0=0, x1=224, base=140, h=44, gain=0.85)),
               ('army_tent', dict(x=60, base=152, w=60, h=36, ramp='paper', stripe='red'))]),
    'pavilion': dict(  # 陣幕: 杭に張った家紋の幕と、床几と幟
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='sand'),
        items=[('jinmaku', dict(x0=12, x1=212, top=50, base=134, crest='blue')), ('nobori', dict(x=196, top=20, base=140, w=16, ramp='blue')),
               ('chair', dict(x=112, base=152, s=1.2))]),
    'garrison': dict(  # 詰め所: 武具の架と卓、兜の置かれた番所
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(26, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=20, bh=10)),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('weapon_rack', dict(x0=70, x1=200, top=36, base=118)),
               ('table', dict(x0=50, x1=170, top=128, legs_to=156)), ('helmet_floor', dict(x=86, base=128)), ('tankard', dict(x=130, base=128)), ('dice', dict(x=150, y=124, s=8, pips=4))]),
    'hillfort': dict(  # 山の砦: 山の柵の砦と、篝火をともした物見櫓
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(100, 40, 40, 0.6)),
        env=_night(moon=None, hz=130, ground='foliage', gain=0.55, hills=[(104, 22, 0.45, 0.6, 9)]),
        items=[('palisade', dict(x0=0, x1=224, base=136, h=40, gain=0.85)), ('watchtower', dict(x=104, base=144, h=126, w=44)),
               ('army_tent', dict(x=186, base=150, w=60, h=40, ramp='paper', stripe='red'))]),
    'citadel2': dict(  # 本丸: 月夜にそびえる石の本丸と旗
        light=dict(pool=(112, 84), radius=(170, 110), fall=1.05, halo=(40, 30, 40, 0.6)),
        env=_night(moon=(40, 30, 11), hz=120, ground='stone', gain=0.55, hills=[(110, 14, 0.45, 0.6, 2)]),
        items=[('castle', dict(x=112, base=136, s=1.25, roof='red', banner='blue'))]),
    'p_odysseys': dict(  # 旅の物語: 古い海図を手前に、夜の海を遠い岸へ向かう船
        light=dict(pool=(112, 110), radius=(170, 110), fall=1.05, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=86, moon=(40, 26, 10, 0.45))),
        items=[('island', dict(x=184, wl=88, w=80, h=16)), ('ship', dict(x=104, wl=104, s=0.7)),
               ('sea_chart', dict(x=112, y=142, w=190, h=40)), ('compass_rose', dict(x=40, y=140, r=14))]),
    'oldchart': dict(  # 古びた海図: 卓に広げた端の焼けた海図と、羅針盤と両脚器
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=66, floor='table')),
        items=[('candle', dict(x=28, base=64, h=10, r=3)), ('sea_chart', dict(x=118, y=112, w=170, h=64)), ('compass_rose', dict(x=58, y=140, r=18)),
               ('dividers', dict(x=168, y=128, ln=34))]),
    'voyage': dict(  # 船出: 夜明けの港の桟橋から、帆を張って出ていく船
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=96, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('sun', dict(x=56, y=92, r=14)), ('ship', dict(x=132, wl=128, s=1.0, flag='blue')), ('long_pier', dict(x=30, y0=110, y1=160, w0=8, w1=60))]),
    'sunkentreasure': dict(  # 沈んだ宝: 海の底の砂に沈む宝箱、こぼれた金貨と海藻
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.1, halo=(112, 0, 80, 0.5)),
        env=('coast', dict(hz=-4, moon=None, stars=0, clouds=())),
        items=[('light_beam', dict(x0=90, y0=0, x1=110, y1=150, w0=14, w1=50, ramp='water')), ('beach', dict(y0=130)),
               ('seaweed', dict(x=30, base=150, h=50)), ('seaweed', dict(x=196, base=152, h=40)), ('seaweed', dict(x=48, base=154, h=30)),
               ('chest', dict(x=72, base=150, w=76, h=34, fill='gold')), ('coin', dict(cx=170, cy=148, r=8, metal='gold')), ('coin', dict(cx=60, cy=154, r=7, metal='gold', stamp='star')),
               ('shell', dict(x=180, y=154, r=5)), ('foam', dict(x0=100, x1=130, y=40))]),
    'distantshore': dict(  # 彼方の岸: 夕焼けの遠い島の浜に、着いた小舟と椰子
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=92, shore=124, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('sun', dict(x=60, y=88, r=16)), ('palm', dict(x=170, base=132, h=80)), ('palm', dict(x=200, base=128, h=60, lean=-0.2)),
               ('boat', dict(x=90, wl=140, w=70)), ('hut', dict(x=148, base=128, w=30, h=18))]),
    'p_townsfolk': dict(  # 町の衆: 風車の見える広場に集まる、触れ手と鍛冶と粉ひき
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=120, ground='stone'),
        items=[('windmill', dict(x=190, base=120, h=70)), ('house', dict(x=0, base=118, w=50, h=30, roof_h=20, roof='red', gain=0.6, windows=[(10, 10, 7, 8, True)])),
               ('figure', dict(x=54, foot=154, h=100, arms=('down', 'raise'), tunic='red', cloak='blue', head='feather', head_ramp='blue', legs_ramp='cloth', props=[(1, 'bell', True)])),
               ('figure', dict(x=168, foot=156, h=102, facing=-1, arms=('low', 'hip'), tunic='paper', apron='paper', head='cap', head_ramp='paper', legs_ramp='cloth', face=True)),
               ('figure', dict(x=112, foot=158, h=108, arms=('down', 'low'), tunic='leather', apron='leather', head='hair', beard='hair', legs_ramp='cloth', face=True,
                               props=[(1, ('hammer', dict(deg=60, length=2.2)), True)]))]),
    'crier2': dict(  # 町の触れ手: 朝の広場で、木箱に乗って触れ書きを読み上げる
        light=dict(pool=(108, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='stone', hills=()),
        items=[('skyline', dict(x0=0, x1=224, base=100, gain=0.5, seed=13, lit=False)),
               ('crate', dict(x=84, y=128, w=50, h=26)),
               ('figure', dict(x=108, foot=130, h=100, arms=('chest', 'raise'), tunic='blue', mantle='red', head='feather', head_ramp='red', legs_ramp='cloth', face=True,
                               props=[(0, ('scroll', dict(length=2.0)), True), (1, 'bell', True)]))]),
    'blacksmith2': dict(  # 村の鍛冶: 炉の火の前で、金床の鉄を打つ
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.15, halo=(30, 62, 54, 0.9), key=0.8),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=14, bh=8)),
        items=[('forge', dict(x=4, y=44, w=56, h=52)), ('anvil', dict(x=150, base=150, s=1.3)), ('hot_bar', dict(x0=130, x1=166, y=118)),
               ('figure', dict(x=96, foot=154, h=112, arms=('forward', 'raise'), tunic='cloth', apron='leather', head='hair', beard='hair', legs_ramp='cloth', face=True,
                               props=[(1, ('hammer', dict(deg=-60, length=2.4)), True)])),
               ('sparks', dict(pts=[(150, 106), (160, 100), (142, 98), (170, 110), (156, 92)]))]),
    'miller': dict(  # 粉ひき: 夕暮れの風車の前で、粉の袋を担ぐ
        light=dict(pool=(108, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=126, hills=((108, 12, 0.5, 0.6, 5),)),
        items=[('windmill', dict(x=170, base=128, h=100)),
               ('figure', dict(x=84, foot=156, h=110, arms=('lift', 'down'), tunic='paper', apron='paper', head='cap', head_ramp='paper', legs_ramp='cloth', face=True,
                               behind=[(0, ('sack_back', {}))])),
               ('sack', dict(x=130, base=156, r=12))]),
    'elder': dict(  # 年寄り: 大樫の下で杖をつく、白いひげの長老
        light=dict(pool=(108, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('tree', dict(x=178, base=134, h=120, kind='oak', gain=0.9, seed=59)),
               ('figure', dict(x=96, foot=156, h=106, arms=('belly', 'forward'), lean=0.12, robe=True, tunic='leather', mantle='green', head='hood', head_ramp='green', beard='paper', face=True,
                               props=[(1, ('cane', {}), True)]))]),
    'p_wizards': dict(  # 術者たち: 紫の光の陣に立ち、杖を掲げる術者
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 130, 50, 0.5)),
        env=('cave', dict(hz=128, seed=13)),
        items=[('rune_circle', dict(x=112, y=146, rx=90, ry=14, ramp='purple')), ('wisps', dict(pts=[(40, 60), (190, 50), (176, 100)])),
               ('figure', dict(x=112, foot=150, h=112, arms=('raise', 'forward'), robe=True, tunic='blue', trim='gold', head='witch', head_ramp='blue', beard='paper', face=True,
                               props=[(0, ('staff', dict(deg=-90, length=2.0, top='knob', below=3.0)), True), (1, ('orb', dict(r=0.6, ramp='purple')), True)]))]),
    'wizstudent': dict(  # 見習い術士: 蝋燭の書斎で、呪文の書から小さな火花を出す
        light=dict(pool=(112, 100), radius=(150, 100), **WARM, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('shelf', dict(x0=140, x1=222, y=40)), ('books_row', dict(x0=144, x1=218, base=40, seed=17)), ('candle', dict(x=30, base=112, h=14, r=3)),
               ('figure', dict(x=104, foot=154, h=100, arms=('present', 'lift'), robe=True, tunic='blue', head='hair', young=True, face=True,
                               props=[(0, ('book', dict(open_=True, w=1.5, h=1.2, ramp='purple')), True)])),
               ('sparks', dict(pts=[(140, 70), (148, 62), (134, 60), (152, 74)]))]),
    'conjurer': dict(  # 呼び出し屋: 光る陣から、小悪魔を呼び出す
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(150, 120, 50, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('rune_circle', dict(x=150, y=146, rx=60, ry=12, ramp='red')), ('imp', dict(x=156, base=136, s=1.4, ramp='red')),
               ('figure', dict(x=66, foot=154, h=110, arms=('forward', 'lift'), robe=True, tunic='red', trim='gold', head='hood', head_ramp='red', face=True,
                               props=[(1, ('staff', dict(deg=-70, length=2.4, top='knob', below=2.0)), True)]))]),
    'warlock': dict(  # 妖術使い: 墓所で、骨の杖に緑の鬼火をともす
        light=dict(pool=(108, 96), radius=(140, 100), fall=1.2, halo=(70, 40, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, sky_ramp='purple', stars=18, ground_ramp='stone', ground_gain=0.5, clouds=())),
        items=[('gravestones', dict(pts=[(30, 132, 22, 28), (186, 128, 20, 26), (208, 140, 16, 20)])),
               ('figure', dict(x=108, foot=154, h=112, arms=('lift', 'forward'), robe=True, tunic='cloth', mantle='purple', head='hood', head_ramp='cloth', face=True,
                               props=[(0, ('bone_staff', {}), True)])),
               ('will_o_wisp', dict(x=160, y=80, r=6, ramp='green')), ('will_o_wisp', dict(x=186, y=110, r=4, ramp='green'))]),
    'lich': dict(  # 屍術師: 地下墓所の棺の前に立つ、冠をかぶった骸骨の術者
        light=dict(pool=(112, 96), radius=(140, 100), fall=1.2, halo=(112, 60, 60, 0.4)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('sarcophagus', dict(x=150, base=156, w=110, h=26)),
               ('figure', dict(x=100, foot=154, h=114, arms=('lift', 'forward'), robe=True, tunic='purple', trim='gold', mantle='cloth', head='crown', skin='paper',
                               props=[(1, ('orb', dict(r=0.6, ramp='green')), True)])),
               ('skull', dict(x=101, y=50, s=0.95)), ('wisps', dict(pts=[(40, 60), (190, 50)]))]),
}
