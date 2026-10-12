const fs = require("node:fs");
module.exports = function measurements(dir, clock = Date.now) {
  const ledger=require("./ledger.cjs")(dir,clock);
  const run = clock();
  const rows = new Map();
  function advance(r) {
    const t = Math.min(clock(), (r.start + 300) * 1000);
    const dt = Math.max(0, t - r.at);
    const naked = Math.abs(r.up - r.down);
    if (naked > 0.01) r.exposedMs += dt;
    r.shareSeconds += naked * dt / 1000;
    r.at = t;
  }
  function row(o) {
    const key = `${o.start}:${o.variante}`;
    if (!rows.has(key)) rows.set(key, {start:o.start, strategy:o.variante,
      up:0, down:0, costUp:0, costDown:0, offers:0, exposedMs:0,
      shareSeconds:0, at:Math.min(clock(), (o.start+300)*1000)});
    return rows.get(key);
  }
  return {
    ledger,
    offer(o) { ledger.offer(o); },
    fill(o, n) {
      ledger.fill(o,n,o.fillEvidence);
    },
    settle(start, winner) {
      ledger.settle(start,winner);
      for (const r of rows.values()) if(r.start===start) {
        r.winner=winner;
        r.settlementPnl=(winner==="Up"?r.up:r.down)-r.costUp-r.costDown;
      }
    },
    snapshot() {
      const saved=ledger.snapshot();
      const out = saved.rows.map(r => {
        advance(r);
        return {...r, unmatched:Math.abs(r.up-r.down), paired:Math.min(r.up,r.down),
          singleLeg:(r.up>0)!==(r.down>0), ended:clock()>=(r.start+300)*1000,
          budgetViolation:r.costUp>50.0001 || r.costDown>50.0001};
      });
      const data = {...saved,run, at:clock(), model:"realism-2",
        assumptions:{minimumLatencyMs:100, orderLatencyMeasured:false, makerFee:0,
          mirrorBuyIgnored:true, cancellationsNeverAdvanceQueue:true,
          legacyModelsIdentical:true, liveOrders:false, publication:"Cloudflare séparé",
          restartContinuity:true}, rows:out};
      fs.writeFileSync(`${dir}/measurements.json.tmp`, JSON.stringify(data));
      fs.renameSync(`${dir}/measurements.json.tmp`, `${dir}/measurements.json`);
      fs.writeFileSync(`${dir}/measurements-${run}.json.tmp`, JSON.stringify(data));
      fs.renameSync(`${dir}/measurements-${run}.json.tmp`, `${dir}/measurements-${run}.json`);
      const esc=x=>String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
      const num=x=>x==null?"En attente":Number(x).toFixed(2);
      const html=`<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Bot95 — mesures corrigées</title>
      <style>body{font:16px system-ui;margin:30px;color:#152638}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:right}td:first-child{text-align:left}.scroll{overflow:auto}p{max-width:1000px;line-height:1.5}</style>
      <h1>Bot95 — mesures maker corrigées</h1><p>Relevé figé au ${esc(new Date(data.at).toISOString())}. Fantôme uniquement. Modèle conservateur : ventes au prix exact, aucun remplissage déduit d'un prix traversé. Une absence de fill simulé ne prouve pas qu'un ordre réel aurait échoué.</p>
      <p>Latence hypothétique ≥100 ms, frais maker supposés nuls. Champs prudent/proportionnel/optimiste identiques. PnL de règlement uniquement après marché fermé et résolu. Aucune preuve d'exécution réelle. Positions connues conservées après redémarrage ; cycles interrompus exclus des performances validées, sans inventer de fills pendant la coupure.</p>
      <div class="scroll"><table><thead><tr><th>Stratégie / cycle UTC</th><th>Offres</th><th>Up</th><th>Down</th><th>Non couvert</th><th>Dépense Up</th><th>Dépense Down</th><th>Exposition s</th><th>PnL réglé</th></tr></thead><tbody>${out.map(r=>`<tr><td>${esc(r.strategy)}<br>${esc(new Date(r.start*1000).toISOString())}</td><td>${r.offers}</td><td>${num(r.up)}</td><td>${num(r.down)}</td><td>${num(r.unmatched)}</td><td>${num(r.costUp)}</td><td>${num(r.costDown)}</td><td>${num(r.exposedMs/1000)}</td><td>${num(r.settlementPnl)}</td></tr>`).join("")}</tbody></table></div></html>`;
      fs.writeFileSync(`${dir}/report.html.tmp`,html);
      fs.renameSync(`${dir}/report.html.tmp`,`${dir}/report.html`);
      for (const [k,r] of rows) if(clock() > (r.start+300)*1000+3600000) {
        fs.appendFileSync(`${dir}/completed.ndjson`, JSON.stringify(out.find(x=>x.start===r.start&&x.strategy===r.strategy))+"\n");
        rows.delete(k);
      }
      return data;
    },
  };
};
