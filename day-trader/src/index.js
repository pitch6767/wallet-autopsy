// Day Trader — mise en app des outils day-trader-skill (Jakeschincariol, licence MIT), sans courtier.
// Actions US + BTC. Rien ici ne passe d'ordre : l'app lit des données publiques et fait des calculs.
import { univers } from "./donnees.js";
import { scanJour, scanOrb } from "./scanner.js";
import { parcours, REGLAGES_DEFAUT } from "./trade.js";
import { nouvelles, analyste, congres, verifierAlertes } from "./infos.js";
import { local, MARCHES, seance, hhmm } from "./temps.js";
import { schema, demarrer, lotSuivant, classement, lireEtat } from "./test.js";
import { tourPapier, resume, tradesPapier } from "./papier.js";
import { suiviNews, statsNews, ITEMS, SEUILS } from "./veille.js";
import { REGLES, BASES, FILTRES } from "./regles.js";
export { Veilleur } from "./veille.js";

const PAPIER_TAILLE = 150; // actions les plus échangées suivies en paper (+ BTC)
let SCHEMA_OK = false;
async function base(env) { if (!SCHEMA_OK) { await schema(env.DB); SCHEMA_OK = true; } }
function veilleur(env) { return env.VEILLEUR.get(env.VEILLEUR.idFromName("8k")); }

export class Coffre {
  constructor(state) { this.s = state.storage; }
  async fetch(req) {
    const { op, cle, valeur } = await req.json();
    if (op === "get") return Response.json({ valeur: (await this.s.get(cle)) ?? null });
    if (op === "put") { await this.s.put(cle, valeur); return Response.json({ ok: true }); }
    return Response.json({ erreur: "op inconnue" }, { status: 400 });
  }
}
function coffre(env) {
  const st = env.COFFRE.get(env.COFFRE.idFromName("principal"));
  const appel = async (corps) => (await st.fetch("https://coffre/", { method: "POST", body: JSON.stringify(corps) })).json();
  return { get: async (cle) => (await appel({ op: "get", cle })).valeur, put: (cle, valeur) => appel({ op: "put", cle, valeur }) };
}
let ENV = null;
async function reglages(c) {
  const r = { ...REGLAGES_DEFAUT, ...((await c.get("reglages")) || {}) };
  if (!r.sec_user_agent && ENV && ENV.DB) {
    try { const l = await ENV.DB.prepare("SELECT valeur FROM config WHERE cle = 'contact_sec'").first(); if (l) r.sec_user_agent = l.valeur; } catch (e) {}
  }
  return r;
}

async function lancerScanJour(env) {
  const c = coffre(env);
  let u = await c.get("univers");
  if (!u || Date.now() - u.le > 7 * 864e5) { const liste = await univers(); u = { le: Date.now(), symboles: liste.map((x) => x[0]) }; await c.put("univers", u); }
  const debut = Date.now();
  const r = await scanJour([...u.symboles, "BTC"], Date.now());
  const doc = { le: new Date().toISOString(), duree: Math.round((Date.now() - debut) / 1000), hits: r.hits, comptes: r.comptes };
  await c.put("scanJour", doc); await c.put("liquides", r.liquides);
  return doc;
}
async function lancerOrb(env, q = {}) {
  const c = coffre(env);
  let u = await c.get("univers");
  if (!u) { const liste = await univers(); u = { le: Date.now(), symboles: liste.map((x) => x[0]) }; await c.put("univers", u); }
  const syms = q.symbols ? q.symbols : [...u.symboles, "BTC"];
  const debut = Date.now();
  const r = await scanOrb(syms, Date.now(), { minutesRange: +(q.minutesRange || 15) });
  const doc = { le: new Date().toISOString(), duree: Math.round((Date.now() - debut) / 1000), ...r };
  await c.put("orb", doc);
  return doc;
}

function horloge() {
  const now = Date.now(); const l = local(now, MARCHES.actions); const se = seance(l.date, MARCHES.actions);
  let etat = "fermée"; if (se && l.min >= se[0] && l.min < se[1]) etat = "ouverte"; else if (se && l.min < se[0]) etat = "pas encore ouverte";
  return { newYork: `${l.date} ${hhmm(l.min)}`, bourse: etat, seance: se ? `${hhmm(se[0])}–${hhmm(se[1])}` : null, utc: new Date(now).toISOString().slice(0, 16).replace("T", " ") };
}

const json = (x, code = 200) => Response.json(x, { status: code, headers: { "Cache-Control": "no-store" } });

