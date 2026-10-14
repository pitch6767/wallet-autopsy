const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib');
test('recorder absorbs synchronous bursts losslessly within bounded storage',
  {skip:!process.env.OFFICIAL_SOURCE},async(t)=>{
  const source=fs.readFileSync(process.env.OFFICIAL_SOURCE,'utf8');
  const begin=source.indexOf('const VALIDATION_BOOT'),end=source.indexOf('const tokIdx');
  assert.ok(begin>=0&&end>begin,'Recording implementation must be present');
  const dir=fs.mkdtempSync(require('node:os').tmpdir()+'/recorder-');
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const context=vm.createContext({VERSION:'test',zlib,fs,DIR:dir});
  vm.runInContext('const REC={};'+source.slice(begin,end)+';globalThis.records=REC;',context);
  vm.runInContext(`
    for(let i=0;i<5000;i++)
      validationRecord(1,{type:"raw",token:"u",row:["B",i,i,
        Array.from({length:50},()=>[.5,2]),Array.from({length:50},()=>[.6,3])]});
  `,context);
  const recorded=context.records[1].validation;
  assert.ok(recorded.pending>2&&recorded.pending<=16);
  const deadline=Date.now()+5000;
  while(recorded.pending&&Date.now()<deadline)await new Promise(r=>setTimeout(r,10));
  assert.equal(recorded.pending,0);
  assert.equal(recorded.complete,true);
  const rows=[...require('./recording-events.cjs').events(recorded,dir+'/validation')];
  assert.equal(rows.length,5000);
  for(let i=0;i<rows.length;i++)assert.equal(rows[i].row[1],i);
  assert.ok(recorded.compressedBytes<=8*1024*1024);
});
