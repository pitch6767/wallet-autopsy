// Collecte de l'historique des marchés « BTC Up or Down » dans D1.
// Chaque minute : découverte des marchés résolus (90 jours), puis traitement
// d'un lot de marchés : tous leurs trades, agrégés par portefeuille et par durée.

const DATA = "https://data-api.polymarket.com";
const GAMMA = "https://gamma-api.polymarket.com";
export const JOURS = 90;

// série Polymarket -> type, fenêtre de découverte (heures) pour ~100 marchés
export const SERIES = [
  { id: 10684, type: "5m", fen: 6, per: 5 / 60 },
  { id: 10192, type: "15m", fen: 24, per: 0.25 },
  { id: 10114, type: "1h", fen: 96, per: 1 },
  { id: 10331, type: "4h", fen: 384, per: 4 },
  { id: 10323, type: "4h", fen: 384, per: 4 },
  { id: 41, type: "1j", fen: 24 * 90, per: 24 },
];

const MAX_MARCHES = 16;
const MAX_FETCH = 400;
const DUREE_MAX_MS = 25_000;

const num = (x) => (x == null || x === "" ? 0 : Number(x)) || 0;
const iso = (ms) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z");

function compteur() {
  let n = 0;
  return {
    get n() { return n; },
    async json(u) {
      n++;
      const r = await fetch(u, { headers: { accept: "application/json", "user-agent": "wallet-autopsy/1.0" } });
      if (!r.ok) throw new Error(`HTTP ${r.status} ${new URL(u).pathname}`);
      return r.json();
    },
  };
}

async function meta(db, k) {
  const r = await db.prepare("SELECT v FROM meta WHERE k=?").bind(k).first();
  return r ? r.v : null;
}
async function setMeta(db, k, v) {
  await db.prepare("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v").bind(k, String(v)).run();
}

// ─── Découverte ──────────────────────────────────────────────
async function decouvrirFenetre(db, f, serie, debutMs, finMs) {
  let ajout = 0;
  for (let off = 0; off < 1000; off += 100) {
    const q = new URLSearchParams({
      series_id: String(serie.id), closed: "true",
      end_date_min: iso(debutMs), end_date_max: iso(finMs),
      limit: "100", offset: String(off),
    });
    const evs = await f.json(`${GAMMA}/events?${q}`);
    if (!Array.isArray(evs) || !evs.length) break;
    const st = [];
    for (const e of evs) {
      for (const m of e.markets || []) {
        let prix = [];
        try { prix = JSON.parse(m.outcomePrices || "[]").map(Number); } catch {}
        const gagnant = prix[0] === 1 ? 0 : prix[1] === 1 ? 1 : null;
        if (gagnant == null || !m.conditionId) continue;
        const fin = Date.parse(m.endDate || e.endDate) / 1000 | 0;
        st.push(db.prepare("INSERT OR IGNORE INTO markets(cid,slug,type,end_ts,gagnant,statut) VALUES(?,?,?,?,?,0)")
          .bind(m.conditionId, m.slug || e.slug || "", serie.type, fin, gagnant));
      }
    }
    if (st.length) {
      const res = await db.batch(st);
      ajout += res.reduce((x, r) => x + (r.meta?.changes || 0), 0);
    }
    if (evs.length < 100) break;
  }
  return ajout;
}

async function decouvrir(db, f) {
  const now = Date.now();
  const borne = now - JOURS * 86400_000;
  let total = 0;
  for (const s of SERIES) {
    // Vers l'avant : les 3 dernières fenêtres (les marchés tout juste résolus)
    const recent = Math.max(borne, now - Math.max(3, 3 * s.per) * 3600_000);
    total += await decouvrirFenetre(db, f, s, recent, now);
    // Vers l'arrière : une fenêtre de plus dans le passé
    const k = "disc_" + s.id;
    let curseur = Number(await meta(db, k)) || recent;
    if (curseur > borne) {
      const debut = Math.max(borne, curseur - s.fen * 3600_000);
      total += await decouvrirFenetre(db, f, s, debut, curseur);
      await setMeta(db, k, debut);
    }
  }
  return total;
}

// ─── Traitement d'un marché ─────────────────────────────────
async function tradesMarche(f, cid) {
  const tout = async (extra) => {
    const rows = [];
    let plein = false;
    for (let off = 0; off <= 10000; off += 500) {
      const q = new URLSearchParams({ market: cid, limit: "500", offset: String(off), takerOnly: "false", ...extra });
      const r = await f.json(`${DATA}/trades?${q}`);
      if (!Array.isArray(r)) break;
      rows.push(...r);
      if (r.length < 500) return { rows, plein: false };
      if (off === 10000) plein = true;
    }
    return { rows, plein };
  };
  const a = await tout({});
  if (!a.plein) return { rows: a.rows, tronque: false };
  const b = await tout({ side: "BUY" });
  const s = await tout({ side: "SELL" });
  return { rows: [...b.rows, ...s.rows], tronque: b.plein || s.plein };
}

