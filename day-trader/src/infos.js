// Nouvelles (trader-news), résultats trimestriels SEC (trader-analyst), achats/ventes du Congrès (trader-pelosi),
// alertes de prix (trader-alerts). Les titres sont des pistes, pas des faits : ouvre l'article avant d'agir.
import { UA, yahoo, spark, graphique } from "./donnees.js";
import { local, marcheDe, estBtc, symYahoo, seance, hhmm, MARCHES } from "./temps.js";

const dec = (s) => String(s || "").replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").trim();
const balise = (xml, b) => { const m = new RegExp(`<${b}[^>]*>([\\s\\S]*?)</${b}>`).exec(xml); return m ? dec(m[1]) : ""; };

// ------------------------------------------------------------- nouvelles
const MOTS = { resultats: /earnings|results|quarter|guidance|revenue|profit|eps/i, deal: /merger|acquir|deal|buyout|takeover/i, analyste: /upgrade|downgrade|price target|rating/i, justice: /lawsuit|sec probe|investigation|recall|fraud/i, dirigeants: /ceo|cfo|resign|appoint|steps down/i };
function etiquettes(t) { return Object.entries(MOTS).filter(([, rx]) => rx.test(t)).map(([k]) => k); }

async function titresRss(sym) {
  const r = await fetch(`https://feeds.finance.yahoo.com/rss/2.0/headline?s=${encodeURIComponent(symYahoo(sym))}&region=US&lang=en-US`, { headers: { "User-Agent": UA } });
  if (r.status !== 200) throw new Error("RSS HTTP " + r.status);
  const xml = await r.text();
  return xml.split("<item>").slice(1).map((it) => ({ titre: balise(it, "title"), lien: balise(it, "link"), date: Date.parse(balise(it, "pubDate")) || null, source: "Yahoo Finance" }));
}
async function titresRecherche(sym) {
  const d = await yahoo(`/v1/finance/search?q=${encodeURIComponent(symYahoo(sym))}&newsCount=15&quotesCount=0`);
  return (d.news || []).map((n) => ({ titre: n.title, lien: n.link, date: n.providerPublishTime ? n.providerPublishTime * 1000 : null, source: n.publisher || "Yahoo" }));
}
export async function nouvelles(symboles, heures = 24, uaSec = "") {
  const out = [];
  for (const sym of symboles.slice(0, 15)) {
    const bloc = { symbol: sym, titres: [], depots: [], mouvement: null, erreurs: [] };
    try { bloc.titres = await titresRss(sym); } catch (e) { try { bloc.titres = await titresRecherche(sym); } catch (e2) { bloc.erreurs.push("titres : " + (e2.message || e2)); } }
    const limite = Date.now() - heures * 3600e3;
    bloc.titres = bloc.titres.filter((t) => !t.date || t.date >= limite).sort((a, b) => (b.date || 0) - (a.date || 0)).slice(0, 12)
      .map((t) => ({ ...t, heureNY: t.date ? fmt(t.date, MARCHES.actions) : "", tags: etiquettes(t.titre) }));
    try {
      const s = await graphique(sym, "1d", "5m"); const m = s.meta;
      if (m.regularMarketPrice && m.chartPreviousClose) bloc.mouvement = { prix: m.regularMarketPrice, veille: m.chartPreviousClose, pct: +(100 * (m.regularMarketPrice / m.chartPreviousClose - 1)).toFixed(2) };
    } catch (e) { bloc.erreurs.push("cours : " + (e.message || e)); }
    if (!estBtc(sym)) {
      if (!uaSec) bloc.erreurs.push("dépôts SEC (8-K) : la SEC exige un nom et un e-mail de contact (réglage « Contact SEC »)");
      else try { bloc.depots = await depots8k(sym, uaSec, heures); } catch (e) { bloc.erreurs.push("SEC : " + (e.message || e)); }
    }
    out.push(bloc);
  }
  return out;
}
function fmt(ms, m) { const l = local(ms, m); return `${l.date} ${hhmm(l.min)}`; }

