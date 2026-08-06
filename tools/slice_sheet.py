"""Slice a generated sprite-sheet strip into game-ready frames.

Handles what image models actually produce: figures at uneven spacing, slightly
different sizes, on a flat background. It finds each figure by looking for
columns of pure background, keys the background out, then normalizes every
frame against a reference sprite already in the game so the body stays ONE
size and the feet sit on ONE ground line (that's what stops the sprite from
growing/shrinking between frames).

Usage:
  python tools/slice_sheet.py <sheet.png> <out_prefix> [--ref goonA_idle] [--n 6]

Example:
  python tools/slice_sheet.py anim_src/goonA_walk_sheet.png goonA_walk --ref goonA_idle
    -> goonA_walk1.png .. goonA_walk6.png  (repo root, ready for assets.js)
"""
import argparse
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the live game loads most sprites from the CDN, so the only local copies of the
# originals are the Godot project's asset backup — use it for size references
REF_DIR = r"C:\Users\kemar\OneDrive\Desktop\NinjaclaatGodot\assets\web"

def key_background(a):
    """Alpha out the flat background (magenta/green/grey) via border flood."""
    if a.shape[2] == 4 and a[..., 3].min() == 0:
        return a                                   # already transparent
    r = a[..., 0].astype(np.float32)
    g = a[..., 1].astype(np.float32)
    b = a[..., 2].astype(np.float32)
    # sample the border to learn the bg colour
    border = np.concatenate([a[0, :, :3], a[-1, :, :3], a[:, 0, :3], a[:, -1, :3]])
    bg = np.median(border.astype(np.float32), axis=0)
    dist = np.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)
    # tolerant match (models render gradients/vignettes in the backdrop), plus
    # the whole magenta/crimson family so any pink shade keys out
    # magenta/crimson signature: red high AND blue lifted ABOVE green. Warm
    # skin and brown hair have blue BELOW green, so they survive — a looser
    # rule ate the face and turned hands lime.
    pink_family = (r - g > 40) & (b - g > 8) & (r > 100)
    close = (dist < 90) | pink_family
    lab, _ = ndimage.label(close)
    edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    edge_labels.discard(0)
    bgmask = np.isin(lab, list(edge_labels))
    # ALSO remove enclosed background pockets (between legs, under an arm) that
    # the border flood can't reach: any pixel very close to the bg colour, or
    # strongly magenta, anywhere in the frame. Character skin/garb sit far from
    # the bright bg hue, so this is safe.
    strong_pink = (r - g > 90) & (b - g > 30) & (r > 140)
    bgmask |= (dist < 60) | strong_pink
    out = a.copy()
    if out.shape[2] == 3:
        out = np.dstack([out, np.full(out.shape[:2], 255, np.uint8)])
    # despill ONLY the thin fringe touching the background, and only pixels
    # that are actually pink-contaminated — otherwise warm skin tones (which
    # sit "near" magenta in RGB) get pushed green
    # desaturate toward luminance instead of subtracting the bg colour —
    # subtracting amplified green and turned skin lime
    fringe = ndimage.binary_dilation(bgmask, iterations=2) & (~bgmask) & pink_family
    lum = (0.30 * r + 0.59 * g + 0.11 * b)
    for c in range(3):
        ch = out[..., c].astype(np.float32)
        ch[fringe] = ch[fringe] * 0.35 + lum[fringe] * 0.65
        out[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(bgmask, 0, 255)
    return out

def body_height(a):
    """Height from the feet to the top of the BODY, ignoring thin protrusions
    like a raised bat or machete (those inflate the bounding box and would
    otherwise shrink the character when normalizing)."""
    al = a[..., 3] > 24
    ys = np.where(al)[0]
    if not len(ys):
        return 1
    rows = al.sum(axis=1)
    wide = np.where(rows > rows.max() * 0.22)[0]
    top = wide.min() if len(wide) else ys.min()
    return max(1, int(ys.max() - top))

def _content_range(profile, floor):
    occ = np.where(profile > floor)[0]
    return (occ[0], occ[-1] + 1) if len(occ) else (0, len(profile))

def seam_cut(profile, x0, x1, n):
    """Cut [x0,x1) into n slices at the thinnest points of `profile` near even
    spacing. Robust to touching figures (evenly-laid-out sheets)."""
    step = (x1 - x0) / n
    cuts = [x0]
    for k in range(1, n):
        ideal = int(x0 + k * step)
        win = max(6, int(step * 0.30))
        lo, hi = max(x0 + 4, ideal - win), min(x1 - 4, ideal + win)
        cuts.append(lo + int(np.argmin(profile[lo:hi])) if hi > lo else ideal)
    cuts.append(x1)
    return [(cuts[k], cuts[k + 1]) for k in range(n)]

def component_figures(a, expect):
    """Split a row into `expect` figures WITHOUT ever cutting through artwork.

    Seam cells decide which figure a blob belongs to (by its centroid), but the
    blob is then taken whole. So a machete overhanging into the neighbour's
    column stays with its owner instead of being chopped (which left a stray
    blade tip in the next frame), and a detached blade is absorbed by the
    figure whose cell it sits in rather than becoming its own "frame".
    """
    alpha = a[..., 3] > 24
    if not alpha.any():
        return None
    colsum = alpha.sum(axis=0)
    x0, x1 = _content_range(colsum, max(2, int(a.shape[0] * 0.006)))
    cells = seam_cut(colsum, x0, x1, expect)
    lab, n = ndimage.label(alpha)
    if n < 1:
        return None
    sizes = ndimage.sum(alpha, lab, range(1, n + 1))
    groups = [np.zeros_like(alpha) for _ in range(expect)]
    for i in range(1, n + 1):
        if sizes[i - 1] < alpha.size * 0.0004:      # speck
            continue
        m = lab == i
        cx = ndimage.center_of_mass(m)[1]
        k = min(range(expect), key=lambda j: 0 if cells[j][0] <= cx < cells[j][1]
                else min(abs(cx - cells[j][0]), abs(cx - cells[j][1])))
        groups[k] |= m
    figs = []
    for m in groups:
        if not m.any():
            return None                              # a cell came out empty
        xs = np.where(m.any(axis=0))[0]
        figs.append((int(xs.min()), int(xs.max()) + 1, m))
    return figs

def find_figures(a, expect=None):
    """Split a row band into figures. With `expect`, cut at thinnest seams
    (handles touching poses); otherwise split on all-background columns."""
    alpha = a[..., 3] > 24
    colsum = alpha.sum(axis=0)
    floor = max(2, int(a.shape[0] * 0.006))
    if expect:
        x0, x1 = _content_range(colsum, floor)
        return seam_cut(colsum, x0, x1, expect)
    runs, start = [], None
    for x, occ in enumerate(colsum > floor):
        if occ and start is None:
            start = x
        elif not occ and start is not None:
            runs.append((start, x)); start = None
    if start is not None:
        runs.append((start, len(colsum)))
    return [(s, e) for s, e in runs if (e - s) > a.shape[1] * 0.008]

def find_rows(a):
    """Split a grid sheet into horizontal bands of content (rows of figures)
    separated by all-background rows. Single-row sheets return one band."""
    alpha = a[..., 3] > 24
    rowsum = alpha.sum(axis=1)
    thresh = max(2, int(a.shape[1] * 0.004))
    occ = rowsum > thresh
    bands, start = [], None
    for y, o in enumerate(occ):
        if o and start is None:
            start = y
        elif not o and start is not None:
            bands.append((start, y)); start = None
    if start is not None:
        bands.append((start, len(occ)))
    # drop thin bands, merge bands split by a small vertical gap (raised arm)
    bands = [(s, e) for s, e in bands if (e - s) > a.shape[0] * 0.06]
    merged = []
    for s, e in bands:
        if merged and s - merged[-1][1] < a.shape[0] * 0.03:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("out_prefix")
    ap.add_argument("--ref", default=None,
                    help="existing sprite key to match size against, e.g. goonA_idle")
    ap.add_argument("--n", type=int, default=None, help="expected frame count (total)")
    ap.add_argument("--cols", type=int, default=None, help="figures per row (grids)")
    ap.add_argument("--start", type=int, default=1, help="first frame number")
    ap.add_argument("--outdir", default=REPO)
    args = ap.parse_args()

    sheet = np.array(Image.open(args.sheet).convert("RGBA"))
    sheet = key_background(sheet)
    figs = []          # (x0,x1,y0,y1) in reading order
    if args.cols and args.n:
        # known grid: seam-cut the content box into rows x cols (deterministic)
        nrows = args.n // args.cols
        rowsum = (sheet[..., 3] > 24).sum(axis=1)
        y0, y1 = _content_range(rowsum, max(2, int(sheet.shape[1] * 0.006)))
        bands = seam_cut(rowsum, y0, y1, nrows)
        for (ys, ye) in bands:
            band = sheet[ys:ye]
            cf = component_figures(band, args.cols)
            if cf:                       # blob split: weapons can overhang safely
                for (xs, xe, m) in cf:
                    figs.append((xs, xe, ys, ye, m))
            else:
                for (xs, xe) in find_figures(band, args.cols):
                    figs.append((xs, xe, ys, ye, None))
        print(f"{os.path.basename(args.sheet)}: grid {nrows}x{args.cols}, {len(figs)} figures")
    else:
        rows = find_rows(sheet)
        per_row = args.n // len(rows) if args.n else None
        for (ys, ye) in rows:
            band = sheet[ys:ye]
            cf = component_figures(band, per_row) if per_row else None
            if cf:
                for (xs, xe, m) in cf:
                    figs.append((xs, xe, ys, ye, m))
            else:
                for (xs, xe) in find_figures(band, per_row):
                    figs.append((xs, xe, ys, ye, None))
        print(f"{os.path.basename(args.sheet)}: {len(rows)} row(s), {len(figs)} figures")

    # reference height: match the family's existing idle sprite so the new
    # frames drop in at the same body scale
    ref_h = None
    if args.ref:
        rp = os.path.join(REF_DIR, args.ref + ".png")
        if os.path.exists(rp):
            # originals sit on a magenta background, so key it before measuring
            ra = key_background(np.array(Image.open(rp).convert("RGBA")))
            ref_h = body_height(ra)
            print(f"  ref {args.ref}: content height {ref_h}px")
        else:
            print(f"  ! ref {args.ref}.png not found, keeping native size")

    # Scale by BODY height (feet -> top of the torso/head), NOT the bounding
    # box. A raised bat or machete makes the bbox much taller than the figure,
    # and scaling that to the reference shrank the character (~10% on the bat
    # goon's overhead swing). body_height() ignores thin protrusions.
    def cut_seg(f):
        x0, x1, y0, y1, m = f
        seg = sheet[y0:y1, x0:x1].copy()
        if m is not None:                       # keep ONLY this figure's pixels
            seg[..., 3] = np.where(m[:, x0:x1], seg[..., 3], 0)
        return seg

    heights = []
    for f in figs:
        heights.append(body_height(cut_seg(f)))
    tallest = max(heights)
    scale = (ref_h / tallest) if ref_h else 1.0

    for i, (f, h) in enumerate(zip(figs, heights)):
        seg = cut_seg(f)
        ys, xs = np.where(seg[..., 3] > 24)
        seg = seg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        im = Image.fromarray(seg)
        if scale != 1.0:
            im = im.resize((max(1, round(im.width * scale)),
                            max(1, round(im.height * scale))), Image.LANCZOS)
        name = f"{args.out_prefix}{args.start + i}.png"
        im.save(os.path.join(args.outdir, name))
        print(f"  {name}: {im.width}x{im.height}")

if __name__ == "__main__":
    main()
