"""夜想曲（cards-nocturne.js）の 77 枚の場面データ。書き方は scenes.py の冒頭を見る。
恵み 12 は夜明け・昼の光（日・月・川・海などの自然）、呪詛 12 と状態 5 は紫の夜、家宝 7 は暖かい灯の小物、
精霊と屍と札は夜の怪異。夜の札ばかりなので、恵みの明るさで散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.75):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _hex(hz=124, ground='stone', gain=0.5, moon=None):
    return ('night', dict(hz=hz, moon=moon, sky_ramp='purple', stars=20, ground_ramp=ground, ground_gain=gain, clouds=()))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.55, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


RAYS = ('light_rays', dict(x=112, y=34, n=11, ln=100))

SCENES = {
    # ================= 恵み 12 =================
    'b_earth': dict(  # 大地の加護: 光の差す岩山と、芽吹く花
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=128),
        items=[RAYS, ('rocks', dict(pts=[(112, 136, 140, 60), (40, 140, 60, 26)], gain=0.9)), ('flowers', dict(rows=[(146, 4.0, 22)])), ('sprout_pot', dict(x=180, base=150))]),
    'b_field': dict(  # 田の加護: 光の注ぐ実りの田と稲の束
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=104, ground='leather'),
        items=[RAYS, ('wheat_field', dict(y0=108)), ('wheat_sheaves', dict(x=40, base=154, n=3))]),
    'b_flame': dict(  # 火の加護: 石の台に燃える清めの火
        light=dict(pool=(112, 96), radius=(150, 100), halo=(112, 90, 70, 0.8), fall=1.05, key=0.8),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('niche', dict(x=112, top=10, w=80, h=100)), ('bonfire', dict(x=112, base=148, s=0.9)), ('sparks', dict(pts=[(100, 50), (124, 40), (110, 30), (130, 56)]))]),
    'b_forest': dict(  # 林の加護: 木々の間から差し込む光の筋
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=61)),
        items=[('light_beam', dict(x0=60, y0=0, x1=120, y1=150, w0=10, w1=50, ramp='gold')), ('light_beam', dict(x0=150, y0=0, x1=170, y1=150, w0=8, w1=30, ramp='gold')),
               ('mushrooms', dict(x=40, base=152)), ('deer', dict(x=150, base=150, s=1.0, facing=-1))]),
    'b_moon': dict(  # 月の加護: 湖に映る大きな満月
        light=dict(pool=(112, 90), radius=(170, 110), fall=1.0, halo=(112, 50, 60, 0.7)),
        env=('coast', dict(hz=104, moon=(112, 50, 24), stars=40, clouds=())),
        items=[('reeds', dict(xs=(10, 26, 196, 212), base=150)), ('rocks', dict(pts=[(30, 160, 70, 20), (200, 160, 60, 18)]))]),
    'b_mountain': dict(  # 峰の加護: 朝日に輝く雪の峰
        light=dict(pool=(112, 70), radius=(180, 110), **DAWN),
        env=_dawn(hz=140, ground='stone', hills=()),
        items=[('peaks', dict()), ('sun', dict(x=40, y=40, r=12))]),
    'b_river': dict(  # 流れの加護: 夜明けの谷をうねって流れる川
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=96),
        items=[('river', dict(y0=96)), ('tree', dict(x=30, base=120, h=60, kind='oak', gain=0.7, seed=91)), ('tree', dict(x=200, base=130, h=66, kind='pine', gain=0.7, seed=92))]),
    'b_sea': dict(  # 潮の加護: 夜明けの海、寄せる白い波
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=96, shore=138, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 100, 8),))),
        items=[('sun', dict(x=60, y=92, r=16)), ('foam', dict(x0=0, x1=224, y=120)), ('foam', dict(x0=0, x1=224, y=134)), ('shell', dict(x=150, y=150, r=7))]),
    'b_sky': dict(  # 天の加護: 雲の切れ間から降りる後光
        light=dict(pool=(112, 70), radius=(180, 120), **DAWN),
        env=('night', dict(hz=150, moon=None, sky_ramp='dawn', stars=0, ground_ramp='foliage', ground_gain=0.7, clouds=((40, 120, 12), (70, 100, 10), (96, 120, 8)))),
        items=[('sun', dict(x=112, y=30, r=14)), ('light_rays', dict(x=112, y=30, n=13, ln=140)), ('hills', dict(base=150, amp=16, gain=0.7, depth=0.2, seed=2)), ('house', dict(x=100, base=150, w=24, h=12, roof_h=10, roof='red', windows=[(6, 3, 5, 5, True)]))]),
    'b_sun': dict(  # 日の加護: 地平から昇る大きな日
        light=dict(pool=(112, 100), radius=(180, 120), **DAWN),
        env=_dawn(hz=112, hills=((112, 16, 0.6, 0.4, 4),)),
        items=[('sun', dict(x=112, y=108, r=34)), ('light_rays', dict(x=112, y=108, n=13, ln=110)), ('hills', dict(base=118, amp=10, gain=0.6, depth=0.3, seed=7))]),
    'b_swamp': dict(  # 沼地の加護: 沼の上をただよう青い鬼火
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(112, 70, 40, 0.4)),
        env=_night(moon=None, ground=None, hz=118),
        items=[('bog', dict(y0=118)), ('tree', dict(x=196, base=124, h=80, kind='dead', ramp='cloth', gain=0.6, seed=93)), ('reeds', dict(xs=(20, 40), base=150)),
               ('will_o_wisp', dict(x=112, y=80, r=7)), ('will_o_wisp', dict(x=60, y=100, r=4)), ('will_o_wisp', dict(x=160, y=96, r=5))]),
    'b_wind': dict(  # 風の加護: 草原を渡る風に舞う葉
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=112),
        items=[('wind_streaks', dict()), ('windmill', dict(x=180, base=120, h=70)), ('leaves', dict(n=24))]),
    # ================= 呪詛 12 =================
    'h_omens': dict(  # 不吉: ほうき星の下、枯れ木に群れる鴉
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.5)),
        env=_hex(),
        items=[('comet', dict(x=40, y=26)), ('tree', dict(x=130, base=130, h=110, kind='dead', ramp='cloth', gain=0.7, seed=94)),
               ('raven', dict(x=100, y=70, s=1.2)), ('raven', dict(x=150, y=56, s=1.0, facing=-1)), ('raven', dict(x=170, y=90, s=1.1, facing=-1))]),
    'h_delusion': dict(  # まどわし: 頭のまわりを紫の渦がめぐる
        light=dict(pool=(112, 86), radius=(150, 100), fall=1.1),
        env=_hex(ground='stone'),
        items=[('figure', dict(x=112, foot=154, h=110, arms=('lift', 'lift'), tunic='cloth', head='hair', legs_ramp='cloth', face=True)), ('spiral_dizzy', dict(x=112, y=34, r=30)),
               ('spiral_dizzy', dict(x=60, y=80, r=14)), ('spiral_dizzy', dict(x=170, y=86, r=14))]),
    'h_envy': dict(  # 妬み: 闇に光る緑の目と、金貨へ伸びる手
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.15),
        env=('room', dict(wall='stone', hz=110, floor='table')),
        items=[('green_eyes', dict(x=112, y=50)), ('grasping_hands', dict(pts=[(10, 100, 15), (214, 96, 165)])), ('stack', dict(cx=112, base=150, r=12, n=6, metal='gold', seed=91))]),
    'h_famine': dict(  # 不作: 干からびた畑と、空の椀
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.0),
        env=_hex(hz=110, ground='leather'),
        items=[('furrows', dict(y0=116)), ('tree', dict(x=60, base=130, h=80, kind='dead', ramp='wood', gain=0.7, seed=97)), ('raven', dict(x=72, y=78, s=1.1, facing=-1)),
               ('weeds', dict(x=150, base=140, n=10, h=16, ramp='leather')), ('weeds', dict(x=190, base=146, n=8, h=12, ramp='leather')),
               ('bowl_floor', dict(x=112, base=152)), ('skull', dict(x=150, y=152, s=0.8))]),
    'h_fear': dict(  # おびえ: 一本の蝋燭に、闇から影の手が伸びる
        light=dict(pool=(112, 110), radius=(120, 80), fall=1.3, halo=(112, 120, 40, 0.6)),
        env=('room', dict(wall='stone', hz=126, floor='flag')),
        items=[('candle', dict(x=112, base=146, h=14, r=4)), ('grasping_hands', dict(pts=[(0, 60, 25), (224, 70, 155), (0, 140, -10), (224, 130, 190)]))]),
    'h_greed': dict(  # 欲ばり: 銅貨の山を抱え込む、骨ばった手
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.15, halo=(30, 40, 40, 0.4)),
        env=('room', dict(wall='stone', hz=100, floor='table', floor_ramp='purple', floor_gain=0.5)),
        items=[('candle', dict(x=28, base=98, h=10, r=3)), ('pile', dict(cx=112, base=150, w=60, h=26, metal='copper', r=9, count=24, seed=15, stamps=('pip', 'star'))),
               ('grasping_hands', dict(pts=[(30, 120, 10), (194, 116, 170)]))]),
    'h_haunting': dict(  # 取り憑き: 寝台の上にのしかかる亡霊
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='stone', hz=118, floor='planks')),
        items=[('window_arch', dict(x=24, y=10, w=30, h=56)), ('bed', dict(x=130, base=150, w=150)), ('ghosts', dict(pts=[(130, 92)])), ('ghosts', dict(pts=[(170, 70)]))]),
    'h_locusts': dict(  # イナゴ: 畑を覆い尽くす虫の群れ
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.0),
        env=_hex(hz=110, ground='leather', gain=0.6),
        items=[('wheat_field', dict(y0=112)), ('locust_swarm', dict(x=112, y=70, n=140, w=110, h=50, seed=3))]),
    'h_misery': dict(  # 不幸: 雨雲の下でうずくまる人
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1),
        env=_hex(hz=124),
        items=[('rain_cloud', dict(x=112, y=40, w=100)),
               ('figure', dict(x=112, foot=154, h=94, arms=('chest', 'chest'), legs='crouch', lean=0.2, tunic='cloth', head='hood', head_ramp='cloth', legs_ramp='cloth'))]),
    'h_plague': dict(  # はやり病: 嘴の面の医者が、霧の路地に立つ
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.5)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)),
               ('figure', dict(x=112, foot=154, h=114, arms=('belly', 'lift'), robe=True, tunic='cloth', head='beak', head_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-92, length=2.2, below=3.0)), True)])), ('fog', dict(bands=[(140, 10)], gain=0.7)), ('wisps', dict(pts=[(170, 60)]))]),
    'h_poverty': dict(  # 貧窮: 口の開いた空の巾着と、銅貨一枚
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(30, 40, 40, 0.4)),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=6, r=3)), ('empty_purse', dict(x=112, base=146)), ('coin', dict(cx=170, cy=150, r=7, metal='copper', stamp='pip', gain=0.7))]),
    'h_war': dict(  # いくさ: 燃える城を背に、交差する剣
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.05, halo=(112, 80, 60, 0.6)),
        env=_hex(hz=130),
        items=[('castle', dict(x=112, base=120, s=0.7, roof='red')), ('fire_line', dict(y=110)), ('smoke_column', dict(x=112, y=60, h=60)),
               ('crossed_swords', dict(x=112, y=130))]),
    # ================= 状態 5 =================
    's_lost': dict(  # 森の迷い子: 霧の森で立ちすくむ子
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1),
        env=('forest', dict(hz=124, moon=None, seed=63)),
        items=[('fog', dict(bands=[(116, 12), (140, 10)], gain=0.8)),
               ('figure', dict(x=112, foot=154, h=84, arms=('chest', 'chest'), tunic='red', head='hood', head_ramp='red', legs_ramp='cloth', face=True))]),
    's_deluded': dict(  # 惑い: 渦に目を回す男
        light=dict(pool=(112, 88), radius=(150, 100), fall=1.1),
        env=_hex(ground='stone'),
        items=[('figure', dict(x=112, foot=154, h=108, arms=('lift', 'down'), legs='stride', lean=-0.08, tunic='green', head='cap', head_ramp='cloth', legs_ramp='cloth', face=True)),
               ('spiral_dizzy', dict(x=124, y=36, r=22))]),
    's_envious': dict(  # 妬み心: 他人の金を横目でにらむ緑の顔
        light=dict(pool=(112, 88), radius=(150, 100), fall=1.1),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('figure', dict(x=80, foot=154, h=110, arms=('chest', 'belly'), tunic='green', skin='green', head='hair', legs_ramp='cloth', face=True)),
               ('chest', dict(x=140, base=154, w=56, h=26, fill='silver'))]),
    's_miserable': dict(  # ふしあわせ: 雨の中にひとり座り込む
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1),
        env=_hex(hz=124),
        items=[('rain_cloud', dict(x=112, y=40, w=80)),
               ('figure', dict(x=112, foot=154, h=90, arms=('chest', 'chest'), legs='crouch', lean=0.18, tunic='blue', head='hair', legs_ramp='cloth')), ('rain', dict(n=80, seed=4))]),
    's_twice': dict(  # ふしあわせ×2: 二つの雨雲の下で、さらに深くうなだれる
        light=dict(pool=(112, 108), radius=(140, 90), fall=1.25),
        env=_hex(hz=124, gain=0.4),
        items=[('rain_cloud', dict(x=70, y=34, w=80)), ('rain_cloud', dict(x=160, y=46, w=80)),
               ('figure', dict(x=112, foot=154, h=84, arms=('chest', 'chest'), legs='crouch', lean=0.3, tunic='cloth', head='hood', head_ramp='cloth', legs_ramp='cloth')), ('rain', dict(n=160, seed=5))]),
    # ================= 家宝 7 =================
    'dimmirror': dict(  # 曇り鏡: 燭台の前の、曇った手鏡
        light=dict(pool=(112, 98), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=118, wall='stone', cloth='purple', cloth_gain=0.55)),
        items=[('candelabra', dict(x=30, base=114, h=24)), ('mirror_stand', dict(x=120, base=152, h=110))]),
    'luckycoin': dict(  # 福銭: 赤い紐を通した、四角い穴の銭
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=126, wall='plank', cloth='red', cloth_gain=0.6)),
        items=[('holed_coin', dict(x=112, y=82, r=36))]),
    'kid': dict(  # 子山羊: 夜明けの野で跳ねる子山羊
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=120),
        items=[('fence', dict(x0=0, x1=224, base=136, h=14, gain=0.6)), ('goat', dict(x=112, base=152, s=2.0, facing=-1))]),
    'cursedcoin': dict(  # 祟り金: 紫の煙を立てる、呪われた金貨
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=104, wall='stone', cloth='purple', cloth_gain=0.5)),
        items=[('coin', dict(cx=112, cy=124, r=26, metal='gold', stamp='crown', tilt=0.6)), ('wisps', dict(pts=[(112, 90), (90, 80), (134, 84)])), ('skull', dict(x=40, y=140, s=0.8))]),
    'wishlamp': dict(  # 願いの灯: 金の油差しのランプから立つ光の煙
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1),
        env=('icon', dict(hz=124, wall='stone', cloth='red', cloth_gain=0.55)),
        items=[('oil_lamp', dict(x=84, base=150, s=1.2))]),
    'grazing': dict(  # 放牧地: 柵の中で草をはむ羊と山羊
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=116),
        items=[('fence', dict(x0=0, x1=224, base=128, h=14, gain=0.6)), ('sheep', dict(x=60, base=148, s=1.4)), ('sheep', dict(x=150, base=140, s=1.1, facing=-1)),
               ('goat', dict(x=186, base=156, s=1.0)), ('hut', dict(x=40, base=118, w=40, h=20))]),
    'purse': dict(  # 巾着: 紐を絞った布の巾着と、こぼれた銭
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('money_bag', dict(x=100, base=148, r=30, ramp='red'))]),
    # ================= 精霊・願い・夜の羽 =================
    'wisp': dict(  # 鬼火: 夜の森をただよう青い火の玉
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(112, 80, 40, 0.4)),
        env=('forest', dict(hz=124, moon=None, seed=65)),
        items=[('will_o_wisp', dict(x=112, y=84, r=10)), ('will_o_wisp', dict(x=50, y=110, r=5)), ('will_o_wisp', dict(x=170, y=70, r=6))]),
    'imp2': dict(  # 小悪魔: 蝙蝠の羽の、赤い小鬼
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('cave', dict(hz=134, seed=67)),
        items=[('imp', dict(x=112, base=146, s=2.2)), ('wisp_candle', dict(x=30, base=150))]),
    'phantom': dict(  # 亡霊: 墓地に立つ、透ける大きな亡霊
        light=dict(pool=(112, 90), radius=(150, 100), fall=1.1, halo=(36, 24, 40, 0.6)),
        env=_night(moon=(36, 24, 11, 0.4), ground='stone'),
        items=[('gravestones', dict(pts=[(40, 148, 16, 26), (190, 150, 16, 26)])), ('big_ghost', dict(x=112, y=96, s=2.4))]),
    'wish2': dict(  # 願い事: 両手で受けた流れ星の光
        light=dict(pool=(112, 90), radius=(150, 100), fall=1.1),
        env=_night(moon=None, stars=60),
        items=[('shooting_star', dict(x=126, y=30)), ('figure', dict(x=112, foot=154, h=100, arms=('present', 'present'), robe=True, gown=True, tunic='blue', head='long', hair='hair', face=True)),
               ('will_o_wisp', dict(x=112, y=86, r=5, ramp='gold'))]),
    'nightwing': dict(  # 夜の羽: 月をよぎる蝙蝠の群れ
        light=dict(pool=(112, 80), radius=(170, 110), fall=1.0, halo=(112, 60, 70, 0.7)),
        env=_night(moon=(112, 60, 30), ground=None, stars=30),
        items=[('bats', dict(pts=[(90, 50, 2.6), (130, 70, 2.2), (70, 90, 1.8), (160, 40, 1.6), (150, 96, 2.0), (40, 60, 1.4)])), ('tower', dict(x=180, base=160, w=36, h=70, roof='purple'))]),
    # ================= 屍 3 =================
    'z_apprentice': dict(  # 屍の弟子: 墓場で古い書を抱える、青白い屍
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(36, 24, 40, 0.6)),
        env=_night(moon=(36, 24, 11, 0.5), ground='leather'),
        items=[('gravestones', dict(pts=[(170, 146, 16, 28), (200, 150, 14, 22)])),
               ('figure', dict(x=100, foot=154, h=108, arms=('chest', 'down'), lean=0.08, robe=True, tunic='cloth', skin='green', head='hair', hair='paper', face=True,
                               props=[(0, ('book', dict(w=1.6, h=1.2, ramp='purple')), True)]))]),
    'z_mason': dict(  # 屍の石工: 墓石の前で、槌を振り上げる屍
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(36, 24, 40, 0.6)),
        env=_hex(hz=124, ground='leather'),
        items=[('gravestones', dict(pts=[(170, 150, 22, 40)])),
               ('figure', dict(x=96, foot=154, h=108, arms=('forward', 'raise'), legs='stride', tunic='cloth', apron='leather', skin='green', head='hair', face=True,
                               props=[(1, ('hammer', dict(deg=-60, length=2.2)), True)]))]),
    'z_spy': dict(  # 屍の密偵: 墓石の陰から遠眼鏡で覗く屍
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.1, halo=(36, 24, 40, 0.6)),
        env=_night(moon=None, ground='leather', stars=40),
        items=[('lantern', dict(x=30, y=60, hang=30)), ('figure', dict(x=96, foot=154, h=104, arms=('down', 'eye'), legs='crouch', lean=0.1, tunic='cloth', cloak='cloth', skin='green', head='hood', head_ramp='cloth',
                               props=[(1, ('spyglass', dict(length=2.2)), True)])),
               ('gravestones', dict(pts=[(80, 158, 40, 40)]))]),
    # ================= 王国カード =================
    'druid': dict(  # 森の賢者: 立石の輪の中で、杖を掲げる白ひげの賢者
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=128),
        items=[('standing_stone', dict(x=30, base=136, w=26, h=60, rune=False)), ('standing_stone', dict(x=196, base=136, w=26, h=64, rune=False)),
               ('figure', dict(x=112, foot=154, h=112, arms=('down', 'raise'), robe=True, tunic='paper', mantle='green', head='hood', head_ramp='green', beard='paper', face=True,
                               props=[(1, ('staff', dict(deg=-92, length=2.0, below=3.2, top='crook')), True)])), ('will_o_wisp', dict(x=150, y=36, r=4, ramp='gold'))]),
    'loyaldog': dict(  # 番の犬: 戸口の前に座り、主を待つ犬
        light=dict(pool=(112, 100), radius=(150, 100), halo=(40, 60, 40, 0.5), fall=1.1),
        env=_night(moon=None, ground='stone'),
        items=[('house', dict(x=110, base=136, w=100, h=70, roof_h=30, roof='wood', windows=[(14, 14, 12, 12, True)], door=(50, 22, 34))), ('lantern', dict(x=40, y=70, hang=40)),
               ('dog', dict(x=100, base=156, s=1.9, facing=-1))]),
    'protector': dict(  # 守り手: 大盾を立てて、子をかばう騎士
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=_night(moon=(30, 22, 10)),
        items=[('figure', dict(x=150, foot=154, h=80, facing=-1, arms=('chest', 'chest'), tunic='red', head='hair', legs_ramp='cloth')),
               ('figure', dict(x=96, foot=154, h=114, arms=('forward', 'low'), tunic='blue', armor=True, head='helm', cloak='blue', legs_ramp='silver',
                               props=[(0, ('shield', dict(ramp='blue')), True)]))]),
    'priory': dict(  # 僧坊: 回廊のある僧院と鐘の塔
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=130, ground='stone'),
        items=[('tower', dict(x=150, base=130, w=30, h=96, roof='red', windows=[(-2, 20, 5, 9)])), ('bell_hang', dict(x=165, y=48)),
               ('arcade_arches', dict(x0=0, x1=150, top=70, base=136, n=3)), ('house', dict(x=0, base=130, w=70, h=40, roof_h=20, roof='red', gain=0.7, windows=[(12, 12, 8, 10, True)]))]),
    'sprite': dict(  # 妖精: 透ける羽で舞う、小さな光の妖精
        light=dict(pool=(112, 90), radius=(150, 100), fall=1.1, halo=(112, 70, 50, 0.4)),
        env=('forest', dict(hz=124, moon=None, seed=67)),
        items=[('fairy_wings', dict(x=112, y=70, s=1.4)),
               ('figure', dict(x=112, foot=120, h=70, arms=('raise', 'raise'), robe=True, gown=True, tunic='green', head='long', hair='gold')), ('mushrooms', dict(x=60, base=154)),
               ('will_o_wisp', dict(x=160, y=110, r=3, ramp='gold'))]),
    'trailer': dict(  # 足跡たどり: 膝をつき、地面の足あとを見る
        light=dict(pool=(104, 104), radius=(160, 105), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=69)),
        items=[('tracks', dict(pts=[(140, 150), (156, 144), (170, 152), (186, 146), (200, 154)])),
               ('figure', dict(x=90, foot=152, h=104, arms=('reach', 'chest'), legs='kneel', lean=0.15, tunic='green', cloak='leather', head='hood', head_ramp='green', legs_ramp='leather'))]),
    'fairychild': dict(  # 化け子: 揺りかごで光る、すり替えられた子
        light=dict(pool=(112, 100), radius=(150, 100), halo=(36, 44, 40, 0.5), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('window_arch', dict(x=24, y=10, w=30, h=56)), ('cradle', dict(x=112, base=150, w=90)), ('fairy_wings', dict(x=170, y=60, s=0.6))]),
    'simpleton': dict(  # うつけ者: 曲がった帽子で花を差し出す、のんきな男
        light=dict(pool=(104, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('figure', dict(x=110, foot=154, h=108, arms=('down', 'present'), tunic='gold', head='jester', legs_ramp='green', face=True, props=[(1, 'flowers_held', True)])),
               ('flowers', dict(rows=[(150, 4.0, 30)]))]),
    'emptytown': dict(  # 無人の町: 灯のひとつもない、霧の町
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05),
        env=_night(moon=(36, 24, 9, 0.6), ground='stone'),
        items=[('house', dict(x=0, base=128, w=56, h=40, roof_h=24, roof='wood', gain=0.6, windows=[(10, 10, 8, 9, False), (34, 10, 8, 9, False)])),
               ('house', dict(x=80, base=124, w=60, h=44, roof_h=24, roof='red', gain=0.55, windows=[(10, 10, 8, 9, False), (38, 10, 8, 9, False)])),
               ('house', dict(x=160, base=130, w=60, h=40, roof_h=22, roof='wood', gain=0.5, windows=[(12, 10, 8, 9, False)])), ('fog', dict(bands=[(130, 12), (150, 8)], gain=0.7))]),
    'goblin': dict(  # 小鬼: 金貨を抱えてにやつく、尖り耳の小鬼
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('cave', dict(hz=134, seed=71)),
        items=[('lantern', dict(x=30, y=50, hang=20)),
               ('figure', dict(x=112, foot=154, h=84, arms=('present', 'present'), legs='crouch', lean=0.1, tunic='leather', skin='green', head='horns', legs_ramp='leather', face=True,
                               props=[(1, ('held_coin', dict(metal='gold', r=0.9)), True)])), ('stack', dict(cx=170, base=152, r=8, n=5, metal='gold', seed=92))]),
    'firewatch': dict(  # 火の番: 櫓の上で、遠くの火に鐘を鳴らす
        light=dict(pool=(104, 80), radius=(150, 100), fall=1.1, halo=(190, 120, 50, 0.5)),
        env=_night(moon=None, ground=None, stars=30),
        items=[('fire_line', dict(y=150)), ('railing', dict(x0=0, x1=150, top=118, base=160)),
               ('figure', dict(x=74, foot=158, h=106, arms=('down', 'raise'), tunic='red', head='hat', head_ramp='cloth', props=[(1, 'bell', True)]))]),
    'hiddencave': dict(  # 隠れ洞: 滝の裏に口を開ける洞
        light=dict(pool=(112, 96), radius=(160, 105), **DAWN),
        env=('forest', dict(hz=128, moon=None, seed=73)),
        items=[('rocks', dict(pts=[(112, 140, 200, 120)], gain=0.8)), ('cave_mouth', dict(x=112, base=136, w=70, h=70)), ('cascade', dict(x=112, y0=20, y1=136)),
               ('tide_pool', dict(x=112, y=146, rx=70, ry=10))]),
    'minstrel': dict(  # 琵琶法師: 頭巾の盲目の法師が、琵琶を弾き語る
        light=dict(pool=(104, 96), radius=(150, 100), fall=1.1, halo=(130, 130, 60, 0.6)),
        env=_night(moon=None, gain=0.5, stars=40),
        items=[('figure', dict(x=100, foot=152, h=100, arms=('belly', 'present'), legs='kneel', robe=True, tunic='cloth', head='hood', head_ramp='paper', face=True, props=[(0, 'lute', True)])),
               ('campfire', dict(x=170, base=152, s=0.9))]),
    'luckyvillage': dict(  # 福の村: 金の提灯と縁起物に飾られた村
        light=dict(pool=(112, 100), radius=(170, 105), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=_night(moon=None, ground='stone'),
        items=[('house', dict(x=10, base=130, w=60, h=36, roof_h=26, roof='red', windows=[(10, 10, 9, 10, True), (38, 10, 9, 10, True)])),
               ('house', dict(x=140, base=130, w=70, h=40, roof_h=28, roof='red', windows=[(12, 12, 9, 10, True), (46, 12, 9, 10, True)])),
               ('lantern_string', dict(y0=30, y1=46, colors=('gold', 'gold', 'red', 'gold', 'gold'))), ('holed_coin', dict(x=112, y=104, r=14))]),
    'graveyard': dict(  # 無縁墓: 月夜の、名のない墓の並び
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(40, 28, 40, 0.6)),
        env=_night(moon=(40, 28, 13), ground='leather', gain=0.5),
        items=[('gravestones', dict(pts=[(30, 140, 14, 22), (70, 146, 16, 28), (112, 150, 20, 36), (156, 146, 16, 26), (196, 140, 14, 22)])),
               ('tree', dict(x=200, base=124, h=70, kind='dead', ramp='cloth', gain=0.6, seed=95)), ('fog', dict(bands=[(150, 8)], gain=0.7))]),
    'secretcouncil': dict(  # 密議: 頭巾の者たちが、一本の蝋燭を囲む
        light=dict(pool=(112, 104), radius=(130, 90), fall=1.25, halo=(112, 110, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('figure', dict(x=50, foot=160, h=100, arms=('present', 'chest'), robe=True, tunic='purple', head='hood', head_ramp='cloth')),
               ('figure', dict(x=174, foot=160, h=100, facing=-1, arms=('present', 'chest'), robe=True, tunic='blue', head='hood', head_ramp='cloth')),
               ('figure', dict(x=112, foot=150, h=92, arms=('present', 'present'), robe=True, tunic='cloth', head='hood', head_ramp='cloth')),
               ('round_table', dict(x=112, y=130, rx=80, ry=14, cloth='purple')), ('candle', dict(x=112, base=128, h=10, r=3))]),
    'demonforge': dict(  # 鬼の仕事場: 赤い炉の前に、角の影が槌を振るう
        light=dict(pool=(104, 96), radius=(150, 100), halo=(40, 70, 60, 0.9), fall=1.1, key=0.8),
        env=('cave', dict(hz=134, seed=75)),
        items=[('forge', dict(x=0, y=50, w=70, h=60)), ('anvil', dict(x=150, base=150, s=1.2)),
               ('figure', dict(x=110, foot=154, h=120, arms=('belly', 'raise'), tunic='red', skin='red', head='horns', legs_ramp='cloth', face=True,
                               props=[(1, ('hammer', dict(deg=-40, length=2.4, big=True)), True)])), ('sparks', dict(pts=[(140, 110), (156, 100), (130, 96)]))]),
    'purifier': dict(  # お祓い師: 幣を振って、紫の煙を散らす
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='plank', hz=122, floor='planks')),
        items=[('figure', dict(x=96, foot=154, h=112, arms=('chest', 'raise'), robe=True, tunic='paper', mantle='red', head='hat', head_ramp='cloth', face=True,
                               props=[(1, 'gohei', True)])), ('wisps', dict(pts=[(170, 60), (190, 100), (150, 40)]))]),
    'deadcaller': dict(  # 死霊使い: 両手を掲げ、土から骸骨を呼び起こす
        light=dict(pool=(104, 92), radius=(150, 100), fall=1.1, halo=(30, 30, 40, 0.5)),
        env=_hex(hz=128),
        items=[('figure', dict(x=80, foot=154, h=112, arms=('raise', 'lift'), robe=True, tunic='cloth', mantle='purple', head='hood', head_ramp='cloth', face=True,
                               props=[(0, 'bone_staff', True)])), ('skeleton_rise', dict(x=164, base=150)), ('wisps', dict(pts=[(170, 80)]))]),
    'herdsman': dict(  # 牧人: 牧杖を手に、羊を追う
        light=dict(pool=(104, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=118),
        items=[('figure', dict(x=74, foot=154, h=110, arms=('down', 'forward'), tunic='leather', cloak='green', head='hat', head_ramp='leather', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-80, length=3.4, below=1.6, top='crook')), False)])),
               ('sheep', dict(x=150, base=150, s=1.3, facing=1)), ('sheep', dict(x=190, base=140, s=1.0, facing=1))]),
    'sneak': dict(  # 忍び足: 抜き足で廊下を進む、頭巾の影
        light=dict(pool=(104, 96), radius=(140, 100), fall=1.2, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('torch', dict(x=18, y=40)), ('doorway', dict(x=184, base=124, w=36, h=70)),
               ('figure', dict(x=104, foot=154, h=104, arms=('forward', 'pull'), legs='stride', lean=0.12, tunic='cloth', head='hood', head_ramp='cloth', mask='cloth', legs_ramp='cloth'))]),
    'shoemender': dict(  # 靴直し: 靴型の靴に錐を通す
        light=dict(pool=(108, 98), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('shelf', dict(x0=140, x1=220, y=50)), ('boots_pair', dict(x=160, base=50)),
               ('figure', dict(x=80, foot=152, h=100, arms=('reach', 'raise'), legs='kneel', tunic='blue', apron='leather', head='cap', head_ramp='leather', props=[(1, ('chisel', dict(deg=60)), True)])),
               ('shoe_last', dict(x=150, base=154))]),
    'tombchamber': dict(  # 石室: 石の棺と、まわりに置かれた宝
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(18, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('sarcophagus', dict(x=104, base=150, w=110, h=34)),
               ('chest', dict(x=170, base=152, w=40, h=18, fill='gold')), ('goblet', dict(x=30, base=152, s=1.3))]),
    'hauntedvillage': dict(  # 祟りの村: 紫の夜、亡霊がさまよう村
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(40, 30, 40, 0.5)),
        env=_hex(hz=126, moon=(40, 30, 12)),
        items=[('ruined_house', dict(x=10, base=130, w=60, h=36, gain=0.6)), ('ruined_house', dict(x=140, base=132, w=66, h=40, gain=0.55)),
               ('ghosts', dict(pts=[(100, 90), (60, 110), (180, 80)]))]),
    'rookery': dict(  # 悪党の巣窟: 暗い酒場で、短剣を卓に立てる者たち
        light=dict(pool=(112, 100), radius=(140, 90), fall=1.2, halo=(112, 50, 40, 0.5)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=112, y=44, hang=0)),
               ('figure', dict(x=56, foot=162, h=100, arms=('present', 'belly'), tunic='cloth', head='hood', head_ramp='cloth', mask='red')),
               ('figure', dict(x=170, foot=162, h=100, facing=-1, arms=('present', 'belly'), tunic='leather', head='hat', head_ramp='cloth', beard='hair')),
               ('table', dict(x0=60, x1=166, top=128, legs_to=160, front=True)), ('sword_stuck', dict(x=112, base=128)), ('tankard', dict(x=140, base=128, s=0.9))]),
    'figurine': dict(  # 土偶: 遮光器の目の土の人形
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(28, 40, 40, 0.5)),
        env=('icon', dict(hz=130, wall='stone', cloth='wood', cloth_gain=0.6)),
        items=[('candle', dict(x=30, base=126, h=12, r=3)), ('dogu', dict(x=112, base=150, s=1.2))]),
    'phantomhorse': dict(  # 化け馬: 霧の中を駆ける、透ける白馬
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.05),
        env=_night(moon=(36, 24, 11, 0.5), ground='stone', gain=0.45),
        items=[('fog', dict(bands=[(110, 12)], gain=0.7)), ('horse', dict(x=112, base=148, s=1.5, gallop=True, ramp='water')), ('fog', dict(bands=[(140, 12)], gain=0.8))]),
    'holygrove': dict(  # 鎮守の森: 注連縄を巻いた神木と、鳥居
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=128, moon=None, seed=75)),
        items=[('shimenawa_tree', dict(x=130, base=150, h=140)), ('torii', dict(x=60, base=150, w=70, h=70))]),
    'bully': dict(  # いじめっ子: 腕組みで見下ろす、大柄な子
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.5)),
        env=_night(moon=None, ground='stone'),
        items=[('figure', dict(x=150, foot=154, h=72, facing=-1, arms=('chest', 'chest'), tunic='blue', head='hair', legs_ramp='cloth', face=True)),
               ('figure', dict(x=90, foot=154, h=104, arms=((-0.2, 1.0, 1.5, 1.2), (0.2, 1.0, -1.5, 1.1)), tunic='red', head='cap', head_ramp='cloth', legs_ramp='leather', face=True))]),
    'doomedhero': dict(  # 薄幸の勇者: 黒雲の下、欠けた鎧で剣を構える
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1),
        env=_hex(hz=128),
        items=[('rain_cloud', dict(x=150, y=30, w=110)),
               ('figure', dict(x=100, foot=154, h=112, arms=('down', 'aim'), legs='stride', tunic='blue', armor=True, head='hair', cloak='cloth', legs_ramp='silver', face=True,
                               props=[(1, ('sword', dict(deg=-30, length=4.0)), True)]))]),
    'bloodsucker': dict(  # 血吸い: 立て襟の外套の、青白い吸血鬼
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=_hex(hz=128, moon=(40, 30, 14)),
        items=[('bats', dict(pts=[(160, 40, 1.6), (186, 60, 1.2), (60, 70, 1.4)])),
               ('figure', dict(x=112, foot=154, h=116, arms=('lift', 'down'), robe=True, tunic='cloth', cloak='red', skin='paper', head='hair', face=True,
                               behind=[(0, ('cape_collar', {}))]))]),
    'wolfman': dict(  # 狼男: 満月の下で、狼の頭に変わった男
        light=dict(pool=(104, 90), radius=(160, 105), fall=1.05, halo=(40, 30, 40, 0.7)),
        env=_night(moon=(40, 30, 16), ground='foliage', gain=0.5),
        items=[('tree', dict(x=196, base=128, h=80, kind='dead', ramp='cloth', gain=0.6, seed=96)),
               ('figure', dict(x=108, foot=154, h=116, arms=('forward', 'raise'), legs='stride', tunic='cloth', skin='leather', head='wolf', legs_ramp='cloth', belt='leather'))]),
    'nightthief': dict(  # 夜盗: 月夜に、袋を背負って塀を越える
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(36, 24, 40, 0.7)),
        env=_night(moon=(36, 24, 11, 0.4), ground='stone'),
        items=[('wall', dict(x0=110, x1=224, top=90, bottom=160, merlon=10, gap=6)),
               ('figure', dict(x=106, foot=154, h=110, arms=('raise', 'reach'), legs='stride', lean=-0.1, tunic='cloth', head='hood', head_ramp='cloth', mask='cloth', legs_ramp='cloth',
                               behind=[(0, ('sack_back', {}))])), ('rope', dict(x0=112, y0=30, x1=150, y1=86))]),
}
