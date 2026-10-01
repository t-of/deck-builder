"""昇る日（cards-risingsun.js）の 35 枚の場面データ。書き方は scenes.py の冒頭を見る。
王国 25 とイベント 10。和の町と山と社の札なので、夜明けの朱い空・提灯の夜の横丁・障子の室内を混ぜ、
人物は髷・烏帽子・兜・笠で描き分ける。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


SHOJI = ('room', dict(wall='shoji', hz=120, floor='planks'))

SCENES = {
    'fishseller': dict(  # 棒手振り: 朝の町を、天秤棒に魚の籠を担いで売り歩く
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=126, ground='sand', hills=()),
        items=[('house', dict(x=0, base=124, w=70, h=40, roof_h=20, wall='paper', roof='wood', windows=[(10, 10, 14, 12, True)])),
               ('house', dict(x=160, base=124, w=64, h=40, roof_h=20, wall='paper', roof='wood', windows=[(30, 10, 14, 12, True)])),
               ('figure', dict(x=112, foot=156, h=110, arms=('lift', 'lift'), legs='stride', tunic='blue', head='bandana', head_ramp='paper', legs_ramp='skin', boots='paper', face=True,
                               props=[(1, ('tenbin', {}), True)]))]),
    'snakecharmer': dict(  # 蛇遣い: 夜の見世物小屋で、笛の音に籠から蛇が立ち上がる
        light=dict(pool=(120, 104), radius=(150, 100), fall=1.15, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('paper_lantern', dict(x=30, y=50, r=10, ramp='fire', string=0)),
               ('figure', dict(x=70, foot=154, h=104, arms=('present', 'present'), legs='kneel', tunic='purple', head='turban', head_ramp='red', legs_ramp='cloth', face=True,
                               props=[(1, ('flute', {}), True)])),
               ('snake_basket', dict(x=150, base=156, r=24)), ('snake', dict(x=150, base=122, s=1.1))]),
    'courtnoble': dict(  # 殿上人: 御簾の下がる殿で、笏を持つ烏帽子の公家
        light=dict(pool=(108, 92), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=SHOJI,
        items=[('hang_banner', dict(x=170, top=0, w=40, h=56, ramp='green', kind='chevron')),
               ('figure', dict(x=104, foot=156, h=114, arms=('belly', 'present'), robe=True, tunic='purple', mantle='purple', trim='gold', head='eboshi', head_ramp='cloth', face=True,
                               props=[(1, ('shaku', {}), True)]))]),
    'meister': dict(  # 名人: 鍛冶場の炉の火の前で、打ち上げた刀を見定める
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(30, 62, 54, 0.9), key=0.8),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('forge', dict(x=4, y=44, w=56, h=52)), ('anvil', dict(x=176, base=152, s=1.0)),
               ('figure', dict(x=108, foot=154, h=112, arms=('belly', 'lift'), robe=True, tunic='paper', head='eboshi', head_ramp='cloth', face=True, beard='paper',
                               props=[(1, ('katana', dict(deg=-75, length=4.4)), True)]))]),
    'ferryboat': dict(  # 屋形船: 夜の川に浮かぶ、提灯をつらねた屋形船
        light=dict(pool=(112, 110), radius=(170, 110), fall=1.05, halo=(40, 30, 40, 0.5)),
        env=('coast', dict(hz=92, moon=(40, 30, 9, 0.4))),
        items=[('skyline', dict(x0=0, x1=224, base=92, gain=0.5, seed=23)), ('gozabune', dict(x=112, wl=146, w=170)),
               ('lantern_string', dict(y0=86, y1=96, colors=('red', 'gold', 'red', 'gold', 'red')))]),
    'cellar2': dict(  # 土蔵: 月夜に扉を開けた蔵、中の灯に米俵と千両箱
        light=dict(pool=(104, 104), radius=(150, 100), fall=1.1, halo=(100, 110, 40, 0.5)),
        env=_night(moon=(30, 20, 8, 0.4), hz=134, ground='stone', gain=0.55),
        items=[('kura', dict(x=104, base=138, w=120, h=76)), ('lantern', dict(x=104, y=96, hang=0)),
               ('rice_bales', dict(x=176, base=156, rows=(2, 1), r=12)), ('chest', dict(x=30, base=156, w=44, h=18, open_=False, band='silver'))]),
    'backalley': dict(  # 横丁: 提灯と暖簾の並ぶ、夜の細い路地
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(112, 60, 50, 0.5)),
        env=_night(moon=None, hz=118, ground='stone', gain=0.55),
        items=[('house', dict(x=-10, base=150, w=80, h=110, roof_h=10, wall='paper', roof='wood', windows=[(30, 20, 24, 30, True), (30, 70, 24, 20, True)])),
               ('house', dict(x=154, base=150, w=80, h=110, roof_h=10, wall='paper', roof='wood', windows=[(16, 20, 24, 30, True), (16, 70, 24, 20, True)])),
               ('road', dict(x=112, top=118, base=160, w0=20, w1=90, ramp='stone')),
               ('noren', dict(x0=60, x1=84, y=96, ramp='blue')), ('noren', dict(x0=140, x1=164, y=96, ramp='red')),
               ('paper_lantern', dict(x=74, y=70, r=8, ramp='fire', string=56)), ('paper_lantern', dict(x=150, y=70, r=8, ramp='fire', string=56)),
               ('paper_lantern', dict(x=112, y=104, r=4, ramp='fire', string=96))]),
    'switchover': dict(  # 入れ替え: 両替の帳場で、小判と銭を天秤で量り替える
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='shoji', hz=96, floor='table')),
        items=[('balance', dict(x=112, base=150, h=64, tilt=5, left='gold', right='copper', s=1.4)), ('koban_coin', dict(x=40, y=140, w=18, h=28, tilt=0.5)),
               ('holed_coin', dict(x=188, y=136, r=12)), ('swap_arrows', dict(x=112, y=60))]),
    'kunoichi': dict(  # くノ一: 満月の瓦屋根に身をかがめ、苦無を構える
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(56, 40, 50, 0.7)),
        env=_night(moon=(56, 40, 22), ground=None, stars=30),
        items=[('roof_ridge', dict(y=120, ramp='cloth')),
               ('figure', dict(x=124, foot=150, h=106, facing=-1, arms=('forward', 'chest'), legs='crouch', lean=0.15, tunic='purple', head='hood', head_ramp='cloth', mask='cloth', legs_ramp='cloth',
                               props=[(1, ('dagger', dict(deg=-20)), True)]))]),
    'poet': dict(  # 詠み人: 夜桜の下で、短冊に筆を走らせる
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.05, halo=(40, 30, 40, 0.6)),
        env=_night(moon=(40, 30, 11), hz=126, gain=0.55),
        items=[('sakura', dict(x=170, base=134, h=120, seed=3)),
               ('figure', dict(x=92, foot=154, h=104, arms=('present', 'present'), legs='kneel', robe=True, tunic='blue', mantle='paper', head='eboshi', head_ramp='cloth', face=True,
                               props=[(1, ('brush_pen', {}), True), (0, ('letter', {}), True)]))]),
    'rivershrine': dict(  # 川の祠: 夜明けの川に足を浸す鳥居と、岸の祠
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=100, moon=None, sky_ramp='dawn', stars=0, ground_ramp='foliage', ground_gain=0.6, hills=[(92, 12, 0.5, 0.6, 4)])),
        items=[('river', dict(y0=100)), ('torii', dict(x=120, base=146, w=110, h=90)), ('wayside_shrine', dict(x=36, base=140)), ('reeds', dict(xs=(190, 206, 220), base=150))]),
    'hillvillage': dict(  # 山あいの村: 滝の見える谷の、茅葺きの家々
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=140, ground='foliage', hills=()),
        items=[('peaks', dict()), ('cascade', dict(x=176, y0=20, y1=120)), ('terraces', dict(y0=116)),
               ('house', dict(x=30, base=134, w=56, h=26, roof_h=30, wall='paper', roof='wood', windows=[(10, 8, 10, 9, True)])),
               ('house', dict(x=96, base=146, w=64, h=28, roof_h=34, wall='paper', roof='wood', chimney=0.5, windows=[(10, 9, 10, 10, True), (42, 9, 10, 10, True)])),
               ('fog', dict(bands=[(112, 8)], gain=0.7))]),
    'goldmine': dict(  # 金の鉱山: 山肌の坑口から、金を積んだ車が出てくる
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(112, 100, 50, 0.5)),
        env=_dawn(hz=130, ground='stone', hills=((80, 40, 0.5, 0.6, 2),)),
        items=[('cave_mouth', dict(x=100, base=134, w=110, h=86)), ('beam_frame', dict(x0=50, x1=150, top=52, bottom=134, w=7)), ('lantern', dict(x=100, y=60, hang=10)),
               ('rails', dict(y=150)), ('gems', dict(pts=[(170, 150, 5, 'gold'), (182, 154, 4, 'gold'), (60, 152, 4, 'gold')])),
               ('cart', dict(x=120, base=152, w=60, h=24, ore='gold')), ('pickaxe', dict(x=190, y=150, ang=-70, length=40))]),
    'imperialenvoy': dict(  # 宮の使い: 大門の前で、勅の巻物を掲げる使者
        light=dict(pool=(108, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=132, ground='sand', hills=()),
        items=[('great_gate', dict(x=150, base=134, w=150, h=110)),
               ('figure', dict(x=80, foot=156, h=112, arms=('belly', 'lift'), robe=True, tunic='red', mantle='red', trim='gold', head='eboshi', head_ramp='cloth', face=True,
                               props=[(1, ('scroll', dict(length=2.2)), True)]))]),
    'kitsune': dict(  # 化け狐: 夜の社の前に座る狐と、青い狐火
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(112, 80, 50, 0.5)),
        env=_night(moon=None, hz=124, ground='stone', gain=0.5, sky_ramp='purple'),
        items=[('torii', dict(x=112, base=126, w=180, h=104)), ('fox', dict(x=104, base=154, s=1.9, facing=-1)),
               ('will_o_wisp', dict(x=50, y=90, r=6)), ('will_o_wisp', dict(x=176, y=84, r=5)), ('will_o_wisp', dict(x=150, y=50, r=4))]),
    'palanquin': dict(  # かご: 夜明けの街道を、二人の担ぎ手が運ぶ駕籠
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, ground='sand'),
        items=[('tree', dict(x=200, base=128, h=70, kind='pine', gain=0.75, seed=71)),
               ('figure', dict(x=36, foot=156, h=100, arms=('lift', 'down'), legs='stride', tunic='paper', head='bandana', head_ramp='blue', legs_ramp='skin', boots='paper')),
               ('kago', dict(x=112, base=136, w=66, h=46)),
               ('figure', dict(x=188, foot=156, h=100, arms=('down', 'lift'), legs='stride', tunic='paper', head='bandana', head_ramp='blue', legs_ramp='skin', boots='paper'))]),
    'ricedealer': dict(  # 米問屋: 蔵の前の米俵の山と、算盤を持つ主人
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='sand'),
        items=[('kura', dict(x=60, base=128, w=100, h=60)), ('rice_bales', dict(x=176, base=156, rows=(3, 2, 1), r=12)),
               ('figure', dict(x=100, foot=156, h=110, arms=('chest', 'chest'), robe=True, tunic='leather', mantle='blue', head='topknot', face=True,
                               props=[(0, ('held_abacus', {}), True)]))]),
    'ronin': dict(  # 素浪人: 夕暮れの風の野に立つ、破れ笠の浪人
        light=dict(pool=(108, 92), radius=(170, 110), **DAWN),
        env=_dawn(hz=128, ground='leather', hills=((110, 14, 0.5, 0.5, 8),)),
        items=[('wind_streaks', dict()), ('leaves', dict(n=16)), ('weeds', dict(x=190, base=152, n=10, h=20, ramp='leather')),
               ('figure', dict(x=104, foot=156, h=114, arms=('hip', 'down'), tunic='cloth', robe=True, mantle='cloth', head='jingasa', head_ramp='sand', face=True,
                               behind=[(0, ('katana', dict(deg=150, length=3.6)))]))]),
    'tanuki': dict(  # 化け狸: 月夜の竹藪で、笠をかぶり徳利を下げた狸
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=('forest', dict(hz=128, moon=(40, 30, 10), seed=73)),
        items=[('tanuki', dict(x=112, base=154, s=1.3))]),
    'teahouse': dict(  # 茶店: 朱の野点傘の下の床几に、湯呑と団子
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, ground='sand'),
        items=[('house', dict(x=140, base=124, w=84, h=40, roof_h=22, wall='paper', roof='wood', windows=[(10, 10, 16, 14, True)])), ('noren', dict(x0=170, x1=214, y=88, ramp='blue')),
               ('sakura', dict(x=30, base=130, h=90, seed=5)), ('parasol', dict(x=104, base=150, h=110, r=60)), ('red_bench', dict(x=104, base=156, w=110))]),
    'peakshrine': dict(  # 峰の祠: 雲海から昇る日と、山頂の小さな祠と鳥居
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=150, ground='stone', hills=()),
        items=[('sun', dict(x=56, y=86, r=20)), ('fog', dict(bands=[(108, 14), (122, 10)], gain=0.9)), ('rocks', dict(pts=[(130, 172, 200, 66)])),
               ('torii', dict(x=130, base=124, w=70, h=56)), ('wayside_shrine', dict(x=136, base=128))]),
    'bushi': dict(  # 武士: 篝火の陣で、鍬形の兜に鎧の武士が槍を立てる
        light=dict(pool=(108, 92), radius=(160, 105), fall=1.1, halo=(30, 70, 40, 0.7)),
        env=_night(moon=None, hz=128, ground='stone', gain=0.55),
        items=[('brazier', dict(x=26, base=126)), ('jinmaku', dict(x0=110, x1=224, top=56, base=128, crest='gold')),
               ('figure', dict(x=100, foot=156, h=116, arms=('belly', 'lift'), tunic='red', armor=True, head='kabuto', head_ramp='cloth', legs_ramp='cloth', face=True,
                               behind=[(1, ('staff', dict(deg=-92, length=5.6, top='spear', below=2.6)))]))]),
    'tonosama': dict(  # 殿様: 城の広間の金の襖の前で、扇を持つ殿様
        light=dict(pool=(108, 92), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.5)),
        env=('room', dict(wall='shoji', hz=124, floor='planks')),
        items=[('rug', dict(x=112, y=148, w=180, d=30, ramp='green')),
               ('figure', dict(x=112, foot=156, h=116, arms=('belly', 'lift'), robe=True, tunic='blue', mantle='blue', trim='gold', head='topknot', face=True,
                               props=[(1, ('fan', dict(ramp='gold')), True)]))]),
    'painter': dict(  # 絵描き: 障子の部屋で、画架に山水を描く
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(30, 40, 40, 0.5)),
        env=SHOJI,
        items=[('easel', dict(x=156, base=152, w=70, h=60)), ('pots', dict(x=196, base=154, n=2)),
               ('figure', dict(x=84, foot=154, h=106, arms=('belly', 'forward'), tunic='green', apron='paper', head='topknot', face=True, legs_ramp='cloth',
                               props=[(1, ('brush_pen', {}), True)]))]),
    'ricebale': dict(  # 米俵: 赤い縄をかけて積んだ俵と小判
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='plank', hz=96, floor='planks')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('rice_bales', dict(x=112, base=156, rows=(4, 3, 2), r=15)),
               ('koban_coin', dict(x=194, y=146, w=16, h=24, tilt=0.5))]),
    # ================= イベント 10 =================
    're_amass': dict(  # 寄せ集め: 荷車に山と積んだ俵・箱・壺
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN), env=_dawn(hz=126, ground='sand'),
        items=[('flat_cart', dict(x=112, base=152, w=150)), ('rice_bales', dict(x=70, base=126, rows=(2, 1), r=11)), ('crate', dict(x=110, y=96, w=30, h=28)),
               ('pots', dict(x=160, base=126, n=2)), ('sack', dict(x=186, base=126, r=10))]),
    're_ascetic': dict(  # 修行: 夜明けの滝に打たれて座る行者
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN), env=('cave', dict(hz=130, seed=31)),
        items=[('cascade', dict(x=112, y0=0, y1=140)), ('tide_pool', dict(x=112, y=146, rx=90, ry=12)),
               ('figure', dict(x=112, foot=150, h=100, arms=('chest', 'chest'), legs='kneel', tunic='paper', robe=True, head='hair', face=True)), ('fog', dict(bands=[(140, 8)], gain=0.8))]),
    're_credit': dict(  # つけ払い: 帳場の大福帳と、つけの札と算盤
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='shoji', hz=86, floor='table')),
        items=[('open_book', dict(x=96, y=124, w=40, h=20)), ('abacus', dict(x=170, y=130, w=60, h=24)), ('debt_tokens', dict(pts=[(40, 140), (52, 148), (186, 100)])),
               ('candle', dict(x=28, base=84, h=12, r=3))]),
    're_foresight': dict(  # 先読み: 峠の上で、手をかざして夜明けの先を見る
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN), env=('pass', dict(hz=124, moon=None)),
        items=[('sun', dict(x=48, y=96, r=14)),
               ('figure', dict(x=124, foot=156, h=112, facing=-1, arms=('down', (0.9, -0.2, 0.1, -0.85)), tunic='blue', cloak='paper', head='jingasa', head_ramp='sand', legs_ramp='cloth', face=True))]),
    're_kintsugi': dict(  # 継ぎ直し: 割れを金で継いだ黒い椀
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.5), key=0.85),
        env=('icon', dict(hz=110, wall='plank', cloth='green', cloth_gain=0.6)),
        items=[('candle', dict(x=28, base=108, h=12, r=3)), ('kintsugi_bowl', dict(x=112, base=150, r=46))]),
    're_practice': dict(  # おさらい: 道場の的に刺さった矢と、弓
        light=dict(pool=(112, 96), radius=(160, 105), **WARM, halo=(30, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('window', dict(x=12, y=12, w=30, h=40, lit=True)), ('target', dict(x=150, y=84, r=36)),
               ('figure', dict(x=70, foot=154, h=110, arms=('pull', 'aim'), legs='stride', tunic='paper', legs_ramp='blue', head='topknot', face=True, props=[(1, 'bow', True)]))]),
    're_seatrade': dict(  # 海の商い: 港の蔵の前に着いた、荷を積んだ船
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=96, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('kura', dict(x=44, base=118, w=80, h=46)), ('ship', dict(x=150, wl=132, s=0.8, sails='paper', masts=1)), ('dock', dict(y=126, x0=0, x1=100)),
               ('rice_bales', dict(x=60, base=150, rows=(3, 2), r=9)), ('crate', dict(x=90, y=128, w=22, h=20))]),
    're_tribute': dict(  # 献上: 社の前の三方に供えた米・餅・橙と徳利
        light=dict(pool=(112, 100), radius=(150, 100), **WARM, halo=(30, 50, 40, 0.6)),
        env=SHOJI,
        items=[('candle_row', dict(x0=10, x1=60, base=118)), ('candle_row', dict(x0=164, x1=214, base=118)), ('sanbo', dict(x=112, base=154, w=64))]),
    're_gather': dict(  # 取りそろえ: 三段の重箱と、並べた小判・俵・魚
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='shoji', hz=96, floor='table')),
        items=[('jubako', dict(x=104, base=150, w=70, h=22, n=3)), ('koban_coin', dict(x=40, y=144, w=18, h=28, tilt=0.5)),
               ('basket', dict(x=184, base=152, w=30, h=10, kind='fish', n=3))]),
    're_continue': dict(  # 続行: 奥へどこまでも続く、千本鳥居の道
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.05, halo=(112, 70, 40, 0.4)),
        env=_night(moon=None, hz=118, ground='stone', gain=0.55),
        items=[('road', dict(x=118, top=118, base=160, w0=12, w1=120, ramp='stone')), ('torii_tunnel', dict(x=112, base=162, n=8)),
               ('paper_lantern', dict(x=40, y=120, r=6, ramp='fire', string=None)), ('paper_lantern', dict(x=190, y=120, r=6, ramp='fire', string=None))]),
}
