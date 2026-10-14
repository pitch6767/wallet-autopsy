# Bot95 — simulation « achat early peu cher » + B3 (27 jours, 12.09 → 08.10.2026)

Demande de Pitch (14.10, 13:10) : « fais une simulation avec 10 $ early achat peu chère et B3 combiné ».

## Verdict

**Acheter tôt le côté peu cher perd de l'argent, avec certitude statistique.** Sur la validation (01–08.10) :

- **E1** (côté le moins cher ≤ 0,45, entre 10 et 60 s) : 2 279 achats, 36 % gagnés pour un prix moyen de 0,373, ROI **−7,5 %**, P&L **−1 720 $**, IC 90 % **[−2 737 ; −701] $** ;
- **E2** (≤ 0,40) : 2 116 achats, ROI **−5,3 %**, P&L **−1 125 $**, IC 90 % [−2 173 ; −70] $ ;
- l'exploration donne la même chose (−5,5 % et −5,8 %). L'intervalle est entièrement sous 0 dans les deux périodes.

La raison est simple : le côté peu cher gagne à peu près aussi souvent que son prix l'annonce (36 % gagnés pour 37 % payés), et les frais coûtent environ 4,4 % de la mise à ce prix. Il n'y a pas d'aubaine à acheter tôt le côté bon marché.

