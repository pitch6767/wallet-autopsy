# Contrôle de robustesse du modèle E (TWAP fin quantiles) contre A (TWAP fin original) — BTC, 2005 cycles (07.10 08:00 → 14.10 07:45)

Apprentissage avant le 08.10 22:00 ; validation 08.10 22:00 → 09.10 23:36 ; nuit du 10.10 à part. Tables E : exactement celles du bot. Écart Bybit → Chainlink recalculé à chaque seconde.

## 1. Décalages de calcul et d'exécution (sans fuite)

δ négatif : le moteur calcule avec des données plus vieilles de |δ|. δ positif : décision avec les données de l'instant, achat |δ| plus tard au prix du carnet de ce moment.

| Décalage | Modèle | Période | Achats | Gagnés | Résultat | Creux | Pertes de suite | Jackpots |
|---|---|---|---|---|---|---|---|---|
| -1.0 s | A | apprentissage | 125 | 26 % | **+157 $** | −458 $ | 12 | 9 |
| -1.0 s | A | validation | 77 | 30 % | **+362 $** | −628 $ | 8 | 6 |
| -1.0 s | A | nuit 10.10 | 41 | 34 % | **−456 $** | −510 $ | 6 | 2 |
| -1.0 s | A | inédit (après 10.10 10:25) | 276 | 31 % | **−1 413 $** | −1 813 $ | 17 | 14 |
| -1.0 s | E | apprentissage | 109 | 39 % | **+523 $** | −360 $ | 7 | 4 |
| -1.0 s | E | validation | 67 | 46 % | **+866 $** | −301 $ | 7 | 5 |
| -1.0 s | E | nuit 10.10 | 40 | 42 % | **−34 $** | −336 $ | 6 | 2 |
| -1.0 s | E | inédit (après 10.10 10:25) | 254 | 33 % | **−2 390 $** | −3 064 $ | 14 | 5 |
| -0.5 s | A | apprentissage | 113 | 26 % | **+503 $** | −396 $ | 12 | 8 |
| -0.5 s | A | validation | 68 | 32 % | **+255 $** | −647 $ | 7 | 5 |
| -0.5 s | A | nuit 10.10 | 42 | 36 % | **−363 $** | −417 $ | 6 | 2 |
| -0.5 s | A | inédit (après 10.10 10:25) | 264 | 28 % | **−1 958 $** | −2 328 $ | 13 | 14 |
| -0.5 s | E | apprentissage | 97 | 38 % | **+83 $** | −416 $ | 7 | 6 |
| -0.5 s | E | validation | 59 | 44 % | **+1 159 $** | −239 $ | 7 | 6 |
| -0.5 s | E | nuit 10.10 | 39 | 44 % | **+7 $** | −322 $ | 6 | 2 |
| -0.5 s | E | inédit (après 10.10 10:25) | 246 | 33 % | **−2 312 $** | −3 014 $ | 14 | 7 |
| +0.0 s | A | apprentissage | 84 | 43 % | **+1 073 $** | −160 $ | 5 | 11 |
| +0.0 s | A | validation | 57 | 47 % | **+887 $** | −215 $ | 5 | 8 |
| +0.0 s | A | nuit 10.10 | 40 | 30 % | **−409 $** | −533 $ | 8 | 3 |
| +0.0 s | A | inédit (après 10.10 10:25) | 211 | 37 % | **+1 615 $** | −806 $ | 13 | 21 |
| +0.0 s | E | apprentissage | 77 | 51 % | **+1 264 $** | −136 $ | 4 | 9 |
| +0.0 s | E | validation | 51 | 51 % | **+935 $** | −141 $ | 4 | 6 |
| +0.0 s | E | nuit 10.10 | 35 | 34 % | **−296 $** | −392 $ | 6 | 2 |
| +0.0 s | E | inédit (après 10.10 10:25) | 198 | 41 % | **+547 $** | −662 $ | 12 | 15 |
| +0.5 s | A | apprentissage | 84 | 43 % | **+1 175 $** | −249 $ | 5 | 7 |
| +0.5 s | A | validation | 57 | 47 % | **+1 279 $** | −192 $ | 5 | 4 |
| +0.5 s | A | nuit 10.10 | 40 | 30 % | **−554 $** | −566 $ | 8 | 1 |
| +0.5 s | A | inédit (après 10.10 10:25) | 210 | 37 % | **+993 $** | −1 122 $ | 13 | 11 |
| +0.5 s | E | apprentissage | 77 | 51 % | **+1 270 $** | −150 $ | 4 | 5 |
| +0.5 s | E | validation | 51 | 51 % | **+1 115 $** | −180 $ | 4 | 4 |
| +0.5 s | E | nuit 10.10 | 35 | 34 % | **−205 $** | −262 $ | 6 | 1 |
| +0.5 s | E | inédit (après 10.10 10:25) | 197 | 41 % | **+844 $** | −667 $ | 12 | 8 |
| +1.0 s | A | apprentissage | 84 | 43 % | **−25 $** | −344 $ | 5 | 6 |
| +1.0 s | A | validation | 57 | 47 % | **+620 $** | −313 $ | 5 | 3 |
| +1.0 s | A | nuit 10.10 | 40 | 30 % | **−524 $** | −662 $ | 8 | 1 |
| +1.0 s | A | inédit (après 10.10 10:25) | 210 | 38 % | **+148 $** | −1 139 $ | 13 | 9 |
| +1.0 s | E | apprentissage | 76 | 51 % | **+518 $** | −339 $ | 4 | 5 |
| +1.0 s | E | validation | 51 | 51 % | **+577 $** | −215 $ | 4 | 3 |
| +1.0 s | E | nuit 10.10 | 35 | 34 % | **−94 $** | −372 $ | 6 | 1 |
| +1.0 s | E | inédit (après 10.10 10:25) | 198 | 41 % | **−195 $** | −804 $ | 12 | 6 |

