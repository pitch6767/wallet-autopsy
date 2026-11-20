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
<h2>Achat/vente puis clôture quand l'écart s'inverse</h2>
<div class="mu">Achat sur A et vente à découvert sur B dès que le gain à l'entrée atteint 25 $ après frais ; clôture (vente sur A, achat sur B) quand l'écart s'est inversé et rapporte au moins 5 $ (variante 5) ou 10 $ (variante 10) après frais.</div>
<div id="cartes2" class="cartes" style="margin-top:8px"></div>
<div class="tab" id="pos2" style="margin-top:8px"></div>
<div class="mu" id="avant" style="margin-top:8px"></div>
<h2>Comptes réels</h2><div id="comptes" class="mu">…</div>
<h2>Emprunt (vente à découvert)</h2><div id="emp" class="mu"></div>
<h2>Plateformes</h2><div id="plat" class="mu"></div>
<h2>Plus gros écarts maintenant</h2><div class="mu">« Gain attendu » au meilleur prix affiché, après frais.</div><div class="tab" id="top"></div>
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
 const dur=ms=>{if(!ms)return"—";const m=Math.round(ms/60e3);return m<60?m+" min":m<1440?(m/60).toFixed(1)+" h":(m/1440).toFixed(1)+" j"};
 const c2=[];for(const v of d.regles.sorties){const f=(d.total2||[]).find(x=>x.variante==v)||{},o=(d.ouvertes2||[]).find(x=>x.variante==v)||{};
  c2.push(["Clôture ≥ "+v+" $ dans le sens contraire — fermés",(f.n||0)+" · "+'<span class="'+cl(f.net)+'">'+usd(f.net||0)+"</span> · durée moy. "+dur(f.duree)],["Clôture ≥ "+v+" $ dans le sens contraire — ouvertes",(o.n||0)]);}
 const av=d.avant||{};document.getElementById("avant").textContent="Avant l'emprunt obligatoire (règles précédentes, non comptés ici) : "+(av.n2||0)+" fermées · "+usd(av.net2||0)+".";
 const es=d.empruntStatut||{};document.getElementById("emp").innerHTML=Object.entries(es).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" cryptos empruntables"+(v.sansPlafond?" · "+v.sansPlafond+" sans plafond publié (quantité non vérifiée)":"")+(v.sansTaux?" · "+v.sansTaux+" sans taux publié (taux estimé)":"")+(v.tauxMax?" · taux = plafond du marché de prêt (prudent, le vrai taux est plus bas)":""):v.err)+"</div>").join("")||"—";
 document.getElementById("cartes2").innerHTML=c2.map(([a,b])=>'<div class="c"><span class="mu">'+a+"</span><b>"+b+"</b></div>").join("");
 const pos=d.positions||[], o2=pos.filter(p=>p.statut==="ouvert"), f2=pos.filter(p=>p.statut!=="ouvert");
 const ligne=(a,b)=>'<div style="display:flex;justify-content:space-between;gap:8px;padding:2px 0"><span class="mu">'+a+'</span><span>'+b+'</span></div>';
 const carte=p=>{const enCours=p.statut==="ouvert";const maint=enCours&&p.sortie_now!=null?p.entree+p.sortie_now:null;
  return '<div class="c" style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;font-weight:600;font-size:16px"><span>'+p.cle+'</span><span class="mu" style="font-weight:400">clôture ≥ '+p.variante+' $</span></div>'
  +ligne("Achat",p.achat_ex+" à "+px(p.px_achat))+ligne("Vente à découvert",p.vente_ex+(p.vente_ex==="aster"?" (perpétuel, DEX)":"")+" à "+px(p.px_vente))+ligne("Gain à l'entrée",'<span class="'+cl(p.entree)+'">'+usd(p.entree)+"</span>")
  +ligne(p.vente_ex==="aster"?"Funding (reçu + / payé −)":"Intérêts d'emprunt",usd(-(p.interet||0)))+ligne(enCours?"Ouverte depuis":"Durée",dur((enCours?Date.now():p.ferme)-p.ouvert))
  +(enCours?ligne("Frais de sortie (2 côtés)",p.frais_sortie_now==null?"—":usd(-p.frais_sortie_now))+ligne("Net après clôture maintenant",maint==null?"—":'<b class="'+cl(maint)+'">'+usd(maint)+"</b>")
     +'<button onclick="fermer('+p.id+','+(maint==null?"null":maint.toFixed(2))+')" style="margin-top:8px;width:100%;padding:10px;border:0;border-radius:8px;background:#7c3aed;color:#fff;font-size:15px;font-weight:600">Clôturer maintenant</button>'
     :(p.raison==="manuelle"?ligne("Clôture","manuelle"):"")+ligne(p.statut==="fermé"?"Résultat net":"Statut",p.statut==="fermé"?'<b class="'+cl(p.net)+'">'+usd(p.net)+"</b>":p.statut))+"</div>";};
 document.getElementById("pos2").innerHTML=(o2.length?'<div class="mu" style="margin:6px 0">Positions ouvertes</div>'+o2.map(carte).join(""):'<div class="mu">Aucune position ouverte.</div>')
  +(f2.length?'<div class="mu" style="margin:10px 0 6px">Positions fermées</div>'+f2.slice(0,30).map(carte).join(""):"");
 const s=d.scan?.statut||{};
 document.getElementById("plat").innerHTML=Object.entries(s).map(([k,v])=>'<div><span class="'+(v.ok?"ok":"ko")+'">'+(v.ok?"●":"✕")+"</span> "+k+" — "+(v.ok?v.n+" marchés":v.err)+"</div>").join("")||"—";
 document.getElementById("top").innerHTML=table(["Actif","Achat (vendeur)","Vente (acheteur)","Écart","Gain attendu","Note"],
  (d.scan?.top||[]).map(p=>[p.cle,p.achat+" "+px(p.ask),p.vente+" "+px(p.bid),pc(p.ecart)+(p.approx?" ~":""),'<span class="'+cl(p.gain)+'">'+usd(p.gain)+"</span>",p.permanent?"écart permanent → ignoré":"—"]));
 const r=d.regles;
 document.getElementById("regles").innerHTML="Mise "+r.mise.toLocaleString("fr-CH")+" $ de chaque côté · scan toutes les 10 s · prix moyens réels des carnets pour toute la quantité · même jeton et même monnaie (USDT ou USDC) · au moins "+(r.volumeMin/1e6)+" M$ échangés sur 24 h sur les 2 plateformes · écart > "+(r.ecartMaxPrix*100)+" % ignoré (jeton probablement différent) · un écart > "+(r.ecartSuspect*100)+" % qui dure plus de "+(r.dureeSuspectS/60)+" min est considéré comme faux (jeton différent ou retraits bloqués) et ignoré ; pas d'entrée tant que l'écart dépasse 1 % ; une position prise n'est jamais annulée, elle va jusqu'à sa clôture · vente à découvert : la crypto vendue est empruntée sur la plateforme de vente, trade seulement si elle y est empruntable pour toute la quantité ; intérêts d'emprunt déduits (toute la durée de tenue), au taux publié par la plateforme, sinon "+(d.tauxDefautH*100).toFixed(3)+" % par heure (estimé, prudent) · Aster (DEX) : seulement côté vente à découvert, en perpétuel USDT (pas d'emprunt) ; le funding réellement versé depuis l'ouverture remplace les intérêts ; marge en USDC/USDT à déposer en réel (non comptée) ; même nom de jeton supposé = même jeton (non vérifié) · entrée si le gain à l'entrée ≥ "+r.entreeMin2+" $ après frais, une position par actif et par variante, clôture quand l'écart dans le sens contraire rapporte ≥ 5 $ ou ≥ 10 $ après frais et intérêts. Frais preneur (palier de base, estimés, prudents) : "+Object.entries(d.frais).map(([k,v])=>k+" "+(v*100).toFixed(2)+"%").join(", ")+".";
}
async function comptes(){try{const d=await (await fetch("/api/comptes",{cache:"no-store"})).json();
 document.getElementById("comptes").innerHTML="<div><b>Mode réel : désactivé</b> — aucun ordre n'est envoyé.</div>"+Object.entries(d.comptes).map(([k,v])=>"<div>"+k+" — "+(!v.cles?"clé API pas encore fournie":v.ok?'<span class="ok">clé OK</span> · '+usd(v.usdt)+" USDT disponibles":'<span class="ko">clé refusée</span> : '+v.err)+"</div>").join("");}catch(e){}}
async function fermer(id,net){if(!confirm("Clôturer cette position maintenant ?\nNet estimé : "+(net==null?"inconnu":usd(net))+" (calculé au vrai carnet au moment du clic, frais et intérêts compris)."))return;
 try{const r=await (await fetch("/api/fermer?id="+id,{method:"POST"})).json();alert(r.ok?"Position clôturée. Net : "+usd(r.net):"Impossible : "+r.err);}catch(e){alert("Erreur : "+e.message)}go();}
go();comptes();setInterval(go,10e3);setInterval(comptes,60e3);
</script></body></html>
