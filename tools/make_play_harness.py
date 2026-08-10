"""Build _play.html: the real game, but drivable in a hidden browser tab.

The Browser pane doesn't composite when it isn't displayed, so
requestAnimationFrame never fires and the canvas stays black — which looks
exactly like broken draw code. This harness is index.html with rAF shimmed onto
a timer (timers keep running while hidden) and the canvas pinned at 960x540,
so a headless tab renders real frames that can be snapshotted.
"""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()

SHIM = """<script>
// timers keep running in a hidden tab; rAF does not
window.requestAnimationFrame=f=>setTimeout(()=>f(performance.now()),16);
window.cancelAnimationFrame=id=>clearTimeout(id);
// The game sizes its canvas to the window, so a snapshot is only as big as the
// viewport. Don't fight it by pinning canvas.width — that clobbers the game's
// own transform and renders the world into a corner. Resize the VIEWPORT instead
// (mcp resize_window / a real window) and the game scales itself correctly.
// hand a frame to tools/shot_sink.py
window.__snap=(name)=>{const c=document.querySelector('canvas');
  return fetch('http://127.0.0.1:8799/shot?name='+name,
    {method:'POST',body:c.toDataURL('image/jpeg',0.85)}).then(r=>r.text());};
// walk a list of x positions, letting the world settle at each one
window.__tour=async(xs,ms)=>{const o=[];for(const x of xs){__dbg.warp(x);
  await new Promise(r=>setTimeout(r,ms||300)); await __snap('g'+x); o.push(x);} return o.join(',');};
</script>"""

i = h.index("<script")
out = h[:i] + SHIM + "\n" + h[i:]
open(os.path.join(REPO, "_play.html"), "w", encoding="utf-8", newline="\n").write(out)
print(f"_play.html written ({len(out)//1024} KB)")
