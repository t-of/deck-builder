#!/bin/bash
# 世代ごとに「自己対局 → 学習 → 測定」を回す（docs/ai-design.md §4）。止まったら同じコマンドで続きから回せる。
# usage: cd deck-builder && sbatch -p DEF -n 64 jobs/job_ai.sh <名前> <始める世代> <世代数> [full|base|preset:<id>]
#   例: sbatch -p DEF -n 64 jobs/job_ai.sh base1 0 30 base      段階 1（基本の王国だけ）
#       sbatch -p DEF -n 64 jobs/job_ai.sh full1 0 100 full     段階 2（全拡張）
#       INIT_MODEL=runs/base1/gen_13 REF_MODEL=runs/base1/gen_13 sbatch -p DEF -n 64 jobs/job_ai.sh p-first 0 15 preset:first   1 つの王国に特化（§11）
# 世代 0 は「さいきょう同士の棋譜を作って学ぶ」。世代 n（1 から）は「重み gen_best で自己対局 → 学ぶ → 測る」。
# 結果: runs/<名前>/log.tsv（1 世代 1 行）、runs/<名前>/gen_<n>.bin/.json、runs/<名前>/best（今の最良の世代の番号）。
# 環境変数（省略できる。bench の結果を見て決める）: EXPERT_GAMES 棋譜の局数, GEN_GAMES 1 世代の自己対局の局数, EVAL_GAMES 測る局数（相手ごと）,
#   EXPERT_EPOCHS・EPOCHS 学習の周回数, TEMP0 最初の温度（世代ごとに ×0.93、下限 0.02）, ACCEPT 新しい世代にする勝率,
#   INIT_MODEL 世代 0 を棋譜の模倣ではなくこのモデル（拡張子なしのパス）の写しにする, REF_MODEL あれば log.tsv の最後に vs_ref 列（gen_N 対 REF_MODEL）を足す,
#   （微調整用）PREV_GAMES 対 前の最良の局数（既定 EVAL_GAMES）, REF_GAMES vs_ref の局数（既定 4000）, LR 学習率（既定は train.py の 1e-3）,
#   KL_W 元のモデル（gen_0）との出力のずれを損失に足す重み（既定は足さない）
#SBATCH -J ai
#SBATCH -p DEF
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -o logs/%x-%j.out
#SBATCH -e logs/%x-%j.out
name=$1; g0=${2:-0}; ng=${3:-1}; stage=${4:-full}
cd "$SLURM_SUBMIT_DIR"
export PATH=$PATH:$HOME/opt/node/bin PYTHONUNBUFFERED=1
set -eo pipefail   # 途中で失敗したらそこで止める（続きは同じコマンドで）
NC=${SLURM_NTASKS:-$(nproc)}
EXPERT_GAMES=${EXPERT_GAMES:-20000}; GEN_GAMES=${GEN_GAMES:-20000}; EVAL_GAMES=${EVAL_GAMES:-400}
EXPERT_EPOCHS=${EXPERT_EPOCHS:-4}; EPOCHS=${EPOCHS:-2}; TEMP0=${TEMP0:-0.15}; ACCEPT=${ACCEPT:-0.55}
PREV_GAMES=${PREV_GAMES:-$EVAL_GAMES}; REF_GAMES=${REF_GAMES:-4000}   # 世代の比べ・vs_ref の局数（微調整は docs/ai-design.md）
TRAIN_OPTS=""; [ -n "$LR" ] && TRAIN_OPTS="--lr $LR"; [ -n "$KL_W" ] && TRAIN_OPTS="$TRAIN_OPTS --ref runs/$name/gen_0 --kl-w $KL_W"
BASE=""; [ "$stage" = base ] && BASE="--base"; [[ "$stage" == preset:* ]] && BASE="--preset ${stage#preset:}"
R=runs/$name; mkdir -p $R logs
LOG=$R/log.tsv
[ -f $LOG ] || printf 'gen\tsamples\tvs_prev\tvs_expert\tvs_normal\taccepted\tsec%s\n' "${REF_MODEL:+$(printf '\tvs_ref')}" > $LOG
[ -f $R/init.bin ] || node train/init-weights.mjs $R/init 1 | tail -1
best=$(cat $R/best 2>/dev/null || echo 0)
echo "$(date) start $name gen $g0..$((g0+ng-1)) stage=$stage NC=$NC best=$best"

