# Bot95 — H799 / H800 : compléter après un fill partiel — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 15:44 UTC. 157 signaux, 31 cycles. Apprentissage 77 signaux / 15 cycles (avant 10:55 UTC) ; test 80 signaux / 16 cycles. Règles R4 (+2 c, recalcul, marge 0,05, 164 ms, 50 $). Seuils choisis sur l'apprentissage : **B1 = B1≥25$**, **B2 = B2 P≥25$ m≥0.20** (parmi 6 et 16 réglages). Toutes les parts comptées sont exécutables contre le carnet enregistré à l'instant d'exécution (quantité affichée, budget restant, frais).

## 1. Tableau B0 / B1 / B2 — TEST (2e moitié, cycles non vus) (livrables 1, 3, 4, 5, 6)

| Politique | P&L total ($) | dont 1res parts | dont compléments | Parts compl. | Prix moyen compl. | vs D ($, IC 90 % / signal) | vs B0 ($, IC 90 % / signal) | Signaux complétés G / P | Jackpots compl. | Drawdown | 5 meilleurs compl. / total compl. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D | +3903 | +3903 | +0 | 0 | 0.000 | +0 [+0.00 ; +0.00] | -564 [-14.44 ; -0.92] | 0 / 0 | 0 | 693 | nan % |
| B0 | +4467 | +3903 | +564 | 1364 | 0.179 | +564 [+0.85 ; +14.24] | +0 [+0.00 ; +0.00] | 8 / 6 | 4 | 700 | 90 % |
| B1≥25$ | +4173 | +3903 | +269 | 471 | 0.271 | +269 [+1.06 ; +5.87] | -294 [-9.24 ; +0.64] | 5 / 1 | 2 | 693 | 104 % |
| B2 P≥25$ m≥0.20 | +4363 | +3903 | +459 | 1148 | 0.157 | +459 [-0.19 ; +12.67] | -104 [-2.96 ; -0.09] | 6 / 4 | 4 | 696 | 99 % |

## 1. Tableau B0 / B1 / B2 — APPRENTISSAGE (1re moitié) (livrables 1, 3, 4, 5, 6)

| Politique | P&L total ($) | dont 1res parts | dont compléments | Parts compl. | Prix moyen compl. | vs D ($, IC 90 % / signal) | vs B0 ($, IC 90 % / signal) | Signaux complétés G / P | Jackpots compl. | Drawdown | 5 meilleurs compl. / total compl. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D | +872 | +872 | +0 | 0 | 0.000 | +0 [+0.00 ; +0.00] | -24 [-2.29 ; +1.64] | 0 / 0 | 0 | 958 | nan % |
| B0 | +896 | +872 | +24 | 1156 | 0.188 | +24 [-1.68 ; +2.30] | +0 [+0.00 ; +0.00] | 4 / 6 | 2 | 939 | 723 % |
| B1≥25$ | +1005 | +872 | +133 | 196 | 0.318 | +133 [+0.00 ; +3.65] | +109 [-0.34 ; +3.22] | 3 / 0 | 1 | 900 | 100 % |
| B2 P≥25$ m≥0.20 | +961 | +872 | +89 | 821 | 0.190 | +89 [-0.44 ; +2.84] | +65 [+0.04 ; +2.01] | 4 / 4 | 2 | 923 | 201 % |

## 1. Tableau B0 / B1 / B2 — TOUT (livrables 1, 3, 4, 5, 6)

| Politique | P&L total ($) | dont 1res parts | dont compléments | Parts compl. | Prix moyen compl. | vs D ($, IC 90 % / signal) | vs B0 ($, IC 90 % / signal) | Signaux complétés G / P | Jackpots compl. | Drawdown | 5 meilleurs compl. / total compl. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D | +4775 | +4775 | +0 | 0 | 0.000 | +0 [+0.00 ; +0.00] | -588 [-7.51 ; -0.44] | 0 / 0 | 0 | 958 | nan % |
| B0 | +5363 | +4775 | +588 | 2520 | 0.183 | +588 [+0.51 ; +7.69] | +0 [+0.00 ; +0.00] | 12 / 12 | 6 | 939 | 86 % |
| B1≥25$ | +5178 | +4775 | +403 | 667 | 0.284 | +403 [+1.07 ; +4.09] | -185 [-4.12 ; +1.34] | 8 / 1 | 3 | 900 | 80 % |
| B2 P≥25$ m≥0.20 | +5324 | +4775 | +549 | 1969 | 0.171 | +549 [+0.47 ; +7.37] | -39 [-1.33 ; +0.59] | 10 / 8 | 6 | 923 | 85 % |

