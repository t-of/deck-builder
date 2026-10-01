# カードの絵の決まり（夜の古い城の作戦卓）

deck-builder の `art/*.png` を生成で描くときの決まりと、その作り方。
描いたもの: 基本セット（`cards-base.js` の 39 枚）とルネサンスの「もの」5 枚（`a_*.png`）、陰謀（`cards-intrigue.js` の 32 枚）、海辺（`cards-seaside.js` の 35 枚）、繁栄（`cards-prosperity.js` の 36 枚）、錬金術（`cards-alchemy.js` の 13 枚）、異郷（`cards-hinterlands.js` の 35 枚）、収穫祭＆ギルド（`cards-guilds.js` の 45 枚）、暗黒時代（`cards-darkages.js` の 47 枚。がれき 5 種を含む。騎士 10 人 `k_*` はもとから絵のファイルがない）、冒険（`cards-adventures.js` の 58 枚。イベント 20 を含む）、帝国（`cards-empires.js` の 76 枚。上下 2 種の山 5・城 8・イベント 13・ランドマーク 21 を含む）、夜想曲（`cards-nocturne.js` の 77 枚。恵み 12・呪詛 12・状態 5・家宝 7・精霊などを含む）、ルネサンス（`cards-renaissance.js` の王国 25 とプロジェクト 19。「もの」5 枚は基本セットの中）。残りの拡張は旧版のまま。

```sh
python3 tools/art/build.py                       # 描ける全部を art/ に書く（パレット外の色があれば止まる）
python3 tools/art/build.py --set intrigue        # 1 つの拡張だけ（base は基本セット＋a_*.png）
python3 tools/art/build.py gold crier            # 指定したものだけ
python3 tools/art/build.py --check --set base    # 2 回描いて同じ PNG になるか確かめる（書かない）
python3 tools/art/compare_sheet.py --set intrigue  # 旧絵と並べた見比べを本部の .audit/deck-art-<拡張>-<n>.png に
```

部品を足したら、前に描いた拡張を描き直して `git status art/` で変わっていないことを確かめる（変えるなら意図して）。

python3 の標準と Pillow だけ。乱数は使うときも `random.Random(<カードの id>)` で種を固定し、
ほとんどの揺らぎは座標から決まる `hsh()` で出すので、何度動かしても同じ PNG になる。

## ファイル

| ファイル | 中身 |
|---|---|
| `palette.py` | 36 色と、色の段（ランプ） |
| `engine.py` | 光（`Light`）、画素の器（`Canvas`）、形（楕円・多角形・棒・円柱）、仕上げ（段への丸め・ディザ・輪郭・PNG） |
| `parts_<拡張>.py` | 暗黒時代から先で足した部品（`from parts import ...` で共通の部品を使う）。`PROPS` に持ち物 |
| `parts.py` | 部品: 背景（石壁・板壁・卓・石畳・夜空・丘・森の地面）、灯り、硬貨、建物、木と花、家具・道具、アイコンの主役 |
| `figure.py` | 人物: 姿勢（腕・脚）、胴・腕・頭の立体、服・かぶり物の差し替え、持ち物 |
| `scenes.py` | 基本セットの場面データ、背景の組み立て、拡張の表をまとめる `SETS` |
| `scenes_<拡張>.py` | 拡張ごとの場面データ（データだけ） |
| `build.py` / `compare_sheet.py` | 書き出しと見比べ |

## 大きさと保存

- 論理 224×160 を最近傍で 2 倍し、448×320 のパレット PNG（モード `P`、36 色の PLTE）で保存する。
- 画素ごとに「ランプ」と「明るさ L（0〜1）」を持ち、最後に L をランプの段に丸めて色を決める。だからパレット外の色は出ようがないが、
  書き出すたびに `check_palette()` で全画素を確かめる。

## 色（`palette.py`）

36 色。どの絵も同じ表だけを使う。

- 闇と石: N0〜N7（ほぼ黒の紺 → 灰紫 → 暖かい灰）
- くすんだ金・木・灯り: G0〜G6（焦茶 → 金 → 白金）
- 銅と肌の明部: CU・K2
- 宝石: 紅玉 R0〜R3、蒼玉 B0〜B3、翠玉 E0〜E3、紫水晶 P0〜P3（災い・呪術）
- 銀: S1〜S3

