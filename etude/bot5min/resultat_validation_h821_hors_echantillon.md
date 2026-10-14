# Bot95 — Validation H821 : H816 contre H816 + filtre H821 (PÉRIODE RÉSERVÉE)

Généré le 14.10.2026 07:40 UTC. Cycles avec décisions H816 : 98 ; décisions H816 : 108 ; retirées par le filtre (dist_sigma > -0.0905) : 23 dont 0 par donnée manquante. Mise 20 $, IC 90 % par cycles. Aucun ordre.

## 1. Résultat principal (164 ms) et sensibilité à la latence

| Délai | Politique | Décisions | Exécutées | Taux de gain | Capital engagé ($) | P&L net ($) | P&L par $ | Drawdown ($) | Pire série de pertes | Jackpots | 5 meilleures / total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 164 ms (critère) | H816 | 108 | 88 | 24 % | 1562 | -362 | -23.2 % | 431 | 8 pertes, -160 $ | 9 | nan % |
| 164 ms (critère) | H816 + H821 | 85 | 70 | 21 % | 1235 | -327 | -26.5 % | 407 | 10 pertes, -183 $ | 7 | nan % |
| 200 ms | H816 | 108 | 84 | 23 % | 1482 | -393 | -26.5 % | 449 | 8 pertes, -160 $ | 8 | nan % |
| 200 ms | H816 + H821 | 85 | 66 | 20 % | 1158 | -355 | -30.6 % | 398 | 10 pertes, -173 $ | 6 | nan % |
| 250 ms | H816 | 108 | 79 | 24 % | 1467 | -381 | -26.0 % | 435 | 8 pertes, -160 $ | 8 | nan % |
| 250 ms | H816 + H821 | 85 | 62 | 21 % | 1157 | -357 | -30.8 % | 401 | 9 pertes, -180 $ | 6 | nan % |
| 500 ms | H816 | 108 | 66 | 20 % | 1249 | -354 | -28.4 % | 417 | 9 pertes, -163 $ | 8 | nan % |
| 500 ms | H816 + H821 | 85 | 51 | 16 % | 982 | -406 | -41.3 % | 444 | 11 pertes, -216 $ | 5 | nan % |

## 2. Différence variante − H816 et filtre

| Délai | Perdants évités | Gagnants supprimés | Jackpots supprimés | Différence de P&L ($) | IC 90 % total ($) | IC 90 % par décision H816 ($) |
|---|---|---|---|---|---|---|
| 164 ms | 12 | 6 | 2 | +35 | [-175 ; +224] | [-1.61 ; +2.09] |
| 200 ms | 12 | 6 | 2 | +39 | [-168 ; +230] | [-1.56 ; +2.15] |
| 250 ms | 11 | 6 | 2 | +24 | [-189 ; +214] | [-1.73 ; +1.99] |
| 500 ms | 10 | 5 | 3 | -51 | [-289 ; +157] | [-2.64 ; +1.46] |

(Perdants / gagnants / jackpots comptés parmi les décisions retirées qui auraient été exécutées ; 5 retirées n'auraient pas été exécutées à 164 ms.)

## 3. Verdict selon le critère pré-enregistré

**ÉCHEC** — différence +35 $, IC 90 % [-178 ; +219] $. La variante est abandonnée ; le seuil n'est pas modifié.

## Limites
- La règle a été choisie parmi 38 candidates, après de nombreuses recherches sur une seule journée de données ; un succès reste une confirmation partielle.
- Peu de cycles : faible puissance ; un échec n'exclut pas un petit effet, un succès peut tenir à quelques trades.
- Une donnée manquante (Chainlink, prix à battre) exclut le signal, comme dans l'étude ; leur nombre est indiqué plus haut.