### Résumé : E − A (validation + nuit) selon le décalage

| Décalage | A | E | E − A |
|---|---|---|---|
| -1.0 s | −1 507 $ | −1 558 $ | **−51 $** |
| -0.5 s | −2 066 $ | −1 146 $ | **+920 $** |
| +0.0 s | +2 093 $ | +1 186 $ | **−906 $** |
| +0.5 s | +1 717 $ | +1 754 $ | **+36 $** |
| +1.0 s | +244 $ | +287 $ | **+44 $** |

### Verdict limité aux cycles INÉDITS (après 10.10 10:25) : E − A selon le décalage

| Décalage | A | E | E − A |
|---|---|---|---|
| -1.0 s | −1 413 $ | −2 390 $ | **−977 $** |
| -0.5 s | −1 958 $ | −2 312 $ | **−353 $** |
| +0.0 s | +1 615 $ | +547 $ | **−1 068 $** |
| +0.5 s | +993 $ | +844 $ | **−149 $** |
| +1.0 s | +148 $ | −195 $ | **−344 $** |

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
| 10.10 | 288 | −244 $ | +59 $ | **+303 $** |
| 11.10 | 288 | +128 $ | +31 $ | **−97 $** |
| 12.10 | 288 | +1 419 $ | −88 $ | **−1 506 $** |
| 13.10 | 285 | +34 $ | +413 $ | **+379 $** |
| 14.10 | 93 | −162 $ | −177 $ | **−15 $** |

Validation + nuit (1550 cycles) : E − A = **−906 $**. Bootstrap par blocs d'une heure (12 cycles, 10 000 tirages) : intervalle à 90 % [−3 407 $ ; +1 102 $] ; probabilité que l'écart soit ≤ 0 : **71 %**.

## 4. Les tables E sont-elles figées et apprises seulement sur l'apprentissage ?

- Le script d'export n'utilise que `TR = [m for m in M if per(m["st"]) == "apprentissage"]` : oui.
- Effectifs des tables (somme des cases « * ») : 29102 mesures, à comparer aux mesures d'apprentissage seules.
- Dans le bot, `QTWAP` est une constante importée d'un fichier ; aucun code ne la modifie (vérifié : aucune affectation à QTWAP dans index.js).
- Le dernier cycle d'apprentissage commence le 08.10 21:55 ; son prix final est publié avant le premier cycle de validation (08.10 22:00).
- Contrôle automatique : affectations à QTWAP trouvées dans index.js = 0.