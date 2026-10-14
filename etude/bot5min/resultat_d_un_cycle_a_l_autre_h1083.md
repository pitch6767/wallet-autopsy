# Bot95 — H1083 : d'un cycle à l'autre (27 jours, 12.09 → 08.10.2026)

## Verdict

**Non.** Ce qui s'est passé avant le cycle (sens et taille du dernier cycle, série de Up/Down, volatilité des 15–30 dernières minutes, distance au prix d'ouverture précédent, chiffre rond, heure) ne prédit pas l'issue mieux que le prix du marché dans les 10 à 30 premières secondes.

- Aucune des 4 règles figées ne passe le critère (intervalle corrigé pour 4 règles entièrement au-dessus de 0).
- La meilleure, **X2** (BTC a baissé sur 30 min et sur les 5 dernières min → acheter Up à 10 s), gagne +11,6 % en validation (+352 $ à 10 $ par achat). L'intervalle simple à 90 % est juste positif [+15 ; +700] $, mais l'intervalle corrigé contient 0 [−100 ; +832] $. Ce n'est **pas démontré** : pas de proposition de fantôme.
- Le modèle statistique qui ajoute les variables inter-cycles au prix du marché n'améliore pas la précision (Brier) en validation. Les écarts sont de l'ordre de 0,001, et chaque intervalle contient 0.
- Le marché est bien calibré en début de cycle, comme dans les études précédentes.

Aucun ordre n'a été passé, et aucun fichier du bot ni aucun fantôme n'a été modifié.

## Méthode

- **Données** : transactions publiques Polymarket BTC 5 min (achats seulement) et Binance BTCUSDT à la seconde. Aucun marché ouvert à partir du 09.10 00:00 UTC n'est utilisé. Le 12.09 sert seulement d'historique, car les variables demandent 24 h de BTC.
- **Exploration** : 12.09–30.09, 5 102 cycles. **Validation** : 01.10–08.10, 2 293 cycles, lue une seule fois.
- **Prix du marché à t** : médiane des achats dans les 6 s qui précèdent. **Prix payé** : médiane des achats du côté acheté entre t+1 et t+6 s, donc après le signal. **Frais** : 0,07·p·(1−p). On garde le billet jusqu'au règlement, avec un seul achat par cycle et par règle.
- **Règles figées et publiées avant la validation** (commit e597196). Les seuils sont les quintiles de l'exploration :
  - X1 : t = 10 s, BTC sur 30 min ≤ −1,018 écart-type → acheter Up.
  - X2 : comme X1, et BTC sur 5 min en baisse → acheter Up.
  - X3 : t = 10 s, volatilité 30 min / 1 h ≥ 1,124 → acheter Down.
  - X4 : t = 20 s, BTC a baissé depuis l'ouverture (≤ −0,23 écart-type du temps restant) → acheter Down. Ce signal est intra-cycle ; il sert de contrôle.
- **Intervalles** : bootstrap par cycles, 10 000 tirages. L'intervalle à 90 % est simple. L'intervalle corrigé (Bonferroni, 4 règles) va des percentiles 1,25 à 98,75.

## Ce que l'exploration a montré

- Acheter au hasard vers 0,50 en début de cycle coûte −3 à −5 % (frais + écart achat/vente).
- Aucune variable inter-cycles ne décale nettement l'issue par rapport au prix. Tous les écarts restent sous 2 erreurs-types, alors qu'une quinzaine de variables ont été regardées.
- Seules pistes retenues : un léger retour à la moyenne après une baisse de 30 min (côté Up), et le côté Down après une baisse dans les 20 premières secondes.
- En exploration, une règle « acheter quand le modèle logistique voit un avantage » perdait −2 à −11 %. Elle n'a donc pas été retenue.

## Résultats par règle (10 $ par achat)

| Règle | Période | Achats | Gagnés | Prix moyen | ROI (IC 90 %) | P&L | IC 90 % P&L | IC corrigé ×4 |
|---|---|---|---|---|---|---|---|---|
| X1 baisse 30 min → Up | exploration | 1 019 | 51,7 % | 0,486 | +5,1 % [−0,6 ; +10,9] | +522 $ | [−68 ; +1 120] | [−289 ; +1 338] |
| X1 baisse 30 min → Up | **validation** | 418 | 51,4 % | 0,478 | **+5,6 %** [−3,6 ; +14,7] | **+233 $** | [−149 ; +623] | **[−289 ; +775]** |
| X2 baisse 30 min et 5 min → Up | exploration | 714 | 51,8 % | 0,469 | +9,0 % [+1,8 ; +16,1] | +639 $ | [+132 ; +1 168] | [−54 ; +1 359] |
| X2 baisse 30 min et 5 min → Up | **validation** | 305 | 52,8 % | 0,462 | **+11,6 %** [+0,4 ; +22,8] | **+352 $** | [+15 ; +700] | **[−100 ; +832]** |
| X3 volatilité haute → Down | exploration | 1 016 | 51,5 % | 0,498 | +1,9 % [−3,7 ; +7,7] | +195 $ | [−377 ; +780] | [−580 ; +991] |
| X3 volatilité haute → Down | **validation** | 490 | 46,1 % | 0,499 | **−10,2 %** [−18,1 ; −2,1] | **−497 $** | [−886 ; −101] | **[−1 029 ; +42]** |
| X4 baisse depuis l'ouverture → Down | exploration | 1 018 | 69,3 % | 0,655 | +4,6 % [+0,8 ; +8,4] | +472 $ | [+76 ; +855] | [−49 ; +989] |
| X4 baisse depuis l'ouverture → Down | **validation** | 415 | 65,8 % | 0,666 | **−4,9 %** [−10,7 ; +0,9] | **−205 $** | [−445 ; +33] | **[−535 ; +117]** |

