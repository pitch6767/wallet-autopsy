# Bot95 — H559–H564 : makers (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 16.10.2026 07:53 UTC. 916 cycles HORS ÉCHANTILLON (≥ 13.10.2026 00:00 UTC). Remplissages SIMULÉS selon trois bornes de file d'attente (prudente, centrale, optimiste) : aucun n'est une exécution garantie.

## 1. Décomposition de M4 (retrait sur flux toxique)

M4a, M4b, M4c gardent UNE seule des trois conditions de M4 (a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms). Même prix que M2 marge 5 c ; seule la règle de retrait change.

### Comparaison directe (fantômes en parallèle sur les mêmes cycles)

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 1284 | 1055 / 1079 / 1090 | 208647 | 52364 $ | -5 $ [-4153 ; +4405] | +320 $ | +451 $ | -0.00 | -3300 $ | -1.7 / -1.7 / -1.7 / -1.6 | 0 |
| M2 cotation marge 5 c | 364329 | 5476 / 5021 / 5327 | 453917 | 150732 $ | +2012 $ [-7471 ; +12199] | +1140 $ | +1390 $ | +0.01 | -6224 $ | -1.2 / -1.1 / -1.0 / -0.7 | 244390 |
| M4 retrait toxique | 302747 | 6157 / 5782 / 6294 | 478873 | 141121 $ | +1303 $ [-6804 ; +9383] | +657 $ | +1035 $ | +0.01 | -5897 $ | -0.8 / -0.8 / -0.7 / -0.5 | 264356 |
| M4a seul bourses -10 $ | 348180 | 5770 / 5277 / 5670 | 473963 | 150210 $ | +1223 $ [-8852 ; +11152] | +1932 $ | +1739 $ | +0.01 | -6163 $ | -1.2 / -1.1 / -1.0 / -0.8 | 261287 |
| M4b seul flux agressif | 351183 | 5700 / 5286 / 5661 | 460323 | 146897 $ | +1876 $ [-7117 ; +11141] | +1987 $ | +2004 $ | +0.01 | -6379 $ | -1.0 / -0.9 / -0.9 / -0.8 | 252786 |
| M4c seul ventes Polymarket | 298370 | 6133 / 5587 / 6022 | 492945 | 145537 $ | +584 $ [-8153 ; +9716] | +443 $ | +444 $ | +0.00 | -3958 $ | -1.1 / -0.9 / -0.7 / -0.5 | 281013 |

**Remplissages de M2 marge 5 c selon la condition toxique active au moment du remplissage (2 s)** — ce que chaque condition aurait évité :

| Condition active | Remplissages | Parts | Résultat de ces parts | par part |
|---|---|---|---|---|
| aucune | 4325 | 166262 | -741 $ | -0.4 c |
| a | 1825 | 93789 | +611 $ | +0.7 c |
| b | 2230 | 113689 | +3005 $ | +2.6 c |
| c | 5071 | 222026 | +2821 $ | +1.3 c |
(une part peut compter dans plusieurs conditions ; mesure disponible depuis la version du 11.10 14:50)

## 2. Durée de vie des cotations (M6)

M2 marge 5 c dont chaque offre est annulée après L ms ; la suivante n'est posée qu'après confirmation de l'annulation (aller-retour mesuré). Les parts remplies pendant le trajet de l'annulation sont comptées (dernière colonne).

### Durées de vie

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 364329 | 5476 / 5021 / 5327 | 453917 | 150732 $ | +2012 $ [-7471 ; +12199] | +1140 $ | +1390 $ | +0.01 | -6224 $ | -1.2 / -1.1 / -1.0 / -0.7 | 244390 |
| M6 duree de vie 100 ms | 1263774 | 8233 / 5542 / 5542 | 767086 | 225409 $ | -2708 $ [-18008 ; +13579] | -3378 $ | -3378 $ | -0.01 | -9940 $ | -1.4 / -1.3 / -1.3 / -1.1 | 513470 |
| M6 duree de vie 250 ms | 776966 | 7904 / 5219 / 5220 | 700489 | 214329 $ | -1123 $ [-15133 ; +12357] | -2778 $ | -2779 $ | -0.01 | -10500 $ | -1.4 / -1.2 / -1.1 / -1.0 | 438830 |
| M6 duree de vie 500 ms | 562913 | 7576 / 5256 / 5389 | 658705 | 204533 $ | +5255 $ [-8151 ; +18143] | +3060 $ | +3165 $ | +0.03 | -10192 $ | -1.4 / -1.2 / -1.2 / -1.0 | 395234 |
| M6 duree de vie 1000 ms | 451157 | 7011 / 5853 / 6346 | 583949 | 186340 $ | +1042 $ [-10003 ; +12825] | -149 $ | +110 $ | +0.01 | -9617 $ | -1.3 / -1.1 / -1.1 / -0.8 | 340527 |

