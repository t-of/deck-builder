"""重みの読み書き。ai/model.json・ai/model.bin と同じ形（float16、shapes の順、Linear は [出, 入]）。
  read_model(prefix) → (meta, {名前: float32 の ndarray})    prefix は 'ai/model' のように拡張子なし
  write_model(prefix, meta, weights)                        weights は名前 → ndarray（float32 でよい）
"""
import json
import numpy as np


def read_model(prefix):
    meta = json.load(open(prefix + '.json'))
    raw = np.fromfile(prefix + '.bin', dtype='<f2')
    w, off = {}, 0
    for name, shape in meta['shapes'].items():
        n = int(np.prod(shape))
        w[name] = raw[off:off + n].astype(np.float32).reshape(shape)
        off += n
    assert off == raw.size, f'model.bin の大きさが model.json と合わない（{off} と {raw.size}）'
    return meta, w


def write_model(prefix, meta, w):
    parts = []
    for name, shape in meta['shapes'].items():
        a = np.asarray(w[name], dtype=np.float32)
        assert list(a.shape) == list(shape), (name, a.shape, shape)
        parts.append(np.clip(a, -65504, 65504).astype('<f2').ravel())
    np.concatenate(parts).tofile(prefix + '.bin')
    json.dump(meta, open(prefix + '.json', 'w'), ensure_ascii=False, separators=(',', ':'))
