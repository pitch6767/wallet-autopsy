# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 11.10.2026 19:35 UTC. 480 signaux réglés sur 107 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 441 | 33 % | 0.22 | 39 | 56 % | 0.30 | +24 | [+8 ; +38] |
| 100 ms | 421 | 32 % | 0.22 | 59 | 56 % | 0.28 | +24 | [+11 ; +37] |
| 250 ms | 333 | 27 % | 0.21 | 147 | 52 % | 0.26 | +24 | [+14 ; +34] |
| 500 ms | 278 | 25 % | 0.20 | 202 | 49 % | 0.26 | +24 | [+15 ; +33] |
| 1000 ms | 260 | 24 % | 0.20 | 220 | 48 % | 0.25 | +24 | [+15 ; +33] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 106 | 88 : 30 % | 18 : 28 % | +852.40 |
| V2-F incertitude 0,01 % | 88 | 46 : 39 % | 42 : 60 % | +328.93 |
| cohorte A : zone + modele monte | 16 | 3 : 33 % | 13 : 54 % | +71.81 |
| cohorte B : V2-F corrige 0,015 % | 70 | 37 : 35 % | 33 : 70 % | +743.16 |
| desaccord 20 60-180 s | 102 | 88 : 24 % | 14 : 29 % | +1194.65 |
| desaccord 20 jeton 0,35-0,65 | 6 | 2 : 0 % | 4 : 100 % | -57.94 |
| desaccord 30 | 92 | 69 : 17 % | 23 : 35 % | +781.88 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
