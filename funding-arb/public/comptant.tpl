<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="app" content="funding-arb-app">
<title>Arbitrage — fantôme</title>
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
<header><div style="display:flex;align-items:center;gap:10px"><h1>Arbitrage<span class="badge">FANTÔME</span></h1></div>
<div class="mu">Aucun ordre réel. Version __VERSION__ · <span id="maj">…</span></div></header>
<main>
<div class="mu">Pièces et dollars supposés déjà déposés sur chaque plateforme (5 000 $ de chaque côté : achat sur une plateforme, vente sur l'autre).</div>
<h2>Stratégie 1 — achat et vente dans la même seconde</h2>
<div class="mu">Achat là où c'est le moins cher, vente là où c'est le plus cher, au même moment : gain acquis tout de suite.</div>
<div id="cartes" class="cartes" style="margin-top:8px"></div>
<h2>Stratégie 2 — achat/vente puis clôture quand l'écart s'inverse</h2>
<div class="mu">Achat sur A et vente sur B dès que l'écart paie les frais d'entrée ; clôture (vente sur A, achat sur B) quand l'écart s'est inversé et rapporte au moins 5 $ (variante 5) ou 10 $ (variante 10) après frais.</div>
<div id="cartes2" class="cartes" style="margin-top:8px"></div>
<div class="tab" id="pos2" style="margin-top:8px"></div>
<div class="mu" id="avant" style="margin-top:8px"></div>
<h2>Comptes réels</h2><div id="comptes" class="mu">…</div>
<h2>Emprunt (vente à découvert)</h2><div id="emp" class="mu"></div>
<h2>Plateformes</h2><div id="plat" class="mu"></div>
<h2>Stratégie 1 — trades (fantôme, gain net après frais)</h2><div class="tab" id="tr"></div>
<h2>À rééquilibrer en réel (pièces et dollars déplacés)</h2><div class="mu">En réel, chaque trade vide un peu une plateforme et en remplit une autre : il faudra virer de temps en temps, avec des frais de retrait non comptés ici.</div><div class="tab" id="mv"></div>
<h2>Plus gros écarts maintenant</h2><div class="mu">« Gain attendu » au meilleur prix affiché, après frais. « Vérifié carnet » = gain réel pour 5 000 $ de chaque côté avec les vrais carnets d'ordres. Coinbase : dernier prix seulement (~), le carnet tranche.</div><div class="tab" id="top"></div>
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
 const a=d.attente||{},n=d.annules||{};
 document.getElementById("cartes").innerHTML=[["Trades validés",t.n||0],["Gain net validé",'<span class="'+cl(t.net)+'">'+usd(t.net||0)+"</span>"],["Intérêts d'emprunt payés",usd(t.interet||0)],["En attente (écart > 1 %, 5 min)",(a.n||0)+" · "+usd(a.net||0)],["Annulés (écart permanent)",(n.n||0)+" · "+usd(n.net||0)],["Depuis",t.debut?hh(t.debut):"—"]]
  .map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 const dur=ms=>{if(!ms)return"—";const m=Math.round(ms/60e3);return m<60?m+" min":m<1440?(m/60).toFixed(1)+" h":(m/1440).toFixed(1)+" j"};
 const c2=[];for(const v of d.regles.sorties){const f=(d.total2||[]).find(x=>x.variante==v)||{},o=(d.ouvertes2||[]).find(x=>x.variante==v)||{};
  c2.push(["Clôture ≥ "+v+" $ dans le sens contraire — fermés",(f.n||0)+" · "+'<span class="'+cl(f.net)+'">'+usd(f.net||0)+"</span> · durée moy. "+dur(f.duree)],["Clôture ≥ "+v+" $ dans le sens contraire — ouvertes",(o.n||0)]);}
 const av=d.avant||{};document.getElementById("avant").textContent="Avant l'emprunt obligatoire (règles précédentes, non comptés ici) : stratégie 1 "+(av.n1||0)+" trades · "+usd(av.net1||0)+" ; stratégie 2 "+(av.n2||0)+" fermées · "+usd(av.net2||0)+".";
 const es=d.empruntStatut||{};document.getElementById("emp").innerHTML=Object.entries(es).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" cryptos empruntables"+(v.sansPlafond?" · "+v.sansPlafond+" sans plafond publié (quantité non vérifiée)":"")+(v.sansTaux?" · "+v.sansTaux+" sans taux publié (taux estimé)":"")+(v.tauxMax?" · taux = plafond du marché de prêt (prudent, le vrai taux est plus bas)":""):v.err)+"</div>").join("")||"—";
 document.getElementById("cartes2").innerHTML=c2.map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 document.getElementById("pos2").innerHTML=table(["Clôture","Actif","Achat","Vente","Ouvert","Statut","Entrée","Intérêts","Net","Règles"],
  (d.positions||[]).map(p=>["≥ "+p.variante+" $ sens contraire",p.cle,p.achat_ex+" "+px(p.px_achat),p.vente_ex+" "+px(p.px_vente),hh(p.ouvert),p.statut+(p.ferme?" ("+dur(p.ferme-p.ouvert)+")":""),usd(p.entree),usd(p.interet||0),p.net==null?"—":'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>",p.regles==d.reglesId?"emprunt":"avant"]));
 const s=d.scan?.statut||{};
 document.getElementById("plat").innerHTML=Object.entries(s).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" marchés":v.err)+"</div>").join("")||"—";
 document.getElementById("tr").innerHTML=table(["Heure","Actif","Achat","Vente","Quantité","Frais","Intérêts","Net","Statut","Règles"],
  d.trades.map(p=>[hh(p.t),p.base+"/"+p.quote,p.achat_ex+" "+px(p.px_achat),p.vente_ex+" "+px(p.px_vente),px(p.qte),usd(p.frais),usd(p.interet||0),'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>",p.statut||"validé",p.regles==d.reglesId?"emprunt":"avant"]));
 const m={};for(const r of d.mouvements){const k=r.ex+"|"+r.base+"/"+r.quote;m[k]=m[k]||{ex:r.ex,a:r.base+"/"+r.quote,q:0,d:0};m[k].q+=r.q;m[k].d-=r.d;}
 document.getElementById("mv").innerHTML=table(["Plateforme","Actif","Pièces","Dollars"],Object.values(m).filter(x=>Math.abs(x.q)>1e-12).map(x=>[x.ex,x.a,(x.q>0?"+":"")+px(x.q),usd(x.d)]));
 document.getElementById("top").innerHTML=table(["Actif","Achat (vendeur)","Vente (acheteur)","Écart","Gain attendu","Vérifié carnet"],
  (d.scan?.top||[]).map(p=>[p.cle,p.achat+" "+px(p.ask),p.vente+" "+px(p.bid),pc(p.ecart)+(p.approx?" ~":""),'<span class="'+cl(p.gain)+'">'+usd(p.gain)+"</span>",p.permanent?"écart permanent → ignoré":(p.verif==null?"—":(typeof p.verif==="number"?usd(p.verif):p.verif))]));
 const r=d.regles;
 document.getElementById("regles").innerHTML="Mise "+r.mise.toLocaleString("fr-CH")+" $ de chaque côté · scan toutes les 10 s · prix moyens réels des carnets pour toute la quantité · même jeton et même monnaie (USDT ou USDC) · au moins "+(r.volumeMin/1e6)+" M$ échangés sur 24 h sur les 2 plateformes · écart > "+(r.ecartMaxPrix*100)+" % ignoré (jeton probablement différent) · un écart > "+(r.ecartSuspect*100)+" % qui dure plus de "+(r.dureeSuspectS/60)+" min est considéré comme faux (jeton différent ou retraits bloqués) : ses trades sont annulés · vente à découvert : la crypto vendue est empruntée sur la plateforme de vente, trade seulement si elle y est empruntable pour toute la quantité ; intérêts d'emprunt déduits (stratégie 1 : "+r.heuresEmpruntS1+" h, le temps de virer les pièces achetées pour rendre l'emprunt ; stratégie 2 : toute la durée de tenue), au taux publié par la plateforme, sinon "+(d.tauxDefautH*100).toFixed(3)+" % par heure (estimé, prudent) · stratégie 1 : gain net ≥ "+r.gainMin+" $, un même actif au plus une fois par "+r.pauseMemeActifS+" s · stratégie 2 : entrée si l'écart couvre les frais d'entrée, une position par actif et par variante, clôture quand l'écart dans le sens contraire rapporte ≥ 5 $ ou ≥ 10 $ après frais et intérêts. Frais preneur (palier de base, estimés, prudents) : "+Object.entries(d.frais).map(([k,v])=>k+" "+(v*100).toFixed(2)+"%").join(", ")+".";
}
async function comptes(){try{const d=await (await fetch("/api/comptes",{cache:"no-store"})).json();
 document.getElementById("comptes").innerHTML="<div><b>Mode réel : désactivé</b> — aucun ordre n'est envoyé.</div>"+Object.entries(d.comptes).map(([k,v])=>"<div>"+k+" — "+(!v.cles?"clé API pas encore fournie":v.ok?'<span class="ok">clé OK</span> · '+usd(v.usdt)+" USDT disponibles":'<span class="ko">clé refusée</span> : '+v.err)+"</div>").join("");}catch(e){}}
go();comptes();setInterval(go,10e3);setInterval(comptes,60e3);
</script></body></html>
