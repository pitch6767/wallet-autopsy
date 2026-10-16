# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 16.10.2026 09:26 UTC. 916 cycles de Dublin, HORS ÉCHANTILLON. Paramètres fixés avant mesure : trajet simple 14 ms, calcul 0.2 ms, retard preneur 150 ms.

Données exclues ou douteuses : cycles avec carnets Binance/Bybit 916, cycles avec trou de carnet ou de transactions (exclus des études de carnets) 901

## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)

| Cause | Nombre | Part |
|---|---|---|
| consommé | 75414 | 24 % |
| mixte | 3117 | 1 % |
| retiré | 161638 | 52 % |
| déplacé | 45933 | 15 % |
| indéterminé | 23215 | 8 % |

« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.

## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)

Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. « Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.

**sans retard preneur (référence théorique)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 98 % (248390) | 98 % (60331) | 99 % (169456) | 99 % (2747) | 100 % |
| 100 ms | 98 % (245214) | 98 % (60878) | 99 % (167120) | 99 % (2686) | 100 % |
| 150 ms | 99 % (243145) | 99 % (61094) | 99 % (165177) | 100 % (2670) | 100 % |
| 200 ms | 99 % (240619) | 99 % (60995) | 99 % (163072) | 100 % (2651) | 100 % |
| 300 ms | 99 % (234848) | 100 % (60257) | 100 % (158504) | 100 % (2631) | 100 % |
| 500 ms | 100 % (224943) | 100 % (58331) | 100 % (150826) | 100 % (2567) | 100 % |

**retard 50 ms (réglage du 17.08 au 04.09)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (248390) | 0 % (60331) | 0 % (169456) | 0 % (2747) | 0 % |
| 100 ms | 95 % (245214) | 94 % (60878) | 96 % (167120) | 98 % (2686) | 80 % |
| 150 ms | 96 % (243145) | 96 % (61094) | 97 % (165177) | 98 % (2670) | 89 % |
| 200 ms | 98 % (240619) | 98 % (60995) | 98 % (163072) | 99 % (2651) | 100 % |
| 300 ms | 98 % (234848) | 99 % (60257) | 99 % (158504) | 99 % (2631) | 100 % |
| 500 ms | 99 % (224943) | 99 % (58331) | 99 % (150826) | 99 % (2567) | 100 % |

**retard 150 ms (réglage actuel)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (248390) | 0 % (60331) | 0 % (169456) | 0 % (2747) | 0 % |
| 100 ms | 0 % (245214) | 0 % (60878) | 0 % (167120) | 0 % (2686) | 0 % |
| 150 ms | 0 % (243145) | 0 % (61094) | 0 % (165177) | 0 % (2670) | 0 % |
| 200 ms | 94 % (240619) | 92 % (60995) | 95 % (163072) | 97 % (2651) | 34 % |
| 300 ms | 96 % (234848) | 96 % (60257) | 97 % (158504) | 98 % (2631) | 75 % |
| 500 ms | 98 % (224943) | 98 % (58331) | 98 % (150826) | 99 % (2567) | 100 % |

Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple 14 ms + calcul + retard preneur 150 ms ≈ **164 ms**.

## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)

Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède (saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).

| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |
|---|---|---|---|---|---|
| toutes | 260443 | 98795 (38 %) | 104 / 487 / 920 | 82296 (32 %) | 66656 (26 %) |
| consommées | 68662 | 28581 (42 %) | 128 / 488 / 918 | 24507 (36 %) | 19518 (28 %) |
| retirées / déplacées | 188837 | 68628 (36 %) | 96 / 487 / 921 | 56353 (30 %) | 46016 (24 %) |
| mixtes | 2944 | 1586 (54 %) | 167 / 470 / 932 | 1436 (49 %) | 1122 (38 %) |

**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin (208388 cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms dans 30 % des cas ; à des instants tirés au hasard (témoin) : 21 %.


C'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.

## 4. Vérification indirecte du retard preneur sur nos marchés

Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = 140788) : p10 / p50 / p90 = 29 / 171 / 654 ms ; jusqu'au 1er retrait (n = 128695) : 7 / 67 / 378 ms. Transactions moins de 150 ms après NOTRE information : 44 %. Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).

## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)

Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).

| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 1284 | 55 | 1055 (82 %) | 1079 (84 %) | 456 | 1408 |
| M1 V2-F ecart qui grandit | 596 | 116 | 373 (63 %) | 379 (64 %) | 249 | 1130 |
| M1 V2-F incertitude 0,01 % | 339 | 57 | 112 (33 %) | 114 (34 %) | 295 | 811 |
| M1 cohorte A : zone + modele monte | 41 | 6 | 25 (61 %) | 25 (61 %) | 100 | 1875 |
| M1 cohorte B : V2-F corrige 0,015 % | 347 | 60 | 132 (38 %) | 133 (38 %) | 290 | 713 |
| M1 desaccord 20 60-180 s | 570 | 108 | 386 (68 %) | 392 (69 %) | 258 | 1212 |
| M1 desaccord 20 jeton 0,35-0,65 | 54 | 12 | 25 (46 %) | 25 (46 %) | 72 | 252 |
| M1 desaccord 30 | 341 | 79 | 227 (67 %) | 230 (67 %) | 160 | 812 |
| M10 double maker meilleur prix | 36911 | 2529 | 8402 (23 %) | 8217 (22 %) | 224 | 637 |
| M11 zone maker | 173 | 36 | 19 (11 %) | 15 (9 %) | 100 | 292 |
| M2 cotation marge 10 c | 573227 | 1858 | 4507 (1 %) | 4227 (1 %) | 382 | 381 |
| M2 cotation marge 5 c | 364329 | 2464 | 5476 (2 %) | 5021 (1 %) | 378 | 369 |
| M21 maker du favori | 24483 | 1597 | 4966 (20 %) | 4588 (19 %) | 217 | 555 |
| M3 anticipation Chainlink | 121878 | 2180 | 4436 (4 %) | 3873 (3 %) | 363 | 264 |
| M4 retrait toxique | 302747 | 2637 | 6157 (2 %) | 5782 (2 %) | 375 | 486 |
| M4a seul bourses -10 $ | 348180 | 2648 | 5770 (2 %) | 5277 (2 %) | 375 | 411 |
| M4b seul flux agressif | 351183 | 2606 | 5700 (2 %) | 5286 (2 %) | 375 | 432 |
| M4c seul ventes Polymarket | 298370 | 2594 | 6133 (2 %) | 5587 (2 %) | 375 | 433 |
| M5 remplissage attendu | 69244 | 5573 | 11115 (16 %) | 8345 (12 %) | 144 | 210 |
| M6 duree de vie 100 ms | 1263774 | 6853 | 8233 (1 %) | 5542 (0 %) | 360 | 91 |
| M6 duree de vie 1000 ms | 451157 | 3431 | 7011 (2 %) | 5853 (1 %) | 372 | 308 |
| M6 duree de vie 250 ms | 776966 | 5013 | 7904 (1 %) | 5219 (1 %) | 364 | 141 |
| M6 duree de vie 500 ms | 562913 | 4068 | 7576 (1 %) | 5256 (1 %) | 368 | 204 |
| M8 hybride V2-F ecart qui grandit | 595 | 115 | 361 (61 %) | 364 (61 %) | 0 | 206 |
| M8 hybride V2-F incertitude 0,01 % | 337 | 52 | 144 (43 %) | 146 (43 %) | 0 | 176 |
| M8 hybride cohorte A : zone + modele monte | 41 | 5 | 27 (66 %) | 27 (66 %) | 11 | 617 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 345 | 55 | 160 (46 %) | 161 (47 %) | 5 | 179 |
| M8 hybride desaccord 20 60-180 s | 569 | 107 | 351 (62 %) | 355 (62 %) | 0 | 215 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 54 | 9 | 32 (59 %) | 32 (59 %) | 7 | 204 |
| M8 hybride desaccord 30 | 341 | 76 | 221 (65 %) | 223 (65 %) | 36 | 315 |
| M8b routeur corrige V2-F ecart qui grandit | 595 | 116 | 353 (59 %) | 357 (60 %) | 10 | 254 |
| M8b routeur corrige V2-F incertitude 0,01 % | 337 | 53 | 139 (41 %) | 141 (42 %) | 8 | 178 |
| M8b routeur corrige cohorte A : zone + modele monte | 41 | 5 | 27 (66 %) | 27 (66 %) | 11 | 617 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 345 | 56 | 157 (46 %) | 158 (46 %) | 12 | 181 |
| M8b routeur corrige desaccord 20 60-180 s | 569 | 108 | 347 (61 %) | 351 (62 %) | 10 | 271 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 54 | 10 | 31 (57 %) | 31 (57 %) | 21 | 189 |
| M8b routeur corrige desaccord 30 | 341 | 78 | 219 (64 %) | 221 (65 %) | 45 | 328 |
| M9 fin de cycle cote acquis | 970 | 149 | 181 (19 %) | 188 (19 %) | 187 | 441 |

