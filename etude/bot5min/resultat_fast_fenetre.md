# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 12.10.2026 19:20 UTC. 408 cycles de Dublin, avant la période réservée (13.10.2026 00:00 UTC). Paramètres fixés avant mesure : trajet simple 14 ms, calcul 0.2 ms, retard preneur 150 ms.

Données exclues ou douteuses : cycle coupé (limite d'événements) 11, cycles avec carnets Binance/Bybit 365, cycles avec trou de carnet ou de transactions (exclus des études de carnets) 303

## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)

| Cause | Nombre | Part |
|---|---|---|
| consommé | 31343 | 21 % |
| mixte | 1411 | 1 % |
| retiré | 77292 | 51 % |
| déplacé | 26701 | 18 % |
| indéterminé | 14750 | 10 % |

« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.

## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)

Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. « Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.

**sans retard preneur (référence théorique)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 98 % (121226) | 98 % (25832) | 98 % (84462) | 99 % (1175) | 100 % |
| 100 ms | 98 % (118624) | 99 % (25925) | 99 % (82682) | 99 % (1146) | 100 % |
| 150 ms | 99 % (116818) | 99 % (25914) | 99 % (81188) | 99 % (1131) | 100 % |
| 200 ms | 99 % (115165) | 99 % (25793) | 99 % (79767) | 99 % (1130) | 100 % |
| 300 ms | 99 % (111508) | 100 % (25256) | 99 % (76955) | 100 % (1122) | 100 % |
| 500 ms | 99 % (105369) | 100 % (23966) | 100 % (72411) | 100 % (1108) | 100 % |

**retard 50 ms (réglage du 17.08 au 04.09)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (121226) | 0 % (25832) | 0 % (84462) | 0 % (1175) | 0 % |
| 100 ms | 95 % (118624) | 95 % (25925) | 96 % (82682) | 97 % (1146) | 92 % |
| 150 ms | 96 % (116818) | 97 % (25914) | 97 % (81188) | 98 % (1131) | 100 % |
| 200 ms | 97 % (115165) | 97 % (25793) | 98 % (79767) | 97 % (1130) | 100 % |
| 300 ms | 98 % (111508) | 99 % (25256) | 98 % (76955) | 99 % (1122) | 100 % |
| 500 ms | 98 % (105369) | 99 % (23966) | 99 % (72411) | 99 % (1108) | 100 % |

**retard 150 ms (réglage actuel)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (121226) | 0 % (25832) | 0 % (84462) | 0 % (1175) | 0 % |
| 100 ms | 0 % (118624) | 0 % (25925) | 0 % (82682) | 0 % (1146) | 0 % |
| 150 ms | 0 % (116818) | 0 % (25914) | 0 % (81188) | 0 % (1131) | 0 % |
| 200 ms | 93 % (115165) | 93 % (25793) | 94 % (79767) | 97 % (1130) | 50 % |
| 300 ms | 95 % (111508) | 96 % (25256) | 96 % (76955) | 96 % (1122) | 83 % |
| 500 ms | 97 % (105369) | 98 % (23966) | 97 % (72411) | 98 % (1108) | 100 % |

Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple 14 ms + calcul + retard preneur 150 ms ≈ **164 ms**.

## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)

Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède (saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).

| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |
|---|---|---|---|---|---|
| toutes | 125841 | 32192 (26 %) | 90 / 406 / 891 | 25384 (20 %) | 19497 (15 %) |
| consommées | 29043 | 8519 (29 %) | 116 / 407 / 896 | 6997 (24 %) | 5211 (18 %) |
| retirées / déplacées | 95477 | 23058 (24 %) | 79 / 408 / 889 | 17875 (19 %) | 13927 (15 %) |
| mixtes | 1321 | 615 (47 %) | 137 / 363 / 882 | 512 (39 %) | 359 (27 %) |

**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin (51349 cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms dans 32 % des cas ; à des instants tirés au hasard (témoin) : 20 %.


C'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.

## 4. Vérification indirecte du retard preneur sur nos marchés

Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = 36399) : p10 / p50 / p90 = 22 / 154 / 563 ms ; jusqu'au 1er retrait (n = 32621) : 6 / 55 / 329 ms. Transactions moins de 150 ms après NOTRE information : 49 %. Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).

## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)

Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).

| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 507 | 18 | 417 (82 %) | 432 (85 %) | 272 | 1438 |
| M1 V2-F ecart qui grandit | 294 | 42 | 202 (69 %) | 205 (70 %) | 143 | 983 |
| M1 V2-F incertitude 0,01 % | 184 | 17 | 76 (41 %) | 76 (41 %) | 239 | 1214 |
| M1 cohorte A : zone + modele monte | 36 | 1 | 20 (56 %) | 21 (58 %) | 100 | 2109 |
| M1 cohorte B : V2-F corrige 0,015 % | 189 | 16 | 91 (48 %) | 91 (48 %) | 240 | 1220 |
| M1 desaccord 20 60-180 s | 280 | 39 | 206 (74 %) | 208 (74 %) | 153 | 989 |
| M1 desaccord 20 jeton 0,35-0,65 | 14 | 2 | 4 (29 %) | 4 (29 %) | 162 | 596 |
| M1 desaccord 30 | 188 | 37 | 130 (69 %) | 132 (70 %) | 100 | 832 |
| M10 double maker meilleur prix | 13695 | 729 | 2456 (18 %) | 2771 (20 %) | 166 | 652 |
| M11 zone maker | 208 | 15 | 28 (13 %) | 19 (9 %) | 45 | 215 |
| M2 cotation marge 10 c | 158861 | 445 | 1500 (1 %) | 1451 (1 %) | 225 | 278 |
| M2 cotation marge 5 c | 105965 | 625 | 1710 (2 %) | 1656 (2 %) | 226 | 338 |
| M21 maker du favori | 8508 | 319 | 1349 (16 %) | 1445 (17 %) | 157 | 577 |
| M3 anticipation Chainlink | 37057 | 667 | 1311 (4 %) | 1204 (3 %) | 215 | 200 |
| M4 retrait toxique | 94271 | 737 | 2117 (2 %) | 2096 (2 %) | 218 | 501 |
| M4a seul bourses -10 $ | 105036 | 682 | 1831 (2 %) | 1786 (2 %) | 223 | 416 |
| M4b seul flux agressif | 103429 | 702 | 1856 (2 %) | 1854 (2 %) | 224 | 432 |
| M4c seul ventes Polymarket | 85989 | 678 | 1945 (2 %) | 1890 (2 %) | 220 | 426 |
| M5 remplissage attendu | 17498 | 844 | 2972 (17 %) | 2414 (14 %) | 128 | 160 |
| M6 duree de vie 100 ms | 455214 | 1404 | 2179 (0 %) | 1452 (0 %) | 194 | 62 |
| M6 duree de vie 1000 ms | 135828 | 876 | 2131 (2 %) | 1857 (1 %) | 216 | 253 |
| M6 duree de vie 250 ms | 256989 | 1156 | 2198 (1 %) | 1398 (1 %) | 201 | 101 |
| M6 duree de vie 500 ms | 178135 | 1001 | 2244 (1 %) | 1514 (1 %) | 208 | 151 |
| M8 hybride V2-F ecart qui grandit | 287 | 39 | 185 (64 %) | 186 (65 %) | 5 | 199 |
| M8 hybride V2-F incertitude 0,01 % | 177 | 14 | 88 (50 %) | 88 (50 %) | 0 | 180 |
| M8 hybride cohorte A : zone + modele monte | 33 | 1 | 23 (70 %) | 23 (70 %) | 8 | 973 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 182 | 13 | 100 (55 %) | 100 (55 %) | 0 | 218 |
| M8 hybride desaccord 20 60-180 s | 271 | 37 | 191 (70 %) | 191 (70 %) | 5 | 199 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 14 | 1 | 7 (50 %) | 7 (50 %) | 97 | 896 |
| M8 hybride desaccord 30 | 183 | 32 | 130 (71 %) | 131 (72 %) | 21 | 339 |
| M8b routeur corrige V2-F ecart qui grandit | 276 | 37 | 177 (64 %) | 178 (64 %) | 10 | 246 |
| M8b routeur corrige V2-F incertitude 0,01 % | 168 | 13 | 80 (48 %) | 80 (48 %) | 0 | 202 |
| M8b routeur corrige cohorte A : zone + modele monte | 33 | 1 | 23 (70 %) | 23 (70 %) | 8 | 972 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 173 | 12 | 92 (53 %) | 92 (53 %) | 0 | 218 |
| M8b routeur corrige desaccord 20 60-180 s | 261 | 36 | 184 (70 %) | 184 (70 %) | 10 | 268 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 13 | 0 | 7 (54 %) | 7 (54 %) | 97 | 895 |
| M8b routeur corrige desaccord 30 | 172 | 30 | 123 (72 %) | 124 (72 %) | 22 | 365 |
| M9 fin de cycle cote acquis | 227 | 12 | 63 (28 %) | 56 (25 %) | 70 | 310 |

