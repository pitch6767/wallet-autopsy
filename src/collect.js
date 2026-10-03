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

const MAX_MARCHES = 70;
const MAX_FETCH = 800;
const DUREE_MAX_MS = 45_000;

const num = (x) => (x == null || x === "" ? 0 : Number(x)) || 0;
const iso = (ms) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z");

function compteur() {
  let n = 0;
  return {
    get n() { return n; },
    async json(u) {
      for (let essai = 0; ; essai++) {
        n++;
        const r = await fetch(u, { headers: { accept: "application/json", "user-agent": "wallet-autopsy/1.0" } });
        if (r.ok) return r.json();
        // Limite de débit de Polymarket : on patiente et on réessaie
        if ((r.status === 429 || r.status >= 500) && essai < 4) { await new Promise((ok) => setTimeout(ok, 800 * (essai + 1))); continue; }
        throw new Error(`HTTP ${r.status} ${new URL(u).pathname}`);
      }
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

function agreger(rows, gagnant, finTs) {
  const W = new Map();
  for (const t of rows) {
    const a = String(t.proxyWallet || "").toLowerCase();
    if (!/^0x[0-9a-f]{40}$/.test(a)) continue;
    if (!W.has(a)) W.set(a, { nom: t.name || t.pseudonym || "", o: [{ ap: 0, ac: 0, vp: 0, vr: 0 }, { ap: 0, ac: 0, vp: 0, vr: 0 }], n: 0, ts: 0, premierAchat: Infinity });
    const w = W.get(a);
    const i = Number(t.outcomeIndex) === 1 ? 1 : 0;
    const sz = num(t.size), px = num(t.price);
    if (String(t.side).toUpperCase() === "BUY") { w.o[i].ap += sz; w.o[i].ac += sz * px; w.premierAchat = Math.min(w.premierAchat, num(t.timestamp) || Infinity); }
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
    let classe, combine = null, dirGagne = 0, px = 0, gagne = 0;
    if ((A.ap > 0 && B.ap > 0) || k > 0) {
      classe = "deux";
      if (pmA != null && pmB != null) combine = pmA + pmB;
    } else {
      const cote = A.ap > 0 ? 0 : 1, pm = cote === 0 ? pmA : pmB;
      const o = cote === 0 ? A : B;
      px = pm; gagne = cote === gagnant ? 1 : 0;
      if (finTs && Number.isFinite(w.premierAchat) && w.premierAchat > finTs) classe = "apres"; // résultat déjà connu : pas une prédiction
      else if (o.vp > 0.1 * o.ap) classe = "scalp"; // revend avant la fin : le résultat ne dit rien de son pari
      else if (pm >= 0.9) classe = "sniper";
      else if (pm <= 0.25) classe = "loterie";
      else { classe = "dir"; dirGagne = gagne; }
    }
    out.push({ adresse, nom: w.nom, n: w.n, ts: w.ts, cout, pnl, roi: pnl / cout, classe, combine, dirGagne, px, gagne, split: k > 0 ? 1 : 0,
      avant: finTs && Number.isFinite(w.premierAchat) ? Math.max(0, finTs - w.premierAchat) : null });
  }
  return out;
}

const sqlNum = (x) => (Number.isFinite(x) ? String(Math.round(x * 1e6) / 1e6) : "0");
const sqlTxt = (s) => "'" + String(s || "").replace(/[^\p{L}\p{N} ._\-]/gu, "").slice(0, 40).replace(/'/g, "''") + "'";

function upserts(db, type, ws) {
  const cols = "wallet,type,nom,n_marches,n_gagnes,cout,pnl,sum_roi,sum_roi2,best_roi,best_pnl,worst_pnl,trades,deux,deux_sous1,sum_combine,n_combine,sniper,loterie,dir,dir_gagne,split,last_ts,px_sniper,g_sniper,px_loterie,g_loterie,px_dir,scalp,sum_avant,n_avant";
  const stm = [];
  for (let i = 0; i < ws.length; i += 80) {
    const vals = ws.slice(i, i + 80).map((w) => "(" + [
      `'${w.adresse}'`, `'${type}'`, sqlTxt(w.nom), 1, w.pnl > 0 ? 1 : 0, sqlNum(w.cout), sqlNum(w.pnl),
      sqlNum(w.roi), sqlNum(w.roi * w.roi), sqlNum(w.roi), sqlNum(w.pnl), sqlNum(w.pnl), w.n,
      w.classe === "deux" ? 1 : 0, w.combine != null && w.combine < 1 ? 1 : 0, sqlNum(w.combine ?? 0), w.combine != null ? 1 : 0,
      w.classe === "sniper" ? 1 : 0, w.classe === "loterie" ? 1 : 0, w.classe === "dir" ? 1 : 0, w.dirGagne, w.split, w.ts,
      w.classe === "sniper" ? sqlNum(w.px) : 0, w.classe === "sniper" ? w.gagne : 0,
      w.classe === "loterie" ? sqlNum(w.px) : 0, w.classe === "loterie" ? w.gagne : 0,
      w.classe === "dir" ? sqlNum(w.px) : 0,
      w.classe === "scalp" ? 1 : 0,
      ["sniper", "loterie", "dir"].includes(w.classe) && w.avant != null ? sqlNum(w.avant) : 0,
      ["sniper", "loterie", "dir"].includes(w.classe) && w.avant != null ? 1 : 0,
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
        dir_gagne=stats.dir_gagne+excluded.dir_gagne, split=stats.split+excluded.split, last_ts=MAX(stats.last_ts,excluded.last_ts),
        px_sniper=stats.px_sniper+excluded.px_sniper, g_sniper=stats.g_sniper+excluded.g_sniper,
        px_loterie=stats.px_loterie+excluded.px_loterie, g_loterie=stats.g_loterie+excluded.g_loterie, px_dir=stats.px_dir+excluded.px_dir,
        scalp=stats.scalp+excluded.scalp, sum_avant=stats.sum_avant+excluded.sum_avant, n_avant=stats.n_avant+excluded.n_avant`));
  }
  return stm;
}

async function traiterMarche(db, f, m) {
  const { rows, tronque } = await tradesMarche(f, m.cid);
  const ws = agreger(rows, m.gagnant, m.end_ts);
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
    const { results } = await db.prepare("SELECT cid,type,gagnant,end_ts FROM markets WHERE statut=0 ORDER BY end_ts DESC LIMIT ?").bind(MAX_MARCHES).all();
    for (let i = 0; i < results.length; i += 3) {
      if (Date.now() - t0 > DUREE_MAX_MS || f.n > MAX_FETCH) break;
      const lot = results.slice(i, i + 3);
      await db.batch(lot.map((m) => db.prepare("UPDATE markets SET statut=2, claim_ts=? WHERE cid=? AND statut=0").bind(Date.now() / 1000 | 0, m.cid)));
      await Promise.all(lot.map(async (m) => {
        try { const nt = await traiterMarche(db, f, m); rapport.trades += nt; rapport.traites++; }
        catch (e) {
          rapport.erreurs++;
          rapport.derniereErreur = String(e.message || e).slice(0, 300);
          await db.prepare("UPDATE markets SET statut=CASE WHEN essais>=8 THEN 9 ELSE 0 END, essais=essais+1, erreur=? WHERE cid=?").bind(String(e.message || e).slice(0, 200), m.cid).run();
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

// ─── Études en tâche de fond ───
export async function tourEtudes(env, etude) {
  const db = env.DB, t0 = Date.now();
  const { results } = await db.prepare(`SELECT s.wallet FROM (
      SELECT wallet, SUM(n_marches) n, SUM(pnl) pnl, SUM(trades) tr, SUM(sum_avant) sa, SUM(n_avant) na FROM stats GROUP BY wallet) s
      LEFT JOIN etudes e ON e.wallet = s.wallet
      WHERE s.n >= 30 AND s.pnl > 0 AND s.tr <= 30 * s.n AND s.na > 0 AND s.sa / s.na >= 60
        AND (e.ts IS NULL OR e.ts < ?)
      ORDER BY (e.ts IS NOT NULL), s.pnl DESC LIMIT 4`).bind((t0 / 1000 | 0) - 86400).all();
  let faits = 0;
  for (const r of results) {
    if (Date.now() - t0 > 40_000) break;
    try {
      const e = await etude(env, r.wallet);
      const m = e.meilleure;
      await db.prepare(`INSERT INTO etudes(wallet,ts,copiable,titre,marches,pnl,roi,marge,roi_cible,n_cible,score,json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(wallet) DO UPDATE SET ts=excluded.ts,copiable=excluded.copiable,titre=excluded.titre,marches=excluded.marches,pnl=excluded.pnl,roi=excluded.roi,
          marge=excluded.marge,roi_cible=excluded.roi_cible,n_cible=excluded.n_cible,score=excluded.score,json=excluded.json`)
        .bind(r.wallet, Date.now() / 1000 | 0, e.copiable ? 1 : 0, e.titre, e.marches, e.pnl || 0, e.roi || 0,
          m ? m.marge : null, m ? m.roi : null, m ? m.n : null, m ? m.marge * Math.sqrt(m.n) : null, JSON.stringify({ ...e, cible: undefined })).run();
      faits++;
    } catch (err) {
      await db.prepare("INSERT INTO etudes(wallet,ts,copiable,titre) VALUES(?,?,0,?) ON CONFLICT(wallet) DO UPDATE SET ts=excluded.ts")
        .bind(r.wallet, Date.now() / 1000 | 0, "Étude impossible").run();
    }
  }
  return faits;
}

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
      SUM(px_sniper) px_sniper, SUM(g_sniper) g_sniper, SUM(px_loterie) px_loterie, SUM(g_loterie) g_loterie, SUM(px_dir) px_dir, SUM(scalp) scalp, SUM(sum_avant) sum_avant, SUM(n_avant) n_avant,
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
    q("t2s", 20, `WHERE t2s IS NOT NULL AND n_marches >= ${Math.max(30, minM)}`),
    q(TRIS[tri], 300, `WHERE ${TRIS[tri]} IS NOT NULL`),
    db.prepare(`SELECT COUNT(*) n FROM (${agg})`).bind(...binds),
  ]);
  const fin = (r) => ({
    ...r,
    roiMoyen: r.sum_roi / r.n_marches,
    regularite: r.t2s == null ? null : Math.sign(r.t2s) * Math.sqrt(Math.abs(r.t2s)),
  });
  const et = await db.prepare(`SELECT wallet, titre, marches, pnl, roi, marge, roi_cible, n_cible, score, json FROM etudes WHERE copiable=1 ORDER BY score DESC LIMIT 20`).all();
  const ws = et.results.map((r) => r.wallet);
  const noms = new Map();
  if (ws.length) {
    const nn = await db.prepare(`SELECT wallet, MAX(nom) nom FROM stats WHERE wallet IN (${ws.map(() => "?").join(",")}) GROUP BY wallet`).bind(...ws).all();
    for (const r of nn.results) noms.set(r.wallet, r);
  }
  const tueurs = et.results.map((r) => {
    const e = JSON.parse(r.json || "{}");
    return { wallet: r.wallet, nom: (noms.get(r.wallet) || {}).nom || "", titre: r.titre, n_marches: r.marches, pnl: r.pnl, roi: r.roi, marge: r.marge,
      roiCible: r.roi_cible, nCible: r.n_cible, cible: e.meilleure ? e.meilleure.lib : "", avant: e.meilleure ? e.meilleure.avant : null, verdict: e.verdict };
  });
  const suivi = await db.prepare("SELECT COUNT(*) n, SUM(copiable) c FROM etudes").first();
  return {
    type, tri, tueurs, etudesFaites: suivi?.n || 0, etudesCopiables: suivi?.c || 0,
    total: total.results[0]?.n || 0,
    perf: perf.results.map(fin),
    copier: copier.results.map(fin),
    table: table.results.map(fin),
  };
}
