# Bot95 — H804 à H806 — rapport du 11.10.2026

Étude hors ligne uniquement. Aucun ordre. Aucun bot ni fantôme modifié. La période réservée n'a pas été lue.

**Données :**
- fantômes maker en direct à Dublin : 5 311 ordres réglés, de 10:55 à 16:55 UTC ;
- 595 marchés complets, avec les exécutions de tous les wallets ;
- 83 cycles de carnet enregistrés à Dublin.

## 1. H804 — M21 contre M1 et M4

**Sur les 24 cycles où M1, M21 et M4 ont tous coté** (mêmes hypothèses d'exécution, fills « prudents ») :

| Moteur | Ordres | Remplis | Parts | P&L | Par ordre | Par part | IC 90 % par cycle | Drawdown | Capital moyen / max par cycle |
|---|---|---|---|---|---|---|---|---|---|
| M1 | 99 | 61 | 21 018 | −2 396 $ | −24,2 $ | −11,4 c | [−133 ; −64] $ | 2 396 | 125 / 250 $ |
| M21 | 161 | 103 | 2 980 | −90 $ | −0,6 $ | −3,0 c | [−17 ; +10] $ | 176 | 80 / 212 $ |
| M4 | 235 | 178 | 9 614 | −489 $ | −2,1 $ | −5,1 c | [−44 ; +4] $ | 606 | 117 / 342 $ |
| M6 | 656 | 622 | 38 947 | +200 $ | +0,3 $ | +0,5 c | [−132 ; +168] $ | 2 572 | 557 / 1 065 $ |
| M8 | 68 | 51 | 17 631 | −1 896 $ | −27,9 $ | −10,8 c | [−129 ; −50] $ | 1 896 | 119 / 250 $ |

**Sur tous les cycles de chaque moteur :**

| Moteur | P&L | Par part | Sans ses 3 meilleurs cycles |
|---|---|---|---|
| M1 | −72 $ | −0,2 c | −3 013 $ |
| M21 | −151 $ | −4,6 c | −376 $ |
| M4 | −650 $ | −3,4 c | — |
| M6 | −826 $ | −1,2 c | — |
| M8 | −1 919 $ | −6,5 c | — |

**Réponse à « pourquoi M1/M21 seraient positifs par part » : ils ne le sont pas.**

Le +2,1 c / +1,6 c par part du rapport précédent venait d'un sous-échantillon plus court. Sur les données plus longues, tous les moteurs maker sont négatifs, sauf M6, qui est quasi nul avec un IC très large.

- **M1 et M8** achètent des outsiders à 0,14 en moyenne. Ils ne gagnent que 3 % du temps, et 60 à 64 % des parts sont remplies sous condition toxique. Leur résultat dépend entièrement de rares jackpots.
- **M21** achète le favori à 0,64 en moyenne et gagne 61 % du temps. Mais il est rempli juste avant que le prix baisse (markout −1,6 c à 5 s), donc il perd sur ces fills.

## 2. H805 — Achats maker à 0,95–0,99 selon le temps restant (M9)

**A. Fills observés de tous les makers** (595 marchés). La borne haute est la borne de Clopper-Pearson à 95 %.

| Prix | Fenêtre | Fills / marchés | Fills perdants | Borne haute du taux de perte | Seuil de rentabilité | Résultat | Pire marché |
|---|---|---|---|---|---|---|---|
| ≥ 0,99 | 30–15 s | 4 830 / 476 | 34 | 0,93 % | ≈ 0,7 % | **−1 033 $** | −4 190 $ |
| ≥ 0,99 | 15–5 s | 3 304 / 487 | 0 | 0,08 % | ≈ 0,7 % | +2 084 $ | 0 |
| ≥ 0,99 | 5–0 s | 1 201 / 268 | 0 | 0,22 % | ≈ 0,7 % | +834 $ | 0 |
| 0,98–0,99 | 30–15 s | 1 293 / 118 | 11 | 1,39 % | ≈ 1,5 % | +404 $ | −457 $ |
| 0,95–0,97 | 30–15 s | 1 547 / 86 | 32 | 2,75 % | ≈ 4 % | +723 $ | −480 $ |

**Attention :** zéro perte n'est pas une garantie. L'unité de risque est le marché, car un retournement touche tous les fills du même marché d'un coup.

- Après 15 s restantes, 0 perte sur 487 marchés. La « règle de trois » (3 / nombre de marchés) donne une borne d'environ **0,6 % par marché**, au même niveau que le seuil de rentabilité à 0,99.
- Le pire marché observé a coûté **−4 190 $** (entre 30 et 15 s).
- Sélection adverse, entre 30 et 15 s à ≥ 0,99 : −1,15 c à +5 s.

**B. Fills non obtenus.** Simulation : on pose une offre au meilleur acheteur du favori (prix 0,95–0,99) sur 61 à 64 cycles Dublin, et on la garde jusqu'à la fin.

| Pose | Taux de fill (prudent / central / optimiste) | Résultat |
|---|---|---|
| 30 s avant la fin | 9 % / 14 % / 36 % | +14 à +50 $ |
| 15 s avant la fin | 0 % / 0 % / 3 % | ≈ 0 |
| 5 s avant la fin | 0 % / 0 % / 5 % | ≈ 0 |

**Conclusion :** la fenêtre sûre (15–0 s) est **inaccessible** pour un nouvel ordre. Elle est servie par des makers déjà dans la file. La fenêtre où l'on est rempli (30–15 s) est justement celle des retournements.

## 3. H806 — Sélection des fills : makers réels contre nos fantômes

**Échantillon :** 83 912 fills de makers réels datés à la milliseconde, contre 4 588 fills de nos fantômes, sur les mêmes cycles.

| | Makers réels | Nos fantômes |
|---|---|---|
| Markout +5 s | **+0,67 c** | **−0,2 à −2,9 c** |
| Fills au meilleur prix | 95 % | 55 % |
| Profondeur médiane à leur niveau | 272 parts | 50 parts |
| Taille du preneur < 10 $ | 96 % | non mesurée |
| Volatilité 30 s | 2,8 c | 5,5 c |

À prix et minute du cycle identiques, les makers réels font environ +0 c à +5 s, alors que nos fantômes font −1 à −3 c. Au règlement, l'écart est encore plus grand.

**Régression commune du markout à +5 s** (IC 90 % par cycles). L'écart brut fantômes − réels est de −1,98 c ; **il tombe à −0,64 c [−1,48 ; +0,33] une fois ces conditions prises en compte**, sans utiliser l'identité des wallets.

| Condition | Effet sur le markout +5 s |
|---|---|
| Être au meilleur prix | +1,9 c [+1,1 ; +2,7] |
| Profondeur à notre niveau (par unité de log) | +0,5 c [+0,3 ; +0,7] |
| Volatilité | léger effet |

**Mécanismes reproductibles :**
- n'être rempli qu'au meilleur prix ;
- n'être rempli que dans une file profonde, où les petits preneurs consomment sans déplacer le prix ;
- éviter les moments volatils.

Nos fantômes sont surtout remplis quand le prix les traverse : ils ne sont plus au meilleur prix, la file est mince et le marché bouge.

## 4. Verdicts

| Piste | Verdict |
|---|---|
| Veto « 3 wallets », Reverse Bot95 | **Abandonnés** (déjà décidé) |
| M1, M8 (maker sur les signaux, outsiders) | **Abandonner** : négatifs, dépendants des jackpots, fills toxiques |
| M21 (maker du favori) | **Abandonner en l'état** : −3 à −4,6 c par part, sélection adverse |
| M4 et variantes, M6 | **Abandonner** : négatifs ou nuls, IC larges |
| M9 (0,95–0,99 en fin de cycle) | **Abandonner** : la fenêtre sûre est inaccessible, la fenêtre accessible est risquée (−4 190 $ sur un seul marché) |
| H806 — mécanisme « meilleur prix + file profonde + calme » | **Poursuivre hors ligne seulement** : c'est la seule explication reproductible. À tester comme filtre sur les fantômes existants avant toute proposition |

Les verdicts reposent sur une seule journée de données en direct. Aucun fantôme n'est arrêté ou modifié sans ton accord.
