"""冒険（cards-adventures.js）の 58 枚（札 38 ＋ イベント 20）の場面データ。書き方は scenes.py の冒頭を見る。
旅の札なので、酒場の暖かい灯・街道の夜明け・山道・沼・遠い海を散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


TAVERN = ('room', dict(wall='plank', hz=96, floor='table'))

SCENES = {
    # ================= 札 =================
    'realmcoin': dict(  # 通用貨: 酒場の卓に置いた銀貨と、泡のジョッキ
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=TAVERN,
        items=[('lantern', dict(x=28, y=40, hang=0)), ('tankard', dict(x=150, base=140, s=1.8)),
               ('stack', dict(cx=82, base=144, r=13, n=4, metal='silver', stamp='crown', seed=71)), ('coin', dict(cx=104, cy=150, r=12, metal='silver', stamp='star'))]),
    'lad': dict(  # 小僧: 肩掛け鞄で、夜明けの街道を行く少年
        light=dict(pool=(104, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=118),
        items=[('road', dict(x=150, top=118, base=160, w0=6, w1=110, ramp='sand')),
               ('figure', dict(x=96, foot=154, h=88, arms=('down', 'belly'), legs='stride', tunic='blue', head='cap', head_ramp='red', legs_ramp='leather', face=True,
                               props=[(0, ('bag', dict(ramp='leather')), True)]))]),
    'farmer': dict(  # 百姓: 麦わら帽で鍬をかつぐ、夜明けの畑
        light=dict(pool=(104, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=112, ground='leather'),
        items=[('furrows', dict(y0=118)), ('haystack', dict(x=186, base=132, r=20)),
               ('figure', dict(x=96, foot=154, h=110, arms=('down', 'lift'), tunic='leather', head='hat', head_ramp='sand', legs_ramp='blue',
                               props=[(1, 'hoe', True)]))]),
    'catpaw': dict(  # 猫の手: 酒場の卓で、硬貨に前足をかける猫
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=TAVERN,
        items=[('lantern', dict(x=28, y=40, hang=0)), ('tankard', dict(x=60, base=130, s=1.2)),
               ('cat', dict(x=130, base=150, s=1.7, facing=-1)), ('coin', dict(cx=96, cy=150, r=9, metal='gold', stamp='crown'))]),
    'wreck': dict(  # 打ち壊し: 街道に打ち捨てられた、壊れた荷車
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=120, ground='stone'),
        items=[('broken_barrel', dict(x=60, base=150)), ('wheel', dict(x=150, y=140, r=18, gain=0.8)),
               ('plank', dict(x0=100, y0=150, x1=200, y1=128, w=3)), ('plank', dict(x0=110, y0=156, x1=196, y1=150, w=3)),
               ('crate', dict(x=170, y=130, w=26, h=20, gain=0.8)), ('pages', dict(pts=[(30, 156), (120, 158)]))]),
    'wardstone': dict(  # 護り石: 夜明けの野に立つ、青く光る印の石
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('standing_stone', dict(x=112, base=146, w=50, h=104)), ('standing_stone', dict(x=40, base=134, w=24, h=44, rune=False)),
               ('standing_stone', dict(x=190, base=136, w=26, h=50, rune=False))]),
    'escort': dict(  # 護衛兵: ランタンと盾で、お召し馬車を守る
        light=dict(pool=(104, 92), radius=(160, 105), fall=1.1, halo=(40, 56, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.65)),
        items=[('coach', dict(x=160, base=150, w=80, h=46)),
               ('figure', dict(x=70, foot=154, h=110, arms=('lift', 'chest'), tunic='blue', armor=True, head='helm', cloak='red', legs_ramp='cloth',
                               props=[(0, ('held_lantern', {}), True), (1, ('shield', dict(ramp='blue')), True)]))]),
    'stonecell': dict(  # 石牢: 壁の鎖、格子の窓から差す月の光
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(150, 26, 30, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('cell_bars', dict(x0=140, x1=176, top=14, base=42, gap=7)), ('light_beam', dict(x0=158, y0=42, x1=110, y1=148)),
               ('wall_chains', dict(x=44, top=60)), ('skull', dict(x=60, y=146, s=0.8)), ('bowl_floor', dict(x=170, base=150))]),
    'kit': dict(  # 旅支度: 背負い袋、水袋、地図、ランタン
        light=dict(pool=(112, 104), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=92, floor='planks')),
        items=[('backpack', dict(x=80, base=146)), ('waterskin', dict(x=140, base=146)), ('held_map_flat', dict(x=170, y=144)),
               ('lantern', dict(x=40, y=134, hang=None)), ('candle', dict(x=200, base=90, h=10, r=3))]),
    'pathguide': dict(  # 道案内: 山道で杖を上げ、行く先を指す
        light=dict(pool=(104, 88), radius=(170, 110), **DAWN),
        env=('pass', dict(hz=126, moon=None)),
        items=[('signpost', dict(x=190, base=140, arrows=(('paper', 1, 0), ('red', -1, 1)))),
               ('figure', dict(x=96, foot=154, h=112, arms=('down', 'aim'), tunic='green', cloak='leather', head='hat', head_ramp='leather', beard='paper', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-30, length=2.6, below=1.0)), True)]))]),
    'copycat': dict(  # 写し: 画架の絵と、そっくりの壺
        light=dict(pool=(112, 98), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('window_arch', dict(x=22, y=10, w=28, h=50)), ('easel', dict(x=82, base=150, w=64, h=56)), ('table', dict(x0=130, x1=200, top=120, legs_to=156)),
               ('vase', dict(x=166, base=120, s=1.4))]),
    'crow': dict(  # カラス: 枯れ枝で、光る硬貨をくわえる鴉
        light=dict(pool=(112, 86), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=('night', dict(hz=140, moon=(40, 30, 14, 0.3), ground_ramp=None, stars=30)),
        items=[('tree', dict(x=60, base=170, h=170, kind='dead', ramp='cloth', gain=0.7, seed=71)), ('raven', dict(x=120, y=80, s=3.0, facing=1)),
               ('coin', dict(cx=176, cy=78, r=5, metal='gold', tilt=0.9))]),
    'courier': dict(  # 早馬: 鞍袋に書状を挿し、夜明けの道を駆ける馬
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, ground='sand'),
        items=[('horse', dict(x=112, base=148, s=1.4, gallop=True, blanket='red')), ('letter_fly', dict(x=126, y=78))]),
    'skinflint': dict(  # けちん坊: 蝋燭一本の灯で、銅貨を数える
        light=dict(pool=(108, 100), radius=(140, 95), fall=1.2, halo=(52, 112, 40, 0.6)),
        env=('room', dict(wall='plank', hz=116, floor='planks')),
        items=[('figure', dict(x=110, foot=170, h=118, arms=('present', 'present'), lean=0.12, robe=True, tunic='cloth', head='coif', head_ramp='leather', beard='paper',
                               face=True)),
               ('table', dict(x0=20, x1=204, top=126, legs_to=160, front=True)),
               ('pile', dict(cx=112, base=132, w=30, h=12, metal='copper', r=6, count=12, seed=7, stamps=('pip',))), ('candle', dict(x=52, base=124, h=6, r=3))]),
    'harbor': dict(  # 港: 倉と桟橋に並ぶ船
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=90, moon=None, sky_ramp='dawn', stars=0)),
        items=[('house', dict(x=0, base=112, w=60, h=40, roof_h=22, roof='red', windows=[(10, 10, 9, 10, True)])),
               ('ship', dict(x=156, wl=120, s=0.55, sails='paper', flag='blue')), ('ship', dict(x=80, wl=110, s=0.32, gain=0.7)),
               ('dock', dict(y=136)), ('crate', dict(x=20, y=118, w=26, h=20)), ('barrel', dict(x=60, base=150, r=11, h=24))]),
    'forester': dict(  # 森番: 角笛を下げ、斧を持って森を見回る
        light=dict(pool=(104, 92), radius=(160, 105), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=41)),
        items=[('figure', dict(x=100, foot=154, h=112, arms=('down', 'lift'), tunic='green', cloak='leather', head='hood', head_ramp='green', legs_ramp='leather',
                               props=[(1, ('axe', dict(deg=-150, length=2.6)), True), (0, 'hunting_horn', True)])), ('stump', dict(x=176, base=154, r=14, h=10))]),
    'shapeshift': dict(  # 化け替え: 外套の男の影が、壁に獣の形で映る
        light=dict(pool=(100, 90), radius=(140, 100), fall=1.2, halo=(26, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=126, floor='flag')),
        items=[('candle', dict(x=26, base=70, h=12, r=3)), ('shelf', dict(x0=8, x1=46, y=70)), ('beast_shadow', dict(x=164, base=130)),
               ('figure', dict(x=96, foot=154, h=110, arms=('chest', 'low'), tunic='purple', cloak='cloth', head='hood', head_ramp='cloth', legs_ramp='cloth')),
               ('wisps', dict(pts=[(120, 60)]))]),
    'tinkerer': dict(  # からくり師: 歯車とぜんまい、組みかけの機械人形
        light=dict(pool=(112, 100), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=104, floor='table')),
        items=[('lantern', dict(x=28, y=40, hang=0)), ('gears', dict(x=80, y=126)), ('automaton', dict(x=168, base=150, s=1.4))]),
    'bridgeogre': dict(  # 橋守の鬼: 石橋の下から、棍棒の鬼がにらむ
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 30, 40, 0.5)),
        env=('night', dict(hz=60, moon=(30, 26, 10, 0.4), stars=20, ground_ramp='stone', ground_gain=0.5)),
        items=[('stream', dict(y0=140, y1=160)),
               ('figure', dict(x=112, foot=156, h=120, arms=('hip', 'lift'), tunic='leather', skin='green', head='hair', hair='hair', legs_ramp='leather', belt='leather',
                               face=True, props=[(1, 'club', True)])),
               ('arch_bridge', dict(x=112, top=32, w=240, span=120))]),
    'bigman': dict(  # 大男: 森の木より大きな男が、笑って見下ろす
        light=dict(pool=(112, 70), radius=(170, 110), **DAWN),
        env=_dawn(hz=140, ground='foliage'),
        items=[('tree', dict(x=30, base=150, h=60, kind='pine', gain=0.6, seed=72)), ('tree', dict(x=190, base=150, h=56, kind='pine', gain=0.6, seed=73)),
               ('figure', dict(x=112, foot=214, h=230, arms=('hip', 'hip'), tunic='red', head='hair', beard='hair', legs_ramp='leather', face=True)),
               ('house', dict(x=150, base=156, w=30, h=16, roof_h=14, roof='red', windows=[(6, 4, 5, 6, True)]))]),
    'mazewood': dict(  # 迷いの森: ねじれた幹と霧、分かれて消える小道
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(112, 80, 40, 0.3)),
        env=('forest', dict(hz=118, moon=None, seed=43)),
        items=[('trail', dict(x=80, top=118, base=160)), ('trail', dict(x=150, top=124, base=160)),
               ('tree', dict(x=112, base=150, h=120, kind='dead', ramp='wood', gain=0.7, seed=74)), ('fog', dict(bands=[(110, 12), (136, 10)], gain=0.8))]),
    'phantomcity': dict(  # 幻の都: 雲の上に浮かぶ、淡く光る塔の都
        light=dict(pool=(112, 80), radius=(170, 110), fall=1.0),
        env=('night', dict(hz=150, moon=None, stars=40, ground_ramp=None, sky_ramp='purple', clouds=())),
        items=[('ghost_city', dict(x=112, base=96)), ('fog', dict(bands=[(100, 14), (120, 12), (142, 10)], gain=0.9))]),
    'oldrelic': dict(  # 古の宝: 遺跡の台座で光る、黄金の座像
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1),
        env=('cave', dict(hz=134, seed=45)),
        items=[('broken_column', dict(x=30, base=136, h=80, r=9, gain=0.7)), ('broken_column', dict(x=196, base=136, h=60, r=9, gain=0.6)),
               ('idol', dict(x=112, base=150))]),
    'carriage': dict(  # お召し馬車: 金の飾りの馬車と白い馬
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 56, 40, 0.5)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.65, stars=30)),
        items=[('lamp_post', dict(x=26, base=140, h=80)), ('coach', dict(x=146, base=150, w=90, h=52)), ('horse', dict(x=60, base=150, s=1.05, ramp='paper', blanket='red'))]),
    'raconteur': dict(  # 講釈師: 焚き火のそばで身ぶりを交えて語る
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(130, 130, 60, 0.6)),
        env=('night', dict(hz=118, moon=None, ground_ramp='foliage', ground_gain=0.5, stars=40)),
        items=[('figure', dict(x=80, foot=154, h=112, arms=('raise', 'forward'), robe=True, tunic='blue', mantle='red', head='hat', head_ramp='cloth', beard='paper', face=True)),
               ('figure', dict(x=186, foot=156, h=78, facing=-1, arms=('chest', 'chest'), legs='crouch', tunic='green', head='hood', head_ramp='leather', legs_ramp='cloth')),
               ('campfire', dict(x=134, base=154, s=1.0))]),
    'bogfiend': dict(  # 沼の魔物: 泥の中から、光る目の魔物が立ち上がる
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(36, 30, 40, 0.5)),
        env=('night', dict(hz=118, moon=(36, 30, 12, 0.5), sky_ramp='purple', stars=20, ground_ramp=None)),
        items=[('tree', dict(x=200, base=126, h=80, kind='dead', ramp='cloth', gain=0.6, seed=75)), ('bog', dict(y0=118)),
               ('bog_monster', dict(x=112, base=140, s=1.3)), ('reeds', dict(xs=(18, 34, 190), base=150))]),
    'windfall': dict(  # 掘り当て: 鶴嘴の先の岩が割れ、金の塊があふれる
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('cave', dict(hz=134, seed=47)),
        items=[('lantern', dict(x=30, y=50, hang=20)), ('vein', dict(pts=[(70, 70), (100, 86), (130, 80), (160, 100)])),
               ('pile', dict(cx=112, base=152, w=50, h=22, metal='gold', r=8, count=18, seed=9)), ('pickaxe', dict(x=150, y=150, ang=-120, length=50))]),
    'vintner': dict(  # 酒屋: 地下の酒蔵の樽、栓から注ぐ杯
        light=dict(pool=(112, 100), radius=(150, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=22, bh=11)),
        items=[('lantern', dict(x=30, y=40, hang=0)), ('barrel', dict(x=100, base=120, r=22, h=56, lying=True)), ('barrel', dict(x=170, base=120, r=22, h=56, lying=True, gain=0.85)),
               ('goblet', dict(x=80, base=150, s=1.6)), ('bottles_row', dict(x0=120, x1=210, base=150, ramps=('green', 'red', 'purple'), seed=7))]),
    'farland': dict(  # 果ての地: 夜明けの海の向こうに、遠い山と城
        light=dict(pool=(112, 80), radius=(180, 120), **DAWN),
        env=('coast', dict(hz=112, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 100, 8), (60, 90, 6)))),
        items=[('hills', dict(base=112, amp=40, gain=0.5, depth=0.6, seed=8, freq=1.3)), ('castle', dict(x=150, base=86, s=0.35, roof='blue')),
               ('ship', dict(x=60, wl=140, s=0.35, gain=0.9)), ('foam', dict(x0=0, x1=224, y=114))]),
    'servant': dict(  # 奉公人: 箒を手に、館を掃き清める娘
        light=dict(pool=(104, 90), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=176, top=0, w=26, h=56, ramp='blue', kind='cross')),
               ('figure', dict(x=108, foot=154, h=108, arms=('belly', 'present'), robe=True, gown=True, tunic='blue', apron='paper', head='coif', head_ramp='paper',
                               props=[(1, 'broom', True)]))]),
    'seeker': dict(  # 探し屋: 遺跡でランタンを掲げ、地図を見る
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(58, 44, 40, 0.7)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.6, stars=30)),
        items=[('broken_column', dict(x=180, base=136, h=70)), ('rubble', dict(x=170, base=150, n=8, seed=11)),
               ('figure', dict(x=90, foot=154, h=108, arms=('lift', 'present'), tunic='blue', cloak='leather', head='cap', head_ramp='leather', legs_ramp='cloth',
                               props=[(0, ('held_lantern', {}), True), (1, ('held_map', {}), True)]))]),
    'fighter': dict(  # 戦士: 剣と盾で踏み込む
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=('pass', dict(hz=126, moon=(30, 22, 10, 0.5))),
        items=[('figure', dict(x=106, foot=154, h=112, arms=('forward', 'aim'), legs='stride', lean=0.1, tunic='red', armor=True, head='helm', cloak='cloth', legs_ramp='cloth',
                               props=[(1, ('sword', dict(deg=-10, length=4.0)), True), (0, ('shield', dict(ramp='red')), True)]))]),
    'paragon': dict(  # 英傑: 後光の中で剣を掲げる、輝く鎧の英雄
        light=dict(pool=(112, 80), radius=(150, 100), fall=1.1),
        env=('battlement', dict(hz=104, moon=None, parapet=(100, 134), stars=20)),
        items=[('light_rays', dict(x=112, y=40, n=13, ln=110)),
               ('figure', dict(x=112, foot=154, h=114, arms=('hip', 'raise'), tunic='blue', armor=True, head='hair', hair='gold', cloak='gold', legs_ramp='silver', face=True,
                               props=[(1, ('sword', dict(deg=-88, length=4.4)), True)]))]),
    'victor': dict(  # 覇者: 月桂冠を戴き、杯を掲げる
        light=dict(pool=(112, 84), radius=(150, 100), fall=1.1, halo=(112, 20, 60, 0.4)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('hang_banner', dict(x=26, top=0, w=28, h=64, ramp='red', kind='circle')), ('hang_banner', dict(x=170, top=0, w=28, h=64, ramp='red', kind='circle')),
               ('figure', dict(x=112, foot=154, h=114, arms=('hip', 'raise'), tunic='red', armor=True, cloak='purple', head='hair', legs_ramp='silver', face=True,
                               props=[(1, 'trophy', True)])),
               ('laurel', dict(x=112, y=36, r=10))]),
    'ashigaru': dict(  # 足軽: 陣笠をかぶり、長い槍を立てる
        light=dict(pool=(104, 88), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='foliage'),
        items=[('banner_pole', dict(x=200, base=134)),
               ('figure', dict(x=104, foot=154, h=110, arms=('hip', 'low'), tunic='blue', armor=True, head='jingasa', head_ramp='cloth', legs_ramp='cloth',
                               behind=[(1, ('staff', dict(deg=-92, length=6.2, top='spear', below=2.4)))]))]),
    'deserter': dict(  # 落ち武者: 折れた刀を手に、破れた具足で逃げる
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=('forest', dict(hz=124, moon=(30, 22, 9, 0.5), seed=45)),
        items=[('figure', dict(x=110, foot=154, h=110, facing=-1, arms=('down', 'low'), legs='stride', lean=0.12, tunic='cloth', armor=True, head='hair', cloak='red',
                               legs_ramp='cloth', face=True, props=[(1, ('broken_sword', {}), True)]))]),
    'follower': dict(  # 門人: 道場で刀を前に置き、膝をついて礼をする
        light=dict(pool=(108, 96), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=160, top=0, w=40, h=70, ramp='paper', kind='circle')),
               ('figure', dict(x=100, foot=152, h=104, arms=('reach', 'present'), legs='kneel', lean=0.12, tunic='blue', head='hair', legs_ramp='cloth')),
               ('katana_flat', dict(x=150, y=150))]),
    'master': dict(  # 師範: ひげの剣の師が、刀を静かに構える
        light=dict(pool=(108, 88), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=170, top=0, w=34, h=70, ramp='paper', kind='cross')),
               ('figure', dict(x=104, foot=154, h=114, arms=('present', 'aim'), robe=True, tunic='cloth', mantle='blue', head='hair', hair='paper', beard='paper', face=True,
                               props=[(1, ('katana', dict(deg=-40, length=4.2)), True)]))]),
    # ================= イベント =================
    'e_soup': dict(  # 炊き出し: 大鍋の粥と、差し出された椀
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(112, 140, 60, 0.6)),
        env=('night', dict(hz=118, moon=None, ground_ramp='stone', ground_gain=0.6, stars=20)),
        items=[('ruined_house', dict(x=150, base=120, w=60, h=36, gain=0.5)), ('cauldron', dict(x=100, base=150, r=32, brew='paper')),
               ('bowls_row', dict(x=170, base=150))]),
    'e_advance': dict(  # 前借り: 証文と引き換えに渡される金貨
        light=dict(pool=(112, 100), radius=(150, 100), halo=(28, 44, 40, 0.6), **WARM),
        env=('icon', dict(hz=60, wall='plank', cloth='wood', cloth_gain=0.75)),
        items=[('candle', dict(x=26, base=58, h=12, r=3)), ('doc', dict(x=90, y=112, w=110, h=70)),
               ('stack', dict(cx=170, base=140, r=13, n=5, metal='gold', seed=72))]),
    'e_trial': dict(  # 腕試し: 的に刺さった矢と、並ぶ稽古の弓
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=120),
        items=[('target', dict(x=140, y=96, r=36)), ('fence', dict(x0=0, x1=80, base=146, h=12))]),
    'e_keep': dict(  # 取り置き: 札を付けて棚に取り置いた包み
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=140, floor='planks')),
        items=[('candle', dict(x=26, base=60, h=12, r=3)), ('shelf', dict(x0=10, x1=50, y=60)), ('shelf', dict(x0=60, x1=200, y=110)),
               ('parcel_big', dict(x=130, base=110)), ('tag', dict(x=156, y=86))]),
    'e_scouts': dict(  # 物見の衆: 丘の上から遠眼鏡で見張る二人
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, hills=((110, 18, 0.5, 0.5, 2),)),
        items=[('figure', dict(x=80, foot=150, h=96, arms=('down', 'eye'), tunic='green', cloak='leather', head='cap', head_ramp='leather', props=[(1, ('spyglass', dict(length=2.2)), True)])),
               ('figure', dict(x=150, foot=152, h=92, arms=('forward', 'down'), tunic='blue', head='hood', head_ramp='green'))]),
    'e_travelfair': dict(  # 旅回りの市: 幌馬車と天幕、提灯の連なり
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.05, halo=(30, 40, 40, 0.5)),
        env=('night', dict(hz=124, moon=None, ground_ramp='foliage', ground_gain=0.6, stars=30)),
        items=[('lantern_string', dict(y0=12, y1=26, colors=('red', 'gold', 'blue', 'gold', 'red'))), ('army_tent', dict(x=150, base=132, w=90, h=66, stripe='red')),
               ('wagon', dict(x=60, base=150, w=80, cover='blue')), ('campfire', dict(x=112, base=154, s=0.8))]),
    'e_bonfire': dict(  # どんど焼き: 組んだ竹と藁が、夜空へ燃え上がる
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.05, halo=(112, 90, 70, 0.8), key=0.8),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.6, stars=30)),
        items=[('bonfire', dict(x=112, base=148, s=1.3))]),
    'e_outing': dict(  # 遠出: 夜明けの丘で敷布を広げる
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=110, hills=((100, 10, 0.5, 0.6, 5),)),
        items=[('tree', dict(x=190, base=128, h=70, kind='oak', gain=0.75, seed=76)), ('picnic', dict(x=100, y=134)), ('flowers', dict(rows=[(152, 4.0, 26)]))]),
    'e_ferry': dict(  # 舟便: 夜明けの川を、荷を積んで渡る舟
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=100, moon=None, sky_ramp='dawn', stars=0)),
        items=[('hills', dict(base=100, amp=12, gain=0.5, depth=0.6, seed=3)), ('boat', dict(x=112, wl=140, w=150)),
               ('crate', dict(x=80, y=110, w=26, h=20)), ('barrel', dict(x=128, base=132, r=10, h=22)), ('sack', dict(x=156, base=132, r=10))]),
    'e_plan': dict(  # 段取り: 卓に広げた図面と、印の駒
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=74, floor='table')),
        items=[('candelabra', dict(x=26, base=72, h=24)), ('blueprint', dict(x=112, y=118)), ('dividers', dict(x=170, y=130, ln=36))]),
    'e_errand': dict(  # 使いの旅: 書状を手に、夜明けの道を急ぐ
        light=dict(pool=(104, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=116),
        items=[('road', dict(x=150, top=116, base=160, w0=6, w1=110, ramp='sand')),
               ('figure', dict(x=90, foot=154, h=104, arms=('present', 'pull'), legs='stride', lean=0.14, tunic='red', cloak='blue', head='feather', head_ramp='blue', legs_ramp='cloth',
                               props=[(0, 'letter', True)]))]),
    'e_pilgrim': dict(  # お参り: 丘の上の祠へ、杖をついて登る人々
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=112, hills=((100, 14, 0.5, 0.6, 4),)),
        items=[('road', dict(x=170, top=110, base=160, w0=6, w1=90, ramp='sand')), ('wayside_shrine', dict(x=176, base=118)),
               ('figure', dict(x=86, foot=140, h=80, arms=('down', 'forward'), tunic='paper', cloak='cloth', head='hood', head_ramp='paper',
                               props=[(1, ('staff', dict(deg=-80, length=2.8, below=2.2)), False)])),
               ('figure', dict(x=40, foot=156, h=92, arms=('down', 'forward'), tunic='paper', head='hat', head_ramp='sand',
                               props=[(1, ('staff', dict(deg=-80, length=2.8, below=2.2)), False)]))]),
    'e_soiree': dict(  # 夜会: シャンデリアの下で踊る二人
        light=dict(pool=(112, 86), radius=(160, 105), halo=(112, 20, 60, 0.5), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('chandelier', dict(x=112, y=16, r=32, chain_top=0)), ('column', dict(x=16, top=0, base=136, r=8)), ('column', dict(x=208, top=0, base=136, r=8, gain=0.8)),
               ('figure', dict(x=86, foot=154, h=110, arms=('down', 'lift'), tunic='blue', trim='gold', cloak='blue', head='hair', legs_ramp='paper')),
               ('figure', dict(x=138, foot=154, h=104, facing=-1, arms=('down', 'lift'), robe=True, gown=True, tunic='red', trim='gold', head='tiara', hair='hair'))]),
    'e_nightraid': dict(  # 夜討ち: 松明を手に、闇の城壁へ忍び寄る影
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 30, 40, 0.4)),
        env=('night', dict(hz=120, moon=(30, 26, 8, 0.6), ground_ramp='foliage', ground_gain=0.5, stars=30)),
        items=[('wall', dict(x0=110, x1=224, top=50, bottom=124, merlon=10, gap=6)),
               ('figure', dict(x=50, foot=152, h=96, arms=('down', 'raise'), legs='stride', lean=0.12, tunic='cloth', head='hood', head_ramp='cloth', legs_ramp='cloth', props=[(1, 'torch_held', True)])),
               ('figure', dict(x=96, foot=156, h=104, arms=('forward', 'raise'), legs='stride', lean=0.12, tunic='cloth', head='hood', head_ramp='cloth', mask='cloth', legs_ramp='cloth',
                               props=[(1, ('sword', dict(deg=-70, length=3.6)), True)]))]),
    'e_searoute': dict(  # 航路開き: 羅針盤の線が導く、水平線へ向かう船
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=104, moon=None, sky_ramp='dawn', stars=0)),
        items=[('ship', dict(x=120, wl=130, s=0.7, sails='paper', flag='red')), ('route_line', dict(x0=10, y0=150, x1=200, y1=106))]),
    'e_barter': dict(  # 物々交換: 魚と布と銀を、卓の上で取り替える
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=92, floor='table')),
        items=[('lantern', dict(x=28, y=40, hang=0)), ('basket', dict(x=60, base=146, w=34, h=12, kind='fish', n=4)),
               ('cloth_bolts', dict(x=150, base=146)), ('swap_arrows', dict(x=108, y=110)), ('stack', dict(cx=108, base=152, r=9, n=3, metal='silver', stamp='tower', seed=73))]),
    'e_inherit': dict(  # 家督: 紋の座布団に、家の鍵と剣と証文
        light=dict(pool=(112, 98), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=88, wall='stone', cloth='red', cloth_gain=0.6)),
        items=[('candelabra', dict(x=26, base=86, h=24)), ('hang_banner', dict(x=150, top=0, w=34, h=70, ramp='blue', kind='chevron')),
               ('cushion', dict(x=100, y=130, w=120, ramp='purple')), ('key', dict(x=106, y=118, s=0.6, ang=-10)), ('doc', dict(x=170, y=136, w=40, h=26, lines=3, sign=False))]),
    'e_secretart': dict(  # 秘伝: 開いた箱の中で光る、巻物の奥義書
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1),
        env=('icon', dict(hz=100, wall='plank', cloth='purple', cloth_gain=0.55)),
        items=[('chest', dict(x=66, base=148, w=90, h=34, fill=None)), ('glow_scroll', dict(x=112, y=104))]),
    'e_practice': dict(  # 修練: 藁人形と、立てかけた木剣
        light=dict(pool=(112, 96), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('torch', dict(x=16, y=40)), ('dummy', dict(x=112, base=150))]),
    'e_signpost': dict(  # 道しるべ: 夜明けの辻に立つ、四方を指す道しるべ
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=110, ground='foliage'),
        items=[('road', dict(x=112, top=110, base=160, w0=8, w1=120, ramp='sand')), ('road_cross', dict(y=134)),
               ('signpost', dict(x=112, base=150, arrows=(('red', -1, 0), ('blue', 1, 1), ('paper', -1, 2), ('green', 1, 3))))]),
}
