# Pression de règlement, grecques, réévaluations et carnet — BTC, 889 cycles (07.10 08:00 → 10.10 10:30)

56625 mesures (une par seconde, 90-20 s). Probabilité = modèle E (tables du bot). Apprentissage avant le 08.10 22:00, validation jusqu'au 09.10 23:36, nuit du 10.10 à part.

## Partie 1-4. Les grecques du règlement apportent-elles quelque chose au signal E ? (premier signal E du cycle, seuils = médianes de l'apprentissage)

| Groupe au moment du signal | Apprentissage (achats / gagnés / résultat / jackpots) | Validation | Nuit 10.10 |
|---|---|---|---|
| tous les signaux E | 60 / 48 % / **+1 399 $** / 7 | 40 / 50 % / **+638 $** / 5 | 34 / 29 % / **−402 $** / 1 |
| delta fort (≥ 0.023 par $) | 30 / 33 % / **+457 $** / 3 | 24 / 42 % / **+455 $** / 2 | 23 / 26 % / **−382 $** / 0 |
| delta faible | 30 / 63 % / **+942 $** / 4 | 16 / 62 % / **+183 $** / 3 | 11 / 36 % / **−20 $** / 1 |
| réévaluation attendue forte (gamma d'information ≥ 0.031) | 30 / 30 % / **+435 $** / 2 | 23 / 43 % / **+498 $** / 2 | 25 / 24 % / **−441 $** / 1 |
| réévaluation attendue faible | 30 / 67 % / **+964 $** / 5 | 17 / 59 % / **+140 $** / 3 | 9 / 44 % / **+39 $** / 0 |
| convexité forte (|gamma| ≥ médiane) | 30 / 47 % / **+617 $** / 4 | 22 / 45 % / **+543 $** / 2 | 29 / 31 % / **−249 $** / 1 |
| le temps qui passe joue pour nous (thêta > 0) | 32 / 62 % / **+200 $** / 3 | 20 / 60 % / **+225 $** / 1 | 22 / 36 % / **−222 $** / 1 |
| le temps qui passe joue contre nous | 28 / 32 % / **+1 199 $** / 4 | 20 / 40 % / **+413 $** / 4 | 12 / 17 % / **−180 $** / 0 |
| barrière qui s'éloigne en notre faveur (dernière seconde) | 4 / 75 % / **+78 $** / 0 | 3 / 33 % / **+88 $** / 0 | 2 / 50 % / **+6 $** / 0 |
| barrière qui se rapproche contre nous | 28 / 32 % / **+865 $** / 4 | 8 / 25 % / **−97 $** / 0 | 4 / 0 % / **−103 $** / 0 |
| idée 3 : E monte, barrière favorable, carnet immobile (< 2 c) | 1 / 100 % / **+50 $** / 0 | 0 / — / — / — | 0 / — / — / — |
| idée 19 : révision E ≥ 10 pts alors que les exchanges ont bougé < 1 $ (fixation pure) | 0 / — / — / — | 0 / — / — / — | 1 / 0 % / **−53 $** / 0 |

Carte de l'idée 13 (avantage E × réévaluation attendue), toutes périodes hors apprentissage :

| Avantage au signal | Réévaluation attendue | Achats / gagnés / résultat / jackpots |
|---|---|---|
| 0,20-0,30 | forte | 35 / 37 % / **+169 $** / 2 |
| 0,20-0,30 | faible | 13 / 69 % / **+362 $** / 2 |
| ≥ 0,30 | forte | 13 / 23 % / **−113 $** / 1 |
| ≥ 0,30 | faible | 13 / 38 % / **−182 $** / 1 |

## Idées 14, 16, 20. D'où viennent les variations de probabilité d'une seconde à l'autre ?

Sur 55796 variations d'une seconde : part « temps qui passe + fixation d'une seconde au prix prévu » ≈ **22 %** de l'amplitude totale ; le reste (≈ 78 %) vient des nouveaux prix (exchanges et Chainlink). Corrélation entre la variation prévue par le thêta et la variation réelle : +0.07.

## Idées 26-33. Comment Polymarket réagit-il à une révision de E ?

Réaction normale apprise (idée 30) : le milieu du carnet bouge en moyenne de **0.58** × la révision de E dans la même seconde (1084 révisions ≥ 5 pts, apprentissage).

| Réaction dans la même seconde | Révisions | Le carnet continue dans le sens de E dans les 2 s suivantes | dans les 5 s | Le côté de la révision gagne |
|---|---|---|---|---|
| sous-réaction (< 1/3 de la normale) | 170 | 62 % | 66 % | 64 % |
| réaction normale | 364 | 50 % | 53 % | 63 % |
| sur-réaction (> 2× la normale) | 96 | 52 % | 51 % | 60 % |

### Idées 10, 26, 38 : prévoir que le prix vendeur du côté de la révision monte d'au moins 2 c dans la seconde (AUC : 0,5 = hasard, 1 = parfait)

| Variable | AUC apprentissage | AUC validation + nuit |
|---|---|---|
| taille de la révision de E | 0.63 | 0.62 |
| gamma d'information | 0.57 | 0.56 |
| delta | 0.57 | 0.56 |
| retrait de quantité au meilleur prix sur 0,5 s (idée 35) | 0.55 | 0.57 |
| spread | 0.53 | 0.58 |
| avantage E − prix | 0.60 | 0.59 |

Taux de base : le prix vendeur monte d'au moins 2 c dans la seconde après une révision ≥ 2 pts dans 31 % des cas (3275 révisions).

### Idées 34, 37, 39 : le carnet se vide-t-il avant que le prix monte ?

| Situation | Mesures | Le prix vendeur monte d'au moins 2 c dans la seconde |
|---|---|---|
| quantité stable ou en hausse | 62412 | 4.4 % |
| quantité au meilleur prix divisée par 2 ou plus en 0,5 s (prix inchangé) | 3182 | 29.9 % |

## Partie 8-10. Balayer le carnet (8 niveaux enregistrés aux signaux depuis le 10.10 01:22)

34 cycles avec signal et résultat officiel (premier signal TWAP fin du cycle, toutes variantes confondues). Petit échantillon : à lire comme une première mesure.

| Politique (50 $ max par cycle) | Cycles achetés | Capital engagé | Résultat | Jackpots |
|---|---|---|---|---|
| meilleur vendeur seul (actuel) | 33 | 801 $ | **−287 $** | 2 |
| balayer tant que l'avantage ≥ 20 pts | 33 | 1200 $ | **−500 $** | 2 |
| balayer tant que l'avantage ≥ 15 pts | 34 | 1608 $ | **−493 $** | 2 |
| balayer tant que l'avantage ≥ 10 pts | 34 | 1650 $ | **−499 $** | 2 |
| balayer tant que l'avantage net > 0 | 34 | 1650 $ | **−499 $** | 2 |
| balayer prudent (proba − 10 pts, avantage ≥ 10 pts) | 32 | 1199 $ | **−499 $** | 2 |
| balayer ≥ 20 pts, jusqu'à 100 $ | 33 | 2289 $ | **−1 122 $** | 2 |

Idée 62 — capacité totale dans les 8 premiers niveaux au moment du signal (médiane / moyenne, en $) :

- avantage ≥ 20 pts : médiane 147 $, moyenne 807 $ ; ≥ 50 $ disponibles dans 22 cycles sur 34.
- avantage ≥ 10 pts : médiane 512 $, moyenne 1056 $ ; ≥ 50 $ disponibles dans 32 cycles sur 34.
- avantage ≥ 0 pts : médiane 512 $, moyenne 1166 $ ; ≥ 50 $ disponibles dans 32 cycles sur 34.
- au seul meilleur vendeur : médiane 13 $.

Idées 64-67 — reconstitution : après le signal, le meilleur prix du signal est-il encore disponible (sans tenir compte de notre propre achat, qui n'a pas eu lieu en vrai) ?

| Délai | Meilleur vendeur au même prix ou moins cher | Quantité médiane à ce prix ou moins cher | Capacité ≥ 20 pts d'avantage (médiane) |
|---|---|---|---|
| 0.25 s | 62 % (34) | 123 jetons | 185 $ |
| 0.5 s | 59 % (34) | 67 jetons | 186 $ |
| 1 s | 53 % (34) | 98 jetons | 164 $ |
| 2 s | 47 % (34) | 0 jetons | 146 $ |
| 5 s | 50 % (34) | 48 jetons | 99 $ |

Idée 68 — exécution patiente (meilleur vendeur à 0 s, puis encore au meilleur vendeur à 1 s et 2 s si l'avantage reste ≥ 20 pts, 50 $ max) : 33 cycles, capital 1283 $, résultat **−660 $**.