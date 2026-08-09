"""Render a sliced frame set at GAME scale so alignment can be eyeballed.

Frames that look fine at full resolution still jitter in game, because the game
draws them ~120px tall with the feet on one ground line. This lays them out at
that size against the game's background with the ground line drawn through, so
a foot that floats or a body that slides is obvious.

Usage:
  python tools/contact_sheet.py anim_src/sliced/nslash{i}.png --n 28 --out anim_src/out/_nslash.png
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw

HERO_H = 120          # game.js HERO_H
BG = (26, 32, 42)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", help="path with {i}, e.g. anim_src/sliced/kick{i}.png")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--zoom", type=float, default=2.0)
    ap.add_argument("--ref", default=None,
                    help="frame index whose height maps to HERO_H (default: the first)")
    args = ap.parse_args()

    paths = [args.pattern.format(i=args.start + k) for k in range(args.n)]
    ims = [Image.open(p).convert("RGBA") for p in paths]

    # the game sizes every frame by famH(): height relative to the idle frame,
    # so replicate that here rather than fitting each frame to the cell
    ref_h = ims[int(args.ref) - args.start].height if args.ref else ims[0].height
    scale = (HERO_H * args.zoom) / ref_h

    cell_w = max(int(im.width * scale) for im in ims) + 12
    cell_h = int(max(im.height for im in ims) * scale) + 40
    sheet = Image.new("RGBA", (cell_w * len(ims), cell_h), BG + (255,))
    d = ImageDraw.Draw(sheet)
    ground = cell_h - 20
    d.line([(0, ground), (sheet.width, ground)], fill=(90, 105, 120, 255), width=1)

    for k, im in enumerate(ims):
        w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        r = im.resize((w, h), Image.LANCZOS)
        # game draws sprite bottom on the ground line, horizontally centred
        sheet.alpha_composite(r, (k * cell_w + (cell_w - w) // 2, ground - h))
        d.text((k * cell_w + 4, 4), str(args.start + k), fill=(150, 165, 180, 255))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    sheet.save(args.out)
    print(f"{args.out}: {len(ims)} frames, cell {cell_w}x{cell_h}")

if __name__ == "__main__":
    main()
