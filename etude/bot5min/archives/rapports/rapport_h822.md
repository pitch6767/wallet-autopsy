# Bot95 — Fusion Engine F1 : H822 à H832 (barrières, figures de liquidité, marge de règlement) — rapport du 12.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- H816, H821, R4 et les fantômes ne sont pas modifiés. La période réservée du 13.10 n'a pas été lue.
- Protocole et code enregistrés sur GitHub **avant** le calcul du test (commit 541c664). Seul le contrôle sur l'apprentissage avait tourné avant.

**Données**
- BTC Binance à la seconde, 30 jours (12.09 → 11.10) : prix, volume, volume agressif (donc le CVD), et l'open interest toutes les 5 minutes.
- Découpage strict dans le temps : apprentissage avant le 02.10, test du 02.10 au 11.10.
- Tous les niveaux sont construits avec les seules données passées. Un pivot n'est utilisable que 6 minutes après sa formation, une fois confirmé.

**Règlement reconstruit**
- Moyenne Binance des 60 dernières secondes contre moyenne des 60 secondes avant le début.
- Contrôle : même résultat que l'officiel Polymarket dans **95,8 %** des cycles (636 contrôlés).
- Les désaccords n'arrivent que lorsque l'écart final est inférieur à 5 $.

**Non mesurable en historique (déclaré, pas estimé)**
- La profondeur loin du prix, son rechargement et son retrait.
- Les liquidations.
- L'open interest n'existe qu'à 5 minutes, ce qui est trop grossier pour des mouvements de 5 à 60 s.

## Réponse courte

**Aucun des modules ne démontre d'avantage.**
- Les supports et résistances ne rejettent pas plus le prix que des niveaux tirés au hasard. Les sommets et creux précédents le rejettent même **moins**.
- Le modèle de règlement avec barrières ou avec figures ne prévoit pas mieux que le modèle de règlement seul.
- Le meilleur veto sur les vraies décisions Bot95 améliore le P&L, mais son intervalle de confiance contient zéro.

## 1. H823 — Rejet au contact d'un niveau (test, 02.10 → 11.10)

Un contact = le prix arrive à ± 16 $ d'un niveau après en avoir été éloigné d'au moins 48 $. On compare ensuite à des **niveaux placebo** : des niveaux fictifs, décalés, soumis exactement aux mêmes règles. Sans cette comparaison, n'importe quel prix « rejette » environ 25 % du temps.

| Niveau | Contacts | Rejet à 60 s | Cassure | Fausse cassure | Rejet en plus du placebo (IC 90 %) |
|---|---|---|---|---|---|
| Chiffre rond 1 000 $ | 342 | 28 % | 33 % | 13 % | −2,5 pts [−8,3 ; +3,0] |
| Chiffre rond 500 $ | 328 | 36 % | 19 % | 16 % | +5,4 pts [−1,5 ; +11,3] |
| Chiffre rond 100 $ | 2 523 | 30 % | 29 % | 16 % | −0,6 pt [−1,6 ; +0,3] |
| Ancien sommet ou creux, 2e contact (double sommet ou creux potentiel) | 3 781 | 15 % | 16 % | 5 % | **−8,7 pts [−12,7 ; −4,8]** |
| Ancien sommet ou creux, 3e contact et plus (triple) | 8 494 | 21 % | 20 % | 8 % | **−3,1 pts [−4,9 ; −1,6]** |

**Lecture**
- Les chiffres ronds ne font rien de plus qu'un prix quelconque. Le 500 $ penche vers le rejet, sans preuve.
- Aux anciens sommets et creux, le prix **ne rejette pas davantage**. Il casse aussi moins souvent : il **stagne** autour du niveau. L'idée « double sommet = rejet » est **contredite** par les données. C'est vrai sur l'apprentissage comme sur le test.
- Le mouvement médian à 5, 10, 20, 30 et 60 s est le même pour les vrais niveaux et pour les placebos.

## 2. H825 — Prévoir cassure, rejet ou fausse cassure avant le contact

L'AUC mesure la capacité à classer les cas : 0,5 = hasard, 1 = parfait.

| Cible | AUC, vrais niveaux | AUC, niveaux placebo |
|---|---|---|
| Rejet | 0,661 | 0,648 |
| Cassure | 0,646 | 0,605 |
| Fausse cassure | 0,767 | 0,725 |

L'issue est en partie prévisible, mais **presque autant sur des niveaux fictifs**. Ce qui prédit, c'est la vitesse d'approche, le flux agressif et la volatilité, pas le niveau lui-même. Les vrais niveaux n'ajoutent qu'environ 0,01 à 0,04 d'AUC.

## 3. H827–H832 — Figures potentielles

Il s'agit de doubles et triples sommets ou creux, de sommets et creux égaux, de balayages de liquidité, de fausses cassures, de cassures avec retest et de compressions. Elles sont toutes détectées comme **potentielles** à l'instant de décision, jamais comme confirmées.

Quand une figure est présente, le taux de victoire Up suit **exactement** la probabilité déjà donnée par le modèle de règlement. Exemples :
- fausse cassure haussière : 79 % de victoires, contre 80 % prévus ;
- double sommet : 63 % de victoires, contre 64 % prévus.

Les figures ne disent rien que la distance au prix à battre ne dise déjà.

## 4. H822 — Règlement avec barrières contre règlement seul (test, 17 274 décisions, 2 879 cycles)