**Ajouter B3 ne sauve rien.** B3 gagne toujours un peu de son côté (validation : 169 achats, 168 gagnés, **+42 $**, IC 90 % [+21 ; +58] $ ; c'est exactement le résultat de H1084). Mais à côté des −1 720 $ de l'achat early, ces +42 $ ne pèsent presque rien :

- **E1 + B3** (les deux, indépendamment) : validation **−1 678 $**, ROI −6,9 %, IC 90 % [−2 727 ; −638] $ ;
- **E3** (B3 seulement dans les cycles où l'early a acheté, en renfort ou en couverture) : validation **−1 679 $**, ROI −6,9 %, IC 90 % [−2 717 ; −652] $.

**La couverture ne sauve jamais une perte.** Dans E3, B3 achète l'autre côté 89 fois en validation (331 fois au total). L'achat early perd alors presque toujours (88 fois sur 89). Avec 10 $ de couverture à 0,97, le gain n'est que d'environ 0,30 $ : la perte du cycle passe de −10 $ à −9,67 $ en moyenne. **Aucune couverture n'annule la perte** (0 sur 331). Pour l'annuler, il faudrait mettre environ 350 $ sur la couverture.

**Conclusion : aucune des règles early n'a d'avantage, et la combinaison avec B3 est perdante.** Seule B3 seule reste positive, comme dans H1084. Les règles early n'ont pas été pré-enregistrées ; mais comme leur intervalle est entièrement négatif dans les deux périodes, ce point ne change pas la conclusion.

Aucun ordre n'a été passé. Aucun fichier du bot (bot95/src, bot95/rapide), aucun workflow et aucun fantôme n'a été modifié.

## Les règles simulées (10 $ par achat, gardé jusqu'au règlement)

| Règle | Quand | Quoi |
|---|---|---|
| E1 « early peu cher » | 10 à 60 s après l'ouverture (instants 10, 15, …, 60 s) | le côté le moins cher, si son prix est ≤ 0,45 ; un achat par cycle |
| E2 | idem | le côté le moins cher, si son prix est ≤ 0,40 |
| E3 | E1, puis 20 à 60 s avant la fin | si B3 déclenche sur le même côté : renfort ; sur l'autre côté : couverture |
| B3 (référence) | 20 à 60 s avant la fin | favori 0,90–0,98 et BTC à au moins 3 écarts-types du prix à battre, dans le sens du favori |
| E1 + B3 | les deux | E1 et B3 chacun de leur côté, dans tous les cycles |

## Résultats — validation (01–08.10, 2 304 cycles)

| Stratégie | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % du P&L | Perte max. depuis un sommet | Pire série de cycles perdants | Mise totale (max. par cycle) |
|---|---|---|---|---|---|---|---|---|---|
| E1 | 2 279 | 814 (35,7 %) | 0,373 | −7,5 % | −1 720 $ | [−2 737 ; −701] | 2 046 $ | 20 | 22 790 $ (10 $) |
| E2 | 2 116 | 707 (33,4 %) | 0,341 | −5,3 % | −1 125 $ | [−2 173 ; −70] | 1 468 $ | 17 | 21 160 $ (10 $) |
| E3 | 2 445 | 979 (40,0 %) | 0,413 | −6,9 % | −1 679 $ | [−2 717 ; −652] | 2 008 $ | 20 | 24 450 $ (20 $) |
| B3 seule | 169 | 168 (99,4 %) | 0,969 | +2,5 % | +42 $ | [+21 ; +58] | 10 $ | 1 | 1 690 $ (10 $) |
| E1 + B3 | 2 448 | 982 (40,1 %) | 0,414 | −6,9 % | −1 678 $ | [−2 727 ; −638] | 2 008 $ | 20 | 24 480 $ (20 $) |

## Résultats — exploration (12.09–30.09, 5 459 cycles)

| Stratégie | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % du P&L | Perte max. depuis un sommet | Pire série | Mise totale (max. par cycle) |
|---|---|---|---|---|---|---|---|---|---|
| E1 | 5 289 | 1 946 (36,8 %) | 0,372 | −5,5 % | −2 907 $ | [−4 462 ; −1 379] | 2 959 $ | 15 | 52 890 $ (10 $) |
| E2 | 4 872 | 1 621 (33,3 %) | 0,338 | −5,8 % | −2 832 $ | [−4 402 ; −1 248] | 2 966 $ | 21 | 48 720 $ (10 $) |
| E3 | 5 767 | 2 416 (41,9 %) | 0,421 | −4,9 % | −2 845 $ | [−4 390 ; −1 326] | 2 899 $ | 15 | 57 670 $ (20 $) |
| B3 seule | 506 | 498 (98,4 %) | 0,968 | +1,5 % | +75 $ | [+24 ; +121] | 31 $ | 1 | 5 060 $ (10 $) |
| E1 + B3 | 5 795 | 2 444 (42,2 %) | 0,424 | −4,9 % | −2 832 $ | [−4 400 ; −1 285] | 2 887 $ | 15 | 57 950 $ (20 $) |

## Résultats — total des 27 jours (7 763 cycles)

| Stratégie | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % du P&L | Perte max. depuis un sommet | Pire série | Mise totale (max. par cycle) |
|---|---|---|---|---|---|---|---|---|---|
| E1 | 7 568 | 2 760 (36,5 %) | 0,372 | −6,1 % | −4 627 $ | [−6 481 ; −2 763] | 4 852 $ | 20 | 75 680 $ (10 $) |
| E2 | 6 988 | 2 328 (33,3 %) | 0,339 | −5,7 % | −3 957 $ | [−5 864 ; −2 029] | 4 205 $ | 21 | 69 880 $ (10 $) |
| E3 | 8 212 | 3 395 (41,3 %) | 0,419 | −5,5 % | −4 524 $ | [−6 383 ; −2 616] | 4 753 $ | 20 | 82 120 $ (20 $) |
| B3 seule | 675 | 666 (98,7 %) | 0,968 | +1,7 % | +117 $ | [+62 ; +166] | 31 $ | 1 | 6 750 $ (10 $) |
| E1 + B3 | 8 243 | 3 426 (41,6 %) | 0,421 | −5,5 % | −4 510 $ | [−6 358 ; −2 665] | 4 740 $ | 20 | 82 430 $ (20 $) |

Lecture : « Perte max. depuis un sommet » = plus forte baisse du P&L cumulé, cycle après cycle. « Pire série » = nombre maximal de cycles perdants d'affilée, parmi les cycles où la stratégie a acheté. « Mise totale » = somme de toutes les mises ; comme un cycle dure 5 minutes et que tout est réglé à la fin, l'argent engagé en même temps ne dépasse jamais la mise maximale d'un cycle (10 $ ou 20 $).

## Au prix pessimiste

Le prix pessimiste est le plus haut entre le prix du signal et le prix payé juste après (on ne profite pas d'une glissade favorable).

| Stratégie | ROI validation | P&L validation | IC 90 % validation | P&L total | IC 90 % total |
|---|---|---|---|---|---|
| E1 | −13,0 % | −2 968 $ | [−3 914 ; −1 993] | −8 913 $ | [−10 632 ; −7 227] |
| E2 | −12,1 % | −2 559 $ | [−3 529 ; −1 616] | −8 550 $ | [−10 283 ; −6 788] |
| E3 | −12,0 % | −2 936 $ | [−3 887 ; −1 984] | −8 838 $ | [−10 524 ; −7 126] |
| B3 seule | +2,0 % | +33 $ | [+13 ; +47] | +84 $ | [+31 ; +132] |
| E1 + B3 | −12,0 % | −2 935 $ | [−3 874 ; −1 960] | −8 829 $ | [−10 602 ; −7 097] |

## E3 : renforts et couvertures

| | Exploration | Validation | Total |
|---|---|---|---|
| Achats early (E1) | 5 289 | 2 279 | 7 568 |
| Cycles où B3 déclenche ensuite | 478 | 166 | 644 |
| Renforts (B3 du même côté) — gagnés | 236 — 232 | 77 — 77 | 313 — 309 |
| P&L des renforts | +32 $ | +21 $ | +53 $ |
| Couvertures (B3 de l'autre côté) — gagnées | 242 — 238 | 89 — 88 | 331 — 326 |
| P&L des couvertures | +30 $ | +19 $ | +50 $ |
| Pertes early adoucies par la couverture | 238 | 88 | 326 |
| Perte moyenne du cycle, sans → avec couverture | −10,00 → −9,71 $ | −10,00 → −9,67 $ | −10,00 → −9,69 $ |
| Couvertures qui annulent la perte | 0 | 0 | 0 |
| Couvertures perdues | 4 | 1 | 5 |

Une couverture à 10 $ achetée vers 0,97 ne rapporte qu'environ 0,30 $ quand elle gagne : elle ne fait qu'effleurer la perte de 10 $ de l'achat early. Renforts et couvertures, ce sont en fait simplement les achats B3 ; ils ajoutent environ +40 $ en validation, contre −1 720 $ pour l'achat early.

## Pourquoi l'achat early perd

- **Le prix est juste.** En validation, le côté peu cher gagne 35,7 % des fois pour un prix payé moyen de 0,373 (E1). Le marché n'est pas en retard au début du cycle.
- **Les frais coûtent cher sur les prix moyens.** Ils valent 0,07 × (1 − p) de la mise, soit environ 4,4 % à 0,37. Pour un favori à 0,97, ce n'est que 0,2 %.
- **Presque tous les cycles déclenchent.** À 10 s, il y a presque toujours un côté sous 0,45 : E1 achète dans 99 % des cycles, la plupart du temps dès l'instant 10 s (1 641 achats sur 2 279 en validation). La règle revient donc à « acheter le côté qui a déjà un peu perdu pendant les 10 premières secondes ». Elle ne sélectionne rien.
- **Les séries de pertes sont longues** : jusqu'à 20 cycles perdants d'affilée (1 h 40), et une baisse maximale d'environ 2 000 $ sur 8 jours à 10 $ par achat.

## Méthode

- **Données** : les mêmes que H1084. Transactions publiques Polymarket BTC 5 min (achats seulement) et Binance BTCUSDT à la seconde. Aucun marché ouvert à partir du 09.10 00:00 UTC n'est utilisé.
- **Périodes** : exploration 12.09–30.09 (5 459 cycles), validation 01.10–08.10 (2 304 cycles).
- **Prix du signal** : médiane des achats des 6 s précédentes, avec au moins 2 achats.
- **Prix payé** : médiane des achats du côté acheté entre t+1 et t+6 s.
- **Frais** : 0,07·p·(1−p). Chaque règle fait au plus un achat par cycle : le premier instant qui déclenche et où une transaction a eu lieu. Le billet est gardé jusqu'au règlement.
- **B3** : reprise à l'identique de H1084. Contrôle : on retrouve exactement 169 achats, 168 gagnés et +41,6 $ en validation.
- **Intervalles** : bootstrap par cycles, 10 000 tirages, percentiles 5 et 95. Tous les cycles de la période comptent, à 0 $ quand rien n'est acheté.
- **Pas de correction pour tests multiples** : la simulation est descriptive. Une correction élargirait les intervalles, mais celui d'E1 reste très loin de 0.

## Limites

- **Les règles early ont été définies le 14.10, après avoir vu ces données en partie.** Elles n'ont pas été pré-enregistrées ; seuls les chiffres de validation avec leur IC comptent. Comme ils sont nettement négatifs, cette limite ne joue pas en faveur d'un avantage.
- **E2 en validation** : l'IC [−2 173 ; −70] $ est sous 0. Mais avec une correction pour plusieurs règles, sa borne haute toucherait probablement 0. On sait que E2 ne gagne pas ; on ne sait pas exactement combien elle perd.
- **Exécution** : le prix payé est celui des autres acheteurs dans les 6 s suivantes, pas celui d'un vrai ordre. Au prix pessimiste, les pertes doublent environ.
- **Binance remplace Chainlink** pour le calcul de B3 (bon gagnant dans ~97,7 % des cycles), comme dans H1084.
- **Seuil de B3** : le seuil 3 a été choisi après plusieurs essais (voir H1084), ce qui rend B3 petite et fragile même seule.

## Fichiers

- Script : `etude/bot5min/simulation_early_b3.py`
- Chiffres bruts : `etude/bot5min/simulation_early_b3.json`
- PDF : `etude/bot5min/archives/pdf/simulation_early_b3.pdf`
