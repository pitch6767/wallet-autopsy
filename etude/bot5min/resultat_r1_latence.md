# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 11.10.2026 14:48 UTC. 283 signaux réglés sur 61 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 263 | 37 % | 0.22 | 20 | 45 % | 0.27 | +8 | [-11 ; +29] |
| 100 ms | 247 | 34 % | 0.22 | 36 | 56 % | 0.24 | +21 | [+3 ; +37] |
| 250 ms | 206 | 30 % | 0.22 | 77 | 56 % | 0.24 | +26 | [+14 ; +38] |
| 500 ms | 180 | 28 % | 0.22 | 103 | 52 % | 0.24 | +24 | [+15 ; +34] |
| 1000 ms | 164 | 27 % | 0.22 | 119 | 51 % | 0.24 | +24 | [+14 ; +34] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 61 | 52 : 37 % | 9 : 22 % | +1013.26 |
| V2-F incertitude 0,01 % | 55 | 31 : 39 % | 24 : 58 % | +205.28 |
| cohorte A : zone + modele monte | 9 | 2 : 50 % | 7 : 71 % | +115.36 |
| cohorte B : V2-F corrige 0,015 % | 36 | 21 : 29 % | 15 : 80 % | +393.29 |
| desaccord 20 60-180 s | 60 | 54 : 26 % | 6 : 50 % | +1164.18 |
| desaccord 20 jeton 0,35-0,65 | 3 | 1 : 0 % | 2 : 100 % | -50.41 |
| desaccord 30 | 59 | 45 : 22 % | 14 : 36 % | +919.32 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
