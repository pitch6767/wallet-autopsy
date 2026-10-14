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
      {name:'Identification de la copie de référence officielle',status:identity?'verifie':'bloquant',detail:error||'Version figée pour les tests ; les mises à jour automatiques du bot officiel ne sont pas encore suivies par ce comparateur.'},
      {name:'Même stratégie dans le comparateur en fonctionnement',status:'bloquant',detail:'Le fantôme actuel reste une stratégie différente. Ses résultats ne valident pas M10.'},
      {name:'Décisions officielles avec exécutions simulées et sorties',status:'bloquant',detail:'Extraction du code M10 disponible ; raccordement complet aux flux et à la comptabilité non terminé.'},
      {name:'Exécution et annulation calibrées',status:'non_verifie',detail:'100 ms est une hypothèse, pas une latence de passage d’ordre mesurée.'},
      {name:'Règlements et réconciliation de compte',status:'non_verifie',detail:'Aucun rapprochement avec des exécutions privées et un compte non vide.'},
    ],
    conclusion:'Aucun feu vert live. Aucun PnL du fantôme simplifié utilisé pour ce verdict.'
  };
}
module.exports={assess};
