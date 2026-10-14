# BOT95 — QUEUE RACE ENGINE · phases 0, 1 et 2 relancées sur toutes les données

Étude hors ligne du 14.10.2026 (aucun bot, aucun workflow modifié). Données : enregistreur du VPS de Dublin, branche `donnees-rapide` : **752 cycles BTC 5 min** (11.10 : 158, 12.10 : 287, 13.10 : 279, 14.10 : 28), soit ≈ 62,7 h d'horloge. Même méthode que `resultat_queue_race_phase12.md` (15 cycles du 11.10), avec trois changements : prix en millièmes pris tels quels quand l'enregistreur les fournit, flux agressifs `fx` ajoutés comme source d'information en phase 2, tableaux par jour au lieu de par cycle. Script : `etude/bot5min/queue_race_phases.py`. Les phases 3 à 6 sont dans `resultat_queue_race_phases36.md`.

## Verdict (en tête)

- **Qui fait disparaître la meilleure offre ?** Sur 248 779 disparitions complètes du meilleur niveau (hors indéterminé), **75,8 % sont des retraits** (dont 18,7 % « déplacés ») et **24,2 % des consommations** par une transaction (1,0 % mixtes). 4 406 disparitions indéterminées exclues. Toutes baisses confondues : 9 188 935 baisses, 9,7 % consommées. Sur 15 cycles (11.10) : 77,4 % / 22,6 % — **le résultat tient sur 752 cycles**.
- **Chronologie** : 70 530 des 229 073 disparitions (30,8 %) sont précédées dans la seconde d'un saut de bourse ≥ 5 $ dans le bon sens, contre 21,9 % avec des informations placées au hasard → l'information de bourse explique ≈ **8,9 points** des disparitions. Médianes après l'information (témoin) : réaction de l'autre côté 20 ms (31), 1er retrait 45 ms (50), 1re consommation 100 ms (146), disparition 222 ms (443). Retrait d'abord 69,6 %, consommation d'abord 28,5 % (témoin 72,8 % / 25,9 %).
- **Course** (ordre parti à la réception de l'information, +0,1 ms de calcul, +14 ms aller simple) : avant la disparition complète 81,7 %, **avant la 1re baisse du niveau visé 63,8 %** contre 74,8 % à des instants au hasard.
- **Course déclenchée par le carnet lui-même** : un niveau devenu meilleur prix vit en médiane 119 ms à ce rang avant de disparaître ; 73,4 % vivent plus que notre délai ≈ 22,7 ms (borne de faisabilité, pas un gain).
- **Signaux du bot (2 246)** : offre visée disparue dans les 2 s pour 1 460 — **retirée 1088** (74,5 %), consommée 128, mixte 244 ; encore là à 2 s 736 ; indéterminé 50.
- **Précurseurs d'une consommation** : déséquilibre du microprix AUC 0,876 juste avant (t−1 ms), 0,619 arrêté à t−500 ms ; modèle combiné 0,904 / 0,639.

## Phase 0 — audit des données

| Jour (heure suisse) | Cycles | Versions | Format des prix | Avec `fx` | Coupés | Changements P (Up) | Transactions | Photos 1 s comparées | Meilleur acheteur : prix · prix+taille | Meilleur vendeur : prix · prix+taille | 5 niveaux : prix acheteur · vendeur | Miroir |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11.10 | 158 | 14 | brut 3, cents 17, millièmes 138 | 141 | 3 | 7 747 374 | 211 119 | 44 944 | 99,6 % · 98,1 % | 99,5 % · 98,1 % | 97,3 % · 97,5 % | 100,0 % |
| 12.10 | 287 | 9 | millièmes 287 | 287 | 8 | 20 593 295 | 424 807 | 83 662 | 99,8 % · 98,3 % | 99,8 % · 98,5 % | 98,7 % · 98,6 % | 100,0 % |
| 13.10 | 279 | 12 | millièmes 279 | 279 | 0 | 23 953 982 | 474 472 | 81 856 | 99,9 % · 98,4 % | 99,9 % · 98,4 % | 99,2 % · 99,1 % | 100,0 % |
| 14.10 | 28 | 1 | millièmes 28 | 28 | 0 | 1 709 775 | 32 811 | 8 381 | 99,8 % · 98,9 % | 99,8 % · 98,8 % | 99,0 % · 98,9 % | 100,0 % |
| **total** | 752 | 33 | | 735 | 11 | 54 004 426 | 1 143 209 | 218 843 | 99,8 % · 98,3 % | 99,8 % · 98,4 % | 98,6 % · 98,6 % | 100,0 % |

- **Couverture** : 752 cycles, du 11.10 10:45 au 14.10 02:15 (heure suisse). Temps de cycle couvert par le flux : **61,1 h sur 62,7 h**. Cycles presque vides (< 5 000 changements, redémarrages) : 10. Cycles sans flux de prix des bourses : 0. Cycles avec flux agressifs `fx` : 735.
- **Format des prix** : 3 cycles bruts, 17 au cent, 732 en millièmes (le défaut « pas de 0,001 » signalé le 11.10 est corrigé dans l'enregistreur depuis ~12:30 le 11.10 ; les baisses près de 0/1 ne sont plus classées indéterminées pour ces cycles).
- **Perte due au filtre ±3 c** (simulée sur les cycles bruts) : meilleur prix+taille 98,0 % / 98,8 % ; 5 niveaux prix+taille 13,4 % / 11,7 %. Le meilleur niveau reste fiable.
- **Sens du champ `side`** : transactions dites acheteuses tombant sur l'offre Up 90,5 % ; dites vendeuses tombant sur la demande Up 84,9 % → `side` = côté du preneur (confirmé).
- **Faux appariement** (fenêtre témoin décalée à −200 ms) : 3,2 % des baisses, 1,8 % des disparitions complètes (à comparer à 9,7 % de baisses consommées).

## Phase 1 — pourquoi la meilleure offre disparaît (toutes les données)

Définitions identiques au 11.10 : *consommé* = transaction(s) au même prix dans [+14 ; +40] ms (heure Polymarket) couvrant la baisse ; *mixte* = couverture partielle ; *retiré* = aucune transaction ; *déplacé* = retiré et même quantité reposée à un autre prix dans [−5 ; +50] ms ; *indéterminé* = reconstruction non confirmée, pas de 0,001 (cycles au cent), ou après coupure.

| Côté | Toutes baisses | consommé | mixte | retiré | déplacé | indéterminé | Volume consommé / volume des baisses |
|---|---|---|---|---|---|---|---|
| offre Up (vendeur Up) | 4 575 061 | 447 124 | 70 265 | 2 857 998 | 1 177 543 | 22 131 | 5,8 % |
| demande Up = offre Down | 4 662 232 | 442 644 | 70 177 | 2 922 820 | 1 200 364 | 26 227 | 5,5 % |

**Disparitions complètes du meilleur niveau, par cause**

| Côté | Disparitions | consommé | mixte | retiré | déplacé | indéterminé | Durée au meilleur rang (ms) 10 % · méd. · 90 % — consommé | — retiré/déplacé | Taille méd. (parts) consommé · retiré |
|---|---|---|---|---|---|---|---|---|---|
| offre Up (vendeur Up) | 127 174 | 28 658 | 1 291 | 71 673 | 23 564 | 1 988 | 0 · 208 · 2 058 | 1 · 103 · 1 649 | 16,5 · 14,2 |
| demande Up = offre Down | 126 011 | 28 907 | 1 237 | 70 456 | 22 993 | 2 418 | 0 · 211 · 2 047 | 1 · 100 · 1 608 | 16,1 · 14,3 |
| **total** | 253 185 | 57 565 | 2 528 | 142 129 | 46 557 | 4 406 | | | |

**Stabilité par jour** (disparitions complètes hors indéterminé)

| Jour | Disparitions | retrait (retiré + déplacé) | consommation (consommé + mixte) |
|---|---|---|---|
| 11.10 | 56 935 | 77,1 % | 22,9 % |
| 12.10 | 98 444 | 76,1 % | 23,9 % |
| 13.10 | 86 350 | 74,7 % | 25,3 % |
| 14.10 | 7 050 | 76,6 % | 23,4 % |

**Remplissage après disparition complète (H499)**

| Côté | Cause | n | Nouvelle quantité au même prix dans 100 · 500 · 1000 ms | Meilleur prix revenu à ce prix ou mieux dans 100 · 500 · 1000 ms |
|---|---|---|---|---|
| offre Up (vendeur Up) | consommé | 29 949 | 18,3 % · 27,6 % · 35,1 % | 19,9 % · 28,8 % · 36,3 % |
| offre Up (vendeur Up) | retiré/déplacé | 95 237 | 22,3 % · 32,4 % · 40,3 % | 24,7 % · 34,2 % · 42,0 % |
| demande Up = offre Down | consommé | 30 144 | 18,1 % · 27,4 % · 35,0 % | 20,0 % · 28,7 % · 36,2 % |
| demande Up = offre Down | retiré/déplacé | 93 449 | 22,4 % · 32,7 % · 40,7 % | 24,8 % · 34,5 % · 42,4 % |

### Phase 1b — offres visées par les signaux réels du bot

Pour chaque signal enregistré, quantité disponible au prix du signal ou mieux suivie 2 s ; *disparue* = moins d'une part. Cause = part du volume disparu expliquée par des transactions appariées (≥ 80 % consommée, ≤ 20 % retirée, sinon mixte). Gagnant : `rapide.json`.

| Catégorie | Signaux | dont gagnants (réglés) | Taux de gain | Disparition (ms) méd. |
|---|---|---|---|---|
| consommée | 128 | 44/108 | 40,7 % | 77 |
| mixte | 244 | 76/192 | 39,6 % | 271 |
| retirée | 1088 | 278/881 | 31,6 % | 236 |
| encore là à 2 s | 736 | 80/610 | 13,1 % | — |
| indéterminé | 50 | 20/41 | 48,8 % | 78 |

Par règle (offre disparue dans 2 s : retirée / consommée+mixte / encore là) :

| Règle | Signaux | retirée | consommée + mixte | encore là à 2 s | gain si retirée | gain si encore là |
|---|---|---|---|---|---|---|
| V2-F ecart qui grandit | 560 | 262 | 76 | 210 | 24,9 % (209) | 13,2 % (174) |
| V2-F incertitude 0,01 % | 334 | 200 | 75 | 47 | 46,7 % (165) | 17,5 % (40) |
| cohorte A : zone + modele monte | 58 | 33 | 15 | 9 | 33,3 % (27) | 33,3 % (6) |
| cohorte B : V2-F corrige 0,015 % | 340 | 191 | 81 | 55 | 45,2 % (157) | 12,5 % (48) |
| desaccord 20 60-180 s | 541 | 225 | 52 | 255 | 21,5 % (177) | 13,0 % (207) |
| desaccord 20 jeton 0,35-0,65 | 29 | 12 | 11 | 5 | 63,6 % (11) | 25,0 % (4) |
| desaccord 30 | 384 | 165 | 62 | 155 | 17,8 % (135) | 10,7 % (131) |

Contrôle de la reconstruction contre la mesure en direct du bot (1832 signaux retrouvés dans `rapide.json`) : même verdict disparue / pas disparue pour 1820/1832 (99,3 %), même instant à 5 ms près pour 1802/1832.

## Phase 2 — chronologie : information → réaction → retrait → transaction

*Information* (fixée à l'avance, comme le 11.10) : saut ≥ 5 $ d'une bourse (Bybit perp, OKX perp, Binance, Coinbase) entre deux échantillons 50 ms, dans le sens qui rend l'offre trop bon marché ; heure = réception à Dublin. **Nouveau** : flux net agressif (achats − ventes preneurs des 4 bourses) ≥ 250 k$ dans une tranche de 50 ms (seuil fixé à l'avance, cycles avec `fx` seulement).

Informations détectées : perp 28 116, okx 23 391, bn 13 616, cb 57 147, cl 213 508, fx 18 635.

**Bourses, saut ≥ 5 $ (critère principal)** — disparitions complètes (hors indét., dans le cycle) : 229 073 ; précédées d'une information : **70 530** (30,8 %) — témoin au hasard (20 tirages) : 21,9 %.

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté | 66 283 | 2 · 20 · 147 | 31 |
| 1er retrait au meilleur niveau | 66 787 | 5 · 45 · 215 | 50 |
| 1re consommation au meilleur niveau | 52 828 | 13 · 100 · 366 | 146 |
| disparition complète | 70 530 | 46 · 222 · 757 | 443 |

Premier après l'information : retrait d'abord 69,6 % (témoin 72,8 %) ; consommation d'abord 28,5 % (témoin 25,9 %) ; même ms 1,8 % (témoin 1,3 %) ; aucun avant la disparition 0,1 % (témoin 0,0 %).

Course : avant la disparition complète 81,7 % (aller simple 14 ms), 77,9 % (aller-retour 28 ms) ; **avant la 1re baisse du niveau : 63,8 %** — témoin 91,2 % et 74,8 %.

**Sensibilité : bourses, saut ≥ 2 $** — disparitions complètes (hors indét., dans le cycle) : 229 073 ; précédées d'une information : **102 241** (44,6 %).

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté | 94 649 | 2 · 18 · 139 | — |
| 1er retrait au meilleur niveau | 95 455 | 5 · 40 · 203 | — |
| 1re consommation au meilleur niveau | 72 252 | 11 · 90 · 354 | — |
| disparition complète | 102 241 | 30 · 178 · 711 | — |

Premier après l'information : retrait d'abord 68,8 % ; consommation d'abord 28,9 % ; même ms 2,1 % ; aucun avant la disparition 0,2 %.

Course : avant la disparition complète 77,5 % (aller simple 14 ms), 73,2 % (aller-retour 28 ms) ; **avant la 1re baisse du niveau : 59,0 %**.

**Chainlink (nouvelle valeur dans le bon sens)** — disparitions complètes (hors indét., dans le cycle) : 229 073 ; précédées d'une information : **100 352** (43,8 %) — témoin au hasard (20 tirages) : 38,0 %.

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté | 94 670 | 3 · 31 · 229 | 33 |
| 1er retrait au meilleur niveau | 97 131 | 6 · 55 · 280 | 53 |
| 1re consommation au meilleur niveau | 78 027 | 18 · 154 · 525 | 146 |
| disparition complète | 100 352 | 96 · 461 · 874 | 439 |

Premier après l'information : retrait d'abord 71,8 % (témoin 72,0 %) ; consommation d'abord 26,7 % (témoin 26,6 %) ; même ms 1,4 % (témoin 1,4 %) ; aucun avant la disparition 0,1 % (témoin 0,0 %).

Course : avant la disparition complète 94,1 % (aller simple 14 ms), 92,5 % (aller-retour 28 ms) ; **avant la 1re baisse du niveau : 79,4 %** — témoin 92,0 % et 76,9 %.

**Flux agressifs ≥ 250 k$ en 50 ms (nouveau)** — disparitions complètes (hors indét., dans le cycle) : 224 209 ; précédées d'une information : **19 178** (8,6 %) — témoin au hasard (20 tirages) : 3,9 %.

| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin : médiane |
|---|---|---|---|
| 1re réaction de l'autre côté | 18 440 | 1 · 15 · 123 | 32 |
| 1er retrait au meilleur niveau | 18 588 | 3 · 30 · 188 | 52 |
| 1re consommation au meilleur niveau | 15 078 | 16 · 132 · 378 | 152 |
| disparition complète | 19 178 | 57 · 265 · 773 | 489 |

Premier après l'information : retrait d'abord 78,2 % (témoin 73,1 %) ; consommation d'abord 20,2 % (témoin 25,6 %) ; même ms 1,5 % (témoin 1,2 %) ; aucun avant la disparition 0,0 % (témoin 0,0 %).

Course : avant la disparition complète 86,2 % (aller simple 14 ms), 83,5 % (aller-retour 28 ms) ; **avant la 1re baisse du niveau : 68,2 %** — témoin 92,5 % et 76,4 %.

**Course déclenchée par le carnet lui-même** : délai ≈ 22,7 ms ; durée au meilleur rang des niveaux qui disparaissent 1 · 119 · 1 736 ms ; plus longue que notre délai pour **73,4 %**.

### Précurseurs d'une consommation complète (contre 3 instants témoins au hasard par événement)

| Fenêtre | Consommations · témoins | déséquilibre du microprix vers l'offre consommée (en fin de fenêtre) | variation de l'écart (compression < 0) | variation log taille du meilleur acheteur d'en face (renforcement > 0) | variation du prix d'en face (millièmes, vers l'offre > 0) | variation log taille de l'offre consommée | écart en fin de fenêtre (millièmes) | Modèle combiné (AUC, validation croisée par cycle) |
|---|---|---|---|---|---|---|---|---|
| 100 ms, jusqu'à t−1 ms | 52 844 · 158 477 | 0,876 | 0,521 | 0,566 | 0,608 | 0,299 | 0,567 | 0,904 |
| 200 ms, jusqu'à t−1 ms | 52 805 · 158 366 | 0,876 | 0,528 | 0,594 | 0,638 | 0,240 | 0,568 | 0,907 |
| 500 ms, jusqu'à t−1 ms | 52 663 · 157 943 | 0,875 | 0,542 | 0,616 | 0,658 | 0,184 | 0,567 | 0,908 |
| 100 ms, arrêté à t−100 ms | 52 812 · 158 383 | 0,799 | 0,505 | 0,620 | 0,571 | 0,340 | 0,545 | 0,834 |
| 200 ms, arrêté à t−200 ms | 52 708 · 158 069 | 0,730 | 0,511 | 0,595 | 0,575 | 0,356 | 0,539 | 0,762 |
| 500 ms, arrêté à t−500 ms | 52 576 · 157 679 | 0,619 | 0,509 | 0,539 | 0,543 | 0,431 | 0,525 | 0,639 |

Lecture : « jusqu'à t−1 ms » = en grande partie mécanique (la file fond déjà) ; « arrêté à t−h » = seulement ce qui était connu h ms avant (utilisable). Témoins non appariés sur prix ni taille.

## Limites

- 3 jours et demi (11.10 → 14.10), un seul actif (BTC 5 min). Les bourses arrivent à Dublin avec ~45 ms (Coinbase) à ~100–130 ms (Bybit, OKX, Binance) de retard ; échantillon 50 ms.
- Profondeur au-delà de ±3 c périmée entre deux carnets complets (10 s). Horloges Dublin (NTP) / Polymarket comparées directement (décalage inclus dans les 8,6 ms).
- Durée d'exécution : 463 s.
