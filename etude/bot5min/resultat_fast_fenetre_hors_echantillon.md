# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 15.10.2026 17:35 UTC. 744 cycles de Dublin, HORS ÉCHANTILLON. Paramètres fixés avant mesure : trajet simple 14 ms, calcul 0.2 ms, retard preneur 150 ms.

Données exclues ou douteuses : cycles avec carnets Binance/Bybit 744, cycles avec trou de carnet ou de transactions (exclus des études de carnets) 729

## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)

| Cause | Nombre | Part |
|---|---|---|
| consommé | 60991 | 24 % |
| mixte | 2479 | 1 % |
| retiré | 133330 | 53 % |
| déplacé | 37925 | 15 % |
| indéterminé | 19143 | 8 % |

« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.

## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)

Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. « Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.

**sans retard preneur (référence théorique)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 98 % (204001) | 98 % (48724) | 99 % (140056) | 99 % (2175) | 100 % |
| 100 ms | 98 % (201412) | 98 % (49217) | 99 % (138130) | 99 % (2126) | 100 % |
| 150 ms | 99 % (199710) | 99 % (49407) | 99 % (136501) | 100 % (2117) | 100 % |
| 200 ms | 99 % (197593) | 99 % (49318) | 99 % (134731) | 100 % (2105) | 100 % |
| 300 ms | 99 % (192678) | 100 % (48617) | 100 % (130908) | 100 % (2083) | 100 % |
| 500 ms | 100 % (184240) | 100 % (46957) | 100 % (124375) | 100 % (2030) | 100 % |

**retard 50 ms (réglage du 17.08 au 04.09)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (204001) | 0 % (48724) | 0 % (140056) | 0 % (2175) | 0 % |
| 100 ms | 95 % (201412) | 94 % (49217) | 96 % (138130) | 98 % (2126) | 78 % |
| 150 ms | 97 % (199710) | 96 % (49407) | 97 % (136501) | 98 % (2117) | 88 % |
| 200 ms | 98 % (197593) | 98 % (49318) | 98 % (134731) | 99 % (2105) | 100 % |
| 300 ms | 98 % (192678) | 99 % (48617) | 99 % (130908) | 99 % (2083) | 100 % |
| 500 ms | 99 % (184240) | 99 % (46957) | 99 % (124375) | 99 % (2030) | 100 % |

**retard 150 ms (réglage actuel)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (204001) | 0 % (48724) | 0 % (140056) | 0 % (2175) | 0 % |
| 100 ms | 0 % (201412) | 0 % (49217) | 0 % (138130) | 0 % (2126) | 0 % |
| 150 ms | 0 % (199710) | 0 % (49407) | 0 % (136501) | 0 % (2117) | 0 % |
| 200 ms | 94 % (197593) | 92 % (49318) | 95 % (134731) | 97 % (2105) | 33 % |
| 300 ms | 96 % (192678) | 96 % (48617) | 97 % (130908) | 98 % (2083) | 74 % |
| 500 ms | 98 % (184240) | 98 % (46957) | 98 % (124375) | 99 % (2030) | 100 % |

Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple 14 ms + calcul + retard preneur 150 ms ≈ **164 ms**.

## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)

Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède (saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).

| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |
|---|---|---|---|---|---|
| toutes | 213702 | 85416 (40 %) | 103 / 491 / 924 | 71038 (33 %) | 57575 (27 %) |
| consommées | 55377 | 24195 (44 %) | 129 / 493 / 921 | 20747 (37 %) | 16522 (30 %) |
| retirées / déplacées | 155994 | 59937 (38 %) | 95 / 490 / 924 | 49126 (31 %) | 40145 (26 %) |
| mixtes | 2331 | 1284 (55 %) | 167 / 470 / 933 | 1165 (50 %) | 908 (39 %) |

**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin (186019 cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms dans 31 % des cas ; à des instants tirés au hasard (témoin) : 21 %.


C'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.

## 4. Vérification indirecte du retard preneur sur nos marchés

Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = 125494) : p10 / p50 / p90 = 30 / 170 / 654 ms ; jusqu'au 1er retrait (n = 114445) : 7 / 67 / 378 ms. Transactions moins de 150 ms après NOTRE information : 44 %. Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).

## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)

Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).

| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 1036 | 47 | 855 (83 %) | 876 (85 %) | 451 | 1291 |
| M1 V2-F ecart qui grandit | 468 | 92 | 289 (62 %) | 295 (63 %) | 278 | 1150 |
| M1 V2-F incertitude 0,01 % | 269 | 43 | 94 (35 %) | 96 (36 %) | 281 | 664 |
| M1 cohorte A : zone + modele monte | 34 | 5 | 21 (62 %) | 21 (62 %) | 100 | 2109 |
| M1 cohorte B : V2-F corrige 0,015 % | 276 | 43 | 113 (41 %) | 114 (41 %) | 277 | 613 |
| M1 desaccord 20 60-180 s | 446 | 86 | 299 (67 %) | 305 (68 %) | 267 | 1353 |
| M1 desaccord 20 jeton 0,35-0,65 | 45 | 9 | 22 (49 %) | 22 (49 %) | 90 | 252 |
| M1 desaccord 30 | 262 | 64 | 174 (66 %) | 177 (68 %) | 133 | 851 |
| M10 double maker meilleur prix | 30996 | 2201 | 7037 (23 %) | 6856 (22 %) | 221 | 626 |
| M11 zone maker | 162 | 34 | 16 (10 %) | 13 (8 %) | 98 | 297 |
| M2 cotation marge 10 c | 499108 | 1532 | 3659 (1 %) | 3416 (1 %) | 388 | 368 |
| M2 cotation marge 5 c | 316313 | 2087 | 4537 (1 %) | 4133 (1 %) | 386 | 345 |
| M21 maker du favori | 20333 | 1371 | 4132 (20 %) | 3783 (19 %) | 213 | 543 |
| M3 anticipation Chainlink | 103739 | 1908 | 3725 (4 %) | 3266 (3 %) | 372 | 258 |
| M4 retrait toxique | 263151 | 2229 | 5056 (2 %) | 4732 (2 %) | 382 | 477 |
| M4a seul bourses -10 $ | 303090 | 2260 | 4790 (2 %) | 4350 (1 %) | 383 | 396 |
| M4b seul flux agressif | 304749 | 2224 | 4729 (2 %) | 4353 (1 %) | 383 | 420 |
| M4c seul ventes Polymarket | 259882 | 2149 | 5018 (2 %) | 4561 (2 %) | 382 | 421 |
| M5 remplissage attendu | 58570 | 4701 | 9100 (16 %) | 6772 (12 %) | 140 | 205 |
| M6 duree de vie 100 ms | 1033743 | 5626 | 6724 (1 %) | 4546 (0 %) | 368 | 92 |
| M6 duree de vie 1000 ms | 385141 | 2865 | 5753 (1 %) | 4817 (1 %) | 380 | 298 |
| M6 duree de vie 250 ms | 641937 | 4059 | 6414 (1 %) | 4251 (1 %) | 373 | 140 |
| M6 duree de vie 500 ms | 472846 | 3337 | 6129 (1 %) | 4283 (1 %) | 376 | 199 |
| M8 hybride V2-F ecart qui grandit | 467 | 91 | 273 (58 %) | 276 (59 %) | 0 | 211 |
| M8 hybride V2-F incertitude 0,01 % | 268 | 41 | 116 (43 %) | 118 (44 %) | 5 | 178 |
| M8 hybride cohorte A : zone + modele monte | 34 | 4 | 22 (65 %) | 22 (65 %) | 10 | 1293 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 275 | 41 | 132 (48 %) | 133 (48 %) | 6 | 181 |
| M8 hybride desaccord 20 60-180 s | 445 | 86 | 265 (60 %) | 269 (60 %) | 0 | 253 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 45 | 8 | 26 (58 %) | 26 (58 %) | 40 | 242 |
| M8 hybride desaccord 30 | 262 | 61 | 171 (65 %) | 173 (66 %) | 34 | 313 |
| M8b routeur corrige V2-F ecart qui grandit | 467 | 92 | 269 (58 %) | 273 (58 %) | 7 | 281 |
| M8b routeur corrige V2-F incertitude 0,01 % | 268 | 42 | 112 (42 %) | 114 (43 %) | 10 | 193 |
| M8b routeur corrige cohorte A : zone + modele monte | 34 | 4 | 22 (65 %) | 22 (65 %) | 10 | 1293 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 275 | 42 | 129 (47 %) | 130 (47 %) | 13 | 188 |
| M8b routeur corrige desaccord 20 60-180 s | 445 | 86 | 264 (59 %) | 268 (60 %) | 10 | 376 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 45 | 9 | 25 (56 %) | 25 (56 %) | 42 | 234 |
| M8b routeur corrige desaccord 30 | 262 | 63 | 168 (64 %) | 170 (65 %) | 45 | 318 |
| M9 fin de cycle cote acquis | 746 | 117 | 138 (18 %) | 143 (19 %) | 221 | 441 |

