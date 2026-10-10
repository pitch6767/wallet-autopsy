# BOT95 V3 — Expérience 003 : modèle logistique simple pré-enregistré

928 cycles BTC 5 min réglés (07.10 08:00 → 10.10 13:45, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 40 cycles seulement (après 10.10 10:25) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.

**Pré-enregistrement** (fixé avant de lancer le calcul) : 10 variables connues à la décision, standardisées sur l'apprentissage, régression logistique L2 (λ = 1, non réglé), règle d'achat « probabilité estimée − prix − frais > 0 », entraînement sur l'apprentissage SEULEMENT, jugement sur validation puis inédit. Deux jeux de candidats déclarés d'avance : signaux V2-F original (O8) et premiers désaccords ≥ 0,20 (désaccord 20).

Variables : 1. écart modèle − vendeur ; 2. prix vendeur ; 3. log temps restant ; 4. log(1 + taille affichée) ; 5. écart acheteur-vendeur (c) ; 6. perp 5 s / (vol·√5) ; 7. Coinbase 3 s (10 $) ; 8. log volatilité 5 min ; 9. âge de l'épisode (s, ≤ 5) ; 10. nuit.

## Candidats : V2-F original (O8)

759 candidats (app. 339 · valid. 380 · inédit 40). Valeurs manquantes remplacées par la moyenne d'apprentissage : perp 5 s / (vol·√5) 56, log volatilité 5 min 12.

### Coefficients (variables standardisées, apprentissage)

| Variable | Coefficient |
|---|---|
| constante | -1.322 |
| écart modèle − vendeur | +0.123 |
| prix vendeur | +0.542 |
| log temps restant | +0.179 |
| log(1 + taille affichée) | -0.240 |
| écart acheteur-vendeur (c) | -0.060 |
| perp 5 s / (vol·√5) | -0.159 |
| Coinbase 3 s (10 $) | +0.170 |
| log volatilité 5 min | +0.059 |
| âge de l'épisode (s, ≤ 5) | +0.067 |
| nuit | -0.328 |

### Qualité de prévision (score de Brier, plus bas = mieux ; « prix » = prendre le prix vendeur comme probabilité ; « modèle du bot » = probabilité du modèle 0,08 %)

| Période | Candidats | Taux de gain réel | Brier logistique | Brier prix | Brier modèle du bot | Proba logistique moyenne |
|---|---|---|---|---|---|---|
| apprentissage | 339 | 23 % | 0.1602 | 0.1695 | 0.2004 | 0.233 |
| validation | 380 | 21 % | 0.1574 | 0.1521 | 0.2010 | 0.198 |
| inédit | 40 | 20 % | 0.1732 | 0.1548 | 0.2267 | 0.328 |

### Résultat en exécution réaliste

**Délai 0 s**

| Période · politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage · tout prendre (339) | 339 | 23 % | **+593 $** | +1,75 $ | +163 $ | −662 $ | −1 389 $ | −2 908 $ | −1 920 $ | 1,07 | [−2 284 $ ; +3 780 $] |
| apprentissage · filtre logistique (212 retenus) | 212 | 27 % | **+2 297 $** | +10,84 $ | +1 867 $ | +1 042 $ | +315 $ | −1 051 $ | −749 $ | 1,57 | [−84 $ ; +4 961 $] |
| apprentissage · rejetés par le filtre | 127 | 17 % | **−1 704 $** | −13,42 $ | −2 036 $ | −2 537 $ | −2 907 $ | −3 661 $ | −2 006 $ | 0,61 | [−2 902 $ ; −502 $] |
| validation · tout prendre (380) | 379 | 21 % | **−711 $** | −1,88 $ | −1 283 $ | −2 233 $ | −2 895 $ | −4 140 $ | −2 485 $ | 0,94 | [−3 379 $ ; +2 082 $] |
| validation · filtre logistique (157 retenus) | 157 | 18 % | **+22 $** | +0,14 $ | −526 $ | −1 138 $ | −1 576 $ | −2 356 $ | −920 $ | 1,01 | [−1 436 $ ; +1 547 $] |
| validation · rejetés par le filtre | 222 | 23 % | **−733 $** | −3,30 $ | −1 305 $ | −2 038 $ | −2 520 $ | −3 594 $ | −2 237 $ | 0,90 | [−2 987 $ ; +1 802 $] |
| inédit · tout prendre (40) | 40 | 20 % | **−851 $** | −21,27 $ | −971 $ | −1 149 $ | −1 239 $ | −1 271 $ | −1 054 $ | 0,33 | [−1 290 $ ; −447 $] |
| inédit · filtre logistique (30 retenus) | 30 | 20 % | **−669 $** | −22,31 $ | −728 $ | −818 $ | −849 $ | −845 $ | −671 $ | 0,21 | [−1 007 $ ; −331 $] |
| inédit · rejetés par le filtre | 10 | 20 % | **−182 $** | −18,16 $ | −301 $ | −369 $ | −264 $ | −0 $ | −421 $ | 0,57 | [−617 $ ; +254 $] |

**Délai 0,5 s**

| Période · politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage · tout prendre (339) | 208 | 19 % | **+424 $** | +2,04 $ | −208 $ | −1 061 $ | −1 826 $ | −3 350 $ | −1 583 $ | 1,07 | [−2 322 $ ; +3 416 $] |
| apprentissage · filtre logistique (212 retenus) | 112 | 24 % | **+2 027 $** | +18,10 $ | +1 394 $ | +542 $ | −185 $ | −1 339 $ | −577 $ | 1,67 | [−7 $ ; +4 261 $] |
| apprentissage · rejetés par le filtre | 96 | 12 % | **−1 603 $** | −16,69 $ | −2 004 $ | −2 592 $ | −2 975 $ | −3 485 $ | −2 168 $ | 0,54 | [−2 873 $ ; −269 $] |
| validation · tout prendre (380) | 276 | 20 % | **−1 945 $** | −7,05 $ | −2 517 $ | −3 192 $ | −3 714 $ | −4 829 $ | −3 204 $ | 0,79 | [−4 495 $ ; +921 $] |
| validation · filtre logistique (157 retenus) | 96 | 18 % | **−1 568 $** | −16,33 $ | −1 912 $ | −2 270 $ | −2 549 $ | −3 028 $ | −1 772 $ | 0,50 | [−2 665 $ ; −493 $] |
| validation · rejetés par le filtre | 180 | 22 % | **−378 $** | −2,10 $ | −949 $ | −1 561 $ | −2 043 $ | −3 091 $ | −1 613 $ | 0,94 | [−2 606 $ ; +2 216 $] |
| inédit · tout prendre (40) | 24 | 8 % | **−939 $** | −39,14 $ | −973 $ | −981 $ | −944 $ | −738 $ | −951 $ | 0,05 | [−1 263 $ ; −664 $] |
| inédit · filtre logistique (30 retenus) | 15 | 7 % | **−579 $** | −38,61 $ | −613 $ | −575 $ | −525 $ | −264 $ | −579 $ | 0,05 | [−696 $ ; −462 $] |
| inédit · rejetés par le filtre | 9 | 11 % | **−360 $** | −40,01 $ | −371 $ | −316 $ | −211 $ | −0 $ | −371 $ | 0,03 | [−632 $ ; −88 $] |

## Candidats : désaccord 20 (premier franchissement ≥ 0,20)

773 candidats (app. 348 · valid. 385 · inédit 40). Valeurs manquantes remplacées par la moyenne d'apprentissage : perp 5 s / (vol·√5) 99, Coinbase 3 s (10 $) 76, log volatilité 5 min 12.

### Coefficients (variables standardisées, apprentissage)

| Variable | Coefficient |
|---|---|
| constante | -1.343 |
| écart modèle − vendeur | +0.226 |
| prix vendeur | +0.469 |
| log temps restant | +0.217 |
| log(1 + taille affichée) | -0.278 |
| écart acheteur-vendeur (c) | -0.139 |
| perp 5 s / (vol·√5) | -0.186 |
| Coinbase 3 s (10 $) | +0.217 |
| log volatilité 5 min | +0.032 |
| âge de l'épisode (s, ≤ 5) | +0.000 |
| nuit | -0.305 |

### Qualité de prévision (score de Brier, plus bas = mieux ; « prix » = prendre le prix vendeur comme probabilité ; « modèle du bot » = probabilité du modèle 0,08 %)

| Période | Candidats | Taux de gain réel | Brier logistique | Brier prix | Brier modèle du bot | Proba logistique moyenne |
|---|---|---|---|---|---|---|
| apprentissage | 348 | 23 % | 0.1599 | 0.1703 | 0.1996 | 0.230 |
| validation | 385 | 21 % | 0.1638 | 0.1538 | 0.2002 | 0.196 |
| inédit | 40 | 20 % | 0.1938 | 0.1618 | 0.2325 | 0.333 |

### Résultat en exécution réaliste

**Délai 0 s**

| Période · politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage · tout prendre (348) | 348 | 23 % | **+352 $** | +1,01 $ | −205 $ | −1 154 $ | −1 947 $ | −3 519 $ | −2 517 $ | 1,04 | [−2 738 $ ; +3 945 $] |
| apprentissage · filtre logistique (210 retenus) | 210 | 28 % | **+2 746 $** | +13,07 $ | +2 189 $ | +1 240 $ | +447 $ | −941 $ | −828 $ | 1,76 | [+139 $ ; +5 654 $] |
| apprentissage · rejetés par le filtre | 138 | 16 % | **−2 394 $** | −17,35 $ | −2 725 $ | −3 199 $ | −3 529 $ | −4 213 $ | −2 452 $ | 0,52 | [−3 860 $ ; −858 $] |
| validation · tout prendre (385) | 385 | 21 % | **−228 $** | −0,59 $ | −799 $ | −1 748 $ | −2 411 $ | −3 612 $ | −2 885 $ | 0,98 | [−3 122 $ ; +2 823 $] |
| validation · filtre logistique (150 retenus) | 150 | 14 % | **−816 $** | −5,44 $ | −1 147 $ | −1 669 $ | −2 051 $ | −2 739 $ | −902 $ | 0,76 | [−1 901 $ ; +372 $] |
| validation · rejetés par le filtre | 235 | 25 % | **+588 $** | +2,50 $ | +16 $ | −933 $ | −1 505 $ | −2 574 $ | −1 983 $ | 1,07 | [−2 147 $ ; +3 520 $] |
| inédit · tout prendre (40) | 40 | 20 % | **−695 $** | −17,36 $ | −880 $ | −1 139 $ | −1 252 $ | −1 283 $ | −817 $ | 0,46 | [−1 212 $ ; −177 $] |
| inédit · filtre logistique (27 retenus) | 27 | 15 % | **−679 $** | −25,16 $ | −738 $ | −808 $ | −811 $ | −785 $ | −681 $ | 0,16 | [−911 $ ; −435 $] |
| inédit · rejetés par le filtre | 13 | 31 % | **−15 $** | −1,17 $ | −200 $ | −460 $ | −421 $ | −158 $ | −211 $ | 0,97 | [−360 $ ; +257 $] |

**Délai 0,5 s**

| Période · politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage · tout prendre (348) | 213 | 20 % | **+854 $** | +4,01 $ | −93 $ | −1 111 $ | −1 876 $ | −3 435 $ | −1 864 $ | 1,13 | [−2 301 $ ; +4 206 $] |
| apprentissage · filtre logistique (210 retenus) | 110 | 25 % | **+2 830 $** | +25,73 $ | +1 883 $ | +865 $ | +138 $ | −1 115 $ | −785 $ | 2,00 | [+374 $ ; +5 671 $] |
| apprentissage · rejetés par le filtre | 103 | 14 % | **−1 976 $** | −19,19 $ | −2 378 $ | −2 916 $ | −3 227 $ | −3 766 $ | −2 390 $ | 0,49 | [−3 257 $ ; −691 $] |
| validation · tout prendre (385) | 292 | 21 % | **−776 $** | −2,66 $ | −1 348 $ | −2 297 $ | −2 972 $ | −4 307 $ | −2 790 $ | 0,92 | [−3 703 $ ; +2 348 $] |
| validation · filtre logistique (150 retenus) | 97 | 15 % | **−1 266 $** | −13,06 $ | −1 610 $ | −2 183 $ | −2 540 $ | −3 022 $ | −1 274 $ | 0,59 | [−2 448 $ ; +62 $] |
| validation · rejetés par le filtre | 195 | 24 % | **+491 $** | +2,52 $ | −81 $ | −1 030 $ | −1 642 $ | −2 770 $ | −1 715 $ | 1,07 | [−2 095 $ ; +3 272 $] |
| inédit · tout prendre (40) | 27 | 7 % | **−874 $** | −32,36 $ | −1 059 $ | −1 090 $ | −1 072 $ | −896 $ | −874 $ | 0,20 | [−1 228 $ ; −524 $] |
| inédit · filtre logistique (27 retenus) | 17 | 6 % | **−635 $** | −37,36 $ | −669 $ | −650 $ | −604 $ | −370 $ | −635 $ | 0,05 | [−801 $ ; −469 $] |
| inédit · rejetés par le filtre | 10 | 10 % | **−239 $** | −23,88 $ | −424 $ | −369 $ | −264 $ | +0 $ | −266 $ | 0,44 | [−427 $ ; −55 $] |
