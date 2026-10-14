# Bot95 — H1089 « ailleurs » : les marchés crypto 15 min et horaires de Polymarket

14.10.2026 — étude hors ligne, aucun ordre. Code : `etude/bot5min/autres_marches_h1089.py` (règles figées au commit 71519549, avant la lecture de la validation) et `autres_marches_h1089_pentes.py`. Téléchargement : `.github/workflows/histo_autres_marches.yml` (nouveau, lecture seule).

## Verdict

**Les marchés 15 min ne sont pas moins efficaces que le 5 min. Le marché horaire l'est un peu : son prix intègre moins bien la distance du BTC au prix d'ouverture. Une seule règle passe le critère : acheter le favori 0,90–0,98 dans les 6 dernières minutes du marché horaire. Le gain est très petit et fragile.**

- **BTC 15 min** : même calibration que le 5 min. En fin de fenêtre, le prix du marché prédit mieux que notre modèle Binance (Brier marché − modèle −0,012, IC 90 % [−0,018 ; −0,006]), comme en 5 min (−0,018). Aucune des deux règles 15 min ne passe la validation.
- **BTC horaire** : c'est le seul marché où le modèle Binance simple fait **aussi bien ou mieux que le prix** en fin de fenêtre (Brier +0,004, IC [−0,000 ; +0,009]). Ajouter le modèle au prix améliore nettement la prédiction (poids 0,71, IC [0,43 ; 1,20], contre 0,28 en 5 min et 0,16 en 15 min). Ce marché a ~3 fois moins de portefeuilles que le 5 min et se règle directement sur la bougie Binance.
- **R2 (horaire, favori 0,90–0,98, ≤ 10 % du temps restant)** : en validation, 48 achats, **48 gagnés**, ROI +10,4 %, **+50 $ pour 10 $ par achat sur 5 jours**. IC 90 % corrigé Bonferroni [+21 ; +100] $. Au prix pessimiste : +5,2 %, +25 $, IC corrigé [+17 ; +32]. La règle **passe le critère fixé d'avance**. Mais avec zéro perte, le bootstrap sous-estime le risque. Un test binomial ne la confirme pas : la borne basse à 98,75 % du taux de gain est de 91,3 %, alors qu'il faut environ 95 % pour couvrir le prix pessimiste et les frais. Sur exploration et validation ensemble : 130 achats, 128 gagnés.
- Le **biais favori-billet** existe dans les deux sens attendus : les favoris tardifs gagnent un peu plus souvent que leur prix ; les billets 0,02–0,20 achetés en fin de fenêtre perdent beaucoup (−32 % en 15 min, −42 % en horaire en exploration). Ce n'est pas nouveau : on voit la même chose en 5 min (H1084), et ce surplus disparaît en grande partie au prix réellement payé.

**Proposition à Pitch, rien n'est lancé :** un fantôme R2 horaire (10 $, aucun argent réel), à confirmer sur des jours neufs (14.10 et après, le 13.10 reste réservé). Ce ne serait pas une source de revenus : environ 10 achats par jour, ~61 $ échangés côté favori dans les 5 secondes qui suivent le signal (médiane), soit quelques dollars par jour au mieux.

## 1. Quels marchés existent (sonde du 10.10, 15 h ET)

| Marché | Slug | Règlement | Frais preneur | Médiane par marché, 29.09–11.10 |
|---|---|---|---|---|
| BTC 5 min | `btc-updown-5m-<début unix>` | TWAP Chainlink 60 s fin ≥ début | 0,07·p·(1−p) | 3 711–3 850 transactions, 35–38 k$ dans la fenêtre, 678–716 portefeuilles, 12 transactions dans les 30 dernières s |
| BTC 15 min | `btc-updown-15m-<début unix>` (pas 900 s) | idem (Chainlink) | 0,07·p·(1−p) | 2 340 transactions, 25 k$, 346 portefeuilles, ~60 transactions dans les 90 dernières s |
| BTC horaire | `bitcoin-up-or-down-<mois>-<jour>-<année>-<h>am\|pm-et` (heure de New York), ouvert ~48 h avant | **bougie 1 h Binance BTC/USDT**, clôture ≥ ouverture | 0,07·p·(1−p) | 2 056–2 229 transactions, 23–27 k$, 225–232 portefeuilles, 118–134 transactions dans les 6 dernières min |
| BTC 4 h | `btc-updown-4h-<début unix>` (fenêtres 12–16 h ET, etc.) | Chainlink | 0,07 | ~19 k$ par marché, 6 par jour : trop peu pour une étude, non téléchargé |
| ETH / SOL / XRP 15 min | `eth-updown-15m-…` etc. | Chainlink | 0,07 | 3,7 k$ / 1,9 k$ / 0,7 k$ par marché (sonde) : non téléchargés |
| ETH / SOL / XRP horaire | `ethereum-up-or-down-…-2026-…-et`, etc. | Binance 1 h | — | non téléchargés (pas de prix 1 s ETH/SOL dans nos données) |

