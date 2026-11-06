const D='https://data-api.polymarket.com/v2';
const J=async u=>{const r=await fetch(u);return [r.status,await r.text()];};
const ws=['0x204f72f35326db932158cba6adff0b9a1da95e14','0x4794657547f6f40d83eac4dfad7cd2b2e7f3cc92'];
for(const v of ['REALIZED_PNL','realized_pnl','CASHPNL','PNL','TOTAL_PNL','PERCENTPNL','CURRENT','TOKENS','RESOLVING','last_event_at','LAST_EVENT_AT']){
 for(const dir of ['ASC']){
 const [s,t]=await J(D+'/positions?user='+ws[0]+'&status=CLOSED&limit=3&sort_by='+v+'&sort_direction='+dir);
 let pn=''; try{pn=JSON.parse(t).data.map(x=>Math.round(x.realized_pnl)).join(' | ')}catch(e){pn=t.slice(0,160)}
 console.log(v,dir,'->',s,pn);}
}
for(const w of ws){ for(const st of ['CLOSED','REDEEMABLE_LOST','REDEEMABLE','OPEN']){
 let cur='',n=0,neg=0,p=0,min=1e18; while(p<200){const [s,t]=await J(D+'/positions?user='+w+'&status='+st+'&limit=500'+(cur?'&cursor='+encodeURIComponent(cur):'')); if(s!==200){console.log(s,t.slice(0,150));break;}
  const k=JSON.parse(t); for(const x of k.data){n++; if(x.realized_pnl<0)neg++; min=Math.min(min,x.realized_pnl);} p++; cur=k.pagination.next_cursor; if(!cur)break;}
 console.log(w.slice(0,10),st,'positions',n,'negatives',neg,'pnl min',Math.round(min),'pages',p); } }
