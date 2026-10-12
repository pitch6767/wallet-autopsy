# Bot95 — Audit de la nuit du 9 au 10 octobre 2026

Toutes les décisions ont été reconstruites seconde par seconde à partir des données enregistrées par le bot : carnet 4 fois par seconde, perp Bybit, OKX et Chainlink. Elles sont comparées aux valeurs officielles publiées par Polymarket.

Aucune stratégie n'a été modifiée.

## En bref

1. **Aucune erreur de règlement.** Le prix à battre du bot est juste à 0,08 $ près dans tous les cycles audités. Le côté acheté, la fenêtre de 60 s et les horodatages sont corrects. Le moteur hors ligne retrouve les mêmes probabilités que le bot, sauf pendant les sauts décrits au point 2.
2. **Les deux anomalies extrêmes ont la même cause : un saut de prix d'une seule seconde sur les exchanges.** Le moteur prolonge ce prix sur toute la fin de la fenêtre, alors que Chainlink ne bouge presque pas.
3. **Le seuil de 0,20 est respecté.** Le « prix payé » enregistré inclut les frais, d'où les écarts apparents un peu sous 20 points.
4. **« Confirmé Chainlink » ne fait pas ce qu'on voulait.** Dans 9 achats sur 11, la « confirmation » arrive moins de 0,2 s après le signal, ce qui équivaut à un achat immédiat. Le flux Chainlink livre souvent ses messages par paquets. Ce n'est pas la règle testée sur l'historique, qui attendait un vrai changement de valeur, environ 0,5 à 1 s plus tard.
5. **Les 11 pertes de suite :** selon les prix payés, il fallait s'attendre à 3 gagnants. Avoir 0 gagnant arrive environ 2 fois sur 100. C'est une très mauvaise série, aggravée par un moteur trop confiant cette nuit-là.
6. **Cette nuit, le carnet a mieux prévu que notre moteur.** Sur TWAP fin original, notre moteur annonçait 14,6 gagnants, le prix du marché 7,6, et il y en a eu 6. Les rejeux hors ligne retrouvent la même perte : ce n'est pas un bug, c'est le modèle qui se trompait dans ce régime calme.
7. **La seule variante TWAP positive cette nuit est « correction spot-perp »** : +47 $, 10 gagnants sur 18. Elle a évité les deux pièges, parce que Binance et Coinbase n'avaient pas confirmé les sauts.

## 1. Anomalie de 05:19:11 — Up acheté à 0,032 $ avec 99,5 %

**Cycle :** 05:15 → 05:20. Le prix à battre du bot est de 82 510,99, contre 82 510,91 officiel.

| Heure | Perp Bybit | OKX | Chainlink |
|---|---|---|---|
| 05:19:05 → 05:19:10 | 82 531,9 (immobile) | 82 545,1 (immobile) | 82 503,8 |
| **05:19:11** | **82 544,6 (+12,7 $ en 1 s)** | 82 550,0 (+4,9 $) | 82 503,87 |

**Ce que voyait le moteur :**
- Les 11 secondes déjà connues de la fenêtre finale avaient une moyenne de 82 503,9, soit 7 $ **sous** le prix à battre.
- Juste avant 05:19:11, le moteur donnait **Down à 99,5 %**.
- La volatilité de la nuit était très faible : 0,8 $ par seconde.
- À 05:19:11, le perp Bybit fait un saut de +12,7 $ en une seconde, environ 15 fois sa volatilité habituelle. Le moteur prolonge ce nouveau prix sur les 48 s restantes et passe à **Up à 99,5 %**.

**Ce qui s'est passé :**
- Chainlink n'a pas bougé.
- 0,6 s plus tard, au prix Chainlink suivant, le moteur était revenu à **Up à 0,5 %**. Le journal du fantôme confirmé le montre, et c'est pour ça qu'il a abandonné ce signal.
- La moyenne finale officielle est de 82 507,22, donc **Down**.

Le marché, qui vendait Up à 3 c, avait raison.

**Cause :** un seul prix Bybit isolé, non suivi par Chainlink ni vraiment par OKX, a fait basculer la probabilité de 0,5 % à 99,5 %.

## 2. Anomalie de 06:29:23 — Down acheté à 0,366 $ avec 96,4 %

