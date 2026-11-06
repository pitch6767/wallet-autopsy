const D='https://data-api.polymarket.com/v2';
async function g(u){ try{const r=await fetch(u); const t=await r.text(); return r.status+' '+t;}catch(e){return 'ERR '+e.message;} }
const show=(n,t,k=1500)=>console.log('\n### '+n+'\n'+t.slice(0,k));
show('status', await g(D+'/status'));
const lb = await g(D+'/leaderboard?limit=3'); show('leaderboard', lb, 2500);
let w; try{ const j=JSON.parse(lb.slice(4)); const a=j.data||j.leaderboard||j; w=(a[0]||{}).proxyWallet||(a[0]||{}).wallet||(a[0]||{}).address||(a[0]||{}).user; }catch(e){}
show('leaderboard PERIOD ALL', await g(D+'/leaderboard?limit=2&timePeriod=ALL&orderBy=PNL'),800);
console.log('wallet test', w);
if(w){
 show('user-stats', await g(D+'/user-stats?user='+w));
 show('positions lost', await g(D+'/positions?user='+w+'&status=REDEEMABLE_LOST&limit=3'),2500);
 show('positions closed', await g(D+'/positions?user='+w+'&status=CLOSED&limit=3'),2500);
 show('user-pnl', await g(D+'/user-pnl?user='+w),800);
}
show('trades global 2023', await g(D+'/trades?limit=2&start=1680000000&end=1680086400'),1500);
show('trades global now', await g(D+'/trades?limit=2'),1500);
const oa = await g('https://edge.goldsky.com/data/openapi.json');
show('goldsky openapi', oa, 300);
try{ const j=JSON.parse(oa.slice(4)); for(const [p,v] of Object.entries(j.paths||{})) console.log('PATH',p,Object.keys(v).join(','),(Object.values(v)[0].summary||'').slice(0,120)); }catch(e){}
