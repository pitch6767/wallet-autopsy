# Bot95 — H1082 : cohérence entre marchés BTC / ETH / SOL 5 min

**Verdict : abandon des 4 règles.** Aucune ne dégage de gain sur la validation ; deux (R1, R2) perdent même nettement, au-delà du bruit. Les marchés ETH et SOL ne sont pas « en retard » sur BTC d'une manière exploitable : quand ils ne suivent pas BTC, c'est en général parce qu'ETH ou SOL lui-même n'a pas suivi, et ils ont raison. **Aucun fantôme proposé.**

Étude hors ligne du 14.10.2026, aucun ordre passé, aucun bot ni workflow modifié. Script figé et publié **avant** le calcul de la validation : `etude/bot5min/coherence_marches_h1082.py` (commit 444bbac).

## L'idée testée

Polymarket propose des paris « Up/Down 5 min » sur BTC, ETH et SOL, sur exactement le même créneau. Les trois cryptos bougent ensemble (corrélation BTC/ETH ~0,8 sur 5 min). Hypothèse : les marchés ETH et SOL, moins liquides, réagiraient en retard aux mouvements de BTC ; acheter le côté « en retard » serait gagnant.

## Résultats sur la validation (12.10 04:50 → 13.10 00:00 UTC, jamais regardée avant le commit)

Mise de 10 $ par achat, prix payé = médiane des achats réels 1 à 6 s **après** la décision + frais preneur. IC = intervalle de confiance par tirage au hasard des créneaux ; « corrigé » = 97,5 % (correction de Bonferroni pour 4 règles).

| Règle | Achats | Gagnés | Prix moyen | ROI | IC 90 % | IC corrigé | P&L | Verdict |
|---|---|---|---|---|---|---|---|---|
| R1 — marché BTC a bougé ≥ 10 pts en 30 s, ETH pas suivi → acheter ETH | 50 | 28 % | 0,36 | **−41 %** | [−64 ; −17] % | [−71 ; −9] % | −207 $ | abandon (perte démontrée) |
| R2 — même chose sur SOL | 58 | 38 % | 0,40 | **−34 %** | [−53 ; −14] % | [−59 ; −5] % | −196 $ | abandon (perte démontrée) |
| R3 — prix ETH/SOL ≥ 15 pts loin de ce que « dit » le prix BTC → acheter le côté bon marché | 251 | 30 % | 0,30 | −5 % | [−25 ; +15] % | [−32 ; +23] % | −131 $ | abandon |
| R4 — BTC spot a bougé fort (z ≥ 2 en 30 s), marché ETH/SOL pas suivi | 33 | 33 % | 0,40 | −35 % | [−63 ; −4] % | [−72 ; +9] % | −115 $ | abandon |

Sur l'exploration (11.10 00:00 → 12.10 04:50, qui a servi à choisir les seuils), les mêmes règles donnaient +2 %, +10 %, +19 % et +42 %. Tout a disparu, ou s'est inversé, sur les heures suivantes : c'était du bruit d'échantillon.

**Témoins** (pour juger la méthode, pas des règles) :
- acheter Up sans condition à 150 s : +9 % en exploration, −0,5 % en validation ; Down : −15 % puis +7 %. La période d'exploration a été haussière : un écart de ±15 % sur ces petites périodes n'est que la tendance du jour.
- R4 quand ETH/SOL a **déjà** suivi : −3 % en exploration comme en validation (≈ les frais) : le marché ETH/SOL qui suit BTC est correctement évalué.

## Ce que ça veut dire, simplement

- Le marché ETH ne copie pas BTC : il suit le prix de l'ETH. Quand BTC bouge et que le marché ETH reste sur place, c'est le plus souvent que l'ETH n'a pas bougé autant ; parier que le marché ETH « va rattraper » revient à parier contre l'information réelle. D'où les pertes de R1 et R2.
- La « correspondance » BTC → ETH ajustée sur l'exploration (pente ~0,6 en logit) existe, mais les écarts à cette correspondance ne sont pas des erreurs de prix.
- Confirme H1061 (13.10) : ETH ne réagit pas plus lentement que BTC aux sauts du perp, et l'avantage apparent venait de la méthode de prix.

## Limites

