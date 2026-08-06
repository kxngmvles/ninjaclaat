# NINJACLAAT — Web Game (Claude Code handoff)

Dark, cinematic Jamaican-ninja beat-em-up platformer. **This repo IS the live web game** — a playable 5-level game (final boss included) shipped on GitHub Pages. **NOT finished**: Kemar plans more levels between the existing ones, a substantial Level 5 rework, and is exploring a full Godot overhaul (smoother skeletal animation, live backgrounds, deeper fight logic). Continue development here unless he says to work in Godot.

> A separate **Godot 2D port** exists on the owner's machine (`Desktop/NinjaclaatGodot/`, has its own CLAUDE.md). It is **pinned / not active** and is NOT in this repo. Ignore unless the owner asks to resume it.

Owner: **Kemar** (GitHub **kxngmvles**). Live: https://kxngmvles.github.io/ninjaclaat/

---

## CREATIVE / SAFETY CONSTRAINTS (carry forward)
- Do **not** replicate any real, identifiable person's likeness. The villain "Derrick" must **not** be based on a real private individual, and his comedy must **not** be rooted in sexuality. Keep him a generic vain street-tyrant.
- Keep humor away from protected-group stereotypes.
- The owner performs their own logins / OAuth / billing. Don't ask for tokens.

---

## REPO LAYOUT
- `index.html` — the **deployed build**. It **inlines three script blocks** in order:
  1. `window.AS = {...}`  (asset manifest = `assets.js`)
  2. `window.STR = {...}` (all player-visible text = `strings.js`)
  3. the engine IIFE      (= `game.js`)
- `*.mp3` — voice/sfx at repo ROOT (referenced `./Name.mp3`).
- `nc_*.png`, `walk_*.png`, `goon_bike*.png`, etc. — locally-hosted, **pre-keyed transparent** sprite frames.

### FIRST STEP in a new session
The maintained editable form is **three separate files** `dist/assets.js`, `dist/strings.js`, `dist/game.js` — **now committed to the repo** (since 2026-07). Edit those, then re-inline to rebuild `index.html`. If `dist/` ever goes missing, recreate it by splitting `index.html`'s three `<script>` blocks.

### DEPLOY PIPELINE (with real git — much nicer than before)
1. Edit `dist/assets.js` / `dist/strings.js` / `dist/game.js`.
2. `node --check` each JS file (engine is one big file — always parse-check).
3. Inline all three back into `index.html` (replace the three script blocks with file contents).
4. `git commit` + `git push` → GitHub Pages redeploys in ~1 min.
   *(Previous sessions used the flaky GitHub web-upload button; with real git in Claude Code, just push.)*

---

