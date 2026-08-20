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
    HERE / "wh_plate_v2.jpg",
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    print("ERROR: Missing required file(s):")
    for p in missing:
        print("  -", p)
    sys.exit(1)

game_path = ROOT / "dist" / "game.js"
assets_path = ROOT / "dist" / "assets.js"
strings_path = ROOT / "dist" / "strings.js"
index_path = ROOT / "index.html"
asset_dest = ROOT / "wh_plate_v2.jpg"

game = game_path.read_text(encoding="utf-8")
assets = assets_path.read_text(encoding="utf-8")
block = r'''/* ====================== L2: CONTINUOUS WAREHOUSE V3 =========================
   The warehouse is part of the harbour world, not a separate segment.
   Player flow:
     harbour -> warehouse doorway -> ground loading floor -> right stairs ->
     middle mezzanine -> left stairs -> upper machinery floor -> freight shaft ->
     ground exit -> outdoor apron -> freighter.
   The single painted warehouse plate is world-locked inside the dock map.        */
const WH={
  off:7350,w:2400,h:1028,
  groundF:0.842,midF:0.572,topF:0.304,roofF:0.050,
  leftStair:{x1:360,x2:675},rightStair:{x1:1690,x2:2035},
  shaft:{x1:1450,x2:1615},gateX:2105
};
const WH_OFF=WH.off, WH_END=WH.off+WH.w, WH_EXIT_END=WH_END+700;
const WH_Y0=Math.round(GROUND_Y-WH.groundF*WH.h);
const WH_F1=GROUND_Y;
const WH_F2=Math.round(WH_Y0+WH.midF*WH.h);
const WH_F3=Math.round(WH_Y0+WH.topF*WH.h);
const WH_TOP=Math.round(WH_Y0+WH.roofF*WH.h);
const whGX=(x)=>WH_OFF+x;
function inWarehouseX(x){return level===2&&seg===L2_DOCK&&x>=WH_OFF&&x<=WH_END;}
function warehouseVisible(){return level===2&&seg===L2_DOCK&&cam.x+VW>WH_OFF-120&&cam.x<WH_END+120;}
let whRoute={armed:false,done:false,hintCd:0};

function drawWarehouse(){
  if(!warehouseVisible())return;
  const im=images.wh_plate, x0=WH_OFF-cam.x;
  ctx.save();
  ctx.beginPath();
  ctx.rect(x0,WH_TOP-40,WH.w,GROUND_Y-WH_TOP+150);
  ctx.clip();

  if(im){
    ctx.drawImage(im,Math.round(x0),WH_Y0,WH.w,WH.h);
  } else {
    const air=ctx.createLinearGradient(0,WH_TOP,0,GROUND_Y);
    air.addColorStop(0,"#101a22"); air.addColorStop(1,"#26343b");
    ctx.fillStyle=air; ctx.fillRect(x0,WH_TOP,WH.w,GROUND_Y-WH_TOP);
    ctx.fillStyle="#59656d";
    ctx.fillRect(x0,WH_F2-10,WH.w,14);
    ctx.fillRect(x0,WH_F3-10,WH.w,14);
    ctx.strokeStyle="#46535c";ctx.lineWidth=6;
    for(let x=120;x<WH.w;x+=240){const sx=x0+x;ctx.beginPath();ctx.moveTo(sx,WH_TOP);ctx.lineTo(sx,GROUND_Y);ctx.stroke();}
    ctx.fillStyle="#17232a";
    for(let x=180;x<WH.w-140;x+=380)ctx.fillRect(x0+x,GROUND_Y-180,240,180);
  }

  const shx=whGX(WH.shaft.x1)-cam.x, shw=WH.shaft.x2-WH.shaft.x1;
  if(shx<VW+80&&shx+shw>-80){
    const sy=WH_F3-18, sh=GROUND_Y-sy;
    const sg=ctx.createLinearGradient(shx,0,shx+shw,0);
    sg.addColorStop(0,"rgba(2,4,7,0.82)");
    sg.addColorStop(0.5,"rgba(8,12,16,0.58)");
    sg.addColorStop(1,"rgba(2,4,7,0.82)");
    ctx.fillStyle=sg; ctx.fillRect(shx,sy,shw,sh);
    ctx.strokeStyle="rgba(116,129,136,0.58)";ctx.lineWidth=4;ctx.strokeRect(shx+4,sy+2,shw-8,sh-4);
    ctx.strokeStyle="rgba(105,118,126,0.34)";ctx.lineWidth=2;
    for(let yy=sy+24;yy<GROUND_Y;yy+=44){
      ctx.beginPath();ctx.moveTo(shx+6,yy);ctx.lineTo(shx+shw-6,yy+28);
      ctx.moveTo(shx+shw-6,yy);ctx.lineTo(shx+6,yy+28);ctx.stroke();
    }
    if(!whRoute.armed){
      ctx.fillStyle="#303941";ctx.fillRect(shx+4,WH_F2-9,shw-8,18);
      ctx.fillStyle="#d0a233";
      for(let xx=shx+8;xx<shx+shw-8;xx+=18)ctx.fillRect(xx,WH_F2-9,9,4);
    }
  }

  if(!whRoute.done){
    const gx=whGX(WH.gateX)-cam.x,gw=165,gy=GROUND_Y-224;
    if(gx<VW+gw&&gx+gw>-80){
      ctx.fillStyle="rgba(16,21,25,0.92)";ctx.fillRect(gx,gy,gw,224);
      for(let yy=gy;yy<GROUND_Y;yy+=18){
        ctx.fillStyle=(Math.floor((yy-gy)/18)%2)?"#242c31":"#20272c";
        ctx.fillRect(gx,yy,gw,16);
      }
      ctx.fillStyle="#8b6b1e";ctx.fillRect(gx,GROUND_Y-8,gw,8);
      ctx.strokeStyle="rgba(145,160,170,0.48)";ctx.lineWidth=3;ctx.strokeRect(gx+1,gy+1,gw-2,222);
    }
  }

  ctx.fillStyle="rgba(210,225,230,0.11)";
  for(let i=0;i<18;i++){
    const wx=((i*337+now*0.010)%WH.w),sx=x0+wx;
    if(sx<-10||sx>VW+10)continue;
    const yy=WH_TOP+70+((i*97+now*0.006)%(GROUND_Y-WH_TOP-100));
    ctx.fillRect(sx,yy,1.5,1.5);
  }
  ctx.restore();
}

function updateWarehouseRoute(){
  if(!inWare())return;
  if(whRoute.hintCd>0)whRoute.hintCd--;
  const lx=player.x-WH_OFF;

  if(!whRoute.armed&&player.y<=WH_F3+18&&lx>WH.shaft.x1-180){
    whRoute.armed=true;
    platforms=platforms.filter(p=>!p.whTrap);
    floatText(player.x,player.y-HERO_H-10,"FREIGHT SHAFT OPEN","#ffd86b");
    shake=Math.max(shake,4);sfx("sfx_reload");
  }
  if(whRoute.armed&&!whRoute.done&&player.y>=GROUND_Y-2&&
     lx>WH.shaft.x1-90&&lx<WH.shaft.x2+90){
    whRoute.done=true;
    floatText(player.x,player.y-HERO_H-12,"EXIT ACCESS OPEN","#5dffa6");
    sfx("sfx_pickup");
  }
  if(!whRoute.done&&player.y>WH_F2+86&&lx>WH.gateX){
    player.x=whGX(WH.gateX);player.vx=Math.min(0,player.vx);
    if(whRoute.hintCd<=0){
      whRoute.hintCd=150;
      floatText(whGX(WH.gateX)-45,GROUND_Y-244,"CONTROL ROOM ABOVE","#ffd86b");
    }
  }
}

function appendWarehouseToHarbour(){
  whRoute={armed:false,done:false,hintCd:0};
  const slab=(x1,x2,top,floor,opt)=>{
    opt=opt||{};if(x2-x1<8)return;
    platforms.push(Object.assign({
      x:whGX((x1+x2)/2),w:x2-x1,top,deck:1,hide:1,whFloor:floor
    },opt));
  };
  const stairs=(x1,x2,y1,y2,floor)=>{
    const rise=Math.abs(y2-y1),n=Math.max(6,Math.ceil(rise/18));
    const tw=Math.abs(x2-x1)/n;
    for(let k=1;k<=n;k++){
      const t=k/n;
      platforms.push({
        x:whGX(x1+(x2-x1)*t),w:tw+3,top:y1+(y2-y1)*t,
        step:1,hide:1,whFloor:floor
      });
    }
  };

  slab(325,WH.shaft.x1,WH_F2,2);
  slab(WH.shaft.x1,WH.shaft.x2,WH_F2,2,{whTrap:1});
  slab(WH.shaft.x2,2055,WH_F2,2);
  slab(650,WH.shaft.x1,WH_F3,3);
  slab(WH.shaft.x2,2140,WH_F3,3);
  stairs(2025,1705,WH_F1,WH_F2,2);
  stairs(390,665,WH_F2,WH_F3,3);

  const box=(x,w,top,opt)=>platforms.push(Object.assign({
    x:whGX(x),w,top,hide:1,cover:1
  },opt||{}));
  box(515,132,GROUND_Y-94);
  box(860,118,GROUND_Y-82);
  box(1125,148,GROUND_Y-108);
  box(1835,112,GROUND_Y-88);
  box(870,122,WH_F2-84,{base:WH_F2,whFloor:2});
  box(1870,108,WH_F2-90,{base:WH_F2,whFloor:2});

  const ww=[
    [["crew",520,"aggro"],["goonA",780,"patrol"]],
    [["blade",1120,"aggro"],["bruiser",1380,"aggro"]],
    [["gunner",1900,"aggro","mid"],["crew",1760,"aggro","mid"]],
    [["blade",1260,"aggro","mid"],["gunner",980,"aggro","mid"]],
    [["gunner",760,"aggro","top"],["crew",920,"aggro","top"]],
    [["blade",1110,"aggro","top"],["gunner",1300,"aggro","top"]],
    [["bruiser",1370,"aggro","top"]],
    [["crew",1770,"aggro"],["goonB",1940,"aggro"]],
    [["bruiser",2140,"aggro"],["blade",2250,"aggro"]],
  ];
  for(const wave of ww){
    waves.push(wave.map(w=>[w[0],whGX(w[1]),w[2],w[3]].filter(v=>v!==undefined)));
  }
  pickups.push(
    {x:whGX(1840),y:WH_F2-42,vy:null,kind:"herb",val:1,t:0},
    {x:whGX(1030),y:WH_F3-42,vy:null,kind:"herb",val:1,t:0},
    {x:whGX(1880),y:GROUND_Y-42,vy:null,kind:"herb",val:1,t:0}
  );

  platforms.push(
    {x:WH_END+165,w:96,top:GROUND_Y-58,sprite:"prop_oildrum",cover:1},
    {x:WH_END+410,w:180,top:GROUND_Y-92,sprite:"prop_crates_ai",cover:1}
  );
  waves.push(
    [["crew",WH_END+180,"aggro"],["goonB",WH_END+390,"aggro"]],
    [["bruiser",WH_END+545,"aggro"]]
  );
}

function buildWarehouse(){
  buildHarbour();
  blockTutDone=true;djumpTutDone=true;scene=null;boarded=false;
  player.x=WH_OFF-220;player.y=GROUND_Y;player.vx=0;player.vy=0;player.onGround=true;
  player._safe=player.x;player._safeY=GROUND_Y;
  cam.x=Math.max(0,player.x-VW*0.38);cam.y=0;camTop=0;
}
'''.rstrip() + "\n\n"

