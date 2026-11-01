import { lireResultats, verifierGrille, rangSuperStar, gainSuperStar, tiragesDepuis } from './resultats.js';

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json; charset=utf-8' } });

const MODELES = [
  '@cf/meta/llama-4-scout-17b-16e-instruct',
  '@cf/mistralai/mistral-small-3.1-24b-instruct',
  '@cf/google/gemma-3-12b-it',
];

const CONSIGNE = `Tu lis la photo d'un billet EuroMillions suisse (Loterie Romande ou Swisslos).
Réponds UNIQUEMENT par un objet JSON, sans texte autour, de la forme :
{"dates":["AAAA-MM-JJ"],"premier_tirage":"AAAA-MM-JJ","nombre_tirages":1,"grilles":[{"numeros":[n,n,n,n,n],"etoiles":[e,e]}],"super_star":["A123B"]}
Règles :
- "grilles" : chaque ligne jouée, 5 numéros entre 1 et 50 puis 2 étoiles entre 1 et 12. Recopie exactement ce qui est imprimé, dans l'ordre des lignes.
- "dates" : toutes les dates de tirage imprimées (format suisse JJ.MM.AA → AAAA-MM-JJ). Les tirages ont lieu le mardi et le vendredi.
- "premier_tirage" et "nombre_tirages" : si le billet indique une durée (ex. « 4 tirages », « Durée ») ou une période, sinon le nombre de dates.
- "super_star" : les codes Super-Star imprimés (5 caractères : une lettre, trois chiffres, une lettre). Liste vide s'il n'y en a pas.
- N'invente rien : si une valeur est illisible, mets null.`;

function extraitJSON(t) {
  if (t && typeof t === 'object') return t;
  t = String(t || '');
  const i = t.indexOf('{'), j = t.lastIndexOf('}');
  if (i < 0 || j < i) return null;
  try { return JSON.parse(t.slice(i, j + 1)); } catch { return null; }
}

function propre(o) {
  const ent = (v, min, max) => { const n = parseInt(v, 10); return n >= min && n <= max ? n : null; };
  const dateOk = d => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d) ? d : null;
  const grilles = (Array.isArray(o?.grilles) ? o.grilles : []).map(g => ({
    numeros: (g?.numeros || []).slice(0, 5).map(v => ent(v, 1, 50)),
    etoiles: (g?.etoiles || []).slice(0, 2).map(v => ent(v, 1, 12)),
  }));
  const dates = (Array.isArray(o?.dates) ? o.dates : []).map(dateOk).filter(Boolean);
  const premier = dateOk(o?.premier_tirage) || dates[0] || null;
  const nombre = ent(o?.nombre_tirages, 1, 200) || Math.max(1, dates.length);
  const superStar = (Array.isArray(o?.super_star) ? o.super_star : [])
    .map(c => String(c || '').toUpperCase().replace(/[^A-Z0-9]/g, '')).filter(c => c.length === 5);
  return { dates, premier_tirage: premier, nombre_tirages: nombre, grilles, super_star: superStar };
}

async function lireBillet(env, image) {
  const erreurs = [];
  for (const modele of MODELES) {
    try {
      const r = await env.AI.run(modele, {
        messages: [{ role: 'user', content: [
          { type: 'text', text: CONSIGNE },
          { type: 'image_url', image_url: { url: image } },
        ] }],
        max_tokens: 2048,
        temperature: 0,
      });
      const o = extraitJSON(r?.response ?? r?.choices?.[0]?.message?.content ?? r);
      if (o && Array.isArray(o.grilles) && o.grilles.length) return { modele, ...propre(o) };
      erreurs.push(modele + ' : réponse sans grille');
    } catch (e) {
      erreurs.push(modele + ' : ' + String(e.message || e).slice(0, 200));
    }
  }
  return { erreur: 'Billet illisible', details: erreurs };
}

