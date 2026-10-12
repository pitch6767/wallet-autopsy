# Bot95 — R4 « retry engine » et H776–H778 — 11.10.2026

Aucun ordre réel. Aucun fantôme gelé modifié. La période réservée (≥ 13.10) n'est pas utilisée pour choisir les paramètres.

## 1. Fantôme R4 lancé à Dublin (version 745c04da7099, vers 15:30 UTC)

- **Signaux :** exactement les signaux Bot95 existants, sans changement de leurs règles.
- **Tentatives :** une première à la décision, exécutée contre le carnet après le trajet + 150 ms (≈ 164 ms). Ensuite, nouvelle tentative toutes les 500 ms pendant 5 s, soit 10 tentatives au maximum.
- **Prix :** plafond = prix du signal + 2 c.
- **Condition d'achat :** avant chaque envoi, probabilité recalculée avec les données reçues à cet instant. On n'achète que si probabilité − prix − frais ≥ 0,05.
- **Taille :** budget de 50 $ par signal, fills partiels cumulés.
- **Pas de double comptage :** un champ « doublon » marque une position déjà exécutée sur le même cycle et le même côté. Le résultat officiel ne la compte qu'une fois.

**Comparaisons mesurées en direct sur les mêmes signaux :**

| Variante | Plafond | Probabilité utilisée | Relances |
|---|---|---|---|
| R4 | +2 c | recalculée | oui |
| R4 +1 c | +1 c | recalculée | oui |
| R4 prix initial | +0 c | recalculée | oui |
| R4 +2 c sans recalcul | +2 c | figée au signal | oui |
| preneur immédiat (Bot95 actuel) | +0 c | aucune condition | non |

**H776 en direct :** après une disparition, on enregistre le délai de réapparition (au prix et à +2 c), le prix, la quantité et la probabilité recalculée.

## 2. Résultats hors ligne (157 signaux, 31 cycles, PRÉLIMINAIRE)

| Politique | Remplis | P&L | par signal (IC 90 %) | 2e moitié |
|---|---|---|---|---|
| Bot95 immédiat | 128 | +4 580 $ | +29,2 [+7,8 ; +54,5] | +47,8 |
| relance 5 s au prix initial | 132 | +5 088 $ | +32,4 | +52,0 |
| relance 5 s, +1 c | 137 | +5 029 $ | +32,0 | +53,1 |
| **R4 (5 s, +2 c, recalcul)** | 137 | **+5 341 $** | +34,0 [+7,6 ; +60,7] | +55,6 |
| 5 s, +2 c, modèle figé | 138 | +5 754 $ | +36,7 | +60,6 |
| M4 / M8 (vivants, 16 mêmes cycles) | — | +190 / +453 $ | — | — |

**Livrables :**

1. **R4 contre Bot95 :** +761 $. IC 90 % de la différence par signal [−3,5 ; +12,9]. **Gain non démontré.**
2. **Offres récupérées :** 10 signaux. **2 gagnants et 8 perdants.**
3. **Quantité récupérée :** 13 628 parts de plus, pour 1 937 $ (coût des relances). Résultat de ces parts : +1 181 $. Elles s'ajoutent surtout à des signaux déjà en partie remplis.
4. **Jackpots récupérés :** 2.
5. **Nouveaux perdants :** 8.
6. **Décisions uniques (45) :** Bot95 +965 $, R4 +1 008 $. Quasi identiques.
7. **Durée :** 1 s fait déjà l'essentiel (+5 141 $ à +2 c). 5 s n'ajoute que +200 $.
8. **Plafond :** +2/+3 c > +0 c, de façon régulière mais faible.
9. **Recalcul du modèle :** il **retire** 400 à 500 $, car la condition refuse un gros gagnant (+420 $). Il n'est pas utile sur cet échantillon.

## 3. H776 — Ce qui réapparaît est moins bon

| Offre disparue (110 signaux) | Signaux | Délai médian | Taux de gain |
|---|---|---|---|
| revient au prix du signal | 36 | 1,2 s | 53 % |
| revient à ≤ +2 c | 83 | 25 ms | 41 % |
| **ne revient jamais** | **27** | — | **81 %** |

**Fait majeur :** les offres qui ne reviennent pas sont les meilleurs signaux. Les vendeurs savent. Relancer récupère surtout des offres remises en vente parce que le marché est parti dans l'autre sens. C'est de la sélection adverse.

## 4. H777 — Relance systématique ou conditionnelle (2e moitié)

| Politique | P&L |
|---|---|
| Bot95 immédiat | +3 827 $ |
| relance systématique | +4 847 $ |
| relance conditionnelle (R4) | +4 445 $ |
| relance si réapparition probable | +4 445 $ |

Les intervalles de confiance se recouvrent. Aucune politique n'est démontrée meilleure.

## 5. Verdict statistique

**Amélioration NON démontrée.** Le gain de R4 vient d'une quantité supplémentaire sur des signaux déjà remplis, pas de la récupération d'offres perdues (8 perdants sur 10). Le fantôme R4 vivant donnera la vraie mesure hors échantillon. Le verdict se fera sur des cycles nouveaux et la période réservée du 13.10.

Détails : etude/bot5min/resultat_retry_h776.md
