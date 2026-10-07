"""価値ネットの学習（docs/ai-design.md §3・§10）。ai/net.js と同じ形を PyTorch で書き、train/selfplay.mjs の記録（シャード）を読んで学ぶ。
  python3 train/train.py --init <前の重み 拡張子なし> --out <出力 拡張子なし> --shards <シャードのフォルダ or 名前>... [--epochs 2]
損失:
  回帰 … 選んだ候補の「自分の勝つ見込み」を最後の結果（勝ち1・引き分け0.5・負け0）に近づける（交差エントロピー。TD-Gammon 型の目標をモンテカルロで）
  順位 … さいきょうの判断（decSource=0）の一部で、全候補の（自分の logit − 相手の logit）の softmax が選んだ候補を当てる
ID の埋め込みは、バッチごとに ID の一部（--id-drop）を 0 にして、カードの性質だけでも打てるようにする。
"""
import argparse, glob, json, math, os, time, warnings
warnings.filterwarnings("ignore", message=".*index_reduce.*")
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from export import read_model, write_model

NB = 5  # 袋の数（features.js の BAGS）
DT = {'int8': '<i1', 'int16': '<i2', 'int32': '<i4', 'float32': '<f4', 'float16': '<f2'}


class Net(nn.Module):
    def __init__(self, meta):
        super().__init__()
        D, H, P = meta['dim'], meta['hidden'], meta['props']
        V = len(meta['ids']) + 1
        self.D, self.V = D, V
        self.emb = nn.Parameter(torch.zeros(V, D))
        self.Wp = nn.Linear(P, D)
        self.Ws = nn.Linear(D + 4, D)
        self.l1 = nn.Linear(NB * D + D + meta['scalars'] + D + 4 + 4, H)
        self.l2 = nn.Linear(H, H)
        self.l3 = nn.Linear(H, meta['outputs'])

    # model.json の shapes の名前 → (層, 属性)
    def table(self):
        return {'emb': (self, 'emb'), 'Wp': (self.Wp, 'weight'), 'bp': (self.Wp, 'bias'), 'Ws': (self.Ws, 'weight'), 'bs': (self.Ws, 'bias'),
                'W1': (self.l1, 'weight'), 'b1': (self.l1, 'bias'), 'W2': (self.l2, 'weight'), 'b2': (self.l2, 'bias'),
                'W3': (self.l3, 'weight'), 'b3': (self.l3, 'bias')}

    def load(self, w):
        with torch.no_grad():
            for k, (m, a) in self.table().items():
                getattr(m, a).copy_(torch.from_numpy(w[k]))

    def weights(self):
        w = {k: getattr(m, a).detach().cpu().numpy().copy() for k, (m, a) in self.table().items()}
        w['emb'][0] = 0
        return w

    def forward(self, b, idmask=None):
        """b: build_batch の結果。行（判断×候補）ごとの logits (R, 2) を返す"""
        D = self.D
        emb = self.emb if idmask is None else self.emb * idmask[:, None]
        emb = torch.cat([torch.zeros(1, D), emb[1:]])  # 行 0（並びにない札）は埋め込みなし
        cv = b['props'] @ self.Wp.weight.T + self.Wp.bias + emb  # (V, D) 札ごとのベクトル
        bag = F.embedding_bag(b['bagIdx'], cv, b['bagOff'], mode='sum', per_sample_weights=b['bagW']).view(-1, NB, D)
        rb = bag[b['rowDec']].clone()  # (R, 5, D)
        cvc = cv[b['candIdx']] * b['candHas'][:, None]  # 候補の札のベクトル（何もしない候補は 0）
        rb[:, 0] += b['deckDelta'][:, None] * cvc  # 選んだあとの自分のデッキ（買う・獲得だけ deckDelta が 0 でない）
        # サプライ（Deep Sets）。選んだ山だけ「残り -0.1」でやり直して差し替える
        h = F.relu(self.Ws(torch.cat([cv[b['supIdx']], b['supExt']], 1)))
        sd = torch.zeros(b['B'], D).index_add(0, b['supDec'], h)[b['rowDec']]
        m = b['supRow']
        if m.numel():
            ext = b['supExt'][b['supLocal']].clone()
            ext[:, 0] -= 0.1
            h2 = F.relu(self.Ws(torch.cat([cv[b['supIdx'][b['supLocal']]], ext], 1)))
            sd = sd.index_add(0, m, h2 - h[b['supLocal']])
        x = torch.cat([rb.reshape(len(rb), -1), sd, b['scalars'][b['rowDec']], cvc, b['kindOH'], b['candExt']], 1)
        return self.l3(F.relu(self.l2(F.relu(self.l1(x)))))


