"""動物園（cards-menagerie.js）の 70 枚の場面データ。書き方は scenes.py の冒頭を見る。
王国 31（駒を含む）・イベント 20・ならい 19。動物の札なので、ならいは 1 匹ずつその住みかで大きく描き、
王国は馬と牧場の札が多いので、雪・夜明け・厩の灯・川で場所を散らす。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


def _night(hz=124, moon=(36, 24, 10), ground='foliage', gain=0.6, **kw):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=ground, ground_gain=gain, **kw))


def _snow(hz=124, moon=None):
    return ('night', dict(hz=hz, moon=moon, ground_ramp=None, stars=20, hills=[(hz - 14, 12, 0.45, 0.6, 5)]))


STABLE = ('room', dict(wall='plank', hz=124, floor='planks'))

SCENES = {
    # ================= 王国 31 =================
    'pony': dict(  # 駒: 夜明けの柵の中の、たてがみの長い小さな馬
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=124),
        items=[('fence', dict(x0=0, x1=224, base=132, h=16)), ('horse', dict(x=112, base=150, s=1.15, ramp='paper')),
               ('flower', dict(x=30, y=150, r=4, ramp='gold')), ('flower', dict(x=196, y=152, r=4, ramp='red'))]),
    'nightcat': dict(  # 夜の猫: 満月の屋根の上に座る、金の目の黒猫
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(60, 46, 50, 0.7)),
        env=_night(moon=(60, 46, 24), ground=None, stars=36),
        items=[('roof_ridge', dict(y=120, ramp='cloth')), 
               ('cat', dict(x=112, base=124, s=2.0, facing=-1))]),
    'sled': dict(  # 馬そり: 雪の野を、荷を積んだそりを曳く馬
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.05, halo=(30, 30, 40, 0.5)),
        env=_snow(hz=124),
        items=[('snow_ground', dict(y0=124)), ('tree', dict(x=200, base=128, h=70, kind='pine', gain=0.7, seed=31)),
               ('sled', dict(x=150, base=150, w=96)), ('harness_lines', dict(x0=96, y0=118, x1=104, y1=134)),
               ('horse', dict(x=64, base=150, s=1.05, blanket='red')), ('snow', dict(n=80, seed=3))]),
    'provisions': dict(  # 糧秣: 厩の隅の干し草と麦の袋、燕麦の桶
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(26, 44, 40, 0.6)),
        env=STABLE,
        items=[('lantern', dict(x=26, y=40, hang=0)), ('pitch_lean', dict(x=200, base=150)), ('wheat_sheaves', dict(x=150, base=146, n=3)),
               ('grain_sacks', dict(x=66, base=152)), ('bucket', dict(x=118, base=158, r=15))]),
    'caravan2': dict(  # 駱駝の隊: 夜明けの砂丘を行く、荷を積んだ駱駝の列
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=118, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('sun', dict(x=50, y=104, r=14)), ('dunes', dict(y0=112)),
               ('camel', dict(x=190, base=122, s=0.6, facing=-1, load='blue')), ('camel', dict(x=150, base=132, s=0.8, facing=-1, load='green')),
               ('camel', dict(x=86, base=152, s=1.25, facing=-1, load='red'))]),
    'goatkeeper': dict(  # 山羊番: 岩の斜面で、杖をついて山羊を見守る
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='stone', hills=((96, 30, 0.5, 0.6, 7),)),
        items=[('rocks', dict(pts=[(190, 150, 70, 30)])),
               ('figure', dict(x=78, foot=154, h=110, arms=('down', 'lift'), tunic='green', cloak='leather', head='hood', head_ramp='leather', legs_ramp='cloth', face=True,
                               props=[(1, ('crook_staff', {}), True)])),
               ('goat', dict(x=162, base=154, s=1.8, facing=-1)), ('goat', dict(x=204, base=122, s=0.9, facing=-1, ramp='leather'))]),
    'scrapiron': dict(  # くず鉄: 鍛冶場の裏に積まれた、錆びた車輪と鍋と鎖
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=110, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=28, y=44, hang=0)), ('scrap_pile', dict(x=118, base=152, w=170))]),
    'herddog': dict(  # 牧犬: 夜明けの丘で、羊の群れを追う牧羊犬
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=_dawn(hz=112),
        items=[('sheep', dict(x=150, base=124, s=1.1)), ('sheep', dict(x=192, base=132, s=1.3)), ('sheep', dict(x=164, base=150, s=1.6)),
               ('dog_stand', dict(x=72, base=152, s=1.6, run=True, ramp='cloth'))]),
    'snowvillage': dict(  # 雪の里: 雪の降る夜、灯のともる雪屋根の家々
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(60, 100, 40, 0.5)),
        env=_snow(hz=120),
        items=[('snow_ground', dict(y0=120)),
               ('house', dict(x=14, base=128, w=48, h=28, roof_h=22, roof='wood', gain=0.7, windows=[(10, 9, 8, 8, True), (30, 9, 8, 8, True)])),
               ('snow_roof', dict(x=14, base=128, w=48, h=28, roof_h=22)),
               ('house', dict(x=150, base=126, w=56, h=30, roof_h=24, roof='red', gain=0.7, windows=[(10, 9, 8, 9, True)], door=(32, 10, 16))),
               ('snow_roof', dict(x=150, base=126, w=56, h=30, roof_h=24)),
               ('house', dict(x=68, base=146, w=64, h=36, roof_h=28, roof='wood', chimney=0.5, windows=[(10, 10, 9, 10, True), (44, 10, 9, 10, True)], door=(27, 11, 20))),
               ('snow_roof', dict(x=68, base=146, w=64, h=36, roof_h=28)),
               ('snow', dict(n=90, seed=5))]),
    'hoardpile': dict(  # 蓄え: 床板をはがした穴の甕から、あふれる金貨
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6), key=0.8),
        env=('room', dict(wall='plank', hz=96, floor='planks')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('dug_hole', dict(x=112, y=146)), ('coin_jar', dict(x=112, base=150, s=1.1)),
               ('plank', dict(x0=164, y0=148, x1=212, y1=136, w=4))]),
    'bountyman': dict(  # 懸賞稼ぎ: 手配書の貼られた壁の前で、縄と剣を持つ男
        light=dict(pool=(104, 92), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('wanted_poster', dict(x=172, y=24, w=46, h=60)), ('wanted_poster', dict(x=60, y=30, w=34, h=44)),
               ('figure', dict(x=110, foot=154, h=112, arms=('hip', 'present'), tunic='leather', cloak='cloth', head='hat', head_ramp='cloth', legs_ramp='cloth', face=True, belt='leather',
                               props=[(1, ('coil_held', {}), True)], behind=[(0, ('sword', dict(deg=120, length=3.0)))]))]),
    'archbishop': dict(  # 大僧正: 色ガラスの窓の下、僧冠をかぶり牧杖を持つ
        light=dict(pool=(108, 88), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('window_arch', dict(x=24, y=8, w=36, h=70)), ('candle_row', dict(x0=150, x1=214, base=120)),
               ('figure', dict(x=112, foot=154, h=114, arms=('present', 'lift'), robe=True, tunic='paper', trim='gold', mantle='red', head='mitre', head_ramp='paper', face=True,
                               props=[(1, ('crook_staff', {}), True)]))]),
    'horsemen': dict(  # 騎馬隊: 夜明けの野を駆ける、槍旗を掲げた騎兵
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=124, hills=((106, 14, 0.5, 0.6, 2),)),
        items=[('rider', dict(x=176, base=126, s=0.6, gallop=True, horse_ramp='cloth', fig_h=40, tunic='blue', head='helm', armor=True)),
               ('rider', dict(x=104, base=152, s=1.2, gallop=True, blanket='red', fig_h=76, tunic='red', head='helm', armor=True, cloak='blue',
                              props=[(1, ('banner', dict(ramp='blue', deg=-110, length=3.6, flag=(1.6, 1.2))), False)]))]),
    'stablehand': dict(  # 馬番: 厩で、刷毛で馬の毛を梳く
        light=dict(pool=(112, 100), radius=(150, 100), **WARM, halo=(24, 40, 40, 0.6)),
        env=STABLE,
        items=[('lantern', dict(x=24, y=40, hang=0)), ('haystack', dict(x=200, base=150, r=26)),
               ('horse', dict(x=136, base=152, s=1.25, ramp='leather')),
               ('figure', dict(x=58, foot=154, h=106, arms=('down', 'forward'), tunic='cloth', apron='leather', head='cap', head_ramp='green', legs_ramp='cloth', face=True,
                               props=[(1, ('brush', {}), True)]))]),
    'hostel': dict(  # 馬宿: 夜道に看板の下がる、厩つきの宿
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05, halo=(40, 70, 40, 0.5)),
        env=_night(moon=(30, 22, 8, 0.4), hz=134, ground='stone', gain=0.6),
        items=[('house', dict(x=30, base=136, w=100, h=50, roof_h=30, roof='red', chimney=0.3,
                              windows=[(10, 10, 12, 12, True), (64, 10, 12, 12, True), (10, 30, 12, 12, True)], door=(40, 16, 24))),
               ('stall_door', dict(x0=136, x1=210, top=92, base=136)), ('horse_head', dict(x=164, y=80, s=1.0)),
               ('sign', dict(x=118, y=74, w=26, h=16, emblem='coin')), ('lamp_post', dict(x=18, base=150, h=70))]),
    'commons': dict(  # 村の広っぱ: 夜明けの共有地に立つ大樫と、草をはむ羊
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=120),
        items=[('house', dict(x=6, base=114, w=30, h=16, roof_h=14, roof='red', gain=0.6, windows=[(10, 4, 5, 5, True)])),
               ('tree', dict(x=112, base=136, h=118, kind='oak', gain=1.0, seed=33)),
               ('sheep', dict(x=50, base=146, s=0.9)), ('sheep', dict(x=180, base=150, s=1.0, facing=-1)), ('fence', dict(x0=150, x1=224, base=128, h=12))]),
    'riverboat': dict(  # 川舟: 夜明けの川を、帆を上げてさかのぼる舟
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=100, moon=None, sky_ramp='dawn', stars=0, ground_ramp='foliage', ground_gain=0.6, hills=[(92, 12, 0.5, 0.6, 4)])),
        items=[('river', dict(y0=100)), ('ship', dict(x=118, wl=140, s=0.75, masts=1, sails='paper', flag='red')),
               ('reeds', dict(xs=(14, 30, 200, 214), base=152)), ('tree', dict(x=200, base=116, h=50, kind='oak', gain=0.7, seed=35))]),
    'witchmeet': dict(  # 魔女の寄り合い: 月の下、大鍋を囲む三角帽の魔女たち
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(112, 116, 50, 0.6)),
        env=_night(moon=(40, 26, 12), ground='stone', gain=0.5, sky_ramp='purple'),
        items=[('figure', dict(x=48, foot=146, h=96, arms=('forward', 'down'), robe=True, tunic='purple', head='witch', head_ramp='cloth', face=True)),
               ('figure', dict(x=176, foot=146, h=96, facing=-1, arms=('forward', 'lift'), robe=True, tunic='green', head='witch', head_ramp='cloth', face=True)),
               ('cauldron', dict(x=112, base=154, r=34, brew='green')), ('smoke', dict(pts=[(112, 104), (106, 84), (114, 64)])),
               ('bats', dict(pts=[(150, 40, 1.0), (176, 26, 0.8)]))]),
    'evict': dict(  # 追い立て: 戸口から指さして追い出す家主と、放り出された荷
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(40, 60, 40, 0.6)),
        env=_night(moon=None, hz=132, ground='stone', gain=0.6),
        items=[('house', dict(x=0, base=136, w=110, h=64, roof_h=30, roof='wood', windows=[(14, 12, 12, 12, True)], door=(60, 22, 36))),
               ('figure', dict(x=88, foot=136, h=100, arms=('hip', 'aim'), tunic='red', head='hat', head_ramp='cloth', legs_ramp='cloth', face=True, beard='hair')),
               ('sack', dict(x=150, base=152, r=13, ramp='red')), ('pots', dict(x=190, base=154, n=2)), ('chair', dict(x=210, base=140, gain=0.7))]),
    'falconer': dict(  # 鷹使い: 夜明けの野で、手甲に鷹をとまらせる
        light=dict(pool=(108, 88), radius=(170, 110), **DAWN),
        env=_dawn(hz=128, hills=((110, 16, 0.5, 0.5, 8),)),
        items=[('figure', dict(x=96, foot=156, h=112, arms=('belly', 'lift'), tunic='green', cloak='red', head='feather', head_ramp='green', legs_ramp='leather', face=True,
                               props=[(1, ('glove_falcon', {}), True)]))]),
    'angler': dict(  # 釣り人: 川岸の岩に立ち、竿を垂れる
        light=dict(pool=(108, 100), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=100, shore=None, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 70, 8),))),
        items=[('hills', dict(base=100, amp=10, gain=0.5, depth=0.5, seed=8)), ('rocks', dict(pts=[(60, 160, 120, 34)])),
               ('figure', dict(x=60, foot=140, h=100, arms=('forward', 'down'), tunic='blue', head='hat', head_ramp='leather', legs_ramp='cloth', face=True,
                               props=[(0, ('fishing_rod', dict(deg=-35, length=6.0)), True)])),
               ('basket', dict(x=100, base=146, w=22, h=10, kind='fish', n=3))]),
    'warder': dict(  # 門衛: 落とし格子の城門で、斧槍を構える番人
        light=dict(pool=(108, 90), radius=(150, 100), fall=1.15, halo=(20, 44, 40, 0.7)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=20, bh=10)),
        items=[('wall_torch', dict(x=18, y=44)), ('gate_bars', dict(x0=120, x1=210, top=24, base=126)),
               ('figure', dict(x=94, foot=154, h=114, arms=('belly', 'lift'), tunic='blue', armor=True, head='helm', cloak='red', legs_ramp='cloth', face=True,
                               props=[(1, ('halberd', {}), True)]))]),
    'huntlodge': dict(  # 狩り小屋: 夜の森の、鹿の角を掲げた丸太小屋
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(70, 110, 40, 0.5)),
        env=('forest', dict(hz=126, moon=None, seed=37)),
        items=[('log_cabin', dict(x=112, base=140, w=124, h=52)), ('logs', dict(x=176, base=154, n=3, r=6)), ('campfire', dict(x=38, base=154, s=0.8))]),
    'kiln': dict(  # 窯: 夜の斜面の登り窯、焚き口の火と焼き上がりの壺
        light=dict(pool=(100, 110), radius=(150, 100), fall=1.1, halo=(40, 120, 50, 0.8)),
        env=_night(moon=None, hz=128, ground='leather', gain=0.55),
        items=[('kiln', dict(x=112, base=136, w=170, h=70)), ('pots', dict(x=150, base=156, n=3)), ('logs', dict(x=10, base=158, n=3, r=5))]),
    'livery': dict(  # 馬貸し: 仕切り戸から顔を出す、何頭もの馬
        light=dict(pool=(112, 96), radius=(150, 100), **WARM, halo=(20, 30, 40, 0.5)),
        env=STABLE,
        items=[('lantern', dict(x=112, y=22, hang=0)),
               ('stall_door', dict(x0=0, x1=72, top=86, base=150)), ('stall_door', dict(x0=76, x1=148, top=86, base=150)), ('stall_door', dict(x0=152, x1=224, top=86, base=150)),
               ('horse_head', dict(x=30, y=56, s=1.0, ramp='paper')), ('horse_head', dict(x=106, y=50, s=1.15)), ('horse_head', dict(x=184, y=56, s=1.0, ramp='cloth'))]),
    'ringleader': dict(  # 元締め: 賭場の奥で、扇を手に骰子を見下ろす親分
        light=dict(pool=(108, 100), radius=(140, 100), fall=1.2, halo=(26, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=112, floor='planks')),
        items=[('candle', dict(x=26, base=58, h=12, r=3)), ('shelf', dict(x0=8, x1=44, y=58)),
               ('figure', dict(x=112, foot=158, h=114, arms=('lift', 'chest'), robe=True, tunic='purple', mantle='red', head='topknot', face=True,
                               props=[(0, ('fan', dict(ramp='gold')), True)])),
               ('table', dict(x0=24, x1=200, top=128, legs_to=160, front=True, cloth='red')), ('dice', dict(x=88, y=132, s=12, pips=6)), ('dice', dict(x=118, y=136, s=12, pips=3, rot=0.4)),
               ('stack', dict(cx=168, base=136, r=9, n=5, metal='gold', seed=21))]),
    'corral': dict(  # 放し飼い場: 夜明けの柵囲いに、放した馬たち
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=_dawn(hz=112),
        items=[('fence', dict(x0=0, x1=224, base=120, h=14)), ('horse', dict(x=176, base=130, s=0.7, ramp='cloth', facing=-1)),
               ('horse', dict(x=60, base=136, s=0.8, ramp='paper')), ('horse', dict(x=124, base=156, s=1.15, ramp='leather', gallop=True))]),
    'refuge': dict(  # 駆け込み寺: 灯のともる山門へ、頭巾の人が駆け込む
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(112, 70, 50, 0.5)),
        env=_night(moon=(30, 22, 8, 0.4), hz=134, ground='stone', gain=0.6),
        items=[('gatehouse_roof', dict(x=130, base=136, w=150, h=100)),
               ('figure', dict(x=78, foot=156, h=104, arms=('forward', 'down'), legs='stride', lean=0.15, tunic='red', robe=True, head='hood', head_ramp='cloth', facing=1))]),
    'warhorse': dict(  # 軍馬: 篝火の陣で、馬鎧を着けて立つ軍馬
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(30, 70, 40, 0.7)),
        env=_night(moon=None, hz=128, ground='stone', gain=0.55),
        items=[('brazier', dict(x=26, base=126)), ('army_tent', dict(x=190, base=128, w=70, h=50, stripe='red')),
               ('horse', dict(x=112, base=154, s=1.5, ramp='cloth', blanket='red'))]),
    'traveler2': dict(  # 旅の人: 夜明けの峠道を、笠をかぶって歩く旅人
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=('pass', dict(hz=124, moon=None)),
        items=[('sun', dict(x=46, y=90, r=12)),
               ('figure', dict(x=112, foot=156, h=112, arms=('hip', 'forward'), legs='stride', tunic='blue', cloak='paper', head='jingasa', head_ramp='sand', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-80, length=2.6, below=2.8)), True)]))]),
    'beastfair': dict(  # 獣の市: 夜店の灯の下、柵に入れた豚と山羊と羊
        light=dict(pool=(112, 104), radius=(170, 110), fall=1.05, halo=(40, 50, 40, 0.5)),
        env=_night(moon=None, hz=118, ground='leather', gain=0.6),
        items=[('lantern_string', dict(y0=16, y1=30, colors=('red', 'gold', 'blue', 'gold', 'red'))), ('tent', dict(x=180, base=118, w=60, h=56)),
               ('goat', dict(x=60, base=134, s=0.9, facing=-1)), ('sheep', dict(x=120, base=130, s=0.9)),
               ('pig', dict(x=110, base=156, s=1.2, facing=-1)), ('fence', dict(x0=0, x1=224, base=160, h=14))]),
    # ================= イベント 20 =================
    'm_delay': dict(  # 先延ばし: 卓の砂時計と、積んだままの手紙
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=92, floor='table')),
        items=[('candle', dict(x=28, base=90, h=12, r=3)), ('hourglass', dict(x=112, base=150, h=80)),
               ('letter_fly', dict(x=176, y=130)), ('book', dict(x=40, y=140, w=30, h=5, t=10, ramp='green'))]),
    'm_despair': dict(  # やけっぱち: 紫の夜、空の財布を前に天を仰いで叫ぶ
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1),
        env=('night', dict(hz=124, moon=None, sky_ramp='purple', stars=20, ground_ramp='stone', ground_gain=0.5, clouds=())),
        items=[('rain_cloud', dict(x=112, y=24, w=110)),
               ('figure', dict(x=112, foot=154, h=104, arms=('raise', 'raise'), legs='kneel', tunic='cloth', head='hair', legs_ramp='cloth', face=True)),
               ('empty_purse', dict(x=176, base=154))]),
    'm_gamble': dict(  # 一か八か: 卓に転がる大きな骰子と、賭けた金貨
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=86, floor='table', floor_ramp='green', floor_gain=0.7)),
        items=[('candle', dict(x=28, base=84, h=12, r=3)), ('dice', dict(x=90, y=118, s=34, pips=6, rot=0.2)), ('dice', dict(x=152, y=128, s=28, pips=1, rot=-0.3)),
               ('pile', dict(cx=56, base=154, w=50, h=16, metal='gold', r=7, count=14, seed=23)), ('coin', dict(cx=196, cy=148, r=9, metal='silver', stamp='tower'))]),
    'm_pursue': dict(  # 追っかけ: 雪の森に残る足跡を、猟犬が追う
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1),
        env=('forest', dict(hz=118, moon=(36, 24, 9), seed=39)),
        items=[('snow_ground', dict(y0=120)), ('tracks', dict(pts=[(200, 124), (180, 130), (160, 134), (140, 140), (120, 146)])),
               ('dog_stand', dict(x=92, base=152, s=1.6, run=True, ramp='leather'))]),
    'm_ride': dict(  # 騎乗: 夜明けの道を、馬で駆けていく
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=128, hills=((110, 12, 0.5, 0.6, 6),)),
        items=[('road', dict(x=112, top=128, base=160, w0=30, w1=200, ramp='sand')),
               ('rider', dict(x=112, base=154, s=1.3, gallop=True, horse_ramp='paper', blanket='blue', fig_h=80, tunic='green', cloak='red', head='feather', head_ramp='green'))]),
    'm_toil': dict(  # 骨折り: 夕暮れの坂で、重い袋を背負って登る
        light=dict(pool=(112, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=130, ground='stone', hills=((104, 20, 0.5, 0.6, 2),)),
        items=[('figure', dict(x=110, foot=154, h=104, arms=('chest', 'down'), legs='stride', lean=0.3, tunic='leather', head='cap', head_ramp='cloth', legs_ramp='cloth',
                               behind=[(0, ('sack_back', {}))])),
               ('rocks', dict(pts=[(30, 160, 60, 20), (200, 160, 50, 16)]))]),
    'm_enhance': dict(  # 磨き: 布の上の大きな原石が、磨かれて光る
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 90, 50, 0.5)),
        env=('icon', dict(hz=96, wall='stone', cloth='blue', cloth_gain=0.7)),
        items=[('light_rays', dict(x=112, y=96, n=11, ln=70)), ('big_gem', dict(x=112, y=104, r=38, ramp='red')), ('sparks', dict(pts=[(70, 80), (150, 70), (160, 120), (66, 126)]))]),
    'm_march': dict(  # 行軍: 夜明けの街道を、槍を担いで進む兵の列
        light=dict(pool=(112, 104), radius=(180, 110), **DAWN),
        env=_dawn(hz=116),
        items=[('nobori', dict(x=176, top=40, base=126, w=16, ramp='red')),
               ('figure', dict(x=190, foot=124, h=60, facing=-1, arms=('down', 'lift'), legs='stride', tunic='red', head='helm', legs_ramp='cloth',
                               behind=[(1, ('staff', dict(deg=-100, length=4.0, top='spear', below=1.0)))])),
               ('figure', dict(x=150, foot=136, h=80, facing=-1, arms=('down', 'lift'), legs='stride', tunic='red', head='helm', legs_ramp='cloth',
                               behind=[(1, ('staff', dict(deg=-100, length=4.2, top='spear', below=1.0)))])),
               ('figure', dict(x=90, foot=156, h=110, facing=-1, arms=('down', 'lift'), legs='stride', tunic='red', armor=True, head='helm', legs_ramp='cloth',
                               behind=[(1, ('staff', dict(deg=-100, length=4.4, top='spear', below=1.0)))]))]),
    'm_transport': dict(  # 運搬: 騾馬が荷馬車を曳いて坂を行く
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='stone'),
        items=[('wagon', dict(x=150, base=150, w=84, cover='paper')), ('mule', dict(x=64, base=152, s=1.0, packs=False))]),
    'm_banish': dict(  # 島流し: 夜の海、小舟が向かう遠い孤島
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=92, moon=(40, 26, 10, 0.4))),
        items=[('island', dict(x=170, wl=96, w=90, h=22)), ('palm', dict(x=172, base=84, h=34)),
               ('boat', dict(x=96, wl=138, w=80)),
               ('figure', dict(x=96, foot=130, h=56, facing=1, arms=('chest', 'chest'), tunic='cloth', head='hood', head_ramp='cloth'))]),
    'm_bargain': dict(  # 掘り出し物: がらくたの山の奥に、光る宝箱
        light=dict(pool=(120, 110), radius=(150, 100), fall=1.15, halo=(130, 120, 50, 0.6)),
        env=('room', dict(wall='plank', hz=108, floor='planks')),
        items=[('lantern', dict(x=26, y=40, hang=0)), ('clutter', dict(x=56, base=150)), ('treasure_chest_glow', dict(x=140, base=152)),
               ('cobweb', dict(x=0, y=0, r=22))]),
    'm_invest': dict(  # 肩入れ: 鉢に植えた若木に、金貨の実がなる
        light=dict(pool=(112, 96), radius=(160, 105), **WARM, halo=(30, 30, 40, 0.5)),
        env=('room', dict(wall='stone', hz=118, floor='table')),
        items=[('window', dict(x=12, y=12, w=30, h=40, lit=True)), ('fruit_tree', dict(x=112, base=136, h=96, fruit='gold')),
               ('pots', dict(x=112, base=152, n=1)), ('stack', dict(cx=170, base=152, r=10, n=6, metal='gold', seed=27))]),
    'm_seize': dict(  # この日をつかめ: 丘の上で、昇る朝日へ腕を突き上げる
        light=dict(pool=(112, 100), radius=(180, 120), **DAWN),
        env=_dawn(hz=124, hills=((118, 12, 0.6, 0.4, 4),)),
        items=[('sun', dict(x=112, y=116, r=36)), ('light_rays', dict(x=112, y=116, n=13, ln=110)),
               ('figure', dict(x=112, foot=158, h=112, arms=('down', 'raise'), tunic='red', cloak='blue', head='hair', legs_ramp='cloth'))]),
    'm_trade': dict(  # 商い: 帳場の天秤に、香辛料の袋と金貨を量る
        light=dict(pool=(112, 104), radius=(150, 100), **WARM, halo=(28, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('spice_sacks', dict(x=190, base=104)),
               ('balance', dict(x=112, base=150, h=64, tilt=-5, left='gold', right='copper', s=1.4)),
               ('cloth_bolts', dict(x=36, base=156))]),
    'm_demand': dict(  # 強請り: 店先で棍棒を肩に、手を突き出す男
        light=dict(pool=(108, 92), radius=(150, 100), fall=1.15, halo=(30, 44, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)), ('shelf', dict(x0=150, x1=220, y=50)), ('pots', dict(x=180, base=50, n=3)),
               ('figure', dict(x=108, foot=154, h=114, facing=-1, arms=('lift', 'present'), tunic='cloth', head='hood', head_ramp='cloth', mask='red', legs_ramp='cloth', belt='leather',
                               props=[(0, ('club', {}), True)]))]),
    'm_stampede': dict(  # 暴れ馬: 土煙を上げて駆け出す馬の群れ
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=118, ground='leather', gain=0.65),
        items=[('horse', dict(x=176, base=128, s=0.7, gallop=True, ramp='cloth')), ('horse', dict(x=40, base=134, s=0.8, gallop=True, ramp='paper')),
               ('smoke', dict(pts=[(150, 140), (190, 146), (90, 150), (210, 130)])),
               ('horse', dict(x=112, base=156, s=1.25, gallop=True, ramp='leather'))]),
    'm_reap': dict(  # 刈り取り: 夕暮れの麦畑で、大鎌を振るう
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=104, ground='leather'),
        items=[('wheat_field', dict(y0=108)), ('wheat_sheaves', dict(x=180, base=156, n=2)),
               ('figure', dict(x=90, foot=156, h=112, arms=('low', 'chest'), legs='stride', lean=0.12, tunic='paper', apron='leather', head='hat', head_ramp='sand', legs_ramp='cloth',
                               props=[(1, ('scythe', {}), True)]))]),
    'm_enclave': dict(  # 飛び地: 夜の海に浮かぶ、城壁で囲んだ小さな島
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=104, moon=(40, 26, 10))),
        items=[('island', dict(x=118, wl=124, w=180, h=30)), ('castle', dict(x=118, base=112, s=0.7)), ('boat', dict(x=40, wl=146, w=40))]),
    'm_league': dict(  # 連合: 色とりどりの盾と旗を一つに束ねる
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.1, halo=(16, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=132, floor='flag')),
        items=[('wall_torch', dict(x=16, y=40)),
               ('hang_banner', dict(x=34, top=0, w=22, h=60, ramp='red', kind='circle')), ('hang_banner', dict(x=74, top=0, w=22, h=66, ramp='blue', kind='cross')),
               ('hang_banner', dict(x=128, top=0, w=22, h=66, ramp='green', kind='chevron')), ('hang_banner', dict(x=168, top=0, w=22, h=60, ramp='purple', kind='circle')),
               ('shield_row', dict(x0=24, x1=200, y=104, ramps=('red', 'blue', 'green', 'gold', 'purple')))]),
    'm_populate': dict(  # 人集め: 夜明けの広場に集まる、さまざまな人々
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=116, ground='stone'),
        items=[('house', dict(x=0, base=114, w=50, h=30, roof_h=20, roof='red', gain=0.6, windows=[(10, 10, 7, 8, True)])),
               ('house', dict(x=170, base=114, w=54, h=32, roof_h=22, roof='wood', gain=0.6, windows=[(10, 10, 8, 8, True)])),
               ('figure', dict(x=40, foot=140, h=80, arms=('down', 'hip'), tunic='green', head='cap', head_ramp='red', legs_ramp='cloth')),
               ('figure', dict(x=184, foot=140, h=80, facing=-1, arms=('hip', 'down'), tunic='purple', gown=True, head='long', legs_ramp='cloth')),
               ('figure', dict(x=78, foot=154, h=100, arms=('down', 'raise'), tunic='blue', head='hat', head_ramp='leather', legs_ramp='cloth')),
               ('figure', dict(x=146, foot=156, h=104, facing=-1, arms=('hip', 'down'), tunic='red', apron='paper', head='hair', legs_ramp='cloth')),
               ('figure', dict(x=112, foot=160, h=74, arms=('down', 'down'), tunic='gold', head='hair', legs_ramp='cloth', young=True))]),
    # ================= ならい 19 =================
    'w_butterfly': dict(  # 蝶のならい: 夜明けの花畑を舞う大きな蝶
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=112),
        items=[('flowers', dict(rows=[(122, 4.0, 22), (146, 7.0, 28)])), ('butterfly', dict(x=170, y=60, s=0.8, ramp='gold')),
               ('butterfly', dict(x=104, y=80, s=2.0, ramp='blue'))]),
    'w_camel': dict(  # 駱駝のならい: 夕日の砂丘に立つ駱駝
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=('night', dict(hz=118, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[('sun', dict(x=50, y=96, r=20)), ('dunes', dict(y0=112)), ('camel', dict(x=112, base=152, s=1.25, facing=-1, load='red'))]),
    'w_frog': dict(  # 蛙のならい: 月夜の池、睡蓮の葉にのる蛙
        light=dict(pool=(112, 110), radius=(160, 100), fall=1.1, halo=(40, 30, 40, 0.6)),
        env=('coast', dict(hz=86, moon=(40, 30, 11), clouds=())),
        items=[('reeds', dict(xs=(10, 24, 200, 214), base=130)), ('lily_pad', dict(x=170, y=104, r=20)),
               ('lily_pad', dict(x=112, y=136, r=56, flower=False)), ('frog', dict(x=112, base=136, s=2.0))]),
    'w_goat': dict(  # 山羊のならい: 夜明けの岩山の頂に立つ山羊
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=150, ground='stone', hills=((120, 20, 0.5, 0.6, 3),)),
        items=[('rocks', dict(pts=[(112, 168, 180, 60)])), ('goat', dict(x=112, base=124, s=2.0, facing=-1, ramp='paper'))]),
    'w_horse': dict(  # 馬のならい: 月夜の草原を駆ける馬
        light=dict(pool=(112, 100), radius=(170, 110), fall=1.05, halo=(40, 26, 40, 0.6)),
        env=_night(moon=(40, 26, 11), hz=120, gain=0.6),
        items=[('horse', dict(x=112, base=154, s=1.6, gallop=True, ramp='paper'))]),
    'w_mole': dict(  # 土竜のならい: 畑の土を盛り上げて顔を出す土竜
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=110, ground='leather'),
        items=[('furrows', dict(y0=114)), ('mole', dict(x=112, base=148, s=1.6)), ('sprout_pot', dict(x=190, base=152))]),
    'w_monkey': dict(  # 猿のならい: 森の枝に長い腕でぶら下がる猿
        light=dict(pool=(104, 90), radius=(160, 105), fall=1.1, halo=(40, 30, 40, 0.5)),
        env=('forest', dict(hz=124, moon=(36, 24, 9), seed=41)),
        items=[('trunk', dict(x=40, top=0, base=150, w=22)), ('rope', dict(x0=0, y0=18, x1=224, y1=10)),
               ('monkey2', dict(x=118, y=56, s=2.0))]),
    'w_mouse': dict(  # 鼠のならい: 蝋燭の卓で、チーズにかじりつく鼠
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.15, halo=(28, 54, 40, 0.6)),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=30, base=94, h=10, r=3)), ('cheese', dict(x=150, base=150, w=56, h=34)), ('mouse', dict(x=84, base=152, s=2.0))]),
    'w_mule': dict(  # 騾馬のならい: 峠道で荷を背負う騾馬
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('pass', dict(hz=124, moon=None)),
        items=[('mule', dict(x=112, base=154, s=1.5, ramp='leather'))]),
    'w_otter': dict(  # 川獺のならい: 夜明けの川に仰向けに浮かび、貝を抱える
        light=dict(pool=(112, 110), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=80, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 60, 8),))),
        items=[('hills', dict(base=80, amp=8, gain=0.5, depth=0.5, seed=3)), ('otter', dict(x=118, y=124, s=1.9))]),
    'w_owl': dict(  # 梟のならい: 月夜の枝にとまる梟
        light=dict(pool=(112, 90), radius=(150, 100), fall=1.1, halo=(50, 36, 50, 0.6)),
        env=('forest', dict(hz=130, moon=(50, 36, 18), seed=43)),
        items=[('trunk', dict(x=200, top=0, base=160, w=24)), ('plank', dict(x0=60, y0=138, x1=210, y1=128, w=5)),
               ('owl', dict(x=120, base=136, s=1.7))]),
    'w_ox': dict(  # 牛のならい: 夜明けの畑で、くびきを着けた牛
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=116, ground='leather'),
        items=[('furrows', dict(y0=120)), ('ox', dict(x=104, base=154, s=1.45, facing=-1, yoke=True))]),
    'w_pig': dict(  # 豚のならい: 夕暮れのぬかるみで、泥にまみれる豚
        light=dict(pool=(112, 104), radius=(170, 110), **DAWN),
        env=_dawn(hz=116, ground='leather'),
        items=[('fence', dict(x0=0, x1=224, base=124, h=14)), ('mud_pool', dict(x=112, y=148, rx=90, ry=12)), ('pig', dict(x=112, base=150, s=1.8, facing=-1))]),
    'w_rat': dict(  # 溝鼠のならい: 地下蔵で、金貨の山に乗る溝鼠
        light=dict(pool=(112, 116), radius=(150, 100), **WARM, halo=(30, 44, 40, 0.6)),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[('lantern', dict(x=30, y=44, hang=0)), ('pile', dict(cx=112, base=154, w=90, h=24, metal='gold', r=8, count=26, seed=29)),
               ('big_rat', dict(x=112, base=138, s=2.6, facing=-1))]),
    'w_seal': dict(  # 海豹のならい: 月夜の岩の上で、頭をもたげる海豹
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(40, 26, 40, 0.6)),
        env=('coast', dict(hz=92, moon=(40, 26, 11))),
        items=[('rocks', dict(pts=[(112, 168, 200, 56)], gain=0.9)), ('foam', dict(x0=0, x1=224, y=126)), ('seal', dict(x=104, base=142, s=1.4, facing=-1))]),
    'w_sheep': dict(  # 羊のならい: 夜明けの丘に立つ、もこもこの羊
        light=dict(pool=(112, 100), radius=(180, 110), **DAWN),
        env=_dawn(hz=116),
        items=[('sheep', dict(x=112, base=152, s=2.6, facing=-1)), ('flower', dict(x=30, y=150, r=4, ramp='gold')), ('flower', dict(x=196, y=152, r=4, ramp='blue'))]),
    'w_squirrel': dict(  # 栗鼠のならい: 秋の森の切り株で、団栗を抱える栗鼠
        light=dict(pool=(112, 96), radius=(160, 105), fall=1.05, halo=(40, 30, 40, 0.4)),
        env=('forest', dict(hz=124, moon=None, seed=45)),
        items=[('leaves', dict(n=24)), ('stump', dict(x=112, base=156, r=34, h=14)), ('squirrel', dict(x=112, base=142, s=1.6, facing=-1)),
               ('acorns', dict(pts=[(60, 150), (70, 154), (170, 152)]))]),
    'w_turtle': dict(  # 亀のならい: 浜辺の砂を、ゆっくり歩く亀
        light=dict(pool=(112, 110), radius=(170, 110), **DAWN),
        env=('coast', dict(hz=86, shore=120, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 60, 8),))),
        items=[('foam', dict(x0=0, x1=224, y=116)), ('shell', dict(x=40, y=146, r=5)), ('turtle', dict(x=112, base=152, s=2.0, facing=-1))]),
    'w_worm': dict(  # 蚯蚓のならい: 雨上がりの土から身をもたげる蚯蚓
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=104, ground='leather'),
        items=[('furrows', dict(y0=108)), ('sprout_pot', dict(x=180, base=150)), ('worm', dict(x=96, base=150, s=1.5)),
               ('mushrooms', dict(x=40, base=154))]),
}
