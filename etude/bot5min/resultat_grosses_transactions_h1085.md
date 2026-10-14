# Bot95 — H1085 : les grosses transactions (27 jours, 12.09 → 08.10.2026)

## Verdict

**Suivre ou contrer les gros acheteurs ne rapporte rien de démontré.** Aucune des 4 règles figées ne passe le critère. Sur les marchés BTC 5 min, un gros achat (500 $ ou plus) gagne presque exactement aussi souvent que son prix le laisse prévoir. Le gros acheteur n'est ni un initié qu'il faudrait suivre, ni un pigeon qu'il faudrait contrer.

Résultats de la validation (01.10 → 08.10, 2 304 cycles), à 10 $ par achat, au prix que nous aurions payé :

| Règle | Achats | Gagnés | Taux | Prix moyen | ROI | P&L | IC 90 % | IC corrigé ×4 |
|---|---|---|---|---|---|---|---|---|
| G1 suivre ≥ 2 000 $, prix 0,30–0,95 | 107 | 69 | 64,5 % | 0,661 | −3,7 % | −40 $ | [−180 ; +101] $ | [−229 ; +154] $ |
| G2 contrer ≥ 2 000 $, prix 0,30–0,95 | 106 | 37 | 34,9 % | 0,338 | +23,9 % | +253 $ | [−183 ; +765] $ | [−310 ; +975] $ |
| G3 contrer ≥ 500 $, prix 0,65–0,95, 60–120 s restantes | 207 | 30 | 14,5 % | 0,141 | −9,7 % | −200 $ | [−815 ; +474] $ | [−1 010 ; +736] $ |
| G4 suivre ≥ 500 $, prix 0,95–0,99, 10–60 s restantes | 915 | 904 | 98,8 % | 0,980 | +0,3 % | +30 $ | [−32 ; +87] $ | [−57 ; +107] $ |

Tous les intervalles corrigés contiennent 0 : **aucun bénéfice démontré, aucun fantôme proposé.**

Deux points à retenir :

- **G2 (contrer les gros) a l'air bonne en validation (+23,9 %), mais c'est un mirage.** Le gain vient du fait que le gros achat fait baisser un instant le prix de l'autre côté, et qu'on l'achète pendant ce creux. Au prix pessimiste (le prix d'avant le gros achat), G2 perd : −7,4 % en exploration et −11,6 % en validation. Avec 37 gains sur 106 achats à environ 0,34, le résultat dépend de quelques billets gagnants.
- **G4 (suivre une baleine qui achète un favori à 0,95–0,99 en fin de cycle) est légèrement positive**, avec +0,6 % en exploration et +0,3 % en validation. L'intervalle contient 0 en validation, et le résultat tombe à 0 au prix pessimiste. Cela ne fait pas mieux que la règle B3 de H1084.

Aucun ordre n'a été passé. Aucun fichier du bot (bot95/src, bot95/rapide), aucun workflow et aucun fantôme n'a été modifié.

## Ce que disent les données (tableau descriptif)

**Où sont les gros achats ?** Sur 5 459 cycles d'exploration, on compte 18 140 gros achats de 500 $ ou plus, 2 065 de 2 000 $ ou plus et 73 de 5 000 $ ou plus. En validation (2 304 cycles) : 6 004, 415 et 26. Environ **2 gros achats sur 3 (68 % en exploration, 62 % en validation) se font à 0,95 ou plus**, c'est-à-dire sur un favori quasi sûr. Ce sont des baleines qui ramassent les derniers centimes d'un résultat presque acquis, pas des paris audacieux. Les achats de 5 000 $ ou plus sont presque toujours des rafales (plusieurs ordres en quelques secondes), rarement une seule transaction.

**Fréquence de gain moins prix payé par le gros**, en points (une valeur positive veut dire que suivre le gros aurait été bon). Le prix est celui payé par le gros acheteur. Les intervalles sont calculés en tirant des cycles au hasard (bootstrap par cycles).

