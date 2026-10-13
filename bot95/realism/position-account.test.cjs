const {test}=require("node:test"),a=require("node:assert/strict"),fs=require("node:fs"),os=require("node:os"),path=require("node:path");
const {PositionAccount}=require("./position-account.cjs");
const order=(id,side,action,quantity,limit,at=1)=>({type:"order",id,side,action,quantity,limit,feeReserve:1,at});
const fill=(id,orderId,quantity,price,fee=0,at=2)=>({type:"fill",id,orderId,quantity,price,fee,at,evidence:{kind:"simulation",source:"fixture"}});
test("partial fill -> cancellation race -> hedge -> final net result",()=>{
 const p=new PositionAccount();p.apply(order("u","Up","buy",100,.4));
 p.apply(fill("f1","u",20,.4,.1));p.apply({type:"cancel-request",orderId:"u",at:3});
 a.equal(p.protection({},3).action,"cancel-and-wait");
 p.apply(fill("late","u",10,.4,.1,4));p.apply({type:"cancelled",orderId:"u",at:5});
 a.equal(p.snapshot().unmatched,30);
 const b={at:6,Up:{bid:{price:.35,quantity:100,feePerShare:.01}},Down:{ask:{price:.5,quantity:10,feePerShare:.01}}};
 const h=p.protection(b,6);a.equal(h.action,"hedge");a.equal(h.quantity,10);
 a.equal(p.snapshot().unmatched,30); // Intent is NOT an execution.
 p.apply({...order("h","Down","buy",10,.5,6),purpose:"hedge"});
 a.equal(p.protection(b,6).action,"wait-for-protection");
 p.apply(fill("hf","h",10,.5,.1,7));
 a.equal(p.snapshot().unmatched,20);
 p.apply(order("s","Up","sell",20,.35,8));p.apply(fill("sf","s",20,.35,.2,9));
 a.equal(p.snapshot().unmatched,0);a.equal(p.snapshot().settlementPnl,null);
 p.apply({type:"settlement",winner:"Down",closed:true,resolved:true,evidence:"resolution fixture",at:10});
 a.ok(Math.abs(p.snapshot().settlementPnl+.5)<1e-9); // 10+7-.2 - (12+.2+5+.1)
 a.equal(p.snapshot().fees,.5);
});
test("pending reservations block new spending until cancellation confirmed",()=>{
 const p=new PositionAccount();p.apply(order("a","Up","buy",98,.5));
 p.apply({type:"cancel-request",orderId:"a",at:2});
 a.throws(()=>p.apply(order("b","Up","buy",1,.5,3)),/budget/);
 p.apply({type:"cancelled",orderId:"a",at:4});p.apply(order("b","Up","buy",1,.5,5));
});
test("duplicate receipt is idempotent; conflicting receipt rejected",()=>{
 const p=new PositionAccount();p.apply(order("a","Up","buy",10,.5));const f=fill("f","a",5,.5);
 p.apply(f);p.apply(f);a.equal(p.snapshot().quantities.Up,5);
 p.apply({type:"cancel-request",orderId:"a",at:3});p.apply(f);
 a.throws(()=>p.apply({...f,quantity:6}),/Conflicting/);
 a.throws(()=>p.apply(fill("over","a",6,.5,0,4)),/reservation/);
});
test("stale books, unknown fees, and absent depth do not manufacture a hedge",()=>{
 const p=new PositionAccount();p.apply(order("a","Up","buy",10,.5));p.apply(fill("f","a",10,.5));
 a.equal(p.protection({at:0},1000).action,"uncovered");
 a.equal(p.protection({at:1000,Down:{ask:{price:.4,quantity:10}}},1000).action,"uncovered");
 a.equal(p.snapshot().unmatched,10);
});
test("journal restores exact exposure; unresolved settlements and oversells fail",()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"position-"));
 try{
 const file=path.join(dir,"account.jsonl"),p=new PositionAccount(file);
 p.apply(order("a","Up","buy",10,.5));p.apply(fill("f","a",10,.5,.1));
 const restored=new PositionAccount(file);a.deepEqual(restored.snapshot(),p.snapshot());
 a.throws(()=>restored.apply(order("s","Up","sell",11,.5,3)),/increase exposure/);
 a.throws(()=>restored.apply({type:"settlement",winner:"Up",closed:true,resolved:false,evidence:"pending",at:3}));
 fs.appendFileSync(file,'{"type":');a.throws(()=>new PositionAccount(file),/Incomplete/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
