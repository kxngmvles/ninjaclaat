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
    # Models like to draw a baseline under the row even when told not to. A thin
    # dark rule spanning most of the sheet is never character art — a body lying
    # down covers a fraction of the width — and if left in it welds every figure
    # into one blob and pads every frame's bbox.
    keep = ~bgmask
    lum = (0.30 * r + 0.59 * g + 0.11 * b)
    wide = (keep.sum(axis=1) > a.shape[1] * 0.72)
    for y in np.where(wide)[0]:
        if lum[y][keep[y]].mean() < 70:
            out[y, :, 3] = 0
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

def foot_anchor(seg, mode="foot"):
    """(x, y) of the frame's ground contact: y = lowest opaque row, x = median
    column across the bottom few rows. Using only the contact rows means a
    kicking leg thrown out mid-air doesn't drag the anchor sideways the way a
    bbox centre or a full centre-of-mass does.

    mode="centre" anchors on the centre of mass instead — for airborne frames
    (a flip) there is no ground contact, and the game is already moving the
    sprite with jump physics, so the pose has to spin in place."""
    al = seg[..., 3] > 24
    ys, xs = np.where(al)
    if not len(ys):
        return seg.shape[1] // 2, seg.shape[0] - 1
    if mode == "centre":
        return int(np.median(xs)), int(np.median(ys))
    ymax = int(ys.max())
    band = max(1, int(round(seg.shape[0] * 0.06)))
    sel = ys >= ymax - band
    return int(np.median(xs[sel])), ymax

def bleed_rgb(a):
    """Flood transparent pixels with the colour of the nearest opaque one.

    Keying only clears ALPHA — the cleared pixels keep their magenta RGB. Any
    later resample (every set gets scaled to the reference height) blends those
    hidden magenta values back in across the silhouette, which is where the
    purple fringing on the sliced frames was coming from. Nothing here changes
    a visible pixel; it only fixes what the filter picks up from behind them."""
    op = a[..., 3] > 0
    if not op.any() or op.all():
        return a
    idx = ndimage.distance_transform_edt(~op, return_distances=False, return_indices=True)
    out = a.copy()
    for c in range(3):
        out[..., c] = a[..., c][tuple(idx)]
    return out

def defringe(a, strength=1.0):
    """Flatten any surviving magenta-family pixel to its own luminance.

    key_background only despills a 2px fringe, which is enough for a character
    whose silhouette is busy but not for a hard-edged object: the generated
    props all kept a visible pink outline along ropes, rims and edges. Objects
    have no genuinely red or pink parts, so anything still reading magenta is
    contamination. Do NOT use this on a character with red clothing."""
    r, g, b = [a[..., i].astype(np.int16) for i in range(3)]
    m = (a[..., 3] > 0) & (b - g > 10) & (r - g > 6)
    if not m.any():
        return a
    lum = (0.30 * r + 0.59 * g + 0.11 * b)
    out = a.copy()
    for c in range(3):
        ch = out[..., c].astype(np.float32)
        ch[m] = ch[m] * (1 - strength) + lum[m] * strength
        out[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
    return out

def body_centre(seg):
    """Horizontal centre of the TORSO/legs — the widest rows — so an outflung
    arm, blade or pipe doesn't drag the centre off the character."""
    al = seg[..., 3] > 24
    rows = al.sum(axis=1)
    if not rows.max():
        return seg.shape[1] / 2
    wide = np.where(rows > rows.max() * 0.35)[0]
    cols = np.where(al[wide].any(axis=0))[0]
    return float(np.median(cols)) if len(cols) else seg.shape[1] / 2

def union_pack(segs, mode="foot"):
    """Put every frame on ONE canvas, aligned by its foot anchor.

    Per-frame cropping is what makes a sliced set jitter: each frame gets its
    own bbox, so the figure snaps around as limbs change the box. Aligning on
    the ground contact instead keeps the feet planted and lets the body move
    within a fixed frame — same property the video pipeline gets from union
    cropping, but it survives sheets whose cells aren't evenly spaced."""
    anchors = [foot_anchor(s, mode) for s in segs]
    # Frames stay locked to each other by the ground anchor (that's what stops
    # the jitter), but the SET is then shifted so the average torso lands on the
    # canvas centre — the engine draws every sprite centred on the entity's x,
    # and a body sitting 25px to one side of its own hitbox makes the hero look
    # like he is swinging past enemies he cannot actually reach. Centring each
    # frame's body individually would bring the jitter straight back.
    m = float(np.mean([body_centre(s) - ax for s, (ax, _) in zip(segs, anchors)]))
    need_l = max(ax for ax, _ in anchors)
    need_r = max(s.shape[1] - ax for s, (ax, _) in zip(segs, anchors))
    half = int(np.ceil(max(need_l + m, need_r - m)))
    ap = int(round(half - m))                       # where the anchor sits
    up = max(ay + 1 for _, ay in anchors)
    down = max(s.shape[0] - ay - 1 for s, (_, ay) in zip(segs, anchors))
    if mode == "centre":            # airborne: centre vertically too
        up = down = max(up, down)
    W, H = half * 2, up + down      # foot mode keeps the anchor on the baseline
    out = []
    for s, (ax, ay) in zip(segs, anchors):
        canvas = np.zeros((H, W, 4), np.uint8)
        x0, y0 = ap - ax, up - ay - 1
        canvas[y0:y0 + s.shape[0], x0:x0 + s.shape[1]] = s
        out.append(canvas)
    return out

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
    lab, n = ndimage.label(alpha)
    if n < expect:
        return None
    sizes = ndimage.sum(alpha, lab, range(1, n + 1))
    # The `expect` LARGEST blobs are the bodies. Anchoring on them beats cutting
    # the row into even cells: models space figures unevenly and crowd them to
    # one side, and an even cut then hands one figure's dropped weapon (or a
    # boot) to its neighbour and leaves another cell empty.
    cores = sorted((int(i) + 1 for i in np.argsort(sizes)[::-1][:expect]),
                   key=lambda i: ndimage.center_of_mass(lab == i)[1])
    groups = [lab == i for i in cores]
    cxs = [ndimage.center_of_mass(g)[1] for g in groups]
    for i in range(1, n + 1):
        if i in cores or sizes[i - 1] < alpha.size * 0.00002:   # core, or speck
            continue
        m = lab == i                                # dropped weapon / stray limb
        cx = ndimage.center_of_mass(m)[1]           # -> joins the nearest body
        groups[min(range(expect), key=lambda j: abs(cx - cxs[j]))] |= m
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

    segs = []
    for f in figs:
        seg = cut_seg(f)
        ys, xs = np.where(seg[..., 3] > 24)
        segs.append(seg[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    segs = union_pack(segs)

    for i, seg in enumerate(segs):
        im = Image.fromarray(bleed_rgb(seg))
        if scale != 1.0:
            im = im.resize((max(1, round(im.width * scale)),
                            max(1, round(im.height * scale))), Image.LANCZOS)
        name = f"{args.out_prefix}{args.start + i}.png"
        im.save(os.path.join(args.outdir, name))
    print(f"  wrote {len(segs)} frames -> {args.out_prefix}{args.start}.."
          f"{args.start + len(segs) - 1}  ({im.width}x{im.height}, foot-aligned)")

if __name__ == "__main__":
    main()
