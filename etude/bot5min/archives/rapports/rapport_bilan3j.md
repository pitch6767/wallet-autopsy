# Bot95 — Bilan des 3 jours des fantômes figés BTC (tâche programmée du 07.10)

> **En bref**
> 1. **Sur 3 jours** (07.10 13:46 → 10.10 13:50), six désaccords V2 sont positifs, de +1 182 $ à +2 458 $ :
>    - V2-D perp 120-269 s, V2-G jury des bourses, V2-F, V2-C, V2-B et V2-H.
>    - **Tous ont gagné beaucoup plus dans la première moitié que dans la seconde.**
>    - V2-F, par exemple : +3 333 $ sur les 368 premiers trades, puis −1 848 $ sur les 387 suivants.
> 2. **Seuls V2-D (+673 $) et V2-G (+160 $) restent positifs sur la seconde moitié.**
>    - Mais sans leurs 3 meilleurs trades, ils sont négatifs.
>    - Les intervalles à 90 % contiennent tous 0, sauf ceux de V2-E et de V1, entièrement négatifs.
> 3. **Les photos « qui a bougé en premier » donnent la clé :**
>    - **Polymarket bouge en premier dans 64 % des cas.**
>    - Le désaccord ne gagne vraiment que si Polymarket **rejoint** le modèle dans les 10 s : +9 130 $, contre des pertes ailleurs.
> 4. **Morts à l'arrivée :** dès 0,25 s, 25 % des offres du premier désaccord 20 ont disparu, et 41 % à 1 s.

Aucune variante n'a été modifiée pour ce bilan. Remarque : la remise à zéro de 13:50 a eu lieu avant ce bilan, mais les chiffres d'avant ont été conservés.

## 1. Totaux du bot sur 3 jours (complets)

Chiffres du bot lui-même, jusqu'à la remise à zéro de 13:50. La colonne « début » couvre les trades d'avant le 09.10, qui n'ont pas été sauvegardés un par un. La colonne « fin » couvre les trades sauvegardés, du 09.10 au 10.10 13:50.

| Stratégie | Trades | Résultat | Moyen par trade | Gagnés | Début : trades / résultat | Fin : trades / résultat |
|---|---|---|---|---|---|---|
| **V2-D perp 120-269 s** | 550 | **+2 458 $** | +4,5 $ | 23 % | 228 / +1 785 $ | 322 / **+673 $** |
| **V2-G jury des bourses** | 693 | **+2 349 $** | +3,4 $ | 22 % | 326 / +2 189 $ | 367 / **+160 $** |
| désaccord 20 (arrêté le 09.10) | 761 | +1 998 $ | +2,6 $ | 24 % | 583 / +2 164 $ | 178 / −166 $ |
| désaccord 20 sans nuit | 442 | +1 487 $ | +3,4 $ | 24 % | 155 / +1 743 $ | 287 / −256 $ |
| V2-F écart qui grandit | 755 | +1 485 $ | +2,0 $ | 22 % | 368 / +3 333 $ | 387 / −1 848 $ |
| V2-C perp | 743 | +1 325 $ | +1,8 $ | 22 % | 355 / +2 332 $ | 388 / −1 007 $ |
| V2-B hors 60-89 s | 758 | +1 220 $ | +1,6 $ | 23 % | 371 / +2 340 $ | 387 / −1 120 $ |
| V2-H veto complet | 737 | +1 182 $ | +1,6 $ | 23 % | 351 / +2 309 $ | 386 / −1 127 $ |
| assurance 4/7/10 (arrêtée le 09.10) | 59 | +84 $ | +1,4 $ | 66 % | — | 59 / +84 $ |
| assurance 6/9/12 (arrêtée le 09.10) | 59 | +82 $ | +1,4 $ | 68 % | — | 59 / +82 $ |
| désaccord confirmé + perp | 156 | −303 $ | −1,9 $ | 31 % | 39 / +399 $ | 117 / −702 $ |
| désaccord confirmé (arrêté) | 139 | −321 $ | −2,3 $ | 31 % | 79 / −129 $ | 60 / −192 $ |
| V1 avec stop (40 derniers trades) | 40 | −493 $ | −12,3 $ | — | — | 40 / −493 $ |
| V2-E persistant | 684 | **−2 751 $** | −4,0 $ | 18 % | 308 / +606 $ | 376 / −3 357 $ |
| V6 loterie (arrêtée le 09.10) | 469 | −4 518 $ | −9,6 $ | 8 % | 409 / −3 951 $ | 60 / −567 $ |
| V5 gain attendu (arrêté le 09.10) | 521 | −4 661 $ | −8,9 $ | 22 % | 461 / −4 738 $ | 60 / +77 $ |

