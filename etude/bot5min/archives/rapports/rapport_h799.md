# Bot95 — H799 / H800 : compléter après un fill partiel — rapport préliminaire du 11.10.2026

Étude hors ligne uniquement. R4 et les fantômes gelés sont inchangés. Aucun ordre réel. La période réservée (≥ 13.10) n'a pas été lue.

**Données :** 157 signaux, 31 cycles.
- Apprentissage : 15 cycles, avant 10:55 UTC.
- Test : 16 cycles non vus.
- Les seuils ont été choisis **uniquement sur l'apprentissage**, puis mesurés une seule fois sur le test.

**Règles communes, celles de R4 :**
- Plafond au prix du signal + 2 c.
- Probabilité recalculée − prix − frais ≥ 0,05.
- Exécution 164 ms après l'envoi.
- Budget de 50 $ par signal.

Toutes les parts comptées sont exécutables contre le carnet enregistré au moment de l'exécution (quantité affichée, budget restant, frais).

**Reconstruction depuis R4 en direct :** possible sans nouveau fantôme. R4 enregistre chaque tentative : heure, probabilité, plafond, meilleur vendeur et sa taille, parts, coût. Pour H800, la reconstruction est approchée quand un fill de R4 a été limité par le budget.

## 1. B0 / B1 / B2 — TEST (16 cycles non vus)

Réglages retenus sur l'apprentissage :
- **B1 :** profondeur au signal ≥ 25 $ (choisi parmi 6 réglages).
- **B2 :** profondeur ≤ plafond à la relance ≥ 25 $ et avantage recalculé ≥ 0,20 (choisi parmi 16 réglages).

| Politique | P&L | 1res parts | Compléments | Parts compl. | Prix moy. compl. | vs D (IC 90 % / signal) | vs B0 | Complétés G / P | Jackpots | Drawdown |
|---|---|---|---|---|---|---|---|---|---|---|
| D sans relance | +3 903 $ | +3 903 | 0 | 0 | — | — | −564 | — | — | 693 |
| **B0** | **+4 467 $** | +3 903 | **+564** | 1 364 | 0,179 | +564 [+0,9 ; +14,2] | 0 | 8 / 6 | 4 | 700 |
| B1 ≥ 25 $ | +4 173 $ | +3 903 | +269 | 471 | 0,271 | +269 [+1,1 ; +5,9] | −294 | 5 / 1 | 2 | 693 |
| B2 (25 $, 0,20) | +4 363 $ | +3 903 | +459 | 1 148 | 0,157 | +459 [−0,2 ; +12,7] | −104 [−3,0 ; −0,1] | 6 / 4 | 4 | 696 |

**Ce que montrent les filtres :**
- B1 rend le complément plus sûr : 5 gagnants pour 1 perdant, et l'IC est plus étroit. Mais il rapporte moins que B0.
- B2 fait moins bien que B0 sur le test.
- Aucun filtre ne bat B0.

**Concentration :** les 5 meilleurs compléments font environ 90 % ou plus du gain des compléments.

## 2. H800 — Taille du complément (test)

| Complément ≤ x % du budget restant | P&L compl. | vs D (IC 90 % / signal) | vs B0 |
|---|---|---|---|
| 25 % | +149 $ | +149 [+0,2 ; +3,6] | −415 |
| 50 % | +299 $ | +299 [+0,5 ; +7,4] | −265 |
| 75 % | +439 $ | +439 [+0,7 ; +11,5] | −125 |
| **100 % (= B0)** | **+564 $** | +564 [+0,9 ; +14,1] | 0 |

Le gain est presque linéaire avec la taille : chaque dollar de complément rapporte à peu près autant. Réduire la taille réduit le gain, et l'incertitude aussi. Le drawdown est identique, autour de 700.

## 3. Sensibilité, sur tout l'échantillon

| Hypothèse | B0 − D | IC 90 % / signal |
|---|---|---|
| Frais normaux, 164 ms | +588 $ | [+0,45 ; +7,6] |
| Frais × 1,5 | +537 $ | [+0,23 ; +7,1] |
| Frais × 2 | +530 $ | [+0,27 ; +7,0] |
| **Latence 250 ms** | **+171 $** | **[−1,9 ; +4,6]** |
| **Latence 500 ms** | **+309 $** | **[−0,4 ; +4,7]** |

Les frais comptent peu. La latence compte : le gain n'est plus démontré dès 250 ms.

## 4. Verdict sur les cycles de test, avec correction des comparaisons multiples

Correction de Bonferroni sur 7 comparaisons.

| Comparaison | Écart / signal | IC 90 % simple | IC corrigé | Verdict |
|---|---|---|---|---|
| B0 − D | +7,05 $ | [+0,9 ; +14,4] | [−0,7 ; +18,0] | positif sans correction seulement |
| **B1 ≥ 25 $ − D** | **+3,37 $** | **[+1,1 ; +5,8]** | **[+0,2 ; +7,2]** | **seul positif après correction** |
| B2 − D | +5,74 $ | [−0,1 ; +12,9] | [−1,0 ; +16,7] | non démontré |
| H800 25 / 50 / 75 % − D | +1,9 / +3,7 / +5,5 $ | tous > 0 | tous contiennent 0 | positifs sans correction seulement |

**Conclusion :**
- Compléter après un fill partiel est **probablement utile**, mais le gain est modeste et concentré.
- B0 rapporte le plus. B1 (profondeur au signal ≥ 25 $) est le seul résultat qui reste positif après correction, mais il rapporte moins.
- Le gain dépend de la latence : il faut 164 ms.
- La validation reste à faire sur R4 en direct (cycles nouveaux), puis sur la période réservée du 13.10. **Rien n'est lancé.**

Détail : etude/bot5min/resultat_completion_h799.md
