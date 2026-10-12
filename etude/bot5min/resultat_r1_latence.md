# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 12.10.2026 23:02 UTC. 1087 signaux réglés sur 255 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 986 | 27 % | 0.21 | 101 | 46 % | 0.27 | +19 | [+8 ; +29] |
| 100 ms | 911 | 27 % | 0.21 | 176 | 39 % | 0.25 | +13 | [+4 ; +22] |
| 250 ms | 710 | 24 % | 0.20 | 377 | 38 % | 0.25 | +14 | [+7 ; +20] |
| 500 ms | 611 | 23 % | 0.20 | 476 | 36 % | 0.24 | +14 | [+8 ; +20] |
| 1000 ms | 545 | 21 % | 0.20 | 542 | 36 % | 0.24 | +15 | [+8 ; +20] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 253 | 194 : 25 % | 59 : 20 % | +641.92 |
| V2-F incertitude 0,01 % | 183 | 89 : 35 % | 94 : 50 % | +393.33 |
| cohorte A : zone + modele monte | 32 | 10 : 30 % | 22 : 45 % | +256.89 |
| cohorte B : V2-F corrige 0,015 % | 166 | 81 : 31 % | 85 : 51 % | +613.94 |
| desaccord 20 60-180 s | 243 | 196 : 20 % | 47 : 23 % | +405.39 |
| desaccord 20 jeton 0,35-0,65 | 12 | 5 : 40 % | 7 : 86 % | -5.06 |
| desaccord 30 | 198 | 135 : 16 % | 63 : 21 % | +1290.44 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
