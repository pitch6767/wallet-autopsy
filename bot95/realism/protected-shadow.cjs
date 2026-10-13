// Runnable, isolated paper strategy driven by timestamped books and prints.
// No exchange client. All generated receipts explicitly say "simulation".
const {PositionAccount}=require("./position-account.cjs");
class ProtectedShadow {
  constructor({latencyMs=100,maxAgeMs=500,entryBudget=10,makerFeePerShare,accountFile,endAt=Infinity}={}){
    if(![latencyMs,maxAgeMs,entryBudget,makerFeePerShare].every(Number.isFinite)||
       latencyMs<0||maxAgeMs<=0||entryBudget<=0||entryBudget>50||makerFeePerShare<0)
      throw Error("Explicit valid simulation assumptions required");
    Object.assign(this,{latencyMs,maxAgeMs,entryBudget,makerFeePerShare});
    this.endAt=endAt;
    this.account=new PositionAccount(accountFile);this.jobs=[];this.book=null;this.t=-Infinity;
    this.seq=0;this.prints=new Set();this.entered=false;this.trace=[];this.latePrints=0;
  }
  id(){return String(++this.seq);}
  emit(e){this.account.apply(e);}
  cancel(o,at){
    if(o.cancelRequested||o.closed)return;
    this.emit({type:"cancel-request",orderId:o.id,at});
    this.jobs.push({type:"cancelled",orderId:o.id,at:at+this.latencyMs});
  }
  order(side,action,quantity,limit,feePerShare,purpose,at){
    const id=this.id();
    this.emit({type:"order",id,side,action,quantity,limit,feeReserve:quantity*feePerShare,purpose,at});
    this.jobs.push({type:"arrive",orderId:id,at:at+this.latencyMs});
  }
  fresh(at){return this.book&&this.book.at<=at&&at-this.book.at<=this.maxAgeMs;}
  receipt(o,n,p,fee,at,source){
    if(n>1e-8)this.emit({type:"fill",id:this.id(),orderId:o.id,quantity:n,price:p,fee:n*fee,at,
      evidence:{kind:"simulation",source}});
  }
  due(at){
    this.jobs.sort((a,b)=>a.at-b.at);
    while(this.jobs.length&&this.jobs[0].at<=at){
      const job=this.jobs.shift(),o=this.account.orders.get(job.orderId);
      if(!o||o.closed)continue;
      if(job.at>=this.endAt){this.emit({type:"cancelled",orderId:o.id,at:job.at});continue;}
      if(job.type==="cancelled"){this.emit(job);continue;}
      if(!this.fresh(job.at)){this.emit({type:"cancelled",orderId:o.id,at:job.at});continue;}
      if(o.purpose==="entry"){
        const b=this.book[o.side];
        // Post-only rejection is not a fill.
        if(!b?.bid||!b?.ask||b.ask.price<=o.limit||b.bid.price!==o.limit){
          this.emit({type:"cancelled",orderId:o.id,at:job.at});continue;
        }
        o.arrival=job.at;o.queue=b.bid.quantity;continue;
      }
      const q=this.book[o.side]?.[o.action==="buy"?"ask":"bid"];
      if(q&&Number.isFinite(q.feePerShare)&&q.feePerShare>=0&&
         (o.action==="buy"?q.price<=o.limit:q.price>=o.limit)){
        const n=Math.min(o.quantity-o.filled,q.quantity,q.feePerShare?o.feeLeft/q.feePerShare:Infinity);
        this.receipt(o,n,q.price,q.feePerShare,job.at,"fresh book at simulated arrival");
        q.quantity-=n; // Do not reuse the same displayed quantity.
      }
      if(!o.closed)this.emit({type:"cancelled",orderId:o.id,at:job.at}); // simulated IOC remainder
    }
  }
  tick(e){
    if(!Number.isFinite(e.at)||e.at<this.t)throw Error("Out-of-order market event");
    this.due(e.at);this.t=e.at;
    if(e.type==="book"){
      for(const side of ["Up","Down"])for(const type of ["bid","ask"]){
        const q=e[side]?.[type];
        if(!q||![q.price,q.quantity,q.feePerShare].every(Number.isFinite)||
           q.price<=0||q.price>1||q.quantity<0||q.feePerShare<0)throw Error("Incomplete two-sided book or fees");
      }
      this.book=structuredClone(e);
    }else if(e.type==="trade"){
      if(e.side==="SELL" && ["Up","Down"].includes(e.token)&&
         [e.sourceAt,e.price,e.quantity].every(Number.isFinite)&&e.quantity>0&&
         e.sourceAt<=e.at&&e.at-e.sourceAt<=this.maxAgeMs){
        const key=e.id||JSON.stringify([e.sourceAt,e.token,e.side,e.price,e.quantity]);
        if(!this.prints.has(key)){
          this.prints.add(key);let remaining=e.quantity;
          for(const o of this.account.orders.values()){
            if(o.closedAt && e.sourceAt<o.closedAt && e.sourceAt>=o.arrival &&
               o.side===e.token && o.limit===e.price)this.latePrints++;
            if(o.closed||o.purpose!=="entry"||o.side!==e.token||o.limit!==e.price||
               o.arrival===undefined||o.arrival>e.sourceAt)continue;
            const ahead=Math.min(o.queue,remaining);o.queue-=ahead;remaining-=ahead;
            const n=Math.min(remaining,o.quantity-o.filled);
            this.receipt(o,n,o.limit,this.makerFeePerShare,e.at,key);remaining-=n;
          }
        }
      }
    }else if(e.type==="settlement"){
      this.emit(e);
    }else if(e.type!=="clock")throw Error("Unknown market event");
    if(!this.account.winner&&e.at<this.endAt){
      const plan=this.account.protection(this.book,e.at,{maxAgeMs:this.maxAgeMs});
      if(plan.action==="cancel-and-wait")for(const id of plan.orderIds)this.cancel(this.account.orders.get(id),e.at);
      if(plan.action==="hedge"||plan.action==="sell")
        this.order(plan.side,plan.action==="hedge"?"buy":"sell",plan.quantity,plan.limit,
          plan.feeReserve/plan.quantity,plan.action==="hedge"?"hedge":"exit",e.at);
      // One initial paired entry per cycle. No martingale or re-entry after rescue.
      if(!this.entered&&this.fresh(e.at)){
        this.entered=true;
        const up=this.book.Up.bid.price,down=this.book.Down.bid.price;
        if(up+down+2*this.makerFeePerShare<1){
          const n=Math.min(this.entryBudget/(up+this.makerFeePerShare),this.entryBudget/(down+this.makerFeePerShare));
          for(const side of ["Up","Down"])this.order(side,"buy",n,this.book[side].bid.price,this.makerFeePerShare,"entry",e.at);
        }
      }
      this.trace.push({at:e.at,position:this.account.snapshot(),decision:plan});
    }
    return this.account.snapshot();
  }
}
module.exports={ProtectedShadow};
if(require.main===module){
  const fs=require("node:fs");
  const [file,fee]=process.argv.slice(2);
  if(!file||fee===undefined)throw Error("Usage: node protected-shadow.cjs market-events.jsonl maker-fee-per-share");
  const s=new ProtectedShadow({makerFeePerShare:Number(fee)});
  for(const line of fs.readFileSync(file,"utf8").split("\n").filter(x=>x.trim()))s.tick(JSON.parse(line));
  console.log(JSON.stringify({status:"SIMULATION_NOT_CALIBRATED",position:s.account.snapshot(),trace:s.trace,events:s.account.events},null,2));
}
