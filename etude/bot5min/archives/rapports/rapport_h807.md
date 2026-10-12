# Bot95 — H807 à H810 : profondeur, meilleur prix, petits flux, calme — 11.10.2026

Étude hors ligne uniquement. Aucun ordre. Aucun fantôme modifié. La période réservée n'a pas été lue.

**Données :** 82 cycles enregistrés à Dublin et 13 955 offres fictives.
- Apprentissage : cycles avant 12:10 UTC. Test : cycles après.
- Tous les seuils ont été choisis sur l'apprentissage uniquement.

**Moteur commun :** une offre d'achat de 20 $ au meilleur acheteur, sur chaque côté, toutes les 2 s entre 30 et 270 s du cycle. Elle vit 5 s, avec une latence de 14 ms. Les fills sont simulés selon trois hypothèses de file : prudente, centrale, optimiste. Pas de frais maker, résultat compté au règlement.

Toutes les variables sont connues au moment de la pose, sauf H808, qui décrit ce qui s'est passé après coup.

## 1. H807 — Profondeur : la file profonde ne protège pas

Résultats en file centrale, sur tous les cycles.

| Profondeur au meilleur prix | Remplies | P&L / $ immobilisé | Markout à 5 s |
|---|---|---|---|
| 0–50 parts | 85 % | −11,5 % | −1,8 c |
| 50–200 | 70 % | −8,7 % | −1,5 c |
| 200–1 000 | 50 % | −0,6 % | −2,1 c |
| ≥ 1 000 | 37 % | −7,9 % | −2,6 c |

Une file plus profonde réduit la probabilité de fill, mais elle **n'améliore pas le markout**, qui est même un peu pire. Se placer premier dans la file (priorité hypothétique) remonte le résultat de −7,3 % à −4,7 % par $, ce qui reste négatif.

## 2. H808 — Rester au meilleur prix est le pire cas

| Part de sa vie passée au meilleur prix | Remplies | P&L / $ immobilisé | Markout à 5 s |
|---|---|---|---|
| < 25 % | 14 % | +4,9 % | +5,6 c |
| 25–75 % | 57 % | +10,7 % | +1,4 c |
| 75–99 % | 83 % | −11,2 % | −1,5 c |
| 99–100 % | 82 % | **−13,4 %** | **−3,0 c** |

Une offre reste au meilleur prix surtout quand le marché descend vers elle. Elle est alors remplie juste avant que le prix baisse : c'est la sélection adverse classique. Quand le prix monte, l'offre est dépassée et peu remplie, mais elle aurait été bonne. **Cette variable n'est connue qu'après coup : elle n'est pas exploitable.**

## 3. H809 — Petits flux récents : l'inverse de l'hypothèse

| Taille moyenne des transactions des 10 s précédentes | P&L / $ immobilisé | Markout à 5 s |
|---|---|---|
| < 10 $ | **−12,3 %** | −1,9 c |
| 10–50 $ | −0,7 % | −1,7 c |

Un régime de petites transactions ne donne pas de fills moins toxiques.

## 4. Volatilité

| Volatilité sur 30 s | P&L / $ immobilisé | IC 90 % |
|---|---|---|
| < 1 c | +17 % | [−118 ; +324] c par offre (très large) |
| 1–2 c | −18 % | — |
| 2–4 c | −7 % | — |
| > 4 c | −6 % | — |

Le markout à 5 s est négatif partout (−1,5 à −2 c).

## 5. H810 — Politiques comparées sur le TEST (cycles non vus)

Réglage retenu sur l'apprentissage : **volatilité < 1 c et profondeur ≥ 300 parts.** Il a été choisi parmi 48 réglages.

| Politique | File | Offres / remplies | P&L / offre (IC 90 %) | P&L / $ immobilisé | Markout 1/3/5/10 s | Drawdown |
|---|---|---|---|---|---|---|
| Sans filtre | prudente | 6 923 / 3 788 | −1,16 $ [−2,11 ; −0,03] | −13,2 % | −1,9 / −2,0 / −2,0 / −1,9 c | 11 142 $ |
| Sans filtre | centrale | 6 923 / 4 453 | −1,02 $ [−2,12 ; +0,35] | −10,1 % | −1,5 / −1,7 / −1,7 / −1,5 c | 11 128 $ |
| **Calme + profond** | prudente | 172 / 32 | +0,83 $ [−1,46 ; +3,11] | +26,7 % | **−4,4 / −4,3 / −4,2 / −3,5 c** | 133 $ |
| **Calme + profond** | centrale | 172 / 42 | +0,88 $ [−1,37 ; +3,24] | +23,3 % | −3,8 / −4,0 / −3,8 / −3,2 c | 145 $ |
| Profondeur ≥ 300 seule | prudente | 2 345 / 815 | −0,54 $ | −9,4 % | −2,8 / −3,1 / −3,0 / −2,7 c | 2 331 $ |
| Volatilité < 2 c seule | prudente | 1 519 / 648 | −0,68 $ | −11,2 % | −1,6 / −1,8 / −1,6 / −1,2 c | 2 166 $ |

Le filtre « calme + profond » paraît positif. Mais :
- il ne retient que 32 fills sur le test ;
- son IC contient 0 ;
- **ses markouts sont les pires de tous (−4 c)**.

Son gain au règlement vient donc de quelques billets gagnants, pas d'une meilleure qualité de fill. Seule l'hypothèse de file optimiste rend le moteur sans filtre proche de 0.

## 6. Verdict

| Mécanisme | Verdict |
|---|---|
| Profondeur (H807) | **Simple corrélation.** Elle réduit le fill sans améliorer le markout. |
| Présence au meilleur prix (H808) | **Non exploitable.** Connue seulement après coup, et elle signale la sélection adverse. |
| Petits flux (H809) | **Rejeté.** L'effet va dans le sens inverse. |
| Calme (H810) | **Non démontré.** Échantillon minuscule, IC contient 0, markouts négatifs. |

Les fills de bonne qualité des makers réels (au meilleur prix, file profonde) **ne se reproduisent pas** en filtrant à l'avance avec ces conditions. Leur avantage est plus probablement lié à leur **présence permanente et à leur place acquise dans la file**, avec annulation rapide. Nos fantômes ne simulent pas cela.

**Recommandation :** ne pas lancer de nouveau fantôme maker sur ces mécanismes. Si l'on veut poursuivre la piste maker, la seule question restante serait la vitesse d'annulation : mesurer, sur les données Dublin, combien de fills toxiques une annulation en moins de 50 ms aurait évités. À ta décision.