## ENGINE CONCEPTS (game.js — vanilla JS canvas, single IIFE)
- `sprites{}` keyed images, `images{}` backgrounds, `sounds{}`.
- **chromaKey(img)** — at load, strips magenta `#FF00FF`, despills pink fringe, **auto-crops** to content. Used by **loadSprite(key,url,tint)**. (Hot pink ≈ magenta and gets keyed out — that's why Derrick's shirt is red.)
- **loadSpriteRaw(key,url)** — loads a **pre-keyed transparent** PNG with **no crop**. Used for all video-derived frame sets so multi-frame anims stay size-consistent (no jitter).
- **MIRROR = {knife:1, fyah:1}** — per-enemy facing flag. Native art faces RIGHT; draw flips when facing left; MIRROR types have LEFT-native art. Match a type's existing facing when adding art.
- **FR{}** player anim tables, **EFR{}** enemy anim tables. Base run/walk use `nc_nrun1..6` (a seamless 6-frame run cut from the owner's video).
- Player kit: dash, block (spin-blade parry), double-jump (L2), smoke screen (L3 spliff), kunai (F), and L4 **chain weapon** (`hasChain`): chain run `nc_crun*`, chain attack `nc_catk*`, grapple throw→swing `nc_cthrow*`/`nc_cswing*`, chain jump/fall/land `nc_chain_jump/fall/land`.
- **Levels** (`levelSel` 1–5 on the title menu):
  - **L1** Dark Beach — boss **Razor**. (Ground must use `images.ground`, level-gated: a bug once made L1 use the ship dock tile — fixed.)
  - **L2** Smuggler's Harbour — stealth takedowns, searchlights, double-jump + block learn-events, ship-deck seg2, boss **Shotta** (enrage, grenades).
  - **L3** Kingston — street seg1 (vendor shop spends BITS, spliff smoke, sub-boss **Derrick**: kick / phone-flash-blind / sandal) → rooftop seg2 (boss **Fyah**: fireballs, punch/kick, enrage, smoke-teleport). 2 segments via `shipfade`.
  - **L4** Don Gorgon's Compound — opens with an **L3 scripted defeat** (enraged Fyah blinds/finishes you) → **cell cutscene** (`bg_cell`) where **Dupree is revealed to be a hallucination / long dead**. Seg1 = compound exterior (`bg_compound_ext`): chain melee + **grapple (F)** swing over a gap under an overhead gantry; enemies goonA/goonB/gunner/dogs. Seg2 = **moped chase** (hill-climb style): diagonal dirt downhill (`bg_forest_night` + `road_dirt`), hero on animated bike `nc_bike1..8`, **goons on bikes** `goon_bikeA/B` + car `enemy_car` that only close the gap when you hit obstacles, **weed = boost**, **ramps = big air**, spinning wheels, escape meter. `updateMoped`/`drawMoped`.
  - **L5** Gorgon's Tower (FINALE, added 2026-07) — `startLevel5`/`buildTower` (`bg_throne` terrace bg, gold-trimmed marble floor). Hero gets the full kit back (dash/3-combo/double-jump/block + kunai x5, smoke x2, 130 maxhp; machete, no chain). 4 elite waves → **DON GORGON** (`gorgon` type, 660hp, `updateGorgon`): cane melee/punch, dark orbs (`darkOrb`, triple fan in phase 2), **jumpable ground shockwaves** (`gorgonShock`, `p.shock` projectiles), **summons backup goons** (`gorgonSummon`, capped at 2 alive), enrage at 50% (purple aura, +speed, boss music `music_lt`). Victory → `l5_outro` (memory returns, farewell to Dupree) → "NINJACLAAT — THE END". Gorgon art = 8 magenta-keyed stills (`gorgon_*`) + `bg_throne`, generated on the standard image pipeline.

### STORY
Amnesiac ninja washes ashore, guided by "Dupree." Razor → Shotta → Derrick/Fyah. L4 twist: **Dupree was a hallucination all along** (dead since the night the hero "died"). L4 ends fleeing to regroup with the old crew — then **L5: the hero returns with the blade, kills Don Gorgon, his memory comes back, and he says goodbye to Dupree.** (Current arc lands there, but Kemar plans additional levels between the existing ones and an L5 rework — treat the "THE END" screen as provisional.)

---

## ASSET PIPELINE (non-obvious)
- **Generated stills** (image model): made on **magenta `#FF00FF`**, hosted as cloudfront URLs, placed in `window.AS`, loaded via `loadSprite` → chromaKey at runtime.
- **Owner's video animations** (run, bike, chain moves, walks): recorded on a **rose-pink `~#DF1461`** background. Pipeline (needs a shell w/ ffmpeg + PIL/numpy):
  1. `ffmpeg` extract frames.
  2. **Find a seamless loop window** (frame-to-frame self-similarity), NOT diff-to-frame0 — clips drift, so blind looping snaps/restarts. (Good run loop was frames 35–52.)
  3. Key rose-pink → transparent: `pink = (r>150)&(g<100)&((r-g)>85)&((b-g)>8)&(b<185)`, then despill kept pinkish pixels.
  4. **Union-crop** all frames of a set to a shared box (no per-frame size jitter); scale to a common height.
  5. Save repo-relative PNG `nc_xxx.png`, reference `"./nc_xxx.png"` in `window.AS`, load via `loadSpriteRaw`.

### GOTCHAS
- Large-file edits: the previous env's Edit tool truncated `game.js` — python string-replace with assertions was safest. (In Claude Code, normal editing/`sed`/patch is fine — just `node --check` after.)
- Appending keys to `assets.js`: mind the trailing comma.
- Always `node --check` before deploy; a truncated build once shipped broken.

---

## PENDING WORK
- **More levels between the existing ones + Level 5 rework** — Kemar wants the game longer and L5 substantially reworked (details TBD with him).
- **Godot overhaul track** — `OneDrive/Desktop/NinjaclaatGodot/` has the godot_ai MCP plugin (server on `http://127.0.0.1:8000/mcp`, needs `uv` — installed 2026-07-06) and a full asset backup in `assets/web/` (293 files, all CDN art/audio downloaded). Goal: skeletal cutout animation, live backgrounds, better fight logic; web game stays live meanwhile.
- **Dedicated L3 music** (rooftop/Kingston reuses other tracks); L5 reuses the `music_lt` boss theme — a dedicated finale track would be nice.
- **Balance pass** — moped-chase feel (gap rates, obstacle spacing, boost), and the L5 Gorgon fight is HARD (shock + orbs + melee together); tune after real playtests.
- **Two broken assets**: `bg_beach` 403s (old `d2ol7oe51mr4n9` bucket is dead — L1's beach parallax layer silently missing; regenerate on the current pipeline). `voice_goon3` has a **malformed URL** in `assets.js` (invalid UUID tail — never worked; regenerate or fix URL).
- Optional polish on any animation the owner re-records (drop clips through the video→frames pipeline above).

## RUN LOCALLY
Open `index.html` in a browser, or visit the live URL.

### 2026-07-31 (later) — sizing, dogs, slash FX

**⚠️ NEVER run `git checkout -- .` in this repo.** All work here is uncommitted
until Kemar pushes; I wiped a whole session with it. Recovery only worked
because the build was still live in a browser tab (pulled the three inlined
`<script>` blocks back out via a POST endpoint). Commit early instead.

- **Per-frame render scale** (`ASCALE` table in game.js, generated offline):
  the game sizes sprites by bbox, but a raised bat/machete inflates the bbox so
  the BODY renders small. `mult = (idle_body/idle_bbox) * (bbox_f/body_f)`,
  clamped to [0.72, 1.18] so genuinely crouched poses aren't stretched, plus a
  width cap so wide falling/lying frames can't balloon. Regenerate the table if
  frames are re-sliced (script is in the session log; measures `body_height()`
  from tools/slice_sheet.py).
- **`body_height()`** added to the slicer: feet → top of the *wide* region, so
  thin protrusions (bat, machete) don't count. Sets are normalized on this now.
- **Auto-detecting character scale does NOT work reliably** — tried bbox height,
  body height and head width; generated art varies in scale and a raised bat
  sits exactly where the head is. Explicit tables + eyeballing a game-scale
  contact sheet is the honest approach.
- **Dogs** hold their stride and never double back on patrol (turning around
  made them unavoidable); they only close in once `alert>=60`. First L1 dog is
  fully passive scenery.
- **chromaKey fix**: `isMag` now requires blue clearly ABOVE green
  (`(b-g)>26 && (r-g)>42`). The old test (`g < min(r,b)*0.8`) was eating the
  dog's light-brown fur. Same class of bug as the hero's hands/hair.
- **Synthesised sword slashes** (`bladeSlash()`): filtered noise whoosh sweeping
  down in pitch + a metallic ring on heavy/powered swings, via WebAudio.
  Overrides `sfx_slash`/`sfx_power_slash`, adds `sfx_slash_heavy`. No assets,
  and each swing varies slightly so it never machine-guns.
  (Higgsfield CANNOT generate SFX — speech only. Don't try.)
- **Razor's flying slash** redrawn as a long tapered crescent (112x30) with
  trailing motion streaks + bright core, instead of the geometric half-circle.

**Slicing figures that overlap** (`component_figures`): seam cells decide which
blob belongs to which figure (by centroid), but each blob is then taken WHOLE
and masked. A straight column cut chopped Razor's machete and put the tip in
the next frame — the lunge sheet was never cut off, my slicing was. Always use
this for weapon poses.

**Sheets are not always the grid you asked for.** The ground-slam sheet came
back 3+2, not 2x3 — forcing 3 columns on row 2 invented a "frame" out of the
impact burst. Check the source rows before setting --cols; slice rows
separately (`--start`) when the layout is ragged. lt_slam is 5 frames.

**Hero power-up is a 5-frame sequence** (`nc_pwr1..5`, generated nano-banana
from nc_power_pose): calm -> tensing -> crouched with energy swirls -> eruption
-> full aura with glowing machete. FR.power plays it once at 7fps; HSCALE
entries correct for the aura inflating the bbox (HSCALE[key] = body/idle_body).

### 2026-08-01 — video-derived combo + heavy, powerup, sword sfx
- **`tools/video_to_frames.py`**: extracts smooth frames from Kemar's recorded
  clips (1440x1440, rose-pink #DF1461 bg, ~73f with idle padding). Keys the
  rose (`(r>150)&(g<115)&(r-g>78)`, keeps the green energy trail), auto-finds
  the ACTIVE swing window by frame-to-frame motion (drops dead idle), union-
  crops, normalizes to a ref BODY height, samples N frames. `pip install
  imageio imageio-ffmpeg` provides the decoder (no system ffmpeg on this box).
- **3-hit combo is now video-smooth**: `slash1_1..14`, `slash2_1..14`,
  `slash3_1..14` (14 frames each). FR.slash1/slash2/slash3 at fps 47/53/42
  loop:0. ATK.c (finisher) switched from the single `nc_kick` to `slash3`.
  These already have the green trail BAKED IN — the code `slashArcs` crescent
  in doMeleeHit still fires on top; if it looks doubled, guard it for these.
- **Heavy attack**: `heavy1..4` sliced from `Heavy slash.png`, FR.heavy at 8fps.
- Frames are pre-normalized to idle BODY height, so famH renders them at a
  consistent body size even though the raised blade/trail inflates the bbox
  (no HSCALE needed — the bbox/body cancel out, see the note in that session).
- Power-up = `nc_pwr1..5` (5-frame sequence). Real recorded `sword_slash.mp3`
  (`sfx_sword`) now backs sfx_slash; bladeSlash() WebAudio layers under heavy.
