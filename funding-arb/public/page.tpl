<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="app" content="funding-arb-app">
<title>Arbitrage de prix — fantôme</title>
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
<header><h1>Arbitrage de prix<span class="badge">FANTÔME</span></h1>
<div class="mu">Aucun ordre réel. Version __VERSION__ · <span id="maj">…</span></div></header>
<main>
<div id="cartes" class="cartes"></div>
<h2>Plateformes</h2><div id="plat" class="mu"></div>
<h2>Positions ouvertes (fantôme, résultat provisoire si on sortait maintenant)</h2><div class="tab" id="ouv"></div>
<h2>Trades fermés (fantôme, résultat après tous les frais)</h2><div class="tab" id="fer"></div>
<h2>Plus gros écarts de prix maintenant</h2>
<div class="mu">Achat au meilleur prix vendeur, vente au meilleur prix acheteur, même actif sur deux plateformes. « Gain attendu » = gain net pour 10 000 $ par jambe si les prix se rejoignent, après frais d'entrée et de sortie et fourchettes achat/vente. « Vérifié carnet » = même calcul avec les vrais carnets d'ordres pour 10 000 $ (seulement pour les candidats).</div>
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
 document.getElementById("maj").textContent=d.t?"dernier scan "+hh(d.t):"pas encore de scan (chaque minute)";
 const t=d.total||{};
 document.getElementById("cartes").innerHTML=[
  ["Trades fermés",t.n||0],["Résultat net fermé",'<span class="'+cl(t.net)+'">'+usd(t.net||0)+"</span>"],
  ["Gagnants",t.n?Math.round(100*t.g/t.n)+"%":"—"],["Frais payés",usd(t.frais||0)],["Funding (pendant la tenue)",usd(t.fund||0)],
  ["Ouvertes",d.ouvertes.length],["Provisoire ouvertes",'<span class="'+cl(d.ouvertes.reduce((a,p)=>a+(p.net||0),0))+'">'+usd(d.ouvertes.reduce((a,p)=>a+(p.net||0),0))+"</span>"]
 ].map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 const s=d.scan?.statut||{};
 document.getElementById("plat").innerHTML=Object.entries(s).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" perps"+(v.lieu?" (lu depuis "+v.lieu+")":""):v.err)+"</div>").join("")||"—";
 const px=x=>x==null?"—":(x>=100?x.toFixed(2):x.toPrecision(5));
 document.getElementById("ouv").innerHTML=table(["Actif","Achat","Vente","Ouvert","Durée","Écart entrée","Gain attendu","Provisoire"],
  d.ouvertes.map(p=>[p.base,p.long+" "+px(p.px_l_in),p.short+" "+px(p.px_s_in),hh(p.ouvert),dur(now-p.ouvert),pc(p.spread_in,3),usd(p.cout_est),'<span class="'+cl(p.net)+'">'+usd(p.net)+"</span>"]));
 document.getElementById("fer").innerHTML=table(["Actif","Achat","Vente","Durée","Écart entrée","Prix","Funding","Frais","Net","Sortie"],
  d.fermees.map(p=>[p.base,p.long,p.short,dur(p.ferme-p.ouvert),pc(p.spread_in,3),usd(p.net-p.fund+p.frais),usd(p.fund),usd(p.frais),'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>",p.raison]));
 document.getElementById("top").innerHTML=table(["Actif","Achat (vendeur)","Vente (acheteur)","Écart","Gain attendu","Vérifié carnet"],
  (d.scan?.top||[]).map(p=>[p.base+(p.stock?'<span class="st">STOCK</span>':""),p.achat+" "+px(p.ask),p.vente+" "+px(p.bid),pc(p.ecart,3),'<span class="'+cl(p.gain)+'">'+usd(p.gain)+"</span>",p.verif==null?"—":(typeof p.verif==="number"?usd(p.verif):p.verif)]));
 const r=d.regles;
 document.getElementById("regles").innerHTML="Mise "+r.notional.toLocaleString("fr-CH")+" $ par jambe · scan chaque minute · entrée si le gain net attendu (prix moyens réels du carnet pour toute la mise, frais taker d'entrée et de sortie des 2 jambes, fourchettes achat/vente) ≥ "+r.gainMin+" $ · une position par actif · sortie dès que le résultat net réalisable atteint "+r.gainMin+" $, ou quand les prix se sont rejoints · écart > "+(r.ecartMaxPrix*100)+" % ignoré (contrats différents) · funding compté pendant la tenue. Frais utilisés : "+Object.entries(d.frais).map(([k,v])=>k+" "+(v*100).toFixed(3)+"%").join(", ")+" (paliers standard, estimés).";
}
go();setInterval(go,60e3);
</script></body></html>
