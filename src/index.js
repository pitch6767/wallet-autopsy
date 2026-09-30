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
      if (url.pathname === "/api/holders") return json(await holdersReport(url.searchParams));
      if (url.pathname === "/api/sante") return json({ ok: true, heure: new Date().toISOString() });
    } catch (e) {
      return json({ erreur: String(e && e.message ? e.message : e) }, 500);
    }
    return env.ASSETS.fetch(req);
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
