# Bot95 — H833 à H835 : comportement de la liquidité, retraits, autres actifs — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole et code enregistrés sur GitHub avant le calcul du test (commit 1d45ee9).

**Données**
- Laboratoire de Dublin : 255 cycles, du 11.10 à 08:50 au 12.10 à 06:00 UTC, soit 21 h.
- BTC, ETH et SOL Binance à la seconde sur 30 jours.

**Découpage**
- Dublin : apprentissage sur la première moitié des cycles, test sur la seconde (123 cycles).
- Binance 30 jours : test du 02.10 au 11.10.
- Le règlement **officiel** est utilisé pour tous les résultats. Le substitut Binance ne diffère de l'officiel que sur 1 cycle de test sur 123.

## 1. Couverture et qualité des données L2

| Donnée | Secondes couvertes |
|---|---|
| Prix Binance, Bybit, OKX, Coinbase, Chainlink | 97 % |
| Carnets Binance et Bybit (meilleurs prix, cumuls à 5/10/20/50 $, ajouts et retraits) | 83 % |
| Photos du carnet Binance sur 10 niveaux (murs) | 82 % |

**Qualité**
- Trous signalés par l'enregistreur : 311 silences sur le carnet Binance, 25 sur Bybit.
- La profondeur au-delà de 50 $ ou de 10 niveaux n'est pas enregistrée.

**Non disponibles à la seconde** (déclarés, pas estimés) : Nasdaq, or, devises, CME. Deribit est enregistré à Dublin depuis aujourd'hui, ce qui servira plus tard.

## 2. H833 — Absorption

**Définition.** Un flux agressif fort (z ≥ 2) qui fait peu bouger le prix, pendant que la profondeur d'en face se reconstitue, que le microprix pointe à l'opposé et que plusieurs niveaux sont consommés. L'hypothèse prévoit un **retournement**.

Variation du BTC après l'événement, en $, signée dans le sens prévu : un chiffre positif veut dire que la prévision était juste. Test, IC 90 % par cycles.

| Type | Flux | Événements | 1 s | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|---|---|---|
| Absorption (retournement prévu) | achats | 25 | **−2,3 [−4,4 ; −0,6]** | **−3,9 [−7,0 ; −1,3]** | **−6,1 [−10,5 ; −2,1]** | −3,7 | −7,0 |
| Absorption (retournement prévu) | ventes | 21 | **−2,7 [−6,0 ; −0,1]** | −3,9 | −3,7 | −4,2 | −11,9 |
| Flux suivi par le prix (continuation prévue) | achats | 117 | **+1,4** | **+4,4** | **+5,3** | **+7,5 [+4,2 ; +10,7]** | +3,6 |
| Flux suivi par le prix (continuation prévue) | ventes | 123 | **+2,6** | **+6,3** | **+7,5** | **+10,0 [+5,9 ; +14,0]** | **+5,6** |

**Lecture**
- **L'hypothèse de l'absorption est contredite.** Après une absorption, le prix ne se retourne pas : il **continue** dans le sens du flux, sur 1 à 10 s, avec un IC hors de zéro. Les événements sont rares (46 sur le test).
- **Le flux agressif suivi par le prix annonce une continuation** de 5 à 10 $ sur 10 à 30 s. C'est démontré sur l'apprentissage comme sur le test.

**Effet sur le règlement officiel** (écart entre le résultat et la probabilité du modèle de règlement au même instant, signé dans le sens prévu)
- Flux suivi : **+0,096 [+0,046 ; +0,148]** sur 147 événements. Le règlement suit plus souvent la direction du flux que ne le prévoit le modèle seul.
- Absorption : +0,056 [−0,094 ; +0,208], non démontré.

## 3. H834 — Retraits de liquidité : annoncent-ils le mouvement ?

