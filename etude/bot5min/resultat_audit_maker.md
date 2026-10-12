# Bot95 — Audit complémentaire maker (M4a/b/c, M6, M8, file d'attente) — DIAGNOSTIC, pas un verdict

Généré le 12.10.2026 19:08 UTC. 335 cycles enregistrés avec la version du 11.10 14:55, avant la période réservée (13.10.2026 00:00 UTC). Aucun fantôme, paramètre ou bot modifié ; aucun ordre.

**Statut** — MESURE : heures, files affichées, transactions, prix. SIMULATION : remplissages (3 bornes de file) et résultats. CONTREFACTUEL : recalcul hors ligne, jamais des remplissages réels. HYPOTHÈSE : retard preneur 150 ms (documentation, non mesuré). Intervalles à 90 % par rééchantillonnage des CYCLES. Moins de 30 remplissages = INSUFFISANT.

## 2. M4 — les huit combinaisons a / b / c sur les mêmes opportunités

Base commune : chaque offre posée par M2 marge 5 c (même prix que M4, aucun retrait) est une opportunité. Pour chaque REMPLISSAGE de M2, on regarde quelles conditions l'auraient évité (déclenchée entre 2 s et le trajet de l'annulation avant le remplissage), avec les seules données reçues avant. Les 8 lignes partitionnent donc les mêmes remplissages : aucune comparaison entre fantômes différents.

| a | b | c | Opportunités (offres posées) | Cotations actives | Remplissages | Parts | Sélection adverse +1/+3/+5/+10 s (c/part) | Victoire finale | Résultat | IC 90 % | Bons remplissages perdus si on retire |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Non | Non | Non | 63253 | 62912 | 1140 | 33839 | -0.6 / -0.3 / -0.1 / +0.6 | 40 % | +1771 $ | [-93 ; +3631] | — |
| Oui | Non | Non | 958 | 948 | 42 | 2343 | -1.6 / +0.8 / -0.0 / +2.1 | 46 % | +351 $ | [-241 ; +979] | 20 |
| Non | Oui | Non | 4390 | 4366 | 139 | 6383 | -0.9 / -1.6 / -1.6 / -1.6 | 25 % | -385 $ | [-1035 ; +374] | 37 |
| Non | Non | Oui | 27025 | 26875 | 629 | 21549 | -0.4 / -0.5 / -0.9 / -1.2 | 40 % | +877 $ | [-445 ; +2222] | 247 |
| Oui | Oui | Non | 1029 | 1016 | 47 | 3313 | -3.9 / -6.1 / -5.1 / -3.2 | 19 % | -564 $ | [-991 ; -96] | 15 |
| Oui | Non | Oui | 1397 | 1388 | 38 | 1728 | +0.4 / -0.1 / +0.6 / +1.2 | 32 % | -100 $ | [-437 ; +221] | 7 |
| Non | Oui | Oui | 3806 | 3766 | 152 | 5469 | -2.4 / -1.6 / -1.5 / -1.5 | 23 % | -610 $ | [-1222 ; +33] | 31 |
| Oui | Oui | Oui | 2813 | 2778 | 146 | 7790 | -1.0 / -0.3 / +1.0 / -0.8 | 28 % | -373 $ | [-1115 ; +379] | 44 |

Remplissages de M2 marge 5 c analysés : 2333 — à lire avec prudence.

