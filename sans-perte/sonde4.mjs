const D='https://data-api.polymarket.com/v2';
const J=async u=>{const r=await fetch(u);return [r.status,await r.text()];};
const w='0x204f72f35326db932158cba6adff0b9a1da95e14';
for(const q of ['sort=realized_pnl_asc','sort_by=REALIZEDPNL&sort_direction=ASC','sortBy=REALIZEDPNL&sortDirection=ASC','order_by=realized_pnl&order=asc','sort=pnl_asc']){
 const [s,t]=await J(D+'/positions?user='+w+'&status=CLOSED&limit=3&'+q);
 let pn=''; try{pn=JSON.parse(t).data.map(x=>Math.round(x.realized_pnl)).join(' | ')}catch(e){pn=t.slice(0,200)}
 console.log(q,'->',s,pn);
}
const [s0,t0]=await J(D+'/positions?user='+w+'&status=CLOSED&limit=500'); try{const k=JSON.parse(t0); console.log('limit500 ->',k.data.length,'neg:',k.data.filter(x=>x.realized_pnl<0).length, 'has_more',k.pagination.has_more)}catch(e){console.log(t0.slice(0,200))}
const [s1,t1]=await J(D+'/user-stats?user='+w); console.log('\nuser-stats FULL', t1);
const [s2,t2]=await J(D+'/activity?user='+w+'&limit=3'); console.log('\nactivity',s2,t2.slice(0,1500));
const [s3,t3]=await J(D+'/activity?user='+w+'&limit=3&type=TRANSFER'); console.log('\nactivity transfer',s3,t3.slice(0,800));
// vitesse et profondeur du classement
let cur='',n=0,p=0,t=Date.now(),last;
while(p<3000){const u=D+'/leaderboard?limit=50&timePeriod=ALL&orderBy=PNL'+(cur?'&cursor='+encodeURIComponent(cur):'');const r=await fetch(u);
 if(r.status!==200){console.log('stop',r.status,(await r.text()).slice(0,200));break;} const k=await r.json(); n+=k.data.length;p++; last=k.data.at(-1); cur=k.pagination?.next_cursor; if(!cur||last.pnl<=0)break; if(Date.now()-t>240000)break;}
console.log('\nclassement: lus',n,'en',Math.round((Date.now()-t)/1000),'s ; dernier',JSON.stringify(last));
