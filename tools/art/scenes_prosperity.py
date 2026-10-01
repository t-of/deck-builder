"""繁栄（cards-prosperity.js）の 36 枚の場面データ。書き方は scenes.py の冒頭を見る。
夜ばかりにならないよう、夜明け（dawn）・室内の暖かい灯・炉・雪を散らしている。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)  # 室内の暖かい灯（光だまりを広く明るく）

SCENES = {
    # ================= 財宝・勝利点 =================
    'platinum': dict(  # 白金: 天鵞絨の箱に並ぶ大きな白金貨、星の刻印
        light=dict(pool=(112, 100), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=74, floor='table')),
        items=[
            ('candelabra', dict(x=26, base=72, h=26)),
            ('velvet_case', dict(x=112, y=124, w=170, h=56, ramp='blue')),
            ('stack', dict(cx=62, base=134, r=15, n=6, metal='silver', stamp='star', seed=31)),
            ('stack', dict(cx=106, base=130, r=15, n=9, metal='silver', stamp='star', seed=32)),
            ('stack', dict(cx=150, base=136, r=15, n=5, metal='silver', stamp='star', seed=33)),
            ('coin', dict(cx=190, cy=144, r=15, metal='silver', stamp='crown', tilt=0.6)),
            ('gems', dict(pts=[(34, 148, 5, 'blue'), (82, 152, 4, 'purple')])),
        ]),
    'colony': dict(  # 新天地: 夜明けの海辺に広がる新しい都、港の船
        light=dict(pool=(112, 80), radius=(180, 120), fall=0.95, flat=0.45),
        env=('coast', dict(hz=104, moon=None, sky_ramp='dawn', stars=0, clouds=((30, 100, 8), (54, 80, 6)), sea_gain=1.2)),
        items=[
            ('skyline', dict(x0=8, x1=216, base=104, gain=0.7, seed=4, dep=0.2)),
            ('palace', dict(x=112, base=100, w=110, h=40, gain=0.9)),
            ('ship', dict(x=40, wl=126, s=0.35, gain=0.85)),
            ('ship', dict(x=190, wl=130, s=0.4, gain=0.9, flag='blue')),
            ('foam', dict(x0=0, x1=224, y=106)),
        ]),
    'anvil': dict(  # 打ち台: 金床の上で金貨を打つ（炉の照り返し）
        light=dict(pool=(112, 96), radius=(150, 100), halo=(16, 70, 50, 0.8), fall=1.1, key=0.8),
        env=('room', dict(wall='stone', hz=112, floor='flag', bw=14, bh=8)),
        items=[
            ('forge', dict(x=-20, y=48, w=50, h=50)),
            ('anvil', dict(x=118, base=148, s=1.9)),
            ('coin', dict(cx=104, cy=96, r=11, metal='gold', stamp='crown')),
            ('hammer_rest', dict(x=148, y=88)),
            ('stack', dict(cx=196, base=152, r=10, n=5, metal='gold', seed=34)),
            ('sparks', dict(pts=[(96, 84), (110, 78), (90, 90), (120, 72), (100, 70)])),
        ]),
    'stoneyard': dict(  # 石工場: 夕暮れの石置き場、切り石と彫りかけの柱
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.0, flat=0.45),
        env=('night', dict(hz=124, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.8, wave=0.6)),
        items=[
            ('crane', dict(x=150, top=20, hook=(146, 56))),
            ('scaffold', dict(x0=120, x1=176, top=20, base=128)),
            ('block', dict(x=132, y=58, w=24, h=14)),
            ('column', dict(x=70, top=40, base=136, r=10)),
            ('block', dict(x=10, y=128, w=36, h=20)), ('block', dict(x=20, y=110, w=24, h=18, gain=1.05)),
            ('block', dict(x=160, y=136, w=40, h=20, gain=0.9)),
            ('stack', dict(cx=104, base=150, r=9, n=3, metal='copper', stamp='pip', seed=35)),
        ]),
    'stake': dict(  # 種銭: 鉢の土に埋めた銭から、金の芽が出る
        light=dict(pool=(112, 100), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=104, floor='table')),
        items=[('candle', dict(x=28, base=100, h=12, r=3)), ('sprout_pot', dict(x=112, base=148)),
               ('coin', dict(cx=56, cy=146, r=8, metal='copper', stamp='pip')), ('coin', dict(cx=170, cy=150, r=8, metal='copper', stamp='star'))]),
    'diadem': dict(  # 髪飾り: 房の座布団に載せた宝石の髪飾り
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 40, 40, 0.5), **WARM),
        env=('icon', dict(hz=82, wall='stone', cloth='purple', cloth_gain=0.55)),
        items=[('candle', dict(x=28, base=80, h=12, r=3)), ('cushion', dict(x=112, y=124, w=110, ramp='red')), ('diadem', dict(x=112, y=104, w=80))]),
    'curio': dict(  # 蒐集箱: 髑髏・貝・剥製・地球儀の並ぶ棚
        light=dict(pool=(112, 84), radius=(150, 105), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=140, floor='planks')),
        items=[('torch', dict(x=14, y=40)), ('curio_shelf', dict(x0=36, x1=200, top=14, base=126))]),
    'orb': dict(  # 占い玉: 金の台座の水晶に、渦の幻が光る
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('icon', dict(hz=118, wall='stone', cloth='purple', cloth_gain=0.6)),
        items=[('crystal_ball', dict(x=112, base=136, r=36, ramp='blue')), ('playing_cards', dict(x=150, y=134))]),
    'warfund': dict(  # 軍資金: 金のあふれる箱に、交差した剣と軍旗
        light=dict(pool=(112, 100), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=110, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('war_chest', dict(x=112, base=148))]),
    'stash': dict(  # 隠し銭: 壁の抜き石の穴に隠した金貨
        light=dict(pool=(112, 84), radius=(140, 100), fall=1.2, halo=(30, 120, 34, 0.6)),
        env=('room', dict(wall='stone', hz=132, floor='planks', bw=24, bh=12)),
        items=[('loose_brick', dict(x=104, y=70, s=2.0)), ('candle', dict(x=34, base=150, h=10, r=3))]),
    'banker': dict(  # 金融屋: 帳場の卓に積んだ硬貨、算盤、帳簿
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 60, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=88, floor='table')),
        items=[
            ('candelabra', dict(x=30, base=86, h=24)),
            ('book', dict(x=36, y=128, w=40, h=4, t=12, ramp='red')),
            ('abacus', dict(x=168, y=104, w=70, h=34)),
            ('stack', dict(cx=96, base=140, r=12, n=7, metal='gold', seed=36)),
            ('stack', dict(cx=126, base=146, r=12, n=5, metal='silver', stamp='tower', seed=37)),
            ('stack', dict(cx=154, base=150, r=12, n=3, metal='copper', stamp='pip', seed=38)),
            ('coin', dict(cx=190, cy=150, r=11, metal='gold', stamp='star')),
        ]),
    'iou': dict(  # 借用書: 署名と封蝋の証文、上に銅貨
        light=dict(pool=(112, 100), radius=(150, 100), halo=(28, 44, 40, 0.6), **WARM),
        env=('icon', dict(hz=60, wall='plank', cloth='wood', cloth_gain=0.75)),
        items=[('candle', dict(x=26, base=58, h=12, r=3)), ('doc', dict(x=112, y=110, w=130, h=78)),
               ('quill_flat', dict(x=170, y=96)), ('coin', dict(cx=78, cy=104, r=9, metal='copper', stamp='pip'))]),
    'charm': dict(  # お守り: 紐で下げた金の札、翠玉が淡く光る
        light=dict(pool=(112, 86), radius=(150, 100), fall=1.15),
        env=('room', dict(wall='plank', hz=150, floor='planks')),
        items=[('amulet', dict(x=112, y=80, r=28))]),
    'forbidden': dict(  # ご禁制: 鎖で縛り、封をした禁制の箱
        light=dict(pool=(112, 98), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=110, floor='flag')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('chest', dict(x=60, base=148, w=104, h=46, open_=False, band='silver')),
            ('chain', dict(x0=56, y0=104, x1=172, y1=150, r=3.5)),
            ('chain', dict(x0=56, y0=150, x1=172, y1=104, r=3.5)),
            ('seal_on', dict(x=112, y=128)),
        ]),
    'seal': dict(  # 御印: 赤い封蝋と金の柄の印章
        light=dict(pool=(112, 100), radius=(150, 100), halo=(28, 44, 40, 0.6), **WARM),
        env=('icon', dict(hz=66, wall='stone', cloth='wood', cloth_gain=0.75)),
        items=[('candle', dict(x=26, base=64, h=12, r=3)), ('doc', dict(x=100, y=116, w=150, h=70, seal=False, lines=5, sign=False)),
               ('wax_seal', dict(x=96, y=120, r=24))]),
    'gamble': dict(  # 山っ気: 卓の上の骰子と札と賭け金
        light=dict(pool=(112, 104), radius=(150, 100), halo=(40, 30, 50, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=84, floor='table', floor_ramp='green', floor_gain=0.7)),
        items=[
            ('lantern', dict(x=40, y=40, hang=0)),
            ('dice', dict(x=80, y=110, s=24, pips=6)), ('dice', dict(x=118, y=124, s=20, pips=1)),
            ('playing_cards', dict(x=146, y=96)),
            ('stack', dict(cx=50, base=146, r=10, n=4, metal='gold', seed=39)), ('coin', dict(cx=176, cy=144, r=9, metal='silver', stamp='tower')),
        ]),
    'stele': dict(  # 石碑: 夜明けの丘に立つ、文字を刻んだ石
        light=dict(pool=(112, 86), radius=(170, 110), fall=1.0, flat=0.45),
        env=('night', dict(hz=128, moon=None, sky_ramp='dawn', stars=0, hills=[(110, 16, 0.5, 0.6, 3)], ground_gain=0.7)),
        items=[('stele', dict(x=112, base=146, w=44, h=104)), ('flower', dict(x=70, y=146, r=4, ramp='gold')), ('flower', dict(x=156, y=150, r=4, ramp='red'))]),
    # ================= 物と場所 =================
    'firetower': dict(  # 火の見やぐら: 雪の夜、鐘を吊った高い櫓
        light=dict(pool=(112, 80), radius=(160, 110), fall=1.05, halo=(120, 30, 40, 0.5)),
        env=('night', dict(hz=130, moon=None, ground_ramp=None, stars=10, clouds=((24, 90, 9), (44, 100, 8)))),
        items=[
            ('house', dict(x=0, base=136, w=50, h=30, roof_h=22, roof='wood', gain=0.6, windows=[(10, 8, 8, 9, True)])),
            ('house', dict(x=172, base=138, w=52, h=30, roof_h=22, roof='red', gain=0.55, windows=[(30, 8, 8, 9, True)])),
            ('snow_cap', dict(x0=0, x1=50, y=114)),
            ('headframe', dict(x=112, base=140, h=100)),
            ('bell_hang', dict(x=112, y=46)),
            ('snow_ground', dict(y0=136)),
            ('snow', dict(n=90, seed=1)),
        ]),
    'castletown': dict(  # 城下町: 丘の城の下にひしめく家並み（夜明け）
        light=dict(pool=(112, 100), radius=(180, 110), fall=0.95, flat=0.44),
        env=('night', dict(hz=120, moon=None, sky_ramp='dawn', stars=0, ground_ramp='stone', ground_gain=0.7, hills=[(76, 18, 0.7, 0.3, 2)])),
        items=[
            ('castle', dict(x=112, base=70, s=0.8, roof='red')),
            ('house', dict(x=0, base=126, w=46, h=30, roof_h=22, roof='red', windows=[(8, 8, 8, 9, True)])),
            ('house', dict(x=46, base=132, w=40, h=34, roof_h=22, roof='wood', windows=[(8, 8, 8, 9, True), (24, 8, 8, 9, False)])),
            ('house', dict(x=136, base=130, w=42, h=32, roof_h=22, roof='red', windows=[(8, 8, 8, 9, True)])),
            ('house', dict(x=180, base=126, w=44, h=30, roof_h=22, roof='wood', gain=0.9, windows=[(10, 8, 8, 9, True)])),
            ('well', dict(x=108, base=150, r=13)),
        ]),
    'artisanrow': dict(  # 職人町: 吊り看板の並ぶ職人の通り
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.0, halo=(40, 70, 40, 0.5)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.3)),
        items=[
            ('house', dict(x=-4, base=132, w=64, h=70, roof_h=24, roof='red', windows=[(10, 12, 9, 10, True), (40, 12, 9, 10, True)], door=(22, 14, 22))),
            ('house', dict(x=66, base=132, w=60, h=64, roof_h=22, roof='wood', gain=0.9, windows=[(10, 12, 9, 10, True), (38, 12, 9, 10, False)], door=(22, 14, 22))),
            ('house', dict(x=136, base=132, w=60, h=70, roof_h=24, roof='red', gain=0.8, windows=[(10, 12, 9, 10, True)], door=(30, 14, 22))),
            ('sign', dict(x=40, y=72, w=24, h=16, emblem='coin')), ('sign', dict(x=112, y=74, w=24, h=16, emblem='scale')),
            ('sign', dict(x=184, y=70, w=24, h=16, emblem='coin')),
            ('lamp_post', dict(x=60, base=150, h=60)),
        ]),
    'coinery': dict(  # 鋳貨所: ねじの打ち出し機で金貨を打つ
        light=dict(pool=(104, 96), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=128, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('screw_press', dict(x=112, base=148)),
               ('stack', dict(cx=188, base=152, r=10, n=7, metal='gold', seed=40)), ('stack', dict(cx=34, base=152, r=10, n=4, metal='gold', stamp='star', seed=41))]),
    'safebox': dict(  # 貸し金庫: 錠のある小引き出しの壁、ひとつ開いて金
        light=dict(pool=(112, 82), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=124, floor='flag')),
        items=[('torch', dict(x=16, y=40)), ('drawers', dict(x0=46, y0=14, cols=6, rows=6, w=22, h=18, open_at=(2, 3)))]),
    'boulevard': dict(  # 大通り: 夕暮れに街灯がともる、奥へ続く広い通り
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.0, flat=0.42),
        env=('night', dict(hz=92, moon=None, sky_ramp='dawn', stars=0, ground_ramp=None)),
        items=[
            ('road', dict(x=112, top=92, base=160, w0=12, w1=200)),
            ('house', dict(x=-30, base=150, w=70, h=90, roof_h=20, roof='blue', windows=[(14, 14, 10, 12, True), (44, 14, 10, 12, True), (14, 48, 10, 12, True)])),
            ('house', dict(x=44, base=112, w=30, h=40, roof_h=12, roof='blue', gain=0.7, windows=[(8, 8, 6, 8, True)])),
            ('house', dict(x=150, base=112, w=30, h=40, roof_h=12, roof='blue', gain=0.6, windows=[(14, 8, 6, 8, True)])),
            ('house', dict(x=180, base=150, w=70, h=90, roof_h=20, roof='blue', gain=0.75, windows=[(14, 14, 10, 12, True), (14, 48, 10, 12, True)])),
            ('lamp_post', dict(x=80, base=118, h=40)), ('lamp_post', dict(x=60, base=140, h=64)),
            ('lamp_post', dict(x=150, base=118, h=40)),
        ]),
    'extension': dict(  # 建て増し: 家の横に、木組みの新しい棟を建てる
        light=dict(pool=(112, 96), radius=(170, 105), fall=1.0, flat=0.44),
        env=('night', dict(hz=128, moon=None, sky_ramp='dawn', stars=0, ground_gain=0.7)),
        items=[
            ('house', dict(x=10, base=134, w=80, h=50, roof_h=34, roof='red', windows=[(12, 12, 10, 12, True), (52, 12, 10, 12, True)], door=(32, 14, 22))),
            ('frame', dict(x0=108, x1=196, base=134, h=50)),
            ('scaffold', dict(x0=110, x1=196, top=60, base=136)),
            ('plank', dict(x0=120, y0=148, x1=200, y1=144, w=3)), ('plank', dict(x0=126, y0=154, x1=206, y1=150, w=3)),
        ]),
    'crucible': dict(  # るつぼ: 炉の中の坩堝に、杯や硬貨を投げ入れて溶かす
        light=dict(pool=(112, 100), radius=(150, 100), halo=(60, 96, 60, 0.9), fall=1.1, key=0.8),
        env=('room', dict(wall='stone', hz=126, floor='flag', bw=14, bh=8)),
        items=[
            ('forge', dict(x=40, y=60, w=120, h=66)),
            ('melting_pot', dict(x=100, y=104)),
            ('goblet', dict(x=170, base=146, s=1.4)), ('coin', dict(cx=190, cy=150, r=7, metal='silver', stamp='tower')),
            ('falling', dict(x=104, y=64)),
        ]),
    'traderoute': dict(  # 通商路: 夜明けの街道、道しるべと遠くの荷馬車
        light=dict(pool=(112, 96), radius=(170, 110), fall=1.0, flat=0.44),
        env=('night', dict(hz=104, moon=None, sky_ramp='dawn', stars=0, hills=[(96, 12, 0.5, 0.6, 5)], ground_gain=0.7)),
        items=[
            ('road', dict(x=124, top=104, base=160, w0=8, w1=150, ramp='sand')),
            ('wagon', dict(x=134, base=110, w=30)),
            ('signpost', dict(x=52, base=150)),
            ('tree', dict(x=196, base=130, h=60, kind='oak', gain=0.7, seed=31)),
        ]),
    'tally': dict(  # 勘定場: 刻み木の束、銅貨の山、帳面
        light=dict(pool=(112, 104), radius=(150, 100), halo=(28, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=90, floor='table')),
        items=[('candle', dict(x=28, base=88, h=12, r=3)), ('tally_sticks', dict(x=70, y=120)),
               ('pile', dict(cx=150, base=150, w=44, h=22, metal='copper', r=9, count=16, seed=4, stamps=('pip', 'star'))),
               ('book', dict(x=150, y=110, w=40, h=3, t=10, ramp='green'))]),
    # ================= 人物 =================
    'prelate': dict(  # 高僧: 色硝子の窓の前で、牧杖と冠
        light=dict(pool=(108, 84), radius=(150, 100), halo=(40, 30, 40, 0.7), **WARM),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[
            ('window_arch', dict(x=24, y=6, w=34, h=66)),
            ('window_arch', dict(x=168, y=6, w=34, h=66)),
            ('figure', dict(x=108, foot=154, h=112, arms=('chest', 'low'), robe=True, tunic='paper', trim='gold', mantle='red', head='mitre', head_ramp='paper',
                            beard='paper', props=[(1, ('crook_staff', {}), False)])),
        ]),
    'scribe': dict(  # 書役: 書き机で羽根ペンを走らせる
        light=dict(pool=(108, 96), radius=(150, 100), halo=(30, 56, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=110, floor='planks')),
        items=[
            ('shelf', dict(x0=140, x1=220, y=40)), ('books_row', dict(x0=144, x1=216, base=40, seed=11)),
            ('candle', dict(x=32, base=104, h=12, r=3, holder=True)),
            ('figure', dict(x=110, foot=170, h=118, arms=('belly', 'present'), lean=0.1, tunic='green', head='cap', head_ramp='red',
                            props=[(1, 'quill', True)])),
            ('table', dict(x0=20, x1=206, top=124, legs_to=160, front=True)),
            ('doc', dict(x=118, y=128, w=70, h=16, seal=False, lines=2, sign=False)),
            ('bottle', dict(x=170, base=124, h=10, r=4, ramp='blue')),
        ]),
    'mob': dict(  # 群衆: 松明と熊手を掲げて押し寄せる人々
        light=dict(pool=(112, 84), radius=(160, 110), fall=1.05, halo=(50, 40, 50, 0.6)),
        env=('night', dict(hz=128, moon=None, ground_ramp='stone', ground_gain=0.65, wave=0.3)),
        items=[
            ('house', dict(x=150, base=126, w=60, h=40, roof_h=24, roof='wood', gain=0.5, windows=[(10, 10, 8, 9, True)])),
            ('figure', dict(x=40, foot=146, h=96, arms=('down', 'raise'), tunic='leather', head='cap', head_ramp='cloth', legs_ramp='cloth', props=[(1, 'torch_held', True)])),
            ('figure', dict(x=172, foot=146, h=96, facing=-1, arms=('down', 'raise'), tunic='green', head='hair', legs_ramp='cloth', props=[(1, 'pitchfork', True)])),
            ('figure', dict(x=108, foot=156, h=110, arms=('forward', 'raise'), legs='stride', tunic='red', head='cap', head_ramp='leather', legs_ramp='cloth',
                            props=[(1, 'torch_held', True)])),
        ]),
    'charlatan': dict(  # まやかし師: 宙に浮かぶ硬貨と紫の煙で客をだます
        light=dict(pool=(108, 88), radius=(150, 100), fall=1.1, halo=(40, 50, 40, 0.5)),
        env=('room', dict(wall='plank', hz=122, floor='planks')),
        items=[
            ('wisps', dict(pts=[(150, 50), (60, 70)])),
            ('figure', dict(x=108, foot=154, h=112, arms=('lift', 'lift'), tunic='purple', cloak='red', head='tophat', head_ramp='cloth', legs_ramp='cloth')),
            ('floating_coins', dict(x=108, y=26)),
        ]),
    'tycoon': dict(  # 大旦那: 金の鎖をかけ、金袋を手に宝箱の脇に立つ
        light=dict(pool=(104, 88), radius=(150, 100), halo=(26, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[
            ('candelabra', dict(x=26, base=76, h=26)), ('shelf', dict(x0=8, x1=46, y=76)),
            ('hang_banner', dict(x=176, top=0, w=28, h=60, ramp='purple', kind='circle')),
            ('figure', dict(x=96, foot=154, h=112, arms=('belly', 'present'), robe=True, tunic='purple', trim='gold', mantle='gold', head='tophat', head_ramp='cloth',
                            beard='hair', props=[(1, ('bag', dict(ramp='gold')), True)])),
            ('chest', dict(x=150, base=154, w=56, h=26, fill='gold')),
        ]),
    'council': dict(  # 御前会議: 玉座の前の円卓に、重臣が居並ぶ
        light=dict(pool=(112, 84), radius=(160, 105), halo=(112, 22, 40, 0.5), **WARM),
        env=('room', dict(wall='stone', hz=118, floor='flag')),
        items=[
            ('chandelier', dict(x=112, y=16, r=26, chain_top=0)),
            ('throne', dict(x=112, base=112)),
            ('figure', dict(x=54, foot=150, h=96, arms=('present', 'chest'), robe=True, tunic='blue', head='hat', head_ramp='cloth')),
            ('figure', dict(x=170, foot=150, h=96, facing=-1, arms=('present', 'chest'), robe=True, tunic='green', head='coif', head_ramp='green', beard='paper')),
            ('round_table', dict(x=112, y=130, rx=100, ry=18, cloth='red')),
            ('held_map_flat', dict(x=112, y=130)),
        ]),
    'hawker': dict(  # 呼び売り: 首から売り台を下げ、声を張り上げる
        light=dict(pool=(108, 88), radius=(150, 105), halo=(40, 60, 40, 0.6), fall=1.1),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.7, wave=0.3, sky_ramp='dawn', stars=0)),
        items=[
            ('house', dict(x=150, base=122, w=60, h=40, roof_h=24, roof='red', gain=0.7, windows=[(10, 10, 8, 9, True)])),
            ('figure', dict(x=100, foot=154, h=112, arms=('belly', 'raise'), legs='stride', tunic='red', trim='gold', head='feather', head_ramp='green',
                            legs_ramp='blue', props=[(0, ('tray_strap', {}), True), (1, ('held_bottle', dict(ramp='green')), True)])),
        ]),
    'quack': dict(  # いかさま薬売り: 荷車の薬瓶を掲げ、効き目をまくし立てる
        light=dict(pool=(104, 92), radius=(150, 100), fall=1.1, halo=(30, 60, 40, 0.6)),
        env=('night', dict(hz=124, moon=None, ground_ramp='stone', ground_gain=0.65, wave=0.3)),
        items=[
            ('lantern', dict(x=30, y=60, hang=40)),
            ('wagon', dict(x=164, base=150, w=80, cover='purple')),
            ('bottles_row', dict(x0=130, x1=200, base=120, seed=2)),
            ('figure', dict(x=84, foot=154, h=112, arms=('belly', 'raise'), tunic='green', cloak='purple', head='tophat', head_ramp='purple', legs_ramp='cloth',
                            props=[(1, ('held_bottle', dict(ramp='purple')), True)])),
            ('wisps', dict(pts=[(96, 30)])),
        ]),
    'bouncer': dict(  # 用心棒: 酒場の戸口で腕組みして立ちはだかる
        light=dict(pool=(108, 88), radius=(150, 100), halo=(40, 50, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=124, floor='planks')),
        items=[
            ('lantern', dict(x=30, y=46, hang=0)),
            ('doorway', dict(x=168, base=124, w=40, h=76)),
            ('sign', dict(x=168, y=20, w=36, h=16, emblem='coin')),
            ('figure', dict(x=104, foot=154, h=118, arms=((-0.2, 1.0, 1.5, 1.2), (0.2, 1.0, -1.5, 1.1)), tunic='leather', head='hair', legs_ramp='cloth',
                            beard='hair', armor=False)),
            ('barrel', dict(x=36, base=154, r=14, h=34, gain=0.9)),
        ]),
}
