const {test}=require("node:test"),assert=require("node:assert/strict"),{replay}=require("./replay-prints.cjs");
const o={start:1200,variante:"M10",oid:"a",cote:"Up",prix:.5,parts:100,tPose:1200000,tArrivee:1200010,qDevant:0,remplR:100};
const t=["T",1200250,1200200,0,0,.5,10];
test("one strategy cannot spend one print twice",()=>{
 const r=replay({start:1200,ev:[t,t]},[o,{...o,oid:"b"}]);assert.equal(r.strategies[0].Up,10);assert.equal(r.duplicates,1);
});
test("arrival, cancellation, side and price filters apply",()=>{
 const r=replay({start:1200,ev:[t]},[{...o,tAnnulee:1200199}]);assert.equal(r.strategies[0].Up,0);
 assert.equal(replay({start:1200,ev:[t]},[o],{latencyMs:300}).strategies[0].Up,0);
 assert.equal(replay({start:1200,ev:[[...t.slice(0,4),1,.5,10]]},[o]).strategies[0].Up,0);
});
test("queue, remaining quantity and side budget limit fills",()=>{
 const r=replay({start:1200,ev:[t]},[{...o,qDevant:3}],{budget:2});
 assert.equal(r.strategies[0].Up,4);assert.equal(r.strategies[0].costUp,2);
});
test("independent strategies are separate counterfactuals",()=>{
 const r=replay({start:1200,ev:[t]},[o,{...o,variante:"other"}]);assert.deepEqual(r.strategies.map(s=>s.Up),[10,10]);
 assert.throws(()=>replay({start:1200,coupe:true,ev:[]},[o]));
});