ランプは暗い側から明るい側へ並べ、**暗い側は紺・紫（寒色）、明るい側は金・白金（暖色）** へ色相をずらす。
どのランプも一番下は N0 で、光の届かない所はどの素材も同じ闇に沈む。
宝石のランプ（red/blue/green/purple）の一番上は同じ色相のままにする（布が別の色に見えないように）。照りは決まった点（`Canvas.dot`）で足す。

## 光（`engine.Light`）

- **光は場面に 1 つ、向きはいつも左上から**（`dir`）。明るさ = 環境光 + 光だまり ×（平らな受け + 向きの受け）。
- **光だまり**: `pool`（中心）と `radius`（半径）のぼかした楕円。中心は主役に置き、外へ向かって段を踏んで暗く落ちる。
  見えている灯り（燭台・窓・月・炉・提灯）のまわりは `halo` でさらに明るむ。最後に四隅をなだらかに落とす（`vignette`）。
- 影の側には右下からの反射光を 1 段だけ足す（`bounce`）。金属は照り（`spec`）を持つ。
- 夜ばかりが並ばないよう、夜明けの空（`sky_ramp='dawn'`）、室内の暖かい灯（光だまりを広く明るく）、炉、雪（`snow` `snow_ground`）を散らす。
- 見えている灯りは、いつも画面の左上の側に置く。ただし毎回同じ物にしない（月・三日月・燭台・ランタン・街灯・篝火・炉・窓・松明・提灯を場面ごとに替え、
  外の場面でも月を出さないものがある）。
- 発光する物（炎・窓の灯り・月・光る液）は `emit` で明るさを直接決め、光に左右されない。

## 描き方

- **段**: 人物（服・肌・持ち物）は、光の向きの受けを 3 段に割る（`Canvas.cel = 3`）。明部・中間・影＋反射光の 3〜4 段になる。
  金属・硬貨・建物は形の向きでそのまま段に丸める。
- **ディザ**: 2×2 の市松だけ。使うのは「段の境目の ±`DITHER_BAND` の帯」で、しかも背景（壁・空・地面・卓・水）と煙だけ。
  物には使わない。全体にばらまくノイズはない。
- **輪郭**: 手前の物の縁（奥の物と接する画素）を、その物のランプの暗い段で描く。光の側の縁は 1 段だけ落とし、影の側は闇の 1 つ上（選択輪郭）。真っ黒の線はない。
- **硬貨**: 楕円の面（盛り上がった縁は左上が明るく右下が暗い、内側に溝、真ん中に刻印＝王冠・塔・星・丸）、手前に厚み（銀と金はギザ）、縁に照りの点。
  面の明るさは光から 1 度だけ求め、縁・溝・刻印はそこからの決まった差で描く（小さくても形が崩れない）。
  量で格を出す: 銅は短い山と数枚、銀は 3 本の山と数枚、金は宝箱からあふれる山と 2 本の高い山と宝石。
- **素材の模様**（どれも座標から決まる）: 石は枕の形にふくらみ、いくつかは角が欠け、ひびが入る。板は継ぎ目と木目。卓は奥ほど細い板目。

## 構図

- 主役は 1 つ。中央か三分割の位置に置き、光だまりの中心を主役に合わせる。背景は奥ほど暗く寒く（`depth`）。
- 手札で幅 60px ほどに縮んでも分かるよう、主役は画面の高さの半分以上を使い、明るい側を暗い背景に当てる。
- 人物は 7 頭身、高さ 108〜114（画面 160 のうち）。小姓だけ少年なので低い。

## 人物（`figure.py`）

`figure(c, x, foot, h, facing, arms, legs, ...)` に、姿勢・服・持ち物を渡すだけで描く。

- 腕（`ARMS`）: `down` `hip` `raise` `lift`（頭の高さに掲げる）`forward` `aim` `present` `chest` `belly` `pull` `overhead` `eye` `reach` `low`。
  名前の代わりに (肘 dx, dy, 手 dx, dy) を直接渡してもよい（頭 1 つ分を 1 とする）。
