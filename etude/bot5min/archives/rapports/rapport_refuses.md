# Bot95 — Les trades refusés par B, C et D : contribution exacte au résultat de A

**Référence A :** tous les premiers signaux E du cycle. Données : 164 trades du 07.10 au 10.10 11:10.

**Les trois filtres :**
- **B :** avantage de 20 à 30 points ;
- **C :** B, et au moins 2 nouvelles valeurs Chainlink reçues avant l'achat ;
- **D :** C, et un avantage qui reste positif sans le dernier mouvement des exchanges.

Pour chaque trade de A qu'un filtre refuse, on mesure ce qu'il a rapporté ou coûté. Achat au meilleur vendeur, limité à la quantité affichée, frais compris.

**Décision enregistrée (la tienne) :** A reste la référence, D est abandonné, B reste en observation. Pas de nouveau fantôme. La suite se fera sur des données prospectives : verdict mardi 14.10 à 08:00, sur les cycles postérieurs au 10.10 10:25.

## Toutes périodes — A : 164 trades, +1 852 $

| Filtre | Trades gardés | Résultat gardé | Trades refusés | Pertes évitées | Gains sacrifiés | dont jackpots | Effet sur le résultat |
|---|---|---|---|---|---|---|---|
| B | 119 | +2 162 $ | 45 | 832 $ (27 trades) | 521 $ (18 trades) | 186 $ (5) | **+310 $** |
| C | 37 | +1 580 $ | 127 | 1 888 $ (70) | 2 160 $ (57) | 433 $ (8) | **−272 $** |
| D | 33 | +1 462 $ | 131 | 1 955 $ (73) | 2 345 $ (58) | 433 $ (8) | **−390 $** |

## Hors apprentissage — A : 87 trades, +588 $

| Filtre | Trades gardés | Résultat gardé | Trades refusés | Pertes évitées | Gains sacrifiés | dont jackpots | Effet sur le résultat |
|---|---|---|---|---|---|---|---|
| B | 62 | +1 176 $ | 25 | 712 $ (18) | 123 $ (7) | 56 $ (2) | **+588 $** |
| C | 16 | +678 $ | 71 | 1 382 $ (42) | 1 293 $ (29) | 302 $ (4) | **+90 $** |
| D | 14 | +727 $ | 73 | 1 432 $ (44) | 1 293 $ (29) | 302 $ (4) | **+139 $** |

## Pourquoi B est plus prometteur que D

1. **B refuse surtout des perdants.** Hors apprentissage, sur 25 trades refusés, il y a 18 pertes (712 $) pour seulement 7 gains (123 $). Ce sont les très gros avantages, souvent des faux cadeaux.
2. **D refuse presque autant de gagnants que de perdants.** Hors apprentissage, il refuse 73 trades : 44 pertes (1 432 $) et 29 gains (1 293 $). Il trie, mais il jette la moitié des bons trades avec les mauvais.
3. **La cause précise : la condition « 2 nouvelles valeurs Chainlink ».** La plupart des signaux naissent au moment même où une nouvelle valeur Chainlink arrive. Au moment de l'achat, il y en a donc **0** depuis la naissance. Exiger 2 valeurs élimine précisément les signaux les plus frais, et une partie des gros gains.
4. **Les plus gros gains que D aurait sacrifiés** (trades gardés par B mais refusés par D) :

| Cycle | Côté | Prix | Avantage | Valeurs Chainlink depuis la naissance | Indépendant du dernier mouvement | Résultat |
|---|---|---|---|---|---|---|
| 09.10 21:53 | Up | 0,17 | 0,21 | 0 | oui | +241 $ |
| 07.10 12:39 | Up | 0,21 | 0,22 | 8 | non | +185 $ |
| 10.10 09:03 | Up | 0,24 | 0,21 | 0 | oui | +156 $ |
| 09.10 11:43 | Down | 0,29 | 0,22 | 0 | oui | +120 $ |
| 09.10 23:19 | Down | 0,33 | 0,21 | 0 | oui | +99 $ |
| 07.10 09:28 | Down | 0,34 | 0,21 | 0 | oui | +95 $ |
| 09.10 23:43 | Down | 0,36 | 0,21 | 0 | oui | +87 $ |
| 10.10 05:33 | Down | 0,37 | 0,22 | 0 | oui | +83 $ |

Au total, ces trades gardés par B mais refusés par D font +700 $ sur toutes les périodes : 40 gagnants, dont 3 jackpots, pour 46 perdants.

5. **La concentration confirme ta leçon.** Les 10 plus gros gains de A font +2 132 $, soit plus que le total de A (+1 852 $). Hors apprentissage, les 5 plus gros font +1 049 $ pour un total de +588 $. **Le bénéfice de Bot95 vient de quelques gagnants très asymétriques.** Un filtre qui en retire quelques-uns pour gagner en taux de réussite perd de l'argent.

## Une précision honnête sur D

Hors apprentissage, D fait **+139 $ de mieux que A** au total. Mais cela tient en deux périodes de sens contraire :
- −173 $ en validation ;
- +312 $ pendant la nuit et la matinée du 10.10.

Et il ne garde que 14 trades. B fait +588 $ de mieux sur les mêmes cycles, avec 62 trades. Ta décision reste cohérente : **B en observation, D abandonné.**

## À propos des PDF que ChatGPT n'a pas retrouvés

Les PDF sont envoyés ici, dans cette conversation. ChatGPT n'y a pas accès. Pour qu'il puisse les lire, il faut les télécharger depuis cette conversation (en touchant chaque fichier), puis les joindre dans ChatGPT.

Les deux qu'il cherchait :
- **Bot95_etat_10-10_1125.pdf** : l'état complet du bot à 11:25, avec le classement de toutes les stratégies et le détail des trades ;
- **Bot95_test_combinaison_D.pdf** : le test de la combinaison D.