for p in (game_path, assets_path, index_path):
    if p.exists():
        bak = p.with_name(p.name + ".warehouse_v2.bak")
        if not bak.exists():
            shutil.copy2(p, bak)

start = -1
for marker in (
    "/* ====================== L2: CONTINUOUS WAREHOUSE V3",
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

route_pat = re.compile(
    r'const L2_DOCK=1, L2_WARE=2, L2_HOLD=3, L2_DECK=4;\n'
    r'const onDock =\(\)=>level===2&&seg===L2_DOCK;\n'
    r'const inWare =\(\)=>level===2&&seg===L2_WARE;\n'
    r'const inHold =\(\)=>level===2&&seg===L2_HOLD;\n'
    r'const onDeck =\(\)=>level===2&&seg===L2_DECK;\n'
    r'/\* Which segment follows which,.*?\*/\n'
    r'const L2_NEXT=\{\[L2_DOCK\]:\(\)=>buildWarehouse\(\),\[L2_WARE\]:\(\)=>buildShipHold\(\),\n'
    r'\s*\[L2_HOLD\]:\(\)=>buildShipDeck\(\)\};',
    re.S,
)
route_new = '''const L2_DOCK=1, L2_WARE=2, L2_HOLD=3, L2_DECK=4;
const onDock =()=>level===2&&seg===L2_DOCK;
// Warehouse V3 lives inside the dock map. L2_WARE remains only as a legacy
// debug id so old bookmarks/dev helpers do not break.
const inWare =()=>level===2&&seg===L2_DOCK&&inWarehouseX(player.x);
const inHold =()=>level===2&&seg===L2_HOLD;
const onDeck =()=>level===2&&seg===L2_DECK;
const L2_NEXT={[L2_DOCK]:()=>buildShipHold(),[L2_HOLD]:()=>buildShipDeck()};'''
game2, n = route_pat.subn(route_new, game, count=1)
if n:
    game = game2
elif "const L2_NEXT={[L2_DOCK]:()=>buildShipHold(),[L2_HOLD]:()=>buildShipDeck()};" not in game:
    raise RuntimeError("Could not update L2 route table.")

game = game.replace(
    "function dryPit(x){ return level===3||inHold()||inWare(); }",
    "function dryPit(x){ return level===3||inHold()||inWarehouseX(x); }",
    1,
)

hb0 = game.find("function buildHarbour(){")
hb1 = game.find("/* ---- L2 seg 2: INSIDE the ship.", hb0)
if hb0 < 0 or hb1 < 0:
    raise RuntimeError("Could not locate buildHarbour().")
hb = game[hb0:hb1]
hb = hb.replace(
    "function buildHarbour(){ LEVEL_W=7400; seg=L2_DOCK;",
    "function buildHarbour(){ LEVEL_W=WH_EXIT_END; seg=L2_DOCK;",
    1,
)
if "appendWarehouseToHarbour();" not in hb:
    anchor = "  waveIdx=0; spawnWave();\n}"
    if anchor not in hb:
        raise RuntimeError("Could not locate end of buildHarbour().")
    hb = hb.replace(anchor, "  appendWarehouseToHarbour();\n  waveIdx=0; spawnWave();\n}", 1)
game = game[:hb0] + hb + game[hb1:]

old_pair = '''    if(onDock()&&!scene&&!boarded&&player.x>LEVEL_W-300){ boarded=true; player.cine=1; player.vx=0; setState("cutscene"); runDialogue(STR.level2_warehouse,()=>{ state="shipfade"; fadeT=72; }); return; }
    // out the far end of the warehouse and down to the freighter
    if(inWare()&&!scene&&!boarded&&whRoute.done&&player.x>LEVEL_W-240&&player.y>=GROUND_Y-2){ boarded=true; player.cine=1; player.vx=0; setState("cutscene"); runDialogue(STR.level2_board,()=>{ state="shipfade"; fadeT=72; }); return; }
'''
new_pair = '''    // Harbour -> warehouse -> outdoor apron is one continuous world. Fade only
    // when NinjaClaat actually boards the freighter.
    if(onDock()&&!scene&&!boarded&&whRoute.done&&player.x>LEVEL_W-260&&player.y>=GROUND_Y-2){ boarded=true; player.cine=1; player.vx=0; setState("cutscene"); runDialogue(STR.level2_board,()=>{ state="shipfade"; fadeT=72; }); return; }
'''
if old_pair in game:
    game = game.replace(old_pair, new_pair, 1)
elif "whRoute.done&&player.x>LEVEL_W-260" not in game:
    raise RuntimeError("Could not replace dock/warehouse transition.")

old_update = "    updatePlayer(); if(inWare())updateWarehouseRoute(); for(const e of enemies)updateEnemy(e);"
new_update = '''    updatePlayer();
    if(level===2&&seg===L2_DOCK){ camTop=inWare()?395:0; if(inWare())updateWarehouseRoute(); }
    for(const e of enemies)updateEnemy(e);'''
if old_update in game:
    game = game.replace(old_update, new_update, 1)
elif "camTop=inWare()?395:0" not in game:
    raise RuntimeError("Could not update warehouse camera/route tick.")

game = game.replace(
    '  else if(seg===L2_WARE){ ctx.fillStyle="#05080c"; ctx.fillRect(0,-camTop-40,VW,VH+camTop+80); } // warehouse: drawWarehouse paints it\n',
    "",
    1,
)

game = game.replace("cx=8960-cam.x", "cx=(LEVEL_W-420)-cam.x", 1)

old_dbg = 'if(location.hostname==="localhost"||location.hostname==="127.0.0.1"){' 
new_dbg = 'if(location.hostname==="localhost"||location.hostname==="127.0.0.1"||new URLSearchParams(location.search).has("dev")){' 
if old_dbg in game:
    game = game.replace(old_dbg, new_dbg, 1)

old_pf = 'const pf=platforms.find(q=>!q.noland&&q.top<GROUND_Y-110&&Math.abs(q.x-sx)<q.w/2);'
new_pf = '''const pf=platforms.find(q=>!q.noland&&q.top<GROUND_Y-110&&Math.abs(q.x-sx)<q.w/2&&
          (w[3]==="top"?q.whFloor===3:w[3]==="mid"?q.whFloor===2:true));'''
if old_pf in game:
    game = game.replace(old_pf, new_pf, 1)

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

checks = [
    ("continuous warehouse block", "CONTINUOUS WAREHOUSE V3" in game),
    ("warehouse merged into harbour", "appendWarehouseToHarbour();" in game),
    ("continuous map width", "LEVEL_W=WH_EXIT_END" in game),
    ("dock routes directly to hold", "const L2_NEXT={[L2_DOCK]:()=>buildShipHold(),[L2_HOLD]:()=>buildShipDeck()};" in game),
    ("zone-based warehouse", "seg===L2_DOCK&&inWarehouseX(player.x)" in game),
    ("no warehouse entry fade", "runDialogue(STR.level2_warehouse" not in game),
    ("dynamic warehouse camera", "camTop=inWare()?395:0" in game),
    ("browser dev hook", 'new URLSearchParams(location.search).has("dev")' in game),
]
bad = [name for name, ok in checks if not ok]
if bad:
    raise RuntimeError("Patch sanity check failed: " + ", ".join(bad))

game_path.write_text(game, encoding="utf-8")

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

print("\nContinuous Warehouse V3 integrated successfully.")
print("Harbour -> warehouse -> outdoor apron is now one Level 2 world.")
