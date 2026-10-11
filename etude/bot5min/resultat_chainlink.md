# Bot95 — Chainlink : moyenne officielle et prévision (PRÉLIMINAIRE)

Généré le 11.10.2026 12:24 UTC. 17 cycles avec le nouveau flux, 4386 valeurs Chainlink BTC (une par seconde), 1628 moyennes officielles 60 s.

## 1. Moyenne officielle 60 s contre notre reconstruction

| Fenêtre reconstruite (valeurs Chainlink 1 s) | Moyennes comparées | Écart médian absolu | Écart max absolu |
|---|---|---|---|
| [T−60 ; T−1] | 879 | 0.2497 $ | 1.6583 $ |
| [T−59 ; T] | 889 | 0.4501 $ | 2.3680 $ |
| [T−60 ; T] | 879 | 0.3484 $ | 1.8470 $ |

Prix à battre calculé par le bot de Dublin (moyenne des valeurs reçues pendant les 60 s avant le début, par seconde de RÉCEPTION) contre la moyenne officielle à l'instant du début : 4 cycles, écart médian absolu 0.07 $, max 2.04 $.

La moyenne officielle arrive à Dublin 1250 ms (médiane) après son instant de calcul.

## 2. Prévoir la valeur Chainlink avant sa publication (~1,2 s de retard)

À l'instant d'observation s d'une valeur Chainlink, on ne la connaîtra qu'environ 1,2 s plus tard. Prévision avec ce que Dublin sait à s + δ : médiane des bourses (Bybit perp, OKX perp, Binance, Coinbase) + écart moyen bourses−Chainlink des 60 dernières valeurs DÉJÀ publiées à ce moment.

| Information utilisée | Valeurs prévues | Erreur médiane absolue | p90 | Témoin : dernière valeur publiée | Témoin p90 |
|---|---|---|---|---|---|
| bourses à s + 0 ms | 4324 | 0.94 $ | 4.08 $ | 0.20 $ | 1.32 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 0 ms) | 4321 | 0.21 $ | 1.26 $ | 0.20 $ | 1.32 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 0 ms) | 4321 | 0.22 $ | 1.26 $ | 0.20 $ | 1.32 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 0 ms) | 4321 | 0.23 $ | 1.42 $ | 0.20 $ | 1.32 $ |
| bourses à s + 100 ms | 4324 | 0.94 $ | 4.12 $ | 0.19 $ | 1.28 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 100 ms) | 4322 | 0.20 $ | 1.25 $ | 0.19 $ | 1.28 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 100 ms) | 4322 | 0.21 $ | 1.26 $ | 0.19 $ | 1.28 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 100 ms) | 4322 | 0.22 $ | 1.41 $ | 0.19 $ | 1.28 $ |
| bourses à s + 250 ms | 4324 | 0.94 $ | 4.16 $ | 0.17 $ | 1.22 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 250 ms) | 4323 | 0.19 $ | 1.20 $ | 0.17 $ | 1.22 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 250 ms) | 4323 | 0.19 $ | 1.24 $ | 0.17 $ | 1.22 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 250 ms) | 4323 | 0.20 $ | 1.39 $ | 0.17 $ | 1.22 $ |
| bourses à s + 500 ms | 4326 | 0.94 $ | 4.22 $ | 0.14 $ | 1.12 $ |
| dernière valeur publiée + 0.25 × variation des bourses depuis son instant (s + 500 ms) | 4324 | 0.16 $ | 1.12 $ | 0.14 $ | 1.12 $ |
| dernière valeur publiée + 0.5 × variation des bourses depuis son instant (s + 500 ms) | 4324 | 0.16 $ | 1.16 $ | 0.14 $ | 1.12 $ |
| dernière valeur publiée + 1.0 × variation des bourses depuis son instant (s + 500 ms) | 4324 | 0.17 $ | 1.38 $ | 0.14 $ | 1.12 $ |

Lecture : si l'erreur de prévision est nettement plus petite que celle du témoin, nous connaissons la prochaine valeur Chainlink environ 1 s avant sa publication (base de M3).

## Limites
- Une seule journée partielle ; chiffres indicatifs.
- L'heure d'observation Chainlink est à la seconde.
