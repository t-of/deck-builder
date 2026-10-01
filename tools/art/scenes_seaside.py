"""海辺（cards-seaside.js）の 35 枚の場面データ。書き方は scenes.py の冒頭を見る。"""

SCENES = {
    # ================= 物と場所 =================
    'cove': dict(  # 隠し港: 崖に囲まれた入り江、洞の口に舫った小舟とランタン
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(66, 70, 40, 0.6)),
        env=('coast', dict(hz=96, moon=None, stars=40)),
        items=[
            ('cliff', dict(x0=0, x1=70, top=30, side=1, gain=0.8)),
            ('cliff', dict(x0=224, x1=160, top=24, side=-1, gain=0.65)),
            ('cave_mouth', dict(x=116, base=118, w=80, h=60)),
            ('lantern', dict(x=72, y=84, hang=60)),
            ('boat', dict(x=118, wl=130, w=60)),
            ('rope', dict(x0=92, y0=122, x1=74, y1=96)),
            ('foam', dict(x0=0, x1=224, y=150)),
        ]),
    'beacon': dict(  # かがり火: 岬の石の台で燃える大きな火
        light=dict(pool=(100, 70), radius=(150, 110), fall=1.05, halo=(88, 44, 60, 0.9), key=0.8),
        env=('coast', dict(hz=104, moon=None, stars=20)),
        items=[
            ('cliff', dict(x0=0, x1=150, top=108, side=1, gain=0.9)),
            ('beacon_tower', dict(x=88, base=112, h=52)),
            ('ship', dict(x=190, wl=110, s=0.32, gain=0.55)),
            ('sparks', dict(pts=[(80, 30), (96, 24), (104, 38), (72, 40), (110, 20)])),
        ]),
    'shorevillage': dict(  # 浜の集落: 砂浜に引き上げた舟と、灯りのともる家
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(36, 26, 40, 0.7)),
        env=('coast', dict(hz=84, shore=118, moon=(36, 26, 10))),
        items=[
            ('house', dict(x=10, base=124, w=44, h=28, roof_h=22, roof='wood', windows=[(8, 8, 8, 9, True)], door=(26, 8, 14))),
            ('house', dict(x=150, base=122, w=46, h=30, roof_h=22, roof='red', gain=0.85, windows=[(8, 8, 8, 9, True), (28, 8, 8, 9, True)])),
            ('boat', dict(x=96, wl=146, w=64)),
            ('boat', dict(x=190, wl=154, w=44, ramp='blue', gain=0.9)),
            ('nets', dict(x0=60, x1=96, top=110, base=130)),
        ]),
    'fishtown': dict(  # 漁師町: 桟橋の小屋、干した網と魚
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(46, 50, 40, 0.6)),
        env=('coast', dict(hz=92, moon=None, stars=26)),
        items=[
            ('hut', dict(x=40, base=118, w=50, h=30)),
            ('lantern', dict(x=60, y=76, hang=60)),
            ('dock', dict(y=118)),
            ('fish_rack', dict(x=96, base=150, w=64)),
            ('nets', dict(x0=170, x1=214, top=110, base=146)),
            ('barrel', dict(x=24, base=156, r=12, h=26, gain=0.9)),
        ]),
    'overlook': dict(  # 見晴らし台: 岬の石の露台に据えた遠眼鏡、沖に船
        light=dict(pool=(96, 96), radius=(160, 105), fall=1.05, halo=(40, 24, 40, 0.7)),
        env=('coast', dict(hz=100, moon=(40, 24, 10, 0.4))),
        items=[
            ('ship', dict(x=168, wl=104, s=0.3, gain=0.6)),
            ('ship', dict(x=200, wl=101, s=0.2, gain=0.45, masts=1)),
            ('stone_wall', dict(y0=118, y1=160, gain=0.85, bw=14, bh=7)),
            ('wall', dict(x0=0, x1=224, top=118, bottom=130, merlon=12, gap=8)),
            ('tripod', dict(x=86, base=118, h=48)),
        ]),
    'contraband': dict(  # 抜け荷: 洞窟に揚げた樽と木箱、ランタンの灯
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.15, halo=(40, 60, 40, 0.7)),
        env=('cave', dict(hz=124, seed=11)),
        items=[
            ('lantern', dict(x=40, y=70, hang=30)),
            ('sea', dict(y0=140)),
            ('boat', dict(x=168, wl=150, w=60)),
            ('crate', dict(x=56, y=104, w=34, h=28)), ('crate', dict(x=60, y=80, w=24, h=24, gain=1.05)),
            ('barrel', dict(x=120, base=136, r=14, h=34)),
            ('barrel', dict(x=150, base=134, r=12, h=28, lying=True, gain=0.9)),
            ('sack', dict(x=26, base=136, r=11)),
        ]),
    'storeroom': dict(  # 納戸: 船倉の棚、巻いた綱、樽、揺れるランタン
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(110, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=114, floor='planks')),
        items=[
            ('beam', dict(y=0)),
            ('lantern', dict(x=112, y=36, hang=6)),
            ('shelf', dict(x0=10, x1=96, y=60)),
            ('bottle', dict(x=24, base=60, h=14, r=4, ramp='green')), ('bottle', dict(x=40, base=60, h=10, r=5, ramp='blue')),
            ('sack', dict(x=66, base=60, r=8)), ('bottle', dict(x=86, base=60, h=12, r=4, ramp='red')),
            ('tool_rack', dict(x0=130, x1=220, y=20, tools=('coil', 'coil', 'saw2'), s=1.4)),
            ('barrel', dict(x=40, base=146, r=17, h=40)),
            ('barrel', dict(x=180, base=150, r=16, h=40, lying=True)),
            ('crate', dict(x=88, y=118, w=34, h=28, gain=0.95)),
        ]),
    'compass': dict(  # 羅針盤: 天鵞絨の上の真鍮の羅針盤
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(28, 34, 40, 0.5)),
        env=('icon', dict(hz=74, wall='plank', cloth='blue', cloth_gain=0.7)),
        items=[('candle', dict(x=28, base=72, h=12, r=3)), ('compass_rose', dict(x=112, y=112, r=44))]),
    'searoute': dict(  # 航路図: 海図に引いた点線の航路と両脚器
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(30, 52, 40, 0.6)),
        env=('room', dict(wall='stone', hz=78, floor='table')),
        items=[
            ('candle', dict(x=28, base=76, h=12, r=3)),
            ('window_arch', dict(x=150, y=6, w=30, h=56)),
            ('sea_chart', dict(x=112, y=118, w=170, h=58)),
            ('dividers', dict(x=160, y=128, ln=44)),
            ('ship_model', dict(x=56, y=104)),
        ]),
    'islet': dict(  # 小島: 月夜の海に浮かぶ椰子と草葺きの小屋
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(40, 24, 40, 0.7)),
        env=('coast', dict(hz=104, moon=(40, 24, 11))),
        items=[
            ('island', dict(x=118, wl=126, w=140, h=30)),
            ('hut', dict(x=140, base=110, w=30, h=16)),
            ('palm', dict(x=92, base=110, h=62, lean=-0.25)),
            ('palm', dict(x=166, base=108, h=46, lean=0.3)),
        ]),
    'oldmap': dict(  # 宝の絵図: 2 つに破れた絵図、合わせると ✕ が現れる
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(28, 40, 40, 0.6)),
        env=('icon', dict(hz=60, wall='plank', cloth='wood', cloth_gain=0.75)),
        items=[('candle', dict(x=26, base=58, h=12, r=3)), ('map_pieces', dict(x=112, y=108)),
               ('coin', dict(cx=196, cy=146, r=9, metal='gold')), ('coin', dict(cx=30, cy=148, r=8, metal='gold', stamp='star'))]),
    'barricade': dict(  # 通せんぼ: 港の道をふさぐ尖った杭の柵
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(30, 56, 40, 0.7)),
        env=('coast', dict(hz=92, shore=130, moon=None)),
        items=[
            ('torch', dict(x=24, y=56)),
            ('ship', dict(x=170, wl=96, s=0.3, gain=0.5)),
            ('barricade', dict(x=112, base=146, w=180)),
            ('crate', dict(x=10, y=124, w=30, h=24, gain=0.85)),
        ]),
    'rockpool': dict(  # 磯: 岩の潮だまりに、ひとで・蟹・貝・海藻
        light=dict(pool=(112, 110), radius=(160, 105), fall=1.05, halo=None),
        env=('coast', dict(hz=70, shore=None, moon=None)),
        items=[
            ('rocks', dict(pts=[(30, 130, 90, 50), (190, 126, 90, 54), (112, 104, 120, 22)])),
            ('tide_pool', dict(x=112, y=136, rx=78, ry=20)),
            ('rocks', dict(pts=[(20, 160, 70, 26), (200, 160, 80, 24)])),
            ('seaweed', dict(x=60, base=146, h=22)), ('seaweed', dict(x=160, base=144, h=18)),
            ('starfish', dict(x=92, y=138, r=10, ramp='red')), ('starfish', dict(x=150, y=144, r=7, ramp='gold')),
            ('crab', dict(x=124, y=122, s=1.0)),
            ('shell', dict(x=40, y=152, r=6)), ('shell', dict(x=184, y=150, r=5)),
        ]),
    'openmarket': dict(  # 朝市: 夜明けの港、魚とかごの並ぶ屋台
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.0, halo=(40, 80, 50, 0.5)),
        env=('coast', dict(hz=86, moon=None, sky_ramp='dawn', stars=0, clouds=((40, 90, 8), (60, 70, 6)), sea_gain=1.15)),
        items=[
            ('dock', dict(y=104, posts=False)),
            ('stall', dict(x0=30, x1=196, top=50, base=146, colors=('blue', 'paper'), counter='crates')),
            ('basket', dict(x=58, base=124, w=28, h=10, kind='fish', n=4)),
            ('basket', dict(x=94, base=124, w=28, h=10, kind='apple', fill='red', n=8)),
            ('basket', dict(x=130, base=124, w=28, h=10, kind='bread', n=5)),
            ('basket', dict(x=166, base=124, w=28, h=10, kind='fish', n=4)),
            ('basket', dict(x=200, base=154, w=30, h=12, kind='cabbage', n=5)),
        ]),
    'tradeship': dict(  # 交易船: 帆いっぱいに風を受け、荷を積んで進む
        light=dict(pool=(108, 76), radius=(170, 110), fall=1.0, halo=(30, 22, 40, 0.7)),
        env=('coast', dict(hz=112, moon=(30, 22, 10))),
        items=[('ship', dict(x=120, wl=134, s=0.95, sails='paper', flag='blue', masts=2)), ('foam', dict(x0=50, x1=190, y=138))]),
    'fort': dict(  # 出城: 岩の上の円い砦、打ち寄せる波
        light=dict(pool=(112, 86), radius=(160, 105), fall=1.1, halo=(30, 22, 40, 0.7)),
        env=('coast', dict(hz=110, moon=(30, 22, 10, 0.5))),
        items=[('sea_fort', dict(x=118, base=128))]),
    'coffer': dict(  # 金蔵: 厚い鉄の扉が開き、棚に金の山
        light=dict(pool=(104, 92), radius=(150, 100), fall=1.15, halo=(20, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=128, floor='flag', bw=20, bh=10)),
        items=[('torch', dict(x=18, y=40)), ('vault_door', dict(x=96, base=128, w=80, h=104)),
               ('stack', dict(cx=40, base=152, r=10, n=6, metal='gold', seed=21)), ('coin', dict(cx=186, cy=150, r=9, metal='gold'))]),
    'pier': dict(  # 波止場: 沖へ伸びる長い桟橋、杭の灯、舫った船
        light=dict(pool=(112, 104), radius=(160, 110), fall=1.05, halo=(112, 70, 40, 0.5)),
        env=('coast', dict(hz=84, moon=(48, 22, 9))),
        items=[
            ('ship', dict(x=176, wl=96, s=0.35, gain=0.65)),
            ('long_pier', dict(x=112, y0=86, y1=160, w0=8, w1=110)),
            ('lantern', dict(x=112, y=70, hang=58)),
            ('boat', dict(x=40, wl=130, w=50, ramp='red', gain=0.85)),
            ('barrel', dict(x=150, base=150, r=11, h=24)),
        ]),
    'privateer': dict(  # 私掠船: 赤い帆と髑髏の旗、砲の煙
        light=dict(pool=(108, 76), radius=(170, 110), fall=1.0, halo=None),
        env=('coast', dict(hz=112, moon=None)),
        items=[('ship', dict(x=112, wl=134, s=0.95, sails='red', hull='wood', kind='pirate', masts=2)),
               ('smoke', dict(pts=[(40, 120), (30, 110), (176, 122)])), ('foam', dict(x0=40, x1=180, y=138))]),
    'raidship': dict(  # 略奪船: 縞の帆、舷に並ぶ盾、櫂の列
        light=dict(pool=(108, 86), radius=(170, 110), fall=1.0, halo=None),
        env=('coast', dict(hz=100, moon=None)),
        items=[('ship', dict(x=114, wl=140, s=0.9, kind='longship', masts=1, hull='wood')), ('foam', dict(x0=30, x1=190, y=146))]),
    'fogship': dict(  # 霧の船: 灯のない白い船が、霧の帯から現れる
        light=dict(pool=(112, 86), radius=(170, 110), fall=1.0, halo=(40, 24, 40, 0.5)),
        env=('coast', dict(hz=118, moon=(40, 24, 10, 0.6), stars=10)),
        items=[
            ('fog', dict(bands=[(60, 10)])),
            ('ship', dict(x=118, wl=136, s=0.9, sails='stone', hull='stone', kind='ghost', masts=2, gain=0.85)),
            ('fog', dict(bands=[(110, 14), (140, 12)])),
        ]),
    'injunction': dict(  # 差し止め: 封印の触れ書きと、鎖でつないだ荷
        light=dict(pool=(112, 92), radius=(150, 100), fall=1.15, halo=(20, 42, 40, 0.7)),
        env=('room', dict(wall='stone', hz=120, floor='flag')),
        items=[
            ('torch', dict(x=18, y=42)),
            ('crate', dict(x=128, y=102, w=40, h=36)), ('crate', dict(x=138, y=72, w=30, h=30, gain=1.05)),
            ('chain', dict(x0=120, y0=96, x1=196, y1=136, r=3)),
            ('chain', dict(x0=124, y0=136, x1=194, y1=92, r=3)),
            ('notice', dict(x=74, top=34, w=56, h=64)),
        ]),
    # ================= 人物・動物 =================
    'gibbon': dict(  # 手長猿: 帆綱に長い腕でぶら下がり、片手を伸ばす
        light=dict(pool=(104, 80), radius=(150, 105), fall=1.1, halo=(40, 60, 30, 0.5)),
        env=('coast', dict(hz=128, moon=None)),
        items=[
            ('rope', dict(x0=60, y0=0, x1=110, y1=56)), ('rope', dict(x0=0, y0=40, x1=224, y1=20)),
            ('monkey2', dict(x=106, y=66, s=1.9)),
            ('ship_rail', dict(y=134)),
        ]),
    'wagon': dict(  # 荷馬車: 海沿いの道を、馬が幌の荷車を引く
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(150, 70, 30, 0.5)),
        env=('coast', dict(hz=96, shore=118, moon=None)),
        items=[
            ('wagon', dict(x=150, base=146, w=78)),
            ('lantern', dict(x=150, y=80, hang=72)),
            ('harness', dict(x0=84, y0=106, x1=116, y1=118)),
            ('horse', dict(x=70, base=148, s=1.05)),
        ]),
    'snatcher': dict(  # ひったくり: 財布をつかんで桟橋を駆け去る
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(44, 50, 40, 0.6)),
        env=('coast', dict(hz=96, moon=None)),
        items=[
            ('lantern', dict(x=44, y=70, hang=40)),
            ('dock', dict(y=120)),
            ('figure', dict(x=118, foot=154, h=110, facing=-1, arms=('aim', 'down'), legs='stride', lean=0.15, tunic='cloth', head='hood', head_ramp='cloth',
                            cloak='red', legs_ramp='cloth', props=[(1, ('bag', dict(ramp='red')), True)])),
            ('coin', dict(cx=176, cy=146, r=6, metal='copper', stamp='pip')), ('coin', dict(cx=188, cy=152, r=5, metal='copper', stamp='star')),
        ]),
    'salvor': dict(  # 引き上げ屋: 綱をたぐって、海から宝箱を引き上げる
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=None),
        env=('coast', dict(hz=90, moon=None)),
        items=[
            ('dock', dict(y=124, x0=0, x1=150)),
            ('chest', dict(x=162, base=148, w=44, h=22, open_=False, band='silver')),
            ('rope', dict(x0=127, y0=70, x1=184, y1=128)),
            ('foam', dict(x0=150, x1=220, y=150)),
            ('figure', dict(x=72, foot=152, h=110, facing=1, arms=('pull', 'aim'), legs='stride', lean=-0.08, tunic='blue', head='cap', head_ramp='red',
                            legs_ramp='cloth')),
        ]),
    'deckhand': dict(  # 水夫: 甲板で綱の束を担ぐ縞の服の男
        light=dict(pool=(108, 86), radius=(150, 100), fall=1.1, halo=(186, 40, 30, 0.5)),
        env=('coast', dict(hz=112, moon=None)),
        items=[
            ('mast', dict(x=186, top=0, base=140)),
            ('lantern', dict(x=186, y=48, hang=30)),
            ('dock', dict(y=132, posts=False)),
            ('ship_rail', dict(y=124)),
            ('figure', dict(x=100, foot=154, h=112, arms=('hip', 'lift'), tunic='blue', head='cap', head_ramp='red', legs_ramp='paper',
                            props=[(1, ('coil_held', {}), True)])),
            ('barrel', dict(x=40, base=156, r=13, h=28)),
        ]),
    'strategist': dict(  # 軍師: 壁の沿岸図を指し棒で示す
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.15, halo=(20, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('wall_map', dict(x0=114, y0=20, x1=214, y1=94)),
            ('figure', dict(x=78, foot=154, h=112, arms=('chest', 'aim'), robe=True, tunic='blue', trim='gold', mantle='red', head='hat', head_ramp='cloth',
                            props=[(1, ('staff', dict(deg=-20, length=2.6, below=0.4)), True)])),
        ]),
    'buccaneer': dict(  # 海の荒くれ: 船刀を構え、宝箱に足をかける
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.7)),
        env=('coast', dict(hz=104, shore=136, moon=(30, 22, 10, 0.4))),
        items=[
            ('ship', dict(x=176, wl=106, s=0.32, sails='red', kind='pirate', gain=0.55)),
            ('chest', dict(x=126, base=154, w=48, h=24, fill='gold')),
            ('figure', dict(x=90, foot=154, h=112, arms=('hip', 'raise'), legs='stride', tunic='red', cloak='cloth', head='hat', head_ramp='cloth',
                            legs_ramp='cloth', props=[(1, ('cutlass', {}), True)])),
        ]),
    'siren': dict(  # 人魚の呪い: 岩の上で歌う人魚、紫の気配
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.1, halo=(34, 24, 40, 0.7)),
        env=('coast', dict(hz=108, moon=(34, 24, 10), sky_ramp='purple', stars=20)),
        items=[
            ('wisps', dict(pts=[(170, 40), (40, 70)])),
            ('figure', dict(x=104, foot=150, h=108, arms=('lift', 'belly'), robe=True, tunic='green', head='long', hair='red')),
            ('rocks', dict(pts=[(110, 160, 140, 54)])),
            ('mermaid_tail', dict(x=160, y=128)),
            ('foam', dict(x0=30, x1=200, y=150)),
        ]),
    'diver': dict(  # 海女: 岩場から上がり、真珠の貝を掲げる
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.1, halo=None),
        env=('coast', dict(hz=104, moon=None)),
        items=[
            ('tub', dict(x=176, wl=136, r=16)),
            ('rocks', dict(pts=[(70, 160, 150, 26)])),
            ('figure', dict(x=90, foot=152, h=110, arms=('lift', 'down'), tunic='paper', head='long', hair='hair', legs_ramp='paper', belt='red',
                            props=[(0, ('pearl', {}), True)])),
        ]),
    'emissary': dict(  # 特使: 港に降り立ち、宝石の小箱を差し出す
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=None),
        env=('coast', dict(hz=104, moon=None)),
        items=[
            ('ship', dict(x=176, wl=110, s=0.4, sails='paper', flag='purple', gain=0.6)),
            ('dock', dict(y=130, posts=True)),
            ('figure', dict(x=96, foot=154, h=112, arms=('present', 'present'), robe=True, tunic='gold', trim='red', mantle='purple', head='coif', head_ramp='paper',
                            props=[(1, ('casket', {}), True)])),
        ]),
    'pilot': dict(  # 水先案内: 小舟で竿の灯を掲げ、船を港へ導く
        light=dict(pool=(104, 80), radius=(150, 100), fall=1.1, halo=(56, 30, 40, 0.8)),
        env=('coast', dict(hz=100, moon=None)),
        items=[
            ('ship', dict(x=184, wl=104, s=0.4, gain=0.55)),
            ('figure', dict(x=104, foot=150, h=104, arms=('lift', 'low'), tunic='green', cloak='leather', head='hat', head_ramp='leather',
                            props=[(0, ('staff', dict(deg=-110, length=2.6, top='lantern', below=1.0)), True)])),
            ('boat', dict(x=110, wl=150, w=110, oars=True)),
        ]),
    'crone': dict(  # 磯の老婆: 曲がった杖をつき、紫の呪いをつぶやく
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.15, halo=(64, 40, 40, 0.7)),
        env=('cave', dict(hz=130, seed=6)),
        items=[
            ('sea', dict(y0=140)),
            ('wisp_candle', dict(x=40, base=134)),
            ('wisps', dict(pts=[(150, 60), (176, 96)])),
            ('figure', dict(x=110, foot=152, h=100, arms=('present', 'lift'), lean=0.2, robe=True, tunic='cloth', head='hood', head_ramp='purple',
                            mantle='purple', props=[(0, ('cane', {}), True), (1, ('orb', dict(r=0.55)), True)])),
        ]),
    'pioneer': dict(  # 開墾者: 夜明けの新しい浜に旗を立て、鋤で土を起こす
        light=dict(pool=(104, 90), radius=(160, 105), fall=1.05, halo=None),
        env=('coast', dict(hz=86, shore=112, moon=None, sky_ramp='dawn', stars=0)),
        items=[
            ('ground', dict(y0=128, ramp='leather', gain=0.8, wave=1.0, seed=7, tufts=False)),
            ('stump', dict(x=184, base=150, r=14, h=10, log=False)),
            ('furrows', dict(y0=134)),
            ('flag_pole', dict(x=40, base=134, ramp='blue')),
            ('figure', dict(x=110, foot=154, h=110, arms=('chest', 'low'), tunic='leather', head='hat', head_ramp='leather', legs_ramp='green',
                            props=[(1, ('spade', {}), True)])),
        ]),
}
