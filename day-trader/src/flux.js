// Pitch 11.11 : « je veux acheter 5 s après la news max ». Flux de news EN DIRECT (Benzinga, via un compte
// d'essai Alpaca) : une connexion ouverte en permanence, la news arrive dès sa sortie. À chaque news, on prend
// le dernier prix (bourse IEX, gratuit) tout de suite, puis 5 s, 30 s, 60 s et 5 min après.
// Clés Alpaca rangées dans la table config de D1 (jamais dans le code).
export const SCHEMA_FLUX = "CREATE TABLE IF NOT EXISTS flux (id TEXT, sym TEXT, recu INTEGER, cree INTEGER, titre TEXT, auteur TEXT, source TEXT, url TEXT, p0 REAL, t0 INTEGER, p5 REAL, t5 INTEGER, p30 REAL, p60 REAL, p300 REAL, PRIMARY KEY (id, sym))";
const WS = "https://stream.data.alpaca.markets/v1beta1/news";
const DATA = "https://data.alpaca.markets";
const DELAIS = [[5, "p5"], [30, "p30"], [60, "p60"], [300, "p300"]];

export class Flux {
  constructor(state, env) { this.state = state; this.env = env; this.s = state.storage; this.ws = null; this.ok = false; }
  async cles() {
    const r = (await this.env.DB.prepare("SELECT cle, valeur FROM config WHERE cle IN ('alpaca_key','alpaca_secret')").all()).results;
    const m = Object.fromEntries(r.map((x) => [x.cle, x.valeur])); return { key: m.alpaca_key, secret: m.alpaca_secret };
  }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/demarrer") { await this.connecter(); if (!(await this.s.getAlarm())) await this.s.setAlarm(Date.now() + 30e3); return Response.json(await this.etat()); }
    if (u.pathname === "/etat") return Response.json(await this.etat());
    return new Response("?", { status: 404 });
  }
  async etat() { return { connecte: !!this.ws, authentifie: this.ok, ...(await this.s.get("etat")), erreur: await this.s.get("erreur") }; }
  async noter(k, v) { const e = (await this.s.get("etat")) || {}; e[k] = v; await this.s.put("etat", e); }
  async alarm() { try { await this.connecter(); } catch (e) {} await this.s.setAlarm(Date.now() + 30e3); }
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
