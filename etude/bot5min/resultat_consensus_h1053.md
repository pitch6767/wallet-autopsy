# Bot95 — H1053 : filtre de consensus sur les gagnantes du 12.10

Généré le 12.10.2026 17:00 UTC. Mise ramenée à 10 $ par trade. Aucun ordre.

## Exploration (avant le 13.10, déjà vue) — 7482 trades, base -1266 $, 5795 perdants

| Règle | Trades gardés | P&L gardé ($) | Perdants gardés | Taux de perdants | Écart avec la base ($) | IC 90 % | IC corrigé (4) | Stratégies améliorées |
|---|---|---|---|---|---|---|---|---|
| K2 consensus ≥ 8 et ≥ 120 s | 3434 / 7482 | +5406 | 2558 / 5795 | 74 % (base 77 %) | +6671 | [+2222 ; +10896] | [+527 ; +12468] | 9 / 10 |
| K1 consensus ≥ 8 | 3976 / 7482 | +3782 | 3012 / 5795 | 76 % (base 77 %) | +5048 | [+1016 ; +9086] | [-370 ; +10280] | 9 / 10 |
| K3 consensus ≥ 6 et ≥ 120 s | 4667 / 7482 | +4464 | 3520 / 5795 | 75 % (base 77 %) | +5730 | [+2372 ; +8978] | [+1059 ; +10168] | 9 / 10 |
| K4 consensus ≥ 10 et ≥ 120 s | 2180 / 7482 | +5153 | 1597 / 5795 | 73 % (base 77 %) | +6419 | [+813 ; +12105] | [-1522 ; +14054] | 8 / 10 |

| Stratégie | Base ($) | K2 ($) | Écart | Perdants base → K2 |
|---|---|---|---|---|
| V2-F + pas les deux baissent BTC | -483 | +393 | +876 | 635 → 273 |
| V2-D perp 120-269 s BTC | +394 | +442 | +48 | 580 → 395 |
| V2-F + plus de 120 s BTC | -127 | +643 | +770 | 539 → 241 |
| V2-C perp BTC | -185 | +471 | +656 | 690 → 359 |
| V2-G jury des bourses BTC | -203 | +451 | +654 | 671 → 449 |
| V2-F ecart qui grandit BTC | -470 | +704 | +1174 | 683 → 250 |
| V2-B hors 60-89 s BTC | -290 | +786 | +1075 | 682 → 161 |
| V2-H veto complet BTC | -396 | +260 | +656 | 686 → 270 |
| desaccord 20 Binance ou perp avec nous BTC | +706 | +671 | -35 | 140 → 41 |
| desaccord 20 sans nuit BTC | -211 | +585 | +797 | 489 → 119 |

## TEST (≥ 13.10, jamais vu) — 0 trades, base +0 $, 0 perdants