- 脚: `stand` `stride` `kneel` `crouch`。`lean` で前かがみ。`facing=-1` で左右反転（光は左上のまま）。
- かぶり物（ルネサンスで足した）: `eboshi`（神主の立烏帽子）、`topknot`（髷）。
- 服: `tunic`（胴と袖の色）、`robe`（裾の長い衣）、`cloak`（背の外套）、`mantle`（肩掛け）、`apron`、`armor`（胸当て）、`trim`（裾の金の縁）、`belt`。
- かぶり物: `hood` `hat` `cap` `feather` `helm` `coif` `hair` `crown` `mitre`（僧冠）`tophat` `turban` `witch`（三角帽）`jester`（道化の鈴帽子）、覆面 `mask`、ひげ `beard`。
- 顔が主役の絵（王・魔女・隠者など）だけ `face=True` で、目 2 つ・眉の影・鼻の照りと影・口を足す。
- 女性: `gown=True`（細い胴と広がる裾）、かぶり物 `long`（長い髪）・`tiara`。
- 持ち物（手に握らせる）: `staff`（穂先 `spear`・金の玉 `knob`・提灯 `lantern`）`sword` `dagger` `axe` `hammer` `chisel` `bow` `quiver` `book`（開いた帳簿も）`scroll` `bag` `bell` `tray`
  `orb` `held_lantern` `held_coin` `held_map` `spyglass` `shield` `banner` `quill`
  `club` `held_keys` `held_candelabra` `parcel` `letter` `fan` `mask_stick` `pot` `rod`、
  `parts.py` 側の `spade` `cutlass` `cane` `casket` `pearl` `coil_held` `pitchfork` `torch_held` `tray_strap` `held_bottle` `crook_staff`
  `basket_held` `held_flask` `bindle` `held_dividers` `silver_plate` `toolbox` `scythe` `broom` `cleaver` `hunting_horn` `peel` `juggle` `halberd`
  `flowers_held` `lead_rope` `hoof`。
- 動物（`parts.py`）: `horse`（馬。胴は 3 つのふくらみ、脚は膝で曲がる 2 節、`gallop` で駆け足、`blanket` で馬着）、`dog`、`cat`、`raven`、`camel`、`monkey`（手長猿）。船は `ship`（交易船・私掠船・縞帆の略奪船・霧の船）と `boat`。持ち物を描いてから手を重ねるので、握って見える。

## 場面データ（`scenes.py` の `SCENES`）

カードごとに書くのは次の 3 つだけ。描き方（色・光・段・ディザ・輪郭）はすべて共通。

```python
'smithy': dict(
    light=dict(pool=(96, 100), radius=(150, 100), halo=(36, 62, 54, 0.9)),  # 光だまりと見えている灯り
    env=('room', dict(wall='stone', hz=112, floor='flag')),                   # どこで（背景の組み立て）
    items=[('forge', dict(...)), ('anvil', dict(...)), ...],                    # 何を（奥から順に部品）
),
```

- 背景（`ENVS`）: `coast`（夜空・水平線までの海・砂浜）、`room`（石壁・板壁＋卓・石畳・床板）、`night`（夜空・月・丘・地面）、`forest`、`battlement`（城壁の上）、`cave`、`pass`（峠）、`icon`（布の台）。
- 部品の名前は `parts.py` の関数名（と `figure`）。
- 人物のカード（16 枚）は人物を主役に、それ以外（23 枚）は物と場所を主役にする。

### 基本セットの場面

