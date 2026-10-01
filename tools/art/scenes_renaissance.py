"""ルネサンス（cards-renaissance.js）の 44 枚の場面データ。書き方は scenes.py の冒頭を見る。
王国 25（「もの」5 枚 a_* は scenes.py）とプロジェクト 19。和の商いと学芸の札が多いので、
人物は烏帽子・髷・陣笠で描き分け、プロジェクトは建物と道具を主役に、夜明け・昼の灯を多めに散らす。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


SCENES = {
    # ================= 王国 25 =================
    'gatekeeper': dict(  # 関守: 関所の門の前で、陣笠をかぶり槍を立てる番人
        light=dict(pool=(108, 90), radius=(160, 105), fall=1.1, halo=(36, 40, 40, 0.6)),
        env=_night(moon=None, ground='stone', gain=0.65, hz=126),
        items=[('great_gate', dict(x=150, base=128, w=150, h=110)), ('lantern', dict(x=34, y=40, hang=14)),
               ('figure', dict(x=84, foot=154, h=112, arms=('belly', 'lift'), tunic='blue', head='jingasa', head_ramp='cloth', legs_ramp='cloth', belt='red',
                               behind=[(1, ('staff', dict(deg=-92, length=5.4, top='spear', below=2.8)))]))]),
    'koban': dict(  # 小判: 緋の布の上に扇形に並べた小判
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6), key=0.8),
        env=('icon', dict(hz=86, wall='plank', cloth='red', cloth_gain=0.7)),
        items=[('candle', dict(x=28, base=84, h=14, r=3)),
               ('koban_coin', dict(x=66, y=118, w=26, h=40, tilt=0.8)), ('koban_coin', dict(x=158, y=118, w=26, h=40, tilt=0.8)),
               ('koban_coin', dict(x=88, y=110, w=28, h=44, tilt=0.9)), ('koban_coin', dict(x=136, y=110, w=28, h=44, tilt=0.9)),
               ('koban_coin', dict(x=112, y=106, w=32, h=50)), ('koban_coin', dict(x=186, y=146, w=22, h=34, tilt=0.45))]),
    'lackeys': dict(  # 手下衆: 提灯の路地に、棍棒を担いだ親分と手下 2 人
        light=dict(pool=(112, 92), radius=(150, 100), fall=1.15, halo=(40, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='flag', bw=16, bh=8)),
        items=[('paper_lantern', dict(x=40, y=40, r=9, ramp='fire', string=0)),
               ('figure', dict(x=56, foot=146, h=92, arms=('down', 'hip'), tunic='cloth', head='hair', legs_ramp='cloth', facing=1)),
               ('figure', dict(x=168, foot=146, h=94, arms=('hip', 'down'), tunic='green', head='topknot', legs_ramp='cloth', facing=-1)),
               ('figure', dict(x=112, foot=156, h=112, arms=('hip', 'raise'), tunic='red', head='topknot', legs_ramp='cloth', belt='gold', face=True,
                               props=[(1, ('club', {}), True)]))]),
    'troupe': dict(  # 旅一座: 夜明けの野営で、幌馬車の前でお手玉をする芸人
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('wagon', dict(x=170, base=140, w=86, cover='red')), ('campfire', dict(x=36, base=146, s=0.9)),
               ('figure', dict(x=100, foot=156, h=110, arms=('lift', 'lift'), tunic='purple', head='jester', legs_ramp='red', face=True,
                               props=[(1, ('juggle', {}), True)]))]),
    'cargo': dict(  # 荷船: 夜明けの川を下る、俵と木箱を積んだ平舟
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=92, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('hills', dict(base=92, amp=10, gain=0.5, depth=0.5, seed=4)), ('sun', dict(x=50, y=80, r=12)),
               ('rice_bales', dict(x=82, base=126, rows=(4, 3, 2), r=10)), ('crate', dict(x=128, y=98, w=28, h=28)), ('crate', dict(x=156, y=106, w=22, h=20, gain=0.9)),
               ('sack', dict(x=184, base=126, r=9)), ('barge', dict(x=112, wl=140, w=176, h=18))]),
    'trial2': dict(  # 試し: 道場の板の間で、刀を振り下ろし巻藁を斬る
        light=dict(pool=(112, 96), radius=(160, 105), **WARM, halo=(30, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('window', dict(x=14, y=14, w=34, h=40, lit=True)),
               ('makiwara', dict(x=164, base=150, h=80)),
               ('figure', dict(x=90, foot=154, h=112, arms=((0.7, 0.9, 1.6, 1.0), (0.8, 0.85, 1.7, 0.9)), legs='stride', lean=0.1, tunic='paper', robe=True, head='topknot', legs_ramp='cloth', belt='blue', face=True,
                               props=[(1, ('katana', dict(deg=25, length=4.0)), True)]))]),
    'improve': dict(  # 手入れ: 縁側の台に置いた盆栽と、剪定の鋏
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(30, 34, 40, 0.5)),
        env=('room', dict(wall='shoji', hz=110, floor='planks')),
        items=[('window', dict(x=14, y=10, w=44, h=48, lit=True)),
               ('table', dict(x0=50, x1=174, top=124, legs_to=156)),
               ('bonsai', dict(x=112, base=124, s=1.25)),
               ('scissors', dict(x=172, y=134))]),
    'flagbearer': dict(  # 旗持ち: 夜明けの野で、長いのぼりを掲げて立つ
        light=dict(pool=(108, 88), radius=(170, 110), **DAWN),
        env=_dawn(hz=128, hills=((110, 16, 0.5, 0.5, 6),)),
        items=[('figure', dict(x=104, foot=154, h=112, arms=('lift', 'belly'), tunic='blue', armor=True, head='jingasa', head_ramp='cloth', legs_ramp='cloth',
                               props=[(0, ('banner', dict(ramp='red', deg=-92, length=3.9, flag=(2.6, 3.0))), False)]))]),
    'lair2': dict(  # 隠れ家: 夜の森の岩陰に口を開けた洞穴、奥にともる灯
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.1, halo=(112, 120, 60, 0.9)),
        env=('forest', dict(hz=124, moon=None, seed=71)),
        items=[('cave_mouth', dict(x=112, base=138, w=140, h=108)), ('bedrolls', dict(pts=[(146, 132, 'red')])), ('campfire', dict(x=104, base=136, s=1.0)),
               ('weeds', dict(x=40, base=146, n=8, h=18)), ('weeds', dict(x=190, base=148, n=8, h=16)), ('crate', dict(x=142, y=118, w=18, h=16, gain=0.8))]),
    'inventor': dict(  # 発明の人: 歯車の工房で、からくり人形にねじを巻く
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(26, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('gears', dict(x=180, y=40)), ('blueprint', dict(x=120, y=40, w=80, h=40)),
               ('automaton', dict(x=158, base=152, s=1.2)),
               ('figure', dict(x=80, foot=154, h=110, arms=('present', 'forward'), tunic='leather', apron='leather', head='cap', head_ramp='blue', legs_ramp='cloth', face=True,
                               props=[(1, ('wrench', {}), True)]))]),
    'mountainvillage': dict(  # 山里: 雪の峰のふもと、段々に寄り合う家々
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=140, ground='foliage', hills=()),
        items=[('peaks', dict()), ('terraces', dict(y0=112)),
               ('house', dict(x=40, base=124, w=40, h=24, roof_h=20, roof='wood', windows=[(8, 8, 7, 8, True)])),
               ('house', dict(x=126, base=118, w=36, h=22, roof_h=18, roof='red', gain=0.85, windows=[(12, 8, 7, 7, True)])),
               ('house', dict(x=80, base=146, w=50, h=30, roof_h=24, roof='wood', chimney=0.5, windows=[(9, 9, 8, 9, True), (32, 9, 8, 9, True)])),
               ('house', dict(x=160, base=150, w=44, h=26, roof_h=20, roof='red', windows=[(8, 8, 8, 8, True)])),
               ('smoke', dict(pts=[(96, 100), (92, 90), (98, 80)]))]),
    'backer': dict(  # 後ろ盾: 広間で金の袋を差し出す、毛皮の肩掛けの旦那
        light=dict(pool=(108, 90), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('candelabra', dict(x=26, base=72, h=24)), ('shelf', dict(x0=8, x1=46, y=72)),
               ('hang_banner', dict(x=176, top=0, w=28, h=66, ramp='green', kind='circle')),
               ('figure', dict(x=104, foot=154, h=114, arms=('belly', 'present'), robe=True, tunic='green', trim='gold', mantle='leather', head='hat', head_ramp='red',
                               beard='hair', face=True, props=[(1, ('bag', dict(ramp='red', r=0.9)), True)])),
               ('chest', dict(x=150, base=152, w=54, h=24, fill='gold'))]),
    'kannushi': dict(  # 神主: 鳥居の前で、烏帽子の神主が幣を振る
        light=dict(pool=(108, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='sand'),
        items=[('torii', dict(x=112, base=128, w=180, h=110)), ('shimenawa_tree', dict(x=206, base=130, h=110)),
               ('figure', dict(x=104, foot=156, h=112, arms=('belly', 'lift'), robe=True, tunic='paper', mantle='paper', head='eboshi', head_ramp='cloth', belt=None, face=True,
                               props=[(1, ('gohei', {}), True)]))]),
    'research': dict(  # 調べもの: 書見台の灯で、虫眼鏡で古い本を読みくらべる
        light=dict(pool=(112, 108), radius=(150, 100), **WARM, halo=(32, 46, 40, 0.7)),
        env=('room', dict(wall='plank', hz=86, floor='table')),
        items=[('shelf', dict(x0=60, x1=220, y=40)), ('books_row', dict(x0=64, x1=216, base=40, seed=11)),
               ('candle', dict(x=32, base=84, h=14, r=3)),
               ('book', dict(x=36, y=124, w=34, h=6, t=12, ramp='blue')), ('book', dict(x=40, y=114, w=30, h=5, t=10, ramp='red')),
               ('open_book', dict(x=124, y=126, w=34, h=18)), ('magnifier', dict(x=136, y=118, r=15, ang=40)), ('scrolls', dict(x=196, base=146))]),
    'draper': dict(  # 呉服屋: 暖簾の奥の衣桁に、金の柄の着物
        light=dict(pool=(112, 92), radius=(150, 100), **WARM, halo=(26, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=128, floor='planks')),
        items=[('noren', dict(x0=0, x1=224, y=0, ramp='blue')), ('kimono_rack', dict(x=112, base=148, w=150, h=118, ramp='red')),
               ('cloth_bolts', dict(x=30, base=156)), ('cloth_bolts', dict(x=196, base=158))]),
    'yamauba': dict(  # 山姥: 山の岩屋で焚き火を前に、白髪を乱して包丁を研ぐ老婆
        light=dict(pool=(112, 100), radius=(140, 100), fall=1.15, halo=(40, 130, 50, 0.8)),
        env=('cave', dict(hz=130, seed=7)),
        items=[('campfire', dict(x=40, base=150, s=1.1)), ('cauldron', dict(x=176, base=154, r=22, brew='green')),
               ('figure', dict(x=112, foot=154, h=108, arms=('hip', 'lift'), lean=0.15, tunic='purple', robe=True, mantle='leather', head='long', hair='paper', face=True,
                               props=[(1, ('dagger', dict(deg=-70)), True)])),
               ('skull', dict(x=200, y=124, s=0.7))]),
    'recruiter': dict(  # 口入れ屋: 帳場で、壁の求人の札を指さす
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.15, halo=(24, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('candle', dict(x=26, base=60, h=12, r=3)), ('shelf', dict(x0=10, x1=44, y=60)),
               ('notice', dict(x=168, top=20, w=60, h=66)),
               ('figure', dict(x=94, foot=154, h=112, arms=('belly', 'aim'), robe=True, tunic='blue', mantle='cloth', head='topknot', face=True,
                               props=[(0, ('held_abacus', {}), True)])),
               ('table', dict(x0=130, x1=220, top=128, legs_to=160, front=True))]),
    'baton': dict(  # 采配: 陣幕の前で、采配を振るう鎧の大将
        light=dict(pool=(108, 88), radius=(160, 105), fall=1.1, halo=(30, 60, 40, 0.7)),
        env=_night(moon=None, hz=128, ground='stone', gain=0.6),
        items=[('clothesline', dict(x0=0, x1=224, y=60, cloths=('paper', 'paper', 'paper', 'paper'))), ('brazier', dict(x=28, base=124)),
               ('nobori', dict(x=190, top=16, base=140, w=22, ramp='blue')),
               ('figure', dict(x=104, foot=156, h=114, arms=('belly', 'raise'), tunic='red', armor=True, head='helm', cloak='red', legs_ramp='cloth', face=True,
                               props=[(1, ('saihai', {}), True)]))]),
    'student': dict(  # 書生: 行灯のもとで、膝をついて本を読みふける若者
        light=dict(pool=(112, 104), radius=(140, 100), **WARM, halo=(40, 90, 40, 0.7)),
        env=('room', dict(wall='shoji', hz=112, floor='planks')),
        items=[('paper_lantern', dict(x=38, y=96, r=14, ramp='fire', string=None)),
               ('book', dict(x=176, y=150, w=30, h=6, t=10, ramp='green')), ('book', dict(x=180, y=142, w=26, h=5, t=10, ramp='blue')), ('book', dict(x=178, y=135, w=24, h=5, t=9, ramp='red')),
               ('figure', dict(x=112, foot=154, h=108, arms=('present', 'present'), legs='kneel', tunic='blue', head='hair', legs_ramp='cloth', young=True, face=True,
                               props=[(1, ('book', dict(open_=True, w=1.6, h=1.3)), True)]))]),
    'carver': dict(  # 彫り師: 木屑の散る作業場で、大きなこけしを彫り上げる
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(26, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('tool_rack', dict(x0=60, x1=210, y=16, tools=('saw', 'hammer', 'pliers'))),
               ('kokeshi', dict(x=150, base=152, s=1.15)),
               ('figure', dict(x=72, foot=154, h=104, arms=((1.0, 0.9, 2.6, 0.7), 'forward'), legs='kneel', tunic='leather', apron='cloth', head='topknot', legs_ramp='cloth',
                               props=[(1, ('chisel', dict(deg=0)), True)])),
               ('shavings', dict(pts=[(120, 152), (130, 154), (176, 152), (110, 156)]))]),
    'clairvoyant': dict(  # 千里眼: 紫の天幕で、水晶玉に遠くの景色を映す占い師
        light=dict(pool=(112, 96), radius=(140, 100), fall=1.2, halo=(112, 110, 50, 0.6)),
        env=('room', dict(wall='plank', hz=118, floor='table', floor_ramp='purple', floor_gain=0.7)),
        items=[('constellation', dict(pts=[(30, 30), (54, 20), (70, 40), (170, 24), (196, 40)])),
               ('figure', dict(x=112, foot=150, h=110, arms=('forward', 'forward'), robe=True, tunic='purple', trim='gold', head='hood', head_ramp='purple', face=True)),
               ('crystal_ball', dict(x=112, base=150, r=28, ramp='blue'))]),
    'spices': dict(  # 香辛の品: 市の台に盛った五色の香辛料
        light=dict(pool=(112, 110), radius=(160, 100), **WARM, halo=(30, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=90, floor='table')),
        items=[('awning', dict(x0=0, x1=224, y=0, depth=18, colors=('green', 'paper'))), ('spice_sacks', dict(x=190, base=96)),
               ('spice_heaps', dict(x=112, base=148, s=1.1))]),
    'swordsman': dict(  # 剣豪: 夜明けの野に、刀を構えて立つ髷の剣士
        light=dict(pool=(108, 88), radius=(170, 110), **DAWN),
        env=_dawn(hz=130, ground='foliage', hills=((112, 14, 0.5, 0.5, 9),)),
        items=[('sun', dict(x=48, y=96, r=14)), ('tree', dict(x=196, base=134, h=90, kind='pine', gain=0.75, seed=12)),
               ('figure', dict(x=108, foot=156, h=114, arms=('chest', 'chest'), legs='stride', tunic='cloth', robe=True, mantle='blue', head='topknot', face=True,
                               props=[(1, ('katana', dict(deg=-70, length=4.4)), True)]))]),
    'treasurer': dict(  # 勘定方: 帳場で算盤をはじく。卓に小判と帳簿
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.7)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('candle', dict(x=28, base=54, h=12, r=3, holder=True)), ('shelf', dict(x0=10, x1=46, y=54)),
               ('drawers', dict(x0=140, y0=14, cols=3, rows=4, w=24, h=18, open_at=(1, 2))),
               ('figure', dict(x=96, foot=158, h=112, arms=('chest', 'chest'), robe=True, tunic='cloth', mantle='blue', head='topknot', face=True)),
               ('table', dict(x0=20, x1=204, top=122, legs_to=160, front=True)),
               ('abacus', dict(x=96, y=128, w=70, h=26)), ('koban_coin', dict(x=162, y=132, w=16, h=24, tilt=0.5)), ('koban_coin', dict(x=180, y=136, w=16, h=24, tilt=0.5)),
               ('book', dict(x=36, y=132, w=26, h=4, t=8, ramp='blue'))]),
    'badguy': dict(  # 悪玉: 月夜の路地で、頬かむりの悪党が匕首を構える
        light=dict(pool=(112, 90), radius=(140, 100), fall=1.2, halo=(40, 28, 36, 0.6)),
        env=_night(moon=(40, 28, 10, 0.5), hz=128, ground='stone', gain=0.55, sky_ramp='purple', stars=14),
        items=[('house', dict(x=0, base=126, w=46, h=34, roof_h=22, roof='wood', gain=0.55, windows=[(14, 10, 7, 8, False)])),
               ('house', dict(x=168, base=128, w=56, h=38, roof_h=24, roof='wood', gain=0.55, windows=[(10, 10, 8, 9, True)])),
               ('figure', dict(x=114, foot=156, h=110, facing=-1, arms=('forward', 'hip'), legs='stride', lean=0.12, tunic='purple', head='hood', head_ramp='cloth', mask='cloth',
                               legs_ramp='cloth', props=[(1, ('dagger', dict(deg=-20)), True)]))]),
    # ================= プロジェクト 19 =================
    'j_cathedral': dict(  # 大伽藍: 夜明けの空の下、反りの大屋根の本堂と五重塔
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=130, ground='sand', hills=((106, 10, 0.5, 0.6, 2),)),
        items=[('pagoda', dict(x=200, base=128, levels=5, w=44)), ('temple_hall', dict(x=100, base=140, w=150, h=40)),
               ('paper_lantern', dict(x=30, y=120, r=6, ramp='fire', string=None))]),
    'j_citygate': dict(  # 町門: 灯の下がる大門と、その奥の町の屋根
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 60, 40, 0.5)),
        env=_night(moon=(36, 24, 9), hz=136, ground='stone', gain=0.6),
        items=[('skyline', dict(x0=0, x1=224, base=100, gain=0.5, seed=4)), ('great_gate', dict(x=112, base=140, w=170, h=124))]),
    'j_pageant': dict(  # 山車: 提灯の連なる祭りの夜、朱の幕の山車
        light=dict(pool=(112, 92), radius=(160, 105), fall=1.05, halo=(40, 40, 40, 0.5)),
        env=_night(moon=None, hz=136, ground='stone', gain=0.6),
        items=[('lantern_string', dict(y0=14, y1=30, colors=('red', 'gold', 'red', 'gold', 'red', 'gold', 'red'))), ('dashi', dict(x=112, base=152, s=1.0))]),
    'j_sewers': dict(  # 下水: 煉瓦の暗渠を流れる水、歩み板の鼠
        light=dict(pool=(112, 110), radius=(140, 100), fall=1.2, halo=(40, 50, 30, 0.5)),
        env=('room', dict(wall='stone', hz=160, floor='flag', bw=14, bh=8)),
        items=[('sewer_tunnel', dict(x=112, top=6, base=150, w=190)), ('wall_torch', dict(x=36, y=52)), ('rat', dict(x=176, base=150))]),
    'j_starchart': dict(  # 星の地図: 卓に広げた天図と、両脚器
        light=dict(pool=(112, 104), radius=(160, 100), fall=1.1, halo=(28, 36, 40, 0.6)),
        env=('room', dict(wall='stone', hz=60, floor='table')),
        items=[('candle', dict(x=28, base=58, h=10, r=3)), ('star_map', dict(x=112, y=108, rx=80, ry=36)), ('dividers', dict(x=176, y=124, ln=36))]),
    'j_exploration': dict(  # 見聞: 夜明けの分かれ道の道しるべと、旅の荷
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=112, hills=((96, 14, 0.5, 0.6, 5), (106, 10, 0.6, 0.4, 2))),
        items=[('sun', dict(x=60, y=96, r=12)), ('road', dict(x=140, top=112, base=160, w0=8, w1=130, ramp='sand')),
               ('signpost', dict(x=190, base=136)),
               ('figure', dict(x=100, foot=156, h=112, arms=('hip', 'lift'), legs='stride', tunic='green', cloak='leather', head='hat', head_ramp='leather', legs_ramp='cloth', face=True,
                               props=[(1, ('staff', dict(deg=-95, length=3.0, below=2.6)), True), (0, ('bindle', {}), True)]))]),
    'j_marketday': dict(  # 市日: 朝の広場に並ぶ日よけの屋台
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=118, ground='stone', gain=0.7, hills=()),
        items=[('skyline', dict(x0=0, x1=224, base=92, gain=0.55, seed=7, lit=False)),
               ('stall', dict(x0=22, x1=118, top=54, base=144, colors=('red', 'paper'))), ('stall', dict(x0=126, x1=212, top=60, base=144, colors=('blue', 'paper'))),
               ('basket', dict(x=56, base=120, w=26, h=10, kind='apple', fill='red', n=7)), ('basket', dict(x=90, base=120, w=24, h=10, kind='bread', n=4)),
               ('basket', dict(x=150, base=122, w=26, h=10, kind='fish', n=4)), ('basket', dict(x=184, base=122, w=26, h=10, kind='cabbage', n=4))]),
    'j_silos': dict(  # 穀物倉: 白壁の土蔵と、積み上げた米俵
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='sand', gain=0.7),
        items=[('kura', dict(x=88, base=128, w=100, h=62)), ('rice_bales', dict(x=176, base=154, rows=(3, 2, 1), r=13))]),
    'j_plot': dict(  # 陰の企て: 蝋燭ひとつの卓に、短刀を突き立てた地図と仮面
        light=dict(pool=(112, 106), radius=(130, 90), fall=1.3, halo=(40, 60, 40, 0.6)),
        env=('room', dict(wall='stone', hz=78, floor='table', floor_ramp='purple', floor_gain=0.6)),
        items=[('candle', dict(x=40, base=96, h=10, r=3)), ('sea_chart', dict(x=118, y=122, w=150, h=56)),
               ('dagger_stuck', dict(x=132, base=124, s=1.3)),
               ('mask', dict(x=58, y=142, ramp='paper')), ('coin', dict(cx=190, cy=148, r=7, metal='gold'))]),
    'j_academy': dict(  # 学問所: 黒板と地球儀、書見台のある学び舎
        light=dict(pool=(112, 96), radius=(160, 105), **WARM, halo=(20, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('window', dict(x=12, y=12, w=30, h=40, lit=True)), ('slate', dict(x=118, y=56, w=100, h=60)),
               ('globe', dict(x=186, base=138, r=16)), ('lectern', dict(x=60, base=154, h=30)), ('open_book', dict(x=60, y=114, w=18, h=9)),
               ('books_row', dict(x0=150, x1=222, base=156, hmin=8, hmax=14, seed=5))]),
    'j_fleet': dict(  # 船団: 夜明けの海を進む、帆を張った大小の船
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=('coast', dict(hz=96, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 80, 8),))),
        items=[('ship', dict(x=176, wl=104, s=0.5, gain=0.7, dep=0.4)), ('ship', dict(x=40, wl=110, s=0.6, gain=0.8, dep=0.25, sails='red')),
               ('ship', dict(x=112, wl=148, s=1.1, flag='blue'))]),
    'j_guildhall': dict(  # 組合の館: 看板と旗の下がる、灯のともる石の館
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 70, 40, 0.5)),
        env=_night(moon=None, hz=136, ground='stone', gain=0.6),
        items=[('lamp_post', dict(x=30, base=146, h=80)),
               ('house', dict(x=56, base=140, w=124, h=60, roof_h=34, wall='stone', roof='blue', timber=False,
                              windows=[(10, 10, 12, 14, True), (36, 10, 12, 14, True), (76, 10, 12, 14, True), (102, 10, 12, 14, True), (10, 36, 12, 14, True), (102, 36, 12, 14, True)],
                              door=(52, 20, 26))),
               ('hang_banner', dict(x=88, top=82, w=14, h=26, ramp='red', kind='circle')), ('hang_banner', dict(x=136, top=82, w=14, h=26, ramp='green', kind='cross')),
               ('sign', dict(x=188, y=96, w=30, h=16, emblem='coin'))]),
    'j_piazza': dict(  # 芝居小屋: 提灯の下、縞の定式幕を引いた舞台
        light=dict(pool=(112, 100), radius=(160, 105), **WARM, halo=(112, 40, 60, 0.4)),
        env=('room', dict(wall='plank', hz=150, floor='planks')),
        items=[('kabuki_stage', dict(x0=10, x1=214, top=30, base=140))]),
    'j_roads': dict(  # 街道網: 夜明けの野を走る十字の道と、一里塚の松
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=_dawn(hz=100, hills=((88, 10, 0.5, 0.6, 1),)),
        items=[('road', dict(x=60, top=100, base=160, w0=6, w1=110, ramp='sand')), ('road', dict(x=170, top=100, base=160, w0=6, w1=110, ramp='sand')),
               ('road_cross', dict(y=124, ramp='sand')), ('tree', dict(x=20, base=124, h=56, kind='pine', gain=0.85, seed=21)),
               ('tree', dict(x=206, base=118, h=48, kind='pine', gain=0.75, seed=22)), ('wagon', dict(x=118, base=150, w=74, cover='paper')),
               ('house', dict(x=94, base=100, w=22, h=10, roof_h=9, roof='red', gain=0.6, windows=[(8, 3, 4, 4, True)]))]),
    'j_barracks': dict(  # 兵営: 篝火の野営に並ぶ陣幕と、武具の架
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(40, 90, 40, 0.6)),
        env=_night(moon=None, hz=124, ground='stone', gain=0.6),
        items=[('army_tent', dict(x=160, base=126, w=96, h=60)), ('army_tent', dict(x=60, base=118, w=70, h=44, ramp='paper', stripe='blue')),
               ('weapon_rack', dict(x0=84, x1=180, top=106, base=152)), ('campfire', dict(x=40, base=150, s=1.0))]),
    'j_croprotation': dict(  # 畑まわし: 夜明けに見下ろす、作物ごとに塗り分けた畑の帯
        light=dict(pool=(112, 110), radius=(180, 110), **DAWN),
        env=_dawn(hz=84, hills=((76, 10, 0.5, 0.6, 3),)),
        items=[('strip_fields', dict(y0=86)), ('windmill', dict(x=184, base=92, h=56)), ('wheat_sheaves', dict(x=40, base=156, n=3))]),
    'j_innovation': dict(  # 新機軸: 図面の上で光る、新しいからくりの歯車
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 80, 50, 0.5)),
        env=('room', dict(wall='plank', hz=86, floor='table')),
        items=[('blueprint', dict(x=112, y=124, w=170, h=54)), ('light_rays', dict(x=112, y=70, n=11, ln=70)), ('gears', dict(x=112, y=70)),
               ('dividers', dict(x=40, y=132, ln=30)), ('candle', dict(x=196, base=84, h=10, r=3))]),
    'j_canal': dict(  # 掘割: 夕暮れの町を流れる堀、石の橋と舟
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('night', dict(hz=100, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.6)),
        items=[('house', dict(x=0, base=104, w=56, h=40, roof_h=24, roof='red', gain=0.75, windows=[(10, 10, 8, 9, True), (34, 10, 8, 9, True)])),
               ('house', dict(x=168, base=104, w=56, h=42, roof_h=26, roof='wood', gain=0.75, windows=[(10, 10, 8, 9, True), (34, 10, 8, 9, True)])),
               ('water', dict(y0=110)), ('arch_bridge', dict(x=112, top=76, w=200, span=90)), ('boat', dict(x=90, wl=146, w=70))]),
    'j_citadel': dict(  # 山城: 夜明けの峰の上にそびえる天守
        light=dict(pool=(112, 80), radius=(180, 110), **DAWN),
        env=_dawn(hz=150, ground='foliage', hills=((128, 20, 0.5, 0.6, 4),)),
        items=[('hills', dict(base=130, amp=8, gain=0.75, depth=0.1, seed=11)), ('tenshu', dict(x=112, base=128, s=1.05)),
               ('tree', dict(x=20, base=150, h=60, kind='pine', gain=0.7, seed=24)), ('tree', dict(x=206, base=154, h=66, kind='pine', gain=0.7, seed=25))]),
}
