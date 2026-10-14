'use strict';
const {OfficialExecution}=require('./official-execution.cjs');
const zlib=require('node:zlib');
function compare(record,source,latencyMs){
  const v=record.validation;
  if(!v||!v.complete||v.partialStartup)throw Error(v?.reason||'Incomplete or startup recording');
  if(v.pending)throw Error('Recording compression unfinished');
  if(![1,2].includes(v.schema))throw Error('Unsupported recording schema');
  const events=[];
  for(const chunk of v.chunks||[]){
    if(typeof chunk!=='string')throw Error('Missing compressed recording block');
    events.push(...JSON.parse(zlib.gunzipSync(Buffer.from(chunk,'base64'),{maxOutputLength:2*1024*1024})));
  }
  events.push(...v.events);
  const first=events[0];
  const firstAt=first?.type==='raw'?first.row?.[1]:first?.input?.t;
  if(!Number.isFinite(firstAt)||firstAt>record.start*1000+5000)
    throw Error('Recording begins after cycle start (including startup warm-up)');
  if(!source.includes(`const VERSION = "${record.version}"`))throw Error('Matching source version unavailable');
  const sim=new OfficialExecution(source,{latencyMs,makerFeePerShare:0});
  const books=new Map(),seen=new Set();let decisions=0,rounding=0;
  function clock(t){
    if(!Number.isFinite(t))throw Error('Invalid timestamp');
    if(t<sim.at){if(sim.at-t>.111)throw Error('Non-monotonic recording');rounding++;return sim.at;}
    return t;
  }
  for(const e of events){
    const eventAt=e.type==='decision'?e.input?.t:e.row?.[1];
    if(eventAt>=(record.start+300)*1000)break;
    if(e.type==='decision'){
      sim.decision({...e.input,t:clock(e.input.t)});decisions++;continue;
    }
    if(e.type!=='raw')throw Error('Unknown recording schema');
    const [kind,time,ts,a,b,c]=e.row,at=clock(time);
    if(kind==='T'){
      const id=JSON.stringify([e.token,ts,a,b,c]);
      // Identical public prints have no reliable execution ID; exclude ambiguity.
      if(seen.has(id))throw Error('Ambiguous duplicate public print');
      seen.add(id);
      sim.trade({id,at,sourceAt:ts,token:e.token,side:a?'BUY':'SELL',price:b,quantity:c});
      continue;
    }
    if(kind==='B')books.set(e.token,{bids:new Map(a),asks:new Map(b)});
    else if(kind==='P'){
      const book=books.get(e.token);if(!book)continue;
      const side=a===0?book.bids:book.asks;
      if(c)side.set(b,c);else side.delete(b);
    }else throw Error('Unknown book event');
    const book=books.get(e.token);
    if(book){
      const ask=Math.min(...[...book.asks].filter(x=>x[1]>0).map(x=>x[0]));
      if(Number.isFinite(ask)&&ask>0&&ask<=1)
        sim.book(e.token,at,{ask,levels:Object.fromEntries(book.bids)});
    }
  }
  if(!decisions)throw Error('No recorded official decisions');
  sim.expire(Math.max(sim.at,(record.start+300)*1000));
  return {sim,decisions,rounding};
}
module.exports={compare};
