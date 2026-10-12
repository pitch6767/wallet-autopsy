# Bot95 — H1053 : filtre de consensus sur les gagnantes du 12.10

Généré le 12.10.2026 19:33 UTC. Mise ramenée à 10 $ par trade. Aucun ordre.

## Exploration (avant le 13.10, déjà vue) — 7687 trades, base -1539 $, 5981 perdants

| Règle | Trades gardés | P&L gardé ($) | Perdants gardés | Taux de perdants | Écart avec la base ($) | IC 90 % | IC corrigé (9) | Stratégies améliorées |
|---|---|---|---|---|---|---|---|---|
| K2 consensus ≥ 8 et ≥ 120 s | 3565 / 7687 | +5164 | 2683 / 5981 | 75 % (base 78 %) | +6703 | [+2024 ; +11236] | [-579 ; +13484] | 9 / 10 |
| K1 consensus ≥ 8 | 4126 / 7687 | +3395 | 3155 / 5981 | 76 % (base 78 %) | +4935 | [+892 ; +9047] | [-1673 ; +11014] | 9 / 10 |
| K3 consensus ≥ 6 et ≥ 120 s | 4809 / 7687 | +4279 | 3653 / 5981 | 76 % (base 78 %) | +5818 | [+2331 ; +9295] | [+236 ; +10847] | 9 / 10 |
| K4 consensus ≥ 10 et ≥ 120 s | 2301 / 7687 | +5011 | 1712 / 5981 | 74 % (base 78 %) | +6551 | [+670 ; +12245] | [-2239 ; +15699] | 8 / 10 |
| K5 K2 et délai ≤ 3 s | 1590 / 7687 | +6066 | 1111 / 5981 | 70 % (base 78 %) | +7605 | [+894 ; +14048] | [-2990 ; +17417] | 9 / 10 |
| K6 K2 et aucun opposé | 3329 / 7687 | +4807 | 2493 / 5981 | 75 % (base 78 %) | +6346 | [+1155 ; +11154] | [-2129 ; +14129] | 10 / 10 |
| K7 K2 et délai ≤ 1 s | 1438 / 7687 | +6396 | 990 / 5981 | 69 % (base 78 %) | +7935 | [+1102 ; +14698] | [-3246 ; +18266] | 9 / 10 |
| K8 K5 et pause si 12 h ≤ 0 | 562 / 7687 | +4507 | 357 / 5981 | 64 % (base 78 %) | +6046 | [-2153 ; +13914] | [-7017 ; +18345] | 9 / 10 |
| K9 K5 et consensus ≥ 15 | 160 / 7687 | +672 | 82 / 5981 | 51 % (base 78 %) | +2211 | [-6366 ; +11084] | [-11395 ; +15298] | 8 / 10 |

| Stratégie | Base ($) | K2 ($) | Écart | Perdants base → K2 |
|---|---|---|---|---|
| V2-F + pas les deux baissent BTC | -414 | +504 | +919 | 656 → 286 |
| V2-D perp 120-269 s BTC | +486 | +554 | +68 | 597 → 410 |
| V2-F + plus de 120 s BTC | -184 | +523 | +706 | 554 → 253 |
| V2-C perp BTC | -143 | +583 | +726 | 712 → 374 |
| V2-G jury des bourses BTC | -54 | +603 | +658 | 687 → 458 |
| V2-F ecart qui grandit BTC | -586 | +584 | +1170 | 704 → 262 |
| V2-B hors 60-89 s BTC | -426 | +646 | +1072 | 705 → 175 |
| V2-H veto complet BTC | -516 | +100 | +616 | 708 → 286 |
| desaccord 20 Binance ou perp avec nous BTC | +626 | +601 | -25 | 148 → 48 |
| desaccord 20 sans nuit BTC | -327 | +466 | +793 | 510 → 131 |

## TEST (≥ 13.10, jamais vu) — 0 trades, base +0 $, 0 perdants
