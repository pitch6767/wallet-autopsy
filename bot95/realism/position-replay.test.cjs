const{test}=require("node:test"),a=require("node:assert/strict"),{run}=require("./position-replay.cjs");
test("entire replay distinguishes hedge intent, partial fill, sale, and settlement",()=>{
 const order=(id,side,action,quantity,limit,purpose,at)=>({type:"order",id,side,action,quantity,limit,purpose,feeReserve:1,at});
 const fill=(id,orderId,quantity,price,at)=>({type:"fill",id,orderId,quantity,price,fee:0,at,evidence:{kind:"simulation"}});
 const r=run([
 order("a","Up","buy",10,.4,"entry",1),fill("a1","a",10,.4,2),
 {type:"book",at:3,Up:{bid:{price:.3,quantity:10,feePerShare:0}},Down:{ask:{price:.5,quantity:5,feePerShare:0}}},
 order("h","Down","buy",5,.5,"hedge",4),fill("h1","h",5,.5,5),
 order("s","Up","sell",5,.3,"exit",6),fill("s1","s",5,.3,7),
 {type:"settlement",at:8,winner:"Down",closed:true,resolved:true,evidence:"fixture"}
 ]);
 a.equal(r.trace[2].protection.action,"hedge");a.equal(r.trace[2].position.unmatched,10);
 a.equal(r.trace[4].position.unmatched,5);a.equal(r.trace[6].position.unmatched,0);
 a.equal(r.position.settlementPnl,0);
});
