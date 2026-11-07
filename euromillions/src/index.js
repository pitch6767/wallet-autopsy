import { lireResultats, verifierGrille, rangSuperStar, gainSuperStar, tiragesDepuis } from './resultats.js';

// Une date qui n'est ni un mardi ni un vendredi (date d'achat) devient le tirage suivant
// Remet une date lue dans l'année plausible (billet de cette année, ou de l'an passé en début d'année)
function anneePlausible(iso) {
  const auj = new Date(new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Zurich' }).format(new Date()) + 'T12:00:00Z');
  let [a, m, j] = iso.split('-').map(Number);
  const y = auj.getUTCFullYear();
  if (a !== y && a !== y - 1 && a !== y + 1) a = y;
  let d = new Date(Date.UTC(a, m - 1, j, 12));
  if (d - auj > 60 * 864e5) d = new Date(Date.UTC(a - 1, m - 1, j, 12));
  return isNaN(d) ? null : d.toISOString().slice(0, 10);
}

// Lit soi-même « MA 10.11.26 » : jour imprimé + date, l'année à 2 chiffres = 20xx
function dateDepuisTexte(t) {
  t = String(t || '').toUpperCase();
  const m = t.match(/(\d{1,2})[.\/-](\d{1,2})[.\/-](\d{2,4})/);
  if (!m) return null;
  let a = +m[3]; if (a < 100) a += 2000;
  let iso = anneePlausible(`${a}-${String(m[2]).padStart(2, '0')}-${String(m[1]).padStart(2, '0')}`);
  if (!iso) return null;
  // Le jour imprimé fait foi : on prend la date de ce jour-là la plus proche (± 3 jours)
  const jour = /\b(MA|MAR|MARDI|DI|DIE|DIENSTAG|TU|TUE)\b/.test(t) ? 2 : /\b(VE|VEN|VENDREDI|FR|FRE|FREITAG)\b/.test(t) ? 5 : null;
  if (jour != null) {
    const d = new Date(iso + 'T12:00:00Z');
    for (const k of [0, -1, 1, -2, 2, -3, 3]) {
      const x = new Date(d); x.setUTCDate(d.getUTCDate() + k);
      if (x.getUTCDay() === jour) { iso = x.toISOString().slice(0, 10); break; }
    }
  }
  return iso;
}

function versTirage(iso) {
  iso = anneePlausible(iso) || iso;
  const d = new Date(iso + 'T12:00:00Z');
  for (let k = 0; k < 7 && d.getUTCDay() !== 2 && d.getUTCDay() !== 5; k++) d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json; charset=utf-8' } });

const MODELES = [
  '@cf/meta/llama-4-scout-17b-16e-instruct',
  '@cf/mistralai/mistral-small-3.1-24b-instruct',
  '@cf/google/gemma-3-12b-it',
];

const CONSIGNE = `Tu lis la photo d'un billet EuroMillions suisse (Loterie Romande ou Swisslos).
Réponds UNIQUEMENT par un objet JSON, sans texte autour, de la forme :
{"texte_dates":["texte exact imprimé, ex. MA 10.11.26"],"dates":["AAAA-MM-JJ"],"premier_tirage":"AAAA-MM-JJ","nombre_tirages":1,"grilles":[{"numeros":[n,n,n,n,n],"etoiles":[e,e]}],"super_star":["A123B"]}
Règles :
- "grilles" : chaque ligne jouée, 5 numéros entre 1 et 50 puis 2 étoiles entre 1 et 12. Recopie exactement ce qui est imprimé, dans l'ordre des lignes.
- "dates" : toutes les dates de tirage imprimées (format suisse JJ.MM.AA → AAAA-MM-JJ). Les tirages ont lieu le mardi et le vendredi. Ne confonds pas avec la date et l'heure d'achat ou d'impression du billet (souvent en bas, avec une heure) : ne mets cette date-là que si aucune date de tirage n'est imprimée.
- "texte_dates" : recopie tel quel le texte imprimé de chaque date de tirage, avec le jour abrégé s'il y en a un (MA, VE, DI, FR…).
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
  const dateOk = d => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d) ? versTirage(d) : null;
  const grilles = (Array.isArray(o?.grilles) ? o.grilles : []).map(g => ({
    numeros: (g?.numeros || []).slice(0, 5).map(v => ent(v, 1, 50)),
    etoiles: (g?.etoiles || []).slice(0, 2).map(v => ent(v, 1, 12)),
  }));
  const depuisTexte = (Array.isArray(o?.texte_dates) ? o.texte_dates : []).map(dateDepuisTexte).filter(Boolean).map(versTirage);
  const dates = depuisTexte.length ? [...new Set(depuisTexte)] : (Array.isArray(o?.dates) ? o.dates : []).map(dateOk).filter(Boolean);
  const premier = depuisTexte[0] || dateOk(o?.premier_tirage) || dates[0] || null;
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
      if (o && Array.isArray(o.grilles) && o.grilles.length) {
        const res = { modele, ...propre(o) };
        await caches.default.put(new Request('https://cache.euromillions/dernier'), new Response(JSON.stringify({ quand: new Date().toISOString(), brut: o, res, image }), { headers: { 'cache-control': 'max-age=172800' } }));
        return res;
      }
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
  let dates = (corps.dates || []).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).map(versTirage);
  if (corps.premier_tirage) corps.premier_tirage = versTirage(corps.premier_tirage);
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
      if (u.pathname === '/api/dernier') {
        const c = await caches.default.match(new Request('https://cache.euromillions/dernier'));
        if (!c) return json({ rien: true });
        const d = await c.json();
        if (u.searchParams.has('photo')) { const b64 = d.image.split(',')[1]; const bin = atob(b64); const a = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i); return new Response(a, { headers: { 'content-type': 'image/jpeg' } }); }
        delete d.image; return json(d);
      }
      if (u.pathname === '/api/controle') {
        // Contrôle après déploiement : lecture du billet d'essai + vérification sur le tirage du 30.10.2026
        const img = await env.ASSETS.fetch(new Request(new URL('/essai.jpg', u)));
        const buf = new Uint8Array(await img.arrayBuffer());
        let bin = ''; for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode(...buf.subarray(i, i + 0x8000));
        const lu = await lireBillet(env, 'data:image/jpeg;base64,' + btoa(bin));
        const v = await verifier({ dates: ['2026-10-30'], grilles: [{ numeros: [3, 12, 14, 40, 41], etoiles: [3, 5] }, { numeros: [13, 19, 39, 1, 2], etoiles: [1, 5] }], super_star: ['N538X'] });
        const v2 = await verifier({ dates: ['2026-10-31'], grilles: [{ numeros: [9, 18, 21, 36, 40], etoiles: [5, 7] }] });
        const v3 = await verifier({ dates: ['2026-11-06'], grilles: [[16,23,26,28,49,1,8],[2,29,34,40,43,8,10],[11,25,40,42,47,5,8],[3,30,38,44,50,3,8],[10,18,23,41,50,8,11]].map(g => ({ numeros: g.slice(0,5), etoiles: g.slice(5) })) });
        return json({ lu, verification: v, samedi: v2, pitch: v3 });
      }
    } catch (e) {
      return json({ erreur: String(e.message || e) }, 500);
    }
    return env.ASSETS.fetch(req);
  },
};
