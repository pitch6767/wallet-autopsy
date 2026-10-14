const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {compare}=require('./recorded-comparison.cjs');
const file=process.env.OFFICIAL_SOURCE;
test('recorded official inputs -> partial fills -> official requote -> settlement',{skip:!file},()=>{
 const source=fs.readFileSync(file,'utf8'),version=source.match(/const VERSION = "([^"]+)"/)[1];
 const input={mk:{start:0,end:300,up:'u',down:'d'},t:10000,tleft:290-1,
  ua:[.55],da:[.5],P:{pu:.52},TOX:{},bids:{u:.5,d:.45}};
 const record={start:0,version,validation:{schema:1,complete:true,partialStartup:false,events:[
  {type:'raw',token:'u',row:['B',1,0,[[.5,2]],[[.55,200]]]},
  {type:'raw',token:'u',row:['B',10000,9999,[[.5,2]],[[.55,200]]]},
  {type:'raw',token:'d',row:['B',10000,9999,[[.45,2]],[[.5,200]]]},
  {type:'decision',input},
  {type:'raw',token:'u',row:['T',10120,10110,0,.5,12]},
  {type:'decision',input:{...input,t:10150,bids:{u:.51,d:.45}}},
  {type:'raw',token:'u',row:['T',10200,10190,0,.5,4]},
  {type:'decision',input:{...input,t:10260,tleft:5}},
 ]}};
 const r=compare(record,source,100);
 assert.equal(r.decisions,3);
 assert.equal(r.sim.snapshot().quantities.Up,14);
 assert.equal(r.sim.orders[2].parts,+(45/.51).toFixed(2));
 assert.equal(r.sim.settle({at:300001,winner:'Up',closed:true,resolved:true,evidence:'fixture'}).settlementPnl,7);
 assert.throws(()=>compare({...record,validation:{...record.validation,complete:false}},source,100),/Incomplete/);
 assert.throws(()=>compare({...record,version:'wrong'},source,100),/Matching/);
 const compressed={...record,validation:{...record.validation,schema:2,pending:0,
  chunks:[require('node:zlib').gzipSync(JSON.stringify(record.validation.events)).toString('base64')],events:[]}};
 assert.equal(compare(compressed,source,100).sim.snapshot().cost,7);
 assert.throws(()=>compare({...compressed,validation:{...compressed.validation,pending:1}},source,100),/unfinished/);
});