function agreger(rows, gagnant) {
  const W = new Map();
  for (const t of rows) {
    const a = String(t.proxyWallet || "").toLowerCase();
    if (!/^0x[0-9a-f]{40}$/.test(a)) continue;
    if (!W.has(a)) W.set(a, { nom: t.name || t.pseudonym || "", o: [{ ap: 0, ac: 0, vp: 0, vr: 0 }, { ap: 0, ac: 0, vp: 0, vr: 0 }], n: 0, ts: 0 });
    const w = W.get(a);
    const i = Number(t.outcomeIndex) === 1 ? 1 : 0;
    const sz = num(t.size), px = num(t.price);
    if (String(t.side).toUpperCase() === "BUY") { w.o[i].ap += sz; w.o[i].ac += sz * px; }
    else { w.o[i].vp += sz; w.o[i].vr += sz * px; }
    w.n++;
    w.ts = Math.max(w.ts, num(t.timestamp));
  }
  const out = [];
  for (const [adresse, w] of W) {
    const [A, B] = w.o;
    let netA = A.ap - A.vp, netB = B.ap - B.vp;
    // Parts vendues sans avoir été achetées = paires créées par « split » à 1 $
    const k = Math.max(0, -netA, -netB);
    netA += k; netB += k;
    const cout = A.ac + B.ac + k;
    const encaisse = A.vr + B.vr;
    const valeur = gagnant === 0 ? netA : netB;
    const pnl = encaisse + valeur - cout;
    if (cout <= 0.000001) continue;
    const pmA = A.ap ? A.ac / A.ap : null, pmB = B.ap ? B.ac / B.ap : null;
    let classe, combine = null, dirGagne = 0;
    if ((A.ap > 0 && B.ap > 0) || k > 0) {
      classe = "deux";
      if (pmA != null && pmB != null) combine = pmA + pmB;
    } else {
      const cote = A.ap > 0 ? 0 : 1, pm = cote === 0 ? pmA : pmB;
      if (pm >= 0.9) classe = "sniper";
      else if (pm <= 0.25) classe = "loterie";
      else { classe = "dir"; dirGagne = cote === gagnant ? 1 : 0; }
    }
    out.push({ adresse, nom: w.nom, n: w.n, ts: w.ts, cout, pnl, roi: pnl / cout, classe, combine, dirGagne, split: k > 0 ? 1 : 0 });
  }
  return out;
}

