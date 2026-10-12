const {test}=require("node:test"),assert=require("node:assert/strict");
async function setup(){
  const {RealismStore}=await import("./cloudflare-realism.mjs");
  const data=new Map();
  const storage={
    async get(k){return structuredClone(data.get(k));},
    async put(k,v){data.set(k,structuredClone(v));},
    async list({prefix="",limit=1000,reverse=false}={}){
      let a=[...data].filter(([k])=>k.startsWith(prefix)).sort(([a],[b])=>a.localeCompare(b));
      if(reverse)a.reverse();return new Map(a.slice(0,limit));
    },
    async transaction(fn){return fn(storage);},
  };
  return new RealismStore({storage});
}
const body={schema:2,model:"realism-2",cohort:"cohort-test",sequence:1,at:1000,started:500,
  rows:[{start:1200,strategy:"M10",up:10,down:2,costUp:5,costDown:1,offers:2,exposedMs:100,shareSeconds:8}]};
const post=(d,ip="107.174.203.201")=>new Request("https://bot95/api/realism/ingest",
  {method:"POST",headers:{"cf-connecting-ip":ip},body:JSON.stringify(d)});
test("ingestion requires the VPS IP",async()=>{
  const s=await setup();assert.equal((await s.fetch(post(body,"1.2.3.4"))).status,403);
});
test("duplicate and out-of-order publications cannot double or reverse positions",async()=>{
  const s=await setup();await s.fetch(post(body));await s.fetch(post(body));
  await s.fetch(post({...body,sequence:0,at:2000,rows:[{...body.rows[0],up:0}]}));
  const d=await (await s.fetch(new Request("https://bot95/api/realism/status"))).json();
  assert.equal(d.rows.length,1);assert.equal(d.rows[0].up,10);assert.equal(d.meta.sequence,1);
});
test("cohorts remain isolated and new schemas reject malformed inventory",async()=>{
  const s=await setup();await s.fetch(post(body));
  await s.fetch(post({...body,cohort:"other",started:600}));
  const d=await(await s.fetch(new Request("https://bot95/api/realism/status?cohort=cohort-test"))).json();
  assert.equal(d.cohorts.length,2);assert.equal(d.rows.length,1);
  assert.equal((await s.fetch(post({...body,rows:[{...body.rows[0],up:-2}]}))).status,400);
});
test("dashboard has polling, stale-state and explicit ghost wording",async()=>{
  const s=await setup();const r=await s.fetch(new Request("https://bot95/rapide-realiste"));
  const text=await r.text();assert.equal(r.status,200);
  for(const phrase of ["Fantôme uniquement","DONNÉES PÉRIMÉES","setInterval(load,15000)","Single leg"])assert.ok(text.includes(phrase));
});
