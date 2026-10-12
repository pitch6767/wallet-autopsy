# Bot95 — Transmission vers Chainlink et tournoi des prévisions

**Données :** BTC, 849 cycles du 07.10 08:00 au 10.10 07:15, tels qu'enregistrés par le bot (carnet 4 fois par seconde, Bybit, OKX, Binance, Coinbase, Chainlink).

**Trois périodes séparées dans le temps :**
- **apprentissage** : avant le 08.10 à 21:55 ;
- **validation** : du 08.10 21:55 au 09.10 23:36 ;
- **nuit du 10.10** : présentée à part.

Les coefficients des modèles C et D ont été appris **uniquement** sur l'apprentissage. Les décisions n'utilisent que ce qui avait été reçu à l'instant.

**Fait ce matin, comme demandé :**
- Le fantôme « confirmé Chainlink » applique maintenant la règle historique. Il n'achète que sur une **nouvelle valeur** Chainlink reçue **au moins 0,5 s** après le signal, si l'avantage reste au moins égal à 0,20.
- Il tourne sous le nom « TWAP fin confirme Chainlink 0,5 s ». L'ancienne version est arrêtée, et son historique est conservé.
- Aucun autre fantôme n'a été modifié.

## Réponses aux trois questions décisives

**Question 1 — Quelle part d'un mouvement des exchanges apparaît dans Chainlink, et en combien de temps ?**

L'écart est mesuré entre le prix de l'exchange (ramené au niveau Chainlink) et le dernier prix Chainlink. Le tableau donne la part de cet écart que Chainlink a rattrapée après chaque délai.

| Source | 0,5 s | 1 s | 2 s | 5 s | 10 s |
|---|---|---|---|---|---|
| Bybit perp | 8 % | 16 % | 33 % | 57 % | 69 % |
| OKX | 9 % | 19 % | 38 % | 63 % | 75 % |
| **Binance** | 12 % | 26 % | 51 % | 78 % | 85 % |
| Coinbase | 9 % | 19 % | 36 % | 56 % | 66 % |
| **consensus des 4** | 12 % | 24 % | 49 % | 80 % | **95 %** |

- Chainlink rattrape **progressivement** : environ la moitié en 2 s et presque tout en 10 s, à condition de suivre **le consensus des exchanges**.
- Un exchange seul est moins bien suivi. Bybit, que notre moteur utilise en premier, est le **moins bien suivi** : 69 % après 10 s.
- Binance est la meilleure source unique.

**Question 2 — Peut-on prévoir cette transmission ?** Oui, en partie.

| Situation (consensus) | 2 s | 5 s | 10 s |
|---|---|---|---|
| 2 exchanges d'accord | 26 % | 59 % | 81 % |
| 3 exchanges d'accord | 31 % | 63 % | 81 % |
| **4 exchanges d'accord** | 60 % | **91 %** | **103 %** |
| régime agité (≥ 2 $ par seconde) | 49 % | 82 % | 96 % |
| **régime calme** (< 2 $ par seconde) | 31 % | **51 %** | **68 %** |

- Un mouvement vu par les 4 exchanges passe presque entièrement dans Chainlink en 5 s.
- **En régime calme, Chainlink ne reprend qu'environ la moitié du mouvement.** C'est exactement la nuit du 10.10.

**Question 3 — Une meilleure prévision de Chainlink améliore-t-elle le résultat ?** Elle améliore la prévision, surtout la nuit, mais **pas le gain les jours normaux** : voir le tournoi plus bas.

## Q17. Les sauts d'une seconde du perp Bybit

Un saut est ici un mouvement d'au moins 4 fois la volatilité par seconde, et d'au moins 3 $, en une seconde.

| Type de saut | Sauts | Reste sur Bybit à 10 s | Passé dans Chainlink à 2 s | à 5 s | à 10 s |
|---|---|---|---|---|---|
| confirmé par OKX ou Binance | 2 663 | 104 % | 35 % | 86 % | 94 % |
| **isolé (Bybit seul)** | 571 | 100 % | 10 % | **43 %** | **47 %** |
| isolé, nuit du 10.10 | 167 | 100 % | 5 % | 33 % | 39 % |

**La découverte importante :** un saut isolé de Bybit **ne disparaît pas de Bybit**, il y reste à 100 %. Mais **Chainlink n'en reprend que 40 à 50 %**, et seulement un tiers la nuit.

Ce n'est donc pas un « saut qui retombe ». C'est Bybit qui s'écarte durablement des autres places, et Chainlink ne le suit pas. Notre moteur, qui prolonge Bybit, se trompe dans ce cas.

## Q18. Les basculements brutaux de probabilité (moteur actuel, 90-20 s)

| Basculement en 1 s | Événements | Déclenché surtout par Bybit | Chainlink a bougé dans le même sens | Le nouveau côté a gagné |
|---|---|---|---|---|
| plus de 20 points | 338 | 62 % | 19 % | 65 % |
| plus de 40 points | 71 | 54 % | 27 % | 76 % |
| plus de 70 points | 14 | 57 % | 21 % | 71 % |
| de moins de 5 % à plus de 95 % | 2 | 100 % | 0 % | 50 % |

- La plupart des grands basculements sont **justes** : le nouveau côté gagne 65 à 76 % du temps. Un veto systématique serait une erreur.
- Les basculements extrêmes (de moins de 5 % à plus de 95 %) sont très rares : 2 en 3 jours, dont celui de 05:19. Ils viennent tous de Bybit, sans mouvement de Chainlink.
- En régime calme, les basculements de plus de 70 points ne gagnent que 56 % du temps (9 cas).

## Le tournoi des modèles