Offres remplies et réglées (fichier bot95/rapide_maker.json) :

| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |
|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 513 | 87402 / 88456 | 21629 $ | +2595 $ | +2817 $ | +0.12 | -1.6 / -1.6 / -1.8 / -1.6 |
| M1 V2-F ecart qui grandit | 241 | 59421 / 60368 | 7443 $ | -1691 $ | -1768 $ | -0.23 | -1.3 / -1.7 / -1.3 / -1.2 |
| M1 V2-F incertitude 0,01 % | 131 | 11559 / 11540 | 2034 $ | +936 $ | +941 $ | +0.46 | +0.6 / +1.4 / +6.6 / +7.8 |
| M1 cohorte A : zone + modele monte | 14 | 3464 / 3464 | 450 $ | +106 $ | +106 $ | +0.23 | -2.1 / -1.6 / -0.4 / -4.0 |
| M1 cohorte B : V2-F corrige 0,015 % | 134 | 17429 / 17370 | 2539 $ | -165 $ | -186 $ | -0.06 | -1.1 / -1.0 / -1.0 / -0.5 |
| M1 desaccord 20 60-180 s | 230 | 63889 / 64697 | 7976 $ | -1058 $ | -1124 $ | -0.13 | -1.1 / -1.8 / -1.6 / -1.1 |
| M1 desaccord 20 jeton 0,35-0,65 | 17 | 1384 / 1384 | 500 $ | +477 $ | +477 $ | +0.95 | +17.1 / +16.6 / +17.8 / +15.5 |
| M1 desaccord 30 | 132 | 58528 / 58298 | 4799 $ | -277 $ | -512 $ | -0.06 | -1.1 / -1.5 / -1.4 / +0.6 |
| M10 double maker meilleur prix | 12850 | 128587 / 137681 | 52976 $ | -1344 $ | -686 $ | -0.03 | -1.0 / -1.0 / -0.9 / -1.2 |
| M11 zone maker | 31 | 853 / 866 | 129 $ | -129 $ | -131 $ | -1.00 | -1.7 / -1.6 / -1.2 / -5.2 |
| M2 cotation marge 10 c | 2086 | 166868 / 165585 | 39990 $ | +273 $ | -104 $ | +0.01 | -0.8 / -0.6 / -0.2 / -0.3 |
| M2 cotation marge 5 c | 2345 | 157647 / 155120 | 50874 $ | +1035 $ | +599 $ | +0.02 | -1.3 / -1.3 / -1.1 / -0.9 |
| M21 maker du favori | 2311 | 54668 / 55682 | 34719 $ | -925 $ | -529 $ | -0.03 | -1.1 / -1.1 / -0.9 / -1.1 |
| M3 anticipation Chainlink | 1816 | 136447 / 131205 | 34302 $ | +1850 $ | +1272 $ | +0.05 | +1.6 / +1.2 / +1.3 / +1.4 |
| M4 retrait toxique | 3038 | 168460 / 169834 | 48036 $ | +1163 $ | +1639 $ | +0.02 | -0.5 / -0.3 / -0.1 / -0.1 |
| M4a seul bourses -10 $ | 2620 | 162560 / 161893 | 50358 $ | +2245 $ | +2842 $ | +0.04 | -1.0 / -1.0 / -1.1 / -1.0 |
| M4b seul flux agressif | 2589 | 155947 / 157085 | 48936 $ | -1528 $ | -970 $ | -0.03 | -0.9 / -0.9 / -0.9 / -0.8 |
| M4c seul ventes Polymarket | 2766 | 166088 / 166258 | 48285 $ | -1104 $ | -440 $ | -0.02 | -0.9 / -0.5 / -0.3 / -0.1 |
| M5 remplissage attendu | 4112 | 230577 / 202636 | 71055 $ | -4564 $ | -3660 $ | -0.06 | -1.0 / -1.0 / -1.1 / -1.4 |
| M6 duree de vie 100 ms | 2826 | 243051 / 212936 | 72075 $ | +282 $ | -24 $ | +0.00 | -1.4 / -1.2 / -1.1 / -0.8 |
| M6 duree de vie 1000 ms | 3106 | 205282 / 186017 | 63831 $ | -55 $ | -613 $ | -0.00 | -1.2 / -1.1 / -1.0 / -0.8 |
| M6 duree de vie 250 ms | 2793 | 235322 / 204349 | 71297 $ | -488 $ | -754 $ | -0.01 | -1.3 / -1.1 / -0.9 / -0.8 |
| M6 duree de vie 500 ms | 2910 | 228152 / 196253 | 69349 $ | -1012 $ | -1024 $ | -0.01 | -1.4 / -1.2 / -1.2 / -1.0 |
| M8 hybride V2-F ecart qui grandit | 240 | 42449 / 43074 | 6454 $ | +315 $ | +264 $ | +0.05 | +0.2 / -0.3 / -0.4 / -0.8 |
| M8 hybride V2-F incertitude 0,01 % | 130 | 10496 / 10476 | 2205 $ | +1757 $ | +1762 $ | +0.80 | +2.8 / +3.2 / +9.7 / +11.7 |
| M8 hybride cohorte A : zone + modele monte | 14 | 2535 / 2535 | 316 $ | +240 $ | +240 $ | +0.76 | -2.0 / -0.8 / +1.0 / -2.7 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 133 | 14527 / 14467 | 2542 $ | +956 $ | +935 $ | +0.38 | +0.3 / +1.0 / +1.4 / +2.6 |
| M8 hybride desaccord 20 60-180 s | 229 | 46784 / 47313 | 6802 $ | +773 $ | +730 $ | +0.11 | -0.5 / -1.2 / -1.3 / -1.1 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 17 | 1412 / 1412 | 513 $ | +492 $ | +492 $ | +0.96 | +17.4 / +16.7 / +17.9 / +15.7 |
| M8 hybride desaccord 30 | 132 | 45462 / 45231 | 4051 $ | +1417 $ | +1180 $ | +0.35 | -0.2 / -0.2 / -0.4 / +2.3 |
| M8b routeur corrige V2-F ecart qui grandit | 240 | 42763 / 43432 | 6385 $ | +66 $ | +11 $ | +0.01 | -0.2 / -0.8 / -0.8 / -1.3 |
| M8b routeur corrige V2-F incertitude 0,01 % | 130 | 10280 / 10260 | 2118 $ | +1526 $ | +1530 $ | +0.72 | +2.4 / +3.6 / +9.4 / +11.6 |
| M8b routeur corrige cohorte A : zone + modele monte | 14 | 2535 / 2535 | 316 $ | +240 $ | +240 $ | +0.76 | -2.0 / -0.8 / +1.0 / -2.7 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 133 | 15194 / 15133 | 2505 $ | +724 $ | +703 $ | +0.29 | -0.1 / +1.0 / +0.9 / +2.5 |
| M8b routeur corrige desaccord 20 60-180 s | 229 | 47562 / 48091 | 6787 $ | +725 $ | +682 $ | +0.11 | -0.6 / -1.2 / -1.3 / -1.1 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 17 | 1412 / 1412 | 513 $ | +492 $ | +492 $ | +0.96 | +17.4 / +16.7 / +17.9 / +15.7 |
| M8b routeur corrige desaccord 30 | 132 | 45558 / 45327 | 4051 $ | +1417 $ | +1180 $ | +0.35 | -0.2 / -0.2 / -0.4 / +2.3 |
| M9 fin de cycle cote acquis | 74 | 2189 / 2469 | 2083 $ | +106 $ | +114 $ | +0.05 | +0.6 / +0.8 / +1.6 / -1.5 |

