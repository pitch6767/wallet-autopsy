// QA tour 2 du convertisseur MP4 (constat seulement)
const { webkit, chromium, devices } = require('playwright');
const { execSync } = require('child_process');
const U = 'https://mp4.pitch67.workers.dev';
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';
const ADM = { 'x-admin-ts': process.env.TS, 'x-admin-sig': process.env.SIG };
const log = (...a) => console.log(...a);
const dort = (ms) => new Promise((r) => setTimeout(r, ms));
const sh = (c) => { try { return execSync(c, { encoding: 'utf8', timeout: 300000 }); } catch (e) { return 'ERREUR ' + (e.stdout || '') + (e.stderr || ''); } };

async function req(path, { method = 'GET', body, h = {} } = {}) {
  const headers = { 'user-agent': UA, ...h };
  if (body !== undefined) headers['content-type'] = 'application/json';
  const r = await fetch(U + path, { method, headers, body: body === undefined ? undefined : (typeof body === 'string' ? body : JSON.stringify(body)), redirect: 'manual' });
  const t = await r.text();
  return { s: r.status, t: t.slice(0, 400), h: r.headers };
}
const curlH = `-A '${UA}' -H 'x-admin-ts: ${ADM['x-admin-ts']}' -H 'x-admin-sig: ${ADM['x-admin-sig']}'`;
const liste = async () => { const r = await fetch(U + '/api/etat', { headers: { 'user-agent': UA, ...ADM } }); const j = await r.json(); if (!j.liste) log('etat admin sans liste :', JSON.stringify(j)); return j.liste || []; };

function sonde(run, nom) {
  log(`-- fichier ${nom} (${run})`);
  log(sh(`curl -s -o /tmp/${run}.mp4 -D /tmp/${run}.h ${curlH} -w "HTTP %{http_code} %{size_download} octets\\n" "${U}/api/fichier?run=${run}"; grep -iE "content-(type|length|disposition)" /tmp/${run}.h`));
  log(sh(`ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,codec_tag_string,profile,width,height -of compact /tmp/${run}.mp4`));
  log('   Range 1000-1999 :', sh(`curl -s -o /dev/null -D - -r 1000-1999 ${curlH} "${U}/api/fichier?run=${run}&voir=1" | grep -iE "^HTTP|content-range|content-length"`).replace(/\r?\n/g, ' | '));
}

