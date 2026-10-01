#!/usr/bin/env python3
"""旧絵と新絵を左右に並べた見比べ画像を、本部の .audit/deck-art-<拡張>-<n>.png に書く。
    python3 tools/art/compare_sheet.py --set intrigue        # 1 つの拡張
    python3 tools/art/compare_sheet.py --set base gold crier # 指定したものだけ
旧絵は、tools/art で最初に描き直す前の版（OLD_REV）から取る。
1 行: カード名 | 旧（半分の大きさ）| 旧（幅 60px）| 新（半分）| 新（幅 60px）
"""
import io
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scenes  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(ROOT)), 't-of.github.io', '.audit')
FONT = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 15)
BIG = (224, 160)
SMALL = (60, 43)
LABEL_W = 120
PAD = 8
ROW_H = BIG[1] + PAD
PER_SHEET = 11
BG = (24, 23, 28)
OLD_REV = '55ad6bc'  # 生成で描き直す前の最後の版


def names():
    out = {}
    for f in sorted(os.listdir(ROOT)):
        if not (f.startswith('cards-') and f.endswith('.js')):
            continue
        src = open(os.path.join(ROOT, f), encoding='utf-8').read()
        for m in re.finditer(r"id: '([a-z_]+)',\s*name: '([^']+)'", src):
            out[m.group(1)] = m.group(2)
        for m in re.finditer(r"\w+\('([a-z_0-9]+)', '([^']+)'", src):  # project('j_…', '名前', …) や way('w_…', …)
            out.setdefault(m.group(1), m.group(2))
    return out


def old_image(cid):
    data = subprocess.run(['git', '-C', ROOT, 'show', f'{OLD_REV}:art/{cid}.png'], capture_output=True).stdout
    return Image.open(io.BytesIO(data)).convert('RGB') if data else Image.new('RGB', (448, 320))


def row(cid, label):
    w = LABEL_W + (BIG[0] + SMALL[0] + PAD * 2) * 2 + PAD
    im = Image.new('RGB', (w, ROW_H), BG)
    d = ImageDraw.Draw(im)
    d.text((8, ROW_H // 2 - 18), label, fill=(235, 230, 220), font=FONT)
    d.text((8, ROW_H // 2 + 2), cid, fill=(140, 135, 128), font=FONT)
    x = LABEL_W
    for src in (old_image(cid), Image.open(os.path.join(ROOT, 'art', f'{cid}.png')).convert('RGB')):
        im.paste(src.resize(BIG, Image.NEAREST), (x, PAD // 2))
        im.paste(src.resize(SMALL, Image.LANCZOS), (x + BIG[0] + PAD, PAD // 2 + BIG[1] - SMALL[1]))
        x += BIG[0] + SMALL[0] + PAD * 2
    return im


def main():
    argv = sys.argv[1:]
    name = 'base'
    if '--set' in argv:
        i = argv.index('--set')
        name = argv[i + 1]
        del argv[i:i + 2]
    ids = argv or list(scenes.SETS[name])
    nm = names()
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = [row(cid, nm.get(cid, cid)) for cid in ids]
    head_h = 26
    for n, i in enumerate(range(0, len(rows), PER_SHEET), 1):
        chunk = rows[i:i + PER_SHEET]
        sheet = Image.new('RGB', (chunk[0].width, head_h + ROW_H * len(chunk)), BG)
        d = ImageDraw.Draw(sheet)
        d.text((LABEL_W, 4), '旧', fill=(200, 195, 185), font=FONT)
        d.text((LABEL_W + BIG[0] + SMALL[0] + PAD * 2, 4), '新', fill=(200, 195, 185), font=FONT)
        for j, r in enumerate(chunk):
            sheet.paste(r, (0, head_h + j * ROW_H))
        path = os.path.join(OUT_DIR, f'deck-art-{name}-{n}.png')
        sheet.save(path)
        print(path)


if __name__ == '__main__':
    main()
