# BOT95 — GRAND AUDIT TEMPOREL (hypothèses H186-H280)

Étude hors ligne du 11.10.2026 — aucun bot, aucun workflow modifié, rien publié. 1146 cycles BTC réglés (07.10 08:00 → 11.10 07:55, heure suisse) : apprentissage 455 (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test 258 (→ 11.10 07:55). Lignes enregistrées jusqu'au 11.10 07:50:59. Le test a déjà été regardé par d'autres études pour la période 10.10 10:25-13:45 : il est **exploratoire**.

## Verdict (en tête)

- **La « série de ~27 pertes »** : aucune suite ininterrompue de 27 pertes dans `V2-F_ecart_qui_grandit_BTC.json`. Ce qui s'en approche : **27 pertes en 29 trades** (09.10 12:08:31 → 09.10 15:02:43, −711 $, période de validation, AVANT la bascule du prix d'exercice) ; la plus longue suite ininterrompue = 18 pertes (11.10 07:45:44 → 11.10 09:11:52), dont 2 seulement couvertes par les lignes enregistrées (fin le 11.10 07:50:59).
- **Dans l'épisode des 27 pertes, le temps n'explique presque rien** : pour 16 des 27 perdants, la politique de fraîcheur change notre probabilité de moins de 0,02 ; le K faux (prix du site, |erreur| jusqu'à 49 $) baisse notre probabilité de −0,03 en médiane chez les perdants, mais aussi de −0,05 chez les gagnants (sur tous les trades d'avant la bascule : −0,03 contre −0,04) → le K faux a fabriqué des signaux, sans distinguer perdants et gagnants.
- **Politique de fraîcheur complète (F8) contre le jumeau du bot (R8)**, règle V2-F, exécution 0,3 s, Δ vs GARDER : app. −334 $ [−2 081 $ ; +1 483 $] ; valid. −790 $ [−2 402 $ ; +848 $] ; test −437 $ [−1 745 $ ; +766 $] → **résultat négatif (aucun gain démontré)**. Composantes : σ « secondes changées » app. −603 $ [−2 168 $ ; +960 $] ; valid. −859 $ [−2 265 $ ; +506 $] ; test −961 $ [−1 588 $ ; −423 $] → **résultat négatif (IC entièrement négatif sur une période)** (elle gonfle σ d'un facteur ≈ 2 par marché calme) ; σ sans cache app. −4 $ [−70 $ ; +62 $] ; valid. +64 $ [−11 $ ; +167 $] ; test −53 $ [−159 $ ; +0 $] ; écarts recalculés chaque seconde app. +262 $ [−571 $ ; +1 233 $] ; valid. +28 $ [−196 $ ; +249 $] ; test −40 $ [−146 $ ; +61 $] ; exclusion des sources > 1 s (indicateur) app. −117 $ [−861 $ ; +644 $] ; valid. −540 $ [−1 695 $ ; +449 $] ; test −152 $ [−1 092 $ ; +721 $]. Variante « 60 rendements changés exigés » : app. −310 $ [−1 979 $ ; +1 587 $] ; valid. −456 $ [−2 124 $ ; +1 306 $] ; test +1 543 $ [+258 $ ; +2 780 $] — le gain du test vient de ne plus trader quand le marché est calme, pas de la fraîcheur, et la validation est négative → **résultat négatif**.
- **L'âge « indicateur » des lignes 0,3 s ne mesure pas la fraîcheur** : Bybit médiane 1,88 s contre 0,30 s d'âge vrai, corrélation 0,39 (un marché calme ressemble à un flux coupé). Tout ce qui repose sur cet indicateur (exclusion, rattrapage, Frankenstein) est au mieux une **hypothèse**, jamais une preuve.
- **Âges VRAIS (vitesse.json, 239 trades V2-F réels depuis le 10.10 14:17)** : Bybit > 1 s chez 27 % des perdants contre 15 % des gagnants ; la règle « Bybit ET OKX > 1 s → pas de décision » aurait sauté 14 trades (11 perdants, 3 gagnants, +208 $ contre GARDER) → **hypothèse prometteuse, données insuffisantes** (14 trades). Sur les décisions réelles « desaccord 30 », c'est l'inverse (Bybit ou OKX > 1 s : 37 % des perdants contre 51 % des gagnants).
- **Prix d'exercice** : jusqu'au 09.10 19:20 le bot utilisait le prix instantané du site (|erreur| médiane 10,45 $, 90 % 33,09 $) ; depuis, la moyenne Chainlink 60 s (0,10 $) → **correction technique prouvée, déjà en place**. Il reste 41 cycles sur 438 à plus de 2 $ après la bascule (dont 9 avec < 40 secondes Chainlink reçues) : **hypothèse prometteuse** (hypothèse 5) à suivre. Rejeu « R8 + K 60 s » : app. +232 $ [−2 402 $ ; +2 758 $] ; valid. +234 $ [−1 320 $ ; +1 788 $] ; test +73 $ [−244 $ ; +410 $].
- **Fuite de données dans les études précédentes** : `meta_router.parts_r` (X8/X1/H1, cohorte B du Hedge Lab) lit la seconde courante en FIN de seconde (jusqu'à 0,999 s de futur) → **correction technique prouvée** ; impact faible (9 et 10 cycles changent). Ce fichier : pas de fuite, deux passes identiques.
- **Rattrapage de flux (D)** : les signaux V2-F dont la croissance de 3 s contient un saut « rattrapage » perdent dans les trois périodes (app. −50 $, valid. −174 $, test −614 $) → **hypothèse prometteuse** (petits effectifs, indicateur d'âge). Rejet par le marché (H) : signes opposés entre apprentissage et validation → **résultat négatif**. Conservation (I) : carnets Up/Down parfaitement miroirs, P(Down) = 1 − P(Up) par construction → rien à corriger.
- **Conclusion chiffrée** : parmi les faux désaccords ≥ 0,30 du rejeu, 58 % portent un drapeau temporel, mais 69 % des gagnants aussi : **part attribuable démontrée ≈ 0 %** ; borne haute avec les âges vrais (excès de « Bybit > 1 s » chez les perdants V2-F) ≈ **13 %**. **Au moins 87 % des fausses alertes restent inexpliquées** par les défauts temporels mesurables à 0,3 s : le problème principal est ailleurs (modèle / sélection des signaux).

## 0. Fidélité du jumeau du bot (R8) et de l'indicateur d'âge

- R8 (reconstruction à la date du code probaV1) contre la probabilité enregistrée O8 sur 750785 lignes : corrélation 0,996, écart absolu médian 0,002, 90 % 0,022, 99 % 0,050. Le jumeau n'est donc PAS identique au bot (caches de phase inconnue, indicateur de réception, prixA reconstruit) : toute comparaison de politique se fait R8 contre F8 (même code, une seule chose change).

| Rejeu | Trades réels (cycles réglés couverts) | Signaux du rejeu (même période) | Cycles communs | Même côté | Même côté à 1 s près |
|---|---|---|---|---|---|
| O8 | 597 | 593 | 584 | 575 | 449 |
| R8 | 597 | 595 | 581 | 566 | 343 |
| F8 | 597 | 593 | 578 | 554 | 215 |

Âge INDICATEUR (temps depuis le dernier changement de valeur dans les lignes) contre âge VRAI (vitesse.json, temps depuis le dernier message) aux mêmes décisions :

| Source | Décisions | Âge vrai médian | Indicateur médian | Corrélation | Vrai > 1 s | Indicateur > 1 s | Accord sur « > 1 s » |
|---|---|---|---|---|---|---|---|
| bybit | 1047 | 0,30 s | 1,88 s | 0,39 | 30 % | 62 % | 66 % |
| okx | 1047 | 0,21 s | 1,29 s | 0,22 | 15 % | 57 % | 55 % |
| chainlink | 1047 | 0,53 s | 0,58 s | 0,83 | 16 % | 20 % | 87 % |
| binance | 1047 | 0,21 s | 0,74 s | 0,25 | 13 % | 42 % | 70 % |
| coinbase | 1047 | 0,14 s | 0,90 s | 0,18 | 6 % | 48 % | 57 % |

Binance et Coinbase ne sont PAS utilisés par probaV1 (seulement Bybit, OKX, Chainlink) : leur fraîcheur ne peut pas changer la probabilité du bot.

## A. La série noire V2-F et ses groupes de contrôle

Fichier `bot95/sauvegarde/V2-F_ecart_qui_grandit_BTC.json` : 631 trades réels (09.10 01:58:25 → 11.10 10:43:17), 495 perdus. Âges vrais (vitesse.json) disponibles pour 239 trades (depuis le 10.10 14:17). Colonnes : âges Bybit / OKX / Chainlink en s ; probabilités pour NOTRE côté ; « prix » = prix réel payé / meilleur vendeur de la ligne enregistrée ≤ décision.

### Série noire : 18 pertes de suite

| Décision | Côté | Net $ | Erreur K $ | Âges vrais | Âges indicateurs | Proba réelle (proba0) | O8 ligne | R8 à la date | F8 fraîcheur | Prix réel / ligne | Raison de la divergence (fraîcheur) | R8 avec K 60 s (écart au prix payé) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11.10 07:45:44 | Up | −45 | 0,0 | 1,2 / 0,0 / 6,3 | 0,9 / 18,0 / 5,7 | 0,50 | 0,50 | 0,49 | 0,49 | 0,29 / 0,30 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,49 (écart 0,20) |
| 11.10 07:50:23 | Up | −53 | 0,0 | 0,1 / 0,0 / 0,1 | 0,0 / 12,9 / 0,0 | 0,48 | 0,48 | 0,48 | 0,48 | 0,29 / 0,28 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,48 (écart 0,18) |
| 11.10 07:55:55 | Up | −49 | — | 2,3 / 0,0 / 1,2 | — | 0,47 | — | — | — | 0,28 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:00:30 | Down | −55 | — | 4,1 / 0,3 / 0,6 | — | 0,46 | — | — | — | 0,27 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:05:16 | Up | −53 | — | 1,2 / 0,8 / 0,1 | — | 0,42 | — | — | — | 0,23 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:12:54 | Up | −38 | — | 1,0 / 0,3 / 1,0 | — | 0,50 | — | — | — | 0,32 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:15:48 | Up | −53 | — | 0,1 / 0,0 / 0,9 | — | 0,50 | — | — | — | 0,32 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:21:56 | Up | −53 | — | 0,0 / 0,7 / 0,2 | — | 0,50 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:26:09 | Down | −54 | — | 1,7 / 0,6 / 0,1 | — | 0,50 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:30:21 | Down | −54 | — | 2,8 / 0,3 / 1,1 | — | 0,51 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:36:54 | Down | −54 | — | 0,8 / 0,1 / 0,2 | — | 0,50 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:40:30 | Down | −54 | — | 0,6 / 1,4 / 0,3 | — | 0,49 | — | — | — | 0,30 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:45:21 | Down | −54 | — | 0,1 / 0,1 / 0,6 | — | 0,49 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:50:23 | Up | −24 | — | 4,2 / 1,9 / 0,6 | — | 0,41 | — | — | — | 0,22 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 08:55:33 | Down | −2 | — | 0,0 / 0,0 / 0,3 | — | 0,38 | — | — | — | 0,18 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 09:02:02 | Down | −19 | — | 0,2 / 0,0 / 0,5 | — | 0,50 | — | — | — | 0,30 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 09:05:21 | Up | −53 | — | 0,0 / 0,1 / 0,2 | — | 0,46 | — | — | — | 0,10 / — | pas de ligne enregistrée (après 11.10 07:51) | — |
| 11.10 09:11:52 | Up | −54 | — | 4,6 / 0,5 / 0,1 | — | 0,49 | — | — | — | 0,31 / — | pas de ligne enregistrée (après 11.10 07:51) | — |

### Épisode élargi : 27 pertes en 29 trades

| Décision | Côté | Net $ | Erreur K $ | Âges vrais | Âges indicateurs | Proba réelle (proba0) | O8 ligne | R8 à la date | F8 fraîcheur | Prix réel / ligne | Raison de la divergence (fraîcheur) | R8 avec K 60 s (écart au prix payé) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09.10 12:08:31 | Up | −3 | 4,8 | — | 0,0 / 0,0 / 0,6 | 0,40 | 0,40 | 0,41 | 0,42 | 0,18 / 0,26 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,44 (écart 0,26) |
| 09.10 12:10:18 | Down | −9 | 22,1 | — | 0,0 / 0,0 / 0,9 | 0,57 | 0,56 | 0,56 | 0,55 | 0,33 / 0,31 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,45 (écart 0,11) |
| 09.10 12:17:50 | Up | −57 | 18,7 | — | 1,2 / 2,7 / 0,0 | 0,32 | 0,32 | 0,32 | pas de décision | 0,14 / 0,13 | politique : Bybit et OKX > 1 s (indicateur) → pas de décision | 0,42 (écart 0,29) |
| 09.10 12:21:22 | Up | −15 | −6,2 | — | 2,4 / 2,4 / 0,9 | 0,45 | 0,44 | 0,44 | pas de décision | 0,25 / 0,28 | politique : Bybit et OKX > 1 s (indicateur) → pas de décision | 0,41 (écart 0,15) |
| 09.10 12:26:18 | Down | −53 | 0,5 | — | 1,2 / 1,8 / 0,0 | 0,39 | 0,39 | 0,37 | pas de décision | 0,18 / 0,17 | politique : Bybit et OKX > 1 s (indicateur) → pas de décision | 0,37 (écart 0,19) |
| 09.10 12:32:18 | Up | −54 | −1,4 | — | 0,0 / 4,8 / 0,0 | 0,42 | 0,42 | 0,43 | 0,44 | 0,23 / 0,21 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,42 (écart 0,19) |
| 09.10 12:35:18 | Up | −54 | −45,2 | — | 0,3 / 0,0 / 0,0 | 0,53 | 0,53 | 0,53 | 0,52 | 0,26 / 0,24 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,33 (écart 0,07) |
| 09.10 12:42:47 | Up | −4 | −0,1 | — | 0,0 / 0,3 / 0,6 | 0,30 | 0,30 | 0,29 | 0,31 | 0,11 / 0,12 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,29 (écart 0,19) |
| 09.10 12:52:53 | Up | −8 | −33,0 | — | 0,9 / 0,0 / 0,0 | 0,53 | 0,53 | 0,55 | 0,55 | 0,25 / 0,29 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,37 (écart 0,12) |
| 09.10 13:02:40 | Up | −53 | −9,3 | — | 0,0 / 1,5 / 0,6 | 0,39 | 0,37 | 0,37 | 0,39 | 0,20 / 0,20 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,32 (écart 0,12) |
| 09.10 13:06:48 | Down | −53 | 5,1 | — | 1,5 / 0,3 / 0,0 | 0,39 | 0,40 | 0,40 | 0,42 | 0,20 / 0,24 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,37 (écart 0,17) |
| 09.10 13:10:03 | Up | −53 | −33,2 | — | 2,1 / 0,6 / 0,0 | 0,53 | 0,50 | 0,55 | 0,54 | 0,33 / 0,32 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,40 (écart 0,06) |
| 09.10 13:16:12 | Down | −32 | 9,4 | — | 0,0 / 0,0 / 0,6 | 0,48 | 0,49 | 0,49 | 0,49 | 0,30 / 0,44 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,44 (écart 0,14) |
| 09.10 13:23:17 | Up | −37 | 10,5 | — | 1,8 / 0,6 / 1,5 | 0,30 | 0,30 | 0,29 | 0,33 | 0,11 / 0,10 | σ (secondes changées) (0,04) | 0,34 (écart 0,23) |
| 09.10 13:28:11 | Down | −11 | 13,1 | — | 9,0 / 0,0 / 0,3 | 0,52 | 0,58 | 0,58 | 0,57 | 0,32 / 0,44 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,51 (écart 0,19) |
| 09.10 13:35:52 | Up | 109 | 19,6 | — | 0,0 / 0,0 / 0,0 | 0,63 | 0,63 | 0,63 | 0,60 | 0,33 / 0,31 | σ (secondes changées) (−0,03) | 0,67 (écart 0,35) |
| 09.10 13:43:36 | Down | 36 | 27,6 | — | 0,6 / 0,9 / 0,0 | 0,61 | 0,61 | 0,57 | 0,56 | 0,40 / 0,44 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,43 (écart 0,03) |
| 09.10 13:53:33 | Up | −8 | −32,2 | — | 0,0 / 0,0 / 0,0 | 0,29 | 0,28 | 0,29 | 0,33 | 0,04 / 0,02 | σ (secondes changées) (0,04) | 0,17 (écart 0,13) |
| 09.10 13:58:38 | Up | −24 | 5,5 | — | 0,3 / 0,6 / 0,6 | 0,32 | 0,32 | 0,31 | 0,32 | 0,12 / 0,13 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,34 (écart 0,21) |
| 09.10 14:01:30 | Down | −44 | 20,3 | — | 0,0 / 0,0 / 0,9 | 0,48 | 0,48 | 0,45 | 0,46 | 0,30 / 0,31 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,36 (écart 0,06) |
| 09.10 14:10:41 | Up | −9 | −48,7 | — | 0,0 / 1,2 / 1,2 | 0,67 | 0,67 | 0,65 | 0,57 | 0,47 / 0,51 | σ (secondes changées) (−0,09) | 0,67 (écart 0,20) |
| 09.10 14:17:30 | Up | −54 | −11,7 | — | 0,0 / 0,9 / 0,6 | 0,40 | 0,34 | 0,37 | 0,39 | 0,21 / 0,19 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,32 (écart 0,11) |
| 09.10 14:27:31 | Up | −1 | −16,5 | — | 0,0 / 0,0 / 0,3 | 0,35 | 0,45 | 0,38 | 0,42 | 0,15 / 0,29 | σ (secondes changées) (0,03) | 0,31 (écart 0,16) |
| 09.10 14:36:21 | Up | −53 | −31,5 | — | 0,6 / 1,2 / 0,3 | 0,47 | 0,45 | 0,42 | pas de décision | 0,28 / 0,27 | σ fraîche incalculable (< 20 secondes changées sur 300 s) → pas de décision | 0,59 (écart 0,31) |
| 09.10 14:40:43 | Up | −53 | −13,7 | — | 0,0 / 0,0 / 0,3 | 0,39 | 0,33 | 0,33 | 0,36 | 0,20 / 0,19 | σ (secondes changées) (0,04) | 0,27 (écart 0,07) |
| 09.10 14:48:17 | Down | −12 | 3,3 | — | 0,6 / 0,6 / 1,5 | 0,23 | 0,23 | 0,22 | 0,23 | 0,04 / 0,03 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,20 (écart 0,17) |
| 09.10 14:51:48 | Up | −53 | −4,8 | — | 0,0 / 0,0 / 0,0 | 0,32 | 0,27 | 0,27 | 0,31 | 0,12 / 0,12 | σ (secondes changées) (0,04) | 0,25 (écart 0,14) |
| 09.10 14:58:22 | Down | −44 | −8,5 | — | 4,5 / 0,0 / 0,6 | 0,30 | 0,31 | 0,31 | 0,32 | 0,11 / 0,14 | pas de divergence temporelle (|F8 − R8| < 0,02) | 0,35 (écart 0,24) |
| 09.10 15:02:43 | Down | −3 | 9,8 | — | 0,6 / 0,3 / 0,3 | 0,30 | 0,23 | 0,23 | 0,25 | 0,10 / 0,08 | σ (secondes changées) (0,02) | 0,19 (écart 0,09) |

**Prix d'exercice dans l'épisode** (avant la bascule du 09.10 19:20) : avec le K « moyenne 60 s » (calculable à la date), notre probabilité (notre côté) change en médiane de −0,03 pour les 27 perdants de l'épisode (baisse ≥ 0,05 : 33 %) et de −0,05 pour ses 2 gagnants ; sur tous les trades réels avant la bascule : −0,03 pour 127 perdants (baisse ≥ 0,05 : 38 %) contre −0,04 pour 39 gagnants (baisse ≥ 0,05 : 49 %). (Le jumeau garde son propre instant : le trade réel aurait pu se déclencher plus tard avec un autre K — voir la ligne « R8+K 60 s » de B pour l'effet sur la règle complète.)


### Âges VRAIS au moment de la décision (vitesse.json) : série contre contrôles

| Groupe | Trades | Âge médian Bybit / OKX / Chainlink (s) | 90 % Bybit / OKX | Bybit > 1 s | Bybit ET OKX > 1 s (politique : pas de décision) | Écart d'âge Bybit−OKX > 1 s |
|---|---|---|---|---|---|---|
| série de 18 pertes (11.10) | 18 | 0,90 / 0,20 / 0,39 | 4,13 / 0,98 | 44 % | 6 % | 39 % |
| autres perdants | 166 | 0,23 / 0,18 / 0,49 | 3,02 / 1,13 | 25 % | 6 % | 28 % |
| gagnants | 55 | 0,17 / 0,23 / 0,53 | 1,67 / 1,13 | 15 % | 5 % | 15 % |

Politique appliquée aux âges VRAIS (seule partie de F8 calculable sans prix) : 14 trades réels auraient été sautés (Bybit et OKX > 1 s) : 11 perdants, 3 gagnants, résultat réel de ces trades −208 $ (les sauter = +208 $ contre GARDER).

### Groupes de contrôle sur tous les trades réels couverts par les lignes

| Groupe | Trades | Résultat réel | Prix rapide Bybit > 1 s (ind.) | Bybit et OKX > 1 s (ind.) | F8 sans décision | médiane F8 − R8 (notre côté) | médiane |F8 − R8| | F8 : écart < 0,20 | médiane |R8 − O8| | σ fraîche / σ bot (médiane) |
|---|---|---|---|---|---|---|---|---|---|---|
| série (27 pertes, si couverte) | 27 | −856 $ | 30 % | 11 % | 4 | 0,009 | 0,015 | 15 | 0,007 | 1,67 |
| tous les perdants | 463 | −17 772 $ | 44 % | 23 % | 111 | 0,008 | 0,008 | 233 | 0,001 | 2,16 |
| tous les gagnants | 127 | +14 771 $ | 44 % | 23 % | 30 | 0,004 | 0,006 | 71 | 0,002 | 2,16 |
| perdants 11.10 | 66 | −2 683 $ | 55 % | 29 % | 20 | 0,002 | 0,002 | 33 | 0,000 | 2,49 |
| gagnants 11.10 | 22 | +1 835 $ | 50 % | 36 % | 8 | 0,002 | 0,005 | 11 | 0,001 | 2,65 |

Lecture : σ fraîche / σ bot > 1 = la politique « secondes changées seulement » GONFLE σ (elle retire les rendements nuls, y compris les vrais) → probabilités moins extrêmes. Remarque de méthode : une variance réalisée par unité de temps n'est PAS biaisée par le remplissage tant que le rattrapage (le saut à la reprise du flux) est dans la fenêtre ; le biais du remplissage n'existe que pendant une coupure EN COURS au moment de la décision.

## B. Politique de fraîcheur : décisions changées et P&L contre GARDER (règle V2-F, tous les cycles)

Référence = jumeau R8 (règle actuelle, position gardée jusqu'au règlement). Chaque ligne change UNE composante (ou toutes : F8). Exécution 0,3 s (meilleur vendeur, ≤ prix de décision, 50 $). « Sautés » = trades de R8 que la variante ne prend plus ; perdants / gagnants évalués à l'exécution 0,3 s.

| Variante | Période | Signaux R8 | Signaux variante | Perdants sautés | Gagnants sautés | Résultat des sautés (R8) | Côté inversé | Instant déplacé > 0,5 s | Cycles nouveaux | R8 | Variante | Δ vs GARDER (0,3 s) [IC 90 % blocs 1 h] | Δ délai 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R8+σ sans cache | apprentissage | 356 | 356 | 0 | 0 | +0 $ | 0 | 6 | 0 | +1 089 $ | +1 084 $ | **−4 $** [−70 $ ; +62 $] | +165 $ |
| R8+σ sans cache | validation | 380 | 380 | 0 | 0 | +0 $ | 0 | 5 | 0 | −652 $ | −588 $ | **+64 $** [−11 $ ; +167 $] | +51 $ |
| R8+σ sans cache | test | 258 | 258 | 0 | 0 | +0 $ | 0 | 1 | 0 | −1 850 $ | −1 903 $ | **−53 $** [−159 $ ; +0 $] | −28 $ |
| R8+σ | apprentissage | 356 | 381 | 0 | 0 | +0 $ | 9 | 158 | 26 | +1 089 $ | +486 $ | **−603 $** [−2 168 $ ; +960 $] | −886 $ |
| R8+σ | validation | 380 | 391 | 1 | 2 | −3 $ | 6 | 146 | 14 | −652 $ | −1 511 $ | **−859 $** [−2 265 $ ; +506 $] | −400 $ |
| R8+σ | test | 258 | 258 | 0 | 0 | +0 $ | 4 | 45 | 0 | −1 850 $ | −2 811 $ | **−961 $** [−1 588 $ ; −423 $] | −1 521 $ |
| R8+écarts | apprentissage | 356 | 358 | 0 | 0 | +0 $ | 0 | 15 | 2 | +1 089 $ | +1 351 $ | **+262 $** [−571 $ ; +1 233 $] | +207 $ |
| R8+écarts | validation | 380 | 383 | 0 | 0 | +0 $ | 0 | 26 | 3 | −652 $ | −624 $ | **+28 $** [−196 $ ; +249 $] | +11 $ |
| R8+écarts | test | 258 | 258 | 0 | 0 | +0 $ | 0 | 8 | 0 | −1 850 $ | −1 890 $ | **−40 $** [−146 $ ; +61 $] | −188 $ |
| R8+exclusion | apprentissage | 356 | 349 | 6 | 0 | −198 $ | 5 | 72 | 0 | +1 089 $ | +971 $ | **−117 $** [−861 $ ; +644 $] | −747 $ |
| R8+exclusion | validation | 380 | 377 | 2 | 0 | −65 $ | 0 | 105 | 0 | −652 $ | −1 192 $ | **−540 $** [−1 695 $ ; +449 $] | −396 $ |
| R8+exclusion | test | 258 | 255 | 2 | 0 | −70 $ | 8 | 116 | 0 | −1 850 $ | −2 002 $ | **−152 $** [−1 092 $ ; +721 $] | −1 095 $ |
| F8 | apprentissage | 356 | 375 | 3 | 0 | −107 $ | 11 | 187 | 24 | +1 089 $ | +755 $ | **−334 $** [−2 081 $ ; +1 483 $] | −314 $ |
| F8 | validation | 380 | 385 | 3 | 2 | −68 $ | 7 | 210 | 11 | −652 $ | −1 442 $ | **−790 $** [−2 402 $ ; +848 $] | −305 $ |
| F8 | test | 258 | 255 | 2 | 1 | −51 $ | 7 | 135 | 0 | −1 850 $ | −2 287 $ | **−437 $** [−1 745 $ ; +766 $] | −1 729 $ |
| F8 (σ : 60 rendements changés exigés) | apprentissage | 356 | 370 | 6 | 0 | −248 $ | 11 | 185 | 24 | +1 089 $ | +778 $ | **−310 $** [−1 979 $ ; +1 587 $] | −243 $ |
| F8 (σ : 60 rendements changés exigés) | validation | 380 | 316 | 49 | 13 | −752 $ | 7 | 172 | 11 | −652 $ | −1 108 $ | **−456 $** [−2 124 $ ; +1 306 $] | +23 $ |
| F8 (σ : 60 rendements changés exigés) | test | 258 | 112 | 83 | 22 | −1 293 $ | 7 | 63 | 0 | −1 850 $ | −308 $ | **+1 543 $** [+258 $ ; +2 780 $] | +341 $ |
| R8+K 60 s | apprentissage | 356 | 315 | 27 | 3 | −727 $ | 45 | 162 | 14 | +1 089 $ | +1 321 $ | **+232 $** [−2 402 $ ; +2 758 $] | +813 $ |
| R8+K 60 s | validation | 380 | 361 | 15 | 1 | −583 $ | 27 | 137 | 4 | −652 $ | −418 $ | **+234 $** [−1 320 $ ; +1 788 $] | +371 $ |
| R8+K 60 s | test | 258 | 258 | 0 | 0 | +0 $ | 2 | 13 | 0 | −1 850 $ | −1 777 $ | **+73 $** [−244 $ ; +410 $] | −244 $ |

Pour mémoire, la règle sur la probabilité ENREGISTRÉE (O8, jumeau A « tel que vu par le bot ») : apprentissage 223 achats +869 $ ; validation 298 achats −1 599 $ ; test 196 achats −2 384 $.

## C. Test de gel des sources (une source retardée à la fois, jumeau R8)

La source est lue à t − délai (valeur ET heure de réception), les autres à t. **+100 ms est approximatif** : les lignes sont espacées de 0,3 s, donc t − 0,1 s tombe sur la ligne précédente dans environ 1 cas sur 3 seulement. Binance et Coinbase n'entrent pas dans probaV1 : effet nul par construction (non testés). Fragilité = (signaux perdus + inversés + déplacés > 0,5 s + nouveaux) / signaux R8.

| Source | Délai | |ΔP| médian (toutes lignes) | |ΔP| 99 % | |ΔP| médian aux signaux | Signaux perdus | Inversés | Déplacés | Nouveaux | Fragilité | ΔP&L app. | ΔP&L valid. | ΔP&L test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bybit | +0,1 s | 0,0000 | 0,0339 | 0,0000 | 8 | 14 | 205 | 6 | **23 %** | −615 $ | +2 $ | −295 $ |
| bybit | +0,5 s | 0,0000 | 0,0388 | 0,0001 | 11 | 17 | 316 | 10 | **36 %** | +184 $ | +113 $ | −703 $ |
| bybit | +1,0 s | 0,0000 | 0,0431 | 0,0008 | 12 | 20 | 359 | 8 | **40 %** | −249 $ | −689 $ | −649 $ |
| okx | +0,1 s | 0,0000 | 0,0275 | 0,0000 | 1 | 0 | 74 | 5 | **8 %** | −388 $ | −294 $ | −92 $ |
| okx | +0,5 s | 0,0000 | 0,0337 | 0,0000 | 2 | 1 | 207 | 6 | **22 %** | −377 $ | −113 $ | +643 $ |
| okx | +1,0 s | 0,0000 | 0,0389 | 0,0000 | 5 | 4 | 254 | 7 | **27 %** | −498 $ | +943 $ | +650 $ |
| chainlink | +0,1 s | 0,0000 | 0,0000 | 0,0000 | 0 | 0 | 0 | 0 | **0 %** | +0 $ | +0 $ | +0 $ |
| chainlink | +0,5 s | 0,0000 | 0,0000 | 0,0000 | 0 | 0 | 0 | 0 | **0 %** | +0 $ | +0 $ | +0 $ |
| chainlink | +1,0 s | 0,0000 | 0,0001 | 0,0000 | 0 | 0 | 0 | 0 | **0 %** | +0 $ | +0 $ | +0 $ |

## D. Sauts de probabilité : information nouvelle ou rattrapage de flux ?

Règle pré-enregistrée (avant de regarder les résultats) : un saut de la probabilité ENREGISTRÉE entre deux lignes consécutives (≤ 0,5 s) est un **rattrapage** si Bybit ou OKX change de valeur à cette ligne alors que son âge (indicateur) dépassait 1 s à la ligne précédente. « Retour à 3 s » = mouvement 3 s plus tard rapporté au saut (médiane ; 0 = le saut tient, −1 = entièrement défait).

Seuil |ΔP| ≥ 0,05 : 6812 sauts.

| Classe | Sauts | Part | Retour à 3 s (médiane) |
|---|---|---|---|
| information nouvelle (source fraîche) | 2841 | 42 % | −0,01 |
| rattrapage (source > 1 s puis mise à jour) | 2518 | 37 % | −0,01 |
| aucune source changée (cache σ/écart, horloge) | 1065 | 16 % | −0,32 |
| Chainlink seul | 385 | 6 % | −0,08 |
| prix d'exercice changé | 3 | 0 % | −0,10 |

Seuil |ΔP| ≥ 0,10 : 395 sauts.

| Classe | Sauts | Part | Retour à 3 s (médiane) |
|---|---|---|---|
| rattrapage (source > 1 s puis mise à jour) | 202 | 51 % | −0,00 |
| information nouvelle (source fraîche) | 186 | 47 % | −0,01 |
| aucune source changée (cache σ/écart, horloge) | 4 | 1 % | −0,98 |
| Chainlink seul | 2 | 1 % | 0,00 |
| prix d'exercice changé | 1 | 0 % | −0,00 |

Signaux V2-F (O8) selon ce qui s'est passé dans les 3 s de croissance de l'écart (exécution 0,3 s) :

| Période | Classe | Achats | Gagnés | Résultat |
|---|---|---|---|---|
| apprentissage | rattrapage dans les 3 s | 24 | 17 % | −50 $ |
| apprentissage | sans saut ≥ 0,05 | 175 | 21 % | +902 $ |
| apprentissage | saut d'information nouvelle | 24 | 17 % | +17 $ |
| test | rattrapage dans les 3 s | 16 | 0 % | −614 $ |
| test | sans saut ≥ 0,05 | 175 | 20 % | −1 833 $ |
| test | saut d'information nouvelle | 5 | 40 % | +63 $ |
| validation | rattrapage dans les 3 s | 38 | 16 % | −174 $ |
| validation | sans saut ≥ 0,05 | 240 | 20 % | −1 845 $ |
| validation | saut d'information nouvelle | 20 | 40 % | +420 $ |

## E. Instantanés « Frankenstein » : les faux désaccords ≥ 0,30 viennent-ils de sources d'âges très différents ?

Premier désaccord ≥ 0,30 de chaque cycle sur la probabilité enregistrée (vendeur 0,02-0,98, ≥ 5 s restantes) : 749 cycles. Dispersion = âge max − âge min (indicateur). p = test de permutation unilatéral (perdants plus dispersés que gagnants), 2 000 tirages.

| Sources | Perdants | Gagnants | Dispersion médiane perdants | gagnants | Dispersion > 1 s perdants | gagnants | p |
|---|---|---|---|---|---|---|---|
| Bybit / OKX / Chainlink (sources du modèle) | 625 | 124 | 1,19 s | 0,75 s | 50 % | 40 % | 0,013 |
| 5 sources | 625 | 124 | 2,10 s | 1,50 s | 68 % | 60 % | 0,135 |

Âges VRAIS (vitesse.json, décisions réelles « desaccord 30 », Bybit / OKX / Chainlink) :

| Issue | Décisions | Dispersion médiane | Dispersion > 1 s | Bybit ou OKX > 1 s | Bybit ET OKX > 1 s |
|---|---|---|---|---|---|
| perdu | 199 | 0,82 s | 41 % | 37 % | 9 % |
| gagné | 37 | 1,24 s | 57 % | 51 % | 8 % |

## F. Fenêtre Chainlink et prix à battre

1145 cycles. Notre K = prix d'exercice enregistré à la première ligne ≥ début + 10 s ; officiel = priceToBeat (officiels.json). « Secondes reçues » = secondes de [début − 60, début − 1] où la valeur Chainlink a changé (indicateur du compte du bot, qui exige ≥ 40). **Le bot a basculé du prix « site » au prix « moyenne Chainlink 60 s » le 09.10 19:20** (premier cycle à partir duquel ≥ 80 % des cycles suivants utilisent la moyenne, |K − moyenne 60 s recalculée| < 0,5 $) : avant, K était le prix instantané du site, faux de plusieurs dollars.

| Régime | Cycles | |erreur K| médiane | 90 % | 99 % | max | > 2 $ | > 10 $ |
|---|---|---|---|---|---|---|---|
| avant la bascule (K du site) | 707 | 10,45 $ | 33,09 $ | 67,80 $ | 103,03 $ | 606 | 363 |
| après la bascule (K = moyenne 60 s) | 438 | 0,10 $ | 1,74 $ | 14,72 $ | 36,02 $ | 41 | 16 |
| moyenne 60 s recalculée sur les lignes (tous cycles) | 1144 | 0,12 $ | 0,87 $ | 25,20 $ | 102,42 $ | 68 | 32 |

Après la bascule, 41 cycles sur 438 ont encore |erreur K| > 2 $ ; secondes Chainlink reçues dans ces cycles (indicateur) : médiane 52 (contre 53 pour tous les cycles après bascule) ; parmi eux 9 ont < 40 secondes reçues (le bot garde alors un autre prix). Erreurs : 09.10 19:20 −21,8 $ (54 s), 09.10 19:25 −3,1 $ (55 s), 09.10 19:30 −9,9 $ (50 s), 09.10 19:45 −10,1 $ (49 s), 09.10 19:50 4,6 $ (55 s), 09.10 20:00 −13,5 $ (55 s), 09.10 20:05 −3,5 $ (54 s), 09.10 20:10 −7,3 $ (56 s), 09.10 20:15 −9,2 $ (51 s), 09.10 20:20 −6,2 $ (56 s), 09.10 20:25 −5,2 $ (14 s), 09.10 20:30 −3,5 $ (57 s), 09.10 20:35 −10,8 $ (54 s), 09.10 20:50 36,0 $ (55 s), 09.10 21:00 −4,1 $ (0 s).


Hypothèse 5 (K calculé avec 40-59 secondes) — erreur de la moyenne 60 s selon le nombre de secondes reçues :

| Secondes reçues (indicateur) | Cycles | |erreur moyenne 60 s| médiane | 90 % | > 2 $ |
|---|---|---|---|---|
| 60 | 3 | 0,04 $ | 0,36 $ | 0 |
| 50-59 | 901 | 0,11 $ | 0,60 $ | 3 |
| 40-49 | 155 | 0,10 $ | 0,84 $ | 5 |
| < 40 | 85 | 6,51 $ | 29,33 $ | 60 |

Fin de cycle (hypothèse 4) : moyenne des 60 secondes REMPLIES contre prix final officiel : |écart| médian 0,12 $ (90 % 0,86 $) ; moyenne des seules secondes REÇUES (pondération du bot) : 0,22 $ (90 % 1,31 $). La moyenne remplie reproduit mieux l'officiel dans 71 % des cycles.

Faux désaccords selon l'erreur de K **dans notre sens** (= de combien notre K faux rendait NOTRE côté plus probable qu'avec le K officiel : (officiel − K) pour Up, (K − officiel) pour Down) :

| Signaux | Régime | Erreur dans notre sens | Signaux | Perdus | Taux de perte | Résultat (exécution 0,3 s) |
|---|---|---|---|---|---|---|
| désaccord ≥ 0,30 (O8) | avant bascule | < −2 $ (contre nous) | 56 | 46 | 82 % | +1 035 $ |
| désaccord ≥ 0,30 (O8) | avant bascule | −2 à +2 $ | 52 | 43 | 83 % | +240 $ |
| désaccord ≥ 0,30 (O8) | avant bascule | +2 à +10 $ | 75 | 66 | 88 % | −1 068 $ |
| désaccord ≥ 0,30 (O8) | avant bascule | > +10 $ (pour nous) | 171 | 129 | 75 % | +3 735 $ |
| désaccord ≥ 0,30 (O8) | après bascule | < −2 $ (contre nous) | 7 | 7 | 100 % | −239 $ |
| désaccord ≥ 0,30 (O8) | après bascule | −2 à +2 $ | 368 | 317 | 86 % | −1 426 $ |
| désaccord ≥ 0,30 (O8) | après bascule | +2 à +10 $ | 11 | 9 | 82 % | +70 $ |
| désaccord ≥ 0,30 (O8) | après bascule | > +10 $ (pour nous) | 9 | 8 | 89 % | −328 $ |
| V2-F (O8) | avant bascule | < −2 $ (contre nous) | 92 | 77 | 84 % | −437 $ |
| V2-F (O8) | avant bascule | −2 à +2 $ | 75 | 60 | 80 % | +1 025 $ |
| V2-F (O8) | avant bascule | +2 à +10 $ | 122 | 98 | 80 % | −408 $ |
| V2-F (O8) | avant bascule | > +10 $ (pour nous) | 254 | 180 | 71 % | +827 $ |
| V2-F (O8) | après bascule | < −2 $ (contre nous) | 9 | 9 | 100 % | −430 $ |
| V2-F (O8) | après bascule | −2 à +2 $ | 395 | 311 | 79 % | −3 060 $ |
| V2-F (O8) | après bascule | +2 à +10 $ | 12 | 10 | 83 % | −174 $ |
| V2-F (O8) | après bascule | > +10 $ (pour nous) | 13 | 12 | 92 % | −457 $ |

Signaux V2-F (O8) pris AVANT que K ne passe à la moyenne Chainlink (K provisoire du site) : 1 ; résultat −53 $.

## G. Causalité et déterminisme

- Lignes strictement croissantes dans le temps : oui ; lignes dans leur cycle [début, début + 300) : 99.83 %.
- Ce fichier : toute valeur à t = dernière ligne ≤ t (`searchsorted(..., 'right') − 1`) ; exécution = première ligne ≥ t + délai (`'left'`) ; 3 s avant = dernière ligne ≤ t − 3 ; séries à la seconde = secondes COMPLÈTES ≤ ts − 1 + valeur à la date pour la seconde courante.
- Déterminisme : deux passes du rejeu F8 → empreintes f672920279f592d5 / f672920279f592d5 ; deux passes de R8 → 0f4d363858822126 / 0f4d363858822126 : identiques.
- Anciens chargeurs audités :
  - `robustesse_E.py` : `sec(nom, s) = der(nom, s + 0,999)` n'est utilisé que pour des secondes < seconde de décision (σ, écart, fenêtre `range(deb, s)`) → **pas de fuite**.
  - `meta_router.py` (`P1`, `CL1`, `volr`, `baser`) repris par `attribution_001.parts_r` et `hedge_lab_commun` (X8, X1, H1, X15/P15/H15, cohorte B) : la seconde COURANTE est lue en fin de seconde (`range(s − 300, s + 1)`, `range(deb, s + 1)`) → **fuite jusqu'à 0,999 s** dans σ, l'écart et la moyenne Chainlink de la fenêtre.
  - `v3_commun.exe` / `attribution_001.execu` : exécution à la première ligne ≥ t + délai, prix ≤ prix de décision → pas de fuite ; `J3` = dernière ligne ≤ t − 3 → pas de fuite.
  - `hedge_lab_commun.arr` : report de la dernière valeur connue (passé seulement) → pas de fuite.
  - Sélection des cycles par l'existence d'un résultat officiel : n'utilise pas l'issue pour décider → pas de fuite de décision.

Impact mesuré de la fuite de `parts_r` (même modèle calculé avec la fin de seconde = « fuite », puis avec la valeur à la date) :

| Modèle | |ΔP| médian | |ΔP| 99 % | Signaux V2-F avec fuite | sans fuite | Cycles dont le signal change | P&L app. fuite → sans | valid. | test |
|---|---|---|---|---|---|---|---|---|---|
| X8 (0,08 %) | 0,0000 | 0,001 | 980 | 980 | 9 | +398 $ → +118 $ | +1 293 $ → +1 293 $ | −1 754 $ → −1 754 $ |
| X15 (0,015 %, cohorte B du Hedge Lab) | 0,0000 | 0,002 | 703 | 699 | 10 | +828 $ → +846 $ | −97 $ → −146 $ | −1 363 $ → −1 310 $ |

## H. Rejet par le marché (H186/H187, version rapide)

Signaux V2-F (O8). Mouvement du modèle pour notre côté sur les 3 s ≥ X, X = médiane de l'apprentissage = 0,018. « Le marché suit » = notre meilleur vendeur a monté d'au moins 1 c à t + k. Résultat = entrée au signal (exécution 0,3 s) gardée jusqu'au règlement (GARDER) ; variante exécutable = si rejet, revendre au meilleur acheteur à t + k (quantité affichée).

| k | Période | Classe | Achats | Gagnés | GARDER | Sortie si rejet | Δ |
|---|---|---|---|---|---|---|---|
| 1 s | apprentissage | le marché ne suit pas (rejet) | 50 | 22 % | +1 311 $ | +303 $ | −1 008 $ |
| 1 s | apprentissage | le marché suit (+1 c ou plus) | 31 | 29 % | +374 $ | +374 $ | +0 $ |
| 1 s | test | le marché ne suit pas (rejet) | 19 | 26 % | −45 $ | −9 $ | +35 $ |
| 1 s | test | le marché suit (+1 c ou plus) | 7 | 14 % | +3 $ | +3 $ | +0 $ |
| 1 s | validation | le marché ne suit pas (rejet) | 56 | 14 % | −147 $ | −290 $ | −144 $ |
| 1 s | validation | le marché suit (+1 c ou plus) | 23 | 22 % | +11 $ | +11 $ | +0 $ |
| 2 s | apprentissage | le marché ne suit pas (rejet) | 49 | 18 % | +739 $ | −218 $ | −956 $ |
| 2 s | apprentissage | le marché suit (+1 c ou plus) | 32 | 34 % | +946 $ | +946 $ | +0 $ |
| 2 s | test | le marché ne suit pas (rejet) | 17 | 29 % | +40 $ | −80 $ | −120 $ |
| 2 s | test | le marché suit (+1 c ou plus) | 9 | 11 % | −82 $ | −82 $ | +0 $ |
| 2 s | validation | le marché ne suit pas (rejet) | 48 | 12 % | −406 $ | −73 $ | +332 $ |
| 2 s | validation | le marché suit (+1 c ou plus) | 31 | 23 % | +270 $ | +270 $ | +0 $ |
| 3 s | apprentissage | le marché ne suit pas (rejet) | 50 | 16 % | +519 $ | −490 $ | −1 009 $ |
| 3 s | apprentissage | le marché suit (+1 c ou plus) | 31 | 39 % | +1 165 $ | +1 165 $ | +0 $ |
| 3 s | test | le marché ne suit pas (rejet) | 15 | 27 % | −72 $ | −222 $ | −150 $ |
| 3 s | test | le marché suit (+1 c ou plus) | 11 | 18 % | +30 $ | +30 $ | +0 $ |
| 3 s | validation | le marché ne suit pas (rejet) | 43 | 12 % | −438 $ | −238 $ | +200 $ |
| 3 s | validation | le marché suit (+1 c ou plus) | 36 | 22 % | +302 $ | +302 $ | +0 $ |

## I. Conservation des probabilités et complémentarité des carnets

- P(Down) = 1 − P(Up) **par construction** dans le code (le bot n'enregistre que P(Up) ; toutes les règles utilisent 1 − p) : conservation exacte, rien à tester numériquement. P(Up) enregistrée dans [0,0000 ; 1,0000].
- Carnets (783526 lignes complètes) : Up acheteur + Down vendeur = 1 → écarts > 1e-6 : 2 (max 0,0400) ; Up vendeur + Down acheteur = 1 → 0 (max 0,0000). Tailles miroirs différentes : 26 / 33 lignes. Les deux carnets sont donc le MÊME carnet vu des deux côtés (Polymarket croise Up et Down).
- Somme des deux meilleurs vendeurs : médiane 1,01 ; lignes où Up vendeur + Down vendeur < 1 (arbitrage apparent = instantané incohérent) : 20 ; Up acheteur + Down acheteur > 1 : 21.

## J. Jumeau causal (hors ligne) : A = R8 (comme le bot), B = F8 (fraîcheur)

Chaque divergence (cycle où A et B ne font pas la même chose), avec le P&L marginal B − A (exécution 0,3 s).

| Cycle | Période | A : côté · instant · prix | B : côté · instant · prix | Type | A P&L | B P&L | B − A |
|---|---|---|---|---|---|---|---|
| 07.10 08:00 | apprentissage | Up · 163 s · 0,13 | Up · 203 s · 0,20 | instant déplacé | −11 $ | −53 $ | −42 $ |
| 07.10 08:10 | apprentissage | Up · 183 s · 0,12 | Up · 144 s · 0,20 | instant déplacé | −53 $ | −12 $ | +42 $ |
| 07.10 08:20 | apprentissage | Up · 42 s · 0,21 | Up · 25 s · 0,25 | instant déplacé | +105 $ | +147 $ | +42 $ |
| 07.10 08:25 | apprentissage | Up · 135 s · 0,13 | Up · 104 s · 0,13 | instant déplacé | +0 $ | +331 $ | +331 $ |
| 07.10 08:30 | apprentissage | Up · 20 s · 0,41 | Up · 27 s · 0,34 | instant déplacé | +26 $ | +95 $ | +69 $ |
| 07.10 08:55 | apprentissage | Up · 191 s · 0,24 | Up · 199 s · 0,24 | instant déplacé | −45 $ | −53 $ | −8 $ |
| 07.10 09:15 | apprentissage | — | Up · 136 s · 0,09 | B seul | +0 $ | −53 $ | −53 $ |
| 07.10 09:20 | apprentissage | — | Down · 106 s · 0,16 | B seul | +0 $ | −53 $ | −53 $ |
| 07.10 09:40 | apprentissage | — | Down · 83 s · 0,12 | B seul | +0 $ | −53 $ | −53 $ |
| 07.10 09:45 | apprentissage | Up · 112 s · 0,15 | Up · 76 s · 0,17 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 09:55 | apprentissage | Up · 121 s · 0,12 | Up · 97 s · 0,13 | instant déplacé | +401 $ | +331 $ | −70 $ |
| 07.10 10:05 | apprentissage | Up · 158 s · 0,19 | Up · 123 s · 0,12 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 07.10 10:10 | apprentissage | Up · 240 s · 0,08 | Up · 239 s · 0,10 | instant déplacé | +0 $ | −2 $ | −2 $ |
| 07.10 10:15 | apprentissage | Up · 149 s · 0,25 | — | B saute | −53 $ | +0 $ | +53 $ |
| 07.10 10:20 | apprentissage | Down · 108 s · 0,13 | Down · 101 s · 0,22 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 10:25 | apprentissage | Down · 193 s · 0,05 | Down · 182 s · 0,04 | instant déplacé | −1 $ | −3 $ | −3 $ |
| 07.10 10:30 | apprentissage | Down · 81 s · 0,48 | Down · 203 s · 0,20 | instant déplacé | −52 $ | −53 $ | −1 $ |
| 07.10 10:40 | apprentissage | Up · 161 s · 0,10 | Up · 145 s · 0,07 | instant déplacé | −31 $ | +0 $ | +31 $ |
| 07.10 10:50 | apprentissage | Up · 120 s · 0,20 | Up · 119 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 11:00 | apprentissage | Down · 154 s · 0,08 | Down · 146 s · 0,12 | instant déplacé | −41 $ | −44 $ | −2 $ |
| 07.10 11:10 | apprentissage | Down · 139 s · 0,15 | Down · 132 s · 0,17 | instant déplacé | −18 $ | −53 $ | −35 $ |
| 07.10 11:15 | apprentissage | Up · 144 s · 0,12 | Up · 126 s · 0,14 | instant déplacé | +0 $ | −4 $ | −4 $ |
| 07.10 11:20 | apprentissage | Up · 178 s · 0,16 | Up · 168 s · 0,18 | instant déplacé | −25 $ | −8 $ | +18 $ |
| 07.10 11:25 | apprentissage | Down · 24 s · 0,36 | Down · 31 s · 0,34 | instant déplacé | −52 $ | −52 $ | −0 $ |
| 07.10 11:30 | apprentissage | Down · 38 s · 0,30 | Down · 39 s · 0,30 | instant déplacé | +114 $ | +58 $ | −56 $ |
| 07.10 11:35 | apprentissage | Down · 190 s · 0,36 | Up · 85 s · 0,26 | côté inversé | −52 $ | +140 $ | +192 $ |
| 07.10 11:40 | apprentissage | Up · 68 s · 0,18 | Up · 53 s · 0,16 | instant déplacé | +225 $ | +280 $ | +55 $ |
| 07.10 11:45 | apprentissage | Down · 215 s · 0,23 | Down · 176 s · 0,24 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 07.10 12:00 | apprentissage | Down · 101 s · 0,42 | — | B saute | +0 $ | +0 $ | +0 $ |
| 07.10 12:40 | apprentissage | — | Up · 217 s · 0,04 | B seul | +0 $ | +0 $ | +0 $ |
| 07.10 12:55 | apprentissage | Up · 191 s · 0,07 | Up · 143 s · 0,10 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 07.10 13:00 | apprentissage | Down · 137 s · 0,10 | Down · 120 s · 0,18 | instant déplacé | +447 $ | +0 $ | −447 $ |
| 07.10 13:20 | apprentissage | Up · 90 s · 0,21 | Up · 53 s · 0,20 | instant déplacé | +0 $ | +167 $ | +167 $ |
| 07.10 13:25 | apprentissage | Up · 67 s · 0,22 | Up · 44 s · 0,25 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 07.10 13:30 | apprentissage | Up · 189 s · 0,07 | Up · 35 s · 0,14 | instant déplacé | −27 $ | +0 $ | +27 $ |
| 07.10 13:35 | apprentissage | Up · 87 s · 0,22 | Up · 26 s · 0,22 | instant déplacé | +0 $ | −15 $ | −15 $ |
| 07.10 13:50 | apprentissage | Up · 196 s · 0,12 | Up · 191 s · 0,16 | instant déplacé | +0 $ | +259 $ | +259 $ |
| 07.10 13:55 | apprentissage | Down · 100 s · 0,22 | Down · 101 s · 0,19 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 07.10 14:05 | apprentissage | Down · 210 s · 0,35 | Down · 214 s · 0,16 | instant déplacé | −3 $ | −53 $ | −50 $ |
| 07.10 14:10 | apprentissage | Up · 182 s · 0,10 | Up · 183 s · 0,09 | instant déplacé | −53 $ | −22 $ | +31 $ |
| 07.10 14:20 | apprentissage | Up · 202 s · 0,33 | Down · 224 s · 0,06 | côté inversé | +99 $ | +0 $ | −99 $ |
| 07.10 14:55 | apprentissage | Down · 204 s · 0,08 | Down · 202 s · 0,11 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 15:00 | apprentissage | Down · 215 s · 0,07 | Down · 215 s · 0,07 | instant déplacé | +398 $ | +751 $ | +353 $ |
| 07.10 15:10 | apprentissage | Up · 167 s · 0,11 | Up · 168 s · 0,09 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 07.10 15:15 | apprentissage | Down · 148 s · 0,10 | Down · 121 s · 0,21 | instant déplacé | +0 $ | −8 $ | −8 $ |
| 07.10 15:30 | apprentissage | — | Down · 174 s · 0,07 | B seul | +0 $ | +0 $ | +0 $ |
| 07.10 15:35 | apprentissage | Up · 37 s · 0,19 | Up · 27 s · 0,16 | instant déplacé | −8 $ | +0 $ | +8 $ |
| 07.10 15:40 | apprentissage | Up · 240 s · 0,19 | Up · 232 s · 0,21 | instant déplacé | −7 $ | −15 $ | −8 $ |
| 07.10 16:00 | apprentissage | Up · 98 s · 0,17 | Up · 62 s · 0,19 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 07.10 16:05 | apprentissage | Up · 59 s · 0,34 | — | B saute | +0 $ | +0 $ | +0 $ |
| 07.10 16:45 | apprentissage | Up · 99 s · 0,51 | Up · 237 s · 0,31 | instant déplacé | +0 $ | −52 $ | −52 $ |
| 07.10 16:50 | apprentissage | Down · 165 s · 0,34 | Down · 207 s · 0,23 | instant déplacé | +0 $ | −44 $ | −44 $ |
| 07.10 16:55 | apprentissage | Down · 26 s · 0,47 | Up · 256 s · 0,04 | côté inversé | +0 $ | −53 $ | −53 $ |
| 07.10 17:05 | apprentissage | Down · 116 s · 0,32 | Up · 170 s · 0,10 | côté inversé | +104 $ | +0 $ | −104 $ |
| 07.10 17:10 | apprentissage | — | Down · 160 s · 0,06 | B seul | +0 $ | −2 $ | −2 $ |
| 07.10 17:15 | apprentissage | Up · 186 s · 0,23 | Up · 192 s · 0,12 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 07.10 17:20 | apprentissage | Up · 178 s · 0,11 | Up · 171 s · 0,08 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 07.10 17:35 | apprentissage | Down · 200 s · 0,07 | Down · 192 s · 0,08 | instant déplacé | −3 $ | +0 $ | +3 $ |
| 07.10 17:40 | apprentissage | — | Down · 145 s · 0,07 | B seul | +0 $ | +0 $ | +0 $ |
| 07.10 17:50 | apprentissage | Down · 143 s · 0,05 | Down · 143 s · 0,05 | instant déplacé | −10 $ | −10 $ | +0 $ |
| 07.10 17:55 | apprentissage | Up · 150 s · 0,24 | Up · 155 s · 0,19 | instant déplacé | +156 $ | +63 $ | −92 $ |
| 07.10 18:05 | apprentissage | Down · 182 s · 0,06 | Down · 164 s · 0,11 | instant déplacé | −19 $ | +0 $ | +19 $ |
| 07.10 18:15 | apprentissage | — | Down · 167 s · 0,12 | B seul | +0 $ | −53 $ | −53 $ |
| 07.10 18:25 | apprentissage | Up · 22 s · 0,24 | Up · 31 s · 0,23 | instant déplacé | +6 $ | +0 $ | −6 $ |
| 07.10 18:40 | apprentissage | Up · 138 s · 0,08 | Up · 66 s · 0,16 | instant déplacé | −5 $ | −53 $ | −48 $ |
| 07.10 18:50 | apprentissage | Up · 233 s · 0,34 | Down · 180 s · 0,09 | côté inversé | +99 $ | −6 $ | −105 $ |
| 07.10 19:00 | apprentissage | Down · 139 s · 0,05 | Down · 189 s · 0,03 | instant déplacé | −41 $ | +0 $ | +41 $ |
| 07.10 19:05 | apprentissage | Up · 69 s · 0,24 | Up · 68 s · 0,26 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 19:10 | apprentissage | Down · 143 s · 0,13 | Down · 63 s · 0,25 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 19:15 | apprentissage | Up · 181 s · 0,09 | Up · 197 s · 0,07 | instant déplacé | −53 $ | −51 $ | +3 $ |
| 07.10 19:20 | apprentissage | Up · 170 s · 0,20 | Up · 149 s · 0,12 | instant déplacé | +0 $ | −28 $ | −28 $ |
| 07.10 19:30 | apprentissage | Down · 185 s · 0,09 | Down · 185 s · 0,10 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 19:45 | apprentissage | Down · 112 s · 0,23 | Down · 110 s · 0,25 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 19:50 | apprentissage | Down · 184 s · 0,10 | Down · 184 s · 0,10 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 07.10 19:55 | apprentissage | Down · 201 s · 0,15 | Down · 157 s · 0,16 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 07.10 20:05 | apprentissage | Down · 100 s · 0,18 | Down · 61 s · 0,08 | instant déplacé | +225 $ | +139 $ | −86 $ |
| 07.10 20:10 | apprentissage | Down · 97 s · 0,27 | Down · 102 s · 0,21 | instant déplacé | −40 $ | −1 $ | +38 $ |
| 07.10 20:15 | apprentissage | Up · 177 s · 0,22 | Up · 183 s · 0,22 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 20:20 | apprentissage | Up · 95 s · 0,24 | Up · 196 s · 0,36 | instant déplacé | +156 $ | +87 $ | −69 $ |
| 07.10 20:25 | apprentissage | Down · 75 s · 0,35 | Down · 120 s · 0,28 | instant déplacé | −22 $ | −53 $ | −31 $ |
| 07.10 20:35 | apprentissage | Down · 208 s · 0,07 | Down · 202 s · 0,05 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 20:55 | apprentissage | Up · 133 s · 0,40 | Up · 142 s · 0,36 | instant déplacé | −17 $ | −52 $ | −36 $ |
| 07.10 21:00 | apprentissage | Down · 146 s · 0,03 | Down · 123 s · 0,07 | instant déplacé | +283 $ | +88 $ | −195 $ |
| 07.10 21:05 | apprentissage | Up · 172 s · 0,17 | Down · 73 s · 0,22 | côté inversé | +4 $ | +0 $ | −4 $ |
| 07.10 21:40 | apprentissage | Down · 211 s · 0,08 | Down · 212 s · 0,07 | instant déplacé | −38 $ | −14 $ | +24 $ |
| 07.10 21:50 | apprentissage | Down · 81 s · 0,25 | Down · 258 s · 0,13 | instant déplacé | +0 $ | −30 $ | −30 $ |
| 07.10 22:00 | apprentissage | Down · 125 s · 0,12 | Down · 37 s · 0,24 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 07.10 22:10 | apprentissage | Down · 22 s · 0,31 | Down · 46 s · 0,33 | instant déplacé | −17 $ | −52 $ | −35 $ |
| 07.10 22:20 | apprentissage | Up · 200 s · 0,19 | Up · 217 s · 0,17 | instant déplacé | −53 $ | −33 $ | +19 $ |
| 07.10 22:30 | apprentissage | Up · 158 s · 0,09 | Up · 143 s · 0,17 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 22:35 | apprentissage | Up · 40 s · 0,10 | Up · 33 s · 0,13 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 07.10 22:40 | apprentissage | Down · 137 s · 0,22 | Down · 169 s · 0,08 | instant déplacé | −1 $ | −18 $ | −17 $ |
| 07.10 22:45 | apprentissage | Up · 161 s · 0,20 | Up · 123 s · 0,15 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 07.10 22:50 | apprentissage | Down · 99 s · 0,18 | Down · 95 s · 0,17 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 23:00 | apprentissage | Up · 126 s · 0,12 | Down · 47 s · 0,28 | côté inversé | −53 $ | +0 $ | +53 $ |
| 07.10 23:10 | apprentissage | Up · 120 s · 0,15 | Up · 181 s · 0,08 | instant déplacé | −21 $ | −53 $ | −32 $ |
| 07.10 23:15 | apprentissage | Down · 138 s · 0,13 | Down · 140 s · 0,13 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 23:20 | apprentissage | Down · 115 s · 0,28 | Down · 129 s · 0,20 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 23:25 | apprentissage | Up · 48 s · 0,11 | Up · 51 s · 0,12 | instant déplacé | −35 $ | −53 $ | −18 $ |
| 07.10 23:30 | apprentissage | Up · 63 s · 0,20 | Up · 62 s · 0,18 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 07.10 23:55 | apprentissage | Down · 111 s · 0,09 | Down · 108 s · 0,10 | instant déplacé | −40 $ | +0 $ | +40 $ |
| 08.10 00:00 | apprentissage | Down · 162 s · 0,04 | Down · 159 s · 0,03 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 00:05 | apprentissage | Down · 63 s · 0,26 | Down · 64 s · 0,27 | instant déplacé | −53 $ | −13 $ | +40 $ |
| 08.10 00:15 | apprentissage | Up · 204 s · 0,07 | Up · 105 s · 0,19 | instant déplacé | −13 $ | −53 $ | −40 $ |
| 08.10 00:25 | apprentissage | Down · 28 s · 0,31 | Down · 119 s · 0,27 | instant déplacé | −52 $ | −53 $ | −0 $ |
| 08.10 00:35 | apprentissage | Up · 72 s · 0,30 | Up · 31 s · 0,23 | instant déplacé | −2 $ | −53 $ | −51 $ |
| 08.10 00:40 | apprentissage | Up · 35 s · 0,24 | Up · 38 s · 0,19 | instant déplacé | +185 $ | +210 $ | +25 $ |
| 08.10 00:55 | apprentissage | Down · 87 s · 0,12 | Down · 81 s · 0,16 | instant déplacé | −34 $ | −53 $ | −19 $ |
| 08.10 01:00 | apprentissage | Up · 22 s · 0,31 | Up · 46 s · 0,25 | instant déplacé | −52 $ | −53 $ | −0 $ |
| 08.10 01:15 | apprentissage | — | Down · 155 s · 0,05 | B seul | +0 $ | −12 $ | −12 $ |
| 08.10 01:20 | apprentissage | Down · 42 s · 0,27 | Down · 50 s · 0,23 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 01:25 | apprentissage | Down · 75 s · 0,13 | Down · 23 s · 0,17 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 01:35 | apprentissage | Up · 133 s · 0,24 | Up · 152 s · 0,22 | instant déplacé | −53 $ | −19 $ | +34 $ |
| 08.10 01:40 | apprentissage | Up · 21 s · 0,21 | Up · 20 s · 0,22 | instant déplacé | −10 $ | −53 $ | −43 $ |
| 08.10 01:50 | apprentissage | Up · 69 s · 0,10 | Up · 62 s · 0,13 | instant déplacé | +0 $ | −12 $ | −12 $ |
| 08.10 02:10 | apprentissage | Up · 36 s · 0,13 | Up · 46 s · 0,22 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 02:20 | apprentissage | — | Up · 134 s · 0,06 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 02:25 | apprentissage | Up · 46 s · 0,27 | Up · 49 s · 0,25 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 02:35 | apprentissage | Up · 115 s · 0,18 | Up · 65 s · 0,19 | instant déplacé | −53 $ | −34 $ | +19 $ |
| 08.10 02:40 | apprentissage | Up · 218 s · 0,32 | Up · 220 s · 0,17 | instant déplacé | +5 $ | +0 $ | −5 $ |
| 08.10 02:45 | apprentissage | Down · 148 s · 0,08 | Down · 120 s · 0,13 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 02:50 | apprentissage | Down · 189 s · 0,12 | Down · 168 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 03:00 | apprentissage | Down · 196 s · 0,03 | Down · 123 s · 0,11 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 03:05 | apprentissage | Down · 182 s · 0,16 | Down · 100 s · 0,12 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 03:20 | apprentissage | — | Up · 70 s · 0,17 | B seul | +0 $ | −53 $ | −53 $ |
| 08.10 03:25 | apprentissage | Down · 129 s · 0,09 | Down · 123 s · 0,14 | instant déplacé | −21 $ | −5 $ | +15 $ |
| 08.10 03:40 | apprentissage | Down · 162 s · 0,14 | Down · 153 s · 0,13 | instant déplacé | +153 $ | +57 $ | −96 $ |
| 08.10 03:45 | apprentissage | Up · 122 s · 0,19 | Up · 121 s · 0,20 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 03:50 | apprentissage | Up · 208 s · 0,04 | Up · 192 s · 0,03 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 03:55 | apprentissage | Up · 39 s · 0,23 | Up · 38 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 04:00 | apprentissage | Down · 156 s · 0,05 | Down · 122 s · 0,12 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 04:05 | apprentissage | Up · 48 s · 0,14 | Up · 48 s · 0,14 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 04:15 | apprentissage | Down · 118 s · 0,16 | Down · 116 s · 0,10 | instant déplacé | +35 $ | +0 $ | −35 $ |
| 08.10 04:20 | apprentissage | Down · 147 s · 0,20 | Down · 144 s · 0,24 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 04:45 | apprentissage | Up · 202 s · 0,25 | Up · 188 s · 0,20 | instant déplacé | −53 $ | −15 $ | +38 $ |
| 08.10 04:55 | apprentissage | Down · 123 s · 0,12 | Down · 70 s · 0,14 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 05:00 | apprentissage | Up · 38 s · 0,39 | Up · 139 s · 0,21 | instant déplacé | −2 $ | −53 $ | −51 $ |
| 08.10 05:20 | apprentissage | Up · 158 s · 0,23 | Up · 113 s · 0,09 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 05:30 | apprentissage | — | Up · 162 s · 0,08 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 06:05 | apprentissage | Up · 64 s · 0,51 | Up · 81 s · 0,51 | instant déplacé | +42 $ | +40 $ | −2 $ |
| 08.10 06:10 | apprentissage | Up · 87 s · 0,23 | Up · 86 s · 0,25 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 06:20 | apprentissage | — | Up · 31 s · 0,08 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 06:30 | apprentissage | Up · 238 s · 0,05 | Up · 204 s · 0,08 | instant déplacé | −28 $ | −7 $ | +22 $ |
| 08.10 06:40 | apprentissage | Up · 78 s · 0,22 | Up · 72 s · 0,20 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 07:15 | apprentissage | Down · 143 s · 0,25 | Down · 144 s · 0,18 | instant déplacé | −53 $ | −1 $ | +52 $ |
| 08.10 07:20 | apprentissage | Down · 160 s · 0,13 | Down · 111 s · 0,18 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 07:25 | apprentissage | Up · 163 s · 0,12 | Up · 122 s · 0,13 | instant déplacé | −6 $ | +0 $ | +6 $ |
| 08.10 07:30 | apprentissage | Up · 132 s · 0,09 | Up · 107 s · 0,20 | instant déplacé | +0 $ | +197 $ | +197 $ |
| 08.10 07:35 | apprentissage | Down · 216 s · 0,33 | Up · 186 s · 0,13 | côté inversé | +0 $ | +0 $ | +0 $ |
| 08.10 07:40 | apprentissage | Up · 189 s · 0,03 | Up · 96 s · 0,13 | instant déplacé | −5 $ | −53 $ | −48 $ |
| 08.10 07:45 | apprentissage | Up · 123 s · 0,14 | Up · 114 s · 0,15 | instant déplacé | +0 $ | +167 $ | +167 $ |
| 08.10 08:10 | apprentissage | Down · 150 s · 0,16 | Down · 96 s · 0,16 | instant déplacé | −48 $ | +0 $ | +48 $ |
| 08.10 08:15 | apprentissage | Down · 120 s · 0,25 | Down · 109 s · 0,27 | instant déplacé | +0 $ | +133 $ | +133 $ |
| 08.10 08:30 | apprentissage | Up · 186 s · 0,04 | Up · 136 s · 0,07 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 08:50 | apprentissage | Down · 76 s · 0,21 | Down · 70 s · 0,23 | instant déplacé | −53 $ | −9 $ | +44 $ |
| 08.10 08:55 | apprentissage | Down · 24 s · 0,27 | Down · 29 s · 0,25 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 09:00 | apprentissage | — | Up · 42 s · 0,19 | B seul | +0 $ | −53 $ | −53 $ |
| 08.10 09:20 | apprentissage | Down · 215 s · 0,06 | Down · 210 s · 0,04 | instant déplacé | −31 $ | −25 $ | +6 $ |
| 08.10 09:25 | apprentissage | Up · 70 s · 0,13 | Up · 28 s · 0,20 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 09:30 | apprentissage | Down · 140 s · 0,19 | Down · 134 s · 0,18 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 09:35 | apprentissage | — | Down · 178 s · 0,07 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 09:40 | apprentissage | Up · 103 s · 0,20 | Up · 27 s · 0,19 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 09:45 | apprentissage | Up · 192 s · 0,12 | Up · 180 s · 0,15 | instant déplacé | −11 $ | −7 $ | +3 $ |
| 08.10 09:50 | apprentissage | Up · 175 s · 0,15 | Up · 169 s · 0,13 | instant déplacé | −9 $ | −4 $ | +5 $ |
| 08.10 10:00 | apprentissage | Up · 168 s · 0,19 | Up · 160 s · 0,21 | instant déplacé | −8 $ | −53 $ | −45 $ |
| 08.10 10:05 | apprentissage | Down · 139 s · 0,27 | Down · 46 s · 0,18 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 10:10 | apprentissage | — | Up · 181 s · 0,06 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 10:20 | apprentissage | Up · 97 s · 0,11 | Up · 100 s · 0,11 | instant déplacé | −26 $ | −15 $ | +11 $ |
| 08.10 10:25 | apprentissage | Down · 135 s · 0,16 | Down · 180 s · 0,05 | instant déplacé | −53 $ | −2 $ | +51 $ |
| 08.10 10:50 | apprentissage | Up · 148 s · 0,14 | Up · 135 s · 0,16 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 10:55 | apprentissage | Up · 162 s · 0,48 | Down · 182 s · 0,23 | côté inversé | +0 $ | −2 $ | −2 $ |
| 08.10 11:00 | apprentissage | Down · 99 s · 0,17 | Down · 46 s · 0,19 | instant déplacé | −53 $ | −10 $ | +43 $ |
| 08.10 11:15 | apprentissage | — | Up · 28 s · 0,23 | B seul | +0 $ | −53 $ | −53 $ |
| 08.10 11:20 | apprentissage | Down · 102 s · 0,20 | Down · 93 s · 0,24 | instant déplacé | +0 $ | −31 $ | −31 $ |
| 08.10 11:35 | apprentissage | Down · 246 s · 0,12 | Down · 232 s · 0,14 | instant déplacé | −3 $ | −53 $ | −50 $ |
| 08.10 11:40 | apprentissage | Down · 182 s · 0,22 | Down · 168 s · 0,24 | instant déplacé | +174 $ | +52 $ | −122 $ |
| 08.10 11:45 | apprentissage | Down · 51 s · 0,15 | Down · 45 s · 0,18 | instant déplacé | +0 $ | +225 $ | +225 $ |
| 08.10 11:55 | apprentissage | Up · 39 s · 0,33 | Up · 41 s · 0,28 | instant déplacé | +0 $ | +126 $ | +126 $ |
| 08.10 12:00 | apprentissage | Down · 152 s · 0,18 | Down · 152 s · 0,19 | instant déplacé | −1 $ | −13 $ | −12 $ |
| 08.10 12:15 | apprentissage | Up · 92 s · 0,08 | Up · 80 s · 0,11 | instant déplacé | +0 $ | −10 $ | −10 $ |
| 08.10 12:20 | apprentissage | Up · 68 s · 0,18 | Up · 40 s · 0,23 | instant déplacé | −53 $ | −16 $ | +37 $ |
| 08.10 12:40 | apprentissage | Up · 218 s · 0,15 | Up · 231 s · 0,23 | instant déplacé | +0 $ | +165 $ | +165 $ |
| 08.10 12:50 | apprentissage | Down · 18 s · 0,35 | Down · 19 s · 0,32 | instant déplacé | −52 $ | −21 $ | +31 $ |
| 08.10 13:05 | apprentissage | Down · 46 s · 0,30 | Down · 24 s · 0,20 | instant déplacé | +114 $ | +197 $ | +83 $ |
| 08.10 13:10 | apprentissage | Up · 180 s · 0,16 | Up · 55 s · 0,13 | instant déplacé | +259 $ | +331 $ | +72 $ |
| 08.10 13:15 | apprentissage | — | Up · 211 s · 0,03 | B seul | +0 $ | −2 $ | −2 $ |
| 08.10 13:45 | apprentissage | Up · 157 s · 0,15 | — | B saute | −53 $ | +0 $ | +53 $ |
| 08.10 13:50 | apprentissage | Down · 60 s · 0,15 | Down · 30 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 14:10 | apprentissage | Up · 71 s · 0,16 | Up · 69 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 14:15 | apprentissage | Up · 225 s · 0,08 | Up · 217 s · 0,08 | instant déplacé | −53 $ | −26 $ | +27 $ |
| 08.10 14:20 | apprentissage | Down · 29 s · 0,15 | Down · 25 s · 0,14 | instant déplacé | +0 $ | −37 $ | −37 $ |
| 08.10 14:35 | apprentissage | Up · 239 s · 0,21 | Up · 247 s · 0,29 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 14:40 | apprentissage | Down · 230 s · 0,13 | Down · 232 s · 0,12 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 14:50 | apprentissage | Down · 120 s · 0,12 | Down · 97 s · 0,13 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 14:55 | apprentissage | Down · 272 s · 0,31 | Up · 281 s · 0,38 | côté inversé | +47 $ | +0 $ | −47 $ |
| 08.10 15:05 | apprentissage | Down · 24 s · 0,20 | Down · 19 s · 0,24 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 15:45 | apprentissage | Up · 232 s · 0,06 | Up · 203 s · 0,14 | instant déplacé | −22 $ | −4 $ | +18 $ |
| 08.10 15:55 | apprentissage | Up · 141 s · 0,16 | Up · 90 s · 0,31 | instant déplacé | +259 $ | +0 $ | −259 $ |
| 08.10 16:00 | apprentissage | Down · 245 s · 0,10 | Down · 243 s · 0,10 | instant déplacé | −15 $ | −50 $ | −35 $ |
| 08.10 16:05 | apprentissage | Down · 224 s · 0,04 | Down · 162 s · 0,12 | instant déplacé | −8 $ | −53 $ | −45 $ |
| 08.10 16:10 | apprentissage | — | Down · 49 s · 0,18 | B seul | +0 $ | −53 $ | −53 $ |
| 08.10 16:20 | apprentissage | Down · 240 s · 0,07 | Down · 238 s · 0,10 | instant déplacé | +549 $ | +447 $ | −102 $ |
| 08.10 16:25 | apprentissage | — | Down · 176 s · 0,04 | B seul | +0 $ | −15 $ | −15 $ |
| 08.10 16:40 | apprentissage | Up · 230 s · 0,15 | Up · 225 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 16:45 | apprentissage | — | Down · 156 s · 0,07 | B seul | +0 $ | −18 $ | −18 $ |
| 08.10 17:05 | apprentissage | Up · 151 s · 0,19 | Up · 116 s · 0,23 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 17:40 | apprentissage | — | Down · 145 s · 0,46 | B seul | +0 $ | +57 $ | +57 $ |
| 08.10 17:50 | apprentissage | Down · 116 s · 0,14 | Down · 90 s · 0,11 | instant déplacé | +0 $ | +252 $ | +252 $ |
| 08.10 18:00 | apprentissage | Up · 155 s · 0,35 | Down · 225 s · 0,14 | côté inversé | +0 $ | +0 $ | +0 $ |
| 08.10 18:10 | apprentissage | Up · 196 s · 0,24 | — | B saute | −1 $ | +0 $ | +1 $ |
| 08.10 18:30 | apprentissage | — | Up · 185 s · 0,12 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 18:35 | apprentissage | Down · 43 s · 0,28 | Down · 30 s · 0,21 | instant déplacé | −9 $ | −23 $ | −14 $ |
| 08.10 19:35 | apprentissage | Up · 187 s · 0,18 | Up · 185 s · 0,14 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 19:40 | apprentissage | Down · 66 s · 0,37 | Down · 92 s · 0,42 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 19:50 | apprentissage | Up · 26 s · 0,24 | Up · 35 s · 0,27 | instant déplacé | +165 $ | +140 $ | −25 $ |
| 08.10 19:55 | apprentissage | Down · 240 s · 0,16 | Down · 241 s · 0,16 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 20:00 | apprentissage | Down · 183 s · 0,33 | Down · 175 s · 0,18 | instant déplacé | +3 $ | +0 $ | −3 $ |
| 08.10 20:05 | apprentissage | Up · 136 s · 0,18 | Up · 135 s · 0,16 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 20:25 | apprentissage | Down · 129 s · 0,41 | Down · 135 s · 0,35 | instant déplacé | +0 $ | −52 $ | −52 $ |
| 08.10 20:35 | apprentissage | Up · 195 s · 0,09 | Up · 193 s · 0,04 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 20:40 | apprentissage | Down · 38 s · 0,34 | Down · 128 s · 0,30 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 20:55 | apprentissage | Up · 239 s · 0,29 | Up · 242 s · 0,12 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 21:10 | apprentissage | Down · 217 s · 0,06 | Down · 139 s · 0,09 | instant déplacé | +0 $ | −44 $ | −44 $ |
| 08.10 21:15 | apprentissage | — | Down · 210 s · 0,03 | B seul | +0 $ | −15 $ | −15 $ |
| 08.10 21:40 | apprentissage | Up · 199 s · 0,06 | Up · 149 s · 0,07 | instant déplacé | −19 $ | +0 $ | +19 $ |
| 08.10 21:45 | apprentissage | Down · 207 s · 0,22 | Down · 205 s · 0,24 | instant déplacé | −19 $ | −53 $ | −34 $ |
| 08.10 21:55 | apprentissage | Down · 162 s · 0,10 | Down · 144 s · 0,13 | instant déplacé | +447 $ | +331 $ | −115 $ |
| 08.10 22:00 | validation | Down · 206 s · 0,09 | Down · 180 s · 0,17 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 08.10 22:05 | validation | Down · 213 s · 0,04 | Down · 215 s · 0,05 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 22:15 | validation | Up · 147 s · 0,26 | Up · 143 s · 0,27 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 08.10 22:30 | validation | Up · 164 s · 0,14 | Up · 170 s · 0,13 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 22:35 | validation | Down · 9 s · 0,31 | Down · 17 s · 0,31 | instant déplacé | −52 $ | +0 $ | +52 $ |
| 08.10 22:40 | validation | Down · 132 s · 0,22 | Down · 152 s · 0,23 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 08.10 22:50 | validation | Down · 246 s · 0,06 | Down · 246 s · 0,05 | instant déplacé | −17 $ | −11 $ | +7 $ |
| 08.10 22:55 | validation | Down · 114 s · 0,29 | Down · 117 s · 0,26 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 23:00 | validation | Up · 106 s · 0,06 | Up · 63 s · 0,16 | instant déplacé | −49 $ | −53 $ | −4 $ |
| 08.10 23:05 | validation | Down · 230 s · 0,18 | Up · 64 s · 0,19 | côté inversé | +0 $ | +0 $ | +0 $ |
| 08.10 23:10 | validation | Down · 125 s · 0,07 | Down · 69 s · 0,14 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 08.10 23:15 | validation | Up · 130 s · 0,23 | Up · 129 s · 0,24 | instant déplacé | +165 $ | +156 $ | −9 $ |
| 08.10 23:20 | validation | Down · 57 s · 0,25 | Down · 59 s · 0,24 | instant déplacé | +156 $ | +74 $ | −81 $ |
| 08.10 23:25 | validation | Up · 24 s · 0,13 | Up · 25 s · 0,12 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 08.10 23:35 | validation | Down · 120 s · 0,06 | Down · 33 s · 0,20 | instant déplacé | −21 $ | −26 $ | −5 $ |
| 08.10 23:45 | validation | — | Up · 132 s · 0,07 | B seul | +0 $ | +0 $ | +0 $ |
| 08.10 23:55 | validation | Down · 120 s · 0,21 | Down · 68 s · 0,21 | instant déplacé | +54 $ | +185 $ | +132 $ |
| 09.10 00:05 | validation | Down · 137 s · 0,19 | Down · 77 s · 0,18 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 00:30 | validation | Up · 29 s · 0,33 | Up · 35 s · 0,26 | instant déplacé | +99 $ | +140 $ | +41 $ |
| 09.10 00:35 | validation | Down · 26 s · 0,14 | Down · 24 s · 0,20 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 00:45 | validation | Down · 128 s · 0,14 | Down · 87 s · 0,21 | instant déplacé | −30 $ | −53 $ | −23 $ |
| 09.10 00:50 | validation | — | Up · 93 s · 0,16 | B seul | +0 $ | +0 $ | +0 $ |
| 09.10 00:55 | validation | Up · 43 s · 0,26 | Up · 26 s · 0,26 | instant déplacé | +165 $ | +0 $ | −165 $ |
| 09.10 01:00 | validation | Down · 64 s · 0,23 | Down · 56 s · 0,28 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 01:05 | validation | Up · 57 s · 0,22 | Up · 56 s · 0,23 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 01:25 | validation | — | Up · 151 s · 0,05 | B seul | +0 $ | −53 $ | −53 $ |
| 09.10 01:30 | validation | Down · 113 s · 0,12 | Down · 60 s · 0,11 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 01:40 | validation | Down · 32 s · 0,29 | Down · 33 s · 0,29 | instant déplacé | +120 $ | +120 $ | +0 $ |
| 09.10 01:45 | validation | — | Up · 77 s · 0,16 | B seul | +0 $ | −38 $ | −38 $ |
| 09.10 01:50 | validation | Down · 160 s · 0,10 | Down · 108 s · 0,14 | instant déplacé | +126 $ | +304 $ | +178 $ |
| 09.10 02:00 | validation | Down · 173 s · 0,34 | Down · 161 s · 0,20 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 02:05 | validation | Down · 24 s · 0,26 | Down · 28 s · 0,28 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 09.10 02:15 | validation | Up · 167 s · 0,07 | Up · 93 s · 0,15 | instant déplacé | −12 $ | −28 $ | −16 $ |
| 09.10 02:35 | validation | Up · 65 s · 0,33 | — | B saute | −52 $ | +0 $ | +52 $ |
| 09.10 02:40 | validation | — | Down · 180 s · 0,06 | B seul | +0 $ | −19 $ | −19 $ |
| 09.10 02:45 | validation | Down · 192 s · 0,12 | Down · 195 s · 0,10 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 02:50 | validation | Down · 197 s · 0,25 | Up · 139 s · 0,15 | côté inversé | −53 $ | +280 $ | +333 $ |
| 09.10 03:00 | validation | Down · 153 s · 0,10 | Down · 152 s · 0,09 | instant déplacé | +258 $ | +502 $ | +244 $ |
| 09.10 03:30 | validation | Up · 50 s · 0,27 | Up · 60 s · 0,24 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 03:45 | validation | Up · 153 s · 0,05 | Up · 105 s · 0,11 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 03:50 | validation | Down · 146 s · 0,21 | Down · 146 s · 0,21 | instant déplacé | +185 $ | +185 $ | +0 $ |
| 09.10 03:55 | validation | Down · 79 s · 0,35 | Down · 81 s · 0,29 | instant déplacé | −52 $ | −53 $ | −0 $ |
| 09.10 04:00 | validation | Down · 88 s · 0,20 | Down · 88 s · 0,20 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 04:05 | validation | Down · 203 s · 0,03 | — | B saute | −13 $ | +0 $ | +13 $ |
| 09.10 04:15 | validation | Up · 171 s · 0,09 | Up · 143 s · 0,07 | instant déplacé | −3 $ | +0 $ | +3 $ |
| 09.10 04:20 | validation | Down · 57 s · 0,48 | Up · 258 s · 0,05 | côté inversé | +8 $ | −19 $ | −27 $ |
| 09.10 04:25 | validation | Up · 221 s · 0,06 | Up · 217 s · 0,09 | instant déplacé | −22 $ | −0 $ | +22 $ |
| 09.10 04:30 | validation | Down · 161 s · 0,17 | Down · 159 s · 0,17 | instant déplacé | −40 $ | −53 $ | −13 $ |
| 09.10 04:35 | validation | Down · 181 s · 0,16 | Down · 110 s · 0,16 | instant déplacé | −8 $ | +0 $ | +8 $ |
| 09.10 04:40 | validation | Down · 187 s · 0,11 | Down · 74 s · 0,20 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 04:55 | validation | Up · 54 s · 0,14 | Up · 62 s · 0,14 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 09.10 05:00 | validation | Up · 178 s · 0,22 | Up · 177 s · 0,25 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 05:10 | validation | Up · 147 s · 0,22 | Up · 102 s · 0,20 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 05:20 | validation | Down · 145 s · 0,08 | Down · 43 s · 0,24 | instant déplacé | −53 $ | −53 $ | +1 $ |
| 09.10 05:30 | validation | Up · 160 s · 0,12 | Up · 161 s · 0,12 | instant déplacé | −24 $ | −6 $ | +19 $ |
| 09.10 05:40 | validation | — | Down · 59 s · 0,15 | B seul | +0 $ | +0 $ | +0 $ |
| 09.10 05:45 | validation | Down · 107 s · 0,29 | Down · 107 s · 0,29 | instant déplacé | +120 $ | +120 $ | +0 $ |
| 09.10 05:55 | validation | Down · 102 s · 0,50 | Down · 111 s · 0,42 | instant déplacé | +0 $ | −52 $ | −52 $ |
| 09.10 06:05 | validation | Down · 155 s · 0,20 | Down · 150 s · 0,17 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 06:30 | validation | Down · 145 s · 0,21 | Down · 143 s · 0,21 | instant déplacé | −16 $ | −53 $ | −37 $ |
| 09.10 06:35 | validation | Down · 46 s · 0,24 | Down · 47 s · 0,26 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 09.10 06:45 | validation | Up · 141 s · 0,10 | Up · 129 s · 0,15 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 06:55 | validation | Down · 76 s · 0,07 | Down · 21 s · 0,18 | instant déplacé | −29 $ | −37 $ | −8 $ |
| 09.10 07:00 | validation | Up · 71 s · 0,25 | Up · 63 s · 0,27 | instant déplacé | +147 $ | +133 $ | −15 $ |
| 09.10 07:25 | validation | Down · 120 s · 0,14 | Down · 67 s · 0,16 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 07:35 | validation | Down · 110 s · 0,08 | Down · 129 s · 0,12 | instant déplacé | +525 $ | +363 $ | −162 $ |
| 09.10 07:40 | validation | Up · 62 s · 0,10 | Up · 4 s · 0,23 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 07:50 | validation | Down · 135 s · 0,28 | Down · 134 s · 0,28 | instant déplacé | +126 $ | +126 $ | +0 $ |
| 09.10 08:00 | validation | Up · 122 s · 0,38 | Up · 167 s · 0,38 | instant déplacé | +14 $ | +0 $ | −14 $ |
| 09.10 08:10 | validation | Down · 79 s · 0,19 | Down · 80 s · 0,19 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 08:25 | validation | Down · 44 s · 0,18 | — | B saute | −53 $ | +0 $ | +53 $ |
| 09.10 08:50 | validation | Up · 102 s · 0,15 | Up · 90 s · 0,18 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 09:00 | validation | Up · 117 s · 0,09 | Up · 88 s · 0,11 | instant déplacé | +0 $ | −34 $ | −34 $ |
| 09.10 09:15 | validation | Down · 48 s · 0,30 | Down · 24 s · 0,18 | instant déplacé | −27 $ | −42 $ | −15 $ |
| 09.10 09:20 | validation | Down · 171 s · 0,06 | Down · 169 s · 0,08 | instant déplacé | −2 $ | −20 $ | −18 $ |
| 09.10 09:25 | validation | Down · 58 s · 0,50 | — | B saute | +48 $ | +0 $ | −48 $ |
| 09.10 09:35 | validation | Up · 210 s · 0,18 | Up · 159 s · 0,15 | instant déplacé | +0 $ | −32 $ | −32 $ |
| 09.10 10:10 | validation | Up · 107 s · 0,23 | Up · 101 s · 0,26 | instant déplacé | +13 $ | +0 $ | −13 $ |
| 09.10 10:15 | validation | Up · 102 s · 0,17 | Up · 87 s · 0,13 | instant déplacé | −34 $ | +0 $ | +34 $ |
| 09.10 10:25 | validation | Down · 223 s · 0,11 | Down · 220 s · 0,12 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 09.10 10:30 | validation | Up · 190 s · 0,11 | Up · 181 s · 0,17 | instant déplacé | −38 $ | −46 $ | −8 $ |
| 09.10 10:40 | validation | Down · 151 s · 0,14 | Down · 151 s · 0,11 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 11:00 | validation | Up · 40 s · 0,18 | Up · 3 s · 0,25 | instant déplacé | −53 $ | −11 $ | +42 $ |
| 09.10 11:05 | validation | Up · 58 s · 0,29 | Up · 58 s · 0,28 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 11:25 | validation | Up · 7 s · 0,23 | Up · 5 s · 0,27 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 11:35 | validation | Down · 81 s · 0,27 | Down · 81 s · 0,27 | instant déplacé | +133 $ | +133 $ | +0 $ |
| 09.10 11:45 | validation | Down · 84 s · 0,22 | Down · 141 s · 0,13 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 11:50 | validation | Down · 80 s · 0,29 | Down · 81 s · 0,29 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 11:55 | validation | Up · 163 s · 0,28 | Up · 160 s · 0,23 | instant déplacé | +0 $ | −46 $ | −46 $ |
| 09.10 12:20 | validation | Up · 83 s · 0,23 | Up · 103 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 12:25 | validation | Down · 78 s · 0,17 | Down · 79 s · 0,17 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 12:35 | validation | Up · 52 s · 0,14 | Up · 22 s · 0,18 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 12:40 | validation | Up · 188 s · 0,12 | Up · 162 s · 0,11 | instant déplacé | −13 $ | −2 $ | +12 $ |
| 09.10 12:55 | validation | — | Down · 81 s · 0,11 | B seul | +0 $ | −19 $ | −19 $ |
| 09.10 13:00 | validation | Up · 188 s · 0,04 | Up · 158 s · 0,20 | instant déplacé | +0 $ | −22 $ | −22 $ |
| 09.10 13:05 | validation | Down · 119 s · 0,16 | Down · 111 s · 0,19 | instant déplacé | −29 $ | −35 $ | −5 $ |
| 09.10 13:15 | validation | Down · 140 s · 0,06 | Down · 98 s · 0,11 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 09.10 13:20 | validation | Up · 207 s · 0,05 | Up · 165 s · 0,05 | instant déplacé | −14 $ | +0 $ | +14 $ |
| 09.10 13:55 | validation | Up · 220 s · 0,10 | Up · 218 s · 0,11 | instant déplacé | −4 $ | +0 $ | +4 $ |
| 09.10 14:10 | validation | Up · 60 s · 0,40 | Up · 82 s · 0,29 | instant déplacé | −52 $ | +0 $ | +52 $ |
| 09.10 14:25 | validation | Up · 198 s · 0,05 | Up · 171 s · 0,11 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 14:35 | validation | Up · 79 s · 0,31 | Up · 121 s · 0,20 | instant déplacé | −52 $ | +0 $ | +52 $ |
| 09.10 14:45 | validation | Down · 223 s · 0,09 | Down · 152 s · 0,10 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 09.10 14:50 | validation | — | Up · 108 s · 0,11 | B seul | +0 $ | +0 $ | +0 $ |
| 09.10 14:55 | validation | Down · 211 s · 0,10 | Down · 211 s · 0,11 | instant déplacé | −52 $ | −53 $ | −1 $ |
| 09.10 15:00 | validation | Down · 163 s · 0,09 | Down · 164 s · 0,14 | instant déplacé | +0 $ | −1 $ | −1 $ |
| 09.10 15:10 | validation | Up · 196 s · 0,03 | Up · 94 s · 0,09 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 15:20 | validation | Down · 25 s · 0,42 | — | B saute | +2 $ | +0 $ | −2 $ |
| 09.10 15:45 | validation | — | Down · 242 s · 0,04 | B seul | +0 $ | −18 $ | −18 $ |
| 09.10 16:00 | validation | Down · 237 s · 0,10 | Down · 236 s · 0,11 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 16:30 | validation | Down · 201 s · 0,14 | Down · 200 s · 0,13 | instant déplacé | −23 $ | +0 $ | +23 $ |
| 09.10 16:45 | validation | Up · 175 s · 0,22 | — | B saute | +0 $ | +0 $ | +0 $ |
| 09.10 16:50 | validation | Down · 199 s · 0,04 | Down · 154 s · 0,10 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 09.10 16:55 | validation | — | Down · 225 s · 0,03 | B seul | +0 $ | −53 $ | −53 $ |
| 09.10 17:20 | validation | Up · 70 s · 0,20 | Up · 69 s · 0,20 | instant déplacé | +0 $ | −18 $ | −18 $ |
| 09.10 17:35 | validation | Down · 162 s · 0,26 | Down · 177 s · 0,31 | instant déplacé | −42 $ | −52 $ | −10 $ |
| 09.10 17:40 | validation | Up · 202 s · 0,06 | Up · 193 s · 0,18 | instant déplacé | −39 $ | −53 $ | −14 $ |
| 09.10 17:45 | validation | Down · 175 s · 0,31 | Down · 174 s · 0,31 | instant déplacé | +1 $ | +1 $ | +0 $ |
| 09.10 17:50 | validation | Down · 84 s · 0,16 | Down · 85 s · 0,16 | instant déplacé | +230 $ | +259 $ | +29 $ |
| 09.10 17:55 | validation | Down · 36 s · 0,11 | Down · 184 s · 0,11 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 18:00 | validation | Up · 161 s · 0,03 | Up · 157 s · 0,03 | instant déplacé | +0 $ | −49 $ | −49 $ |
| 09.10 18:15 | validation | Down · 150 s · 0,11 | Down · 152 s · 0,10 | instant déplacé | +254 $ | +98 $ | −156 $ |
| 09.10 18:30 | validation | Down · 221 s · 0,07 | Down · 189 s · 0,08 | instant déplacé | −19 $ | +0 $ | +19 $ |
| 09.10 18:35 | validation | Up · 200 s · 0,29 | Down · 106 s · 0,15 | côté inversé | −53 $ | +0 $ | +53 $ |
| 09.10 18:40 | validation | Up · 189 s · 0,20 | Up · 230 s · 0,31 | instant déplacé | −19 $ | −53 $ | −33 $ |
| 09.10 18:50 | validation | Down · 149 s · 0,13 | Down · 152 s · 0,12 | instant déplacé | +331 $ | +363 $ | +32 $ |
| 09.10 19:00 | validation | Up · 223 s · 0,16 | Down · 64 s · 0,17 | côté inversé | −21 $ | +241 $ | +262 $ |
| 09.10 19:05 | validation | Up · 183 s · 0,23 | Up · 185 s · 0,24 | instant déplacé | −3 $ | −53 $ | −50 $ |
| 09.10 19:10 | validation | Up · 42 s · 0,30 | Up · 71 s · 0,24 | instant déplacé | +0 $ | −10 $ | −10 $ |
| 09.10 19:15 | validation | Down · 216 s · 0,06 | Down · 247 s · 0,06 | instant déplacé | −53 $ | −3 $ | +50 $ |
| 09.10 19:20 | validation | Up · 214 s · 0,03 | Up · 186 s · 0,03 | instant déplacé | −24 $ | +0 $ | +24 $ |
| 09.10 19:25 | validation | — | Down · 60 s · 0,12 | B seul | +0 $ | −33 $ | −33 $ |
| 09.10 19:35 | validation | Down · 190 s · 0,14 | Down · 155 s · 0,10 | instant déplacé | −53 $ | −34 $ | +19 $ |
| 09.10 19:45 | validation | Up · 103 s · 0,16 | Up · 42 s · 0,12 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 19:55 | validation | Down · 193 s · 0,21 | Down · 208 s · 0,17 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 20:15 | validation | Up · 56 s · 0,22 | Up · 92 s · 0,15 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 20:25 | validation | Up · 193 s · 0,23 | Up · 112 s · 0,19 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 20:40 | validation | Down · 129 s · 0,21 | Down · 66 s · 0,18 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 20:50 | validation | Down · 33 s · 0,28 | Down · 45 s · 0,17 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 21:00 | validation | Down · 171 s · 0,11 | Down · 189 s · 0,25 | instant déplacé | −53 $ | −53 $ | +1 $ |
| 09.10 21:10 | validation | Down · 175 s · 0,26 | Down · 150 s · 0,27 | instant déplacé | −53 $ | −34 $ | +19 $ |
| 09.10 21:15 | validation | Up · 232 s · 0,15 | Up · 107 s · 0,18 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 21:20 | validation | Down · 147 s · 0,24 | Down · 154 s · 0,19 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 09.10 21:25 | validation | Up · 118 s · 0,12 | Up · 93 s · 0,20 | instant déplacé | −44 $ | −53 $ | −9 $ |
| 09.10 21:30 | validation | Up · 174 s · 0,23 | Up · 175 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 21:35 | validation | Up · 186 s · 0,06 | Up · 164 s · 0,12 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 21:40 | validation | Up · 169 s · 0,30 | Up · 170 s · 0,32 | instant déplacé | +0 $ | +70 $ | +70 $ |
| 09.10 21:50 | validation | Up · 119 s · 0,09 | Up · 101 s · 0,12 | instant déplacé | +0 $ | +360 $ | +360 $ |
| 09.10 21:55 | validation | Up · 239 s · 0,10 | Up · 182 s · 0,16 | instant déplacé | −16 $ | −9 $ | +8 $ |
| 09.10 22:00 | validation | Down · 164 s · 0,13 | Down · 91 s · 0,12 | instant déplacé | +331 $ | +31 $ | −301 $ |
| 09.10 22:10 | validation | Down · 57 s · 0,34 | Down · 74 s · 0,23 | instant déplacé | −52 $ | −53 $ | −0 $ |
| 09.10 22:20 | validation | Down · 137 s · 0,05 | Down · 55 s · 0,17 | instant déplacé | +0 $ | −5 $ | −5 $ |
| 09.10 22:30 | validation | Up · 121 s · 0,12 | Up · 171 s · 0,19 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 22:40 | validation | Down · 47 s · 0,31 | Down · 22 s · 0,28 | instant déplacé | +0 $ | +126 $ | +126 $ |
| 09.10 22:45 | validation | Down · 29 s · 0,27 | Down · 38 s · 0,21 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 09.10 23:00 | validation | Down · 171 s · 0,25 | Down · 173 s · 0,24 | instant déplacé | −46 $ | −14 $ | +31 $ |
| 09.10 23:10 | validation | Down · 166 s · 0,22 | Down · 161 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 09.10 23:15 | validation | Up · 190 s · 0,26 | Up · 194 s · 0,15 | instant déplacé | +0 $ | −1 $ | −1 $ |
| 09.10 23:20 | validation | Down · 69 s · 0,28 | Down · 72 s · 0,19 | instant déplacé | +126 $ | +210 $ | +84 $ |
| 09.10 23:35 | validation | Up · 195 s · 0,32 | Up · 206 s · 0,04 | instant déplacé | +0 $ | −4 $ | −4 $ |
| 10.10 00:00 | validation | Up · 94 s · 0,14 | Up · 89 s · 0,18 | instant déplacé | −53 $ | −31 $ | +22 $ |
| 10.10 00:05 | validation | Down · 110 s · 0,20 | Down · 67 s · 0,22 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 00:10 | validation | Up · 61 s · 0,22 | Up · 76 s · 0,22 | instant déplacé | −7 $ | −53 $ | −46 $ |
| 10.10 00:25 | validation | Up · 113 s · 0,22 | Up · 114 s · 0,22 | instant déplacé | −23 $ | −23 $ | +0 $ |
| 10.10 00:40 | validation | Down · 122 s · 0,23 | Down · 154 s · 0,27 | instant déplacé | +165 $ | +133 $ | −32 $ |
| 10.10 00:50 | validation | Down · 210 s · 0,28 | Down · 216 s · 0,19 | instant déplacé | −53 $ | −6 $ | +46 $ |
| 10.10 01:00 | validation | Up · 71 s · 0,22 | Up · 192 s · 0,19 | instant déplacé | +0 $ | −25 $ | −25 $ |
| 10.10 01:05 | validation | Down · 167 s · 0,28 | Down · 195 s · 0,26 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 01:20 | validation | Up · 60 s · 0,14 | Up · 28 s · 0,17 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 01:30 | validation | Down · 63 s · 0,25 | Down · 63 s · 0,22 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 01:35 | validation | Up · 91 s · 0,24 | Up · 94 s · 0,21 | instant déplacé | −28 $ | −53 $ | −24 $ |
| 10.10 01:40 | validation | Down · 123 s · 0,21 | Down · 124 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 01:45 | validation | Down · 28 s · 0,23 | Down · 28 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 02:05 | validation | Up · 84 s · 0,29 | Up · 90 s · 0,25 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 02:10 | validation | Down · 50 s · 0,18 | Down · 25 s · 0,22 | instant déplacé | −19 $ | −53 $ | −34 $ |
| 10.10 02:15 | validation | Up · 210 s · 0,21 | Up · 224 s · 0,15 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 02:25 | validation | Up · 26 s · 0,14 | Up · 27 s · 0,15 | instant déplacé | +165 $ | +0 $ | −165 $ |
| 10.10 02:30 | validation | Up · 66 s · 0,19 | Up · 62 s · 0,22 | instant déplacé | +0 $ | −37 $ | −37 $ |
| 10.10 02:40 | validation | Up · 19 s · 0,27 | Up · 22 s · 0,24 | instant déplacé | −8 $ | −53 $ | −44 $ |
| 10.10 02:45 | validation | Up · 124 s · 0,29 | Up · 176 s · 0,27 | instant déplacé | +120 $ | +32 $ | −88 $ |
| 10.10 02:50 | validation | Down · 126 s · 0,25 | Down · 127 s · 0,24 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 02:55 | validation | Up · 81 s · 0,27 | Up · 127 s · 0,14 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 03:00 | validation | Up · 122 s · 0,23 | Up · 127 s · 0,20 | instant déplacé | +165 $ | +197 $ | +33 $ |
| 10.10 03:05 | validation | Down · 214 s · 0,28 | Down · 232 s · 0,18 | instant déplacé | −53 $ | −3 $ | +50 $ |
| 10.10 03:20 | validation | Up · 41 s · 0,21 | Up · 26 s · 0,19 | instant déplacé | −53 $ | −26 $ | +27 $ |
| 10.10 03:25 | validation | Down · 74 s · 0,12 | Down · 56 s · 0,23 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 03:30 | validation | Up · 91 s · 0,17 | Up · 60 s · 0,23 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 03:35 | validation | Down · 135 s · 0,28 | Down · 149 s · 0,16 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 03:40 | validation | Down · 121 s · 0,14 | Down · 123 s · 0,10 | instant déplacé | −46 $ | −14 $ | +31 $ |
| 10.10 03:45 | validation | Down · 57 s · 0,17 | Down · 54 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 04:00 | validation | Up · 67 s · 0,21 | Up · 66 s · 0,21 | instant déplacé | +181 $ | +197 $ | +16 $ |
| 10.10 04:05 | validation | Up · 170 s · 0,26 | Up · 36 s · 0,17 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 04:10 | validation | Down · 99 s · 0,05 | Down · 18 s · 0,21 | instant déplacé | +28 $ | +185 $ | +157 $ |
| 10.10 04:15 | validation | Up · 86 s · 0,26 | Up · 166 s · 0,16 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 04:20 | validation | Up · 88 s · 0,16 | Up · 90 s · 0,13 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 04:25 | validation | Up · 178 s · 0,28 | Up · 178 s · 0,28 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 04:30 | validation | Down · 163 s · 0,29 | Down · 190 s · 0,26 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 04:35 | validation | Down · 44 s · 0,23 | Down · 43 s · 0,26 | instant déplacé | −53 $ | −24 $ | +29 $ |
| 10.10 04:40 | validation | Up · 41 s · 0,17 | Up · 38 s · 0,24 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 04:45 | validation | Up · 183 s · 0,18 | Up · 33 s · 0,22 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 04:50 | validation | Down · 20 s · 0,25 | Down · 51 s · 0,18 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 04:55 | validation | Down · 23 s · 0,30 | Down · 162 s · 0,15 | instant déplacé | +114 $ | +280 $ | +166 $ |
| 10.10 05:00 | validation | Up · 84 s · 0,21 | Up · 50 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 05:10 | validation | Up · 180 s · 0,11 | Up · 182 s · 0,15 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 05:15 | validation | Up · 110 s · 0,26 | Up · 145 s · 0,24 | instant déplacé | −53 $ | −3 $ | +50 $ |
| 10.10 05:30 | validation | Up · 243 s · 0,29 | Up · 245 s · 0,26 | instant déplacé | −14 $ | −53 $ | −39 $ |
| 10.10 05:55 | validation | Down · 100 s · 0,24 | Down · 103 s · 0,23 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 06:25 | validation | Down · 33 s · 0,26 | Down · 5 s · 0,27 | instant déplacé | −29 $ | −3 $ | +26 $ |
| 10.10 06:30 | validation | Up · 16 s · 0,20 | Up · 14 s · 0,20 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 06:35 | validation | Down · 68 s · 0,21 | Down · 71 s · 0,16 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 06:40 | validation | Down · 47 s · 0,24 | Down · 42 s · 0,25 | instant déplacé | −53 $ | −47 $ | +6 $ |
| 10.10 06:55 | validation | Up · 92 s · 0,16 | Up · 93 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 07:05 | validation | Up · 6 s · 0,26 | Up · 6 s · 0,26 | instant déplacé | +140 $ | +140 $ | +0 $ |
| 10.10 07:10 | validation | Down · 82 s · 0,14 | Down · 83 s · 0,13 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 07:20 | validation | Up · 191 s · 0,30 | Up · 206 s · 0,26 | instant déplacé | −53 $ | −29 $ | +24 $ |
| 10.10 07:25 | validation | Down · 20 s · 0,22 | Up · 122 s · 0,27 | côté inversé | +174 $ | −53 $ | −227 $ |
| 10.10 07:30 | validation | Down · 51 s · 0,23 | Down · 61 s · 0,08 | instant déplacé | −53 $ | −53 $ | −1 $ |
| 10.10 07:35 | validation | Up · 12 s · 0,28 | Up · 40 s · 0,21 | instant déplacé | +126 $ | +35 $ | −91 $ |
| 10.10 07:45 | validation | Up · 5 s · 0,19 | Up · 53 s · 0,23 | instant déplacé | +0 $ | −6 $ | −6 $ |
| 10.10 07:50 | validation | Down · 239 s · 0,27 | Down · 240 s · 0,28 | instant déplacé | +0 $ | −22 $ | −22 $ |
| 10.10 08:05 | validation | Up · 89 s · 0,15 | Up · 7 s · 0,13 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 08:15 | validation | Up · 62 s · 0,27 | Down · 184 s · 0,14 | côté inversé | +133 $ | −3 $ | −135 $ |
| 10.10 08:20 | validation | Up · 38 s · 0,14 | Up · 8 s · 0,22 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 08:30 | validation | Up · 43 s · 0,18 | Up · 27 s · 0,23 | instant déplacé | −2 $ | −53 $ | −51 $ |
| 10.10 08:35 | validation | Down · 144 s · 0,14 | Down · 194 s · 0,10 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 08:40 | validation | Down · 64 s · 0,26 | Down · 90 s · 0,10 | instant déplacé | −53 $ | −53 $ | −1 $ |
| 10.10 09:00 | validation | Down · 46 s · 0,18 | Down · 17 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 09:05 | validation | Up · 86 s · 0,25 | Up · 87 s · 0,25 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 09:20 | validation | Up · 52 s · 0,21 | Up · 40 s · 0,21 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 09:25 | validation | Up · 146 s · 0,27 | Up · 148 s · 0,27 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 09:30 | validation | Down · 195 s · 0,26 | Down · 196 s · 0,26 | instant déplacé | −53 $ | −1 $ | +51 $ |
| 10.10 09:35 | validation | Down · 8 s · 0,14 | Down · 6 s · 0,13 | instant déplacé | −53 $ | −18 $ | +35 $ |
| 10.10 09:40 | validation | Down · 107 s · 0,21 | Down · 122 s · 0,19 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 09:45 | validation | Down · 126 s · 0,23 | Down · 141 s · 0,21 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 10:35 | test | Up · 222 s · 0,29 | Up · 234 s · 0,29 | instant déplacé | +11 $ | +0 $ | −11 $ |
| 10.10 10:45 | test | Up · 54 s · 0,21 | Up · 54 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 11:05 | test | Down · 146 s · 0,29 | Down · 175 s · 0,09 | instant déplacé | −53 $ | −14 $ | +39 $ |
| 10.10 11:10 | test | Down · 24 s · 0,31 | Down · 25 s · 0,26 | instant déplacé | −52 $ | +0 $ | +52 $ |
| 10.10 11:15 | test | Up · 27 s · 0,22 | Up · 28 s · 0,19 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 11:30 | test | Down · 76 s · 0,21 | Down · 82 s · 0,17 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 11:50 | test | Up · 27 s · 0,24 | Up · 28 s · 0,24 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 11:55 | test | Down · 118 s · 0,26 | Down · 133 s · 0,23 | instant déplacé | −31 $ | −2 $ | +28 $ |
| 10.10 12:15 | test | Down · 109 s · 0,28 | Down · 110 s · 0,27 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 12:20 | test | Up · 90 s · 0,29 | Up · 144 s · 0,13 | instant déplacé | −53 $ | −1 $ | +52 $ |
| 10.10 12:25 | test | Up · 34 s · 0,32 | Up · 93 s · 0,24 | instant déplacé | +0 $ | −28 $ | −28 $ |
| 10.10 12:30 | test | Up · 126 s · 0,27 | Up · 131 s · 0,26 | instant déplacé | +61 $ | +140 $ | +79 $ |
| 10.10 12:35 | test | Down · 18 s · 0,21 | Down · 19 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 12:50 | test | Down · 63 s · 0,16 | Down · 66 s · 0,16 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 13:00 | test | Up · 51 s · 0,27 | Up · 63 s · 0,17 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 13:05 | test | Up · 155 s · 0,27 | Up · 162 s · 0,25 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 13:10 | test | Up · 40 s · 0,29 | Up · 46 s · 0,29 | instant déplacé | −11 $ | −35 $ | −24 $ |
| 10.10 13:15 | test | Up · 145 s · 0,27 | Up · 147 s · 0,27 | instant déplacé | −17 $ | −53 $ | −36 $ |
| 10.10 13:20 | test | Down · 45 s · 0,21 | Down · 60 s · 0,21 | instant déplacé | −4 $ | −53 $ | −48 $ |
| 10.10 13:25 | test | Down · 58 s · 0,20 | Up · 155 s · 0,29 | côté inversé | −53 $ | +58 $ | +111 $ |
| 10.10 13:30 | test | Down · 201 s · 0,29 | Down · 212 s · 0,26 | instant déplacé | +0 $ | +140 $ | +140 $ |
| 10.10 13:40 | test | Down · 7 s · 0,21 | Down · 46 s · 0,18 | instant déplacé | −53 $ | −16 $ | +37 $ |
| 10.10 13:45 | test | Up · 84 s · 0,24 | Up · 211 s · 0,28 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 13:50 | test | Down · 208 s · 0,27 | Down · 232 s · 0,18 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 14:00 | test | Up · 42 s · 0,26 | Up · 50 s · 0,24 | instant déplacé | −53 $ | −25 $ | +27 $ |
| 10.10 14:15 | test | Up · 112 s · 0,35 | Up · 129 s · 0,28 | instant déplacé | −52 $ | +0 $ | +52 $ |
| 10.10 14:30 | test | Down · 18 s · 0,15 | Down · 35 s · 0,15 | instant déplacé | −23 $ | −53 $ | −30 $ |
| 10.10 14:35 | test | Up · 61 s · 0,29 | Up · 99 s · 0,14 | instant déplacé | +0 $ | −14 $ | −14 $ |
| 10.10 14:50 | test | Up · 80 s · 0,29 | Up · 101 s · 0,26 | instant déplacé | −5 $ | +0 $ | +5 $ |
| 10.10 14:55 | test | Up · 30 s · 0,24 | Up · 49 s · 0,20 | instant déplacé | −4 $ | −53 $ | −49 $ |
| 10.10 15:05 | test | Up · 50 s · 0,24 | Up · 179 s · 0,08 | instant déplacé | −53 $ | −53 $ | −1 $ |
| 10.10 15:15 | test | Up · 33 s · 0,25 | Up · 34 s · 0,25 | instant déplacé | +15 $ | +147 $ | +133 $ |
| 10.10 15:25 | test | Up · 4 s · 0,23 | Up · 5 s · 0,22 | instant déplacé | +174 $ | +174 $ | +0 $ |
| 10.10 15:35 | test | Up · 38 s · 0,17 | Up · 5 s · 0,26 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 15:40 | test | Up · 104 s · 0,15 | Up · 107 s · 0,14 | instant déplacé | −53 $ | −13 $ | +40 $ |
| 10.10 15:50 | test | Down · 4 s · 0,27 | Down · 13 s · 0,38 | instant déplacé | +18 $ | +79 $ | +61 $ |
| 10.10 16:10 | test | Down · 77 s · 0,29 | Down · 81 s · 0,28 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 16:15 | test | Down · 45 s · 0,30 | Down · 47 s · 0,30 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 16:20 | test | Up · 66 s · 0,20 | Up · 64 s · 0,21 | instant déplacé | +197 $ | +185 $ | −12 $ |
| 10.10 16:30 | test | Up · 44 s · 0,20 | Up · 43 s · 0,21 | instant déplacé | +197 $ | +185 $ | −12 $ |
| 10.10 16:35 | test | Down · 108 s · 0,17 | Down · 124 s · 0,10 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 16:40 | test | Up · 175 s · 0,23 | Up · 175 s · 0,23 | instant déplacé | −5 $ | −5 $ | −0 $ |
| 10.10 16:45 | test | Down · 122 s · 0,18 | Down · 76 s · 0,22 | instant déplacé | +0 $ | +174 $ | +174 $ |
| 10.10 16:50 | test | Down · 191 s · 0,26 | Down · 192 s · 0,25 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 17:20 | test | Up · 70 s · 0,15 | Up · 69 s · 0,16 | instant déplacé | −21 $ | −53 $ | −32 $ |
| 10.10 17:25 | test | Down · 112 s · 0,23 | Down · 112 s · 0,23 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 18:05 | test | Up · 58 s · 0,08 | Up · 7 s · 0,15 | instant déplacé | +0 $ | −23 $ | −23 $ |
| 10.10 18:10 | test | Down · 82 s · 0,21 | Down · 41 s · 0,23 | instant déplacé | −10 $ | −53 $ | −43 $ |
| 10.10 18:25 | test | Up · 195 s · 0,26 | Up · 196 s · 0,25 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 18:30 | test | Down · 140 s · 0,28 | Down · 141 s · 0,28 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 18:40 | test | Down · 42 s · 0,17 | Down · 43 s · 0,17 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 18:45 | test | Up · 77 s · 0,21 | Up · 55 s · 0,27 | instant déplacé | −1 $ | −53 $ | −52 $ |
| 10.10 19:00 | test | Down · 145 s · 0,17 | Down · 149 s · 0,17 | instant déplacé | +0 $ | −29 $ | −29 $ |
| 10.10 19:15 | test | Down · 106 s · 0,30 | Down · 114 s · 0,19 | instant déplacé | +114 $ | +204 $ | +90 $ |
| 10.10 19:40 | test | Up · 131 s · 0,21 | Up · 108 s · 0,23 | instant déplacé | +18 $ | +0 $ | −18 $ |
| 10.10 19:50 | test | Up · 21 s · 0,23 | Up · 100 s · 0,24 | instant déplacé | −11 $ | −3 $ | +9 $ |
| 10.10 19:55 | test | Down · 31 s · 0,36 | Up · 42 s · 0,18 | côté inversé | +0 $ | −53 $ | −53 $ |
| 10.10 20:05 | test | Down · 64 s · 0,14 | Down · 7 s · 0,22 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 20:10 | test | Up · 75 s · 0,19 | Up · 76 s · 0,17 | instant déplacé | −40 $ | −53 $ | −13 $ |
| 10.10 20:25 | test | Up · 113 s · 0,12 | Up · 24 s · 0,18 | instant déplacé | −53 $ | −3 $ | +50 $ |
| 10.10 20:30 | test | Down · 43 s · 0,21 | Down · 65 s · 0,13 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 20:35 | test | Up · 69 s · 0,13 | Up · 28 s · 0,17 | instant déplacé | −27 $ | −11 $ | +16 $ |
| 10.10 20:40 | test | Down · 56 s · 0,23 | Down · 57 s · 0,20 | instant déplacé | +0 $ | −35 $ | −35 $ |
| 10.10 20:45 | test | Down · 101 s · 0,24 | — | B saute | −53 $ | +0 $ | +53 $ |
| 10.10 20:55 | test | Up · 41 s · 0,18 | Up · 37 s · 0,21 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 21:10 | test | Down · 35 s · 0,26 | Down · 33 s · 0,27 | instant déplacé | +140 $ | +133 $ | −7 $ |
| 10.10 21:15 | test | Down · 35 s · 0,28 | Down · 58 s · 0,29 | instant déplacé | −43 $ | −53 $ | −10 $ |
| 10.10 21:20 | test | Down · 28 s · 0,28 | Down · 37 s · 0,26 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 21:25 | test | Down · 70 s · 0,29 | Down · 162 s · 0,18 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 21:45 | test | Down · 86 s · 0,27 | Down · 209 s · 0,13 | instant déplacé | −53 $ | −1 $ | +52 $ |
| 10.10 21:50 | test | Up · 155 s · 0,16 | Up · 158 s · 0,11 | instant déplacé | −11 $ | +0 $ | +11 $ |
| 10.10 21:55 | test | Down · 12 s · 0,16 | Down · 31 s · 0,11 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 10.10 22:00 | test | Down · 80 s · 0,27 | Down · 106 s · 0,28 | instant déplacé | −16 $ | −53 $ | −37 $ |
| 10.10 22:05 | test | Up · 19 s · 0,21 | Up · 51 s · 0,23 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 22:10 | test | Up · 43 s · 0,17 | Up · 46 s · 0,09 | instant déplacé | −53 $ | −2 $ | +51 $ |
| 10.10 22:15 | test | Up · 88 s · 0,30 | Up · 92 s · 0,20 | instant déplacé | +114 $ | +27 $ | −87 $ |
| 10.10 22:20 | test | Up · 155 s · 0,29 | Up · 31 s · 0,25 | instant déplacé | −53 $ | −13 $ | +39 $ |
| 10.10 22:35 | test | Down · 99 s · 0,28 | Down · 101 s · 0,28 | instant déplacé | −15 $ | −53 $ | −38 $ |
| 10.10 22:45 | test | Down · 10 s · 0,30 | Down · 63 s · 0,25 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 10.10 22:50 | test | Down · 180 s · 0,27 | Down · 238 s · 0,05 | instant déplacé | −53 $ | −13 $ | +40 $ |
| 10.10 22:55 | test | Down · 6 s · 0,27 | Down · 7 s · 0,27 | instant déplacé | +102 $ | +133 $ | +30 $ |
| 10.10 23:05 | test | Down · 6 s · 0,25 | Down · 7 s · 0,25 | instant déplacé | +147 $ | +147 $ | +0 $ |
| 10.10 23:10 | test | Down · 45 s · 0,36 | Down · 77 s · 0,35 | instant déplacé | +10 $ | +91 $ | +81 $ |
| 10.10 23:20 | test | Down · 194 s · 0,33 | Down · 196 s · 0,32 | instant déplacé | +0 $ | −52 $ | −52 $ |
| 10.10 23:25 | test | Up · 50 s · 0,29 | Up · 60 s · 0,29 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 10.10 23:30 | test | Down · 17 s · 0,21 | Down · 45 s · 0,16 | instant déplacé | −53 $ | −8 $ | +45 $ |
| 10.10 23:35 | test | Down · 12 s · 0,30 | Down · 114 s · 0,26 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 10.10 23:45 | test | Down · 41 s · 0,21 | Down · 43 s · 0,19 | instant déplacé | −28 $ | −53 $ | −25 $ |
| 10.10 23:55 | test | Down · 49 s · 0,28 | Down · 50 s · 0,27 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 00:00 | test | Up · 127 s · 0,33 | Up · 199 s · 0,23 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 00:10 | test | Down · 112 s · 0,26 | Down · 113 s · 0,26 | instant déplacé | +140 $ | +140 $ | +0 $ |
| 11.10 00:20 | test | Up · 71 s · 0,19 | Up · 81 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 00:25 | test | Down · 38 s · 0,26 | Down · 46 s · 0,26 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 00:30 | test | Down · 152 s · 0,33 | Down · 180 s · 0,27 | instant déplacé | −52 $ | −53 $ | −0 $ |
| 11.10 00:35 | test | Up · 28 s · 0,27 | Down · 57 s · 0,24 | côté inversé | +0 $ | +0 $ | +0 $ |
| 11.10 00:50 | test | Down · 58 s · 0,12 | Down · 57 s · 0,21 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 00:55 | test | Down · 151 s · 0,24 | — | B saute | −18 $ | +0 $ | +18 $ |
| 11.10 01:05 | test | Up · 109 s · 0,25 | Up · 122 s · 0,06 | instant déplacé | −53 $ | −1 $ | +52 $ |
| 11.10 01:10 | test | Down · 31 s · 0,29 | Down · 73 s · 0,27 | instant déplacé | +120 $ | +29 $ | −91 $ |
| 11.10 01:20 | test | Up · 124 s · 0,28 | Up · 142 s · 0,20 | instant déplacé | −53 $ | −3 $ | +50 $ |
| 11.10 01:25 | test | Down · 98 s · 0,19 | Down · 99 s · 0,28 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 11.10 01:30 | test | Down · 31 s · 0,21 | Down · 21 s · 0,22 | instant déplacé | −46 $ | −53 $ | −7 $ |
| 11.10 01:35 | test | Up · 39 s · 0,29 | Up · 134 s · 0,21 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 11.10 01:40 | test | Up · 18 s · 0,21 | Up · 69 s · 0,24 | instant déplacé | +0 $ | −6 $ | −6 $ |
| 11.10 01:45 | test | Up · 27 s · 0,24 | Up · 23 s · 0,27 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 01:50 | test | Down · 156 s · 0,28 | Down · 157 s · 0,24 | instant déplacé | −53 $ | +0 $ | +53 $ |
| 11.10 01:55 | test | Up · 216 s · 0,11 | Up · 236 s · 0,11 | instant déplacé | −1 $ | −8 $ | −7 $ |
| 11.10 02:15 | test | Up · 42 s · 0,28 | Up · 43 s · 0,28 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 02:20 | test | Up · 127 s · 0,30 | Up · 169 s · 0,23 | instant déplacé | −53 $ | −13 $ | +39 $ |
| 11.10 02:25 | test | Up · 95 s · 0,22 | Up · 124 s · 0,13 | instant déplacé | −25 $ | −26 $ | −1 $ |
| 11.10 02:30 | test | Up · 72 s · 0,28 | Up · 88 s · 0,26 | instant déplacé | +0 $ | +62 $ | +62 $ |
| 11.10 02:35 | test | Down · 27 s · 0,25 | Down · 29 s · 0,26 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 02:40 | test | Up · 126 s · 0,20 | Up · 128 s · 0,16 | instant déplacé | −1 $ | −11 $ | −10 $ |
| 11.10 02:50 | test | Down · 102 s · 0,28 | Up · 150 s · 0,11 | côté inversé | +0 $ | −53 $ | −53 $ |
| 11.10 03:10 | test | Up · 89 s · 0,29 | Up · 91 s · 0,21 | instant déplacé | +27 $ | +23 $ | −4 $ |
| 11.10 03:15 | test | Down · 11 s · 0,21 | Down · 12 s · 0,23 | instant déplacé | +0 $ | −13 $ | −13 $ |
| 11.10 03:20 | test | Up · 85 s · 0,19 | Up · 88 s · 0,19 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 03:25 | test | Up · 67 s · 0,29 | — | B saute | +19 $ | +0 $ | −19 $ |
| 11.10 03:30 | test | Down · 6 s · 0,23 | Down · 14 s · 0,24 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 03:35 | test | Down · 116 s · 0,31 | Down · 120 s · 0,20 | instant déplacé | −35 $ | −16 $ | +19 $ |
| 11.10 03:50 | test | Down · 120 s · 0,32 | Down · 122 s · 0,31 | instant déplacé | +109 $ | +109 $ | +0 $ |
| 11.10 03:55 | test | Up · 10 s · 0,24 | Up · 10 s · 0,24 | instant déplacé | +41 $ | +0 $ | −41 $ |
| 11.10 04:00 | test | Down · 15 s · 0,34 | Up · 17 s · 0,18 | côté inversé | +0 $ | −45 $ | −45 $ |
| 11.10 04:15 | test | Down · 137 s · 0,28 | Down · 138 s · 0,27 | instant déplacé | +126 $ | +23 $ | −103 $ |
| 11.10 04:20 | test | Down · 28 s · 0,27 | Down · 50 s · 0,22 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 04:25 | test | Up · 38 s · 0,30 | Up · 72 s · 0,23 | instant déplacé | −53 $ | −53 $ | −0 $ |
| 11.10 04:30 | test | Down · 35 s · 0,25 | Down · 42 s · 0,25 | instant déplacé | +0 $ | −24 $ | −24 $ |
| 11.10 04:45 | test | Up · 14 s · 0,18 | Up · 10 s · 0,21 | instant déplacé | −6 $ | −53 $ | −47 $ |
| 11.10 05:00 | test | Up · 22 s · 0,27 | Up · 152 s · 0,05 | instant déplacé | −53 $ | −13 $ | +40 $ |
| 11.10 05:05 | test | Up · 35 s · 0,20 | Up · 38 s · 0,20 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 05:15 | test | Down · 128 s · 0,32 | Up · 153 s · 0,27 | côté inversé | +104 $ | −53 $ | −156 $ |
| 11.10 05:25 | test | Down · 25 s · 0,17 | Down · 20 s · 0,22 | instant déplacé | −23 $ | −53 $ | −29 $ |
| 11.10 05:40 | test | Up · 25 s · 0,19 | Up · 6 s · 0,19 | instant déplacé | −53 $ | −1 $ | +52 $ |
| 11.10 06:00 | test | Up · 75 s · 0,13 | Up · 16 s · 0,11 | instant déplacé | +363 $ | +44 $ | −319 $ |
| 11.10 06:05 | test | Down · 27 s · 0,26 | Down · 37 s · 0,22 | instant déplacé | +140 $ | +15 $ | −124 $ |
| 11.10 06:25 | test | Down · 52 s · 0,23 | Down · 59 s · 0,21 | instant déplacé | +0 $ | −11 $ | −11 $ |
| 11.10 06:35 | test | Down · 76 s · 0,25 | Down · 76 s · 0,25 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 06:45 | test | Down · 31 s · 0,26 | Down · 113 s · 0,29 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 06:55 | test | Up · 21 s · 0,28 | Up · 28 s · 0,19 | instant déplacé | +0 $ | +0 $ | +0 $ |
| 11.10 07:15 | test | Down · 42 s · 0,29 | Down · 84 s · 0,27 | instant déplacé | +0 $ | −53 $ | −53 $ |
| 11.10 07:20 | test | Up · 6 s · 0,12 | Up · 88 s · 0,13 | instant déplacé | −53 $ | −53 $ | +0 $ |
| 11.10 07:30 | test | Up · 55 s · 0,24 | Down · 114 s · 0,21 | côté inversé | +30 $ | −53 $ | −83 $ |
| 11.10 07:35 | test | Up · 59 s · 0,21 | Up · 60 s · 0,18 | instant déplacé | −45 $ | +0 $ | +45 $ |
| 11.10 07:40 | test | Up · 113 s · 0,30 | Up · 195 s · 0,26 | instant déplacé | +114 $ | +12 $ | −102 $ |
| 11.10 07:45 | test | Up · 44 s · 0,27 | Up · 169 s · 0,06 | instant déplacé | +0 $ | −6 $ | −6 $ |

Total des divergences : instant déplacé 532 (−950 $) ; B seul 35 (−666 $) ; côté inversé 25 (−190 $) ; B saute 14 (+226 $).

## Conclusion chiffrée et classement

| Constat | Classement |
|---|---|
| Fuite de 0 à 0,999 s dans `meta_router.parts_r` (X8/X1/H1, cohorte B) | **correction technique prouvée** (à corriger dans les études ; impact faible, section G) |
| K = prix du site jusqu'au 09.10 19:20 | **correction technique prouvée, déjà en place** (F) |
| (1) σ et écart perp → Chainlink en cache 5 s | σ sans cache : résultat négatif (aucun gain démontré) ; écarts sans cache : résultat négatif (aucun gain démontré) |
| (2) série remplie → σ sous-estimée | σ « secondes changées » : résultat négatif (IC entièrement négatif sur une période) ; la variance par unité de temps n'est pas biaisée par le remplissage si le rattrapage est dans la fenêtre |
| (3) prix rapide = source reçue la plus récente | exclusion > 1 s sur l'indicateur : résultat négatif (aucun gain démontré) ; âges vrais : hypothèse prometteuse, **données insuffisantes** (14 trades) |
| (4) pondération des secondes Chainlink manquantes dans E | moyenne remplie plus proche de l'officiel dans 71 % des cycles → **hypothèse prometteuse** (correction possible : remplir les secondes manquantes) |
| (5) K avec 40-59 secondes | 40-59 s : erreur médiane ≈ 0,1 $ → **résultat négatif** ; < 40 s : 6,51 $ → **hypothèse prometteuse** |
| (6) prixA 6 s de recul / gel Chainlink ≤ 1 s | |ΔP| ≤ 0,0001 → **résultat négatif** (Chainlink n'entre que par des moyennes) |
| Gel Bybit / OKX (C) | fragilité 8-40 % des signaux déplacés, ΔP&L de signe instable → **résultat négatif** (pas de sensibilité systématique) |
| Rattrapage de flux avant le signal (D) | **hypothèse prometteuse** (indicateur) |
| Frankenstein (E) | indicateur : perdants plus dispersés (p = 0,013) ; âges vrais : l'inverse → **données insuffisantes** |
| Rejet par le marché H186/H187 (H) | **résultat négatif** |
| Conservation des probabilités / carnets (I) | rien à corriger |
| Part des faux désaccords potentiellement temporelle | démontrée ≈ 0 % ; borne haute ≈ 13 % ; inexpliqué ≥ 87 % |

Détail des drapeaux (désaccords ≥ 0,30 du rejeu, probabilité enregistrée) :

| Drapeau | Perdants | Gagnants |
|---|---|---|
| source du prix rapide > 1 s (indicateur) | 22 % | 17 % |
| politique F8 : plus de signal (écart < 0,20 ou pas de décision) | 22 % | 18 % |
| erreur de K > 2 $ en faveur de notre côté | 34 % | 44 % |
| rattrapage de flux dans les 3 s | 12 % | 19 % |
| au moins un des drapeaux | 58 % | 69 % |

Mêmes drapeaux sur les trades RÉELS V2-F couverts par les lignes (463 perdants, 127 gagnants) :

| Drapeau | Perdants | Gagnants |
|---|---|---|
| source du prix rapide > 1 s (indicateur) | 23 % | 23 % |
| politique F8 : plus de signal (écart < 0,20 ou pas de décision) | 74 % | 80 % |
| erreur de K > 2 $ en faveur de notre côté | 24 % | 28 % |
| rattrapage de flux dans les 3 s | 11 % | 9 % |
| au moins un des drapeaux | 84 % | 91 % |

### Ce que l'enregistreur de Dublin permettra de vérifier

- **Âge vrai de chaque source à chaque instant** (dernier prix + horodatage de la SOURCE toutes les 50 ms) : remplace l'indicateur « dernier changement », qui confond un marché calme et un flux coupé ; permet de rejouer F8 exactement et de séparer latence réseau et avance réelle.
- **Carnet Polymarket avec horodatages Polymarket** : mesurer si le carnet a bougé AVANT notre flux (le vrai test de H186/H187 et du rattrapage, section D), à 50 ms au lieu de 0,3 s ; rendre exact le +100 ms de la section C.
- **Transactions** : savoir si une offre a disparu par exécution (quelqu'un l'a prise) ou par retrait (le teneur de marché a reculé) — la cause des « offres disparues ».
- **Limite actuelle** : branche `donnees-rapide` avec très peu de cycles : aucune conclusion statistique possible avant plusieurs centaines de cycles.