| Taille | Temps restant | Expl. : n (cycles) | Expl. : prix du gros → fréquence | Expl. : écart (pts) [IC 90 %] | Valid. : n (cycles) | Valid. : prix → fréquence | Valid. : écart (pts) [IC 90 %] |
|---|---|---|---|---|---|---|---|
| ≥ 500 $ | 0–30 s | 1848 (999) | 0,974 → 0,976 | +0,1 [−0,6 ; +0,8] | 470 (310) | 0,968 → 0,981 | +1,3 [−0,1 ; +2,5] |
| ≥ 500 $ | 30–60 s | 4207 (2152) | 0,967 → 0,971 | +0,4 [−0,1 ; +0,9] | 1257 (815) | 0,959 → 0,967 | +0,8 [−0,0 ; +1,6] |
| ≥ 500 $ | 60–120 s | 6491 (3128) | 0,951 → 0,946 | −0,5 [−1,1 ; +0,1] | 2031 (1153) | 0,943 → 0,950 | +0,7 [−0,3 ; +1,6] |
| ≥ 500 $ | 120–200 s | 2897 (1766) | 0,843 → 0,839 | −0,5 [−1,9 ; +1,0] | 1088 (693) | 0,809 → 0,805 | −0,4 [−2,3 ; +1,6] |
| ≥ 500 $ | 200–300 s | 2697 (1775) | 0,601 → 0,590 | −1,1 [−2,9 ; +0,8] | 1158 (730) | 0,560 → 0,555 | −0,5 [−3,2 ; +2,2] |
| ≥ 2 000 $ | 0–30 s | 193 (178) | 0,985 → 0,990 | +0,4 [−0,9 ; +1,5] | 31 (24) | 0,984 → 1,000 | +1,6 [+1,3 ; +1,9] |
| ≥ 2 000 $ | 30–60 s | 424 (412) | 0,980 → 0,976 | −0,4 [−1,5 ; +0,7] | 54 (52) | 0,934 → 0,944 | +1,1 [−4,2 ; +6,5] |
| ≥ 2 000 $ | 60–120 s | 872 (839) | 0,975 → 0,963 | −1,1 [−2,2 ; −0,2] | 173 (164) | 0,954 → 0,954 | −0,0 [−1,9 ; +1,5] |
| ≥ 2 000 $ | 120–200 s | 417 (382) | 0,943 → 0,940 | −0,3 [−1,9 ; +1,2] | 89 (85) | 0,864 → 0,820 | −4,4 [−10,1 ; +0,9] |
| ≥ 2 000 $ | 200–300 s | 159 (137) | 0,647 → 0,585 | −6,2 [−13,2 ; +0,9] | 68 (61) | 0,643 → 0,662 | +1,9 [−8,9 ; +12,7] |
| ≥ 5 000 $ | 0–30 s | 6 (5) | 0,976 → 1,000 | +2,4 | 1 (1) | 0,937 → 1,000 | — |
| ≥ 5 000 $ | 30–60 s | 5 (4) | 0,952 → 1,000 | +4,8 | 0 | — | — |
| ≥ 5 000 $ | 60–120 s | 25 (25) | 0,948 → 0,800 | −14,8 [−27,2 ; −4,7] | 5 (5) | 0,883 → 0,600 | −28,3 |
| ≥ 5 000 $ | 120–200 s | 20 (19) | 0,919 → 1,000 | +8,1 | 10 (10) | 0,769 → 0,700 | −6,9 [−28,0 ; +12,0] |
| ≥ 5 000 $ | 200–300 s | 17 (17) | 0,771 → 0,647 | −12,3 [−29,3 ; +4,3] | 10 (10) | 0,711 → 0,600 | −11,1 [−34,8 ; +11,9] |

