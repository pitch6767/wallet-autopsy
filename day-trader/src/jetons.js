// Pitch 11.11 : « on limite aux actions tokenisées ». Prix EN DIRECT et gratuits, 24 h/24 :
// Hyperliquid (marchés « xyz ») et Kraken (perpétuels xStocks). Dès qu'un jeton saute de 0,5 % ou 1 %
// en 5, 15 ou 30 s, achat papier (1 000 $) ; les 9 façons de vendre sont testées sur l'heure qui suit.
// On rattache ensuite la news éventuelle (SEC, agences, flux) vue sur la même action.
import { calculerSorties } from "./flux.js";
import { univers, sparkTout } from "./donnees.js";

const G = 0.001; // 0,1 % payé à l'entrée et à la sortie (écart + frais estimés sur ces marchés)
export const NOM_JETONS = "jetons-v2";
export const FENETRES = [5, 15, 30];
export const SEUILS_J = [0.5, 1];
export const SCHEMA_JETONS = "CREATE TABLE IF NOT EXISTS jeton_trades (cle TEXT PRIMARY KEY, sym TEXT, place TEXT, fenetre INTEGER, seuil REAL, t INTEGER, base REAL, entree REAL, news TEXT, sorties TEXT, statut TEXT)";
const HL_WS = "https://api.hyperliquid.xyz/ws";
const KF_WS = "https://futures.kraken.com/ws/v1";