## 3. Début de cycle (180–300 s restantes) contre le reste

| Variante | Temps restant à la pose | Offres remplies | $ exécutés | Résultat prudent [IC 90 %] | par $ |
|---|---|---|---|---|---|
| M2 cotation marge 5 c | 180–300 s | 5415 | 121853 $ | +1033 $ [-7171 ; +9580] | +0.01 |
| M2 cotation marge 5 c | 60–180 s | 1017 | 26890 $ | +455 $ [-4875 ; +5972] | +0.02 |
| M2 cotation marge 5 c | 0–60 s | 66 | 1988 $ | +525 $ [-1512 ; +2994] | +0.26 |
| M4 retrait toxique | 180–300 s | 5764 | 102217 $ | -257 $ [-7751 ; +7037] | -0.00 |
| M4 retrait toxique | 60–180 s | 1944 | 36419 $ | +1600 $ [-3712 ; +6956] | +0.04 |
| M4 retrait toxique | 0–60 s | 107 | 2485 $ | -40 $ [-1233 ; +1317] | -0.02 |
| M5 remplissage attendu | 180–300 s | 10003 | 181277 $ | +195 $ [-11429 ; +12225] | +0.00 |
| M5 remplissage attendu | 60–180 s | 2091 | 39620 $ | +544 $ [-7528 ; +9590] | +0.01 |
| M5 remplissage attendu | 0–60 s | 111 | 3613 $ | -1874 $ [-3846 ; -75] | -0.52 |
| M0 temoin aleatoire | 180–300 s | 606 | 24468 $ | +1502 $ [-1166 ; +4176] | +0.06 |
| M0 temoin aleatoire | 60–180 s | 640 | 25672 $ | -515 $ [-3901 ; +3211] | -0.02 |
| M0 temoin aleatoire | 0–60 s | 55 | 2224 $ | -992 $ [-1361 ; -609] | -0.45 |

Aucune conclusion à ce stade (trop peu de remplissages).

## 4. File d'attente : trois bornes

Prudente : seules les transactions nous font avancer. Centrale : un retrait sans transaction libère la file au prorata de notre place. Optimiste : tout retrait sans transaction vient de devant nous. Les trois colonnes de résultat des tableaux ci-dessus correspondent à ces bornes.

### Autres variantes permanentes

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 10 c | 573227 | 4507 / 4227 / 4466 | 501104 | 121805 $ | -1463 $ [-11466 ; +9102] | -2153 $ | -2027 $ | -0.01 | -5139 $ | -1.0 / -0.8 / -0.7 / -0.7 | 258860 |
| M3 anticipation Chainlink | 121878 | 4436 / 3873 / 4137 | 404575 | 107959 $ | +2656 $ [-4862 ; +10169] | +2813 $ | +2610 $ | +0.02 | -3076 $ | +0.6 / +0.6 / +0.7 / +1.0 | 184900 |
| M5 remplissage attendu | 69244 | 11115 / 8345 / 8643 | 714420 | 224510 $ | -1136 $ [-14023 ; +13358] | +331 $ | +793 $ | -0.01 | -8962 $ | -1.0 / -1.1 / -1.1 / -1.2 | 455931 |

## 5. Hybride maker / preneur (M8) contre M1 sur les mêmes signaux

- M1 (toujours maker) : 39754 positions (0 preneur, 39754 maker), résultat prudent -5573 $ [IC 90 % -18658 ; +7203], creux -10947 $
- M8 hybride : 4580 positions (1300 preneur, 3280 maker), résultat prudent +19658 $ [IC 90 % -119 ; +39966], creux -4729 $

Le tournoi FAST / SLOW / HYBRID (preneur) sur les mêmes signaux est dans resultat_fast_fenetre.md, section 6.

## 6. Retard preneur
Le retard de 150 ms vient de la documentation Polymarket (changelog du 04.09.2026) et du drapeau itode=true de nos marchés ; il n'est PAS mesuré sur notre infrastructure. M8 et FAST l'utilisent comme hypothèse. Seul un ordre réel (test de 1 $, en attente de l'accord de Pitch) peut le mesurer.

## 7. Validation
Période réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais utilisée pour régler une règle. Verdict avec --hors-echantillon après plusieurs jours.
