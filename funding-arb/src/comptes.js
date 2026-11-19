// Comptes réels (lecture seule pour l'instant) : Gate, Bybit, OKX, KuCoin.
// Les clés ne sont jamais dans le code : secrets Cloudflare, posés par le déploiement depuis les secrets GitHub.
// AUCUN ORDRE n'est envoyé : le mode réel n'existe pas encore (« rien de réel maintenant », Pitch, 19.11.2026).
const enc = new TextEncoder();
const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
const b64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)));
async function hmac(algo, secret, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: algo }, false, ["sign"]);
  return crypto.subtle.sign("HMAC", k, enc.encode(msg));
}
async function lire(url, init) {
  const r = await fetch(url, init);
  const t = await r.text();
  let d; try { d = JSON.parse(t); } catch (e) { d = t; }
  if (!r.ok) throw new Error("HTTP " + r.status + " " + t.slice(0, 160));
  return d;
}

export const PLATEFORMES_REELLES = ["gate", "bybit", "okx", "kucoin"];
const CLES = {
  gate: ["GATE_KEY", "GATE_SECRET"],
  bybit: ["BYBIT_KEY", "BYBIT_SECRET"],
  okx: ["OKX_KEY", "OKX_SECRET", "OKX_PASSPHRASE"],
  kucoin: ["KUCOIN_KEY", "KUCOIN_SECRET", "KUCOIN_PASSPHRASE"],
};
export const clesPresentes = (env, ex) => CLES[ex].every((n) => env[n]);

// ---------- Requêtes signées (documentation officielle de chaque plateforme)
const SIGNE = {
  async gate(env, method, path, query = "", body = "") { // HexEncode(HMAC_SHA512(secret, METHOD\n/api/v4/...\nquery\nHexEncode(SHA512(body))\nts))
    const ts = Math.floor(Date.now() / 1000).toString();
    const h = hex(await crypto.subtle.digest("SHA-512", enc.encode(body)));
    const sign = hex(await hmac("SHA-512", env.GATE_SECRET, [method, "/api/v4" + path, query, h, ts].join("\n")));
    return lire("https://api.gateio.ws/api/v4" + path + (query ? "?" + query : ""), { method, body: body || undefined,
      headers: { KEY: env.GATE_KEY, Timestamp: ts, SIGN: sign, "Content-Type": "application/json", Accept: "application/json" } });
  },
  async bybit(env, method, path, query = "", body = "") { // hex HMAC_SHA256(secret, ts + key + recvWindow + (query | body))
    const ts = Date.now().toString(), rw = "5000";
    const sign = hex(await hmac("SHA-256", env.BYBIT_SECRET, ts + env.BYBIT_KEY + rw + (method === "GET" ? query : body)));
    return lire("https://api.bybit.com" + path + (query ? "?" + query : ""), { method, body: body || undefined,
      headers: { "X-BAPI-API-KEY": env.BYBIT_KEY, "X-BAPI-TIMESTAMP": ts, "X-BAPI-RECV-WINDOW": rw, "X-BAPI-SIGN": sign, "Content-Type": "application/json" } });
  },
  async okx(env, method, path, query = "", body = "") { // base64 HMAC_SHA256(secret, isoTs + METHOD + path?query + body)
    const ts = new Date().toISOString(), p = path + (query ? "?" + query : "");
    const sign = b64(await hmac("SHA-256", env.OKX_SECRET, ts + method + p + body));
    return lire("https://www.okx.com" + p, { method, body: body || undefined,
      headers: { "OK-ACCESS-KEY": env.OKX_KEY, "OK-ACCESS-SIGN": sign, "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": env.OKX_PASSPHRASE, "Content-Type": "application/json" } });
  },
  async kucoin(env, method, path, query = "", body = "") { // base64 HMAC_SHA256(secret, ts + METHOD + path?query + body) ; passphrase signée (version 2)
    const ts = Date.now().toString(), p = path + (query ? "?" + query : "");
    const sign = b64(await hmac("SHA-256", env.KUCOIN_SECRET, ts + method + p + body));
    const pass = b64(await hmac("SHA-256", env.KUCOIN_SECRET, env.KUCOIN_PASSPHRASE));
    return lire("https://api.kucoin.com" + p, { method, body: body || undefined,
      headers: { "KC-API-KEY": env.KUCOIN_KEY, "KC-API-SIGN": sign, "KC-API-TIMESTAMP": ts, "KC-API-PASSPHRASE": pass, "KC-API-KEY-VERSION": "2", "Content-Type": "application/json" } });
  },
};

// ---------- Contrôle des comptes : la clé fonctionne-t-elle, combien d'USDT disponibles ?
const SOLDE = {
  async gate(env) { const d = await SIGNE.gate(env, "GET", "/unified/accounts"); return Number(d.balances?.USDT?.available ?? 0); },
  async bybit(env) { const d = await SIGNE.bybit(env, "GET", "/v5/account/wallet-balance", "accountType=UNIFIED");
    if (d.retCode !== 0) throw new Error(d.retMsg); const c = (d.result?.list?.[0]?.coin || []).find((x) => x.coin === "USDT"); return Number(c?.walletBalance ?? 0); },
  async okx(env) { const d = await SIGNE.okx(env, "GET", "/api/v5/account/balance", "ccy=USDT");
    if (d.code !== "0") throw new Error(d.msg); return Number(d.data?.[0]?.details?.[0]?.availBal ?? 0); },
  async kucoin(env) { const d = await SIGNE.kucoin(env, "GET", "/api/v1/accounts", "currency=USDT");
    if (d.code !== "200000") throw new Error(d.msg); return (d.data || []).reduce((s, a) => s + Number(a.available || 0), 0); },
};

export async function etatComptes(env) {
  const out = {};
  await Promise.all(PLATEFORMES_REELLES.map(async (ex) => {
    if (!clesPresentes(env, ex)) { out[ex] = { cles: false }; return; }
    try { out[ex] = { cles: true, ok: true, usdt: await SOLDE[ex](env) }; }
    catch (e) { out[ex] = { cles: true, ok: false, err: String(e.message || e).slice(0, 160) }; }
  }));
  return { reel: false, comptes: out };
}
