# Bot95 — H817 : moteur de sauvetage prédictif et progressif — rapport du 11.10.2026

**Cadre**
- Étude hors ligne uniquement. Aucun ordre réel.
- R4, H816 et les fantômes ne sont pas modifiés. La période réservée n'a pas été lue.
- Le protocole (grilles de paramètres, règles de sélection) a été enregistré sur GitHub **avant** le calcul (commit 22fecd0).

**Positions de départ (les mêmes pour toutes les politiques)**
- 70 décisions uniques de Bot95 sur des cycles enregistrés à Dublin : mise de 20 $, achat 164 ms après la décision.
- Apprentissage sur la 1re moitié des cycles (36 positions), test sur la 2e moitié (34 positions).

**Comment les sorties sont simulées**
- Une décision de sortie est possible toutes les 500 ms, avec uniquement les données disponibles à ce moment-là.
- Une vente est limitée au meilleur acheteur affiché au moment de la décision, et exécutée sur le carnet réel 164 ms plus tard.
- La quantité vendue est plafonnée à ce qui est affiché dans le carnet. Les frais sont déduits.

## 0. Audit des données

| Point | Constat |
|---|---|
| Carnet, transactions, prix des bourses, Chainlink | Disponibles pour environ 80 cycles Dublin. La profondeur au-delà de ±3 c du meilleur prix n'est connue que toutes les 10 s. |
| Annuler un ordre preneur pendant le délai d'attente de Polymarket | **Impossible.** La documentation Polymarket dit que l'ordre est « pending and cannot be canceled ». Seul l'envoi volontairement différé (G4) reste testable. |
| Délai preneur | 150 ms selon le changelog du 04.09.2026 ; une page de la documentation indique encore 250 ms. Testé à 164, 264 et 500 ms. |
| Couverture par la jambe inverse | Voir §3 : elle équivaut exactement à une vente. |

## 1. H817-A — Notre probabilité de victoire est moins bien calibrée que le prix du marché

| Probabilité de victoire selon notre modèle | Victoire observée | Prix médian Polymarket |
|---|---|---|
| 0,1–0,3 | 0 % | 5 % |
| 0,3–0,5 | 22 % | 20 % |
| 0,5–0,7 | 77 % | 69 % |
| 0,7–0,9 | 100 % | 97 % |

Erreur moyenne au carré (Brier, plus bas = meilleur) : **modèle 0,215, contre 0,144 pour le prix médian Polymarket**.

Pendant la vie d'une position, le marché estime mieux la probabilité de gagner que notre modèle. Un sauvetage qui compare l'acheteur à notre modèle déclenche donc surtout du bruit.

## 2. H817-B / J — Le carnet ne réagit pas « en retard »

Nous avons repéré 184 chutes de notre probabilité d'au moins 5 points en 1 seconde :
- au même instant, le meilleur acheteur n'a pas bougé (variation médiane : 0 c) ;
- 3 secondes plus tard, il n'a toujours pas bougé (médiane : 0 c).

Une vente reste exécutable 164 ms après dans 84 % de ces cas. Mais le marché n'est pas en retard : ces chutes ne présagent pas d'une baisse du prix, c'est notre modèle qui bouge à tort.

## 3. H817-D / K — Couvrir par la jambe inverse = vendre

Sur Polymarket, le meilleur vendeur de Down est exactement 1 − le meilleur acheteur de Up : ce sont les mêmes ordres, appariés par la plateforme. Les frais sont aussi identiques.

Acheter n parts de la jambe inverse verrouille donc **exactement le même résultat** que vendre n parts de la position, à la même profondeur. La seule différence est que le capital reste immobilisé jusqu'au règlement. **Il n'y a ni arbitrage ni avantage propre à la couverture.**

## 4. Politiques de sortie

Les réglages ont été choisis sur l'apprentissage, puis mesurés sur le test. L'intervalle de confiance (IC) à 90 % est calculé par cycle.

| Politique (réglage choisi) | Test : écart avec HOLD | IC 90 % par position | Tout l'échantillon : écart avec HOLD | Pertes évitées / gains abandonnés (tout) | Interventions |
|---|---|---|---|---|---|
| SELL — vendre 25 % si acheteur ≥ probabilité + 0,10 | +3,2 $ | [−0,94 ; +1,26] | −1,2 $ | +64 / −66 $ | 24 |
| ÉCHELLE — ventes par paliers de 20 % | +1,8 $ | [−3,56 ; +4,13] | **−142,8 $** | +187 / −330 $ | 1 659 |
| BUDGET — plafond de perte à 50 % | +20,1 $ | [0,00 ; +1,23] | +20,1 $ | +20 / 0 $ | **2** |
| REBOND — vendre 50 % si l'acheteur remonte de 5 c | +4,0 $ | [0,00 ; +0,33] | +4,0 $ | +4 / 0 $ | **1** |
| Stop naïf −10 c (référence) | — | — | **−290,6 $** | +288 / −579 $ | 45 |
| Stop naïf −20 c (référence) | — | — | −44,7 $ | +112 / −156 $ | 37 |

**Lecture des politiques**
- Les ventes intelligentes et les ventes par paliers évitent des pertes, mais abandonnent autant ou plus de gains. Leur résultat est nul ou négatif.
- Les stops naïfs détruisent les gros gagnants. Cela confirme l'étude des 1 053 sauvetages historiques.
- BUDGET et REBOND paraissent positifs, mais sur 2 interventions et 1 intervention seulement : ce n'est pas exploitable statistiquement.
- **Sensibilité à la latence (264 et 500 ms)** : aucune politique ne devient positive.
- **Sous-ensemble H816** (prix 0,20–0,50) : SELL −21 $, ÉCHELLE −176 $, BUDGET et REBOND n'interviennent jamais.

## 5. H817-G — Différer volontairement l'envoi

Principe : attendre δ ms avant d'envoyer, recalculer la probabilité et le vendeur, puis n'envoyer que si l'avantage reste d'au moins 0,10.

| Envoi | Positions exécutées | Écart avec l'envoi immédiat |
|---|---|---|
| Différé 50 ms | 58 | −13,6 $ |
| Différé 100 ms | 54 | −44,3 $ |
| Différé 150 ms | 52 | +14,7 $ |

Tous les IC contiennent 0 : **aucun gain démontré**.

## 6. Recommandation par module

| Module | Décision |
|---|---|
| A — Probabilité de victoire par notre modèle | **Rejeté comme juge de sortie.** Le prix Polymarket est mieux calibré. Toute reprise devra partir du prix du marché. |
| B / J — Retard du carnet, sortir avant la panique | **Rejeté.** Aucun retard du carnet mesuré. |
| C — Vente intelligente | **Rejeté.** Résultat nul. |
| D / K — Couverture par la jambe inverse | **Rejeté.** Identique à la vente, par construction. |
| O — Ventes progressives par paliers | **Rejeté.** Détruit des gains (−143 $). |
| O6 — Budget de perte, H / L — Rebond | **Non démontrés.** 1 à 2 interventions seulement. À observer passivement sur de nouvelles données, sans déploiement. |
| G — Envoi différé | **Rejeté.** L'annulation pendant le délai est impossible et le report n'apporte rien. |
| E / N — Routeur | **Non construit.** Aucun composant n'a démontré de valeur, conformément à ta consigne. |

**Réponse à la question centrale.** Sur ces données, aucune politique de sortie, de couverture ou de vente partielle n'améliore le résultat par rapport au HOLD de façon démontrée. La meilleure façon de garder les gros gains reste de conserver la position jusqu'au règlement.