# ---- シャード ----
def load_shard(prefix):
    h = json.load(open(prefix + '.json'))
    A = {k: np.fromfile(prefix + '.bin', dtype=DT[v['type']], count=v['length'], offset=v['offset']) for k, v in h['arrays'].items()}
    ns, p = h['ns'], h['p']
    A['scalars'] = A['scalars'].reshape(-1, ns)
    A['supExt'] = A['supExt'].reshape(-1, 4)
    A['candExt'] = A['candExt'].reshape(-1, 4)
    A['cardProps'] = A['cardProps'].reshape(-1, p)
    A['gameResult'] = A['gameResult'].reshape(-1, 2)
    V = A['cardProps'].shape[0]
    D = len(A['decGame'])
    co = A['candOff']
    A['candDec'] = np.repeat(np.arange(D), np.diff(co))
    # 選んだあとの状態の規則（§10）。候補の札が自分のデッキに何枚あるか／サプライのどの山か
    def lookup(entry_dec, entry_idx, q):
        keys = entry_dec.astype(np.int64) * V + entry_idx
        order = np.argsort(keys, kind='stable')
        sk = keys[order]
        pos = np.minimum(np.searchsorted(sk, q), max(len(sk) - 1, 0))
        hit = (len(sk) > 0) & (sk[pos] == q) if len(sk) else np.zeros(len(q), bool)
        return order[pos], hit
    q = A['candDec'].astype(np.int64) * V + A['candIdx']
    bo = A['bagOff']
    pos0, len0 = ragged(bo[0:D * NB:NB], bo[1:D * NB + 1:NB])
    o, hit = lookup(np.repeat(np.arange(D), len0), A['bagIdx'][pos0], q)
    A['candN'] = np.where(hit, A['bagCnt'][pos0][o], 0).astype(np.float32)
    so = A['supOff']
    o, hit = lookup(np.repeat(np.arange(D), np.diff(so)), A['supIdx'], q)
    A['candSup'] = np.where(hit, o, -1)
    return A


def ragged(starts, ends):
    """区間 [starts, ends) の添字を全部つないだもの、と区間の長さ"""
    lens = ends - starts
    tot = int(lens.sum())
    cs = np.cumsum(lens) - lens
    return np.repeat(starts - cs, lens) + np.arange(tot), lens


def build_batch(A, sel, rank):
    """判断 sel（配列）の行を作る。rank が真の判断は全候補、そうでなければ選んだ候補だけ"""
    B = len(sel)
    co = A['candOff']
    nc = co[sel + 1] - co[sel]
    starts = np.where(rank, co[sel], co[sel] + A['decChosen'][sel])
    rows, rlens = ragged(starts, starts + np.where(rank, nc, 1))
    rowDec = np.repeat(np.arange(B), rlens)
    bo = A['bagOff']
    bid = (sel[:, None] * NB + np.arange(NB)).ravel()
    bpos, blens = ragged(bo[bid], bo[bid + 1])
    spos, slens = ragged(A['supOff'][sel], A['supOff'][sel + 1])
    kind = A['candKind'][rows].astype(np.int64)
    cs = A['candSup'][rows]
    fl = lambda a: torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32))
    ln = lambda a: torch.from_numpy(np.ascontiguousarray(a, dtype=np.int64))
    gain = (kind <= 1)
    n = A['candN'][rows]
    sloc0 = np.cumsum(slens) - slens  # 判断ごとの、バッチの中のサプライの始まり
    hit = gain & (cs >= 0)
    supRow = np.nonzero(hit)[0]
    res = A['gameResult'][A['decGame'][sel], A['decSeat'][sel]]
    chosen = np.cumsum(rlens) - rlens + np.where(rank, A['decChosen'][sel], 0)
    return {
        'B': B, 'props': fl(A['cardProps']),
        'bagIdx': ln(A['bagIdx'][bpos]), 'bagW': fl(np.log1p(A['bagCnt'][bpos].astype(np.float32))),
        'bagOff': ln(np.cumsum(blens) - blens),
        'rowDec': ln(rowDec), 'candIdx': ln(A['candIdx'][rows]), 'candHas': fl(kind != 3),
        'deckDelta': fl(np.where(gain, np.log1p(n + 1) - np.log1p(n), 0)),
        'supIdx': ln(A['supIdx'][spos]), 'supExt': fl(A['supExt'][spos]), 'supDec': ln(np.repeat(np.arange(B), slens)),
        'supRow': ln(supRow), 'supLocal': ln(cs[hit] - A['supOff'][sel][rowDec][hit] + sloc0[rowDec][hit]),
        'scalars': fl(A['scalars'][sel]), 'kindOH': fl(np.eye(4)[kind]), 'candExt': fl(A['candExt'][rows]),
        # 損失用
        'chosen': ln(chosen), 'result': fl(res), 'rank': ln(np.nonzero(rank & (nc > 1))[0]), 'rowsPer': ln(rlens),
        'expert': A['decSource'][sel] == 0,
    }


def losses(logits, b, rank_w):
    """回帰（選んだ行）＋順位（rank の判断）"""
    lc = logits[b['chosen']]
    t = torch.stack([b['result'], 1 - b['result']], 1)
    reg = -(t * F.log_softmax(lc, 1)).sum(1).mean()
    rk = torch.zeros(())
    ri = b['rank']
    if len(ri) and rank_w > 0:
        score = logits[:, 0] - logits[:, 1]
        dec = b['rowDec']
        mx = torch.zeros(b['B']).index_reduce(0, dec, score.detach(), 'amax', include_self=False)
        lse = torch.log(torch.zeros(b['B']).index_add(0, dec, torch.exp(score - mx[dec]))) + mx
        rk = (lse - score[b['chosen']])[ri].mean()
    return reg, rk


