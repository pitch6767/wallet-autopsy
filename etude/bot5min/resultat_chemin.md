# Temps utile, forme du chemin, passage de cycle — BTC, vrais carnets (06.10 18:30 -> 08.10 18:45)

93 trades « zone + Binance et perp + sortie -10 » (plancher 0,05 $).

## Chaque variable en trois tiers

| Regle | Trades | Perdants | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux | Rendement / $ |
|---|---|---|---|---|---|---|---|---|---|---|
| REFERENCE | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| temps utile (distance / volatilite, + = on gagne deja) — tiers bas (< -0.30) | 31 | 16 | +1082 | +443 | +764 | +233 | **+2522 $** | +1681 $ | -159 $ | +163 % |
| temps utile (distance / volatilite, + = on gagne deja) — tiers milieu | 31 | 19 | +617 | +564 | -180 | +631 | **+1631 $** | +832 $ | -432 $ | +105 % |
| temps utile (distance / volatilite, + = on gagne deja) — tiers haut (>= -0.09) | 31 | 25 | -225 | +316 | +3 | -136 | **-41 $** | -640 $ | -348 $ | -3 % |
| traversees du seuil (60 s) — tiers milieu | 58 | 35 | +1316 | +747 | +287 | +498 | **+2849 $** | +2029 $ | -316 $ | +98 % |
| traversees du seuil (60 s) — tiers haut (>= 1.00) | 35 | 25 | +158 | +576 | +300 | +229 | **+1263 $** | +443 $ | -190 $ | +72 % |
| part du temps de notre cote (60 s) — tiers milieu | 62 | 38 | +1657 | +765 | +462 | +379 | **+3263 $** | +2423 $ | -297 $ | +105 % |
| part du temps de notre cote (60 s) — tiers haut (>= 0.56) | 31 | 22 | -182 | +557 | +124 | +348 | **+848 $** | +49 $ | -305 $ | +55 % |
| acceleration Chainlink dans notre sens (10 s vs 10 s avant) — tiers bas (< -1.59) | 31 | 18 | +168 | +940 | +311 | +542 | **+1961 $** | +1141 $ | -231 $ | +126 % |
| acceleration Chainlink dans notre sens (10 s vs 10 s avant) — tiers milieu | 31 | 20 | +624 | +267 | +569 | -106 | **+1354 $** | +534 $ | -268 $ | +87 % |
| acceleration Chainlink dans notre sens (10 s vs 10 s avant) — tiers haut (>= 3.98) | 31 | 22 | +683 | +115 | -293 | +291 | **+796 $** | +36 $ | -468 $ | +51 % |
| mouvement Chainlink 10 s dans notre sens — tiers bas (< -0.91) | 31 | 20 | -38 | +664 | +130 | +743 | **+1499 $** | +679 $ | -312 $ | +97 % |
| mouvement Chainlink 10 s dans notre sens — tiers milieu | 31 | 20 | +602 | +447 | +296 | -100 | **+1245 $** | +446 $ | -234 $ | +80 % |
| mouvement Chainlink 10 s dans notre sens — tiers haut (>= 3.70) | 31 | 20 | +911 | +211 | +161 | +84 | **+1367 $** | +587 $ | -228 $ | +88 % |
| cycle precedent gagne dans NOTRE sens | 38 | 22 | +664 | +932 | +381 | +693 | **+2669 $** | +1828 $ | -211 $ | +140 % |
| cycle precedent gagne dans l'autre sens | 55 | 38 | +811 | +391 | +206 | +35 | **+1443 $** | +643 $ | -446 $ | +52 % |

## Filtres et mises 25/50 testes (garde : total >= 95 % de la reference, ou rendement / $ nettement meilleur)

| Regle | Trades | Perdants | Q1 | Q2 | Q3 | Q4 | **Total** | Sans top 3 | Creux | Rendement / $ |
|---|---|---|---|---|---|---|---|---|---|---|
| REFERENCE | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| sans le tiers haut de « temps utile (distance / volatilite, + = on gagne deja) » | 62 | 35 | +1699 | +1007 | +584 | +863 | **+4153 $** | +3312 $ | -226 $ | +134 % |
| 25 $ sur le tiers haut de « temps utile (distance / volatilite, + = on gagne deja) », 50 $ sinon | 93 | 60 | +1587 | +1166 | +585 | +795 | **+4133 $** | +3292 $ | -313 $ | +107 % |
| sans le tiers bas de « traversees du seuil (60 s) » | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| 25 $ sur le tiers bas de « traversees du seuil (60 s) », 50 $ sinon | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| sans le tiers bas de « part du temps de notre cote (60 s) » | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| 25 $ sur le tiers bas de « part du temps de notre cote (60 s) », 50 $ sinon | 93 | 60 | +1474 | +1323 | +587 | +728 | **+4111 $** | +3270 $ | -455 $ | +88 % |
| 25 $ sur « cycle precedent dans l'autre sens », 50 $ sinon | 93 | 60 | +1069 | +1129 | +484 | +710 | **+3392 $** | +2551 $ | -316 $ | +104 % |
| sans le tiers haut de « acceleration Chainlink dans notre sens (10 s vs 10 s avant) » | 62 | 38 | +791 | +1207 | +880 | +436 | **+3315 $** | +2474 $ | -379 $ | +107 % |
| sans le tiers haut de « part du temps de notre cote (60 s) » | 62 | 38 | +1657 | +765 | +462 | +379 | **+3263 $** | +2423 $ | -297 $ | +105 % |
| sans « cycle precedent dans l'autre sens » | 38 | 22 | +664 | +932 | +381 | +693 | **+2669 $** | +1828 $ | -211 $ | +140 % |