// Données gratuites et publiques : Yahoo Finance (cours), Nasdaq Trader (liste des actions US).
// Yahoo n'est pas une API officielle : elle peut avoir du retard ou refuser des requêtes.
import { local, seance, marcheDe, symYahoo } from "./temps.js";

export const UA = "Mozilla/5.0 (compatible; day-trader-app/1.0; +https://day-trader.pitch67.workers.dev)";
const HOTES = ["https://query2.finance.yahoo.com", "https://query1.finance.yahoo.com"];

export class ErreurDonnees extends Error {}

async function texte(url, entetes = {}) {
  const r = await fetch(url, { headers: { "User-Agent": UA, Accept: "*/*", ...entetes } });
  return { code: r.status, txt: await r.text() };
}

// GET Yahoo : query2 puis query1 sur 429 / 5xx, un seul nouvel essai après une pause si 429.
export async function yahoo(chemin) {
  let dernier = "pas de réponse";
  for (const essai of [0, 1]) {
    let vu429 = false;
    for (const h of HOTES) {
      try {
        const { code, txt } = await texte(h + chemin);
        if (code === 200) return JSON.parse(txt);
        dernier = "HTTP " + code;
        if (code === 429) { vu429 = true; continue; }
        if (code >= 500) continue;
        if (txt.trim().startsWith("{")) return JSON.parse(txt);
        throw new ErreurDonnees("Yahoo a répondu " + dernier);
      } catch (e) { if (e instanceof ErreurDonnees) throw e; dernier = String(e.message || e); }
    }
    if (essai === 0 && vu429) { await new Promise((r) => setTimeout(r, 3000)); continue; }
    break;
  }
  throw new ErreurDonnees("Yahoo a répondu " + dernier);
}

export function serie(res) {
  const q = ((res.indicators || {}).quote || [{}])[0] || {};
  const t = res.timestamp || [];
  const col = (k) => (Array.isArray(q[k]) ? t.map((_, i) => (q[k][i] ?? null)) : null);
  return { t, c: col("close") || t.map(() => null), o: col("open"), h: col("high"), l: col("low"), v: col("volume"), meta: res.meta || {} };
}

export async function graphique(sym, plage, intervalle) {
  const doc = await yahoo(`/v8/finance/chart/${encodeURIComponent(symYahoo(sym))}?range=${plage}&interval=${intervalle}`);
  const res = doc && doc.chart && doc.chart.result;
  if (!res || !res.length) {
    const err = (doc && doc.chart && doc.chart.error) || {};
    throw new ErreurDonnees(`pas de données pour ${sym} : ${err.description || "symbole inconnu"}`);
  }
  return serie(res[0]);
}

// Spark : 20 symboles par requête, clôtures seulement. -> {SYM: serie}
export async function spark(symboles, plage, intervalle) {
  const voulu = Object.fromEntries(symboles.map((s) => [symYahoo(s), s]));
  const doc = await yahoo(`/v7/finance/spark?symbols=${symboles.map(symYahoo).map(encodeURIComponent).join(",")}&range=${plage}&interval=${intervalle}`);
  const sp = doc && doc.spark;
  if (!sp) throw new ErreurDonnees("réponse spark inattendue");
  const out = {};
  for (const it of sp.result || []) {
    const resp = it.response || [];
    if (!resp.length) continue;
    const ys = String(it.symbol || (resp[0].meta || {}).symbol || "").toUpperCase();
    out[voulu[ys] || ys.replace("-", ".")] = serie(resp[0]);
  }
  return out;
}

// Exécute des tâches avec au plus `n` en parallèle
export async function parLots(items, n, f) {
  const res = new Array(items.length); let k = 0;
  async function ouvrier() { while (k < items.length) { const i = k++; try { res[i] = await f(items[i], i); } catch (e) { res[i] = { erreur: String(e.message || e) + " @ " + String(e.stack || "").split("\n").slice(1, 3).join(" | ") }; } } }
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, ouvrier));
  return res;
}

export async function sparkTout(symboles, plage, intervalle) {
  const lots = []; for (let i = 0; i < symboles.length; i += 20) lots.push(symboles.slice(i, i + 20));
  const data = {}, echecs = {};
  const res = await parLots(lots, 6, (lot) => spark(lot, plage, intervalle));
  res.forEach((r, i) => {
    if (!r || r.erreur) { for (const s of lots[i]) echecs[s] = r ? r.erreur : "?"; return; }
    for (const s of lots[i]) { if (r[s]) data[s] = r[s]; else echecs[s] = "pas de données Yahoo"; }
  });
  return { data, echecs };
}