**Cycle :** 06:25 → 06:30. Le prix à battre du bot est de 82 590,25, contre 82 590,20 officiel.

| Heure | Perp Bybit | OKX | Chainlink |
|---|---|---|---|
| 06:29:17 → 06:29:22 | 82 641 | 82 641,4 | 82 603,0 → 82 603,1 |
| **06:29:23** | **82 616,2 (−24 $ en 1 s)** | **82 620,3 (−21 $)** | 82 601,6 (−1,5 $) |

**Ce que voyait le moteur :**
- Les 23 secondes déjà connues avaient une moyenne de 82 602,45, soit 12 $ au-dessus du prix à battre.
- La chute brutale des deux exchanges, prolongée sur les 37 s restantes, donnait une moyenne prévue de 82 586 environ, donc sous le prix à battre. Résultat : **Down à 96 %**.

**Ce qui s'est passé :**
- Chainlink n'a suivi que partiellement.
- La moyenne finale officielle est de 82 591,01, soit **0,81 $ au-dessus** du prix à battre : **Up**.

Ici, la chute était réelle sur deux exchanges, mais le moteur l'a jugée certaine (96 %) alors que l'issue s'est jouée à 81 cents près. La variante « correction spot-perp » a acheté **Up** au même instant et a gagné.

## 3. Le seuil d'entrée

Le code compare la probabilité au **prix affiché du meilleur vendeur**. Le « prix payé » enregistré, lui, inclut les frais Polymarket (environ 7 % × prix × (1 − prix)).

Exemple de 01:58:57 : vendeur à 0,71, probabilité 0,916, donc un avantage de 0,206. Le prix payé enregistré est de 0,7248 avec les frais, ce qui fait paraître l'écart à 0,19.

Tous les achats audités respectent le seuil sur le prix affiché.

## 4. TWAP fin confirmé Chainlink — les 23 signaux de la nuit

| Signal | Côté | Restant | Proba / vendeur au signal | Chainlink suivant après | Proba / vendeur après | Décision | Gagnant |
|---|---|---|---|---|---|---|---|
| 01:58:57 | Down | 62 s | 0,916 / 0,71 | 0,29 s | 0,921 / 0,83 | abandon | Down |
| 02:03:49 | Up | 71 s | 0,371 / 0,16 | 0,98 s | 0,378 / 0,21 | abandon | Down |
| 02:18:44 | Up | 75 s | 0,343 / 0,14 | **0,04 s** | 0,343 / 0,13 | achat | Down |
| 02:28:39 | Up | 81 s | 0,808 / 0,59 | 1,07 s | 0,626 / 0,65 | abandon | Up |
| 02:43:32 | Up | 87 s | 0,981 / 0,78 | 1,14 s | 0,983 / 0,79 | abandon | Down |
| 02:48:57 | Down | 62 s | 0,803 / 0,40 | **0,03 s** | 0,803 / 0,40 | achat | Up |
| 03:03:30 | Down | 89 s | 0,459 / 0,23 | **0,16 s** | 0,458 / 0,23 | achat | Up |
| 03:08:36 | Down | 84 s | 0,434 / 0,23 | **0,04 s** | 0,434 / 0,23 | achat | Up |
| 03:59:00 | Up | 60 s | 0,990 / 0,77 | 0,77 s | 0,991 / 0,88 | abandon | Up |
| 04:08:31 | Up | 88 s | 0,340 / 0,13 | 0,71 s | 0,338 / 0,12 | achat | Down |
| 04:13:54 | Down | 66 s | 0,610 / 0,31 | 0,41 s | 0,651 / 0,80 | abandon | Down |
| 04:28:30 | Up | 90 s | 0,483 / 0,20 | **0,04 s** | 0,483 / 0,20 | achat | Down |
| 04:49:04 | Up | 56 s | 0,655 / 0,45 | 1,14 s | 0,655 / 0,56 | abandon | Down |
| 04:53:31 | Down | 89 s | 0,398 / 0,19 | 0,08 s | 0,249 / 0,28 | abandon | Up |
| 05:04:00 | Down | 59 s | 0,377 / 0,11 | 0,37 s | 0,908 / 0,81 | abandon | Down |
| 05:19:11 | Up | 48 s | 0,995 / 0,03 | 0,62 s | **0,005** / 0,70 | abandon | Down |
| 05:34:04 | Up | 56 s | 0,481 / 0,28 | **0,03 s** | 0,481 / 0,26 | achat | Down |
| 05:43:38 | Up | 81 s | 0,415 / 0,21 | **0,18 s** | 0,414 / 0,21 | achat | Down |
| 06:13:55 | Down | 64 s | 0,562 / 0,36 | **0,05 s** | 0,562 / 0,35 | achat | Up |
| 06:29:23 | Down | 37 s | 0,964 / 0,35 | 0,27 s | 0,812 / 0,58 | achat | Up |
| 06:53:30 | Up | 89 s | 0,985 / 0,46 | 0,63 s | 1,000 / 0,83 | abandon | Up |
| 07:23:30 | Up | 90 s | 0,736 / 0,18 | 0,18 s | 0,736 / 0,19 | achat | (pas encore publié) |
| 07:29:08 | Up | 51 s | 0,452 / 0,03 | 0,97 s | 0,075 / 0,04 | abandon | (pas encore publié) |

