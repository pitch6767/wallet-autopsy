# Bot95 — META-ROUTER : le choix dynamique bat-il une stratégie fixe ?

> **Verdict : non.**
> - **Toute la période hors apprentissage (validation + inédit, 469 cycles) :**
>   - **la meilleure stratégie fixe (V2-F 0,01 %) fait +1 352 $ ;**
>   - le routeur selon la volatilité et la tendance fait +326 $ ;
>   - le même routeur avec l'heure en plus fait +117 $ ;
>   - le portefeuille fixe des six stratégies fait +97 $.
> - **Le choix dynamique perd 1 027 $ contre la stratégie fixe** (et 1 236 $ avec l'heure en plus). La probabilité que ce soit en réalité ≤ 0 est de 85 % et 92 %.
> - **Selon ta règle, on abandonne le routeur.** Aucun fantôme n'a été modifié et aucun routeur n'est actif.

**Méthode**
- Six stratégies, rejouées sur les carnets enregistrés 4 fois par seconde, du 07.10 08:00 au 10.10 13:25 : 924 cycles BTC réglés.
- Ce sont les **mêmes cycles** pour toutes ; les cycles sans achat comptent 0 $.
- Une décision par cycle et une seule enveloppe de 50 $.
- Achat au seul meilleur vendeur, dans la quantité réellement affichée, frais compris.
- Jackpot = gain d'au moins 4 fois la mise.

**Les trois périodes**
- **Apprentissage :** jusqu'au 08.10 22:00, 455 cycles.
- **Validation :** jusqu'au 10.10 10:25, 433 cycles, déjà explorés par d'autres études.
- **Inédit :** après le 10.10 10:25, seulement 36 cycles.

**Les routeurs**
- Leurs règles sont figées sur l'apprentissage seul, puis jugées sur le reste.
- Aucun résultat futur n'entre dans une décision.
- Le régime est mesuré **avant** le début de chaque cycle.

## 1. Complémentarité

**Chaque stratégie seule**

| Stratégie | Apprentissage | Validation | Inédit (36 cycles) | Jackpots (app. / val.) |
|---|---|---|---|---|
| V2-D perp 120-269 s | +1 678 $ (215 achats) | −845 $ (287) | −882 $ (35) | 26 / 18 |
| Zone 30 + modèle monte | +1 734 $ (51) | +796 $ (62) | −137 $ (4) | 12 / 15 |
| V2-G jury des bourses | +234 $ (294) | +1 421 $ (346) | −374 $ (36) | 28 / 27 |
| V2-F original | +593 $ (339) | −711 $ (379) | −971 $ (36) | 26 / 21 |
| **V2-F 0,01 %** | **+2 209 $** (236) | **+1 508 $** (231) | −156 $ (25) | 16 / 13 |
| V2-F miroir 1 s | +1 621 $ (207) | −109 $ (174) | −137 $ (10) | 21 / 9 |

**Les stratégies se ressemblent trop pour qu'un routeur ait de quoi choisir.**
- Corrélation des résultats cycle par cycle :
  - V2-F et V2-F miroir 1 s : 0,80 ;
  - V2-F et V2-G jury : 0,77 ;
  - V2-F et V2-D : 0,73.
- V2-F achète dans 754 cycles et V2-G dans 676 : **675 de ces cycles sont communs, et 517 sont des pertes communes.**
- **Gagnants exclusifs** (un cycle gagné par une seule des six) :
  - V2-F 0,01 % en a 47, pour +1 395 $ ;
  - les autres en ont entre 0 et 3.
- **V2-F 0,01 % est la seule vraiment différente.** Zone 30 + modèle monte est la moins corrélée (0,28 à 0,41), mais elle achète peu.

## 2. Régimes

**Effectifs** (apprentissage / hors apprentissage) :
- **Volatilité :**
  - agité : 430 / 296 cycles ;
  - calme : **21** / 158 cycles.
- **Tendance (directionnel ou oscillant) :** environ 220 cycles par côté dans chaque période.
- **Chainlink lent ou rapide :** environ 200 à 250 cycles par côté.
- **Blocs horaires UTC :** de 70 à 144 cycles par bloc.

**Ce que montrent les régimes**
- **Le marché calme est presque absent de l'apprentissage** : 21 cycles seulement. Aucun routeur ne peut y apprendre quoi que ce soit.
  - Hors apprentissage, en calme, V2-F original fait −1 181 $ et V2-D fait −1 081 $.
  - V2-F 0,01 % y reste légèrement positif : +178 $.
- **Ce qui marche dans une case à l'apprentissage s'inverse souvent ensuite.** Exemples :
  - V2-F original, marché directionnel : +611 $, puis −1 552 $ ;
  - V2-D, bloc 06-12 UTC : +1 351 $, puis −1 364 $ ;
  - Zone 30, marché oscillant : +1 313 $, puis −94 $.
- **Seule V2-F 0,01 % reste positive dans presque toutes les cases**, avant comme après. Exceptions :
  - en calme pendant l'apprentissage : −80 $, sur 12 achats ;
  - en marché directionnel hors apprentissage : −77 $ ;
  - dans le bloc 00-06 UTC hors apprentissage : −169 $.
- **Transmission Chainlink :** aucune stratégie n'est meilleure de façon stable en Chainlink lent qu'en rapide, ni l'inverse.

## 3. Routeurs

**Hors apprentissage (validation + inédit, 469 cycles)**

| Routeur | Achats | Gagnés | Résultat net | Creux max | Pertes de suite max | Capital engagé | Jackpots |
|---|---|---|---|---|---|---|---|
| **R0 — V2-F 0,01 % fixe** | 256 | 34 % | **+1 352 $** | −829 $ | 9 | 7 535 $ | 13 (+2 398 $) |
| R1 — volatilité + tendance | 112 | 37 % | +326 $ | −446 $ | 10 | 3 215 $ | 6 (+268 $) |
| R2 — R1 + heure | 157 | 27 % | +117 $ | −954 $ | 13 | 5 012 $ | 9 (+1 917 $) |
| R3 — portefeuille fixe des 6 (8,33 $ chacune) | 422 | 23 % | +97 $ | −1 334 $ | 19 | 11 329 $ | 22 (+4 104 $) |

**Par période**

| Routeur | Apprentissage | Validation | Inédit (36 cycles) |
|---|---|---|---|
| R0 | +2 209 $ | **+1 508 $** | −156 $ |
| R1 | +3 194 $ | +391 $ | −65 $ (2 achats) |
| R2 | +3 698 $ | +182 $ | −65 $ (2 achats) |
| R3 | +2 233 $ | +603 $ | −506 $ |

**Le schéma classique du sur-apprentissage**
- R1 et R2 sont les meilleurs sur l'apprentissage, qui a servi à les construire.
- Ils deviennent les moins bons dès qu'on les juge ailleurs.
- R1 construit « après coup » sur les cycles jugés eux-mêmes ferait +2 764 $. C'est le mirage qu'on obtient quand on optimise sur les données qu'on juge.

**Incertitude** (rééchantillonnage par blocs d'une heure, hors apprentissage) :

| Comparaison | Différence | Intervalle à 90 % | Probabilité ≤ 0 |
|---|---|---|---|
| R1 − R0 | −1 027 $ | [−2 658 $ ; +536 $] | 85 % |
| R2 − R0 | −1 236 $ | [−2 712 $ ; +215 $] | 92 % |
| R3 − R0 | −1 255 $ | [−2 658 $ ; +265 $] | 91 % |
| R1 − R3 | +229 $ | [−1 715 $ ; +2 068 $] | 42 % |

**Le routeur est aussi fragile**
- Pendant l'étude, j'ai corrigé un défaut de la mesure de tendance : elle manquait sur 368 cycles à cause de trous dans les données de prix. Elle ne manque plus que sur 43.
- Ce seul changement a fait passer R1 de +1 509 $ à +326 $ hors apprentissage.
- Une règle aussi sensible à un détail de mesure n'est pas fiable.

**Le portefeuille fixe (R3) n'aide pas non plus**
- Diversifier entre des stratégies corrélées à 0,7–0,8 revient surtout à acheter plus souvent les mêmes pertes.
- Il engage 50 % de capital en plus, a le pire creux (−1 334 $) et les plus longues séries de pertes (19).
- Il garde en revanche le plus de jackpots (22).

## Honnêtement

- **La période inédite est minuscule** : 36 cycles. Tout y est négatif ; R1 et R2 y perdent le moins parce qu'ils n'achètent presque pas (2 achats). Elle ne permet aucune conclusion à elle seule.
- **R0 n'est pas totalement « vierge » en validation.** V2-F 0,01 % avait déjà été repérée par une étude précédente sur les données du 07.10 au 09.10.
- **Ces rejeux achètent au seul meilleur vendeur.** C'est pour cela que V2-F original y est plus faible que dans les rejeux précédents, faits à 50 $ complets, et que sur le fantôme en direct (qui achète jusqu'au vendeur + 1 c).

## Décision proposée (à toi de trancher)

1. **Abandonner le META-ROUTER**, selon ta règle : il ne bat ni la meilleure stratégie fixe ni de façon sûre le portefeuille.
2. **Point d'observation :** V2-F 0,01 % est la seule stratégie qui reste positive dans presque tous les régimes et la seule à gagner des cycles que les autres ne gagnent pas. Elle tourne en fantôme depuis 12:33 (« V2-F incertitude 0,01 % »). Le verdict prospectif de mardi 14.10 dira si cela tient.

**À noter :** tous les fantômes ont été remis à 0 à 13:50 (P&L, gains, pertes, historique). Les trades d'avant sont conservés à part dans le bot et sur GitHub.
