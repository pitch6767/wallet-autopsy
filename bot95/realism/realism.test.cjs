const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const os = require("node:os");
const path = require("node:path");
const source = fs.readFileSync(path.join(__dirname,"rapide.cjs"),"utf8").split('log("bot95 rapide", VERSION')[0];
function setup() {
  const timers=[];
  const ctx=vm.createContext({require:k=>k==="./measurements.cjs"?()=>({offer(){},fill(){},snapshot(){return {};},ledger:{canQuote:()=>true,budget:()=>50}}):k==="./publish.cjs"?()=>()=>{}:k==="fs"?{mkdirSync(){}}:require(k),
    process:{env:{BOT95_DIR:"/tmp/test"},on(){}}, __dirname:"/tmp", performance:{timeOrigin:1000000,now:()=>0},
    console, setInterval(){},setTimeout(fn){timers.push(fn);},clearInterval(){},Date,fetch(){throw Error("network forbidden");}});
  vm.runInContext(source,ctx);
  vm.runInContext(`
    function order(q=0) {return {start:900,variante:"test",etat:"posee",id:"token",prix:.5,parts:100,
      qp:q,qr:q,qo:q,remplP:0,remplR:0,remplO:0,annulP:0,annulR:0,
      tArrivee:999000,tPose:998900,toxRempl:[],rempl:[],mo:{p:{},r:{},o:{}},moModele:{p:{},r:{},o:{}}};}
  `,ctx);
  return {run:code=>vm.runInContext(code,ctx),timers};
}
test("book delta and matching print consume queue only once",()=>{
  const {run}=setup();
  assert.equal(run(`const o=order(100); OFFRES.push(o); makerNiveau("token",.5,100,90);makerTransaction("token","SELL",.5,10,999900);o.qp`),90);
});
test("trade-through is not an unlimited fill",()=>{
  const {run}=setup();
  assert.equal(run(`const o=order();OFFRES.push(o);makerTransaction("token","SELL",.49,1,999900);o.remplP`),0);
});
test("same-strategy quotes share print; duplicates ignored",()=>{
  const {run}=setup();
  assert.equal(run(`const a=order(),b=order();OFFRES.push(a,b);makerTransaction("token","SELL",.5,10,999900);makerTransaction("token","SELL",.5,10,999900);a.remplP+b.remplP`),10);
});
test("prints before simulated arrival, stale prints and mirrored BUY ignored",()=>{
  const {run}=setup();
  assert.equal(run(`const o=order();o.tArrivee=999950;OFFRES.push(o);
    makerTransaction("token","SELL",.5,10,999900);makerTransaction("token","SELL",.5,10,900000);
    makerTransaction("token","BUY",.5,10,999990);o.remplP`),0);
});
test("independent strategies are separate counterfactuals",()=>{
  const {run}=setup();
  assert.equal(run(`const a=order(),b=order();b.variante="other";OFFRES.push(a,b);makerTransaction("token","SELL",.5,10,999900);a.remplP+b.remplP`),20);
});
test("delayed pre-cancellation print counts; post-cancellation print does not",()=>{
  const {run}=setup();
  assert.equal(run(`const o=order();o.etat="annulee";o.tAnnulee=999950;OFFRES.push(o);
    makerTransaction("token","SELL",.5,10,999900);makerTransaction("token","SELL",.5,10,999980);o.remplP`),10);
});
test("requote waits for cancellation, including late fill in next budget",()=>{
  const {run}=setup();
  assert.equal(run(`
    M[900]={start:900,end:1200,up:"token",down:"down"};
    livres.token={bids:new Map([[.5,0]]),asks:new Map([[.8,1000]]),tRecu:1000000};
    const Q={}; const s=coter(Q,"test",M[900],true,.5,true,{},1000000);
    s.O.etat="posee"; coter(Q,"test",M[900],true,.4,true,{},1000100);
    const count=OFFRES.length; s.O.remplP=s.O.remplR=s.O.remplO=100;s.O.etat="annulee";
    coter(Q,"test",M[900],true,.4,true,{},1000300);
    count===1 && OFFRES.length===1 && s.depense===50;
  `),true);
});
test("global budget reserves all outstanding orders",()=>{
  const {run}=setup();
  assert.equal(run(`
    const mk={start:900,end:1200,up:"token",down:"down"};
    livres.token={bids:new Map(),asks:new Map([[.8,1000]]),tRecu:1000000};
    const a=poser("test",mk,true,.5,50,{}),b=poser("test",mk,true,.5,50,{});
    a.parts*.5+b.parts*.5;
  `),50);
});
test("measurement distinguishes two-sided positions from hedges and persists",()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),"bot95-test-"));
  let t=1000000;const m=require("./measurements.cjs")(dir,()=>t);
  const o={start:900,variante:"test",cote:"Up",prix:.5};m.offer(o);m.fill(o,100);
  t+=1000;m.fill({...o,cote:"Down"},10);t+=1000;
  const row=m.snapshot().rows[0];
  assert.equal(row.unmatched,90);assert.equal(row.singleLeg,false);assert.equal(row.exposedMs,2000);assert.equal(row.shareSeconds,190);
  fs.rmSync(dir,{recursive:true,force:true});
});