| カード | 場所 | 主役 | 灯り |
|---|---|---|---|
| 銅 copper | 板壁の部屋の卓 | 銅貨の短い山と 3 枚、革袋 | 燭台 |
| 銀 silver | 石壁の部屋の石の卓 | 銀貨の山 3 本と数枚 | 月の窓 |
| 金 gold | 宝物庫の卓 | 宝箱からあふれる金貨の山、高い山 2 本、宝石 | 三つ又の燭台 |
| 小屋 estate | 月夜の丘 | 木組みの小さな家、柵、花 | 月 |
| 荘園 duchy | 夜の野 | 二階建ての石の館と離れ | 街灯 |
| 領地 province | 丘の上 | 天守と丸塔の城、麓の家 | 三日月 |
| 災い curse | 紫の夜の墓地 | 髑髏と墓石、枯れ木、紫の煙 | 紫の炎 |
| 穴蔵 warehouse | 地下蔵 | 横倒しの樽の山、木箱、袋 | 吊りランタン |
| 祈りの庵 abbey | 石の礼拝所 | 祭壇（卓掛け・蝋燭・開いた書）と壁龕 | 月の窓 |
| 水濠 moat | 城の前 | 城壁と城門、月の映る堀 | 三日月 |
| 集落 village | 夜の村 | 寄り合う家々と井戸 | 灯りのともる窓 |
| 作業場 workshop | 板壁の工房 | 壁の道具掛け、作業台の鋸・槌・万力 | 吊りランタン |
| 花畑 meadow | 月夜の丘 | 手前ほど大きい花の列 | 地平の大きな月 |
| 質屋 pawnbroker | 帳場 | 天秤（銅と金）、質草の棚 | 蝋燭 |
| 建て替え remodel | 夜の普請場 | 足場、積みかけの石壁、吊った石 | 松明 |
| 鍛冶場 smithy | 鍛冶場 | 金床と焼けた鉄、火花 | 炉 |
| 集会所 assembly | 広間 | 梁から下がる 4 色の旗、長い卓 | 松明 |
| 夜店 fair | 夜の市 | 提灯の連なり、縞の日よけの屋台 | 大きな提灯 |
| 錬金室 alembic | 実験室 | 炎の上で緑に光るフラスコと管、薬瓶の棚 | 蝋燭 |
| 文書館 archive | 書庫 | 天井までの書棚と梯子、書見台 | 燭台 |
| 露店 market | 夜の市 | 緑の日よけ、りんご・パン・菜・魚のかご | 吊りランタン |
| 鉱脈 mine | 坑道 | 支え木、金の筋、鉱車、つるはし | 吊りランタン |
| 晩餐 banquet | 広間の卓 | 丸焼き、杯、パンと果物 | 燭台 |
| 呼び込み crier | 夜の通り | 鈴を振る男（赤い服・羽根帽子） | 街灯 |
| 両替商 moneylender | 帳場 | 銀貨をかざす商人（緑の衣・帽子）、卓の硬貨 | 蝋燭 |
| 小姓 attendant | 広間 | 盆を捧げる少年 | 松明 |
| 徴税官 official | 石の廊下 | 台帳を開いて指さす役人（赤い衣） | 松明 |
| 猟師 hunter | 夜の森 | 弓を引く狩人（緑の頭巾） | 月 |
| 自警団 mercenary | 町の門 | 盾を構え剣を上げる兵（胸当て・兜） | 松明 |
| 号令 command | 城壁の上 | 旗を立て剣で指す将（青・赤い外套） | 篝火 |
| 峠の盗賊 highwayman | 峠 | 覆面で剣を突きつける男（左向き） | 三日月 |
| 番兵 sentinel | 城壁の上 | ランタンを掲げ槍を立てる兵 | 手のランタン |
| 呪術師 sorcerer | 洞窟 | 紫の光の玉を掲げる術師 | 光の玉 |
| 匠 craftsman | 工房 | 膝をついて像を彫る職人 | 吊りランタン |
| 薪割り woodsman | 夜の森 | 斧を振りかぶる男、切り株と丸太 | 枝のランタン |
| 会計係 bursar | 書斎 | 帳簿を開く会計係、鍵束、銀の箱 | 燭台 |
| 物見 scout | 物見台 | 遠眼鏡をのぞく男、遠い村の灯 | 星明かり（見えない光） |
| すり pickpocket | 路地 | しゃがんで財布を握る男（覆面） | 吊りランタン |
| 宝探し explorer | 洞窟 | ランタンを掲げ地図を持つ男、宝箱 | 手のランタン |
| 千両箱 a_chest | 布の台 | 錠前と鉄の帯の箱 | 蝋燭 |
| のぼり旗 a_flag | 夜の野 | 縦長の旗 | 月 |
| 法螺貝 a_horn | 布の台 | 巻貝と房 | 見えない光 |
| 合鍵 a_key | 天鵞絨の台 | 真鍮の大きな鍵 | 見えない光 |
| 提灯 a_lantern | 軒先 | 骨の見える紙の提灯 | 提灯そのもの |

## 拡張に広げるとき

下の「引き継ぎ」の手順に従う。

## 引き継ぎ

ここまでで描いたのは、基本・陰謀・海辺・繁栄・錬金術・異郷・収穫祭＆ギルド・暗黒時代・冒険・帝国・夜想曲・ルネサンス。
残りは menagerie・allies・plunder・risingsun・promo。

### 読む順

1. この STYLE.md の上の節（決まり）。
2. `palette.py`（36 色とランプ）。色は足さない。ランプ（色の段の並び）は足してよいが、`PALETTE` の色だけで組む。
3. `engine.py`: `Light`（光だまり）、`Canvas.paint`（形・ランプ・明るさ）、`Canvas.brighten`（暈）、`Canvas.dot`（決まった 1 色の点）、
   形の関数（`ellipse` `poly` `rect` `capsule` `vcyl`）。
