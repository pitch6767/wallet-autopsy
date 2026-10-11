// Passage en réel : ordres signés Polymarket (client officiel v2), clés lues dans les secrets Cloudflare.
// Rien ne part tant que le secret MODE_REEL ne vaut pas "oui" ET que l'arrêt d'urgence n'est pas actif.
import axios from "axios";
import { ClobClient, Side, OrderType } from "@polymarket/clob-client-v2";
import { createWalletClient, http } from "viem";
import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";
import { polygon } from "viem/chains";

// Cloudflare Workers : pas de module http de Node. L'adaptateur « fetch » d'axios (1.20) impose cache: "default" à chaque requête, ce que
// Cloudflare refuse (« Unsupported cache mode: default ») : tous les appels du client officiel échouaient. Adaptateur minimal à la place.
export async function adaptateurFetch(config) {
  const url = axios.getUri(config), h = config.headers && config.headers.toJSON ? config.headers.toJSON() : { ...(config.headers || {}) };
  const headers = {}; for (const [k, v] of Object.entries(h)) if (v != null && v !== false) headers[k] = String(v);
  const r = await fetch(url, { method: (config.method || "get").toUpperCase(), headers, body: config.data == null ? undefined : config.data });
  const data = config.responseType === "arraybuffer" ? await r.arrayBuffer() : await r.text();
  const response = { data, status: r.status, statusText: r.statusText, headers: Object.fromEntries(r.headers.entries()), config, request: null };
  const ok = config.validateStatus ? config.validateStatus(r.status) : r.status >= 200 && r.status < 300;
  if (ok) return response;
  throw new axios.AxiosError("Request failed with status code " + r.status, r.status >= 500 ? "ERR_BAD_RESPONSE" : "ERR_BAD_REQUEST", config, null, response);
}
axios.defaults.adapter = adaptateurFetch;
const HOTE = "https://clob.polymarket.com";
const norm = (k) => (k.startsWith("0x") ? k : "0x" + k).trim();

export class Reel {
  constructor(env) { this.env = env; this.client = null; this.journal = []; }
  configure() { return !!(this.env.POLY_CLE_PRIVEE && this.env.POLY_ADRESSE_PORTEFEUILLE); }
  modeReel() { return this.configure() && this.env.MODE_REEL === "oui"; }
  noter(x) { this.journal.unshift({ t: new Date().toISOString(), ...x }); this.journal.length = Math.min(this.journal.length, 50); }

  async init(typeSignature) {
    const st = typeSignature ?? (this.typeSignature || +(this.env.POLY_TYPE_SIGNATURE || 1));
    if (this.client && this.typeSignature === st) return this.client;
    const account = privateKeyToAccount(norm(this.env.POLY_CLE_PRIVEE));
    const signer = createWalletClient({ account, chain: polygon, transport: http("https://polygon-rpc.com") });
    const funder = this.env.POLY_ADRESSE_PORTEFEUILLE.trim();
    const base = new ClobClient({ host: HOTE, chain: 137, signer, signatureType: st, funderAddress: funder, throwOnError: true });
    const creds = await base.createOrDeriveApiKey();
    this.client = new ClobClient({ host: HOTE, chain: 137, signer, creds, signatureType: st, funderAddress: funder, throwOnError: true });
    this.typeSignature = st; this.signataire = account.address; this.portefeuille = funder;
    await this.client.getVersion();                     // mis en cache : pas de requête au moment de l'ordre
    return this.client;
  }

  // garde la connexion vers Polymarket ouverte (appelé régulièrement)
  async rechauffer() { if (this.client) { try { await this.client.getOk(); } catch (_) {} } }

  async solde() {
    const c = await this.init();
    const r = await c.getBalanceAllowance({ asset_type: "COLLATERAL" });
    return +r.balance / 1e6;
  }

  // achat immédiat : tout ce qui est disponible jusqu'à prixMax, pour montantUsd au plus ; le reste est annulé
  async acheter(tokenID, prixMax, montantUsd) {
    const c = await this.init(), t0 = Date.now();
    const r = await c.createAndPostMarketOrder({ tokenID, price: prixMax, amount: +montantUsd.toFixed(2), side: Side.BUY }, { tickSize: "0.01", negRisk: false }, OrderType.FAK);
    this.noter({ op: "achat", tokenID: tokenID.slice(0, 8), prixMax, montantUsd, ms: Date.now() - t0, r });
    return { ms: Date.now() - t0, usd: +(r.makingAmount || 0), parts: +(r.takingAmount || 0), statut: r.status, id: r.orderID, brut: r };
  }

