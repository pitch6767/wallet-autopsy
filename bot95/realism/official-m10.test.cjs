const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {create,extract}=require('./official-m10.cjs');
const {assess}=require('./readiness.cjs');
test('unknown source fails closed',()=>{
  assert.throws(()=>extract(''),/contract changed/);
  assert.equal(assess('').verdict,'PREUVES_INSUFFISANTES');
  assert.equal(assess('').official,null);
});
// Opt-in source snapshot is read-only and never executed as a program.
const file=process.env.OFFICIAL_SOURCE;
test('official M10 decisions: budget, recotations, toxic withdrawal, time window', {skip:!file},()=>{
  const orders=[],cancels=[];
  const strategy=create(fs.readFileSync(file,'utf8'),{
    poser:(v,mk,up,prix,budget)=>{const o={etat:'posee',prix,remplR:0,up,budget};orders.push(o);return o;},
    annuler:(o,reason)=>{o.tAnnulDemande=1;cancels.push(reason);}
  });
  const input={mk:{up:'u',down:'d'},t:10000,tleft:200,ua:[.55],da:[.5],P:{pu:.52},TOX:{},bids:{u:.5,d:.45}};
  strategy.step(input);
  assert.equal(orders.length,2);
  assert.deepEqual(orders.map(x=>x.budget),[50,50]);
  orders[0].remplR=10;
  strategy.step({...input,t:10100,bids:{u:.51,d:.45}});
  assert.equal(orders[2].budget,45);
  assert.equal(cancels[0],'re-cotation');
  strategy.step({...input,t:10200,TOX:{u:{a:10200,b:0,c:0}}});
  assert.ok(cancels.includes('toxique'));
  const before=orders.length;
  strategy.step({...input,t:10300,tleft:5});
  assert.equal(orders.length,before);
  assert.equal(strategy.identity.sha256.length,64);
  assert.throws(()=>strategy.step({...input,TOX:null}),/Complete official/);
});
