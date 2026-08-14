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

AS_REWRITE = """
// The hidden tab can't reach the CDN at all - fetch and image decode both hang
// - so every character silently fails to load and the level renders empty.
// Repoint the manifest at the local mirror in _cdn/ (gitignored, copied from
// the Godot port's asset backup). Must run AFTER window.AS is defined and
// BEFORE the engine reads it. Harness only; the shipped build is untouched.
(()=>{const LOCAL={".gdignore":"","bat_attack":".png","bat_dead":".png","bat_idle":".png","bat_swing":".png","bat_walk1":".png","bat_walk2":".png","bat_walk3":".png","bat_walk4":".png","bg_cell":".png","bg_compound":".png","bg_compound_ext":".png","bg_downhill":".png","bg_far":".png","bg_forest_night":".png","bg_harbour":".png","bg_rooftop":".png","bg_ship":".png","bg_street":".png","bg_street2":".png","bg_street3":".png","bg_throne":".png","blade_attack":".png","blade_dead":".png","blade_idle":".png","blade_lunge":".png","blade_walk1":".png","blade_walk2":".jpeg","boat":".jpeg","bruiser_attack":".png","bruiser_dead":".png","bruiser_idle":".png","bruiser_strike":".png","bruiser_walk1":".png","bruiser_walk2":".jpeg","bullet":".png","derrick_charge":".png","derrick_dead":".jpeg","derrick_idle":".png","derrick_kick":".png","derrick_phone":".png","derrick_power":".png","derrick_sandal":".png","derrick_slap":".png","derrick_walk1":".png","derrick_walk2":".png","derrick_walk3":".png","derrick_walk4":".png","dock_ground":".png","dog_dead":".png","dog_idle":".png","dog_lunge":".png","dog_walk":".png","dog_walk2":".png","dup_idle":".png","dup_talk":".png","enemy_biker":".png","enemy_car":".png","favicon":".png","fyah_cast":".png","fyah_dead":".png","fyah_enrage":".png","fyah_idle":".png","fyah_kick":".png","fyah_punch":".jpeg","fyah_smoke":".png","fyah_walk1":".png","fyah_walk2":".png","fyah_walk3":".png","fyah_walk4":".png","goonA_attack":".png","goonA_attack2":".png","goonA_death":".png","goonA_idle":".png","goonA_walk":".png","goonA_walk1":".png","goonA_walk2":".png","goonA_walk3":".png","goonA_walk4":".png","goonB_attack":".png","goonB_attack2":".png","goonB_death":".png","goonB_idle":".png","goonB_walk":".png","goonB_walk1":".png","goonB_walk2":".png","goonB_walk3":".png","goonB_walk4":".png","goon_bikeA":".png","goon_bikeB":".png","gorgon_attack":".png","gorgon_attack2":".png","gorgon_cast":".png","gorgon_dead":".png","gorgon_enrage":".png","gorgon_idle":".png","gorgon_walk1":".png","gorgon_walk2":".png","ground":".png","gunner_dead":".png","gunner_idle":".png","gunner_shoot":".png","gunner_walk1":".png","gunner_walk2":".jpeg","hobo_sleep":".png","item_herb":".png","item_machete":".png","item_orb":".png","knife_attack":".png","knife_dead":".png","knife_idle":".png","knife_walk1":".png","knife_walk2":".png","knife_walk3":".png","knife_walk4":".png","lady_run1":".png","lady_run2":".png","lt_attack":".png","lt_attack2":".png","lt_cast":".png","lt_dead":".png","lt_death":".png","lt_enrage":".png","lt_idle":".png","lt_walk":".png","lt_walk1":".png","lt_walk2":".png","lt_walk3":".png","lt_walk4":".png","molotov_dead":".png","molotov_idle":".png","molotov_walk1":".png","molotov_walk2":".png","molotov_walk3":".png","molotov_walk4":".png","mosq_dead":".png","mosq_fly":".png","mosq_fly2":".png","mosq_swoop":".png","music_level1":".m4a","music_level2":".m4a","music_lt":".m4a","nc_attack_a":".png","nc_attack_b":".png","nc_bike1":".png","nc_bike2":".png","nc_bike3":".png","nc_bike4":".png","nc_bike5":".png","nc_bike6":".png","nc_bike7":".png","nc_bike8":".png","nc_block1":".png","nc_block2":".png","nc_block3":".png","nc_catk1":".png","nc_catk2":".png","nc_catk3":".png","nc_chain_fall":".png","nc_chain_idle":".png","nc_chain_jump":".png","nc_chain_land":".png","nc_chain_swing":".png","nc_chain_whip":".png","nc_crouch":".png","nc_crun1":".png","nc_crun2":".png","nc_crun3":".png","nc_crun4":".png","nc_cswing1":".png","nc_cswing2":".png","nc_cswing3":".png","nc_cthrow1":".png","nc_cthrow2":".png","nc_dash":".png","nc_death":".png","nc_death2":".png","nc_flip":".png","nc_flip2":".png","nc_flip3":".png","nc_hurt":".png","nc_idle":".png","nc_idle2":".png","nc_jump_fall":".png","nc_jump_land":".png","nc_jump_up":".png","nc_kick":".png","nc_kunai":".png","nc_moped":".png","nc_nrun1":".png","nc_nrun2":".png","nc_nrun3":".png","nc_nrun4":".png","nc_nrun5":".png","nc_nrun6":".png","nc_nrun7":".png","nc_nrun8":".png","nc_power_pose":".png","nc_run1":".jpeg","nc_run2":".jpeg","nc_run3":".png","nc_run4":".png","nc_run_a":".png","nc_run_b":".png","nc_slashA_wind":".png","nc_smoke":".png","nc_takedown":".png","nc_walk":".png","nc_walk2":".png","nc_walk_a":".png","nc_walk_b":".png","nc_walk_c":".png","palm_trunk":".jpeg","portrait_dup":".png","portrait_nc":".png","portrait_razor":".png","prop_barrel":".jpeg","prop_bus":".png","prop_car":".png","prop_container":".png","prop_container1":".png","prop_container2":".png","prop_crane":".png","prop_crane2":".png","prop_crate":".png","prop_dumpster":".png","prop_gangway":".png","prop_gantry":".png","prop_hobo":".png","prop_log":".png","prop_oildrum":".png","prop_pallets":".png","prop_rock":".png","prop_shipfront":".png","prop_shiptower":".png","prop_stall":".png","prop_warehouse":".png","prop_warehouse2":".png","rastaman":".png","road_dirt":".png","rock":".jpeg","searchlight":".png","sfx_alarm":".mp3","sfx_bark":".mp3","sfx_dash":".mp3","sfx_death":".mp3","sfx_grunt":".mp3","sfx_gunshot":".mp3","sfx_hit":".mp3","sfx_jump":".mp3","sfx_mosq":".mp3","sfx_pickup":".mp3","sfx_power_slash":".mp3","sfx_power_up":".mp3","sfx_reload":".mp3","sfx_slash":".mp3","shed_dred":".png","shield_attack":".png","shield_baton":".png","shield_dead":".png","shield_down":".png","shield_gun":".png","shield_idle":".png","shield_walk1":".png","shield_walk2":".png","shield_walk3":".png","shield_walk4":".png","ship_bow":".png","ship_deck_bg":".png","shotta_death":".png","shotta_enrage":".png","shotta_hurt":".png","shotta_idle":".png","shotta_reload":".png","shotta_shoot":".png","shotta_walk1":".png","shotta_walk2":".png","shotta_walk3":".png","shotta_walk4":".png","thumbnail":".jpeg","vendor":".png","vendor2":".png","voice_bomboclaat":".mp3","voice_dup_line":".wav","voice_goon2":".mp3","voice_gorgon_laugh":".mp3","voice_heybwoy":".mp3","voice_lt_taunt":".wav","voice_nc_dongorgon":".wav","voice_power":".mp3","voice_rasta":".mp3","voice_razor_enrage":".mp3","voice_shotta_enrage":".mp3","voice_shotta_meet":".mp3"}; let n=0;
 for(const k in window.AS){ if(LOCAL[k]&&/^https?:/.test(window.AS[k]||'')){ window.AS[k]='./_cdn/'+k+LOCAL[k]; n++; } }
 window.__localAssets=n;})();
"""

