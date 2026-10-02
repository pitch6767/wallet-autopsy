import { etude } from "./etude.js";
import { tourDeCollecte, etatCollecte, classement } from "./collect.js";
// wallet-autopsy — profilage de portefeuilles Polymarket
// Lecture seule : uniquement les API publiques de Polymarket, aucune clé, aucun ordre.

const DATA = "https://data-api.polymarket.com";
const GAMMA = "https://gamma-api.polymarket.com";
const PAGE = 500;
const MAX_PAGES = 20; // 10 000 lignes au plus par type de requête

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/api/wallet") return json(await walletReport(url.searchParams));
      if (url.pathname === "/api/etude") return json(await etude(env, url.searchParams.get("addr")));
      if (url.pathname === "/api/btc/classement") return json(await classement(env, url.searchParams));
      if (url.pathname === "/api/btc/tour") return json(await tourDeCollecte(env));
      if (url.pathname === "/api/btc/etat") return json(await etatCollecte(env));
      if (url.pathname === "/api/copier") return json(await copierReport(url.searchParams));
      if (url.pathname === "/api/market") return json(await marketReport(url.searchParams));
      if (url.pathname === "/api/holders") return json(await holdersReport(url.searchParams));
      if (url.pathname === "/api/sante") return json({ ok: true, heure: new Date().toISOString() });
    } catch (e) {
      return json({ erreur: String(e && e.message ? e.message : e) }, 500);
    }
    return env.ASSETS.fetch(req);
  },
  async scheduled(event, env, ctx) {
    ctx.waitUntil(tourDeCollecte(env).catch((e) => console.log("collecte", e && e.message)));
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

async function getJSON(u) {
  const r = await fetch(u, { headers: { accept: "application/json", "user-agent": "wallet-autopsy/1.0" } });
  if (!r.ok) throw new Error(`Polymarket a répondu ${r.status} sur ${new URL(u).pathname}`);
  return r.json();
}

// Pagination sur l'API data de Polymarket
async function paged(path, params) {
  const out = [];
  let tronque = false;
  for (let p = 0; p < MAX_PAGES; p++) {
    const q = new URLSearchParams({ ...params, limit: String(PAGE), offset: String(p * PAGE) });
    let rows;
    try {
      rows = await getJSON(`${DATA}${path}?${q}`);
    } catch (e) {
      if (p === 0) throw e;
      tronque = true; // l'API refuse souvent les décalages trop grands
      break;
    }
    if (!Array.isArray(rows) || rows.length === 0) break;
    out.push(...rows);
    if (rows.length < PAGE) break;
    if (p === MAX_PAGES - 1) tronque = true;
  }
  return { rows: out, tronque };
}

const isAddr = (a) => /^0x[0-9a-fA-F]{40}$/.test(a || "");
const num = (x) => (x == null || x === "" ? 0 : Number(x));

async function walletReport(sp) {
  const addr = (sp.get("addr") || "").trim();
  if (!isAddr(addr)) throw new Error("Adresse invalide : il faut 0x suivi de 40 caractères.");
  const market = (sp.get("market") || "").trim(); // conditionId facultatif
  const filtre = (sp.get("filtre") || "").trim().toLowerCase();

  const base = { user: addr };
  if (market) base.market = market;

  const [tr, act] = await Promise.all([
    paged("/trades", { ...base, takerOnly: "false" }),
    paged("/activity", { ...base, type: "SPLIT,MERGE,REDEEM" }).catch(() => ({ rows: [], tronque: false, erreur: true })),
  ]);

  // Regroupement par marché
  const marches = new Map();
  const get = (cid, row) => {
    if (!marches.has(cid)) {
      marches.set(cid, {
        conditionId: cid,
        titre: row.title || "",
        slug: row.slug || "",
        eventSlug: row.eventSlug || "",
        issues: {}, // outcomeIndex -> stats
        merges: 0, mergeUsdc: 0, splits: 0, splitUsdc: 0, redeemUsdc: 0,
        ts: [],
      });
    }
    return marches.get(cid);
  };
  const issue = (m, idx, nom) => {
    const k = String(idx ?? nom ?? "?");
    if (!m.issues[k]) m.issues[k] = { nom: nom || `Issue ${k}`, achatParts: 0, achatCout: 0, venteParts: 0, venteRecette: 0, nAchats: 0, nVentes: 0, prixAchats: [] };
    if (nom && m.issues[k].nom.startsWith("Issue ")) m.issues[k].nom = nom;
    return m.issues[k];
  };

  for (const t of tr.rows) {
    const cid = t.conditionId || t.market || "?";
    const m = get(cid, t);
    const o = issue(m, t.outcomeIndex, t.outcome);
    const size = num(t.size), price = num(t.price), ts = num(t.timestamp);
    if (String(t.side).toUpperCase() === "BUY") {
      o.achatParts += size; o.achatCout += size * price; o.nAchats++;
      o.prixAchats.push([ts, price, size]);
    } else {
      o.venteParts += size; o.venteRecette += size * price; o.nVentes++;
    }
    m.ts.push(ts);
  }
  for (const a of act.rows) {
    const cid = a.conditionId || "?";
    const m = get(cid, a);
    const type = String(a.type).toUpperCase();
    const size = num(a.size), usdc = num(a.usdcSize ?? a.size);
    if (type === "MERGE") { m.merges += size; m.mergeUsdc += usdc; }
    else if (type === "SPLIT") { m.splits += size; m.splitUsdc += usdc; }
    else if (type === "REDEEM") { m.redeemUsdc += usdc; }
  }

  // On ne garde que les marchés ayant des trades dans la fenêtre téléchargée :
  // un remboursement sans les achats correspondants fausserait les flux.
  let liste = [...marches.values()].map(analyseMarche).filter((m) => m.nTrades > 0);
  if (filtre) liste = liste.filter((m) => (m.titre + " " + m.slug).toLowerCase().includes(filtre));
  liste.sort((a, b) => b.dernier - a.dernier);

  // Synthèse
  const avecPaires = liste.filter((m) => m.pairesAchetees > 0);
  const tousTs = liste.flatMap((m) => m._ts);
  const s = {
    marches: liste.length,
    trades: liste.reduce((x, m) => x + m.nTrades, 0),
    volumeAchats: liste.reduce((x, m) => x + m.coutAchats, 0),
    marchesDeuxCotes: avecPaires.length,
    marchesSousUn: avecPaires.filter((m) => m.combine < 1).length,
    margePairesTotale: avecPaires.reduce((x, m) => x + m.margePaires, 0),
    pairesTotales: avecPaires.reduce((x, m) => x + m.pairesAchetees, 0),
    fluxRealise: liste.reduce((x, m) => x + m.fluxRealise, 0),
    ecartMedianSec: medianeEcarts(tousTs),
    memeSecondePct: memeSeconde(tousTs),
  };
  s.combineMoyenPondere = s.pairesTotales > 0 ? 1 - s.margePairesTotale / s.pairesTotales : null;
  s.profil = profil(s);

  for (const m of liste) delete m._ts;
  return {
    adresse: addr,
    filtre: filtre || null,
    market: market || null,
    lignes: { trades: tr.rows.length, activite: act.rows.length },
    tronque: tr.tronque || act.tronque,
    activiteIndisponible: !!act.erreur,
    synthese: s,
    marches: liste,
  };
}

function analyseMarche(m) {
  const cles = Object.keys(m.issues).sort();
  const issues = cles.map((k) => {
    const o = m.issues[k];
    return {
      index: k,
      nom: o.nom,
      achatParts: o.achatParts,
      prixMoyenAchat: o.achatParts > 0 ? o.achatCout / o.achatParts : null,
      venteParts: o.venteParts,
      prixMoyenVente: o.venteParts > 0 ? o.venteRecette / o.venteParts : null,
      nAchats: o.nAchats,
      nVentes: o.nVentes,
      tendancePrix: tendance(o.prixAchats),
      accumulation: accumulation(o.prixAchats),
    };
  });

  let paires = 0, combine = null, marge = 0;
  if (issues.length === 2 && issues[0].achatParts > 0 && issues[1].achatParts > 0) {
    paires = Math.min(issues[0].achatParts, issues[1].achatParts);
    combine = issues[0].prixMoyenAchat + issues[1].prixMoyenAchat;
    marge = paires * (1 - combine);
  }
  const cout = issues.reduce((x, o) => x + (o.achatParts * (o.prixMoyenAchat || 0)), 0);
  const recette = issues.reduce((x, o) => x + (o.venteParts * (o.prixMoyenVente || 0)), 0);
  const ts = m.ts.filter(Boolean).sort((a, b) => a - b);
  const desequilibre = issues.length === 2 ? Math.abs(issues[0].achatParts - issues[1].achatParts) : null;

  return {
    conditionId: m.conditionId,
    titre: m.titre,
    slug: m.slug,
    eventSlug: m.eventSlug,
    issues,
    nTrades: ts.length,
    premier: ts[0] || 0,
    dernier: ts[ts.length - 1] || 0,
    dureeMin: ts.length > 1 ? (ts[ts.length - 1] - ts[0]) / 60 : 0,
    ecartMedianSec: medianeEcarts(ts),
    memeSecondePct: memeSeconde(ts),
    coutAchats: cout,
    recetteVentes: recette,
    pairesAchetees: paires,
    combine,
    margePaires: marge,
    partsNonAppariees: desequilibre,
    merges: m.merges,
    mergeUsdc: m.mergeUsdc,
    splits: m.splits,
    splitUsdc: m.splitUsdc,
    redeemUsdc: m.redeemUsdc,
    // Flux de trésorerie déjà réalisés (hors valeur des parts encore détenues)
    fluxRealise: recette + m.mergeUsdc + m.redeemUsdc - cout - m.splitUsdc,
    _ts: ts,
  };
}

function medianeEcarts(ts) {
  const t = [...ts].filter(Boolean).sort((a, b) => a - b);
  if (t.length < 2) return null;
  const d = [];
  for (let i = 1; i < t.length; i++) d.push(t[i] - t[i - 1]);
  d.sort((a, b) => a - b);
  return d[Math.floor(d.length / 2)];
}
function memeSeconde(ts) {
  const t = [...ts].filter(Boolean).sort((a, b) => a - b);
  if (t.length < 2) return null;
  let n = 0;
  for (let i = 1; i < t.length; i++) if (t[i] === t[i - 1]) n++;
  return (100 * n) / (t.length - 1);
}
// Prix d'achat : moitié tardive vs moitié précoce (pondéré par la taille)
function tendance(a) {
  if (a.length < 4) return null;
  const s = [...a].sort((x, y) => x[0] - y[0]);
  const h = Math.floor(s.length / 2);
  const moy = (arr) => { const q = arr.reduce((x, r) => x + r[2], 0); return q ? arr.reduce((x, r) => x + r[1] * r[2], 0) / q : 0; };
  return moy(s.slice(h)) - moy(s.slice(0, h));
}
// Taille moyenne des achats tardifs / précoces
function accumulation(a) {
  if (a.length < 4) return null;
  const s = [...a].sort((x, y) => x[0] - y[0]);
  const h = Math.floor(s.length / 2);
  const moy = (arr) => arr.reduce((x, r) => x + r[2], 0) / arr.length;
  const p = moy(s.slice(0, h));
  return p ? moy(s.slice(h)) / p : null;
}
function profil(s) {
  const tags = [];
  if (s.trades >= 20 && s.ecartMedianSec != null && s.ecartMedianSec <= 2) tags.push("Automate probable (écart médian ≤ 2 s)");
  if (s.memeSecondePct != null && s.memeSecondePct >= 30) tags.push("Nombreux ordres dans la même seconde");
  if (s.marchesDeuxCotes > 0 && s.marchesDeuxCotes >= 0.6 * s.marches) tags.push("Achète les deux côtés sur la plupart des marchés");
  if (s.combineMoyenPondere != null && s.combineMoyenPondere < 1) tags.push("Paires acquises sous 1 $ en moyenne");
  if (!tags.length) tags.push("Pas de signature particulière");
  return tags;
}

// Détenteurs principaux d'un événement / marché
async function holdersReport(sp) {
  let saisie = (sp.get("q") || "").trim();
  if (!saisie) throw new Error("Colle l'adresse de la page Polymarket ou le slug de l'événement.");
  let slug = saisie;
  const m = saisie.match(/polymarket\.com\/(?:[a-z]{2}\/)?(event|market)\/([^/?#]+)(?:\/([^/?#]+))?/i);
  if (m) slug = m[3] || m[2];

  // On tente d'abord l'événement, puis le marché
  let marches = [];
  let titre = "";
  const ev = await getJSON(`${GAMMA}/events?slug=${encodeURIComponent(m ? m[2] : slug)}`).catch(() => []);
  if (Array.isArray(ev) && ev.length) {
    titre = ev[0].title || "";
    marches = ev[0].markets || [];
    if (m && m[3]) marches = marches.filter((x) => x.slug === m[3]).length ? marches.filter((x) => x.slug === m[3]) : marches;
  } else {
    const mk = await getJSON(`${GAMMA}/markets?slug=${encodeURIComponent(slug)}`).catch(() => []);
    if (Array.isArray(mk) && mk.length) { marches = mk; titre = mk[0].question || ""; }
  }
  if (!marches.length) throw new Error("Événement introuvable sur Polymarket avec ce lien ou ce slug.");
  marches = marches.slice(0, 5);

  const res = [];
  for (const mk of marches) {
    const cid = mk.conditionId;
    if (!cid) continue;
    let h = [];
    try { h = await getJSON(`${DATA}/holders?market=${cid}&limit=20`); } catch { h = []; }
    let outcomes = [];
    try { outcomes = JSON.parse(mk.outcomes || "[]"); } catch {}
    const cotes = (Array.isArray(h) ? h : []).map((bloc) => ({
      token: bloc.token,
      detenteurs: (bloc.holders || []).map((x) => ({
        adresse: x.proxyWallet,
        nom: x.name || x.pseudonym || "",
        parts: num(x.amount),
        issue: outcomes[num(x.outcomeIndex)] || String(x.outcomeIndex ?? ""),
      })),
    }));
    res.push({ conditionId: cid, question: mk.question || "", slug: mk.slug || "", cotes });
  }
  return { titre, marches: res };
}


// ─────────────────────────────────────────────────────────────
// Analyse de TOUS les portefeuilles ayant tradé sur un marché
// ─────────────────────────────────────────────────────────────
async function resoudreMarche(saisie) {
  saisie = saisie.trim();
  if (/^0x[0-9a-fA-F]{64}$/.test(saisie)) {
    const mk = await getJSON(`${GAMMA}/markets?condition_ids=${saisie}`).catch(() => []);
    if (Array.isArray(mk) && mk.length) return { titre: mk[0].question, marche: mk[0] };
  }
  const m = saisie.match(/polymarket\.com\/(?:[a-z]{2}\/)?(event|market)\/([^/?#]+)(?:\/([^/?#]+))?/i);
  const evSlug = m ? m[2] : saisie;
  const mkSlug = m ? m[3] : null;
  const ev = await getJSON(`${GAMMA}/events?slug=${encodeURIComponent(evSlug)}`).catch(() => []);
  if (Array.isArray(ev) && ev.length && (ev[0].markets || []).length) {
    const ms = ev[0].markets;
    const choisi = (mkSlug && ms.find((x) => x.slug === mkSlug)) || ms[0];
    return { titre: ev[0].title || choisi.question, marche: choisi, autres: ms.length };
  }
  const mk = await getJSON(`${GAMMA}/markets?slug=${encodeURIComponent(mkSlug || evSlug)}`).catch(() => []);
  if (Array.isArray(mk) && mk.length) return { titre: mk[0].question, marche: mk[0] };
  throw new Error("Marché introuvable sur Polymarket avec ce lien.");
}

const parseArr = (x) => { try { return Array.isArray(x) ? x : JSON.parse(x || "[]"); } catch { return []; } };

async function marketReport(sp) {
  const saisie = sp.get("q") || "";
  if (!saisie.trim()) throw new Error("Colle le lien de la page Polymarket du marché.");
  const { titre, marche, autres } = await resoudreMarche(saisie);
  const cid = marche.conditionId;
  const issuesNoms = parseArr(marche.outcomes);
  const prix = parseArr(marche.outcomePrices).map(Number);
  const resolu = !!marche.closed && prix.some((p) => p === 1);
  const fin = marche.endDate ? Math.floor(Date.parse(marche.endDate) / 1000) : null;

  // 1. Tous les trades du marché
  const tr = await paged("/trades", { market: cid, takerOnly: "false" });

  // 2. Regroupement par portefeuille
  const W = new Map();
  for (const t of tr.rows) {
    const a = (t.proxyWallet || "").toLowerCase();
    if (!a) continue;
    if (!W.has(a)) W.set(a, { adresse: a, nom: t.name || t.pseudonym || "", o: [0, 1].map(() => ({ ap: 0, ac: 0, vp: 0, vr: 0, n: 0 })), ts: [], tailles: [] });
    const w = W.get(a);
    const i = Number(t.outcomeIndex) === 1 ? 1 : 0;
    const size = num(t.size), price = num(t.price), ts = num(t.timestamp);
    if (String(t.side).toUpperCase() === "BUY") { w.o[i].ap += size; w.o[i].ac += size * price; }
    else { w.o[i].vp += size; w.o[i].vr += size * price; }
    w.o[i].n++;
    w.ts.push(ts);
    w.tailles.push(size * price);
  }

  // 3. Fusions / splits / remboursements pour les plus gros portefeuilles
  const parVolume = [...W.values()].map((w) => ({ w, vol: w.o[0].ac + w.o[1].ac + w.o[0].vr + w.o[1].vr })).sort((a, b) => b.vol - a.vol);
  const TOP_ACT = 40;
  const cibles = parVolume.slice(0, TOP_ACT).map((x) => x.w);
  for (let k = 0; k < cibles.length; k += 8) {
    await Promise.all(cibles.slice(k, k + 8).map(async (w) => {
      try {
        const rows = await getJSON(`${DATA}/activity?user=${w.adresse}&market=${cid}&type=SPLIT,MERGE,REDEEM&limit=500`);
        w.act = { merge: 0, mergeUsdc: 0, split: 0, splitUsdc: 0, redeemUsdc: 0 };
        for (const r of rows || []) {
          const ty = String(r.type).toUpperCase();
          if (ty === "MERGE") { w.act.merge += num(r.size); w.act.mergeUsdc += num(r.usdcSize ?? r.size); }
          if (ty === "SPLIT") { w.act.split += num(r.size); w.act.splitUsdc += num(r.usdcSize ?? r.size); }
          if (ty === "REDEEM") w.act.redeemUsdc += num(r.usdcSize ?? r.size);
        }
      } catch { /* laissé vide */ }
    }));
  }

  // 4. Calculs par portefeuille
  const liste = [...W.values()].map((w) => {
    const [A, B] = w.o;
    const pmA = A.ap ? A.ac / A.ap : null, pmB = B.ap ? B.ac / B.ap : null;
    const act = w.act || { merge: 0, mergeUsdc: 0, split: 0, splitUsdc: 0, redeemUsdc: 0 };
    const netA = A.ap - A.vp - act.merge + act.split;
    const netB = B.ap - B.vp - act.merge + act.split;
    const cout = A.ac + B.ac + act.splitUsdc;
    const encaisse = A.vr + B.vr + act.mergeUsdc;
    // Valeur des parts restantes : prix de résolution si résolu, sinon dernier prix connu
    const valeur = (prix.length === 2) ? Math.max(netA, 0) * (prix[0] || 0) + Math.max(netB, 0) * (prix[1] || 0) : null;
    const pnl = valeur == null ? null : encaisse + valeur - cout;
    const paires = A.ap && B.ap ? Math.min(A.ap, B.ap) : 0;
    const combine = A.ap && B.ap ? pmA + pmB : null;
    const ts = w.ts.sort((a, b) => a - b);
    const n = ts.length;
    const ecart = medianeEcarts(ts);
    const meme = memeSeconde(ts);
    const tags = [];
    if (n >= 10 && ecart != null && ecart <= 2) tags.push("Automate");
    if (paires > 0 && combine != null) tags.push(combine < 1 ? "Paires < 1 $" : "Deux côtés");
    else if (A.ap || B.ap) tags.push("Directionnel " + (A.ap >= B.ap ? (issuesNoms[0] || "A") : (issuesNoms[1] || "B")));
    if (A.vp + B.vp > 0) tags.push("Revend");
    if (act.merge > 0) tags.push("Fusionne");
    return {
      adresse: w.adresse, nom: w.nom, trades: n,
      achatA: A.ap, pmA, achatB: B.ap, pmB, venteA: A.vp, venteB: B.vp,
      combine, paires, margePaires: paires ? paires * (1 - combine) : 0,
      cout, encaisse, valeur, pnl, roi: pnl != null && cout > 0 ? pnl / cout : null,
      premier: ts[0] || 0, dernier: ts[n - 1] || 0,
      avantFinSec: fin && ts[0] ? fin - ts[0] : null,
      ecartMedianSec: ecart, memeSecondePct: meme,
      merge: act.merge, mergeUsdc: act.mergeUsdc, redeemUsdc: act.redeemUsdc,
      activiteLue: !!w.act, tags,
    };
  });
  liste.sort((a, b) => (b.cout + b.encaisse) - (a.cout + a.encaisse));

  // 5. Synthèse du marché
  const somme = (f) => liste.reduce((x, w) => x + (f(w) || 0), 0);
  const avecPnl = liste.filter((w) => w.pnl != null);
  const gagnants = avecPnl.filter((w) => w.pnl > 0);
  const synthese = {
    portefeuilles: liste.length,
    trades: tr.rows.length,
    volumeAchats: somme((w) => w.cout),
    automates: liste.filter((w) => w.tags.includes("Automate")).length,
    deuxCotes: liste.filter((w) => w.paires > 0).length,
    pairesSousUn: liste.filter((w) => w.combine != null && w.combine < 1).length,
    gagnants: gagnants.length,
    perdants: avecPnl.filter((w) => w.pnl < 0).length,
    pnlGagnants: gagnants.reduce((x, w) => x + w.pnl, 0),
    pnlTotal: avecPnl.reduce((x, w) => x + w.pnl, 0),
    partTop10Volume: (() => { const t = somme((w) => w.cout); return t ? liste.slice(0, 10).reduce((x, w) => x + w.cout, 0) / t : null; })(),
  };

  return {
    titre, question: marche.question, conditionId: cid, slug: marche.slug,
    issues: issuesNoms, prix, resolu, ferme: !!marche.closed, fin: marche.endDate || null,
    autresMarches: autres && autres > 1 ? autres : null,
    tronque: tr.tronque, activiteLuePourTop: Math.min(TOP_ACT, liste.length),
    synthese, portefeuilles: liste,
  };
}

// ─────────────────────────────────────────────────────────────
// « À copier » : historique de chaque portefeuille sur les marchés
// du même type (même famille de slug, ex. btc-updown-5m)
// ─────────────────────────────────────────────────────────────
function famille(slug, titre) {
  slug = slug || "";
  if (/-\d{6,}$/.test(slug)) return { cle: "slug", val: slug.replace(/-\d{6,}$/, "") };
  return { cle: "titre", val: String(titre || "").split(" - ")[0].trim().toLowerCase() };
}
function memeFamille(f, slug, titre) {
  if (f.cle === "slug") return (slug || "").replace(/-\d{6,}$/, "") === f.val && /-\d{6,}$/.test(slug || "");
  return String(titre || "").split(" - ")[0].trim().toLowerCase() === f.val;
}

async function historiqueFamille(addr, f) {
  const rows = [];
  for (let p = 0; p < 4; p++) {
    const q = new URLSearchParams({ user: addr, limit: "50", offset: String(p * 50), sortBy: "TIMESTAMP", sortDirection: "DESC" });
    let r;
    try { r = await getJSON(`${DATA}/closed-positions?${q}`); } catch { break; }
    if (!Array.isArray(r) || !r.length) break;
    rows.push(...r);
    if (r.length < 50) break;
  }
  const M = new Map();
  for (const r of rows) {
    if (!memeFamille(f, r.slug, r.title)) continue;
    const cid = r.conditionId;
    if (!M.has(cid)) M.set(cid, { pnl: 0, cout: 0, ts: num(r.timestamp), cotes: [] });
    const m = M.get(cid);
    const c = num(r.avgPrice) * num(r.totalBought);
    m.pnl += num(r.realizedPnl);
    m.cout += c;
    m.cotes.push({ prix: num(r.avgPrice), parts: num(r.totalBought), cout: c, gagnant: num(r.curPrice) >= 0.99 });
  }
  const ms = [...M.values()];
  const n = ms.length;
  const pnl = ms.reduce((x, m) => x + m.pnl, 0);
  const cout = ms.reduce((x, m) => x + m.cout, 0);
  const gagnes = ms.filter((m) => m.pnl > 0).length;
  const rois = ms.filter((m) => m.cout > 0).map((m) => m.pnl / m.cout);
  const moy = rois.length ? rois.reduce((a, b) => a + b, 0) / rois.length : null;
  const sd = rois.length > 1 ? Math.sqrt(rois.reduce((a, b) => a + (b - moy) ** 2, 0) / (rois.length - 1)) : null;
  const regularite = sd && sd > 0 ? (moy / sd) * Math.sqrt(rois.length) : null;
  // Profil de stratégie sur l'historique
  const deux = ms.filter((m) => m.cotes.length >= 2);
  const un = ms.filter((m) => m.cotes.length === 1);
  const parts = ms.reduce((x, m) => x + m.cotes.reduce((y, c) => y + c.parts, 0), 0);
  const combines = deux.map((m) => m.cotes[0].prix + m.cotes[1].prix);
  const cat = (f) => { const l = un.filter((m) => f(m.cotes[0].prix)); return { n: l.length, g: l.filter((m) => m.cotes[0].gagnant).length, px: l.reduce((x, m) => x + m.cotes[0].prix, 0) }; };
  const profil = {
    deux: { n: deux.length, combine: combines.length ? combines.reduce((a, b) => a + b, 0) / combines.length : null, sous1: combines.filter((c) => c < 1).length, nComb: combines.length },
    sniper: cat((p) => p >= 0.9), loterie: cat((p) => p <= 0.25), dir: cat((p) => p > 0.25 && p < 0.9),
    pireMarche: ms.length ? Math.min(...ms.map((m) => m.pnl)) : null,
    meilleurMarche: ms.length ? Math.max(...ms.map((m) => m.pnl)) : null,
    miseMoyenne: n ? cout / n : null,
  };
  return { adresse: addr, marches: n, gagnes, pctGagnes: n ? gagnes / n : null, pnl, cout, roi: cout > 0 ? pnl / cout : null, roiMoyen: moy, regularite, positionsLues: rows.length, profil };
}

async function copierReport(sp) {
  const slug = sp.get("slug") || "", titre = sp.get("titre") || "";
  const addrs = (sp.get("addrs") || "").split(",").map((a) => a.trim().toLowerCase()).filter(isAddr).slice(0, 60);
  if (!addrs.length) throw new Error("Aucune adresse à évaluer.");
  const f = famille(slug, titre);
  const out = [];
  for (let k = 0; k < addrs.length; k += 10) {
    out.push(...(await Promise.all(addrs.slice(k, k + 10).map((a) => historiqueFamille(a, f).catch(() => null)))));
  }
  return { famille: f.val, evalues: addrs.length, portefeuilles: out.filter(Boolean) };
}
