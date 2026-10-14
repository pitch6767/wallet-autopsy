# Bot95 — Étude de calibration (PÉRIODE RÉSERVÉE)

Généré le 14.10.2026 07:40 UTC. Apprentissage : 381 décisions uniques (294 cycles). Évaluation : 329 décisions (266 cycles). Aucun ordre ; H816 inchangé.

Coefficients appris : C1 logit(Bot95) [-0.659, +1.537] ; C2 logit(Bot95) + logit(prix) [+0.565, +0.219, +1.183] ; C3 C2 + temps restant [+0.346, +0.233, +1.143, +0.295]

## Toutes les décisions uniques (329 décisions, 266 cycles)

| Estimateur | Brier | Log loss | Brier − prix a0 | IC 90 % | IC corrigé (3 candidats) | Bat le marché ? |
|---|---|---|---|---|---|---|
| Bot95 brut | 0.1849 | 0.5572 | +0.0272 | [+0.0161 ; +0.0385] | [+0.0129 ; +0.0422] | — |
| prix a0 (marché) | 0.1577 | 0.4875 | — | — | — | référence |
| C1 logit(Bot95) | 0.1539 | 0.4788 | -0.0039 | [-0.0093 ; +0.0017] | [-0.0107 ; +0.0038] | non |
| C2 logit(Bot95) + logit(prix) | 0.1533 | 0.4791 | -0.0044 | [-0.0098 ; +0.0012] | [-0.0114 ; +0.0030] | non |
| C3 C2 + temps restant | 0.1523 | 0.4768 | -0.0055 | [-0.0107 ; -0.0001] | [-0.0122 ; +0.0017] | non |

| Temps restant | Décisions | Victoire | Bot95 | Prix a0 | C2 |
|---|---|---|---|---|---|
| 0–60 s | 15 | 13 % | 0.44 | 0.17 | 0.21 |
| 60–120 s | 141 | 15 % | 0.38 | 0.17 | 0.20 |
| 120–180 s | 114 | 27 % | 0.41 | 0.20 | 0.25 |
| 180–240 s | 39 | 46 % | 0.49 | 0.28 | 0.37 |
| 240–301 s | 20 | 50 % | 0.58 | 0.37 | 0.48 |

## Plage H816 (prix 0,20–0,50), descriptif (131 décisions, 118 cycles)

| Estimateur | Brier | Log loss | Brier − prix a0 | IC 90 % | IC corrigé (3 candidats) | Bat le marché ? |
|---|---|---|---|---|---|---|
| Bot95 brut | 0.2286 | 0.6510 | +0.0308 | [+0.0064 ; +0.0548] | [+0.0001 ; +0.0621] | — |
| prix a0 (marché) | 0.1979 | 0.5808 | — | — | — | référence |
| C1 logit(Bot95) | 0.1955 | 0.5779 | -0.0024 | [-0.0126 ; +0.0094] | [-0.0158 ; +0.0127] | non |
| C2 logit(Bot95) + logit(prix) | 0.1932 | 0.5737 | -0.0047 | [-0.0165 ; +0.0076] | [-0.0200 ; +0.0109] | non |
| C3 C2 + temps restant | 0.1901 | 0.5664 | -0.0078 | [-0.0191 ; +0.0039] | [-0.0221 ; +0.0068] | non |

| Temps restant | Décisions | Victoire | Bot95 | Prix a0 | C2 |
|---|---|---|---|---|---|
| 0–60 s | 5 | 0 % | 0.51 | 0.31 | 0.40 |
| 60–120 s | 48 | 19 % | 0.48 | 0.26 | 0.34 |
| 120–180 s | 45 | 33 % | 0.49 | 0.28 | 0.36 |
| 180–240 s | 23 | 57 % | 0.53 | 0.33 | 0.43 |
| 240–301 s | 10 | 50 % | 0.52 | 0.31 | 0.41 |

## Critère
Un candidat bat le marché si l'IC corrigé de la différence de Brier est entièrement < 0. Sinon, aucune calibration n'est retenue.
