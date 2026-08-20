NINJACLAAT — WAREHOUSE V2
==========================

This is a working replacement for Level 2's warehouse segment, not a prompt.

NEW PLAYABLE ROUTE
------------------
Ground loading floor (left -> right)
    -> right steel stairs
Middle mezzanine (right -> left)
    -> left stairs
Upper machinery floor (left -> right)
    -> freight-shaft drop
Ground exit unlocks
    -> continue to the ship hold

WHAT THE BUILD CHANGES
----------------------
- Removes the repeated/chopped architectural-bay warehouse.
- Uses one unique, cinematic three-storey warehouse environment plate.
- Rebuilds warehouse collision around an intentional playable route.
- Keeps collision geometry hidden so the art carries the scene.
- Adds middle/top-floor-aware enemy spawning.
- Adds a locked dispatch shutter to prevent sprinting straight along the bottom.
- Opens the freight shaft after reaching the upper route.
- Unlocks the exit only after dropping back to ground through the shaft.
- Leaves the rest of Level 2 intact: harbour, existing lessons, ship hold,
  weather deck and Shotta progression.

HOW TO APPLY
------------
The warehouse-v2-rebuild branch is automatically integrated by GitHub Actions.
The installer remains here as a reproducible fallback and build record.

Manual fallback from the ROOT of the NinjaClaat repo:

    python warehouse_v2/apply_warehouse_v2.py

The installer backs up the original maintained/deployed files once, patches
dist/game.js and dist/assets.js, copies the new art, runs Node syntax checks,
and runs the repo's existing tools/build.py to rebuild index.html.

This branch intentionally keeps main untouched until the new warehouse has been
reviewed and tested.