**Tous les réglages B1 (pour transparence ; la sélection ne regarde que l'apprentissage)**

| Réglage | Apprentissage ($) | Test ($) |
|---|---|---|
| B1≥0$ | +896 | +4467 |
| B1≥10$ | +954 | +4184 |
| B1≥25$ | +1005 | +4173 |
| B1≥50$ | +948 | +4041 |
| B1≥100$ | +948 | +3978 |
| B1≥200$ | +872 | +3903 |

**Tous les réglages B2**

| Réglage | Apprentissage ($) | Test ($) |
|---|---|---|
| B2 P≥0$ m≥0.05 | +896 | +4467 |
| B2 P≥0$ m≥0.10 | +900 | +4465 |
| B2 P≥0$ m≥0.15 | +900 | +4371 |
| B2 P≥0$ m≥0.20 | +916 | +4375 |
| B2 P≥10$ m≥0.05 | +900 | +4469 |
| B2 P≥10$ m≥0.10 | +900 | +4467 |
| B2 P≥10$ m≥0.15 | +900 | +4373 |
| B2 P≥10$ m≥0.20 | +916 | +4377 |
| B2 P≥25$ m≥0.05 | +945 | +4455 |
| B2 P≥25$ m≥0.10 | +945 | +4453 |
| B2 P≥25$ m≥0.15 | +945 | +4359 |
| B2 P≥25$ m≥0.20 | +961 | +4363 |
| B2 P≥50$ m≥0.05 | +887 | +4488 |
| B2 P≥50$ m≥0.10 | +887 | +4486 |
| B2 P≥50$ m≥0.15 | +887 | +4392 |
| B2 P≥50$ m≥0.20 | +904 | +4396 |

## 2. H800 — Taille du complément (livrable 2)

| Politique | P&L total ($) | dont 1res parts | dont compléments | Parts compl. | Prix moyen compl. | vs D ($, IC 90 % / signal) | vs B0 ($, IC 90 % / signal) | Signaux complétés G / P | Jackpots compl. | Drawdown | 5 meilleurs compl. / total compl. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| compléments ≤ 25 % du restant (test) | +4052 | +3903 | +149 | 367 | 0.177 | +149 [+0.21 ; +3.61] | -415 [-10.39 ; -0.77] | 8 / 6 | 4 | 694 | 92 % |
| compléments ≤ 50 % du restant (test) | +4202 | +3903 | +299 | 715 | 0.179 | +299 [+0.52 ; +7.40] | -265 [-6.63 ; -0.44] | 8 / 6 | 4 | 696 | 91 % |
| compléments ≤ 75 % du restant (test) | +4342 | +3903 | +439 | 1050 | 0.179 | +439 [+0.65 ; +11.49] | -125 [-3.23 ; -0.21] | 8 / 6 | 4 | 698 | 90 % |
| compléments ≤ 100 % du restant (test) | +4467 | +3903 | +564 | 1364 | 0.179 | +564 [+0.85 ; +14.07] | +0 [+0.00 ; +0.00] | 8 / 6 | 4 | 700 | 90 % |
| compléments ≤ 25 % du restant (tout) | +4930 | +4775 | +155 | 663 | 0.180 | +155 [+0.10 ; +2.01] | -433 [-5.76 ; -0.29] | 12 / 12 | 6 | 953 | 89 % |
| compléments ≤ 50 % du restant (tout) | +5086 | +4775 | +311 | 1301 | 0.182 | +311 [+0.20 ; +4.09] | -277 [-3.68 ; -0.21] | 12 / 12 | 6 | 949 | 87 % |
| compléments ≤ 75 % du restant (tout) | +5232 | +4775 | +457 | 1921 | 0.183 | +457 [+0.30 ; +5.93] | -131 [-1.78 ; -0.08] | 12 / 12 | 6 | 944 | 87 % |
| compléments ≤ 100 % du restant (tout) | +5363 | +4775 | +588 | 2520 | 0.183 | +588 [+0.44 ; +7.80] | +0 [+0.00 ; +0.00] | 12 / 12 | 6 | 939 | 86 % |

## 3. Sensibilité aux frais et à la latence (livrable 7) — tout l'échantillon

| Hypothèse | D ($) | B0 ($) | B0 − D ($) | IC 90 % / signal |
|---|---|---|---|---|
| frais normaux, 164 ms | +4775 | +5363 | +588 | [+0.45 ; +7.61] |
| frais × 1,5 | +4533 | +5070 | +537 | [+0.23 ; +7.12] |
| frais × 2 | +4265 | +4796 | +530 | [+0.27 ; +7.03] |
| latence 250 ms | +4130 | +4301 | +171 | [-1.90 ; +4.64] |
| latence 500 ms | +3397 | +3705 | +309 | [-0.36 ; +4.69] |

## 4. Verdict sur les cycles de test (livrable 8) — correction de Bonferroni pour 7 comparaisons (IC à 98.6 %)

| Comparaison (test) | Écart moyen / signal | IC 90 % simple | IC corrigé | Verdict |
|---|---|---|---|---|
| B0 − D | +7.05 $ | [+0.92 ; +14.44] | [-0.68 ; +17.97] | positif non corrigé seulement |
| B1≥25$ − D | +3.37 $ | [+1.13 ; +5.83] | [+0.18 ; +7.19] | positif (corrigé) |
| B2 P≥25$ m≥0.20 − D | +5.74 $ | [-0.14 ; +12.88] | [-0.96 ; +16.74] | non démontré |
| H800 25 % − D | +1.86 $ | [+0.23 ; +3.79] | [-0.16 ; +4.75] | positif non corrigé seulement |
| H800 50 % − D | +3.73 $ | [+0.50 ; +7.73] | [-0.21 ; +9.68] | positif non corrigé seulement |
| H800 75 % − D | +5.48 $ | [+0.81 ; +11.23] | [-0.39 ; +13.70] | positif non corrigé seulement |
| H800 100 % − D | +7.05 $ | [+0.82 ; +14.46] | [-0.65 ; +17.56] | positif non corrigé seulement |

Les « cycles nouveaux » ici sont la 2e moitié de la journée. La vraie validation reste le fantôme R4 vivant (cycles postérieurs au 11.10 15:30 UTC), dont chaque tentative est enregistrée, puis la période réservée du 13.10.

## Limites
- Une journée ; ~15 cycles de test ; gains concentrés.
- Modèle recalculé hors ligne (fidèle à ±0,005 pour ~3/4 des signaux).
- Reconstruction H800 depuis R4 vivant : approximative quand un fill de R4 a été limité par le budget (quantité réellement disponible inconnue au-delà).
