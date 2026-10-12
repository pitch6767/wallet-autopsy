# Bot95 — Suite R4 : H796 à H798 — rapport préliminaire du 11.10.2026

**Cadre :**
- Hors ligne uniquement. Aucun ordre réel.
- R4 en direct et les fantômes gelés sont inchangés.
- La période réservée (≥ 13.10) n'a pas été lue.

**Données :** 157 signaux sur 31 cycles. Séparation chronologique :
- apprentissage : 16 cycles, avant 10:55 UTC ;
- test : 15 cycles indépendants, après.

Les intervalles de confiance (IC 90 %) sont calculés par cycles.

## 1. H796 — Prédicteur de non-retour

**Échantillon :** 122 offres retirées dans les 5 s.
- Le retrait arrive en médiane 125 ms après la décision.
- Dans 22 % des cas, l'offre ne revient pas à ≤ prix + 2 c dans les 5 s.
- Le signal gagne 81 % du temps quand l'offre ne revient pas, contre 40 % quand elle revient.

**Prédicteurs testés** (seules variables connues au retrait, appris sur la 1re moitié, mesurés sur la 2e) :

| Modèle | AUC test | IC 90 % | Brier (taux de base 0,214) |
|---|---|---|---|
| Témoin BTC (Binance 1 s / 3 s, Bybit 3 s) | 0,87 | [0,76 ; 0,97] | 0,134 |
| Témoin Chainlink (5 s) | 0,60 | [0,46 ; 0,75] | 0,214 |
| Témoin carnet (vendeur, acheteur, profondeur) | 0,95 | [0,90 ; 0,99] | 0,140 |
| **Prédicteur complet** | **0,95** | [0,87 ; 0,99] | **0,100** |

**Calibration (test) :**
- prédit < 0,2 : 42 offres, 2 % de non-retour observé ;
- prédit ≥ 0,2 : 19 offres, 80 à 88 % de non-retour observé.

**Lecture :** le non-retour est très prévisible. Le carnet est en partie mécanique : si le vendeur est déjà remonté de plusieurs cents, il revient rarement. Le mouvement BTC dans le sens du signal prédit aussi le non-retour (AUC 0,87).

**Avance temporelle :** la prédiction est disponible environ 5 s avant que le non-retour soit constaté. Mais l'offre au prix du signal est déjà partie à ce moment-là.

**Valeur économique (test) :**

| Politique | Résultat |
|---|---|
| Toutes les relances R4 après le retrait | +433 $ |
| Relances seulement si retour probable | +404 $ |
| Poursuite jusqu'à +5 c si non-retour probable | +415 $ (3 offres exécutées sur 11) |

**Conclusion :** l'information est réelle, mais **pas exploitable** de façon significative. On sait que le signal est bon, mais on ne peut plus l'acheter à un prix raisonnable.

## 2. H797 — Relance après zéro fill ou après fill partiel

Toutes les politiques suivent les mêmes règles que R4 (+2 c, recalcul, avantage ≥ 0,05) : même budget, même latence, mêmes frais.

| Politique | P&L | Marginal vs D (IC 90 % / signal) | Drawdown | Jackpots | Signaux en plus G / P |
|---|---|---|---|---|---|
| Bot95 actuel | +4 580 $ | −195 $ | 767 | 24 | — |
| D — aucune relance | +4 775 $ | 0 | 958 | 25 | — |
| A — après zéro fill | +4 753 $ | −23 $ [−1,1 ; +0,9] | 958 | 25 | 1 / 2 |
| **B — après fill partiel** | **+5 363 $** | **+588 $ [+0,3 ; +7,9]** | 939 | 25 | 0 / 0 |
| C — les deux (= R4) | +5 341 $ | +566 $ [−0,0 ; +7,8] | 939 | 25 | 1 / 2 |

**Parts supplémentaires :**

| Cas | Signaux | Dépensé | Résultat | Gagnants / perdants |
|---|---|---|---|---|
| Après zéro fill | 3 | 146 $ | −23 $ (−16 % par $) | 1 / 2 |
| **Après fill partiel** | **24** | **461 $** | **+588 $ (+128 % par $)** | **12 / 12** |

**Conclusion :** tout le gain de R4 vient des relances **après un fill partiel**. Relancer après zéro fill ne rapporte rien. C'est cohérent avec H776 : une offre totalement partie qui revient est un mauvais signe.

## 3. H798 — Le premier fill renseigne-t-il ?

**Tranches de premier fill** (24 signaux avec parts supplémentaires) :

| Premier fill | Résultat par $ des parts supplémentaires |
|---|---|
| < 25 % du budget | +199 % |
| ≥ 25 % du budget | +101 % |

Le taux de gain est de 50 % dans les deux cas.

**Régression logistique** (134 signaux avec un premier fill, contrôles prix, profondeur, temps restant, volatilité et modèle) :

| Variable | Coefficient | IC 90 % | Lecture |
|---|---|---|---|
| Fraction remplie au premier fill | −0,11 | [−0,54 ; +0,40] | non significatif |
| Profondeur au signal | +0,63 | [+0,26 ; +1,19] | significatif |
| Prix du signal | +0,68 | [+0,08 ; +1,49] | significatif |

Le délai du premier fill ne varie presque pas : c'est quasi toujours la 1re tentative, à 164 ms.

**Conclusion :** la quantité du premier fill **ne prédit pas** la qualité des parts supplémentaires. C'est la profondeur affichée au signal qui compte : plus d'offre au prix du signal va de pair avec plus de gains.

## 4. Verdict sur les cycles indépendants (2e moitié, test)

| Comparaison | Écart par signal | IC 90 % | Verdict |
|---|---|---|---|
| **B contre D** | **+7,05 $** | **[+0,7 ; +13,9]** | **positif**, seul résultat dont l'IC exclut 0 |
| C (= R4) contre D | +6,76 $ | [−0,5 ; +14,8] | non démontré |
| A contre D | −0,28 $ | [−2,4 ; +1,8] | nul |

**Prudence :** une seule journée et 15 cycles de test. Plusieurs comparaisons ont été faites, donc le résultat de B doit être confirmé sur des cycles nouveaux.

**Pas besoin de nouveau fantôme :** le fantôme R4 en direct enregistre chaque tentative séparément. Les politiques A, B, C et D se recalculent donc exactement à partir de ses données réelles, sans modifier R4. Le verdict se fera sur des cycles nouveaux, puis sur la période réservée du 13.10.
