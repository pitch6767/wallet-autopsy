# Contrôle de robustesse du modèle E (TWAP fin quantiles) contre A (TWAP fin original) — BTC, 850 cycles (07.10 08:00 → 10.10 07:15)

Apprentissage avant le 08.10 22:00 ; validation 08.10 22:00 → 09.10 23:36 ; nuit du 10.10 à part. Tables E : exactement celles du bot. Écart Bybit → Chainlink recalculé à chaque seconde.

## 1. Décalages de calcul et d'exécution (sans fuite)

δ négatif : le moteur calcule avec des données plus vieilles de |δ|. δ positif : décision avec les données de l'instant, achat |δ| plus tard au prix du carnet de ce moment.

| Décalage | Modèle | Période | Achats | Gagnés | Résultat | Creux | Pertes de suite | Jackpots |
|---|---|---|---|---|---|---|---|---|
| -1.0 s | A | apprentissage | 125 | 26 % | **+157 $** | −458 $ | 12 | 9 |
| -1.0 s | A | validation | 77 | 30 % | **+362 $** | −628 $ | 8 | 6 |
| -1.0 s | A | nuit 10.10 | 29 | 41 % | **−195 $** | −446 $ | 6 | 2 |
| -1.0 s | E | apprentissage | 109 | 39 % | **+523 $** | −360 $ | 7 | 4 |
| -1.0 s | E | validation | 67 | 46 % | **+866 $** | −301 $ | 7 | 5 |
| -1.0 s | E | nuit 10.10 | 29 | 55 % | **+205 $** | −336 $ | 4 | 2 |
| -0.5 s | A | apprentissage | 113 | 26 % | **+503 $** | −396 $ | 12 | 8 |
| -0.5 s | A | validation | 68 | 32 % | **+255 $** | −647 $ | 7 | 5 |
| -0.5 s | A | nuit 10.10 | 30 | 43 % | **−140 $** | −382 $ | 6 | 2 |
| -0.5 s | E | apprentissage | 97 | 38 % | **+83 $** | −416 $ | 7 | 6 |
| -0.5 s | E | validation | 59 | 44 % | **+1 159 $** | −239 $ | 7 | 6 |
| -0.5 s | E | nuit 10.10 | 29 | 55 % | **+204 $** | −322 $ | 4 | 2 |
| +0.0 s | A | apprentissage | 84 | 43 % | **+1 073 $** | −160 $ | 5 | 11 |
| +0.0 s | A | validation | 57 | 47 % | **+887 $** | −215 $ | 5 | 8 |
| +0.0 s | A | nuit 10.10 | 28 | 36 % | **−182 $** | −322 $ | 8 | 3 |
| +0.0 s | E | apprentissage | 77 | 51 % | **+1 264 $** | −136 $ | 4 | 9 |
| +0.0 s | E | validation | 51 | 51 % | **+935 $** | −141 $ | 4 | 6 |
| +0.0 s | E | nuit 10.10 | 25 | 44 % | **−95 $** | −280 $ | 3 | 2 |
| +0.5 s | A | apprentissage | 84 | 43 % | **+1 175 $** | −249 $ | 5 | 7 |
| +0.5 s | A | validation | 57 | 47 % | **+1 279 $** | −192 $ | 5 | 4 |
| +0.5 s | A | nuit 10.10 | 28 | 36 % | **−350 $** | −364 $ | 8 | 1 |
| +0.5 s | E | apprentissage | 77 | 51 % | **+1 270 $** | −150 $ | 4 | 5 |
| +0.5 s | E | validation | 51 | 51 % | **+1 115 $** | −180 $ | 4 | 4 |
| +0.5 s | E | nuit 10.10 | 25 | 44 % | **−19 $** | −232 $ | 3 | 1 |
| +1.0 s | A | apprentissage | 84 | 43 % | **−25 $** | −344 $ | 5 | 6 |
| +1.0 s | A | validation | 57 | 47 % | **+620 $** | −313 $ | 5 | 3 |
| +1.0 s | A | nuit 10.10 | 28 | 36 % | **−354 $** | −495 $ | 8 | 1 |
| +1.0 s | E | apprentissage | 76 | 51 % | **+518 $** | −339 $ | 4 | 5 |
| +1.0 s | E | validation | 51 | 51 % | **+577 $** | −215 $ | 4 | 3 |
| +1.0 s | E | nuit 10.10 | 25 | 44 % | **+70 $** | −311 $ | 3 | 1 |

### Résumé : E − A (validation + nuit) selon le décalage

| Décalage | A | E | E − A |
|---|---|---|---|
| -1.0 s | +167 $ | +1 071 $ | **+904 $** |
| -0.5 s | +115 $ | +1 362 $ | **+1 247 $** |
| +0.0 s | +705 $ | +840 $ | **+135 $** |
| +0.5 s | +929 $ | +1 096 $ | **+167 $** |
| +1.0 s | +266 $ | +647 $ | **+381 $** |

## 2. Décomposition de l'écart E − A en validation (décalage 0)

Écart total : **+48 $** (A +887 $, E +935 $).

| Composante | Cycles | Résultat A | Résultat E | Contribution à E − A |
|---|---|---|---|---|
| communs, même côté, même instant | 32 | +459 $ | +459 $ | **+0 $** |
| communs, même côté, instant différent (prix différent) | 15 | +488 $ | +361 $ | **−128 $** |
| communs, côtés opposés | 4 | +13 $ | +116 $ | **+103 $** |
| A seul achète (E s'abstient) | 6 | −73 $ | — | **+73 $** |
| E seul achète | 0 | — | +0 $ | **+0 $** |

Dans les cycles où **seul A achète** : 5 pertes évitées par E (−77 $), 1 gains sacrifiés (+4 $), dont 1 jackpots (+4 $).
Dans les cycles où **seul E achète** : 0 gagnés (+0 $), 0 perdus (+0 $), dont 0 jackpots.
Les 3 plus grosses contributions à l'écart : 09.10 00:15 (−206 $), 09.10 09:10 (−164 $), 09.10 23:15 (+151 $).

## 3. Par journée (heure suisse) et incertitude statistique

| Journée | Cycles | A | E | E − A |
|---|---|---|---|---|
| 07.10 | 191 | +372 $ | +491 $ | **+119 $** |
| 08.10 | 288 | +879 $ | +971 $ | **+92 $** |
| 09.10 | 284 | +740 $ | +751 $ | **+11 $** |
| 10.10 | 87 | −213 $ | −108 $ | **+105 $** |

Validation + nuit (395 cycles) : E − A = **+135 $**. Bootstrap par blocs d'une heure (12 cycles, 10 000 tirages) : intervalle à 90 % [−678 $ ; +927 $] ; probabilité que l'écart soit ≤ 0 : **38 %**.

## 4. Les tables E sont-elles figées et apprises seulement sur l'apprentissage ?

- Le script d'export n'utilise que `TR = [m for m in M if per(m["st"]) == "apprentissage"]` : oui.
- Effectifs des tables (somme des cases « * ») : 29102 mesures, à comparer aux mesures d'apprentissage seules.
- Dans le bot, `QTWAP` est une constante importée d'un fichier ; aucun code ne la modifie (vérifié : aucune affectation à QTWAP dans index.js).
- Le dernier cycle d'apprentissage commence le 08.10 21:55 ; son prix final est publié avant le premier cycle de validation (08.10 22:00).
- Contrôle automatique : affectations à QTWAP trouvées dans index.js = 0.