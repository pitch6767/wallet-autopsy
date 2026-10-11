# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 11.10.2026 12:41 UTC. 46 cycles de Dublin, avant la période réservée (13.10.2026 00:00 UTC). Paramètres fixés avant mesure : trajet simple 14 ms, calcul 0.2 ms, retard preneur 150 ms.

Données exclues ou douteuses : cycle coupé (limite d'événements) 3, cycles avec carnets Binance/Bybit 3

## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)

| Cause | Nombre | Part |
|---|---|---|
| consommé | 2658 | 17 % |
| mixte | 114 | 1 % |
| retiré | 7320 | 46 % |
| déplacé | 2926 | 18 % |
| indéterminé | 2821 | 18 % |

« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.

## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)

Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. « Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.

**sans retard preneur (référence théorique)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 96 % (12474) | 99 % (2196) | 98 % (8257) | 99 % (89) | 100 % |
| 100 ms | 97 % (11962) | 99 % (2200) | 99 % (7965) | 99 % (84) | 100 % |
| 150 ms | 98 % (11750) | 99 % (2170) | 99 % (7751) | 99 % (80) | 100 % |
| 200 ms | 97 % (11540) | 99 % (2151) | 99 % (7556) | 99 % (77) | 100 % |
| 300 ms | 98 % (11119) | 99 % (2077) | 99 % (7254) | 100 % (77) | 100 % |
| 500 ms | 98 % (10582) | 99 % (1983) | 99 % (6852) | 100 % (79) | 100 % |

**retard 50 ms (réglage du 17.08 au 04.09)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (12474) | 0 % (2196) | 0 % (8257) | 0 % (89) | 0 % |
| 100 ms | 94 % (11962) | 96 % (2200) | 95 % (7965) | 95 % (84) | 100 % |
| 150 ms | 94 % (11750) | 97 % (2170) | 96 % (7751) | 100 % (80) | 100 % |
| 200 ms | 95 % (11540) | 97 % (2151) | 97 % (7556) | 99 % (77) | 100 % |
| 300 ms | 95 % (11119) | 98 % (2077) | 98 % (7254) | 100 % (77) | 100 % |
| 500 ms | 96 % (10582) | 98 % (1983) | 98 % (6852) | 97 % (79) | 100 % |

**retard 150 ms (réglage actuel)**

| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |
|---|---|---|---|---|---|
| 50 ms | 0 % (12474) | 0 % (2196) | 0 % (8257) | 0 % (89) | 0 % |
| 100 ms | 0 % (11962) | 0 % (2200) | 0 % (7965) | 0 % (84) | 0 % |
| 150 ms | 0 % (11750) | 0 % (2170) | 0 % (7751) | 0 % (80) | 0 % |
| 200 ms | 92 % (11540) | 94 % (2151) | 94 % (7556) | 97 % (77) | 72 % |
| 300 ms | 93 % (11119) | 95 % (2077) | 95 % (7254) | 96 % (77) | 96 % |
| 500 ms | 94 % (10582) | 97 % (1983) | 96 % (6852) | 96 % (79) | 100 % |

Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple 14 ms + calcul + retard preneur 150 ms ≈ **164 ms**.

## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)

Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède (saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).

| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |
|---|---|---|---|---|---|
| toutes | 12056 | 1119 (9 %) | 81 / 443 / 847 | 876 (7 %) | 698 (6 %) |
| consommées | 2505 | 261 (10 %) | 88 / 374 / 859 | 197 (8 %) | 146 (6 %) |
| retirées / déplacées | 9444 | 827 (9 %) | 77 / 455 / 847 | 654 (7 %) | 530 (6 %) |
| mixtes | 107 | 31 (29 %) | 122 / 662 / 865 | 25 (23 %) | 22 (21 %) |

**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin (1686 cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms dans 24 % des cas ; à des instants tirés au hasard (témoin) : 16 %.


C'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.

## 4. Vérification indirecte du retard preneur sur nos marchés

Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = 1154) : p10 / p50 / p90 = 23 / 177 / 594 ms ; jusqu'au 1er retrait (n = 955) : 8 / 76 / 436 ms. Transactions moins de 150 ms après NOTRE information : 44 %. Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).

## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)

Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).

| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |
|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 8 | 1 | 5 (62 %) | 5 (62 %) | 425 | 812 |
| M1 V2-F ecart qui grandit | 4 | 1 | 3 (75 %) | 3 (75 %) | 74 | 767 |
| M1 V2-F incertitude 0,01 % | 4 | 0 | 0 (0 %) | 0 (0 %) | 638 | nan |
| M1 cohorte A : zone + modele monte | 2 | 0 | 0 (0 %) | 0 (0 %) | 0 | nan |
| M1 cohorte B : V2-F corrige 0,015 % | 4 | 0 | 1 (25 %) | 0 (0 %) | 638 | 182 |
| M1 desaccord 20 60-180 s | 5 | 0 | 4 (80 %) | 4 (80 %) | 367 | 2229 |
| M1 desaccord 30 | 3 | 1 | 1 (33 %) | 0 (0 %) | 76 | 202 |
| M2 cotation marge 10 c | 829 | 4 | 23 (3 %) | 23 (3 %) | 55 | 1212 |
| M2 cotation marge 5 c | 808 | 0 | 19 (2 %) | 19 (2 %) | 80 | 855 |
| M3 anticipation Chainlink | 357 | 4 | 14 (4 %) | 13 (4 %) | 89 | 97 |
| M4 retrait toxique | 856 | 6 | 64 (7 %) | 62 (7 %) | 90 | 560 |
| M5 remplissage attendu | 184 | 4 | 42 (23 %) | 32 (17 %) | 92 | 136 |

Offres remplies et réglées (fichier bot95/rapide_maker.json) :

| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |
|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 5 | 498 / 499 | 199 $ | +114 $ | +114 $ | +0.57 | +0.2 / -4.1 / -6.5 / +11.1 |
| M1 V2-F ecart qui grandit | 12 | 2266 / 2266 | 504 $ | +181 $ | +181 $ | +0.36 | -2.5 / -3.4 / -3.0 / -3.1 |
| M1 V2-F incertitude 0,01 % | 11 | 548 / 548 | 150 $ | -74 $ | -74 $ | -0.49 | — / — / — / — |
| M1 cohorte A : zone + modele monte | 4 | 670 / 670 | 100 $ | +212 $ | +212 $ | +2.13 | — / — / — / — |
| M1 cohorte B : V2-F corrige 0,015 % | 11 | 1622 / 1622 | 250 $ | -250 $ | -250 $ | -1.00 | — / — / — / — |
| M1 desaccord 20 60-180 s | 11 | 2822 / 2828 | 401 $ | +215 $ | +215 $ | +0.54 | -1.2 / +1.7 / +1.7 / -5.1 |
| M1 desaccord 30 | 11 | 2559 / 2559 | 350 $ | +330 $ | +330 $ | +0.94 | — / — / — / — |
| M2 cotation marge 10 c | 56 | 3031 / 3114 | 1036 $ | +117 $ | +151 $ | +0.11 | -3.2 / -7.9 / -8.2 / -8.0 |
| M2 cotation marge 5 c | 52 | 3174 / 3044 | 1195 $ | +120 $ | +111 $ | +0.10 | -4.9 / -9.2 / -10.1 / -10.7 |
| M3 anticipation Chainlink | 10 | 980 / 922 | 242 $ | +22 $ | -15 $ | +0.09 | +5.8 / +1.1 / -1.7 / +18.4 |
| M4 retrait toxique | 69 | 2805 / 2626 | 602 $ | +206 $ | +376 $ | +0.34 | -1.2 / -1.5 / -1.2 / -1.6 |
| M5 remplissage attendu | 25 | 1305 / 1375 | 428 $ | +82 $ | +86 $ | +0.19 | -1.3 / -4.8 / -4.0 / -4.8 |

**Par prix d'achat et temps restant (toutes variantes maker, prudent)**

