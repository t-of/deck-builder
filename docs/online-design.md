# online-design — 「みんなのスマホで」を deck-builder に足す設計メモ

対象: `~/GitHub/tof/apps/deck-builder/`。catan/carcassonne と同じ online-kit（ホスト方式、pub/priv/$uid/hostState）に乗せる。
コードはまだ書かない。段階に分けて engineer に 1 段階ずつ頼む想定。

## 0. 今の作りで効くところ

- 効果はジェネレータ（`engine.js` の `play(game, player, pi)`）。選択が要ると `{ type, player, owner, purpose, options/choices/cards, min, max }` を `yield` し、`main.js` の `step()` が `.next(答え)` で返す。これは catan の「操作を送って結果を待つ」と同じ形だが、**途中のジェネレータが状態の一部になる**のが catan には無い難しさ。
- `main.js` の `doCpuMove(pi)`（1382行目付近）がすでに `{ type: 'buy', id }` のような小さなオブジェクト1つで「次の1手」を表し、`run(...)` を呼ぶ**ディスパッチャ**になっている。これを人の操作にも広げれば、ほぼそのまま `act()` になる（Q5 の答え）。
- `undoLast()` のために、購入・行動の直前に `structuredClone(game)` を取ってある（969・1045行目）。これはホスト引き継ぎの再生に使う「直前の控え」とまったく同じもの（Q3 の答えの核）。
- 乱数は `Math.random()` を直接呼んでいる（`engine.js` の `shuffle()` など）。種は無い。

## 1. ジェネレータが状態に走っている問題（Q1）

**方針: ジェネレータ自体は配らない。ホストのメモリにだけ生きたまま置く。配るのは「今の game」と「今出ている問い」の2つ。**

- ゲストが描くために要るもの:
  - `pub`: `game` から他人の手札を枚数だけにしたもの（2-2 参照）。
  - 今待っている問いがあれば、**その問いの「誰あて」かと「どんな問い」**。`q` オブジェクト（`type / player / owner / purpose / min / max / choices` 等）はカードの id を直接含む型（`supply` の `options` は id、`cards` の `cards` は id）と、位置だけを含む型（`hand` の `options` は手札の位置の配列）がある。
- **`hand` 型だけ変換が要る**: `renderQuestion` は位置から `game.players[q.owner].hand[pos]` を引いて絵を出している。ネットワーク越しに配るときは、位置ではなく**その場で id を埋め込んだ配列**にする（`cardsAt: q.options.map(pos => owner.hand[pos])`）。これで受け取る端末は「owner の手札そのもの」を持たなくても描ける。
- **誰に何を配るか**:
  - 問いに答える人（`q.player`）の priv にだけ、上の「id入りの問い」を入れる（`activeQuestion`）。
  - ほかの参加者の pub には、中身の無い知らせだけ入れる: `{ type, player, owner, purpose }`（例: 「○○ が『民兵』で捨てる手札を選んでいます」）。今の `choiceWho`/`choiceLabel` の表示と同じ情報量。
  - `q.player` が CPU 席なら、ホストはそのまま `cpuAnswer()` で即座に答え、何も配らない（今の分岐 `!isHumanSeat(q.player)` のまま）。
- **答えの受け取り**: ゲストは `room.send('answerQuestion', { value })`。ホストは「送り主の席 == 今の `activeQuestion.player`」を確かめてから `step(pendingGen.next(value))` を呼ぶ（catan の操作の表と同じ二重確認。問いが無い・あて先が違う送信は捨てる）。
- まとめると `pub`/`priv`/`hostState` の中身:
  - `pub`: `game`（手札は他人は枚数だけ）＋ 今の問いの「概要」（誰が・何のため、中身なし）。
  - `priv/$uid`: その席の手札そのもの ＋（自分が `q.player` のときだけ）id 入りの `activeQuestion`。
  - `hostState`: `game` まるごと（手札も山札の並びも全部）＋ 生きたジェネレータは**入れられない**ので、代わりに 2 の「再生用の記録」を入れる。

## 2. 手番でない人への問い（Q2）

- deck-builder の全員参加系の効果（アタックの捨て札・水濠を見せるか等）は `attackOthers()` が**席順に1人ずつ** `yield* fn(pi)` する作り（383行目）。catan の「7人が同時に捨てる」のような**並行**の問いは無い。待っている問いは常に1つだけ。
- なので catan のような「pending の列」は要らない。`activeQuestion` ひとつだけ持てば足りる（Q1 の設計がそのまま使える）。これは deck-builder 側の簡単な点として明記しておく。

## 3. ホストの引き継ぎ（Q3）

