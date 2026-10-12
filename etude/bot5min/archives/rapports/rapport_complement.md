# TWAP FIN — les 23 nouvelles idées testées et commentées

Données : BTC, 693 cycles du 07.10 au 09.10. Pour chaque cycle, on prend le premier signal TWAP FIN original (+2 323 $ au total sur 140 signaux).

Tout est séparé dans le temps :
- **apprentissage** : cycles avant le 08.10 20:30 ;
- **validation** : cycles après.

Une piste ne compte que si elle tient dans les deux périodes. Aucun fantôme n'a été modifié et aucun nouveau bot n'a été créé.

Le nouveau fantôme « TWAP fin confirme Chainlink » est en ligne depuis 00:52.

## En bref

1. **Le moment du signal compte beaucoup.**
   - Signaux entre 90 et 60 s : 85 achats, 53 % gagnés, **+1 882 $**, positifs dans les deux périodes.
   - Signaux entre 40 et 20 s : 13 achats, +26 $ seulement, et −41 $ en validation.
2. **Fiabilité :** le carnet prévoit mieux que notre moteur entre 40 et 20 s. Notre moteur est meilleur de 80 à 40 s. La version « sauts » prévoit mieux que l'original à partir de 50 s.
3. **Attendre Chainlink** n'aide qu'entre 60 et 40 s (+573 $ contre +414 $). Entre 90 et 60 s, attendre fait manquer 9 jackpots et coûte 700 $.
4. **Le contrat opposé n'apporte rien.** Sur Polymarket, revendre directement ou passer par le contrat opposé donne exactement le même prix : les deux carnets sont un seul et même carnet. Les écarts « acheter les deux côtés pour moins de 1 $ » n'existent pratiquement pas (1 mesure sur 69 161).
5. **Bid et spread :** quelques pistes (spread de 3 à 6 c), mais sur 17 achats seulement. À observer, pas à appliquer.

## A. Qui prévoit le mieux, selon le temps restant (idée 1)

Le score de Brier mesure l'erreur de prévision : plus bas = meilleur. Une mesure par seconde.

| Temps restant | Original | Sauts | Spot-perp | Carnet |
|---|---|---|---|---|
| 90-80 s | 0,111 | 0,111 | 0,110 | 0,111 |
| 80-70 s | 0,112 | 0,112 | 0,111 | 0,115 |
| 70-60 s | 0,111 | 0,110 | 0,111 | 0,114 |
| 60-50 s | 0,109 | 0,109 | 0,109 | 0,112 |
| 50-40 s | 0,095 | **0,092** | 0,096 | 0,096 |
| 40-30 s | 0,082 | 0,078 | 0,079 | **0,073** |
| 30-20 s | 0,079 | **0,072** | 0,078 | 0,074 |
| 20-10 s | 0,075 | 0,068 | **0,066** | 0,082 |

**Quand le moteur et le carnet divergent de plus de 15 points :**
- de 80 à 40 s, notre moteur a nettement raison plus souvent (0,207 contre 0,254 entre 80 et 70 s, par exemple) ;
- entre 40 et 30 s, c'est le carnet (0,151 contre 0,114) ;
- entre 30 et 20 s, ils sont à égalité.

**Rentabilité selon le moment du signal :**

| Signal | Achats | Gagnés | Résultat | Apprentissage | Validation |
|---|---|---|---|---|---|
| 90-60 s | 85 | 53 % | **+1 882 $** | +912 $ | +970 $ |
| 60-40 s | 42 | 38 % | +414 $ | +318 $ | +96 $ |
| 40-20 s | 13 | 23 % | +26 $ | +68 $ | −41 $ |

**Ce que je te propose (tu décides) :** ne rien changer. Au bilan, vérifier en direct si les achats du fantôme entre 40 et 20 s font aussi peu.

Si c'est confirmé, on pourra discuter d'une variante « TWAP fin 90-40 s ». Ce serait un nouveau fantôme : l'original n'est pas touché.

## A bis. Acheter tout de suite, attendre Chainlink ou ne rien faire (idées 2 et 3)

| Fenêtre | Signaux | Tout de suite | Attendre Chainlink | Pertes évitées | Gains manqués (jackpots) |
|---|---|---|---|---|---|
| 90-60 s | 85 | **+1 882 $** | +1 164 $ | +191 $ | +1 129 $ (9) |
| 60-40 s | 42 | +414 $ | **+573 $** | +319 $ | +640 $ (2) |
| 40-20 s | 13 | +26 $ | −75 $ | +44 $ | +176 $ (0) |