Volume par jour (BTC) : 5 min ≈ 10,7 M$ (288 marchés), 15 min ≈ 2,4 M$ (96 marchés), horaire ≈ 0,6 M$ (24 marchés). Il y a donc moins de concurrence, mais aussi beaucoup moins d'argent à prendre. Données : 1 247 marchés 15 min et 311 marchés horaires (29.09 → 11.10), aucun coupé par la limite de téléchargement. Le prix du marché (au moins 2 achats en 6 s) est observable à 69–72 % des instants en 15 min et à 38–42 % en horaire (90 % en 5 min). Le sens Binance donne le bon gagnant dans 98 % des cas en 5 et 15 min (approximation de Chainlink), et dans 99,7 % des cas en horaire (règlement Binance).

## 2. Calibration (descriptif, toutes les données 29.09–11.10)

Les deux tableaux portent sur le même instant t. La **pente** se lit ainsi : une pente supérieure à 1 veut dire que les favoris sont un peu sous-payés (biais favori-billet). Le **poids du modèle** mesure ce que la distance au prix à battre, exprimée en σ (Φ(z), BTC Binance 1 s), ajoute au prix. Pour **Brier marché − modèle**, un chiffre négatif veut dire que le prix prédit mieux que notre modèle. IC 90 % par marchés.

**Début et milieu de fenêtre (≥ 15 % du temps restant)**

| | 5 min | 15 min | horaire |
|---|---|---|---|
| Marchés | 3 743 | 1 240 | 311 |
| Pente | 1,04 [1,00 ; 1,08] | 1,10 [1,03 ; 1,18] | 1,15 [1,00 ; 1,32] |
| Poids du modèle | 0,20 [0,14 ; 0,27] | 0,11 [−0,03 ; 0,26] | 0,30 [−0,08 ; 0,71] |
| Brier marché − modèle | −0,004 [−0,006 ; −0,003] | −0,003 [−0,005 ; −0,001] | −0,002 [−0,006 ; +0,002] |

**Fin de fenêtre (< 15 % du temps restant : 45 s / 2 min 15 / 9 min)**

| | 5 min | 15 min | horaire |
|---|---|---|---|
| Marchés | 3 472 | 1 159 | 278 |
| Pente | 1,19 [1,12 ; 1,25] | 1,15 [1,06 ; 1,25] | 1,21 [1,03 ; 1,52] |
| Poids du modèle | 0,28 [0,22 ; 0,34] | 0,16 [0,07 ; 0,25] | **0,71 [0,43 ; 1,20]** |
| Brier marché − modèle | −0,018 [−0,022 ; −0,014] | −0,012 [−0,018 ; −0,006] | **+0,004 [−0,000 ; +0,009]** |

Ce qu'on en retient :

- Le léger biais favori-billet (pente > 1) se retrouve **partout, 5 min compris**. Il n'est pas plus marqué sur les marchés longs.
- Ce qui distingue l'horaire, c'est le modèle Binance : en fin de fenêtre, le prix ne contient pas toute l'information de distance. Les signes sont les mêmes en exploration et en validation (poids 0,80 puis 0,57).
- Dans le détail (fichiers `autres_marches_h1089_*_validation.json`), les favoris 0,90–0,98 en fin de fenêtre gagnent 2 à 7 points de plus que leur prix de signal, sur les **trois** marchés. En 5 min, H1084 a montré que ce surplus disparaît au prix réellement payé, parce que les transactions arrivent quand le favori vacille.

## 3. Règles figées sur l'exploration (29.09–06.10), validation (07.10–11.10) lue une fois

Conventions : prix du signal = médiane des achats dans (t−6, t] ; prix payé = médiane des achats du côté acheté dans (t+1, t+6] ; frais 0,07·p·(1−p) ; un achat par marché et par règle ; 10 $ par achat ; tous les marchés comptent. Prix pessimiste = max(signal, payé). Une vingtaine de variantes ont été essayées en exploration avant de retenir ces 4 règles : le risque de sélection est réel.

