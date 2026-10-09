# Sensibilité de la marge d'incertitude du modèle — V2-F BTC, rejeu complet sur les vrais carnets

Pour chaque marge, toute la règle V2-F est rejouée. « Rempli au carnet » = 50 $ au meilleur vendeur mais au plus la quantité affichée à ce prix (pas de remontée dans le carnet) : c'est l'hypothèse prudente.

| Marge | Trades | Gagnés | % gagnés | Prix moyen | Résultat (50 $ toujours remplis) | Résultat rempli au carnet | Mise moyenne remplie | Creux (rempli au carnet) | Pertes de suite max | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bot enregistré 0,08 % (V2-F) | 448 | 107 | 24 % | 0.19 | +6'096 $ | **+1'497 $** | 31 $ | −1'973 $ | 25 | +661 $ | +123 $ | −278 $ | +991 $ |
| reconstruit 0,08 % | 431 | 102 | 24 % | 0.19 | +6'040 $ | **+554 $** | 28 $ | −2'009 $ | 25 | +271 $ | −423 $ | −360 $ | +1'066 $ |
| 0,04 % | 348 | 104 | 30 % | 0.21 | +8'139 $ | **+1'603 $** | 25 $ | −779 $ | 11 | +725 $ | +716 $ | +198 $ | −37 $ |
| 0,03 % | 330 | 113 | 34 % | 0.24 | +8'244 $ | **+1'578 $** | 27 $ | −731 $ | 10 | +766 $ | +407 $ | +157 $ | +248 $ |
| 0,02 % | 309 | 112 | 36 % | 0.26 | +7'520 $ | **+1'375 $** | 27 $ | −687 $ | 10 | +830 $ | +409 $ | +341 $ | −205 $ |
| 0,015 % (fantôme « corrigé » en direct) | 306 | 115 | 38 % | 0.26 | +8'282 $ | **+2'350 $** | 26 $ | −580 $ | 8 | +1'261 $ | +407 $ | +417 $ | +265 $ |
| 0,0125 % | 301 | 116 | 39 % | 0.27 | +8'617 $ | **+2'131 $** | 26 $ | −580 $ | 8 | +1'316 $ | +169 $ | +407 $ | +239 $ |
| 0,01 % | 303 | 119 | 39 % | 0.27 | +8'820 $ | **+2'300 $** | 26 $ | −580 $ | 8 | +1'400 $ | +276 $ | +407 $ | +217 $ |
| 0,0075 % | 301 | 120 | 40 % | 0.27 | +8'988 $ | **+2'489 $** | 26 $ | −653 $ | 8 | +1'476 $ | +368 $ | +498 $ | +147 $ |
| 0,005 % | 299 | 120 | 40 % | 0.28 | +8'815 $ | **+2'319 $** | 26 $ | −627 $ | 8 | +1'518 $ | +146 $ | +483 $ | +173 $ |
| 0 % (aucune marge) | 298 | 120 | 40 % | 0.28 | +8'426 $ | **+2'236 $** | 26 $ | −603 $ | 8 | +1'534 $ | +61 $ | +479 $ | +161 $ |

## Mêmes cycles : d'où vient le gain ?

Comparaison avec le moteur reconstruit à 0,08 % (même moteur de rejeu, seule la marge change). Résultats remplis au carnet.

| Marge | Cycles communs | Résultat 0,08 % sur ces cycles | Résultat nouvelle marge sur ces cycles | Cycles abandonnés (que 0,08 % prenait) | Leur résultat à 0,08 % | Cycles nouveaux | Leur résultat |
|---|---|---|---|---|---|---|---|
| 0,02 % | 301 | +3'365 $ | +1'313 $ | 130 | −2'811 $ | 8 | +62 $ |
| ↳ sur les cycles communs | | prix moyen 0.21 | prix moyen 0.25 | achat en moyenne +12 s plus tard (médiane +0 s) | | | |
| 0,015 % (fantôme « corrigé » en direct) | 298 | +3'407 $ | +2'239 $ | 133 | −2'853 $ | 8 | +110 $ |
| ↳ sur les cycles communs | | prix moyen 0.21 | prix moyen 0.26 | achat en moyenne +10 s plus tard (médiane +0 s) | | | |
| 0,01 % | 294 | +3'581 $ | +2'188 $ | 137 | −3'026 $ | 9 | +112 $ |
| ↳ sur les cycles communs | | prix moyen 0.21 | prix moyen 0.27 | achat en moyenne +8 s plus tard (médiane +0 s) | | | |