Le « regret de l'abstention » (idée 3) est clair. Entre 90 et 60 s, l'attente évite 191 $ de pertes mais fait manquer 1 129 $ de gains, dont 9 jackpots (gain d'au moins 4 fois la mise). C'est cohérent avec la découverte précédente : le marché nous rejoint en moins d'une seconde.

Le nouveau fantôme « confirmé Chainlink » permettra de vérifier cela en direct.

## B. Le bid et le spread (idées 10 à 13)

Le spread est l'écart entre le prix vendeur et le prix acheteur de notre côté.

| Groupe | Achats | Gagnés | Résultat | Appr. | Valid. |
|---|---|---|---|---|---|
| spread ≤ 2 c | 117 | 41 % | +2 091 $ | +1 236 $ | +855 $ |
| spread 3-6 c | 17 | 65 % | +220 $ (+165 % par $) | +52 $ | +169 $ |
| spread > 6 c | 6 | 83 % | +11 $ | | |
| vendeur monté plus que le bid (BAPT < 0) | 28 | 61 % | +250 $ (+120 % par $) | +42 $ | +208 $ |
| bid monté plus que le vendeur (BAPT > 0) | 4 | 75 % | +106 $ | | |

- **Idée 10 (écart bid-vendeur) :** un spread de 3 à 6 c donne plus de gagnants, positif dans les deux périodes. Mais 17 achats, c'est trop peu. À observer.
- **Idée 11 (le bid monte avant le vendeur) :** cela n'arrive **jamais** dans les 3 s qui précèdent nos signaux (0 cas). Pas de signal à en tirer.
- **Idée 12 (le spread se resserre) :** aucun resserrement de plus de 1,5 c dans les 3 s avant nos signaux. Il n'y a rien à mesurer.
- **Idée 13 (BAPT) :** quand le vendeur a monté plus que le bid, c'est mieux (28 achats, +250 $), dans les deux périodes. Mais l'échantillon est petit et ce n'est pas l'intuition de départ (c'était le bid qui devait monter). À observer, pas à appliquer.

## Idées 4 et 5. Les modèles d'accord ou dispersés

On compare l'écart entre les trois probabilités (original, sauts, spot-perp) au moment du signal.

| Groupe | Achats | Résultat | Appr. | Valid. |
|---|---|---|---|---|
| modèles proches (écart ≤ 8,7 pts) | 70 | +1 215 $ | +548 $ | +668 $ |
| modèles dispersés | 70 | +1 108 $ | +750 $ | +358 $ |

Pas de différence stable : la robustesse entre modèles ne sert pas de filtre. Rejeté pour l'instant.

## Idée 6. Le carnet est très sûr de lui

On regarde le cas où le côté bon marché coûte 10 c ou moins, entre 60 et 20 s.

| Notre probabilité pour le côté bon marché | Mesures | Prix moyen | Gagnés | Gagné − prix − frais |
|---|---|---|---|---|
| sous le prix | 563 | 0,023 | 1,2 % | −1,3 pts |
| prix à prix + 5 pts | 305 | 0,041 | 4,3 % | −0,1 pt |
| prix + 5 à 15 pts | 196 | 0,062 | 7,7 % | +1,0 pt |
| plus de 15 pts au-dessus | 86 | 0,073 | **14,0 %** | **+6,2 pts** |

Notre moteur trie bien les petits contrats. Quand il les juge sans valeur, ils perdent vraiment, comme le protège déjà le garde-fou. Quand il les juge nettement sous-évalués, ils gagnent deux fois plus que leur prix.

## Idée 7. La compression des probabilités

Ce n'est pas mesuré à part : c'est déjà dans le tableau A. Dans les 50 dernières secondes, le Brier baisse plus vite pour la version « sauts » que pour l'original. Les queues épaisses décrivent mieux la fin du cycle. La version sauts est déjà en fantôme.

## Idée 8. Surface de prime (toutes les cotations, pas seulement nos achats)

Chaque case donne gagné − prix − frais, en points.

| Prix | 90-60 s appr. / valid. | 60-40 s appr. / valid. | 40-20 s appr. / valid. |
|---|---|---|---|
| 1-5 c | −1,3 / −1,9 | −1,2 / −1,8 | −1,7 / −0,8 |
| 5-15 c | +0,2 / −0,9 | **+3,2 / +1,8** | +0,8 / −3,3 |
| 15-35 c | −1,4 / −0,3 | −0,3 / +0,7 | −1,9 / −13,2 |
| 35-65 c | −2,5 / −4,6 | −3,4 / −4,7 | −4,5 / −6,4 |
| 65-85 c | −2,7 / −3,1 | −5,3 / −2,0 | −2,4 / +10,1 |
| 85-95 c | −2,7 / −3,3 | −5,3 / −5,0 | −2,6 / +2,5 |
| 95-99 c | −0,2 / 0,0 | −1,4 / −2,2 | +2,0 / −0,8 |

**Acheter « à l'aveugle » perd presque partout**, d'à peu près les frais. Le marché n'a pas de prime de risque exploitable sans modèle. Seule la case 5-15 c à 60-40 s est positive deux fois, faiblement : c'est trop peu pour en faire une règle.

Cela confirme que notre gain vient du moteur, pas d'une zone de prix.

## Idée 9. Alpha d'information contre alpha de valorisation

Avec les chiffres de la nuit, par jeton :
- **Information :** le prix acheteur rejoint notre prix d'achat + 0,12 en 5 s (gain de revente possible).
- **Valorisation :** il reste +0,08 de plus en gardant jusqu'au règlement (+0,20 au total).

Donc environ **60 % de l'alpha est de l'information** captée dans les secondes qui suivent, et **40 % de la valorisation** qui persiste jusqu'au règlement.

## Idées 14 à 18. Le contrat opposé

- **Idée 14 (deux carnets) :** les carnets Up et Down sont parfaitement miroirs. Le vendeur Up est toujours égal à 1 − l'acheteur Down. Polymarket croise automatiquement les deux côtés : c'est la même liquidité affichée deux fois.
- **Idées 15-16 (vente synthétique, routeur de sortie) :** la vente directe et la voie « acheter l'opposé puis fusionner » donnent exactement la même valeur, à +1, 5, 10 et 20 s. **Aucun gain.** Rejeté.
- **Idée 17 (acheter les deux côtés sous 1 $) :** 1 mesure sur 69 161, soit 4 cents. Inexistant. Rejeté.
- **Idée 18 (verrouiller en achetant l'opposé) :**

| Moment | Gain verrouillé | Gain en gardant | Verrouillage meilleur |
|---|---|---|---|
| +1 s | +0,09 | **+0,20** | 76 / 140 |
| +5 s | +0,12 | **+0,20** | 74 / 138 |
| +20 s | +0,19 | **+0,26** | 53 / 116 |

Garder rapporte en moyenne environ 0,08 à 0,10 $ de plus par jeton. Verrouiller réduit le risque, mais coûte environ 40 % du gain. Rejeté, sauf si tu veux un jour réduire la variance en réel.

## Idées 19 à 21. Recyclage du capital et routeur

- **Idée 19 (recyclage du capital) :** une position TWAP fin dure au plus 90 s, plus le règlement. Avec un achat de 50 $ par cycle, le capital n'est jamais la limite. Recycler n'a d'intérêt que si on manque de capital en réel. Sans objet pour l'instant.
- **Idée 20 (exposition nette entre stratégies) :** cela ne s'applique qu'aux vraies positions. Ce sera utile seulement si plusieurs stratégies tournent en réel en même temps.
- **Idée 21 (laboratoire du contrat opposé) :** inutile, puisque les deux carnets sont miroirs (idée 14).

## Idées 22 et 23. Expériences prioritaires et règles de validation

- **A (fiabilité selon le temps) :** fait. La bascule se fait vers 40 s.
- **B (bid/spread) :** fait. Pistes faibles, à observer.
- **C (exécution par le contrat opposé) :** fait. Sans valeur.
- **D (recyclage) :** sans objet tant qu'on est en fantôme.

Les règles demandées sont respectées : pas de fantôme modifié, données disponibles à l'instant seulement, mêmes cycles, frais compris, apprentissage et validation séparés dans le temps.

## Ce que je te propose (tu décides)

1. Ne rien changer. Au bilan, regarder en direct les achats TWAP fin par fenêtre (90-60, 60-40, 40-20 s).
2. Si la fenêtre 40-20 s reste mauvaise en direct, ajouter un fantôme « TWAP fin 90-40 s » (sans toucher à l'original).
3. Abandonner les pistes du contrat opposé (14 à 18, 21) : elles ne peuvent rien rapporter sur Polymarket.
4. Garder spread et BAPT en observation, à revoir avec une semaine de données.