// ------------------------------------------------------------- SEC
async function sec(url, ua) {
  const r = await fetch(url, { headers: { "User-Agent": ua, Accept: "application/json" } });
  if (r.status === 404) throw new Error("la SEC n'a pas de données à cette adresse");
  if (r.status !== 200) throw new Error(`la SEC a répondu HTTP ${r.status}`);
  return r.json();
}
let CACHE_TICKERS = null;
async function cik(sym, ua) {
  if (!CACHE_TICKERS) CACHE_TICKERS = await sec("https://www.sec.gov/files/company_tickers.json", ua);
  const s = sym.toUpperCase().replace(".", "-");
  for (const v of Object.values(CACHE_TICKERS)) if (String(v.ticker).toUpperCase() === s) return { cik: String(v.cik_str).padStart(10, "0"), nom: v.title };
  throw new Error(`${sym} introuvable dans la liste de la SEC`);
}
async function depots8k(sym, ua, heures) {
  const c = await cik(sym, ua);
  const sub = await sec(`https://data.sec.gov/submissions/CIK${c.cik}.json`, ua);
  const r = sub.filings.recent; const out = [];
  const limite = new Date(Date.now() - Math.max(heures, 72) * 3600e3).toISOString().slice(0, 10);
  for (let i = 0; i < r.form.length && out.length < 5; i++) {
    if (r.form[i] !== "8-K" || r.filingDate[i] < limite) continue;
    const acc = r.accessionNumber[i].replace(/-/g, "");
    out.push({ date: r.filingDate[i], items: r.items ? r.items[i] : "", lien: `https://www.sec.gov/Archives/edgar/data/${+c.cik}/${acc}/${r.primaryDocument[i]}` });
  }
  return out;
}

const CONCEPTS = {
  revenu: ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "RevenuesNetOfInterestExpense", "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "SalesRevenueGoodsNet", "SalesRevenueServicesNet"],
  cout: ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold"],
  margeBrute: ["GrossProfit"], resultatOp: ["OperatingIncomeLoss"],
  resultatNet: ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"],
  bpa: ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"],
};
const jours = (a, b) => Math.round((Date.parse(b) - Date.parse(a)) / 864e5);
function trimestres(faits) {
  const dernier = {}, premier = {};
  for (const f of faits) {
    if (!f.start || !["10-Q", "10-K", "20-F", "40-F"].includes(String(f.form || "").split("/")[0])) continue;
    const k = f.start + "|" + f.end; const st = (f.filed || "") + (f.accn || "");
    if (!dernier[k] || st > (dernier[k].filed || "") + (dernier[k].accn || "")) dernier[k] = f;
    if (!premier[k] || st < (premier[k].filed || "") + (premier[k].accn || "")) premier[k] = f;
  }
  const q = {}, ans = [];
  for (const [k, f] of Object.entries(dernier)) {
    const [s, e] = k.split("|"); const d = jours(s, e);
    if (d >= 80 && d <= 100) q[e] = { valeur: f.val, debut: s, fin: e, derive: false, fy: premier[k].fy, fp: premier[k].fp, depose: f.filed };
    else if (d >= 350 && d <= 380) ans.push([s, e, f, premier[k]]);
  }
  for (const [s, e, f, p] of ans) {
    if (q[e]) continue;
    const dedans = Object.values(q).filter((v) => v.debut >= s && v.fin < e).sort((a, b) => a.fin.localeCompare(b.fin));
    if (dedans.length !== 3) continue;
    q[e] = { valeur: f.val - dedans.reduce((a, v) => a + v.valeur, 0), debut: dedans[2].fin, fin: e, derive: true, fy: p.fy, fp: "Q4", depose: f.filed };
  }
  return q;
}
export async function analyste(sym, ua, nb = 6) {
  if (!ua) throw new Error("La SEC exige un nom et un e-mail de contact : remplis le réglage « Contact SEC ».");
  if (estBtc(sym)) throw new Error("Le BTC n'a pas de comptes trimestriels à la SEC.");
  const c = await cik(sym, ua);
  const cf = await sec(`https://data.sec.gov/api/xbrl/companyfacts/CIK${c.cik}.json`, ua);
  const s = {};
  for (const [cle, liste] of Object.entries(CONCEPTS)) {
    const unite = cle === "bpa" ? "USD/shares" : "USD"; const fus = {};
    for (const con of liste) {
      const node = ((cf.facts || {})["us-gaap"] || {})[con]; if (!node) continue;
      const u = node.units[unite] ? unite : Object.keys(node.units)[0];
      const q = trimestres(node.units[u] || []);
      for (const [e, v] of Object.entries(q)) if (!fus[e]) fus[e] = v;
    }
    s[cle] = fus;
  }
  const yoy = (serie, fin) => { const cible = Date.parse(fin) - 365 * 864e5; let best = null; for (const e of Object.keys(serie)) { const g = Math.abs((Date.parse(e) - cible) / 864e5); if (g <= 10 && (!best || g < best[0])) best = [g, e]; } return best ? serie[best[1]].valeur : null; };
  const pc = (a, b) => (a == null || !b ? null : +(100 * (a - b) / Math.abs(b)).toFixed(1));
  const mg = (p, w) => (p == null || !w ? null : +(100 * p / w).toFixed(1));
  const fins = [...new Set([...Object.keys(s.revenu), ...Object.keys(s.resultatNet)])].sort().reverse().slice(0, nb);
  if (!fins.length) throw new Error("pas de revenu ni de résultat net trimestriel dans les données XBRL");
  const lignes = fins.map((e) => {
    const r = s.revenu[e]?.valeur ?? null; let mb = s.margeBrute[e]?.valeur ?? null;
    if (mb == null && r != null && s.cout[e]) mb = r - s.cout[e].valeur;
    const op = s.resultatOp[e]?.valeur ?? null, net = s.resultatNet[e]?.valeur ?? null, bpa = s.bpa[e]?.valeur ?? null;
    const base = s.revenu[e] || s.resultatNet[e] || {};
    return { fin: e, periode: `${base.fp || ""} ${base.fy || ""}`.trim(), derive: !!(s.revenu[e]?.derive || s.resultatNet[e]?.derive), revenu: r, resultatNet: net, bpa: bpa != null ? +bpa.toFixed(2) : null,
      margeBrute: mg(mb, r), margeOp: mg(op, r), margeNette: mg(net, r), revenuSurUnAn: pc(r, yoy(s.revenu, e)), netSurUnAn: pc(net, yoy(s.resultatNet, e)), bpaSurUnAn: pc(bpa, yoy(s.bpa, e)), depose: base.depose };
  });
  return { symbol: sym.toUpperCase(), nom: cf.entityName || c.nom, cik: c.cik, lignes, note: "Chiffres seulement : cet outil ne dit jamais si une action est à acheter. Le T4 est déduit (année − 3 trimestres) et marqué « déduit »." };
}

