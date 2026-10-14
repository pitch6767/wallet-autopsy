# Bot95 — H1087 : confirmation de B3 et X2 sur 5 jours neufs (09.10 → 13.10.2026)

## Verdict

**B3 : non confirmée.** Sur les jours neufs, B3 **perd un peu** :

- 95 achats, 91 gagnés (95,8 %) pour un prix moyen de 0,957 ;
- ROI **−1,3 %**, P&L **−13 $** à 10 $ par achat ;
- intervalle de confiance à 90 % : **[−49 ; +18] $**. Il contient 0.
- Au prix pessimiste : ROI −1,8 %, P&L −17 $, IC 90 % [−53 ; +13] $.

En validation (01–08.10), B3 avait gagné 168 fois sur 169. Ici, 4 pertes sont tombées le même jour (10.10) et effacent les gains des autres jours. Comme chaque achat gagne environ 0,40 $ et chaque perte coûte 10 $, **une seule perte efface environ 25 gains**. Avec si peu de pertes, quelques jours ne suffisent pas à savoir si la règle gagne.

**X2 : non confirmée.** Sur les jours neufs, X2 **gagne**, mais pas de façon démontrée :

- 149 achats, 74 gagnés (49,7 %) pour un prix moyen de 0,455 ;
- ROI **+9,1 %**, P&L **+136 $** à 10 $ par achat ;
- intervalle de confiance à 90 % : **[−118 ; +390] $**. Il contient 0.

Le signe est le même qu'en validation (+11,6 %), mais l'écart est trop petit face au hasard. Deux jours sur cinq sont négatifs. Ce résultat **ne prouve pas** que X2 est rentable.

Les deux fantômes continuent de tourner comme avant : rien n'a été modifié. Aucun ordre n'a été passé. Aucun fichier du bot (bot95/src, bot95/rapide), aucun workflow et aucun fantôme n'a été touché.

## Règles testées (figées avant tout calcul)

Le script a été écrit et poussé (commit bc7c12d) **avant** de calculer le moindre chiffre sur 09–13.10. Le calcul a ensuite été lancé une seule fois. Avant le gel, on a vérifié sur le 08.10 (jour de validation déjà lu) que la copie du code redonne **exactement** les mêmes achats que les scripts d'origine H1084 et H1083 (10 achats B3, 45 achats X2, mêmes cycles, mêmes prix).

- **B3** (H1084) : entre 60 et 20 secondes avant la fin, si le favori vaut 0,90 à 0,98 et que BTC est à au moins 3 écarts-types du prix à battre dans le sens du favori, on achète le favori. Prix payé = prix médian des achats du favori dans les 6 secondes qui suivent. Un achat par cycle au plus.
- **X2** (H1083) : 10 secondes après le début du cycle, si BTC a baissé sur les 30 dernières minutes (r30 ≤ −1,018 écart-type) **et** sur les 5 dernières minutes (r5 < 0), on achète Up. Prix payé = prix médian des achats Up entre 10 et 16 secondes.
- Pour les deux : frais 0,07·p·(1−p), billet gardé jusqu'au règlement, 10 $ par achat.
- **Critère, pour chaque règle** : ROI > 0 **et** intervalle à 90 % du P&L entièrement au-dessus de 0. L'intervalle est calculé en tirant des cycles au hasard (10 000 tirages ; un cycle sans achat compte pour 0 $).

## Résultats par jour

**B3 — prix observé**

| Jour | Cycles | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|---|
| 09.10 | 288 | 16 | 16 | 0,963 | +3,9 % | +6 $ | [+3 ; +11] $ |
| 10.10 | 288 | 41 | 37 | 0,942 | −7,3 % | −30 $ | [−64 ; +1] $ |
| 11.10 | 288 | 24 | 24 | 0,967 | +3,3 % | +8 $ | [+5 ; +12] $ |
| 12.10 | 178 | 5 | 5 | 0,981 | +1,8 % | +1 $ | [+0 ; +2] $ |
| 13.10 | 251 | 9 | 9 | 0,974 | +2,4 % | +2 $ | [+1 ; +4] $ |
| **Total** | **1 293** | **95** | **91** | **0,957** | **−1,3 %** | **−13 $** | **[−49 ; +18] $** |

