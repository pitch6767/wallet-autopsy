'use strict';
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
function* events(v,root){
  let fd;
  try{
    if(v.schema===4){
      if(!root||!/^[a-zA-Z0-9_-]+\.blocks$/.test(v.file||''))throw Error('Invalid recording file');
      if(v.chunks.length)fd=fs.openSync(path.join(root,v.file),fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
    }
    function decode(e){
      if(v.schema<3)return e;
      if(e[0]==='R'){
        if(typeof v.tokens?.[e[1]]!=='string')throw Error('Unknown recorded token');
        return {type:'raw',token:v.tokens[e[1]],row:e[2]};
      }
      if(e[0]!=='D'||!v.market?.up||!v.market?.down)throw Error('Missing recorded market');
      const mk={...v.market};
      return {type:'decision',input:{mk,t:e[1],tleft:e[2],ua:e[3],da:e[4],P:e[5],
        TOX:{[mk.up]:e[6],[mk.down]:e[7]},bids:{[mk.up]:e[8],[mk.down]:e[9]}}};
    }
    for(const block of v.chunks||[]){
      let bytes;
      if(v.schema===4){
        if(!Number.isSafeInteger(block?.offset)||block.offset<0||
          !Number.isSafeInteger(block?.length)||block.length<1||block.length>2*1024*1024)
          throw Error('Invalid recording block');
        bytes=Buffer.alloc(block.length);
        let n=0;
        while(n<bytes.length){
          const got=fs.readSync(fd,bytes,n,bytes.length-n,block.offset+n);
          if(!got)throw Error('Truncated recording block');
          n+=got;
        }
      }else{
        if(typeof block!=='string')throw Error('Missing compressed recording block');
        bytes=Buffer.from(block,'base64');
      }
      for(const e of JSON.parse(zlib.gunzipSync(bytes,{maxOutputLength:2*1024*1024})))yield decode(e);
    }
    for(const e of v.events||[])yield decode(e);
  }finally{if(fd!==undefined)fs.closeSync(fd);}
}
module.exports={events};
