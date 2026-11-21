// Veille — surveillance en direct du réseau de wallets trouvé sur les calls cryptoyeezuscalls (Solana)
// Alerte téléphone (notification web de la PWA) quand un wallet surveillé achète un token ; suivi auto des wallets qu'il finance ;
// lecture du canal Telegram pour mesurer l'avance de chaque alerte sur le call.
const VERSION = "1.1.1";
const MARQUEUR = "Veille wallets yeezus";
const RPC = ["https://solana-rpc.publicnode.com", "https://solana.drpc.org", "https://api.mainnet-beta.solana.com"];
const PAR_PASSAGE = 12;   // wallets lus par minute (rotation), pour rester sous les limites des serveurs gratuits
const dormir = ms => new Promise(r => setTimeout(r, ms));
const CANAL = "https://t.me/s/cryptoyeezuscalls";
const IGNORE = new Set(["So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"]);
const SEUIL_TRANSFERT = 0.5;   // SOL envoyés vers un nouveau wallet => on le suit
const MAX_WALLETS = 200;
const SEED = {"51o5VwwsB2KG1Ejuq2FdmaCQcnuTyKRF6c5HjtYVmEgr":"groupe FT9VD","5aud5SUDR3eS2Es6a7gZDXedXMEJUnJG1XdzXXHu89YS":"groupe FT9VD","FT9VDscMGy2qDkcbFBD4xLkaGPBqkEgDA6E59GaHN7u6":"groupe FT9VD",
"43hawvey7znGUfxnGo54Wrm4uGRN7S4tawVBWgrxf4uV":"groupe 9jA4MU","4r6qNe1XPwGaghFY6hmuDngdzzWaRJuhf8rdYA5vY4KZ":"groupe 9jA4MU","592X5D58VB9QyHVv2EyKw7PnkJPY4x2giwVqtN32ays1":"groupe 9jA4MU","5LE1mUudCxAZigJbaJDC4itTbbiy8P274fF256aQSQv":"groupe 9jA4MU","97WJWwFk23Nu5QkxCSYgqRo89UvdsEApPJtSwhMJfzd9":"groupe 9jA4MU","9jA4MUtsPAXy3ZhsiQUhkSXMop2ogrCWYv7rE9xovsWp":"groupe 9jA4MU","BDo54QPVCaFWEEfu4ftvyKL2tLXWEEa6dYvcBgVWpNYP":"groupe 9jA4MU","C3zCUv1QyMLKmavQ4Q3a54zyfTBBfKjXcodp3AxkKiwi":"groupe 9jA4MU","D2rcDMoWyayhMAPUdoHKoJz3syY6MHKm4hz4564jhetE":"groupe 9jA4MU","E6syzgXYWzmqFnFRZM9bymhbTm8CKaBQ6wqYVXTvGhYW":"groupe 9jA4MU","vAvfo5rEFSFh3zwYP9crZWZSnGT8FEn9FLoCpUJenzu":"groupe 9jA4MU",
"4xmBBT6ULCFgUUUPtc1L19Yjfxt912GYLx4da9pxKNr5":"relais (collecte FT9VD)","FX5rF3QAvqzhw5xTAJCF1Bo1gGVd8nSzquEnwhDRYeHX":"relais vers 9jA4MU","BdpVwDK5qKNhPBuaXxMYPLuA4ufnNjYRvucytWPopNGB":"reçu 188 SOL de 4xmBBT6U","32WtUYouq7EtqtxfV8jC5GmVcRcQW9xfy1GEiyNcWGjm":"reçu 51 SOL de 4xmBBT6U","6Di9hEvtEmoTPHCy6L7PGr5jqTLXRPG1hY9dgjMTarY5":"reçu 56 SOL de 4xmBBT6U","Byw469gjf6Urs4NvCc2x2hJtkf43X7bhxaR3xABiMBug":"reçu 43 SOL de 4xmBBT6U"};

function b64u(b) { let s = ""; for (const x of b) s += String.fromCharCode(x); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }

const SW = `self.addEventListener("push", e => e.waitUntil(fetch("/api/derniere", { cache: "no-store" }).then(r => r.json()).then(d => self.registration.showNotification(d.title || "Veille", { body: d.message || "", data: { url: d.click || "/" }, tag: String(d.ts || Date.now()) }))));
self.addEventListener("notificationclick", e => { e.notification.close(); e.waitUntil(clients.openWindow(e.notification.data.url)); });`;