**Par prix d'achat et temps restant (toutes variantes maker, prudent)**

| Prix | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0.00–0.20 | 7370 | 107341 $ | +34022 $ | +0.32 |
| 0.20–0.35 | 17967 | 295902 $ | -16438 $ | -0.06 |
| 0.35–0.50 | 17103 | 346583 $ | -12585 $ | -0.04 |
| 0.50–0.65 | 5490 | 59914 $ | +2992 $ | +0.05 |
| 0.65–1.00 | 3545 | 41484 $ | -123 $ | -0.00 |

| Temps restant à la pose | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0–60 s | 667 | 19680 $ | +7856 $ | +0.40 |
| 60–120 s | 3114 | 83756 $ | -9203 $ | -0.11 |
| 120–180 s | 6661 | 135218 $ | +8718 $ | +0.06 |
| 180–300 s | 41033 | 612570 $ | +497 $ | +0.00 |
(temps restant enregistré seulement depuis la version du 11.10 13:55)


**Intervalle de confiance à 90 % du résultat prudent (rééchantillonnage par cycles)**

- M0 temoin aleatoire : +2595 $ sur 310 cycles, IC 90 % [-772 ; +6394] $
- M1 V2-F ecart qui grandit : -1691 $ sur 241 cycles, IC 90 % [-3699 ; +576] $
- M1 V2-F incertitude 0,01 % : +936 $ sur 131 cycles, IC 90 % [-527 ; +2646] $
- M1 cohorte A : zone + modele monte : +106 $ sur 14 cycles, IC 90 % [-500 ; +1167] $
- M1 cohorte B : V2-F corrige 0,015 % : -165 $ sur 134 cycles, IC 90 % [-1265 ; +1041] $
- M1 desaccord 20 60-180 s : -1058 $ sur 230 cycles, IC 90 % [-3192 ; +1311] $
- M1 desaccord 20 jeton 0,35-0,65 : +477 $ sur 17 cycles, IC 90 % [+95 ; +881] $
- M1 desaccord 30 : -277 $ sur 132 cycles, IC 90 % [-2569 ; +2320] $
- M10 double maker meilleur prix : -1344 $ sur 346 cycles, IC 90 % [-4746 ; +2073] $
- M11 zone maker : -129 $ sur 13 cycles, IC 90 % [-328 ; -1] $
- M2 cotation marge 10 c : +273 $ sur 338 cycles, IC 90 % [-5864 ; +7279] $
- M2 cotation marge 5 c : +1035 $ sur 346 cycles, IC 90 % [-5196 ; +7747] $
- M21 maker du favori : -925 $ sur 334 cycles, IC 90 % [-2555 ; +682] $
- M3 anticipation Chainlink : +1850 $ sur 339 cycles, IC 90 % [-2228 ; +6670] $
- M4 retrait toxique : +1163 $ sur 344 cycles, IC 90 % [-3588 ; +6268] $
- M4a seul bourses -10 $ : +2245 $ sur 345 cycles, IC 90 % [-3799 ; +9358] $
- M4b seul flux agressif : -1528 $ sur 345 cycles, IC 90 % [-6408 ; +4018] $
- M4c seul ventes Polymarket : -1104 $ sur 345 cycles, IC 90 % [-5806 ; +3816] $
- M5 remplissage attendu : -4564 $ sur 346 cycles, IC 90 % [-10602 ; +2157] $
- M6 duree de vie 100 ms : +282 $ sur 344 cycles, IC 90 % [-7974 ; +9075] $
- M6 duree de vie 1000 ms : -55 $ sur 346 cycles, IC 90 % [-6971 ; +7202] $
- M6 duree de vie 250 ms : -488 $ sur 346 cycles, IC 90 % [-8602 ; +8650] $
- M6 duree de vie 500 ms : -1012 $ sur 346 cycles, IC 90 % [-9232 ; +7290] $
- M8 hybride V2-F ecart qui grandit : +315 $ sur 240 cycles, IC 90 % [-1686 ; +2632] $
- M8 hybride V2-F incertitude 0,01 % : +1757 $ sur 130 cycles, IC 90 % [+322 ; +3520] $
- M8 hybride cohorte A : zone + modele monte : +240 $ sur 14 cycles, IC 90 % [-368 ; +1285] $
- M8 hybride cohorte B : V2-F corrige 0,015 % : +956 $ sur 133 cycles, IC 90 % [-244 ; +2289] $
- M8 hybride desaccord 20 60-180 s : +773 $ sur 229 cycles, IC 90 % [-1473 ; +3032] $
- M8 hybride desaccord 20 jeton 0,35-0,65 : +492 $ sur 17 cycles, IC 90 % [+120 ; +886] $
- M8 hybride desaccord 30 : +1417 $ sur 132 cycles, IC 90 % [-974 ; +4083] $
- M8b routeur corrige V2-F ecart qui grandit : +66 $ sur 240 cycles, IC 90 % [-1908 ; +2288] $
- M8b routeur corrige V2-F incertitude 0,01 % : +1526 $ sur 130 cycles, IC 90 % [+85 ; +3235] $
- M8b routeur corrige cohorte A : zone + modele monte : +240 $ sur 14 cycles, IC 90 % [-368 ; +1285] $
- M8b routeur corrige cohorte B : V2-F corrige 0,015 % : +724 $ sur 133 cycles, IC 90 % [-483 ; +2062] $
- M8b routeur corrige desaccord 20 60-180 s : +725 $ sur 229 cycles, IC 90 % [-1502 ; +2969] $
- M8b routeur corrige desaccord 20 jeton 0,35-0,65 : +492 $ sur 17 cycles, IC 90 % [+120 ; +886] $
- M8b routeur corrige desaccord 30 : +1417 $ sur 132 cycles, IC 90 % [-974 ; +4083] $
- M9 fin de cycle cote acquis : +106 $ sur 41 cycles, IC 90 % [+78 ; +138] $

Sélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.


## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)

Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : 496. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).

| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |
|---|---|---|---|---|
| FAST : preneur exécuté 164 ms après le signal | 1440 | 54153 $ | +4525 $ [IC 90 % -4780 ; +13507] | +0.08 |
| SLOW : preneur exécuté 1,164 s après (offre persistante) | 910 | 39479 $ | -2737 $ [IC 90 % -9992 ; +5079] | -0.07 |
| HYBRID : FAST sinon SLOW (règle fixée avant) | 1471 | 55565 $ | +4525 $ [IC 90 % -4535 ; +14224] | +0.08 |
| C : moteur alpha exécutable (exécution mesurée à 300 ms) | 131 | — | +784 $ | — |
| M1 : offre posée au signal (prudent ; proportionnel -1097 $) | 10657 | 67047 $ | -1350 $ | -0.02 |
| M2 marge 5 c (prudent ; proportionnel +6003 $) | 1923 | 41918 $ | +6172 $ | +0.15 |
| M2 marge 10 c (prudent ; proportionnel +4974 $) | 1704 | 34122 $ | +5388 $ | +0.16 |
| M0 témoin aléatoire (prudent ; proportionnel +3985 $) | 431 | 18366 $ | +3769 $ | +0.21 |
| M3 anticipation Chainlink (prudent ; proportionnel +3839 $) | 1481 | 28593 $ | +4340 $ | +0.15 |
| M4 retrait toxique (prudent ; proportionnel +24392 $) | 9072 | 161938 $ | +21334 $ | +0.13 |
| M5 remplissage attendu (prudent ; proportionnel +3556 $) | 3179 | 56442 $ | +3764 $ | +0.07 |

Période hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.


## Limites
- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.
- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.
- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.
- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.
