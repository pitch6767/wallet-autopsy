'use strict';
// Explicit, single-market-cycle replay. Never converts incomplete public
// snapshots into invented official probability/toxicity inputs.
const fs=require('node:fs'),readline=require('node:readline');
const {OfficialExecution}=require('./official-execution.cjs');
async function replay(source,input,options){
  const sim=new OfficialExecution(source,options);
  let decisions=0,market=null;
  for await(const line of readline.createInterface({input,crlfDelay:Infinity})){
    if(!line.trim())continue;
    const e=JSON.parse(line);
    switch(e.type){
      case 'decision':
        if(!Number.isFinite(e.input?.mk?.start))throw Error('Market cycle identity required');
        if(market!==null&&market!==e.input.mk.start)throw Error('Separate account required for every market cycle');
        market=e.input.mk.start;sim.decision(e.input);decisions++;break;
      case 'book':sim.book(e.token,e.at,e.book);break;
      case 'trade':sim.trade(e);break;
      case 'clock':sim.advance(e.at);break;
      case 'expiry':sim.expire(e.at);break;
      case 'settlement':sim.settle(e);break;
      default:throw Error('Unknown canonical event: '+e.type);
    }
  }
  if(!decisions)throw Error('No official decision inputs: replay cannot validate strategy');
  return {market,decisions,assumptions:options,...sim.snapshot(),journal:sim.events};
}
module.exports={replay};
if(require.main===module){
  const [source,file,latency,fee]=process.argv.slice(2);
  if(!source||!file||latency===undefined||fee===undefined)
    throw Error('Usage: node replay-official.cjs official-source.js events.jsonl latency-ms maker-fee-per-share');
  replay(fs.readFileSync(source,'utf8'),fs.createReadStream(file),
    {latencyMs:Number(latency),makerFeePerShare:Number(fee)})
    .then(result=>process.stdout.write(JSON.stringify(result)+'\n'))
    .catch(error=>{console.error(error.message);process.exitCode=1;});
}
