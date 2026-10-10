# BOT95 META-ROUTER — étude (aucun routeur actif)

924 cycles BTC réglés : 07.10 08:00 → 10.10 13:25. Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · inédit 36 (après).

Achat au seul meilleur vendeur, quantité affichée, frais compris, 50 $ maximum, une décision par cycle ; cycles sans achat = 0 $. Jackpot = gain ≥ 4 × la mise.

## Étape 1 — Complémentarité

### Chaque stratégie seule

**apprentissage**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| V2-D perp 120-269 s | 455 | 215 | 26 % | **+1 678 $** | −1 379 $ | 22 | +6 537 $ | 26 (+4 895 $) |
| Zone 30 + modèle monte | 455 | 51 | 39 % | **+1 734 $** | −146 $ | 6 | +1 195 $ | 12 (+1 664 $) |
| V2-G jury des bourses | 455 | 294 | 21 % | **+234 $** | −1 028 $ | 22 | +7 269 $ | 28 (+4 218 $) |
| V2-F original | 455 | 339 | 23 % | **+593 $** | −1 920 $ | 25 | +10 187 $ | 26 (+4 589 $) |
| V2-F 0,01 % | 455 | 236 | 40 % | **+2 209 $** | −293 $ | 6 | +5 921 $ | 16 (+1 527 $) |
| V2-F miroir 1 s | 455 | 207 | 26 % | **+1 621 $** | −840 $ | 14 | +5 297 $ | 21 (+3 810 $) |

**validation**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| V2-D perp 120-269 s | 433 | 287 | 22 % | **−845 $** | −1 863 $ | 12 | +10 682 $ | 18 (+3 682 $) |
| Zone 30 + modèle monte | 433 | 62 | 37 % | **+796 $** | −230 $ | 5 | +1 869 $ | 15 (+1 394 $) |
| V2-G jury des bourses | 433 | 346 | 21 % | **+1 421 $** | −1 227 $ | 18 | +11 908 $ | 27 (+6 193 $) |
| V2-F original | 433 | 379 | 21 % | **−711 $** | −2 485 $ | 19 | +13 616 $ | 21 (+4 711 $) |
| V2-F 0,01 % | 433 | 231 | 35 % | **+1 508 $** | −658 $ | 9 | +6 976 $ | 13 (+2 398 $) |
| V2-F miroir 1 s | 433 | 174 | 18 % | **−109 $** | −903 $ | 13 | +6 047 $ | 9 (+2 676 $) |

**inédit**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| V2-D perp 120-269 s | 36 | 35 | 11 % | **−882 $** | −962 $ | 10 | +1 476 $ | 1 (+56 $) |
| Zone 30 + modèle monte | 36 | 4 | 0 % | **−137 $** | −137 $ | 4 | +129 $ | 0 (+0 $) |
| V2-G jury des bourses | 36 | 36 | 14 % | **−374 $** | −573 $ | 10 | +1 138 $ | 1 (+154 $) |
| V2-F original | 36 | 36 | 17 % | **−971 $** | −1 052 $ | 10 | +1 250 $ | 0 (+0 $) |
| V2-F 0,01 % | 36 | 25 | 24 % | **−156 $** | −231 $ | 7 | +559 $ | 0 (+0 $) |
| V2-F miroir 1 s | 36 | 10 | 20 % | **−137 $** | −257 $ | 5 | +340 $ | 0 (+0 $) |

### Chevauchements (toute la période) : cycles achetés par les deux · même côté · pertes communes

| | V2-D | Zone+monte | V2-G | V2-F | V2-F 0,01 | Miroir |
|---|---|---|---|---|---|---|
| V2-D | **537** | 102 · 96 · 60 | 493 · 482 · 373 | 533 · 530 · 408 | 356 · 325 · 223 | 296 · 295 · 221 |
| Zone+monte | 102 · 96 · 60 | **117** | 116 · 109 · 68 | 117 · 111 · 69 | 113 · 106 · 66 | 65 · 63 · 40 |
| V2-G | 493 · 482 · 373 | 116 · 109 · 68 | **676** | 675 · 656 · 517 | 452 · 398 · 278 | 362 · 355 · 275 |
| V2-F | 533 · 530 · 408 | 117 · 111 · 69 | 675 · 656 · 517 | **754** | 479 · 423 · 289 | 391 · 391 · 303 |
| V2-F 0,01 | 356 · 325 · 223 | 113 · 106 · 66 | 452 · 398 · 278 | 479 · 423 · 289 | **492** | 258 · 232 · 158 |
| Miroir | 296 · 295 · 221 | 65 · 63 · 40 | 362 · 355 · 275 | 391 · 391 · 303 | 258 · 232 · 158 | **391** |

