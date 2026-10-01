"""プロモ（cards-promo.js）の 14 枚の場面データ。書き方は scenes.py の冒頭を見る。
王国 11（上下 2 種の山とその 2 種を含む）とイベント 1。雪の蒸し風呂と氷の湯、和の奉行・若殿・船頭、闇の市などを描き分ける。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


def _snow(hz=124, moon=None):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=None, stars=24, hills=[(hz - 14, 12, 0.45, 0.6, 5)]))


SCENES = {
    'chapel2': dict(  # 礼拝所: 夜明けの丘の、鐘を吊った小さな礼拝堂
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=128),
        items=[('tower', dict(x=126, base=128, w=26, h=96, roof='red', windows=[(-2, 26, 6, 10)])), ('bell_hang', dict(x=139, y=46)),
               ('house', dict(x=60, base=134, w=70, h=40, roof_h=30, wall='stone', roof='red', timber=False, windows=[(12, 12, 10, 14, True), (46, 12, 10, 14, True)], door=(28, 14, 22))),
               ('gravestones', dict(pts=[(30, 146, 14, 18), (190, 148, 14, 18)]))]),
    'darkmarket': dict(  # 闇の市: 紫の提灯の路地で、外套を広げて品を見せる商人
        light=dict(pool=(112, 100), radius=(140, 100), fall=1.2, halo=(40, 46, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('paper_lantern', dict(x=36, y=46, r=10, ramp='purple', string=0)), ('paper_lantern', dict(x=190, y=40, r=8, ramp='purple', string=0)),
               ('figure', dict(x=112, foot=156, h=112, arms=('lift', 'lift'), robe=True, tunic='purple', cloak='cloth', head='hood', head_ramp='cloth', mask='cloth')),
               ('gems', dict(pts=[(84, 92, 4, 'red'), (90, 104, 3, 'green'), (138, 92, 4, 'blue'), (134, 104, 3, 'gold')])), ('bottle', dict(x=180, base=154, h=16, r=5, ramp='purple', glow=True)),
               ('crate', dict(x=20, y=134, w=30, h=22, gain=0.8))]),
    'dismantle': dict(  # 解体: 作業場で、ばらした荷車の車輪と板と釘
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('wheel', dict(x=150, y=112, r=28)), ('broken_beams', dict(x0=30, x1=120, top=100, bottom=150)),
               ('nails_box', dict(x=80, base=154)), ('mallet', dict(x=180, y=150)), ('coin', dict(cx=40, cy=154, r=7, metal='gold'))]),
    'legate': dict(  # 内通者: 隠し戸の陰で、頭巾の男が封書を差し出す
        light=dict(pool=(104, 92), radius=(140, 100), fall=1.2, halo=(150, 90, 40, 0.5)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('secret_door', dict(x=160, base=124, w=50, h=86)),
               ('figure', dict(x=96, foot=154, h=110, arms=('down', 'present'), lean=0.1, tunic='green', cloak='cloth', head='hood', head_ramp='cloth', mask='cloth', legs_ramp='cloth',
                               props=[(1, 'letter', True)]))]),
    'fencedvillage': dict(  # 囲いの村: 夜明けの丸太の柵に囲まれた、寄り合う家々
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=118),
        items=[('house', dict(x=30, base=118, w=50, h=28, roof_h=24, roof='red', windows=[(10, 9, 8, 8, True)])),
               ('house', dict(x=126, base=114, w=56, h=30, roof_h=24, roof='wood', chimney=0.5, windows=[(10, 9, 8, 9, True), (36, 9, 8, 9, True)])),
               ('house', dict(x=82, base=124, w=44, h=24, roof_h=20, roof='wood', gain=0.85, windows=[(16, 8, 8, 8, True)])),
               ('palisade', dict(x0=0, x1=224, base=152, h=40, gain=0.95))]),
    'bugyo': dict(  # 奉行: 白洲の上段で、裃を着て扇を構える奉行
        light=dict(pool=(108, 92), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.5)),
        env=('room', dict(wall='shoji', hz=130, floor='planks')),
        items=[('rug', dict(x=112, y=150, w=200, d=24, ramp='sand')),
               ('figure', dict(x=112, foot=154, h=114, arms=('belly', 'lift'), robe=True, tunic='cloth', mantle='blue', head='topknot', face=True,
                               props=[(1, ('fan', dict(ramp='paper')), True)])),
               ('scrolls', dict(x=190, base=150))]),
    'borderland': dict(  # 境の地: 夜明けの峠に立つ境の石と、両側の色の違う旗
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=('pass', dict(hz=124, moon=None)),
        items=[('road', dict(x=112, top=124, base=160, w0=10, w1=110, ramp='sand')), ('stele', dict(x=112, base=148, w=36, h=78)),
               ('nobori', dict(x=44, top=50, base=146, w=16, ramp='red')), ('nobori', dict(x=180, top=50, base=146, w=16, ramp='blue'))]),
    'nestegg': dict(  # 隠し財布: 木の洞の鳥の巣に隠した、口の開いた財布と金貨
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.4)),
        env=('forest', dict(hz=130, moon=None, seed=75)),
        items=[('trunk', dict(x=112, top=0, base=160, w=60)), ('nest', dict(x=112, y=118, r=50))]),
    'skipper': dict(  # 船頭: 夜明けの川で、棹を差して平舟を進める
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=('night', dict(hz=100, moon=None, sky_ramp='dawn', stars=0, ground_ramp='foliage', ground_gain=0.6, hills=[(92, 12, 0.5, 0.6, 5)])),
        items=[('river', dict(y0=100)), ('barge', dict(x=112, wl=148, w=150, h=14)),
               ('figure', dict(x=132, foot=136, h=104, facing=-1, arms=('forward', 'lift'), tunic='blue', head='jingasa', head_ramp='sand', legs_ramp='skin', boots='paper',
                               props=[(1, ('staff', dict(deg=-115, length=5.0, below=3.6)), True)]))]),
    'youngload': dict(  # 若殿: 城の縁側で、刀を差して立つ若い殿
        light=dict(pool=(108, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=132, ground='sand', hills=()),
        items=[('tenshu', dict(x=170, base=132, s=0.7)), ('sakura', dict(x=30, base=134, h=90, seed=7)),
               ('figure', dict(x=100, foot=156, h=104, arms=('belly', 'hip'), robe=True, tunic='purple', mantle='red', trim='gold', head='topknot', young=True, face=True,
                               behind=[(0, ('katana', dict(deg=160, length=3.0)))]))]),
    'p_sauna': dict(  # 蒸し風呂／氷の湯: 雪の夜、湯気の立つ小屋と、凍った湖の氷の穴
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(60, 110, 40, 0.5)),
        env=_snow(hz=118),
        items=[('snow_ground', dict(y0=118)), ('sauna_hut', dict(x=70, base=134, w=96, h=48)), ('ice_hole', dict(x=170, y=146, rx=40, ry=10)), ('snow', dict(n=70, seed=7))]),
    'steambath': dict(  # 蒸し風呂: 板の小屋の中、焼け石から立ちこめる湯気
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(112, 120, 50, 0.6)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('benches', dict(y0=96)), ('hot_stones', dict(x=112, base=152, r=30)), ('steam_cloud', dict(pts=[(100, 112), (118, 92), (96, 72), (124, 52), (64, 66), (166, 72)])),
               ('bucket', dict(x=180, base=156, r=12, fill='water'))]),
    'icebath': dict(  # 氷の湯: 月夜の凍った湖に開けた、氷の穴と梯子
        light=dict(pool=(112, 120), radius=(160, 105), fall=1.05, halo=(50, 30, 50, 0.6)),
        env=_snow(hz=106, moon=(50, 30, 12)),
        items=[('snow_ground', dict(y0=106)), ('tree', dict(x=200, base=110, h=60, kind='pine', gain=0.7, seed=77)), ('sauna_hut', dict(x=40, base=110, w=50, h=26)), ('ice_hole', dict(x=120, y=138, rx=70, ry=16)),
               ('snow', dict(n=60, seed=9))]),
    'e_summon': dict(  # 呼び寄せ: 夜明けの丘で、角笛を吹いて仲間を呼ぶ
        light=dict(pool=(108, 92), radius=(180, 110), **DAWN),
        env=_dawn(hz=128, hills=((110, 16, 0.5, 0.5, 6),)),
        items=[('figure', dict(x=104, foot=156, h=112, arms=('down', 'eye'), tunic='green', cloak='red', head='feather', head_ramp='green', legs_ramp='leather', face=True,
                               props=[(1, ('hunting_horn', {}), True)])),
               ('figure', dict(x=190, foot=128, h=44, facing=-1, arms=('down', 'raise'), tunic='blue', head='helm', legs_ramp='cloth')),
               ('figure', dict(x=210, foot=126, h=40, facing=-1, arms=('down', 'down'), tunic='red', head='helm', legs_ramp='cloth'))]),
}