**Réponses aux 12 points demandés :**
- **Cycle, signal, côté, prix et quantité :** tous vérifiés, ils sont cohérents.
- **Le Chainlink de confirmation est-il postérieur au signal ?** Oui, son heure d'observation est plus récente. Mais il arrive le plus souvent quelques centièmes de seconde après : le flux livre deux observations presque ensemble. La probabilité et le prix sont alors identiques, donc la « confirmation » n'apporte aucune information.
- **Aucune donnée future n'est utilisée :** vérifié, la décision ne lit que le dernier message reçu.
- **Différence avec le test historique :** le test attendait un **changement de valeur** de Chainlink visible dans les enregistrements (4 par seconde), en pratique 0,5 à 1 s plus tard. Le fantôme en direct accepte n'importe quel nouveau message, même 30 ms plus tard. **Ce n'est pas la même règle.**
- **Pourquoi des pertes de 53 $ quand l'original ne perd que 1 $ sur le même cycle (03:08, 04:08) ?** L'original a acheté quand il n'y avait que 1 ou 2 $ de disponible au meilleur vendeur. Le confirmé a acheté une fraction de seconde plus tard, après que le carnet s'est rechargé, donc 50 $ au même prix. La perte vient de la taille, pas du prix.
- **Les signaux abandonnés :** sur les 12, le côté du signal a gagné 6 fois.
- **Mauvaise série ou erreur systématique ?** Les deux.
  - Mauvaise série : 0 gagnant sur 11 alors que les prix payés en annonçaient 3. Cela arrive environ 2 fois sur 100.
  - Problème systématique : la confirmation ne confirme rien quand elle arrive en quelques centièmes de seconde.

## 5. La nuit, fantôme par fantôme (01:36 → 07:30)

| Fantôme | Achats | Gagnés | Attendus selon le prix payé | Attendus selon notre moteur | Probabilité d'aussi mal faire (selon le prix) | Résultat |
|---|---|---|---|---|---|---|
| TWAP fin | 23 | 6 | 7,6 | 14,6 | 30 % | −183 $ |
| TWAP fin sauts | 18 | 5 | 6,7 | 13,0 | 25 % | −288 $ |
| TWAP fin correction spot-perp | 18 | 10 | 7,0 | 11,8 | — | **+47 $** |
| TWAP fin confirmé Chainlink | 11 | 0 | 3,0 | 5,9 | 2 % | −293 $ |

**Les causes possibles, une par une :**
- **Régime de marché :** oui. La nuit était très calme : volatilité médiane de 1,5 $ par seconde, contre 4,0 $ du 07 au 09.10. Le perp Bybit est resté immobile 90 à 109 secondes sur 120 avant la plupart des achats. Dans ce régime, notre moteur est trop sûr de lui.
- **Surestimation des probabilités :** oui, cette nuit. 14,6 gagnants annoncés pour 6 réels. Le marché (7,6) était bien plus proche.
- **Anomalie Chainlink :** non. Le prix à battre et les moyennes sont justes.
- **Défaut de synchronisation :** non, en dehors des deux sauts d'une seconde décrits plus haut.
- **Exécution simulée :** non. Le rejeu hors ligne, fait de façon indépendante, retrouve la même perte (28 signaux, −241 $).
- **Variance normale :** en partie. Selon les prix payés, une nuit comme celle-ci arrive 1 fois sur 3 à 1 fois sur 4.