### Gagnants exclusifs et jackpots (toute la période)

| Stratégie | Gagnants | dont exclusifs (aucune autre ne gagne ce cycle) | Gain des exclusifs | Jackpots | dont exclusifs |
|---|---|---|---|---|---|
| V2-D perp 120-269 s | 123 | 1 | +203 $ | 45 | 9 |
| Zone 30 + modèle monte | 43 | 1 | +69 $ | 27 | 9 |
| V2-G jury des bourses | 141 | 0 | +0 $ | 56 | 6 |
| V2-F original | 164 | 3 | +291 $ | 47 | 3 |
| V2-F 0,01 % | 183 | 47 | +1 395 $ | 29 | 0 |
| V2-F miroir 1 s | 88 | 0 | +0 $ | 30 | 0 |

### Corrélation des résultats par cycle (cycles sans achat = 0)

| | V2-D | Zone+monte | V2-G | V2-F | V2-F 0,01 | Miroir |
|---|---|---|---|---|---|---|
| V2-D | +1.00 | +0.33 | +0.67 | +0.73 | +0.44 | +0.58 |
| Zone+monte | +0.33 | +1.00 | +0.41 | +0.32 | +0.39 | +0.28 |
| V2-G | +0.67 | +0.41 | +1.00 | +0.77 | +0.53 | +0.60 |
| V2-F | +0.73 | +0.32 | +0.77 | +1.00 | +0.52 | +0.80 |
| V2-F 0,01 | +0.44 | +0.39 | +0.53 | +0.52 | +1.00 | +0.41 |
| Miroir | +0.58 | +0.28 | +0.60 | +0.80 | +0.41 | +1.00 |

## Étape 2 — Régimes (mesurés AVANT le début du cycle)

- Volatilité : écart type des variations du perp sur les 5 minutes d'avant ; calme < 2 $/s, agité ≥ 2 $/s (seuil du modèle E, pas réoptimisé).
- Directionnel / oscillant : efficacité du mouvement sur les 15 minutes d'avant (|déplacement net| / somme des mouvements minute par minute) ; seuil = médiane de l'apprentissage (0.23).
- Transmission Chainlink : nombre de nouvelles valeurs Chainlink reçues par minute sur les 10 minutes d'avant ; seuil = médiane de l'apprentissage (46.3 par minute).
- Blocs horaires UTC fixes : 00-06, 06-12, 12-18, 18-24 (heure suisse = UTC + 2).

Chaque case : résultat net (achats). Colonnes « app. » = apprentissage, « hors app. » = validation + inédit.

### Volatilité

| Stratégie | agité app. | agité hors app. | calme app. | calme hors app. |
|---|---|---|---|---|
| *cycles* | 430 | 296 | 21 | 158 |
| V2-D perp 120-269 s | +2 188 $ (195) | −498 $ (178) | −629 $ (19) | −1 081 $ (135) |
| Zone 30 + modèle monte | +1 773 $ (48) | +1 143 $ (38) | −2 $ (2) | −402 $ (26) |
| V2-G jury des bourses | +496 $ (275) | +1 070 $ (222) | −315 $ (17) | +75 $ (148) |
| V2-F original | +1 073 $ (316) | −215 $ (248) | −485 $ (21) | −1 181 $ (154) |
| V2-F 0,01 % | +2 304 $ (223) | +1 219 $ (148) | −80 $ (12) | +178 $ (102) |
| V2-F miroir 1 s | +1 846 $ (193) | +255 $ (128) | −230 $ (12) | −385 $ (47) |

### Tendance

| Stratégie | directionnel app. | directionnel hors app. | oscillant app. | oscillant hors app. |
|---|---|---|---|---|
| *cycles* | 221 | 239 | 221 | 200 |
| V2-D perp 120-269 s | +793 $ (98) | −1 184 $ (169) | +887 $ (112) | −272 $ (140) |
| Zone 30 + modèle monte | +458 $ (27) | +756 $ (29) | +1 313 $ (23) | −94 $ (35) |
| V2-G jury des bourses | −42 $ (150) | +233 $ (201) | +346 $ (135) | +1 207 $ (161) |
| V2-F original | +611 $ (171) | −1 552 $ (216) | +202 $ (158) | +367 $ (176) |
| V2-F 0,01 % | +1 730 $ (118) | −77 $ (135) | +542 $ (112) | +1 487 $ (113) |
| V2-F miroir 1 s | +823 $ (107) | −765 $ (88) | +861 $ (94) | +733 $ (79) |

### Transmission Chainlink

