const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {compare}=require('./recorded-comparison.cjs');
const file=process.env.OFFICIAL_SOURCE;
test('recorded official inputs -> partial fills -> official requote -> settlement',{skip:!file},(t)=>{
 const source=fs.readFileSync(file,'utf8'),version=source.match(/const VERSION = "([^"]+)"/)[1];
 const input={mk:{start:0,end:300,up:'u',down:'d'},t:10000,tleft:290-1,
  ua:[.55],da:[.5],P:{pu:.52},TOX:{},bids:{u:.5,d:.45}};
 const record={start:0,version,validation:{schema:1,complete:true,partialStartup:false,events:[
  {type:'raw',token:'u',row:['B',1,0,[[.5,2]],[[.55,200]]]},
  {type:'raw',token:'u',row:['B',10000,9999,[[.5,2]],[[.55,200]]]},
  {type:'raw',token:'d',row:['B',10000,9999,[[.45,2]],[[.5,200]]]},
  {type:'decision',input},
   {type:'raw',token:'u',row:['P',10050,10049,0,.5,2]},
   {type:'raw',token:'u',row:['P',10050,10049,1,.55,200]},
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
 const packed=record.validation.events.map(e=>{
  if(e.type==='raw')return ['R',e.token==='u'?0:1,e.row];
  const i=e.input;return ['D',i.t,i.tleft,i.ua,i.da,i.P,i.TOX.u,i.TOX.d,i.bids.u,i.bids.d];
 });
 const dictionary={...compressed,validation:{...compressed.validation,schema:3,tokens:['u','d'],
  market:input.mk,chunks:[require('node:zlib').gzipSync(JSON.stringify(packed)).toString('base64')]}};
 assert.equal(compare(dictionary,source,100).sim.snapshot().cost,7);
 const dir=fs.mkdtempSync(require('node:os').tmpdir()+'/disk-replay-');
 t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const bytes=Buffer.from(dictionary.validation.chunks[0],'base64');
 fs.writeFileSync(dir+'/test.blocks',bytes);
 const disk={...dictionary,validation:{...dictionary.validation,schema:4,file:'test.blocks',
  chunks:[{offset:0,length:bytes.length}]}};
 assert.equal(compare(disk,source,100,dir).sim.snapshot().cost,7);
 assert.equal(compare(disk,source,100,dir,{stepTimeoutMs:0}).sim.snapshot().cost,7);
 assert.throws(()=>compare({...disk,validation:{...disk.validation,file:'../test.blocks'}},source,100,dir),/Invalid/);
 fs.truncateSync(dir+'/test.blocks',bytes.length-1);
 assert.throws(()=>compare(disk,source,100,dir),/Truncated/);
 const buyDuplicates={...record,validation:{...record.validation,events:[...record.validation.events,
  {type:'raw',token:'u',row:['T',10300,10299,1,.5,12]},
  {type:'raw',token:'u',row:['T',10300,10299,1,.5,12]}]}};
 assert.equal(compare(buyDuplicates,source,100).sim.snapshot().cost,7);
 assert.throws(()=>compare({...compressed,validation:{...compressed.validation,pending:1}},source,100),/unfinished/);
});
