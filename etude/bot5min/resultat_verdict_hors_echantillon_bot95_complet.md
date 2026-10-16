# Bot95 — verdict hors échantillon : récapitulatif par variante maker

Généré le 16.10.2026 07:53 UTC. Fichier bot95/rapide_maker.json (sauvegarde du dépôt). Offres réglées hors échantillon : cycles du 13.10 00:00 au 16.10 07:35 UTC (877 cycles avec au moins une offre réglée). Remplissages SIMULÉS (borne prudente), aucun ordre réel.

Résultat prudent en $ ; IC 90 % par rééchantillonnage des cycles (2 000 tirages) ; creux = pire baisse cumulée ; sélection adverse = milieu du carnet h s après le remplissage moins notre prix (c par part, négatif = contre nous).

| Variante | Remplissages | Parts | $ engagés | Résultat prudent | IC 90 % | Central | Creux | Sélection adverse +1/+3/+5/+10 s | Écart à M0 (même cycles) [IC 90 %] | Avant le 13.10 (prudent) [IC 90 %] |
|---|---|---|---|---|---|---|---|---|---|---|
| M0 témoin aléatoire | 1068 | 208647 | 52364 $ | -5 $ | [-4153 ; +4405] | +320 $ | -3300 $ | -1.7 / -1.7 / -1.7 / -1.6 | — | -4028 $ [-5692 ; -2347] |
| M1 offre au signal (toutes cohortes) | 1284 | 524714 | 62493 $ | -680 $ | [-11237 ; +9501] | -892 $ | -5380 $ | -1.0 / -1.1 / -0.9 / +0.1 | -675 [-11144 ; +10054] | +373 $ [-7019 ; +8169] |
| M2 marge 5 c | 5545 | 453917 | 150732 $ | +2012 $ | [-7471 ; +12199] | +1140 $ | -6224 $ | -1.2 / -1.1 / -1.0 / -0.7 | +2017 [-8100 ; +12368] | +340 $ [-2565 ; +3326] |
| M2 marge 10 c | 4592 | 501104 | 121805 $ | -1463 $ | [-11466 ; +9102] | -2153 $ | -5139 $ | -1.0 / -0.8 / -0.7 / -0.7 | -1458 [-11804 ; +9332] | +612 $ [-3093 ; +4493] |
| M4 retrait toxique | 6251 | 478873 | 141121 $ | +1303 $ | [-6804 ; +9383] | +657 $ | -5897 $ | -0.8 / -0.8 / -0.7 / -0.5 | +1308 [-7669 ; +10189] | +930 $ [-3323 ; +5539] |
| M5 remplissage attendu | 11179 | 714420 | 224510 $ | -1136 $ | [-14023 ; +13358] | +331 $ | -8962 $ | -1.0 / -1.1 / -1.1 / -1.2 | -1131 [-14753 ; +13275] | +1138 $ [-3719 ; +6617] |
| M8 hybride (toutes cohortes) | 1303 (preneur 421, maker 882) | 398243 | 55384 $ | +10647 $ | [+738 ; +20788] | +10294 $ | -2186 $ | -0.3 / -0.2 / -0.1 / +1.0 | +10652 [+929 ; +20995] | -1266 $ [-7396 ; +5674] |
| M8b routeur corrigé (toutes cohortes) | 1280 (preneur 352, maker 928) | 402457 | 54950 $ | +9010 $ | [-820 ; +19294] | +8703 $ | -2594 $ | -0.4 / -0.4 / -0.3 / +1.0 | +9015 [-945 ; +19456] | -1517 $ [-7699 ; +4597] |
| M3 anticipation Chainlink | 4484 | 404575 | 107959 $ | +2656 $ | [-4862 ; +10169] | +2813 $ | -3076 $ | +0.6 / +0.6 / +0.7 / +1.0 | +2661 [-4828 ; +9708] | +1039 $ [-2135 ; +4624] |
| M10 double maker | 8503 | 393925 | 164139 $ | -4589 $ | [-11569 ; +2928] | -2259 $ | -7689 $ | -1.1 / -1.1 / -1.1 / -1.1 | -4584 [-12316 ; +3699] | -207 $ [-2666 ; +2360] |

## Moteur C (preneur, exécution à 300 ms) : tous les signaux réglés de la période réservée

| Période | Signaux avec résultat | Trades exécutés | $ engagés | Résultat | IC 90 % | Creux |
|---|---|---|---|---|---|---|
| ≥ 13.10.2026 (hors échantillon) | 227 | 177 | 8228 $ | +1252 $ | [-344 ; +3029] | -627 $ |
| avant le 13.10 | 111 | 76 | 3378 $ | +765 $ | [-125 ; +1813] | -531 $ |

## FAST / SLOW / HYBRID (preneur) : recalcul descriptif avec les fonctions figées de fast_fenetre.py

646 cycles avec signaux réglés. Totaux identiques attendus à resultat_fast_fenetre_hors_echantillon.md section 6 ; ajoute parts et creux.

| Stratégie | Trades | Parts | $ engagés | Résultat | IC 90 % | par $ | Creux |
|---|---|---|---|---|---|---|---|
| FAST | 1923 | 474240 | 71938 $ | +7827 $ | [-2712 ; +18516] | +0.11 | -3173 $ |
| SLOW | 1210 | 427436 | 52827 $ | +1770 $ | [-8315 ; +12772] | +0.03 | -8290 $ |
| HYBRID | 1959 | 485735 | 73571 $ | +9157 $ | [-1671 ; +20969] | +0.12 | -3640 $ |

## Lecture

- M0 témoin aléatoire : non démontré (l'IC contient 0).
- M1 offre au signal (toutes cohortes) : non démontré (l'IC contient 0).
- M2 marge 5 c : non démontré (l'IC contient 0).
- M2 marge 10 c : non démontré (l'IC contient 0).
- M4 retrait toxique : non démontré (l'IC contient 0).
- M5 remplissage attendu : non démontré (l'IC contient 0).
- M8 hybride (toutes cohortes) : gain démontré (IC entièrement au-dessus de 0).
- M8b routeur corrigé (toutes cohortes) : non démontré (l'IC contient 0).
- M3 anticipation Chainlink : non démontré (l'IC contient 0).
- M10 double maker : non démontré (l'IC contient 0).

## Limites
- Sauvegarde maker réparée : offres réglées couvrant toute la période réservée jusqu'au cycle du 16.10.2026 07:35 UTC.
- Remplissages simulés (file d'attente reconstituée), pas des exécutions réelles ; retard preneur de 150 ms supposé, non mesuré.
- Variantes testées en parallèle sur les mêmes cycles : avec une dizaine de variantes, un IC qui exclurait 0 de peu pourrait être dû au hasard.
