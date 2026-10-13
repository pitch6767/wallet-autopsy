// Offline diagnostic: replay public prints against frozen historical quotes.
// NOT a backtest: historical quote decisions are not regenerated after changed fills.
const fs=require("node:fs"),zlib=require("node:zlib");
function replay(record,offers,{latencyMs=100,budget=50}={}){
  if(record.coupe)throw Error("Truncated recording");
  if(!Number.isFinite(latencyMs)||latencyMs<0||!Number.isFinite(budget)||budget<0)throw Error("Invalid assumptions");
  const seen=new Set(),stats=new Map();
  const orders=offers.filter(o=>o.type!=="resume"&&o.start===record.start&&Number.isFinite(o.tArrivee)&&Number.isFinite(o.qDevant))
    .map(o=>({...o,filled:0,queue:Math.max(0,o.qDevant),arrival:Math.max(o.tArrivee,o.tPose+latencyMs),
      // Keep original cancellation rather than invent an unobserved quote extension.
      end:Math.min(o.tAnnulee||Infinity,(o.start+300)*1000)}))
    .sort((a,b)=>a.arrival-b.arrival||String(a.oid).localeCompare(String(b.oid)))
    .filter(o=>{const k=o.variante+":"+o.oid;if(seen.has(k))return false;seen.add(k);return true;});
  for(const o of orders)if(!stats.has(o.variante))stats.set(o.variante,{strategy:o.variante,
    Up:0,Down:0,costUp:0,costDown:0,publishedUp:0,publishedDown:0,publishedCost:0,matchedPrints:0});
  for(const o of orders){const s=stats.get(o.variante);s["published"+o.cote]+=o.remplR;s.publishedCost+=o.remplR*o.prix;}
  const unique=new Set();let trades=0,duplicates=0;
  for(const t of record.ev.filter(t=>t[0]==="T").sort((a,b)=>a[2]-b[2])){
    const [_,received,source,token,side,price,volume]=t;
    if(side!==0||![received,source,price,volume].every(Number.isFinite)||volume<=0||received-source>1000||source-received>50)continue;
    const id=JSON.stringify([source,token,side,price,volume]);
    if(unique.has(id)){duplicates++;continue;}unique.add(id);trades++;
    const remaining=new Map();
    for(const o of orders){
      if((o.cote==="Up"?0:1)!==token||Math.abs(o.prix-price)>1e-9||source<o.arrival||source>=o.end||o.filled>=o.parts)continue;
      const s=stats.get(o.variante);
      let left=remaining.has(o.variante)?remaining.get(o.variante):volume;
      const ahead=Math.min(o.queue,left);o.queue-=ahead;left-=ahead;
      const fill=Math.min(left,o.parts-o.filled,Math.max(0,budget-s["cost"+o.cote])/o.prix);
      if(fill>0){o.filled+=fill;s[o.cote]+=fill;s["cost"+o.cote]+=fill*o.prix;s.matchedPrints++;}
      remaining.set(o.variante,left-fill);
    }
  }
  return {kind:"FROZEN_QUOTE_DIAGNOSTIC_NOT_BACKTEST",start:record.start,version:record.version,
    latencyMs,budget,trades,duplicates,strategies:[...stats.values()].map(s=>({...s,unmatched:Math.abs(s.Up-s.Down)})),
    limitations:["Exact-price SELL prints only; no mirror or trade-through inference.",
      "Historical queue snapshots; no inferred queue cancellations.",
      "Identical prints are deduplicated conservatively and might be distinct trades.",
      "Quote policy is frozen, not recomputed from replayed fills.",
      "Missing/unpublished orders are not reconstructed. No live PnL prediction."]};
}
module.exports={replay};
if(require.main===module){
 const[, ,rec,offers]=process.argv;
 if(!rec||!offers)throw Error("Usage: node replay-prints.cjs cycle.json.gz maker.json");
 const r=JSON.parse(zlib.gunzipSync(fs.readFileSync(rec)));
 console.log(JSON.stringify(replay(r,JSON.parse(fs.readFileSync(offers)).offres),null,2));
}
