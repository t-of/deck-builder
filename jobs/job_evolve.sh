#!/bin/bash
# 買い方表を進化で作り（docs/ai-specialize.md §3-1）、できた表を さいきょう CPU と汎用モデルに当てる。計算は数分〜数十分。
# usage: cd deck-builder && sbatch -p DEF -n 64 --nice=10000 jobs/job_evolve.sh <名前> [世代数] [モデル（拡張子なしのパス。例 runs/base1/gen_28）]
#   例: sbatch -p DEF -n 64 --nice=10000 jobs/job_evolve.sh e1 300 runs/base1/gen_28
# 止まったら同じコマンドで続きから（runs/<名前>/gen_N.json の最後から）。世代数は「この世代数になるまで」。
# 環境変数（省略できる）: POP 集団, OPPS 相手の数, GAMES 相手 1 つあたりの局数, EVAL_GAMES 測る局数, PRESET 王国
# 結果: runs/<名前>/gen_<N>.json、ログの最後に 表の bot 対 さいきょう・対 モデル の勝率（引き分け 0.5）。
#SBATCH -J evolve
#SBATCH -p DEF
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -o logs/%x-%j.out
#SBATCH -e logs/%x-%j.out
name=${1:-e1}; ng=${2:-300}; model=$3
cd "$SLURM_SUBMIT_DIR"   # sbatch はスクリプトを別の場所に写して動かすので、$0 でなくここから探す
export PATH=$PATH:$HOME/opt/node/bin
set -eo pipefail
NC=${SLURM_NTASKS:-$(nproc)}
POP=${POP:-64}; OPPS=${OPPS:-8}; GAMES=${GAMES:-50}; EVAL_GAMES=${EVAL_GAMES:-400}; PRESET=${PRESET:-first}
R=runs/$name; mkdir -p $R logs
echo "$(date) start evolve $name gens=$ng pop=$POP NC=$NC host=$(hostname)"
node train/evolve.mjs --name $name --gens $ng --pop $POP --opps $OPPS --games $GAMES --procs $NC --preset $PRESET
last=$(ls $R | sed -n 's/^gen_\([0-9]*\)\.json$/\1/p' | sort -n | tail -1)

# 測る: 表（最後の世代の最高）対 相手 を EVAL_GAMES 局（NC プロセスで割る。先後は局ごとに交代）
rate() { # 相手 種
  seq $2 $(($2 + NC - 1)) | xargs -P $NC -I{} node train/match.mjs --a table:$R/gen_$last.json --b $1 --games $(( (EVAL_GAMES + NC - 1) / NC )) --seed {} --preset $PRESET 2>/dev/null \
    | grep RESULT | awk '{w+=$2;d+=$3;l+=$4;n+=$5} END{printf "勝 %d 分 %d 負 %d 局 %d 勝率 %.3f", w, d, l, n, n ? (w + d / 2) / n : 0}'
}
echo "==== 結果 (gen_$last の最高の表, 王国 $PRESET)"
echo "対 さいきょう CPU: $(rate expert 1000)"
[ -n "$model" ] && echo "対 $model: $(rate $model 2000)"
echo "$(date) done evolve"
