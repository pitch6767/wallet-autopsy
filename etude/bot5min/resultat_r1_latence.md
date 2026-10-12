# Bot95 — R1 garde latence (avant le 13.10) — mesure pure

Généré le 12.10.2026 06:08 UTC. 851 signaux réglés sur 193 cycles. « Resté » = encore une quantité achetable au prix du signal après le délai. IC 90 % par rééchantillonnage de cycles.

| Délai après décision | Restés | gagnés | prix moyen | Partis | gagnés | prix moyen | Écart partis − restés (points) | IC 90 % |
|---|---|---|---|---|---|---|---|---|
| 50 ms | 776 | 30 % | 0.22 | 75 | 44 % | 0.28 | +14 | [+3 ; +26] |
| 100 ms | 717 | 29 % | 0.22 | 134 | 40 % | 0.26 | +11 | [+2 ; +22] |
| 250 ms | 553 | 26 % | 0.21 | 298 | 39 % | 0.25 | +13 | [+6 ; +21] |
| 500 ms | 482 | 24 % | 0.21 | 369 | 39 % | 0.25 | +15 | [+8 ; +22] |
| 1000 ms | 424 | 23 % | 0.21 | 427 | 38 % | 0.24 | +15 | [+8 ; +22] |

**Par variante (250 ms)**

| Variante | Signaux | Restés : gagnés | Partis : gagnés | P&L réel à 250 ms ($) |
|---|---|---|---|---|
| V2-F ecart qui grandit | 191 | 148 : 28 % | 43 : 21 % | +997.10 |
| V2-F incertitude 0,01 % | 150 | 72 : 38 % | 78 : 51 % | +457.34 |
| cohorte A : zone + modele monte | 26 | 8 : 38 % | 18 : 44 % | +350.14 |
| cohorte B : V2-F corrige 0,015 % | 130 | 67 : 33 % | 63 : 56 % | +694.87 |
| desaccord 20 60-180 s | 185 | 147 : 22 % | 38 : 21 % | +1050.99 |
| desaccord 20 jeton 0,35-0,65 | 11 | 4 : 25 % | 7 : 86 % | -77.90 |
| desaccord 30 | 158 | 107 : 18 % | 51 : 22 % | +1524.76 |

Lecture : un écart positif et stable signifie que les signaux gagnants sont pris par d'autres avant nous (sélection adverse par la latence). Aucune règle n'est tirée de cette mesure sans décision de Pitch.
