// Pitch 11.11 : « je veux acheter 5 s après la news max ». Flux de news EN DIRECT (Benzinga, via un compte
// d'essai Alpaca) : une connexion ouverte en permanence, la news arrive dès sa sortie. À chaque news, on prend
// le dernier prix (bourse IEX, gratuit) tout de suite, puis 5 s, 30 s, 60 s et 5 min après.
// Clés Alpaca rangées dans la table config de D1 (jamais dans le code).
export const SCHEMA_FLUX = "CREATE TABLE IF NOT EXISTS flux (id TEXT, sym TEXT, recu INTEGER, cree INTEGER, titre TEXT, auteur TEXT, source TEXT, url TEXT, p0 REAL, t0 INTEGER, p5 REAL, t5 INTEGER, p30 REAL, p60 REAL, p300 REAL, PRIMARY KEY (id, sym))";
const WS = "https://stream.data.alpaca.markets/v1beta1/news";
const DATA = "https://data.alpaca.markets";
const DELAIS = [[5, "p5"], [30, "p30"], [60, "p60"], [300, "p300"]];
const IEX = "https://stream.data.alpaca.markets/v2/iex";
const G = 0.0005; // glissement estimé à l'entrée et à la sortie
export const SEUILS_ECLAIR = [0.5, 1]; // Pitch 10.11 : pas plus de 1 %
export const SCHEMA_ECLAIR = [
  "CREATE TABLE IF NOT EXISTS eclair (cle TEXT PRIMARY KEY, sym TEXT, source TEXT, titre TEXT, recu INTEGER, cree INTEGER, p0 REAL, age0 INTEGER, p5 REAL, max5m REAL, min5m REAL, fin INTEGER DEFAULT 0)",
  "CREATE TABLE IF NOT EXISTS eclair_trade (cle TEXT, seuil REAL, sym TEXT, entree REAL, t_entree INTEGER, sorties TEXT, statut TEXT, PRIMARY KEY (cle, seuil))",
  "ALTER TABLE eclair ADD COLUMN ppub REAL", "ALTER TABLE eclair ADD COLUMN t5 INTEGER",
  "CREATE TABLE IF NOT EXISTS eclair_vue (sym TEXT, source TEXT, id TEXT, recu INTEGER, cree INTEGER, titre TEXT, PRIMARY KEY (source, id))",
];
// Sorties testées en parallèle sur le même achat (Pitch 11.11 : « vendre au bon moment, pas bêtement »)
export const SORTIES = ["suiveur 1 %", "suiveur 2 %", "suiveur 3 %", "moitié à +3 % puis suiveur 2 %", "objectif 2R (stop au prix de la news)", "5 min", "15 min", "30 min", "60 min"];
export function calculerSorties(tr, entree, t0, p0) {
  const out = {}; const fin = (p, quand, raison) => ({ pct: +((p * (1 - G)) / entree - 1).toFixed(5), quand, raison });
  const dernier = tr.length ? tr[tr.length - 1] : [t0, entree];
  for (const x of [1, 2, 3]) { let m = entree, r = null; for (const [ms, p] of tr) { m = Math.max(m, p); if (p <= m * (1 - x / 100)) { r = fin(p, ms, `recul de ${x} % depuis le plus haut`); break; } } out[`suiveur ${x} %`] = r || fin(dernier[1], dernier[0], "fin de l'heure"); }
  { let m = entree, moitie = null, r = null; for (const [ms, p] of tr) { m = Math.max(m, p); if (!moitie && p >= entree * 1.03) moitie = p; if (p <= m * 0.98) { r = [p, ms]; break; } } const reste = r || [dernier[1], dernier[0]];
    const pct = moitie ? 0.5 * ((moitie * (1 - G)) / entree - 1) + 0.5 * ((reste[0] * (1 - G)) / entree - 1) : (reste[0] * (1 - G)) / entree - 1; out["moitié à +3 % puis suiveur 2 %"] = { pct: +pct.toFixed(5), quand: reste[1], raison: moitie ? "moitié vendue à +3 %" : "+3 % jamais atteint" }; }
  { let stop = Math.min(p0, entree * 0.997); const cible = entree + 2 * (entree - stop); let r = null; for (const [ms, p] of tr) { if (p <= stop) { r = fin(p, ms, "stop"); break; } if (p >= cible) { r = fin(p, ms, "objectif"); break; } } out["objectif 2R (stop au prix de la news)"] = r || fin(dernier[1], dernier[0], "fin de l'heure"); }
  for (const mn of [5, 15, 30, 60]) { let r = null; for (const [ms, p] of tr) if (ms >= t0 + mn * 60e3) { r = fin(p, ms, `${mn} min écoulées`); break; } out[`${mn} min`] = r || fin(dernier[1], dernier[0], "fin des données"); }
  return out;
}

