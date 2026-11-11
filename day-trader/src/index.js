// Day Trader — mise en app des outils day-trader-skill (Jakeschincariol, licence MIT), sans courtier.
// Actions US + BTC. Rien ici ne passe d'ordre : l'app lit des données publiques et fait des calculs.
import { univers } from "./donnees.js";
import { scanJour, scanOrb } from "./scanner.js";
import { parcours, REGLAGES_DEFAUT } from "./trade.js";
import { nouvelles, analyste, congres, verifierAlertes } from "./infos.js";
import { local, MARCHES, seance, hhmm } from "./temps.js";
import { schema, demarrer, lotSuivant, classement, lireEtat, ecrireEtat } from "./test.js";
import { tourPapier, resume, tradesPapier } from "./papier.js";
import { suiviNews, statsNews, photosJetons, ITEMS, SEUILS } from "./veille.js";
import { REGLES, BASES, FILTRES } from "./regles.js";
import { REGLES_J, BASES_J, FILTRES_J } from "./labo.js";
export { Veilleur } from "./veille.js";
export { Flux } from "./flux.js";
export { Jetons } from "./jetons.js";
import { statsJetons, verifierJetons } from "./jetons.js";
import { enregistrerFigures, tourSuivi, lireSuivi } from "./suivi.js";
import { statsFlux, statsEclair } from "./flux.js";
import { classementCombos, CONDITIONS, NB_REGLES } from "./combos.js";
import { tourPapierJour, resumePJ } from "./pj.js";
import { classeurXlsx } from "./xlsx.js";
import { demarrerPA, lotPA, lirePA, classementCap } from "./paraction.js";
import { nomRegle } from "./combos.js";
import { tourOrigine, statsOrigine } from "./origine.js";