Offres remplies et réglées (fichier bot95/rapide_maker.json) :

| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |
|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 1301 | 208647 / 210577 | 52364 $ | -5 $ | +320 $ | -0.00 | -1.7 / -1.7 / -1.7 / -1.6 |
| M1 V2-F ecart qui grandit | 600 | 154658 / 155488 | 18587 $ | -1099 $ | -1185 $ | -0.06 | -1.2 / -1.3 / -1.3 / -0.4 |
| M1 V2-F incertitude 0,01 % | 342 | 28564 / 28709 | 5073 $ | +1732 $ | +1799 $ | +0.34 | -0.2 / +0.3 / +3.1 / +7.5 |
| M1 cohorte A : zone + modele monte | 41 | 7993 / 7993 | 1250 $ | -456 $ | -456 $ | -0.37 | -2.0 / -4.3 / -4.7 / -5.3 |
| M1 cohorte B : V2-F corrige 0,015 % | 348 | 37720 / 37811 | 5970 $ | +470 $ | +506 $ | +0.08 | -1.0 / -1.0 / -0.4 / +2.7 |
| M1 desaccord 20 60-180 s | 575 | 163647 / 164426 | 19214 $ | -467 $ | -467 $ | -0.02 | -1.1 / -1.4 / -1.3 / -0.8 |
| M1 desaccord 20 jeton 0,35-0,65 | 53 | 3403 / 3403 | 1250 $ | +841 $ | +841 $ | +0.67 | +4.8 / +5.7 / +4.8 / +8.3 |
| M1 desaccord 30 | 337 | 128729 / 128505 | 11149 $ | -1699 $ | -1929 $ | -0.15 | -1.1 / -0.8 / -0.7 / -0.2 |
| M10 double maker meilleur prix | 37285 | 393925 / 411340 | 164139 $ | -4589 $ | -2259 $ | -0.03 | -1.1 / -1.1 / -1.1 / -1.1 |
| M11 zone maker | 173 | 3511 / 3293 | 662 $ | -305 $ | -269 $ | -0.46 | -2.2 / -2.4 / -2.9 / -4.0 |
| M2 cotation marge 10 c | 5436 | 501104 / 491908 | 121805 $ | -1463 $ | -2153 $ | -0.01 | -1.0 / -0.8 / -0.7 / -0.7 |
| M2 cotation marge 5 c | 6498 | 453917 / 443441 | 150732 $ | +2012 $ | +1140 $ | +0.01 | -1.2 / -1.1 / -1.0 / -0.7 |
| M21 maker du favori | 6630 | 182251 / 179043 | 114267 $ | -3618 $ | -2703 $ | -0.03 | -1.3 / -1.3 / -1.0 / -1.3 |
| M3 anticipation Chainlink | 5263 | 404575 / 384082 | 107959 $ | +2656 $ | +2813 $ | +0.02 | +0.6 / +0.6 / +0.7 / +1.0 |
| M4 retrait toxique | 7815 | 478873 / 475247 | 141121 $ | +1303 $ | +657 $ | +0.01 | -0.8 / -0.8 / -0.7 / -0.5 |
| M4a seul bourses -10 $ | 6961 | 473963 / 464908 | 150210 $ | +1223 $ | +1932 $ | +0.01 | -1.2 / -1.1 / -1.0 / -0.8 |
| M4b seul flux agressif | 6968 | 460323 / 455007 | 146897 $ | +1876 $ | +1987 $ | +0.01 | -1.0 / -0.9 / -0.9 / -0.8 |
| M4c seul ventes Polymarket | 7490 | 492945 / 485817 | 145537 $ | +584 $ | +443 $ | +0.00 | -1.1 / -0.9 / -0.7 / -0.5 |
| M5 remplissage attendu | 12205 | 714420 / 640905 | 224510 $ | -1136 $ | +331 $ | -0.01 | -1.0 / -1.1 / -1.1 / -1.2 |
| M6 duree de vie 100 ms | 8350 | 767086 / 684551 | 225409 $ | -2708 $ | -3378 $ | -0.01 | -1.4 / -1.3 / -1.3 / -1.1 |
| M6 duree de vie 1000 ms | 8262 | 583949 / 533593 | 186340 $ | +1042 $ | -149 $ | +0.01 | -1.3 / -1.1 / -1.1 / -0.8 |
| M6 duree de vie 250 ms | 7986 | 700489 / 619911 | 214329 $ | -1123 $ | -2778 $ | -0.01 | -1.4 / -1.2 / -1.1 / -1.0 |
| M6 duree de vie 500 ms | 7910 | 658705 / 580510 | 204533 $ | +5255 $ | +3060 $ | +0.03 | -1.4 / -1.2 / -1.2 / -1.0 |
| M8 hybride V2-F ecart qui grandit | 599 | 106581 / 107035 | 15435 $ | +2631 $ | +2540 $ | +0.17 | -0.5 / -0.7 / -0.7 / -0.3 |
| M8 hybride V2-F incertitude 0,01 % | 340 | 28814 / 28810 | 5672 $ | +2610 $ | +2612 $ | +0.46 | +1.8 / +2.7 / +5.0 / +10.2 |
| M8 hybride cohorte A : zone + modele monte | 41 | 7582 / 7582 | 1231 $ | -188 $ | -188 $ | -0.15 | -0.2 / -2.3 / -2.7 / -2.3 |
| M8 hybride cohorte B : V2-F corrige 0,015 % | 346 | 34328 / 34284 | 6246 $ | +1924 $ | +1899 $ | +0.31 | +0.9 / +1.1 / +1.6 / +5.4 |
| M8 hybride desaccord 20 60-180 s | 574 | 111053 / 111500 | 15241 $ | +2908 $ | +2900 $ | +0.19 | -0.9 / -1.1 / -1.3 / -0.8 |
| M8 hybride desaccord 20 jeton 0,35-0,65 | 53 | 3978 / 3978 | 1513 $ | +912 $ | +912 $ | +0.60 | +3.6 / +3.8 / +2.6 / +9.0 |
| M8 hybride desaccord 30 | 337 | 105906 / 105681 | 10045 $ | -150 $ | -381 $ | -0.01 | -0.5 / -0.0 / -0.1 / +0.9 |
| M8b routeur corrige V2-F ecart qui grandit | 599 | 107669 / 108167 | 15310 $ | +2254 $ | +2160 $ | +0.15 | -0.7 / -1.0 / -1.0 / -0.3 |
| M8b routeur corrige V2-F incertitude 0,01 % | 340 | 28070 / 28096 | 5499 $ | +2221 $ | +2247 $ | +0.40 | +1.5 / +2.3 / +4.5 / +10.2 |
| M8b routeur corrige cohorte A : zone + modele monte | 41 | 7582 / 7582 | 1231 $ | -188 $ | -188 $ | -0.15 | -0.2 / -2.3 / -2.7 / -2.3 |
| M8b routeur corrige cohorte B : V2-F corrige 0,015 % | 346 | 35781 / 35766 | 6220 $ | +1438 $ | +1437 $ | +0.23 | +0.6 / +1.0 / +1.2 / +5.1 |
| M8b routeur corrige desaccord 20 60-180 s | 574 | 112306 / 112752 | 15231 $ | +2786 $ | +2778 $ | +0.18 | -0.9 / -1.2 / -1.2 / -0.8 |
| M8b routeur corrige desaccord 20 jeton 0,35-0,65 | 53 | 3863 / 3863 | 1463 $ | +848 $ | +848 $ | +0.58 | +3.8 / +3.8 / +2.5 / +8.8 |
| M8b routeur corrige desaccord 30 | 337 | 107185 / 106960 | 9994 $ | -348 $ | -579 $ | -0.03 | -0.5 / +0.0 / -0.1 / +1.0 |
| M9 fin de cycle cote acquis | 219 | 7492 / 7755 | 7072 $ | +152 $ | +151 $ | +0.02 | -0.2 / -0.3 / -0.8 / -5.2 |

