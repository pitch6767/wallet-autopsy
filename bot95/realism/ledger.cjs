const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

function atomic(file, value) {
  const fd = fs.openSync(file + ".tmp", "w", 0o600);
  try { fs.writeFileSync(fd, JSON.stringify(value)); fs.fsyncSync(fd); }
  finally { fs.closeSync(fd); }
  fs.renameSync(file + ".tmp", file);
  const dir = fs.openSync(path.dirname(file), "r");
  try { fs.fsyncSync(dir); } finally { fs.closeSync(dir); }
}

module.exports = function ledger(dir, clock = Date.now) {
  fs.mkdirSync(dir, {recursive:true});
  const file = path.join(dir, "ledger-v2.json");
  const wal = path.join(dir, "ledger-v2.wal");
  let state = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file,"utf8")) : null;
  const restored = !!state;
  if (!state) {
    const experimentStart = Math.ceil(clock()/300000)*300000;
    state = {schema:2, cohort:crypto.randomUUID(), started:clock(), experimentStart,
      experimentEnd:experimentStart+86400000, sequence:0, lastHeartbeat:clock(), rows:{}};
    // Preserve known inventories from v1, but never call incomplete legacy data validated.
    const legacy = path.join(dir, "measurements.json");
    if (fs.existsSync(legacy)) {
      for (const row of JSON.parse(fs.readFileSync(legacy,"utf8")).rows || []) {
        const k = `${row.start}:${row.strategy}`;
        state.rows[k] = {...row, incomplete:true, reasons:["import incomplet du modèle précédent"]};
      }
    }
  }
  if (fs.existsSync(wal)) {
    const text = fs.readFileSync(wal,"utf8");
    const lines = text.split("\n");
    if (lines.at(-1) !== "") {
      // An interrupted final write is not replayable. Preserve evidence; trim only the tail.
      fs.writeFileSync(wal + ".torn-" + clock(), lines.at(-1));
      lines.pop();
      fs.writeFileSync(wal, lines.join("\n")+"\n");
    } else lines.pop();
    for (const line of lines) {
      if (!line) continue;
      const e = JSON.parse(line);
      if (e.sequence <= state.sequence) continue;
      if (e.sequence !== state.sequence+1) throw Error("Ledger sequence gap");
      state.rows[e.key] = e.row;
      state.sequence = e.sequence;
    }
  }
  const interruptedCycle = Math.floor(clock()/300000)*300;
  if (restored) {
    for (const r of Object.values(state.rows)) {
      if ((r.start+300)*1000 > state.lastHeartbeat) {
        r.incomplete=true;
        r.reasons=[...new Set([...(r.reasons||[]),"interruption : fills possibles non observés"])];
        r.at=Math.min(clock(),(r.start+300)*1000);
      }
    }
    state.interruptions=(state.interruptions||0)+1;
  }
  atomic(file,state);
  const fd = fs.openSync(wal,"a",0o600);
  let closed=false;
  const id = o=>`${o.start}:${o.variante}`;
  function row(o) {
    const key=id(o);
    const partial=o.start*1000<state.experimentStart||(restored&&o.start===interruptedCycle);
    if (!state.rows[key]) state.rows[key]={start:o.start,strategy:o.variante,up:0,down:0,
      costUp:0,costDown:0,offers:0,exposedMs:0,shareSeconds:0,
      at:Math.min(clock(),(o.start+300)*1000), incomplete:partial,
      reasons:partial?["cycle de démarrage / reprise partiel"]:[]};
    return state.rows[key];
  }
  function advance(r) {
    const t=Math.min(clock(),(r.start+300)*1000),dt=Math.max(0,t-r.at),q=Math.abs(r.up-r.down);
    if(q>0.01)r.exposedMs+=dt;
    r.shareSeconds+=q*dt/1000;
    r.at=t;
  }
  function durable(key,r,event) {
    const e={sequence:state.sequence+1,key,row:r,event,at:clock()};
    const line=JSON.stringify(e)+"\n";
    fs.writeSync(fd,line); fs.fsyncSync(fd);
    state.sequence=e.sequence;state.rows[key]=r;
  }
  return {
    meta:state,
    canQuote(start) {return !(restored && start===interruptedCycle);},
    budget(start,strategy,side) {
      const r=state.rows[`${start}:${strategy}`];
      return Math.max(0,50-(r?(side==="Up"?r.costUp:r.costDown):0));
    },
    offer(o) {const r=row(o);r.offers++;},
    fill(o,n,evidence) {
      const r={...row(o)};advance(r);
      r[o.cote==="Up"?"up":"down"]+=n;r[o.cote==="Up"?"costUp":"costDown"]+=n*o.prix;
      durable(id(o),r,{type:"fill",oid:o.oid,side:o.cote,price:o.prix,quantity:n,evidence});
    },
    pendingStarts() {
      return [...new Set(Object.values(state.rows).filter(r=>!r.winner && clock()>(r.start+360)*1000).map(r=>r.start))];
    },
    settle(start,winner) {
      if (!["Up","Down"].includes(winner)) throw Error("Invalid winner");
      for(const [k,r0] of Object.entries(state.rows)) if(r0.start===start && !r0.winner) {
        const r={...r0};advance(r);r.winner=winner;
        r.settlementPnl=(winner==="Up"?r.up:r.down)-r.costUp-r.costDown;
        durable(k,r,{type:"settlement",winner});
      }
    },
    heartbeat(healthy=true) {
      const t=clock(),gap=t-state.lastHeartbeat;
      if(gap>10000 || !healthy) {
        for(const r of Object.values(state.rows)) if((r.start+300)*1000>state.lastHeartbeat) {
          r.incomplete=true;r.reasons=[...new Set([...(r.reasons||[]),"lacune ou flux périmé"])];
        }
      }
      state.healthyMs=(state.healthyMs||0)+(healthy?Math.min(5000,Math.max(0,gap)):0);
      state.lastHeartbeat=t;
    },
    snapshot() {
      const rows=Object.values(state.rows).map(r=>{
        advance(r);
        return {...r,cohort:state.cohort,unmatched:Math.abs(r.up-r.down),
          paired:Math.min(r.up,r.down),singleLeg:(r.up>0)!==(r.down>0),
          ended:clock()>=(r.start+300)*1000,budgetViolation:r.costUp>50.0001||r.costDown>50.0001};
      });
      atomic(file,state);
      return {schema:2,model:"realism-2",cohort:state.cohort,sequence:state.sequence,
        started:state.started,experimentStart:state.experimentStart,experimentEnd:state.experimentEnd,
        at:clock(),interruptions:state.interruptions||0,healthyMs:state.healthyMs||0,rows};
    },
    close(){if(!closed){atomic(file,state);fs.closeSync(fd);closed=true;}},
  };
};
module.exports.atomic=atomic;
