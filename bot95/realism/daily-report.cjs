const fs=require("node:fs");
function summarize(data, events=[]) {
  const window=data.rows.filter(r=>r.start*1000>=data.experimentStart && r.start*1000<data.experimentEnd);
  const groups={};
  for(const r of window){
    const g=groups[r.strategy] ||= {strategy:r.strategy,cycles:0,complete:0,incomplete:0,pending:0,
      filledCycles:0,singleLegCycles:0,imbalancedCycles:0,offers:0,up:0,down:0,
      unmatched:0,exposedSeconds:0,shareSeconds:0,cost:0,pnl:0,budgetViolations:0};
    g.cycles++;g.offers+=r.offers;g.incomplete+=!!r.incomplete;
    if(!r.ended||!r.winner)g.pending++;
    g.budgetViolations+=!!r.budgetViolation;
    if(!r.ended||r.incomplete||!r.winner)continue;
    g.complete++;g.filledCycles+=(r.up+r.down)>0;g.singleLegCycles+=r.singleLeg;
    g.imbalancedCycles+=r.unmatched>.01;g.up+=r.up;g.down+=r.down;
    g.unmatched+=r.unmatched;g.exposedSeconds+=r.exposedMs/1000;g.shareSeconds+=r.shareSeconds;
    g.cost+=r.costUp+r.costDown;g.pnl+=r.settlementPnl;
  }
  const matched=new Map();let noEvidence=0,invalidTiming=0;
  const lags=[];
  for(const e of events) {
    if(e.event?.type!=="fill")continue;
    const f=e.event,p=f.evidence;
    if(!p){noEvidence++;continue;}
    const k=e.key+":"+p.key;
    const a=matched.get(k)||{quantity:0,available:p.volume};
    a.quantity+=f.quantity;matched.set(k,a);
    if(p.sourceMs<p.arrivalMs || (p.cancelMs!=null&&p.sourceMs>=p.cancelMs))invalidTiming++;
    lags.push(p.receivedMs-p.sourceMs);
  }
  lags.sort((a,b)=>a-b);
  const violations=[...matched.values()].filter(x=>x.quantity>x.available+.0001).length;
  const strategies=Object.values(groups).map(g=>({...g,
    singleLegRate:g.filledCycles?g.singleLegCycles/g.filledCycles:null,
    imbalancedRate:g.filledCycles?g.imbalancedCycles/g.filledCycles:null,
    pnlWith1bpCost:g.pnl-g.cost*.0001,pnlWith5bpCost:g.pnl-g.cost*.0005}));
  return {status:data.at<data.experimentEnd?"collecte en cours":"fenêtre de 24 h écoulée",
    complete24h:data.at>=data.experimentEnd,windowStart:data.experimentStart,windowEnd:data.experimentEnd,
    elapsedHours:Math.max(0,Math.min(data.at,data.experimentEnd)-data.experimentStart)/3600000,
    expectedCycles:288,observedCycles:new Set(window.map(r=>r.start)).size,
    excludedRows:window.filter(r=>r.incomplete).length,strategies,
    audit:{fillsWithEvidence:lags.length,noEvidence,volumeViolations:violations,invalidTiming,
      publicPrintLagP50:lags.length?lags[Math.floor(lags.length*.5)]:null,
      publicPrintLagP90:lags.length?lags[Math.floor(lags.length*.9)]:null},
    limitations:["latence d'ordres hypothétique ≥100 ms","frais maker supposés nuls ; sensibilités, pas barème vérifié",
      "file d'attente conservatrice non observable précisément","aucune exécution réelle confirmée",
      "aucun ordre fantôme n'est une preuve de rentabilité","taux single leg calculé sur cycles avec remplissage"]};
}
function build(dir,data) {
  const file=dir+"/ledger-v2.wal";
  const events=fs.existsSync(file)?fs.readFileSync(file,"utf8").trim().split("\n").filter(Boolean).map(x=>JSON.parse(x)):[];
  const report=summarize(data,events);
  require("./ledger.cjs").atomic(dir+"/daily-report.json",report);
  return report;
}
module.exports={summarize,build};
