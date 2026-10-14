# Bot95 — H1053 : filtre de consensus sur les gagnantes du 12.10

Généré le 14.10.2026 06:54 UTC. Mise ramenée à 10 $ par trade. Aucun ordre.

## Exploration (avant le 13.10, déjà vue) — 8029 trades, base -98 $, 6234 perdants

| Règle | Trades gardés | P&L gardé ($) | Perdants gardés | Taux de perdants | Écart avec la base ($) | IC 90 % | IC corrigé (9) | Stratégies améliorées |
|---|---|---|---|---|---|---|---|---|
| K2 consensus ≥ 8 et ≥ 120 s | 3708 / 8029 | +5732 | 2786 / 6234 | 75 % (base 78 %) | +5830 | [+983 ; +10393] | [-1702 ; +13120] | 9 / 10 |
| K1 consensus ≥ 8 | 4353 / 8029 | +3981 | 3323 / 6234 | 76 % (base 78 %) | +4078 | [-189 ; +8183] | [-2793 ; +10307] | 8 / 10 |
| K3 consensus ≥ 6 et ≥ 120 s | 4979 / 8029 | +4755 | 3780 / 6234 | 76 % (base 78 %) | +4853 | [+1225 ; +8442] | [-1308 ; +10170] | 9 / 10 |
| K4 consensus ≥ 10 et ≥ 120 s | 2437 / 8029 | +5649 | 1808 / 6234 | 74 % (base 78 %) | +5747 | [-175 ; +11758] | [-3520 ; +14549] | 9 / 10 |
| K5 K2 et délai ≤ 3 s | 1697 / 8029 | +6058 | 1188 / 6234 | 70 % (base 78 %) | +6156 | [-1177 ; +13017] | [-4430 ; +16356] | 9 / 10 |
| K6 K2 et aucun opposé | 3456 / 8029 | +5434 | 2582 / 6234 | 75 % (base 78 %) | +5532 | [+49 ; +10595] | [-3509 ; +13337] | 9 / 10 |
| K7 K2 et délai ≤ 1 s | 1541 / 8029 | +6255 | 1066 / 6234 | 69 % (base 78 %) | +6353 | [-918 ; +13372] | [-4306 ; +16779] | 9 / 10 |
| K8 K5 et pause si 12 h ≤ 0 | 669 / 8029 | +4500 | 434 / 6234 | 65 % (base 78 %) | +4597 | [-3996 ; +12571] | [-8036 ; +16747] | 8 / 10 |
| K9 K5 et consensus ≥ 15 | 208 / 8029 | +928 | 111 / 6234 | 53 % (base 78 %) | +1026 | [-8310 ; +9925] | [-12853 ; +14714] | 7 / 10 |

| Stratégie | Base ($) | K2 ($) | Écart | Perdants base → K2 |
|---|---|---|---|---|
| V2-F + pas les deux baissent BTC | -159 | +699 | +858 | 686 → 297 |
| V2-D perp 120-269 s BTC | +588 | +510 | -78 | 616 → 425 |
| V2-F + plus de 120 s BTC | -28 | +727 | +755 | 572 → 263 |
| V2-C perp BTC | +50 | +499 | +449 | 743 → 389 |
| V2-G jury des bourses BTC | +236 | +719 | +484 | 710 → 469 |
| V2-F ecart qui grandit BTC | -340 | +789 | +1128 | 734 → 272 |
| V2-B hors 60-89 s BTC | -353 | +632 | +985 | 739 → 183 |
| V2-H veto complet BTC | -441 | +67 | +509 | 743 → 299 |
| desaccord 20 Binance ou perp avec nous BTC | +594 | +618 | +24 | 160 → 52 |
| desaccord 20 sans nuit BTC | -245 | +471 | +716 | 531 → 137 |

## TEST (≥ 13.10, jamais vu) — 1342 trades, base +1307 $, 1061 perdants

| Règle | Trades gardés | P&L gardé ($) | Perdants gardés | Taux de perdants | Écart avec la base ($) | IC 90 % | IC corrigé (9) | Stratégies améliorées |
|---|---|---|---|---|---|---|---|---|
| K2 consensus ≥ 8 et ≥ 120 s | 653 / 1342 | +1193 | 474 / 1061 | 73 % (base 79 %) | -114 | [-3418 ; +2683] | [-6022 ; +3856] | 4 / 10 |
| K1 consensus ≥ 8 | 880 / 1342 | -244 | 687 / 1061 | 78 % (base 79 %) | -1550 | [-4750 ; +1096] | [-6971 ; +2068] | 2 / 10 |
| K3 consensus ≥ 6 et ≥ 120 s | 744 / 1342 | +1320 | 543 / 1061 | 73 % (base 79 %) | +13 | [-3187 ; +2675] | [-5394 ; +3685] | 5 / 10 |
| K4 consensus ≥ 10 et ≥ 120 s | 565 / 1342 | +1437 | 403 / 1061 | 71 % (base 79 %) | +130 | [-3289 ; +3033] | [-5869 ; +4079] | 4 / 10 |
| K5 K2 et délai ≤ 3 s | 482 / 1342 | +646 | 347 / 1061 | 72 % (base 79 %) | -661 | [-4192 ; +2553] | [-6798 ; +3788] | 2 / 10 |
| K6 K2 et aucun opposé | 648 / 1342 | +1243 | 469 / 1061 | 72 % (base 79 %) | -64 | [-3428 ; +2712] | [-5392 ; +3893] | 4 / 10 |
| K7 K2 et délai ≤ 1 s | 457 / 1342 | +695 | 328 / 1061 | 72 % (base 79 %) | -612 | [-4323 ; +2559] | [-6153 ; +3923] | 2 / 10 |
| K8 K5 et pause si 12 h ≤ 0 | 290 / 1342 | +503 | 212 / 1061 | 73 % (base 79 %) | -803 | [-4518 ; +2598] | [-6856 ; +4002] | 2 / 10 |
| K9 K5 et consensus ≥ 15 | 260 / 1342 | +1421 | 165 / 1061 | 63 % (base 79 %) | +114 | [-3593 ; +3483] | [-6185 ; +4732] | 5 / 10 |

| Stratégie | Base ($) | K2 ($) | Écart | Perdants base → K2 |
|---|---|---|---|---|
| V2-F + pas les deux baissent BTC | -39 | -33 | +5 | 86 → 31 |
| V2-D perp 120-269 s BTC | +429 | +201 | -229 | 107 → 91 |
| V2-F + plus de 120 s BTC | +513 | +471 | -42 | 114 → 69 |
| V2-C perp BTC | +226 | +166 | -60 | 206 → 93 |
| V2-G jury des bourses BTC | +474 | +456 | -17 | 180 → 66 |
| V2-F ecart qui grandit BTC | -69 | -31 | +38 | 88 → 30 |
| V2-B hors 60-89 s BTC | +29 | -53 | -81 | 86 → 23 |
| V2-H veto complet BTC | +177 | +41 | -136 | 70 → 24 |
| desaccord 20 Binance ou perp avec nous BTC | -235 | +54 | +289 | 71 → 30 |
| desaccord 20 sans nuit BTC | -198 | -79 | +119 | 53 → 17 |

**Verdict K2 : non confirmée** (IC [-3372 ; +2732], 4 stratégies sur 10 améliorées).


**Verdict K5 : non confirmée** (IC [-4294 ; +2519], 2 stratégies sur 10 améliorées).

