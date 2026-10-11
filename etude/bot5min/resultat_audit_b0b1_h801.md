# Bot95 — H801–H803 et validation future de B0 / B1 — PRÉLIMINAIRE

Généré le 11.10.2026 16:23 UTC. Hors ligne : 157 signaux, 31 cycles enregistrés à Dublin (test = cycles ≥ 10:55 UTC). B0 et B1 figés (B1 : profondeur au signal ≥ 25 $), aucun seuil ré-optimisé. Toutes les parts sont vérifiées ≤ quantité affichée au plafond à l'instant d'exécution (aucune violation).

## 1. H801 — Dépendance aux gros gains (compléments)

### test (cycles non vus)

| Politique | P&L total | dont compléments | 1 meilleur | 3 meilleurs | 5 meilleurs | compl. sans le meilleur | sans les 3 | sans les 5 | Complétés G / P | ES 10 % compl. / signal complété | Drawdown total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | +4467 | +564 | +222 | +371 | +505 | +342 | +193 | +59 | 8 / 6 | -16.0 | 700 |
| B1 | +4173 | +269 | +75 | +216 | +280 | +194 | +53 | -10 | 5 / 1 | -10.2 | 693 |

### tout

| Politique | P&L total | dont compléments | 1 meilleur | 3 meilleurs | 5 meilleurs | compl. sans le meilleur | sans les 3 | sans les 5 | Complétés G / P | ES 10 % compl. / signal complété | Drawdown total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | +5363 | +588 | +222 | +371 | +505 | +366 | +217 | +83 | 12 / 12 | -32.7 | 939 |
| B1 | +5178 | +403 | +75 | +216 | +323 | +328 | +187 | +80 | 8 / 1 | -10.2 | 900 |

**Compléments par prix du billet (tout)**

| Prix moyen du complément | B0 : signaux | B0 : P&L | B1 : signaux | B1 : P&L |
|---|---|---|---|---|
| 0.00–0.10 | 4 | +23 | 0 | +0 |
| 0.10–0.20 | 12 | +154 | 3 | +105 |
| 0.20–0.35 | 5 | +321 | 3 | +207 |
| 0.35–1.00 | 3 | +90 | 3 | +90 |

## 2. H802 — Migration des fills selon la latence (B0)

| Latence | D (1re tentative) | Compléments B0 | B0 total | Signaux complétés | Envois où l'offre visible à l'envoi a disparu à l'exécution |
|---|---|---|---|---|---|
| 164 ms | +4775 | +588 | +5363 | 24 | 36 / 1011 (4 %) |
| 250 ms | +4130 | +171 | +4301 | 21 | 58 / 1011 (6 %) |
| 500 ms | +3397 | +309 | +3705 | 18 | 84 / 1011 (8 %) |

**164 ms contre 250 ms** — écart B0 total +1063 $ =
- 1re tentative (offres déjà parties au moment d'exécuter = disponibilité) : +645 $
- sélection des signaux complétés : complétés seulement à 164 ms (8 signaux, +254 $) moins complétés seulement à 250 ms (5 signaux, -64 $) = +318 $
- sur les 16 signaux complétés aux deux délais : effet quantité +101 $, effet prix -2 $
- reste (arrondis, interaction) : +0 $

**164 ms contre 500 ms** — écart B0 total +1658 $ =
- 1re tentative (offres déjà parties au moment d'exécuter = disponibilité) : +1379 $
- sélection des signaux complétés : complétés seulement à 164 ms (12 signaux, +182 $) moins complétés seulement à 500 ms (6 signaux, +14 $) = +168 $
- sur les 12 signaux complétés aux deux délais : effet quantité +124 $, effet prix -12 $
- reste (arrondis, interaction) : -0 $

## 3. H803 — Stabilité de la profondeur et valeur de B1

Profondeur = $ affichés au plafond (prix + 2 c) du côté acheté.

| Instant | Médiane ($) | 25e / 75e centiles | Corrélation (rang) avec la profondeur au signal |
|---|---|---|---|
| au signal | 66 | 20 / 196 | +1.00 |
| au 1er fill (exécution de la 1re tentative) | 79 | 19 / 265 | +0.48 |
| à la relance 1 (envoi à 0.5 s) | 67 | 0 / 283 | +0.31 |
| à la relance 2 (envoi à 1.0 s) | 42 | 0 / 167 | +0.31 |
| à la relance 4 (envoi à 2.0 s) | 32 | 0 / 171 | +0.30 |
| à la relance 9 (envoi à 4.5 s) | 43 | 0 / 200 | +0.35 |

**B1 apporte-t-il quelque chose après contrôles ?** Signaux avec un 1er fill partiel (là où B0 et B1 diffèrent) : 40.

Régression (MCO) du rendement par $ des compléments B0, variables standardisées, IC 90 % par cycles :

| Variable | Coefficient | IC 90 % |
|---|---|---|
| prof0 ≥ 25 $ | +0.55 | [-0.19 ; +1.31] |
| prix du signal | -0.36 | [-1.50 ; +0.26] |
| temps restant | -0.33 | [-0.81 ; +0.56] |
| volatilité | +0.22 | [-0.47 ; +1.23] |

Brut : compléments quand profondeur au signal ≥ 25 $ : 17 signaux, +213 % par $ ; < 25 $ : 23 signaux, +68 % par $.

## 4. Validation future : B0 / B1 / D recalculés sur les cycles NOUVEAUX du fantôme R4 vivant

Signaux réglés avec R4 : 24 ; décisions uniques (1 par cycle et côté, sans double position) : 8 sur 6 cycles.

| Politique | P&L ($) | / décision | IC 90 % | vs D ($) | IC 90 % de l'écart / décision |
|---|---|---|---|---|---|
| D | +100 | +12.52 | [-30.47 ; +60.69] | +0 | [+0.00 ; +0.00] |
| B0 | +45 | +5.59 | [-32.34 ; +43.51] | -55 | [-14.85 ; +0.00] |
| B1 | +100 | +12.52 | [-30.47 ; +57.28] | +0 | [+0.00 ; +0.00] |

Trop peu de cycles pour conclure tant que l'IC contient 0 ; ce tableau se met à jour à chaque relance du script.

## 5. Verdict

- Hors ligne, cycles de test : B0 − D [+1.13 ; +14.16] $/signal ; B1 − D [+1.10 ; +5.72] $/signal.
- Le verdict final (B0, B1 ou aucune amélioration démontrée) ne sera donné que sur les cycles nouveaux de R4 puis la période réservée.