def evaluate(net, shards, batch):
    net.eval()
    reg = acc = n = ne = 0
    with torch.no_grad():
        for A in shards:
            D = len(A['decGame'])
            for i in range(0, D, batch):
                sel = np.arange(i, min(i + batch, D))
                b = build_batch(A, sel, np.ones(len(sel), bool))
                lg = net(b)
                r, _ = losses(lg, b, 0)
                reg += float(r) * len(sel); n += len(sel)
                score = (lg[:, 0] - lg[:, 1]).numpy()
                rows = np.repeat(np.arange(len(sel)), b['rowsPer'].numpy())
                best = np.full(len(sel), -1e9); np.maximum.at(best, rows, score)
                ch = score[b['chosen'].numpy()]
                ex = b['expert']
                acc += int(((ch >= best - 1e-6) & ex).sum()); ne += int(ex.sum())
    net.train()
    return reg / max(n, 1), acc / max(ne, 1)


def find_shards(args):
    out = []
    for a in args:
        out += sorted(glob.glob(os.path.join(a, '*.json'))) if os.path.isdir(a) else [a + '.json' if not a.endswith('.json') else a]
    return [p[:-5] for p in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--init', required=True); ap.add_argument('--out', required=True); ap.add_argument('--shards', nargs='+', required=True)
    ap.add_argument('--epochs', type=int, default=2); ap.add_argument('--batch', type=int, default=1024); ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--id-drop', type=float, default=0.1); ap.add_argument('--rank-frac', type=float, default=0.25); ap.add_argument('--rank-w', type=float, default=0.1)
    ap.add_argument('--val', type=int, default=1, help='最後の何シャードを検証に取っておくか（シャードが 2 つ以上のとき）')
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--max-seconds', type=float, default=0)
    ap.add_argument('--ref', default='', help='元のモデル（拡張子なし）。--kl-w と合わせて、出力がここから離れすぎないようにする')
    ap.add_argument('--kl-w', type=float, default=0, help='元のモデルとの出力（ロジット）の二乗のずれを損失に足す重み（既定 0 = 足さない）')
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get('TORCH_THREADS') or 8))  # HAKUSAN の bench で 8 スレッドが 64 の 5 倍速かった
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    meta, w = read_model(a.init)
    net = Net(meta); net.load(w)
    paths = find_shards(a.shards)
    nval = a.val if len(paths) >= 2 else 0
    train_p, val_p = paths[:len(paths) - nval], paths[len(paths) - nval:]
    val = [load_shard(p) for p in val_p]
    ref = None
    if a.kl_w > 0 and a.ref:
        ref = Net(read_model(a.ref)[0]); ref.load(read_model(a.ref)[1])
    opt = torch.optim.Adam(net.parameters(), lr=a.lr)
    t0 = time.time(); seen = 0; total = a.epochs * len(train_p); step = 0
    print(f'シャード {len(train_p)}（検証 {len(val_p)}）、スレッド {torch.get_num_threads()}', flush=True)
    for ep in range(a.epochs):
        for si in rng.permutation(len(train_p)):
            A = load_shard(train_p[si])
            D = len(A['decGame'])
            perm = rng.permutation(D)
            lr = a.lr * (1 - 0.9 * step / max(total, 1)); step += 1
            for g in opt.param_groups: g['lr'] = lr
            sr = sk = nb = 0
            for i in range(0, D, a.batch):
                sel = perm[i:i + a.batch]
                rank = (A['decSource'][sel] == 0) & (rng.random(len(sel)) < a.rank_frac)
                b = build_batch(A, sel, rank)
                mask = (torch.rand(net.V) >= a.id_drop).float()
                lg = net(b, mask)
                reg, rk = losses(lg, b, a.rank_w)
                loss = reg + a.rank_w * rk
                if ref is not None:
                    with torch.no_grad(): lr_ = ref(b, mask)
                    loss = loss + a.kl_w * ((lg - lr_) ** 2).mean()
                opt.zero_grad(); loss.backward()
                nn.utils.clip_grad_norm_(net.parameters(), 5.0)
                opt.step()
                sr += reg.item(); sk += float(rk.detach()); nb += 1; seen += len(sel)
            print(f'epoch {ep} shard {si}: 回帰 {sr / nb:.4f} 順位 {sk / nb:.4f}  累計 {seen} サンプル {seen / (time.time() - t0):.0f}/秒', flush=True)
            if a.max_seconds and time.time() - t0 > a.max_seconds: break
    if val:
        r, acc = evaluate(net, val, a.batch)
        print(f'検証: 回帰 {r:.4f}（結果を 0.5 と置いた基準 0.6931）、さいきょうの手との一致 {acc:.3f}', flush=True)
    write_model(a.out, meta, net.weights())
    print(f'書き出し {a.out}.bin/.json  {time.time() - t0:.1f} 秒  samples={seen}', flush=True)


if __name__ == '__main__':
    main()
