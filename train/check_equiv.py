"""JS（ai/net.js）と PyTorch（train.py の Net）の推論が同じ値になるか確かめる。
  python3 train/check_equiv.py [判断の数 40]
乱数の重み（埋め込み・バイアスも 0 でない）を float16 で書き、Node でその重みを使って数局打ち、最初の N 判断の全候補の値を記録に書かせ（selfplay.mjs --check）、
同じ重みと同じ入力（float32 で書いた記録）から PyTorch で出した値と比べる。差が 1e-4 を超えたら落ちる。
"""
import os, subprocess, sys, tempfile
import numpy as np
import torch
from export import read_model, write_model
from train import Net, load_shard, build_batch

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
tmp = tempfile.mkdtemp()
meta, w = read_model(os.path.join(root, 'ai', 'model'))
rng = np.random.default_rng(7)
for k in ('emb', 'bp', 'bs', 'b1', 'b2', 'b3'):
    w[k] = rng.normal(0, 0.3, w[k].shape).astype(np.float32)
write_model(f'{tmp}/m', meta, w)
subprocess.run(['node', 'train/selfplay.mjs', '--games', '2', '--mode', 'expert', '--seed', '5', '--model', f'{tmp}/m', '--out', f'{tmp}/s', '--f32', '--check', str(N)],
               cwd=root, check=True, stdout=subprocess.DEVNULL)
_, w16 = read_model(f'{tmp}/m')  # float16 に丸めたあとの重み（JS が読むのと同じ）
net = Net(meta); net.load(w16)
A = load_shard(f'{tmp}/s')
sel = np.arange(N)
b = build_batch(A, sel, np.ones(N, bool))
with torch.no_grad():
    py = torch.softmax(net(b), 1).numpy()
assert len(b['supRow']) > 0 and float(b['deckDelta'].abs().sum()) > 0, '買う候補が入っていない'
js = A['checkOut'].reshape(-1, 2)
assert py.shape == js.shape, (py.shape, js.shape)
d = float(np.abs(py - js).max())
print(f'候補 {len(js)} 個、JS と PyTorch の差の最大 {d:.2e}')
assert d < 1e-4, '差が 1e-4 を超えた'
