# Bot95 — Chainlink : moyenne officielle et prévision (PRÉLIMINAIRE)

Généré le 11.10.2026 12:41 UTC. 21 cycles avec le nouveau flux, 5405 valeurs Chainlink BTC (une par seconde), 2646 moyennes officielles 60 s.

## 1. Moyenne officielle 60 s contre notre reconstruction

| Fenêtre reconstruite (valeurs Chainlink 1 s) | Moyennes comparées | Écart médian absolu | Écart max absolu |
|---|---|---|---|
| [T−60 ; T−1] | 1457 | 0.2455 $ | 1.6771 $ |
| [T−59 ; T] | 1472 | 0.4273 $ | 2.5141 $ |
| [T−60 ; T] | 1457 | 0.3420 $ | 2.1531 $ |

Prix à battre calculé par le bot de Dublin (moyenne des valeurs reçues pendant les 60 s avant le début, par seconde de RÉCEPTION) contre la moyenne officielle à l'instant du début : 7 cycles, écart médian absolu 0.09 $, max 2.04 $.

La moyenne officielle arrive à Dublin 1239 ms (médiane) après son instant de calcul.

## 2. Prévoir la valeur Chainlink avant sa publication (~1,2 s de retard)

À l'instant d'observation s d'une valeur Chainlink, on ne la connaîtra qu'environ 1,2 s plus tard. Prévision avec ce que Dublin sait à s + δ : médiane des bourses (Bybit perp, OKX perp, Binance, Coinbase) + écart moyen bourses−Chainlink des 60 dernières valeurs DÉJÀ publiées à ce moment.

| Information utilisée | Valeurs prévues | Erreur médiane absolue | p90 | Témoin : dernière valeur publiée | Témoin p90 |
|---|---|---|---|---|---|
| bourses à s + 0 ms | 5343 | 0.98 $ | 4.29 $ | 0.20 $ | 1.39 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 0 ms) | 5340 | 0.21 $ | 1.32 $ | 0.20 $ | 1.39 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 0 ms) | 5340 | 0.22 $ | 1.33 $ | 0.20 $ | 1.39 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 0 ms) | 5340 | 0.23 $ | 1.50 $ | 0.20 $ | 1.39 $ |
| bourses à s + 100 ms | 5343 | 0.98 $ | 4.36 $ | 0.19 $ | 1.33 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 100 ms) | 5341 | 0.20 $ | 1.28 $ | 0.19 $ | 1.33 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 100 ms) | 5341 | 0.21 $ | 1.31 $ | 0.19 $ | 1.33 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 100 ms) | 5341 | 0.22 $ | 1.49 $ | 0.19 $ | 1.33 $ |
| bourses à s + 250 ms | 5343 | 0.98 $ | 4.38 $ | 0.17 $ | 1.26 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 250 ms) | 5342 | 0.18 $ | 1.23 $ | 0.17 $ | 1.26 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 250 ms) | 5342 | 0.19 $ | 1.28 $ | 0.17 $ | 1.26 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 250 ms) | 5342 | 0.20 $ | 1.48 $ | 0.17 $ | 1.26 $ |
| bourses à s + 500 ms | 5344 | 0.98 $ | 4.45 $ | 0.14 $ | 1.15 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 500 ms) | 5342 | 0.16 $ | 1.15 $ | 0.14 $ | 1.15 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 500 ms) | 5342 | 0.16 $ | 1.21 $ | 0.14 $ | 1.15 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 500 ms) | 5342 | 0.17 $ | 1.45 $ | 0.14 $ | 1.15 $ |

Lecture : si l'erreur de prévision est nettement plus petite que celle du témoin, nous connaissons la prochaine valeur Chainlink environ 1 s avant sa publication (base de M3).

## Limites
- Une seule journée partielle ; chiffres indicatifs.
- L'heure d'observation Chainlink est à la seconde.