export default {
  async fetch(req, env) { return env.VEILLE.get(env.VEILLE.idFromName("v1")).fetch(req); },
  async scheduled(ev, env, ctx) { ctx.waitUntil(env.VEILLE.get(env.VEILLE.idFromName("v1")).fetch("https://x/tick")); },
};

async function rpc(method, params) {
  let err = "";
  for (const u of [...RPC, RPC[0]]) {
    try {
      const r = await fetch(u, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }) });
      if (!r.ok) { err = u + " " + r.status; await dormir(400); continue; }
      const j = await r.json();
      if ("result" in j) return j.result;
      err = u + " " + JSON.stringify(j.error || {}).slice(0, 80);
    } catch (e) { err = u + " " + e.message; }
  }
  throw new Error(err);
}

export class Veille {
  constructor(ctx, env) {
    this.sql = ctx.storage.sql; this.env = env;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS wallets(addr TEXT PRIMARY KEY, label TEXT, ajoute INTEGER, last_sig TEXT, last_act INTEGER, n_achats INTEGER DEFAULT 0, source TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER, type TEXT, wallet TEXT, mint TEXT, sol REAL, detail TEXT, sig TEXT UNIQUE)`);
    try { this.sql.exec(`ALTER TABLE wallets ADD COLUMN last_scan INTEGER DEFAULT 0`); } catch (e) {}
    this.sql.exec(`CREATE TABLE IF NOT EXISTS calls(mint TEXT PRIMARY KEY, ts INTEGER, msg INTEGER)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS abos(endpoint TEXT PRIMARY KEY, ajoute INTEGER)`);
    const n = this.sql.exec(`SELECT count(*) c FROM wallets`).one().c;
    if (!n) for (const [a, l] of Object.entries(SEED)) this.sql.exec(`INSERT INTO wallets(addr,label,ajoute,source) VALUES(?,?,?,?)`, a, l, Date.now(), "départ");
  }
  get(k) { const r = this.sql.exec(`SELECT v FROM kv WHERE k=?`, k).toArray(); return r.length ? r[0].v : null; }
  set(k, v) { this.sql.exec(`INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v`, k, String(v)); }

  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/tick") { await this.tick(); return new Response("ok"); }
    if (u.pathname === "/api/etat") return Response.json(this.etat(), { headers: { "cache-control": "no-store" } });
    if (u.pathname === "/api/vapid") return new Response((await this.cles()).pub);
    if (u.pathname === "/api/abonner" && req.method === "POST") { const j = await req.json(); if (j && j.endpoint) this.sql.exec(`INSERT OR REPLACE INTO abos(endpoint,ajoute) VALUES(?,?)`, j.endpoint, Date.now()); return Response.json({ ok: true, abonnes: this.sql.exec(`SELECT count(*) c FROM abos`).one().c }); }
    if (u.pathname === "/api/derniere") return Response.json(JSON.parse(this.get("derniere") || "{}"), { headers: { "cache-control": "no-store" } });
    if (u.pathname === "/sw.js") return new Response(SW, { headers: { "content-type": "text/javascript", "cache-control": "no-store" } });
    if (u.pathname === "/api/test-alerte") { const r = await this.notifier("Test Veille", "Si tu lis ceci, les alertes marchent.", 3, "https://veille.pitch67.workers.dev/"); return new Response(r); }
    if (u.pathname === "/manifest.webmanifest") return new Response(JSON.stringify({ name: "Veille wallets", short_name: "Veille", start_url: "/", display: "standalone", background_color: "#0f1115", theme_color: "#0f1115", icons: [{ src: "/icone.svg", sizes: "any", type: "image/svg+xml" }] }), { headers: { "content-type": "application/manifest+json" } });
    if (u.pathname === "/icone.svg") return new Response(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#0f1115"/><circle cx="50" cy="50" r="30" fill="none" stroke="#f5c542" stroke-width="8"/><circle cx="50" cy="50" r="10" fill="#f5c542"/></svg>`, { headers: { "content-type": "image/svg+xml" } });
    return new Response(PAGE.replaceAll("__V__", VERSION), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
  }

