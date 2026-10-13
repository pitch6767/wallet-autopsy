const{test}=require("node:test"),a=require("node:assert/strict"),{snapshot,delta}=require("./public-books.cjs");
const snap=timestamp=>({timestamp,bids:[{price:".4",size:"10"}],asks:[{price:".6",size:"20"}]});
test("out-of-order updates at different levels must both apply",()=>{
 const b=snapshot(null,snap(100),101);
 delta(b,{side:"BUY",price:".4",size:"15"},120,121);
 delta(b,{side:"BUY",price:".3",size:"7"},110,122);
 a.equal(b.bids.get(.4),15);a.equal(b.bids.get(.3),7);
 delta(b,{side:"BUY",price:".4",size:"2"},115,123);
 a.equal(b.bids.get(.4),15);
});
test("older snapshot preserves newer deltas including deleted levels",()=>{
 let b=snapshot(null,snap(100),101);
 delta(b,{side:"BUY",price:".4",size:"0"},120,121);
 b=snapshot(b,snap(110),130);a.equal(b.bids.has(.4),false);
 b=snapshot(b,snap(125),131);a.equal(b.bids.get(.4),10);
});
test("a snapshot already includes earlier deltas",()=>{
 const b=snapshot(null,snap(100),101);
 delta(b,{side:"BUY",price:".4",size:"1"},99,102);
 a.equal(b.bids.get(.4),10);
});
