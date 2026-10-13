# Bot95 — H1074 : écart Polymarket à l'achat (stratégies du bot)

13.10.2026 soir, 7 049 trades BTC (11.10 08:05 → 12.10 24:00) joints au carnet Dublin de la seconde avant l'achat. Exploration (3 périodes regardées).

| Filtre | Apprentissage gardés / écartés | Validation | Test | Écart, IC 90 % par cycles |
|---|---|---|---|---|
| Écart ≤ 1 c | +6 % (+7 563 $) / −23 % (−2 328 $) | +154 % / −47 % | +14 % (+10 094 $) / −48 % (−2 489 $) | A [−8 ; +61], V [+29 ; +402], T [+18 ; +107] pts |
| Écart ≤ 1 c + carnet pour nous | +24 % / −8 % | +255 % / +31 % | +47 % (+18 146 $) / −29 % | A [+1 ; +62], T [+37 ; +120] pts |

Quand l'écart Polymarket dépasse 1 c au moment d'acheter (≈ 10 % des trades), les stratégies du bot perdent nettement dans les 3 périodes.
Fantômes « <stratégie> + ecart serre » et « <stratégie> + carnet ecart serre » en ligne. Aucun ordre réel.
