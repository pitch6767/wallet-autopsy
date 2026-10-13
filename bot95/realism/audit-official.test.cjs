const{test}=require("node:test"),assert=require("node:assert/strict"),{audit}=require("./audit-official.cjs");
const row=(oid,cote,remplR,prix=.5)=>({oid,cote,remplR,prix,start:1200,variante:"M10"});
test("two legs do not imply a hedge",()=>{
 const r=audit({offres:[row("1","Up",100),row("2","Down",10)]}).strategies[0];
 assert.equal(r.singleLegCycles,0);assert.equal(r.imbalancedOverOneShare,1);
 assert.equal(r.unmatchedShareFraction,90/110);
});
test("duplicate publications cannot inflate quantities",()=>{
 const a=row("1","Up",120),r=audit({offres:[a,a]});
 assert.equal(r.duplicatesRemoved,1);assert.equal(r.strategies[0].maximumSideSpend,60);
});
test("zero fill cycle is not a filled success",()=>{
 const r=audit({offres:[row("1","Up",0)]}).strategies[0];
 assert.equal(r.reportedCycles,1);assert.equal(r.filledCycles,0);assert.equal(r.unmatchedShareFraction,null);
});
test("invalid and empty input fail explicitly",()=>{
 assert.throws(()=>audit({offres:[]}));assert.throws(()=>audit({offres:[row("1","Up",NaN)]}));
});
