// Étude d'un portefeuille sur les marchés « Bitcoin Up or Down ».
// Télécharge ses trades, les rattache aux marchés (fin, gagnant), puis cherche
// ce qui le caractérise vraiment. Chaque constat n'est écrit que s'il est
// observé dans ses données, avec ses chiffres.

const DATA = "https://data-api.polymarket.com";
const GAMMA = "https://gamma-api.polymarket.com";
const num = (x) => (x == null || x === "" ? 0 : Number(x)) || 0;

const DUREE = { "5m": 300, "15m": 900, "4h": 14400 };
function typeDepuisSlug(slug) {
  const m = /^btc-updown-(5m|15m|4h)-(\d+)$/.exec(slug || "");
  if (m) return { type: m[1], fin: Number(m[2]) + DUREE[m[1]] };
  if (/^bitcoin-up-or-down-on-/.test(slug || "")) return { type: "1j", fin: null };
  if (/^bitcoin-up-or-down-/.test(slug || "")) return { type: "1h", fin: null };
  return null;
}
const estBtc = (t) => {
  const s = String(t.slug || "");
  return /^btc-updown-/.test(s) || /^bitcoin-up-or-down-/.test(s);
};

// ─── formatage ───
const usd = (x) => (x < 0 ? "−" : "") + "$" + Math.abs(x).toLocaleString("fr-CH", { maximumFractionDigits: Math.abs(x) >= 100 ? 0 : 2 });
const pc = (x) => (Math.abs(x) < 0.1 ? (x * 100).toFixed(1) : Math.round(x * 100)) + " %";
const px = (x) => x.toFixed(x < 0.1 ? 3 : 2) + " $";
const dur = (s) => {
  const a = Math.abs(s);
  const t = a < 60 ? Math.round(a) + " s" : a < 3600 ? Math.round(a / 60) + " min" : (a / 3600).toFixed(1) + " h";
  return t;
};
const jour = (ts) => new Date(ts * 1000).toLocaleDateString("fr-CH", { day: "2-digit", month: "2-digit", timeZone: "Europe/Zurich" });
const heureZ = (ts) => Number(new Date(ts * 1000).toLocaleString("en-GB", { hour: "2-digit", hour12: false, timeZone: "Europe/Zurich" }));
const med = (a) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };

async function getJSON(u) {
  for (let e = 0; ; e++) {
    const r = await fetch(u, { headers: { accept: "application/json", "user-agent": "wallet-autopsy/1.0" } });
    if (r.ok) return r.json();
    if ((r.status === 429 || r.status >= 500) && e < 3) { await new Promise((ok) => setTimeout(ok, 700 * (e + 1))); continue; }
    throw new Error(`Polymarket a répondu ${r.status}`);
  }
}

async function tradesWallet(addr) {
  const rows = [];
  let tronque = false;
  for (let off = 0; off <= 10000; off += 500) {
    let r;
    try { r = await getJSON(`${DATA}/trades?user=${addr}&limit=500&offset=${off}&takerOnly=false`); }
    catch { tronque = off > 0; break; }
    if (!Array.isArray(r) || !r.length) break;
    rows.push(...r);
    if (r.length < 500) break;
    if (off === 10000) tronque = true;
  }
  return { rows, tronque };
}

async function infosMarches(env, cids, slugs) {
  const info = new Map();
  for (let i = 0; i < cids.length; i += 90) {
    const lot = cids.slice(i, i + 90);
    const q = `SELECT cid,type,end_ts,gagnant FROM markets WHERE cid IN (${lot.map(() => "?").join(",")})`;
    const { results } = await env.DB.prepare(q).bind(...lot).all();
    for (const r of results) if (r.gagnant != null) info.set(r.cid, { type: r.type, fin: r.end_ts, gagnant: r.gagnant });
  }
  // Marchés pas encore collectés : on interroge Polymarket (limité pour rester rapide)
  const manquants = cids.filter((c) => !info.has(c)).slice(0, 40);
  await Promise.all(manquants.map(async (cid) => {
    try {
      const mk = await getJSON(`${GAMMA}/markets?slug=${encodeURIComponent(slugs.get(cid))}`);
      const m = Array.isArray(mk) && mk[0];
      if (!m) return;
      const p = JSON.parse(m.outcomePrices || "[]").map(Number);
      const g = p[0] === 1 ? 0 : p[1] === 1 ? 1 : null;
      if (g == null) return;
      const t = typeDepuisSlug(m.slug);
      info.set(cid, { type: t ? t.type : "?", fin: Date.parse(m.endDate) / 1000 | 0, gagnant: g });
    } catch {}
  }));
  return info;
}

