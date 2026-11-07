// QA tour 3 du convertisseur MP4 (constat seulement, ne modifie pas l'app)
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
  const r = await fetch(U + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), redirect: 'manual' });
  return { s: r.status, t: (await r.text()).slice(0, 300) };
}
const curlH = `-A '${UA}' -H 'x-admin-ts: ${ADM['x-admin-ts']}' -H 'x-admin-sig: ${ADM['x-admin-sig']}'`;
const liste = async () => (await (await fetch(U + '/api/etat', { headers: { 'user-agent': UA, ...ADM } })).json());
function sonde(run) {
  log(sh(`curl -s -o /tmp/${run}.mp4 -D /tmp/${run}.h ${curlH} -w "HTTP %{http_code} %{size_download} octets\\n" "${U}/api/fichier?run=${run}"; grep -iE "content-(type|length|disposition)" /tmp/${run}.h`));
  log(sh(`ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,codec_tag_string,profile,width,height -of compact /tmp/${run}.mp4`));
  log('   Range 1000-1999 :', sh(`curl -s -o /dev/null -D - -r 1000-1999 ${curlH} "${U}/api/fichier?run=${run}&voir=1" | grep -iE "^HTTP|content-range|content-length"`).replace(/\r?\n/g, ' | '));
}
const lum = (c) => { const v = c.match(/[\d.]+/g).slice(0, 3).map((x) => { x = x / 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const contraste = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return ((x + 0.05) / (y + 0.05)).toFixed(2); };

(async () => {
  log('===== 1. ANONYME');
  for (const [n, p, o] of [
    ['etat', '/api/etat', {}],
    ['lancer youtu.be/abc', '/api/lancer', { method: 'POST', body: { url: 'youtu.be/abc', qualite: '360p' } }],
    ['suivi', '/api/suivi?run=x', {}],
    ['fichier', '/api/fichier?run=x', {}],
    ['essai (porte f)', '/api/essai', { method: 'POST', body: { acteur: 'apify~hello-world', entree: {} } }],
  ]) { const r = await req(p, o); log(`${n}: HTTP ${r.s} ${r.t}`); }

  log('\n===== 2. ADMIN SANS COUT');
  const E = await liste();
  log('version', E.version, 'connecte', E.connecte);
  const L = E.liste || [];
  log('historique (', L.length, 'entrées) :');
  for (const x of L) log(' ', JSON.stringify({ run: x.run, id: x.id, q: x.qualite, statut: x.statut, titre: x.titre, m: x.m }));
  log('titres = identifiant brut :', L.filter((x) => !x.titre || /^Vidéo [\w-]{11}$/.test(x.titre) || x.titre === x.id).length);
  log('entrées « essai » :', L.filter((x) => /essai|test/i.test(JSON.stringify(x))).length);
  log('entrées d\'un autre module :', L.filter((x) => x.m !== 'marielise.dev~youtube-video-downloader').length);
  for (const x of L.filter((x) => x.statut === 'prêt')) log(`  codec ${x.run} ${x.qualite} :`, sh(`curl -s -r 0-3000000 -o /tmp/p.mp4 ${curlH} "${U}/api/fichier?run=${x.run}"; ffprobe -v error -show_entries stream=codec_name,width,height -of compact /tmp/p.mp4 2>&1 | head -3`).replace(/\n/g, ' '));
  const re = await req('/api/essai', { method: 'POST', body: { acteur: 'apify~hello-world', entree: {} }, h: ADM }); log('essai en admin :', re.s, re.t);
  const re2 = await req('/api/essai', { h: ADM }); log('essai GET en admin :', re2.s, re2.t);
  for (const l of ['youtu.be/abc', 'https://example.com/watch?v=dQw4w9WgXcQ', 'pas un lien']) { const r = await req('/api/lancer', { method: 'POST', body: { url: l, qualite: '720p' }, h: ADM }); log(`lancer [${l}] : HTTP ${r.s} ${r.t}`); }
  log('entrées après liens invalides :', ((await liste()).liste || []).length, '(avant', L.length + ')');
  const pr = L.find((x) => x.statut === 'prêt');
  if (pr) log('Range sur', pr.run, ':', sh(`curl -s -o /dev/null -D - -r 1000-1999 ${curlH} "${U}/api/fichier?run=${pr.run}&voir=1" | grep -iE "^HTTP|content-range|content-length"`).replace(/\r?\n/g, ' | '));

  log('\n===== 3. INTERFACE iPhone (WebKit)');
  const wb = await webkit.launch();
  const ctx = async (sch, adm = true) => { const c = await wb.newContext({ ...devices['iPhone 13'], locale: 'fr-CH', colorScheme: sch }); if (adm) await c.setExtraHTTPHeaders(ADM); return c; };
  { const c = await ctx('light', false); const p = await c.newPage(); await p.goto(U); await p.waitForTimeout(2500);
    log('anonyme :', JSON.stringify(await p.evaluate(() => ({ cle: !document.getElementById('boxCle').hidden, conv: !document.getElementById('boxConv').hidden, liste: !document.getElementById('boxListe').hidden, label: document.getElementById('labelCle').textContent }))));
    await p.screenshot({ path: 'iphone_anonyme.png', fullPage: true }); await c.close(); }
  for (const sch of ['light', 'dark']) {
    const c = await ctx(sch); const p = await c.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
    await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])', { timeout: 15000 }).catch(() => log('boxConv invisible')); await p.waitForTimeout(2000);
    const m = await p.evaluate(() => {
      const g = (el) => getComputedStyle(el); const s = document.getElementById('qualite');
      const r = s.getBoundingClientRect();
      return { sw: document.documentElement.scrollWidth, iw: innerWidth, body: [g(document.body).color, g(document.body).backgroundColor], carte: g(document.querySelector('.carte')).backgroundColor, petit: g(document.querySelector('.petit')).color,
        select: { color: g(s).color, bg: g(s).backgroundColor, bgImage: g(s).backgroundImage.slice(0, 60), bgPos: g(s).backgroundPosition, padR: g(s).paddingRight, rect: [r.x, r.y, r.width, r.height] }, liste: document.getElementById('liste').innerText };
    });
    log(sch, JSON.stringify(m)); log(sch, 'contraste texte/fond', contraste(m.body[0], m.body[1]), 'petit/carte', contraste(m.petit, m.carte), 'select', contraste(m.select.color, m.select.bg)); log('erreurs JS', JSON.stringify(errs));
    log(sch, 'liste avec id brut :', /Vidéo [\w-]{11}\b/.test(m.liste), '| contient essai :', /essai/i.test(m.liste));
    await p.screenshot({ path: `iphone_${sch}.png`, fullPage: true });
    const [x, y, w, h] = m.select.rect; await p.screenshot({ path: `iphone_${sch}_menu.png`, clip: { x: x + w - 60, y, width: 60, height: h } });
    await c.close();
  }
  { // UI : lien invalide
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.fill('#url', 'youtu.be/abc'); await p.click('#btnGo'); await p.waitForTimeout(3000);
    log('UI youtu.be/abc :', JSON.stringify(await p.textContent('#msg')), 'bouton actif', await p.isEnabled('#btnGo'));
    await c.close(); }
  { // (c) le réseau ne répond plus pendant l'envoi
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.route('**/api/lancer', () => {}); // jamais de réponse
    await p.fill('#url', 'https://youtu.be/jNQXAC9IVRw'); await p.click('#btnGo');
    for (const t of [5, 20, 30, 40]) { await p.waitForTimeout(t === 5 ? 5000 : t === 20 ? 15000 : 10000); log(`envoi suspendu +${t}s :`, JSON.stringify(await p.textContent('#msg')), 'bouton actif', await p.isEnabled('#btnGo')); }
    await p.screenshot({ path: 'iphone_envoi_suspendu.png' }); await c.close(); }
  { // (c) le réseau ne répond plus pendant le suivi
    const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
    await p.route('**/api/lancer', (r) => r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ run: pr ? pr.run : 'x' }) }));
    let bloque = true; await p.route('**/api/suivi*', (r) => { if (!bloque) r.continue(); });
    await p.fill('#url', 'https://youtu.be/jNQXAC9IVRw'); await p.click('#btnGo');
    for (const t of [20, 35, 60]) { await p.waitForTimeout(t === 20 ? 20000 : t === 35 ? 15000 : 25000); log(`suivi suspendu +${t}s :`, JSON.stringify(await p.textContent('#msg')), 'bouton actif', await p.isEnabled('#btnGo')); }
    bloque = false; await p.waitForTimeout(12000);
    log('après retour réseau +12s :', JSON.stringify(await p.textContent('#msg')), 'liens', await p.$$eval('#res a', (a) => a.map((e) => e.textContent)));
    await c.close(); }

  if (process.env.CONV !== 'oui') { await wb.close(); return; }
  log('\n===== 4. UNE CONVERSION REELLE (19 s, 360p, lien sans https, par l\'interface)');
  const c = await ctx('light'); const p = await c.newPage(); await p.goto(U); await p.waitForSelector('#boxConv:not([hidden])');
  await p.fill('#url', 'youtube.com/watch?v=jNQXAC9IVRw'); await p.selectOption('#qualite', '360p'); await p.click('#btnGo');
  const t0 = Date.now();
  await p.waitForFunction(() => /Prêt|échou|introuvable|refuse|Crédit|trop de temps/.test(document.getElementById('msg').textContent), null, { timeout: 600000 }).catch(() => log('pas de fin en 10 min'));
  log(`fin après ${Math.round((Date.now() - t0) / 1000)} s :`, JSON.stringify(await p.textContent('#msg')), 'liens', await p.$$eval('#res a', (a) => a.map((e) => e.textContent)));
  await p.waitForTimeout(2000); log('liste :', await p.textContent('#liste'));
  await p.screenshot({ path: 'iphone_conversion.png', fullPage: true });
  const href = await p.$eval('#res a', (a) => a.getAttribute('href')).catch(() => null);
  await c.close();
  const run = href && decodeURIComponent((href.match(/run=([^&]+)/) || [])[1] || '');
  log('run', run); if (run) sonde(run);
  await wb.close();
})().catch((e) => log('ERREUR SCRIPT', e.stack));
