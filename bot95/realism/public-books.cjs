// CLOB deltas can arrive out of source-time order across DIFFERENT price levels.
// Keep per-level versions; a snapshot supersedes only updates at/before its time.
function snapshot(previous,message,received){
 const ts=Number(message.timestamp);
 if(previous&&ts<previous.snapshotTs)return previous;
 const b={bids:new Map(message.bids.map(x=>[+x.price,+x.size]).filter(x=>x[1]>0)),
   asks:new Map(message.asks.map(x=>[+x.price,+x.size]).filter(x=>x[1]>0)),
   updates:new Map(),snapshotTs:ts,source:ts,received};
 if(previous)for(const[key,u]of previous.updates)if(u.ts>ts){
   b.updates.set(key,u);const levels=u.side==="BUY"?b.bids:b.asks;
   if(u.size>0)levels.set(u.price,u.size);else levels.delete(u.price);
   b.source=Math.max(b.source,u.ts);
 }
 return b;
}
function delta(b,x,ts,received){
 if(!b||ts<b.snapshotTs)return;
 const key=x.side+":"+x.price,old=b.updates.get(key);
 if(old&&old.ts>ts)return;
 const u={side:x.side,price:+x.price,size:+x.size,ts};
 b.updates.set(key,u);const levels=x.side==="BUY"?b.bids:b.asks;
 if(u.size>0)levels.set(u.price,u.size);else levels.delete(u.price);
 b.source=Math.max(b.source,ts);b.received=received;
}
module.exports={snapshot,delta};
