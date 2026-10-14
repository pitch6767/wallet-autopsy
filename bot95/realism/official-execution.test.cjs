const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {OfficialExecution}=require('./official-execution.cjs');
const file=process.env.OFFICIAL_SOURCE;
test('official decisions react to partial and cancellation-window fills, then settle',{skip:!file},()=>{
  const sim=new OfficialExecution(fs.readFileSync(file,'utf8'),{latencyMs:100,makerFeePerShare:0});
  const input={mk:{up:'u',down:'d'},t:10000,tleft:200,ua:[.55],da:[.5],P:{pu:.52},TOX:{},bids:{u:.5,d:.45}};
  sim.book('u',10000,{ask:.55,levels:{'.5':2,'0.5':2}});
  sim.book('d',10000,{ask:.5,levels:{'0.45':2}});
  sim.decision(input);
  sim.trade({id:'a',at:10120,sourceAt:10110,token:'u',side:'SELL',price:.5,quantity:12});
  assert.equal(sim.orders[0].remplR,10);
  sim.decision({...input,t:10150,bids:{u:.51,d:.45}});
  assert.equal(sim.orders[2].parts,+(45/.51).toFixed(2));
  sim.trade({id:'b',at:10200,sourceAt:10190,token:'u',side:'SELL',price:.5,quantity:4});
  assert.equal(sim.orders[0].remplR,14); // callback and ledger use the SAME object
  assert.equal(sim.snapshot().cost,7);
  sim.trade({id:'b',at:10200,sourceAt:10190,token:'u',side:'SELL',price:.5,quantity:4});
  assert.equal(sim.snapshot().cost,7);
  sim.decision({...input,t:10260,tleft:5});
  assert.equal(sim.orders[0].etat,'annulee');
  sim.expire(10400);
  const before=sim.snapshot(),{settleRecorded}=require('./settle-recorded.cjs');
  const confirmation={at:10401,winner:'Up',closed:true,resolved:true,evidence:'fixture'};
  const cached=settleRecorded(before,confirmation);
  assert.equal(cached.settlementPnl,7);
  assert.equal(settleRecorded(cached,{...confirmation,at:10500}).exposureMs,cached.exposureMs);
  assert.throws(()=>settleRecorded(before,{...confirmation,resolved:false}),/Confirmed/);
  assert.throws(()=>settleRecorded({...before,error:'uncertain'},confirmation),/Confirmed/);
  assert.throws(()=>sim.settle({at:10400,winner:'Up',closed:true,resolved:false,evidence:'test'}),/Confirmed/);
  assert.equal(sim.settle({at:10401,winner:'Up',closed:true,resolved:true,evidence:'synthetic fixture'}).settlementPnl,7);
});
test('freshness and uncertain late prints never silently validate',{skip:!file},()=>{
  const sim=new OfficialExecution(fs.readFileSync(file,'utf8'),{latencyMs:100,makerFeePerShare:0});
  const o=sim.place({up:'u',down:'d'},true,.5,10);
  sim.advance(100);
  assert.equal(o.etat,'rejetee');
  assert.ok(sim.snapshot().issues.length);
  assert.throws(()=>sim.trade({id:'x',at:99,sourceAt:99,token:'u',side:'SELL',price:.5,quantity:2}),/chronology/);
});
