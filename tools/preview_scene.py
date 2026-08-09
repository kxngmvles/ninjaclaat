"""Render a background-drawing function from dist/game.js to a PNG, offscreen.

The engine is one IIFE, so its draw functions can't be poked at from the page.
This pulls the requested functions OUT of the real source (so what gets checked
is what ships, not a hand-copy that drifts) and drops them into a standalone
page with just enough of the engine's globals to run.

Usage:
  python tools/preview_scene.py drawWarehouse --cam 2900 --seg 1 --out out.html
then open the page and read window.__png (a data: URL).
"""
import argparse, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def grab(src, name):
    """Extract `function name(...)  { ... }` by brace matching."""
    i = src.index(f"function {name}(")
    j = src.index("{", i)
    depth = 0
    for k in range(j, len(src)):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[i:k + 1]
    raise ValueError(f"unbalanced braces in {name}")

def grab_const(src, name):
    m = re.search(rf"^const {name}=\{{.*?\}};", src, re.M | re.S)
    return m.group(0) if m else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fns", nargs="+", help="function names to include; ALL are called, in order")
    ap.add_argument("--cam", type=float, default=0)
    ap.add_argument("--seg", type=int, default=1)
    ap.add_argument("--level", type=int, default=2)
    ap.add_argument("--gaps", default="", help="x1:x2,x1:x2 to draw as pits")
    ap.add_argument("--platforms", default="", help="x:w:top:kind,... kind=deck|step")
    ap.add_argument("--images", default="",
                    help="comma-separated image keys to preload from the repo root")
    ap.add_argument("--out", default="_scene.html")
    args = ap.parse_args()

    src = open(os.path.join(REPO, "dist", "game.js"), encoding="utf-8").read()
    calls = "\n".join(f"{f}();" for f in args.fns)
    imgjs = "[" + ",".join('"%s"' % k for k in args.images.split(",") if k) + "]"
    bodies = "\n".join(grab(src, f) for f in args.fns)

    gaps = [g for g in args.gaps.split(",") if g]
    gapjs = ",".join("{x1:%s,x2:%s}" % tuple(g.split(":")) for g in gaps)
    pfs = [p for p in args.platforms.split(",") if p]
    pfjs = ",".join(
        "{x:%s,w:%s,top:GROUND_Y-%s,%s:1}" % tuple(p.split(":")) for p in pfs)

    html = f"""<!doctype html><meta charset=utf-8><body style="margin:0;background:#111">
<canvas id=c width=960 height=540></canvas><script>
const VW=960, VH=540, GROUND_Y=474, DECK_Y=GROUND_Y-150;
const cv=document.getElementById('c'), ctx=cv.getContext('2d');
let cam={{x:{args.cam}}}, level={args.level}, seg={args.seg};
let LEVEL_W=8000;
let gaps=[{gapjs}], platforms=[{pfjs}], sprites={{}}, images={{}};
let searchlights=[{{x:{args.cam}+560,sy:GROUND_Y-300,gy:GROUND_Y,range:210,half:50,t:0.7,sp:0,alarmCd:0}}];
let now=1400;
let player={{x:{args.cam}+480,y:GROUND_Y}};
{grab_const(src, "WH")}
{grab_const(src, "SH")}
function clamp(v,a,b){{return v<a?a:v>b?b:v;}}
{bodies}
// Backdrops are <img>s. Draw only once they have actually decoded, or the scene
// comes out empty and it looks like the draw code is broken.
const NEED={imgjs};
function draw(){{
// night sky + a plain ground band, the way drawBackground lays them down first
let g=ctx.createLinearGradient(0,0,0,VH);
g.addColorStop(0,'#0a1326');g.addColorStop(0.6,'#0c1a2b');g.addColorStop(1,'#0a141d');
ctx.fillStyle=g;ctx.fillRect(0,0,VW,VH);
ctx.fillStyle='#16202c';ctx.fillRect(0,GROUND_Y,VW,VH-GROUND_Y);
{calls}
// JPEG at half size: this is a composition check, and a full-res PNG data
// URL is too big to read back out of the page in one go
const h=document.createElement('canvas'); h.width=VW/2; h.height=VH/2;
h.getContext('2d').drawImage(cv,0,0,h.width,h.height);
window.__png=h.toDataURL('image/jpeg',0.82);
// expose it for a plain fetch: the harness page is served from the repo, so
// the runner can read it back without funnelling 100KB through a tool result
document.body.appendChild(Object.assign(document.createElement('textarea'),
  {{id:'png',value:window.__png,style:'width:99%;height:40px'}}));
document.title='rendered '+window.__png.length;
}}
let left=NEED.length;
if(!left)draw();
for(const k of NEED){{ const im=new Image();
  im.onload=im.onerror=()=>{{ images[k]=im; if(--left===0)draw(); }}; im.src='./'+k+'.png'; }}
</script></body>"""
    path = os.path.join(REPO, args.out)
    open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"wrote {args.out}  (fns: {', '.join(args.fns)})")

if __name__ == "__main__":
    main()