Offres remplies et réglées (fichier bot95/rapide_maker.json) :

| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |
|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 352 | 64240 / 64977 | 13996 $ | -3099 $ | -3071 $ | -0.22 | -1.4 / -1.6 / -2.0 / -2.3 |
| M1 V2-F ecart qui grandit | 211 | 49622 / 49728 | 7321 $ | +76 $ | +144 $ | +0.01 | -0.8 / -1.0 / -0.8 / -1.0 |
| M1 V2-F incertitude 0,01 % | 145 | 16198 / 16230 | 2757 $ | -186 $ | -207 $ | -0.07 | +0.1 / -0.0 / -1.5 / -0.5 |
| M1 cohorte A : zone + modele monte | 28 | 4859 / 4860 | 750 $ | +405 $ | +406 $ | +0.54 | -0.2 / +1.0 / +0.3 / +5.4 |
| M1 cohorte B : V2-F corrige 0,015 % | 147 | 20294 / 20300 | 3309 $ | -341 $ | -376 $ | -0.10 | -1.1 / -0.7 / -1.7 / -1.8 |
| M1 desaccord 20 60-180 s | 198 | 57232 / 57270 | 7524 $ | -622 $ | -625 $ | -0.08 | -1.1 / -1.5 / -1.6 / -1.2 |
| M1 desaccord 20 jeton 0,35-0,65 | 10 | 307 / 307 | 150 $ | -67 $ | -67 $ | -0.44 | -2.7 / -8.5 / -8.6 / -10.5 |
| M1 desaccord 30 | 139 | 52809 / 52918 | 5052 $ | +1001 $ | +980 $ | +0.20 | -0.3 / -0.4 / +0.0 / -0.0 |
| M10 double maker meilleur prix | 8711 | 68803 / 76113 | 28665 $ | +967 $ | +770 $ | +0.03 | -0.8 / -0.7 / -0.6 / -0.8 |
| M11 zone maker | 143 | 1181 / 1111 | 229 $ | -61 $ | -62 $ | -0.27 | -0.7 / -1.2 / -3.2 / +0.1 |
| M2 cotation marge 10 c | 1310 | 97324 / 94248 | 26738 $ | +433 $ | +739 $ | +0.02 | -0.5 / -0.5 / -0.4 / -0.8 |
| M2 cotation marge 5 c | 1508 | 87125 / 85925 | 29988 $ | +998 $ | +415 $ | +0.03 | -1.0 / -0.9 / -0.8 / -0.6 |
| M21 maker du favori | 1432 | 31815 / 33049 | 20007 $ | -460 $ | -762 $ | -0.02 | -0.9 / -1.0 / -0.9 / -1.2 |
| M3 anticipation Chainlink | 1144 | 84426 / 79849 | 19444 $ | +900 $ | +1001 $ | +0.05 | +2.1 / +2.3 / +1.7 / +1.2 |
| M4 retrait toxique | 2045 | 99688 / 97714 | 28482 $ | +987 $ | +1196 $ | +0.03 | -0.5 / -0.2 / -0.3 / -0.6 |
| M4a seul bourses -10 $ | 1633 | 88597 / 86662 | 28514 $ | +1692 $ | +599 $ | +0.06 | -0.8 / -0.6 / -0.6 / -0.7 |
| M4b seul flux agressif | 1713 | 89274 / 88924 | 28269 $ | +1336 $ | +419 $ | +0.05 | -0.7 / -0.6 / -0.6 / -0.5 |
| M4c seul ventes Polymarket | 1794 | 93973 / 94532 | 27687 $ | -1816 $ | -1849 $ | -0.07 | -0.8 / -0.6 / -0.3 / -0.5 |
| M5 remplissage attendu | 2420 | 118323 / 105124 | 39254 $ | +1615 $ | +1219 $ | +0.04 | -0.8 / -0.8 / -0.5 / -0.8 |
| M6 duree de vie 100 ms | 1399 | 112505 / 98803 | 36341 $ | -1267 $ | -1054 $ | -0.03 | -1.2 / -1.0 / -0.7 / -0.6 |
| M6 duree de vie 1000 ms | 1750 | 100993 / 91464 | 33555 $ | +113 $ | -426 $ | +0.00 | -1.0 / -1.0 / -0.8 / -0.5 |
| M6 duree de vie 250 ms | 1470 | 113519 / 97313 | 37049 $ | -860 $ | -1568 $ | -0.02 | -1.2 / -1.1 / -0.8 / -0.5 |
| M6 duree de vie 500 ms | 1529 | 111590 / 95205 | 36651 $ | +224 $ | -157 $ | +0.01 | -1.0 / -1.0 / -0.9 / -0.6 |
| M8 hybride V2-F ecart qui grandit | 196 | 34275 / 34374 | 5653 $ | +281 $ | +349 $ | +0.05 | -0.3 / -0.5 / -0.4 / -1.2 |
| M8 hybride V2-F incertitude 0,01 % | 131 | 14419 / 14421 | 2514 $ | -118 $ | -131 $ | -0.05 | +1.5 / +1.8 / +0.4 / +1.8 |
| M8 hybride cohorte A : zone + modele monte | 22 | 3873 / 3873 | 609 $ | -100 $ | -100 $ | -0.16 | -0.1 / +0.9 / -0.9 / +1.7 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 133 | 16605 / 16599 | 2918 $ | -283 $ | -293 $ | -0.10 | -0.2 / +0.4 / -0.6 / -0.3 |
| M8 hybride desaccord 20 60-180 s | 183 | 38435 / 38435 | 5715 $ | -654 $ | -654 $ | -0.11 | -0.9 / -1.6 / -1.7 / -1.4 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 10 | 307 / 307 | 150 $ | -67 $ | -67 $ | -0.44 | -2.7 / -8.5 / -8.6 / -10.5 |
| M8 hybride desaccord 30 | 126 | 45225 / 45351 | 4349 $ | +56 $ | +51 $ | +0.01 | -0.3 / -0.7 / -0.7 / -0.5 |
| M8b routeur corrige V2-F ecart qui grandit | 186 | 33496 / 33594 | 5430 $ | +140 $ | +209 $ | +0.03 | -0.2 / -0.4 / -0.4 / -1.3 |
| M8b routeur corrige V2-F incertitude 0,01 % | 123 | 13445 / 13448 | 2332 $ | -61 $ | -74 $ | -0.03 | +1.6 / +1.6 / +0.3 / +1.9 |
| M8b routeur corrige cohorte A : zone + modele monte | 22 | 3873 / 3873 | 609 $ | -100 $ | -100 $ | -0.16 | -0.1 / +0.9 / -0.9 / +1.7 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 125 | 15725 / 15718 | 2724 $ | -401 $ | -411 $ | -0.15 | -0.1 / +0.5 / -0.3 / +0.2 |
| M8b routeur corrige desaccord 20 60-180 s | 174 | 39325 / 39325 | 5586 $ | -726 $ | -726 $ | -0.13 | -1.0 / -1.7 / -1.8 / -1.4 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 9 | 307 / 307 | 150 $ | -67 $ | -67 $ | -0.44 | -2.7 / -8.5 / -8.6 / -10.5 |
| M8b routeur corrige desaccord 30 | 116 | 43572 / 43699 | 4044 $ | +79 $ | +74 $ | +0.02 | -0.5 / -0.7 / -0.9 / -1.0 |
| M9 fin de cycle cote acquis | 60 | 1939 / 1825 | 1839 $ | +100 $ | +40 $ | +0.05 | -2.2 / -1.6 / -0.3 / -3.4 |