**Une hypothèse testée et rejetée :** « la volatilité du perp sous-estime le bruit de Chainlink ». En réalité, Chainlink bouge **moins** que le perp (1,05 $ par seconde contre 1,50 $ cette nuit). Utiliser la plus grande des deux ne change rien (−298 $ contre −241 $).

## 6. Famille « désaccord 30 zone » — mêmes cycles

**Nuit du 10.10 (01:36 → 07:30) :**

| Stratégie | Trades | Gagnés | Résultat | Jackpots |
|---|---|---|---|---|
| zone simple | 36 | 8 | +158 $ | 7 (+1 265 $) |
| **zone + modèle monte** | 16 | 5 | **+359 $** | 4 (+836 $) |
| zone + Binance/perp | 31 | 7 | −94 $ | 6 (+1 010 $) |
| zone + sortie −10 | 36 | 8 | +303 $ | 7 (+1 265 $) |
| zone + Binance/perp + sortie −10 | 31 | 7 | −13 $ | 6 (+1 010 $) |
| combiné taille 25/50 | 30 | 7 | +175 $ | 6 (+860 $) |

**Depuis le début commun (08.10 18:52 → 10.10 07:30) :**

| Stratégie | Trades | Gagnés | Résultat | Jackpots | Cycles évités par rapport à zone simple (gagnants / perdants) | Résultat évité |
|---|---|---|---|---|---|---|
| zone simple | 152 | 42 | +1 718 $ | 26 | — | — |
| **zone + modèle monte** | 88 | 33 | **+2 563 $** | 23 | 9 / 55 | **−1 209 $ évités** |
| zone + Binance/perp | 126 | 38 | +1 809 $ | 22 | 4 / 22 | −649 $ |
| zone + sortie −10 | 152 | 42 | +1 670 $ | 22 | 0 / 0 | — |
| zone + Binance/perp + sortie −10 | 126 | 38 | +1 661 $ | 20 | 4 / 22 | −649 $ |
| combiné taille 25/50 | 117 | 37 | +2 206 $ | 20 | 5 / 30 | −710 $ |

**Quelle règle apporte vraiment quelque chose :**
- **« Modèle monte » (le désaccord doit venir d'une hausse de notre probabilité) :**
  - C'est la règle qui apporte le plus.
  - Elle écarte 64 cycles de « zone simple », dont 55 perdants, ce qui évite 1 209 $ de pertes.
  - Elle sacrifie 3 jackpots.
  - Sur les cycles communs, elle gagne un peu moins (+2 563 $ contre +2 927 $), car elle entre plus tard et un peu plus cher.
  - Au total : +845 $ par rapport à zone simple.
- **« Binance/perp » :** elle évite aussi des perdants (−649 $), mais perd davantage en entrant plus tard sur les cycles communs. Gain net faible : +91 $.
- **« Sortie −10 » :** la nuit, elle aide (+145 $). Sur toute la période, elle coûte légèrement (−48 $). Au total, rien de démontré.
- **Taille 25/50 :** elle réduit les pertes comme les gains, et reste en dessous de « modèle monte ».

## 7. Ce que je te propose (tu décides)

Rien n'est modifié tant que tu n'as pas validé.

1. **Confirmé Chainlink : corriger la règle pour qu'elle corresponde au test historique.** La confirmation n'est acceptée que si la **valeur** Chainlink a changé ET si au moins 0,5 s s'est écoulée depuis le signal. Sinon, ce fantôme reste un doublon de l'original avec une taille plus grande.
2. **Protection contre les sauts d'une seconde :** un fantôme parallèle « TWAP fin anti-saut ». Il n'utilise un mouvement des exchanges que s'il est vu à la fois par Bybit et par OKX (ou Binance), ou s'il dure au moins 2 s. L'original reste inchangé, comme référence.
3. **Garder « zone + modèle monte » comme référence prioritaire**, sans rien y changer.
4. **Le test réel à 1 $ reste reporté**, comme demandé.
