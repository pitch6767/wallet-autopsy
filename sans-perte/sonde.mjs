// Sonde des index on-chain Polymarket (Goldsky) : schéma + échantillons
const P = 'https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/';
const subs = ['pnl-subgraph/0.0.14','pnl-subgraph/prod','positions-subgraph/0.0.7','positions-subgraph/prod','activity-subgraph/0.0.4','activity-subgraph/prod','orderbook-subgraph/0.0.1','orderbook-subgraph/prod'];
async function q(url, query){
  try{ const r = await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({query})});
    return await r.text(); }catch(e){ return 'ERR '+e.message; }
}
const intro = `{__schema{queryType{fields{name}} types{name kind fields{name type{name kind ofType{name kind ofType{name}}}}}}}`;
for (const s of subs){
  const url = P+s+'/gn';
  console.log('\n######## '+s);
  const t = await q(url, intro);
  try{ const j = JSON.parse(t);
    if(!j.data){ console.log(t.slice(0,300)); continue; }
    for(const ty of j.data.__schema.types){
      if(ty.kind!=='OBJECT'||ty.name.startsWith('_')||ty.name==='Query'||ty.name==='Subscription') continue;
      console.log(ty.name+': '+ty.fields.map(f=>f.name+':'+(f.type.name||f.type.ofType?.name||f.type.ofType?.ofType?.name)).join(', '));
    }
    console.log('META', await q(url,'{_meta{block{number timestamp} hasIndexingErrors}}'));
  }catch(e){ console.log(t.slice(0,300)); }
}
