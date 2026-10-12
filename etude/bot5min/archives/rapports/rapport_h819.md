# Bot95 — H819 / H820 / H821 : calibration, gagnants contre perdants, filtres qui gardent les jackpots — rapport du 11.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel, aucun déploiement.
- R4, H816 et les fantômes sont inchangés. La période réservée du 13.10 n'a pas été lue.
- Protocole et code versionnés avant le calcul (commit ad2208f). Résultats : commit 42eb8ac.

**Données et méthode**
- 77 décisions uniques (première décision par cycle × côté) sur 55 cycles enregistrés à Dublin, dont 62 dans la plage H816 (prix 0,20–0,50).
- Mise de 20 $, exécution 164 ms après la décision, mêmes frais et quantités que H816.
- Découpage chronologique : apprentissage = cycles avant 12:30 UTC (41 décisions), test = cycles après (36 décisions).
- IC à 90 % calculés par cycle. Correction de Bonferroni pour les 10 variables de H820. La règle H821 est choisie sur l'apprentissage, puis mesurée **une seule fois** sur le test.

## 1. H819 — Bot95 est moins bien calibré que le marché

**Toutes les décisions uniques enregistrées (144 décisions, 107 cycles)**

| | Brier (plus bas = mieux) | Log loss |
|---|---|---|
| Probabilité Bot95 | 0,217 | 0,630 |
| Prix payé (probabilité implicite) | **0,206** | **0,596** |

| Probabilité Bot95 | Décisions | Bot95 moyen | Prix moyen | Victoire observée |
|---|---|---|---|---|
| 0,3–0,4 | 21 | 0,36 | 0,15 | 19 % |
| 0,4–0,5 | 82 | 0,45 | 0,24 | 32 % |
| 0,5–0,7 | 24 | 0,58 | 0,35 | 54 % |
| 0,7–1,0 | 13 | 0,82 | 0,61 | 69 % |

La victoire observée se situe **entre** le prix et la probabilité Bot95, plus près du prix. Bot95 surestime systématiquement ses chances, d'environ 13 à 20 points. Le prix sous-estime un peu : c'est de là que vient l'avantage modeste.

**Par temps restant**

| Temps restant | Décisions | Bot95 | Prix | Victoire | Brier Bot95 / prix |
|---|---|---|---|---|---|
| 60–120 s | 21 | 0,45 | 0,21 | **14 %** | 0,182 / **0,093** |
| 120–180 s | 31 | 0,48 | 0,26 | 32 % | 0,182 / 0,156 |
| 180–240 s | 41 | 0,50 | 0,29 | 44 % | 0,255 / 0,275 |
| 240–301 s | 51 | 0,50 | 0,29 | 41 % | 0,223 / 0,229 |

À moins de 2 minutes, Bot95 est nettement trompé : il annonce 45 %, le marché 21 %, et on gagne 14 %. Au-delà de 3 minutes, Bot95 et le prix se valent, et on gagne plus que le prix ne l'indique.

**Test Dublin (36 décisions)**

| Estimateur | Brier test | Log loss test |
|---|---|---|
| Bot95 | 0,265 | 0,752 |
| Milieu du carnet Polymarket | 0,234 | 0,662 |
| Prix payé | **0,233** | **0,660** |
| Combinaison Bot95 + milieu (apprise) | 0,249 | 0,724 |

La combinaison, meilleure sur l'apprentissage, ne bat pas le prix sur le test.

## 2. H820 — Aucune différence démontrée entre gagnants et perdants

À prix et temps restant égaux, aucune des 10 variables observables au signal ne distingue les gagnants des perdants. C'est vrai avec la correction Bonferroni, **et aussi sans correction**.

| Variable | Gagnants (médiane) | Perdants (médiane) | IC 90 % | Verdict |
|---|---|---|---|---|
| Écart modèle − marché | +0,21 | +0,21 | [−0,15 ; +0,66] | rien |
| Distance au prix à battre (écarts-types) | −0,17 | −0,25 | [−0,32 ; +0,83] | rien |
| Distance au prix à battre ($) | −2,08 | −2,19 | [−0,86 ; +0,22] | rien |
| Tendance BTC 10 s | +0,00 | −0,13 | [−0,12 ; +0,92] | rien |
| Tendance BTC 30 s | +0,00 | −0,53 | [−0,26 ; +0,84] | rien |
| Volatilité BTC 60 s | +0,14 | +0,17 | [−0,46 ; +0,39] | rien |
| Profondeur vendeuse | 3,7 $ | 3,2 $ | [−0,38 ; +0,85] | rien |
| Déséquilibre acheteurs / vendeurs | −0,47 | −0,27 | [−0,55 ; +0,30] | rien |
| Flux preneur 10 s | +5 | −77 | [−0,37 ; +0,61] | rien |
| Déclenché par le carnet | oui | oui | [−0,70 ; +0,29] | rien |