- **Très peu de données** : seulement 2 jours (11–12.10) où les transactions ETH et SOL existent ; 230 créneaux en validation, 33 à 58 achats par règle (sauf R3). Les IC sont très larges ; un petit avantage (quelques %) ne serait pas détectable.
- Pas de confirmation ≥ 13.10 : aucune transaction ETH/SOL n'existe pour ces jours (et pas d'accès réseau ici pour les récupérer).
- Les transactions BTC publiques du 12.10 après ~19:25 UTC manquent : R1–R3 n'y sont pas testées (R4 utilise le BTC spot, disponible).
- Pas de carnet d'ordres ETH/SOL : le prix « milieu » est la médiane des transactions des 10 dernières secondes (bruité sur SOL, ~1 transaction/s) et le prix payé est approché par les achats réels des autres participants (H1061 a montré que c'est plutôt optimiste — ce qui renforce l'abandon).
- XRP non testé (pas de transactions enregistrées).

## Détail complet (sortie du script)

Créneaux : exploration 346, validation 230. Correspondance (exploration) : ETH logit = 0.632·logit(pBTC) +0.029, SOL logit = 0.575·logit(pBTC) -0.014. Aucun ordre.

| Règle | Période | Achats | Créneaux | Gagnants | Prix moyen | ROI | IC 90 % du ROI | IC 97,5 % (Bonferroni) du ROI | P&L à 10 $ | IC 97,5 % du P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 ETH en retard sur le marché BTC | exploration | 132 | 132 | 36 % | 0.370 | +2.0 % | [-24.8 ; +30.7] % | [-34.0 ; +44.1] % | +26 $ | [-449 ; +582] $ |
| R1 ETH en retard sur le marché BTC | validation | 50 | 50 | 28 % | 0.360 | -41.4 % | [-63.9 ; -17.4] % | [-71.3 ; -9.1] % | -207 $ | [-356 ; -45] $ |
| R2 SOL en retard sur le marché BTC | exploration | 109 | 109 | 45 % | 0.424 | +9.6 % | [-16.1 ; +37.4] % | [-23.7 ; +49.7] % | +105 $ | [-259 ; +542] $ |
| R2 SOL en retard sur le marché BTC | validation | 58 | 58 | 38 % | 0.395 | -33.8 % | [-52.9 ; -13.6] % | [-59.2 ; -5.3] % | -196 $ | [-344 ; -31] $ |
| R3 écart à la correspondance BTC → ETH/SOL ≥ 0,15 | exploration | 565 | 313 | 37 % | 0.314 | +18.7 % | [+4.5 ; +32.6] % | [+0.1 ; +37.9] % | +1055 $ | [+4 ; +2148] $ |
| R3 écart à la correspondance BTC → ETH/SOL ≥ 0,15 | validation | 251 | 143 | 30 % | 0.304 | -5.2 % | [-25.4 ; +15.1] % | [-32.3 ; +23.4] % | -131 $ | [-806 ; +597] $ |
| R4 BTC spot a bougé (z ≥ 2), ETH/SOL pas suivi | exploration | 69 | 56 | 54 % | 0.481 | +42.3 % | [-6.3 ; +97.3] % | [-17.5 ; +121.6] % | +292 $ | [-121 ; +825] $ |
| R4 BTC spot a bougé (z ≥ 2), ETH/SOL pas suivi | validation | 33 | 27 | 33 % | 0.401 | -34.7 % | [-63.3 ; -4.1] % | [-72.1 ; +9.2] % | -115 $ | [-233 ; +29] $ |
| Témoin : Up à 150 s | exploration | 438 | 283 | 55 % | 0.512 | +8.6 % | [-5.4 ; +23.0] % | [-9.1 ; +28.7] % | +378 $ | [-396 ; +1269] $ |
| Témoin : Up à 150 s | validation | 308 | 193 | 47 % | 0.501 | -0.5 % | [-21.7 ; +22.2] % | [-28.8 ; +31.1] % | -15 $ | [-878 ; +966] $ |
| Témoin : Down à 150 s | exploration | 442 | 287 | 46 % | 0.491 | -15.2 % | [-27.5 ; -1.0] % | [-30.8 ; +3.9] % | -670 $ | [-1372 ; +173] $ |
| Témoin : Down à 150 s | validation | 308 | 194 | 53 % | 0.502 | +7.2 % | [-10.4 ; +25.6] % | [-15.8 ; +32.7] % | +222 $ | [-487 ; +1013] $ |
| Témoin : R4 mais ALT a déjà suivi | exploration | 358 | 216 | 71 % | 0.720 | -2.8 % | [-9.8 ; +4.0] % | [-12.0 ; +6.6] % | -100 $ | [-430 ; +239] $ |
| Témoin : R4 mais ALT a déjà suivi | validation | 221 | 131 | 72 % | 0.718 | -3.4 % | [-12.0 ; +5.4] % | [-15.0 ; +8.3] % | -74 $ | [-334 ; +184] $ |

