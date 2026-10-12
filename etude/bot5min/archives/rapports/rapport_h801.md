# Bot95 — H801 à H803 et validation future de B0 / B1 — rapport du 11.10.2026

Étude hors ligne. Aucun ordre. R4 et les fantômes gelés sont inchangés. B0 et B1 sont **figés** : aucun seuil n'a été ré-optimisé. La période réservée (≥ 13.10) n'a pas été lue.

- **D** = 1re tentative de R4 seule, sans relance.
- **B0** = on complète par les relances de R4 après tout fill partiel.
- **B1** = comme B0, mais seulement si la profondeur affichée au signal est d'au moins 25 $.

Vérification : aucune part simulée ne dépasse la quantité réellement affichée au plafond au moment de l'exécution.

## 1. H801 — Dépendance aux gros gains

Cycles de test (16 cycles non vus) :

| | B0 | B1 |
|---|---|---|
| P&L total | +4 467 $ | +4 173 $ |
| dont compléments | +564 $ | +269 $ |
| 1 / 3 / 5 meilleurs compléments | +222 / +371 / +505 $ | +75 / +216 / +280 $ |
| Compléments sans le meilleur | +342 $ | +194 $ |
| Compléments sans les 3 meilleurs | +193 $ | +53 $ |
| Compléments sans les 5 meilleurs | **+59 $** | **−10 $** |
| Compléments gagnants / perdants | 8 / 6 | 5 / 1 |
| Expected Shortfall 10 % (par signal complété) | −16 $ | −10 $ |
| Drawdown total | 700 | 693 |

Sur toute la journée, les gains des compléments B0 se concentrent sur les billets à 0,10–0,35 : +475 $ sur +588 $.

**Conclusion :** sans les 5 meilleurs compléments, le gain disparaît presque (B0) ou devient négatif (B1). B1 limite les pertes (moins de perdants, Expected Shortfall plus faible) mais dépend tout autant des gros gains.

## 2. H802 — Migration des fills selon la latence (B0, toute la journée)

| Latence | D | Compléments | B0 total | Signaux complétés | Offres visibles à l'envoi mais parties à l'exécution |
|---|---|---|---|---|---|
| 164 ms | +4 775 $ | +588 $ | +5 363 $ | 24 | 4 % |
| 250 ms | +4 130 $ | +171 $ | +4 301 $ | 21 | 6 % |
| 500 ms | +3 397 $ | +309 $ | +3 705 $ | 18 | 8 % |

**Décomposition de l'écart 164 ms → 250 ms (+1 063 $) :**

| Cause | Montant |
|---|---|
| 1re tentative (offres déjà parties) | +645 $ |
| Sélection des signaux complétés (8 signaux seulement à 164 ms, 5 seulement à 250 ms) | +318 $ |
| Quantité, sur les 16 signaux communs | +101 $ |
| Prix | −2 $ |

**Décomposition de l'écart 164 ms → 500 ms (+1 658 $) :**

| Cause | Montant |
|---|---|
| 1re tentative | +1 379 $ |
| Sélection des signaux complétés | +168 $ |
| Quantité | +124 $ |
| Prix | −12 $ |

**Conclusion :** la latence coûte par la **disponibilité des offres** (la 1re tentative trouve moins de quantité), puis par la **sélection** des signaux complétés. Le prix ne joue pas : le plafond limite déjà le prix payé.

## 3. H803 — Stabilité de la profondeur

Profondeur en $ au plafond (prix du signal + 2 c) :

| Instant | Médiane | 25e / 75e centiles | Corrélation avec la profondeur au signal |
|---|---|---|---|
| Au signal | 66 $ | 20 / 196 | — |
| Au 1er fill | 79 $ | 19 / 265 | +0,48 |
| Relance à 0,5 s | 67 $ | 0 / 283 | +0,31 |
| Relance à 1 s | 42 $ | 0 / 167 | +0,31 |
| Relance à 2 s | 32 $ | 0 / 171 | +0,30 |
| Relance à 4,5 s | 43 $ | 0 / 200 | +0,35 |

La profondeur au signal ne prédit que faiblement la profondeur pendant les relances (corrélation 0,3).

**Valeur de B1 après contrôles** (40 signaux avec 1er fill partiel ; régression du rendement par $ des compléments) :

| Variable | Coefficient | IC 90 % |
|---|---|---|
| Profondeur au signal ≥ 25 $ | +0,55 | [−0,19 ; +1,31] |
| Prix du signal | −0,36 | [−1,50 ; +0,26] |
| Temps restant | −0,33 | [−0,81 ; +0,56] |
| Volatilité | +0,22 | [−0,47 ; +1,23] |

Brut : +213 % par $ quand la profondeur au signal est ≥ 25 $, contre +68 % sinon. Après contrôle, l'effet de B1 reste positif mais **n'est pas démontré** (l'IC contient 0).

## 4. Validation future sur les cycles nouveaux de R4 en direct

Les politiques D, B0 et B1 se recalculent exactement à partir des tentatives enregistrées par R4. Le tableau se met à jour toutes les heures, sans aucun réglage modifié.

**À 16:24 UTC :** 24 signaux réglés, soit **8 décisions uniques sur 6 cycles**.

| Politique | P&L | Écart à D (IC 90 % / décision) |
|---|---|---|
| D | +100 $ | — |
| B0 | +45 $ | −55 $ [−14,9 ; 0,0] (2 compléments, tous deux perdants) |
| B1 | +100 $ | 0 (aucun complément déclenché) |

C'est encore beaucoup trop tôt pour conclure.

## 5. Verdict

**Aucune amélioration démontrée pour l'instant.**
- Hors ligne, sur les cycles de test : B0 − D est compris entre +1,1 et +14,2 $ par signal, et B1 − D entre +1,1 et +5,7 $.
- Mais ces gains disparaissent si l'on retire les 5 meilleurs compléments, et ils exigent 164 ms.
- Les premiers cycles en direct sont pour l'instant négatifs pour B0 (2 compléments perdants) et neutres pour B1.

On garde B0 et B1 figés. Le verdict se fera sur les cycles nouveaux de R4, puis sur la période réservée du 13.10.
