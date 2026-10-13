// One input file = one market cycle + one independent strategy.
// Read explicit events; never infer executions from decisions.
const fs=require("node:fs"),{PositionAccount}=require("./position-account.cjs");
function run(events){
  const account=new PositionAccount(),trace=[];
  let book=null,last=-Infinity;
  for(const event of events){
    if(!Number.isFinite(event.at)||event.at<last)throw Error("Replay chronology invalid");
    last=event.at;
    if(event.type==="book")book=event;
    else account.apply(event);
    trace.push({at:event.at,event:event.type,position:account.snapshot(),protection:account.protection(book,event.at)});
  }
  return {verdict:"OFFLINE_ACCOUNTING_NOT_LIVE_VALIDATED",position:account.snapshot(),trace};
}
module.exports={run};
if(require.main===module){
  if(!process.argv[2])throw Error("Usage: node position-replay.cjs events.jsonl");
  const events=fs.readFileSync(process.argv[2],"utf8").split("\n").filter(x=>x.trim()).map(x=>JSON.parse(x));
  console.log(JSON.stringify(run(events),null,2));
}