4. `figure.py` の `figure()` の引数（姿勢・服・かぶり物・持ち物）と `ARMS`。
5. `scenes.py`: 背景の組み立て（`ENVS`）、部品の登録（`PARTS` `PROPS`）、拡張の表（`SETS`）、`render()`。
6. お手本: `scenes_nocturne.py` と `parts_nocturne.py`（いちばん新しく、書き方がそろっている）。

### 新しい拡張を描く手順

1. 札の一覧を出す。`cards-<拡張>.js` の `id: '...', name: '...'` のうち、**`art/<id>.png` があるもの**が対象
   （対局の組み合わせ `{ id, name, cards: [...] }` は除く）。`knight('k_ade', ...)` のような関数で作る札は
   `id:` の形で書かれていないので、`art/` のファイル名と突き合わせて漏れを探す。名前と `main` `desc` から場面を決める。
2. `tools/art/parts_<拡張>.py` を作る。先頭は `from engine import ...` と `from parts import ...`（前の拡張の部品は
   `from parts_nocturne import ...` のように使ってよい）。手に持つ物は `(c, fig, hand)` を受ける関数を返す関数にし、
   ファイル末尾の `PROPS = {...}` に入れる。**既にある部品の関数は書き換えない**（前の絵が変わる）。直したいときは
   新しい名前で作るか、引数を足して既定値では前と同じ描き方になるようにする。
3. `tools/art/scenes_<拡張>.py` に `SCENES = {id: dict(light=..., env=..., items=[...])}` を書く。1 枚 1 行のコメント
   （「名前: 何をどこで」）を付ける。`WARM` `DAWN` `_dawn()` `_night()` などの小さな手助けは各ファイルに写して使う。
4. `scenes.py` に 3 か所足す: `import parts_<拡張>` と `for _mod in (...)` の並び、`import scenes_<拡張>`、`SETS` に `'<拡張>': scenes_<拡張>.SCENES`。
5. 描く: `python3 tools/art/build.py --set <拡張>`。何枚かずつ見るときは `python3 tools/art/build.py id1 id2`。
6. 見る: 3 列に並べた下見（スクラッチパッドで PIL で並べる）と、`python3 tools/art/compare_sheet.py --set <拡張>`
   （本部の `.audit/deck-art-<拡張>-<n>.png`。旧絵・幅 60px の縮小と並ぶ）。直したら 5 に戻る。
7. 確かめる（コミットの前に必ず）:
   ```sh
   python3 tools/art/build.py                     # 全部描き直す（2〜5 分。長いときはバックグラウンドで）
   git status --porcelain art | wc -l             # 変わったのがこの拡張の枚数だけか
   python3 tools/art/build.py --check --set <拡張> # 2 回描いて同じ PNG か
   ```
   ほかの拡張の絵が変わっていたら、部品を書き換えてしまっている。意図した直し（例: 馬の作り直し）なら、
   その絵の拡張の見比べ画像も出し直し、コミットの本文に書く。
8. STYLE.md の冒頭の「描いたもの」の文を更新し、`git add art/ tools/art/` だけをコミットする（拡張ごとに 1 つ）。
   `__pycache__` は `.gitignore` 済み。

### よくある失敗と直し方

