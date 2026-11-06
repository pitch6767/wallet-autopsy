const D='https://data-api.polymarket.com/v2';
const J=async u=>{try{const r=await fetch(u,{headers:{accept:'application/json'}});return [r.status,await r.text()];}catch(e){return [0,'ERR '+e.message]}};
const w2='0x4794657547f6f40d83eac4dfad7cd2b2e7f3cc92', w1='0x204f72f35326db932158cba6adff0b9a1da95e14';
let [s,t]=await J(D+'/positions?user='+w2+'&sort_by=TOTAL_PNL&sort_direction=ASC&limit=5');
try{console.log('TOTAL asc w2', JSON.parse(t).data.map(x=>[x.status,Math.round(x.realized_pnl),Math.round(x.total_pnl),x.redeemable,x.current_size].join('/')).join(' | '))}catch(e){console.log(t.slice(0,300))}
[s,t]=await J(D+'/positions?user='+w2+'&sort_by=REALIZED_PNL&sort_direction=ASC&limit=3&status=CLOSED');
try{console.log('REAL asc CLOSED w2', JSON.parse(t).data.map(x=>[x.status,Math.round(x.realized_pnl)].join('/')).join(' | '))}catch(e){console.log(t.slice(0,300))}
[s,t]=await J(D+'/activity?user='+w1+'&limit=1&type=XYZ'); console.log('types?',t.slice(0,300));
for(const b of ['https://polygon.blockscout.com/api/v2/addresses/'+w1+'/token-transfers?type=ERC-20','https://polygon.blockscout.com/api/v2/addresses/'+w1]){
 [s,t]=await J(b); console.log('\n',b,s,t.slice(0,1500)); }
[s,t]=await J('https://polygon.blockscout.com/api?module=account&action=tokentx&address='+w1+'&sort=desc&offset=5&page=1'); console.log('\netherscan-style',s,t.slice(0,1500));
