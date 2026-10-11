# Bot95 — Autopsie des makers et preneurs rentables (H681–H710) — PRÉLIMINAIRE

Généré le 11.10.2026 16:58 UTC. 600 marchés BTC 5 min lus du 09.10 13:40 au 11.10 15:35 UTC (avant la période réservée). Marchés INCOMPLETS (≥ 10 000 exécutions, plafond de l'API) : 5 — exclus de tous les calculs de résultat ci-dessous.

FAITS : exécutions (API Data : portefeuille, maker/preneur, issue, côté, parts, prix, seconde) et activité (fusions, règlements, récompenses). INFÉRENCES : l'interprétation. Frais preneur 0,07·p·(1−p) comptés ; ristourne maker comptée seulement si visible dans l'activité (REWARD). Une vente sans achat visible (jetons venus d'une séparation ou d'un transfert) est signalée.

## 1. Les portefeuilles étudiés (25 plus gros makers, 20 plus rentables, 3 preneurs)

| Portefeuille (adresse complète) | Marchés | Volume maker | Volume preneur | Résultat (paires + jambes seules + ventes − frais) | par $ | 1re moitié / 2e moitié | Creux | Part des 5 meilleurs marchés | Capital médian / max par marché | Fusions | Récompenses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4da70f3e6d5eee06933ebef143efc87` | 584 | 571543 $ | 128 $ | -3292 $ | -0.6 % | +1446 / -4738 $ | -8897 $ | — | 754 / 5837 $ | 0 | 0 $ |
| `0x21f4c1a1be34a39a7bc20985df4b7e5a39fb691d` | 581 | 335992 $ | 97643 $ | -6465 $ | -1.5 % | -8609 / +2144 $ | -10443 $ | — | 541 / 7112 $ | 0 | 0 $ |
| `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354` | 595 | 269307 $ | 335469 $ | +473 $ | +0.1 % | -565 / +1037 $ | -1314 $ | 158 % | 909 / 2922 $ | 0 | 0 $ |
| `0xaa1a4f31c010d4a63fc49770d4ca2d69ea370602` | 573 | 236711 $ | 0 $ | -3389 $ | -1.4 % | -2652 / -737 $ | -4135 $ | — | 365 / 1429 $ | 0 | 0 $ |
| `0xe29042f5d913dcc4015aab3455c13c58514ca33f` | 593 | 231170 $ | 18712 $ | +3595 $ | +1.4 % | +1601 / +1994 $ | -747 $ | 35 % | 360 / 1652 $ | 0 | 0 $ |
| `0x239e726f1f4131ca78a7e5abf1fec86bfc151c10` | 594 | 192993 $ | 38929 $ | -2262 $ | -1.0 % | -3246 / +984 $ | -5672 $ | — | 276 / 2673 $ | 0 | 0 $ |
| `0x764fd57b0b885cbeada5a119cdf0a113ee4ec347` | 503 | 188634 $ | 27169 $ | -8088 $ | -3.7 % | -9056 / +968 $ | -9876 $ | — | 201 / 5069 $ | 103 | 488 $ |
| `0x6940545d736920890c575cc73dbf0959a3831c6c` | 69 | 181102 $ | 21968 $ | +395 $ | +0.2 % | +247 / +148 $ | -5 $ | 35 % | 1003 / 10509 $ | 0 | 5 $ |
| `0x1a80c37798935774f92fa2f376f0a4e4a7e83b26` | 450 | 157105 $ | 12788 $ | -252 $ | -0.1 % | -308 / +55 $ | -549 $ | — | 302 / 659 $ | 0 | 58 $ |
| `0x32ed2e546b187ca15e2841edc82b22c713cf8ec3` | 492 | 156335 $ | 62281 $ | -124 $ | -0.1 % | +1909 / -2032 $ | -3629 $ | — | 317 / 2770 $ | 200 | 524 $ |
| `0x18c18e0c8c3154360b4f730ec8b9d8013ceb2183` | 501 | 154058 $ | 2301 $ | +1841 $ | +1.2 % | +748 / +1093 $ | -153 $ | 16 % | 269 / 1411 $ | 10 | 0 $ |
| `0xcd30457c790d8b35a08bcf3f894ad6bb52bc2dd0` | 590 | 153287 $ | 499 $ | +2685 $ | +1.7 % | +1185 / +1500 $ | -431 $ | 37 % | 208 / 1243 $ | 0 | 0 $ |
| `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c` | 587 | 147462 $ | 0 $ | +1209 $ | +0.8 % | +16 / +1193 $ | -1451 $ | 71 % | 197 / 1247 $ | 137 | 0 $ |
| `0x73e40b377cf4ac7034d0afaf66abb58f3424fb79` | 189 | 139661 $ | 2221 $ | -370 $ | -0.3 % | -456 / +86 $ | -1186 $ | — | 891 / 1300 $ | 0 | 20 $ |
| `0x3725d52f3c252e8374999cc8617292ea2608ad88` | 456 | 138485 $ | 40100 $ | +34 $ | +0.0 % | +1537 / -1503 $ | -5010 $ | 8975 % | 288 / 3710 $ | 174 | 488 $ |
| `0xc2ad03f79ca3f3c17d8c7de2612ce0c89b7d40ed` | 465 | 135990 $ | 39777 $ | -2592 $ | -1.5 % | -287 / -2305 $ | -5868 $ | — | 258 / 2046 $ | 192 | 473 $ |
| `0x55aeeb3eb4e8cc0da6d9e4939caf533bf6c3f5df` | 466 | 135095 $ | 640 $ | +940 $ | +0.7 % | +1089 / -149 $ | -810 $ | 216 % | 222 / 620 $ | 103 | 22 $ |
| `0xee65685de42f8de9a03b4c53ee77d56a20d2cfc9` | 197 | 133608 $ | 26796 $ | +2433 $ | +1.5 % | +1924 / +509 $ | -1088 $ | 254 % | 39 / 9017 $ | 0 | 74 $ |
| `0x322b2e7c44237c9fed01d534cd1c96687d52aa0c` | 592 | 130457 $ | 0 $ | -1478 $ | -1.1 % | -1173 / -305 $ | -1636 $ | — | 194 / 658 $ | 0 | 0 $ |
| `0x4c9497941333332d29f1c235dd23200f3623ffad` | 594 | 127408 $ | 0 $ | +1781 $ | +1.4 % | +1084 / +697 $ | -738 $ | 50 % | 176 / 937 $ | 161 | 0 $ |
| `0xaef68b9bbd746ffe4e582a687cf8a21f1c44134f` | 524 | 120108 $ | 0 $ | -145 $ | -0.1 % | -126 / -19 $ | -754 $ | — | 263 / 588 $ | 0 | 37 $ |
| `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b` | 595 | 119868 $ | 0 $ | +1279 $ | +1.1 % | +863 / +416 $ | -765 $ | 70 % | 166 / 860 $ | 165 | 0 $ |
| `0x3884acd922095fc579938f2c6d1569decc38416d` | 132 | 119304 $ | 0 $ | +119 $ | +0.1 % | +82 / +38 $ | +0 $ | 25 % | 84 / 9990 $ | 0 | 2 $ |
| `0x6bfcdf6d90886487e1c70b84776f148dba73b939` | 143 | 118944 $ | 2095 $ | -779 $ | -0.6 % | +711 / -1490 $ | -2005 $ | — | 880 / 2005 $ | 0 | 17 $ |
| `0xb1d30490fa2ec8dc55591e8c71d3d64b6e0fc279` | 139 | 117929 $ | 72900 $ | -174 $ | -0.1 % | +1780 / -1954 $ | -2985 $ | — | 441 / 9133 $ | non lu | non lu |
| `0x9783f45ce35f794be38ca47dd0816a5c241383b9` | 55 | 0 $ | 23169 $ | +13414 $ | +57.9 % | +11321 / +2092 $ | -3469 $ | 88 % | 173 / 2743 $ | non lu | non lu |
| `0x11aade7bb6828721f988af53e2a70b67dec9c3d7` | 57 | 338 $ | 58160 $ | +11023 $ | +18.8 % | +13921 / -2898 $ | -5550 $ | 148 % | 705 / 3800 $ | 0 | 8 $ |
| `0x3048d65321be3497164cdfc2996f94f98a2e7537` | 548 | 70428 $ | 252543 $ | +4746 $ | +1.5 % | +3549 / +1197 $ | -1597 $ | 44 % | 408 / 3851 $ | 0 | 215 $ |
| `0xe9076a87c5ed90ef16e6fe6529c943baeca0cff6` | 494 | 4873 $ | 92337 $ | +4639 $ | +4.8 % | +5741 / -1102 $ | -3357 $ | 124 % | 25 / 2310 $ | 0 | 0 $ |
| `0x8640e5845b5cb4ea3d2497a38f55485da2cf0e7d` | 27 | 0 $ | 57900 $ | +4207 $ | +7.3 % | +632 / +3575 $ | -3085 $ | 138 % | 0 / 2000 $ | non lu | non lu |
| `0xc6e3fec2e1a29e7a03e1f2d57f4e4eee39dc8b84` | 182 | 0 $ | 39428 $ | +3835 $ | +9.7 % | +931 / +2903 $ | -2284 $ | 51 % | 147 / 622 $ | non lu | non lu |
| `0xb4f9069e989adfc31eb8d6d551832b1fe1810b71` | 26 | 0 $ | 18287 $ | +3600 $ | +19.7 % | +5556 / -1956 $ | -3645 $ | 235 % | 486 / 1000 $ | non lu | non lu |
| `0x9cbb1a5c3352691f07e2e26209193ce5a2c433d0` | 67 | 0 $ | 10101 $ | +3148 $ | +31.2 % | +2017 / +1131 $ | -896 $ | 56 % | 145 / 409 $ | non lu | non lu |
| `0x6515bf178d18f61c2661983a33c3e96990a8366d` | 26 | 0 $ | 2478 $ | +2919 $ | +117.8 % | +2533 / +386 $ | -247 $ | 92 % | 21 / 433 $ | non lu | non lu |
| `0x32e0f4b7ab1559ba2ba0089cdc05d40e746958be` | 348 | 435 $ | 53405 $ | +2763 $ | +5.1 % | +1416 / +1347 $ | -1829 $ | 34 % | 150 / 165 $ | non lu | non lu |
| `0x7f36360df1dcda25dcc2ea99f67bc2ad4d3afc98` | 277 | 3358 $ | 27135 $ | +2743 $ | +9.0 % | +842 / +1901 $ | -1102 $ | 98 % | 70 / 716 $ | non lu | non lu |
| `0x2ed94d1a460379292d2e3b46f2cf7d94b033f271` | 584 | 25842 $ | 90503 $ | +2577 $ | +2.2 % | +1568 / +1009 $ | -1521 $ | 77 % | 130 / 1822 $ | non lu | non lu |
| `0x6094e34888bc7682fd73e4f9aea4e0b350323bd9` | 24 | 0 $ | 16044 $ | +2383 $ | +14.9 % | +1918 / +465 $ | -895 $ | 148 % | 102 / 869 $ | non lu | non lu |
| `0x21d0a97aac03917e752857a551bbe5103a00e8d7` | 342 | 18510 $ | 20 $ | +2286 $ | +12.3 % | +2869 / -583 $ | -1004 $ | 126 % | 32 / 913 $ | 0 | 200 $ |
| `0xd6c1c2488cb546e0187f083938c744977620ad7e` | 26 | 2148 $ | 10855 $ | +2215 $ | +17.0 % | +739 / +1476 $ | -845 $ | 147 % | 98 / 1973 $ | non lu | non lu |
| `0xeda9247a2b3c99a9e0bf46cdac6e1974365cf589` | 54 | 31 $ | 8811 $ | +2065 $ | +23.4 % | +1658 / +407 $ | -40 $ | 61 % | 32 / 884 $ | non lu | non lu |
| `0xaaeb932924a3ff58124a0cf42bd7bdd90208f963` | 50 | 0 $ | 3341 $ | +1860 $ | +55.7 % | +560 / +1299 $ | -485 $ | 108 % | 28 / 311 $ | non lu | non lu |
| `0xc4e21390f8357e33f6692c3cfc4979592de8fef6` | 208 | 0 $ | 114862 $ | +877 $ | +0.8 % | -1358 / +2235 $ | -2285 $ | 205 % | 374 / 802 $ | 0 | 0 $ |

## 2. Paires Up + Down : d'où vient vraiment le résultat ?

Par portefeuille et par marché : parts appariées = min(Up acheté, Down acheté) après ventes ; coût de la paire = prix moyen Up + prix moyen Down ; résultat des paires = parts appariées × (1 − coût) (acquis quel que soit le gagnant) ; jambe seule = le reste, réglée au résultat officiel.

| Portefeuille | Marchés avec paire | Paire < 1 $ | < 0,98 $ | < 0,95 $ | Coût médian | Délai médian 1re → 2e jambe | Résultat des paires | Résultat des jambes seules | Ventes réalisées | Vente de jetons séparés (déduit) | Frais preneur | Part du résultat venant des paires |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4…` | 517 | 35 % | 30 % | 22 % | 1.071 | 33 s | -42347 $ | +39063 $ | +0 $ | +0 $ (0 $ séparés) | 8 $ | nan % |
| `0x21f4c1a1be…` | 573 | 73 % | 67 % | 56 % | 0.936 | 30 s | +18338 $ | -22908 $ | +0 $ | +0 $ (0 $ séparés) | 1896 $ | nan % |
| `0x41e2e1ccf1…` | 595 | 53 % | 33 % | 15 % | 0.996 | 6 s | +2892 $ | +5830 $ | +0 $ | +0 $ (0 $ séparés) | 8249 $ | 612 % |
| `0xaa1a4f31c0…` | 568 | 70 % | 52 % | 28 % | 0.977 | 16 s | +6619 $ | -10008 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0xe29042f5d9…` | 577 | 74 % | 58 % | 32 % | 0.972 | 22 s | +8444 $ | -4385 $ | +0 $ | +0 $ (0 $ séparés) | 464 $ | 235 % |
| `0x239e726f1f…` | 488 | 73 % | 69 % | 63 % | 0.880 | 42 s | +26801 $ | -27720 $ | +0 $ | +0 $ (0 $ séparés) | 1344 $ | nan % |
| `0x764fd57b0b…` | 498 | 47 % | 40 % | 28 % | 1.005 | 11 s | +550 $ | -8191 $ | +0 $ | +0 $ (0 $ séparés) | 447 $ | nan % |
| `0x6940545d73…` | 1 | 0 % | 0 % | 0 % | 1.009 | 18 s | -5 $ | +409 $ | +0 $ | +0 $ (0 $ séparés) | 10 $ | -1 % |
| `0x1a80c37798…` | 190 | 46 % | 1 % | 1 % | 1.000 | 3 s | -225 $ | -91 $ | +119 $ | +0 $ (0 $ séparés) | 55 $ | nan % |
| `0x32ed2e546b…` | 372 | 45 % | 40 % | 37 % | 1.022 | 42 s | -7645 $ | +9242 $ | +0 $ | +0 $ (0 $ séparés) | 1721 $ | nan % |
| `0x18c18e0c8c…` | 500 | 61 % | 45 % | 23 % | 0.987 | 4 s | +2963 $ | -1451 $ | +344 $ | +0 $ (0 $ séparés) | 15 $ | 161 % |
| `0xcd30457c79…` | 569 | 41 % | 33 % | 22 % | 1.029 | 22 s | -5042 $ | +7781 $ | -40 $ | +0 $ (0 $ séparés) | 15 $ | -188 % |
| `0xf9b7876ba2…` | 569 | 31 % | 20 % | 11 % | 1.042 | 12 s | -5939 $ | +7149 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -491 % |
| `0x73e40b377c…` | 1 | 0 % | 0 % | 0 % | 1.952 | 31 s | -57 $ | -311 $ | +0 $ | +0 $ (0 $ séparés) | 3 $ | nan % |
| `0x3725d52f3c…` | 319 | 46 % | 44 % | 37 % | 1.024 | 48 s | -6136 $ | +7230 $ | +0 $ | +0 $ (0 $ séparés) | 1060 $ | -18185 % |
| `0xc2ad03f79c…` | 323 | 54 % | 50 % | 43 % | 0.980 | 46 s | -4214 $ | +2671 $ | +0 $ | +0 $ (0 $ séparés) | 1049 $ | nan % |
| `0x55aeeb3eb4…` | 142 | 23 % | 6 % | 6 % | 1.000 | 16 s | +2452 $ | -1503 $ | +0 $ | +0 $ (0 $ séparés) | 9 $ | 261 % |
| `0xee65685de4…` | 16 | 0 % | 0 % | 0 % | 1.050 | 138 s | -587 $ | +3022 $ | +0 $ | +0 $ (0 $ séparés) | 2 $ | -24 % |
| `0x322b2e7c44…` | 591 | 68 % | 47 % | 21 % | 0.983 | 19 s | +2486 $ | -3964 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0x4c94979413…` | 573 | 28 % | 19 % | 11 % | 1.046 | 15 s | -5252 $ | +7033 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -295 % |
| `0xaef68b9bbd…` | 0 | — | — | — | — | — | +0 $ | -145 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0x568b079891…` | 575 | 28 % | 21 % | 11 % | 1.045 | 16 s | -5296 $ | +6575 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -414 % |
| `0x3884acd922…` | 0 | — | — | — | — | — | +0 $ | +119 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0x6bfcdf6d90…` | 0 | — | — | — | — | — | +0 $ | -776 $ | +0 $ | +0 $ (0 $ séparés) | 3 $ | 0 % |
| `0xb1d30490fa…` | 4 | 50 % | 50 % | 50 % | 1.165 | 42 s | -4 $ | -74 $ | +0 $ | +0 $ (0 $ séparés) | 96 $ | nan % |
| `0x9783f45ce3…` | 0 | — | — | — | — | — | +0 $ | +14198 $ | +0 $ | +0 $ (0 $ séparés) | 784 $ | 0 % |
| `0x11aade7bb6…` | 1 | 100 % | 100 % | 100 % | 0.848 | 339 s | +0 $ | +14422 $ | -1933 $ | +0 $ (0 $ séparés) | 1466 $ | 0 % |
| `0x3048d65321…` | 529 | 65 % | 54 % | 38 % | 0.974 | 12 s | +9485 $ | +2886 $ | +0 $ | +0 $ (0 $ séparés) | 7625 $ | 200 % |
| `0xe9076a87c5…` | 247 | 48 % | 43 % | 39 % | 1.011 | 90 s | +1424 $ | +37 $ | +5203 $ | +0 $ (0 $ séparés) | 2025 $ | 31 % |
| `0x8640e5845b…` | 0 | — | — | — | — | — | +0 $ | -5200 $ | +10052 $ | +0 $ (0 $ séparés) | 645 $ | 0 % |
| `0xc6e3fec2e1…` | 1 | 0 % | 0 % | 0 % | 1.064 | 249 s | -3 $ | +4933 $ | +0 $ | +0 $ (0 $ séparés) | 1095 $ | -0 % |
| `0xb4f9069e98…` | 0 | — | — | — | — | — | +0 $ | +1332 $ | +2925 $ | +0 $ (0 $ séparés) | 657 $ | 0 % |
| `0x9cbb1a5c33…` | 0 | — | — | — | — | — | +0 $ | +3464 $ | +56 $ | +0 $ (0 $ séparés) | 372 $ | 0 % |
| `0x6515bf178d…` | 0 | — | — | — | — | — | +0 $ | +2996 $ | +20 $ | +0 $ (0 $ séparés) | 97 $ | 0 % |
| `0x32e0f4b7ab…` | 0 | — | — | — | — | — | +0 $ | +2666 $ | +1370 $ | +0 $ (0 $ séparés) | 1273 $ | 0 % |
| `0x7f36360df1…` | 36 | 3 % | 3 % | 3 % | 1.423 | 106 s | -262 $ | +2815 $ | +662 $ | +0 $ (0 $ séparés) | 472 $ | -10 % |
| `0x2ed94d1a46…` | 456 | 55 % | 49 % | 41 % | 0.981 | 58 s | -633 $ | +5078 $ | +0 $ | +0 $ (0 $ séparés) | 1868 $ | -25 % |
| `0x6094e34888…` | 1 | 100 % | 100 % | 100 % | 0.355 | 223 s | +591 $ | -1246 $ | +3432 $ | +0 $ (0 $ séparés) | 394 $ | 25 % |
| `0x21d0a97aac…` | 98 | 98 % | 87 % | 45 % | 0.953 | 58 s | +246 $ | +2041 $ | +0 $ | +0 $ (0 $ séparés) | 1 $ | 11 % |
| `0xd6c1c2488c…` | 8 | 62 % | 62 % | 62 % | 0.852 | 157 s | -26 $ | +2071 $ | +408 $ | +0 $ (0 $ séparés) | 238 $ | -1 % |
| `0xeda9247a2b…` | 24 | 88 % | 79 % | 75 % | 0.783 | 32 s | +666 $ | +605 $ | +935 $ | +0 $ (0 $ séparés) | 142 $ | 32 % |
| `0xaaeb932924…` | 21 | 14 % | 14 % | 14 % | 1.201 | 10 s | +156 $ | +1813 $ | +0 $ | +0 $ (0 $ séparés) | 110 $ | 8 % |
| `0xc4e21390f8…` | 3 | 67 % | 67 % | 0 % | 0.980 | 27 s | +1 $ | -744 $ | +3377 $ | +0 $ (0 $ séparés) | 1757 $ | 0 % |

Vente de jetons séparés : un portefeuille qui VEND des jetons sans les avoir achetés les a obtenus en séparant 1 $ en Up + Down ; on compte ce coût (1 $ la paire) et la jambe non vendue gardée jusqu'au règlement. C'est une déduction (la séparation elle-même n'est visible que dans l'activité).


Lecture : un portefeuille gagne « grâce aux paires » si le résultat des paires est positif et porte l'essentiel du total ; s'il vient des jambes seules, c'est un pari directionnel.

## 3. Autopsie des trois preneurs

### `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354`

595 marchés, volume preneur 335469 $, maker 269307 $ ; marchés avec les deux côtés : 595.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| maker | 0–60 s | BUY | 9065 | 58930 $ | -2331 $ | -0.040 |
| maker | 60–120 s | BUY | 8424 | 53969 $ | +200 $ | +0.004 |
| maker | 120–180 s | BUY | 8723 | 58964 $ | -133 $ | -0.002 |
| maker | 180–240 s | BUY | 9029 | 59847 $ | -556 $ | -0.009 |
| maker | 240–300 s | BUY | 5636 | 37597 $ | +479 $ | +0.013 |
| preneur | 0–60 s | BUY | 2501 | 51629 $ | +3110 $ | +0.060 |
| preneur | 60–120 s | BUY | 3302 | 74702 $ | +1232 $ | +0.016 |
| preneur | 120–180 s | BUY | 3570 | 85066 $ | -1800 $ | -0.021 |
| preneur | 180–240 s | BUY | 3483 | 92988 $ | +525 $ | +0.006 |
| preneur | 240–300 s | BUY | 902 | 31084 $ | -253 $ | -0.008 |

### `0x11aade7bb6828721f988af53e2a70b67dec9c3d7`

57 marchés, volume preneur 58160 $, maker 338 $ ; marchés avec les deux côtés : 1.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| maker | 60–120 s | SELL | 22 | 213 $ | -174 $ | -0.818 |
| maker | 240–300 s | SELL | 23 | 125 $ | +125 $ | +1.000 |
| preneur | -180–-120 s | BUY | 2 | 75 $ | +60 $ | +0.800 |
| preneur | -120–-60 s | BUY | 10 | 955 $ | -493 $ | -0.516 |
| preneur | -60–0 s | BUY | 37 | 6891 $ | +499 $ | +0.072 |
| preneur | 0–60 s | BUY | 53 | 11628 $ | +1308 $ | +0.112 |
| preneur | 60–120 s | BUY | 44 | 13164 $ | +5205 $ | +0.395 |
| preneur | 60–120 s | SELL | 1 | 250 $ | -95 $ | -0.380 |
| preneur | 120–180 s | BUY | 69 | 13135 $ | +8002 $ | +0.609 |
| preneur | 120–180 s | SELL | 1 | 312 $ | -25 $ | -0.080 |
| preneur | 180–240 s | BUY | 25 | 7646 $ | -2991 $ | -0.391 |
| preneur | 180–240 s | SELL | 2 | 64 $ | +60 $ | +0.932 |
| preneur | 240–300 s | BUY | 8 | 2339 $ | -490 $ | -0.210 |
| preneur | 240–300 s | SELL | 4 | 1700 $ | +33 $ | +0.019 |

### `0xc4e21390f8357e33f6692c3cfc4979592de8fef6`

208 marchés, volume preneur 114862 $, maker 0 $ ; marchés avec les deux côtés : 3.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| preneur | 0–60 s | BUY | 1505 | 66423 $ | +2577 $ | +0.039 |
| preneur | 0–60 s | SELL | 1 | 120 $ | -13 $ | -0.105 |
| preneur | 60–120 s | BUY | 481 | 22059 $ | -499 $ | -0.023 |
| preneur | 60–120 s | SELL | 5 | 1748 $ | -269 $ | -0.154 |
| preneur | 120–180 s | BUY | 89 | 4915 $ | +184 $ | +0.037 |
| preneur | 120–180 s | SELL | 12 | 6914 $ | +210 $ | +0.030 |
| preneur | 180–240 s | BUY | 15 | 389 $ | -36 $ | -0.094 |
| preneur | 180–240 s | SELL | 16 | 5118 $ | -976 $ | -0.191 |
| preneur | 240–300 s | BUY | 6 | 95 $ | -18 $ | -0.184 |
| preneur | 240–300 s | SELL | 20 | 7081 $ | -284 $ | -0.040 |

## 4. Risque d'achat à 0,95–0,99 en fin de cycle (M9) — toutes les exécutions de tous les portefeuilles

Achats MAKER à ces prix dans les 30 dernières secondes (aucun frais maker ; ristourne non comptée, de l'ordre de 0,02 c par part à ces prix).

| Prix | Remplissages | Parts | Marchés | Remplissages perdants | Taux de victoire nécessaire (seuil) | Taux observé | Résultat | par part | Plus grosse perte d'un remplissage |
|---|---|---|---|---|---|---|---|---|---|
| 0,95–0,97 | 1830 | 38075 | 93 | 37 | ≈ 96 % | 97.98 % | +914 $ | +2.40 c | 54 $ |
| 0,97–0,98 | 1081 | 29590 | 103 | 1 | ≈ 97,5 % | 99.91 % | +868 $ | +2.93 c | 18 $ |
| 0,98–0,99 | 1633 | 54686 | 134 | 11 | ≈ 98,5 % | 99.33 % | +627 $ | +1.15 c | 132 $ |
| ≥ 0,99 | 12617 | 1319814 | 588 | 34 | ≈ 99,3 % | 99.73 % | +4187 $ | +0.32 c | 584 $ |

Lecture : à 0,98, une seule part perdue coûte 0,98 $ et efface 49 parts gagnées. Une politique plafonnée à 0,95 se lit sur la 1re ligne.

**Séparation par temps restant** (achats maker, mêmes tranches de prix)

| Prix | 30–15 s restantes : remplis / perdants / résultat | 15–5 s | 5–0 s |
|---|---|---|---|
| 0,95–0,97 | 1547 / 32 / +723 $ | 213 / 5 / +52 $ | 59 / 0 / +76 $ |
| 0,97–0,98 | 908 / 1 / +706 $ | 136 / 0 / +113 $ | 31 / 0 / +38 $ |
| 0,98–0,99 | 1293 / 11 / +404 $ | 271 / 0 / +170 $ | 53 / 0 / +27 $ |
| ≥ 0,99 | 4830 / 34 / -1033 $ | 3304 / 0 / +2084 $ | 1201 / 0 / +834 $ |

## 5. Intégrité des données

- Marchés lus : 600 ; incomplets (≥ 10 000 exécutions) : 5 (exclus des résultats). Plafond de l'API Data : décalage ≤ 10 000.
- Événements blockchain (OrderFilled) : le sous-graphe public Goldsky a répondu « trop de requêtes » (429) depuis GitHub ; reconstruction par la blockchain NON faite à ce stade.
- Maker / preneur : déduit de l'API Data (liste « preneur seulement »), non vérifié contre les événements blockchain.
- Fusions, séparations, règlements, récompenses : lus dans l'activité des portefeuilles étudiés seulement (« non lu » sinon). Une vente sans achat visible signale des jetons venus d'une séparation.
- Ristournes maker : comptées seulement si l'activité les montre. Frais preneur : calculés (0,07·p·(1−p)).