| Règle | Période | Marchés | Achats | Gagnés | Prix payé | ROI | P&L 10 $ | IC 90 % | IC 90 % corrigé (4 règles) | ROI pessimiste |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 15 min : favori 0,55–0,90, ≥ 65 % du temps restant → favori | expl. | 768 | 744 | 485 | 0,598 | +6,0 % | +444 $ | [+96 ; +794] | [−16 ; +921] | +4,5 % |
| | **valid.** | 479 | 448 | 283 | 0,599 | +2,3 % | +103 $ | [−176 ; +376] | **[−278 ; +465]** | +0,9 % |
| R4 15 min : favori 0,60–0,92, modèle − prix ≥ 0,08 → favori | expl. | 768 | 629 | 478 | 0,727 | +3,1 % | +193 $ | [−51 ; +430] | [−144 ; +515] | +2,5 % |
| | **valid.** | 479 | 407 | 292 | 0,731 | −4,0 % | −162 $ | [−363 ; +45] | **[−438 ; +115]** | −4,5 % |
| R2 horaire : favori 0,90–0,98, ≤ 10 % du temps restant → favori | expl. | 192 | 82 | 80 | 0,947 | +2,7 % | +22 $ | [−5 ; +44] | [−17 ; +48] | +2,1 % |
| | **valid.** | 119 | 48 | **48** | 0,924 | +10,4 % | +50 $ | [+25 ; +83] | **[+21 ; +100]** | +5,2 % (+25 $, IC corr. [+17 ; +32]) |
| R3 horaire : \|modèle − prix\| ≥ 0,15 → côté du modèle | expl. | 192 | 53 | 38 | 0,637 | +14,0 % | +74 $ | [−20 ; +166] | [−54 ; +198] | +13,5 % |
| | **valid.** | 119 | 31 | 23 | 0,683 | +7,8 % | +24 $ | [−39 ; +85] | **[−63 ; +106]** | +7,6 % |

- **R1** (favoris du début de fenêtre en 15 min) : positif en validation mais beaucoup plus faible, et l'IC contient 0. Pas démontré. La même règle perdait −10,5 % sur l'horaire en exploration, ce qui suggère surtout un effet de la tendance de la période.
- **R4** (le modèle juge le favori 15 min sous-payé) : négatif en validation. Abandon.
- **R3** (horaire, côté que préfère le modèle) : va dans le sens de la section 2, mais seulement 31 achats ; l'IC contient largement 0. Pas démontré.
- **R2** (horaire, favoris tardifs) : passe le critère formel (ROI > 0 dans les deux périodes, borne basse corrigée > 0, au prix observé comme au prix pessimiste). Points faibles :
  - Zéro perte en validation, donc un IC bootstrap trop étroit. En test binomial, 48/48 donne une borne basse (98,75 %) de 91,3 % de gains, sous le seuil de rentabilité d'environ 92,9 % (prix payé) ou 95,1 % (prix pessimiste). Sur les deux périodes réunies (128 gagnés sur 130), la borne basse est d'environ 93,8 %, toujours sous le seuil pessimiste.
  - En validation, le prix payé (0,924) est inférieur au prix du signal (0,939). Le gain vient en partie de cette glissade favorable, qu'un vrai ordre n'obtiendrait pas forcément. Au prix pessimiste, le ROI tombe à +5,2 %.
  - La taille est minuscule : ~61 $ achetés côté favori dans les 5 s après le signal (médiane), ~10 occasions par jour. Même parfaitement réel, cela ferait quelques dollars par jour.
  - La règle ressemble à B3 (H1084, favoris tardifs en 5 min), qui passait aussi en validation puis n'a pas été confirmée sur des jours neufs (H1087).

## 4. Proposition (à décider par Pitch, rien n'est lancé)

Seule R2 a un IC corrigé > 0. Je propose, si Pitch le souhaite, un **fantôme R2 horaire** sans argent réel, avec la règle exacte figée ici : favori 0,90–0,98 avec ≤ 6 min restantes, premier signal du marché, 10 $. Le but est de compter les achats réellement servis et les pertes sur au moins 2 semaines (~140 marchés) avant toute conclusion. L'autre possibilité est une confirmation hors ligne sur les jours 14.10 et suivants, avec le même workflow (`type=btc-1h`), dès que le BTC 1 s de ces jours sera disponible.

## Limites

- 13 jours seulement : 311 marchés horaires au total, 119 en validation. Une seule semaine de marché (tendance, volatilité) peut tout expliquer.
- Le prix Binance 1 s approxime Chainlink pour les marchés 5 et 15 min (bon gagnant 98 %). Pour l'horaire, Binance est la vraie source de règlement, mais l'ouverture est approchée par la clôture de la seconde précédente (bon gagnant 99,7 %).
- Le prix « observé » est la médiane des achats publics, pas le carnet d'ordres : le prix exécutable réel peut être moins bon. Le piège de sélection (une transaction n'existe que si quelqu'un vend) s'applique ici aussi.
- Le BTC 1 s s'arrête au 11.10 : le 12.10 n'a pas été téléchargé, le 13.10 (réservé) n'a pas été touché.
- ETH / SOL / XRP (15 min et horaire) et BTC 4 h existent, mais n'ont pas été étudiés (volumes faibles, pas de prix 1 s).
- Une vingtaine de variantes ont été regardées en exploration, puis 4 règles retenues. La correction Bonferroni ne porte que sur ces 4 règles.
