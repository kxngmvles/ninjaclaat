#!/usr/bin/env python3
from pathlib import Path
import re, shutil, subprocess, sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent

required = [
    ROOT / "dist" / "game.js",
    ROOT / "dist" / "assets.js",
    ROOT / "dist" / "strings.js",
    ROOT / "tools" / "build.py",
    HERE / "warehouse_v2_block.js",
    HERE / "wh_plate_v2.jpg",
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    print("ERROR: Missing required file(s):")
    for p in missing:
        print("  -", p)
    print("\nRun this script from the NinjaClaat repository root, with the bundle files together.")
    sys.exit(1)

game_path = ROOT / "dist" / "game.js"
assets_path = ROOT / "dist" / "assets.js"
strings_path = ROOT / "dist" / "strings.js"
index_path = ROOT / "index.html"
asset_dest = ROOT / "wh_plate_v2.jpg"

game = game_path.read_text(encoding="utf-8")
assets = assets_path.read_text(encoding="utf-8")
block = (HERE / "warehouse_v2_block.js").read_text(encoding="utf-8").rstrip() + "\n\n"

for p in (game_path, assets_path, index_path):
    if p.exists():
        bak = p.with_name(p.name + ".warehouse_v2.bak")
        if not bak.exists():
            shutil.copy2(p, bak)

# Replace the complete old warehouse implementation.
start = -1
for marker in (
    "/* ============================ L2 seg 2: THE WAREHOUSE V2",
    "/* ============================ L2 seg 2: THE WAREHOUSE",
):
    start = game.find(marker)
    if start >= 0:
        break
end = game.find("function drawShipHold(){", start if start >= 0 else 0)
if start < 0 or end < 0:
    raise RuntimeError("Could not locate the warehouse block in dist/game.js.")
game = game[:start] + block + game[end:]

# Floor-aware enemy relocation when a wave would spawn on-camera.
old_pf = 'const pf=platforms.find(q=>!q.noland&&q.top<GROUND_Y-110&&Math.abs(q.x-sx)<q.w/2);'
new_pf = '''const pf=platforms.find(q=>!q.noland&&q.top<GROUND_Y-110&&Math.abs(q.x-sx)<q.w/2&&
          (w[3]==="top"?q.whFloor===3:w[3]==="mid"?q.whFloor===2:true));'''
if old_pf in game:
    game = game.replace(old_pf, new_pf, 1)

# Floor-aware actual spawn height.
old_spawn = 'if(w[3]==="roof"||w[3]==="deck"){ for(const pf of platforms){ if(Math.abs(pf.x-w[1])<pf.w/2&&pf.top<GROUND_Y-110){ e.y=pf.top; } } e._safeX=w[1]; }'
new_spawn = '''if(w[3]==="roof"||w[3]==="deck"||w[3]==="mid"||w[3]==="top"){
    for(const pf of platforms){
      const floorOK=w[3]==="top"?pf.whFloor===3:w[3]==="mid"?pf.whFloor===2:true;
      if(floorOK&&Math.abs(pf.x-w[1])<pf.w/2&&pf.top<GROUND_Y-110){ e.y=pf.top; break; }
    }
    e._safeX=w[1];
  }'''
if old_spawn in game:
    game = game.replace(old_spawn, new_spawn, 1)

# Run the warehouse route state machine after player movement.
old_update = 'updatePlayer(); for(const e of enemies)updateEnemy(e);'
new_update = 'updatePlayer(); if(inWare())updateWarehouseRoute(); for(const e of enemies)updateEnemy(e);'
if old_update in game:
    game = game.replace(old_update, new_update, 1)

# Gate the segment exit until the upper route and shaft drop are completed.
old_exit = 'if(inWare()&&!scene&&!boarded&&player.x>LEVEL_W-240&&player.y>=GROUND_Y-2){'
new_exit = 'if(inWare()&&!scene&&!boarded&&whRoute.done&&player.x>LEVEL_W-240&&player.y>=GROUND_Y-2){'
if old_exit in game:
    game = game.replace(old_exit, new_exit, 1)

checks = [
    ("Warehouse V2 block", "THE WAREHOUSE V2" in game),
    ("route updater", "if(inWare())updateWarehouseRoute();" in game),
    ("route-gated exit", "whRoute.done&&player.x>LEVEL_W-240" in game),
    ("middle-floor spawn", 'w[3]==="mid"' in game),
    ("top-floor spawn", 'w[3]==="top"' in game),
]
bad = [name for name, ok in checks if not ok]
if bad:
    raise RuntimeError("Patch sanity check failed: " + ", ".join(bad))

game_path.write_text(game, encoding="utf-8")

# Reuse the existing wh_plate image key so the image loader needs no new code.
assets2, count = re.subn(
    r'("wh_plate"\s*:\s*)["\'][^"\']+["\']',
    r'\1"./wh_plate_v2.jpg"',
    assets,
    count=1,
)
if count != 1 and '"./wh_plate_v2.jpg"' not in assets:
    raise RuntimeError('Could not update "wh_plate" in dist/assets.js.')
assets_path.write_text(assets2, encoding="utf-8")
shutil.copy2(HERE / "wh_plate_v2.jpg", asset_dest)

node = shutil.which("node")
if node:
    for p in (assets_path, strings_path, game_path):
        subprocess.run([node, "--check", str(p)], check=True)
else:
    print("WARNING: Node.js not found; skipped node --check.")

subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=True)

print("\nWarehouse V2 installed successfully.")
print("Modified: dist/game.js, dist/assets.js, wh_plate_v2.jpg, index.html")
print("Original backups use the suffix .warehouse_v2.bak")
