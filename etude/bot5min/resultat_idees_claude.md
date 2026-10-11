# Bot95 — Trois idées de Claude, premier test sur les cycles enregistrés (PRÉLIMINAIRE)

51 cycles de Dublin (avant la période réservée) ; gagnant lu dans le carnet de fin de cycle (inconnu pour 21). Aucune règle, aucun bot modifié.

## I1. Suivre les gros preneurs Polymarket

| Taille de la transaction preneuse | Transactions | Mouvement du milieu dans son sens +1 s / +5 s / +30 s (c) | Suivre au même prix : résultat par part au règlement |
|---|---|---|---|
| < 100 $ | 56344 | +0.47 / +0.62 / +0.30 | -0.40 c (35312) |
| 100–500 $ | 862 | +0.16 / -0.05 / -1.15 | -2.19 c (563) |
| ≥ 500 $ | 57 | +1.54 / -0.08 / -0.94 | -11.29 c (36) |

Si les grosses transactions continuent dans leur sens, on peut les suivre sans course de vitesse (horizon de secondes, pas de millisecondes).

## I2. Maker de fin de cycle sur le côté presque acquis (≥ 0,90 à 30 s de la fin)

- Cycles avec un côté ≥ 0,90 à 30 s de la fin : 9 ; ce côté a gagné 9 fois (100 %).
- Cycles où des vendeurs ont frappé les acheteurs de ce côté (≥ 0,90) dans les 30 dernières s : 8 ; volume médian 1227 parts ; prix moyen 0.984 ; le côté a gagné 8 fois sur 8.
- Un acheteur posé à ces prix (sans frais maker, avec ristourne) gagne 1 − prix par part si le côté gagne, perd le prix sinon.

## I3. Double maker (meilleur acheteur ET meilleur vendeur du jeton Up)

- Fenêtres de 10 s : 1428 ; meilleur acheteur consommé : 1181 ; meilleur vendeur consommé : 1183 ; LES DEUX : 1119 (78 %). Écart médian au début de la fenêtre : 1.0 c.
- Un double maker en tête de file gagnerait l'écart sur ces fenêtres ; ailleurs il garde un côté seul (risque directionnel, sélection adverse mesurée sur M2).

## Limites
- Une journée de données ; aucune file d'attente simulée pour I2 et I3 (on suppose être en tête) : ce sont des PLAFONDS.
