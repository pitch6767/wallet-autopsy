// casque — page de test de demande : désinfection de casques moto et ski (Chablais).
// Liste d'attente seulement : aucun paiement, aucun service vendu.
import { DurableObject } from "cloudflare:workers";
import QRLIB from "./qrlib.js";

const json = (o, st = 200) => Response.json(o, { status: st, headers: { "cache-control": "no-store" } });
const html = (s) => new Response(s, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
const nettoie = (s, n) => String(s || "").replace(/[<>"'`]/g, "").trim().slice(0, n);
const empreinte = async (c) =>
  [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode("casque-admin|" + String(c || ""))))]
    .map((x) => x.toString(16).padStart(2, "0")).join("");

export class Liste extends DurableObject {
  async fetch(req) {
    const u = new URL(req.url);
    const st = this.ctx.storage;

    if (u.pathname === "/api/inscrire" && req.method === "POST") {
      let b; try { b = await req.json(); } catch { return json({ ok: false, erreur: "demande illisible" }, 400); }
      if (b.piege) return json({ ok: true }); // champ caché : robots
      const email = nettoie(b.email, 120).toLowerCase();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json({ ok: false, erreur: "adresse e-mail invalide" }, 400);
      const types = ["moto", "ski", "vélo", "plusieurs"];
      const type = types.includes(b.type) ? b.type : "";
      const prix = ["5", "8", "10"].includes(String(b.prix)) ? String(b.prix) : "";
      const ou = nettoie(b.ou, 40) || "direct";
      const cle = "i:" + email;
      const deja = await st.get(cle);
      await st.put(cle, { email, type, prix, ou, quand: deja?.quand || new Date().toISOString() });
      return json({ ok: true, deja: !!deja });
    }

    if (u.pathname === "/api/visite" && req.method === "POST") {
      const ou = nettoie(u.searchParams.get("ou"), 40) || "direct";
      const k = "v:" + ou;
      await st.put(k, ((await st.get(k)) || 0) + 1);
      return json({ ok: true });
    }

    if (u.pathname === "/api/admin/code" && req.method === "POST") {
      let b; try { b = await req.json(); } catch { return json({ ok: false }, 400); }
      const h = await st.get("codeAdmin");
      if (h && (await empreinte(b.ancien)) !== h) return json({ ok: false, erreur: "ancien code faux" }, 401);
      if (String(b.nouveau || "").length < 6) return json({ ok: false, erreur: "6 caractères minimum" }, 400);
      await st.put("codeAdmin", await empreinte(b.nouveau));
      return json({ ok: true });
    }

    if (u.pathname === "/api/admin/liste") {
      const h = await st.get("codeAdmin");
      if (!h) return json({ ok: false, a_definir: true }, 401);
      if ((await empreinte(req.headers.get("x-code"))) !== h) return json({ ok: false, erreur: "code faux" }, 401);
      const inscrits = [...(await st.list({ prefix: "i:" })).values()].sort((a, b) => (a.quand < b.quand ? 1 : -1));
      const visites = Object.fromEntries([...(await st.list({ prefix: "v:" })).entries()].map(([k, v]) => [k.slice(2), v]));
      return json({ ok: true, inscrits, visites });
    }
    return json({ ok: false }, 404);
  }
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname.startsWith("/api/")) return env.LISTE.get(env.LISTE.idFromName("principal")).fetch(req);
    if (u.pathname === "/admin") return html(ADMIN);
    if (u.pathname === "/affiche") return html(AFFICHE);
    if (u.pathname === "/qr.js") return new Response(QRLIB, { headers: { "content-type": "text/javascript; charset=utf-8", "cache-control": "public, max-age=86400" } });
    if (u.pathname === "/" || u.pathname === "/index.html") return html(PAGE);
    return new Response("introuvable", { status: 404 });
  },
};