// Barres 5 minutes complètes d'une séance, sur la grille, dans les heures de séance.
// -> [{date, slot, min, o,h,l,c,v}] triées
export function barres(s, sym, maintenantMs, pas = 5) {
  const m = marcheDe(sym);
  let asOf = maintenantMs;
  const rmt = s.meta && s.meta.regularMarketTime;
  if (typeof rmt === "number" && rmt * 1000 < asOf && m.tz !== "UTC") asOf = rmt * 1000; // comme l'original : le temps des données
  const out = new Map();
  for (let i = 0; i < s.t.length; i++) {
    const ts = s.t[i]; const o = s.o ? s.o[i] : null, h = s.h ? s.h[i] : null, l = s.l ? s.l[i] : null, c = s.c[i];
    if (ts == null || c == null) continue;
    if (ts % (pas * 60)) continue; // le tick en direct, hors grille
    const lo = local(ts * 1000, m);
    const se = seance(lo.date, m);
    if (!se || lo.min < se[0] || lo.min >= se[1]) continue;
    if (ts * 1000 + pas * 60e3 > asOf) continue; // barre pas encore terminée
    out.set(ts, { ts, date: lo.date, min: lo.min, slot: (lo.min - se[0]) / pas, o, h, l, c, v: s.v ? (s.v[i] || 0) : 0 });
  }
  return [...out.keys()].sort((a, b) => a - b).map((k) => out.get(k));
}

// ------------------------------------------------------------- univers Nasdaq Trader
const TICKER = /^[A-Z]{1,5}$|^[A-Z]{1,4}\.[A-Z]$/;
const TOUJOURS_DEHORS = [/\bwarrants?\b/, /\b(units?|rights?),? (each|that|entitling)\b|(?<!the )\brights? to\b/, /\b(notes?|etns?|debentures?)\b/, /%/, /(?<!american )(?<!global )\bdepositary shares?\b/];
const COMMUN = /\bcommon (stock|shares?|units?)\b|\bord(inary)? shares?\b|\bshares? of beneficial interest\b|\b(american|global) deposit[ao]ry\b|\bads[s]?\b|\badrs?\b|\b(limited partnership|partnership|trust) units?\b|\bl\.?p\.? units?\b|\bunits? (of|representing)\b.*\b(limited partner|partnership|beneficial interest|limited liability)/;
const DEHORS_DOUX = [/\bunits?\b/, /\brights?\b/, /\bbonds?\b/, /\bpreferred\b|\bpreference\b/];

function garder(r) {
  const sym = (r["Symbol"] || r["ACT Symbol"] || "").trim();
  if ((r["Test Issue"] || "").trim() !== "N") return false;
  if ((r["ETF"] || "").trim() !== "N") return false;
  if ((r["NextShares"] || "N").trim() !== "N") return false;
  if (!TICKER.test(sym) || /\.[UWR]$/.test(sym)) return false;
  const nom = (r["Security Name"] || "").toLowerCase().split(/\s+/).join(" ");
  if (TOUJOURS_DEHORS.some((rx) => rx.test(nom))) return false;
  if (COMMUN.test(nom)) return true;
  return !DEHORS_DOUX.some((rx) => rx.test(nom));
}
export async function univers() {
  const garde = {};
  for (const f of ["nasdaqlisted.txt", "otherlisted.txt"]) {
    const { code, txt } = await texte("https://www.nasdaqtrader.com/dynamic/SymDir/" + f);
    if (code !== 200) throw new ErreurDonnees(`nasdaqtrader.com a répondu HTTP ${code} pour ${f}`);
    const lignes = txt.replace(/\r/g, "").split("\n").filter((l) => l.trim());
    const ent = lignes[0].split("|").map((h) => h.trim());
    for (const l of lignes.slice(1)) {
      if (l.startsWith("File Creation Time")) continue;
      const v = l.split("|"); const r = Object.fromEntries(ent.map((h, i) => [h, v[i]]));
      if (garder(r)) garde[(r["Symbol"] || r["ACT Symbol"]).trim()] = (r["Security Name"] || "").split(/\s+/).join(" ");
    }
  }
  return Object.keys(garde).sort().map((s) => [s, garde[s]]);
}
