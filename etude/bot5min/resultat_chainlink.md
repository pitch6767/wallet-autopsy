# Bot95 — Chainlink : moyenne officielle et prévision (PRÉLIMINAIRE)

Généré le 12.10.2026 19:12 UTC. 383 cycles avec le nouveau flux, 110376 valeurs Chainlink BTC (une par seconde), 107566 moyennes officielles 60 s.

## 1. Moyenne officielle 60 s contre notre reconstruction

| Fenêtre reconstruite (valeurs Chainlink 1 s) | Moyennes comparées | Écart médian absolu | Écart max absolu |
|---|---|---|---|
| [T−60 ; T−1] | 53597 | 0.3603 $ | 7.4798 $ |
| [T−59 ; T] | 54224 | 0.6008 $ | 11.1581 $ |
| [T−60 ; T] | 53597 | 0.4814 $ | 10.1606 $ |

Prix à battre calculé par le bot de Dublin (moyenne des valeurs reçues pendant les 60 s avant le début, par seconde de RÉCEPTION) contre la moyenne officielle à l'instant du début : 340 cycles, écart médian absolu 0.29 $, max 7.15 $.

La moyenne officielle arrive à Dublin 1269 ms (médiane) après son instant de calcul.

## 2. Prévoir la valeur Chainlink avant sa publication (~1,2 s de retard)

À l'instant d'observation s d'une valeur Chainlink, on ne la connaîtra qu'environ 1,2 s plus tard. Prévision avec ce que Dublin sait à s + δ : médiane des bourses (Bybit perp, OKX perp, Binance, Coinbase) + écart moyen bourses−Chainlink des 60 dernières valeurs DÉJÀ publiées à ce moment.

| Information utilisée | Valeurs prévues | Erreur médiane absolue | p90 | Témoin : dernière valeur publiée | Témoin p90 |
|---|---|---|---|---|---|
| bourses à s + 0 ms | 110308 | 1.90 $ | 5.83 $ | 0.46 $ | 4.71 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 0 ms) | 110299 | 0.45 $ | 3.58 $ | 0.46 $ | 4.71 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 0 ms) | 110299 | 0.48 $ | 3.02 $ | 0.46 $ | 4.71 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 0 ms) | 110299 | 0.55 $ | 4.09 $ | 0.46 $ | 4.71 $ |
| bourses à s + 100 ms | 110309 | 1.92 $ | 5.96 $ | 0.44 $ | 4.41 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 100 ms) | 110301 | 0.43 $ | 3.36 $ | 0.44 $ | 4.41 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 100 ms) | 110301 | 0.47 $ | 2.96 $ | 0.44 $ | 4.41 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 100 ms) | 110301 | 0.53 $ | 4.19 $ | 0.44 $ | 4.41 $ |
| bourses à s + 250 ms | 110308 | 1.96 $ | 6.17 $ | 0.38 $ | 3.84 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 250 ms) | 110300 | 0.40 $ | 2.99 $ | 0.38 $ | 3.84 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 250 ms) | 110300 | 0.43 $ | 2.87 $ | 0.38 $ | 3.84 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 250 ms) | 110300 | 0.50 $ | 4.27 $ | 0.38 $ | 3.84 $ |
| bourses à s + 500 ms | 110309 | 2.02 $ | 6.61 $ | 0.31 $ | 2.97 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 500 ms) | 110303 | 0.35 $ | 2.54 $ | 0.31 $ | 2.97 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 500 ms) | 110303 | 0.40 $ | 2.85 $ | 0.31 $ | 2.97 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 500 ms) | 110303 | 0.46 $ | 4.67 $ | 0.31 $ | 2.97 $ |

Lecture : si l'erreur de prévision est nettement plus petite que celle du témoin, nous connaissons la prochaine valeur Chainlink environ 1 s avant sa publication (base de M3).

## Limites
- Une seule journée partielle ; chiffres indicatifs.
- L'heure d'observation Chainlink est à la seconde.
