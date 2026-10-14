'use strict';
const {extract}=require('./official-m10.cjs');
function assess(source) {
  let identity=null,error=null;
  try {const s=extract(source);identity={version:s.version,sha256:s.sha256};}
  catch(e){error=e.message;}
  return {
    at:Date.now(), verdict:'PREUVES_INSUFFISANTES', official:identity,
    scope:'M10 officiel — aucun ordre réel',
    evidence:[
      {name:'Identification de la copie de référence officielle',status:identity?'verifie':'bloquant',detail:error||'Référence initiale vérifiée ; le relevé de comparaison indique la version courante et archive les sources observées. Tout cycle sans sa version exacte est exclu.'},
      {name:'Même stratégie et mêmes entrées',status:'raccorde',detail:'Le rejeu utilise les signaux enregistrés par M10 et le code de la même version. Les captures incomplètes sont exclues ; l’ancien essai reste hors validation.'},
      {name:'Décisions officielles avec exécutions simulées et règlement',status:'raccorde',detail:'Les enregistrements officiels sont rejoués séparément à 100, 250 et 500 ms. Les scénarios calculables sont réglés après confirmation Gamma ; les cas indéterminés restent signalés. Cela ne vérifie pas les exécutions privées.'},
      {name:'Exécution et annulation calibrées',status:'non_verifie',detail:'100 ms est une hypothèse, pas une latence de passage d’ordre mesurée.'},
      {name:'Règlements et réconciliation de compte',status:'non_verifie',detail:'Aucun rapprochement avec des exécutions privées et un compte non vide.'},
    ],
    conclusion:'Aucun feu vert live. Aucun PnL du fantôme simplifié utilisé pour ce verdict.'
  };
}
module.exports={assess};