export default {
  async fetch(req, env, ctx) {
    ENV = env;
    const u = new URL(req.url); const p = u.pathname; const c = coffre(env);
    try {
      if (!p.startsWith("/api/")) return env.ASSETS.fetch(req);
      const corps = req.method === "POST" ? await req.json().catch(() => ({})) : {};
      if (p === "/api/etat") {
        const [r, sj, orb, al] = await Promise.all([reglages(c), c.get("scanJour"), c.get("orb"), c.get("alertes")]);
        await base(env); const taches = (await env.DB.prepare("SELECT cle, valeur FROM etat WHERE cle LIKE 'dernier-%' OR cle LIKE 'erreur-%'").all()).results;
        return json({ horloge: horloge(), reglages: r, scanJour: sj && { le: sj.le, trouves: sj.hits.length }, orb: orb && { le: orb.le, trouves: orb.hits.length }, alertes: al || [], taches: Object.fromEntries(taches.map((t) => [t.cle, JSON.parse(t.valeur)])) });
      }
      if (p === "/api/reglages" && req.method === "POST") {
        const r = { ...(await reglages(c)) };
        for (const [k, v] of Object.entries(corps)) if (k in REGLAGES_DEFAUT || k === "sec_user_agent") r[k] = v;
        await c.put("reglages", r); return json(r);
      }
      if (p === "/api/scan-jour") return json(req.method === "POST" ? await lancerScanJour(env) : (await c.get("scanJour")) || { hits: [], vide: true });
      if (p === "/api/orb") return json(req.method === "POST" ? await lancerOrb(env, corps) : (await c.get("orb")) || { hits: [], vide: true });
      if (p === "/api/trade" && req.method === "POST") return json(await parcours(corps, await reglages(c), (await c.get("journal")) || []));
      if (p === "/api/nouvelles") {
        const syms = (u.searchParams.get("symbols") || "").toUpperCase().split(/[\s,]+/).filter(Boolean);
        return json(await nouvelles(syms, +(u.searchParams.get("heures") || 24), (await reglages(c)).sec_user_agent || ""));
      }
      if (p === "/api/analyste") return json(await analyste(u.searchParams.get("symbol") || "", (await reglages(c)).sec_user_agent || "", +(u.searchParams.get("trimestres") || 6)));
      if (p === "/api/congres") return json(await congres({ annee: +(u.searchParams.get("annee") || new Date().getUTCFullYear()), membre: u.searchParams.get("membre") || "", depuis: u.searchParams.get("depuis") || "" }));
      if (p === "/api/alertes") {
        let al = (await c.get("alertes")) || [];
        if (req.method === "POST") {
          const nouvelles = Array.isArray(corps.alertes) ? corps.alertes : [corps];
          for (const a of nouvelles) { if (!a.type) continue; al.push({ ...a, symbol: a.symbol ? String(a.symbol).toUpperCase() : undefined, id: crypto.randomUUID().slice(0, 8), creeLe: new Date().toISOString() }); }
          await c.put("alertes", al);
        }
        if (req.method === "DELETE") { const id = u.searchParams.get("id"); al = id === "toutes" ? [] : al.filter((a) => a.id !== id); await c.put("alertes", al); }
        if (req.method === "PATCH") { const id = u.searchParams.get("id"); al = al.map((a) => (a.id === id ? { ...a, sonneeLe: null, texte: null, jourSonne: null } : a)); await c.put("alertes", al); }
        return json(al);
      }
      if (p === "/api/journal") {
        let j = (await c.get("journal")) || [];
        if (req.method === "POST") { j.push({ ...corps, date: corps.date || local(Date.now(), MARCHES.actions).date, le: new Date().toISOString() }); j = j.slice(-500); await c.put("journal", j); }
        if (req.method === "DELETE") { const le = u.searchParams.get("le"); j = j.filter((x) => x.le !== le); await c.put("journal", j); }
        return json(j);
      }
      if (p.startsWith("/api/test") || p.startsWith("/api/papier") || p.startsWith("/api/news") || p === "/api/regles") await base(env);
      if (p === "/api/regles") return json({ bases: BASES, filtres: FILTRES, regles: REGLES.map((r) => ({ id: r.id, base: r.base.nom, filtre: r.filtre.nom, camp: r.filtre.camp })), news: SEUILS.map((x) => ({ id: "news-" + x, nom: `8-K puis hausse de ${x} % dans les 30 min, stop sous le prix de la nouvelle, cible 2R` })) });
      if (p === "/api/test/demarrer" && req.method === "POST") { const l = (await c.get("liquides")) || []; if (!l.length) return json({ erreur: "Lance d'abord le scan du jour (il donne la liste des actions liquides)." }, 400); return json(await demarrer(env, [...l, "BTC"])); }
      if (p === "/api/test") return json(await classement(env.DB, +(u.searchParams.get("mise") || 1000)));
      if (p === "/api/papier") return json(await resume(env.DB, { mise: +(u.searchParams.get("mise") || 1000), depuis: u.searchParams.get("depuis") || "" }));
      if (p === "/api/papier/trades") return json(await tradesPapier(env.DB, { regle: u.searchParams.get("regle") || "", date: u.searchParams.get("date") || "" }, +(u.searchParams.get("mise") || 1000)));
      if (p === "/api/news") { const st = await statsNews(env.DB); const ve = await (await veilleur(env).fetch("https://v/etat")).json(); return json({ ...st, veilleur: ve, items: ITEMS }); }
      if (p === "/api/sonde2") {
        const essai = async (nom, url, opt = {}) => { const t = Date.now(); try { const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0 (compatible; day-trader-app)" }, ...opt }); const x = await r.text(); return { nom, code: r.status, ms: Date.now() - t, debut: x.slice(0, 700) }; } catch (e) { return { nom, err: String(e) }; } };
        const post = (b) => ({ method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(b) });
        return json(await Promise.all([
          essai("globenewswire", "https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies"),
          essai("prnewswire", "https://www.prnewswire.com/rss/news-releases-list.rss"),
          essai("businesswire", "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeEFpRWQ=="),
          essai("accesswire", "https://www.accessnewswire.com/newsroom/api/rss"),
          essai("hyperliquid-xyz", "https://api.hyperliquid.xyz/info", post({ type: "allMids", dex: "xyz" })),
          essai("hyperliquid-dexs", "https://api.hyperliquid.xyz/info", post({ type: "perpDexs" })),
          (async () => { const r = await (await fetch("https://api.kraken.com/0/public/AssetPairs")).json(); const k = Object.entries(r.result || {}).filter(([n, v]) => /NVDA|TSLA|AAPL/i.test(n + (v.wsname || ""))).map(([n, v]) => n + "=" + v.wsname); return { nom: "kraken-spot-x", code: 200, debut: JSON.stringify(k).slice(0, 600) }; })(),
          (async () => { const r = await (await fetch("https://futures.kraken.com/derivatives/api/v3/tickers")).json(); const k = (r.tickers || []).filter((t) => /NVDA|TSLA|AAPL|SPY|QQQ/i.test(t.symbol + (t.pair || ""))).map((t) => t.symbol + "=" + t.pair + "@" + t.markPrice); return { nom: "kraken-fut-x", code: 200, debut: JSON.stringify(k).slice(0, 600) }; })(),
          essai("globe2", "https://www.globenewswire.com/rss/list"),
          essai("newsfile", "https://feeds.newsfilecorp.com/feed/newsfile_ca.xml"),
        ]));
      }
      if (p === "/api/sonde") return json({ ok: true, horloge: horloge() });
      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e && e.message || e) }, 500);
    }
  },
  async scheduled(ev, env, ctx) {
    ENV = env;
    const c = coffre(env);
    if (ev.cron === "17 13 * * 1-5") { ctx.waitUntil(lancerScanJour(env).catch(() => {})); return; }
    await base(env);
    const journal = async (cle, f) => { try { const r = await f(); await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("dernier-" + cle, JSON.stringify({ quand: new Date().toISOString(), r })).run(); } catch (e) { await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("erreur-" + cle, JSON.stringify({ quand: new Date().toISOString(), e: String(e.message || e) })).run(); } };
    // 1. veilleur des nouvelles toujours armé
    await journal("veilleur", async () => (await veilleur(env).fetch("https://v/demarrer")).json());
    // 2. alertes de prix
    await journal("alertes", async () => {
      const al = (await c.get("alertes")) || []; if (!al.length) return 0;
      const son = await verifierAlertes(al); await c.put("alertes", al);
      if (son.length) { const h = (await c.get("sonneries")) || []; await c.put("sonneries", [...son, ...h].slice(0, 200)); }
      return son.length;
    });
    // 3. suivi des nouvelles
    await journal("news", () => suiviNews(env));
    // 4. paper toutes les 5 minutes (une minute après la clôture de chaque barre)
    const min = new Date(ev.scheduledTime).getUTCMinutes();
    if (min % 5 === 1) await journal("papier", async () => {
      const liq = (await c.get("liquides")) || []; const sj = (await c.get("scanJour")) || { hits: [] };
      return tourPapier(env, liq.slice(0, PAPIER_TAILLE), new Set(sj.hits.map((h) => h.symbol)), ev.scheduledTime);
    });
    // 5. banc d'essai : démarre tout seul la première fois, puis un lot de 40 actions par minute
    else await journal("test", async () => {
      const e = await lireEtat(env.DB, "test");
      if (!e) { const l = (await c.get("liquides")) || []; if (!l.length) return "pas de liste"; const d = await demarrer(env, [...l, "BTC"]); return { demarre: d.liste.length }; }
      if (e.fini) return "fini";
      const r = await lotSuivant(env, 40); return { pos: r.pos, total: r.liste.length };
    });
  },
};