async function fichierExcel(env) {
  await base(env);
  const db = env.DB; const e = await lireEtat(db, "test");
  const cl = await classement(db, 1000);
  const rg = await (async () => { const n = {}; for (const r of [...REGLES, ...REGLES_J]) n[r.id] = { nom: `${r.base.nom} ${r.filtre.nom}`, camp: r.filtre.camp, famille: r.famille }; return n; })();
  const pj = await resumePJ(db); const pi = await resume(db);
  const cc = await classementCap(db, true);
  const ligneC = (r, i) => [i + 1, r.regle, r.nom, r.A.trades, r.A.gagnants, r.A.gain, r.B.trades, r.B.gagnants, r.B.gain, r.A.gain + r.B.gain, r.batQqq ? "OUI" : "non", r.batGarder ? "OUI" : "non", r.tient ? "OUI" : "non"];
  const enteteC = ["Rang", "Code", "Description", "A trades", "A % gagnants", "A gain $", "B trades", "B % gagnants", "B gain $", "Total $", "Bat le QQQ (A et B)", "Bat garder les actions (A et B)", "Tient"];
  const bc = cc.bench;
  const pa = await lirePA(db);
  const feuilles = [
    ["Par action", [["Action", "Groupe", "Meilleure stratégie (code)", "Description", "Gagne sur A et B", "Stratégie $", "Garder l'action $", "Garder le QQQ $", "Verdict", "A trades", "A gain $", "B trades", "B gain $", "Garder l'action A $", "Garder l'action B $", "QQQ A $", "QQQ B $", "Du", "Coupure A/B", "Au", "Stratégies comparées"],
      ...pa.lignes.map((x) => [x.sym, x.groupe, x.regle || "", x.nom || "", x.tient ? "OUI" : "non", x.strat ?? "", x.garder ?? "", x.qqq ?? "", x.mieux == null ? "" : x.mieux > 0 ? "stratégie meilleure" : "garder était mieux", x.an, x.ga ?? "", x.bn, x.gb ?? "", x.garder_a ?? "", x.garder_b ?? "", x.qqq_a ?? "", x.qqq_b ?? "", x.du || "", x.coupure || "", x.au || "", x.candidats])]],
    ["Meilleures stratégies", [[`Capital égal : 1 000 $ par action (${bc.actions} actions = ${bc.capital} $), une position à la fois. Référence : garder les actions A ${bc.garderA} $ / B ${bc.garderB} $ ; garder le QQQ A ${bc.qqqA} $ / B ${bc.qqqB} $.`], enteteC, ...cc.regles.filter((r) => r.tient).map(ligneC)]],
    ["Toutes combinaisons", [enteteC, ...cc.regles.map(ligneC)]],
    ["Leurs règles + nos filtres", [["Code", "Famille", "Camp du filtre", "Description", "A trades", "A % gagnants", "A gain $", "B trades", "B % gagnants", "B gain $", "Creux $", "Tient"],
      ...cl.regles.sort((a, b) => (b.tient - a.tient) || (((b.B || {}).gain ?? -1e9) - ((a.B || {}).gain ?? -1e9))).map((x) => [x.regle, (rg[x.regle] || {}).famille || "", (rg[x.regle] || {}).camp || "", (rg[x.regle] || {}).nom || "", x.A?.trades ?? "", x.A?.gagnants ?? "", x.A?.gain ?? "", x.B?.trades ?? "", x.B?.gagnants ?? "", x.B?.gain ?? "", x.creuxTotal, x.tient ? "OUI" : "non"])]],
    ["Paper journalier", [["Combinaison", "Description", "Signaux", "Fermés", "Ouverts", "Gagnants", "Gain $", "vs QQQ $"], ...pj.parRegle.map((x) => [x.regle, nomRegle(x.regle), x.signaux, x.fermes, x.ouverts, x.gagnants, x.gain, x.contreQqq])]],
    ["Paper intraday", [["Règle", "Description", "Trades", "Gagnants", "Ouverts", "Gain $", "Gain du jour $", "Creux $"], ...pi.regles.map((x) => [x.regle, (rg[x.regle] || {}).nom || x.regle, x.trades, x.gagnants, x.ouverts, x.gain, x.gainJour, x.creux])]],
    ["Lisez-moi", [["Rubrique", "Explication"],
      ["Créé le", new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC"],
      ["Actions testées", e ? `${e.liste.length} : 25 plus grosses (${(e.grosses || []).join(", ")}) + 75 plus volatiles` : ""],
      ["Périodes (journalier)", e ? `A = du ${e.premiereJ} au ${e.coupureJ} ; B = du ${e.coupureJ} au ${e.derniereJ}` : ""],
      ["Périodes (intraday)", e ? `A = du ${e.premiere} au ${e.coupure} ; B = du ${e.coupure} au ${e.derniere}` : ""],
      ["Capital égal", "Par action et par stratégie : 1 000 $, une seule position à la fois (un signal est ignoré tant qu'on est investi). Comparé à 1 000 $ achetés et gardés dans l'action, et 1 000 $ gardés dans le QQQ, même période. Achat à l'ouverture du lendemain + 0,05 % de glissement, stop 2 × ATR."],
      ["Tient (Par action)", "Au moins 3 trades sur A et sur B, gagne sur A et sur B."],
      ["Tient (Meilleures stratégies)", "Au moins 30 trades sur A et B, gagne sur A et B, et gagne plus que garder le QQQ avec le même capital sur A et sur B."],
      ["Feuille Leurs règles", "Ancienne mesure (1 000 $ par trade, positions qui se chevauchent) : sert seulement à comparer leurs idées entre elles, pas à les comparer au QQQ."],
      ["Attention", "Avec près de 2 000 combinaisons testées, certaines passent par hasard. Ce sont des simulations sur le passé, pas des exécutions réelles : seul le paper sur des jours nouveaux départage."]]],
  ];
  const nom = `meilleures-strategies-${new Date().toISOString().slice(0, 10)}.xlsx`;
  return new Response(classeurXlsx(feuilles), { headers: { "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Content-Disposition": `attachment; filename="${nom}"`, "Cache-Control": "no-store" } });
}

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
  const r = await scanJour(u.symboles, Date.now());
  const doc = { le: new Date().toISOString(), duree: Math.round((Date.now() - debut) / 1000), hits: r.hits, comptes: r.comptes };
  await c.put("scanJour", doc); await c.put("liquides", r.liquides);
  try { await enregistrerFigures(env.DB, r.hits); } catch (e) {}
  return doc;
}
async function lancerOrb(env, q = {}) {
  const c = coffre(env);
  let u = await c.get("univers");
  if (!u) { const liste = await univers(); u = { le: Date.now(), symboles: liste.map((x) => x[0]) }; await c.put("univers", u); }
  const syms = q.symbols ? q.symbols : u.symboles;
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
      if (p === "/excel") return await fichierExcel(env);
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
      if (p.startsWith("/api/test") || p.startsWith("/api/combos") || p.startsWith("/api/papier") || p.startsWith("/api/news") || p === "/api/regles") await base(env);
      if (p === "/api/regles") return json({ bases: BASES, filtres: FILTRES, regles: [...REGLES, ...REGLES_J].map((r) => ({ id: r.id, base: r.base.nom, filtre: r.filtre.nom, camp: r.filtre.camp, famille: r.famille })), news: [...SEUILS.map((x) => ({ id: "news-" + x, nom: `Toutes les news : hausse de ${x} % dans les 30 min, stop sous le prix de la nouvelle, cible 2R` })), { id: "news-choisies", nom: "News choisies (types qui font monter) : hausse de 1 % dans les 30 min, stop sous le prix de la nouvelle, cible 2R" }] });
      if (p === "/api/test/demarrer" && req.method === "POST") { const l = (await c.get("liquides")) || []; if (!l.length) return json({ erreur: "Lance d'abord le scan du jour (il donne la liste des actions liquides)." }, 400); return json(await demarrer(env, l)); }
      if (p === "/api/par-action") return json(await lirePA(env.DB));
      if (p === "/api/combos") return json({ ...(await classementCap(env.DB)), conditions: CONDITIONS, nbRegles: NB_REGLES, etat: await lireEtat(env.DB, "paraction") });
      if (p === "/api/papier-j") return json(await resumePJ(env.DB, +(u.searchParams.get("mise") || 1000)));
      if (p === "/api/papier-j/tour" && req.method === "POST") return json(await tourPapierJour(env));
      if (p === "/api/test") return json(await classement(env.DB, +(u.searchParams.get("mise") || 1000)));
      if (p === "/api/papier") return json(await resume(env.DB, { mise: +(u.searchParams.get("mise") || 1000), depuis: u.searchParams.get("depuis") || "" }));
      if (p === "/api/papier/trades") return json(await tradesPapier(env.DB, { regle: u.searchParams.get("regle") || "", date: u.searchParams.get("date") || "" }, +(u.searchParams.get("mise") || 1000)));
      if (p === "/api/news") { const st = await statsNews(env.DB); const ve = await (await veilleur(env).fetch("https://v/etat")).json(); return json({ ...st, origine: await statsOrigine(env.DB), veilleur: ve, items: ITEMS }); }
      if (p === "/api/figures-suivi") return json(await lireSuivi(env.DB));
      if (p === "/api/jetons") return json({ ...(await statsJetons(env.DB)), etat: await (await env.JETONS.get(env.JETONS.idFromName("jetons-v2")).fetch("https://j/etat")).json() });
      if (p === "/api/eclair") return json(await statsEclair(env.DB));
      if (p === "/api/flux") return json({ ...(await statsFlux(env.DB)), etat: await (await env.FLUX.get(env.FLUX.idFromName("alpaca")).fetch("https://f/etat")).json() });
      if (p === "/api/origine/tour") return json(await tourOrigine(env));
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
    if (ev.cron === "25 21 * * 1-5") { await base(env); try { const r = await tourPapierJour(env); await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("dernier-papier-j", JSON.stringify({ quand: new Date().toISOString(), r })).run(); } catch (e) { await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("erreur-papier-j", JSON.stringify({ quand: new Date().toISOString(), e: String(e.message || e) })).run(); } return; }
    await base(env);
    const journal = async (cle, f) => { try { const r = await f(); await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("dernier-" + cle, JSON.stringify({ quand: new Date().toISOString(), r })).run(); } catch (e) { await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?, ?)").bind("erreur-" + cle, JSON.stringify({ quand: new Date().toISOString(), e: String(e.message || e) })).run(); } };
    // 1. veilleur des nouvelles toujours armé
    await journal("veilleur", async () => { await veilleur(env).fetch("https://v/demarrer"); return (await veilleur(env).fetch("https://v/etat")).json(); });
    await journal("jetons", async () => { const r = await (await env.JETONS.get(env.JETONS.idFromName("jetons-v2")).fetch("https://j/demarrer")).json(); return { hl: r.hl, kf: r.kf, jetons: r.jetons, ouverts: r.ouverts, erreurs: Object.fromEntries(Object.entries(r.derniers || {}).filter(([k]) => k.startsWith("erreur"))), exemple: Object.entries(r.derniers || {}).slice(0, 5) }; });
    { const mn = new Date(ev.scheduledTime).getUTCMinutes(); if (mn % 30 === 2 || !(await lireEtat(env.DB, "jetons_actions"))) await journal("jetons_actions", async () => { const r = await verifierJetons(env); await ecrireEtat(env.DB, "jetons_actions", { le: new Date().toISOString(), ...r }); return r; }); }
    { const mn = new Date(ev.scheduledTime).getUTCMinutes(); if (mn % 5 === 3) await journal("suivi", async () => { const sj = await coffre(env).get("scanJour"); if (sj && sj.hits) await enregistrerFigures(env.DB, sj.hits); return tourSuivi(env); }); }
    await journal("flux", async () => (await env.FLUX.get(env.FLUX.idFromName("alpaca")).fetch("https://f/demarrer")).json());
    // 2. alertes de prix
    await journal("alertes", async () => {
      const al = (await c.get("alertes")) || []; if (!al.length) return 0;
      const son = await verifierAlertes(al); await c.put("alertes", al);
      if (son.length) { const h = (await c.get("sonneries")) || []; await c.put("sonneries", [...son, ...h].slice(0, 200)); }
      return son.length;
    });
    // 3. suivi des nouvelles
    await journal("news", () => suiviNews(env));
    await journal("jetons", () => photosJetons(env));
    await journal("origine", () => tourOrigine(env, ev.scheduledTime));
    // 4. paper toutes les 5 minutes (une minute après la clôture de chaque barre)
    const min = new Date(ev.scheduledTime).getUTCMinutes();
    if (min % 5 === 1) await journal("papier", async () => {
      const e = await lireEtat(env.DB, "test"); const sj = (await c.get("scanJour")) || { hits: [] };
      const univ = e && e.liste ? e.liste : ((await c.get("liquides")) || []).slice(0, PAPIER_TAILLE);
      return tourPapier(env, univ, new Set(sj.hits.map((h) => h.symbol)), ev.scheduledTime, new Set((e && e.grosses) || []));
    });
    // 5. banc d'essai : démarre tout seul la première fois, puis un lot de 40 actions par minute
    else await journal("test", async () => {
      const e = await lireEtat(env.DB, "test");
      if (!e) { const l = (await c.get("liquides")) || []; if (!l.length) return "pas de liste"; const d = await demarrer(env, l); return { demarre: d.liste.length }; }
      if (e.fini) { const pa = await lireEtat(env.DB, "paraction"); if (!pa) return demarrerPA(env).then((x) => ({ paraction: "démarré" })); if (!pa.fini) return lotPA(env, 10); return "fini"; }
      const r = await lotSuivant(env, 12); return { pos: r.pos, total: r.liste.length };
    });
  },
};
