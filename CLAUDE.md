# NINJACLAAT — Web Game (Claude Code handoff)

Dark, cinematic Jamaican-ninja beat-em-up platformer. **This repo IS the live web game** — a finished, playable 4-level game shipped on GitHub Pages. Continue development here.

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
The maintained editable form is **three separate files** `dist/assets.js`, `dist/strings.js`, `dist/game.js`. They are **not committed** — they only ever lived in scratch. **Recreate them by splitting `index.html`'s three `<script>` blocks into `dist/*.js`**, edit those, then re-inline to rebuild `index.html`. (Then commit `dist/` so it's versioned.)

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
- **Levels** (`levelSel` 1–4 on the title menu):
  - **L1** Dark Beach — boss **Razor**. (Ground must use `images.ground`, level-gated: a bug once made L1 use the ship dock tile — fixed.)
  - **L2** Smuggler's Harbour — stealth takedowns, searchlights, double-jump + block learn-events, ship-deck seg2, boss **Shotta** (enrage, grenades).
  - **L3** Kingston — street seg1 (vendor shop spends BITS, spliff smoke, sub-boss **Derrick**: kick / phone-flash-blind / sandal) → rooftop seg2 (boss **Fyah**: fireballs, punch/kick, enrage, smoke-teleport). 2 segments via `shipfade`.
  - **L4** Don Gorgon's Compound — opens with an **L3 scripted defeat** (enraged Fyah blinds/finishes you) → **cell cutscene** (`bg_cell`) where **Dupree is revealed to be a hallucination / long dead**. Seg1 = compound exterior (`bg_compound_ext`): chain melee + **grapple (F)** swing over a gap under an overhead gantry; enemies goonA/goonB/gunner/dogs. Seg2 = **moped chase** (hill-climb style): diagonal dirt downhill (`bg_forest_night` + `road_dirt`), hero on animated bike `nc_bike1..8`, **goons on bikes** `goon_bikeA/B` + car `enemy_car` that only close the gap when you hit obstacles, **weed = boost**, **ramps = big air**, spinning wheels, escape meter. `updateMoped`/`drawMoped`.

### STORY
Amnesiac ninja washes ashore, guided by "Dupree." Razor → Shotta → Derrick/Fyah. L4 twist: **Dupree was a hallucination all along** (dead since the night the hero "died"). L4 ends fleeing to regroup with the old crew before **Don Gorgon** — the **final boss is NOT built yet**.

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
- **Build the Don Gorgon final boss / finale** (biggest missing piece).
- **Dedicated L3 music** (rooftop/Kingston currently reuses other tracks).
- **Balance pass** — especially moped-chase feel (gap rates, obstacle spacing, boost).
- Optional polish on any animation the owner re-records (drop clips through the video→frames pipeline above).

## RUN LOCALLY
Open `index.html` in a browser, or visit the live URL.
