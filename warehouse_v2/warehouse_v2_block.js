/* ============================ L2 seg 2: THE WAREHOUSE V2 ====================
   One unique, cinematic warehouse plate. The route snakes through the same
   building instead of repeating architectural bays:
     ground loading floor -> right stair -> middle mezzanine -> left stair ->
     upper machinery floor -> freight-shaft drop -> ground exit.
   Collision is authored to the visible structure and kept hidden so the art,
   not debug-looking slabs, carries the scene.                                      */
const WH={
  w:2400,h:1028,
  groundF:0.842, midF:0.572, topF:0.304, roofF:0.050,
  leftStair:{x1:360,x2:675}, rightStair:{x1:1690,x2:2035},
  shaft:{x1:1450,x2:1615}, gateX:2105
};
const WH_Y0=Math.round(GROUND_Y-WH.groundF*WH.h);
const WH_F1=GROUND_Y;
const WH_F2=Math.round(WH_Y0+WH.midF*WH.h);
const WH_F3=Math.round(WH_Y0+WH.topF*WH.h);
const WH_TOP=Math.round(WH_Y0+WH.roofF*WH.h);
const WH_X1=92, WH_X2=WH.w-92;
const whIndoor=(x)=>x>WH_X1&&x<WH_X2;
let whRoute={armed:false,done:false,hintCd:0};

function drawWarehouse(){ if(!inWare())return;
  const im=images.wh_plate;
  ctx.save();
  ctx.fillStyle="#04070a";
  ctx.fillRect(0,-camTop-80,VW,VH+camTop+160);

  if(im){
    ctx.drawImage(im,Math.round(-cam.x),WH_Y0,WH.w,WH.h);
  } else {
    const x0=-cam.x;
    ctx.fillStyle="#111820"; ctx.fillRect(x0,WH_TOP,WH.w,GROUND_Y-WH_TOP);
    ctx.fillStyle="#202b33";
    ctx.fillRect(x0,WH_F2-12,WH.w,18); ctx.fillRect(x0,WH_F3-12,WH.w,18);
    ctx.strokeStyle="#5a6770"; ctx.lineWidth=4;
    for(let x=120;x<WH.w;x+=240){const sx=x-cam.x;ctx.beginPath();ctx.moveTo(sx,WH_TOP);ctx.lineTo(sx,GROUND_Y);ctx.stroke();}
  }

  const shx=WH.shaft.x1-cam.x, shw=WH.shaft.x2-WH.shaft.x1;
  if(shx<VW+80&&shx+shw>-80){
    const sy=WH_F3-18, sh=GROUND_Y-sy;
    const sg=ctx.createLinearGradient(shx,0,shx+shw,0);
    sg.addColorStop(0,"rgba(2,4,7,0.92)"); sg.addColorStop(0.5,"rgba(8,12,16,0.70)"); sg.addColorStop(1,"rgba(2,4,7,0.92)");
    ctx.fillStyle=sg; ctx.fillRect(shx,sy,shw,sh);
    ctx.strokeStyle="rgba(116,129,136,0.58)"; ctx.lineWidth=4;
    ctx.strokeRect(shx+4,sy+2,shw-8,sh-4);
    ctx.strokeStyle="rgba(105,118,126,0.34)"; ctx.lineWidth=2;
    for(let yy=sy+24;yy<GROUND_Y;yy+=44){ctx.beginPath();ctx.moveTo(shx+6,yy);ctx.lineTo(shx+shw-6,yy+28);ctx.moveTo(shx+shw-6,yy);ctx.lineTo(shx+6,yy+28);ctx.stroke();}
    if(!whRoute.armed){
      ctx.fillStyle="#303941"; ctx.fillRect(shx+4,WH_F2-9,shw-8,18);
      ctx.fillStyle="#d0a233";
      for(let xx=shx+8,n=0;xx<shx+shw-8;xx+=18,n++)ctx.fillRect(xx,WH_F2-9,9,4);
    }
  }

  if(!whRoute.done){
    const gx=WH.gateX-cam.x, gw=165, gy=GROUND_Y-224;
    if(gx<VW+gw&&gx+gw>-80){
      ctx.fillStyle="rgba(16,21,25,0.96)";ctx.fillRect(gx,gy,gw,224);
      for(let yy=gy;yy<GROUND_Y;yy+=18){ctx.fillStyle=(Math.floor((yy-gy)/18)%2)?"#242c31":"#20272c";ctx.fillRect(gx,yy,gw,16);}
      ctx.fillStyle="#8b6b1e";ctx.fillRect(gx,GROUND_Y-8,gw,8);
      ctx.strokeStyle="rgba(145,160,170,0.48)";ctx.lineWidth=3;ctx.strokeRect(gx+1,gy+1,gw-2,222);
    }
  }

  ctx.fillStyle="rgba(210,225,230,0.11)";
  for(let i=0;i<18;i++){
    const wx=((i*337+now*0.010)%WH.w), sx=wx-cam.x;
    if(sx<-10||sx>VW+10)continue;
    const yy=WH_TOP+70+((i*97+now*0.006)%(GROUND_Y-WH_TOP-100));
    ctx.fillRect(sx,yy,1.5,1.5);
  }
  ctx.restore();
}