| Prix | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0.00–0.20 | 57 | 1137 $ | +264 $ | +0.23 |
| 0.20–0.35 | 125 | 2050 $ | +1304 $ | +0.64 |
| 0.35–0.50 | 91 | 2072 $ | -274 $ | -0.13 |
| 0.50–0.65 | 1 | 50 $ | -50 $ | -1.00 |
| 0.65–1.00 | 3 | 149 $ | +31 $ | +0.21 |

| Temps restant à la pose | Offres remplies | $ exécutés | Résultat | par $ |
|---|---|---|---|---|
| 0–60 s | 3 | 100 $ | -100 $ | -1.00 |
| 60–120 s | 11 | 161 $ | -57 $ | -0.35 |
| 120–180 s | 49 | 879 $ | -641 $ | -0.73 |
| 180–300 s | 92 | 1282 $ | +2094 $ | +1.63 |
(temps restant enregistré seulement depuis la version du 11.10 13:55)


**Intervalle de confiance à 90 % du résultat prudent (rééchantillonnage par cycles)**

- M0 temoin aleatoire : +114 $ sur 3 cycles, IC 90 % [-97 ; +324] $
- M1 V2-F ecart qui grandit : +181 $ sur 12 cycles, IC 90 % [-305 ; +708] $
- M1 V2-F incertitude 0,01 % : -74 $ sur 11 cycles, IC 90 % [-200 ; +27] $
- M1 cohorte A : zone + modele monte : +212 $ sur 4 cycles, IC 90 % [-100 ; +738] $
- M1 cohorte B : V2-F corrige 0,015 % : -250 $ sur 11 cycles, IC 90 % [-400 ; -100] $
- M1 desaccord 20 60-180 s : +215 $ sur 11 cycles, IC 90 % [-224 ; +714] $
- M1 desaccord 30 : +330 $ sur 11 cycles, IC 90 % [-350 ; +1113] $
- M2 cotation marge 10 c : +117 $ sur 12 cycles, IC 90 % [-182 ; +413] $
- M2 cotation marge 5 c : +120 $ sur 12 cycles, IC 90 % [-224 ; +440] $
- M3 anticipation Chainlink : +22 $ sur 3 cycles, IC 90 % [-150 ; +193] $
- M4 retrait toxique : +206 $ sur 3 cycles, IC 90 % [-77 ; +489] $
- M5 remplissage attendu : +82 $ sur 3 cycles, IC 90 % [-9 ; +173] $

Sélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.


## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)

Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : 12. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).

| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |
|---|---|---|---|---|
| FAST : preneur exécuté 164 ms après le signal | 43 | 1638 $ | +928 $ [IC 90 % -467 ; +2498] | +0.57 |
| SLOW : preneur exécuté 1,164 s après (offre persistante) | 34 | 1323 $ | +593 $ [IC 90 % -877 ; +2192] | +0.45 |
| HYBRID : FAST sinon SLOW (règle fixée avant) | 45 | 1738 $ | +1233 $ [IC 90 % -455 ; +2928] | +0.71 |
| C : moteur alpha exécutable (exécution mesurée à 300 ms) | 3 | — | +355 $ | — |
| M1 : offre posée au signal (prudent ; proportionnel +614 $) | 60 | 1756 $ | +615 $ | +0.35 |
| M2 marge 5 c (prudent ; proportionnel +111 $) | 52 | 1195 $ | +120 $ | +0.10 |
| M2 marge 10 c (prudent ; proportionnel +151 $) | 56 | 1036 $ | +117 $ | +0.11 |
| M0 témoin aléatoire (prudent ; proportionnel +114 $) | 5 | 199 $ | +114 $ | +0.57 |
| M3 anticipation Chainlink (prudent ; proportionnel -15 $) | 10 | 242 $ | +22 $ | +0.09 |
| M4 retrait toxique (prudent ; proportionnel +376 $) | 69 | 602 $ | +206 $ | +0.34 |
| M5 remplissage attendu (prudent ; proportionnel +86 $) | 25 | 428 $ | +82 $ | +0.19 |

Période hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.


## Limites
- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.
- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.
- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.
- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.
