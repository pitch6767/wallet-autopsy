// Isolated read-only dashboard + IP-authorized ingestion. Never calls trading code.
const headers={"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const json=(x,status=200)=>new Response(JSON.stringify(x),{status,headers});
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const page=`<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Bot95 — résultats corrigés</title>
<style>body{font:16px system-ui;background:#f4f6f9;color:#17283a;margin:0;padding:24px}main{max-width:1400px;margin:auto}h1{margin-bottom:8px}.card{background:white;border:1px solid #dce2ea;border-radius:8px;padding:20px;margin:16px 0}.muted{color:#56677a}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:10px;border-bottom:1px solid #dde3eb;text-align:right}td:first-child,th:first-child{text-align:left}.scroll{overflow:auto}button,select{padding:9px;border:1px solid #ccd;border-radius:4px;background:white}a{color:#125ca1}.bad{color:#a52020}.ok{color:#16683f}p{line-height:1.5}#status{font-weight:600}</style>
<main><a href="/">Ancien tableau — résultats non comparables</a><h1>Bot95 · résultats maker corrigés</h1>
<p class="muted">Fantôme uniquement. Aucun ordre réel. Les anciennes simulations restent séparées.</p>
<div class="card"><label>Campagne <select id="cohort"></select></label> <button id="refresh">Actualiser</button>
<p id="status" role="status">Chargement…</p><p id="coverage"></p><p id="quality"></p></div>
<div class="card"><h2>Bilan sur 24 heures</h2><p>Seuls les cycles terminés, réglés et sans interruption entrent dans le PnL ci-dessous. Un taux de single leg nul sans aucun cycle rempli n'est pas un succès.</p>
<div class="scroll"><table><thead><tr><th>Stratégie</th><th>Cycles valides</th><th>Cycles remplis</th><th>Incomplets</th><th>En attente</th><th>Single leg</th><th>Déséquilibrés</th><th>Parts non couvertes</th><th>Exposition (s)</th><th>Dépense</th><th>PnL réglé</th></tr></thead><tbody id="summary"></tbody></table></div></div>
<div class="card"><h2>Dernières positions connues</h2><p>Deux côtés achetés ne signifient pas deux quantités égales. Les positions d'un cycle interrompu restent visibles, mais leur PnL n'est pas validé.</p>
<div class="scroll"><table><thead><tr><th>Cycle / stratégie</th><th>État</th><th>Up</th><th>Down</th><th>Non couvert</th><th>Coût Up</th><th>Coût Down</th><th>PnL connu</th></tr></thead><tbody id="positions"></tbody></table></div></div>
<div class="card"><h2>Contrôle des remplissages et limites</h2><p id="audit"></p><ul id="limits"></ul><p>La fin des 24 heures n'est pas une certification de rentabilité. La priorité exacte en file et les latences d'ordres restent à calibrer sur des exécutions confirmées.</p><a id="download" href="/api/realism/status">Télécharger les mesures JSON</a></div></main>
<script>
const el=id=>document.getElementById(id),esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const n=x=>x==null?"—":Number(x).toLocaleString("fr-CH",{maximumFractionDigits:2});
const pct=x=>x==null?"Sans remplissage":n(100*x)+" %";
let busy=false;
async function load(){if(busy)return;busy=true;try{
const choice=el("cohort").value;const url="/api/realism/status"+(choice?"?cohort="+encodeURIComponent(choice):"");
const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);const d=await r.json();
const selected=d.cohort;el("cohort").innerHTML=(d.cohorts||[]).map(c=>'<option value="'+esc(c.cohort)+'" '+(c.cohort===selected?"selected":"")+'>'+esc(c.model)+" · "+esc(new Date(c.started).toLocaleString("fr-CH"))+'</option>').join("");
if(!d.meta){el("status").textContent="En attente du premier envoi du VPS.";return;}
const m=d.meta,report=m.report||{},age=Date.now()-m.at,stale=age>120000;
el("status").className=stale?"bad":"ok";
el("status").textContent=(stale?"DONNÉES PÉRIMÉES — ":"Collecte reçue — ")+new Date(m.at).toLocaleString("fr-CH");
el("coverage").textContent=n(report.elapsedHours)+" / 24 h · "+n(report.observedCycles)+" cycles observés / 288 attendus. "+(report.complete24h?"Fenêtre écoulée ; vérifier les lacunes et règlements en attente.":"Bilan provisoire, collecte en cours.");
el("quality").textContent=n(report.excludedRows)+" lignes exclues pour données incomplètes · "+n(m.interruptions)+" interruption(s).";
el("summary").innerHTML=(report.strategies||[]).map(s=>"<tr>"+[s.strategy,n(s.complete),n(s.filledCycles),n(s.incomplete),n(s.pending),pct(s.singleLegRate),pct(s.imbalancedRate),n(s.unmatched),n(s.exposedSeconds),n(s.cost),n(s.pnl)].map(x=>"<td>"+esc(x)+"</td>").join("")+"</tr>").join("")||'<tr><td colspan="11">Aucun cycle validé pour le moment.</td></tr>';
el("positions").innerHTML=(d.rows||[]).map(s=>"<tr>"+[new Date(s.start*1000).toLocaleString("fr-CH")+" · "+s.strategy,s.incomplete?"INCOMPLET":s.winner?"Réglé":s.ended?"Règlement attendu":"En cours",n(s.up),n(s.down),n(s.unmatched),n(s.costUp),n(s.costDown),n(s.settlementPnl)].map(x=>"<td>"+esc(x)+"</td>").join("")+"</tr>").join("");
const a=report.audit||{};el("audit").textContent=n(a.fillsWithEvidence)+" fills reliés à un print · "+n(a.volumeViolations)+" violations de volume · "+n(a.invalidTiming)+" incohérences temporelles. Retard public médian / p90 : "+n(a.publicPrintLagP50)+" / "+n(a.publicPrintLagP90)+" ms (pas une latence d'ordre).";
el("limits").innerHTML=(report.limitations||[]).map(x=>"<li>"+esc(x)+"</li>").join("");el("download").href=url;
}catch(e){el("status").className="bad";el("status").textContent="Collecte indisponible : "+e.message;}finally{busy=false;}}
el("cohort").onchange=load;el("refresh").onclick=load;load();setInterval(load,15000);
</script></html>`;

export class RealismStore {
  constructor(ctx){this.ctx=ctx;}
  async fetch(req) {
    const u=new URL(req.url);
    if(u.pathname==="/rapide-realiste")return new Response(page,{headers:{"content-type":"text/html; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"}});
    if(u.pathname==="/api/realism/ingest"&&req.method==="POST"){
      if(req.headers.get("cf-connecting-ip")!=="107.174.203.201")return json({error:"Forbidden"},403);
      const text=await req.text();
      if(text.length>200000)return json({error:"Batch too large"},413);
      let d;try{d=JSON.parse(text);}catch{return json({error:"Invalid JSON"},400);}
      if(d.schema!==2 || d.model!=="realism-2" || !/^[a-zA-Z0-9-]{1,80}$/.test(d.cohort||"") ||
        !finite(d.at)||!finite(d.started)||!Array.isArray(d.rows)||d.rows.length>100||
        !Number.isInteger(d.sequence)||d.sequence<0)return json({error:"Invalid envelope"},400);
      for(const r of d.rows) if(!Number.isInteger(r.start)||typeof r.strategy!=="string"||r.strategy.length>180 ||
        !["up","down","costUp","costDown","offers","exposedMs","shareSeconds"].every(k=>finite(r[k])&&r[k]>=0) ||
        (r.settlementPnl!=null&&!finite(r.settlementPnl)))return json({error:"Invalid row"},400);
      const storage=this.ctx.storage;
      await storage.transaction(async tx=>{
        const metaKey="meta:"+d.cohort,old=await tx.get(metaKey);
        if(!old || d.sequence>old.sequence || (d.sequence===old.sequence&&d.at>=old.at)){
          const {rows,...meta}=d;await tx.put(metaKey,meta);
          const latest=await tx.get("latest");
          if(!latest||d.started>=latest.started)await tx.put("latest",{cohort:d.cohort,started:d.started});
        }
        for(const r of d.rows){
          const key="row:"+d.cohort+":"+r.start+":"+r.strategy;
          const prev=await tx.get(key);
          if(!prev || d.sequence>prev.sequence || (d.sequence===prev.sequence&&d.at>=prev.at))
            await tx.put(key,{sequence:d.sequence,at:d.at,row:r});
        }
      });
      return json({ok:true,cohort:d.cohort,sequence:d.sequence,rows:d.rows.length});
    }
    if(u.pathname==="/api/realism/status"&&req.method==="GET"){
      const s=this.ctx.storage;
      const cohorts=[...(await s.list({prefix:"meta:",limit:100})).values()].map(x=>({cohort:x.cohort,model:x.model,started:x.started})).sort((a,b)=>b.started-a.started);
      const cohort=u.searchParams.get("cohort")||(await s.get("latest"))?.cohort;
      if(!cohort)return json({cohorts,meta:null,rows:[]});
      if(!/^[a-zA-Z0-9-]{1,80}$/.test(cohort))return json({error:"Invalid cohort"},400);
      const meta=await s.get("meta:"+cohort);
      const records=await s.list({prefix:"row:"+cohort+":",reverse:true,limit:300});
      return json({cohort,cohorts,meta:meta||null,rows:[...records.values()].map(x=>x.row).sort((a,b)=>b.start-a.start)});
    }
    return json({error:"Not found"},404);
  }
}
