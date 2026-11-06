// sans-perte — cherche sur Polymarket les portefeuilles qui n'ont jamais perdu une position
// Source : API publique Polymarket v2 (classement tous temps trié par gain + positions par portefeuille)
import { DurableObject } from 'cloudflare:workers';

const D = 'https://data-api.polymarket.com/v2';
const MIN_POS = 20;            // décision de Pitch : 20 minimum
const SEUIL = -0.005;          // en dessous d'un demi-centime = vraie perte (au-dessus = bruit d'arrondi)
const PAGES_CLASSEMENT = 30;   // pages de 50 lues par réveil
const LOT = 36;                // portefeuilles vérifiés par réveil
const PARALLELE = 6;

async function api(path) {
  for (let essai = 0; essai < 3; essai++) {
    const r = await fetch(D + path, { headers: { accept: 'application/json', 'user-agent': 'sans-perte/1.0' } });
    if (r.status === 429) { const e = new Error('429'); e.retry = +(r.headers.get('retry-after') || 30); throw e; }
    if (r.status >= 500) { await new Promise(s => setTimeout(s, 800 * (essai + 1))); continue; }
    if (!r.ok) throw new Error(r.status + ' ' + (await r.text()).slice(0, 120));
    return r.json();
  }
  throw new Error('5xx répété');
}