`hostState` にジェネレータは置けないので、**「直前の控え＋そこから打った手の記録」から作り直す**（catan 仕様の案と同じ方向）。

- **乱数を種つきにする**: `engine.js` の `Math.random()` 呼び出し（`shuffle()` ほか数か所。grep で全部洗う）を、`game` に紐づく `rng()` に置き換える。`newGame()` で `game.rngSeed`（`Date.now()` 等から）を1つ取り、`mulberry32` のような小さい PRNG を種から作って `game.rng = makeRng(seed)` に持つ（非列挙 or `JSON.stringify` で無視される形。`players[].game` の非列挙と同じやり方）。これは通信の有無に関わらず常に使ってよい（1台モードの見た目は変わらない、同じ対局の再現性が上がるだけ）。
- **控えを取るタイミング**: 今の undo と同じ「トップレベルの手を打つ直前」。`act(type, args)` の入り口で、呼ぶたびに
  - `beforeSnapshot = structuredClone(game)`
  - `action = { type, args }`
  - `answers = []`（この手の中で出た問いへの答えを順に積む）
  を `hostState.inProgress` に書く（`publish` のたび更新）。手が終わって `pendingGen` が無くなったら `inProgress = null` にする。
- **引き継ぎの手順**（新しいホストが `hostState` を読んだ直後）:
  1. `inProgress` が無ければ、ただ `game` を置いて続ける（ジェネレータが無い＝ターン開始前や購入フェイズの合間。これが一番多い）。
  2. `inProgress` があれば: `game = inProgress.beforeSnapshot` に戻し、`act(inProgress.action.type, inProgress.action.args)` を**画面に出さず**呼び直し、`inProgress.answers` を先頭から順に `pendingGen.next(answer)` へ流し込む（CPU 席の自動応答もこの再生の間は呼ばない。記録された答えをそのまま使う）。種つき乱数のおかげで、同じ山札・同じ結果が出る。
  3. 答えを使い切ったところで、元のホストが止まった問いにちょうど戻る。そこから先はふつうに `activeQuestion` を配って続ける。
- これは `undoLast()` の控えの取り方をほぼそのまま借用できる（`structuredClone` 済みの実装例が1045行目にある）。新しく覚える仕組みではなく、**既存の undo 用のコードを「通信のときはホストの引き継ぎにも使う」よう1本化する**のが一番楽（ついでに「通信中は戻す（取り消し）を出さない」決まりとも整合: 控え自体は取るが、ボタンは出さないだけ）。

## 4. 隠し情報（Q4）

- **手札**: 本人の `priv/$uid`。他人には枚数だけ（`pub` 側の `players[i].hand` を `{ length: n }` などに変える関数を engine 側に1つ足す。catan の `viewFor(game, seat)` と同じ形。カードごとの枚数内訳が要る効果は無いはずだが、念のため段階4の終わりで確認）。
- **山札の並び**: 誰にも見せない。`pub`・`priv` どちらにも `deck` は配列のまま持つ必要があるが、**中身を見せてよいのは一番上が分かる効果が起きたときだけ**で、ふだんは「山札の枚数」で足りる絵しか使っていないはず（`main.js` を見る限り山札の中身を表示する場面は無い）。配るときは `deck` も `{ length: n }` にして、山札を触る効果（見る・置き直す）は専用の問い（`askCards` で山札から引いた一時的な配列を渡す）経由で見せる、という今のまま運用すれば崩れない。
- **公開された札**: 場（`playArea`）・サプライ（`supply`）・捨て札（`discard`）・廃棄（`trash`）はそのまま `pub` でよい（今も全員に見えている情報）。
- **実装**: `engine.js` に `viewFor(game, seat)`（catan 同様の名）を1つ足す。中身は「手札・山札を `length` に潰したコピーを返す」関数。`priv/$uid` は `viewFor` の結果に **その席だけ** `hand`・`deck` を戻したもの。

## 5. act() に集める場所（Q5）

- `doCpuMove(pi)`（main.js 1382行目）の `m.type` ディスパッチが、求める形にいちばん近い。これを `act(type, args)` という1つの関数に格上げし、
  - 今 `doCpuMove` が直接呼んでいる `run(playAction(...))` などの中身を、そのまま `act()` の中身として使う。
  - 人のタップ側（`run(beginTurn(game))` 839行目、`run(buyCard(...))` 1047行目、`run(playTreasureGen(...))` 1137行目、`run(playAction(...))` 1330行目、`run(endTurn(...))` 1335行目、`spendVillager`/`spendCoffers` の直呼び 949・952行目 など）を、同じ `{ type, id/n }` を作って `act()` を呼ぶ形に揃える。
  - `onDone` の後始末（`soundBuy()`・`backToTurn()`・`renderTurn()` 等）は `act()` の中（またはコールバック）に残してよい。「音を鳴らす・次の画面を出す」は見た目の話で、通信とは関係ない。
