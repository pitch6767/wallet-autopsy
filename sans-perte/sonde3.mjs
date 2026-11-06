const r=await fetch('https://edge.goldsky.com/data/openapi.json'); const j=await r.json();
for(const p of ['/data/polymarket/positions','/data/polymarket/activity']){ const o=j.paths[p].get;
 console.log('\n## '+p+'\n'+(o.description||'').slice(0,600));
 for(const x of (o.parameters||[])) console.log(' param',x.name,x.in,x.required?'REQUIRED':'',(x.description||'').replace(/\n/g,' ').slice(0,160)); }
console.log('\nsecurity', JSON.stringify(j.security||j.components?.securitySchemes).slice(0,300));
// profondeur du classement gratuit, tous temps
const D='https://data-api.polymarket.com/v2'; let cur='',n=0,pages=0,last;
while(pages<400){ const u=D+'/leaderboard?limit=50&timePeriod=ALL&orderBy=PNL'+(cur?'&cursor='+encodeURIComponent(cur):'');
 const r=await fetch(u); if(r.status!==200){console.log('stop',r.status,(await r.text()).slice(0,200));break;}
 const k=await r.json(); n+=k.data.length; pages++; last=k.data[k.data.length-1]; cur=k.pagination?.next_cursor; if(!cur)break; }
console.log('\nclassement ALL : portefeuilles lus',n,'pages',pages,'dernier',JSON.stringify(last));
const w='0x204f72f35326db932158cba6adff0b9a1da95e14';
for(const s of ['REDEEMABLE_LOST','CLOSED']){ const t=await (await fetch(D+'/positions?user='+w+'&status='+s+'&limit=2')).text(); console.log('\n## positions',s,t.slice(0,1200)); }
console.log('\n## user-stats',(await (await fetch(D+'/user-stats?user='+w)).text()).slice(0,800));