export class Jetons {
  constructor(state, env) {
    this.state = state; this.env = env; this.s = state.storage;
    this.ws = {}; this.hist = new Map(); this.positions = new Map(); this.derniers = {}; this.actions = null;
    // reprise après redémarrage : positions ouvertes et liste des vraies actions gardées en mémoire durable
    state.blockConcurrencyWhile(async () => {
      const l = (await this.s.get("actions")) || null; this.actions = l ? new Set(l) : null;
      for (const [k, v] of await this.s.list({ prefix: "pos:" })) this.positions.set(k.slice(4), v);
    });
  }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/demarrer") { await this.connecter(); if (!(await this.s.getAlarm())) await this.s.setAlarm(Date.now() + 30e3); return Response.json(this.etat()); }
    if (u.pathname === "/etat") return Response.json(this.etat());
    if (u.pathname === "/actions") { const l = await req.json(); this.actions = new Set(l); await this.s.put("actions", l); return Response.json({ ok: l.length }); }
    return new Response("?", { status: 404 });
  }
  etat() { return { hl: !!this.ws.hl, kf: !!this.ws.kf, jetons: this.hist.size, actions: this.actions ? this.actions.size : null, ouverts: this.positions.size, derniers: this.derniers }; }
  async alarm() {
    // l'ancienne instance (nom « jetons », sans filtre) s'arrête d'elle-même
    if (this.state.id.toString() !== this.env.JETONS.idFromName(NOM_JETONS).toString()) { for (const w of Object.values(this.ws)) try { w && w.close(); } catch (e) {} this.ws = {}; await this.s.deleteAll(); return; }
    try { await this.connecter(); } catch (e) {}
    // sauvegarde des positions (avec leur parcours de prix) et fermeture de celles qui ont 1 heure
    const t = Date.now();
    for (const [id, pos] of [...this.positions]) {
      if (t - pos.t >= 60 * 60e3) { try { await this.fermer(id); } catch (e) {} }
      else await this.s.put("pos:" + id, pos);
    }
    await this.s.setAlarm(Date.now() + 30e3);
  }
  async connecter() {
    await this.env.DB.prepare(SCHEMA_JETONS).run();
    if (!this.ws.hl) await this.ouvrir("hl", HL_WS, (ws) => ws.send(JSON.stringify({ method: "subscribe", subscription: { type: "allMids", dex: "xyz" } })), (j) => {
      const m = j && j.channel === "allMids" && j.data && j.data.mids; if (!m) return;
      const t = Date.now(); for (const [k, v] of Object.entries(m)) if (k.startsWith("xyz:")) this.prix("hl", k.slice(4), +v, t);
    });
    if (!this.ws.kf) {
      const ids = await this.produitsKraken();
      if (ids.length) await this.ouvrir("kf", KF_WS, (ws) => ws.send(JSON.stringify({ event: "subscribe", feed: "ticker_lite", product_ids: ids })), (j) => {
        if (!j || j.feed !== "ticker_lite" || !j.product_id) return; const m = /^PF_([A-Z]+)XUSD$/.exec(j.product_id); const p = j.bid && j.ask ? (+j.bid + +j.ask) / 2 : +(j.markPrice || j.last || 0);
        if (m && p) this.prix("kf", m[1], p, Date.now());
      });
    }
  }
  async produitsKraken() {
    try { const j = await (await fetch("https://futures.kraken.com/derivatives/api/v3/tickers")).json(); return (j.tickers || []).map((t) => t.symbol).filter((s) => /^PF_[A-Z]+XUSD$/.test(s || "")); } catch (e) { return []; }
  }
  async ouvrir(nom, url, apres, surMessage) {
    const r = await fetch(url, { headers: { Upgrade: "websocket" } }); const ws = r.webSocket; if (!ws) { this.derniers["erreur_" + nom] = "HTTP " + r.status; return; }
    ws.accept(); this.ws[nom] = ws; apres(ws);
    ws.addEventListener("message", (ev) => { let j; try { j = JSON.parse(ev.data); } catch (e) { return; } try { surMessage(j); } catch (e) {} });
    const fin = () => { this.ws[nom] = null; };
    ws.addEventListener("close", fin); ws.addEventListener("error", fin);
    if (nom === "hl") { const ping = setInterval(() => { if (this.ws.hl !== ws) return clearInterval(ping); try { ws.send(JSON.stringify({ method: "ping" })); } catch (e) {} }, 30e3); }
  }
  // Chaque prix : historique des 60 dernières secondes, détection des sauts, suivi des positions ouvertes
  prix(place, sym, p, t) {
    const k = place + ":" + sym; this.derniers[k] = p;
    let h = this.hist.get(k); if (!h) { h = []; this.hist.set(k, h); }
    if (h.length && h[h.length - 1][1] === p) { h[h.length - 1][0] = t; } else h.push([t, p]);
    while (h.length && h[0][0] < t - 60e3) h.shift();
    for (const pos of this.positions.values()) if (pos.k === k) { const d = pos.tr; if (!d.length || d[d.length - 1][1] !== p) d.push([t, p]); }
    if (!this.actions || !this.actions.has(k)) return; // Pitch 11.11 : seulement les vraies actions cotées tokenisées
    for (const w of FENETRES) {
      let mini = Infinity; for (const [ms, q] of h) if (ms >= t - w * 1000 && q < mini) mini = q;
      if (!isFinite(mini)) continue;
      for (const s of SEUILS_J) {
        if (p < mini * (1 + s / 100)) continue;
        const cle = `${k}|${w}|${s}`; if ([...this.positions.values()].some((x) => x.id === cle)) continue;
        const pos = { id: cle, k, place, sym, w, s, t, base: mini, entree: p * (1 + G), tr: [] }; const id = `${cle}|${t}`;
        this.positions.set(id, pos);
        this.state.waitUntil(this.ouvrirTrade(id, pos));
      }
    }
  }
  async ouvrirTrade(id, pos) {
    const db = this.env.DB; let news = null;
    try {
      const n = await db.prepare("SELECT source, titre, vu FROM news WHERE sym = ? AND vu BETWEEN ? AND ? ORDER BY vu DESC LIMIT 1").bind(pos.sym, pos.t - 30 * 60e3, pos.t + 60e3).first();
      if (n) news = `${n.source} · ${n.titre || ""}`.slice(0, 300);
      else { const f = await db.prepare("SELECT source, titre FROM eclair_vue WHERE sym = ? AND recu BETWEEN ? AND ? ORDER BY recu DESC LIMIT 1").bind(pos.sym, pos.t - 30 * 60e3, pos.t + 60e3).first(); if (f) news = `${f.source} · ${f.titre || ""}`.slice(0, 300); }
    } catch (e) {}
    pos.news = news;
    await db.prepare("INSERT OR IGNORE INTO jeton_trades (cle, sym, place, fenetre, seuil, t, base, entree, news, statut) VALUES (?,?,?,?,?,?,?,?,?,?)").bind(id, pos.sym, pos.place, pos.w, pos.s, pos.t, pos.base, pos.entree, news, "ouvert").run();
  }
  async fermer(id) {
    const pos = this.positions.get(id); if (!pos) return; this.positions.delete(id); await this.s.delete("pos:" + id);
    const so = calculerSorties(pos.tr.map(([ms, p]) => [ms, p * (1 - G) / (1 - 0.0005)]), pos.entree, pos.t, pos.base);
    await this.env.DB.prepare("UPDATE jeton_trades SET sorties = ?, statut = 'ferme' WHERE cle = ?").bind(JSON.stringify(so), id).run();
  }
}

