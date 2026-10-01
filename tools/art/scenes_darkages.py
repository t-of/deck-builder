"""暗黒時代（cards-darkages.js）の 47 枚の場面データ。書き方は scenes.py の冒頭を見る。
荒れ果てた世の札なので、霧・曇った夜明け・焚き火・墓地の月・廃墟を散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)
DAWN = dict(fall=1.0, flat=0.45)


def _dawn(hz=118, ground='foliage', hills=((100, 12, 0.5, 0.6, 3),), gain=0.7):
    return ('night', dict(hz=hz, moon=None, sky_ramp='dawn', stars=0, hills=list(hills), ground_ramp=ground, ground_gain=gain))


SCENES = {
    # ================= がれき・避難所・特別な札 =================
    'ruins': dict(  # がれき: 崩れた柱と石の山、伸びた草
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=126, ground='stone'),
        items=[('broken_column', dict(x=70, base=136, h=76)), ('broken_column', dict(x=160, base=132, h=44, r=8, gain=0.85)),
               ('rubble', dict(x=112, base=150, n=14, seed=21)), ('block', dict(x=96, y=128, w=30, h=16)),
               ('weeds', dict(x=40, base=150)), ('weeds', dict(x=190, base=148))]),
    'ruin_mine': dict(  # 崩れた坑: 傾いた支え木と、坑口をふさぐ岩
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('cave', dict(hz=134, seed=31)),
        items=[('broken_beams', dict(x0=50, x1=174, top=34, bottom=136)), ('lantern', dict(x=36, y=60, hang=30)),
               ('cart', dict(x=180, base=156, w=40, h=14))]),
    'ruin_library': dict(  # 焼けた書庫: 焦げた書棚、残り火と煙、散らばった頁
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.1, halo=(60, 130, 50, 0.6)),
        env=('room', dict(wall='stone', hz=128, floor='flag')),
        items=[('burnt_shelf', dict(x0=10, x1=214, top=0, bottom=128)), ('smoke_column', dict(x=150, y=70)),
               ('pages', dict(pts=[(40, 150), (90, 154), (130, 144), (176, 156), (200, 146)])), ('embers', dict(pts=[(70, 140)]))]),
    'ruin_market': dict(  # さびれた市: 破れた日よけ、空の木箱、朝の霧
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='stone'),
        items=[('torn_awning', dict(x0=40, x1=184, y=50)), ('crate', dict(x=50, y=120, w=30, h=24, gain=0.8)),
               ('crate', dict(x=140, y=128, w=26, h=20, gain=0.75)), ('basket', dict(x=110, base=150, w=26, h=8, n=0)),
               ('fog', dict(bands=[(120, 10), (146, 8)], gain=0.8))]),
    'ruin_village': dict(  # 捨てられた村: 屋根の破れた家々、枯れ木と鴉
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.05),
        env=('night', dict(hz=126, moon=(36, 24, 10, 0.6), ground_ramp='stone', ground_gain=0.6, stars=20)),
        items=[('ruined_house', dict(x=10, base=128, w=56, h=34)), ('ruined_house', dict(x=120, base=132, w=64, h=38, roof='red', gain=0.75)),
               ('tree', dict(x=196, base=132, h=80, kind='dead', ramp='cloth', gain=0.7, seed=61)), ('raven', dict(x=200, y=78, s=1.0, facing=-1)),
               ('weeds', dict(x=90, base=148))]),
    'ruin_survivors': dict(  # 生き残り: 焚き火を囲んで身を寄せ合う人々
        light=dict(pool=(112, 110), radius=(150, 100), fall=1.15, halo=(112, 132, 60, 0.7)),
        env=('night', dict(hz=118, moon=None, ground_ramp='stone', ground_gain=0.55, stars=30)),
        items=[('ruined_house', dict(x=150, base=120, w=60, h=36, gain=0.5)),
               ('figure', dict(x=62, foot=150, h=92, arms=('reach', 'belly'), legs='crouch', lean=0.15, tunic='cloth', cloak='leather', head='hood', head_ramp='cloth', legs_ramp='cloth')),
               ('figure', dict(x=168, foot=152, h=92, facing=-1, arms=('reach', 'chest'), legs='crouch', lean=0.15, tunic='leather', head='hair', legs_ramp='cloth')),
               ('campfire', dict(x=112, base=150, s=1.1))]),
    'shack': dict(  # 掘っ立て小屋: 継ぎはぎの板と、灯のひとつ窓（雨の夜）
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(118, 98, 30, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp='leather', ground_gain=0.55, stars=0, clouds=((30, 110, 12), (50, 90, 10)))),
        items=[('shack', dict(x=112, base=140, w=110, h=64)), ('barrel', dict(x=190, base=150, r=11, h=24, gain=0.7)), ('rain', dict(n=120, seed=2))]),
    'tombs': dict(  # 墓所: 半ば埋もれた霊廟と、墓石の並び
        light=dict(pool=(112, 100), radius=(160, 105), fall=1.1, halo=(36, 26, 40, 0.7)),
        env=('night', dict(hz=128, moon=(36, 26, 11), ground_ramp='stone', ground_gain=0.6, stars=24)),
        items=[('crypt', dict(x=112, base=130, w=96, h=60)),
               ('gravestones', dict(pts=[(28, 148, 16, 26), (54, 152, 14, 22), (176, 150, 16, 26), (202, 154, 14, 20)])),
               ('fog', dict(bands=[(146, 8)], gain=0.7))]),
    'wildestate': dict(  # 荒れた小屋: 草に呑まれた、灯のない家
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='foliage'),
        items=[('ruined_house', dict(x=70, base=134, w=70, h=40, roof='wood', gain=0.85)), ('tree', dict(x=196, base=128, h=70, kind='oak', gain=0.6, seed=62)),
               ('weeds', dict(x=70, base=150, n=10, h=24)), ('weeds', dict(x=140, base=152, n=9, h=22)), ('fence', dict(x0=0, x1=60, base=150, h=12, gain=0.55))]),
    'booty': dict(  # ぶんどり品: 口の開いた袋から、杯・首飾り・金貨がこぼれる
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('loot_sack', dict(x=104, base=150))]),
    'lunatic': dict(  # 乱心者: ぼろをまとい、両腕を振り上げて笑う
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=('night', dict(hz=126, moon=(30, 22, 12), sky_ramp='purple', ground_ramp='stone', ground_gain=0.55, stars=30)),
        items=[('figure', dict(x=110, foot=154, h=112, arms=('raise', 'lift'), legs='stride', tunic='cloth', head='hair', hair='paper', legs_ramp='cloth', belt=None, face=True)),
               ('wisps', dict(pts=[(170, 50), (50, 70)]))]),
    'sellsword': dict(  # 雇われ剣士: 両手剣を肩に担ぐ、傷だらけの剣士
        light=dict(pool=(104, 84), radius=(150, 100), fall=1.1, halo=(18, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)),
               ('figure', dict(x=112, foot=154, h=116, arms=('hip', 'lift'), tunic='leather', armor=True, head='hair', beard='hair', cloak='red', legs_ramp='cloth',
                               face=True, props=[(1, 'big_sword', True)]))]),
    'knights': dict(  # 遍歴騎士: 鎧の騎士が、馬着の馬の傍らで旗を立てる
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=126),
        items=[('horse', dict(x=152, base=150, s=1.2, blanket='red')),
               ('figure', dict(x=68, foot=154, h=112, arms=('chest', 'low'), tunic='blue', armor=True, head='helm', cloak='red', legs_ramp='silver',
                               props=[(0, ('shield', dict(ramp='blue')), True)], behind=[(1, ('banner', dict(ramp='red', deg=-92, length=4.6, flag=(2.2, 1.8))))])),
               ('plume', dict(x=68, y=48))]),
    # ================= 王国カード: 物と場所 =================
    'poorhouse': dict(  # 貧乏長屋: 割れた窓の長屋、外の粥の鍋
        light=dict(pool=(112, 100), radius=(170, 105), fall=1.05, halo=(150, 130, 50, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.6, stars=10)),
        items=[('ruined_house', dict(x=0, base=132, w=90, h=60, roof='wood', gain=0.75)), ('ruined_house', dict(x=100, base=132, w=80, h=56, roof='red', gain=0.65)),
               ('cauldron', dict(x=150, base=154, r=20, brew='paper'))]),
    'marketsquare': dict(  # 広小路: 霧の朝、市の十字碑のまわりの屋台
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=_dawn(hz=120, ground='stone'),
        items=[('house', dict(x=-10, base=118, w=60, h=50, roof_h=22, roof='wood', gain=0.6, windows=[(12, 12, 8, 9, True)])),
               ('house', dict(x=172, base=118, w=60, h=50, roof_h=22, roof='red', gain=0.55, windows=[(12, 12, 8, 9, False)])),
               ('stall', dict(x0=10, x1=70, top=98, base=150, colors=('blue', 'paper'))), ('stall', dict(x0=154, x1=214, top=98, base=150, colors=('red', 'paper'))),
               ('market_cross', dict(x=112, base=150)), ('fog', dict(bands=[(110, 10)], gain=0.75))]),
    'lumberroom': dict(  # がらくた部屋: 屋根裏に積もったがらくたと蜘蛛の巣
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.1, halo=(40, 30, 40, 0.5)),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[('window_arch', dict(x=26, y=8, w=24, h=40)), ('cobweb', dict(x=224, y=0, r=26)), ('clutter', dict(x=112, base=150))]),
    'arsenal': dict(  # 武具蔵: 壁の剣と槍の立て掛け、盾の列
        light=dict(pool=(112, 90), radius=(150, 100), halo=(16, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=132, floor='flag')),
        items=[('torch', dict(x=14, y=40)), ('shield_row', dict(x0=30, x1=210, y=30)), ('weapon_rack', dict(x0=30, x1=210, top=58, base=132)),
               ('barrel', dict(x=200, base=156, r=12, h=26, gain=0.8))]),
    'corpsecart': dict(  # 屍車: 霧の通りを行く、布包みを積んだ荷車
        light=dict(pool=(108, 100), radius=(150, 100), fall=1.1, halo=(40, 50, 40, 0.6)),
        env=('night', dict(hz=126, moon=None, ground_ramp='stone', ground_gain=0.55, stars=10)),
        items=[('ruined_house', dict(x=150, base=126, w=64, h=40, gain=0.45)), ('lantern', dict(x=40, y=60, hang=30)),
               ('flat_cart', dict(x=96, base=152, w=96)), ('shrouds', dict(x=96, y=120, n=3)), ('fog', dict(bands=[(130, 10), (152, 8)], gain=0.7))]),
    'fief': dict(  # 知行地: 畑に囲まれた小さな砦と、領主の旗
        light=dict(pool=(112, 90), radius=(180, 110), **DAWN),
        env=_dawn(hz=116, ground='leather'),
        items=[('tower', dict(x=96, base=114, w=36, h=60, roof='red', windows=[(-2, 20, 4, 7)])), ('wall', dict(x0=60, x1=170, top=96, bottom=116, merlon=6, gap=4)),
               ('flag_pole', dict(x=172, base=96, ramp='blue')), ('furrows', dict(y0=124)), ('wheat_sheaves', dict(x=20, base=156, n=2)),
               ('stack', dict(cx=190, base=154, r=9, n=3, metal='silver', stamp='tower', seed=61))]),
    'stronghold': dict(  # 城郭: 岩山の上の、厚い壁の砦
        light=dict(pool=(112, 80), radius=(170, 110), fall=1.05),
        env=('night', dict(hz=140, moon=(30, 24, 10, 0.4), ground_ramp=None, stars=30)),
        items=[('rocks', dict(pts=[(112, 160, 230, 60), (40, 160, 80, 30)], gain=0.75)),
               ('tower', dict(x=64, base=104, w=40, h=74, roof=None, crenel=True, windows=[(-2, 24, 5, 8)])),
               ('tower', dict(x=126, base=106, w=44, h=86, roof=None, crenel=True, windows=[(-2, 26, 5, 8), (-2, 50, 5, 8)])),
               ('wall', dict(x0=40, x1=190, top=80, bottom=108, merlon=8, gap=5))]),
    'hardware': dict(  # 金物売り: 吊るした鍋・蝶番・釘の箱、道具の棚
        light=dict(pool=(112, 96), radius=(150, 100), halo=(30, 44, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('lantern', dict(x=26, y=44, hang=0)), ('tool_rack', dict(x0=60, x1=214, y=12, tools=('saw', 'hammer', 'pliers', 'tongs', 'coil'), s=1.4)),
               ('table', dict(x0=30, x1=200, top=118, legs_to=156, front=True)),
               ('pots', dict(x=50, base=118, n=3)), ('nails_box', dict(x=140, base=118)), ('hinges', dict(x=180, base=116))]),
    'hideout': dict(  # 盗賊のねぐら: 洞窟の焚き火、寝床、ぶんどり品
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(110, 124, 60, 0.7)),
        env=('cave', dict(hz=128, seed=33)),
        items=[('bedrolls', dict(pts=[(40, 146, 'red'), (184, 150, 'blue')])), ('campfire', dict(x=110, base=148, s=1.1)),
               ('chest', dict(x=150, base=132, w=44, h=20, fill='gold')), ('barrel', dict(x=30, base=128, r=12, h=28, gain=0.7)),
               ('sword_stuck', dict(x=74, base=136))]),
    'ossuary': dict(  # 骨の間: 壁一面に積んだ髑髏と骨、蝋燭
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15, halo=(112, 100, 50, 0.5)),
        env=('room', dict(wall='stone', hz=130, floor='flag')),
        items=[('skull_wall', dict(x0=10, x1=214, top=4, bottom=130)), ('candle', dict(x=112, base=148, h=16, r=4))]),
    'forgery': dict(  # 贋金: 鋳型と、本物の金貨に混ぜた鉛の偽金
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=96, floor='table')),
        items=[('candle', dict(x=28, base=94, h=12, r=3)), ('forger_table_big', dict(x=124, y=124)), ('burner', dict(x=190, base=118))]),
    'ransack': dict(  # 強奪: 荒らされた部屋、倒れた椅子、開いた箱
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('torch', dict(x=18, y=40)), ('shelf', dict(x0=130, x1=220, y=50)), ('pages', dict(pts=[(150, 46), (176, 46)])),
               ('ransacked', dict())]),
    'rework': dict(  # 再普請: 屋根を葺き直す家、梯子と新しい梁
        light=dict(pool=(112, 96), radius=(180, 110), **DAWN),
        env=_dawn(hz=128),
        items=[('house', dict(x=40, base=140, w=100, h=56, roof_h=40, roof='wood', windows=[(14, 14, 12, 12, True), (70, 14, 12, 12, True)], door=(42, 18, 26))),
               ('frame', dict(x0=96, x1=150, base=84, h=0)), ('ladder', dict(x=150, top=70, base=150, w=16)),
               ('plank', dict(x0=160, y0=152, x1=214, y1=148, w=3))]),
    'offering': dict(  # 供物台: 果物の盛り皿、杯、蝋燭、香の煙
        light=dict(pool=(112, 104), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[('niche', dict(x=112, top=8, w=60, h=70)), ('offering_altar', dict(x=112, base=148))]),
    'huntland': dict(  # 猟場: 夜明けの森、狩り小屋と鹿
        light=dict(pool=(112, 100), radius=(170, 110), **DAWN),
        env=('forest', dict(hz=124, moon=None, seed=31)),
        items=[('hut', dict(x=50, base=126, w=60, h=30)), ('deer', dict(x=150, base=146, s=1.4, facing=-1))]),
    'rats': dict(  # どぶネズミ: 穀物の袋にたかるネズミの群れ
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=116, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)), ('grain_sacks', dict(x=112, base=148)),
               ('big_rat', dict(x=60, base=152, facing=1)), ('big_rat', dict(x=96, base=126, facing=1)), ('big_rat', dict(x=150, base=154, facing=1)), ('big_rat', dict(x=176, base=148, facing=1)), ('big_rat', dict(x=130, base=100, facing=1))]),
    # ================= 王国カード: 人物 =================
    'pauper': dict(  # 文なし: 道ばたに座り、銅貨の椀を差し出す
        light=dict(pool=(104, 100), radius=(150, 100), fall=1.1, halo=(40, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=36, y=40, hang=0)),
               ('figure', dict(x=110, foot=154, h=104, arms=('present', 'belly'), legs='crouch', lean=0.1, tunic='cloth', cloak='leather', head='hood', head_ramp='leather',
                               legs_ramp='cloth', belt=None, face=True, props=[(1, 'bowl', True)])),
               ('coin', dict(cx=176, cy=152, r=5, metal='copper', stamp='pip'))]),
    'footman': dict(  # 若党: 家紋の胴着で槍を立てる若い家来
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(16, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('hang_banner', dict(x=170, top=0, w=28, h=60, ramp='green', kind='chevron')),
               ('figure', dict(x=104, foot=154, h=104, arms=('hip', 'low'), tunic='green', trim='gold', head='cap', head_ramp='green', legs_ramp='paper',
                               behind=[(1, ('staff', dict(deg=-92, length=5.6, top='spear', below=2.4)))]))]),
    'rover': dict(  # 風来坊: 杖をつき、犬を連れて旅する
        light=dict(pool=(104, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=120, ground='foliage'),
        items=[('road', dict(x=150, top=120, base=160, w0=6, w1=110, ramp='sand')),
               ('figure', dict(x=90, foot=154, h=110, arms=('down', 'forward'), legs='stride', tunic='red', cloak='cloth', head='hat', head_ramp='leather', legs_ramp='cloth',
                               props=[(1, ('staff', dict(deg=-80, length=3.4, below=2.2)), False)])),
               ('dog', dict(x=170, base=156, s=1.1, ramp='paper'))]),
    'gleaner': dict(  # くず拾い: 刈り跡の畑で、落ち穂を拾う
        light=dict(pool=(104, 96), radius=(170, 110), **DAWN),
        env=_dawn(hz=112, ground='leather'),
        items=[('furrows', dict(y0=118)), ('wheat_sheaves', dict(x=170, base=134, n=2)),
               ('figure', dict(x=88, foot=154, h=104, arms=('reach', 'present'), lean=0.22, robe=True, gown=True, tunic='leather', head='hood', head_ramp='paper',
                               props=[(1, ('basket_held', {}), True)]))]),
    'recluse': dict(  # 世捨て人: 洞の口で蝋燭を灯す、ひげの隠者
        light=dict(pool=(104, 92), radius=(150, 100), fall=1.15, halo=(48, 104, 40, 0.6)),
        env=('cave', dict(hz=130, seed=35)),
        items=[('candle', dict(x=48, base=150, h=10, r=3, holder=False)),
               ('figure', dict(x=112, foot=154, h=108, arms=('chest', 'low'), lean=0.08, robe=True, tunic='leather', head='hood', head_ramp='leather', beard='paper',
                               face=True, props=[(1, ('staff', dict(deg=-90, length=3.6, below=2.6, top='crook')), False)])),
               ('book', dict(x=150, y=148, w=24, h=4, t=8, ramp='leather'))]),
    'scholar': dict(  # 物知り: 髑髏と蝋燭のそばで、大きな書を読む
        light=dict(pool=(108, 96), radius=(150, 100), halo=(36, 74, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=116, floor='planks')),
        items=[('shelf', dict(x0=130, x1=222, y=36)), ('books_row', dict(x0=134, x1=218, base=36, seed=61)),
               ('shelf', dict(x0=130, x1=222, y=70)), ('books_row', dict(x0=134, x1=218, base=70, seed=62)),
               ('figure', dict(x=96, foot=170, h=118, arms=('present', 'present'), lean=0.08, robe=True, tunic='blue', head='coif', head_ramp='blue', beard='paper', face=True)),
               ('table', dict(x0=10, x1=214, top=124, legs_to=160, front=True)),
               ('open_book', dict(x=100, y=118, w=22, h=10)), ('skull', dict(x=168, y=118, s=0.8)), ('candle', dict(x=40, base=124, h=12, r=3))]),
    'waif': dict(  # 宿なし子: 雪の路地で、両手を差し出す子
        light=dict(pool=(104, 96), radius=(150, 100), fall=1.1, halo=(40, 60, 40, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp=None, stars=0, clouds=((20, 100, 10),))),
        items=[('ruined_house', dict(x=130, base=128, w=80, h=60, gain=0.6)), ('lantern', dict(x=40, y=60, hang=30)),
               ('snow_ground', dict(y0=126)),
               ('figure', dict(x=96, foot=154, h=86, arms=('present', 'present'), tunic='cloth', cloak='leather', head='hood', head_ramp='paper', legs_ramp='cloth',
                               belt=None, face=True)),
               ('snow', dict(n=90, seed=11))]),
    'ravager': dict(  # 荒らし: 燃える家を背に、松明を振り上げる
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.05, halo=(150, 60, 60, 0.6)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.6, stars=10)),
        items=[('house_fire', dict(x=130, base=130, w=80, h=46)),
               ('figure', dict(x=76, foot=154, h=114, arms=('down', 'raise'), legs='stride', tunic='red', armor=True, head='helm', cloak='cloth', legs_ramp='cloth',
                               props=[(1, 'torch_held', True), (0, ('axe', dict(deg=100, length=2.2)), True)]))]),
    'parade': dict(  # 練り歩き: 太鼓と旗の行列が、町の通りを進む
        light=dict(pool=(112, 90), radius=(170, 110), **DAWN),
        env=_dawn(hz=124, ground='stone'),
        items=[('house', dict(x=150, base=122, w=60, h=40, roof_h=22, roof='red', gain=0.6, windows=[(10, 10, 8, 9, True)])),
               ('figure', dict(x=170, foot=148, h=94, facing=-1, arms=('down', 'lift'), tunic='blue', head='cap', head_ramp='blue', legs_ramp='paper',
                               props=[(1, ('banner', dict(ramp='blue', deg=-92, length=3.2, flag=(2.0, 1.6))), True)])),
               ('figure', dict(x=110, foot=154, h=104, facing=-1, arms=('belly', 'present'), tunic='red', trim='gold', head='feather', head_ramp='red', legs_ramp='paper',
                               props=[(1, 'drum', True)])),
               ('figure', dict(x=52, foot=158, h=108, facing=-1, arms=('down', 'lift'), tunic='green', head='cap', head_ramp='gold', legs_ramp='paper',
                               props=[(1, ('banner', dict(ramp='gold', deg=-92, length=3.4, flag=(2.0, 1.6))), True)]))]),
    'scrounger': dict(  # あさり屋: ごみの山をあさり、袋に詰める
        light=dict(pool=(104, 100), radius=(150, 100), fall=1.1, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)), ('clutter', dict(x=150, base=154)),
               ('figure', dict(x=80, foot=154, h=100, arms=('reach', 'low'), legs='crouch', lean=0.18, tunic='leather', head='cap', head_ramp='cloth', legs_ramp='cloth',
                               props=[(1, ('bag', dict(ramp='paper')), True)]))]),
    'troubadour': dict(  # 旅芸人: 羽根帽子でリュートを奏でる
        light=dict(pool=(104, 88), radius=(150, 100), halo=(30, 52, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[('lantern', dict(x=28, y=44, hang=0)), ('hang_banner', dict(x=176, top=0, w=26, h=50, ramp='green', kind='circle')),
               ('figure', dict(x=108, foot=154, h=112, arms=('belly', 'present'), legs='stride', tunic='red', cloak='green', head='feather', head_ramp='blue',
                               legs_ramp='gold', face=True, props=[(0, 'lute', True)]))]),
    'impostor': dict(  # なりすまし: 姿見に別の顔が映る、仮面を掲げる男
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.1, halo=(30, 40, 40, 0.5)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('mirror_stand', dict(x=170, base=150, h=96)),
               ('figure', dict(x=84, foot=154, h=110, arms=('down', 'raise'), tunic='purple', cloak='cloth', head='hair', legs_ramp='cloth',
                               props=[(1, ('mask_stick', dict(ramp='paper')), True)]))]),
    'viscount': dict(  # 子爵: 羽根帽子に杖、金の鎖の貴族
        light=dict(pool=(104, 86), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[('candelabra', dict(x=26, base=76, h=26)), ('shelf', dict(x0=8, x1=46, y=76)), ('hang_banner', dict(x=170, top=0, w=30, h=66, ramp='blue', kind='cross')),
               ('figure', dict(x=108, foot=154, h=114, arms=('hip', 'low'), tunic='blue', trim='gold', mantle='gold', cloak='red', head='feather', head_ramp='cloth', beard='hair',
                               legs_ramp='paper', face=True, props=[(1, ('staff', dict(deg=-92, length=3.0, below=1.4, top='knob')), False)]))]),
    'zealot': dict(  # 邪教徒: 頭巾の信徒が、紫の印の前で松明を掲げる
        light=dict(pool=(104, 88), radius=(150, 100), fall=1.15, halo=(64, 40, 50, 0.7)),
        env=('cave', dict(hz=130, seed=37)),
        items=[('rune_circle', dict(x=150, y=60, rx=36, ry=36, ramp='purple')),
               ('figure', dict(x=92, foot=154, h=110, arms=('lift', 'chest'), robe=True, tunic='purple', head='hood', head_ramp='cloth', mantle='cloth',
                               props=[(0, 'torch_held', True)])),
               ('wisps', dict(pts=[(180, 100)]))]),
    'gravedigger': dict(  # 墓荒らし: 月夜の墓地で、鋤で墓を掘り返す
        light=dict(pool=(104, 96), radius=(160, 105), fall=1.1, halo=(36, 24, 40, 0.7)),
        env=('night', dict(hz=126, moon=(36, 24, 11), ground_ramp='leather', ground_gain=0.55, stars=24)),
        items=[('gravestones', dict(pts=[(150, 138, 18, 30), (190, 142, 14, 24), (30, 140, 14, 22)])),
               ('dug_hole', dict(x=150, y=150)), ('lantern', dict(x=176, y=140, hang=None)),
               ('figure', dict(x=92, foot=154, h=110, arms=('reach', 'low'), lean=0.12, tunic='cloth', cloak='leather', head='hood', head_ramp='cloth', legs_ramp='cloth',
                               props=[(1, 'spade', True)]))]),
    'junkman': dict(  # 古物商: がらくたを山積みにした手押し車
        light=dict(pool=(104, 96), radius=(170, 105), **DAWN),
        env=_dawn(hz=124, ground='stone'),
        items=[('flat_cart', dict(x=150, base=152, w=90)), ('clutter_cart', dict(x=150, y=124)),
               ('figure', dict(x=70, foot=154, h=108, arms=('belly', 'forward'), tunic='leather', apron='paper', head='tophat', head_ramp='leather', beard='paper', legs_ramp='cloth'))]),
    'psychic': dict(  # 霊能者: 頭布の女が、光る玉に手をかざす
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(112, 120, 50, 0.4)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[('wisps', dict(pts=[(170, 40), (50, 50)])),
               ('figure', dict(x=112, foot=170, h=118, arms=('present', 'present'), robe=True, gown=True, tunic='purple', head='long', hair='hair', face=True)),
               ('table', dict(x0=20, x1=204, top=126, legs_to=160, front=True, cloth='purple')),
               ('crystal_ball', dict(x=112, base=132, r=16, ramp='purple'))]),
    'villain': dict(  # 悪漢: 黒い外套で短剣を隠し持つ、にやりと笑う男
        light=dict(pool=(104, 88), radius=(140, 100), fall=1.2, halo=(30, 40, 40, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag', bw=16, bh=8)),
        items=[('lantern', dict(x=30, y=44, hang=0)),
               ('figure', dict(x=112, foot=154, h=114, arms=('chest', 'low'), tunic='purple', cloak='cloth', head='tophat', head_ramp='cloth', beard='hair', legs_ramp='cloth',
                               face=True, props=[(1, ('dagger', dict(deg=110)), True)]))]),
}
