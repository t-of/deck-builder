#!/bin/bash
# 計測ジョブ（数分）: 自己対局・学習・測定の速さと記録の大きさを測る。docs/ai-design.md §4 の見積もりを直すため。
# usage: cd deck-builder && sbatch -p DEF -n 64 jobs/job_ai_bench.sh        （-n はコア数。中のプロセス数もこれに合わせる）
# 結果は logs/aibench-<ジョブ番号>.out の「==== 結果」から下。それをそのまま貼る。
#SBATCH -J aibench
#SBATCH -p DEF
#SBATCH -N 1
#SBATCH -n 64
#SBATCH -o logs/%x-%j.out
#SBATCH -e logs/%x-%j.out
cd "$SLURM_SUBMIT_DIR"
export PATH=$PATH:$HOME/opt/node/bin PYTHONUNBUFFERED=1
set -eo pipefail   # 途中で失敗したらそこで止める（続きは同じコマンドで）
mkdir -p logs
NC=${SLURM_NTASKS:-$(nproc)}
W=runs/bench; rm -rf $W; mkdir -p $W
echo "$(date) start bench NC=$NC host=$(hostname)"
node -v; python3 -c "import torch,numpy;print('torch',torch.__version__,'numpy',numpy.__version__)"
node train/init-weights.mjs $W/init 1 | tail -1

sh_run() { # 名前 局数/プロセス モード [追加の引数]
  local name=$1 n=$2 mode=$3; shift 3
  mkdir -p $W/$name
  local s=$SECONDS
  seq 0 $((NC-1)) | xargs -P $NC -I{} node train/selfplay.mjs --games $n --mode $mode --seed {} --out $W/$name/s{} "$@" > $W/$name/log.txt 2>&1
  echo "$name $((SECONDS - s)) 秒" >> $W/times.txt
}
sh_run expert 2 expert --model $W/init
sh_run ai 4 ai --model $W/init
sh_run self 4 self --model $W/init
OUTPUT=$(mktemp)
cp $W/times.txt $OUTPUT

# 学習: コア数と同じスレッド数、8 スレッドの 2 通りを 60 秒ずつ
for th in $NC 8; do
  echo "--- 学習 スレッド $th"
  SLURM_NTASKS=$th python3 train/train.py --init $W/init --out $W/g_$th --shards $W/expert $W/ai $W/self --epochs 1 --max-seconds 60 --val 0 2>&1 | tail -3
done

# 測定: 1 プロセス 2 局（乱数の重みの AI なので勝ち負けに意味はない。時間だけ見る）
mm() { local s=$SECONDS; seq 0 $((NC-1)) | xargs -P $NC -I{} node train/match.mjs --a $W/init --b $1 --games 2 --seed {} | grep RESULT | awk '{w+=$2;d+=$3;l+=$4;n+=$5} END{print "勝 引分 負 局:",w,d,l,n}' >> $OUTPUT; echo "match_vs_$1 $((SECONDS - s)) 秒（1 プロセス 2 局）" >> $OUTPUT; }
mm normal; mm expert

echo "==== 結果 (NC=$NC)"
echo "-- 自己対局の 1 プロセス分（局数 打ち切り 判断 候補 秒 秒/局 バイト）"
for m in expert ai self; do echo "$m: $(head -1 $W/$m/log.txt)"; done
echo "-- 全プロセスの所要秒（NC プロセスが同時に 2〜4 局ずつ打った時間）"
cat $OUTPUT
echo "-- 記録の大きさ"
for m in expert ai self; do echo "$m: $(cat $W/$m/*.bin | wc -c) バイト / $(grep -h -o '^[0-9]* 局' $W/$m/log.txt | awk '{s+=$1} END{print s}') 局"; done
echo "$(date) done bench"