Les lignes « ≥ 2 000 $ » sont incluses dans « ≥ 500 $ ». Pour les achats de 5 000 $ ou plus, les échantillons sont minuscules : les intervalles ne veulent rien dire, et ils sont omis quand toutes les observations vont dans le même sens.

**Lecture.** Dans presque toutes les cases, l'écart reste dans ±1,5 point et l'intervalle contient 0. Aucune case ne va dans le même sens, avec un intervalle qui exclut 0, sur les deux périodes. Le seul signe qui se répète est celui des achats de 5 000 $ ou plus avec 60–120 s restantes, qui gagnent moins que leur prix (−15 et −28 points). Mais cela repose sur 25 puis 5 cas : c'est une piste, pas une preuve.

**Gros achat dans le sens de BTC ou contre lui** (BTC sur les 10 s d'avant, Binance, en écarts-types) :

| | Explo. : écart gros | Explo. : écart à notre prix | Valid. : écart gros | Valid. : écart à notre prix |
|---|---|---|---|---|
| ≥ 500 $ contre BTC (1 235 / 459) | −8,4 [−10,9 ; −5,7] | −2,1 [−4,4 ; +0,2] | −2,3 [−5,8 ; +1,1] | +0,9 [−2,4 ; +4,2] |
| ≥ 500 $ sans mouvement net (12 346 / 4 059) | +0,1 [−0,5 ; +0,6] | +0,2 [−0,3 ; +0,7] | −0,0 [−1,0 ; +0,9] | −0,4 [−1,4 ; +0,5] |
| ≥ 500 $ avec BTC (4 559 / 1 486) | +0,9 [+0,3 ; +1,6] | +0,3 [−0,2 ; +1,0] | +2,2 [+1,2 ; +3,0] | +1,3 [+0,5 ; +2,2] |

- **Le gros qui achète contre BTC paie trop cher** (−8 points en exploration). Mais quand nous arrivons 1 à 6 s plus tard, le prix a déjà corrigé (−2 points, intervalle qui touche 0), et ce signe ne se retrouve qu'à moitié en validation. Ce n'est pas exploitable.
- **Le gros qui achète dans le sens de BTC gagne un peu plus que son prix** : +0,9 puis +2,2 points. À notre prix, l'écart est de +0,3 point en exploration (intervalle qui contient 0) et de +1,3 point en validation (intervalle [+0,5 ; +2,2]). Cette condition n'a **pas** été figée comme règle, car elle était trop faible en exploration. Elle a été vue après la validation : c'est au mieux une piste, à pré-enregistrer sur des données neuves (≥ 09.10) si Pitch le souhaite.

**Le prix continue-t-il dans le sens du gros ?** Non. Entre juste avant le gros achat et notre entrée (1 à 6 s après), le prix a déjà bougé dans son sens : +0,8 à +1 point quand le prix du gros est ≥ 0,95, +2,4 à +7 points en dessous de 0,95. Ce mouvement est l'impact du gros lui-même. **Après notre entrée**, le prix ne prolonge pas ce mouvement :

- à 10 s, l'écart moyen va de −1,0 à +0,3 point selon la taille et la zone de prix ;
- à 30 s, il va de −2,4 à 0 point, sauf les 6 achats de 5 000 $ ou plus à ≥ 0,95 de la validation (+2,3 points).

Quand l'écart est mesurable, il va légèrement dans l'autre sens (par exemple ≥ 500 $ à ≥ 0,95 : −0,6 [−0,7 ; −0,4] point à 30 s en exploration, −0,4 [−0,7 ; −0,2] en validation). L'impact d'un gros achat se résorbe un peu, il ne s'amplifie pas. Prendre le train en marche coûte donc l'impact, sans rien rapporter ensuite.

## Méthode

**Données.** Transactions publiques Polymarket des marchés BTC 5 min Up/Down, du 12.09 au 08.10.2026 (27 jours). Les marchés qui commencent le 09.10 ou après sont écartés. On utilise aussi BTCUSDT Binance à la seconde.

**Découpage.** Exploration du 12.09 au 30.09 (5 459 cycles), validation du 01.10 au 08.10 (2 304 cycles). Les règles ont été figées et poussées (commit cd14ca8) **avant** le calcul de la validation, puis la validation a été lancée une seule fois.

**Qui est l'acheteur ?** Une transaction (même hash) contient une ligne par participant. La **première ligne est le preneur**, c'est-à-dire l'ordre qui traverse le carnet. Les suivantes sont les teneurs de marché servis. Vérification sur une journée :

- dans les transactions de 3 lignes ou plus, la taille de la première ligne est égale à la somme des autres dans plus de 99 % des cas ;
- les exceptions sont ambiguës, quand un seul teneur fait presque tout le volume.

Les paires « BUY Up + BUY Down » sont des créations de parts : le preneur achète un côté, le teneur l'autre. Les paires « SELL X + BUY X » sont des échanges directs. Pour les paires, on ne peut pas vérifier l'ordre des lignes par la taille, qui est la même : on suppose la même convention. On ne garde que **la première ligne de chaque transaction, quand c'est un achat**. Chaque achat agressif est ainsi compté une seule fois, sans compter aussi sa contrepartie.

**Gros achat.** On regroupe les achats preneur d'un même portefeuille sur la même issue quand ils sont à 3 s ou moins l'un de l'autre, sur une rafale de 5 s au plus. Le montant est la somme de prix × parts. L'événement a lieu à la seconde où le cumul franchit 500, 2 000 ou 5 000 $.

**Notre achat.** On achète l'issue choisie au prix médian des achats de cette issue entre te+1 et te+6 s : on réagit après avoir vu le gros achat.

- Frais : 0,07·p·(1−p).
- Le billet est gardé jusqu'au règlement.
- Un seul achat par cycle et par règle : le premier événement qui déclenche.
- 10 $ par achat.
- Intervalles par bootstrap sur les cycles (0 $ pour les cycles sans achat, 10 000 tirages). Correction Bonferroni pour 4 règles : percentiles 1,25 et 98,75.
- Le prix pessimiste est le plus haut entre notre prix et le prix de ce côté juste avant le gros achat.

**Comment les règles ont été choisies.** Environ 360 combinaisons ont été testées en exploration (taille, tranche de prix, temps restant, sens BTC, suivre ou contrer). G1 et G2 sont le test central (suivre ou contrer les 2 000 $ ou plus hors favori quasi sûr). G3 est la meilleure case de l'exploration, donc la plus exposée au hasard. G4 est la version « baleine » de Bot95.

## Limites

- **Exécution inconnue.** Notre prix est la médiane des transactions des 5 secondes suivantes, pas un vrai ordre. Après un gros achat, le carnet est déplacé : un vrai ordre aurait pu payer plus cher (voir le prix pessimiste) ou ne pas être servi.
- **Identification du preneur.** Elle repose sur l'ordre des lignes renvoyé par l'API, vérifié par les tailles mais pas sur la blockchain. Les ventes agressives (vendre Up, ce qui revient à parier sur Down) ne sont pas comptées comme de gros achats.
- **Échantillons.** Il y a peu d'événements de 5 000 $ ou plus (73 + 26) et peu d'événements de 2 000 $ ou plus hors zone 0,95 (environ 260 + 107 cycles). Les achats contrariants sont des billets bon marché, avec des résultats très dispersés.
- **Une seule fenêtre de validation**, de 8 jours. BTC est remplacé par Binance pour le mouvement des 10 dernières secondes.
- **La piste « gros achat dans le sens de BTC » a été vue après la validation.** Elle ne compte pas comme résultat.

Fichiers : etude/bot5min/grosses_transactions_h1085.py (règles figées, docstring), etude/bot5min/grosses_transactions_h1085_exploration.json, etude/bot5min/grosses_transactions_h1085_validation.json.