**B3 — prix pessimiste** (le plus haut entre le prix au signal et le prix payé)

| Jour | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|
| 09.10 | 16 | 16 | 0,976 | +2,3 % | +4 $ | [+2 ; +5] $ |
| 10.10 | 41 | 37 | 0,973 | −7,6 % | −31 $ | [−65 ; −1] $ |
| 11.10 | 24 | 24 | 0,970 | +2,9 % | +7 $ | [+4 ; +10] $ |
| 12.10 | 5 | 5 | 0,981 | +1,8 % | +1 $ | [+0 ; +2] $ |
| 13.10 | 9 | 9 | 0,974 | +2,4 % | +2 $ | [+1 ; +4] $ |
| **Total** | **95** | **91** | **0,973** | **−1,8 %** | **−17 $** | **[−53 ; +13] $** |

Les intervalles d'un jour sans perte (par exemple [+3 ; +11] $) ne veulent pas dire que la règle est sûre : ils disent seulement que ce jour-là, aucune perte n'est arrivée.

Les 4 pertes du 10.10 : deux achats payés 0,96 et 0,98 (favori qui se retourne dans les dernières secondes), et deux achats où le prix payé était tombé à **0,32 et 0,41** dans les 6 secondes après le signal (le favori à 0,93–0,97 s'effondrait déjà). C'est le piège déjà décrit dans H1084 : un achat n'est servi que si quelqu'un vend, et on vend surtout quand le favori vacille.

**X2 — prix observé**

| Jour | Cycles | Achats | Gagnés | Prix moyen | ROI | P&L | IC 90 % |
|---|---|---|---|---|---|---|---|
| 09.10 | 286 | 31 | 17 | 0,469 | +13,9 % | +43 $ | [−56 ; +150] $ |
| 10.10 | 286 | 29 | 10 | 0,425 | −19,9 % | −58 $ | [−159 ; +50] $ |
| 11.10 | 286 | 27 | 15 | 0,463 | +38,1 % | +103 $ | [−31 ; +252] $ |
| 12.10 | 132 | 28 | 13 | 0,440 | −1,6 % | −4 $ | [−102 ; +100] $ |
| 13.10 | 269 | 34 | 19 | 0,475 | +15,3 % | +52 $ | [−58 ; +172] $ |
| **Total** | **1 259** | **149** | **74** | **0,455** | **+9,1 %** | **+136 $** | **[−118 ; +390] $** |

## Cycles écartés

Les 5 jours comptent 1 440 cycles, tous avec un résultat officiel.

- **B3** : 147 cycles écartés faute de données BTC complètes, tous les 12.10 (110) et 13.10 (37). Il reste 1 293 cycles.
- **X2** : 181 cycles écartés. 113 faute de données BTC (surtout le 12.10), 66 avec moins de 5 achats autour de l'ouverture (règle d'origine de H1083), 2 sans prix de marché lisible. Il reste 1 259 cycles.

## Limites

- **Prix BTC.** Jusqu'au 11.10, ce sont les bougies Binance 1 s utilisées par les études d'origine. Les 12.10 et 13.10 viennent des relevés du bot (colonne binance_spot), avec des trous. Sur ces deux jours, une partie des cycles manque, surtout le 12.10.
- **Écart-type avec trous.** Il est calculé sur les écarts 1 s disponibles (au moins la moitié de l'heure exigée). Une valeur peut être reportée de 2 secondes au plus, ce qui baisse un peu l'écart-type.
- **Peu de pertes pour B3.** Avec 95 achats, les 4 pertes décident de tout. Il faudrait plusieurs centaines d'achats de plus pour trancher.
- **Prix simulé.** Le prix payé est celui des autres acheteurs dans les secondes qui suivent, pas celui d'un vrai ordre. Les fantômes en direct mesurent mieux le prix réellement obtenu.
- **Deux règles testées.** Chacune est jugée seule, sans correction pour essais multiples. Une correction rendrait les deux verdicts encore plus nets.

## Fichiers

- Script figé : etude/bot5min/confirmation_b3_x2_h1087.py (commit bc7c12d)
- Chiffres bruts : etude/bot5min/confirmation_b3_x2_h1087.json
- PDF : etude/bot5min/archives/pdf/confirmation_b3_x2_h1087.pdf
