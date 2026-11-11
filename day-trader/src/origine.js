// Pitch 11.11 : « quand une news est sortie, cherche la première source qui l'a donnée ».
// Pour chaque news vue (SEC ou PR Newswire), 3 min puis 30 min après : on cherche la même news partout
// (Google News = des milliers de sites, Yahoo Finance, Stocktwits) et on garde l'heure de publication de chacun.
// On regarde aussi si l'action bougeait déjà AVANT qu'on voie la news (= une source plus rapide existe).
import { graphique, yahoo, UA } from "./donnees.js";
import { local, MARCHES } from "./temps.js";

export const SCHEMA_ORIGINE = [
  "CREATE TABLE IF NOT EXISTS origine (news_id TEXT, source TEXT, editeur TEXT, titre TEXT, publie INTEGER, lien TEXT, score REAL, PRIMARY KEY (news_id, source, lien))",
  "ALTER TABLE news ADD COLUMN or_n INTEGER", "ALTER TABLE news ADD COLUMN or_premier TEXT", "ALTER TABLE news ADD COLUMN or_premier_ms INTEGER",
  "ALTER TABLE news ADD COLUMN or_bouge_ms INTEGER", "ALTER TABLE news ADD COLUMN or_nb INTEGER",
];
let PRET = false;
export async function schemaOrigine(db) { if (PRET) return; for (const s of SCHEMA_ORIGINE) { try { await db.prepare(s).run(); } catch (e) {} } PRET = true; }