**Par prix d'achat et temps restant (toutes variantes maker, prudent)**

| Prix | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0.00–0.20 | 19009 | 293784 $ | +9763 $ | +0.03 |
| 0.20–0.35 | 47119 | 835414 $ | +3518 $ | +0.00 |
| 0.35–0.50 | 49108 | 1003482 $ | -4615 $ | -0.00 |
| 0.50–0.65 | 18309 | 256159 $ | +10402 $ | +0.04 |
| 0.65–1.00 | 10083 | 141874 $ | +1068 $ | +0.01 |

| Temps restant à la pose | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0–60 s | 2103 | 63145 $ | +3541 $ | +0.06 |
| 60–120 s | 10760 | 278593 $ | +21823 $ | +0.08 |
| 120–180 s | 17656 | 383195 $ | -6997 $ | -0.02 |
| 180–300 s | 113109 | 1805779 $ | +1769 $ | +0.00 |
(temps restant enregistré seulement depuis la version du 11.10 13:55)


**Intervalle de confiance à 90 % du résultat prudent (rééchantillonnage par cycles)**

- M0 temoin aleatoire : -5 $ sur 777 cycles, IC 90 % [-4153 ; +4405] $
- M1 V2-F ecart qui grandit : -1099 $ sur 600 cycles, IC 90 % [-4796 ; +2480] $
- M1 V2-F incertitude 0,01 % : +1732 $ sur 342 cycles, IC 90 % [-169 ; +3993] $
- M1 cohorte A : zone + modele monte : -456 $ sur 41 cycles, IC 90 % [-1300 ; +638] $
- M1 cohorte B : V2-F corrige 0,015 % : +470 $ sur 348 cycles, IC 90 % [-1206 ; +2227] $
- M1 desaccord 20 60-180 s : -467 $ sur 575 cycles, IC 90 % [-4341 ; +3261] $
- M1 desaccord 20 jeton 0,35-0,65 : +841 $ sur 53 cycles, IC 90 % [+183 ; +1466] $
- M1 desaccord 30 : -1699 $ sur 337 cycles, IC 90 % [-5220 ; +2200] $
- M10 double maker meilleur prix : -4589 $ sur 877 cycles, IC 90 % [-11569 ; +2928] $
- M11 zone maker : -305 $ sur 30 cycles, IC 90 % [-991 ; +437] $
- M2 cotation marge 10 c : -1463 $ sur 846 cycles, IC 90 % [-11466 ; +9102] $
- M2 cotation marge 5 c : +2012 $ sur 876 cycles, IC 90 % [-7471 ; +12199] $
- M21 maker du favori : -3618 $ sur 841 cycles, IC 90 % [-7090 ; -298] $
- M3 anticipation Chainlink : +2656 $ sur 858 cycles, IC 90 % [-4862 ; +10169] $
- M4 retrait toxique : +1303 $ sur 871 cycles, IC 90 % [-6804 ; +9383] $
- M4a seul bourses -10 $ : +1223 $ sur 875 cycles, IC 90 % [-8852 ; +11152] $
- M4b seul flux agressif : +1876 $ sur 873 cycles, IC 90 % [-7117 ; +11141] $
- M4c seul ventes Polymarket : +584 $ sur 872 cycles, IC 90 % [-8153 ; +9716] $
- M5 remplissage attendu : -1136 $ sur 877 cycles, IC 90 % [-14023 ; +13358] $
- M6 duree de vie 100 ms : -2708 $ sur 874 cycles, IC 90 % [-18008 ; +13579] $
- M6 duree de vie 1000 ms : +1042 $ sur 876 cycles, IC 90 % [-10003 ; +12825] $
- M6 duree de vie 250 ms : -1123 $ sur 876 cycles, IC 90 % [-15133 ; +12357] $
- M6 duree de vie 500 ms : +5255 $ sur 875 cycles, IC 90 % [-8151 ; +18143] $
- M8 hybride V2-F ecart qui grandit : +2631 $ sur 599 cycles, IC 90 % [-925 ; +6173] $
- M8 hybride V2-F incertitude 0,01 % : +2610 $ sur 340 cycles, IC 90 % [+663 ; +4762] $
- M8 hybride cohorte A : zone + modele monte : -188 $ sur 41 cycles, IC 90 % [-1103 ; +1000] $
- M8 hybride cohorte B : V2-F corrige 0,015 % : +1924 $ sur 346 cycles, IC 90 % [+117 ; +3814] $
- M8 hybride desaccord 20 60-180 s : +2908 $ sur 574 cycles, IC 90 % [-577 ; +6415] $
- M8 hybride desaccord 20 jeton 0,35-0,65 : +912 $ sur 53 cycles, IC 90 % [+246 ; +1556] $
- M8 hybride desaccord 30 : -150 $ sur 337 cycles, IC 90 % [-3390 ; +3538] $
- M8b routeur corrige V2-F ecart qui grandit : +2254 $ sur 599 cycles, IC 90 % [-1287 ; +5907] $
- M8b routeur corrige V2-F incertitude 0,01 % : +2221 $ sur 340 cycles, IC 90 % [+331 ; +4372] $
- M8b routeur corrige cohorte A : zone + modele monte : -188 $ sur 41 cycles, IC 90 % [-1103 ; +1000] $
- M8b routeur corrige cohorte B : V2-F corrige 0,015 % : +1438 $ sur 346 cycles, IC 90 % [-378 ; +3296] $
- M8b routeur corrige desaccord 20 60-180 s : +2786 $ sur 574 cycles, IC 90 % [-672 ; +6381] $
- M8b routeur corrige desaccord 20 jeton 0,35-0,65 : +848 $ sur 53 cycles, IC 90 % [+176 ; +1496] $
- M8b routeur corrige desaccord 30 : -348 $ sur 337 cycles, IC 90 % [-3574 ; +3362] $
- M9 fin de cycle cote acquis : +152 $ sur 112 cycles, IC 90 % [-52 ; +326] $

Sélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.


## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)

Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : 646. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).

| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |
|---|---|---|---|---|
| FAST : preneur exécuté 164 ms après le signal | 1923 | 71938 $ | +7827 $ [IC 90 % -2712 ; +18516] | +0.11 |
| SLOW : preneur exécuté 1,164 s après (offre persistante) | 1210 | 52827 $ | +1770 $ [IC 90 % -8315 ; +12772] | +0.03 |
| HYBRID : FAST sinon SLOW (règle fixée avant) | 1959 | 73571 $ | +9157 $ [IC 90 % -1671 ; +20969] | +0.12 |
| C : moteur alpha exécutable (exécution mesurée à 300 ms) | 175 | — | +1352 $ | — |
| M1 : offre posée au signal (prudent ; proportionnel +4525 $) | 28877 | 180307 $ | +2797 $ | +0.02 |
| M2 marge 5 c (prudent ; proportionnel +17421 $) | 5055 | 117244 $ | +18113 $ | +0.15 |
| M2 marge 10 c (prudent ; proportionnel +13284 $) | 4414 | 101180 $ | +14338 $ | +0.14 |
| M0 témoin aléatoire (prudent ; proportionnel +2857 $) | 1063 | 43275 $ | +2516 $ | +0.06 |
| M3 anticipation Chainlink (prudent ; proportionnel +8837 $) | 4167 | 85822 $ | +8972 $ | +0.10 |
| M4 retrait toxique (prudent ; proportionnel +66623 $) | 22993 | 460283 $ | +67133 $ | +0.15 |
| M5 remplissage attendu (prudent ; proportionnel +19290 $) | 9294 | 174488 $ | +20755 $ | +0.12 |

Période hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.


## Limites
- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.
- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.
- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.
- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.