SHIM = """<script>
// timers keep running in a hidden tab; rAF does not
window.requestAnimationFrame=f=>setTimeout(()=>f(performance.now()),16);
window.cancelAnimationFrame=id=>clearTimeout(id);
// The game sizes its canvas to the window, so a snapshot is only as big as the
// viewport. Don't fight it by pinning canvas.width — that clobbers the game's
// own transform and renders the world into a corner. Resize the VIEWPORT instead
// (mcp resize_window / a real window) and the game scales itself correctly.

// A hidden tab eventually stops decoding images fetched by URL - the load
// event simply never fires - while the same bytes pulled with fetch() and
// handed over as a blob decode fine. Without this the game sits there with
// backgrounds missing and it looks exactly like a broken asset path.
(()=>{const D=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
 Object.defineProperty(HTMLImageElement.prototype,'src',{configurable:true,
  get(){return D.get.call(this);},
  set(v){ if(/^(blob:|data:)/.test(v)){D.set.call(this,v);return;}
    // Fall back to the plain path on any failure. Routing CDN sprites through
    // fetch() trips CORS and silently loses every character in the game, which
    // is much worse than a background that occasionally doesn't decode.
    fetch(v,{mode:'cors'}).then(r=>r.ok?r.blob():Promise.reject(0))
      .then(b=>D.set.call(this,URL.createObjectURL(b)))
      .catch(()=>D.set.call(this,v)); }});})();
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
# The manifest rewrite must land BETWEEN the assets block and the engine block:
# after window.AS exists, before the engine reads it.
k = out.index("</script>", out.index(SHIM) + len(SHIM)) + len("</script>")
out = out[:k] + "\n<script>" + AS_REWRITE + "</script>" + out[k:]
open(os.path.join(REPO, "_play.html"), "w", encoding="utf-8", newline="\n").write(out)
print(f"_play.html written ({len(out)//1024} KB)")
