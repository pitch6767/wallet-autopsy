# Contrôle des résultats officiels — NON VALIDÉS POUR LE LIVE

Sources : API publiques /api/rapide et /api/rapidemaker de bot95.pitch67.workers.dev,
et source officielle GitHub bot95/src/rapide_code.js.
Version signalée par la télémétrie et le code consulté : e0f02935f49a.
Les offres individuelles ne portent pas de version : leur fenêtre ne doit pas
être attribuée intégralement à cette version.

Fenêtre des cycles publiés analysés : 13 octobre 2026, 09:15–15:15 UTC.
9 482 offres, aucun doublon de clé (cycle, stratégie, oid) dans cet échantillon.
Calculs sur remplR, modèle proportionnel publié ; ce ne sont pas des fills réels.

| Stratégie | Cycles publiés remplis | Single leg | Déséquilibre > 1 part | Parts non couvertes | Côtés > 50 $ | Dépense maximale / côté |
|---|---:|---:|---:|---:|---:|---:|
| M10 double maker meilleur prix | 58 | 0 | 58 | 47,04 % | 78 / 116 | 230,25 $ |
| M2 cotation marge 10 c | 58 | 35 | 58 | 74,00 % | 38 / 116 | 315,42 $ |
| M2 cotation marge 5 c | 58 | 23 | 58 | 50,72 % | 50 / 116 | 588,53 $ |

Un cycle à deux jambes n'est pas nécessairement couvert. La fraction non couverte
est somme(abs(Up-Down))/somme(Up+Down), sans pondération temporelle.
Les cycles absents de l'API ne sont pas supposés réussis ou sans remplissage.
La somme des dépenses est reconstituée depuis les quantités remplies et leurs prix.
Le code de cotation M2 utilise un budget de 50, qui n'est pas respecté dans ces données.

Constats de code : latence supposée égale à la moitié du RTT médian (minimum 5 ms),
transactions BUY transformées en ventes du jeton complémentaire, simulation de file
via transactions et retraits de carnet, re-cotation avant fin effective d'annulation,
règlement déduit d'un outcomePrice égal à 1 sans exiger explicitement closed/resolved.
Ces hypothèses nécessitent une validation ; un nom « prudent » n'en est pas une.

Le PnL publié n'est pas recalculé en inventant de nouveaux fills. Il ne peut pas
être utilisé comme estimation validée de performance réelle.

Reproduction : node audit-official.cjs /chemin/vers/maker.json 6
Tests : node --test audit-official.test.cjs

## Relecture des transactions enregistrées

Cycle de 15:15 UTC (start 1791904500), enregistrement officiel e0f02935f49a,
non marqué tronqué. Le diagnostic hors ligne rejoue les transactions SELL au
prix exact, déduit la file affichée, partage chaque volume entre les offres
d'une même stratégie et limite les dépenses à 50 $ par côté.

Pour M10, les offres publiées annoncent 389,9932 parts Up et 111,38 Down,
soit une dépense totale de 223,38 $. Cette relecture stricte ne reproduit aucun
de ces remplissages. Même constat avec planchers de latence de 0, 50, 100 et
250 ms, sans avancer l'arrivée avant celle de l'enregistrement.

Cela ne prouve PAS qu'aucun ordre réel n'aurait été exécuté : cette variante
exclut les transactions miroirs, les niveaux traversés et les annulations
supposées devant nous. Les décisions de cotation historiques sont figées,
pas recalculées avec les nouveaux fills. C'est un diagnostic de sensibilité,
pas un backtest complet ni une borne garantie de performance réelle.

Reproduction :
node replay-prints.cjs cycle.json.gz maker.json
Tests :
node --test audit-official.test.cjs replay-prints.test.cjs

Aucune modification du bot officiel, d'une stratégie, du Worker ou de main.
Le contrôle SSH n'a pas été effectué : aucune clé d'hôte connue n'était disponible
dans cette session ; le contrôle strict n'a pas été contourné.

Pour des résultats exploitables : comparer hors production un fantôme distinct
aux événements enregistrés, borner les volumes et budgets, conserver l'exposition
et les coûts, puis calibrer les hypothèses d'exécution. Intégration uniquement via
GitHub et accord explicite, sans utiliser ce rapport comme autorisation de live.
