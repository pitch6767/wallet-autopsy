// Separate, offline execution account. No network, wallet, or order-sending code.
const fs = require("node:fs");
class PositionAccount {
  constructor(file) {
    this.file=file; this.orders=new Map(); this.receipts=new Map(); this.events=[];
    this.qty={Up:0,Down:0}; this.spent={Up:0,Down:0}; this.proceeds=0; this.fees=0;
    this.winner=null; this.lastAt=-Infinity;
    if(file && fs.existsSync(file)){
      const text=fs.readFileSync(file,"utf8");
      if(text && !text.endsWith("\n"))throw Error("Incomplete journal: reconciliation required");
      for(const line of text.trim().split("\n").filter(Boolean))this.apply(JSON.parse(line),true);
    }
  }
  apply(e,restoring=false) {
    if(!e)throw Error("Missing event");
    if(e.type==="fill" && this.receipts.has(e.id)){
      if(JSON.stringify(this.receipts.get(e.id))!==JSON.stringify(e))throw Error("Conflicting execution ID");
      return;
    }
    if(!Number.isFinite(e.at) || e.at<this.lastAt)throw Error("Invalid event chronology");
    if(this.winner)throw Error("Account settled");
    const positive=x=>Number.isFinite(x)&&x>0;
    const price=x=>positive(x)&&x<=1;
    let mutate;
    if(e.type==="order"){
      const purpose=e.purpose||(e.action==="sell"?"exit":"entry");
      if(!e.id || this.orders.has(e.id)||!["Up","Down"].includes(e.side)||
        !["buy","sell"].includes(e.action)||!positive(e.quantity)||!price(e.limit)||
        !Number.isFinite(e.feeReserve)||e.feeReserve<0||
        !["entry","hedge","exit"].includes(purpose))throw Error("Invalid order");
      const gap=this.qty.Up-this.qty.Down;
      if(purpose==="entry"&&Math.abs(gap)>1e-8)throw Error("Uncovered position: new entries blocked");
      if(purpose==="hedge" && (e.action!=="buy" || e.side!==(gap>0?"Down":"Up") || e.quantity>Math.abs(gap)+1e-8))
        throw Error("Hedge would increase exposure");
      if(purpose==="exit" && (e.action!=="sell" || e.side!==(gap>0?"Up":"Down") || e.quantity>Math.abs(gap)+1e-8))
        throw Error("Exit would increase exposure");
      const pending=[...this.orders.values()].filter(o=>!o.closed&&o.side===e.side&&o.action===e.action);
      const reserved=pending.reduce((s,o)=>s+(o.quantity-o.filled)*(o.action==="buy"?o.limit:1)+(o.action==="buy"?o.feeLeft:0),0);
      if(e.action==="buy"&&this.spent[e.side]+reserved+e.quantity*e.limit+e.feeReserve>50+1e-8)throw Error("Side budget exceeded");
      if(e.action==="sell"&&reserved+e.quantity>this.qty[e.side]+1e-8)throw Error("Unowned shares");
      if(purpose!=="entry" && [...this.orders.values()].some(o=>!o.closed))
        throw Error("Wait for outstanding orders before protection");
      mutate=()=>this.orders.set(e.id,{...e,purpose,filled:0,feeLeft:e.feeReserve,closed:false,cancelRequested:false});
    }else if(e.type==="cancel-request"||e.type==="cancelled"){
      const o=this.orders.get(e.orderId);if(!o||o.closed)throw Error("Unknown or closed order");
      mutate=()=>{if(e.type==="cancel-request")o.cancelRequested=true;else o.closed=true;};
    }else if(e.type==="fill"){
      const o=this.orders.get(e.orderId);
      if(!e.id||!o||o.closed||!positive(e.quantity)||!price(e.price)||!Number.isFinite(e.fee)||e.fee<0||
         !e.evidence||!["simulation","execution-confirmed"].includes(e.evidence.kind))throw Error("Invalid fill/evidence");
      if(e.quantity>o.quantity-o.filled+1e-8 || e.fee>o.feeLeft+1e-8)throw Error("Execution exceeds reservation");
      if(o.action==="buy"?e.price>o.limit+1e-8:e.price<o.limit-1e-8)throw Error("Execution outside limit");
      if(o.action==="sell"&&e.quantity>this.qty[o.side]+1e-8)throw Error("Oversell");
      mutate=()=>{
        o.filled+=e.quantity;o.feeLeft-=e.fee;
        if(o.quantity-o.filled<1e-8)o.closed=true;
        this.qty[o.side]+=o.action==="buy"?e.quantity:-e.quantity;
        if(o.action==="buy")this.spent[o.side]+=e.quantity*e.price+e.fee;
        else this.proceeds+=e.quantity*e.price-e.fee;
        this.fees+=e.fee;this.receipts.set(e.id,e);
      };
    }else if(e.type==="settlement"){
      if(!["Up","Down"].includes(e.winner)||e.closed!==true||e.resolved!==true||
         !e.evidence || [...this.orders.values()].some(o=>!o.closed))throw Error("Unconfirmed settlement or orders still open");
      mutate=()=>{this.winner=e.winner;this.proceeds+=this.qty[e.winner];this.qty={Up:0,Down:0};};
    }else throw Error("Unknown event");
    // Commit before mutation. A write failure aborts the caller, never hides lost accounting.
    if(this.file&&!restoring){
      const fd=fs.openSync(this.file,"a",0o600);
      try{fs.writeSync(fd,JSON.stringify(e)+"\n");fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
    }
    mutate();this.lastAt=e.at;this.events.push(e);
  }
  snapshot(){
    return {quantities:{...this.qty},paired:Math.min(this.qty.Up,this.qty.Down),
      unmatched:Math.abs(this.qty.Up-this.qty.Down),spent:{...this.spent},fees:this.fees,
      netCash:this.proceeds-this.spent.Up-this.spent.Down,
      settlementPnl:this.winner?this.proceeds-this.spent.Up-this.spent.Down:null,
      winner:this.winner,openOrders:[...this.orders.values()].filter(o=>!o.closed).length,
      simulatedFills:[...this.receipts.values()].filter(e=>e.evidence.kind==="simulation").length};
  }
  protection(book,now,{maxAgeMs=500}={}){
    if(this.winner)return {action:"settled"};
    const open=[...this.orders.values()].filter(o=>!o.closed);
    const gap=this.qty.Up-this.qty.Down;
    if(Math.abs(gap)<1e-8)return {action:"balanced"};
    // Cancellation requests do not release quantities or cash.
    if(open.some(o=>o.purpose!=="entry"))return {action:"wait-for-protection",orderIds:open.map(o=>o.id)};
    if(open.length)return {action:"cancel-and-wait",orderIds:open.map(o=>o.id)};
    if(!book||!Number.isFinite(book.at)||book.at>now||now-book.at>maxAgeMs)
      return {action:"uncovered",reason:"No fresh book",quantity:Math.abs(gap)};
    const side=gap>0?"Up":"Down",opposite=side==="Up"?"Down":"Up",quantity=Math.abs(gap);
    const candidates=[];
    for(const [kind,s,quote] of [["sell",side,book[side]?.bid],["hedge",opposite,book[opposite]?.ask]]){
      if(!quote||![quote.price,quote.quantity,quote.feePerShare].every(Number.isFinite)||
         quote.price<=0||quote.price>1||quote.quantity<=0||quote.feePerShare<0)continue;
      let n=Math.min(quantity,quote.quantity);
      if(kind==="hedge")n=Math.min(n,Math.max(0,50-this.spent[s])/(quote.price+quote.feePerShare));
      if(n>1e-8)candidates.push({action:kind,side:s,quantity:n,limit:quote.price,
        feeReserve:n*quote.feePerShare,valuePerShare:(kind==="sell"?quote.price:1-quote.price)-quote.feePerShare});
    }
    candidates.sort((a,b)=>b.valuePerShare-a.valuePerShare);
    return candidates[0]?{...candidates[0],status:"intent-only",residualIfFullyFilled:quantity-candidates[0].quantity}:
      {action:"uncovered",quantity,reason:"No executable depth, fee estimate or budget"};
  }
}
module.exports={PositionAccount};