export async function etude(env, addr) {
  addr = String(addr || "").toLowerCase();
  if (!/^0x[0-9a-f]{40}$/.test(addr)) throw new Error("Adresse invalide.");
  const { rows, tronque } = await tradesWallet(addr);
  const btc = rows.filter(estBtc);
  const autres = rows.length - btc.length;

  // Regroupement par marché
  const M = new Map();
  for (const t of btc) {
    const cid = t.conditionId;
    if (!M.has(cid)) M.set(cid, { cid, slug: t.slug, titre: t.title, o: [0, 1].map(() => ({ ap: 0, ac: 0, vp: 0, vr: 0 })), achats: [], ventes: 0, n: 0 });
    const m = M.get(cid);
    const i = Number(t.outcomeIndex) === 1 ? 1 : 0;
    const sz = num(t.size), p = num(t.price), ts = num(t.timestamp);
    if (String(t.side).toUpperCase() === "BUY") { m.o[i].ap += sz; m.o[i].ac += sz * p; m.achats.push({ i, sz, p, ts, usd: sz * p }); }
    else { m.o[i].vp += sz; m.o[i].vr += sz * p; m.ventes++; }
    m.n++;
  }
  const slugs = new Map([...M.values()].map((m) => [m.cid, m.slug]));
  const info = await infosMarches(env, [...M.keys()], slugs);

  const marches = [];
  for (const m of M.values()) {
    const inf = info.get(m.cid);
    if (!inf) continue; // non résolu ou introuvable
    const [A, B] = m.o;
    let netA = A.ap - A.vp, netB = B.ap - B.vp;
    const k = Math.max(0, -netA, -netB);
    netA += k; netB += k;
    const cout = A.ac + B.ac + k;
    if (cout < 0.01) continue;
    const pnl = A.vr + B.vr + (inf.gagnant === 0 ? netA : netB) - cout;
    const cote = A.ac >= B.ac ? 0 : 1;
    const oc = m.o[cote];
    const deux = A.ap > 0 && B.ap > 0;
    const fin = inf.fin || (typeDepuisSlug(m.slug) || {}).fin;
    const premier = m.achats.length ? Math.min(...m.achats.map((a) => a.ts)) : null;
    // Première entrée : côté et prix des achats faits dans les 10 s suivant le premier achat
    let e1 = null;
    if (premier != null) {
      const p0 = m.achats.filter((a) => a.ts <= premier + 10);
      const c0 = p0.find((a) => a.ts === premier).i;
      const l = p0.filter((a) => a.i === c0);
      const q = l.reduce((x, a) => x + a.sz, 0);
      e1 = { cote: c0, prix: q ? l.reduce((x, a) => x + a.sz * a.p, 0) / q : null };
    }
    marches.push({
      cid: m.cid, slug: m.slug, titre: m.titre, type: inf.type, fin, gagnant: inf.gagnant,
      cout, pnl, roi: pnl / cout, gagne: pnl > 0,
      cote, prixCote: oc.ap ? oc.ac / oc.ap : null, coteGagne: cote === inf.gagnant,
      deux, combine: deux ? A.ac / A.ap + B.ac / B.ap : null,
      revend: oc.vp > 0.1 * oc.ap || k > 0,
      e1cote: e1 ? e1.cote : null, e1prix: e1 ? e1.prix : null, e1juste: e1 ? e1.cote === inf.gagnant : null,
      avantFin: fin && premier ? fin - premier : null,
      achats: m.achats.map((a) => ({ ...a, avantFin: fin ? fin - a.ts : null, gagnant: a.i === inf.gagnant })),
      ts: premier || 0, ordres: m.n,
    });
  }
  marches.sort((a, b) => a.ts - b.ts);
  return analyser(addr, marches, { tronque, autres, totalTrades: rows.length, btcTrades: btc.length, nonResolus: M.size - marches.length });
}