# 自己対局のシャードを 1 つ作る（できていれば飛ばす。.json は最後に書かれる）
play_shard() { # i
  local i=$1 d=$PLAY_DIR; [ -f $d/s$i.json ] && return
  local per=$(( (PLAY_GAMES + NC - 1) / NC )) seed=$(( PLAY_SEED + i * 1000 ))
  if [ "$PLAY_MODE" = expert ]; then
    node train/selfplay.mjs --games $per --mode expert --seed $seed --out $d/s$i $BASE --model $R/init
  elif [ $((i % 10)) -eq 0 ]; then   # 1 割: 対 さいきょう
    node train/selfplay.mjs --games $per --mode ai --seed $seed --temp $TEMP --model $R/gen_$best --out $d/s$i $BASE
  elif [ $((i % 10)) -eq 1 ] && [ $N -ge 2 ]; then  # 1 割: 対 過去の世代
    node train/selfplay.mjs --games $per --mode self --seed $seed --temp $TEMP --model $R/gen_$best --opp-model $R/gen_$(( (i / 10) % N )) --out $d/s$i $BASE
  else                               # 8 割: 今のモデル同士
    node train/selfplay.mjs --games $per --mode self --seed $seed --temp $TEMP --model $R/gen_$best --out $d/s$i $BASE
  fi > /dev/null
}
export -f play_shard
export R NC BASE

# A 対 B を EVAL_GAMES 局（NC プロセスで割る）。勝率（引き分けは 0.5）を出す
rate() { # a b seed [games]
  local G=${4:-$EVAL_GAMES}
  seq $3 $(($3 + NC - 1)) | xargs -P $NC -I{} node train/match.mjs --a $1 --b $2 --games $(( (G + NC - 1) / NC )) --seed {} $BASE 2>/dev/null \
    | grep RESULT | awk '{w+=$2;d+=$3;n+=$5} END{printf "%.3f", n ? (w + d / 2) / n : 0}'
}

for N in $(seq $g0 $((g0 + ng - 1))); do
  [ -f $R/gen_$N.bin ] && { echo "gen $N は済み"; continue; }
  s=$SECONDS
  if [ $N -eq 0 ] && [ -n "$INIT_MODEL" ]; then   # 世代 0 はこのモデルの写し（学習しない）
    echo "$(date) gen 0: INIT_MODEL=$INIT_MODEL を写す"
    cp $INIT_MODEL.bin $R/gen_0.bin.tmp && cp $INIT_MODEL.json $R/gen_0.json && mv $R/gen_0.bin.tmp $R/gen_0.bin
    samples=-
  else
  best=$(cat $R/best 2>/dev/null || echo 0)
  TEMP=$(awk -v n=$N -v t=$TEMP0 'BEGIN{x=t; for(i=1;i<n;i++) x*=0.93; if (x<0.02) x=0.02; print x}')
  if [ $N -eq 0 ]; then PLAY_MODE=expert; PLAY_GAMES=$EXPERT_GAMES; PLAY_DIR=$R/expert; init=$R/init; ep=$EXPERT_EPOCHS
  else PLAY_MODE=self; PLAY_GAMES=$GEN_GAMES; PLAY_DIR=$R/play_$N; init=$R/gen_$best; ep=$EPOCHS; fi
  PLAY_SEED=$(( 1000000 + N * 100000 )); export PLAY_MODE PLAY_GAMES PLAY_DIR PLAY_SEED TEMP N best
  mkdir -p $PLAY_DIR
  echo "$(date) gen $N: 自己対局 mode=$PLAY_MODE games=$PLAY_GAMES temp=$TEMP best=$best"
  seq 0 $((NC-1)) | xargs -P $NC -I{} bash -c 'play_shard {}'
  echo "$(date) gen $N: 学習 init=$init"
  python3 train/train.py --init $init --out $R/gen_$N --shards $PLAY_DIR --epochs $ep $TRAIN_OPTS | tee $R/train_$N.log | tail -3
  samples=$(grep -o 'samples=[0-9]*' $R/train_$N.log | tail -1 | cut -d= -f2)
  fi
  echo "$(date) gen $N: 測定"
  seed=$(( 5000000 + N * 1000 ))
  vs_exp=$(rate $R/gen_$N expert $seed)
  vs_nor=$(rate $R/gen_$N normal $seed)
  if [ $N -eq 0 ]; then vs_prev=-; acc=1
  else
    vs_prev=$(rate $R/gen_$N $R/gen_$best $seed $PREV_GAMES)
    acc=$(awk -v r=$vs_prev -v a=$ACCEPT 'BEGIN{print (r >= a) ? 1 : 0}')
  fi
  [ $acc -eq 1 ] && echo $N > $R/best
  ref=""; [ -n "$REF_MODEL" ] && ref=$(printf '\t%s' $(rate $R/gen_$N $REF_MODEL $seed $REF_GAMES))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s%s\n' $N $samples $vs_prev $vs_exp $vs_nor $acc $((SECONDS - s)) "$ref" | tee -a $LOG
  [ $N -ge 2 ] && rm -rf $R/play_$((N - 1))   # 古い記録は捨てる（棋譜 expert は残す）
done
echo "$(date) done"; tail -3 $LOG