const STYLE = `
:root{--fond:#f6f4ef;--carte:#fff;--texte:#1d1f22;--doux:#5d636b;--accent:#0f6e6a;--bord:#dcd8cf}
@media (prefers-color-scheme:dark){:root{--fond:#121416;--carte:#1c1f22;--texte:#eceae5;--doux:#a3a9b0;--accent:#4fc1b9;--bord:#2e3236}}
*{box-sizing:border-box}body{margin:0;background:var(--fond);color:var(--texte);font:17px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:520px;margin:0 auto;padding:28px 16px 48px}
h1{font-size:1.75rem;line-height:1.2;margin:.2em 0 .4em}.doux{color:var(--doux)}
.carte{background:var(--carte);border:1px solid var(--bord);border-radius:14px;padding:18px;margin:18px 0}
label{display:block;font-weight:600;margin:14px 0 6px}
input[type=email],input[type=password]{width:100%;font:inherit;padding:12px;border:1px solid var(--bord);border-radius:10px;background:var(--fond);color:var(--texte)}
.choix{display:flex;gap:8px;flex-wrap:wrap}.choix label{font-weight:400;margin:0;border:1px solid var(--bord);border-radius:999px;padding:8px 14px;cursor:pointer}
.choix input{margin-right:6px}
button{width:100%;margin-top:18px;font:inherit;font-weight:700;padding:14px;border:0;border-radius:12px;background:var(--accent);color:#fff;cursor:pointer}
ul.points{padding-left:1.1em}ul.points li{margin:6px 0}
.ok{color:var(--accent);font-weight:700}.err{color:#c0392b}
table{width:100%;border-collapse:collapse;font-size:.9rem}td,th{border-bottom:1px solid var(--bord);padding:6px 4px;text-align:left}
`;