const VIDES = new Set("the a an and or of to in on for with at by from as is are its inc corp corporation company co ltd plc llc group holdings announces announce reports report new will has have".split(" "));
const mots = (t) => new Set(String(t || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter((w) => w.length > 2 && !VIDES.has(w)));
function ressemblance(a, b) { const A = mots(a), B = mots(b); if (!A.size || !B.size) return 0; let c = 0; for (const w of A) if (B.has(w)) c++; return c / Math.min(A.size, B.size); }
const nomCourt = (n) => String(n || "").replace(/\b(inc|corp|corporation|co|ltd|plc|llc|holdings?|group|company|the)\b\.?/gi, "").replace(/[,.]/g, " ").replace(/\s+/g, " ").trim();
const dec = (s) => String(s || "").replace(/<!\[CDATA\[|\]\]>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();

async function googleNews(q) {
  const r = await fetch(`https://news.google.com/rss/search?q=${encodeURIComponent(q)}&hl=en-US&gl=US&ceid=US:en`, { headers: { "User-Agent": NAV, "Accept-Language": "en-US,en;q=0.9" } });
  if (!r.ok) throw new Error("Google News HTTP " + r.status);
  const xml = await r.text(); const out = [];
  for (const it of xml.split("<item>").slice(1)) {
    const g = (b) => dec(((new RegExp(`<${b}[^>]*>([\\s\\S]*?)</${b}>`)).exec(it) || [])[1] || "");
    const editeur = g("source"); const titre = g("title").replace(new RegExp(`\\s+-\\s+${editeur.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`), "");
    out.push({ source: "Google News", editeur, titre, publie: Date.parse(g("pubDate")), lien: g("link") });
  }
  return out;
}
const NAV = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36";
// Bing News : autre agrégateur de milliers de sites (Google News refuse souvent les serveurs Cloudflare)
async function bingNews(q) {
  const r = await fetch(`https://www.bing.com/news/search?q=${encodeURIComponent(q)}&format=rss&qft=sortbydate%3d%221%22`, { headers: { "User-Agent": NAV } });
  if (!r.ok) throw new Error("Bing News HTTP " + r.status);
  const xml = await r.text(); const out = [];
  for (const it of xml.split("<item>").slice(1)) {
    const g = (b) => dec(((new RegExp(`<${b}[^>]*>([\\s\\S]*?)</${b}>`)).exec(it) || [])[1] || "");
    out.push({ source: "Bing News", editeur: g("News:Source") || g("news:Source"), titre: g("title"), publie: Date.parse(g("pubDate")), lien: g("link") });
  }
  return out;
}
async function yahooNews(sym) {
  const j = await yahoo(`/v1/finance/search?q=${encodeURIComponent(sym)}&quotesCount=0&newsCount=25`);
  return (j.news || []).map((x) => ({ source: "Yahoo Finance", editeur: x.publisher || "", titre: x.title || "", publie: (x.providerPublishTime || 0) * 1000, lien: x.link || "" }));
}
async function stocktwits(sym) {
  const r = await fetch(`https://api.stocktwits.com/api/2/streams/symbol/${encodeURIComponent(sym)}.json`, { headers: { "User-Agent": UA } });
  if (!r.ok) throw new Error("Stocktwits HTTP " + r.status);
  const j = await r.json();
  return (j.messages || []).map((m) => ({ source: "Stocktwits", editeur: "@" + ((m.user || {}).username || "?"), titre: String(m.body || "").slice(0, 200), publie: Date.parse(m.created_at), lien: `https://stocktwits.com/message/${m.id}` }));
}

// Première minute où l'action a bougé d'au moins 0,5 % dans les 30 min AVANT qu'on voie la news
async function bougeAvant(sym, vu) {
  const s = await graphique(sym, "5d", "1m"); let ref = null;
  for (let i = 0; i < s.t.length; i++) {
    const ms = s.t[i] * 1000, c = s.c[i]; if (c == null) continue;
    if (ms <= vu - 30 * 60e3) { ref = c; continue; }
    if (ms > vu) break;
    if (ref && Math.abs(c / ref - 1) >= 0.005) return ms;
  }
  return null;
}

export async function tourOrigine(env, maintenant = Date.now()) {
  const db = env.DB; await schemaOrigine(db);
  const l = (await db.prepare(`SELECT * FROM news WHERE vu IS NOT NULL AND vu >= ? AND ((or_n IS NULL AND vu <= ?) OR (or_n = 1 AND vu <= ?)) ORDER BY vu DESC LIMIT 6`)
    .bind(maintenant - 2 * 864e5, maintenant - 3 * 60e3, maintenant - 30 * 60e3).all()).results;
  const st = []; const erreurs = {};
  for (const n of l) {
    const aTitre = n.titre && n.titre !== "8-K";
    const q = aTitre ? `"${n.sym}" OR "${nomCourt(n.nom) || n.sym}"` : `"${nomCourt(n.nom) || n.sym}"`;
    const trouves = [];
    for (const [nom, f] of [["google", () => googleNews(q + " when:2d")], ["bing", () => bingNews(q)], ["yahoo", () => yahooNews(n.sym)], ["stocktwits", () => stocktwits(n.sym)]]) {
      try { trouves.push(...(await f())); } catch (e) { erreurs[nom] = String(e.message || e); }
    }
    // même news = publiée entre 12 h avant et 2 h après notre lecture, et (si on a le titre) titre ressemblant
    const garde = trouves.filter((x) => x.publie && x.publie >= n.vu - 12 * 3600e3 && x.publie <= n.vu + 2 * 3600e3)
      .map((x) => ({ ...x, score: aTitre ? ressemblance(n.titre, x.titre) : null }))
      .filter((x) => (aTitre ? x.score >= 0.35 : x.source !== "Stocktwits" && x.publie >= n.vu - 3 * 3600e3));
    for (const x of garde) st.push(db.prepare("INSERT OR IGNORE INTO origine VALUES (?,?,?,?,?,?,?)").bind(n.id, x.source, x.editeur, x.titre, x.publie, x.lien, x.score));
    // notre propre source compte aussi, avec son heure officielle de publication
    const cands = [...garde.map((x) => ({ qui: `${x.editeur || x.source} (via ${x.source})`, ms: x.publie })), { qui: n.source === "prnewswire" ? "PR Newswire" : "SEC 8-K", ms: n.quand || n.vu }];
    const p = cands.sort((a, b) => a.ms - b.ms)[0];
    let bouge = null; try { bouge = await bougeAvant(n.sym, n.vu); } catch (e) {}
    st.push(db.prepare("UPDATE news SET or_n = COALESCE(or_n, 0) + 1, or_premier = ?, or_premier_ms = ?, or_bouge_ms = ?, or_nb = ? WHERE id = ?").bind(p.qui, p.ms, bouge, garde.length, n.id));
  }
  if (st.length) await db.batch(st);
  return { cherchees: l.length, erreurs };
}

// Moment de la news : séance normale, avant/après séance (achetable chez la plupart des courtiers US), ou marché fermé
export function moment(ms) {
  const l = local(ms, MARCHES.actions); const j = new Date(ms).getUTCDay();
  if (j === 0 || j === 6) return "week-end";
  if (l.min >= 570 && l.min < 960) return "séance (15 h 30 – 22 h)";
  if (l.min >= 240 && l.min < 570) return "avant séance (10 h – 15 h 30)";
  if (l.min >= 960 && l.min < 1200) return "après séance (22 h – 2 h)";
  return "nuit (marché fermé)";
}

export async function statsOrigine(db) {
  await schemaOrigine(db);
  const l = (await db.prepare("SELECT id, sym, titre, source, quand, vu, or_premier, or_premier_ms, or_bouge_ms, or_nb, hl0, kf0 FROM news WHERE or_n >= 1 ORDER BY vu DESC LIMIT 1000").all()).results;
  const par = {};
  for (const n of l) {
    const qui = (n.or_premier || "?").replace(/ \(via .*\)$/, "");
    const x = (par[qui] = par[qui] || { source: qui, premier: 0, avance: [] }); x.premier++;
    if (n.or_premier_ms && n.vu) x.avance.push(Math.round((n.vu - n.or_premier_ms) / 1000));
  }
  const med = (a) => { if (!a.length) return null; const s = [...a].sort((p, q) => p - q); return s[Math.floor(s.length / 2)]; };
  const sources = Object.values(par).map((x) => ({ source: x.source, premier: x.premier, avanceMediane: med(x.avance) })).sort((a, b) => b.premier - a.premier);
  const moments = {}; for (const n of l) { const m = moment(n.vu); const x = (moments[m] = moments[m] || { moment: m, news: 0, jeton: 0 }); x.news++; if (n.hl0 != null || n.kf0 != null) x.jeton++; }
  return { cherchees: l.length, bougeaitAvant: l.filter((n) => n.or_bouge_ms).length, sources, moments: Object.values(moments),
    exemples: l.slice(0, 30).map((n) => ({ sym: n.sym, titre: n.titre, vu: n.vu, premier: n.or_premier, premierMs: n.or_premier_ms, bouge: n.or_bouge_ms, nb: n.or_nb })) };
}
