'use strict';
const {OfficialExecution}=require('./official-execution.cjs');
const zlib=require('node:zlib');
function compare(record,source,latencyMs){
  const v=record.validation;
  if(!v||!v.complete||v.partialStartup)throw Error(v?.reason||'Incomplete or startup recording');
  if(v.pending)throw Error('Recording compression unfinished');
  if(![1,2,3].includes(v.schema))throw Error('Unsupported recording schema');
  const events=[];
  for(const chunk of v.chunks||[]){
    if(typeof chunk!=='string')throw Error('Missing compressed recording block');
    events.push(...JSON.parse(zlib.gunzipSync(Buffer.from(chunk,'base64'),{maxOutputLength:2*1024*1024})));
  }
  events.push(...v.events);
  if(v.schema===3)for(let n=0;n<events.length;n++){
    const e=events[n];
    if(e[0]==='R'){
      if(typeof v.tokens?.[e[1]]!=='string')throw Error('Unknown recorded token');
      events[n]={type:'raw',token:v.tokens[e[1]],row:e[2]};
    }else if(e[0]==='D'){
      const mk={...v.market};
      if(!mk.up||!mk.down)throw Error('Missing recorded market');
      events[n]={type:'decision',input:{mk,t:e[1],tleft:e[2],ua:e[3],da:e[4],P:e[5],
        TOX:{[mk.up]:e[6],[mk.down]:e[7]},bids:{[mk.up]:e[8],[mk.down]:e[9]}}};
    }else throw Error('Unknown packed event');
  }
  const first=events[0];
  const firstAt=first?.type==='raw'?first.row?.[1]:first?.input?.t;
  if(!Number.isFinite(firstAt)||firstAt>record.start*1000+5000)
    throw Error('Recording begins after cycle start (including startup warm-up)');
  if(!source.includes(`const VERSION = "${record.version}"`))throw Error('Matching source version unavailable');
  if(!events.some(e=>e.type==='decision'))throw Error('No recorded official decisions');
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
      // Taker BUY cannot execute M10's passive BUY orders. It only advances time.
      if(a===1){sim.advance(at);continue;}
      const id=JSON.stringify([e.token,ts,a,b,c]);
      // Identical public prints have no reliable execution ID; exclude ambiguity.
      if(seen.has(id))throw Error('Ambiguous duplicate public print');
      seen.add(id);
      sim.trade({id,at,sourceAt:ts,token:e.token,side:a?'BUY':'SELL',price:b,quantity:c});
      continue;
    }
    // Advance against the previous book before changing its shared levels.
    sim.advance(at);
    if(kind==='B')books.set(e.token,{bids:Object.fromEntries(a),asks:new Map(b),ask:null});
    else if(kind==='P'){
      const book=books.get(e.token);if(!book)continue;
      if(a===0){if(c)book.bids[b]=c;else delete book.bids[b];}
      else {
        if(c)book.asks.set(b,c);else book.asks.delete(b);
        if(book.ask===null||b<=book.ask)book.ask=null;
      }
    }else throw Error('Unknown book event');
    const book=books.get(e.token);
    if(book){
      const ask=book.ask===null?Math.min(...[...book.asks].filter(x=>x[1]>0).map(x=>x[0])):book.ask;
      book.ask=ask;
      if(Number.isFinite(ask)&&ask>0&&ask<=1)
        sim.book(e.token,at,{ask,levels:book.bids});
    }
  }
  if(!decisions)throw Error('No recorded official decisions');
  sim.expire(Math.max(sim.at,(record.start+300)*1000));
  return {sim,decisions,rounding};
}
module.exports={compare};
