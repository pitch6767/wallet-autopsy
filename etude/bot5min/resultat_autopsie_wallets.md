# Bot95 — Autopsie des makers et preneurs rentables (H681–H710) — PRÉLIMINAIRE

Généré le 11.10.2026 14:08 UTC. 300 marchés BTC 5 min lus du 10.10 12:25 au 11.10 13:20 UTC (avant la période réservée). Marchés INCOMPLETS (≥ 10 000 exécutions, plafond de l'API) : 88 — exclus de tous les calculs de résultat ci-dessous.

FAITS : exécutions (API Data : portefeuille, maker/preneur, issue, côté, parts, prix, seconde) et activité (fusions, règlements, récompenses). INFÉRENCES : l'interprétation. Frais preneur 0,07·p·(1−p) comptés ; ristourne maker comptée seulement si visible dans l'activité (REWARD). Une vente sans achat visible (jetons venus d'une séparation ou d'un transfert) est signalée.

## 1. Les portefeuilles étudiés (25 plus gros makers, 20 plus rentables, 3 preneurs)

| Portefeuille (adresse complète) | Marchés | Volume maker | Volume preneur | Résultat (paires + jambes seules + ventes − frais) | par $ | 1re moitié / 2e moitié | Creux | Part des 5 meilleurs marchés | Capital médian / max par marché | Fusions | Récompenses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4da70f3e6d5eee06933ebef143efc87` | 207 | 156476 $ | 0 $ | +8989 $ | +5.7 % | +5539 / +3450 $ | -589 $ | 20 % | 683 / 2783 $ | non lu | non lu |
| `0xe29042f5d913dcc4015aab3455c13c58514ca33f` | 210 | 90373 $ | 8369 $ | -749 $ | -0.8 % | -44 / -705 $ | -1537 $ | — | 453 / 1218 $ | non lu | non lu |
| `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354` | 212 | 80879 $ | 91346 $ | +600 $ | +0.3 % | +16 / +584 $ | -348 $ | 102 % | 770 / 1656 $ | non lu | non lu |
| `0x21f4c1a1be34a39a7bc20985df4b7e5a39fb691d` | 207 | 76141 $ | 15852 $ | +1015 $ | +1.1 % | +814 / +200 $ | -583 $ | 92 % | 385 / 1656 $ | non lu | non lu |
| `0xaa1a4f31c010d4a63fc49770d4ca2d69ea370602` | 207 | 64300 $ | 0 $ | -1377 $ | -2.1 % | -639 / -738 $ | -1508 $ | — | 312 / 665 $ | non lu | non lu |
| `0x18c18e0c8c3154360b4f730ec8b9d8013ceb2183` | 177 | 55402 $ | 1474 $ | +384 $ | +0.7 % | +169 / +215 $ | -98 $ | 59 % | 308 / 616 $ | non lu | non lu |
| `0x32ed2e546b187ca15e2841edc82b22c713cf8ec3` | 180 | 49087 $ | 21700 $ | +3379 $ | +4.8 % | +3630 / -251 $ | -1318 $ | 58 % | 309 / 1940 $ | non lu | non lu |
| `0x239e726f1f4131ca78a7e5abf1fec86bfc151c10` | 211 | 47708 $ | 3463 $ | -6253 $ | -12.2 % | -1911 / -4342 $ | -6471 $ | — | 204 / 918 $ | non lu | non lu |
| `0x1a80c37798935774f92fa2f376f0a4e4a7e83b26` | 148 | 47107 $ | 2769 $ | +23 $ | +0.0 % | +112 / -90 $ | -161 $ | 129 % | 298 / 636 $ | non lu | non lu |
| `0xaef68b9bbd746ffe4e582a687cf8a21f1c44134f` | 190 | 44917 $ | 0 $ | +661 $ | +1.5 % | +566 / +95 $ | -314 $ | 6 % | 294 / 419 $ | non lu | non lu |
| `0xc2ad03f79ca3f3c17d8c7de2612ce0c89b7d40ed` | 177 | 44657 $ | 12165 $ | +1933 $ | +3.4 % | +2309 / -376 $ | -1092 $ | 69 % | 213 / 1773 $ | non lu | non lu |
| `0x3725d52f3c252e8374999cc8617292ea2608ad88` | 177 | 44063 $ | 9472 $ | +3763 $ | +7.0 % | +3297 / +466 $ | -989 $ | 48 % | 223 / 1385 $ | non lu | non lu |
| `0x55aeeb3eb4e8cc0da6d9e4939caf533bf6c3f5df` | 161 | 40837 $ | 190 $ | +360 $ | +0.9 % | +66 / +294 $ | -332 $ | 188 % | 137 / 600 $ | non lu | non lu |
| `0xdcedfd60071d904471fb22464be85f54139992c6` | 207 | 39995 $ | 0 $ | +262 $ | +0.7 % | +481 / -219 $ | -377 $ | 146 % | 159 / 594 $ | non lu | non lu |
| `0xee65685de42f8de9a03b4c53ee77d56a20d2cfc9` | 84 | 39799 $ | 15377 $ | -922 $ | -1.7 % | -721 / -201 $ | -1180 $ | — | 38 / 6881 $ | non lu | non lu |
| `0xcd30457c790d8b35a08bcf3f894ad6bb52bc2dd0` | 210 | 38415 $ | 184 $ | +1196 $ | +3.1 % | +784 / +412 $ | -178 $ | 31 % | 171 / 545 $ | non lu | non lu |
| `0xf8af03f1e68ee7162db8983f0d6dd0dc869854c6` | 212 | 37752 $ | 1459 $ | -220 $ | -0.6 % | +222 / -442 $ | -648 $ | — | 154 / 580 $ | non lu | non lu |
| `0x322b2e7c44237c9fed01d534cd1c96687d52aa0c` | 210 | 34044 $ | 0 $ | -614 $ | -1.8 % | -271 / -343 $ | -775 $ | — | 160 / 304 $ | non lu | non lu |
| `0x720babbde4ee159d8735ee09a1e35c4bdb46d2cd` | 172 | 33365 $ | 3124 $ | -124 $ | -0.3 % | +40 / -164 $ | -215 $ | — | 198 / 339 $ | non lu | non lu |
| `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c` | 209 | 32923 $ | 0 $ | +1944 $ | +5.9 % | +1501 / +443 $ | -174 $ | 21 % | 141 / 411 $ | non lu | non lu |
| `0x4c9497941333332d29f1c235dd23200f3623ffad` | 212 | 31447 $ | 0 $ | +1818 $ | +5.8 % | +1381 / +437 $ | -162 $ | 22 % | 137 / 417 $ | non lu | non lu |
| `0x85a186d1a0be8593bf7eb5d323f96d932bc991b9` | 210 | 30783 $ | 0 $ | -639 $ | -2.1 % | -278 / -361 $ | -687 $ | — | 147 / 249 $ | non lu | non lu |
| `0xeba7be146396301075344bb2d477f2ffdba92d1f` | 86 | 30716 $ | 0 $ | +310 $ | +1.0 % | +160 / +151 $ | +0 $ | 6 % | 396 / 396 $ | non lu | non lu |
| `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b` | 212 | 29760 $ | 0 $ | +1360 $ | +4.6 % | +954 / +407 $ | -220 $ | 25 % | 135 / 407 $ | non lu | non lu |
| `0x56f609c609975454bf851f0d91079fbc4a5fe251` | 177 | 29595 $ | 4699 $ | +2982 $ | +8.7 % | +2145 / +837 $ | -349 $ | 18 % | 342 / 1000 $ | non lu | non lu |
| `0x368a83f2686acc0db0681e010f410ce323e53057` | 53 | 0 $ | 59936 $ | +7166 $ | +12.0 % | +6191 / +975 $ | -1236 $ | 65 % | 900 / 4716 $ | non lu | non lu |
| `0xc4e21390f8357e33f6692c3cfc4979592de8fef6` | 96 | 0 $ | 56837 $ | +5890 $ | +10.4 % | +3143 / +2747 $ | -1589 $ | 31 % | 410 / 802 $ | non lu | non lu |
| `0x32e0f4b7ab1559ba2ba0089cdc05d40e746958be` | 127 | 0 $ | 19569 $ | +4269 $ | +21.8 % | +2525 / +1743 $ | -532 $ | 15 % | 150 / 150 $ | non lu | non lu |
| `0xc6e3fec2e1a29e7a03e1f2d57f4e4eee39dc8b84` | 79 | 0 $ | 26153 $ | +3880 $ | +14.8 % | +1188 / +2692 $ | -1669 $ | 49 % | 270 / 613 $ | non lu | non lu |
| `0xa9a7b6ac35afed85fed9cde1768c1b09a13bfa09` | 35 | 9016 $ | 12987 $ | +1673 $ | +7.6 % | +1273 / +400 $ | -599 $ | 71 % | 50 / 600 $ | non lu | non lu |
| `0x7f36360df1dcda25dcc2ea99f67bc2ad4d3afc98` | 103 | 1604 $ | 9225 $ | +1555 $ | +14.4 % | +809 / +746 $ | -258 $ | 79 % | 75 / 275 $ | non lu | non lu |
| `0x8718dce13f775c14054c4840cded8b2d2fb7ff8c` | 23 | 0 $ | 6564 $ | +1206 $ | +18.4 % | -7 / +1213 $ | -516 $ | 132 % | 100 / 700 $ | non lu | non lu |
| `0x361528e242bc6cc789ac8da6fd5cb98046178fdf` | 124 | 0 $ | 17516 $ | +1200 $ | +6.9 % | +736 / +464 $ | -246 $ | 54 % | 92 / 927 $ | non lu | non lu |
| `0x2ed94d1a460379292d2e3b46f2cf7d94b033f271` | 209 | 4857 $ | 28448 $ | +1156 $ | +3.5 % | +318 / +838 $ | -683 $ | 102 % | 114 / 1008 $ | non lu | non lu |
| `0x81ff4f443803cb0885cd3683d412b1cd1aa79c4d` | 212 | 11841 $ | 0 $ | +1098 $ | +9.3 % | +660 / +438 $ | -37 $ | 18 % | 48 / 246 $ | non lu | non lu |
| `0xeebde7a0e019a63e6b476eb425505b7b3e6eba30` | 204 | 4112 $ | 30537 $ | +1027 $ | +3.0 % | +293 / +734 $ | -526 $ | 77 % | 124 / 1051 $ | non lu | non lu |
| `0x11aade7bb6828721f988af53e2a70b67dec9c3d7` | 22 | 0 $ | 21799 $ | -713 $ | -3.3 % | -2803 / +2090 $ | -4696 $ | — | 547 / 2900 $ | non lu | non lu |

## 2. Paires Up + Down : d'où vient vraiment le résultat ?

Par portefeuille et par marché : parts appariées = min(Up acheté, Down acheté) après ventes ; coût de la paire = prix moyen Up + prix moyen Down ; résultat des paires = parts appariées × (1 − coût) (acquis quel que soit le gagnant) ; jambe seule = le reste, réglée au résultat officiel.

| Portefeuille | Marchés avec paire | Paire < 1 $ | < 0,98 $ | < 0,95 $ | Coût médian | Délai médian 1re → 2e jambe | Résultat des paires | Résultat des jambes seules | Ventes réalisées | Vente de jetons séparés (déduit) | Frais preneur | Part du résultat venant des paires |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x86b14772a4…` | 195 | 48 % | 42 % | 32 % | 1.005 | 27 s | -2693 $ | +11682 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -30 % |
| `0xe29042f5d9…` | 204 | 72 % | 58 % | 33 % | 0.970 | 22 s | +3239 $ | -3797 $ | +0 $ | +0 $ (0 $ séparés) | 191 $ | nan % |
| `0x41e2e1ccf1…` | 212 | 53 % | 33 % | 12 % | 0.996 | 5 s | +1279 $ | +1509 $ | +0 $ | +0 $ (0 $ séparés) | 2187 $ | 213 % |
| `0x21f4c1a1be…` | 203 | 72 % | 65 % | 53 % | 0.944 | 38 s | +5151 $ | -3876 $ | +0 $ | +0 $ (0 $ séparés) | 260 $ | 508 % |
| `0xaa1a4f31c0…` | 204 | 62 % | 41 % | 19 % | 0.991 | 16 s | +746 $ | -2123 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0x18c18e0c8c…` | 177 | 65 % | 47 % | 20 % | 0.985 | 4 s | +1243 $ | -1144 $ | +288 $ | +0 $ (0 $ séparés) | 3 $ | 324 % |
| `0x32ed2e546b…` | 125 | 46 % | 42 % | 39 % | 1.016 | 40 s | -1397 $ | +5392 $ | +0 $ | +0 $ (0 $ séparés) | 617 $ | -41 % |
| `0x239e726f1f…` | 156 | 75 % | 72 % | 67 % | 0.867 | 31 s | +5487 $ | -11608 $ | +0 $ | +0 $ (0 $ séparés) | 133 $ | nan % |
| `0x1a80c37798…` | 67 | 46 % | 0 % | 0 % | 1.000 | 3 s | -104 $ | +105 $ | +33 $ | +0 $ (0 $ séparés) | 12 $ | -457 % |
| `0xaef68b9bbd…` | 0 | — | — | — | — | — | +0 $ | +661 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0xc2ad03f79c…` | 111 | 45 % | 41 % | 41 % | 1.020 | 44 s | -1706 $ | +3935 $ | +0 $ | +0 $ (0 $ séparés) | 296 $ | -88 % |
| `0x3725d52f3c…` | 105 | 46 % | 44 % | 36 % | 1.011 | 41 s | -939 $ | +4942 $ | +0 $ | +0 $ (0 $ séparés) | 241 $ | -25 % |
| `0x55aeeb3eb4…` | 57 | 25 % | 7 % | 7 % | 1.000 | 22 s | +708 $ | -343 $ | +0 $ | +0 $ (0 $ séparés) | 6 $ | 197 % |
| `0xdcedfd6007…` | 174 | 22 % | 17 % | 14 % | 1.114 | 55 s | -1621 $ | +1883 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -619 % |
| `0xee65685de4…` | 5 | 0 % | 0 % | 0 % | 1.051 | 160 s | -145 $ | -776 $ | +0 $ | +0 $ (0 $ séparés) | 1 $ | nan % |
| `0xcd30457c79…` | 202 | 47 % | 34 % | 24 % | 1.006 | 18 s | -457 $ | +1671 $ | -12 $ | +0 $ (0 $ séparés) | 5 $ | -38 % |
| `0xf8af03f1e6…` | 178 | 22 % | 20 % | 13 % | 1.115 | 60 s | -1769 $ | +1595 $ | +0 $ | +0 $ (0 $ séparés) | 46 $ | nan % |
| `0x322b2e7c44…` | 210 | 61 % | 38 % | 11 % | 0.991 | 18 s | +296 $ | -910 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0x720babbde4…` | 62 | 39 % | 0 % | 0 % | 1.000 | 8 s | -80 $ | -83 $ | +49 $ | +0 $ (0 $ séparés) | 10 $ | nan % |
| `0xf9b7876ba2…` | 204 | 41 % | 28 % | 19 % | 1.020 | 14 s | -964 $ | +2908 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -50 % |
| `0x4c94979413…` | 207 | 36 % | 23 % | 14 % | 1.030 | 14 s | -918 $ | +2736 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -51 % |
| `0x85a186d1a0…` | 210 | 56 % | 32 % | 6 % | 0.996 | 18 s | +98 $ | -737 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | nan % |
| `0xeba7be1463…` | 0 | — | — | — | — | — | +0 $ | +310 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | 0 % |
| `0x568b079891…` | 207 | 34 % | 25 % | 14 % | 1.021 | 15 s | -916 $ | +2276 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -67 % |
| `0x56f609c609…` | 0 | — | — | — | — | — | +0 $ | +0 $ | +0 $ | +3108 $ (61827 $ séparés) | 125 $ | 0 % |
| `0x368a83f268…` | 2 | 0 % | 0 % | 0 % | 1.383 | 128 s | -0 $ | +10492 $ | -2524 $ | +0 $ (0 $ séparés) | 802 $ | -0 % |
| `0xc4e21390f8…` | 3 | 67 % | 67 % | 0 % | 0.980 | 27 s | +1 $ | +6658 $ | +200 $ | +0 $ (0 $ séparés) | 967 $ | 0 % |
| `0x32e0f4b7ab…` | 0 | — | — | — | — | — | +0 $ | +4487 $ | +239 $ | +0 $ (0 $ séparés) | 457 $ | 0 % |
| `0xc6e3fec2e1…` | 1 | 0 % | 0 % | 0 % | 1.064 | 249 s | -3 $ | +4603 $ | +0 $ | +0 $ (0 $ séparés) | 719 $ | -0 % |
| `0xa9a7b6ac35…` | 0 | — | — | — | — | — | +0 $ | +960 $ | +908 $ | +0 $ (0 $ séparés) | 195 $ | 0 % |
| `0x7f36360df1…` | 7 | 0 % | 0 % | 0 % | 1.325 | 74 s | -26 $ | +1358 $ | +367 $ | +0 $ (0 $ séparés) | 144 $ | -2 % |
| `0x8718dce13f…` | 0 | — | — | — | — | — | +0 $ | +1033 $ | +348 $ | +0 $ (0 $ séparés) | 175 $ | 0 % |
| `0x361528e242…` | 9 | 22 % | 22 % | 11 % | 1.136 | 63 s | -82 $ | +1440 $ | +0 $ | +0 $ (0 $ séparés) | 158 $ | -7 % |
| `0x2ed94d1a46…` | 147 | 55 % | 50 % | 40 % | 0.981 | 53 s | +288 $ | +1427 $ | +0 $ | +0 $ (0 $ séparés) | 559 $ | 25 % |
| `0x81ff4f4438…` | 179 | 39 % | 34 % | 25 % | 1.029 | 24 s | -439 $ | +1536 $ | +0 $ | +0 $ (0 $ séparés) | 0 $ | -40 % |
| `0xeebde7a0e0…` | 144 | 49 % | 44 % | 36 % | 1.005 | 53 s | -53 $ | +1626 $ | +0 $ | +0 $ (0 $ séparés) | 546 $ | -5 % |
| `0x11aade7bb6…` | 0 | — | — | — | — | — | +0 $ | +1075 $ | -1327 $ | +0 $ (0 $ séparés) | 462 $ | 0 % |

Vente de jetons séparés : un portefeuille qui VEND des jetons sans les avoir achetés les a obtenus en séparant 1 $ en Up + Down ; on compte ce coût (1 $ la paire) et la jambe non vendue gardée jusqu'au règlement. C'est une déduction (la séparation elle-même n'est visible que dans l'activité).


Lecture : un portefeuille gagne « grâce aux paires » si le résultat des paires est positif et porte l'essentiel du total ; s'il vient des jambes seules, c'est un pari directionnel.

## 3. Autopsie des trois preneurs

### `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354`

212 marchés, volume preneur 91346 $, maker 80879 $ ; marchés avec les deux côtés : 212.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| maker | 0–60 s | BUY | 3474 | 22034 $ | -1825 $ | -0.083 |
| maker | 60–120 s | BUY | 2821 | 17787 $ | +305 $ | +0.017 |
| maker | 120–180 s | BUY | 2738 | 18468 $ | -98 $ | -0.005 |
| maker | 180–240 s | BUY | 2438 | 17186 $ | -83 $ | -0.005 |
| maker | 240–300 s | BUY | 646 | 5403 $ | -49 $ | -0.009 |
| preneur | 0–60 s | BUY | 1039 | 19524 $ | +1220 $ | +0.062 |
| preneur | 60–120 s | BUY | 1246 | 26045 $ | +764 $ | +0.029 |
| preneur | 120–180 s | BUY | 1092 | 23971 $ | +291 $ | +0.012 |
| preneur | 180–240 s | BUY | 835 | 19019 $ | +57 $ | +0.003 |
| preneur | 240–300 s | BUY | 94 | 2787 $ | +17 $ | +0.006 |

### `0x11aade7bb6828721f988af53e2a70b67dec9c3d7`

22 marchés, volume preneur 21799 $, maker 0 $ ; marchés avec les deux côtés : 0.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| preneur | -180–-120 s | BUY | 2 | 75 $ | +60 $ | +0.800 |
| preneur | -60–0 s | BUY | 8 | 1202 $ | -202 $ | -0.168 |
| preneur | 0–60 s | BUY | 24 | 4749 $ | -872 $ | -0.184 |
| preneur | 60–120 s | BUY | 17 | 5505 $ | -1561 $ | -0.284 |
| preneur | 120–180 s | BUY | 32 | 6719 $ | +1769 $ | +0.263 |
| preneur | 180–240 s | BUY | 7 | 1840 $ | +51 $ | +0.028 |
| preneur | 180–240 s | SELL | 2 | 64 $ | +60 $ | +0.932 |
| preneur | 240–300 s | SELL | 2 | 1646 $ | -18 $ | -0.011 |

### `0xc4e21390f8357e33f6692c3cfc4979592de8fef6`

96 marchés, volume preneur 56837 $, maker 0 $ ; marchés avec les deux côtés : 3.

| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |
|---|---|---|---|---|---|---|
| preneur | 0–60 s | BUY | 816 | 39211 $ | +5535 $ | +0.141 |
| preneur | 60–120 s | BUY | 173 | 9719 $ | +906 $ | +0.093 |
| preneur | 60–120 s | SELL | 2 | 810 $ | -159 $ | -0.196 |
| preneur | 120–180 s | BUY | 69 | 4155 $ | -51 $ | -0.012 |
| preneur | 120–180 s | SELL | 2 | 1664 $ | -311 $ | -0.187 |
| preneur | 180–240 s | BUY | 5 | 262 $ | +84 $ | +0.319 |
| preneur | 180–240 s | SELL | 3 | 1016 $ | -112 $ | -0.111 |

## 4. Risque d'achat à 0,95–0,99 en fin de cycle (M9) — toutes les exécutions de tous les portefeuilles

Achats MAKER à ces prix dans les 30 dernières secondes (aucun frais maker ; ristourne non comptée, de l'ordre de 0,02 c par part à ces prix).

| Prix | Remplissages | Parts | Marchés | Remplissages perdants | Taux de victoire nécessaire (seuil) | Taux observé | Résultat | par part | Plus grosse perte d'un remplissage |
|---|---|---|---|---|---|---|---|---|---|
| 0,95–0,97 | 159 | 4709 | 13 | 0 | ≈ 96 % | 100.00 % | +200 $ | +4.24 c | 0 $ |
| 0,97–0,98 | 134 | 4208 | 17 | 0 | ≈ 97,5 % | 100.00 % | +126 $ | +3.00 c | 0 $ |
| 0,98–0,99 | 239 | 7432 | 21 | 0 | ≈ 98,5 % | 100.00 % | +149 $ | +2.00 c | 0 $ |
| ≥ 0,99 | 3722 | 246126 | 209 | 0 | ≈ 99,3 % | 100.00 % | +1632 $ | +0.66 c | 0 $ |

Lecture : à 0,98, une seule part perdue coûte 0,98 $ et efface 49 parts gagnées. Une politique plafonnée à 0,95 se lit sur la 1re ligne.

## 5. Intégrité des données

- Marchés lus : 300 ; incomplets (≥ 10 000 exécutions) : 88 (exclus des résultats). Plafond de l'API Data : décalage ≤ 10 000.
- Événements blockchain (OrderFilled) : le sous-graphe public Goldsky a répondu « trop de requêtes » (429) depuis GitHub ; reconstruction par la blockchain NON faite à ce stade.
- Maker / preneur : déduit de l'API Data (liste « preneur seulement »), non vérifié contre les événements blockchain.
- Fusions, séparations, règlements, récompenses : lus dans l'activité des portefeuilles étudiés seulement (« non lu » sinon). Une vente sans achat visible signale des jetons venus d'une séparation.
- Ristournes maker : comptées seulement si l'activité les montre. Frais preneur : calculés (0,07·p·(1−p)).
