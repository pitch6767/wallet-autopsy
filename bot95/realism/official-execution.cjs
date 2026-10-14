'use strict';
// Isolated deterministic replay adapter; no network or real order capability.
const {create}=require('./official-m10.cjs');
class OfficialExecution {
  constructor(source,{latencyMs,makerFeePerShare,stepTimeoutMs=100}){
    if(![latencyMs,makerFeePerShare].every(x=>Number.isFinite(x)&&x>=0))throw Error('Explicit execution assumptions required');
    Object.assign(this,{latencyMs,makerFeePerShare,at:0,orders:[],active:new Set(),cancelled:[],events:[],seen:new Map(),books:{},
      qty:{Up:0,Down:0},cost:0,fees:0,exposureMs:0,peakUnmatched:0,
      peakCommitted:{Up:0,Down:0},lastAt:null,winner:null,issues:[]});
    this.strategy=create(source,{poser:(v,m,u,p,b)=>this.place(m,u,p,b),annuler:(o,r)=>this.cancel(o,r)},{stepTimeoutMs});
  }
  event(type,fields={}){this.events.push({at:this.at,type,...fields});}
  place(mk,up,prix,budget){
    const o={id:this.orders.length+1,token:up?mk.up:mk.down,side:up?'Up':'Down',
      prix,parts:+(budget/prix).toFixed(2),remplR:0,etat:'envoi',arrival:this.at+this.latencyMs};
    this.orders.push(o);this.active.add(o);
    const committed=this.orders.filter(x=>x.side===o.side).reduce((n,x)=>
      n+(this.active.has(x)?x.parts:x.remplR)*x.prix,0);
    this.peakCommitted[o.side]=Math.max(this.peakCommitted[o.side],committed);
    this.event('order',{...o,budget});return o;
  }
  cancel(o,reason){
    if(o.tAnnulDemande)return;
    o.tAnnulDemande=this.at;o.cancelAt=this.at+this.latencyMs;
    this.event('cancel-request',{id:o.id,reason});
  }
  advance(at){
    if(!Number.isFinite(at)||at<this.at||this.winner)throw Error('Invalid chronology or settled account');
    if(this.lastAt!==null&&Math.abs(this.qty.Up-this.qty.Down)>1e-8)this.exposureMs+=at-this.lastAt;
    this.at=at;this.lastAt=at;
    for(const o of this.active){
      if(o.etat==='envoi'&&o.arrival<=at){
        const b=this.books[o.token];
        // Do not use a later snapshot as though it had existed at arrival.
        if(!b||b.at>o.arrival||o.arrival-b.at>500){
          o.etat='rejetee';this.issues.push('Missing fresh book at arrival');
        }else if(b.ask<=o.prix)o.etat='rejetee';
        else{o.etat='posee';o.queue=b.levels[String(o.prix)]||0;}
        this.event('arrival',{id:o.id,state:o.etat});
      }
      if(o.cancelAt<=at&&['envoi','posee'].includes(o.etat)){
        o.etat='annulee';this.cancelled.push(o);this.event('cancelled',{id:o.id});
      }
      if(!['envoi','posee'].includes(o.etat))this.active.delete(o);
    }
    this.cancelled=this.cancelled.filter(o=>at-o.cancelAt<=1000);
  }
  book(token,at,{ask,levels}){
    if(!Number.isFinite(ask)||ask<=0||ask>1||!levels||
      Object.entries(levels).some(([p,q])=>!Number.isFinite(+p)||!Number.isFinite(q)||q<0))throw Error('Invalid book');
    this.advance(at);this.books[token]={at,ask,levels:{...levels}};
  }
  decision(input){
    this.advance(input.t);this.strategy.step(input);
    this.event('decision',{identity:this.strategy.identity});
  }
  trade({id,at,sourceAt,token,side,price,quantity}){
    if(!id||![at,sourceAt,price,quantity].every(Number.isFinite)||quantity<=0||price<=0||price>=1||sourceAt>at)throw Error('Invalid trade evidence');
    const signature=JSON.stringify([sourceAt,token,side,price,quantity]);
    if(this.seen.has(id)){
      if(this.seen.get(id)!==signature)throw Error('Conflicting trade ID');
      return;
    }
    this.advance(at);this.seen.set(id,signature);
    if(side!=='SELL')return;
    if(at-sourceAt>1000){this.issues.push('Stale public print');return;}
    if(this.cancelled.some(o=>o.token===token&&o.prix===price&&sourceAt>=o.arrival&&sourceAt<o.cancelAt))
      this.issues.push('Ambiguous print received after cancellation');
    let remaining=quantity;
    for(const o of this.active){
      if(o.token!==token||o.prix!==price||sourceAt<o.arrival)continue;
      if(o.etat==='annulee'&&sourceAt<o.cancelAt){this.issues.push('Ambiguous print received after cancellation');continue;}
      if(o.etat!=='posee')continue;
      const ahead=Math.min(o.queue,remaining);o.queue-=ahead;remaining-=ahead;
      const n=Math.min(o.parts-o.remplR,remaining);
      if(n<=0)continue;
      o.remplR+=n;remaining-=n;
      this.qty[o.side]+=n;this.cost+=n*o.prix;
      this.peakUnmatched=Math.max(this.peakUnmatched,Math.abs(this.qty.Up-this.qty.Down));
      this.fees+=n*this.makerFeePerShare;
      this.event('fill',{id:o.id,tradeId:id,quantity:n,price:o.prix,fee:n*this.makerFeePerShare});
    }
  }
  settle({at,winner,closed,resolved,evidence}){
    if(!closed||!resolved||!['Up','Down'].includes(winner)||!evidence)throw Error('Confirmed settlement required');
    this.advance(at);
    if(this.active.size)throw Error('Expire or cancel orders before settlement');
    this.winner=winner;this.event('settlement',{winner,evidence});
    return this.snapshot();
  }
  expire(at){
    this.advance(at);
    this.expiredAt=at;
    for(const o of this.orders)if(['envoi','posee'].includes(o.etat))o.etat='fin du cycle';
    this.active.clear();
    this.event('expiry');
  }
  snapshot(){
    const spent={Up:0,Down:0};
    for(const o of this.orders)spent[o.side]+=o.remplR*o.prix;
    return {identity:this.strategy.identity,quantities:{...this.qty},cost:this.cost,fees:this.fees,spent,expiredAt:this.expiredAt??null,
      peakCommitted:{...this.peakCommitted},peakUnmatched:this.peakUnmatched,
      sideSpendOver50:spent.Up>50.01||spent.Down>50.01,
      exposureMs:this.exposureMs,unmatched:Math.abs(this.qty.Up-this.qty.Down),
      settlementPnl:this.winner?this.qty[this.winner]-this.cost-this.fees:null,
      issues:[...new Set(this.issues)],liveValidated:false};
  }
}
module.exports={OfficialExecution};