// ------------------------------------------------------------- Congrès (Chambre des représentants)
async function dezip(buf, voulu) {
  const v = new DataView(buf); let p = buf.byteLength - 22;
  while (p >= 0 && v.getUint32(p, true) !== 0x06054b50) p--;
  if (p < 0) throw new Error("ZIP illisible");
  let cd = v.getUint32(p + 16, true); const n = v.getUint16(p + 10, true);
  for (let i = 0; i < n; i++) {
    const meth = v.getUint16(cd + 10, true), taille = v.getUint32(cd + 20, true), ln = v.getUint16(cd + 28, true), le = v.getUint16(cd + 30, true), lc = v.getUint16(cd + 32, true), off = v.getUint32(cd + 42, true);
    const nom = new TextDecoder().decode(new Uint8Array(buf, cd + 46, ln));
    if (nom.toLowerCase().endsWith(voulu)) {
      const debut = off + 30 + v.getUint16(off + 26, true) + v.getUint16(off + 28, true);
      const brut = new Uint8Array(buf, debut, taille);
      if (meth === 0) return new TextDecoder().decode(brut);
      const flux = new Blob([brut]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
      return await new Response(flux).text();
    }
    cd += 46 + ln + le + lc;
  }
  throw new Error("fichier " + voulu + " absent du ZIP");
}
export async function congres({ annee = new Date().getUTCFullYear(), membre = "", depuis = "" } = {}) {
  const r = await fetch(`https://disclosures-clerk.house.gov/public_disc/financial-pdfs/${annee}FD.zip`, { headers: { "User-Agent": UA } });
  if (r.status !== 200) throw new Error(`la Chambre a répondu HTTP ${r.status}`);
  const xml = await dezip(await r.arrayBuffer(), ".xml");
  const m = (membre || "").toLowerCase().trim();
  const out = [];
  for (const bloc of xml.split("<Member>").slice(1)) {
    if (balise(bloc, "FilingType") !== "P") continue;
    const nom = [balise(bloc, "First"), balise(bloc, "Last")].join(" ").trim();
    if (m && !nom.toLowerCase().includes(m)) continue;
    const dt = balise(bloc, "FilingDate"); const [mm, jj, aa] = dt.split("/"); const iso = aa ? `${aa}-${mm.padStart(2, "0")}-${jj.padStart(2, "0")}` : dt;
    if (depuis && iso < depuis) continue;
    const doc = balise(bloc, "DocID");
    out.push({ membre: [balise(bloc, "Prefix"), nom, balise(bloc, "Suffix")].join(" ").trim(), circonscription: balise(bloc, "StateDst"), depose: iso, docId: doc, pdf: `https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/${annee}/${doc}.pdf` });
  }
  out.sort((a, b) => b.depose.localeCompare(a.depose));
  return { annee, nombre: out.length, rapports: out.slice(0, 300), note: "Déclarations publiques (STOCK Act), déposées jusqu'à 45 jours après le trade ; montants en fourchettes. Ce n'est pas une information privilégiée. Chambre seulement (le Sénat exige une acceptation manuelle)." };
}

// ------------------------------------------------------------- alertes de prix
export async function verifierAlertes(alertes, maintenantMs = Date.now()) {
  const actives = alertes.filter((a) => !a.sonneeLe || a.type === "pct" || a.type === "heure");
  const syms = [...new Set(actives.filter((a) => a.symbol).map((a) => a.symbol))];
  const cours = {};
  for (let i = 0; i < syms.length; i += 20) {
    try { const d = await spark(syms.slice(i, i + 20), "1d", "5m"); for (const [k, s] of Object.entries(d)) cours[k] = { prix: s.meta.regularMarketPrice, veille: s.meta.chartPreviousClose ?? s.meta.previousClose }; } catch (e) { /* on retentera à la minute suivante */ }
  }
  const sonnees = [];
  for (const a of alertes) {
    const m = a.symbol ? marcheDe(a.symbol) : MARCHES.actions; const l = local(maintenantMs, m);
    if (a.date && a.date !== l.date) continue;
    const c = a.symbol ? cours[a.symbol] : null;
    let sonne = false, texte = "";
    if (a.type === "dessus" && c && !a.sonneeLe) { sonne = c.prix >= a.prix; texte = `${a.symbol} à ${c.prix} ≥ ${a.prix}`; }
    else if (a.type === "dessous" && c && !a.sonneeLe) { sonne = c.prix <= a.prix; texte = `${a.symbol} à ${c.prix} ≤ ${a.prix}`; }
    else if (a.type === "pct" && c && c.veille && a.jourSonne !== l.date) { const p = 100 * (c.prix / c.veille - 1); sonne = Math.abs(p) >= a.pct; texte = `${a.symbol} ${p >= 0 ? "+" : ""}${p.toFixed(2)} % depuis la veille`; if (sonne) a.jourSonne = l.date; }
    else if (a.type === "heure" && a.jourSonne !== l.date) { const se = seance(l.date, m); const h = +a.heure.slice(0, 2) * 60 + +a.heure.slice(3); sonne = !!se && l.min >= h; texte = `${a.libelle || "heure"} : ${a.heure} (${m.tz})`; if (sonne) a.jourSonne = l.date; }
    else if (a.type === "ouverture" && a.jourSonne !== l.date) { const se = seance(l.date, m); sonne = !!se && l.min >= se[0]; texte = "La Bourse de New York vient d'ouvrir"; if (sonne) a.jourSonne = l.date; }
    if (c) a.dernierPrix = c.prix;
    if (sonne) { a.sonneeLe = new Date(maintenantMs).toISOString(); a.texte = texte; sonnees.push({ id: a.id, texte, quand: a.sonneeLe }); }
  }
  return sonnees;
}
