"""Extract smooth sprite frames from one of Kemar's recorded move clips.

The clips are 1440x1440 on the rose-pink ~#DF1461 background, ~73 frames with
idle padding before/after the actual move. This:
  - keys the rose-pink out (keeps the green energy trail),
  - finds the ACTIVE window (where the swing actually happens) by frame-to-frame
    motion, so we drop the dead idle padding,
  - union-crops every kept frame to one shared box (no size jitter),
  - normalizes to a reference sprite's BODY height,
  - samples up to N frames evenly across the window.

Usage: python tools/video_to_frames.py anim_src/slash_1.mp4 slash1 --ref nc_idle --n 14
"""
import argparse, os, sys
import numpy as np
import imageio.v3 as iio
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slice_sheet import body_height, key_background  # noqa
REF_DIR = r"C:\Users\kemar\OneDrive\Desktop\NinjaclaatGodot\assets\web"

def key_rose(f):
    r, g, b = [f[..., i].astype(np.int16) for i in range(3)]
    pink = (r > 150) & (g < 115) & ((r - g) > 78) & ((b - g) > -6) & (b < 200)
    lab, _ = ndimage.label(pink)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    border.discard(0)
    bg = np.isin(lab, list(border)) | pink            # rose is bright + saturated; also kill interior pockets
    out = np.dstack([f[..., :3].astype(np.uint8), np.where(bg, 0, 255).astype(np.uint8)])
    # despill the thin pink fringe toward luminance (keeps skin/dread colour sane)
    fringe = ndimage.binary_dilation(bg, iterations=2) & (~bg) & pink
    lum = (0.30 * r + 0.59 * g + 0.11 * b)
    for c in range(3):
        ch = out[..., c].astype(np.float32)
        ch[fringe] = ch[fringe] * 0.4 + lum[fringe] * 0.6
        out[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out_prefix")
    ap.add_argument("--ref", default="nc_idle")
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--outdir", default="anim_src/sliced")
    ap.add_argument("--pad", type=int, default=2)
    args = ap.parse_args()

    raw = list(iio.imiter(args.video))
    keyed = [key_rose(f) for f in raw]
    alpha = np.stack([k[..., 3] > 24 for k in keyed])

    # motion = change in the keyed image between consecutive frames
    motion = np.array([0.0] + [np.abs(keyed[i][..., :3].astype(np.int16)[alpha[i] | alpha[i - 1]]
                                      - keyed[i - 1][..., :3].astype(np.int16)[alpha[i] | alpha[i - 1]]).mean()
                               if (alpha[i] | alpha[i - 1]).any() else 0.0
                               for i in range(1, len(keyed))])
    thr = motion.max() * 0.30
    active = np.where(motion > thr)[0]
    lo = max(0, active.min() - args.pad)
    hi = min(len(keyed) - 1, active.max() + args.pad)
    print(f"{os.path.basename(args.video)}: {len(keyed)} frames, active window {lo}-{hi}")

    # union crop across the window
    x0 = y0 = 10 ** 9; x1 = y1 = -1
    for i in range(lo, hi + 1):
        ys, xs = np.where(alpha[i])
        if not len(ys):
            continue
        x0 = min(x0, xs.min()); x1 = max(x1, xs.max())
        y0 = min(y0, ys.min()); y1 = max(y1, ys.max())
    pad = 6
    x0, y0 = max(x0 - pad, 0), max(y0 - pad, 0)
    x1, y1 = x1 + pad, y1 + pad

    # scale to the reference body height
    ra = key_background(np.array(Image.open(os.path.join(REF_DIR, args.ref + ".png")).convert("RGBA")))
    ref_body = body_height(ra)
    idxs = [lo + round(k * (hi - lo) / (args.n - 1)) for k in range(args.n)] if hi > lo else [lo]
    idxs = sorted(set(idxs))
    # one scale for the whole set (from the tallest body in the window)
    bodies = [body_height(keyed[i][y0:y1 + 1, x0:x1 + 1]) for i in idxs]
    scale = ref_body / max(bodies)
    os.makedirs(args.outdir, exist_ok=True)
    for j, i in enumerate(idxs, 1):
        crop = keyed[i][y0:y1 + 1, x0:x1 + 1]
        im = Image.fromarray(crop)
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        im.save(os.path.join(args.outdir, f"{args.out_prefix}{j}.png"))
    print(f"  wrote {len(idxs)} frames -> {args.out_prefix}1..{len(idxs)}  ({im.width}x{im.height})")

if __name__ == "__main__":
    main()
