# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 11.10.2026 23:44 UTC. 684 signaux réglés sur 154 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 623 | 31 % | 0.22 | 61 | 46 % | 0.28 | +15 | [+3 ; +28] |
| 100 ms | 582 | 29 % | 0.21 | 102 | 48 % | 0.27 | +19 | [+7 ; +31] |
| 250 ms | 445 | 25 % | 0.21 | 239 | 45 % | 0.25 | +20 | [+12 ; +28] |
| 500 ms | 382 | 23 % | 0.21 | 302 | 43 % | 0.25 | +20 | [+12 ; +27] |
| 1000 ms | 343 | 22 % | 0.20 | 341 | 42 % | 0.24 | +20 | [+12 ; +27] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 152 | 119 : 27 % | 33 : 24 % | +679.69 |
| V2-F incertitude 0,01 % | 123 | 60 : 37 % | 63 : 59 % | +215.76 |
| cohorte A : zone + modele monte | 22 | 5 : 40 % | 17 : 47 % | +302.99 |
| cohorte B : V2-F corrige 0,015 % | 104 | 52 : 33 % | 52 : 63 % | +604.65 |
| desaccord 20 60-180 s | 147 | 119 : 21 % | 28 : 21 % | +762.27 |
| desaccord 20 jeton 0,35-0,65 | 8 | 2 : 0 % | 6 : 100 % | -57.94 |
| desaccord 30 | 128 | 88 : 16 % | 40 : 22 % | +945.07 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
