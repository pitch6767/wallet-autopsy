# Bot95 — H1079 : les deux candidates rejouées sur les jours de transactions publiques

Approximations : voir l'en-tête du script. Résultat par dollar engagé (mise fixe). Aucun ordre.

## D30M : 198 achats, 143 gagnants, prix moyen 0.638, ROI +13.0 % (IC 90 % [+3.4 ; +22.9] %)

|   jour |   achats |   gagnants |   roi |   gain_pour_10_dollars |
|-------:|---------:|-----------:|------:|-----------------------:|
|    3.1 |       28 |         18 |  -9.3 |                  -26.1 |
|    4.1 |       20 |         16 |  64.2 |                  128.4 |
|    5.1 |       20 |         12 |  -2   |                   -4.1 |
|    6.1 |       24 |         22 |  51.9 |                  124.6 |
|    7.1 |       21 |         14 |   9.2 |                   19.3 |
|    8.1 |       19 |         14 |   4.8 |                    9.2 |
|    9.1 |       18 |         15 |  26.9 |                   48.4 |
|   10.1 |       27 |         17 | -15.2 |                  -41.1 |
|   11.1 |       21 |         15 |  -0.9 |                   -1.9 |

Jours positifs : 5 sur 9.

## TWAPF : 1347 achats, 342 gagnants, prix moyen 0.252, ROI -25.8 % (IC 90 % [-38.1 ; -11.7] %)

|   jour |   achats |   gagnants |   roi |   gain_pour_10_dollars |
|-------:|---------:|-----------:|------:|-----------------------:|
|    3.1 |      150 |         36 |  -0.3 |                   -5.1 |
|    4.1 |      151 |         33 | -32.7 |                 -494.2 |
|    5.1 |      157 |         41 |  -3.3 |                  -51.8 |
|    6.1 |      145 |         45 |  27.5 |                  398.7 |
|    7.1 |      152 |         36 | -53.9 |                 -818.8 |
|    8.1 |      139 |         43 | -48.1 |                 -668.2 |
|    9.1 |      140 |         46 | -20.1 |                 -282   |
|   10.1 |      163 |         31 | -48.5 |                 -790   |
|   11.1 |      150 |         31 | -51   |                 -764.7 |

Jours positifs : 1 sur 9.


## Sensibilité à l'exécution (même signaux, prix payé = PREMIÈRE transaction dans les 2 s au lieu de la médiane sur 6 s)

- D30M : 198 achats, prix moyen 0,416, ROI **+99 %** (IC 90 % [+80 ; +120] %) au lieu de +13 %.
- TWAPF : 1 293 achats, prix moyen 0,238, ROI −10 % (IC [−23 ; +4] %) au lieu de −26 %.

## Lecture (14.10.2026)

- D30M est une stratégie de **vitesse** : elle se déclenche quand BTC vient de bouger et que Polymarket rattrape ; le prix grimpe de 0,25–0,35
  à 0,42 (première transaction) puis 0,64 (médiane sur 6 s). Son gain dépend entièrement d'être servi dans la seconde. Positive dans les deux
  hypothèses, 5 jours positifs sur 9 avec l'hypothèse lente.
- TWAP fin ne peut pas être jugée ainsi : en fin de cycle, l'écart Binance / Chainlink (le vrai juge) décide de beaucoup de règlements serrés, et
  les signaux sont justement pris là où l'approximation se trompe le plus. Il faudrait l'historique Chainlink.
- Conclusion : ce rejeu ne remplace pas les jours en direct ; il dit surtout que la n°1 doit être exécutée très vite.