function updateWarehouseRoute(){
  if(!inWare())return;
  if(whRoute.hintCd>0)whRoute.hintCd--;

  if(!whRoute.armed && player.y<=WH_F3+18 && player.x>WH.shaft.x1-180){
    whRoute.armed=true;
    platforms=platforms.filter(p=>!p.whTrap);
    floatText(player.x,player.y-HERO_H-10,"FREIGHT SHAFT OPEN","#ffd86b");
    shake=Math.max(shake,4); sfx("sfx_reload");
  }
  if(whRoute.armed&&!whRoute.done&&player.y>=GROUND_Y-2&&player.x>WH.shaft.x1-90&&player.x<WH.shaft.x2+90){
    whRoute.done=true;
    floatText(player.x,player.y-HERO_H-12,"EXIT ACCESS OPEN","#5dffa6");
    sfx("sfx_pickup");
  }
  if(!whRoute.done&&player.y>WH_F2+86&&player.x>WH.gateX){
    player.x=WH.gateX; player.vx=Math.min(0,player.vx);
    if(whRoute.hintCd<=0){
      whRoute.hintCd=150;
      floatText(WH.gateX-45,GROUND_Y-244,"CONTROL ROOM ABOVE","#ffd86b");
    }
  }
}

function buildWarehouse(){
  seg=L2_WARE; mopedMode=false; boarded=false; fadeT=0; scene=null; shipDeck=null;
  bossDefeated=false; bossActive=false; bossDeathT=0;
  enemies=[]; projectiles=[]; pickups=[]; particles=[]; floaters=[]; ghosts=[];
  slashArcs=[]; searchlights=[]; shadows=[]; gaps=[];
  blockTutDone=true; djumpTutDone=true;
  LEVEL_W=WH.w;
  camTop=395; cam.x=0; cam.y=0;
  whRoute={armed:false,done:false,hintCd:0};
  player.x=110; player.y=GROUND_Y; player.vx=0; player.vy=0; player.onGround=true;
  player._safe=110; player._safeY=GROUND_Y;

  const P=[];
  const slab=(x1,x2,top,floor,opt)=>{
    opt=opt||{}; if(x2-x1<8)return;
    P.push(Object.assign({x:(x1+x2)/2,w:x2-x1,top,deck:1,hide:1,whFloor:floor},opt));
  };
  const stairs=(x1,x2,y1,y2,floor)=>{
    const rise=Math.abs(y2-y1), n=Math.max(6,Math.ceil(rise/18));
    const tw=Math.abs(x2-x1)/n;
    for(let k=1;k<=n;k++){
      const t=k/n;
      P.push({x:x1+(x2-x1)*t,w:tw+3,top:y1+(y2-y1)*t,step:1,hide:1,whFloor:floor});
    }
  };

  slab(325,WH.shaft.x1,WH_F2,2);
  slab(WH.shaft.x1,WH.shaft.x2,WH_F2,2,{whTrap:1});
  slab(WH.shaft.x2,2055,WH_F2,2);

  slab(650,WH.shaft.x1,WH_F3,3);
  slab(WH.shaft.x2,2140,WH_F3,3);

  stairs(2025,1705,WH_F1,WH_F2,2);
  stairs(390,665,WH_F2,WH_F3,3);

  P.push({x:515,w:132,top:GROUND_Y-94,hide:1,cover:1});
  P.push({x:860,w:118,top:GROUND_Y-82,hide:1,cover:1});
  P.push({x:1125,w:148,top:GROUND_Y-108,hide:1,cover:1});
  P.push({x:1835,w:112,top:GROUND_Y-88,hide:1,cover:1});
  P.push({x:870,w:122,top:WH_F2-84,base:WH_F2,hide:1,cover:1,whFloor:2});
  P.push({x:1870,w:108,top:WH_F2-90,base:WH_F2,hide:1,cover:1,whFloor:2});
  platforms=P;

  waves=[
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
  pickups=[
    {x:1840,y:WH_F2-42,vy:null,kind:"herb",val:1,t:0},
    {x:1030,y:WH_F3-42,vy:null,kind:"herb",val:1,t:0},
    {x:1880,y:GROUND_Y-42,vy:null,kind:"herb",val:1,t:0}
  ];
  waveIdx=0; spawnWave();
}
