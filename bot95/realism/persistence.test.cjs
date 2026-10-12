const {test}=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),os=require("node:os"),path=require("node:path");
const ledger=require("./ledger.cjs");
function temp(t){const d=fs.mkdtempSync(path.join(os.tmpdir(),"bot95-ledger-"));t.after(()=>fs.rmSync(d,{recursive:true,force:true}));return d;}
const order={start:1200,variante:"M10",cote:"Up",prix:.5,oid:"test"};
test("durable fills survive restart, current interrupted cycle cannot quote",t=>{
  const dir=temp(t);let now=1200100;
  const a=ledger(dir,()=>now);a.offer(order);a.fill(order,20);a.close();
  now+=2000;const b=ledger(dir,()=>now);
  assert.equal(b.snapshot().rows[0].up,20);assert.equal(b.budget(1200,"M10","Up"),40);
  assert.equal(b.canQuote(1200),false);assert.equal(b.snapshot().rows[0].incomplete,true);
  now=1600000;b.settle(1200,"Down");assert.equal(b.snapshot().rows[0].settlementPnl,-10);b.close();
});
test("WAL recovers a fill not yet in checkpoint",t=>{
  const dir=temp(t);
  const {spawnSync}=require("node:child_process");
  const child=spawnSync(process.execPath,["-e",`const l=require(${JSON.stringify(path.join(__dirname,"ledger.cjs"))})(${JSON.stringify(dir)},()=>1200000);l.fill(${JSON.stringify(order)},15);process.exit(0);`]);
  assert.equal(child.status,0);
  const b=ledger(dir,()=>1205000);
  assert.equal(b.snapshot().rows[0].up,15);assert.equal(b.snapshot().rows[0].costUp,7.5);b.close();
});
test("torn WAL tail is preserved but not invented into inventory",t=>{
  const dir=temp(t),a=ledger(dir,()=>1200000);a.fill(order,10);a.close();
  fs.appendFileSync(dir+"/ledger-v2.wal",'{"sequence":');
  const b=ledger(dir,()=>1201000);assert.equal(b.snapshot().rows[0].up,10);
  assert.ok(fs.readdirSync(dir).some(x=>x.includes(".torn-")));b.close();
});
test("corrupt committed WAL fails explicitly",t=>{
  const dir=temp(t),a=ledger(dir,()=>1200000);a.close();
  fs.appendFileSync(dir+"/ledger-v2.wal","BROKEN\n");
  assert.throws(()=>ledger(dir,()=>1201000));
});
test("repeated settlement is idempotent and zero-fill rows remain",t=>{
  const dir=temp(t),a=ledger(dir,()=>1200000);a.offer(order);a.settle(1200,"Up");
  const seq=a.meta.sequence;a.settle(1200,"Up");assert.equal(a.meta.sequence,seq);
  assert.equal(a.snapshot().rows[0].settlementPnl,0);assert.equal(a.snapshot().rows[0].offers,1);a.close();
});
test("publisher retries failed batches and skips acknowledged unchanged rows",async t=>{
  const dir=temp(t);let calls=0,fail=true;
  const pub=require("./publish.cjs")(dir,"https://invalid",async(_url,opt)=>{
    calls++;const body=JSON.parse(opt.body);
    if(fail){fail=false;return {ok:false,status:500};}
    return {ok:true,json:async()=>({ok:true,cohort:body.cohort,sequence:body.sequence})};
  });
  const data={cohort:"test",sequence:1,rows:[{start:1200,strategy:"M10",up:1}]};
  await assert.rejects(pub(data),/500/);assert.equal(fs.existsSync(dir+"/publication.json"),false);
  assert.equal((await pub(data)).changed,1);
  assert.equal((await pub(data)).changed,0);assert.equal(calls,3);
});
test("daily report excludes interruptions and uses filled cycles as denominator",()=>{
  const base={start:1200,strategy:"M10",ended:true,winner:"Up",offers:10,up:100,down:10,
    unmatched:90,exposedMs:1000,shareSeconds:90,costUp:50,costDown:5,settlementPnl:45,singleLeg:false};
  const d={at:1600000,experimentStart:1200000,experimentEnd:87600000,rows:[base,{...base,start:1500,incomplete:true}]};
  const r=require("./daily-report.cjs").summarize(d);
  assert.equal(r.strategies[0].complete,1);assert.equal(r.strategies[0].pnl,45);
  assert.equal(r.strategies[0].imbalancedRate,1);assert.equal(r.strategies[0].singleLegRate,0);
  assert.equal(r.complete24h,false);
});
test("daily evidence catches excessive volume and invalid timestamps",()=>{
  const d={at:1600000,experimentStart:1200000,experimentEnd:87600000,rows:[]};
  const e={key:"1200:M10",event:{type:"fill",quantity:20,evidence:{key:"print1",volume:10,sourceMs:100,receivedMs:150,arrivalMs:110}}};
  const a=require("./daily-report.cjs").summarize(d,[e]).audit;
  assert.equal(a.volumeViolations,1);assert.equal(a.invalidTiming,1);
});
