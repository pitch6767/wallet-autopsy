// Day Trader — mise en app des outils day-trader-skill (Jakeschincariol, licence MIT), sans courtier.
// Actions US + BTC. Rien ici ne passe d'ordre : l'app lit des données publiques et fait des calculs.
import { univers } from "./donnees.js";
import { scanJour, scanOrb } from "./scanner.js";
import { parcours, REGLAGES_DEFAUT } from "./trade.js";
import { nouvelles, analyste, congres, verifierAlertes } from "./infos.js";
import { local, MARCHES, seance, hhmm } from "./temps.js";

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
        return json({ horloge: horloge(), reglages: r, scanJour: sj && { le: sj.le, trouves: sj.hits.length }, orb: orb && { le: orb.le, trouves: orb.hits.length }, alertes: al || [] });
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
      if (p === "/api/sonde") return json({ ok: true, horloge: horloge() });
      return json({ erreur: "inconnu" }, 404);
    } catch (e) {
      return json({ erreur: String(e && e.message || e) }, 500);
    }
  },
  async scheduled(ev, env, ctx) {
    const c = coffre(env);
    if (ev.cron === "17 13 * * 1-5") { ctx.waitUntil(lancerScanJour(env).catch(() => {})); return; }
    const al = (await c.get("alertes")) || [];
    if (!al.length) return;
    const son = await verifierAlertes(al);
    if (son.length) { await c.put("alertes", al); const h = (await c.get("sonneries")) || []; await c.put("sonneries", [...son, ...h].slice(0, 200)); }
    else await c.put("alertes", al);
  },
};