| Stratégie | Chainlink lent app. | Chainlink lent hors app. | Chainlink rapide app. | Chainlink rapide hors app. |
|---|---|---|---|---|
| *cycles* | 218 | 195 | 229 | 256 |
| V2-D perp 120-269 s | +946 $ (80) | −166 $ (117) | +726 $ (131) | −1 394 $ (196) |
| Zone 30 + modèle monte | +541 $ (24) | +480 $ (31) | +1 230 $ (26) | +232 $ (34) |
| V2-G jury des bourses | +68 $ (138) | +1 146 $ (147) | +174 $ (152) | +275 $ (222) |
| V2-F original | +334 $ (151) | −134 $ (164) | +366 $ (183) | −1 211 $ (236) |
| V2-F 0,01 % | +554 $ (109) | +1 169 $ (105) | +1 738 $ (123) | +341 $ (146) |
| V2-F miroir 1 s | +769 $ (99) | −461 $ (83) | +960 $ (103) | +537 $ (91) |

### Bloc horaire

| Stratégie | 00-06 UTC app. | 00-06 UTC hors app. | 06-12 UTC app. | 06-12 UTC hors app. | 12-18 UTC app. | 12-18 UTC hors app. | 18-24 UTC app. | 18-24 UTC hors app. |
|---|---|---|---|---|---|---|---|---|
| *cycles* | 72 | 143 | 144 | 137 | 143 | 70 | 96 | 119 |
| V2-D perp 120-269 s | +131 $ (40) | −201 $ (110) | +1 351 $ (79) | −1 364 $ (110) | +135 $ (37) | −85 $ (21) | +62 $ (59) | −76 $ (81) |
| Zone 30 + modèle monte | +158 $ (8) | +26 $ (20) | +728 $ (26) | +6 $ (24) | +384 $ (7) | +4 $ (4) | +463 $ (10) | +623 $ (18) |
| V2-G jury des bourses | +364 $ (49) | +293 $ (123) | +394 $ (98) | +112 $ (124) | −564 $ (80) | −210 $ (38) | +41 $ (67) | +853 $ (97) |
| V2-F original | −14 $ (59) | −48 $ (131) | +930 $ (115) | −1 032 $ (130) | −523 $ (88) | −409 $ (43) | +200 $ (77) | −193 $ (111) |
| V2-F 0,01 % | +308 $ (39) | −169 $ (80) | +998 $ (81) | +244 $ (86) | +577 $ (66) | +504 $ (25) | +325 $ (50) | +774 $ (65) |
| V2-F miroir 1 s | +125 $ (33) | +265 $ (55) | +1 433 $ (71) | −566 $ (53) | −474 $ (59) | +34 $ (27) | +536 $ (44) | +22 $ (49) |

## Étape 3 — Routeurs (règles figées sur l'apprentissage, jugées sur validation et inédit)

R1 et R2 : dans chaque case, la stratégie au meilleur résultat d'apprentissage (au moins 10 achats), « aucun achat » si aucune n'y gagne ; case trop maigre → choix de R1 (pour R2) ou de R0. Les fantômes qui achètent au même moment ne cumulent rien : une seule enveloppe de 50 $ par cycle ; dans le portefeuille, chaque achat ne prend que la quantité affichée laissée par les achats précédents au même prix.

**apprentissage**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| R0 — meilleure stratégie fixe de l'apprentissage (V2-F 0,01 %) | 455 | 236 | 40 % | **+2 209 $** | −293 $ | 6 | +5 921 $ | 16 (+1 527 $) |
| R1 — choix selon volatilité et tendance | 455 | 140 | 44 % | **+2 967 $** | −280 $ | 7 | +3 388 $ | 18 (+2 125 $) |
| R2 — R1 + bloc horaire | 455 | 204 | 34 % | **+4 504 $** | −449 $ | 12 | +5 438 $ | 25 (+5 250 $) |
| R3 — portefeuille fixe des 6 (8,33 $ chacune, 50 $ au total) | 455 | 350 | 27 % | **+2 233 $** | −836 $ | 17 | +7 840 $ | 29 (+4 879 $) |

**validation**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| R0 — meilleure stratégie fixe de l'apprentissage (V2-F 0,01 %) | 433 | 231 | 35 % | **+1 508 $** | −658 $ | 9 | +6 976 $ | 13 (+2 398 $) |
| R1 — choix selon volatilité et tendance | 433 | 110 | 37 % | **+391 $** | −446 $ | 8 | +3 152 $ | 6 (+268 $) |
| R2 — R1 + bloc horaire | 433 | 155 | 27 % | **+182 $** | −888 $ | 13 | +4 950 $ | 9 (+1 917 $) |
| R3 — portefeuille fixe des 6 (8,33 $ chacune, 50 $ au total) | 433 | 386 | 23 % | **+603 $** | −1 059 $ | 19 | +10 300 $ | 21 (+4 013 $) |