// ─── Analyse : chaque détecteur renvoie un constat ou rien ───
function analyser(addr, ms, meta) {
  const n = ms.length;
  const out = { adresse: addr, marches: n, meta, constats: [], titre: "", verdict: "", copiable: false };
  if (!n) {
    out.titre = "Aucun marché BTC exploitable";
    out.verdict = "Pas de marché BTC Up or Down résolu dans son historique téléchargeable.";
    return out;
  }
  const C = (poids, texte) => out.constats.push({ poids, texte });
  const pnl = ms.reduce((x, m) => x + m.pnl, 0), cout = ms.reduce((x, m) => x + m.cout, 0);
  const gagnes = ms.filter((m) => m.gagne).length;
  const debut = ms[0].ts, finP = ms[n - 1].ts, jours = Math.max(1, (finP - debut) / 86400);
  const parType = {};
  for (const m of ms) (parType[m.type] = parType[m.type] || []).push(m);
  const achats = ms.flatMap((m) => m.achats.map((a) => ({ ...a, m })));
  const usdAchats = achats.reduce((x, a) => x + a.usd, 0) || 1;

  // 1. Achats après la fin de la fenêtre (résultat déjà connu)
  const apres = achats.filter((a) => a.avantFin != null && a.avantFin < 0);
  const usdApres = apres.reduce((x, a) => x + a.usd, 0);
  const mApres = new Set(apres.map((a) => a.m.cid));
  let ramasseur = false;
  if (mApres.size >= 3 && mApres.size >= 0.3 * n) {
    ramasseur = true;
    const pMed = med(apres.map((a) => a.p)), dMed = med(apres.map((a) => -a.avantFin));
    const ok = apres.filter((a) => a.gagnant).length;
    C(100, `<b>Il achète après la fin de la fenêtre</b> sur ${mApres.size} de ses ${n} marchés (${pc(usdApres / usdAchats)} de ses achats en $), en médiane <b>${dur(dMed)} après la clôture</b>, au prix médian de ${px(pMed)}. À ce moment le prix de clôture du BTC est déjà connu ; le marché n'est simplement pas encore réglé. Il ramasse les ordres de vente restés en carnet : ${ok} de ces ${apres.length} achats portent sur le côté qui a effectivement gagné.`);
  }

  // 2. Achats dans les toutes dernières secondes
  const fin10 = achats.filter((a) => a.avantFin != null && a.avantFin >= 0 && a.avantFin <= 10);
  const mFin10 = new Set(fin10.map((a) => a.m.cid));
  if (!ramasseur && mFin10.size >= 5 && mFin10.size >= 0.3 * n) {
    const ok = fin10.filter((a) => a.gagnant).length;
    C(90, `${pc(mFin10.size / n)} de ses marchés comportent des achats dans les <b>10 dernières secondes</b>, au prix médian de ${px(med(fin10.map((a) => a.p)))} — côté gagnant dans ${ok} cas sur ${fin10.length}. Il réagit au mouvement final du BTC plus vite que le carnet ne se met à jour.`);
  }

  // 3. Concentration du gain
  if (pnl > 0 && n >= 3) {
    const best = ms.reduce((a, b) => (b.pnl > a.pnl ? b : a));
    const part = best.pnl / pnl;
    if (part >= 0.5) {
      const sans = pnl - best.pnl, coutSans = cout - best.cout;
      C(95, `<b>${pc(Math.min(part, 9.99))} de son gain vient d'un seul marché</b> (${jour(best.ts)}, ${esc(best.titre)}) : ${usd(best.cout)} misés à ${px(best.prixCote)} sont devenus ${usd(best.cout + best.pnl)}. Sans ce marché, il est à ${usd(sans)} (ROI ${coutSans > 0 ? pc(sans / coutSans) : "—"}) sur les ${n - 1} autres.`);
    }
  }

  // 4. Première entrée contre résultat réel. On classe chaque marché par le prix
  // de sa première entrée (ce que verrait quelqu'un qui le copie) et on compte
  // TOUT ce qu'il fait ensuite dans ce marché (couvertures, reventes comprises).
  const simples = ms.filter((m) => !m.deux && !m.revend && m.prixCote != null && !mApres.has(m.cid));
  const entrees = ms.filter((m) => m.e1prix != null && !mApres.has(m.cid));
  const tranches = [[0, 0.1, "moins de 0,10 $"], [0.1, 0.3, "0,10 à 0,30 $"], [0.3, 0.5, "0,30 à 0,50 $"], [0.5, 0.7, "0,50 à 0,70 $"], [0.7, 0.9, "0,70 à 0,90 $"], [0.9, 1.01, "0,90 $ et plus"]];
  const lignes = [];
  let meilleure = null;
  for (const [a, b, lib] of tranches) {
    const l = entrees.filter((m) => m.e1prix >= a && m.e1prix < b);
    if (l.length < 5) continue;
    const att = l.reduce((x, m) => x + m.e1prix, 0), ok = l.filter((m) => m.e1juste).length;
    const v = l.reduce((x, m) => x + m.e1prix * (1 - m.e1prix), 0);
    const z = v > 0 ? (ok - att) / Math.sqrt(v) : 0;
    const p = l.reduce((x, m) => x + m.pnl, 0), c = l.reduce((x, m) => x + m.cout, 0);
    const avant = med(l.filter((m) => m.avantFin != null).map((m) => m.avantFin));
    const couverts = l.filter((m) => m.deux || m.revend).length;
    const t = { lib, n: l.length, ok, att, z, p, c, avant, couverts };
    lignes.push(t);
    // Copiable seulement si l'avance survit au retard d'un copieur : >= 5 points, ROI >= 5 %, 30 marchés
    t.marge = (ok - att) / l.length;
    if (z >= 2 && p > 0 && p / c >= 0.05 && t.marge >= 0.05 && l.length >= 30 && avant != null && avant >= 60 && (!meilleure || t.marge * Math.sqrt(t.n) > meilleure.marge * Math.sqrt(meilleure.n))) meilleure = t;
  }
  if (lignes.length) {
    const exclus = mApres.size ? `, hors ${mApres.size} marché${mApres.size > 1 ? "s" : ""} acheté${mApres.size > 1 ? "s" : ""} après la clôture` : "";
    const txt = lignes.map((l) => `première entrée ${l.lib} : ${l.n} marchés, bon côté ${l.ok} fois pour ${Math.round(l.att)} attendues par le prix, résultat final ${usd(l.p)} (ROI ${pc(l.p / l.c)})` + (l.couverts ? `, ${l.couverts} rattrapés ensuite en achetant l'autre côté ou en revendant` : "")).join(" ; ");
    const fort = lignes.filter((l) => l.z >= 2 && l.p > 0);
    let conclu = fort.length ? ` <b>Sa première entrée bat le prix sur ${fort.map((l) => l.lib).join(", ")}.</b>` : " Le côté qu'il choisit en entrant ne bat le prix du marché sur aucune tranche : son résultat ne vient pas de sa lecture de la direction.";
    const faux = lignes.filter((l) => l.z >= 2 && l.p <= 0);
    if (faux.length) conclu += ` Sur ${faux.map((l) => l.lib).join(", ")}, il choisit souvent le bon côté mais perd quand même de l'argent : ses couvertures et reventes coûtent plus que ce qu'elles protègent.`;
    const tard = fort.filter((l) => l.avant != null && l.avant < 60);
    if (tard.length) conclu += ` Sur ${tard.map((l) => l.lib).join(", ")} il entre moins d'une minute avant la fin : le résultat est alors presque joué, ce n'est pas suivable.`;
    C(fort.length ? 85 : 60, `Ce que vivrait quelqu'un qui le copie (${entrees.length} marchés${exclus}, classés par le prix de sa première entrée, tout ce qu'il fait ensuite compris) — ${txt}.${conclu}`);
  }

  // 4b. Où il gagne et où il perd
  const cats = [
    ["paris sur un seul côté gardés jusqu'au bout", simples],
    ["marchés où il achète les deux côtés", ms.filter((m) => m.deux && !mApres.has(m.cid))],
    ["marchés où il revend avant la fin", ms.filter((m) => !m.deux && m.revend && !mApres.has(m.cid))],
    ["achats après la clôture", ms.filter((m) => mApres.has(m.cid))],
  ].filter(([, l]) => l.length).map(([lib, l]) => ({ lib, n: l.length, p: l.reduce((x, m) => x + m.pnl, 0), c: l.reduce((x, m) => x + m.cout, 0) }));
  if (cats.length >= 2) {
    const g = cats.filter((c) => c.p > 0), pr = cats.filter((c) => c.p < 0);
    C(75, "D'où vient son résultat : " + cats.map((c) => `${c.lib} ${usd(c.p)} sur ${c.n} marchés (ROI ${pc(c.p / c.c)})`).join(" ; ") + "."
      + (g.length && pr.length ? ` Il gagne sur les ${g.map((c) => c.lib).join(" et ")} et le reperd sur les ${pr.map((c) => c.lib).join(" et ")}.` : ""));
  }

  // 5. Deux côtés / arbitrage
  const deux = ms.filter((m) => m.deux && m.combine != null);
  if (deux.length >= 5 && deux.length >= 0.25 * n) {
    const sous = deux.filter((m) => m.combine < 1).length;
    const pd = deux.reduce((x, m) => x + m.pnl, 0);
    C(80, `Il achète les deux côtés sur ${deux.length} marchés, prix combiné médian ${px(med(deux.map((m) => m.combine)))}, sous 1 $ dans ${sous} cas. Résultat de ces marchés : ${usd(pd)}. ${med(deux.map((m) => m.combine)) < 1 ? "C'est de l'arbitrage : la paire vaut 1 $ quel que soit le gagnant." : "Payée plus de 1 $, la paire ne rapporte que si un côté est revendu à temps."}`);
  }

  // 6. Revente avant la fin
  const rev = ms.filter((m) => m.revend);
  if (rev.length >= 5 && rev.length >= 0.25 * n) {
    const pr = rev.reduce((x, m) => x + m.pnl, 0);
    C(70, `Sur ${rev.length} marchés il revend avant le résultat (trading des variations de prix) : ${usd(pr)} au total sur ces marchés, contre ${usd(pnl - pr)} sur ceux qu'il garde jusqu'au bout.`);
  }

  // 7. Moment d'entrée
  const av = ms.filter((m) => m.avantFin != null && m.avantFin >= 0).map((m) => m.avantFin);
  if (av.length >= 5 && !ramasseur) {
    const md = med(av);
    C(60, `Il entre en médiane <b>${dur(md)} avant la fin</b> du marché` + (md < 30 ? " : trop tard pour être suivi à la main." : md < 120 ? " : suivable seulement par un automate." : " : assez tôt pour être suivi.") );
  }

  // 8. Côté préféré
  const up = simples.filter((m) => m.cote === 0), dn = simples.filter((m) => m.cote === 1);
  if (simples.length >= 15 && Math.max(up.length, dn.length) >= 0.75 * simples.length) {
    const l = up.length > dn.length ? up : dn, nom = up.length > dn.length ? "Up" : "Down";
    C(55, `Il joue presque toujours <b>${nom}</b> (${l.length} paris sur ${simples.length}), gagnant ${l.filter((m) => m.coteGagne).length} fois. Ses gains dépendent donc de la tendance du BTC sur la période.`);
  }

  // 9. Taille des mises : grosses mises mieux choisies ?
  if (simples.length >= 20) {
    const s = [...simples].sort((a, b) => b.cout - a.cout);
    const q = Math.max(5, Math.floor(s.length / 4));
    const gros = s.slice(0, q), petits = s.slice(-q);
    const rg = gros.reduce((x, m) => x + m.pnl, 0) / gros.reduce((x, m) => x + m.cout, 0);
    const rp = petits.reduce((x, m) => x + m.pnl, 0) / petits.reduce((x, m) => x + m.cout, 0);
    if (Math.abs(rg - rp) > 0.1) C(50, `Ses ${q} plus grosses mises (médiane ${usd(med(gros.map((m) => m.cout)))}) font un ROI de ${pc(rg)}, ses ${q} plus petites ${pc(rp)} : ${rg > rp ? "ses grosses mises sont mieux choisies : la taille de sa mise est un signal." : rg < 0 ? "il perd quand il mise gros." : "ses grosses mises rapportent moins que les petites."}`);
  }

  // 10. Stabilité dans le temps
  if (n >= 20) {
    const h = Math.floor(n / 2);
    const r = (l) => l.reduce((x, m) => x + m.pnl, 0) / l.reduce((x, m) => x + m.cout, 0);
    const r1 = r(ms.slice(0, h)), r2 = r(ms.slice(h));
    C(65, `Première moitié de la période (jusqu'au ${jour(ms[h - 1].ts)}) : ROI ${pc(r1)} ; seconde moitié : ${pc(r2)}.` + (r1 > 0 && r2 > 0 ? " Gagnant sur les deux : le résultat tient dans le temps." : r1 > 0 && r2 <= 0 ? " <b>Il a cessé de gagner récemment.</b>" : r1 <= 0 && r2 > 0 ? " Il gagne seulement depuis peu." : " Perdant sur les deux moitiés."));
  }

  // 11. Pire série
  if (n >= 15) {
    let cum = 0, haut = 0, dd = 0, serie = 0, pire = 0;
    for (const m of ms) { cum += m.pnl; haut = Math.max(haut, cum); dd = Math.min(dd, cum - haut); serie = m.gagne ? 0 : serie + 1; pire = Math.max(pire, serie); }
    if (dd < 0) C(45, `Pire passage : ${usd(dd)} perdus depuis un sommet, et ${pire} marché${pire > 1 ? "s" : ""} perdu${pire > 1 ? "s" : ""} d'affilée au maximum. C'est ce que tu dois pouvoir encaisser en le copiant.`);
  }

  // 12. Horaires
  const concentreTot = pnl > 0 && n >= 3 && Math.max(...ms.map((m) => m.pnl)) / pnl >= 0.5;
  if (n >= 30 && !concentreTot) {
    const blocs = [[0, 6, "la nuit (0 h–6 h)"], [6, 12, "le matin (6 h–12 h)"], [12, 18, "l'après-midi (12 h–18 h)"], [18, 24, "le soir (18 h–24 h)"]].map(([a, b, lib]) => {
      const l = ms.filter((m) => { const hh = heureZ(m.ts); return hh >= a && hh < b; });
      return { lib, n: l.length, p: l.reduce((x, m) => x + m.pnl, 0) };
    });
    const bmax = blocs.reduce((a, b) => (b.p > a.p ? b : a));
    if (pnl > 0 && bmax.p > 0.7 * pnl && bmax.n < 0.5 * n) C(40, `L'essentiel de son gain (${usd(bmax.p)}) est fait ${bmax.lib}, heure suisse, sur ${bmax.n} marchés.`);
  }

  // 13. Durées
  const types = Object.entries(parType).filter(([, l]) => l.length >= 5);
  if (types.length >= 2) {
    C(40, "Par durée de marché : " + types.map(([t, l]) => `${t} ${l.length} marchés, ${usd(l.reduce((x, m) => x + m.pnl, 0))}`).join(" ; ") + ".");
  }

  // 14. Activité et taille
  const coutMed = med(ms.map((m) => m.cout));
  C(30, `Actif du ${jour(debut)} au ${jour(finP)} : ${n} marchés BTC (${(n / jours).toFixed(1)} par jour), mise médiane ${usd(coutMed)} par marché, ${gagnes} marchés gagnants, PnL ${usd(pnl)} pour ${usd(cout)} misés (ROI ${pc(pnl / cout)}).` + (meta.autres ? ` Il trade aussi d'autres marchés (${meta.autres} trades hors BTC, non comptés).` : "") + (meta.tronque ? " Historique limité par Polymarket aux 10 000 derniers trades." : ""));

  // ─── Titre et verdict, déduits des constats ───
  const z = meilleure ? meilleure.z : 0;
  const mdAv = av.length ? med(av) : null;
  const concentre = pnl > 0 && n >= 3 && Math.max(...ms.map((m) => m.pnl)) / pnl >= 0.5;
  if (ramasseur) out.titre = "Ramasseur d'ordres après la clôture";
  else if (deux.length >= 0.5 * n) out.titre = med(deux.map((m) => m.combine)) < 1 ? "Arbitreur de paires" : "Achète les deux côtés";
  else if (rev.length >= 0.5 * n) out.titre = "Trader intra-marché";
  else if (mFin10.size >= 0.3 * n) out.titre = "Sniper des dernières secondes";
  else if (meilleure) out.titre = `Parieur avec avantage (${meilleure.lib})`;
  else if (lignes.some((l) => l.z >= 2 && l.p > 0 && l.avant >= 60)) out.titre = "Avantage réel mais trop mince pour être copié";
  else if (lignes.some((l) => l.z >= 2 && l.p > 0)) out.titre = "Bat le prix, mais trop tard pour être suivi";
  else if (concentre) out.titre = "Un gros coup, le reste au hasard";
  else out.titre = pnl > 0 ? "Gagnant sans avantage démontré" : "Perdant";

  if (n < 20) out.verdict = `Ne pas copier pour l'instant : ${n} marchés, c'est trop peu pour séparer le talent de la chance.`;
  else if (ramasseur) out.verdict = "Non copiable : il n'anticipe rien, il achète un résultat déjà connu. Il faut un automate plus rapide que lui sur les mêmes ordres oubliés, et les quantités disponibles sont minuscules.";
  else if (out.titre === "Arbitreur de paires") out.verdict = "Non copiable : l'arbitrage disparaît dès qu'il a pris les prix ; en le suivant tu achètes plus cher.";
  else if (concentre) out.verdict = "Non : ses résultats reposent sur un seul marché. Rien ne dit qu'il saura le refaire.";
  else if (meilleure) {
    const m = meilleure, roiT = m.p / m.c, marge = (m.ok - m.att) / m.n;
    out.copiable = true;
    out.verdict = `Oui, mais <b>seulement quand sa première entrée est ${m.lib}</b> : bon côté ${m.ok} fois sur ${m.n} quand le prix en annonçait ${Math.round(m.att)}, ROI ${pc(roiT)} sur ces marchés en reproduisant tout ce qu'il fait ensuite, entrée médiane ${dur(m.avant)} avant la fin. `
      + (pnl < 0.5 * m.p ? `Ne copie pas le reste : son résultat global n'est que de ${usd(pnl)} (ROI ${pc(pnl / cout)}) parce qu'il perd ${usd(Math.abs(pnl - m.p))} sur ses autres marchés. ` : "")
      + `Son avance sur le prix est de ${Math.round(marge * 100)} points : chaque centime payé en plus par part en mange un. En achetant au plus ${Math.max(1, Math.floor(marge * 100 / 2))} centimes au-dessus de son prix, tu gardes au moins la moitié de son avance.`
      + (m.couverts > 0.2 * m.n ? ` Attention : sur ${m.couverts} de ces ${m.n} marchés il agit encore après son entrée (achat de l'autre côté ou revente) ; ce résultat suppose de reproduire aussi ces gestes.` : "");
  } else if (lignes.some((l) => l.z >= 2 && l.p > 0 && l.avant >= 60)) {
    const l = lignes.filter((x) => x.z >= 2 && x.p > 0 && x.avant >= 60).sort((a, b) => b.marge - a.marge)[0];
    out.verdict = `Non en pratique : sa première entrée ${l.lib} bat bien le prix, mais de ${Math.round(l.marge * 100)} point${l.marge >= 0.015 ? "s" : ""} seulement (ROI ${pc(l.p / l.c)}). En le copiant quelques secondes plus tard, tu paierais ${l.marge < 0.02 ? "au moins un centime" : "quelques centimes"} de plus par part, ce qui suffit à effacer son avance.`;
  } else if (lignes.some((l) => l.z >= 2 && l.p > 0)) out.verdict = "Non : il bat le prix du marché, mais uniquement sur des achats pris dans la dernière minute, quand le résultat est presque connu. Impossible à suivre sans être aussi rapide que lui.";
  else if (mdAv != null && mdAv < 30) out.verdict = "Non à la main : il entre trop près de la fin pour qu'on ait le temps de le suivre.";
  else out.verdict = pnl > 0 ? "Pas convaincant : il gagne, mais aucune de ses catégories de paris ne bat le prix du marché au-delà du hasard." : "Non : il perd de l'argent sur la période étudiée.";

  out.constats.sort((a, b) => b.poids - a.poids);
  out.meilleure = meilleure ? { lib: meilleure.lib, n: meilleure.n, marge: meilleure.marge, roi: meilleure.p / meilleure.c, p: meilleure.p, avant: meilleure.avant } : null;
  out.pnl = pnl; out.roi = cout ? pnl / cout : null;
  return out;
}

function esc(s) { return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