export class Flux {
  constructor(state, env) { this.state = state; this.env = env; this.s = state.storage; this.ws = null; this.ok = false; this.wsP = null; this.okP = false; this.suivis = new Map(); this.actifs = new Map(); }
  async cles() {
    const r = (await this.env.DB.prepare("SELECT cle, valeur FROM config WHERE cle IN ('alpaca_key','alpaca_secret')").all()).results;
    const m = Object.fromEntries(r.map((x) => [x.cle, x.valeur])); return { key: m.alpaca_key, secret: m.alpaca_secret };
  }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/demarrer") { await this.connecter(); if (!(await this.s.getAlarm())) await this.s.setAlarm(Date.now() + 30e3); return Response.json(await this.etat()); }
    if (u.pathname === "/etat") return Response.json(await this.etat());
    if (u.pathname === "/reagir") { const l = await req.json(); const c = await this.cles(); for (const e of l) this.state.waitUntil(this.reagir(e, c)); return Response.json({ ok: l.length }); }
    return new Response("?", { status: 404 });
  }
  async etat() { return { connecte: !!this.ws, authentifie: this.ok, prixDirect: this.okP, suivis: [...this.suivis.keys()], ...(await this.s.get("etat")), erreur: await this.s.get("erreur") }; }
  async noter(k, v) { const e = (await this.s.get("etat")) || {}; e[k] = v; await this.s.put("etat", e); }
  async alarm() { try { await this.connecter(); } catch (e) {} try { await this.connecterPrix(); } catch (e) {} await this.s.setAlarm(Date.now() + 30e3); }
  // Prix en direct (bourse IEX) : abonnement aux seules actions qui viennent d'avoir une news (30 au plus)
  async connecterPrix() {
    if (this.wsP) return;
    const c = await this.cles(); if (!c.key) return;
    const r = await fetch(IEX, { headers: { Upgrade: "websocket" } }); const ws = r.webSocket; if (!ws) return;
    ws.accept(); this.wsP = ws; this.okP = false;
    ws.addEventListener("message", (ev) => {
      let l; try { l = JSON.parse(ev.data); } catch (e) { return; }
      for (const m of Array.isArray(l) ? l : [l]) {
        if (m.T === "success" && m.msg === "connected") ws.send(JSON.stringify({ action: "auth", key: c.key, secret: c.secret }));
        else if (m.T === "success" && m.msg === "authenticated") { this.okP = true; const syms = [...this.suivis.keys()]; if (syms.length) ws.send(JSON.stringify({ action: "subscribe", trades: syms })); }
        else if (m.T === "t") { const x = this.suivis.get(m.S); if (x) x.tr.push([Date.parse(m.t), m.p]); }
      }
    });
    const fin = () => { this.wsP = null; this.okP = false; };
    ws.addEventListener("close", fin); ws.addEventListener("error", fin);
  }
  suivre(sym) {
    if (this.suivis.has(sym)) return this.suivis.get(sym);
    if (this.suivis.size >= 30) { const plusVieux = [...this.suivis.entries()].sort((a, b) => a[1].debut - b[1].debut)[0]; this.lacher(plusVieux[0]); }
    const x = { debut: Date.now(), tr: [] }; this.suivis.set(sym, x);
    if (this.wsP && this.okP) this.wsP.send(JSON.stringify({ action: "subscribe", trades: [sym] }));
    return x;
  }
  lacher(sym) { this.suivis.delete(sym); if (this.wsP && this.okP) try { this.wsP.send(JSON.stringify({ action: "unsubscribe", trades: [sym] })); } catch (e) {} }
  // Réaction éclair : prix à la news, prix 5 s après ; achat papier si la hausse dépasse le seuil ; sorties testées sur l'heure qui suit
  async reagir(e, c) {
    const sym = String(e.sym || "").replace("-", "."); if (!/^[A-Z.]{1,6}$/.test(sym) || !c.key) return;
    const recu = Date.now(); const db = this.env.DB;
    for (const q of SCHEMA_ECLAIR) { try { await db.prepare(q).run(); } catch (x) {} }
    await db.prepare("INSERT OR IGNORE INTO eclair_vue VALUES (?,?,?,?,?,?)").bind(sym, e.source || "", String(e.id), recu, e.cree || null, (e.titre || "").slice(0, 300)).run();
    const a = this.actifs.get(sym); if (a && recu - a < 10 * 60e3) return; // même action déjà suivie depuis moins de 10 min : on ne rachète pas
    this.actifs.set(sym, recu);
    try { await this.connecterPrix(); } catch (x) {}
    const suivi = this.suivre(sym);
    const p = (await this.prix([sym], c))[sym]; const p0 = p ? p.p : null; const age0 = p ? recu - Date.parse(p.t) : null;
    const cle = `${sym}|${recu}`;
    await db.prepare("INSERT OR IGNORE INTO eclair (cle, sym, source, titre, recu, cree, p0, age0) VALUES (?,?,?,?,?,?,?,?)").bind(cle, sym, e.source || "", (e.titre || "").slice(0, 300), recu, e.cree || null, p0, age0).run();
    if (p0 == null) return;
    await new Promise((r) => setTimeout(r, 5000));
    const recents = suivi.tr.filter(([ms]) => ms > recu);
    let p5 = recents.length ? recents[recents.length - 1][1] : null;
    if (p5 == null) { const q = (await this.prix([sym], c))[sym]; if (q && Date.parse(q.t) > recu) p5 = q.p; }
    const t5 = Date.now();
    // Pitch 11.11 : de combien le titre avait déjà bougé entre la publication de la news et notre achat ?
    let ppub = null;
    if (e.cree && e.cree < recu) try {
      const h = await fetch(`${DATA}/v2/stocks/${encodeURIComponent(sym)}/trades?feed=iex&limit=1000&start=${new Date(e.cree - 30 * 60e3).toISOString()}&end=${new Date(e.cree).toISOString()}&sort=desc`, { headers: { "APCA-API-KEY-ID": c.key, "APCA-API-SECRET-KEY": c.secret } });
      if (h.ok) { const j = await h.json(); const t = (j.trades || [])[0]; if (t) ppub = t.p; }
    } catch (x) {}
    await db.prepare("UPDATE eclair SET p5 = ?, ppub = ?, t5 = ? WHERE cle = ?").bind(p5, ppub, t5, cle).run();
    const achats = SEUILS_ECLAIR.filter((s) => p5 != null && p5 >= p0 * (1 + s / 100)).map((s) => ({ seuil: s, entree: p5 * (1 + G) }));
    for (const x of achats) await db.prepare("INSERT OR IGNORE INTO eclair_trade VALUES (?,?,?,?,?,?,?)").bind(cle, x.seuil, sym, x.entree, t5, null, "ouvert").run();
    await new Promise((r) => setTimeout(r, 60 * 60e3 - 5000));
    const apres = suivi.tr.filter(([ms]) => ms > t5);
    const dans5 = suivi.tr.filter(([ms]) => ms > recu && ms <= recu + 5 * 60e3).map((x) => x[1]);
    const st = [db.prepare("UPDATE eclair SET max5m = ?, min5m = ?, fin = 1 WHERE cle = ?").bind(dans5.length ? Math.max(...dans5) : null, dans5.length ? Math.min(...dans5) : null, cle)];
    for (const x of achats) st.push(db.prepare("UPDATE eclair_trade SET sorties = ?, statut = 'ferme' WHERE cle = ? AND seuil = ?").bind(JSON.stringify(calculerSorties(apres, x.entree, t5, p0)), cle, x.seuil));
    await db.batch(st);
    if (this.actifs.get(sym) === recu) { this.actifs.delete(sym); this.lacher(sym); }
  }
  async connecter() {
    if (this.ws) return;
    const c = await this.cles(); if (!c.key) { await this.s.put("erreur", { quand: new Date().toISOString(), texte: "pas de clés Alpaca" }); return; }
    await this.env.DB.prepare(SCHEMA_FLUX).run();
    const r = await fetch(WS, { headers: { Upgrade: "websocket" } });
    const ws = r.webSocket;
    if (!ws) { await this.s.put("erreur", { quand: new Date().toISOString(), texte: "connexion refusée : HTTP " + r.status }); return; }
    ws.accept(); this.ws = ws; this.ok = false;
    await this.noter("connecteLe", new Date().toISOString());
    ws.addEventListener("message", (ev) => this.state.waitUntil(this.message(ev.data, c)));
    const fin = (quoi) => { this.ws = null; this.ok = false; this.state.waitUntil(this.s.put("erreur", { quand: new Date().toISOString(), texte: quoi })); };
    ws.addEventListener("close", (ev) => fin(`connexion fermée (${ev.code} ${ev.reason || ""})`));
    ws.addEventListener("error", () => fin("erreur de connexion"));
  }
  async message(data, c) {
    let l; try { l = JSON.parse(data); } catch (e) { return; }
    for (const m of Array.isArray(l) ? l : [l]) {
      if (m.T === "success" && m.msg === "connected") this.ws.send(JSON.stringify({ action: "auth", key: c.key, secret: c.secret }));
      else if (m.T === "success" && m.msg === "authenticated") { this.ok = true; this.ws.send(JSON.stringify({ action: "subscribe", news: ["*"] })); await this.noter("authentifieLe", new Date().toISOString()); await this.s.delete("erreur"); }
      else if (m.T === "subscription") await this.noter("abonnement", m.news);
      else if (m.T === "error") await this.s.put("erreur", { quand: new Date().toISOString(), texte: `Alpaca : ${m.code} ${m.msg}` });
      else if (m.T === "n") await this.news(m, c);
    }
  }
  async prix(syms, c) {
    const r = await fetch(`${DATA}/v2/stocks/trades/latest?symbols=${syms.map(encodeURIComponent).join(",")}&feed=iex`, { headers: { "APCA-API-KEY-ID": c.key, "APCA-API-SECRET-KEY": c.secret } });
    if (!r.ok) return {}; const j = await r.json(); return j.trades || {};
  }
  async news(m, c) {
    const recu = Date.now(); const cree = Date.parse(m.created_at) || null;
    const syms = (m.symbols || []).filter((x) => /^[A-Z.]{1,6}$/.test(x)).slice(0, 3);
    const e = (await this.s.get("etat")) || {}; e.recues = (e.recues || 0) + 1; e.derniere = new Date(recu).toISOString(); await this.s.put("etat", e);
    if (!syms.length) return;
    for (const sy of syms) this.state.waitUntil(this.reagir({ id: m.id, sym: sy, source: m.source || "benzinga", titre: m.headline, cree }, c));
    const p = await this.prix(syms, c);
    await this.env.DB.batch(syms.map((s) => this.env.DB.prepare("INSERT OR IGNORE INTO flux (id, sym, recu, cree, titre, auteur, source, url, p0, t0) VALUES (?,?,?,?,?,?,?,?,?,?)")
      .bind(String(m.id), s, recu, cree, m.headline || "", m.author || "", m.source || "", m.url || "", p[s] ? p[s].p : null, p[s] ? Date.parse(p[s].t) : null)));
    for (const [sec, col] of DELAIS) setTimeout(() => this.state.waitUntil((async () => {
      const q = await this.prix(syms, c);
      const st = syms.filter((s) => q[s]).map((s) => this.env.DB.prepare(`UPDATE flux SET ${col} = ?${col === "p5" ? ", t5 = ?" : ""} WHERE id = ? AND sym = ?`).bind(...(col === "p5" ? [q[s].p, Date.parse(q[s].t)] : [q[s].p]), String(m.id), s));
      if (st.length) await this.env.DB.batch(st);
    })()), sec * 1000);
  }
}

