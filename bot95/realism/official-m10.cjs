'use strict';
// Extract, do not reimplement, official decisions. No network or order transport.
const vm = require('node:vm');
const crypto = require('node:crypto');
function extract(source) {
  const start = source.indexOf('function coter(Q,');
  const end = source.indexOf('function coterX(', start);
  const m10 = source.indexOf('// M10 DOUBLE MAKER');
  const loop = source.indexOf('for (const up of sides)', m10);
  const next = source.indexOf('// M11 ', loop);
  if ([start,end,m10,loop,next].some(x=>x<0) || !(start<end && m10<loop && loop<next))
    throw Error('Official source contract changed: review required');
  const quote = source.slice(start,end);
  const decision = source.slice(loop,next);
  if (!quote.includes('50 - S2.depense') || !decision.includes('M10 double maker meilleur prix'))
    throw Error('Unrecognized official strategy');
  return {quote,decision,sha256:crypto.createHash('sha256').update(source).digest('hex'),
    version:source.match(/const VERSION = "([^"]+)"/)?.[1] || null};
}
function create(source, execution, {stepTimeoutMs=100}={}) {
  const spec = extract(source);
  // execution must feed the official order objects with simulated fills and
  // cancellation acknowledgements; source decisions are never rewritten.
  if (!execution || typeof execution.poser !== 'function' || typeof execution.annuler !== 'function')
    throw Error('Execution adapter required');
  const context = vm.createContext({
    Q:{}, poser:execution.poser, annuler:execution.annuler,
    sides:[true,false], r2:x=>Math.round(x*100)/100,
  }, {codeGeneration:{strings:false,wasm:false}});
  new vm.Script(spec.quote).runInContext(context,{timeout:100});
  const script = new vm.Script(spec.decision);
  return {
    identity:{version:spec.version,sha256:spec.sha256},
    step({mk,t,tleft,ua,da,P,TOX,bids}) {
      if (![t,tleft,ua?.[0],da?.[0],P?.pu,bids?.[mk?.up],bids?.[mk?.down]].every(Number.isFinite) || !TOX)
        throw Error('Complete official market and toxicity inputs required');
      Object.assign(context,{mk,t,tleft,ua,da,P,TOX,meilleurAcheteur:id=>bids[id]});
      script.runInContext(context,stepTimeoutMs?{timeout:stepTimeoutMs}:undefined);
    }
  };
}
module.exports={extract,create};
