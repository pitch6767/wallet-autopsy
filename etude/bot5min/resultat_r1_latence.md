# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 16.10.2026 07:18 UTC. 1226 signaux réglés sur 294 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 1110 | 28 % | 0.21 | 116 | 48 % | 0.27 | +21 | [+10 ; +31] |
| 100 ms | 1023 | 27 % | 0.21 | 203 | 41 % | 0.24 | +14 | [+5 ; +22] |
| 250 ms | 795 | 24 % | 0.20 | 431 | 40 % | 0.24 | +16 | [+10 ; +22] |
| 500 ms | 685 | 22 % | 0.20 | 541 | 39 % | 0.24 | +16 | [+10 ; +22] |
| 1000 ms | 612 | 20 % | 0.19 | 614 | 39 % | 0.24 | +18 | [+12 ; +24] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 290 | 217 : 23 % | 73 : 26 % | +29.63 |
| V2-F incertitude 0,01 % | 204 | 98 : 39 % | 106 : 52 % | +954.18 |
| cohorte A : zone + modele monte | 35 | 11 : 36 % | 24 : 46 % | +454.01 |
| cohorte B : V2-F corrige 0,015 % | 187 | 91 : 34 % | 96 : 52 % | +992.44 |
| desaccord 20 60-180 s | 278 | 221 : 19 % | 57 : 26 % | +232.38 |
| desaccord 20 jeton 0,35-0,65 | 13 | 5 : 40 % | 8 : 75 % | -5.06 |
| desaccord 30 | 219 | 152 : 16 % | 67 : 22 % | +1062.48 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