(async () => {
  // ===== 1. Accès anonyme
  log('===== 1. ANONYME (sans en-têtes)');
  const ex = 'BUf0NnpIT4hvJAOvn';
  for (const [n, p, o] of [
    ['etat', '/api/etat', {}],
    ['lancer (lien invalide : 401 attendu avant 400)', '/api/lancer', { method: 'POST', body: { url: 'youtu.be/abc', qualite: '360p' } }],
    ['fichier', `/api/fichier?run=${ex}`, {}],
    ['fichier voir', `/api/fichier?run=${ex}&voir=1`, { h: { range: 'bytes=0-99' } }],
    ['suivi', `/api/suivi?run=${ex}`, {}],
    ['essai', '/api/essai', { method: 'POST', body: { acteur: 'x', entree: {} } }],
    ['fichier faux cookie', `/api/fichier?run=${ex}`, { h: { cookie: 'mp4acces=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef' } }],
    ['fichier fausse signature', `/api/fichier?run=${ex}`, { h: { 'x-admin-ts': String(Date.now()), 'x-admin-sig': ADM['x-admin-sig'] } }],
    ['cle fausse', '/api/cle', { method: 'POST', body: { cle: 'apify_api_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' } }],
  ]) { const r = await req(p, o); log(`${n}: HTTP ${r.s} ${r.t.slice(0, 200)}`); }
  const o = await fetch(U + '/api/lancer', { method: 'OPTIONS', headers: { 'user-agent': UA, origin: 'https://evil.example', 'access-control-request-method': 'POST' } });
  log('OPTIONS CORS: HTTP', o.status, 'allow-origin =', o.headers.get('access-control-allow-origin'));

  // ===== 2. Admin, sans coût
  log('\n===== 2. ADMIN SANS COUT');
  let L = await liste();
  log('liste (', L.length, 'entrées) :');
  for (const x of L) log(' ', JSON.stringify({ run: x.run, id: x.id, q: x.qualite, statut: x.statut, titre: x.titre, message: x.message }));
  const n0 = L.length;
  for (const l of ['youtu.be/abc', 'https://youtu.be/abc', 'abc', '', 'pas un lien', 'https://example.com/watch?v=dQw4w9WgXcQ', 'https://www.youtube.com/playlist?list=PLx', 'https://www.youtube.com/@RickAstleyYT']) {
    const r = await req('/api/lancer', { method: 'POST', body: { url: l, qualite: '720p' }, h: ADM }); log(`lancer [${l}] : HTTP ${r.s} ${r.t}`);
  }
  L = await liste(); log('entrées après liens invalides :', L.length, '(avant', n0 + ')');
  const r404 = await req('/api/xyz', { h: ADM }); log('api inconnue :', r404.s, r404.t);
  const rs = await req('/api/suivi?run=xxxxxxxxxxxxxxxxx', { h: ADM }); log('suivi run bidon :', rs.s, rs.t);
  const rf = await req('/api/fichier?run=bidon', { h: ADM }); log('fichier bidon :', rf.s, rf.t);
  log('-- Range sur fichier existant', ex);
  for (const r of ['1000-1999', '-500', '5000-', '999999999-']) log(`  -r ${r} :`, sh(`curl -s -o /dev/null -D - -r ${r} ${curlH} "${U}/api/fichier?run=${ex}&voir=1" | grep -iE "^HTTP|content-range|content-length"`).replace(/\r?\n/g, ' | '));
  log('  sans Range :', sh(`curl -s -o /dev/null -D - ${curlH} "${U}/api/fichier?run=${ex}" | grep -iE "^HTTP|content-length|accept-ranges"`).replace(/\r?\n/g, ' | '));
  log('-- codecs des fichiers « prêt » encore dans l\'historique');
  for (const x of L.filter((x) => x.statut === 'prêt')) {
    log(`  ${x.run} ${x.qualite} ${x.titre}`);
    log('   ', sh(`curl -s -r 0-3000000 -o /tmp/p.mp4 ${curlH} "${U}/api/fichier?run=${x.run}"; ffprobe -v error -show_entries stream=codec_name,width,height -of compact /tmp/p.mp4 2>&1 | head -3`).replace(/\n/g, ' '));
  }

  // ===== 3. Interface, sans coût
  log('\n===== 3. INTERFACE');
  const wb = await webkit.launch();
  const ctx = async (sch, adm = true) => { const c = await wb.newContext({ ...devices['iPhone 13'], locale: 'fr-CH', colorScheme: sch }); if (adm) await c.setExtraHTTPHeaders(ADM); return c; };
  { const c = await ctx('light', false); const p = await c.newPage(); await p.goto(U); await p.waitForTimeout(2500);
    log('anonyme iPhone :', JSON.stringify(await p.evaluate(() => ({ cle: !document.getElementById('boxCle').hidden, conv: !document.getElementById('boxConv').hidden, liste: !document.getElementById('boxListe').hidden }))));
    await p.screenshot({ path: 'iphone_anonyme.png', fullPage: true }); await c.close(); }
  for (const sch of ['light', 'dark']) {
    const c = await ctx(sch); const p = await c.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
    await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])', { timeout: 15000 }).catch(() => log('boxConv invisible')); await p.waitForTimeout(2000);
    const m = await p.evaluate(() => {
      const s = document.getElementById('qualite'), cs = getComputedStyle(s), oc = getComputedStyle(s.options[0]);
      return { sw: document.documentElement.scrollWidth, iw: innerWidth, select: { color: cs.color, bg: cs.backgroundColor, appearance: cs.webkitAppearance || cs.appearance, bgImage: cs.backgroundImage }, option: { color: oc.color, bg: oc.backgroundColor }, liste: document.getElementById('liste').innerText };
    });
    log(sch, JSON.stringify(m)); log('erreurs JS', JSON.stringify(errs));
    await p.screenshot({ path: `iphone_${sch}.png`, fullPage: true });
    await p.focus('#qualite'); await p.screenshot({ path: `iphone_${sch}_qualite.png` });
    await c.close();
  }
  { // lien invalide dans l'UI
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    for (const l of ['youtu.be/abc', 'https://example.com/x']) { await p.fill('#url', l); await p.click('#btnGo'); await p.waitForTimeout(3000); log(`UI lien [${l}] :`, JSON.stringify(await p.textContent('#msg')), await p.getAttribute('#msg', 'class'), 'bouton actif', await p.isEnabled('#btnGo')); }
    await p.screenshot({ path: 'iphone_lien_invalide.png' });
    // coupure réseau (déconnexion franche)
    await p.route('**/api/lancer', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ run: ex }) }));
    await p.fill('#url', 'https://youtu.be/jNQXAC9IVRw'); await c.setOffline(false);
    await p.click('#btnGo'); await p.waitForTimeout(500); await c.setOffline(true);
    for (const t of [5, 12]) { await p.waitForTimeout(t === 5 ? 5000 : 7000); log(`hors ligne +${t}s :`, JSON.stringify(await p.textContent('#msg'))); }
    await p.screenshot({ path: 'iphone_hors_ligne.png' });
    await c.setOffline(false); await p.waitForTimeout(10000);
    log('retour réseau +10s :', JSON.stringify(await p.textContent('#msg')), 'liens :', await p.$$eval('#res a', (a) => a.map((e) => e.textContent)));
    await p.screenshot({ path: 'iphone_retour_reseau.png' });
    await c.close();
  }
  { // réseau qui ne répond plus (requête suspendue, cas wifi→4G)
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.route('**/api/lancer', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ run: ex }) }));
    let bloque = true; await p.route('**/api/suivi*', async (r) => { if (bloque) return; r.continue(); });
    await p.fill('#url', 'https://youtu.be/jNQXAC9IVRw'); await p.click('#btnGo');
    for (const t of [10, 30, 60]) { await p.waitForTimeout(t === 10 ? 10000 : t === 30 ? 20000 : 30000); log(`suivi suspendu +${t}s :`, JSON.stringify(await p.textContent('#msg')), 'bouton actif', await p.isEnabled('#btnGo')); }
    bloque = false; await p.waitForTimeout(15000);
    log('après déblocage +15s :', JSON.stringify(await p.textContent('#msg')));
    await p.screenshot({ path: 'iphone_suivi_suspendu.png' });
    await c.close();
  }
  { // erreur serveur non JSON pendant le suivi
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.route('**/api/lancer', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ run: ex }) }));
    await p.route('**/api/suivi*', (r) => r.fulfill({ status: 502, contentType: 'text/html', body: '<html>Bad gateway</html>' }));
    await p.fill('#url', 'https://youtu.be/jNQXAC9IVRw'); await p.click('#btnGo'); await p.waitForTimeout(6000);
    log('suivi 502 HTML :', JSON.stringify(await p.textContent('#msg')));
    await c.close();
  }
  { const cb = await chromium.launch();
    for (const sch of ['light', 'dark']) { const c = await cb.newContext({ viewport: { width: 1366, height: 900 }, locale: 'fr-CH', colorScheme: sch }); await c.setExtraHTTPHeaders(ADM);
      const p = await c.newPage(); await p.goto(U); await p.waitForTimeout(2500); await p.screenshot({ path: `ordinateur_${sch}.png`, fullPage: true });
      log('ordinateur', sch, JSON.stringify(await p.evaluate(() => { const s = getComputedStyle(document.getElementById('qualite').options[1]); return { sw: document.documentElement.scrollWidth, iw: innerWidth, option: [s.color, s.backgroundColor] }; }))); await c.close(); }
    await cb.close(); }

  if (process.env.CONV !== 'oui') { await wb.close(); return; }

  // ===== 4. Conversions réelles (3 max)
  log('\n===== 4. CONVERSIONS REELLES');
  const runs = {};
  for (const [n, url, q] of [['B shorts 1080p', 'youtu.be/-ILEX-5hlbE?si=abc123', '1080p'], ['C zoo 720p (240p max)', 'https://www.youtube.com/watch?v=jNQXAC9IVRw', '720p']]) {
    const r = await req('/api/lancer', { method: 'POST', body: { url, qualite: q }, h: ADM }); log(`lancé ${n} [${url}] :`, r.s, r.t); try { runs[n] = JSON.parse(r.t).run; } catch {}
  }
  { // A : par l'interface iPhone, lien sans https, puis on ferme la page
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.fill('#url', 'youtube.com/watch?v=dQw4w9WgXcQ'); await p.selectOption('#qualite', '720p'); await p.click('#btnGo');
    await p.waitForFunction(() => /en cours/.test(document.getElementById('msg').textContent), null, { timeout: 20000 }).catch(() => {});
    log('A interface :', JSON.stringify(await p.textContent('#msg'))); await p.screenshot({ path: 'iphone_A_en_cours.png' });
    await c.close(); log('A : page fermée à', new Date().toISOString());
  }
  L = await (async () => { const r = await fetch(U + '/api/etat', { headers: { 'user-agent': UA, ...ADM } }); return (await r.json()).liste; })();
  runs['A rick 720p (UI)'] = (L.find((x) => x.id === 'dQw4w9WgXcQ' && Date.now() - x.t < 120000) || {}).run;
  log('runs', JSON.stringify(runs));
  log('attente 90 s sans aucune requête…'); await dort(90000);
  let fini = false;
  for (let k = 0; k < 20 && !fini; k++) {
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForTimeout(3000);
    const txt = await p.textContent('#liste'); const L2 = await p.evaluate(async () => (await (await fetch('/api/etat')).json()).liste);
    const st = Object.entries(runs).map(([n, r]) => [n, (L2.find((x) => x.run === r) || {}).statut]);
    log(`réouverture ${k} :`, JSON.stringify(st));
    fini = st.every(([, s]) => s && s !== 'en cours');
    if (fini || k === 19) { log('texte liste :', txt); await p.screenshot({ path: 'iphone_reouverture.png', fullPage: true });
      for (const x of L2.filter((x) => Object.values(runs).includes(x.run))) log('  entrée', JSON.stringify(x)); }
    await c.close(); if (!fini) await dort(20000);
  }
  for (const [n, r] of Object.entries(runs)) if (r) sonde(r, n);
  await wb.close();
})().catch((e) => log('ERREUR SCRIPT', e.stack));