Les modèles prévoient différemment les prix Chainlink encore à venir. **L'incertitude est la même pour tous** : seule la moyenne finale prévue change.

| Modèle | Prévision des prix Chainlink restants |
|---|---|
| A — actuel | dernier prix Bybit prolongé |
| B — anti-saut | un saut de Bybit n'est pris en compte que s'il est confirmé par un autre exchange ou s'il dure au moins 2 s |
| C — persistance | garde 0,88 d'un saut récent (appris) |
| C2 — persistance selon confirmation | garde 0,60 d'un saut isolé, 0,89 d'un saut confirmé (appris) |
| D — prévision Chainlink | dernier Chainlink + 0,98 × (consensus des 4 exchanges − Chainlink) (appris) |

**Erreurs de prévision.** Pour chaque période : l'erreur sur la moyenne finale, puis la part des probabilités annoncées au-dessus de 99 % qui se sont révélées fausses.

| Modèle | Apprentissage | Validation | Nuit 10.10 | Régime calme |
|---|---|---|---|---|
| A — actuel | 21,28 $ / 0,0 % | 15,88 $ / 0,4 % | 7,70 $ / 1,6 % | 7,99 $ / 1,9 % |
| B — anti-saut | 21,28 $ / 0,0 % | 15,88 $ / 0,4 % | 7,69 $ / 1,6 % | 7,98 $ / 1,9 % |
| C — persistance | 21,28 $ / 0,0 % | 15,87 $ / 0,4 % | 7,70 $ / 1,6 % | 7,99 $ / 1,9 % |
| C2 — selon confirmation | 21,28 $ / 0,0 % | 15,87 $ / 0,4 % | 7,69 $ / 1,6 % | 7,98 $ / 1,9 % |
| **D — prévision Chainlink** | **21,13 $** / 0,0 % | **15,74 $ / 0,3 %** | **7,31 $ / 1,2 %** | **7,61 $ / 1,2 %** |

D est le meilleur prévisionniste partout. Il réduit d'un tiers les fausses certitudes au-dessus de 99 % la nuit et en régime calme.

**Rejeu TWAP FIN.** Premier signal du cycle, avantage d'au moins 0,20, entre 90 et 20 s, 50 $ au maximum limité à la quantité affichée, frais compris.

| Modèle | Apprentissage | Validation | Nuit 10.10 | Jackpots (appr. / valid. / nuit) |
|---|---|---|---|---|
| A — actuel | +1 195 $ (86) | +1 214 $ (58) | −241 $ (28) | 10 / 8 / 3 |
| **B — anti-saut** | **+1 403 $** (85) | +1 214 $ (58) | **−215 $** (28) | 11 / 8 / 3 |
| C — persistance | +1 192 $ (83) | +1 257 $ (58) | −409 $ (28) | 10 / 8 / 1 |
| C2 — selon confirmation | +1 400 $ (82) | **+1 257 $** (58) | −297 $ (28) | 11 / 8 / 1 |
| D — prévision Chainlink | +1 197 $ (68) | +811 $ (37) | **+175 $** (24) | 10 / 4 / 3 |

**Lecture :**
- **B (anti-saut)** n'est **jamais moins bon** que A : +208 $ en apprentissage, égal en validation, +26 $ la nuit, avec moins de pertes de suite la nuit (5 contre 8). C'est un petit gain, mais sans coût observé.
- **C et C2 (persistance)** améliorent un peu la validation (+43 $), mais font pire la nuit. Ils ne sont pas démontrés.
- **D (prévision Chainlink)** est le seul à **gagner la nuit** (+175 $ contre −241 $). Mais il fait **nettement moins bien les jours normaux** : −403 $ en validation, avec 21 achats et 4 jackpots de moins. Il voit moins d'occasions, car il colle davantage à Chainlink, donc au carnet.
- **Aucun modèle n'est meilleur partout.** Le bon modèle dépend du régime : D en régime calme, A ou B en régime agité.

## Réponses aux autres demandes

- **Shock Decay (idées 8-10) :** la persistance apprise d'un saut de Bybit est de 0,88 sur tous les sauts, et de 0,60 sur les sauts isolés. Elle réduit un peu les erreurs extrêmes, mais n'améliore pas le résultat de façon fiable. La correction continue n'est pas meilleure que l'anti-saut simple.
- **Coefficient de transmission (idée 12)** et **confirmation multi-exchanges (idée 13) :** voir les tableaux des questions 1 et 2. Plus il y a d'exchanges d'accord, mieux le mouvement passe.
- **Le cas de 06:29 :** deux exchanges seulement étaient d'accord (Bybit et OKX). Dans cette situation, Chainlink ne reprend que 59 % du mouvement à 5 s. Prolonger 100 % de la chute était donc excessif.
- **Prévision directe de Chainlink (idées 14-15, 20) :** c'est le modèle D. Il est meilleur la nuit, moins bon le jour.
- **Respect des horodatages (idée 16) :** les heures de réception ont été utilisées partout, jamais les heures d'observation Chainlink.

## Ce que je te propose (tu décides)

Rien d'autre n'est modifié sans ton accord.

1. **Ajouter deux fantômes de comparaison**, sans toucher aux existants :
   - « TWAP fin anti-saut » (modèle B) : jamais moins bon dans les trois périodes ;
   - « TWAP fin prévision Chainlink » (modèle D) : meilleur la nuit et en régime calme.
2. **Ne pas lancer C ni C2** : ils ne sont pas démontrés.
3. Plus tard, avec plus de nuits enregistrées : tester un modèle qui choisit selon le régime (D quand le marché est calme, A ou B sinon). Pour l'instant, une seule nuit ne suffit pas à le régler sans tricher.
4. Le test réel à 1 $ reste reporté.
