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

### 2026-08-09 — combo rework, Katana-Zero FX, L2 interior, L2 enemy sheets

**The 3-hit combo looked like one move because it WAS one move.** slash1/2/3 are
three takes of the same overhead-to-low sweep. No amount of retiming fixes that.
Combo is now spin cut (`nslash1..17`, from Kemar's external sheet) -> overhead
sweep (`slash2_*`) -> kick (`kick1..4`, sliced at last from `combo3_sheet.png`,
which had sat unused while the build used the single-frame `nc_kick` still).
ATK.d removed — a 4th swing only ever read as the 2nd one again.

**tools/slice_sheet.py — three fixes, all learned the hard way:**
- **Foot-anchored union packing** (`union_pack`). Per-frame cropping is what made
  sliced sets jitter; every frame now sits on ONE canvas aligned by its ground
  contact (median x of the bottom 6% of rows, so a kicking leg doesn't drag the
  anchor). `mode="centre"` anchors on centre of mass instead — for airborne
  frames, where the game's own jump physics is already moving the sprite.
  New sets need no ASCALE entry.
- **Body-anchored blob grouping.** `component_figures` used to cut the row into
  even cells; models space figures unevenly and crowd them to one side, so a
  dropped weapon went to the neighbour and a cell came out empty. Now the
  `expect` LARGEST blobs are the bodies and every stray blob joins the nearest.
- **Baseline removal** in `key_background`: a thin dark rule spanning >72% of the
  sheet is never art. Left in, it welds every figure into one blob.

**Generated sheets weld together.** The first bruiser sheets came back as TWO
connected components — the figures physically touched, so NO splitter can
separate them. Check the component count before trusting a slice:
`ndimage.label(alpha)` should give >= frame count. The fix is regeneration with
"figures at ~60% height, WIDE EMPTY MAGENTA GAP between each, nothing may touch
or overlap the neighbour" — not more clever slicing. Blade/gunner were fine
first time; only wide figures with long weapons collide.

**New L2 enemy movesets**: `{gunner,bruiser,blade}_atk1..5` + `_die1..5`,
nano_banana_pro at 4k 21:9, each with its existing `*_idle` CDN sprite imported
via `media_import_url` as the reference (keeps them on-model).
**`die1` is the standing stagger, so it doubles as the `hurt` pose** — a recoil
is just the first beat of a death. Saved generating three more frames.

**EFPS was starving every multi-frame enemy anim.** attack was 5.5fps inside a
~25-frame window, so goonA's 5-frame swing only ever reached frame 2. Now
attack/attack2 11, shoot 24 (10-frame burst window), dead 5.5 (fades over 70).

**Slash FX**: the geometric half-circle fired on every swing including whiffs and
fought the green trail baked into the video frames. Replaced by `slashGash()` —
a tapered cut placed ON the enemy hit, white core over a coloured bloom, ~6
frames — plus a screen flash on connect. Never drawn on a miss.

**Power-up** holds now: fps 7->5 and `nc_pwr5` repeated x4 (same trick as Razor's
enrage sitting on lt_enr3), `powerupT` 48->96, iframes for the whole pose, and
the hurt-blink suppressed so it doesn't strobe through the moment.

**L2 rebuilt vertical.** Steps before the pit are one container row (138px) —
a single jump clears ~149 (JUMP_V/G) and the double jump is still being taught
there; past it, two-row stacks and catwalks needing both. `gaps[0]` still gates
the djump lesson, `x>1880` still gates the block lesson — keep those anchors.
New **warehouse interior** at x2300-3280 (`WH`/`drawWarehouse`): drawn in canvas,
WORLD-LOCKED (no parallax) so it can't swim against the platforms bolted to it,
clipped to its own span so the doorways read as walls. `dryPit(x)` makes pits
inside it drop into dark instead of harbour water.

**tools/build.py** — node --checks all three dist files then inlines them into
index.html. Use it instead of hand-editing the three `<script>` blocks.
**tools/contact_sheet.py** — renders a sliced set at HERO_H on the game bg with
the ground line drawn through. Frames that look fine at full res still jitter in
game; this is how you catch it.

**Payload ceiling**: sprite frames are stored at nc_idle's native scale (~1800px)
because famH() sizes every frame relative to it. The new sets add ~40MB. Fixing
it means downscaling every set at once plus HSCALE entries — not worth it until
first-load time actually hurts.

### 2026-08-09 (later) — combat feel, L2 three-segment rebuild, ship interior

**The reach complaint and the "no stagger" complaint were mostly ONE bug.**
`union_pack` sized each canvas to its content, so the hero's torso sat up to
**25px to one side of player.x** — he visually swung past enemies his hitbox
never reached, so nothing connected, so nothing ever flinched. Frames are now
foot-locked to each other (no jitter) and the SET is shifted so the mean
`body_centre()` lands on the canvas centre. Every set measures mean 0.0px.
**Any new frame set must go through union_pack or it will be off-centre.**
Reach was also nudged (a 70→80, b 66→76, kick 84→90) as insurance.

**Real hitstun**: `hurtT` 12 → 20 (bosses 9, so they can't be stun-locked), plus
`state="hurt"` and `attackCd>=28` on hit. A 12-frame flinch let goons walk
straight back into the swing they were already winding up.

**`nc_block1..3` are authored at HALF resolution** (1024px vs nc_idle's 2048),
so famH sized the block stance at exactly 60px. `HSCALE 0.5` fixes it. Check
source height before blaming the pose when a sprite renders small.

**The dog walked on water** because the stealth patrol stride `return`s before
the shared over-gap check further down. Both the patrol and chase strides now
refuse to step into a gap.

**A `gap` makes GROUND_Y itself non-solid.** Do not use one to mean "hole in an
upper walkway" — the player falls THROUGH the floor below and takes fall damage.
Just leave a space between platforms; they land on the ground normally.

**Tutorial triggers now require `player.y>=GROUND_Y-2`.** The block lesson
spawns a gunner firing along the ground line, so triggering it from a crate put
the player above every shot. The 1800-2350 stretch is also deliberately FLAT —
don't put anything standable there.

**L2 is three segments now**: dock (`buildHarbour`, 5600 wide) -> **ship interior**
(`buildShipHold`, seg 2, 4200 wide) -> weather deck (`buildShipDeck`, now **seg 3**).
`shipfade` dispatches on the OLD seg value. Anything testing `level===2&&seg===2`
for "the deck" had to become `seg===3`.

**New `crew` enemy** — boat-hook deckhands, `crew_pose1..5` (idle + 4 walk),
`crew_atk1..5`, `crew_die1..5`, plus `crew_idle` aliased to pose1 because
`drawEnemy` sizes every enemy via `famH(key, type+"_idle", h)`. **Add that alias
for any new enemy type** or it renders unnormalized.

**Generated sheets drift between prompts.** The crew's overalls came back worn
UP in the walk/death sheets and peeled DOWN in the attack sheet. Fix by
regenerating the odd one out with a PRIOR JOB ID as the reference image
(`medias:[{role:"image",value:"<job-id>"}]`) and restating the outfit explicitly.

**Video for enemy animation** (`--bg magenta` on video_to_frames.py): wan2_7 with
the magenta idle sprite as `start_image` and "LOCKED STATIC CAMERA" in the prompt.
Motion blur smears the character THROUGH the magenta, leaving contaminated bands
far wider than the fringe despill — a whole swinging pipe came out purple. The
surviving smear is DARK magenta (r,b under 65, g near zero), so `key_magenta`
flattens it to luminance with deliberately low thresholds. **Not safe for a
character with genuinely red parts** (the knife fighter's bandana).

**EFPS was starving enemy anims** (see prior entry) — attack 11, shoot 24, dead 5.5.

**New tools**: `tools/build.py` (parse-check + inline), `tools/contact_sheet.py`
(renders a set at HERO_H on the game bg), `tools/preview_scene.py` (pulls a draw
function OUT of dist/game.js by brace-matching and renders it standalone, so what
gets eyeballed is what ships).

**`voice_goon3` is dead for real** — 403 with and without the malformed UUID tail,
the file was never uploaded. Set to `""` so loadSound no-ops instead of firing
three failed requests per load. `bg_beach` (403, dead bucket) still needs
regenerating — it's L1's beach parallax layer.

### 2026-08-09 (3) — walkable stairs, ship deck, minigun Shotta, video-first rule

**RULE FROM KEMAR: every MOVEMENT animation now comes from a generated video,
sliced — not from a still sprite strip.** Stills are only for single poses.
`video_to_frames.py --bg magenta` + wan2_7 with the character's magenta idle as
`start_image` and "LOCKED STATIC CAMERA" is the pipeline.

**`--loop` for cycles.** A 4s walk clip holds several strides; sampling evenly
across all of them gives frames that never repeat and the cycle stutters. `--loop`
finds the ONE stride that closes on itself (min frame-to-frame difference over
period 12-45), then samples inside it. Search runs on 1/8-scale frames — at full
res it takes minutes.

**Transparent pixels keep their magenta RGB.** Keying only clears ALPHA, so every
later LANCZOS resize pulled hidden background magenta back in along the
silhouette — that was the purple fringing, NOT a bad chroma threshold.
`bleed_rgb()` floods transparent pixels with the nearest opaque colour before any
resize. Wired into BOTH pipelines. Do not remove it.

**Magenta spill over dark cloth goes VIOLET** (blue ends up above red), so
key_magenta tests "blue AND red both clearly above green" rather than a magenta
ratio. Navy, teal and blue-grey garments sit at or below green on b-g and survive.

**STAIRS**: `step:1` platforms plus a STEP_UP=46 auto-step in the player physics.
Walking into a tread lifts you onto it and off the far side. The gate is
`player.onGround` — LAST frame's value — which is what makes stepping DOWN work,
since the landing check can't have fired yet. Treads must ABUT in x (58 wide,
58 apart) and rise <= STEP_UP, or it reads as floating platforms again.
**`tools/check_level.py` validates this** — every stair run must connect at both
ends, every "roof" spawn must land on a real platform. Run it after any layout edit.

**Enemies no longer pop in on screen.** `spawnWave` pushes any spawn whose
authored x is on camera to just past the edge the player is walking toward, so
they walk in. Skipped for "roof" spawns (they'd miss their walkway) and bosses.
Patrol anchors use the RELOCATED x, not the authored one.

**L2 seg1 is 7200 wide**, warehouse 3150-5550 with THREE stair runs and no floor
pit (Kemar: no drop in the warehouse). Ship hold is 5200 with two stair runs.

**Ship deck (seg 3) is drawn, not a backdrop image**: horizon, sea, parallaxing
deckhouse with lit windows, container stacks, guard rail, deck plating (the
segment previously rendered NO ground band), and props sized off HERO_H — bollard
knee-high, vent chest-high, winch waist-high. Searchlight mast is a braced
lattice tower now, not `fillRect(sx-4,sy,8,h)`.

**SHOTTA**: 380hp, video walk/run/reload (the reload clip actually DROPS the
magazine — the old 2-frame version left it hanging in mid-air), a backward ROLL
when you close to melee, and a SWEEP that walks a wall of fire across the deck.
Phase 2 swaps to a **minigun** (`shotta_mg1..7`) — `eState` forces every armed
pose to come from that set or the weapon pops in and out of his hands. Crates at
4380/4760/5060 give you something to break line of fire behind.

**L3 backdrop** uses `drawBgStrip(["bg_street","bg_street2","bg_street3"])` —
different plates side by side instead of tiling one shopfront every 1400px.

**tools/preview_scene.py** calls EVERY listed function in order (it used to call
only the last, which silently rendered an empty scene). It emits a half-size JPEG
and posts it to a local sink, because a full-res PNG data URL is too big to read
back through the tool channel.

### 2026-08-09 (4) — painted backdrops, filmed water, Shotta overheat cycle

**Backdrops are GENERATED ART now, not canvas rectangles.** Kemar: "generate it
with ai, not code". `bg_warehouse.png` and `bg_deck.png` are nano_banana_pro
21:9 plates, trimmed so the artwork's own floor line IS the image bottom (the
warehouse plate came back with 480px of dead black under the floor — crop it or
the character walks in a black band), downscaled to 1920 wide, drawn MIRRORED
(`drawBgMirror`) so the repeats have no seam. The warehouse plate is world-locked
and anchored to `WH.x1`; the deck plate parallaxes at 0.5.
Prompt shape that worked: "flat side-scroller perspective, no vanishing point",
"the bottom fifth must be plain empty floor so a character can stand on it",
"NO characters, NO text".

**Deck props are generated sprites** (`prop_container_ai`, `prop_crates_ai`,
`prop_winch_ai`, `prop_drums_ai`, `prop_bollard_ai`) sliced from one magenta
strip and scaled by MULTIPLES OF HERO_H — container 2.25x, crates 1.05x, winch
0.85x, drums 0.80x, bollard 0.42x. They are `cover:1` platforms, so they double
as the thing you hide behind during Shotta's sweep.

**THE FIRST JUMP WAS IMPOSSIBLE.** Player runs 3.0px/frame and a jump lasts
43.9 frames (2*JUMP_V/G), so a single jump covers **131px** and a double covers
**~258px only if the second is frame-perfect at apex**. The gap was 250px. It is
168px now. Any new gap: keep it between 140 and 200 if the double jump is
required, under 120 if it isn't.

**Stairs are 30px tread / 19px rise** (was 58/38, which read as wide floating
slabs). Rise must stay under STEP_UP=46. Treads must ABUT — `check_level.py`
verifies that and that both ends of every run meet a walkway.

**Water is a filmed plate** (`water1..10`, from a wan2_7 clip of the still).
Water does NOT loop — best residual was ~19 vs ~0.5 for a character walk — so
the draw cross-dissolves the last quarter of the cycle back into frame 1
instead of hard-cutting. Do not bother hunting for a clean water loop.

**Shotta's overheat cycle** is the fight's rhythm: firing and sweeping add heat,
at 100 the minigun overheats (`shotta_hot*`, glowing barrels + smoke) and he is
helpless for ~112 frames — that is the damage window. While hot he HURLS oil
drums (`shotta_thr*`, a `drum:1` projectile that arcs and explodes on impact or
contact). Point-blank he gun-butts (`shotta_butt*`) with heavy knockback.

**preview_scene.py** now preloads backdrop images (`--images bg_deck`) and calls
every listed function in order. Image-based scenes rendered EMPTY before, which
looked like broken draw code — it was just `images={}`.

### 2026-08-09 (5) — L3 goes video, Derrick redesigned, warehouse cross-section

**Every L3 character now moves from sliced video** (Kemar's rule). wan2_7 with
each character's existing magenta idle as `start_image`:
Derrick walk/photo/kick/enrage, Fyah walk/punch/cast, and bat, knife, molotov
and shield each walk + attack. Walks use `--loop`, attacks don't.

**MIRROR types must be generated FACING LEFT.** `MIRROR={knife:1,fyah:1}` means
their native art faces left and the engine flips for right. Prompt those two
"facing LEFT" or every frame comes out flipped in game.

**Derrick is redesigned**: hard, humourless, deeply lined, no grin (Kemar: "he
needs to be serious not smiling, and have more wrinkles"). New `derrick_idle` is
a local pre-keyed PNG scaled to the OLD idle's body height so nothing else
shifts. His enrage aura is a full RAINBOW and holds its last two poses;
`enrageT` 60 -> 112 to cover it.

**Sound routing** (Kemar corrected me): `Camera.mp3` is the shutter on the photo
flash. `Derrick camera.mp3` is his enrage SHOUT and fires when he starts taking
pictures, not when he snaps. The enrage animation itself gets `powerSurge()` — a
synthesised rising sub sweep + detuned square + noise discharge, no asset —
reused for Shotta. `there-goes-another-victim` plays only when Shotta is the one
who kills you.

**The warehouse is ONE building in cross-section.** The previous attempt drew a
separate frontage beside the interior with its own lower roofline, so the outside
was visibly shorter than the inside. Now: one roof band across the whole span
overhanging both ends, a full-height end wall at each end with a doorway punched
through it, and the interior plate clipped BELOW the same eaves line
(`WH_ROOF`/`WH_EAVE`/`WH_WALL`). Interior also fades to black at both thresholds.

**Deck backdrop is option A** (container canyon under floodlights). Generating
four and letting Kemar pick beat guessing — he rejected two earlier attempts.

**Sprite props must NOT be stretched to their collision box.** `drawPlatforms`
was drawing `pf.w x (baseY-pf.top)`, which squashed every generated prop. It
draws at the ART's aspect now (`s.w*(h/s.h)`), and the boxes were resized to
match. Pass `fit:1` on a platform to opt back into stretching.

**preview_scene.py copies scalar consts too.** A scene referencing one the
harness hadn't copied threw ReferenceError and rendered an EMPTY frame, which is
indistinguishable from broken draw code. Check the console before believing a
blank preview.

### 2026-08-09 (6) — the vanishing-hero bug, and a two-storey warehouse

**THE HERO DISAPPEARING WAS A THROWN EXCEPTION, not a draw-order or z-index
problem.** In `drawPlatforms` I declared `const dark=...` BELOW the `if(pf.deck)`
branch that reads it. `const` is in the temporal dead zone until its declaration
runs, so every frame with a catwalk on camera threw
`ReferenceError: Cannot access 'dark' before initialization`, which aborted the
rest of the frame — player, enemies, HUD, everything after `drawPlatforms`. The
level kept scrolling because UPDATE still ran; only DRAW died.
**Symptom to remember: if the hero and the HUD vanish together while the world
still moves, it is an exception mid-draw. Check the console first.**

**Debug hook**: `window.__dbg` is exposed on localhost only (`player`, `cam`,
`platforms`, `enemies`, `images`, `sprites`, `warp(x)`). `__dbg.warp(3900)` drops
you straight at the warehouse instead of playing the level up to it. It is gated
on hostname so it never exists on the deployed build.

**The block lesson now clears the stage before it starts.** It only completes
when the DEFLECTED bullet kills the scripted gunner; any other goon standing
around eats the shot, the gunner survives, and the player is left blocking
forever with the scene stuck open. Killing off non-scripted enemies at
`startBlockScene` fixes it at the root, whatever the wave layout does.

**Warehouse is a two-storey cross-section now** (Kemar's reference: Katana Zero).
Ground floor -> 8-tread stair -> a 1360px UPPER FLOOR you fight along -> 8-tread
stair -> catwalk, with a stair back down at the far end. Enemies are placed on
both levels via "roof" spawns. `drawWarehouseProps()` adds the depth the painted
plate can't: support posts under the upper floor, strip lights slung beneath it
pooling light on the ground, pallet racking, hanging chains, hazard markings and
oil stains. Without it the building read as an empty box with catwalks stuck on.

**A stair run must actually REACH the floor it serves.** 7 treads of 19px only
climbs to 133, not to the 152 upper floor — `check_level.py` caught it. It now
also accepts a bottom tread within STEP_UP of the ground as connected.
