const{test}=require("node:test"),a=require("node:assert/strict"),{ProtectedShadow}=require("./protected-shadow.cjs");
const quote=(price,quantity=100)=>({price,quantity,feePerShare:0});
const book=at=>({type:"book",at,Up:{bid:quote(.4,0),ask:quote(.5)},Down:{bid:quote(.4,0),ask:quote(.5)}});
test("actual strategy loop: fill -> delayed cancellation -> partial hedge -> hedge remainder -> settlement",()=>{
 const s=new ProtectedShadow({makerFeePerShare:0});s.tick(book(0));s.tick({type:"clock",at:100});
 s.tick({type:"trade",at:110,sourceAt:105,token:"Up",side:"SELL",price:.4,quantity:10,id:"t1"});
 a.equal(s.account.snapshot().unmatched,10);
 const b=book(200);b.Down.ask.quantity=4;s.tick(b);
 s.tick({type:"clock",at:210}); // cancellation confirmed, then protective order
 s.tick({type:"clock",at:310}); // only 4 can fill, residual remains
 a.equal(s.account.snapshot().unmatched,6);
 s.tick(book(350));s.tick({type:"clock",at:450});
 a.equal(s.account.snapshot().unmatched,0);
 s.tick({type:"settlement",at:500,winner:"Up",closed:true,resolved:true,evidence:"fixture"});
 a.equal(s.account.snapshot().settlementPnl,1);
});
test("without complete, fresh books no imaginary rescue",()=>{
 const s=new ProtectedShadow({makerFeePerShare:0,maxAgeMs:150});s.tick(book(0));s.tick({type:"clock",at:100});
 s.tick({type:"trade",at:110,sourceAt:105,token:"Up",side:"SELL",price:.4,quantity:10});
 s.tick({type:"clock",at:500});
 a.equal(s.account.snapshot().unmatched,10);a.equal(s.account.snapshot().settlementPnl,null);
 a.throws(()=>new ProtectedShadow(),/assumptions/);
 a.throws(()=>s.tick({type:"book",at:600,Up:{}}),/Incomplete/);
});
test("strategy chooses a sale when covering is more expensive",()=>{
 const s=new ProtectedShadow({makerFeePerShare:0});s.tick(book(0));s.tick({type:"clock",at:100});
 s.tick({type:"trade",at:110,sourceAt:105,token:"Up",side:"SELL",price:.4,quantity:10,id:"t"});
 const b=book(200);b.Up.bid.quantity=20;b.Down.ask.price=.9;s.tick(b);
 s.tick({type:"clock",at:210});
 a.ok([...s.account.orders.values()].some(o=>o.purpose==="exit"));
 s.tick({type:"clock",at:310});a.equal(s.account.snapshot().unmatched,0);
 a.equal(s.account.snapshot().quantities.Down,0);
 s.tick({type:"settlement",at:400,winner:"Down",closed:true,resolved:true,evidence:"fixture"});
 a.equal(s.account.snapshot().settlementPnl,0);
});
