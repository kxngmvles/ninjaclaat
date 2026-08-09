"""Static sanity check on the hand-authored level layouts in dist/game.js.

Layout bugs here are invisible until you walk into them, and a stair run that
ends in mid-air or a "roof" spawn that misses its walkway both look fine in the
source. This parses the platform/wave tables straight out of the engine and
checks the things that have actually broken:

  - every `step` run connects to something walkable at BOTH ends
    (within STEP_UP, or the ground)
  - every wave entry tagged "roof" lands on a real raised platform
  - no platform is authored beyond LEVEL_W

Usage: python tools/check_level.py     (exit code 1 if anything is broken)
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GY, STEP_UP = 474, 46
LEVELS = ["buildHarbour", "buildShipHold", "buildShipDeck", "buildLevel",
          "buildStreet", "buildRoof", "buildCompound", "buildTower"]

def section(src, fn):
    i = src.index(f"function {fn}(")
    j = src.index("waveIdx=0", i)
    return src[i:j]

def platforms(body):
    out = []
    for m in re.finditer(r"\{x:(\d+),\s*(?:y:\d+,\s*)?w:(\d+),\s*top:GROUND_Y-(\d+)([^}]*)\}", body):
        x, w, top, rest = int(m.group(1)), int(m.group(2)), GY - int(m.group(3)), m.group(4)
        kind = "step" if "step:1" in rest else ("deck" if "deck:1" in rest else "solid")
        out.append((x - w / 2, x + w / 2, top, kind, "noland:1" in rest))
    return sorted(out)

def waves(body):
    return re.findall(r'\["(\w+)",\s*(\d+)(?:,\s*"(\w+)")?(?:,\s*"(\w+)")?\]', body)

def level_w(body):
    m = re.search(r"LEVEL_W=(\d+)", body)
    return int(m.group(1)) if m else None

def main():
    src = open(os.path.join(REPO, "dist", "game.js"), encoding="utf-8").read()
    problems = []
    for fn in LEVELS:
        try:
            body = section(src, fn)
        except ValueError:
            continue
        ps, LW = platforms(body), level_w(body)
        land = [p for p in ps if not p[4]]

        # --- stair runs ---
        steps = [p for p in land if p[3] == "step"]
        runs, cur = [], []
        for p in steps:
            if cur and abs(p[0] - cur[-1][1]) <= 2:
                cur.append(p)
            else:
                if cur:
                    runs.append(cur)
                cur = [p]
        if cur:
            runs.append(cur)
        for r in runs:
            for end, label in ((r[0], "left"), (r[-1], "right")):
                edge = end[0] if label == "left" else end[1]
                nb = [p for p in land if p[3] != "step" and p[0] - 8 <= edge <= p[1] + 8
                      and abs(p[2] - end[2]) <= STEP_UP]
                if not (nb or abs(end[2] - (GY - 38)) <= 2):
                    problems.append(f"{fn}: stair run {r[0][0]:.0f}-{r[-1][1]:.0f} "
                                    f"{label} end at height {GY-end[2]} connects to nothing")

        # --- roof spawns ---
        for t, x, mode, tag in waves(body):
            if tag == "roof" or mode == "roof":
                x = int(x)
                if not any(p[0] <= x <= p[1] and p[2] < GY - 110 for p in land):
                    problems.append(f"{fn}: '{t}' roof-spawns at x={x} with no raised platform there")

        # --- runaway platforms ---
        if LW:
            for p in ps:
                if p[1] > LW:
                    problems.append(f"{fn}: platform ends at {p[1]:.0f}, past LEVEL_W={LW}")
        print(f"{fn}: {len(ps)} platforms, {len(runs)} stair run(s), LEVEL_W={LW}")

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  ! " + p)
        sys.exit(1)
    print("\nall level layouts OK")

if __name__ == "__main__":
    main()