async function resultats(dateIso) {
  const [a, m, j] = dateIso.split('-');
  const url = `https://www.euro-millions.com/fr/resultats/${j}-${m}-${a}`;
  const cache = caches.default;
  const cle = new Request('https://cache.euromillions/' + dateIso);
  const deja = await cache.match(cle);
  if (deja) return deja.json();
  const r = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1', 'accept-language': 'fr-CH,fr' } });
  if (!r.ok) return null;
  const res = lireResultats(await r.text(), dateIso);
  // On ne garde en cache qu'un tirage complet (gains suisses publiés)
  if (res && Object.keys(res.rangs).length >= 13) {
    await cache.put(cle, new Response(JSON.stringify(res), { headers: { 'cache-control': 'max-age=21600' } }));
  }
  return res;
}

function aujourdhuiSuisse() {
  return new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Zurich' }).format(new Date());
}

async function verifier(corps) {
  const grilles = (corps.grilles || []).filter(g => g.numeros?.length === 5 && g.etoiles?.length === 2 && [...g.numeros, ...g.etoiles].every(Number.isInteger));
  const superStar = (corps.super_star || []).map(c => String(c).toUpperCase().replace(/[^A-Z0-9]/g, '')).filter(c => c.length === 5);
  let dates = (corps.dates || []).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d));
  if (corps.premier_tirage && corps.nombre_tirages > dates.length) dates = tiragesDepuis(corps.premier_tirage, corps.nombre_tirages);
  dates = [...new Set(dates)].sort();
  if (!dates.length) return { erreur: 'Aucune date de tirage' };
  if (!grilles.length && !superStar.length) return { erreur: 'Aucune grille valable' };

  const auj = aujourdhuiSuisse();
  const tirages = [];
  let total = 0;
  for (const d of dates) {
    if (d > auj) { tirages.push({ date: d, etat: 'a_venir' }); continue; }
    const res = await resultats(d);
    if (!res) { tirages.push({ date: d, etat: d === auj ? 'a_venir' : 'introuvable' }); continue; }
    const lignes = grilles.map(g => ({ ...g, ...verifierGrille(g, res) }));
    const ss = superStar.map(code => { const rang = rangSuperStar(code, res.superStar); return { code, rang, gain: gainSuperStar(rang, res) }; });
    const sousTotal = lignes.reduce((s, l) => s + l.gain + l.swissWinGain, 0) + ss.reduce((s, x) => s + x.gain, 0);
    total += sousTotal;
    tirages.push({ date: d, etat: 'ok', numeros: res.numeros, etoiles: res.etoiles, swissWin: res.swissWin, superStar: res.superStar, lignes, superStarLignes: ss, total: Math.round(sousTotal * 100) / 100 });
  }
  return { total: Math.round(total * 100) / 100, tirages };
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    try {
      if (u.pathname === '/api/lire' && req.method === 'POST') {
        const { image } = await req.json();
        if (!image || !String(image).startsWith('data:image/')) return json({ erreur: 'Photo manquante' }, 400);
        return json(await lireBillet(env, image));
      }
      if (u.pathname === '/api/verifier' && req.method === 'POST') {
        return json(await verifier(await req.json()));
      }
      if (u.pathname === '/api/controle') {
        // Contrôle après déploiement : lecture du billet d'essai + vérification sur le tirage du 30.10.2026
        const img = await env.ASSETS.fetch(new Request(new URL('/essai.jpg', u)));
        const buf = new Uint8Array(await img.arrayBuffer());
        let bin = ''; for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode(...buf.subarray(i, i + 0x8000));
        const lu = await lireBillet(env, 'data:image/jpeg;base64,' + btoa(bin));
        const v = await verifier({ dates: ['2026-10-30'], grilles: [{ numeros: [3, 12, 14, 40, 41], etoiles: [3, 5] }, { numeros: [13, 19, 39, 1, 2], etoiles: [1, 5] }], super_star: ['N538X'] });
        return json({ lu, verification: v });
      }
    } catch (e) {
      return json({ erreur: String(e.message || e) }, 500);
    }
    return env.ASSETS.fetch(req);
  },
};
