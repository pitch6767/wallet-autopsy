const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
test('recorder absorbs synchronous bursts losslessly within bounded storage',
  {skip:!process.env.OFFICIAL_SOURCE},async()=>{
  const source=fs.readFileSync(process.env.OFFICIAL_SOURCE,'utf8');
  const begin=source.indexOf('const VALIDATION_BOOT'),end=source.indexOf('const tokIdx');
  assert.ok(begin>=0&&end>begin,'Recording implementation must be present');
  const context=vm.createContext({VERSION:'test',zlib});
  vm.runInContext('const REC={};'+source.slice(begin,end)+';globalThis.records=REC;',context);
  vm.runInContext(`
    for(let i=0;i<20000;i++)
      validationRecord(1,{type:"raw",row:["P",i,i,0,.5,2],payload:"x".repeat(230)});
  `,context);
  const recorded=context.records[1].validation;
  assert.ok(recorded.pending>2&&recorded.pending<=16);
  const deadline=Date.now()+5000;
  while(recorded.pending&&Date.now()<deadline)await new Promise(r=>setTimeout(r,10));
  assert.equal(recorded.pending,0);
  assert.equal(recorded.complete,true);
  const rows=recorded.chunks.flatMap(x=>JSON.parse(zlib.gunzipSync(Buffer.from(x,'base64'))))
    .concat(recorded.events);
  assert.equal(rows.length,20000);
  for(let i=0;i<rows.length;i++)assert.equal(rows[i].row[1],i);
  assert.ok(recorded.compressedBytes<=8*1024*1024);
});
