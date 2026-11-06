// sans-perte — ÉTAPE TEST : peut-on lire gratuitement toute l'histoire des trades Polymarket sur la blockchain Polygon ?
import { DurableObject } from 'cloudflare:workers';

const RPCS = ['https://polygon-rpc.com', 'https://polygon.drpc.org', 'https://polygon-bor-rpc.publicnode.com',
  'https://1rpc.io/matic', 'https://polygon.llamarpc.com', 'https://polygon-pokt.nodies.app'];
const TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
// anciennes bourses Polymarket (V1), pour tester l'accès à l'historique ancien
const V1 = ['0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e', '0xc5d563a36ae78145c45a50134d48a1215220f80a'];

async function rpc(url, method, params, ms = 25000) {
  const t = Date.now();
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), signal: AbortSignal.timeout(ms) });
    const txt = await r.text(); let j; try { j = JSON.parse(txt); } catch { return { ok: false, ms: Date.now() - t, err: r.status + ' ' + txt.slice(0, 120) }; }
    if (j.error) return { ok: false, ms: Date.now() - t, err: JSON.stringify(j.error).slice(0, 160) };
    return { ok: true, ms: Date.now() - t, res: j.result };
  } catch (e) { return { ok: false, ms: Date.now() - t, err: e.message }; }
}
const hex = n => '0x' + n.toString(16);

export class Scan extends DurableObject {
  async test() {
    const R = { debut: new Date().toISOString() };
    // 1. découvrir les contrats et événements d'un trade actuel (V2)
    const tr = await (await fetch('https://data-api.polymarket.com/v2/trades?limit=60')).json();
    const txs = [...new Set(tr.data.map(x => x.transaction_hash))].slice(0, 6);
    const tally = {}; let okRpc = null;
    for (const tx of txs) {
      for (const u of (okRpc ? [okRpc] : RPCS)) {
        const r = await rpc(u, 'eth_getTransactionReceipt', [tx]);
        if (r.ok && r.res) { okRpc = u; for (const l of r.res.logs) { const k = l.address.toLowerCase() + ' ' + l.topics[0]; tally[k] = (tally[k] || 0) + 1; } break; }
      }
    }
    R.rpc_recu = okRpc;
    R.evenements_dans_trades = Object.entries(tally).sort((a, b) => b[1] - a[1]).slice(0, 12);
    const cible = R.evenements_dans_trades.find(([k]) => !k.endsWith(TRANSFER) && !k.includes('0x4dfe1bbbcf077ddc3e01291eea2d5c70c2b422b415d95645b9adcfd678cb1d63'));
    if (!cible) return R;
    const [adr, topic] = cible[0].split(' ');
    R.cible = { contrat: adr, evenement: topic };
    // 2. chaque RPC : hauteur, taille de fenêtre acceptée, vitesse
    R.rpcs = [];
    for (const u of RPCS) {
      const h = await rpc(u, 'eth_blockNumber', [], 10000);
      const e = { rpc: u, ok: h.ok, err: h.err };
      if (h.ok) {
        const head = parseInt(h.res, 16); e.bloc = head; e.fenetres = [];
        for (const w of [100, 1000, 5000, 10000, 50000]) {
          const r = await rpc(u, 'eth_getLogs', [{ address: adr, topics: [topic], fromBlock: hex(head - w), toBlock: hex(head - 1) }]);
          e.fenetres.push({ blocs: w, ok: r.ok, ms: r.ms, nb: r.ok ? r.res.length : null, err: r.err });
          if (!r.ok) break;
        }
        // historique ancien : bloc ~45 M (2023)
        const v = await rpc(u, 'eth_getLogs', [{ address: V1, fromBlock: hex(45000000), toBlock: hex(45000999) }]);
        e.historique_2023 = { ok: v.ok, ms: v.ms, nb: v.ok ? v.res.length : null, err: v.err };
      }
      R.rpcs.push(e);
    }
    R.fin = new Date().toISOString();
    return R;
  }
}
const json = o => new Response(JSON.stringify(o, null, 1), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === '/api/test') return json(await env.SCAN.get(env.SCAN.idFromName('test')).test());
    return env.ASSETS.fetch(req);
  }
};