export async function statsFlux(db) {
  await db.prepare(SCHEMA_FLUX).run();
  const l = (await db.prepare("SELECT * FROM flux ORDER BY recu DESC LIMIT 300").all()).results;
  const ret = l.filter((x) => x.cree).map((x) => (x.recu - x.cree) / 1000).sort((a, b) => a - b);
  // course contre nos autres sources (SEC, PR Newswire) : même action, à moins d'une heure d'écart
  const course = (await db.prepare(`SELECT f.sym, f.titre, f.recu, n.vu, n.source FROM flux f JOIN news n ON n.sym = f.sym AND ABS(n.vu - f.recu) < 3600000 ORDER BY f.recu DESC LIMIT 200`).all()).results;
  const pc = (a, b) => (a && b ? +(100 * (b / a - 1)).toFixed(2) : null);
  return { recues: l.length, retardMedianS: ret.length ? +ret[Math.floor(ret.length / 2)].toFixed(1) : null,
    course: { paires: course.length, benzingaPremier: course.filter((x) => x.recu <= x.vu).length, avanceMedianeS: course.length ? Math.round([...course.map((x) => (x.vu - x.recu) / 1000)].sort((a, b) => a - b)[Math.floor(course.length / 2)]) : null },
    dernieres: l.slice(0, 40).map((x) => ({ sym: x.sym, titre: x.titre, recu: x.recu, retardS: x.cree ? +((x.recu - x.cree) / 1000).toFixed(1) : null, prixAge: x.t0 ? Math.round((x.recu - x.t0) / 1000) : null, m5: pc(x.p0, x.p5), m30: pc(x.p0, x.p30), m60: pc(x.p0, x.p60), m300: pc(x.p0, x.p300) })) };
}

