// Barrières — MODE FANTÔME (aucun ordre réel).
// Compare les paliers Polymarket « Bitcoin/Ethereum descend à X / atteint X » (options à barrière, payées dès que le prix TOUCHE le niveau)
// au prix des options Deribit, et suit des trades fictifs COUVERTS.
//
// Couverture (principe de réflexion) : un palier qui paie 1 $ au toucher ≈ 2 digitales européennes au même niveau.
// Une digitale est reconstruite par un écart d'options Deribit (put spread pour « descend à », call spread pour « atteint »).
// Au moment où le prix touche le niveau, la digitale vaut environ 0,5 → 2 digitales ≈ 1 $ : on débouclera la couverture À CE MOMENT-LÀ.
// Risques résiduels mesurés (rien n'est supposé parfait) :
//   1. le prix touche puis la couverture ne vaut pas exactement 1 $ (pente de volatilité, temps restant, retard jusqu'au relevé suivant) ;
//   2. l'échéance Deribit n'est pas exactement la fin du palier Polymarket (décalage en heures affiché) ;
//   3. Polymarket règle sur Binance BTC/USDT (bougie 1 min), la détection ici se fait sur le perpétuel Deribit + le prix Polymarket ;
//   4. tous les frais (Polymarket taker, Deribit à l'ouverture ET à la fermeture) et les écarts achat/vente sont payés aux vrais carnets.
const VERSION = "1.0.1";

// Règles proposées — Pitch décide, modifiables ici
const R = {
  parts: 1000,          // taille fictive : 1000 parts Polymarket = 1000 $ payés si gagnant
  ratio: 2,             // 2 digitales par part (principe de réflexion)
  seuil: 0.03,          // ouvrir seulement si le gain attendu APRÈS tous les frais ≥ 3 points (30 $ pour 1000 parts)
  decalageMaxH: 96,     // échéance Deribit au plus 4 jours après la fin du palier
  ecartStrikeMax: 0.01, // milieu des deux strikes à moins de 1 % du niveau
  largeurMax: 0.05,     // écart entre les deux strikes ≤ 5 % du niveau (sinon la digitale reconstruite est trop grossière)
  prixMin: 0.02, prixMax: 0.98,
  maxNouveaux: 5,       // nouveaux trades par relevé (limite d'appels)
};
const FEE_DERIBIT = 0.0003, PLAFOND_DERIBIT = 0.125; // par contrat et par jambe, plafonné à 12,5 % du prix
const G = "https://gamma-api.polymarket.com", C = "https://clob.polymarket.com", D = "https://www.deribit.com/api/v2/public";
const MOIS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"];
const MOIS_D = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const ACTIFS = { BTC: "bitcoin", ETH: "ethereum" };

