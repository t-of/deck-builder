"""錬金術（cards-alchemy.js）の 13 枚の場面データ。書き方は scenes.py の冒頭を見る。"""

WARM = dict(fall=1.1, amb=0.07, flat=0.46)

SCENES = {
    'potion': dict(  # 霊薬: 栓をした大瓶に、青く光る薬
        light=dict(pool=(112, 96), radius=(150, 100), halo=(28, 44, 40, 0.5), **WARM),
        env=('room', dict(wall='stone', hz=100, floor='table')),
        items=[('candle', dict(x=28, base=98, h=12, r=3)), ('big_potion', dict(x=112, base=146, ramp='blue')),
               ('bottle', dict(x=60, base=146, h=16, r=5, ramp='green')), ('bottle', dict(x=166, base=148, h=12, r=5, ramp='purple'))]),
    'transform': dict(  # 転化: 光る陣の上で、鉛の杯が金に変わる
        light=dict(pool=(112, 104), radius=(150, 100), fall=1.15, halo=(112, 130, 50, 0.5)),
        env=('room', dict(wall='stone', hz=96, floor='flag')),
        items=[('rune_circle', dict(x=112, y=132, rx=90, ry=22, ramp='gold')), ('half_gold_goblet', dict(x=112, base=134, s=3.0)),
               ('wisps', dict(pts=[(170, 70), (60, 80)]))]),
    'vinerack': dict(  # ぶどう棚: 夜明けの丘の棚に実る紫の房
        light=dict(pool=(112, 90), radius=(170, 110), fall=1.0, flat=0.45),
        env=('night', dict(hz=118, moon=None, sky_ramp='dawn', stars=0, hills=[(100, 14, 0.5, 0.6, 4)], ground_gain=0.7)),
        items=[('trellis', dict(x0=20, x1=204, top=56, base=146)), ('basket', dict(x=60, base=154, w=36, h=12, kind='apple', fill='purple', n=8))]),
    'herbpicker': dict(  # 草摘み: 夜明けの野で、かごに薬草を摘む
        light=dict(pool=(104, 90), radius=(170, 110), fall=1.0, flat=0.45),
        env=('night', dict(hz=118, moon=None, sky_ramp='dawn', stars=0, hills=[(100, 12, 0.5, 0.6, 6)], ground_gain=0.75)),
        items=[
            ('flowers', dict(rows=[(126, 3.0, 22), (150, 5.0, 30)])),
            ('figure', dict(x=104, foot=154, h=110, arms=('reach', 'present'), lean=0.08, robe=True, gown=True, tunic='green', head='long', hair='leather',
                            props=[(1, ('basket_held', {}), True)])),
        ]),
    'druggist': dict(  # 調薬師: 薬棚の前で、乳鉢で薬をすり潰す
        light=dict(pool=(108, 92), radius=(150, 100), halo=(28, 52, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=112, floor='planks')),
        items=[
            ('shelf', dict(x0=120, x1=220, y=34)), ('bottles_row', dict(x0=124, x1=216, base=34, seed=3)),
            ('shelf', dict(x0=120, x1=220, y=68)), ('bottles_row', dict(x0=124, x1=216, base=68, seed=4)),
            ('candle', dict(x=28, base=106, h=12, r=3)),
            ('figure', dict(x=90, foot=170, h=118, arms=('present', 'present'), lean=0.1, robe=True, tunic='blue', mantle='leather', head='coif', head_ramp='paper')),
            ('table', dict(x0=14, x1=210, top=124, legs_to=160, front=True)),
            ('mortar', dict(x=96, base=126, r=16)),
            ('bottle', dict(x=150, base=124, h=14, r=5, ramp='red')),
        ]),
    'mirrorpool': dict(  # のぞき水鏡: 廃墟の水盤の水面に、こちらを見る目
        light=dict(pool=(112, 100), radius=(150, 100), fall=1.15, halo=(112, 110, 60, 0.4)),
        env=('night', dict(hz=118, moon=None, stars=30, ground_ramp='stone', ground_gain=0.6, hills=[(100, 10, 0.4, 0.7, 3)])),
        items=[('column', dict(x=30, top=30, base=126, r=9, gain=0.7)), ('column', dict(x=194, top=50, base=126, r=9, gain=0.6)),
               ('scrying_pool', dict(x=112, y=124, rx=70, ry=18)), ('wisps', dict(pts=[(150, 60), (80, 70)]))]),
    'academy': dict(  # 学び舎: 石板の図、地球儀、砂時計、本の山
        light=dict(pool=(112, 92), radius=(150, 100), halo=(18, 40, 40, 0.6), **WARM),
        env=('room', dict(wall='stone', hz=116, floor='planks')),
        items=[
            ('torch', dict(x=16, y=40)),
            ('slate', dict(x=124, y=52, w=96, h=56)),
            ('table', dict(x0=30, x1=200, top=118, legs_to=158)),
            ('globe', dict(x=60, base=118, r=16)), ('hourglass', dict(x=170, base=118, h=34)),
            ('book', dict(x=96, y=114, w=36, h=4, t=10, ramp='red')), ('book', dict(x=100, y=106, w=28, h=4, t=8, ramp='blue')),
        ]),
    'adept': dict(  # 術士: 緑に光るフラスコを掲げる、ひげの錬金術師
        light=dict(pool=(104, 84), radius=(150, 100), fall=1.15, halo=(62, 36, 40, 0.7)),
        env=('room', dict(wall='stone', hz=122, floor='flag')),
        items=[
            ('shelf', dict(x0=150, x1=220, y=50)), ('bottles_row', dict(x0=154, x1=216, base=50, seed=5)),
            ('figure', dict(x=108, foot=154, h=112, arms=('lift', 'belly'), robe=True, tunic='purple', trim='gold', mantle='blue', head='hair', hair='paper',
                            beard='paper', props=[(0, ('held_flask', dict(ramp='green')), True)])),
            ('burner', dict(x=180, base=150)),
        ]),
    'blackcat': dict(  # 使い猫: 月夜の屋根で金の目を光らせる黒猫と紫の煙
        light=dict(pool=(124, 92), radius=(150, 100), fall=1.1, halo=(60, 42, 40, 0.6)),
        env=('night', dict(hz=170, moon=(60, 42, 22), stars=40, ground_ramp=None, sky_ramp='purple', clouds=())),
        items=[('roof_ridge', dict(y=132)), ('cat', dict(x=140, base=134, s=2.0)), ('wisps', dict(pts=[(200, 50), (196, 100)])),
               ('chimney', dict(x=30, base=134))]),
    'arcanestone': dict(  # 秘石: 石の台から伸びる、光る結晶の束
        light=dict(pool=(112, 96), radius=(150, 100), fall=1.15),
        env=('cave', dict(hz=130, seed=13)),
        items=[('crystal_cluster', dict(x=112, base=146, s=1.6, ramp='blue')), ('gems', dict(pts=[(46, 148, 4, 'blue'), (184, 150, 3, 'purple')]))]),
    'clayman': dict(  # 土人形: 胸の文字が光る、土でこねた大きな人形
        light=dict(pool=(108, 84), radius=(150, 100), fall=1.1, halo=(20, 40, 40, 0.6)),
        env=('cave', dict(hz=128, seed=17)),
        items=[('torch', dict(x=18, y=40)),
               ('figure', dict(x=112, foot=154, h=124, arms=('down', 'forward'), legs='stride', tunic='leather', legs_ramp='leather', skin='leather', head='hair', hair='leather',
                               belt=None, boots='leather')),
               ('rune_mark', dict(x=112, y=86))]),
    'pupil': dict(  # 内弟子: 蝋燭のそばで本を抱えて学ぶ少年
        light=dict(pool=(104, 92), radius=(150, 100), halo=(36, 74, 40, 0.6), **WARM),
        env=('room', dict(wall='plank', hz=120, floor='planks')),
        items=[
            ('shelf', dict(x0=130, x1=222, y=40)), ('books_row', dict(x0=134, x1=218, base=40, seed=14)),
            ('candle', dict(x=40, base=112, h=12, r=3)), ('shelf', dict(x0=20, x1=60, y=112)),
            ('figure', dict(x=110, foot=154, h=94, arms=('chest', 'chest'), tunic='green', head='hair', legs_ramp='cloth',
                            props=[(1, ('book', dict(open_=True, w=1.6, h=1.3)), True)])),
            ('book', dict(x=150, y=150, w=30, h=4, t=10, ramp='red')),
        ]),
    'takeover': dict(  # 乗っ取り: 上から伸びる手が、糸で人形を操る
        light=dict(pool=(112, 84), radius=(150, 105), fall=1.1),
        env=('room', dict(wall='stone', hz=140, floor='flag')),
        items=[('marionette', dict(x=112, top=60, base=136))]),
}