**Par prix d'achat et temps restant (toutes variantes maker, prudent)**

| Prix | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0.00–0.20 | 4329 | 71494 $ | -10556 $ | -0.15 |
| 0.20–0.35 | 10829 | 167242 $ | +15664 $ | +0.09 |
| 0.35–0.50 | 11898 | 210657 $ | -4066 $ | -0.02 |
| 0.50–0.65 | 3680 | 31645 $ | +268 $ | +0.01 |
| 0.65–1.00 | 2111 | 25315 $ | -1261 $ | -0.05 |

| Temps restant à la pose | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0–60 s | 327 | 10854 $ | -579 $ | -0.05 |
| 60–120 s | 2155 | 54590 $ | -9621 $ | -0.18 |
| 120–180 s | 3632 | 70243 $ | -2804 $ | -0.04 |
| 180–300 s | 26611 | 367630 $ | +13073 $ | +0.04 |
(temps restant enregistré seulement depuis la version du 11.10 13:55)


**Intervalle de confiance à 90 % du résultat prudent (rééchantillonnage par cycles)**

- M0 temoin aleatoire : -3099 $ sur 212 cycles, IC 90 % [-4603 ; -1514] $
- M1 V2-F ecart qui grandit : +76 $ sur 211 cycles, IC 90 % [-2110 ; +2490] $
- M1 V2-F incertitude 0,01 % : -186 $ sur 145 cycles, IC 90 % [-1298 ; +1079] $
- M1 cohorte A : zone + modele monte : +405 $ sur 28 cycles, IC 90 % [-378 ; +1330] $
- M1 cohorte B : V2-F corrige 0,015 % : -341 $ sur 147 cycles, IC 90 % [-1578 ; +911] $
- M1 desaccord 20 60-180 s : -622 $ sur 198 cycles, IC 90 % [-2557 ; +1654] $
- M1 desaccord 20 jeton 0,35-0,65 : -67 $ sur 10 cycles, IC 90 % [-200 ; +50] $
- M1 desaccord 30 : +1001 $ sur 139 cycles, IC 90 % [-1486 ; +3876] $
- M10 double maker meilleur prix : +967 $ sur 216 cycles, IC 90 % [-1255 ; +3228] $
- M11 zone maker : -61 $ sur 29 cycles, IC 90 % [-309 ; +200] $
- M2 cotation marge 10 c : +433 $ sur 238 cycles, IC 90 % [-3019 ; +3991] $
- M2 cotation marge 5 c : +998 $ sur 241 cycles, IC 90 % [-1732 ; +3871] $
- M21 maker du favori : -460 $ sur 207 cycles, IC 90 % [-1620 ; +731] $
- M3 anticipation Chainlink : +900 $ sur 210 cycles, IC 90 % [-1930 ; +3732] $
- M4 retrait toxique : +987 $ sur 232 cycles, IC 90 % [-2199 ; +4313] $
- M4a seul bourses -10 $ : +1692 $ sur 226 cycles, IC 90 % [-1273 ; +4713] $
- M4b seul flux agressif : +1336 $ sur 226 cycles, IC 90 % [-1588 ; +4408] $
- M4c seul ventes Polymarket : -1816 $ sur 226 cycles, IC 90 % [-4518 ; +980] $
- M5 remplissage attendu : +1615 $ sur 232 cycles, IC 90 % [-2512 ; +5905] $
- M6 duree de vie 100 ms : -1267 $ sur 226 cycles, IC 90 % [-4932 ; +2448] $
- M6 duree de vie 1000 ms : +113 $ sur 226 cycles, IC 90 % [-3221 ; +3614] $
- M6 duree de vie 250 ms : -860 $ sur 226 cycles, IC 90 % [-4799 ; +3161] $
- M6 duree de vie 500 ms : +224 $ sur 226 cycles, IC 90 % [-3657 ; +4301] $
- M8 hybride V2-F ecart qui grandit : +281 $ sur 196 cycles, IC 90 % [-1491 ; +2047] $
- M8 hybride V2-F incertitude 0,01 % : -118 $ sur 131 cycles, IC 90 % [-1164 ; +1069] $
- M8 hybride cohorte A : zone + modele monte : -100 $ sur 22 cycles, IC 90 % [-592 ; +524] $
- M8 hybride cohorte B : V2-F corrige 0,015 % : -283 $ sur 133 cycles, IC 90 % [-1361 ; +1042] $
- M8 hybride desaccord 20 60-180 s : -654 $ sur 183 cycles, IC 90 % [-2281 ; +1044] $
- M8 hybride desaccord 20 jeton 0,35-0,65 : -67 $ sur 10 cycles, IC 90 % [-200 ; +50] $
- M8 hybride desaccord 30 : +56 $ sur 126 cycles, IC 90 % [-1854 ; +2287] $
- M8b routeur corrige V2-F ecart qui grandit : +140 $ sur 186 cycles, IC 90 % [-1533 ; +1846] $
- M8b routeur corrige V2-F incertitude 0,01 % : -61 $ sur 123 cycles, IC 90 % [-1141 ; +1158] $
- M8b routeur corrige cohorte A : zone + modele monte : -100 $ sur 22 cycles, IC 90 % [-592 ; +524] $
- M8b routeur corrige cohorte B : V2-F corrige 0,015 % : -401 $ sur 125 cycles, IC 90 % [-1477 ; +774] $
- M8b routeur corrige desaccord 20 60-180 s : -726 $ sur 174 cycles, IC 90 % [-2342 ; +980] $
- M8b routeur corrige desaccord 20 jeton 0,35-0,65 : -67 $ sur 9 cycles, IC 90 % [-200 ; +50] $
- M8b routeur corrige desaccord 30 : +79 $ sur 116 cycles, IC 90 % [-1881 ; +2366] $
- M9 fin de cycle cote acquis : +100 $ sur 31 cycles, IC 90 % [+75 ; +128] $

Sélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.


## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)

Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : 217. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).

| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |
|---|---|---|---|---|
| FAST : preneur exécuté 164 ms après le signal | 679 | 21990 $ | +3470 $ [IC 90 % -2388 ; +10008] | +0.16 |
| SLOW : preneur exécuté 1,164 s après (offre persistante) | 437 | 16920 $ | +620 $ [IC 90 % -4254 ; +5993] | +0.04 |
| HYBRID : FAST sinon SLOW (règle fixée avant) | 704 | 23015 $ | +3684 $ [IC 90 % -2525 ; +10383] | +0.16 |
| C : moteur alpha exécutable (exécution mesurée à 300 ms) | 61 | — | +251 $ | — |
| M1 : offre posée au signal (prudent ; proportionnel +1551 $) | 8534 | 52183 $ | +1752 $ | +0.03 |
| M2 marge 5 c (prudent ; proportionnel +1848 $) | 1372 | 27536 $ | +2271 $ | +0.08 |
| M2 marge 10 c (prudent ; proportionnel +2145 $) | 1209 | 25179 $ | +1910 $ | +0.08 |
| M0 témoin aléatoire (prudent ; proportionnel -2907 $) | 335 | 13546 $ | -2935 $ | -0.22 |
| M3 anticipation Chainlink (prudent ; proportionnel +2181 $) | 1017 | 17793 $ | +1934 $ | +0.11 |
| M4 retrait toxique (prudent ; proportionnel +6590 $) | 6575 | 104616 $ | +7662 $ | +0.07 |
| M5 remplissage attendu (prudent ; proportionnel +3440 $) | 2158 | 35368 $ | +4219 $ | +0.12 |

Période hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.


## Limites
- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.
- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.
- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.
- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.
