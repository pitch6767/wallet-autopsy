# L'erreur du prix à battre affiché — BTC, 07.10 08:00 → 09.10 22:35

## 1. Continuité officielle

Prix final officiel d'un cycle = prix à battre officiel du suivant : **740 sur 740** paires de cycles consécutifs (à 1 centime près).

## 2. Taille de l'erreur

739 cycles avec valeurs officielles.

| Erreur | Moyenne (biais) | Médiane absolue | 75 % | 90 % | 95 % | max |
|---|---|---|---|---|---|---|
| début (prix à battre affiché − officiel) | -0.48 $ | 10.0 $ | 18.3 $ | 32.4 $ | 43.9 $ | 103.0 $ |
| fin (clôture affichée − officielle) | -0.38 $ | 10.0 $ | 18.3 $ | 32.4 $ | 43.9 $ | 103.0 $ |
| sur la différence fin − début (ce qui décide le gagnant) | +0.10 $ | 14.8 $ | 28.5 $ | 46.7 $ | 61.7 $ | 173.6 $ |

Corrélation erreur de début / erreur de fin : **-0.07** (les erreurs de bord se compensent si elle est proche de +1).

## 3. Gagnant faux avec les chiffres affichés

**83 cycles sur 739** (11.2 %).

| Écart final affiché (|clôture − prix à battre|) | Cycles | Gagnant faux | % |
|---|---|---|---|
| 0-5 $ | 55 | 25 | 45 % |
| 5-10 $ | 47 | 17 | 36 % |
| 10-20 $ | 76 | 20 | 26 % |
| 20-30 $ | 77 | 9 | 12 % |
| 30-50 $ | 145 | 7 | 5 % |
| 50 $ et plus | 339 | 5 | 1 % |

## 4. L'erreur de début est-elle prévisible par le mouvement du BTC juste avant ?

| Mouvement du BTC (perp) avant le début | Corrélation avec l'erreur de début | Pente ($ d'erreur par $ de mouvement) |
|---|---|---|
| 5 s | +0.37 | +0.73 |
| 15 s | +0.63 | +0.70 |
| 30 s | +0.85 | +0.68 |
| 60 s | +0.90 | +0.48 |

Test sur cycles futurs (appris sur la 1re moitié, testé sur la 2e, mouvement 15 s) : erreur absolue moyenne 14.7 $ sans correction → 11.2 $ avec correction.