export class Scan extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`CREATE TABLE IF NOT EXISTS etat(k TEXT PRIMARY KEY, v TEXT)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS w(addr TEXT PRIMARY KEY, nom TEXT, rang INT, pnl REAL, vol REAL,
      statut TEXT DEFAULT 'a_verifier', pire REAL, pire_titre TEXT, nb_pos INT, dernier_ts INT, verifie_at INT, erreur TEXT)`);
    this.sql.exec(`CREATE INDEX IF NOT EXISTS w_statut ON w(statut, rang)`);
  }
  get(k, d = null) { const r = this.sql.exec(`SELECT v FROM etat WHERE k=?`, k).toArray(); return r.length ? r[0].v : d; }
  set(k, v) { this.sql.exec(`INSERT INTO etat(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v`, k, String(v)); }

  async demarrer() { if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + 1000); return this.etat(); }

  async alarm() {
    let pause = 2000;
    try {
      if (this.get('classement_fini') !== '1') await this.lireClassement();
      await this.verifierLot();
    } catch (e) {
      if (e.retry) { pause = e.retry * 1000; this.set('dernier_429', new Date().toISOString()); }
      else this.set('derniere_erreur', new Date().toISOString() + ' ' + e.message);
    }
    this.set('dernier_reveil', new Date().toISOString());
    const reste = this.sql.exec(`SELECT count(*) n FROM w WHERE statut='a_verifier'`).one().n;
    if (reste > 0 || this.get('classement_fini') !== '1') await this.ctx.storage.setAlarm(Date.now() + pause);
    else this.set('fini_at', new Date().toISOString());
  }

  async lireClassement() {
    let cur = this.get('curseur', '');
    for (let p = 0; p < PAGES_CLASSEMENT; p++) {
      const k = await api('/leaderboard?limit=50&timePeriod=ALL&orderBy=PNL' + (cur ? '&cursor=' + encodeURIComponent(cur) : ''));
      let fini = false;
      for (const x of k.data) {
        if (!(x.pnl > 0)) { fini = true; break; }   // un portefeuille sans perte a forcément un gain > 0
        this.sql.exec(`INSERT INTO w(addr,nom,rang,pnl,vol) VALUES(?,?,?,?,?) ON CONFLICT(addr) DO UPDATE SET pnl=excluded.pnl, vol=excluded.vol, rang=excluded.rang, nom=excluded.nom`,
          x.user_id, x.user_name || '', x.rank, x.pnl, x.volume || 0);
      }
      cur = k.pagination && k.pagination.next_cursor;
      this.set('curseur', cur || '');
      this.set('classement_lus', this.sql.exec(`SELECT count(*) n FROM w`).one().n);
      if (fini || !cur) { this.set('classement_fini', '1'); this.set('classement_fini_at', new Date().toISOString()); return; }
    }
  }

  async verifierLot() {
    const lot = this.sql.exec(`SELECT addr FROM w WHERE statut='a_verifier' ORDER BY rang LIMIT ?`, LOT).toArray();
    for (let i = 0; i < lot.length; i += PARALLELE) {
      const res = await Promise.allSettled(lot.slice(i, i + PARALLELE).map(x => this.verifier(x.addr)));
      const r429 = res.find(r => r.status === 'rejected' && r.reason && r.reason.retry);
      res.forEach((r, j) => {
        const a = lot[i + j].addr;
        if (r.status === 'fulfilled') {
          const v = r.value;
          this.sql.exec(`UPDATE w SET statut=?, pire=?, pire_titre=?, nb_pos=?, dernier_ts=?, verifie_at=?, erreur=NULL WHERE addr=?`,
            v.statut, v.pire ?? null, v.titre ?? null, v.nb ?? null, v.dernier ?? null, Date.now(), a);
        } else if (!r.reason.retry) {
          this.sql.exec(`UPDATE w SET statut='erreur', erreur=?, verifie_at=? WHERE addr=?`, String(r.reason.message).slice(0, 200), Date.now(), a);
        }
      });
      if (r429) throw r429.reason;
    }
  }

  // Une position perdante = gain réalisé négatif, ou position terminée (marché résolu / fermée) avec gain total négatif.
  // Les positions encore ouvertes (marché pas résolu) ne comptent pas comme perdues.
  async verifier(addr) {
    const a = await api(`/positions?user=${addr}&sort_by=REALIZED_PNL&sort_direction=ASC&limit=1`);
    const p0 = a.data[0];
    if (p0 && p0.realized_pnl < SEUIL) return { statut: 'perdant', pire: p0.realized_pnl, titre: p0.title };
    let cur = '';
    for (let page = 0; page < 10; page++) {
      const b = await api(`/positions?user=${addr}&sort_by=TOTAL_PNL&sort_direction=ASC&limit=100` + (cur ? '&cursor=' + encodeURIComponent(cur) : ''));
      let stop = false;
      for (const x of b.data) {
        if (!(x.total_pnl < SEUIL)) { stop = true; break; }
        if (x.status !== 'OPEN') return { statut: 'perdant', pire: x.total_pnl, titre: x.title };
      }
      cur = b.pagination && b.pagination.next_cursor;
      if (stop || !cur) break;
      if (page === 9) return { statut: 'erreur_trop_ouvertes' };
    }
    // nombre de positions terminées (marchés), on s'arrête dès qu'on atteint le minimum
    let nb = 0; cur = '';
    for (let page = 0; page < 40 && nb < MIN_POS; page++) {
      const c = await api(`/positions?user=${addr}&limit=500` + (cur ? '&cursor=' + encodeURIComponent(cur) : ''));
      nb += c.data.filter(x => x.status !== 'OPEN').length;
      cur = c.pagination && c.pagination.next_cursor;
      if (!cur) break;
    }
    const act = await api(`/activity?user=${addr}&limit=1`);
    const dernier = act.data[0] ? act.data[0].timestamp : null;
    return { statut: nb >= MIN_POS ? 'gagnant' : 'trop_peu', nb, dernier, pire: 0 };
  }

  etat() {
    const c = {}; for (const r of this.sql.exec(`SELECT statut, count(*) n FROM w GROUP BY statut`)) c[r.statut] = r.n;
    const e = {}; for (const r of this.sql.exec(`SELECT k,v FROM etat WHERE k<>'curseur'`)) e[r.k] = r.v;
    return { compteurs: c, ...e };
  }
  liste() {
    return this.sql.exec(`SELECT addr,nom,rang,pnl,vol,nb_pos,dernier_ts,verifie_at FROM w WHERE statut='gagnant' ORDER BY pnl DESC`).toArray();
  }
  echantillon(statut, n) {
    return this.sql.exec(`SELECT addr,nom,rang,pnl,pire,pire_titre,nb_pos,erreur FROM w WHERE statut=? ORDER BY rang LIMIT ?`, statut, n).toArray();
  }
}

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    const scan = env.SCAN.get(env.SCAN.idFromName('principal'));
    if (u.pathname === '/api/etat') return json(await scan.etat());
    if (u.pathname === '/api/liste') return json(await scan.liste());
    if (u.pathname === '/api/demarrer') return json(await scan.demarrer());
    if (u.pathname === '/api/echantillon') return json(await scan.echantillon(u.searchParams.get('statut') || 'perdant', +(u.searchParams.get('n') || 20)));
    return env.ASSETS.fetch(req);
  },
  async scheduled(ev, env) { await env.SCAN.get(env.SCAN.idFromName('principal')).demarrer(); }
};