  // vente immédiate de `parts` au prix plancher prixMin
  async vendre(tokenID, prixMin, parts) {
    const c = await this.init(), t0 = Date.now();
    const r = await c.createAndPostMarketOrder({ tokenID, price: prixMin, amount: +parts.toFixed(2), side: Side.SELL }, { tickSize: "0.01", negRisk: false }, OrderType.FAK);
    this.noter({ op: "vente", tokenID: tokenID.slice(0, 8), prixMin, parts, ms: Date.now() - t0, r });
    return { ms: Date.now() - t0, parts: +(r.makingAmount || 0), usd: +(r.takingAmount || 0), statut: r.status, id: r.orderID, brut: r };
  }

  // offre posée (n'achète jamais au prix affiché : rejetée si elle croiserait le carnet)
  async poserOffre(tokenID, prix, parts) {
    const c = await this.init(), t0 = Date.now();
    const r = await c.createAndPostOrder({ tokenID, price: prix, size: +parts.toFixed(2), side: Side.BUY }, { tickSize: "0.01", negRisk: false }, OrderType.GTC, true);
    this.noter({ op: "offre", tokenID: tokenID.slice(0, 8), prix, parts, ms: Date.now() - t0, r });
    return { ms: Date.now() - t0, id: r.orderID, statut: r.status, brut: r };
  }
  async etatOrdre(id) { const c = await this.init(); return c.getOrder(id); }
  async annuler(id) { const c = await this.init(); const r = await c.cancelOrder({ orderID: id }); this.noter({ op: "annulation", id, r }); return r; }
  async toutAnnuler() { const c = await this.init(); const r = await c.cancelAll(); this.noter({ op: "tout annuler", r }); return r; }

  // test sans risque : offre de 5 parts à 0,01 (jamais servie), puis annulation ; détecte le bon type de signature
  async test(tokenID) {
    const essais = [];
    for (const st of [+(this.env.POLY_TYPE_SIGNATURE || 1), 1, 2, 0].filter((x, i, a) => a.indexOf(x) === i)) {
      try {
        this.client = null;
        await this.init(st);
        const o = await this.poserOffre(tokenID, 0.01, 5);
        const a = o.id ? await this.annuler(o.id) : null;
        essais.push({ typeSignature: st, ok: !!o.id, ms: o.ms, ordre: o.brut, annulation: a });
        if (o.id) return { ok: true, typeSignature: st, signataire: this.signataire, portefeuille: this.portefeuille, solde: await this.solde(), essais };
      } catch (err) { essais.push({ typeSignature: st, erreur: String((err && err.message) || err).slice(0, 300) }); }
    }
    this.client = null;
    return { ok: false, essais };
  }
}

// Identifiants API pour le flux PolyBolt (lecture des prix) : tirés d'un portefeuille JETABLE, vide, créé ici. Aucun lien avec le portefeuille de Pitch.
// Authentification L1 de Polymarket faite à la main avec fetch (le client officiel passe par axios, qui échoue dans Cloudflare : « Unsupported cache mode »).
export async function identifiantsLecture(storage) {
  let k = await storage.get("pb:cleJetable");
  if (!k) { k = generatePrivateKey(); await storage.put("pb:cleJetable", k); }
  const account = privateKeyToAccount(k), ts = String(Math.floor(Date.now() / 1000));
  const sig = await account.signTypedData({
    domain: { name: "ClobAuthDomain", version: "1", chainId: 137 },
    types: { ClobAuth: [{ name: "address", type: "address" }, { name: "timestamp", type: "string" }, { name: "nonce", type: "uint256" }, { name: "message", type: "string" }] },
    primaryType: "ClobAuth",
    message: { address: account.address, timestamp: ts, nonce: 0n, message: "This message attests that I control the given wallet" } });
  const headers = { POLY_ADDRESS: account.address, POLY_SIGNATURE: sig, POLY_TIMESTAMP: ts, POLY_NONCE: "0" };
  const essais = [];
  for (const [methode, chemin] of [["GET", "/auth/derive-api-key"], ["POST", "/auth/api-key"]]) {
    const r = await fetch(HOTE + chemin, { method: methode, headers }); const txt = await r.text(); essais.push(methode + " " + r.status + " " + txt.slice(0, 120));
    let d = null; try { d = JSON.parse(txt); } catch (_) {}
    if (r.ok && d && (d.apiKey || d.key)) return { apiKey: d.apiKey || d.key, secret: d.secret, passphrase: d.passphrase, adresse: account.address };
  }
  throw new Error(essais.join(" | "));
}
