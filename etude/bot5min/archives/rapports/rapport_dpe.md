# Bot95 — Dynamic Position Engine H841–H860 — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- Aucun bot ni fantôme modifié ; H816, H821 et R4 sont inchangés. La période réservée n'a pas été lue.
- Protocole et code enregistrés sur GitHub avant le calcul du test (commit 2cb9607).

**Données et découpage**
- Cycles enregistrés à Dublin, avec le carnet Polymarket rejoué seconde par seconde.
- Apprentissage : 169 cycles. Validation : 85 cycles.
- **Test inédit** : 42 cycles du 12.10 à partir de 06:00 UTC. Aucune étude ne les avait encore utilisés.
- Résultat officiel Chainlink pour tous les cycles.

**Règles de simulation**
- Budget : 50 $ de capital net par cycle, jamais dépassé.
- Une décision par seconde, de 10 à 290 s.
- Exécution 164 ms plus tard, au prix vu au moment de la décision au plus, et seulement sur les quantités affichées.
- La liquidité que nous avons prise reste indisponible 5 s.
- Frais à l'achat comme à la vente. Paires Up + Down fusionnées dès qu'elles existent.
- Aucun ordre maker : tous les makers testés précédemment étaient perdants.

**Même probabilité et même signal pour toutes les politiques**
- Probabilité : modèle de règlement Chainlink, recalibré sur l'apprentissage.
- Entrée au premier avantage net ≥ 0,05 après frais. Ce seuil a été choisi sur l'apprentissage.

## Réponse courte

**Aucune gestion dynamique ne bat le hold de façon robuste.** Sur la validation comme sur le test, la référence elle-même (achat unique et conservation) **perd** : −787 $ et −165 $. La probabilité utilisée n'a pas d'avantage hors apprentissage, et aucune façon de gérer la position ne peut en créer un.

Quatre mécanismes de protection **réduisent les pertes sur le test**, avec un IC corrigé positif, mais **pas sur la validation**. Ils ne sont donc pas démontrés.

## 1. Tableau des politiques (P&L en $, écart avec le hold A, IC 90 % corrigé pour 14 comparaisons)

| Politique | Apprentissage | Validation | Test inédit | Écart test vs A (IC corrigé) | Verdict |
|---|---|---|---|---|---|
| A — achat unique, hold (référence) | +214 | −787 | −165 | — | perd hors apprentissage |
| B — achats fractionnés à horaires fixes | −456 | −1 299 | −568 | −402 [−806 ; −59] | **pire que le hold, démontré** |
| C — hold + couverture statique 20 % | +109 | −651 | −164 | +2 [−245 ; +227] | rien |
| D — vente partielle simple | −110 | −732 | −168 | −2 | rien |
| G — abstention | 0 | 0 | 0 | +165 [−794 ; +949] | — |
| H857 — échelle conditionnelle | +53 | −193 | −4 | +162 [−403 ; +707] | non démontré |
| H842 — achat sur repli | +154 | −550 | −197 | −31 | rien |
| H854a — vendre 50 % de la jambe | +49 | −819 | −151 | +14 | rien |
| H854b — acheter l'opposé | +194 | −820 | −141 | **+24 [+1 ; +59]** | test seul, pas validation |
| H851/H858 — rotations achat/vente | −296 | −532 | −445 | −280 [−797 ; +178] | **perd de l'argent** |
| H849 — verrou de paire | −156 | −745 | −6 | **+159 [+20 ; +349]** | test seul, pas apprentissage ni validation |
| H850 — cliquet | −55 | −620 | −184 | −19 | rien |
| H852 — couverture au retournement (carnet) | +112 | −819 | −131 | **+34 [+4 ; +75]** | test seul |
| H856 — couverture avant la moyenne finale | +229 | −774 | −109 | **+57 [+18 ; +107]** | test seul |
| H859/H847 — DPE complet | −174 | −64 | −262 | −97 [−1 109 ; +903] | non démontré, 257 transactions |

**H848, combinaison** : non construite. La règle pré-enregistrée exige qu'un composant batte le hold sur la validation **et** sur le test. Aucun n'y arrive.

## 2. Livrables détaillés

**Journal d'inventaire seconde par seconde** (DPE, test) : resultat_dpe_h841_journal.csv.gz, 1 774 lignes (action, parts Up et Down, trésorerie, probabilité).

**Achats fractionnés.** À horaires fixes (B), c'est le pire choix : −402 $ contre le hold, démontré. Une échelle conditionnée à l'avantage (H857) est neutre.

**Rotations** (H851/H858). Elles font −280 $ sur le test et −510 $ sur l'apprentissage. Les frais doublent (113 $ contre 55 $) : chaque aller-retour paie deux fois l'écart et les frais.

**Couvertures et vente d'une jambe**
- Acheter l'opposé (H854b) fait légèrement mieux que vendre une partie de la jambe (H854a) : +24 $ contre +14 $ sur le test.
- Les deux ne font qu'écrêter la perte.
- La couverture statique (C) ne change rien.

**Paires verrouillées** (H849). 501 paires fusionnées sur le test. Le nombre de cycles gagnants passe de 7 à 13, et la perte de −165 $ à −6 $. Mais sur l'apprentissage, le verrou coûte −371 $ : il plafonne aussi les gains.

**Capital et risque**
- Capital maximal : 50 $ pour toutes les politiques.
- Pire cycle : −50 $, partout.
- Drawdown sur le test : 278 $ pour A, 227 $ pour H849, 206 $ pour H857, 570 $ pour B.

**Jackpots** (cycles à au moins +50 $). Sur le test : 6 pour A, 6 pour H849 et C, mais seulement 2 pour les rotations et 3 pour le DPE complet.

**Frais et latence** (test)

| Variante | A | DPE | H849 |
|---|---|---|---|
| 164 ms (référence) | −165 $ | −262 $ | −6 $ |
| 300 ms | −292 $ | −257 $ | −125 $ |
| 500 ms | −263 $ | −517 $ | −136 $ |

**Une observation de sensibilité.** Avec la probabilité de règlement **non recalibrée**, A fait +667 $ sur la validation et +229 $ sur le test, contre −787 $ et −165 $ recalibrée. Ce n'était pas l'hypothèse principale du protocole. Je le note comme piste à pré-enregistrer, **sans en tirer de conclusion**.

## 3. Carte des occasions (H855)

Les secondes avec un avantage exécutable ≥ 0,05 sont fréquentes. Le tableau complet par temps restant est dans le fichier de résultats. Le problème n'est pas de trouver des occasions, c'est que la probabilité ne prévoit pas mieux que le prix.

## 4. Verdict et décision proposée

| Famille | Décision |
|---|---|
| Achats fractionnés à horaires fixes (B) | **Abandonner** : pire que le hold, démontré |
| Rotations achat/vente (H851/H858) | **Abandonner** : perdantes partout |
| DPE complet (H859/H847) | **Abandonner pour l'instant** : beaucoup de transactions, aucun gain |
| Verrou de paire, couvertures H852/H856, achat de l'opposé H854b | **Approfondir** : ils écrêtent les pertes sur le test, mais pas sur la validation. À pré-enregistrer tels quels et à juger sur des cycles nouveaux. |
| Échelle conditionnelle H857, vente partielle, cliquet, repli, couverture statique | Rien de démontré |

**La leçon principale.** Gérer la position ne crée pas d'avantage quand la probabilité n'en a pas. La priorité reste de trouver une probabilité qui bat le prix du marché. C'est l'objet de H917–H972, et en premier H971/H972 (pression contre capacité).

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_dpe_h841.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/dpe_h841.py