const sqlNum = (x) => (Number.isFinite(x) ? String(Math.round(x * 1e6) / 1e6) : "0");
const sqlTxt = (s) => "'" + String(s || "").replace(/[^\p{L}\p{N} ._\-]/gu, "").slice(0, 40).replace(/'/g, "''") + "'";

function upserts(db, type, ws) {
  const cols = "wallet,type,nom,n_marches,n_gagnes,cout,pnl,sum_roi,sum_roi2,best_roi,best_pnl,worst_pnl,trades,deux,deux_sous1,sum_combine,n_combine,sniper,loterie,dir,dir_gagne,split,last_ts";
  const stm = [];
  for (let i = 0; i < ws.length; i += 80) {
    const vals = ws.slice(i, i + 80).map((w) => "(" + [
      `'${w.adresse}'`, `'${type}'`, sqlTxt(w.nom), 1, w.pnl > 0 ? 1 : 0, sqlNum(w.cout), sqlNum(w.pnl),
      sqlNum(w.roi), sqlNum(w.roi * w.roi), sqlNum(w.roi), sqlNum(w.pnl), sqlNum(w.pnl), w.n,
      w.classe === "deux" ? 1 : 0, w.combine != null && w.combine < 1 ? 1 : 0, sqlNum(w.combine ?? 0), w.combine != null ? 1 : 0,
      w.classe === "sniper" ? 1 : 0, w.classe === "loterie" ? 1 : 0, w.classe === "dir" ? 1 : 0, w.dirGagne, w.split, w.ts,
    ].join(",") + ")").join(",");
    stm.push(db.prepare(`INSERT INTO stats(${cols}) VALUES ${vals}
      ON CONFLICT(wallet,type) DO UPDATE SET
        nom=CASE WHEN excluded.nom<>'' THEN excluded.nom ELSE stats.nom END,
        n_marches=stats.n_marches+1, n_gagnes=stats.n_gagnes+excluded.n_gagnes,
        cout=stats.cout+excluded.cout, pnl=stats.pnl+excluded.pnl,
        sum_roi=stats.sum_roi+excluded.sum_roi, sum_roi2=stats.sum_roi2+excluded.sum_roi2,
        best_roi=MAX(stats.best_roi,excluded.best_roi), best_pnl=MAX(stats.best_pnl,excluded.best_pnl), worst_pnl=MIN(stats.worst_pnl,excluded.worst_pnl),
        trades=stats.trades+excluded.trades, deux=stats.deux+excluded.deux, deux_sous1=stats.deux_sous1+excluded.deux_sous1,
        sum_combine=stats.sum_combine+excluded.sum_combine, n_combine=stats.n_combine+excluded.n_combine,
        sniper=stats.sniper+excluded.sniper, loterie=stats.loterie+excluded.loterie, dir=stats.dir+excluded.dir,
        dir_gagne=stats.dir_gagne+excluded.dir_gagne, split=stats.split+excluded.split, last_ts=MAX(stats.last_ts,excluded.last_ts)`));
  }
  return stm;
}

async function traiterMarche(db, f, m) {
  const { rows, tronque } = await tradesMarche(f, m.cid);
  const ws = agreger(rows, m.gagnant);
  const st = upserts(db, m.type, ws);
  st.push(db.prepare("UPDATE markets SET statut=1, n_trades=?, n_wallets=?, tronque=?, traite_ts=? WHERE cid=? AND statut=2")
    .bind(rows.length, ws.length, tronque ? 1 : 0, Date.now() / 1000 | 0, m.cid));
  await db.batch(st);
  return rows.length;
}

// ─── Tour de collecte (cron) ────────────────────────────────
export async function tourDeCollecte(env) {
  const db = env.DB;
  const t0 = Date.now();
  // Verrou : un seul tour à la fois
  const verrou = await db.prepare("UPDATE meta SET v=? WHERE k='verrou' AND CAST(v AS INTEGER) < ?").bind(String(t0 + 170_000), t0).run();
  if (!verrou.meta.changes) return { saute: true };
  const f = compteur();
  const rapport = { decouverts: 0, traites: 0, erreurs: 0, trades: 0 };
  try {
    await setMeta(db, "tour_debut", new Date().toISOString());
    try { rapport.decouverts = await decouvrir(db, f); } catch (e) { rapport.erreurDecouverte = String(e.message || e); }
    // Marchés restés « en cours » après un tour interrompu
    await db.prepare("UPDATE markets SET statut=0 WHERE statut=2 AND claim_ts < ?").bind((t0 / 1000 | 0) - 600).run();
    const { results } = await db.prepare("SELECT cid,type,gagnant FROM markets WHERE statut=0 ORDER BY end_ts DESC LIMIT ?").bind(MAX_MARCHES).all();
    for (let i = 0; i < results.length; i += 2) {
      if (Date.now() - t0 > DUREE_MAX_MS || f.n > MAX_FETCH) break;
      const lot = results.slice(i, i + 2);
      await db.batch(lot.map((m) => db.prepare("UPDATE markets SET statut=2, claim_ts=? WHERE cid=? AND statut=0").bind(Date.now() / 1000 | 0, m.cid)));
      await Promise.all(lot.map(async (m) => {
        try { const nt = await traiterMarche(db, f, m); rapport.trades += nt; rapport.traites++; }
        catch (e) {
          rapport.erreurs++;
          rapport.derniereErreur = String(e.message || e).slice(0, 300);
          await db.prepare("UPDATE markets SET statut=CASE WHEN essais>=3 THEN 9 ELSE 0 END, essais=essais+1, erreur=? WHERE cid=?").bind(String(e.message || e).slice(0, 200), m.cid).run();
        }
      }));
    }
  } catch (e) {
    rapport.erreurTour = String(e && e.stack || e).slice(0, 500);
  } finally {
    rapport.fetch = f.n;
    rapport.ms = Date.now() - t0;
    await setMeta(db, "dernier_tour", JSON.stringify({ ...rapport, a: new Date().toISOString() }));
    await db.prepare("UPDATE meta SET v='0' WHERE k='verrou'").run();
  }
  return rapport;
}

// ─── Lecture ────────────────────────────────────────────────
export async function etatCollecte(env) {
  const db = env.DB;
  const { results } = await db.prepare(`SELECT type,
      SUM(statut=1) traites, SUM(statut IN (0,2)) attente, SUM(statut=9) echecs,
      MIN(CASE WHEN statut=1 THEN end_ts END) plus_ancien, MAX(CASE WHEN statut=1 THEN end_ts END) plus_recent,
      SUM(CASE WHEN statut=1 THEN n_trades END) trades, SUM(tronque) tronques
    FROM markets GROUP BY type`).all();
  const w = await db.prepare("SELECT COUNT(DISTINCT wallet) n FROM stats").first();
  return { parType: results, portefeuilles: w?.n || 0, dernierTour: JSON.parse((await meta(db, "dernier_tour")) || "null"), jours: JOURS };
}

const TYPES = ["5m", "15m", "1h", "4h", "1j"];

export async function classement(env, sp) {
  const db = env.DB;
  const type = TYPES.includes(sp.get("type")) ? sp.get("type") : "tous";
  const minM = Math.max(1, parseInt(sp.get("marches") || "1", 10) || 1);
  const minT = Math.max(0, parseInt(sp.get("trades") || "0", 10) || 0);
  const minC = Math.max(0, parseFloat(sp.get("mise") || "0") || 0);
  const rs = sp.get("roi");
  const minR = rs === "" || rs == null || isNaN(parseFloat(rs)) ? null : parseFloat(rs) / 100;
  const TRIS = {
    pnl: "pnl", roi: "roi", regularite: "t2s", best_roi: "best_roi", n_marches: "n_marches", pct: "pct", cout: "cout",
  };
  const tri = TRIS[sp.get("tri")] ? sp.get("tri") : "pnl";

  const binds = [];
  let where = "";
  if (type !== "tous") { where = "WHERE type=?"; binds.push(type); }
  binds.push(minM, minT, minC);
  let having = "SUM(n_marches) >= ? AND SUM(trades) >= ? AND SUM(cout) >= ?";
  if (minR != null) { having += " AND SUM(pnl) / SUM(cout) >= ?"; binds.push(minR); }
  const agg = `SELECT wallet, MAX(nom) nom, SUM(n_marches) n_marches, SUM(n_gagnes) n_gagnes, SUM(cout) cout, SUM(pnl) pnl,
      SUM(pnl) / SUM(cout) roi, SUM(n_gagnes) * 1.0 / SUM(n_marches) pct,
      SUM(sum_roi) sum_roi, SUM(sum_roi2) sum_roi2, MAX(best_roi) best_roi, MAX(best_pnl) best_pnl, MIN(worst_pnl) worst_pnl,
      SUM(trades) trades, SUM(deux) deux, SUM(deux_sous1) deux_sous1, SUM(sum_combine) sum_combine, SUM(n_combine) n_combine,
      SUM(sniper) sniper, SUM(loterie) loterie, SUM(dir) dir, SUM(dir_gagne) dir_gagne, SUM(split) split, MAX(last_ts) last_ts,
      GROUP_CONCAT(type || ':' || n_marches) types,
      CASE WHEN SUM(n_marches) > 1 AND (SUM(sum_roi2) - SUM(sum_roi) * SUM(sum_roi) / SUM(n_marches)) > 1e-12
        THEN (CASE WHEN SUM(sum_roi) > 0 THEN 1.0 ELSE -1.0 END) * (SUM(sum_roi) * SUM(sum_roi) / SUM(n_marches))
             / ((SUM(sum_roi2) - SUM(sum_roi) * SUM(sum_roi) / SUM(n_marches)) / (SUM(n_marches) - 1))
        ELSE NULL END t2s
    FROM stats ${where} GROUP BY wallet HAVING ${having}`;
  const q = (order, lim, extra = "") =>
    db.prepare(`SELECT * FROM (${agg}) ${extra} ORDER BY ${order} DESC LIMIT ${lim}`).bind(...binds);
  const [perf, copier, table, total] = await db.batch([
    q("pnl", 20),
    q("t2s", 20, `WHERE t2s IS NOT NULL AND n_marches >= ${Math.max(10, minM)}`),
    q(TRIS[tri], 300, `WHERE ${TRIS[tri]} IS NOT NULL`),
    db.prepare(`SELECT COUNT(*) n FROM (${agg})`).bind(...binds),
  ]);
  const fin = (r) => ({
    ...r,
    roiMoyen: r.sum_roi / r.n_marches,
    regularite: r.t2s == null ? null : Math.sign(r.t2s) * Math.sqrt(Math.abs(r.t2s)),
  });
  return {
    type, tri,
    total: total.results[0]?.n || 0,
    perf: perf.results.map(fin),
    copier: copier.results.map(fin),
    table: table.results.map(fin),
  };
}
