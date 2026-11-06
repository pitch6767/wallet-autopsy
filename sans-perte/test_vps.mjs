// Test lecture blockchain Polygon depuis le VPS (court, ~2 min, lecture seule, ne touche pas au bot)
const RPCS=['https://polygon-bor-rpc.publicnode.com','https://polygon.drpc.org','https://1rpc.io/matic','https://polygon-rpc.com','https://polygon.llamarpc.com','https://polygon.gateway.tenderly.co','https://rpc.ankr.com/polygon'];
const EX='0xe111180000d2663c0091e4f400237545b87b996b', EV='0xd543adfd945773f1a62f74f0ee55a5e3b9b1a28262980ba90b1a89f2ea84d8ee';
const V1=['0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e','0xc5d563a36ae78145c45a50134d48a1215220f80a'];
const hex=n=>'0x'+n.toString(16);
async function rpc(u,m,p){const t=Date.now();try{const r=await fetch(u,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:m,params:p}),signal:AbortSignal.timeout(20000)});const x=await r.text();let j;try{j=JSON.parse(x)}catch{return{ok:0,ms:Date.now()-t,err:r.status+' '+x.slice(0,90)}}if(j.error)return{ok:0,ms:Date.now()-t,err:JSON.stringify(j.error).slice(0,110)};return{ok:1,ms:Date.now()-t,res:j.result}}catch(e){return{ok:0,ms:Date.now()-t,err:e.message}}}
const clean=s=>String(s).replace(/[<>]/g,'');
let best=null;
for(const u of RPCS){const h=await rpc(u,'eth_blockNumber',[]);if(!h.ok){console.log(clean(u+' | bloc: ECHEC '+h.err));continue}
 const head=parseInt(h.res,16);let line=u+' | bloc '+head;let maxw=0;
 for(const w of [100,1000,5000,10000,50000]){const r=await rpc(u,'eth_getLogs',[{address:EX,topics:[EV],fromBlock:hex(head-w),toBlock:hex(head-1)}]);
  line+=' | '+w+' blocs: '+(r.ok?r.res.length+' trades en '+r.ms+' ms':'ECHEC '+r.err);if(!r.ok)break;maxw=w}
 const v=await rpc(u,'eth_getLogs',[{address:V1,fromBlock:hex(45000000),toBlock:hex(45000999)}]);
 line+=' | histoire 2023: '+(v.ok?v.res.length+' evenements en '+v.ms+' ms':'ECHEC '+v.err);
 console.log(clean(line)); if(maxw&&(!best||maxw>best.w))best={u,w:maxw,head}}
if(best){ // debit soutenu 60 s sur le meilleur acces
 let b=best.head-1,blocs=0,trades=0,err=0;const t=Date.now();const w=Math.min(best.w,10000);
 while(Date.now()-t<60000){const r=await rpc(best.u,'eth_getLogs',[{address:EX,topics:[EV],fromBlock:hex(b-w),toBlock:hex(b-1)}]);
  if(r.ok){blocs+=w;trades+=r.res.length;b-=w}else{err++;await new Promise(s=>setTimeout(s,2000))}}
 const s=(Date.now()-t)/1000;console.log(clean('DEBIT '+best.u+' : '+blocs+' blocs ('+(blocs/43200).toFixed(1)+' jours) et '+trades+' trades lus en '+s.toFixed(0)+' s, erreurs '+err));}
console.log('FIN TEST');
