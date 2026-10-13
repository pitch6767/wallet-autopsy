// Public-data-only collector. Never loads credentials and never sends exchange orders.
const fs=require("node:fs"),path=require("node:path"),zlib=require("node:zlib");
const {ProtectedShadow}=require("./protected-shadow.cjs");
const {PositionAccount}=require("./position-account.cjs");
const publicBooks=require("./public-books.cjs");
const DIR=process.env.BOT95_PROTECTED_DIR||path.join(__dirname,"data");
fs.mkdirSync(DIR,{recursive:true});
const log=(type,fields={})=>console.log(JSON.stringify({at:new Date().toISOString(),type,...fields}));
const atomic=(file,obj)=>{fs.writeFileSync(file+".tmp",JSON.stringify(obj));fs.renameSync(file+".tmp",file);};
let current=null,starting=false,lastStart=null,shutting=false;
const bootCycle=Math.floor(Date.now()/300000)*300;
const VERSION="protected-shadow-1";
async function get(url){
 const r=await fetch(url,{signal:AbortSignal.timeout(12000)});
 if(!r.ok)throw Error(`Public GET HTTP ${r.status}: ${new URL(url).pathname}`);
 return r.json();
}
async function market(start){
 const d=await get(`https://gamma-api.polymarket.com/events?slug=btc-updown-5m-${start}`);
 const m=d[0]?.markets?.[0];if(!m)throw Error("Market metadata absent");return m;
}
function status(c){
 return {version:VERSION,start:c.start,slug:c.slug,at:Date.now(),complete:c.complete,
   reasons:[...c.reasons],messages:c.messages,books:c.books,prints:c.prints,
   connected:c.ws?.readyState===1,position:c.sim.account.snapshot(Date.now()),
   assumptions:{makerFee:0,takerRate:.07,feeType:"crypto_fees_v2",latencyMs:100,
     liveOrders:false,executionCalibrated:false,exactPriceSellOnly:true},
   verdict:"SIMULATION_NOT_LIVE_VALIDATED"};
}
function save(c){atomic(path.join(c.dir,"status.json"),status(c));atomic(path.join(DIR,"latest.json"),status(c));}
function incomplete(c,reason){if(!c.reasons.has(reason)){c.reasons.add(reason);c.complete=false;log("incomplete",{start:c.start,reason});}}
function emit(c,e){
 if(c.finished)return;
 fs.writeSync(c.events,JSON.stringify(e)+"\n");
 c.sim.tick(e);c.sim.trace.length=0; // durable events/account remain; don't retain duplicate trace in RAM
 if(c.sim.latePrints)incomplete(c,"late print after cancellation: execution ambiguous");
}
function top(c,at){
 if(c.tokens.some(id=>!c.maps[id]||at-c.maps[id].received>500||at-c.maps[id].source>1000))return null;
 const out={type:"book",at,sourceAt:{}};
 for(let i=0;i<2;i++){
   const b=c.maps[c.tokens[i]],bid=[...b.bids].sort((a,b)=>b[0]-a[0])[0],ask=[...b.asks].sort((a,b)=>a[0]-b[0])[0];
   if(!bid||!ask||bid[0]<=0||ask[0]>=1||bid[0]>=ask[0])return null;
   const q=x=>({price:x[0],quantity:x[1],feePerShare:.07*x[0]*(1-x[0])});
   out[i===0?"Up":"Down"]={bid:q(bid),ask:q(ask)};
   out.sourceAt[i===0?"Up":"Down"]=b.source;
 }
 return out;
}
function message(c,m){
 if(c.finished||Date.now()>=(c.start+300)*1000)return;
 const at=Date.now(),ts=Number(m.timestamp);
 c.messages++;c.lastMessage=at;
 if(!["book","price_change","last_trade_price"].includes(m.event_type))return;
 if(!Number.isFinite(ts)||ts>at+50){incomplete(c,"invalid source timestamp");return;}
 if(m.event_type==="book" && c.tokens.includes(m.asset_id)){
   c.maps[m.asset_id]=publicBooks.snapshot(c.maps[m.asset_id],m,at);
 }else if(m.event_type==="price_change"){
   for(const x of m.price_changes||[]){
     const b=c.maps[x.asset_id];if(!b)continue;
     publicBooks.delta(b,x,ts,at);
   }
 }else if(m.event_type==="last_trade_price" && c.tokens.includes(m.asset_id)){
   c.prints++;emit(c,{type:"trade",at,sourceAt:ts,token:c.tokens.indexOf(m.asset_id)===0?"Up":"Down",
     side:m.side,price:+m.price,quantity:+m.size});
 }
 // Coalesce top snapshots to 50 ms. Trades always processed, independently.
 if(at-c.lastBook>=50){const b=top(c,at);if(b){emit(c,b);c.lastBook=at;c.books++;}}
}
function connect(c){
 c.maps={};c.lastConnect=Date.now();c.lastMessage=Date.now();
 const ws=c.ws=new WebSocket("wss://ws-subscriptions-clob.polymarket.com/ws/market");
 ws.addEventListener("open",()=>{log("connected",{start:c.start});ws.send(JSON.stringify({assets_ids:c.tokens,type:"market"}));});
 ws.addEventListener("message",e=>{
   if(e.data==="PONG")return;
   try{const parsed=JSON.parse(e.data);for(const m of Array.isArray(parsed)?parsed:[parsed])message(c,m);}
   catch(error){fatal(error);}
 });
 ws.addEventListener("error",()=>incomplete(c,"websocket error"));
 ws.addEventListener("close",()=>{if(!c.finished){incomplete(c,"websocket disconnected");}});
}
async function start(start){
 const m=await market(start);
 if(m.feeType!=="crypto_fees_v2"||m.feesEnabled!==true)throw Error("Unrecognized fee schedule: no simulation started");
 const tokens=JSON.parse(m.clobTokenIds),outcomes=JSON.parse(m.outcomes);
 if(tokens.length!==2||outcomes.join(",")!=="Up,Down")throw Error("Unexpected token mapping");
 const dir=path.join(DIR,String(start));
 if(fs.existsSync(dir)){lastStart=start;log("skip-existing-cycle",{start});return;}
 fs.mkdirSync(dir);
 const c={start,dir,slug:m.slug,tokens,maps:{},events:fs.openSync(path.join(dir,"events.jsonl"),"a",0o600),
   sim:new ProtectedShadow({makerFeePerShare:0,accountFile:path.join(dir,"account.jsonl"),endAt:(start+300)*1000}),
   complete:true,reasons:new Set(),messages:0,books:0,prints:0,lastBook:0,lastMessage:Date.now(),finished:false};
 // Startup during a cycle is retained for diagnostics but never counted as a full observation.
 if(start===bootCycle||Date.now()-start*1000>5000)incomplete(c,"partial startup cycle");
 current=c;lastStart=start;connect(c);save(c);log("cycle-start",{start,slug:m.slug});
}
function finish(c){
 if(c.finished)return;
 const at=Date.now();
 emit(c,{type:"clock",at});
 for(const o of c.sim.account.orders.values())if(!o.closed)
   c.sim.account.apply({type:"cancelled",orderId:o.id,at}); // market expiry in this simulation
 c.finished=true;c.ws?.close();fs.fsyncSync(c.events);fs.closeSync(c.events);save(c);
 const input=fs.createReadStream(path.join(c.dir,"events.jsonl"));
 const output=fs.createWriteStream(path.join(c.dir,"events.jsonl.gz"));
 input.on("error",fatal);output.on("error",fatal);
 input.pipe(zlib.createGzip()).pipe(output).on("finish",()=>fs.unlinkSync(path.join(c.dir,"events.jsonl")));
 log("cycle-end",status(c));
}
async function settlements(){
 for(const name of fs.readdirSync(DIR).filter(x=>/^\d+$/.test(x))){
   const dir=path.join(DIR,name),file=path.join(dir,"status.json");
   if(!fs.existsSync(file)||Date.now()<(Number(name)+360)*1000)continue;
   const s=JSON.parse(fs.readFileSync(file));if(s.position.winner)continue;
   const m=await market(Number(name));
   if(m.closed!==true||m.umaResolutionStatus!=="resolved")continue;
   const prices=JSON.parse(m.outcomePrices).map(Number),outcomes=JSON.parse(m.outcomes);
   if(!prices.includes(1))continue;
   const account=new PositionAccount(path.join(dir,"account.jsonl"));
   const at=Date.now();
   if(account.snapshot().openOrders){
     s.complete=false;s.reasons=[...new Set([...s.reasons,"interruption before cycle expiry"])];
     for(const o of account.orders.values())if(!o.closed)account.apply({type:"cancelled",orderId:o.id,at});
   }
   account.apply({type:"settlement",at,winner:outcomes[prices.indexOf(1)],closed:true,resolved:true,evidence:{slug:m.slug,source:"Gamma"}});
   s.beforeSettlement=s.position;s.position=account.snapshot();s.at=at;atomic(file,s);log("settled",{start:s.start,complete:s.complete,pnl:s.position.settlementPnl});
 }
 // Keep compact accounting indefinitely, bounded raw feed retention (48 h).
 for(const name of fs.readdirSync(DIR).filter(x=>/^\d+$/.test(x)))
   if(Number(name)<Date.now()/1000-172800){
     const file=path.join(DIR,name,"events.jsonl.gz");if(fs.existsSync(file))fs.unlinkSync(file);
   }
 const cycles=fs.readdirSync(DIR).filter(x=>/^\d+$/.test(x)).map(name=>{
   const file=path.join(DIR,name,"status.json");return fs.existsSync(file)?JSON.parse(fs.readFileSync(file)):null;
 }).filter(Boolean);
 const eligible=cycles.filter(s=>s.complete&&s.position.winner);
 atomic(path.join(DIR,"report.json"),{at:Date.now(),version:VERSION,
   verdict:"SIMULATION_NOT_LIVE_VALIDATED",cycles:cycles.length,eligibleSettledCycles:eligible.length,
   excludedIncomplete:cycles.filter(s=>!s.complete).length,pending:cycles.filter(s=>!s.position.winner).length,
   simulatedNetPnl:eligible.length?eligible.reduce((n,s)=>n+s.position.settlementPnl,0):null,
   filledCycles:eligible.filter(s=>s.position.simulatedFills>0).length,
   fees:eligible.reduce((n,s)=>n+s.position.fees,0),recent:cycles.slice(-12)});
}
function fatal(e){log("fatal",{error:e.message});process.exit(1);}
setInterval(async()=>{
 if(shutting||starting)return;
 const t=Date.now(),s=Math.floor(t/300000)*300;
 try{
   if(current&&current.start!==s){finish(current);current=null;}
   if(!current&&lastStart!==s){starting=true;try{await start(s);}finally{starting=false;}return;}
   if(current){
     emit(current,{type:"clock",at:t});
     if(t-current.lastMessage>10000){incomplete(current,"market feed silent over 10s");current.ws?.close();}
     if(current.ws?.readyState===3&&t-current.lastConnect>10000)connect(current);
   }
 }catch(e){fatal(e);}
},100);
setInterval(()=>{if(current){save(current);log("heartbeat",status(current));}},30000);
setInterval(()=>{if(current?.ws?.readyState===1)current.ws.send("PING");},10000);
let settling=false;
setInterval(async()=>{if(settling)return;settling=true;try{await settlements();}catch(e){log("settlement-error",{error:e.message});}finally{settling=false;}},60000);
process.on("SIGTERM",()=>{shutting=true;if(current){incomplete(current,"service interrupted");save(current);fs.fsyncSync(current.events);}process.exit(0);});
log("boot",{version:VERSION,liveOrders:false,dir:DIR,feeSource:"https://docs.polymarket.com/trading/fees"});
