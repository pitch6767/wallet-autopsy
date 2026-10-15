# Bot95 — verdict hors échantillon : récapitulatif par variante maker

Généré le 15.10.2026 17:36 UTC. Fichier bot95/rapide_maker.json (sauvegarde du dépôt). Offres réglées hors échantillon : cycles du 13.10 00:00 au 14.10 07:50 UTC (346 cycles avec au moins une offre réglée). Remplissages SIMULÉS (borne prudente), aucun ordre réel.

Résultat prudent en $ ; IC 90 % par rééchantillonnage des cycles (2 000 tirages) ; creux = pire baisse cumulée ; sélection adverse = milieu du carnet h s après le remplissage moins notre prix (c par part, négatif = contre nous).

| Variante | Remplissages | Parts | $ engagés | Résultat prudent | IC 90 % | Central | Creux | Sélection adverse +1/+3/+5/+10 s | Écart à M0 (même cycles) [IC 90 %] | Avant le 13.10 (prudent) [IC 90 %] |
|---|---|---|---|---|---|---|---|---|---|---|
| M0 témoin aléatoire | 440 | 87402 | 21629 $ | +2595 $ | [-772 ; +6394] | +2817 $ | -1691 $ | -1.6 / -1.6 / -1.8 / -1.6 | — | -4028 $ [-5692 ; -2347] |
| M1 offre au signal (toutes cohortes) | 530 | 215675 | 25740 $ | -1673 $ | [-8134 ; +5540] | -2067 $ | -5380 $ | -0.9 / -1.3 / -0.8 / -0.1 | -4268 [-10914 ; +3074] | +373 $ [-7019 ; +8169] |
| M2 marge 5 c | 1921 | 157647 | 50874 $ | +1035 $ | [-5196 ; +7747] | +599 $ | -5343 $ | -1.3 / -1.3 / -1.1 / -0.9 | -1560 [-8428 ; +5629] | +340 $ [-2565 ; +3326] |
| M2 marge 10 c | 1695 | 166868 | 39990 $ | +273 $ | [-5864 ; +7279] | -104 $ | -5139 $ | -0.8 / -0.6 / -0.2 / -0.3 | -2322 [-8840 ; +5469] | +612 $ [-3093 ; +4493] |
| M4 retrait toxique | 2279 | 168460 | 48036 $ | +1163 $ | [-3588 ; +6268] | +1639 $ | -2429 $ | -0.5 / -0.3 / -0.1 / -0.1 | -1432 [-6767 ; +4463] | +930 $ [-3323 ; +5539] |
| M5 remplissage attendu | 3675 | 230577 | 71055 $ | -4564 $ | [-10602 ; +2157] | -3660 $ | -8169 $ | -1.0 / -1.0 / -1.1 / -1.4 | -7159 [-14088 ; -145] | +1138 $ [-3719 ; +6617] |
| M8 hybride (toutes cohortes) | 547 (preneur 184, maker 363) | 163664 | 22884 $ | +5951 $ | [-724 ; +13004] | +5603 $ | -2146 $ | +0.2 / -0.0 / +0.3 / +1.1 | +3355 [-3448 ; +10780] | -1266 $ [-7396 ; +5674] |
| M8b routeur corrigé (toutes cohortes) | 538 (preneur 153, maker 385) | 165303 | 22676 $ | +5189 $ | [-1496 ; +12459] | +4838 $ | -2223 $ | -0.0 / -0.2 / +0.1 / +0.9 | +2594 [-4088 ; +9905] | -1517 $ [-7699 ; +4597] |
| M3 anticipation Chainlink | 1490 | 136447 | 34302 $ | +1850 $ | [-2228 ; +6670] | +1272 $ | -2394 $ | +1.6 / +1.2 / +1.3 / +1.4 | -745 [-4889 ; +3520] | +1039 $ [-2135 ; +4624] |
| M10 double maker | 2764 | 128587 | 52976 $ | -1344 $ | [-4746 ; +2073] | -686 $ | -2541 $ | -1.0 / -1.0 / -0.9 / -1.2 | -3939 [-8746 ; +398] | -207 $ [-2666 ; +2360] |

## Moteur C (preneur, exécution à 300 ms) : tous les signaux réglés de la période réservée

| Période | Signaux avec résultat | Trades exécutés | $ engagés | Résultat | IC 90 % | Creux |
|---|---|---|---|---|---|---|
| ≥ 13.10.2026 (hors échantillon) | 174 | 132 | 6056 $ | +734 $ | [-501 ; +1953] | -627 $ |
| avant le 13.10 | 111 | 76 | 3378 $ | +765 $ | [-125 ; +1813] | -531 $ |

## FAST / SLOW / HYBRID (preneur) : recalcul descriptif avec les fonctions figées de fast_fenetre.py

496 cycles avec signaux réglés. Totaux identiques attendus à resultat_fast_fenetre_hors_echantillon.md section 6 ; ajoute parts et creux.

| Stratégie | Trades | Parts | $ engagés | Résultat | IC 90 % | par $ | Creux |
|---|---|---|---|---|---|---|---|
| FAST | 1440 | 356200 | 54153 $ | +4525 $ | [-4780 ; +13507] | +0.08 | -3173 $ |
| SLOW | 910 | 309169 | 39479 $ | -2737 $ | [-9992 ; +5079] | -0.07 | -8290 $ |
| HYBRID | 1471 | 365814 | 55565 $ | +4525 $ | [-4535 ; +14224] | +0.08 | -3640 $ |

## Lecture

- M0 témoin aléatoire : non démontré (l'IC contient 0).
- M1 offre au signal (toutes cohortes) : non démontré (l'IC contient 0).
- M2 marge 5 c : non démontré (l'IC contient 0).
- M2 marge 10 c : non démontré (l'IC contient 0).
- M4 retrait toxique : non démontré (l'IC contient 0).
- M5 remplissage attendu : non démontré (l'IC contient 0).
- M8 hybride (toutes cohortes) : non démontré (l'IC contient 0).
- M8b routeur corrigé (toutes cohortes) : non démontré (l'IC contient 0).
- M3 anticipation Chainlink : non démontré (l'IC contient 0).
- M10 double maker : non démontré (l'IC contient 0).

## Limites
- Les offres réglées s'arrêtent au cycle du 14.10.2026 07:50 UTC : depuis, la sauvegarde de bot95/rapide_maker.json échoue (l'adresse /api/rapidemaker du bot répond « erreur 500 »). Le volet maker couvre donc ~32 h de la période réservée, pas 2,7 jours.
- Remplissages simulés (file d'attente reconstituée), pas des exécutions réelles ; retard preneur de 150 ms supposé, non mesuré.
- Variantes testées en parallèle sur les mêmes cycles : avec une dizaine de variantes, un IC qui exclurait 0 de peu pourrait être dû au hasard.
