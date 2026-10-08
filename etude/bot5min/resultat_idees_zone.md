# 7 idees testees sur la zone — BTC, vrais carnets (99 trades zone, 634 desaccords >= 0,10 pour la calibration)

## 1. Les deux juges (modele + prix Polymarket)

Appris sur la 1re moitie : poids du modele **0.68**, poids du prix Polymarket **0.66** (en echelle logit).
Precision sur la 2e moitie (Brier, plus bas = mieux) : modele seul 0.211 · Polymarket seul 0.195 · **melange 0.195**

| Regle | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Par trade |
|---|---|---|---|---|---|---|
| zone (reference) | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| zone + juge : proba melangee >= prix + 0 c | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| zone + juge : proba melangee >= prix + 3 c | 97 | 30 | +1312 $ | +1545 $ | **+2857 $** | +29.5 $ |
| zone + juge : proba melangee >= prix + 5 c | 53 | 21 | +1121 $ | +1258 $ | **+2379 $** | +44.9 $ |
| zone + juge : proba melangee >= prix + 10 c | 4 | 4 | +156 $ | +585 $ | **+740 $** | +185.0 $ |

## 2. Calibration du modele selon le temps restant (desaccords >= 0,10)

| Temps restant | Desaccords | Modele moyen | Prix Polymarket moyen | **Gagnes en vrai** |
|---|---|---|---|---|
| 10-60 s | 18 | 0.41 | 0.20 | **0.17** |
| 60-120 s | 66 | 0.38 | 0.23 | **0.20** |
| 120-200 s | 131 | 0.39 | 0.26 | **0.30** |
| 200-300 s | 419 | 0.45 | 0.31 | **0.31** |

| Modele dit | Desaccords | **Gagnes en vrai** | Prix Polymarket moyen |
|---|---|---|---|
| 0.10-0.30 | 69 | **0.13** | 0.11 |
| 0.30-0.45 | 280 | **0.23** | 0.25 |
| 0.45-0.60 | 261 | **0.36** | 0.36 |
| 0.60-0.80 | 23 | **0.65** | 0.49 |
| 0.80-1.00 | 1 | **0.00** | 0.72 |

## 5. Horloge elastique : mouvements divises par la volatilite de la derniere minute

| Regle | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Par trade |
|---|---|---|---|---|---|---|
| zone (reference) | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| Binance et perp >= 0 (brut) | 55 | 20 | +1773 $ | +952 $ | **+2725 $** | +49.5 $ |
| Binance et perp >= -0.5 ecart-type (elastique) | 66 | 22 | +1666 $ | +902 $ | **+2568 $** | +38.9 $ |
| Binance et perp >= -1.0 ecart-type (elastique) | 68 | 22 | +1613 $ | +849 $ | **+2462 $** | +36.2 $ |
| Binance et perp >= +0,5 ecart-type (vraiment avec nous) | 28 | 14 | +1121 $ | +1204 $ | **+2325 $** | +83.0 $ |

## 6. Execution reelle : et si l'ordre arrive 0,25 / 0,5 / 1 s plus tard ?

Ordre a cours limite = prix vu + 1 c. Rempli seulement si le vendeur est encore la a ce prix.

| Delai | Remplis | Non remplis | Resultat des remplis | Par trade | Gain perdu vs instantane |
|---|---|---|---|---|---|
| instantane (reference) | 99 | 0 | +3002 $ | +30.3 $ | — |
| 0,25 s | 84 | 15 (dont 7 gagnants) | +2023 $ | +24.1 $ | -979 $ |
| 0,5 s | 71 | 28 (dont 13 gagnants) | +1226 $ | +17.3 $ | -1776 $ |
| 1 s | 69 | 30 (dont 15 gagnants) | +916 $ | +13.3 $ | -2086 $ |

Taille : le meilleur vendeur avait moins que les parts voulues (50 $) dans **42 / 99** cas ; ces trades font +550 $.

## 7. D'ou vient le desaccord (3 s avant l'achat) ?

| Regle | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Par trade |
|---|---|---|---|---|---|---|
| le modele monte | 26 | 14 | +1441 $ | +1080 $ | **+2520 $** | +96.9 $ |
| Polymarket baisse | 49 | 11 | -61 $ | +220 $ | **+159 $** | +3.2 $ |
| les deux | 5 | 3 | +188 $ | +402 $ | **+590 $** | +118.0 $ |
| deja la (rien n'a bouge en 3 s) | 17 | 3 | -59 $ | -103 $ | **-162 $** | -9.5 $ |
| autre | 2 | 0 | -53 $ | -53 $ | **-106 $** | -53.0 $ |

## 8. Tendance du BTC (perp) avant l'achat — dans le sens du trade ou contre

| Regle | Trades | Gagnes | 1re moitie | 2e moitie | **Total** | Par trade |
|---|---|---|---|---|---|---|
| tendance 15 min DANS notre sens | 34 | 11 | +877 $ | +249 $ | **+1126 $** | +33.1 $ |
| tendance 15 min CONTRE nous | 50 | 15 | +481 $ | +762 $ | **+1244 $** | +24.9 $ |
| tendance 60 min DANS notre sens | 46 | 17 | +1044 $ | +852 $ | **+1895 $** | +41.2 $ |
| tendance 60 min CONTRE nous | 44 | 12 | +397 $ | +558 $ | **+955 $** | +21.7 $ |
| cote Up (pour comparer) | 44 | 18 | +1380 $ | +1136 $ | **+2516 $** | +57.2 $ |
| cote Down (pour comparer) | 55 | 13 | +76 $ | +409 $ | **+486 $** | +8.8 $ |

## 9. Chaque filtre : pertes evitees contre gagnants perdus

| Filtre | Trades ecartes | Perdants ecartes | Gagnants ecartes | Pertes evitees | Gains perdus | **Net du filtre** | Net 1re moitie | Net 2e moitie |
|---|---|---|---|---|---|---|---|---|
| Binance et perp >= 0 | 44 | 33 | 11 | +1746 $ | +2023 $ | **-277 $** | +317 $ | -593 $ |
| perp >= 0 | 38 | 28 | 10 | +1481 $ | +1813 $ | **-331 $** | +368 $ | -699 $ |
| juge >= prix | 0 | 0 | 0 | +0 $ | +0 $ | **+0 $** | +0 $ | +0 $ |
| juge >= prix + 5 c | 46 | 36 | 10 | +1908 $ | +2530 $ | **-622 $** | -335 $ | -287 $ |
| pas « Polymarket baisse » | 49 | 38 | 11 | +2011 $ | +2170 $ | **-159 $** | +61 $ | -220 $ |
| pas « modele monte » | 26 | 12 | 14 | +636 $ | +3156 $ | **-2520 $** | -1441 $ | -1080 $ |
| tendance 15 min >= 0 | 50 | 35 | 15 | +1852 $ | +3096 $ | **-1244 $** | -481 $ | -762 $ |
| tendance 60 min >= 0 | 44 | 32 | 12 | +1694 $ | +2650 $ | **-955 $** | -397 $ | -558 $ |
| elastique Binance et perp >= -0,5 | 33 | 24 | 9 | +1270 $ | +1704 $ | **-434 $** | +209 $ | -643 $ |