- カード自体の効果（`cards-*.js` の `play`/`onAttack` 等）は一切さわらない。どれも `yield` で止まり、answererの確認は `engine.js` の `answerer()` が既にしているので、**拡張を増やしても `act()` を触らずに済む**（依頼の「カードごとの手直しが要らない形」の答え）。
- 通信のときの `act()` の分岐はcatanと同じ3通り:
  - 1台モード: 今まで通り直接呼ぶ。
  - 通信・ホスト: 送り主の席を確かめてから呼び、呼んだあとに `publish`。
  - 通信・ゲスト: `room.send(type, args)` して返事（`pub`/`priv` の更新）を待つ。
  - 問いの答え（`answerQuestion`）は `act()` とは別口の小さな経路（3人称の良いタイミングが無いので、`act('answerQuestion', { value })` として同じ入り口を通してもよいが、確かめる相手が「今動いてよい席」ではなく「今の `activeQuestion.player`」なので、確認の条件だけ変える）。

## 6. 段階の分け方（1段階 = engineer 1回）

catan の段階0〜10に倣う。deck-builder は拡張が多い代わりに「全員同時の問い」が無く、インタラクションの数（攻撃の反応・交易）も catan より少ないので、段階5が1本で収まる見込み。

| 段階 | やること | 終わりの条件 |
|---|---|---|
| 0 | （オーナー・不要）Firebase は `tof-online` を使い回す。online-kit をコピーするだけ | — |
| 1 | 乱数を種つきにする（`game.rng`、`Math.random` 直呼びを置換）。`newGame` の対局が種から再現できる小さなテスト（同じ種→同じ盤・同じ初手ドロー） | `node test/sim.mjs` が今まで通り落ちない。種を固定した新しいテストが通る |
| 2 | `act(type, args)` に人のタップとCPUの手を1本化（`doCpuMove` を土台に広げる）。1台モードの動きは変えない | main.js に `run(playAction(...))` 等の直呼びが `act()` の外に残っていない（grep で確認）。1台・CPU戦とも最後まで遊べる |
| 3 | `engine.js` に `viewFor(game, seat)` を足す（手札・山札を枚数に潰す）。ホストの引き継ぎ用の控え（`inProgress`: `beforeSnapshot`/`action`/`answers`）を `act()` の入り口に仕込む（まだ Firebase には繋がず、ローカルで「控えを取って→同じ答えで再生したら同じ状態になる」小さなテスト） | 種つき乱数の上で、控えから再生した `game` が、再生しなかった場合の `game` と一致する（`JSON.stringify` 比較）テストが通る |
| 4 | online-kit をコピー（`online.js`・`room.js`・`database.rules.json`）。タイトル→名前→部屋を作る/入る→待合（席・CPU・人数3〜4人） | 2台で、作る・コードで入る・CPUの席を足す・はじめると、同じ `kingdom` で対局画面が開く |
| 5 | 対局の同期本体: `act()` の通信版（ホストでの確かめ）、`activeQuestion` の配布（4・1の形で pub は概要、priv は id 入り）、ゲストの手札だけ表示、CPUはホストでそのまま、音・演出の同期 | 人2+CPU2で最後まで遊べる。ゲストが自分の番でない操作をできない。アタックの捨て札・水濠を見せるかが正しい相手に出る |
| 6 | 切断・つなぎ直し・「CPUに代わってもらう」・ホストの引き継ぎ（3の再生を実地で）・部屋に戻る・後片付け | 対局中にゲストを閉じ直すと同じ席に戻る。ホストを閉じると、別の端末が `inProgress` から続きを引き継げる |
| 7 | 拡張を1つずつ通信で開ける（今のプリセット・王国構成の生成がそのまま使えるか確認するだけの軽い段階が多いはず） | その拡張で人2+CPUが最後まで遊べる |

段階1・2・3はFirebase無しで進められる（カードの効果やCPUに触れない、安全な土台作り)。

## 残った確認（オーナー向け、必須ではない）

- 人数・CPU混在・拡張の出し方は catan の決め（3〜4人・人2人以上・空席CPU可・拡張は1つずつあとで開ける）をそのまま踏襲してよいか。
- 種つき乱数を1台モードにも常時使うこと（挙動は変わらないが `game` に `rng`/`rngSeed` が増える＝保存データの形が変わる）に問題ないか。古い保存（`deck-builder.game` 等）には `rng` が無いので、読み込み時に種を振り直す引き継ぎ処理を入れる。