| Modèle | Brier | Log loss | Précision | Écart de Brier avec la référence (IC corrigé) |
|---|---|---|---|---|
| Règlement seul, recalibré (référence) | 0,1081 | 0,3382 | 84,6 % | — |
| Trajectoires simulées sans barrières | 0,1085 | 0,3480 | 84,3 % | +0,0004 [−0,0005 ; +0,0014] |
| Trajectoires avec barrières (H822) | 0,1085 | 0,3480 | 84,3 % | identique : aucun rejet en excès appris |
| Avec figures et obstacles (H827–H832) | 0,1084 | 0,3388 | 84,4 % | +0,0003 [−0,0003 ; +0,0009] |

**Sous-ensemble à marge faible** (|z| < 0,5 : 3 460 décisions)
- Les figures sont légèrement **moins** bonnes : Brier 0,2410 contre 0,2399.
- Les trajectoires avec barrières sont identiques aux trajectoires sans barrières.

**Pourquoi H822 = H823.** Le protocole prévoyait de n'injecter de rejets dans les trajectoires que si un rejet en excès était démontré sur l'apprentissage. Il ne l'a été pour aucun type de niveau, donc le modèle avec barrières est resté égal au modèle sans barrières.

## 5. H824 — Marge de sécurité au règlement

Marge nécessaire en écarts-types (z = distance au prix à battre ÷ incertitude restante), apprise sur l'apprentissage, puis vérifiée sur le test :

| Temps restant | Pour 90 % de victoires | Pour 95 % de victoires | Effet d'un obstacle majeur devant |
|---|---|---|---|
| 240–180 s | 1,9 σ | 2,6 σ | aucun |
| 120–90 s | 1,8–1,9 σ | 2,5–2,6 σ | +0,05 σ environ |
| 60 s | 1,6–1,8 σ | 2,3–2,7 σ | +0,1 à 0,3 σ, non démontré |
| 30 s | 1,2–1,4 σ | 2,0–2,4 σ | instable |

Sur le test, au-delà de ces marges, on gagne de 93 à 100 % du temps : la règle est prudente. L'obstacle ne change pratiquement pas la marge nécessaire.

## 6. H826 — Veto près d'une barrière, sur les vraies décisions Bot95

**Deux ensembles de décisions**
- **U1** : les fantômes Cloudflare, première décision par cycle et par côté, 20 $ au prix enregistré. Apprentissage du 06.10 au 08.10 (413 décisions), test du 09.10 au 11.10 (1 099 décisions).
- **U2** : les décisions H816 de Dublin du 11.10, avec exécution réelle à 164 ms (64 décisions).

**Méthode**
- 12 règles fixées d'avance : 6 types d'obstacle ou de figure contraire × une marge de 0,5 ou 1,0.
- La règle est choisie sur l'apprentissage, puis mesurée une seule fois sur le test.

**Règle retenue :** refuser le pari si une **compression contre un niveau** se trouve devant le prix et si la marge du côté parié est inférieure à 1 σ.

| Échantillon | Décisions | Gardées | Perdants évités | Gagnants supprimés | dont jackpots | P&L sans → avec veto | Gain (IC corrigé, par décision) | Drawdown sans → avec |
|---|---|---|---|---|---|---|---|---|
| Test U1 | 1 099 | 850 | 180 | 69 | 43 | −2 955 → −2 604 $ | +350 $ [−1,25 ; +1,60] | 3 068 → 2 909 $ |
| Test U2 (H816, 164 ms) | 64 | 43 | 16 | 4 | 2 | +283 → +407 $ | +124 $ [−3,84 ; +6,69] | 119 → 79 $ |

**Lecture**
- Le veto va dans le bon sens sur les deux tests, mais les intervalles contiennent zéro : **non démontré**.
- Il supprime aussi 43 jackpots sur U1.
- Le veto « double ou triple sommet contraire » **détruit** de l'argent (−197 à −351 $ sur le test), ce qui est cohérent avec H823.

**Cas symétrique** (Down près d'un support) : il est inclus, toutes les règles étant signées selon le côté parié.

**Marge faible, test U1 (descriptif seulement)**

| | Décisions | Taux de gain | Prix moyen | P&L |
|---|---|---|---|---|
| Avec obstacle majeur devant | 618 | 25 % | 0,29 | −2 391 $ |
| Sans obstacle majeur devant | 363 | 25 % | 0,25 | −700 $ |

Le taux de gain est identique. La différence de P&L vient du prix payé, plus élevé, pas d'un rejet.

## 7. Verdict

| Module | Verdict |
|---|---|
| H822 Règlement avec barrières | **Non démontré.** Aucun rejet en excès à injecter : identique au modèle sans barrières. |
| H823 Rejet au premier contact | **Contredit pour les anciens sommets et creux** (moins de rejets que le hasard, IC hors de zéro). Chiffres ronds : rien. |
| H824 Marge de sécurité | **Utile comme table** : environ 1,9 σ pour 90 % et 2,6 σ pour 95 % avant 90 s. L'obstacle ne change rien. |
| H825 Cassure / rejet / fausse cassure | Prévisible en partie (AUC 0,65 à 0,77), mais **presque autant sur des niveaux fictifs** : ce n'est pas le niveau qui informe. |
| H826 Veto près d'une barrière | **Non démontré.** Meilleure règle +350 $ et +124 $, IC corrigés contenant 0, 43 jackpots supprimés sur U1. |
| H827–H832 Figures de liquidité | **Aucune information en plus** du modèle de règlement. Le veto double/triple sommet est même perdant. |

**Recommandation :** ne rien ajouter au moteur. Garder H816 et H821 tels quels pour le verdict du 14.10.

Si tu le souhaites, la règle « compression devant, z < 1 » pourrait être enregistrée comme candidate séparée et jugée plus tard sur des données nouvelles, sans aucun déploiement.

Fichiers :
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_barrieres_h822.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/barrieres_h822.py