  async cles() {
    let k = this.get("vapid");
    if (!k) {
      const kp = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
      const priv = await crypto.subtle.exportKey("jwk", kp.privateKey);
      const pub = b64u(new Uint8Array(await crypto.subtle.exportKey("raw", kp.publicKey)));
      k = JSON.stringify({ priv, pub }); this.set("vapid", k);
    }
    return JSON.parse(k);
  }
  async notifier(title, message, priority, click) {
    this.set("derniere", JSON.stringify({ title, message, click, ts: Date.now() }));
    const { priv, pub } = await this.cles();
    const cle = await crypto.subtle.importKey("jwk", priv, { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
    const abos = this.sql.exec(`SELECT endpoint FROM abos`).toArray();
    const res = [];
    for (const { endpoint } of abos) {
      try {
        const aud = new URL(endpoint).origin;
        const enc = o => b64u(new TextEncoder().encode(JSON.stringify(o)));
        const base = enc({ typ: "JWT", alg: "ES256" }) + "." + enc({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: "mailto:alertes@i-a.fan" });
        const sig = b64u(new Uint8Array(await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, cle, new TextEncoder().encode(base))));
        const r = await fetch(endpoint, { method: "POST", headers: { TTL: "3600", Urgency: priority >= 4 ? "high" : "normal", Authorization: `vapid t=${base}.${sig}, k=${pub}` }, body: "" });
        res.push(r.status);
        if (r.status === 404 || r.status === 410) this.sql.exec(`DELETE FROM abos WHERE endpoint=?`, endpoint);
        else if (!r.ok) this.set("err_push", r.status + " " + (await r.text()).slice(0, 150));
      } catch (e) { this.set("err_push", e.message); res.push("ERR"); }
    }
    return abos.length ? "envoyé à " + abos.length + " appareil(s) : " + res.join(",") : "aucun appareil abonné";
  }

  async tick() {
    if (Date.now() - Number(this.get("tick_en_cours") || 0) < 50000) return;   // pas deux passages en même temps
    this.set("tick_en_cours", Date.now());
    const t0 = Date.now(); let erreurs = 0, lus = 0;
    const ws = this.sql.exec(`SELECT * FROM wallets ORDER BY COALESCE(last_scan,0) ASC LIMIT ?`, PAR_PASSAGE).toArray();
    for (const w of ws) {
      this.sql.exec(`UPDATE wallets SET last_scan=? WHERE addr=?`, Date.now(), w.addr);
      if (Date.now() - t0 > 40000) break;
      try { lus += await this.scanWallet(w); await dormir(250); } catch (e) { erreurs++; this.set("derniere_erreur", new Date().toISOString() + " " + w.addr.slice(0, 6) + " " + e.message); }
    }
    if (Date.now() - Number(this.get("canal_ts") || 0) > 4 * 60000) { try { await this.lireCanal(); } catch (e) { this.set("err_canal", e.message); } this.set("canal_ts", Date.now()); }
    this.set("dernier_tick", Date.now()); this.set("tick_ms", Date.now() - t0); this.set("tick_err", erreurs); this.set("tick_tx", lus);
    this.set("tick_en_cours", 0);
  }

  async scanWallet(w) {
    const vide = w.last_sig === "VIDE";   // wallet sans transaction récente : tout ce qui arrive est nouveau
    const sigs = await rpc("getSignaturesForAddress", [w.addr, w.last_sig && !vide ? { limit: 25, until: w.last_sig } : { limit: vide ? 25 : 1 }]);
    if (!sigs.length) { if (!w.last_sig) this.sql.exec(`UPDATE wallets SET last_sig='VIDE' WHERE addr=?`, w.addr); return 0; }
    if (!w.last_sig) { this.sql.exec(`UPDATE wallets SET last_sig=?, last_act=? WHERE addr=?`, sigs[0].signature, (sigs[0].blockTime || 0) * 1000, w.addr); return 0; }
    let n = 0;
    for (const s of sigs.slice(0, 15).reverse()) {
      if (s.err) continue;
      const tx = await rpc("getTransaction", [s.signature, { maxSupportedTransactionVersion: 0, encoding: "jsonParsed" }]);
      if (tx) { n++; await this.analyser(w, s.signature, tx); }
    }
    this.sql.exec(`UPDATE wallets SET last_sig=? WHERE addr=?`, sigs[0].signature, w.addr);
    return n;
  }

  async analyser(w, sig, tx) {
    const ts = (tx.blockTime || Date.now() / 1000) * 1000;
    const keys = tx.transaction.message.accountKeys.map(k => typeof k === "string" ? k : k.pubkey);
    const i = keys.indexOf(w.addr);
    const dsol = i >= 0 ? (tx.meta.postBalances[i] - tx.meta.preBalances[i]) / 1e9 : 0;
    // 1) achat : le solde d'un token (hors SOL/USDC/USDT) du wallet augmente ET il dépense des SOL
    const pre = {}, post = {};
    for (const b of tx.meta.preTokenBalances || []) if (b.owner === w.addr) pre[b.mint] = Number(b.uiTokenAmount.uiAmount || 0);
    for (const b of tx.meta.postTokenBalances || []) if (b.owner === w.addr) post[b.mint] = Number(b.uiTokenAmount.uiAmount || 0);
    let wsol = 0;
    for (const m of new Set([...Object.keys(pre), ...Object.keys(post)])) if (m === "So11111111111111111111111111111111111111112") wsol = (post[m] || 0) - (pre[m] || 0);
    const depense = -(dsol + wsol);
    for (const m of Object.keys(post)) {
      if (IGNORE.has(m) || (post[m] || 0) <= (pre[m] || 0) || depense < 0.01) continue;
      this.sql.exec(`INSERT OR IGNORE INTO events(ts,type,wallet,mint,sol,detail,sig) VALUES(?,?,?,?,?,?,?)`, ts, "achat", w.addr, m, Math.round(depense * 1000) / 1000, "", sig + ":" + m.slice(0, 8));
      this.sql.exec(`UPDATE wallets SET last_act=?, n_achats=n_achats+1 WHERE addr=?`, ts, w.addr);
      const qui = this.sql.exec(`SELECT DISTINCT wallet FROM events WHERE type='achat' AND mint=? AND ts>?`, m, ts - 30 * 60000).toArray().map(r => r.wallet);
      const lien = "https://gmgn.ai/sol/token/" + m;
      if (qui.length === 1) await this.notifier(`Achat ${w.label}`, `${w.addr.slice(0, 6)}… achète ${depense.toFixed(2)} SOL de ${m}`, 4, lien);
      else if (qui.length === 2) await this.notifier(`SIGNAL FORT : 2 wallets du réseau`, `${qui.map(x => x.slice(0, 6)).join(" + ")} achètent ${m}`, 5, lien);
    }
    // 2) transfert de SOL vers un autre wallet : on suit le receveur
    const ins = [...tx.transaction.message.instructions, ...(tx.meta.innerInstructions || []).flatMap(g => g.instructions)];
    for (const x of ins) {
      const p = x.parsed;
      if (x.program !== "system" || !p || p.type !== "transfer" || p.info.source !== w.addr) continue;
      const sol = p.info.lamports / 1e9, dst = p.info.destination;
      if (sol < SEUIL_TRANSFERT) continue;
      this.sql.exec(`INSERT OR IGNORE INTO events(ts,type,wallet,mint,sol,detail,sig) VALUES(?,?,?,?,?,?,?)`, ts, "transfert", w.addr, null, sol, dst, sig + ":" + dst.slice(0, 8));
      this.sql.exec(`UPDATE wallets SET last_act=? WHERE addr=?`, ts, w.addr);
      const deja = this.sql.exec(`SELECT 1 FROM wallets WHERE addr=?`, dst).toArray().length;
      const total = this.sql.exec(`SELECT count(*) c FROM wallets`).one().c;
      if (!deja && total < MAX_WALLETS) {
        this.sql.exec(`INSERT INTO wallets(addr,label,ajoute,source) VALUES(?,?,?,?)`, dst, `reçu ${sol.toFixed(1)} SOL de ${w.addr.slice(0, 6)}`, Date.now(), w.addr);
        await this.notifier(`Nouveau wallet suivi`, `${w.addr.slice(0, 6)}… envoie ${sol.toFixed(2)} SOL à ${dst} — ajouté à la surveillance`, 3, "https://solscan.io/account/" + dst);
      }
    }
  }

  async lireCanal() {
    const t = await (await fetch(CANAL, { headers: { "user-agent": "Mozilla/5.0" } })).text();
    const blocs = t.split('class="tgme_widget_message_wrap').slice(1);
    let n = 0;
    for (const b of blocs) {
      const id = (b.match(/data-post="cryptoyeezuscalls\/(\d+)"/) || [])[1];
      const d = (b.match(/datetime="([^"]+)"/) || [])[1];
      if (!id || !d) continue;
      for (const ca of new Set(b.match(/[1-9A-HJ-NP-Za-km-z]{32,44}/g) || [])) {
        if (/^\d+$/.test(ca)) continue;
        this.sql.exec(`INSERT OR IGNORE INTO calls(mint,ts,msg) VALUES(?,?,?)`, ca, Date.parse(d), Number(id)); n++;
      }
    }
    this.set("canal_n", n);
  }

  etat() {
    const ev = this.sql.exec(`SELECT e.*, w.label, c.ts call_ts, c.msg FROM events e LEFT JOIN wallets w ON w.addr=e.wallet LEFT JOIN calls c ON c.mint=e.mint ORDER BY e.ts DESC LIMIT 300`).toArray();
    const ws = this.sql.exec(`SELECT * FROM wallets ORDER BY COALESCE(last_act,0) DESC`).toArray();
    const kv = Object.fromEntries(this.sql.exec(`SELECT k,v FROM kv`).toArray().map(r => [r.k, r.v]));
    const appels = this.sql.exec(`SELECT count(*) c FROM calls`).one().c;
    return { version: VERSION, marqueur: MARQUEUR, events: ev, wallets: ws, diag: { dernier_tick: Number(kv.dernier_tick || 0), tick_ms: kv.tick_ms, erreurs: kv.tick_err, tx_lues: kv.tick_tx, derniere_erreur: kv.derniere_erreur || "", calls_connus: appels, err_canal: kv.err_canal || "", err_push: kv.err_push || "", appareils: this.sql.exec(`SELECT count(*) c FROM abos`).one().c } };
  }
}

const PAGE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Veille wallets</title><link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/icone.svg"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="theme-color" content="#0f1115">
<!-- Veille wallets yeezus -->
<style>body{margin:0;font:15px -apple-system,system-ui,sans-serif;background:#0f1115;color:#e8e8e8}
header{position:sticky;top:0;background:#171a21;padding:12px 14px calc(10px) 14px;display:flex;gap:10px;align-items:center;border-bottom:1px solid #2a2f3a;z-index:2}
header h1{font-size:17px;margin:0;flex:1}#retour{display:none;font-size:22px;background:none;border:0;color:#f5c542;padding:0 8px 0 0}
nav{display:flex;gap:8px}nav button{background:#262b36;color:#ddd;border:0;border-radius:8px;padding:7px 10px;font-size:14px}nav button.on{background:#f5c542;color:#111}
main{padding:12px}.c{background:#171a21;border:1px solid #2a2f3a;border-radius:10px;padding:10px 12px;margin-bottom:8px}
.t{font-size:12px;color:#9aa}.fort{border-color:#f5c542}.ok{color:#4ade80}.ko{color:#f87171}a{color:#7cc4ff;word-break:break-all}.mono{font-family:ui-monospace,monospace;font-size:12px;word-break:break-all}
.pill{display:inline-block;font-size:11px;padding:2px 6px;border-radius:6px;background:#262b36;margin-right:4px}.v{font-size:11px;color:#667;text-align:center;padding:16px}</style></head><body>
<header><button id="retour" aria-label="Retour à l'accueil">←</button><h1>Veille wallets</h1><nav><button id="b-a" class="on">Alertes</button><button id="b-w">Wallets</button></nav></header>
<div id="push" style="padding:12px 12px 0"></div><main id="m">Chargement…</main><div class="v">version __V__ · heure de Paris</div>
<script>
const V="__V__";try{if(sessionStorage.getItem("v")!==V){sessionStorage.setItem("v",V);}}catch(e){}
const P=t=>new Date(t).toLocaleString("fr-CH",{timeZone:"Europe/Paris",day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"});
const C=a=>a?a.slice(0,6)+"…"+a.slice(-4):"";
let E=null,vue="a";
function aff(){const m=document.getElementById("m");if(!E)return;document.getElementById("b-a").className=vue==="a"?"on":"";document.getElementById("b-w").className=vue==="w"?"on":"";document.getElementById("retour").style.display=vue==="a"?"none":"inline";
const d=E.diag,age=Math.round((Date.now()-d.dernier_tick)/1000);
let h='<div class="c t">Dernier passage : '+(d.dernier_tick?('il y a '+age+' s'):'pas encore')+' · '+E.wallets.length+' wallets surveillés · '+d.calls_connus+' adresses lues dans le canal</div>';
if(vue==="a"){const ev=E.events;if(!ev.length)h+='<div class="c">Aucun mouvement depuis le démarrage. Dès qu’un wallet du réseau achète un token ou envoie des SOL à un nouveau wallet, il apparaît ici et sur ton téléphone.</div>';
const cnt={};ev.filter(e=>e.type==="achat").forEach(e=>{cnt[e.mint]=(cnt[e.mint]||new Set()).add(e.wallet)});
for(const e of ev){if(e.type==="achat"){const n=cnt[e.mint].size;let av="";if(e.call_ts){const dm=Math.round((e.call_ts-e.ts)/60000);av=dm>=0?'<span class="ok">Appelé par le canal '+dm+' min après cet achat</span>':'<span class="ko">Le canal l’avait appelé '+(-dm)+' min avant</span>';}
h+='<div class="c'+(n>1?' fort':'')+'"><div class="t">'+P(e.ts)+' · '+(n>1?'<b>SIGNAL FORT : '+n+' wallets</b>':'achat')+'</div><b>'+(e.label||'')+'</b> '+C(e.wallet)+' achète '+e.sol+' SOL<div class="mono"><a href="https://gmgn.ai/sol/token/'+e.mint+'" target="_blank">'+e.mint+'</a></div>'+(av?'<div>'+av+'</div>':'')+'</div>';}
else h+='<div class="c"><div class="t">'+P(e.ts)+' · transfert</div>'+C(e.wallet)+' envoie '+(+e.sol).toFixed(2)+' SOL à <a class="mono" href="https://solscan.io/account/'+e.detail+'" target="_blank">'+e.detail+'</a></div>';}}
else{for(const w of E.wallets)h+='<div class="c"><span class="pill">'+(w.label||'')+'</span><div class="mono"><a href="https://gmgn.ai/sol/address/'+w.addr+'" target="_blank">'+w.addr+'</a></div><div class="t">dernière activité vue : '+(w.last_act?P(w.last_act):'aucune depuis le démarrage')+' · achats vus : '+w.n_achats+'</div></div>';}
m.innerHTML=h;}
async function charger(){try{E=await (await fetch("/api/etat",{cache:"no-store"})).json();if(E.version!==V){try{if(sessionStorage.getItem("rl")!==E.version){sessionStorage.setItem("rl",E.version);location.reload();return}}catch(e){}}aff();}catch(e){document.getElementById("m").textContent="Erreur de chargement";}}
function aller(x){if(x!==vue){vue=x;if(x!=="a")history.pushState({v:x},"");aff();}}
document.getElementById("b-a").onclick=()=>{vue="a";aff()};document.getElementById("b-w").onclick=()=>aller("w");document.getElementById("retour").onclick=()=>{vue="a";aff()};
addEventListener("popstate",()=>{vue="a";aff()});
async function etatPush(){const z=document.getElementById("push");const ios=/iPhone|iPad/.test(navigator.userAgent),inst=matchMedia("(display-mode: standalone)").matches||navigator.standalone;
if(!("serviceWorker" in navigator)||!("PushManager" in window)){z.innerHTML=ios&&!inst?'<div class="c"><b>Pour recevoir les alertes sur l’iPhone</b> : ajoute d’abord cette page sur l’écran d’accueil (Safari → Partager → Sur l’écran d’accueil), puis ouvre-la depuis l’icône.</div>':'<div class="c">Ce navigateur ne peut pas recevoir les alertes.</div>';return}
const reg=await navigator.serviceWorker.register("/sw.js");const sub=await reg.pushManager.getSubscription();
z.innerHTML=sub&&Notification.permission==="granted"?'<div class="c ok">Alertes activées sur cet appareil. <button id="tst" style="margin-left:6px">Tester</button></div>':'<div class="c"><button id="act" style="background:#f5c542;color:#111;border:0;border-radius:8px;padding:10px 14px;font-size:16px;font-weight:600">Activer les alertes sur ce téléphone</button></div>';
const a=document.getElementById("act");if(a)a.onclick=async()=>{const p=await Notification.requestPermission();if(p!=="granted"){alert("Autorisation refusée");return}
const k=await (await fetch("/api/vapid")).text();const key=Uint8Array.from(atob(k.replace(/-/g,"+").replace(/_/g,"/")+"==".slice(0,(4-k.length%4)%4)),c=>c.charCodeAt(0));
const s=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key});await fetch("/api/abonner",{method:"POST",body:JSON.stringify(s)});etatPush();};
const t=document.getElementById("tst");if(t)t.onclick=async()=>{t.textContent="envoi…";t.textContent=await (await fetch("/api/test-alerte")).text();};}
etatPush().catch(e=>{document.getElementById("push").innerHTML='<div class="c ko">Alertes : '+e.message+'</div>'});
charger();setInterval(charger,20000);
</script></body></html>`;
