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
from slice_sheet import body_height, key_background, body_centre, bleed_rgb  # noqa
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
    # The rose ground-contact streak under the figure survives the test above:
    # it is the same hue but darker, so the r>150 gate misses it. Test by ratio
    # instead, and ONLY in the bottom band — the maroon dreads sit within ~3
    # degrees of the background hue, so a global ratio rule eats the hair.
    shadow = (r - g > r * 0.42) & (b - g > 20) & (b < r * 0.85) & (r > 45)
    shadow[:int(f.shape[0] * 0.86)] = False
    out[..., 3] = np.where(shadow, 0, out[..., 3])
    return out

def key_magenta(f):
    """Key a model-generated clip shot on magenta #FF00FF.

    Video needs more than the still-sheet keyer: motion blur smears the
    character THROUGH the background, leaving contaminated bands far wider than
    the thin fringe key_background despills — a whole swinging pipe came out
    purple. Anything still reading pink after keying is contamination here, so
    it gets flattened to its own luminance.

    Only safe because these clips are of characters with no genuinely red or
    pink parts. Do not reuse for one that has (the knife fighter's bandana).
    """
    a = key_background(np.dstack([f[..., :3], np.full(f.shape[:2], 255, np.uint8)]))
    r, g, b = [a[..., i].astype(np.int16) for i in range(3)]
    # Thresholds run LOW on purpose: the surviving smear is DARK magenta, and
    # over dark clothing it skews violet (blue ends up above red), so the test
    # keys on "blue and red both clearly above green" rather than on a magenta
    # ratio. Navy, teal and blue-grey garments all sit at or below green on
    # blue-minus-green, so they survive.
    spill = (a[..., 3] > 0) & (b - g > 14) & (r - g > 6)
    lum = (0.30 * r + 0.59 * g + 0.11 * b)
    for c in range(3):
        ch = a[..., c].astype(np.float32)
        ch[spill] = lum[spill]
        a[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
    return a

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out_prefix")
    ap.add_argument("--ref", default="nc_idle")
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--outdir", default="anim_src/sliced")
    ap.add_argument("--pad", type=int, default=2)
    ap.add_argument("--bg", choices=("rose", "magenta"), default="rose",
                    help="rose = Kemar's recorded clips; magenta = model-generated video")
    ap.add_argument("--loop", action="store_true",
                    help="cyclic move (walk/run): find ONE stride that loops seamlessly")
    args = ap.parse_args()

    raw = list(iio.imiter(args.video))
    key = key_rose if args.bg == "rose" else key_magenta
    keyed = [key(f) for f in raw]
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

    if args.loop:
        # A walk/run clip contains several strides. Sampling evenly across all of
        # them gives a set that never repeats, so the cycle visibly stutters when
        # the game loops it. Find the ONE stride that closes on itself: the
        # (start, period) whose first and last frames match most closely. Compare
        # frame-to-frame, never against frame 0 — these clips drift.
        # search on 1/8-scale frames — this is a similarity comparison, not a
        # measurement, and at full res it takes minutes
        gray = [(k[::8, ::8, :3].astype(np.float32).mean(axis=2)
                 * (k[::8, ::8, 3] > 24)) for k in keyed]
        best, bestd = None, 1e18
        for period in range(12, 46):
            for st in range(lo, hi - period + 1):
                d = np.abs(gray[st] - gray[st + period]).mean()
                if d < bestd:
                    bestd, best = d, (st, period)
        lo, hi = best[0], best[0] + best[1] - 1
        print(f"  loop: stride of {best[1]} frames at {lo}-{hi} (residual {bestd:.2f})")

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
    crops = [keyed[i][y0:y1 + 1, x0:x1 + 1] for i in idxs]
    # The shared crop box already kills jitter, but it is centred on the CONTENT,
    # not the character — and the engine draws every sprite centred on the
    # entity's x. Shift the whole set (equally, so the motion is preserved) so
    # the average torso sits on the canvas centre.
    shift = int(round(np.mean([body_centre(c) for c in crops]) - crops[0].shape[1] / 2))
    if shift:
        pad = abs(shift) * 2
        padded = []
        for c in crops:
            canvas = np.zeros((c.shape[0], c.shape[1] + pad, 4), np.uint8)
            x0p = pad if shift > 0 else 0
            canvas[:, x0p:x0p + c.shape[1]] = c
            padded.append(canvas)
        crops = padded
    for j, c in enumerate(crops, 1):
        im = Image.fromarray(bleed_rgb(c))
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        im.save(os.path.join(args.outdir, f"{args.out_prefix}{j}.png"))
    print(f"  wrote {len(crops)} frames -> {args.out_prefix}1..{len(crops)}  "
          f"({im.width}x{im.height}, body-centred)")

if __name__ == "__main__":
    main()