async function j(url, init) {
  const r = await fetch(url, { ...init, headers: { "user-agent": "barrieres/1", "content-type": "application/json", ...(init?.headers || {}) } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} ${url.slice(0, 80)} ${t.slice(0, 100)}`);
  return JSON.parse(t);
}
const N = (x) => { const t = 1 / (1 + 0.2316419 * Math.abs(x)); const d = 0.3989423 * Math.exp(-x * x / 2); const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))); return x > 0 ? 1 - p : p; };
// Probabilité de toucher la barrière avant T (mouvement brownien géométrique, sans dérive de taux)
function pToucher(S, B, sig, T) {
  if (T <= 0 || sig <= 0) return 0;
  const x = Math.log(B / S), nu = -sig * sig / 2, s = sig * Math.sqrt(T), k = Math.exp(2 * nu * x / (sig * sig));
  return B < S ? Math.min(1, N((x - nu * T) / s) + k * N((x + nu * T) / s)) : Math.min(1, N((-x + nu * T) / s) + k * N((-x - nu * T) / s));
}
const fraisPoly = (p, rate) => rate * p * (1 - p);
const echeanceMs = (e) => { const m = e.match(/^(\d{1,2})([A-Z]{3})(\d{2})$/); return m ? Date.UTC(2000 + +m[3], MOIS_D.indexOf(m[2]), +m[1], 8) : null; };

// Prix moyen pour acheter n parts en remontant le carnet (asks) ; null si pas assez de profondeur
function prixPour(asks, n) {
  let reste = n, cout = 0;
  for (const a of [...asks].sort((x, y) => x.price - y.price)) { const q = Math.min(reste, a.size); cout += q * a.price; reste -= q; if (reste <= 1e-9) return cout / n; }
  return null;
}

// ---------- 1. Paliers Polymarket
async function paliers() {
  const now = new Date(), slugs = new Set();
  for (const [, nom] of Object.entries(ACTIFS)) for (const dm of [0, 1]) {
    const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + dm, 1));
    slugs.add(`what-price-will-${nom}-hit-in-${MOIS[d.getUTCMonth()]}-${d.getUTCFullYear()}`);
  }
  for (const nom of Object.values(ACTIFS)) {
    try {
      const r = await j(`${G}/public-search?q=${encodeURIComponent("What price will " + nom + " hit")}&events_status=active&limit_per_type=20`);
      for (const e of r.events || []) if (e.slug?.startsWith(`what-price-will-${nom}-hit`) && !e.closed) slugs.add(e.slug);
    } catch (e) { }
  }
  const out = [];
  for (const s of [...slugs].slice(0, 14)) {
    let ev; try { ev = (await j(`${G}/events?slug=${s}`))[0]; } catch (e) { continue; }
    if (!ev) continue;
    for (const m of ev.markets || []) {
      const q = m.question || "", mm = q.match(/Will (Bitcoin|Ethereum) (dip to|reach) \$([\d,.]+)/i);
      if (!mm || m.closed || !m.acceptingOrders && m.acceptingOrders !== undefined) continue;
      const tk = JSON.parse(m.clobTokenIds || "[]"), fin = Date.parse(m.endDate);
      if (tk.length < 2 || !(fin > Date.now() + 3600e3)) continue;
      out.push({ actif: mm[1].toLowerCase() === "bitcoin" ? "BTC" : "ETH", sens: mm[2].toLowerCase() === "dip to" ? "bas" : "haut", niveau: +mm[3].replace(/,/g, ""),
        fin, yes: tk[0], no: tk[1], rate: m.feeSchedule?.rate ?? 0.07, slug: m.slug, question: q, evenement: ev.slug });
    }
  }
  return out;
}

async function carnets(tokens) {
  const res = {};
  for (let i = 0; i < tokens.length; i += 200) {
    const r = await j(`${C}/books`, { method: "POST", body: JSON.stringify(tokens.slice(i, i + 200).map((t) => ({ token_id: t }))) });
    for (const b of r) res[b.asset_id] = { bids: (b.bids || []).map((x) => ({ price: +x.price, size: +x.size })), asks: (b.asks || []).map((x) => ({ price: +x.price, size: +x.size })) };
  }
  return res;
}

// ---------- 2. Options Deribit
async function options(actif) {
  const r = await j(`${D}/get_book_summary_by_currency?currency=${actif}&kind=option`);
  const par = {};
  for (const o of r.result || []) {
    const [, ech, k, t] = o.instrument_name.split("-");
    (par[ech] ??= { ms: echeanceMs(ech), P: {}, C: {}, F: o.underlying_price, S: o.estimated_delivery_price })[t][+k] = o;
  }
  return par;
}

// Choix de l'écart d'options qui reconstruit la digitale au niveau B
function choisirEcart(par, p) {
  const ech = Object.entries(par).filter(([, e]) => e.ms && e.ms >= p.fin).sort((a, b) => a[1].ms - b[1].ms)[0];
  if (!ech) return null;
  const [nom, e] = ech, decalageH = (e.ms - p.fin) / 3600e3;
  const t = p.sens === "bas" ? "P" : "C", ks = Object.keys(e[t]).map(Number).sort((a, b) => a - b);
  let best = null;
  for (let i = 0; i < ks.length - 1; i++) for (let k = i + 1; k < Math.min(ks.length, i + 4); k++) {
    const mil = (ks[i] + ks[k]) / 2, d = Math.abs(mil - p.niveau) / p.niveau;
    if (d <= R.ecartStrikeMax && (ks[k] - ks[i]) / p.niveau <= R.largeurMax && (!best || d < best.d - 1e-9 || (Math.abs(d - best.d) < 1e-9 && ks[k] - ks[i] < best.dk))) best = { bas: ks[i], haut: ks[k], d, dk: ks[k] - ks[i] };
  }
  if (!best) return null;
  const ob = e[t][best.bas], oh = e[t][best.haut];
  // jambe « riche » = la plus chère : put au strike haut, call au strike bas
  const riche = t === "P" ? oh : ob, pauvre = t === "P" ? ob : oh;
  if (!(riche.bid_price > 0 && riche.ask_price > 0 && pauvre.ask_price > 0)) return null;
  return { echeance: nom, decalageH, t, kBas: best.bas, kHaut: best.haut, dk: best.dk, F: e.F || riche.underlying_price, S: e.S, riche, pauvre,
    iv: (ob.mark_iv + oh.mark_iv) / 200 };
}

const fraisJambe = (prixBtc) => Math.min(FEE_DERIBIT, PLAFOND_DERIBIT * Math.max(prixBtc, 0)); // en unité de l'actif par contrat

// Gain attendu par part (1 $ payé) pour les deux stratégies couvertes, aux vrais prix
function evaluer(p, e, yesAsk, noAsk) {
  const u = R.ratio / e.dk;                                // contrats Deribit par part et par jambe
  const fr = 2 * u * e.F * (fraisJambe(e.riche.mark_price) + fraisJambe(e.pauvre.mark_price)); // ouverture + fermeture
  const recu = u * e.F * ((e.riche.bid_price || 0) - e.pauvre.ask_price);   // vendre 2 digitales
  const paye = u * e.F * (e.riche.ask_price - (e.pauvre.bid_price || 0));    // acheter 2 digitales
  const netAchat = yesAsk == null ? null : recu - (yesAsk + fraisPoly(yesAsk, p.rate)) - fr;   // acheter le palier OUI + vendre la couverture
  const netVente = noAsk == null ? null : 1 - (noAsk + fraisPoly(noAsk, p.rate)) - paye - fr;  // acheter le NON + acheter la couverture
  const pOptions = u * e.F * (e.riche.mark_price - e.pauvre.mark_price);
  return { netAchat, netVente, pOptions, coutCouv: fr + u * e.F * ((e.riche.ask_price - (e.riche.bid_price || 0)) + (e.pauvre.ask_price - (e.pauvre.bid_price || 0))) / 2 };
}

// ---------- 3. Toucher : plus bas / plus haut du perpétuel Deribit (1 min) depuis le dernier relevé
async function extremes(actif, depuis) {
  const r = await j(`${D}/get_tradingview_chart_data?instrument_name=${actif}-PERPETUAL&resolution=1&start_timestamp=${depuis}&end_timestamp=${Date.now()}`);
  const x = r.result || {};
  return { bas: Math.min(...(x.low || [Infinity])), haut: Math.max(...(x.high || [-Infinity])) };
}

async function carnetDeribit(nom) {
  const r = await j(`${D}/get_order_book?instrument_name=${nom}&depth=20`);
  return r.result;
}
// prix moyen pour qte contrats (achat → asks, vente → bids), null si profondeur insuffisante
function prixDeribit(ob, qte, achat) {
  let reste = qte, s = 0;
  for (const [px, q] of (achat ? ob.asks : ob.bids)) { const x = Math.min(reste, q); s += x * px; reste -= x; if (reste <= 1e-9) return s / qte; }
  return null;
}
const nomInstr = (actif, ech, k, t) => `${actif}-${ech}-${k}-${t}`;

// Valeur de la couverture en $ (signe : ce qu'on encaisse) pour ouvrir/fermer, aux vrais carnets
async function couverture(actif, ech, kBas, kHaut, t, contrats, vendreDigitale) {
  const nr = nomInstr(actif, ech, t === "P" ? kHaut : kBas, t), np = nomInstr(actif, ech, t === "P" ? kBas : kHaut, t);
  const [or, op] = await Promise.all([carnetDeribit(nr), carnetDeribit(np)]);
  const pr = prixDeribit(or, contrats, !vendreDigitale), pp = prixDeribit(op, contrats, vendreDigitale);
  if (pr == null || pp == null) return null;
  const F = or.underlying_price || or.index_price;
  const flux = (vendreDigitale ? pr - pp : pp - pr) * contrats * F;
  const frais = contrats * F * (fraisJambe(pr) + fraisJambe(pp));
  return { flux, frais, F, spot: or.index_price };
}

// ---------- Relevé (toutes les 10 min)
async function tick(env) {
  const now = Date.now(), etat = {};
  for (const r of (await env.DB.prepare("SELECT cle, valeur FROM etat").all()).results) etat[r.cle] = r.valeur;
  const journal = [];
  const ps = await paliers();
  const books = await carnets([...new Set(ps.flatMap((p) => [p.yes, p.no]))]);
  const opt = {}, ext = {};
  for (const a of Object.keys(ACTIFS)) {
    try { opt[a] = await options(a); } catch (e) { journal.push("deribit " + a + " " + e.message); }
    try { ext[a] = await extremes(a, +(etat["vu_" + a] || now - 15 * 60e3)); } catch (e) { journal.push("extremes " + a + " " + e.message); }
  }
  const lignes = [], candidats = [];
  for (const p of ps) {
    const e = opt[p.actif] && choisirEcart(opt[p.actif], p);
    const by = books[p.yes], bn = books[p.no];
    const yesAsk = by ? prixPour(by.asks, R.parts) : null, noAsk = bn ? prixPour(bn.asks, R.parts) : null;
    const yesBid = by?.bids?.length ? Math.max(...by.bids.map((x) => x.price)) : null;
    const spot = e?.S;
    const deja = spot && (p.sens === "bas" ? spot <= p.niveau * 1.002 : spot >= p.niveau * 0.998);
    if (!e || deja || yesBid == null || yesBid < R.prixMin || yesBid > R.prixMax) { lignes.push({ p, e: null, raison: !e ? "pas d'options adaptées" : deja ? "déjà au niveau" : "prix hors 2-98 c" }); continue; }
    const v = evaluer(p, e, yesAsk, noAsk), T = (p.fin - now) / (365.25 * 86400e3);
    const pm = pToucher(spot, p.niveau, e.iv, T);
    lignes.push({ p, e, v, yesBid, yesAsk, noAsk, pm });
    await env.DB.prepare("INSERT INTO releves VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(now, p.actif, p.sens, p.niveau, p.fin, p.yes, yesBid, yesAsk, noAsk, spot, e.echeance, e.decalageH, e.kBas, e.kHaut, e.iv, pm, v.pOptions, v.coutCouv, v.netAchat, v.netVente).run();
    if (e.decalageH <= R.decalageMaxH) {
      if (v.netAchat != null && v.netAchat >= R.seuil) candidats.push({ p, e, cote: "OUI", net: v.netAchat, px: yesAsk });
      if (v.netVente != null && v.netVente >= R.seuil) candidats.push({ p, e, cote: "NON", net: v.netVente, px: noAsk });
    }
  }
  // Fermetures
  const ouvertes = (await env.DB.prepare("SELECT * FROM positions WHERE statut='ouverte'").all()).results;
  for (const o of ouvertes) {
    const x = ext[o.actif], l = lignes.find((l) => l.p.yes === o.token_yes);
    const yesBid = books[o.token_yes]?.bids?.length ? Math.max(...books[o.token_yes].bids.map((b) => b.price)) : null;
    let touche = (x && (o.sens === "bas" ? x.bas <= o.niveau : x.haut >= o.niveau)) || (yesBid != null && yesBid >= 0.97);
    let fini = now >= o.fin;
    if (!l && !touche) { // palier disparu de la liste : on lit son règlement officiel chez Polymarket
      try {
        const m = (await j(`${G}/markets?clob_token_ids=${o.token_yes}`))[0];
        if (m?.closed) { const op = JSON.parse(m.outcomePrices || "[]"); if (+op[0] >= 0.99) touche = true; else if (+op[1] >= 0.99) fini = true; }
      } catch (e) { journal.push("reglement " + o.id + " " + e.message); }
    }
    if (!touche && !fini) continue;
    const vendreAvant = o.cote === "OUI"; // OUI : on avait vendu la couverture → on la rachète
    let c;
    try { c = await couverture(o.actif, o.echeance, o.k_bas, o.k_haut, o.sens === "bas" ? "P" : "C", o.contrats, !vendreAvant); } catch (e) { journal.push("fermeture " + o.id + " " + e.message); continue; }
    if (!c) { journal.push("fermeture " + o.id + " : carnet Deribit trop fin, réessai au prochain relevé"); continue; }
    const gagnePoly = touche ? (o.cote === "OUI") : (o.cote === "NON");
    const polySortie = gagnePoly ? o.parts : 0;
    const net = polySortie - o.parts * o.px_poly - o.frais_poly + o.prime_couv + c.flux - o.frais_couv - c.frais;
    await env.DB.prepare("UPDATE positions SET statut='fermee', ferme=?, raison=?, poly_sortie=?, couv_sortie=?, net=?, retard_min=?, spot_sortie=? WHERE id=?")
      .bind(now, touche ? "niveau touché" : "fin du palier sans toucher", polySortie, c.flux - c.frais, net, touche ? (now - +(etat["vu_" + o.actif] || now)) / 60e3 : 0, c.spot, o.id).run();
  }
  // Ouvertures (une seule position par palier et par côté)
  const dejaOuv = new Set((await env.DB.prepare("SELECT token_yes || cote k FROM positions WHERE statut='ouverte'").all()).results.map((r) => r.k));
  let n = 0;
  for (const k of candidats.sort((a, b) => b.net - a.net)) {
    if (n >= R.maxNouveaux || dejaOuv.has(k.p.yes + k.cote)) continue;
    const brut = R.ratio * R.parts / k.e.dk, contrats = k.p.actif === "ETH" ? Math.max(1, Math.round(brut)) : Math.max(0.1, Math.round(brut * 10) / 10); // pas Deribit : 0,1 BTC, 1 ETH
    let c; try { c = await couverture(k.p.actif, k.e.echeance, k.e.kBas, k.e.kHaut, k.e.t, contrats, k.cote === "OUI"); } catch (e) { journal.push("ouverture " + e.message); continue; }
    if (!c) continue;
    const fp = R.parts * fraisPoly(k.px, k.p.rate);
    const attendu = (k.cote === "OUI" ? 0 : R.parts) - R.parts * k.px - fp + c.flux - 2 * c.frais; // vérifié au vrai carnet Deribit
    if (attendu < R.seuil * R.parts) continue;
    await env.DB.prepare("INSERT INTO positions (ouvert, actif, sens, niveau, fin, token_yes, cote, parts, px_poly, frais_poly, echeance, k_bas, k_haut, contrats, prime_couv, frais_couv, net_attendu, spot_entree) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
      .bind(now, k.p.actif, k.p.sens, k.p.niveau, k.p.fin, k.p.yes, k.cote, R.parts, k.px, fp, k.e.echeance, k.e.kBas, k.e.kHaut, contrats, c.flux, c.frais, attendu, c.spot).run();
    n++;
  }
  const dernier = lignes.map((l) => l.e ? { actif: l.p.actif, sens: l.p.sens, niveau: l.p.niveau, fin: l.p.fin, q: l.p.question, ev: l.p.evenement, yesBid: l.yesBid, yesAsk: l.yesAsk, noAsk: l.noAsk, pm: l.pm, po: l.v.pOptions, na: l.v.netAchat, nv: l.v.netVente, ech: l.e.echeance, dec: l.e.decalageH, k: `${l.e.kBas}/${l.e.kHaut}` } : { actif: l.p.actif, sens: l.p.sens, niveau: l.p.niveau, fin: l.p.fin, q: l.p.question, raison: l.raison });
  const maj = [["dernier", JSON.stringify({ t: now, lignes: dernier, journal })], ...Object.keys(ACTIFS).map((a) => ["vu_" + a, String(now)])];
  for (const [k, v] of maj) await env.DB.prepare("INSERT OR REPLACE INTO etat VALUES (?,?)").bind(k, v).run();
  return { paliers: ps.length, evalues: lignes.filter((l) => l.e).length, candidats: candidats.length, ouverts: n, journal };
}

// ---------- Bilan au format de l'étude fantôme
function bilan(fermees, toutes) {
  const res = {};
  for (const cote of ["OUI", "NON"]) {
    const f = fermees.filter((p) => p.cote === cote).sort((a, b) => a.ferme - b.ferme);
    let cum = 0, pic = 0, creux = 0; for (const p of f) { cum += p.net; pic = Math.max(pic, cum); creux = Math.min(creux, cum - pic); }
    const n = f.length, m = n ? cum / n : 0, sd = n > 1 ? Math.sqrt(f.reduce((s, p) => s + (p.net - m) ** 2, 0) / (n - 1)) : 0;
    const t0 = toutes.length ? Math.min(...toutes.map((p) => p.ouvert)) : Date.now(), jours = Math.max(1, (Date.now() - t0) / 86400e3);
    // capital immobilisé : coût Polymarket + pire perte de la couverture (vendue : largeur × contrats ; achetée : prime payée)
    const cap = (p) => p.parts * p.px_poly + p.frais_poly + (p.cote === "OUI" ? Math.max(0, (p.k_haut - p.k_bas) * p.contrats - p.prime_couv) : -p.prime_couv);
    const evts = toutes.filter((p) => p.cote === cote).flatMap((p) => [[p.ouvert, cap(p)], [p.ferme || Infinity, -cap(p)]]).sort((a, b) => a[0] - b[0]);
    let c = 0, cmax = 0; for (const [, d] of evts) { c += d; cmax = Math.max(cmax, c); }
    res[cote] = { n, net: cum, jour: cum / jours, creux, miseMax: cmax, ic: n > 1 ? [cum - 1.96 * sd * Math.sqrt(n), cum + 1.96 * sd * Math.sqrt(n)] : null, ouvertes: toutes.filter((p) => p.cote === cote && p.statut === "ouverte").length };
  }
  return res;
}

const hP = (t) => new Date(t).toLocaleString("fr-CH", { timeZone: "Europe/Zurich", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
const f0 = (x) => x == null ? "—" : Math.round(x).toLocaleString("fr-CH");
const pc = (x) => x == null ? "—" : (x * 100).toFixed(1);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

async function page(env) {
  const d = JSON.parse((await env.DB.prepare("SELECT valeur FROM etat WHERE cle='dernier'").first())?.valeur || '{"lignes":[],"journal":[]}');
  const toutes = (await env.DB.prepare("SELECT * FROM positions ORDER BY ouvert DESC").all()).results;
  const b = bilan(toutes.filter((p) => p.statut === "fermee"), toutes);
  const lv = (d.lignes || []).filter((l) => l.pm != null).sort((a, b) => Math.max(b.na ?? -9, b.nv ?? -9) - Math.max(a.na ?? -9, a.nv ?? -9));
  const ligneB = (nom, x) => `<tr><td>${nom}</td><td>${x.n} (+${x.ouvertes} ouvertes)</td><td>${f0(x.net)}</td><td>${f0(x.jour)}</td><td>${f0(x.creux)}</td><td>${f0(x.miseMax)}</td><td>${x.ic ? f0(x.ic[0]) + " à " + f0(x.ic[1]) : "trop tôt"}</td><td>pas encore</td><td>${x.n < 20 ? "trop tôt" : x.net > 0 && x.ic && x.ic[0] > 0 ? "à discuter" : "Non"}</td></tr>`;
  return `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Barrières (fantôme)</title>
<link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/icon-180.png"><meta name="apple-mobile-web-app-capable" content="yes">
<style>body{font-family:-apple-system,system-ui,sans-serif;background:#12161f;color:#e6e9ef;margin:0;padding:0 10px 30px;font-size:14px}header{position:sticky;top:0;background:#12161f;padding:10px 0;border-bottom:1px solid #2a3142}h1{font-size:18px;margin:0}h2{font-size:16px;margin:22px 0 6px}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border-bottom:1px solid #2a3142;padding:4px;text-align:right;white-space:nowrap}td:first-child,th:first-child{text-align:left}.box{overflow-x:auto}.ok{color:#5fd38d}.ko{color:#ff7b7b}.note{color:#9aa3b5;font-size:12px;line-height:1.5}a{color:#7fb2ff}</style></head>
<body data-app="barrieres-app"><header><h1><a href="/" style="color:inherit;text-decoration:none">Barrières Polymarket ↔ Deribit</a></h1><div class="note">MODE FANTÔME — aucun ordre réel · version ${VERSION} · relevé du ${d.t ? hP(d.t) : "—"} (heure de Paris), toutes les 10 min</div></header>
<h2>Verdict (trades fictifs fermés, frais compris)</h2><div class="box"><table><tr><th>Variante</th><th>Trades</th><th>Gain net $</th><th>Gain/jour $</th><th>Creux max $</th><th>Mise max $</th><th>IC 95 %</th><th>Périodes inédites</th><th>Go / Non</th></tr>
${ligneB("Acheter le OUI + vendre 2 digitales Deribit", b.OUI)}${ligneB("Acheter le NON + acheter 2 digitales Deribit", b.NON)}</table></div>
<h2>Paliers maintenant</h2><div class="note">« Gain attendu » = par 1000 parts, aux vrais carnets Polymarket (1000 parts) et Deribit, tous frais d'ouverture ET de fermeture compris. Trade fictif ouvert si ≥ ${R.seuil * R.parts} $. Proba « options » = prix Deribit de 2 digitales ; proba « modèle » = calcul de toucher avec la volatilité Deribit au niveau.</div>
<div class="box"><table><tr><th>Palier</th><th>Fin</th><th>OUI vente/achat c</th><th>Proba options %</th><th>Proba modèle %</th><th>Gain OUI couvert $</th><th>Gain NON couvert $</th><th>Options (décalage h)</th></tr>
${lv.map((l) => `<tr><td>${l.actif} ${l.sens === "bas" ? "↓" : "↑"} ${f0(l.niveau)}</td><td>${hP(l.fin)}</td><td>${pc(l.yesBid)} / ${pc(l.yesAsk)}</td><td>${pc(l.po)}</td><td>${pc(l.pm)}</td><td class="${l.na >= R.seuil ? "ok" : ""}">${l.na == null ? "—" : f0(l.na * R.parts)}</td><td class="${l.nv >= R.seuil ? "ok" : ""}">${l.nv == null ? "—" : f0(l.nv * R.parts)}</td><td>${l.ech} ${l.k} (${Math.round(l.dec)})</td></tr>`).join("") || "<tr><td>aucun palier évalué pour l'instant</td></tr>"}</table></div>
<h2>Trades fictifs</h2><div class="box"><table><tr><th>Ouvert</th><th>Palier</th><th>Côté</th><th>Prix c</th><th>Couverture</th><th>Attendu $</th><th>Statut</th><th>Raison</th><th>Retard débouclage min</th><th>Net $</th></tr>
${toutes.map((p) => `<tr><td>${hP(p.ouvert)}</td><td>${p.actif} ${p.sens === "bas" ? "↓" : "↑"} ${f0(p.niveau)}</td><td>${p.cote}</td><td>${pc(p.px_poly)}</td><td>${p.contrats} × ${p.echeance} ${p.k_bas}/${p.k_haut}</td><td>${f0(p.net_attendu)}</td><td>${p.statut}</td><td>${p.raison || ""}</td><td>${p.retard_min == null ? "" : p.retard_min.toFixed(0)}</td><td class="${p.net > 0 ? "ok" : p.net < 0 ? "ko" : ""}">${p.net == null ? "" : f0(p.net)}</td></tr>`).join("") || "<tr><td>aucun trade fictif pour l'instant</td></tr>"}</table></div>
<h2>Risques résiduels suivis</h2><div class="note">1. Au toucher, 2 digitales ne valent pas exactement 1 $ (pente de volatilité, temps restant) : l'écart apparaît dans le « Net » de chaque trade fermé.<br>2. Le débouclage se fait au relevé suivant le toucher (jusqu'à 10 min de retard, colonne « Retard »).<br>3. Échéance Deribit ≥ fin du palier, au plus ${R.decalageMaxH} h après ; la couverture est fermée au prix du marché à la fin du palier.<br>4. Polymarket règle sur Binance BTC/USDT (bougie 1 min) ; ici le toucher est détecté sur le perpétuel Deribit ou quand le OUI Polymarket dépasse 97 c.<br>5. Capital : la mise max compte le coût Polymarket + la pire perte possible de la couverture.</div>
${(d.journal || []).length ? `<h2>Journal</h2><div class="note">${d.journal.map(esc).join("<br>")}</div>` : ""}
<script>const v="${VERSION}";try{if(sessionStorage.getItem("v")!==v){sessionStorage.setItem("v",v);}}catch(e){}</script></body></html>`;
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname === "/api/version") return Response.json({ version: VERSION });
    if (u.pathname === "/api/sonde") { try { return Response.json(await tick(env)); } catch (e) { return Response.json({ erreur: e.message }, { status: 500 }); } }
    if (u.pathname === "/api/etat") {
      const d = JSON.parse((await env.DB.prepare("SELECT valeur FROM etat WHERE cle='dernier'").first())?.valeur || "{}");
      const toutes = (await env.DB.prepare("SELECT * FROM positions ORDER BY ouvert DESC").all()).results;
      return Response.json({ version: VERSION, regles: R, dernier: d, positions: toutes, bilan: bilan(toutes.filter((p) => p.statut === "fermee"), toutes) });
    }
    if (u.pathname === "/" || u.pathname === "/index.html") return new Response(await page(env), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store, max-age=0" } });
    return env.ASSETS.fetch(req);
  },
  async scheduled(ev, env, ctx) { ctx.waitUntil(tick(env).catch((e) => console.log("tick", e.message))); },
};