Variables utilisées :
- OFI (flux d'ordres au meilleur prix) ;
- retraits d'offres non expliqués par les transactions ;
- variation de profondeur ;
- déséquilibres ;
- écart entre le microprix et le milieu ;
- écart achat-vente ;
- taille et âge des murs.

On compare deux prévisions sur 20 935 instants : la première avec seulement les mouvements passés du prix et la volatilité, la seconde avec en plus les variables de liquidité. L'AUC mesure la qualité du classement : 0,5 = hasard.

| Cible | AUC prix passé seul | AUC + liquidité | Gain (IC 90 % par cycles) |
|---|---|---|---|
| Hausse à 10 s | 0,617 | 0,702 | **+0,085 [+0,075 ; +0,094]** |
| Hausse à 30 s | 0,601 | 0,665 | **+0,064 [+0,051 ; +0,077]** |
| Grand mouvement vers le haut à 30 s | 0,571 | 0,655 | **+0,083 [+0,059 ; +0,106]** |
| Grand mouvement vers le bas à 30 s | 0,624 | 0,667 | **+0,043 [+0,024 ; +0,060]** |

**Démontré : le carnet annonce la direction des 10 à 30 secondes suivantes**, nettement mieux que le prix seul. C'est le premier signal de ce type qui tient sur le test.

## 4. H835 — Autres actifs et autres places

**(a) ETH et SOL contre BTC, 30 jours à la seconde.**
- La corrélation simultanée est forte : 0,68 à 0,84.
- Il existe aussi une **petite avance** : un mouvement passé d'ETH ou de SOL sur 1 à 5 s annonce celui de BTC. Le R² hors échantillon passe d'environ 1,5 % à 2,2 %, soit un gain de 0,4 à 0,7 point.
- Cette avance est réelle, sur 10 jours de test, mais petite. Elle disparaît presque à 30 s.

**(b) Places BTC à Dublin, toutes les 50 ms.** Corrélation entre le mouvement passé d'une place et le mouvement suivant de Binance spot :

| Place | 100 ms | 250 ms | 500 ms | 1 s |
|---|---|---|---|---|
| Perp Bybit | **+0,40** | +0,38 | +0,33 | +0,29 |
| OKX swap | **+0,38** | +0,35 | +0,29 | +0,25 |
| Coinbase | +0,07 | +0,07 | +0,09 | +0,13 |
| Chainlink | +0,05 | +0,07 | +0,08 | +0,09 |

**Les perpétuels (Bybit, OKX) mènent nettement Binance spot**, sur 100 ms à 1 s. Coinbase et Chainlink suivent.

## 5. Modèles A / B / C / D — prévoir le règlement officiel (test : 738 décisions, 123 cycles)

| Modèle | Brier | Log loss | Précision | Apport marginal (IC corrigé) |
|---|---|---|---|---|
| A règlement seul | 0,1144 | 0,3594 | 85,1 % | — |
| B + flux BTC | 0,1140 | 0,3586 | 84,8 % | +0,0004 [−0,0046 ; +0,0051] |
| C + liquidité L2 | 0,1111 | 0,3624 | 85,1 % | +0,0029 [−0,0046 ; +0,0097] |
| D + autres places | 0,1108 | 0,3621 | 85,1 % | +0,0003 [−0,0004 ; +0,0009] |

**Situations proches de 50 %** (115 décisions)

| Modèle | Brier | Précision |
|---|---|---|
| A | 0,2411 | 58 % |
| B | 0,2377 | 60 % |
| C | 0,2455 | 59 % |
| D | 0,2455 | 61 % |

**Marge faible** (146 décisions)

| Modèle | Brier | Précision |
|---|---|---|
| A | 0,2400 | 60 % |
| D | 0,2389 | 62 % |

**Lecture.** Sur la probabilité de règlement, **aucun apport n'est démontré**. La liquidité annonce bien les 10 à 30 secondes suivantes, mais un cycle se décide sur une moyenne de 60 s, à 30 à 240 s de distance. Le signal court s'y dilue.

## 6. P&L exécutable (test)

Règle : achat de 20 $ si le modèle donne un avantage ≥ 0,05 après frais sur le prix vendeur, au plus une fois par cycle. Exécution 164 ms plus tard sur le carnet Polymarket enregistré, conservation jusqu'au règlement officiel.

| Modèle | Cycles avec achat | P&L | Écart avec A | IC 90 % par cycles (non corrigé) |
|---|---|---|---|---|
| A règlement seul | 104 | −471 $ | — | — |
| B + flux BTC | 102 | −169 $ | +302 $ | [−136 ; +765] |
| C + liquidité L2 | 106 | **+560 $** | +1 031 $ | [+81 ; +2 355] |
| D + autres places | 104 | **+732 $** | +1 203 $ | [+162 ; +2 544] |

Les modèles C et D font mieux que A en P&L, avec un IC non corrigé au-dessus de zéro. **Ce n'est pas une preuve**, pour trois raisons :
- 123 cycles d'une seule journée ;
- 3 comparaisons ;
- l'amélioration en Brier n'est pas démontrée.

Le critère pré-enregistré exige les deux.

## 7. Décision par module

| Module | Décision |
|---|---|
| H833 Absorption → retournement | **Rejeté.** C'est l'inverse : le prix continue dans le sens du flux. |
| H833 Flux agressif suivi par le prix | **Conservé comme signal de court terme** : continuation démontrée sur 10 à 30 s, effet sur le règlement +0,10 [+0,05 ; +0,15]. |
| H834 Retraits et liquidité L2 | **Conservé comme signal de court terme** : +0,04 à +0,09 d'AUC à 10–30 s, démontré. Pas d'apport démontré sur le règlement. |
| H835 ETH / SOL | Petite avance réelle sur 1 à 5 s (R² +0,5 point). **À garder en réserve**, sans effet démontré sur le règlement. |
| H835 Perpétuels Bybit / OKX | **Mènent le spot** de 100 ms à 1 s : utile pour l'exécution. |
| H835 Nasdaq, or, devises, CME | **Non testés** : pas de données à la seconde. |
| Modèles B, C, D pour le règlement | **Non conservés** selon le critère pré-enregistré (Brier non démontré). P&L de C et D prometteur mais non démontré. |

**Suite proposée (tu décides)**
- Les signaux de court terme (flux, carnet, perpétuels) servent surtout au **moment d'exécution** et à la **gestion dynamique** : c'est exactement le moteur DPE H841–H860, que je traite maintenant.
- Les modèles C et D pourraient être pré-enregistrés tels quels et jugés sur des cycles nouveaux, sans déploiement.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_liquidite_h833.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/liquidite_h833.py
