'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {compare}=require('./recorded-comparison.cjs');
const HOME='/opt/bot95-comparison',OFFICIAL='/opt/bot95-rapide';
const atomic=(p,v)=>{fs.writeFileSync(p+'.tmp',JSON.stringify(v),{mode:0o644});fs.renameSync(p+'.tmp',p);};
async function main(){
  const source=fs.readFileSync(OFFICIAL+'/rapide.js','utf8');
  const version=source.match(/const VERSION = "([^"]+)"/)?.[1];
  if(!/^[a-f0-9]+$/.test(version||''))throw Error('Unknown official version');
  const ref=HOME+'/data/'+version+'.js';
  if(!fs.existsSync(ref))fs.writeFileSync(ref,source,{mode:0o600});
  let state={cycles:{}};
  if(fs.existsSync(HOME+'/data/state.json'))state=JSON.parse(fs.readFileSync(HOME+'/data/state.json'));
  const files=[];
  for(const day of fs.readdirSync(OFFICIAL+'/cycles').sort().slice(-2)){
    const dir=path.join(OFFICIAL,'cycles',day);
    if(!fs.statSync(dir).isDirectory())continue;
    for(const f of fs.readdirSync(dir))if(f.endsWith('.gz'))files.push(path.join(dir,f));
  }
  let checked=0;
  for(const file of files.sort().slice(-36).reverse()){
    const stat=fs.statSync(file),stamp=stat.mtimeMs+':'+stat.size;
    const old=state.cycles[file];
    if(old?.stamp===stamp&&(old.settled||old.excluded))continue;
    if(++checked>6)break; // bounded work; subsequent timer runs continue backlog
    let record;
    try{record=JSON.parse(zlib.gunzipSync(fs.readFileSync(file),{maxOutputLength:128*1024*1024}));}
    catch{state.cycles[file]={stamp,excluded:true,reason:'Unreadable recording'};continue;}
    if(!record.validation){state.cycles[file]={stamp,excluded:true,reason:'Before recorder installation',legacy:true};continue;}
    const result={stamp,start:record.start,version:record.version,settled:false,scenarios:[]};
    try{
      const historical=HOME+'/data/'+record.version+'.js';
      if(!fs.existsSync(historical))throw Error('Reference source for this version unavailable');
      const code=fs.readFileSync(historical,'utf8');
      const r=await fetch('https://gamma-api.polymarket.com/events?slug=btc-updown-5m-'+record.start,{signal:AbortSignal.timeout(12000)});
      if(!r.ok)throw Error('Resolution HTTP '+r.status);
      const m=(await r.json())[0]?.markets?.[0];
      if(m?.feeType!=='crypto_fees_v2'||m?.feesEnabled!==true)throw Error('Fee schedule unverified');
      const prices=JSON.parse(m.outcomePrices||'[]').map(Number),outcomes=JSON.parse(m.outcomes||'[]');
      const winner=m.closed===true&&m.umaResolutionStatus==='resolved'?outcomes[prices.indexOf(1)]:null;
      for(const delay of [100,250,500]){
        const replay=compare(record,code,delay);
        const before=replay.sim.snapshot();
        if(before.issues.length)throw Error(before.issues.join('; '));
        const snapshot=winner?replay.sim.settle({at:Math.max(Date.now(),replay.sim.at),winner,closed:true,resolved:true,evidence:{source:'Gamma',slug:m.slug}}):before;
        result.scenarios.push({latencyMs:delay,decisions:replay.decisions,roundingAdjustments:replay.rounding,...snapshot});
      }
      result.settled=!!winner;state.cycles[file]=result;
    }catch(e){
      // Transport/metadata failures are retried; invalid recordings remain explicit.
      state.cycles[file]={...result,excluded:true,reason:e.message};
      if(/HTTP|fetch|timeout|Fee schedule/.test(e.message))state.cycles[file].excluded=false;
    }
  }
  const rows=Object.values(state.cycles).filter(x=>!x.legacy).sort((a,b)=>(a.start||0)-(b.start||0));
  atomic(HOME+'/data/state.json',state);
  atomic(HOME+'/public/comparison.json',{at:Date.now(),officialVersion:version,
    officialSha256:require('node:crypto').createHash('sha256').update(source).digest('hex'),
    latestRecordedCycle:rows.length?Math.max(...rows.map(x=>x.start||0)):null,
    verdict:'PREUVES_INSUFFISANTES',mode:'REPLAY_DES_SIGNAUX_OFFICIELS',
    assumptions:'Maker 0; latences hypothétiques 100/250/500 ms; SELL au prix exact; file affichée; aucune exécution privée.',
    limitations:['Calibration réelle absente','Continuité réseau non prouvée par cet enregistrement','Expiration simulée en fin de cycle ; annulation privée non vérifiée','M10 uniquement : aucune revente ou couverture ajoutée à ses règles'],
    cycles:rows.length,settled:rows.filter(x=>x.settled).length,excluded:rows.filter(x=>x.excluded).length,
    recent:rows.slice(-12)});
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