export async function statsJetons(db) {
  await db.prepare(SCHEMA_JETONS).run();
  const l = (await db.prepare("SELECT * FROM jeton_trades ORDER BY t DESC LIMIT 3000").all()).results;
  const res = {};
  for (const x of l) {
    if (!x.sorties) continue; const avecNews = x.news ? "avec news" : "sans news";
    for (const [v, r] of Object.entries(JSON.parse(x.sorties))) {
      const k = `${x.seuil}|${x.fenetre}|${avecNews}|${v}`;
      const y = (res[k] = res[k] || { seuil: x.seuil, fenetre: x.fenetre, news: avecNews, sortie: v, trades: 0, gagnants: 0, gain: 0 });
      y.trades++; if (r.pct > 0) y.gagnants++; y.gain += r.pct * 1000;
    }
  }
  return { trades: l.length, ouverts: l.filter((x) => x.statut === "ouvert").length,
    resultats: Object.values(res).map((y) => ({ ...y, gain: Math.round(y.gain) })).sort((a, b) => b.gain - a.gain),
    derniers: l.slice(0, 40).map((x) => ({ sym: x.sym, place: x.place, fenetre: x.fenetre, seuil: x.seuil, t: x.t, news: x.news, statut: x.statut, meilleur: x.sorties ? Math.max(...Object.values(JSON.parse(x.sorties)).map((r) => r.pct)) : null })) };
}

// Liste des jetons qui sont de VRAIES actions cotées aux États-Unis : symbole présent dans la liste officielle
// de Nasdaq Trader (actions, hors ETF) ET prix du jeton à moins de 5 % du prix de l'action en bourse.
export async function verifierJetons(env) {
  const stub = env.JETONS.get(env.JETONS.idFromName(NOM_JETONS));
  const e = await (await stub.fetch("https://j/etat")).json(); const prix = e.derniers || {};
  const cotees = new Set((await univers()).map((x) => x[0]));
  const cles = Object.keys(prix).filter((k) => !k.startsWith("erreur") && cotees.has(k.split(":")[1]));
  const syms = [...new Set(cles.map((k) => k.split(":")[1]))];
  const { data } = await sparkTout(syms, "1d", "5m");
  const garde = [], ecart = [];
  for (const k of cles) {
    const c = data[k.split(":")[1]]; const cl = c && c.c ? [...c.c].reverse().find((x) => x != null) : null;
    if (cl && Math.abs(prix[k] / cl - 1) < 0.05) garde.push(k); else ecart.push(k);
  }
  await (await stub.fetch("https://j/actions", { method: "POST", body: JSON.stringify(garde) })).json();
  const exclus = Object.keys(prix).filter((k) => !k.startsWith("erreur") && !garde.includes(k));
  return { actions: garde.length, exclus: exclus.length, exemplesExclus: exclus.slice(0, 40) };
}
