<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="app" content="funding-arb-app">
<title>Arbitrage au comptant — fantôme</title>
<link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="theme-color" content="#12161f">
<style>
body{margin:0;background:#12161f;color:#e5e7eb;font:14px -apple-system,system-ui,sans-serif}
header{position:sticky;top:0;background:#0b0e14;padding:10px 12px;padding-top:max(10px,env(safe-area-inset-top));border-bottom:1px solid #263041;z-index:2}
h1{font-size:17px;margin:0}.badge{background:#7c3aed;color:#fff;border-radius:6px;padding:1px 6px;font-size:11px;margin-left:6px}
.mu{color:#94a3b8;font-size:12px}main{padding:10px 12px 40px}h2{font-size:15px;margin:18px 0 6px}
.cartes{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}
.c{background:#1b2230;border-radius:10px;padding:10px}.c b{display:block;font-size:18px;margin-top:2px}
.tab{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:12.5px}th,td{padding:6px 5px;border-bottom:1px solid #263041;text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}th{color:#94a3b8;font-weight:600}
.v{color:#4ade80}.r{color:#f87171}.o{color:#fbbf24}.ok{color:#4ade80}.ko{color:#f87171}
.st{background:#4b2b0b;color:#fbbf24;font-size:10px;border-radius:4px;padding:0 4px;margin-left:4px}
</style></head><body>
<header><div style="display:flex;align-items:center;gap:10px"><a href="/" style="color:#e5e7eb;font-size:22px;text-decoration:none" aria-label="Accueil">←</a>
<h1>Arbitrage au comptant<span class="badge">FANTÔME</span></h1></div>
<div class="mu">Aucun ordre réel. Version __VERSION__ · <span id="maj">…</span></div></header>
<main>
<div class="mu">Pièces et dollars supposés déjà déposés sur chaque plateforme : on achète là où c'est le moins cher et on vend là où c'est le plus cher dans la même seconde. Le gain est acquis tout de suite, il n'y a pas de position à fermer.</div>
<div id="cartes" class="cartes" style="margin-top:10px"></div>
<h2>Plateformes</h2><div id="plat" class="mu"></div>
<h2>Trades (fantôme, gain net après frais)</h2><div class="tab" id="tr"></div>
<h2>À rééquilibrer en réel (pièces et dollars déplacés)</h2><div class="mu">En réel, chaque trade vide un peu une plateforme et en remplit une autre : il faudra virer de temps en temps, avec des frais de retrait non comptés ici.</div><div class="tab" id="mv"></div>
<h2>Plus gros écarts maintenant</h2><div class="mu">« Gain attendu » au meilleur prix affiché, après frais. « Vérifié carnet » = gain réel pour 10 000 $ avec les vrais carnets d'ordres. Coinbase : dernier prix seulement (~), le carnet tranche.</div><div class="tab" id="top"></div>
<h2>Règles</h2><div id="regles" class="mu"></div>
</main>
<script>
const V="__VERSION__";
const pc=(x,d=3)=>x==null?"—":(x*100).toFixed(d)+"%";
const usd=x=>x==null?"—":(x<0?"-":"")+"$"+Math.abs(x).toFixed(2);
const cl=x=>x>0?"v":x<0?"r":"";
const hh=t=>new Date(t).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"});
const px=x=>x==null?"—":(x>=100?x.toFixed(2):x.toPrecision(5));
function table(cols,rows){return rows.length?"<table><tr>"+cols.map(c=>"<th>"+c+"</th>").join("")+"</tr>"+rows.map(r=>"<tr>"+r.map(c=>"<td>"+c+"</td>").join("")+"</tr>").join("")+"</table>":'<div class="mu">Aucun pour l\'instant.</div>'}
async function go(){
 const d=await (await fetch("/api/comptant",{cache:"no-store"})).json();
 document.getElementById("maj").textContent=d.t?"dernier scan "+hh(d.t):"pas encore de scan (toutes les 10 s)";
 const t=d.total||{};
 document.getElementById("cartes").innerHTML=[["Trades",t.n||0],["Gain net",'<span class="'+cl(t.net)+'">'+usd(t.net||0)+"</span>"],["Frais payés",usd(t.frais||0)],["Depuis",t.debut?hh(t.debut):"—"]]
  .map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 const s=d.scan?.statut||{};
 document.getElementById("plat").innerHTML=Object.entries(s).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" marchés":v.err)+"</div>").join("")||"—";
 document.getElementById("tr").innerHTML=table(["Heure","Actif","Achat","Vente","Quantité","Frais","Net"],
  d.trades.map(p=>[hh(p.t),p.base+"/"+p.quote,p.achat_ex+" "+px(p.px_achat),p.vente_ex+" "+px(p.px_vente),px(p.qte),usd(p.frais),'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>"]));
 const m={};for(const r of d.mouvements){const k=r.ex+"|"+r.base+"/"+r.quote;m[k]=m[k]||{ex:r.ex,a:r.base+"/"+r.quote,q:0,d:0};m[k].q+=r.q;m[k].d-=r.d;}
 document.getElementById("mv").innerHTML=table(["Plateforme","Actif","Pièces","Dollars"],Object.values(m).filter(x=>Math.abs(x.q)>1e-12).map(x=>[x.ex,x.a,(x.q>0?"+":"")+px(x.q),usd(x.d)]));
 document.getElementById("top").innerHTML=table(["Actif","Achat (vendeur)","Vente (acheteur)","Écart","Gain attendu","Vérifié carnet"],
  (d.scan?.top||[]).map(p=>[p.cle,p.achat+" "+px(p.ask),p.vente+" "+px(p.bid),pc(p.ecart)+(p.approx?" ~":""),'<span class="'+cl(p.gain)+'">'+usd(p.gain)+"</span>",p.verif==null?"—":(typeof p.verif==="number"?usd(p.verif):p.verif)]));
 const r=d.regles;
 document.getElementById("regles").innerHTML="Mise "+r.mise.toLocaleString("fr-CH")+" $ par trade · scan toutes les 10 s · trade si le gain net (prix moyens réels des carnets pour toute la quantité, frais d'achat et de vente) ≥ "+r.gainMin+" $ · même jeton et même monnaie (USDT ou USDC) · au moins "+(r.volumeMin/1e6)+" M$ échangés sur 24 h sur les 2 plateformes · écart > "+(r.ecartMaxPrix*100)+" % ignoré (jeton probablement différent) · un même actif au plus une fois par "+r.pauseMemeActifS+" s. Frais preneur (palier de base, estimés, prudents) : "+Object.entries(d.frais).map(([k,v])=>k+" "+(v*100).toFixed(2)+"%").join(", ")+".";
}
go();setInterval(go,10e3);
</script></body></html>
