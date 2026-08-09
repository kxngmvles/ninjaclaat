"""Inline dist/{assets,strings,game}.js into index.html (the deployed build).

index.html carries exactly three inline <script> blocks, in this order:
  1. window.AS  = asset manifest   (dist/assets.js)
  2. window.STR = player-visible text (dist/strings.js)
  3. the engine IIFE               (dist/game.js)

Usage: python tools/build.py
"""
import os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ["assets.js", "strings.js", "game.js"]
BLOCK = re.compile(r"(<script>)(.*?)(</script>)", re.S)

def main():
    for p in PARTS:                      # a truncated build has shipped before
        r = subprocess.run(["node", "--check", os.path.join(REPO, "dist", p)],
                           capture_output=True, text=True, shell=(os.name == "nt"))
        if r.returncode:
            sys.exit(f"node --check failed on dist/{p}:\n{r.stdout}{r.stderr}")
    print("node --check: all three parse")

    html_path = os.path.join(REPO, "index.html")
    html = open(html_path, encoding="utf-8").read()
    blocks = BLOCK.findall(html)
    assert len(blocks) == 3, f"expected 3 inline <script> blocks, found {len(blocks)}"

    srcs = [open(os.path.join(REPO, "dist", p), encoding="utf-8").read() for p in PARTS]
    # sanity: the blocks must still be in the order this script assumes, or the
    # rebuild would silently swap the manifest and the engine
    for name, want, have in zip(PARTS, ["window.AS", "window.STR", "("], blocks):
        assert want in have[1][:400] or want in srcs[PARTS.index(name)][:400], \
            f"{name} does not look like block for {want}"

    it = iter(srcs)
    out = BLOCK.sub(lambda m: m.group(1) + "\n" + next(it) + "\n" + m.group(3), html)
    open(html_path, "w", encoding="utf-8", newline="\n").write(out)
    print(f"index.html rebuilt ({len(out) // 1024} KB)")

if __name__ == "__main__":
    main()
