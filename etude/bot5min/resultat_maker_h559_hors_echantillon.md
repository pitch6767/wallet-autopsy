# Bot95 — H559–H564 : makers (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 15.10.2026 17:12 UTC. 744 cycles HORS ÉCHANTILLON (≥ 13.10.2026 00:00 UTC). Remplissages SIMULÉS selon trois bornes de file d'attente (prudente, centrale, optimiste) : aucun n'est une exécution garantie.

## 1. Décomposition de M4 (retrait sur flux toxique)

M4a, M4b, M4c gardent UNE seule des trois conditions de M4 (a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms). Même prix que M2 marge 5 c ; seule la règle de retrait change.

### Comparaison directe (fantômes en parallèle sur les mêmes cycles)

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 1036 | 855 / 876 / 883 | 87402 | 21629 $ | +2595 $ [-772 ; +6394] | +2817 $ | +2921 $ | +0.12 | -1691 $ | -1.6 / -1.6 / -1.8 / -1.6 | 0 |
| M2 cotation marge 5 c | 316313 | 4537 / 4133 / 4377 | 157647 | 50874 $ | +1035 $ [-5196 ; +7747] | +599 $ | +623 $ | +0.02 | -5343 $ | -1.3 / -1.3 / -1.1 / -0.9 | 75845 |
| M4 retrait toxique | 263151 | 5056 / 4732 / 5147 | 168460 | 48036 $ | +1163 $ [-3588 ; +6268] | +1639 $ | +1767 $ | +0.02 | -2429 $ | -0.5 / -0.3 / -0.1 / -0.1 | 84238 |
| M4a seul bourses -10 $ | 303090 | 4790 / 4350 / 4666 | 162560 | 50358 $ | +2245 $ [-3799 ; +9358] | +2842 $ | +2659 $ | +0.04 | -3725 $ | -1.0 / -1.0 / -1.1 / -1.0 | 80010 |
| M4b seul flux agressif | 304749 | 4729 / 4353 / 4662 | 155947 | 48936 $ | -1528 $ [-6408 ; +4018] | -970 $ | -1207 $ | -0.03 | -4440 $ | -0.9 / -0.9 / -0.9 / -0.8 | 76928 |
| M4c seul ventes Polymarket | 259882 | 5018 / 4561 / 4916 | 166088 | 48285 $ | -1104 $ [-5806 ; +3816] | -440 $ | -529 $ | -0.02 | -3437 $ | -0.9 / -0.5 / -0.3 / -0.1 | 83785 |

**Remplissages de M2 marge 5 c selon la condition toxique active au moment du remplissage (2 s)** — ce que chaque condition aurait évité :

| Condition active | Remplissages | Parts | Résultat de ces parts | par part |
|---|---|---|---|---|
| aucune | 1452 | 51722 | -53 $ | -0.1 c |
| a | 754 | 37891 | -306 $ | -0.8 c |
| b | 930 | 44631 | +2855 $ | +6.4 c |
| c | 2047 | 85295 | +1512 $ | +1.8 c |
(une part peut compter dans plusieurs conditions ; mesure disponible depuis la version du 11.10 14:50)

## 2. Durée de vie des cotations (M6)

M2 marge 5 c dont chaque offre est annulée après L ms ; la suivante n'est posée qu'après confirmation de l'annulation (aller-retour mesuré). Les parts remplies pendant le trajet de l'annulation sont comptées (dernière colonne).

### Durées de vie

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 316313 | 4537 / 4133 / 4377 | 157647 | 50874 $ | +1035 $ [-5196 ; +7747] | +599 $ | +623 $ | +0.02 | -5343 $ | -1.3 / -1.3 / -1.1 / -0.9 | 75845 |
| M6 duree de vie 100 ms | 1033743 | 6724 / 4546 / 4546 | 243051 | 72075 $ | +282 $ [-7974 ; +9075] | -24 $ | -24 $ | +0.00 | -7058 $ | -1.4 / -1.2 / -1.1 / -0.8 | 142153 |
| M6 duree de vie 250 ms | 641937 | 6414 / 4251 / 4252 | 235322 | 71297 $ | -488 $ [-8602 ; +8650] | -754 $ | -755 $ | -0.01 | -6138 $ | -1.3 / -1.1 / -0.9 / -0.8 | 131117 |
| M6 duree de vie 500 ms | 472846 | 6129 / 4283 / 4395 | 228152 | 69349 $ | -1012 $ [-9232 ; +7290] | -1024 $ | -1012 $ | -0.01 | -8043 $ | -1.4 / -1.2 / -1.2 / -1.0 | 122529 |
| M6 duree de vie 1000 ms | 385141 | 5753 / 4817 / 5227 | 205282 | 63831 $ | -55 $ [-6971 ; +7202] | -613 $ | -486 $ | -0.00 | -6687 $ | -1.2 / -1.1 / -1.0 / -0.8 | 109033 |

