"""異郷（cards-hinterlands.js）の 35 枚の場面データ。書き方は scenes.py の冒頭を見る。
旅と辺境の札なので、街道・夜明け・砂漠・森・雪を散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)

SCENES = {
    # ================= 物と場所 =================
    'crossing': dict(  # 辻: 夜明けに道が交わる所、灯のともる祠
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=('night', dict(hz=104, moon=None, sky_ramp='dawn', stars=0, hills=[(96, 12, 0.5, 0.6, 2)], ground_gain=0.7)),
        items=[('road', dict(x=112, top=104, base=160, w0=8, w1=120, ramp='sand')),
               ('road_cross', dict(y=128)),
               ('wayside_shrine', dict(x=64, base=136)), ('tree', dict(x=186, base=122, h=56, kind='oak', gain=0.7, seed=41))]),
    'pyrite': dict(  # にせ金: 岩から突き出た、金色の立方体の結晶
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.6)),
        env=('cave', dict(hz=132, seed=21)),
        items=[('lantern', dict(x=30, y=50, hang=20)), ('pyrite_rock', dict(x=116, base=150, s=1.4))]),
    'grading': dict(  # 造成: 夜明けの斜面を段に均し、土を運ぶ
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=100, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('terraces', dict(y0=100)), ('wheelbarrow', dict(x=150, base=150)), ('spade_stuck', dict(x=70, base=146))]),
    'spring': dict(  # 泉のほとり: 苔の岩から湧く水と、羊歯の茂る水辺
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=118, moon=None, seed=7)),
        items=[('rocks', dict(pts=[(112, 118, 110, 46)], gain=0.85)), ('cascade', dict(x=112, y0=80, y1=126)),
               ('tide_pool', dict(x=112, y=136, rx=86, ry=16)), ('seaweed', dict(x=30, base=150, h=26)), ('seaweed', dict(x=190, base=152, h=24)),
               ('mushrooms', dict(x=150, base=156))]),
    'groundwork': dict(  # 根回し: 大木の根が地の下に広がり、根もとに埋めた書状
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05),
        env=('night', dict(hz=92, moon=(36, 24, 9, 0.4), ground_ramp=None)),
        items=[('tree', dict(x=112, base=92, h=110, kind='oak', gain=0.9, seed=42)), ('roots', dict(x=112, ground_y=92))]),
    'underpass': dict(  # 地下道: 石の橋の下をくぐる道、奥にランタン
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(112, 112, 40, 0.5)),
        env=('night', dict(hz=60, moon=None, stars=30, ground_ramp='stone', ground_gain=0.6)),
        items=[('road', dict(x=112, top=100, base=160, w0=30, w1=120)), ('lantern', dict(x=112, y=102, hang=80)),
               ('arch_bridge', dict(x=112, top=40, w=240, span=96)), ('foliage_top', dict(y=36))]),
    'loom': dict(  # 機織り: 木の機に張った縦糸と、模様の布
        light=dict(pool=(112, 96), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=138, floor='planks')),
        items=[('candle', dict(x=26, base=60, h=12, r=3)), ('shelf', dict(x0=8, x1=46, y=60)), ('loom', dict(x=118, base=150, w=130, h=120))]),
    'causeway': dict(  # 石畳: 沼を渡って城へ続く、敷石の長い道
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=90, moon=None, sky_ramp='dawn', stars=0, sea_gain=0.9)),
        items=[('castle', dict(x=112, base=88, s=0.5, roof='red')), ('road', dict(x=112, top=90, base=160, w0=8, w1=120, ramp='stone')),
               ('reeds', dict(xs=(10, 30, 180, 205), base=150))]),
    'hatago': dict(  # 宿場: 灯籠の下がる旅籠、つないだ馬
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(56, 70, 40, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.3)),
        items=[('house', dict(x=20, base=134, w=110, h=56, roof_h=26, roof='wood', windows=[(14, 12, 12, 12, True), (46, 12, 12, 12, True), (78, 12, 12, 12, True)], door=(44, 22, 26))),
               ('paper_lantern', dict(x=56, y=96, r=7, ramp='red', string=78)), ('paper_lantern', dict(x=100, y=96, r=7, ramp='red', string=78)),
               ('horse', dict(x=178, base=150, s=0.85))]),
    'stable': dict(  # 馬小屋: 仕切り戸から顔を出す馬、干し草
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=28, y=44, hang=0)), ('horse_head', dict(x=106, y=40, s=1.8)), ('stall_door', dict(x0=60, x1=164, top=96, base=150)),
               ('haystack', dict(x=196, base=154, r=22)), ('pitch_lean', dict(x=36, base=150))]),
    'stewpot': dict(  # 煮え鍋: 薪の火にかけた黒い大鍋が紫に泡立つ
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(112, 140, 60, 0.6)),
        env=('cave', dict(hz=140, seed=22)),
        items=[('cauldron', dict(x=112, base=150, r=38, brew='purple')), ('wisps', dict(pts=[(120, 50), (90, 40)]))]),
    'fleamarket': dict(  # のみの市: 地べたの絨毯に並ぶ、壺・本・燭台・靴
        light=dict(pool=(112, 110), radius=(170, 105), **DAWN),
        env=('night', dict(hz=104, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.7)),
        items=[('house', dict(x=140, base=110, w=60, h=40, roof_h=22, roof='red', gain=0.6, windows=[(10, 10, 8, 9, True)])),
               ('rug', dict(x=112, y=154, w=200, d=42, ramp='red')),
               ('pots', dict(x=40, base=146, n=3)), ('goblet', dict(x=104, base=144, s=1.3, ramp='silver', wine=False)),
               ('candelabra', dict(x=130, base=140, h=20, arms=1)), ('book', dict(x=150, y=146, w=24, h=4, t=8, ramp='blue')),
               ('boots_pair', dict(x=184, base=148)), ('globe', dict(x=78, base=150, r=9))]),
    'charmhut': dict(  # まじない小屋: 骨と護符の下がる小屋、煙突から紫の煙
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(40, 60, 40, 0.5)),
        env=('forest', dict(hz=128, moon=None, seed=9)),
        items=[('hut', dict(x=112, base=134, w=90, h=46)), ('chimney', dict(x=140, base=96, w=10, h=16)), ('wisps', dict(pts=[(150, 60), (130, 40)])),
               ('charms', dict(x0=70, x1=154, y=92)), ('skull', dict(x=60, y=140, s=0.9)), ('wisp_candle', dict(x=170, base=152))]),
    'gatevillage': dict(  # 関所の村: 屋根つきの木の門の向こうに村の灯
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.05, halo=(60, 80, 40, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.3)),
        items=[('house', dict(x=40, base=118, w=40, h=26, roof_h=20, roof='wood', gain=0.55, windows=[(8, 8, 7, 8, True)])),
               ('house', dict(x=120, base=116, w=44, h=26, roof_h=20, roof='red', gain=0.5, windows=[(10, 8, 7, 8, True), (26, 8, 7, 8, True)])),
               ('road', dict(x=112, top=116, base=160, w0=20, w1=110)), ('gatehouse_roof', dict(x=112, base=152, w=120, h=84)),
               ('fence', dict(x0=0, x1=50, base=150, h=14)), ('fence', dict(x0=176, x1=224, base=150, h=14))]),
    'fields': dict(  # 田畑: 夜明けの畝と、干し草の山
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=('night', dict(hz=96, moon=None, sky_ramp='dawn', stars=0, hills=[(90, 10, 0.5, 0.6, 3)], ground_ramp='leather', ground_gain=0.75)),
        items=[('furrows', dict(y0=110)), ('furrows', dict(y0=134)), ('haystack', dict(x=60, base=124, r=18)), ('haystack', dict(x=170, base=140, r=26)),
               ('tree', dict(x=206, base=100, h=40, kind='oak', gain=0.6, seed=43)), ('fence', dict(x0=0, x1=120, base=158, h=12))]),
    'omen': dict(  # お告げ: 髑髏にとまる鴉、空を裂くほうき星
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, stars=40, sky_ramp='purple', ground_ramp='stone', ground_gain=0.6, clouds=())),
        items=[('comet', dict(x=40, y=30)), ('tree', dict(x=180, base=128, h=96, kind='dead', ramp='cloth', gain=0.7, seed=44)),
               ('rocks', dict(pts=[(112, 150, 90, 24)])), ('skull', dict(x=112, y=118, s=2.0)), ('raven', dict(x=114, y=92, s=1.6))]),
    'tent': dict(  # 幕営: 夜の陣営の大きな天幕と焚き火
        light=dict(pool=(108, 104), radius=(150, 100), fall=1.1, halo=(150, 120, 60, 0.6)),
        env=('night', dict(hz=118, moon=None, stars=40, ground_gain=0.6)),
        items=[('army_tent', dict(x=150, base=132, w=110, h=80, stripe='blue')), ('army_tent', dict(x=36, base=122, w=60, h=44, stripe='red')),
               ('campfire', dict(x=96, base=150, s=1.2)), ('banner_pole', dict(x=206, base=134))]),
    'silkway': dict(  # 絹の道: 夜明けの砂丘を行く駱駝の隊商
        light=dict(pool=(112, 100), radius=(190, 120), **DAWN),
        env=('night', dict(hz=110, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('dunes', dict(y0=110)), ('camel', dict(x=180, base=126, s=0.6, load='blue')), ('camel', dict(x=40, base=140, s=0.8, load='purple')),
               ('camel', dict(x=124, base=154, s=1.35, load='red'))]),
    'hiddengold': dict(  # 隠し金: 木の根もとを掘り返すと、金の箱
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(28, 40, 40, 0.6)),
        env=('night', dict(hz=118, moon=(28, 22, 9, 0.5), ground_gain=0.7)),
        items=[('tree', dict(x=40, base=124, h=96, kind='oak', gain=0.8, seed=45)), ('dug_hole', dict(x=126, y=136)),
               ('chest', dict(x=104, base=146, w=46, h=20, fill='gold')), ('spade_stuck', dict(x=180, base=142)), ('lantern', dict(x=160, y=128, hang=None))]),
    'legation': dict(  # 公館: 色とりどりの国の旗が並ぶ館
        light=dict(pool=(112, 86), radius=(170, 110), **DAWN),
        env=('night', dict(hz=124, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.7)),
        items=[('palace', dict(x=112, base=120, w=180, h=56, wings=True)),
               ('flag_pole', dict(x=30, base=150, ramp='red')), ('flag_pole', dict(x=76, base=154, ramp='blue')),
               ('flag_pole', dict(x=148, base=154, ramp='green')), ('flag_pole', dict(x=194, base=150, ramp='purple'))]),
    'dirtymoney': dict(  # 悪銭: 泥の水たまりに沈む銭、紫のにおい
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.4)),
        env=('night', dict(hz=90, moon=None, ground_ramp='leather', ground_gain=0.6, stars=20)),
        items=[('lantern', dict(x=30, y=50, hang=24)), ('mud', dict(x=112, y=130)),
               ('coin', dict(cx=96, cy=128, r=10, metal='copper', stamp='pip', gain=0.7)), ('coin', dict(cx=126, cy=136, r=10, metal='copper', stamp='star', gain=0.7)),
               ('coin', dict(cx=150, cy=124, r=9, metal='copper', stamp='pip', gain=0.7)), ('wisps', dict(pts=[(110, 100), (140, 96)])),
               ('rat', dict(x=184, base=150))]),
    'pathway': dict(  # けもの道: 森の奥へ続く細い道、獣の足あと
        light=dict(pool=(112, 120), radius=(180, 120), fall=0.9, flat=0.5),
        env=('forest', dict(hz=118, moon=None, seed=12)),
        items=[('trail', dict(x=112, top=118, base=160)), ('tracks', dict(pts=[(104, 154), (118, 146), (106, 138), (116, 132), (110, 126)])),
               ('mushrooms', dict(x=40, base=150)), ('mushrooms', dict(x=170, base=146, n=2))]),
    # ================= 人物・動物 =================
    'watchdog': dict(  # 見張り犬: 門の前に座り、吠える犬
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.7, stars=24)),
        items=[('lantern', dict(x=38, y=64, hang=30)), ('gatehouse_roof', dict(x=150, base=132, w=100, h=80)), ('fence', dict(x0=0, x1=96, base=136, h=16)),
               ('dog', dict(x=96, base=154, s=2.0))]),
    'handyman': dict(  # 何でも屋: 道具袋を下げ、梯子と道具箱を持つ
        light=dict(pool=(104, 90), radius=(150, 100), fall=1.1, halo=(40, 60, 40, 0.5)),
        env=('night', dict(hz=124, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.7)),
        items=[('house', dict(x=130, base=126, w=70, h=50, roof_h=26, roof='red', gain=0.75, windows=[(12, 12, 9, 10, True)], door=(40, 12, 20))),
               ('ladder', dict(x=150, top=60, base=152, w=16)),
               ('figure', dict(x=84, foot=154, h=112, arms=('belly', 'low'), tunic='blue', apron='leather', head='cap', head_ramp='red', legs_ramp='cloth',
                               props=[(1, ('hammer', dict(deg=100, length=2.0)), True), (0, ('toolbox', {}), True)]))]),
    'spicer': dict(  # 香料売り: 色とりどりの香料の袋を前に、頭布の商人
        light=dict(pool=(104, 96), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('awning', dict(x0=0, x1=224, y=0, depth=14, colors=('gold', 'red'))), ('lantern', dict(x=28, y=40, hang=14)),
               ('figure', dict(x=112, foot=150, h=106, arms=('present', 'belly'), robe=True, tunic='green', mantle='gold', head='turban', head_ramp='paper', beard='hair')),
               ('spice_sacks', dict(x=112, base=154))]),
    'silverdealer': dict(  # 銀の商人: 銀の皿と杯を並べ、一枚を掲げる
        light=dict(pool=(104, 92), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('candelabra', dict(x=26, base=76, h=24)), ('shelf', dict(x0=8, x1=46, y=76)),
               ('figure', dict(x=108, foot=164, h=114, arms=('belly', 'lift'), robe=True, tunic='blue', trim='silver', head='hat', head_ramp='blue',
                               props=[(1, 'silver_plate', True)])),
               ('table', dict(x0=24, x1=200, top=126, legs_to=160, front=True, cloth='blue')),
               ('goblet', dict(x=60, base=128, s=1.4, ramp='silver', wine=False)), ('goblet', dict(x=166, base=128, s=1.2, ramp='silver', wine=False)),
               ('stack', dict(cx=134, base=130, r=9, n=5, metal='silver', stamp='tower', seed=42)), ('plate', dict(x=94, y=132))]),
    'drifter': dict(  # 流れ者: 夕暮れの街道を、包みを担いで行く
        light=dict(pool=(104, 90), radius=(170, 110), **DAWN),
        env=('night', dict(hz=110, moon=None, sky_ramp='dawn', stars=0, hills=[(100, 14, 0.5, 0.6, 7)], ground_gain=0.7)),
        items=[('road', dict(x=150, top=110, base=160, w0=6, w1=120, ramp='sand')),
               ('figure', dict(x=96, foot=154, h=110, facing=1, arms=('down', 'lift'), legs='stride', tunic='leather', cloak='cloth', head='hat', head_ramp='cloth',
                               legs_ramp='cloth', props=[(1, ('bindle', {}), True)])),
               ('signpost', dict(x=196, base=140, arrows=(('paper', 1, 0),)))]),
    'mapmaker': dict(  # 測地師: 両脚器を手に、広げた地図を測る
        light=dict(pool=(104, 92), radius=(150, 100), halo=(28, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=112, floor='flag')),
        items=[('candelabra', dict(x=26, base=70, h=24)), ('shelf', dict(x0=8, x1=46, y=70)),
               ('wall_map', dict(x0=136, y0=18, x1=214, y1=80)),
               ('figure', dict(x=96, foot=170, h=118, arms=('present', 'present'), lean=0.1, robe=True, tunic='green', mantle='leather', head='hat', head_ramp='leather',
                               props=[(1, 'held_dividers', True)])),
               ('table', dict(x0=10, x1=214, top=126, legs_to=160, front=True)),
               ('sea_chart', dict(x=112, y=134, w=120, h=16))]),
    'bargainer': dict(  # 値切り上手: 品をはさんで、指を立てて値を詰める
        light=dict(pool=(112, 92), radius=(160, 100), halo=(30, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=112, y=36, hang=0)),
               ('figure', dict(x=56, foot=160, h=108, arms=('belly', 'forward'), tunic='red', head='cap', head_ramp='green', legs_ramp='cloth')),
               ('figure', dict(x=170, foot=160, h=108, facing=-1, arms=('belly', 'present'), robe=True, tunic='purple', head='turban', head_ramp='gold', beard='hair',
                               props=[(1, ('held_coin', dict(metal='silver', r=0.6)), True)])),
               ('table', dict(x0=70, x1=154, top=128, legs_to=160, front=True, cloth='green')),
               ('goblet', dict(x=112, base=130, s=1.6))]),
    'warden': dict(  # 国守: 国境の砦で、旗の下に立つ鎧の領主
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.7)),
        env=('battlement', dict(hz=100, moon=(30, 22, 10, 0.4), parapet=(98, 132))),
        items=[('figure', dict(x=108, foot=154, h=114, arms=('chest', 'low'), tunic='green', armor=True, head='crown', cloak='blue', legs_ramp='cloth',
                               props=[(0, 'letter', True)], behind=[(1, ('banner', dict(ramp='green', deg=-92, length=4.0, flag=(2.4, 2.0))))]))]),
    'brute': dict(  # 暴れ者: 大男が樽を踏み割り、棍棒を振り回す
        light=dict(pool=(104, 88), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('broken_barrel', dict(x=168, base=152)),
               ('figure', dict(x=100, foot=156, h=128, arms=('forward', 'raise'), legs='stride', tunic='leather', head='hair', beard='hair', legs_ramp='cloth',
                               props=[(1, 'club', True)]))]),
    'wheeler': dict(  # 車輪職人: 膝をついて、車輪の輪を槌で嵌める
        light=dict(pool=(104, 96), radius=(150, 100), halo=(26, 44, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('wheel', dict(x=190, y=96, r=24, gain=0.8)), ('wheel', dict(x=160, y=128, r=26)),
               ('figure', dict(x=84, foot=152, h=106, arms=('present', 'raise'), legs='kneel', tunic='red', apron='leather', head='hair', legs_ramp='cloth',
                               props=[(1, ('hammer', dict(deg=-50, length=2.0)), True)]))]),
    'lady': dict(  # 奥方: 窓辺で手紙を持つ、ヴェールの婦人
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(40, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('window_arch', dict(x=22, y=8, w=40, h=76)), ('hang_banner', dict(x=176, top=0, w=28, h=60, ramp='blue', kind='circle')),
               ('figure', dict(x=112, foot=154, h=112, arms=('present', 'belly'), robe=True, gown=True, tunic='red', trim='gold', head='long', hair='hair',
                               props=[(0, 'letter', True)])),
               ('veil', dict(x=112, y=42))]),
    'outlaw': dict(  # 無法者: 手配書の木の下で、覆面の弓の男
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.1, halo=(30, 22, 34, 0.6)),
        env=('forest', dict(hz=124, moon=(30, 22, 9, 0.5), seed=14)),
        items=[('trunk', dict(x=186, top=0, base=126, w=18)), ('poster', dict(x=186, y=56)),
               ('figure', dict(x=100, foot=152, h=110, facing=1, arms=('down', 'hip'), tunic='cloth', head='hood', head_ramp='red', mask='cloth', cloak='green',
                               legs_ramp='cloth', props=[(0, ('bow', dict(height=4.0)), False)], behind=[(0, ('quiver', {}))]))]),
    'magistrate': dict(  # 代官: 御白洲の机で、帳面と印を前に裁く
        light=dict(pool=(108, 96), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=116, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=88, top=0, w=48, h=56, ramp='purple', kind='circle')),
               ('figure', dict(x=112, foot=170, h=118, arms=('present', 'present'), robe=True, tunic='purple', trim='gold', mantle='red', head='hat', head_ramp='cloth',
                               beard='paper')),
               ('table', dict(x0=10, x1=214, top=128, legs_to=160, front=True, cloth='red')),
               ('doc', dict(x=86, y=134, w=60, h=14, seal=False, lines=2, sign=False)), ('wax_seal', dict(x=140, y=134, r=8))]),
}