Lecture :

- X3 et X4 s'inversent en validation. C'était du bruit d'exploration.
- X1 et X2 restent positives sur les deux périodes. Elles mesurent le même phénomène, X2 étant un sous-ensemble de X1 : après une baisse de BTC sur 30 min, le côté Up à 10 s serait un peu sous-payé.
- Pour X2, ~300 achats en 8 jours ne suffisent pas à séparer +11 % de 0 une fois la correction appliquée. Il faudrait environ 3 fois plus de jours pour trancher.

## Calibration du marché (t = 10, 20 et 30 s regroupés)

| Prix Up | Exploration : prix → fréquence réelle | Validation : prix → fréquence réelle |
|---|---|---|
| ≤ 0,30 | 0,241 → 0,245 | 0,238 → 0,270 |
| 0,30–0,40 | 0,357 → 0,334 | 0,355 → 0,320 |
| 0,40–0,45 | 0,429 → 0,410 | 0,428 → 0,415 |
| 0,45–0,50 | 0,480 → 0,473 | 0,479 → 0,481 |
| 0,50–0,55 | 0,529 → 0,562 | 0,529 → 0,561 |
| 0,55–0,60 | 0,578 → 0,600 | 0,579 → 0,624 |
| 0,60–0,70 | 0,650 → 0,636 | 0,651 → 0,652 |
| > 0,70 | 0,762 → 0,766 | 0,772 → 0,793 |

Le marché est calibré à 2–4 points près. Dans les deux périodes, un Up légèrement favori (0,50–0,60) gagne 3 à 4 points de plus que son prix, et un Up à 0,30–0,40 en gagne 2 à 3 de moins. Ce constat est observé après coup et n'a pas été testé comme règle. De plus, chaque cycle compte 3 fois (une fois par instant), donc les écarts-types sont sous-estimés. L'écart reste du même ordre que les frais et l'écart achat/vente.

## Précision (Brier) : variables inter-cycles + prix contre prix seul, en validation

Différence = Brier du modèle − Brier du prix. Une valeur négative signifie que le modèle fait mieux.

| Instant | Modèle | Brier prix | Brier modèle | Différence (IC 90 %) |
|---|---|---|---|---|
| 10 s | inter-cycles | 0,2333 | 0,2325 | −0,0008 [−0,0022 ; +0,0006] |
| 20 s | inter-cycles | 0,2251 | 0,2254 | +0,0003 [−0,0010 ; +0,0015] |
| 30 s | inter-cycles | 0,2159 | 0,2156 | −0,0003 [−0,0015 ; +0,0009] |
| 10 s | inter-cycles + mouvement depuis l'ouverture | 0,2333 | 0,2328 | −0,0005 [−0,0020 ; +0,0009] |
| 20 s | idem | 0,2251 | 0,2256 | +0,0005 [−0,0008 ; +0,0018] |
| 30 s | idem | 0,2159 | 0,2157 | −0,0002 [−0,0014 ; +0,0010] |

Aucune amélioration démontrée : tous les intervalles contiennent 0. Le modèle est ajusté sur l'exploration seulement.

## Limites

- **Taille** : 27 jours, dont 8 en validation (~2 300 cycles, 300 à 500 achats par règle). Un avantage de quelques points ne peut pas être démontré avec si peu de données.
- **Prix payé** : c'est une médiane des transactions publiques dans les 6 s qui suivent le signal, pas un carnet d'ordres réel. La taille disponible et le glissement pour 10 $ ne sont pas vérifiés.
- **Prix de référence** : le règlement se fait sur Chainlink, alors que les variables utilisent Binance. Environ la moitié des secondes Binance ont un prix inchangé (secondes sans transaction ou comblées), ce qui rend le mouvement des 10–20 premières secondes imprécis.
- **Comparaisons multiples** : une quinzaine de variables ont été regardées en exploration, puis 4 règles retenues. Les bons chiffres d'exploration sont donc gonflés, comme le montre l'effondrement de X3 et X4.
- **Régime** : une seule période de marché (septembre–octobre 2026). Rien ne garantit que le léger retour à la moyenne sur 30 min persiste.

Fichiers : `d_un_cycle_a_l_autre_h1083.py` (règles figées, commit e597196 avant validation), `d_un_cycle_a_l_autre_h1083_exploration.json`, `d_un_cycle_a_l_autre_h1083_validation.json`.
