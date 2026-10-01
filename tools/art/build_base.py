#!/usr/bin/env python3
"""基本セット（cards-base.js の 39 枚）と a_*.png 5 枚を描く。
    python3 tools/art/build_base.py            # art/ に書く
    python3 tools/art/build_base.py --check    # 2 回描いてハッシュが同じか、パレット外の色がないかだけ確かめる
    python3 tools/art/build_base.py gold crier # 指定したものだけ書く
"""
import hashlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import Canvas, check_palette  # noqa: E402
import scenes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(ROOT, 'art')


def png_bytes(cid):
    buf = io.BytesIO()
    scenes.render(cid, Canvas).image().save(buf, format='PNG', optimize=True)
    return buf.getvalue()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ids = args or list(scenes.SCENES)
    if '--check' in sys.argv:
        for cid in ids:
            a, b = png_bytes(cid), png_bytes(cid)
            assert hashlib.sha256(a).digest() == hashlib.sha256(b).digest(), f'{cid}: 2 回の結果が違う'
        print(f'{len(ids)} 枚: 2 回描いて同じ')
        return
    total = 0
    for cid in ids:
        path = os.path.join(ART, f'{cid}.png')
        data = png_bytes(cid)
        with open(path, 'wb') as f:
            f.write(data)
        check_palette(path)
        total += len(data)
    print(f'{len(ids)} 枚を書いた。パレット外の色なし。平均 {total / len(ids) / 1024:.1f} KB')


if __name__ == '__main__':
    main()
