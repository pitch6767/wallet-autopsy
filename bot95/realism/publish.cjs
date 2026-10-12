const fs=require("node:fs");
const {atomic}=require("./ledger.cjs");
module.exports=function publisher(dir,url,fetcher=fetch){
  let busy=false;
  return async function publish(data){
    if(busy)return {skipped:true};busy=true;
    try{
      const file=dir+"/publication.json";
      const prev=fs.existsSync(file)?JSON.parse(fs.readFileSync(file,"utf8")):{rows:{}};
      if(prev.cohort!==data.cohort)prev.rows={};
      const hashes=require("node:crypto");
      const changed=data.rows.filter(r=>prev.rows[`${r.start}:${r.strategy}`]!==hashes.createHash("sha256").update(JSON.stringify(r)).digest("hex"));
      for(let i=0;i<Math.max(1,changed.length);i+=60){
        const rows=changed.slice(i,i+60);
        const response=await fetcher(url+"/api/realism/ingest",{method:"POST",headers:{"content-type":"application/json"},
          body:JSON.stringify({...data,rows}),signal:AbortSignal.timeout(15000)});
        if(!response.ok)throw Error("Publication HTTP "+response.status);
        const ack=await response.json();
        if(!ack.ok||ack.cohort!==data.cohort||ack.sequence!==data.sequence)throw Error("Invalid publication acknowledgement");
        for(const r of rows)prev.rows[`${r.start}:${r.strategy}`]=hashes.createHash("sha256").update(JSON.stringify(r)).digest("hex");
        prev.lastSuccess=Date.now();prev.cohort=data.cohort;
        atomic(file,prev);
      }
      return {ok:true,changed:changed.length};
    } finally{busy=false;}
  };
};