export async function statsEclair(db) {
  for (const q of SCHEMA_ECLAIR) await db.prepare(q).run();
  const ev = (await db.prepare("SELECT * FROM eclair ORDER BY recu DESC LIMIT 300").all()).results;
  const tr = (await db.prepare("SELECT t.*, e.titre, e.source, e.p0, e.recu FROM eclair_trade t JOIN eclair e ON e.cle = t.cle ORDER BY t.t_entree DESC LIMIT 500").all()).results;
  const res = {};
  for (const t of tr) {
    if (!t.sorties) continue; const so = JSON.parse(t.sorties); const groupe = (t.p0 || 0) >= 1 ? "1 $ et plus" : "moins de 1 $";
    for (const [v, r] of Object.entries(so)) { const k = `${t.seuil}|${groupe}|${v}`; const x = (res[k] = res[k] || { seuil: t.seuil, groupe, sortie: v, trades: 0, gagnants: 0, gain: 0 }); x.trades++; if (r.pct > 0) x.gagnants++; x.gain += r.pct * 1000; }
  }
  // qui voit la news en premier, chez nous : même action, sources différentes, à moins de 10 min
  const vues = (await db.prepare("SELECT * FROM eclair_vue ORDER BY recu DESC LIMIT 2000").all()).results;
  const groupes = []; for (const v of [...vues].reverse()) { const g = groupes.find((x) => x.sym === v.sym && v.recu - x.debut < 10 * 60e3); if (g) g.v.push(v); else groupes.push({ sym: v.sym, debut: v.recu, v: [v] }); }
  const premier = {}; for (const g of groupes) { const p = g.v[0].source; const x = (premier[p] = premier[p] || { source: p, premier: 0, total: 0 }); x.premier++; }
  for (const v of vues) (premier[v.source] = premier[v.source] || { source: v.source, premier: 0, total: 0 }).total++;
  const pc = (a, b) => (a && b ? +(100 * (b / a - 1)).toFixed(2) : null);
  // avance du titre avant qu'on puisse acheter : prix à la publication -> prix à notre achat possible (5 s après réception)
  const av = ev.filter((x) => x.ppub && x.p5 && x.cree);
  const med = (a) => { if (!a.length) return null; const t = [...a].sort((p, q) => p - q); return t[Math.floor(t.length / 2)]; };
  const avance = { news: av.length, retardMedianS: med(av.map((x) => (x.t5 - x.cree) / 1000)), avanceMedianePct: med(av.map((x) => 100 * (x.p5 / x.ppub - 1))),
    parSource: Object.values(av.reduce((m, x) => { const k = x.source; const y = (m[k] = m[k] || { source: k, news: 0, r: [], a: [] }); y.news++; y.r.push((x.t5 - x.cree) / 1000); y.a.push(100 * (x.p5 / x.ppub - 1)); return m; }, {})).map((y) => ({ source: y.source, news: y.news, retardMedianS: med(y.r), avanceMedianePct: med(y.a) })) };
  return { avance, evenements: ev.length, achats: tr.length, resultats: Object.values(res).map((x) => ({ ...x, gain: Math.round(x.gain) })).sort((a, b) => b.gain - a.gain),
    premiers: Object.values(premier).sort((a, b) => b.premier - a.premier),
    derniers: ev.slice(0, 40).map((x) => ({ avantNous: pc(x.ppub, x.p5), retardS: x.cree && x.t5 ? Math.round((x.t5 - x.cree) / 1000) : null, sym: x.sym, source: x.source, titre: x.titre, recu: x.recu, age0: x.age0, p0: x.p0, m5s: pc(x.p0, x.p5), max5m: pc(x.p0, x.max5m), min5m: pc(x.p0, x.min5m), achete: tr.some((t) => t.cle === x.cle) })) };
}