## 2. Détail sur les trades sauvegardés (09.10 → 10.10 13:50)

Le creux, la concentration et les résultats sans les meilleurs trades ne peuvent se calculer que trade par trade. Ils portent donc seulement sur cette seconde moitié.

| Stratégie | Trades | Résultat | Intervalle 90 % | Creux max | Part des 5 meilleurs dans les gains | Sans le meilleur | Sans les 3 | Sans les 5 |
|---|---|---|---|---|---|---|---|---|
| V2-D perp 120-269 s | 322 | +673 $ | [−2 280 $ ; +3 626 $] | −1 774 $ | 17 % | +220 $ | −577 $ | −1 304 $ |
| V2-G jury des bourses | 367 | +160 $ | [−2 959 $ ; +3 279 $] | −1 273 $ | 19 % | −496 $ | −1 538 $ | −2 233 $ |
| désaccord 20 sans nuit | 287 | −256 $ | [−2 626 $ ; +2 113 $] | −1 565 $ | 22 % | −698 $ | −1 461 $ | −2 085 $ |
| V2-C perp | 388 | −1 007 $ | [−4 182 $ ; +2 167 $] | −2 480 $ | 18 % | −1 665 $ | −2 519 $ | −3 279 $ |
| V2-B hors 60-89 s | 387 | −1 120 $ | [−3 963 $ ; +1 724 $] | −2 736 $ | 20 % | −1 689 $ | −2 537 $ | −3 301 $ |
| V2-H veto complet | 386 | −1 127 $ | [−4 492 $ ; +2 238 $] | −2 070 $ | 19 % | −1 900 $ | −2 916 $ | −3 713 $ |
| V2-F écart qui grandit | 387 | −1 848 $ | [−4 290 $ ; +593 $] | −2 827 $ | 16 % | −2 212 $ | −2 836 $ | −3 396 $ |
| V2-E persistant | 376 | −3 357 $ | [−6 662 $ ; −51 $] | −4 536 $ | 22 % | −3 983 $ | −5 125 $ | −6 070 $ |
| V1 avec stop | 40 | −493 $ | [−865 $ ; −120 $] | −509 $ | 40 % | −530 $ | −606 $ | −671 $ |

**Résultat par jour (heure suisse, trades sauvegardés)**