Les tendances BTC à 10 s et 30 s vont dans le sens attendu (les gagnants ont un BTC qui va moins contre eux), mais sans signification statistique.

## 3. H821 — Règles simples d'exclusion

**Méthode**
- 38 règles candidates : une variable, un seuil au tercile de l'apprentissage, dans les deux sens.
- Une règle est admissible si, sur l'apprentissage, elle ne supprime **aucun jackpot** (gain ≥ 2× la mise) et garde au moins 50 % des signaux.

**Règle retenue sur l'apprentissage** : exclure le signal si la distance Chainlink au prix à battre, dans notre sens, est supérieure à −0,09 écart-type. Autrement dit, on exclut les signaux où Chainlink est déjà à peu près au prix à battre ou du bon côté, alors que le marché paie moins de 0,50.

**Explication possible** : quand Chainlink nous donne déjà raison mais que le marché refuse de payer, le marché voit sans doute autre chose (le perp en avance sur Chainlink). Cette explication n'est **pas démontrée**.

| Échantillon | Politique | Signaux | Perdants évités | Gagnants perdus | Jackpots perdus | P&L | Marginal | IC 90 % du marginal par signal | Drawdown |
|---|---|---|---|---|---|---|---|---|---|
| Test — tous | base | 36 | — | — | — | +72 $ | — | — | 147 $ |
| Test — tous | avec la règle | 26 | 8 | 2 | **0** | +211 $ | **+139 $** | [+2,0 ; +5,8] | 82 $ |
| Test — H816 | H816 | 29 | — | — | — | +47 $ | — | — | 131 $ |
| Test — H816 | H816 + règle | 23 | 5 | 1 | **0** | +126 $ | **+79 $** | [+0,8 ; +4,9] | 82 $ |
| Apprentissage — tous | avec la règle | 27 / 41 | 10 | 4 | 0 | +351 $ | +87 $ | [+0,1 ; +4,1] | 40 $ (au lieu de 63) |

**Concentration** : sur le test H816, les 5 meilleurs trades pèsent 644 % du P&L sans la règle, et 239 % avec. La dépendance aux jackpots diminue, mais reste forte.

**Pourquoi ce résultat n'est pas une preuve**
1. **Choix parmi 38 règles.** L'IC de +2,0 à +5,8 ne tient pas compte de cette sélection. Avec une correction pour 38 essais, il contiendrait très probablement zéro.
2. **Test minuscule.** 36 décisions, une seule après-midi. Le résultat tient à 8 perdants évités.
3. **Incohérence avec H820.** H820 ne trouve aucun effet de cette variable, et le coefficient y est même de signe opposé (+0,18 : plus on est du bon côté, plus on gagne). La règle exploite un effet de seuil, pas une tendance.
4. **La 2e meilleure règle de l'apprentissage s'effondre sur le test** (flux preneur : +68 $ en apprentissage, −138 $ en test). C'est le profil typique du bruit.
5. **Échelle de volatilité ad hoc.** Les écarts-types reposent sur la volatilité du perp sur 60 s, une mesure fixée par moi et non par Bot95.

## 4. Gagnants et jackpots conservés

Avec la règle, aucun jackpot n'est perdu, ni en apprentissage ni en test. Sur le test, 2 gagnants ordinaires sont perdus (1 dans la plage H816).

## 5. P&L net et drawdown

Sur le test, la règle fait passer le P&L de +47 $ à +126 $ (H816), et le drawdown de 131 $ à 82 $. Cela reste **un seul échantillon de test**.

## 6. Verdict statistique

- **H819** : démontré. Bot95 est moins bien calibré que le prix du marché, surtout à moins de 2 minutes. Le marché est le meilleur juge de probabilité disponible.
- **H820** : aucune différence entre gagnants et perdants démontrée, même sans correction.
- **H821** : une règle donne un **indice** positif hors échantillon, sans perte de jackpot. Elle **n'est pas démontrée**, car l'IC n'est pas corrigé pour les 38 essais, l'échantillon est minuscule et la règle contredit H820.
- **Aucune rentabilité démontrée** : l'IC de H816 lui-même contient toujours zéro.

## 7. Recommandation

1. **Conserver H816 tel quel.** Il reste le seul protocole jugé le 14.10 sur la période réservée.
2. **Option, avec ton accord uniquement** : pré-enregistrer, avant le 13.10, une variante séparée **« H816 + exclusion distance > −0,09 σ »**, figée dans un commit et calculée hors ligne sur la même période réservée, à côté de H816. Pas de nouveau fantôme ni de déploiement : simple recalcul sur les données enregistrées.
3. Si cette variante bat H816 le 13.10 avec un IC par cycle > 0, on aura une seconde preuve indépendante. Sinon, on l'abandonne.
4. Piste à explorer plus tard : remplacer la probabilité Bot95 par le prix du marché corrigé, puisque le marché calibre mieux. Cela ferait l'objet d'un nouveau protocole, pas d'une retouche de H816.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_selection_h819.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/selection_h819.py
