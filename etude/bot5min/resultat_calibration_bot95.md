# Bot95 — Étude de calibration (CONTRÔLE DU CODE sur la période antérieure — pas un verdict)

Généré le 11.10.2026 20:04 UTC. Apprentissage : 73 décisions uniques (53 cycles). Évaluation : 71 décisions (54 cycles). Aucun ordre ; H816 inchangé.

Coefficients appris : C1 logit(Bot95) [-0.322, +1.370] ; C2 logit(Bot95) + logit(prix) [+1.092, +0.103, +1.407] ; C3 C2 + temps restant [+0.561, +0.184, +1.385, +0.726]

## Toutes les décisions uniques (71 décisions, 54 cycles)

| Estimateur | Brier | Log loss | Brier − prix a0 | IC 90 % | IC corrigé (3 candidats) | Bat le marché ? |
|---|---|---|---|---|---|---|
| Bot95 brut | 0.2078 | 0.6157 | +0.0312 | [+0.0085 ; +0.0546] | [+0.0018 ; +0.0604] | — |
| prix a0 (marché) | 0.1766 | 0.5278 | — | — | — | référence |
| C1 logit(Bot95) | 0.1837 | 0.5692 | +0.0071 | [-0.0094 ; +0.0237] | [-0.0141 ; +0.0298] | non |
| C2 logit(Bot95) + logit(prix) | 0.1770 | 0.5441 | +0.0004 | [-0.0174 ; +0.0199] | [-0.0235 ; +0.0258] | non |
| C3 C2 + temps restant | 0.1753 | 0.5403 | -0.0013 | [-0.0200 ; +0.0186] | [-0.0255 ; +0.0248] | non |

| Temps restant | Décisions | Victoire | Bot95 | Prix a0 | C2 |
|---|---|---|---|---|---|
| 60–120 s | 12 | 8 % | 0.40 | 0.17 | 0.24 |
| 120–180 s | 17 | 29 % | 0.45 | 0.24 | 0.35 |
| 180–240 s | 22 | 36 % | 0.51 | 0.30 | 0.45 |
| 240–301 s | 20 | 40 % | 0.55 | 0.34 | 0.49 |

## Plage H816 (prix 0,20–0,50), descriptif (42 décisions, 37 cycles)

| Estimateur | Brier | Log loss | Brier − prix a0 | IC 90 % | IC corrigé (3 candidats) | Bat le marché ? |
|---|---|---|---|---|---|---|
| Bot95 brut | 0.2176 | 0.6273 | +0.0138 | [-0.0286 ; +0.0574] | [-0.0431 ; +0.0693] | — |
| prix a0 (marché) | 0.2038 | 0.5948 | — | — | — | référence |
| C1 logit(Bot95) | 0.1943 | 0.5781 | -0.0095 | [-0.0348 ; +0.0167] | [-0.0418 ; +0.0247] | non |
| C2 logit(Bot95) + logit(prix) | 0.1934 | 0.5754 | -0.0104 | [-0.0413 ; +0.0202] | [-0.0491 ; +0.0305] | non |
| C3 C2 + temps restant | 0.1947 | 0.5776 | -0.0091 | [-0.0386 ; +0.0229] | [-0.0476 ; +0.0316] | non |

| Temps restant | Décisions | Victoire | Bot95 | Prix a0 | C2 |
|---|---|---|---|---|---|
| 60–120 s | 5 | 20 % | 0.43 | 0.22 | 0.33 |
| 120–180 s | 7 | 43 % | 0.47 | 0.26 | 0.40 |
| 180–240 s | 17 | 41 % | 0.50 | 0.29 | 0.44 |
| 240–301 s | 13 | 23 % | 0.46 | 0.25 | 0.38 |

## Critère
Un candidat bat le marché si l'IC corrigé de la différence de Brier est entièrement < 0. Sinon, aucune calibration n'est retenue.