| Stratégie | 09.10 | 10.10 (jusqu'à 13:50) |
|---|---|---|
| V2-D perp 120-269 s | +2 266 $ | −1 592 $ |
| V2-G jury des bourses | +536 $ | −376 $ |
| V2-C perp | +543 $ | −1 550 $ |
| V2-B hors 60-89 s | +521 $ | −1 640 $ |
| V2-H veto complet | −15 $ | −1 112 $ |
| V2-F écart qui grandit | −260 $ | −1 589 $ |
| V2-E persistant | −1 768 $ | −1 588 $ |

**La journée du 10.10 (nuit et matin) a été mauvaise pour toutes les stratégies V2**, entre −376 $ et −1 640 $.

## 3. Qui a bougé en premier ? (748 photos, 07.10 → 10.10)

Les photos couvrent les 10 s, au dixième de seconde, avant le premier désaccord ≥ 0,20 de chaque cycle. « A bougé » veut dire :
- au moins 5 $ dans notre sens, pour une bourse ou pour Chainlink ;
- au moins 1 c de baisse du vendeur de notre côté, pour Polymarket.

| Premier à bouger | Photos | Part | Désaccord gagné | Gain (50 $ au prix du signal, sans limite de quantité) |
|---|---|---|---|---|
| **Polymarket** (vendeur qui baisse) | 478 | **64 %** | 22 % | −938 $ |
| Coinbase | 106 | 14 % | 20 % | +1 737 $ |
| Bybit perp | 82 | 11 % | 20 % | −756 $ |
| personne de façon nette | 47 | 6 % | 29 % | +438 $ |
| OKX perp | 16 | 2 % | 19 % | −491 $ |
| Chainlink | 14 | 2 % | 36 % | −4 $ |
| Binance | 5 | 1 % | 40 % | +293 $ |

| Qui a créé le désaccord | Photos | Gagné | Gain |
|---|---|---|---|
| seul Polymarket a bougé, bourses immobiles | 338 | 22 % | +158 $ |
| **seules les bourses ont bougé, Polymarket immobile** | 108 | 17 % | **−1 352 $** |
| les deux ont bougé | 255 | 24 % | **+1 034 $** |

**Ce que montrent les photos**
- **La plupart des désaccords naissent parce que Polymarket bouge, pas parce que les bourses bougent.** Quand seules nos bourses bougent et que Polymarket ne suit pas, le désaccord perd. Polymarket a souvent raison de ne pas suivre.
- **Coinbase est la bourse qui bouge le plus tôt quand elle bouge** (moment médian 2,9 s dans la fenêtre de 10 s). Bybit suit à 3,3 s, OKX et Chainlink à 4,0 s, Binance à 4,7 s.
- Les désaccords où Coinbase bouge en premier sont les seuls nettement positifs : +1 737 $ sur 106 photos.

**10 s après le signal**

| Ce qui s'est passé | Photos | Gagné | Gain |
|---|---|---|---|
| **Polymarket a rejoint le modèle** (vendeur +3 c ou plus) | 251 | 33 % | **+9 130 $** |
| Polymarket n'a pas bougé (±3 c) | 189 | 17 % | −3 765 $ |
| Polymarket s'est encore éloigné, et les bourses sont revenues en arrière | 148 | 15 % | −2 920 $ |
| Polymarket s'est encore éloigné | 85 | 16 % | −1 295 $ |
| Polymarket immobile, et les bourses sont revenues en arrière | 47 | 17 % | −450 $ |

**Tout le gain vient des cas où Polymarket finit par donner raison au modèle.** Mais au moment d'acheter, on ne sait pas encore dans quel cas on se trouve.

## 4. Morts à l'arrivée (773 premiers désaccords 20)

L'offre vue au signal existe-t-elle encore un peu plus tard, au même prix ou mieux ? Achat au seul meilleur vendeur, dans la quantité affichée.

| Délai | Encore achetables | Morts à l'arrivée | Valeur des morts (si achetés au signal) | dont gagnants | Résultat des achetables |
|---|---|---|---|---|---|
| 0,25 s | 578 | 195 (25 %) | +237 $ | 49 | −493 $ |
| 0,5 s | 532 | 241 (31 %) | +261 $ | 62 | −796 $ |
| 1 s | 458 | **315 (41 %)** | **+1 619 $** | 83 | −1 490 $ |
| 2 s | 437 | 336 (43 %) | +1 258 $ | 88 | −1 916 $ |

**La conclusion de l'attribution V2-F 0,01 % se confirme :** les meilleures offres disparaissent en moins d'une seconde, et ce qui reste achetable ensuite perd de l'argent.

## Ce que je propose (à toi de décider)

1. **Garder en observation V2-D perp 120-269 s et V2-G jury des bourses** : ce sont les deux seuls positifs sur les deux moitiés. Ce n'est pas encore démontré, puisque l'intervalle contient 0.
2. **V2-E persistant est le seul perdant clair :** −2 751 $, et son intervalle sur la seconde moitié est entièrement négatif. Tu peux l'arrêter si tu le souhaites.
3. **Piste à vérifier sur des cycles nouveaux :** les désaccords où Coinbase bouge en premier (+1 737 $ sur 106 photos). C'est une observation, pas un filtre.
4. **La vitesse d'exécution reste le point décisif.** Elle est maintenant mesurée à chaque signal et sera dans le verdict de mardi.