const PAGE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Casque propre — Chablais</title><style>${STYLE}</style></head><body><main>
<p class="doux">Bientôt dans le Chablais</p>
<h1>Ton casque moto, vélo ou ski désinfecté en 4 minutes</h1>
<p>Une machine à ozone en libre-service : elle tue bactéries, champignons et mauvaises odeurs à l'intérieur du casque. Sans eau, sans produit, sans démonter la mousse.</p>
<ul class="points"><li>4 minutes par casque</li><li>Moto et vélo l'été, ski l'hiver</li><li>Prix prévu : environ 5 CHF</li></ul>
<div class="carte" id="zone">
<form id="f">
<label for="email">Ton e-mail — on te prévient à l'ouverture</label>
<input id="email" type="email" required autocomplete="email" placeholder="nom@exemple.ch">
<label>Pour quel casque ?</label>
<div class="choix"><label><input type="radio" name="type" value="moto">Moto</label><label><input type="radio" name="type" value="ski">Ski</label><label><input type="radio" name="type" value="vélo">Vélo</label><label><input type="radio" name="type" value="plusieurs">Plusieurs</label></div>
<label>Tu paierais combien par passage ?</label>
<div class="choix"><label><input type="radio" name="prix" value="5">5 CHF</label><label><input type="radio" name="prix" value="8">8 CHF</label><label><input type="radio" name="prix" value="10">10 CHF</label></div>
<input name="piege" id="piege" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px">
<button type="submit">Me prévenir</button><p id="msg"></p>
</form></div>
<p class="doux" style="font-size:.85rem">Service en préparation : rien n'est vendu aujourd'hui. Ton e-mail sert uniquement à te prévenir de l'ouverture, n'est jamais transmis, et est effacé sur simple demande.</p>
</main><script>
const ou=new URLSearchParams(location.search).get('ou')||'direct';
fetch('/api/visite?ou='+encodeURIComponent(ou),{method:'POST'}).catch(()=>{});
document.getElementById('f').onsubmit=async e=>{e.preventDefault();const m=document.getElementById('msg');m.className='';m.textContent='Envoi…';
const v=n=>(document.querySelector('input[name='+n+']:checked')||{}).value||'';
try{const r=await fetch('/api/inscrire',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,type:v('type'),prix:v('prix'),ou,piege:document.getElementById('piege').value})});const j=await r.json();
if(j.ok){document.getElementById('zone').innerHTML='<p class="ok">Merci ! Tu seras prévenu à l\\'ouverture.</p>'}else{m.className='err';m.textContent=j.erreur||'Erreur'}}catch{m.className='err';m.textContent='Pas de connexion, réessaie.'}};
</script></body></html>`;

const ADMIN = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Casque — inscrits</title><style>${STYLE}</style></head><body><main>
<h1>Inscrits</h1><div id="out" class="doux">Chargement…</div>
</main><script>
let code='';try{code=sessionStorage.getItem('c')||''}catch{}
async function charger(){const r=await fetch('/api/admin/liste',{headers:{'x-code':code}});const j=await r.json();const o=document.getElementById('out');
if(j.a_definir){const n=prompt('Choisis ton code admin (6 caractères minimum) :');if(!n)return;if(prompt('Retape le code :')!==n){alert('Les deux codes diffèrent');return}
const d=await(await fetch('/api/admin/code',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({nouveau:n})})).json();if(!d.ok){alert(d.erreur);return}code=n;try{sessionStorage.setItem('c',code)}catch{};return charger()}
if(!j.ok){code=prompt('Code admin :')||'';try{sessionStorage.setItem('c',code)}catch{};if(code)return charger();return}
const vis=Object.entries(j.visites).map(([k,v])=>'<tr><td>'+k+'</td><td>'+v+'</td><td>'+j.inscrits.filter(i=>i.ou===k).length+'</td></tr>').join('');
const cpt=(f,v)=>j.inscrits.filter(i=>i[f]===v).length;
o.className='';o.innerHTML='<div class="carte"><b>'+j.inscrits.length+' inscrits</b><br>Moto '+cpt('type','moto')+' · Vélo '+cpt('type','vélo')+' · Ski '+cpt('type','ski')+' · Plusieurs '+cpt('type','plusieurs')+'<br>5 CHF '+cpt('prix','5')+' · 8 CHF '+cpt('prix','8')+' · 10 CHF '+cpt('prix','10')+'</div>'+
'<div class="carte"><b>Par lieu (affiche)</b><table><tr><th>Lieu</th><th>Visites</th><th>Inscrits</th></tr>'+vis+'</table></div>'+
'<div class="carte"><table><tr><th>Date</th><th>E-mail</th><th>Type</th><th>Prix</th><th>Lieu</th></tr>'+j.inscrits.map(i=>'<tr><td>'+i.quand.slice(0,10)+'</td><td>'+i.email+'</td><td>'+i.type+'</td><td>'+i.prix+'</td><td>'+i.ou+'</td></tr>').join('')+'</table></div>'}
charger();
</script></body></html>`;

const AFFICHE = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Affiche casque</title>
<script src="/qr.js"></script>
<style>body{margin:0;background:#fff;color:#111;font-family:system-ui,-apple-system,sans-serif}
.a4{max-width:190mm;margin:0 auto;padding:16mm 10mm;text-align:center}
h1{font-size:46px;line-height:1.1;margin:0 0 14px}p{font-size:22px;margin:8px 0}.gros{font-size:30px;font-weight:800}
#qr svg{width:70mm;height:70mm}.reglage{padding:12px;background:#eee;font-size:15px}@media print{.reglage{display:none}}</style></head><body>
<div class="reglage">Lieu de cette affiche : <input id="lieu" placeholder="ex. moto-shop-monthey"> <button onclick="maj()">Mettre à jour</button> puis Partager → Imprimer</div>
<div class="a4"><h1>Ton casque désinfecté<br>en 4 minutes</h1>
<p class="gros">Moto · Vélo · Ski</p><p>Machine à ozone en libre-service, bientôt dans le Chablais.<br>Sans eau, sans produit, environ 5 CHF.</p>
<div id="qr"></div><p><b>Scanne pour être prévenu à l'ouverture</b></p><p style="font-size:16px">casque.pitch67.workers.dev</p></div>
<script>function maj(){const l=(document.getElementById('lieu').value||new URLSearchParams(location.search).get('ou')||'affiche').trim().toLowerCase().replace(/[^a-z0-9-]+/g,'-');
document.getElementById('lieu').value=l;const q=qrcode(0,'M');q.addData('https://casque.pitch67.workers.dev/?ou='+l);q.make();document.getElementById('qr').innerHTML=q.createSvgTag({scalable:true,margin:2})}maj();</script>
</body></html>`;