**inédit**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| R0 — meilleure stratégie fixe de l'apprentissage (V2-F 0,01 %) | 36 | 25 | 24 % | **−156 $** | −231 $ | 7 | +559 $ | 0 (+0 $) |
| R1 — choix selon volatilité et tendance | 36 | 2 | 0 % | **−65 $** | −65 $ | 2 | +62 $ | 0 (+0 $) |
| R2 — R1 + bloc horaire | 36 | 2 | 0 % | **−65 $** | −65 $ | 2 | +62 $ | 0 (+0 $) |
| R3 — portefeuille fixe des 6 (8,33 $ chacune, 50 $ au total) | 36 | 36 | 14 % | **−506 $** | −572 $ | 10 | +1 029 $ | 1 (+91 $) |

**hors apprentissage (validation + inédit)**

| Politique | Cycles | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots (gain) |
|---|---|---|---|---|---|---|---|---|
| R0 — meilleure stratégie fixe de l'apprentissage (V2-F 0,01 %) | 469 | 256 | 34 % | **+1 352 $** | −829 $ | 9 | +7 535 $ | 13 (+2 398 $) |
| R1 — choix selon volatilité et tendance | 469 | 112 | 37 % | **+326 $** | −446 $ | 10 | +3 215 $ | 6 (+268 $) |
| R2 — R1 + bloc horaire | 469 | 157 | 27 % | **+117 $** | −954 $ | 13 | +5 012 $ | 9 (+1 917 $) |
| R3 — portefeuille fixe des 6 (8,33 $ chacune, 50 $ au total) | 469 | 422 | 23 % | **+97 $** | −1 334 $ | 19 | +11 329 $ | 22 (+4 104 $) |

### Ce que les routeurs ont choisi (sur l'apprentissage)

| Case R1 (volatilité, tendance) | Choix | Cycles app. | Cycles hors app. |
|---|---|---|---|
| agité / directionnel | V2-F 0,01 % | 210 | 153 |
| agité / oscillant | Zone 30 + modèle monte | 210 | 123 |
| agité / None | V2-F 0,01 % | 10 | 20 |
| calme / directionnel | aucun achat | 11 | 81 |
| calme / oscillant | aucun achat | 10 | 74 |
| calme / None | V2-F 0,01 % | 0 | 3 |
| None / directionnel | V2-F 0,01 % | 0 | 5 |
| None / oscillant | V2-F 0,01 % | 1 | 3 |
| None / None | V2-F 0,01 % | 3 | 7 |

| Case R2 | Choix | Cycles app. | Cycles hors app. |
|---|---|---|---|
| agité / directionnel / 00-06 UTC | V2-F 0,01 % | 38 | 47 |
| agité / directionnel / 06-12 UTC | V2-F original | 69 | 38 |
| agité / directionnel / 12-18 UTC | V2-F 0,01 % | 64 | 26 |
| agité / directionnel / 18-24 UTC | aucun achat | 39 | 42 |
| agité / oscillant / 00-06 UTC | V2-G jury des bourses | 34 | 31 |
| agité / oscillant / 06-12 UTC | Zone 30 + modèle monte | 68 | 29 |
| agité / oscillant / 12-18 UTC | V2-F 0,01 % | 70 | 28 |
| agité / oscillant / 18-24 UTC | V2-F original | 38 | 35 |
| calme / directionnel / 00-06 UTC | aucun achat | 0 | 29 |
| calme / directionnel / 06-12 UTC | aucun achat | 2 | 35 |
| calme / directionnel / 18-24 UTC | aucun achat | 9 | 17 |
| calme / oscillant / 00-06 UTC | aucun achat | 0 | 31 |
| calme / oscillant / 06-12 UTC | aucun achat | 2 | 30 |
| calme / oscillant / 18-24 UTC | aucun achat | 8 | 13 |

### Le dynamique bat-il le fixe ? Différence hors apprentissage, incertitude par blocs d'une heure

| Comparaison | Différence | Intervalle à 90 % | Probabilité que ce soit ≤ 0 |
|---|---|---|---|
| R1 − R0 | −1 027 $ | [−2 658 $ ; +536 $] | 85 % |
| R2 − R0 | −1 236 $ | [−2 712 $ ; +215 $] | 92 % |
| R1 − R3 | +229 $ | [−1 715 $ ; +2 068 $] | 42 % |
| R2 − R3 | +20 $ | [−1 634 $ ; +1 623 $] | 50 % |
| R3 − R0 | −1 255 $ | [−2 658 $ ; +265 $] | 91 % |

Pour mesurer l'illusion : R1 construit en regardant les cycles hors apprentissage eux-mêmes ferait +2 764 $ sur ces cycles — c'est ce qu'on obtient quand on optimise sur les données qu'on juge.
