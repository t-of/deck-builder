"""陰謀（cards-intrigue.js）の 32 枚の場面データ。書き方は scenes.py の冒頭を見る。"""

SCENES = {
    # ================= 物と場所 =================
    'backyard': dict(  # 裏庭: 裏口の灯、物干しの布、樽と柵
        light=dict(pool=(118, 96), radius=(160, 100), fall=1.1, halo=(40, 76, 30, 0.35)),
        env=('night', dict(hz=124, moon=None, ground_ramp='foliage', ground_gain=0.7, wave=1.0)),
        items=[
            ('house', dict(x=0, base=128, w=70, h=56, roof_h=30, roof='wood', windows=[(10, 12, 10, 12, True)], door=(40, 14, 26), gain=0.8)),
            ('lantern', dict(x=40, y=80, hang=72)),
            ('clothesline', dict(x0=86, x1=216, y=56, cloths=('paper', 'blue', 'red', 'paper', 'green'))),
            ('fence', dict(x0=70, x1=224, base=136, h=16, gain=0.75)),
            ('barrel', dict(x=96, base=150, r=13, h=30, gain=0.95)),
            ('logs', dict(x=150, base=156, n=3, r=6)),
        ]),
    'slum': dict(  # 長屋: 狭い路地に、背の高い家がひしめき、窓から窓へ物干し
        light=dict(pool=(112, 104), radius=(190, 130), fall=0.9, halo=(112, 18, 20, 0.4), flat=0.3),
        env=('night', dict(hz=140, moon=(112, 18, 8, 0.4), ground_ramp='stone', ground_gain=0.65, wave=0.3, clouds=())),
        items=[
            ('house', dict(x=-6, base=146, w=46, h=104, roof_h=18, roof='wood', gain=0.8, windows=[(8, 12, 7, 9, True), (26, 12, 7, 9, False), (8, 40, 7, 9, False), (26, 40, 7, 9, True), (8, 68, 7, 9, True)])),
            ('house', dict(x=40, base=146, w=40, h=86, roof_h=16, roof='red', gain=0.7, windows=[(8, 12, 7, 9, True), (24, 40, 7, 9, True), (8, 60, 7, 9, False)])),
            ('house', dict(x=140, base=146, w=40, h=92, roof_h=16, roof='wood', gain=0.65, windows=[(8, 14, 7, 9, False), (24, 14, 7, 9, True), (8, 44, 7, 9, True)])),
            ('house', dict(x=176, base=146, w=48, h=108, roof_h=18, roof='red', gain=0.55, windows=[(10, 12, 7, 9, True), (28, 40, 7, 9, True), (10, 70, 7, 9, False)])),
            ('clothesline', dict(x0=60, x1=160, y=60, cloths=('red', 'paper', 'blue'))),
            ('clothesline', dict(x0=74, x1=150, y=96, cloths=('paper', 'green'))),
            ('barrel', dict(x=110, base=152, r=10, h=22, gain=0.8)),
        ]),
    'fountain': dict(  # 占いの泉: 中庭の泉、水底に投げ入れた硬貨が光る
        light=dict(pool=(112, 104), radius=(160, 105), fall=1.1, halo=(36, 26, 40, 0.7)),
        env=('night', dict(hz=104, moon=(36, 26, 11), ground_ramp='stone', ground_gain=0.75, wave=0.3,
                           hills=[(92, 10, 0.45, 0.7, 3)])),
        items=[
            ('tree', dict(x=20, base=110, h=56, kind='pine', gain=0.6, seed=12)),
            ('tree', dict(x=206, base=110, h=60, kind='oak', gain=0.6, seed=13)),
            ('fountain', dict(x=112, base=146, r=46)),
        ]),
    'suspension': dict(  # つり橋: 深い谷に渡した綱と板の橋
        light=dict(pool=(112, 96), radius=(180, 120), fall=0.95, halo=(40, 24, 40, 0.7), flat=0.5),
        env=('pass', dict(hz=170, moon=(40, 24, 10, 0.3))),
        items=[
            ('cliff', dict(x0=0, x1=58, top=96, side=1, gain=0.9)),
            ('cliff', dict(x0=224, x1=166, top=92, side=-1, gain=0.75)),
            ('rope_bridge', dict(x0=50, y0=96, x1=172, y1=92, sag=26)),
        ]),
    'foundry': dict(  # 鋳造所: 傾けた坩堝から型へ、溶けた金属が流れる
        light=dict(pool=(100, 100), radius=(150, 100), fall=1.15, halo=(80, 80, 60, 0.9), key=0.8),
        env=('room', dict(wall='stone', hz=118, floor='flag', bw=14, bh=8)),
        items=[
            ('tool_rack', dict(x0=150, x1=220, y=24, tools=('tongs', 'hammer', 'tongs'))),
            ('forge', dict(x=4, y=44, w=50, h=50)),
            ('crucible_pour', dict(x=128, y=76, s=1.5)),
            ('molds', dict(x0=72, y=142, n=3, w=34)),
            ('sparks', dict(pts=[(86, 118), (96, 126), (80, 130), (108, 122), (74, 112)])),
            ('stack', dict(cx=200, base=152, r=11, n=6, metal='gold', seed=11)),
        ]),
    'watermill': dict(  # 水車小屋: 小川の水を受けて回る大きな水車
        light=dict(pool=(108, 92), radius=(160, 105), fall=1.1, halo=(30, 22, 40, 0.7)),
        env=('night', dict(hz=118, moon=(30, 22, 10), hills=[(100, 12, 0.45, 0.65, 4)], ground_gain=0.7)),
        items=[
            ('house', dict(x=96, base=124, w=60, h=46, roof_h=30, roof='wood', windows=[(10, 10, 9, 10, True), (36, 10, 9, 10, True)], door=(22, 12, 18), timber=True)),
            ('stream', dict(y0=130, y1=160)),
            ('waterwheel', dict(x=68, y=110, r=30)),
            ('tree', dict(x=200, base=126, h=60, kind='oak', gain=0.7, seed=14)),
        ]),
    'minetown': dict(  # 鉱山町: 坑口の櫓と、斜面に寄り添う家並み
        light=dict(pool=(112, 90), radius=(160, 105), fall=1.1, halo=(36, 24, 40, 0.7)),
        env=('night', dict(hz=128, moon=(36, 24, 10, 0.45), hills=[(70, 40, 0.5, 0.55, 2)], ground_ramp='stone', ground_gain=0.7)),
        items=[
            ('headframe', dict(x=146, base=112, h=72)),
            ('house', dict(x=20, base=114, w=34, h=22, roof_h=18, roof='red', gain=0.65, windows=[(8, 6, 6, 7, True)])),
            ('house', dict(x=180, base=120, w=34, h=24, roof_h=18, roof='wood', gain=0.6, windows=[(16, 7, 6, 7, True)])),
            ('house', dict(x=46, base=138, w=48, h=30, roof_h=22, roof='wood', windows=[(8, 8, 8, 9, True), (30, 8, 8, 9, True)], door=(20, 8, 13))),
            ('rails', dict(y=150)),
            ('cart', dict(x=150, base=152, w=44, h=18)),
        ]),
    'tunnel': dict(  # 抜け道: 書棚が回って開き、奥に松明の灯る下り階段
        light=dict(pool=(112, 92), radius=(150, 100), fall=1.15, halo=(130, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=126, floor='flag')),
        items=[
            ('bookcase', dict(x0=0, x1=72, top=10, bottom=126)),
            ('secret_door', dict(x=110, base=126, w=60, h=96)),
            ('bookcase', dict(x0=174, x1=224, top=10, bottom=126)),
            ('candle', dict(x=70, base=150, h=10, r=3)),
        ]),
    'marquis': dict(  # 荘園主: 生垣の庭の奥に、両翼をもつ大きな館
        light=dict(pool=(112, 84), radius=(170, 110), fall=1.05, halo=(28, 22, 40, 0.7)),
        env=('night', dict(hz=112, moon=(28, 22, 10), hills=[(96, 10, 0.45, 0.7, 6)], ground_gain=0.7)),
        items=[
            ('palace', dict(x=112, base=104, w=170, h=54)),
            ('hedge', dict(x0=0, x1=96, base=134, h=10)), ('hedge', dict(x0=128, x1=224, base=134, h=10)),
            ('topiary', dict(x=60, base=150, h=28)), ('topiary', dict(x=164, base=150, h=28)),
            ('carpet', dict(x=112, top=110, base=160, w0=12, w1=50, ramp='stone')),
        ]),
    'swap': dict(  # 取り替え: 本物の金の杯と、紫の災いが立つ偽の杯をすり替える
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(28, 60, 40, 0.6)),
        env=('room', dict(wall='stone', hz=104, floor='table', floor_ramp='wood', floor_gain=0.8)),
        items=[
            ('candle', dict(x=28, base=100, h=12, r=3)),
            ('table_cloth', dict(y=112, ramp='purple')),
            ('goblet', dict(x=82, base=132, s=2.4)),
            ('goblet', dict(x=150, base=132, s=2.4, ramp='stone', wine=False)),
            ('wisps', dict(pts=[(160, 90), (146, 96)])),
            ('swap_arrows', dict(x=116, y=86)),
        ]),
    'tradepost': dict(  # 取引所: 看板の下に木箱と袋、帳場に銀貨
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.0, halo=(34, 46, 40, 0.6), flat=0.48),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[
            ('lantern', dict(x=34, y=44, hang=0)),
            ('sign', dict(x=112, y=24, w=60, h=26, emblem='coin')),
            ('crate', dict(x=10, y=104, w=36, h=30)), ('crate', dict(x=16, y=78, w=26, h=26, gain=1.05)),
            ('sack', dict(x=196, base=148, r=14)), ('sack', dict(x=176, base=152, r=11, ramp='leather')),
            ('table', dict(x0=60, x1=166, top=114, legs_to=158, front=True)),
            ('stack', dict(cx=96, base=118, r=10, n=5, metal='silver', stamp='tower', seed=12)),
            ('book', dict(x=118, y=112, w=24, h=3, t=8, ramp='red')),
        ]),
    'refine': dict(  # 手直し: 万力の宝石をやすりで削り、一段上の石に仕上げる
        light=dict(pool=(112, 108), radius=(150, 100), fall=1.1, halo=(30, 54, 40, 0.6)),
        env=('room', dict(wall='stone', hz=92, floor='table', floor_ramp='wood')),
        items=[
            ('candle', dict(x=30, base=94, h=12, r=3)),
            ('shelf', dict(x0=130, x1=218, y=48)),
            ('bottle', dict(x=146, base=48, h=12, r=4, ramp='blue')), ('bottle', dict(x=166, base=48, h=14, r=4, ramp='red')),
            ('gem_bench', dict(x=108, y=128, s=1.7)),
        ]),
    'mansion': dict(  # 豪邸: 金の門の向こう、灯りのあふれる柱廊の館
        light=dict(pool=(112, 80), radius=(165, 110), fall=1.05, halo=(112, 70, 60, 0.4)),
        env=('night', dict(hz=118, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.3)),
        items=[
            ('palace', dict(x=112, base=114, w=230, h=78, cols=6)),
            ('gate_bars', dict(x0=0, x1=224, top=118, base=160)),
            ('coin', dict(cx=112, cy=136, r=12, metal='gold', tilt=0.95, stamp='crown')),
        ]),
    'hideaway': dict(  # 隠れ部屋: 床板の落とし戸の下に、梯子と金貨
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(30, 50, 40, 0.6)),
        env=('room', dict(wall='plank', hz=86, floor='planks')),
        items=[
            ('candle', dict(x=30, base=118, h=12, r=3)),
            ('crate', dict(x=170, y=88, w=34, h=28, gain=0.8)),
            ('trapdoor', dict(x=112, y=124, w=70, d=26)),
            ('sack', dict(x=50, base=150, r=10)),
        ]),
    'hall': dict(  # 広間: 柱の列、天井のシャンデリア、絨毯の先の玉座
        light=dict(pool=(112, 90), radius=(160, 105), fall=1.1, halo=(112, 30, 50, 0.5)),
        env=('room', dict(wall='stone', hz=108, floor='flag')),
        items=[
            ('window_arch', dict(x=78, y=10, w=22, h=50)), ('window_arch', dict(x=124, y=10, w=22, h=50)),
            ('carpet', dict(x=112, top=108, base=160, w0=26, w1=90)),
            ('throne', dict(x=112, base=112)),
            ('column', dict(x=46, top=10, base=128, r=8)), ('column', dict(x=178, top=10, base=128, r=8, gain=0.85)),
            ('column', dict(x=12, top=0, base=150, r=10, gain=0.8)), ('column', dict(x=212, top=0, base=150, r=10, gain=0.65)),
            ('chandelier', dict(x=112, y=22, r=22, chain_top=0)),
        ]),
    'toll': dict(  # 通行料: 街道の遮断棒と番小屋、銭箱
        light=dict(pool=(112, 98), radius=(160, 100), fall=1.1, halo=(44, 54, 40, 0.7)),
        env=('night', dict(hz=118, moon=None, hills=[(104, 14, 0.45, 0.6, 9)], ground_ramp='stone', ground_gain=0.7)),
        items=[
            ('house', dict(x=6, base=132, w=42, h=34, roof_h=20, roof='red', windows=[(10, 10, 10, 10, True)], door=(28, 8, 18))),
            ('lantern', dict(x=58, y=70, hang=50)),
            ('toll_gate', dict(x=70, base=146, length=140)),
            ('coin_box', dict(x=58, base=154)),
            ('tree', dict(x=206, base=120, h=56, kind='pine', gain=0.6, seed=15)),
        ]),
    # ================= 人物 =================
    'prowler': dict(  # 忍び: 屋根の上に身を低くして進む影
        light=dict(pool=(112, 80), radius=(150, 100), fall=1.1, halo=(40, 26, 40, 0.7)),
        env=('night', dict(hz=170, moon=(40, 26, 13), stars=40, ground_ramp=None)),
        items=[
            ('house', dict(x=150, base=170, w=60, h=60, roof_h=24, roof='wood', gain=0.4, windows=[(10, 8, 8, 9, True)])),
            ('roof_ridge', dict(y=128)),
            ('figure', dict(x=108, foot=132, h=100, arms=('reach', 'chest'), legs='crouch', lean=0.15, tunic='cloth', head='hood', head_ramp='cloth',
                            mask='cloth', cloak='purple', legs_ramp='cloth', props=[(1, ('dagger', dict(deg=60)), True)])),
        ]),
    'errand': dict(  # 使い走り: 包みを抱えて夜の通りを駆ける少年
        light=dict(pool=(108, 88), radius=(150, 105), fall=1.1, halo=(30, 60, 34, 0.6)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.4)),
        items=[
            ('lamp_post', dict(x=30, base=136, h=86)),
            ('house', dict(x=140, base=122, w=48, h=36, roof_h=24, roof='red', gain=0.55, windows=[(10, 10, 8, 9, True)])),
            ('figure', dict(x=104, foot=152, h=94, arms=((-0.3, 1.0, -1.4, 0.4), 'present'), legs='stride', lean=0.12, tunic='green',
                            head='cap', head_ramp='red', legs_ramp='leather', props=[(1, 'parcel', True)])),
            ('letter_fly', dict(x=58, y=100)),
        ]),
    'carnival': dict(  # 仮装行列: 仮面を掲げ、紙吹雪の中を練り歩く
        light=dict(pool=(108, 84), radius=(150, 105), fall=1.1, halo=(26, 40, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.65, wave=0.4)),
        items=[
            ('lantern_string', dict(y0=12, y1=26, colors=('gold', 'red', 'blue', 'green', 'gold'))),
            ('paper_lantern', dict(x=26, y=44, r=10, ramp='gold', string=0)),
            ('mask', dict(x=176, y=86, ramp='blue')), ('mask', dict(x=196, y=100, ramp='red')),
            ('figure', dict(x=108, foot=152, h=110, arms=('down', 'raise'), legs='stride', tunic='red', trim='gold', cloak='green',
                            head='feather', head_ramp='purple', mask='gold', legs_ramp='blue', props=[(1, ('mask_stick', dict(ramp='purple')), True)])),
            ('confetti', dict(area=(10, 30, 214, 120), n=46, seed=3)),
        ]),
    'butler': dict(  # 家令: 燭台と鍵束を持ち、館の奥を取り仕切る
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.15, halo=(76, 50, 40, 0.6)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[
            ('doorway', dict(x=186, base=122, w=34, h=66)),
            ('hang_banner', dict(x=26, top=0, w=24, h=58, ramp='green', kind='chevron')),
            ('figure', dict(x=108, foot=152, h=112, arms=('lift', 'low'), robe=True, tunic='cloth', trim='gold', mantle='blue', head='hair',
                            props=[(0, 'held_candelabra', True), (1, 'held_keys', True)])),
        ]),
    'conman': dict(  # ぺてん師: 伏せた椀の賭けで、客の銭を巻き上げる
        light=dict(pool=(108, 96), radius=(150, 100), fall=1.15, halo=(28, 48, 40, 0.6)),
        env=('room', dict(wall='plank', hz=112, floor='planks')),
        items=[
            ('candle', dict(x=28, base=110, h=12, r=3)),
            ('figure', dict(x=108, foot=158, h=112, arms=('belly', 'forward'), tunic='purple', trim='gold', head='hat', head_ramp='red',
                            props=[(1, ('held_coin', dict(metal='gold', r=0.6)), True)])),
            ('table', dict(x0=22, x1=202, top=122, legs_to=160, front=True, cloth='green')),
            ('cups_game', dict(x=108, y=128)),
            ('coin', dict(cx=56, cy=126, r=7, metal='copper', stamp='pip')), ('coin', dict(cx=170, cy=128, r=7, metal='silver', stamp='tower')),
        ]),
    'landlord': dict(  # 地主: 借地の小屋を指して、証文と金袋を持つ
        light=dict(pool=(100, 86), radius=(150, 105), fall=1.1, halo=(30, 22, 40, 0.7)),
        env=('night', dict(hz=120, moon=(30, 22, 10), hills=[(104, 12, 0.45, 0.6, 2)], ground_gain=0.7)),
        items=[
            ('house', dict(x=150, base=122, w=54, h=30, roof_h=28, roof='wood', gain=0.75, windows=[(10, 8, 9, 9, True)], door=(32, 9, 16))),
            ('fence', dict(x0=140, x1=224, base=134, h=12, gain=0.65)),
            ('figure', dict(x=86, foot=152, h=112, arms=('belly', 'aim'), tunic='green', robe=True, trim='gold', mantle='red', head='hat', head_ramp='leather',
                            props=[(0, 'letter', True)], behind=[(0, ('bag', {}))])),
        ]),
    'plotter': dict(  # 黒幕: 地図と駒の卓に身を乗り出し、たくらみを練る
        light=dict(pool=(108, 100), radius=(140, 95), fall=1.25, halo=(40, 92, 40, 0.6)),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[
            ('figure', dict(x=112, foot=170, h=118, arms=('present', 'present'), lean=0.12, robe=True, tunic='purple', head='hood', head_ramp='cloth',
                            mantle='cloth')),
            ('table', dict(x0=10, x1=214, top=118, legs_to=160, front=True, cloth='red')),
            ('chess_board', dict(x=140, y=130, w=60)),
            ('held_map_flat', dict(x=60, y=124)),
            ('candle', dict(x=40, base=114, h=12, r=3)),
        ]),
    'envoy': dict(  # 使節: 城門の前で封をした書状を差し出す
        light=dict(pool=(104, 86), radius=(150, 100), fall=1.1, halo=(18, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag', bw=20, bh=10)),
        items=[
            ('torch', dict(x=16, y=40)),
            ('drawbridge_gate', dict(x=176, base=122, w=50, h=80)),
            ('figure', dict(x=100, foot=152, h=112, arms=('down', 'present'), tunic='blue', trim='gold', cloak='green', head='feather', head_ramp='green',
                            legs_ramp='paper', props=[(1, 'letter', True)], behind=[(0, ('banner', dict(ramp='green', deg=-95, length=4.6, flag=(2.0, 1.8))))])),
        ]),
    'chamberlain': dict(  # 侍従: 職杖を立て、金の鎖をかけて玉座の間に立つ
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.15, halo=(16, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('hang_banner', dict(x=160, top=0, w=30, h=72, ramp='red', kind='circle')),
            ('carpet', dict(x=112, top=122, base=160, w0=40, w1=110)),
            ('figure', dict(x=108, foot=154, h=112, arms=('chest', 'low'), robe=True, tunic='red', trim='gold', mantle='blue', head='coif', head_ramp='red',
                            behind=[(1, ('staff', dict(deg=-92, length=5.8, top='knob', below=2.6)))])),
        ]),
    'henchman': dict(  # 子分: 路地で棍棒を担ぎ、腕を張る
        light=dict(pool=(108, 88), radius=(140, 100), fall=1.2, halo=(26, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag', bw=16, bh=8)),
        items=[
            ('lantern', dict(x=28, y=44, hang=0)),
            ('barrel', dict(x=196, base=132, r=15, h=38, gain=0.75)),
            ('figure', dict(x=108, foot=154, h=116, arms=('hip', 'lift'), legs='stride', tunic='leather', head='cap', head_ramp='cloth',
                            legs_ramp='cloth', apron=None, props=[(1, 'club', True)])),
        ]),
    'nightwatch': dict(  # 夜回り: 竿の先に提灯を下げ、寝静まった町を回る
        light=dict(pool=(108, 80), radius=(150, 100), fall=1.1, halo=(150, 46, 40, 0.6)),
        env=('night', dict(hz=126, moon=None, ground_ramp='stone', ground_gain=0.65, wave=0.3, stars=40)),
        items=[
            ('house', dict(x=0, base=124, w=50, h=40, roof_h=26, roof='wood', gain=0.5, windows=[(10, 10, 8, 9, False), (30, 10, 8, 9, False)])),
            ('house', dict(x=170, base=124, w=50, h=38, roof_h=24, roof='red', gain=0.45, windows=[(10, 10, 8, 9, False)])),
            ('figure', dict(x=100, foot=152, h=112, facing=-1, arms=('belly', 'lift'), legs='stride', tunic='cloth', cloak='green', head='hat', head_ramp='cloth',
                            legs_ramp='cloth', props=[(1, ('staff', dict(deg=-60, length=3.2, top='lantern', below=1.6)), True), (0, 'bell', True)])),
        ]),
    'jailer': dict(  # 牢番: 鉄格子の前で鍵束を下げる
        light=dict(pool=(104, 90), radius=(140, 100), fall=1.2, halo=(18, 40, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag', bw=14, bh=8)),
        items=[
            ('torch', dict(x=16, y=40)),
            ('cell_bars', dict(x0=140, x1=220, top=20, base=122)),
            ('figure', dict(x=96, foot=154, h=114, arms=('hip', 'present'), tunic='red', armor=True, head='helm', cloak='cloth', legs_ramp='cloth',
                            props=[(1, 'held_keys', True)])),
            ('skull', dict(x=196, y=114, s=0.8)),
        ]),
    'aristocrat': dict(  # 貴人: 舞踏の間で扇を持つ、宝冠の婦人
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.1, halo=(112, 20, 50, 0.6)),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[
            ('chandelier', dict(x=112, y=16, r=30, chain_top=0)),
            ('column', dict(x=24, top=0, base=136, r=9, gain=0.85)), ('column', dict(x=200, top=0, base=136, r=9, gain=0.7)),
            ('figure', dict(x=112, foot=154, h=112, arms=('lift', 'belly'), robe=True, gown=True, tunic='blue', trim='gold', head='tiara', hair='hair',
                            props=[(0, ('fan', dict(ramp='red')), True)])),
            ('necklace_on', dict(x=112, y=70)),
        ]),
    'tinker': dict(  # 鋳物師: 膝をつき、銅の鍋を槌で叩いて直す
        light=dict(pool=(104, 96), radius=(150, 100), fall=1.15, halo=(30, 44, 40, 0.7)),
        env=('room', dict(wall='plank', hz=118, floor='planks')),
        items=[
            ('lantern', dict(x=28, y=44, hang=0)),
            ('pots', dict(x=150, base=154, n=3)),
            ('figure', dict(x=86, foot=152, h=106, arms=('present', 'raise'), legs='kneel', tunic='blue', apron='leather', head='cap', head_ramp='leather',
                            legs_ramp='cloth', props=[(0, ('pot', {}), True), (1, ('hammer', dict(deg=-50, length=2.0)), True)])),
            ('stack', dict(cx=196, base=126, r=8, n=4, metal='copper', stamp='pip', seed=13)),
        ]),
    'surveyor': dict(  # 測量士: 丘の上に器械の三脚を立て、目盛り竿を持つ
        light=dict(pool=(104, 84), radius=(160, 105), fall=1.05, halo=(30, 22, 40, 0.7)),
        env=('night', dict(hz=124, moon=(30, 22, 10, 0.2), hills=[(100, 16, 0.45, 0.65, 7), (112, 10, 0.55, 0.45, 2)], ground_gain=0.7)),
        items=[
            ('far_lights', dict(pts=[(170, 108), (186, 112), (40, 114)])),
            ('figure', dict(x=78, foot=152, h=112, arms=('down', 'lift'), tunic='green', cloak='leather', head='hat', head_ramp='leather',
                            legs_ramp='cloth', props=[(1, 'rod', False)])),
            ('tripod', dict(x=158, base=152, h=48)),
        ]),
    'wrecker': dict(  # 壊し屋: 大槌を振るい、石壁を打ち抜く
        light=dict(pool=(108, 88), radius=(150, 100), fall=1.1, halo=(30, 22, 40, 0.6)),
        env=('night', dict(hz=128, moon=(30, 22, 9, 0.5), ground_ramp='stone', ground_gain=0.7, wave=0.5)),
        items=[
            ('broken_wall', dict(x0=120, x1=224, base=134, top=36)),
            ('figure', dict(x=76, foot=152, h=112, arms=('overhead', 'overhead'), legs='stride', tunic='red', head='cap', head_ramp='cloth',
                            legs_ramp='leather', props=[(1, ('hammer', dict(deg=-20, length=3.2, big=True)), True)])),
            ('rubble', dict(x=150, base=152, n=10, seed=4)),
        ]),
}
