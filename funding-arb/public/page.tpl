<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="app" content="funding-arb-app">
<title>Funding Arb — fantôme</title>
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
<header><h1>Funding Arb<span class="badge">FANTÔME</span></h1>
<div class="mu">Aucun ordre réel. Version __VERSION__ · <span id="maj">…</span></div></header>
<main>
<div id="cartes" class="cartes"></div>
<h2>Plateformes</h2><div id="plat" class="mu"></div>
<h2>Positions ouvertes (fantôme, résultat provisoire)</h2><div class="tab" id="ouv"></div>
<h2>Trades fermés (fantôme, résultat après frais)</h2><div class="tab" id="fer"></div>
<h2>Meilleurs écarts maintenant</h2>
<div class="mu">Short sur la plateforme au funding le plus haut, long sur la plus basse. Taux ramenés à l'heure pour comparer 1 h / 4 h / 8 h. « Amorti en » = heures de funding nécessaires pour payer le coût aller-retour.</div>
<div class="tab" id="top"></div>
<h2>Règles du fantôme</h2><div id="regles" class="mu"></div>
</main>
<script>
const V="__VERSION__";
try{if(sessionStorage.getItem("v")!==V){fetch("/api/version",{cache:"no-store"}).then(r=>r.json()).then(d=>{if(d.version!==V&&!sessionStorage.getItem("r"+d.version)){sessionStorage.setItem("r"+d.version,1);location.reload()}else sessionStorage.setItem("v",V)})}}catch(e){}
const pc=(x,d=4)=>x==null?"—":(x*100).toFixed(d)+"%";
const usd=x=>x==null?"—":(x<0?"-":"")+"$"+Math.abs(x).toFixed(2);
const cl=x=>x>0?"v":x<0?"r":"";
const dur=ms=>{if(ms==null)return"—";const m=Math.round(ms/60e3);return m<60?m+" min":m<1440?(m/60).toFixed(1)+" h":(m/1440).toFixed(1)+" j"};
const hh=t=>new Date(t).toLocaleString("fr-CH",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"});
const FR={binance:.0005,bybit:.00055,okx:.0005,hyperliquid:.00045,deribit:.0005};
function table(cols,rows){return rows.length?"<table><tr>"+cols.map(c=>"<th>"+c+"</th>").join("")+"</tr>"+rows.map(r=>"<tr>"+r.map(c=>"<td>"+c+"</td>").join("")+"</tr>").join("")+"</table>":'<div class="mu">Aucun pour l\'instant.</div>'}
async function go(){
 const d=await (await fetch("/api/etat",{cache:"no-store"})).json();
 const now=Date.now();
 document.getElementById("maj").textContent=d.t?"dernier scan "+hh(d.t):"pas encore de scan (toutes les 5 min)";
 const t=d.total||{};
 const ouvPnl=d.ouvertes.map(p=>{const s=p.notional/p.px_s_in*(p.px_s_in-p.last_s_ask),l=p.notional/p.px_l_in*(p.last_l_bid-p.px_l_in);return p.fund+s+l-p.frais-p.notional*(FR[p.short]+FR[p.long])});
 document.getElementById("cartes").innerHTML=[
  ["Trades fermés",t.n||0],["Résultat net fermé",'<span class="'+cl(t.net)+'">'+usd(t.net||0)+"</span>"],
  ["Gagnants",t.n?Math.round(100*t.g/t.n)+"%":"—"],["Funding encaissé",usd(t.fund||0)],["Frais payés",usd(t.frais||0)],
  ["Ouvertes",d.ouvertes.length],["Provisoire ouvertes",'<span class="'+cl(ouvPnl.reduce((a,b)=>a+b,0))+'">'+usd(ouvPnl.reduce((a,b)=>a+b,0))+"</span>"]
 ].map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 const s=d.scan?.statut||{};
 document.getElementById("plat").innerHTML=Object.entries(s).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" perps"+(v.lieu?" (lu depuis "+v.lieu+")":""):v.err)+"</div>").join("")||"—";
 document.getElementById("ouv").innerHTML=table(["Actif","Short","Long","Ouvert","Durée","Écart/h entrée","Funding","Frais","Provisoire"],
  d.ouvertes.map((p,i)=>[p.base,p.short,p.long,hh(p.ouvert),dur(now-p.ouvert),pc(p.spread_in),usd(p.fund),usd(p.frais),'<span class="'+cl(ouvPnl[i])+'">'+usd(ouvPnl[i])+"</span>"]));
 document.getElementById("fer").innerHTML=table(["Actif","Short","Long","Durée","Funding","Prix","Frais","Net","Sortie"],
  d.fermees.map(p=>{const px=p.fund-p.frais;return[p.base,p.short,p.long,dur(p.ferme-p.ouvert),usd(p.fund),usd(p.net-p.fund+p.frais),usd(p.frais),'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>",p.raison]}));
 document.getElementById("top").innerHTML=table(["Actif","Short","Long","Écart/h","Annualisé","Coût A/R","Amorti en","Dure depuis"],
  (d.scan?.top||[]).map(p=>[p.base+(p.stock?'<span class="st">STOCK</span>':""),p.short+" "+pc(p.rs)+"/"+p.is+"h",p.long+" "+pc(p.rl)+"/"+p.il+"h",pc(p.sh),pc(p.sh*24*365,0),pc(p.cout,3),p.cout&&p.sh>0?(p.cout/p.sh).toFixed(1)+" h":"—",p.depuis?dur(now-p.depuis):"—"]));
 const r=d.regles;
 document.getElementById("regles").innerHTML="Mise "+r.notional+" $ par jambe · entrée si l'écart (même paire de plateformes) dure ≥ "+r.persistanceMin+" min ET si le funding attendu sur "+r.horizonH+" h ≥ "+r.multipleCout+"× le coût aller-retour estimé (frais taker des 2 jambes, entrée + sortie, + fourchette achat/vente) · une position par actif · sortie dès que l'écart de la paire passe ≤ 0 · entrée au prix vendeur/acheteur réel du moment, sortie idem. Frais taker utilisés : "+Object.entries(d.frais).map(([k,v])=>k+" "+(v*100).toFixed(3)+"%").join(", ")+" (paliers standard, estimés).";
}
go();setInterval(go,60e3);
</script></body></html>
