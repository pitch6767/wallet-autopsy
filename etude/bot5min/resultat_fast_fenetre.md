# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 11.10.2026 12:23 UTC. 42 cycles de Dublin, avant la période réservée (13.10.2026 00:00 UTC). Paramètres fixés avant mesure : trajet simple 14 ms, calcul 0.2 ms, retard preneur 150 ms.

Données exclues ou douteuses : cycle coupé (limite d'événements) 3

## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)

| Cause | Nombre | Part |
|---|---|---|
| consommé | 2413 | 17 % |
| mixte | 104 | 1 % |
| retiré | 6580 | 46 % |
| déplacé | 2633 | 19 % |
| indéterminé | 2496 | 18 % |

« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.

## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)

Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. « Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.

**sans retard preneur (référence théorique)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 96 % (11358) | 99 % (2011) | 98 % (7475) | 99 % (82) | 100 % |
| 100 ms | 97 % (10918) | 99 % (2020) | 99 % (7221) | 100 % (76) | 100 % |
| 150 ms | 98 % (10745) | 99 % (1994) | 99 % (7049) | 99 % (73) | 100 % |
| 200 ms | 98 % (10548) | 99 % (1980) | 99 % (6883) | 99 % (70) | 100 % |
| 300 ms | 98 % (10168) | 99 % (1915) | 99 % (6621) | 100 % (71) | 100 % |
| 500 ms | 98 % (9689) | 99 % (1827) | 99 % (6259) | 100 % (72) | 100 % |

**retard 50 ms (réglage du 17.08 au 04.09)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (11358) | 0 % (2011) | 0 % (7475) | 0 % (82) | 0 % |
| 100 ms | 94 % (10918) | 96 % (2020) | 95 % (7221) | 96 % (76) | 100 % |
| 150 ms | 94 % (10745) | 97 % (1994) | 96 % (7049) | 100 % (73) | 100 % |
| 200 ms | 95 % (10548) | 97 % (1980) | 97 % (6883) | 99 % (70) | 100 % |
| 300 ms | 95 % (10168) | 98 % (1915) | 98 % (6621) | 100 % (71) | 100 % |
| 500 ms | 96 % (9689) | 98 % (1827) | 98 % (6259) | 99 % (72) | 100 % |

**retard 150 ms (réglage actuel)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (11358) | 0 % (2011) | 0 % (7475) | 0 % (82) | 0 % |
| 100 ms | 0 % (10918) | 0 % (2020) | 0 % (7221) | 0 % (76) | 0 % |
| 150 ms | 0 % (10745) | 0 % (1994) | 0 % (7049) | 0 % (73) | 0 % |
| 200 ms | 92 % (10548) | 94 % (1980) | 94 % (6883) | 97 % (70) | 73 % |
| 300 ms | 93 % (10168) | 95 % (1915) | 95 % (6621) | 96 % (71) | 96 % |
| 500 ms | 94 % (9689) | 97 % (1827) | 96 % (6259) | 97 % (72) | 100 % |

Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple 14 ms + calcul + retard preneur 150 ms ≈ **164 ms**.

## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)

Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède (saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).

| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |
|---|---|---|---|---|---|
| toutes | 10866 | 967 (9 %) | 84 / 418 / 846 | 757 (7 %) | 588 (5 %) |
| consommées | 2281 | 228 (10 %) | 93 / 370 / 846 | 176 (8 %) | 127 (6 %) |
| retirées / déplacées | 8488 | 712 (8 %) | 76 / 432 / 847 | 559 (7 %) | 442 (5 %) |
| mixtes | 97 | 27 (28 %) | 126 / 662 / 796 | 22 (23 %) | 19 (20 %) |

**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin (1484 cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms dans 24 % des cas ; à des instants tirés au hasard (témoin) : 16 %.


C'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.

## 4. Vérification indirecte du retard preneur sur nos marchés

Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = 1035) : p10 / p50 / p90 = 24 / 179 / 590 ms ; jusqu'au 1er retrait (n = 854) : 8 / 76 / 438 ms. Transactions moins de 150 ms après NOTRE information : 43 %. Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).

## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)

Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).

| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 3 | 0 | 3 (100 %) | 3 (100 %) | 148 | 1735 |
| M1 V2-F ecart qui grandit | 2 | 0 | 2 (100 %) | 2 (100 %) | 37 | 400 |
| M1 V2-F incertitude 0,01 % | 2 | 0 | 0 (0 %) | 0 (0 %) | 638 | nan |
| M1 cohorte A : zone + modele monte | 1 | 0 | 0 (0 %) | 0 (0 %) | 0 | nan |
| M1 cohorte B : V2-F corrige 0,015 % | 2 | 0 | 0 (0 %) | 0 (0 %) | 638 | nan |
| M1 desaccord 20 60-180 s | 2 | 0 | 2 (100 %) | 2 (100 %) | 206 | 1351 |
| M1 desaccord 30 | 1 | 0 | 0 (0 %) | 0 (0 %) | 104 | nan |
| M2 cotation marge 10 c | 303 | 4 | 16 (5 %) | 13 (4 %) | 40 | 272 |
| M2 cotation marge 5 c | 277 | 0 | 9 (3 %) | 8 (3 %) | 39 | 197 |
| M3 anticipation Chainlink | 112 | 1 | 6 (5 %) | 6 (5 %) | 40 | 136 |
| M4 retrait toxique | 336 | 6 | 38 (11 %) | 32 (10 %) | 60 | 432 |
| M5 remplissage attendu | 69 | 1 | 17 (25 %) | 14 (20 %) | 89 | 107 |

Offres remplies et réglées (fichier bot95/rapide_maker.json) :

| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |
|---|---|---|---|---|---|---|---|
| M1 V2-F ecart qui grandit | 9 | 1525 / 1525 | 354 $ | -146 $ | -146 $ | -0.41 | — / — / — / — |
| M1 V2-F incertitude 0,01 % | 8 | 548 / 548 | 150 $ | -74 $ | -74 $ | -0.49 | — / — / — / — |
| M1 cohorte A : zone + modele monte | 3 | 670 / 670 | 100 $ | +212 $ | +212 $ | +2.13 | — / — / — / — |
| M1 cohorte B : V2-F corrige 0,015 % | 8 | 1622 / 1622 | 250 $ | -250 $ | -250 $ | -1.00 | — / — / — / — |
| M1 desaccord 20 60-180 s | 8 | 2576 / 2576 | 350 $ | +29 $ | +29 $ | +0.08 | — / — / — / — |
| M1 desaccord 30 | 9 | 2559 / 2559 | 350 $ | +330 $ | +330 $ | +0.94 | — / — / — / — |
| M2 cotation marge 10 c | 36 | 1951 / 1986 | 680 $ | -56 $ | -58 $ | -0.08 | — / — / — / — |
| M2 cotation marge 5 c | 41 | 2125 / 1990 | 802 $ | -65 $ | -78 $ | -0.08 | — / — / — / — |

Sélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.


## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)

Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : 9. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).

| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |
|---|---|---|---|---|
| FAST : preneur exécuté 164 ms après le signal | 34 | 1280 $ | +394 $ | +0.31 |
| SLOW : preneur exécuté 1,164 s après (offre persistante) | 29 | 1103 $ | +252 $ | +0.23 |
| HYBRID : FAST sinon SLOW (règle fixée avant) | 36 | 1380 $ | +699 $ | +0.51 |
| C : moteur alpha exécutable (exécution mesurée à 300 ms) | 2 | — | +336 $ | — |
| M1 : offre posée au signal (prudent ; proportionnel +101 $) | 45 | 1554 $ | +101 $ | +0.06 |
| M2 marge 5 c (prudent ; proportionnel -78 $) | 41 | 802 $ | -65 $ | -0.08 |
| M2 marge 10 c (prudent ; proportionnel -58 $) | 36 | 680 $ | -56 $ | -0.08 |
| M0 témoin aléatoire (prudent ; proportionnel +0 $) | 0 | 0 $ | +0 $ | +nan |
| M3 anticipation Chainlink (prudent ; proportionnel +0 $) | 0 | 0 $ | +0 $ | +nan |
| M4 retrait toxique (prudent ; proportionnel +0 $) | 0 | 0 $ | +0 $ | +nan |
| M5 remplissage attendu (prudent ; proportionnel +0 $) | 0 | 0 $ | +0 $ | +nan |

Période hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.


## Limites
- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.
- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.
- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.
- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.