| 見え方 | 原因 | 直し方 |
|---|---|---|
| 巻物が台・箱に見える | 持ち物の `scroll` は縦に長く、胸の前だと卓に見える | `letter`（封書）か、手を上げて `scroll` を短く。広げるなら `held_map_flat` か `doc` |
| 光の暈が暗い円盤・泡になる | 発光の楕円（`emit`）を薄い明るさで重ねると、暗い段の丸として残る | 暈は `c.brighten(x, y, rx, ry, 0.1〜0.3)` で下の絵を明るくする。発光は芯だけにする |
| 月が毎回左上に出て単調 | `_night()` の既定が月あり | `moon=None` にして、ランタン・街灯・焚き火・窓・夜明け（`sky_ramp='dawn'`）で灯りを替える。三日月は 4 つ目の値（0.3〜0.6） |
| 夜の絵ばかり並ぶ | 夜の背景が既定 | 夜明け、暖かい室内（`WARM`）、炉、雪を散らす。拡張の 3〜4 割は夜以外に |
| 主役が小さくて 60px で潰れる | 人物 h が 100 未満、物の `s` が 1 | 人物は h=108〜116、物は `s=1.4〜2` に。主役の明るい側を暗い背景に当てる |
| 物が宙に浮く | 床の高さ（`hz`）と部品の `base` がずれている | `base` を床の線より下に。遠くの物は `hills` や `ground` の上に置く |
| 似た絵が続く | 同じ背景・同じ構図 | 壁を `stone`/`plank`、床を `table`/`flag`/`planks`、外を `coast`/`forest`/`cave`/`pass`/`battlement` で替える |
| 人物の腕が T 字・木偶っぽい | 腕の姿勢 `aim` `forward` を両腕に | 片腕は `down` `hip` `belly` `chest`。腕を数値 `(肘 dx, dy, 手 dx, dy)` で直接決めてもよい |
| 光源が右上になる | 月や灯りを右に置いた | 見える灯りはいつも左上の側（x < 112, y < 80 くらい）。`light.halo` も合わせる |
| 動物の脚や頭が逆向き | `facing` の向き | `horse` は既定で頭が左。`facing=-1` で右 |
| パレット外の色 | ランプに `PALETTE` にない名前を入れた | `palette.py` の末尾の assert で止まる。色は既にある名前だけで |
| 2 回描いて違う PNG | `random` を種なしで使った | `hsh(...)` か `c.rng`（カードの id が種）だけを使う |

### 残りの拡張で使えそうな既存の部品

- **動物**（menagerie・allies・plunder で多い）: `horse`（`gallop` `blanket`、作り直し済み）、`dog`、`cat`、`raven`、`camel`、
  `deer`（parts_darkages）、`goat` `sheep` `bats`（parts_nocturne）、`rat` `big_rat`、`monkey`、`crab` `starfish`。
  亀・梟・蝶・鼠・カワウソ・牛・ラバ（`w_*`）は無い。`goat` や `dog` の書き方（`X = lambda dx` で向きを返す）を写して作る。
- **海・船**（plunder）: `sea` `beach` `ship`（`kind='merchant'|'pirate'|'longship'|'ghost'`）`boat` `dock` `long_pier` `island`
  `foam` `cliff` `cave_mouth` `chest` `pile` `coin_pile` `gem` `map_pieces` `cutlass` `smoke`。
- **日本の情景**（risingsun）: `torii` `dohyo` `noren` `wood_tub` `steam` `pagoda` `great_gate`（parts_empires）、
  `paper_lantern` `lantern_string` `gatehouse_roof` `wayside_shrine` `shimenawa_tree` `gohei` `holed_coin`、
  かぶり物 `jingasa`、持ち物 `katana` `katana_flat`、`hang_banner`。
- **ルネサンス**（学芸・商い）: `easel` `vase` `gears` `automaton` `telescope` `globe` `books_row` `bookcase` `open_book`
  `slate` `hourglass` `ship`、旗 `banner` `nobori` `flag_pole`、`sign` `stall` `awning`。
- **同盟**（allies、人物と組合が多い）: `palace` `house` `guildhall` 系の組み合わせ、`round_table` `chess_board` `throne`、
  かぶり物ほぼ全部、`face=True`。
- **人物**: `figure()` の姿勢 14 通り・脚 4 通り、`gown`、`face`、`beard`、持ち物は `scenes.PROPS` のキー一覧を見る。

### 積み残し

- **手長猿**（海辺の `gibbon`）: `parts.monkey` が棒を組んだように硬い。menagerie で猿を使う前に、馬と同じく
  胴のふくらみ・2 節の腕で作り直す。作り直したら `gibbon` が変わるので、海辺の見比べ画像も出し直す。
- **狼男**（夜想曲 `wolfman`）: かぶり物 `wolf` の頭が体に比べて小さい。`figure.py` の `kind == 'wolf'` を大きくする
  （使っているのは `wolfman` だけ）。
- **天の加護**（`b_sky`）: 空ばかりで地面が暗い。丘を明るく、主役（後光の日）を大きく。
- **顔**: `face=True` は目・眉・鼻・口を 1 段足すだけ。王や女王が主役の札が多い拡張では、もう 1 段（頬の影など）を足してもよい。
- 夜想曲の怪異の札は、まだ月が左上に出る絵が多め。
- **大きさ**: 1 枚 4〜5 KB。全面のノイズがないためで、上限（40 KB）の内。旧版は平均 19〜27 KB。ここまで報告して水準は保てていると言われている。
