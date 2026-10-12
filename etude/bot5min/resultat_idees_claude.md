# Bot95 — Trois idées de Claude, premier test sur les cycles enregistrés (PRÉLIMINAIRE)

408 cycles de Dublin (avant la période réservée) ; gagnant lu dans le carnet de fin de cycle (inconnu pour 152). Aucune règle, aucun bot modifié.

## I1. Suivre les gros preneurs Polymarket

| Taille de la transaction preneuse | Transactions | Mouvement du milieu dans son sens +1 s / +5 s / +30 s (c) | Suivre au même prix : résultat par part au règlement |
|---|---|---|---|
| < 100 $ | 524681 | +0.41 / +0.45 / +0.28 | -0.13 c (348105) |
| 100–500 $ | 7752 | +0.02 / -0.17 / -0.71 | -1.24 c (5552) |
| ≥ 500 $ | 768 | +0.56 / +0.17 / -1.51 | -2.74 c (607) |

Si les grosses transactions continuent dans leur sens, on peut les suivre sans course de vitesse (horizon de secondes, pas de millisecondes).

## I2. Maker de fin de cycle sur le côté presque acquis (≥ 0,90 à 30 s de la fin)

- Cycles avec un côté ≥ 0,90 à 30 s de la fin : 32 ; ce côté a gagné 31 fois (97 %).
- Cycles où des vendeurs ont frappé les acheteurs de ce côté (≥ 0,90) dans les 30 dernières s : 30 ; volume médian 1987 parts ; prix moyen 0.981 ; le côté a gagné 29 fois sur 30.
- Un acheteur posé à ces prix (sans frais maker, avec ristourne) gagne 1 − prix par part si le côté gagne, perd le prix sinon.

## I3. Double maker (meilleur acheteur ET meilleur vendeur du jeton Up)

- Fenêtres de 10 s : 11424 ; meilleur acheteur consommé : 9829 ; meilleur vendeur consommé : 9884 ; LES DEUX : 9147 (80 %). Écart médian au début de la fenêtre : 1.0 c.
- Un double maker en tête de file gagnerait l'écart sur ces fenêtres ; ailleurs il garde un côté seul (risque directionnel, sélection adverse mesurée sur M2).

## Limites
- Une journée de données ; aucune file d'attente simulée pour I2 et I3 (on suppose être en tête) : ce sont des PLAFONDS.