## 3. Début de cycle (180–300 s restantes) contre le reste

| Variante | Temps restant à la pose | Offres remplies | $ exécutés | Résultat prudent [IC 90 %] | par $ |
|---|---|---|---|---|---|
| M2 cotation marge 5 c | 180–300 s | 1976 | 41337 $ | +328 $ [-4430 ; +5030] | +0.01 |
| M2 cotation marge 5 c | 60–180 s | 347 | 8833 $ | +102 $ [-3103 ; +4097] | +0.01 |
| M2 cotation marge 5 c | 0–60 s | 22 | 703 $ | +604 $ [-1150 ; +2863] | +0.86 |
| M4 retrait toxique | 180–300 s | 2315 | 36068 $ | +1087 $ [-3219 ; +5522] | +0.03 |
| M4 retrait toxique | 60–180 s | 701 | 11409 $ | -208 $ [-3155 ; +2947] | -0.02 |
| M4 retrait toxique | 0–60 s | 22 | 559 $ | +284 $ [-372 ; +1031] | +0.51 |
| M5 remplissage attendu | 180–300 s | 3476 | 59225 $ | -1311 $ [-7864 ; +5312] | -0.02 |
| M5 remplissage attendu | 60–180 s | 596 | 10767 $ | -2296 $ [-5286 ; +1081] | -0.21 |
| M5 remplissage attendu | 0–60 s | 40 | 1063 $ | -957 $ [-1546 ; -394] | -0.90 |
| M0 temoin aleatoire | 180–300 s | 252 | 10845 $ | +519 $ [-1087 ; +2240] | +0.05 |
| M0 temoin aleatoire | 60–180 s | 248 | 10285 $ | +2367 $ [-649 ; +5752] | +0.23 |
| M0 temoin aleatoire | 0–60 s | 13 | 500 $ | -291 $ [-443 ; -140] | -0.58 |

Aucune conclusion à ce stade (trop peu de remplissages).

## 4. File d'attente : trois bornes

Prudente : seules les transactions nous font avancer. Centrale : un retrait sans transaction libère la file au prorata de notre place. Optimiste : tout retrait sans transaction vient de devant nous. Les trois colonnes de résultat des tableaux ci-dessus correspondent à ces bornes.

### Autres variantes permanentes

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 10 c | 499108 | 3659 / 3416 / 3600 | 166868 | 39990 $ | +273 $ [-5864 ; +7279] | -104 $ | -336 $ | +0.01 | -5139 $ | -0.8 / -0.6 / -0.2 / -0.3 | 71692 |
| M3 anticipation Chainlink | 103739 | 3725 / 3266 / 3481 | 136447 | 34302 $ | +1850 $ [-2228 ; +6670] | +1272 $ | +1222 $ | +0.05 | -2394 $ | +1.6 / +1.2 / +1.3 / +1.4 | 49718 |
| M5 remplissage attendu | 58570 | 9100 / 6772 / 7010 | 230577 | 71055 $ | -4564 $ [-10602 ; +2157] | -3660 $ | -3582 $ | -0.06 | -8169 $ | -1.0 / -1.0 / -1.1 / -1.4 | 130028 |

## 5. Hybride maker / preneur (M8) contre M1 sur les mêmes signaux

- M1 (toujours maker) : 13780 positions (0 preneur, 13780 maker), résultat prudent -3146 $ [IC 90 % -10336 ; +4870], creux -7060 $
- M8 hybride : 1790 positions (583 preneur, 1207 maker), résultat prudent +11139 $ [IC 90 % -2202 ; +25597], creux -4357 $

Le tournoi FAST / SLOW / HYBRID (preneur) sur les mêmes signaux est dans resultat_fast_fenetre.md, section 6.

## 6. Retard preneur
Le retard de 150 ms vient de la documentation Polymarket (changelog du 04.09.2026) et du drapeau itode=true de nos marchés ; il n'est PAS mesuré sur notre infrastructure. M8 et FAST l'utilisent comme hypothèse. Seul un ordre réel (test de 1 $, en attente de l'accord de Pitch) peut le mesurer.

## 7. Validation
Période réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais utilisée pour régler une règle. Verdict avec --hors-echantillon après plusieurs jours.
