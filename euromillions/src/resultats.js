// Lecture des résultats d'un tirage sur euro-millions.com (page en français).
// Tableau suisse en CHF (#PrizeCH), Super-Star et Swiss Win (#DrawCH).

const nettoie = s => s.replace(/<[^>]+>/g, ' ').replace(/&nbsp;|&#160;/g, ' ').replace(/\s+/g, ' ').trim();
const montant = s => {
  const t = nettoie(s).replace(/CHF|&[a-z]+;/gi, '').replace(/[\s ']/g, '').replace(',', '.');
  const v = parseFloat(t);
  return Number.isFinite(v) ? v : null;
};

function bloc(html, debut, fin) {
  const i = html.indexOf(debut);
  if (i < 0) return '';
  const j = fin ? html.indexOf(fin, i + debut.length) : -1;
  return html.slice(i, j > 0 ? j : i + 40000);
}

function boules(ul) {
  return [...ul.matchAll(/<li class="resultBall ([^"]*)">\s*(\d+)\s*<\/li>/g)].map(m => ({ cls: m[1], v: +m[2] }));
}

function lignes(table) {
  return [...table.matchAll(/<tr([^>]*)>([\s\S]*?)<\/tr>/g)].filter(m => !/totals/.test(m[1])).map(m => m[2]).filter(r => /<td/.test(r));
}

export function lireResultats(html, dateIso) {
  // Le titre doit porter la bonne date, sinon la page n'est pas celle du tirage demandé
  const [a, m, j] = dateIso.split('-').map(Number);
  const mois = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][m - 1];
  const titre = (html.match(/<title>([\s\S]*?)<\/title>/) || [])[1] || '';
  if (!titre.toLowerCase().includes(`${j} ${mois} ${a}`)) return null;

  const ulAsc = (html.match(/<ul class="balls" id="ballsAscending">([\s\S]*?)<\/ul>/) || [])[1];
  if (!ulAsc) return null;
  const b = boules(ulAsc);
  const numeros = b.filter(x => /\bball\b/.test(x.cls)).map(x => x.v);
  const etoiles = b.filter(x => /lucky-star/.test(x.cls)).map(x => x.v);
  if (numeros.length !== 5 || etoiles.length !== 2) return null;

  // Rangs suisses en CHF
  const rangs = {};
  const ch = bloc(html, '<div id="PrizeCH"', '</table>');
  for (const r of lignes(ch)) {
    const nb = (r.match(/<span class="ball">\s*(\d)/) || [])[1];
    const et = (r.match(/<span class="star">\s*(\d)/) || [])[1] || '0';
    const tds = [...r.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(x => x[1]);
    if (nb == null || tds.length < 2) continue;
    rangs[`${nb}+${et}`] = { gain: montant(tds[1]), gagnants: montant(tds[2] || '') };
  }

  // Super-Star et Swiss Win
  const zoneCH = html.slice(html.indexOf('<div id="DrawCH"'));
  const superStar = (zoneCH.match(/<div class="superStar">\s*([A-Z0-9]{5})\s*<\/div>/) || [])[1] || null;
  const tSS = (zoneCH.match(/<div class="superStar">[\s\S]*?<table[\s\S]*?<\/table>/) || [''])[0];
  const superStarGains = lignes(tSS).map(r => {
    const tds = [...r.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(x => x[1]);
    return { libelle: nettoie(tds[0] || ''), gain: montant(tds[1] || '') };
  });

  const iSW = zoneCH.indexOf('id="second-chance"');
  let swissWin = null, swissWinGains = {};
  if (iSW >= 0) {
    const z = zoneCH.slice(iSW);
    const ul = (z.match(/<ul class="balls">([\s\S]*?)<\/ul>/) || [])[1] || '';
    swissWin = boules(ul).map(x => x.v);
    const t = (z.match(/<table[\s\S]*?<\/table>/) || [''])[0];
    for (const r of lignes(t)) {
      const tds = [...r.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map(x => x[1]);
      const n = (nettoie(tds[0] || '').match(/^(\d)/) || [])[1];
      if (n) swissWinGains[n] = montant(tds[1] || '');
    }
  }

  return { date: dateIso, numeros, etoiles, rangs, superStar, superStarGains, swissWin, swissWinGains };
}

// Barème Super-Star dans l'ordre de la page (9 lignes). Montants par défaut si la page ne les donne pas.
const SS_DEFAUT = [250000, 5000, 2000, 1000, 275, 50, 20, 10, 4];

export function rangSuperStar(code, tire) {
  code = (code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (code.length !== 5 || !tire) return 0;
  let p = 0; while (p < 5 && code[p] === tire[p]) p++;
  let s = 0; while (s < 5 && code[4 - s] === tire[4 - s]) s++;
  if (p === 5) return 1;
  if (p === 2 && s === 2) return 2;
  if ((p === 3 && s === 1) || (p === 1 && s === 3)) return 3;
  if (p === 4 || s === 4) return 4;
  if ((p === 2 && s === 1) || (p === 1 && s === 2)) return 5;
  if (p === 3 || s === 3) return 6;
  if (p === 1 && s === 1) return 7;
  if (p === 2 || s === 2) return 8;
  if (p === 1 || s === 1) return 9;
  return 0;
}

export function gainSuperStar(rang, res) {
  if (!rang) return 0;
  const g = res.superStarGains[rang - 1];
  return g && g.gain != null ? g.gain : SS_DEFAUT[rang - 1];
}

const RANGS_VALIDES = ['5+2','5+1','5+0','4+2','4+1','3+2','4+0','2+2','3+1','3+0','1+2','2+1','2+0'];

export function verifierGrille(g, res) {
  const n = g.numeros.filter(x => res.numeros.includes(x)).length;
  const e = g.etoiles.filter(x => res.etoiles.includes(x)).length;
  const cle = `${n}+${e}`;
  const gain = RANGS_VALIDES.includes(cle) && res.rangs[cle] ? res.rangs[cle].gain || 0 : 0;
  let sw = 0, swGain = 0;
  if (res.swissWin && res.swissWin.length === 5) {
    sw = g.numeros.filter(x => res.swissWin.includes(x)).length;
    if (sw >= 3) swGain = res.swissWinGains[String(sw)] || 0;
  }
  return { bons: n, etoiles: e, rang: RANGS_VALIDES.includes(cle) ? cle : null, gain, swissWinBons: sw, swissWinGain: swGain };
}

// Prochains tirages (mardi et vendredi) à partir d'une date
export function tiragesDepuis(premierIso, nombre) {
  const out = [];
  const d = new Date(premierIso + 'T12:00:00Z');
  let garde = 0;
  while (out.length < nombre && garde++ < 400) {
    const j = d.getUTCDay();
    if (j === 2 || j === 5) out.push(d.toISOString().slice(0, 10));
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return out;
}
