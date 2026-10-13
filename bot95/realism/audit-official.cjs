// Read-only audit of published ghost results. Never places orders or changes the bot.
const fs=require("node:fs");
function audit(data,hours=6){
  const source=data.offres.filter(r=>r.type!=="resume");
  if(!source.length)throw Error("No published offers");
  const latest=Math.max(...source.map(r=>r.start)),cut=latest-hours*3600;
  const rows=source.filter(r=>r.start>=cut),seen=new Set(),groups=new Map();
  let duplicates=0;
  for(const r of rows){
    if(!["Up","Down"].includes(r.cote)||![r.start,r.prix,r.remplR].every(Number.isFinite))throw Error("Invalid offer");
    const id=JSON.stringify([r.start,r.variante,r.oid]);
    if(seen.has(id)){duplicates++;continue;}seen.add(id);
    const k=JSON.stringify([r.start,r.variante]);
    const g=groups.get(k)||{strategy:r.variante,start:r.start,Up:0,Down:0,costUp:0,costDown:0};
    g[r.cote]+=r.remplR;g["cost"+r.cote]+=r.remplR*r.prix;groups.set(k,g);
  }
  const strategies=[...new Set([...groups.values()].map(g=>g.strategy))].sort().map(strategy=>{
    const cycles=[...groups.values()].filter(g=>g.strategy===strategy);
    const filled=cycles.filter(g=>g.Up+g.Down>0);
    const shares=filled.reduce((s,g)=>s+g.Up+g.Down,0);
    const unmatched=filled.reduce((s,g)=>s+Math.abs(g.Up-g.Down),0);
    const singleLeg=filled.filter(g=>(g.Up>0)!==(g.Down>0)).length;
    return {strategy,reportedCycles:cycles.length,filledCycles:filled.length,singleLegCycles:singleLeg,
      imbalancedOverOneShare:filled.filter(g=>Math.abs(g.Up-g.Down)>1).length,
      unmatchedShares:unmatched,unmatchedShareFraction:shares?unmatched/shares:null,
      sideCyclesOver50:cycles.reduce((s,g)=>s+(g.costUp>50.01)+(g.costDown>50.01),0),
      maximumSideSpend:Math.max(...cycles.flatMap(g=>[g.costUp,g.costDown]))};
  });
  return {verdict:"NOT_VALIDATED_FOR_LIVE",model:"published proportional fills (remplR)",
    firstReportedCycleUTC:new Date(Math.min(...rows.map(r=>r.start))*1000).toISOString(),
    lastReportedCycleUTC:new Date(latest*1000).toISOString(),windowHours:hours,rows:rows.length,
    duplicatesRemoved:duplicates,strategies,
    limitations:["Only published offers; absent/zero-fill cycles may be missing.",
      "Offers lack version identifiers: do not attribute the whole window to the current version.",
      "Unmatched share fraction is not time-weighted exposure.",
      "Spend above 50 is an observed amount, not proof of the intended budget for every strategy.",
      "Public prints and simulated fills are not private execution confirmations.",
      "No corrected PnL is invented; queue position, order latency and fees are not calibrated."]};
}
module.exports={audit};
if(require.main===module){
  if(!process.argv[2])throw Error("Usage: node audit-official.cjs maker.json [hours]");
  console.log(JSON.stringify(audit(JSON.parse(fs.readFileSync(process.argv[2],"utf8")),Number(process.argv[3]||6)),null,2));
}