**Effet marginal de chaque condition** (sur les mêmes remplissages : résultat des remplissages qu'elle seule ferait éviter, et ceux évités par elle quelle que soit la combinaison) :

- a : seule → 42 remplissages évités, +351 $ ; au total → 273 remplissages évités, -686 $ (dont 86 gagnants perdus).
- b : seule → 139 remplissages évités, -385 $ ; au total → 484 remplissages évités, -1933 $ (dont 127 gagnants perdus).
- c : seule → 629 remplissages évités, +877 $ ; au total → 965 remplissages évités, -207 $ (dont 329 gagnants perdus).

Interaction = résultat des lignes à plusieurs conditions comparé à la somme des lignes à une condition. Une condition active sur un remplissage gagnant ou perdant ne prouve rien à elle seule : seul l'écart contre le contrefactuel aléatoire (section 3) mesure une capacité de prédiction.

**Comparaison directe des fantômes** (même prix, mêmes cycles, chacun simulé seul) :

| Fantôme | Remplissages | Parts | Résultat prudent | IC 90 % | Sélection adverse +3 s |
|---|---|---|---|---|---|
| M2 cotation marge 5 c | 1439 | 82587 | +925 $ | [-1717 ; +3723] | -0.8 c |
| M4 retrait toxique | 1954 | 94960 | +827 $ | [-2057 ; +4134] | -0.2 c |
| M4a seul bourses -10 $ | 1633 | 88597 | +1692 $ | [-1273 ; +4713] | -0.6 c |
| M4b seul flux agressif | 1713 | 89274 | +1336 $ | [-1588 ; +4408] | -0.6 c |
| M4c seul ventes Polymarket | 1794 | 93973 | -1816 $ | [-4518 ; +980] | -0.6 c |
| M0 temoin aleatoire | 341 | 62257 | -3373 $ | [-4838 ; -1889] | -1.6 c |

## 3. Contrôles contre les faux gains (CONTREFACTUELS hors ligne, base : remplissages de M2 marge 5 c)

| Contrefactuel | Remplissages gardés | Parts | Résultat |
|---|---|---|---|
| B. M4 sans annulations (= M2 marge 5 c) | 2333 | 82414 | +965 $ |
| A. M4 complet (recalculé) | 1140 | 33839 | +1771 $ |
| C. M4 annulations retardées de 100 ms | 1219 | 36693 | +2087 $ |
| C. M4 annulations retardées de 300 ms | 1326 | 41923 | +1339 $ |
| C. M4 annulations retardées de 1000 ms | 1493 | 48401 | +15 $ |
| D. Annulations aléatoires, même fréquence de retrait (40 % des poses) — 300 tirages | — | — | médiane +637 $ [p5 -510 ; p95 +1765] |
| E. Même durée de présence : mêmes nombres de pauses de 2 s placées au hasard — 300 tirages | — | — | médiane +1184 $ [p5 +222 ; p95 +2128] |
| F. Mêmes horaires, autres prix de cotation | — | — | NON CALCULABLE de façon fiable hors ligne : la file aux autres prix n'est enregistrée qu'à ±3 c du meilleur prix (proposé comme fantôme après le verdict) |

**Lecture** : M4 recalculé garde +1771 $ ; des retraits au hasard de même durée gardent +1184 $ en médiane. Part des tirages aléatoires au moins aussi bons que M4 : 13 %. Si cette part est faible (< 5 %), M4 prédit vraiment la toxicité ; sinon son avantage peut venir d'une simple exposition réduite.

Validation de la méthode : le résultat « A recalculé » doit être proche du fantôme M4 réel (section 2) ; un écart signale une différence de calcul des conditions.

## 4. M6 — durée de vie des cotations

| Variante | Ordres posés | Remplacements | Temps réellement actif (min) | Attente d'annulation (s) | Délai confirmation → nouvelle pose (médiane ms) | Remplissages pendant l'annulation (parts) | Remplissages partiels | Parts | Résultat prudent | par ordre posé | par minute d'exposition | par $ exécuté | Capital immobilisé moyen ($ posés) | Bons remplissages manqués vs M2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 104671 | 0 | 890.0 | 0.0 | nan | 42049 | 582 | 82587 | +925 $ | +0.009 $ | +1.04 $ | +0.03 | 26.6 $ | — |
| M6 duree de vie 100 ms | 455214 | 377385 | 659.0 | 13206.9 | 3 | 75170 | 734 | 112505 | -1267 $ | -0.003 $ | -1.92 $ | -0.03 | 19.7 $ | 0 |
| M6 duree de vie 250 ms | 256989 | 159718 | 815.5 | 5722.9 | 3 | 74388 | 783 | 113519 | -860 $ | -0.003 $ | -1.06 $ | -0.02 | 24.3 $ | 0 |
| M6 duree de vie 500 ms | 178135 | 73855 | 891.6 | 2749.7 | 3 | 69699 | 782 | 111590 | +224 $ | +0.001 $ | +0.25 $ | +0.01 | 26.6 $ | 0 |
| M6 duree de vie 1000 ms | 135828 | 29115 | 918.1 | 1182.8 | 3 | 62144 | 738 | 100993 | +113 $ | +0.001 $ | +0.12 $ | +0.00 | 27.4 $ | 0 |

Une durée courte n'est pas meilleure parce qu'elle évite des remplissages toxiques : il faut regarder le résultat par minute d'exposition et les bons remplissages manqués. La perte de priorité par remplacement est détaillée dans resultat_verifications_h559.md (section 2).

## 5. File d'attente — huit contrôles

Offres remplies contrôlées : 31996 (indéterminées faute de transactions enregistrées : 0).

- 1. prudent > central : **7193**
- 2. central > optimiste : **0**
- 3. 1er remplissage prudent AVANT le central (ordre de priorité) : **2686**
- 5. parts remplies > volume échangé à notre prix : **4**
- 6. remplissage avant l'arrivée de l'offre : **0**
- 7. annulée sans heure effective : **0**
- 8. remplissage après l'annulation effective : **0**
- 4. double comptage d'un retrait entre fantômes : corrigé dans le code le 11.10 à 14:55 (une seule attribution transaction / retrait par baisse du niveau, partagée par tous les fantômes) ; les remplissages d'avant ne sont pas utilisés ici. Les fantômes restent simulés SEULS face au carnet : leurs résultats ne s'additionnent pas.

Défaut connu (contrôle 1) : seule la borne prudente est plafonnée à la quantité affichée ; la centrale et l'optimiste ne le sont pas. Fantômes gelés : pas de correction avant le verdict. Annulation : effective chez Polymarket après le trajet simple (≈ 15 ms) ; un remplissage entre la demande et cet instant est compté (comme en réel). Aucune de ces bornes n'est notre position réelle dans la file.

## 6. M8 — routeur maker / preneur

Formule actuelle (code gelé) — PRENEUR : parts disponibles au prix vu (50 $) × probabilité du modèle − coût frais compris ; le retard de 150 ms et la disparition de l'offre n'entrent PAS dans la décision (seulement dans l'exécution simulée). MAKER : parts attendues en 10 s × (probabilité du modèle − prix − 2 c) ; ce n'est PAS « probabilité de remplissage × gain conditionnel au remplissage » : la sélection adverse est une constante (2 c) au lieu de la probabilité de victoire SACHANT le remplissage. Abstention : oui, si aucune voie n'a une espérance positive (preneur) ou ≥ 0,50 $ (maker). **Non conforme à la formule demandée** ; version conforme proposée après le verdict, M8 actuel inchangé.

| Décision | Nombre | Remplies | Parts | Résultat prudent | Jackpots (≤ 0,25 gagnés) | Creux |
|---|---|---|---|---|---|---|
| preneur | 239 | 126 | 15583 | -1146 $ | 8 | -1320 $ |
| maker | 562 | 389 | 137555 | +260 $ | 50 | -3243 $ |
| abstention | 401 (signaux sans décision M8) | — | — | — | — | — |

## 7–8. Comparaison des moteurs sur les mêmes cycles (délai preneur : plusieurs scénarios)

Cycles communs : 202. FAST / SLOW / HYBRID : achat preneur de 50 $ au prix du signal ou mieux, frais 0,07·p·(1−p), aux délais 0 / 50 / 150 / 250 ms (150 = HYPOTHÈSE documentée).

| Moteur | Positions | $ engagés (capital) | Prix moyen | Frais | Résultat | IC 90 % | Sélection adverse +3 s (c/part) | Creux max | Pire série de pertes | Jackpots |
|---|---|---|---|---|---|---|---|---|---|---|
| FAST (délai 0 ms) | 802 | 18615 $ | 0.225 | 982 $ | -1023 $ | [-4855 ; +2906] | +nan | -2758 $ | 57 | 76 |
| FAST (délai 50 ms) | 745 | 20651 $ | 0.220 | 1101 $ | -480 $ | [-5218 ; +4384] | +nan | -2722 $ | 56 | 71 |
| FAST (délai 150 ms) | 624 | 19931 $ | 0.212 | 1080 $ | -254 $ | [-5147 ; +5111] | +nan | -1907 $ | 44 | 62 |
| SLOW (délai 150 ms) | 397 | 15362 $ | 0.188 | 860 $ | -1324 $ | [-5560 ; +3345] | +nan | -2458 $ | 48 | 38 |
| HYBRID (délai 150 ms) | 647 | 20856 $ | 0.211 | 1131 $ | -344 $ | [-5565 ; +5018] | +nan | -2037 $ | 44 | 64 |
| FAST (délai 250 ms) | 531 | 18085 $ | 0.203 | 993 $ | +88 $ | [-4788 ; +4966] | +nan | -1836 $ | 41 | 56 |
| M0 témoin (prudent) | 267 | 13097 $ | 0.475 | 0 $ | -3208 $ | [-4647 ; -1676] | -2.3 | -3446 $ | 9 | 4 |
| M1 maker sur signal (prudent) | 1961 | 50141 $ | 0.382 | 0 $ | -511 $ | [-7572 ; +7302] | -0.8 | -4412 $ | 24 | 102 |
| M2 marge 5 c (prudent) | 1043 | 26025 $ | 0.360 | 0 $ | +2199 $ | [-502 ; +4838] | -0.7 | -1148 $ | 19 | 30 |
| M4 (prudent) | 1360 | 25937 $ | 0.314 | 0 $ | +2020 $ | [-954 ; +5067] | -0.2 | -1059 $ | 27 | 71 |
| M4a (prudent) | 1169 | 26276 $ | 0.342 | 0 $ | +2915 $ | [-117 ; +5842] | -0.5 | -987 $ | 18 | 55 |
| M4b (prudent) | 1189 | 25887 $ | 0.339 | 0 $ | +2783 $ | [-52 ; +5676] | -0.5 | -1472 $ | 17 | 50 |
| M4c (prudent) | 1282 | 25567 $ | 0.316 | 0 $ | -217 $ | [-2843 ; +2500] | -0.5 | -1747 $ | 28 | 51 |
| M6 100 ms (prudent) | 1256 | 32648 $ | 0.353 | 0 $ | +1283 $ | [-2426 ; +4798] | -0.9 | -1452 $ | 30 | 38 |
| M6 250 ms (prudent) | 1353 | 34095 $ | 0.344 | 0 $ | +824 $ | [-2965 ; +4604] | -0.9 | -1724 $ | 40 | 43 |
| M6 500 ms (prudent) | 1342 | 33654 $ | 0.349 | 0 $ | +2174 $ | [-1743 ; +6145] | -0.9 | -1573 $ | 37 | 40 |
| M6 1000 ms (prudent) | 1283 | 30717 $ | 0.352 | 0 $ | +1772 $ | [-1503 ; +5122] | -0.8 | -1448 $ | 35 | 34 |
| M8 routeur (prudent) | 515 | 21909 $ | 0.196 | 0 $ | -885 $ | [-6540 ; +4988] | +2.1 | -3531 $ | 33 | 58 |
| M8b routeur corrigé (prudent) | 480 | 20875 $ | 0.191 | 0 $ | -1136 $ | [-6866 ; +5075] | +2.0 | -3618 $ | 33 | 54 |
| M9 fin de cycle (prudent) | 48 | 1839 $ | 0.946 | 0 $ | +100 $ | [+76 ; +125] | -1.1 | +0 $ | 0 | 0 |
| M10 double maker (prudent) | 1433 | 25091 $ | 0.455 | 0 $ | +1546 $ | [-509 ; +3621] | -0.8 | -643 $ | 13 | 43 |
| M11 zone maker (prudent) | 21 | 229 $ | 0.183 | 0 $ | -61 $ | [-289 ; +186] | -0.9 | -172 $ | 13 | 2 |
| M21 maker du favori (prudent) | 914 | 18762 $ | 0.639 | 0 $ | -541 $ | [-1645 ; +555] | -1.2 | -931 $ | 9 | 0 |

**Résultat marginal contre M4 et contre M0 (différence par cycle, IC 90 %)** :

- FAST 0 − M4 : -3043 $ [-6971 ; +611]
- FAST 0 − M0 témoin : +2185 $ [-1704 ; +6231]
- FAST 50 − M4 : -2500 $ [-6944 ; +1832]
- FAST 50 − M0 témoin : +2728 $ [-1787 ; +7509]
- FAST 150 − M4 : -2274 $ [-6670 ; +2067]
- FAST 150 − M0 témoin : +2955 $ [-1849 ; +7873]
- SLOW 150 − M4 : -3343 $ [-7625 ; +735]
- SLOW 150 − M0 témoin : +1885 $ [-2175 ; +6314]
- HYBRID 150 − M4 : -2364 $ [-6934 ; +2179]
- HYBRID 150 − M0 témoin : +2864 $ [-2118 ; +7992]
- FAST 250 − M4 : -1932 $ [-6417 ; +2279]
- FAST 250 − M0 témoin : +3296 $ [-1451 ; +8041]
- M1 maker sur signal − M4 : -2531 $ [-8550 ; +3670]
- M1 maker sur signal − M0 témoin : +2697 $ [-4523 ; +10414]
- M2 marge 5 c − M4 : +179 $ [-2624 ; +2644]
- M2 marge 5 c − M0 témoin : +5407 $ [+2622 ; +8385]
- M4a − M4 : +895 $ [-1410 ; +3004]
- M4a − M0 témoin : +6123 $ [+2985 ; +9265]
- M4b − M4 : +763 $ [-1659 ; +2925]
- M4b − M0 témoin : +5991 $ [+2897 ; +9189]
- M4c − M4 : -2237 $ [-4758 ; -93]
- M4c − M0 témoin : +2991 $ [+7 ; +6001]
- M6 100 ms − M4 : -737 $ [-4368 ; +2442]
- M6 100 ms − M0 témoin : +4491 $ [+647 ; +8147]
- M6 250 ms − M4 : -1196 $ [-4925 ; +2146]
- M6 250 ms − M0 témoin : +4032 $ [-22 ; +8005]
- M6 500 ms − M4 : +154 $ [-3216 ; +3357]
- M6 500 ms − M0 témoin : +5382 $ [+1238 ; +9356]
- M6 1000 ms − M4 : -248 $ [-3386 ; +2683]
- M6 1000 ms − M0 témoin : +4980 $ [+1471 ; +8534]
- M8 routeur − M4 : -2905 $ [-7931 ; +2284]
- M8 routeur − M0 témoin : +2323 $ [-3585 ; +8731]
- M8b routeur corrigé − M4 : -3156 $ [-8316 ; +1971]
- M8b routeur corrigé − M0 témoin : +2072 $ [-3794 ; +8283]
- M9 fin de cycle − M4 : -1920 $ [-4963 ; +1037]
- M9 fin de cycle − M0 témoin : +3308 $ [+1838 ; +4696]
- M10 double maker − M4 : -474 $ [-3551 ; +2321]
- M10 double maker − M0 témoin : +4754 $ [+2277 ; +7202]
- M11 zone maker − M4 : -2081 $ [-5210 ; +896]
- M11 zone maker − M0 témoin : +3147 $ [+1697 ; +4505]
- M21 maker du favori − M4 : -2561 $ [-5931 ; +724]
- M21 maker du favori − M0 témoin : +2667 $ [+761 ; +4478]

**Par temps restant à la pose (makers, prudent)** :

| Moteur | 180–300 s | 60–180 s | 0–60 s |
|---|---|---|---|
| M0 | -747 $ (127) | -2278 $ (135) | -183 $ (5 — insuffisant) |
| M1 | +1919 $ (1528) | -2469 $ (398) | +39 $ (35) |
| M2 5 c | +2793 $ (924) | -605 $ (115) | +11 $ (4 — insuffisant) |
| M4 | +1921 $ (1018) | +421 $ (319) | -322 $ (23 — insuffisant) |
| M5 | +5190 $ (1541) | -1255 $ (280) | +4 $ (2 — insuffisant) |
| M6 1000 ms | +2466 $ (1116) | -699 $ (163) | +5 $ (4 — insuffisant) |
| M8 | -59 $ (219) | -1684 $ (708) | -278 $ (68) |

## 9–10. Limites
- Données d'une seule journée pour la version du 11.10 14:55 : la plupart des lignes sont INSUFFISANTES.
- Remplissages simulés (trois bornes), jamais des exécutions réelles ; retard preneur de 150 ms non mesuré (test réel de 1 $ soumis à ton accord).
- Les fantômes sont simulés seuls : leurs résultats ne s'additionnent pas.
- Aucune règle n'a été réglée sur ces chiffres ; la période réservée du 13.10 n'est pas lue.
