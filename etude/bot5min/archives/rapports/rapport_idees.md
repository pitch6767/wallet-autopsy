# Bot95 — 7 idées testées sur la zone désaccord 30

Analyse du 08.10.2026 · vrais carnets enregistrés par le bot sur les 48 dernières heures (4 mesures par seconde) · BTC · 99 trades dans la zone (écart ≥ 30 pts, jeton 0,15-0,35 $, > 60 s) · 50 $ par trade, frais compris · « 1re / 2e moitié » = les deux moitiés de la période, pour vérifier que le résultat ne tient pas au hasard d'un seul moment.

## En bref

- **Découverte n°1 — l'origine du désaccord.** Le désaccord créé par le modèle qui monte (le BTC a bougé, Polymarket pas encore) rapporte +97 $ par trade sur 26 trades, positif sur les deux moitiés. Le désaccord créé par Polymarket qui baisse rapporte zéro.
- **Découverte n°2 — la vitesse.** Acheter 0,25 s plus tard coûte un tiers du gain ; 0,5 s plus tard, 60 %. En argent réel, la latence décide de tout.
- **Découverte n°3 — notre modèle est trop optimiste** d'environ 10-15 points, surtout en fin de cycle. Le prix Polymarket est bien calibré. C'est pour ça qu'il faut un écart de 30 pts.
- **N'aident pas :** les deux juges, l'horloge élastique, le filtre de tendance seul. Le filtre Binance et perp ne gagne plus sur les toutes dernières heures.
> **Proposition :** un nouveau fantôme « zone + le modèle a monté d'au moins 3 pts sur les 3 dernières secondes ». Et avant toute mise en réel : mesurer le délai réel de nos ordres sur Polymarket.
---PAGE---
## 5. D'où vient le désaccord ?


| Règle | Trades | Gagnés | 1re moitié | 2e moitié | **Total** | Par trade |
|---|---|---|---|---|---|---|
| le modèle monte | 26 | 14 | +1441 $ | +1080 $ | **+2520 $** | +96.9 $ |
| Polymarket baisse | 49 | 11 | -61 $ | +220 $ | **+159 $** | +3.2 $ |
| les deux | 5 | 3 | +188 $ | +402 $ | **+590 $** | +118.0 $ |
| déjà là (rien n'a bouge en 3 s) | 17 | 3 | -59 $ | -103 $ | **-162 $** | -9.5 $ |
| autre | 2 | 0 | -53 $ | -53 $ | **-106 $** | -53.0 $ |

> **Verdict : la vraie découverte du jour.** Quand le désaccord vient du **modèle qui monte** (le BTC a bougé, le modèle le voit), c'est +97 $ par trade, positif sur les deux moitiés (+1 441 / +1 080). Quand il vient de **Polymarket qui baisse** (un vendeur casse son prix), c'est zéro : le vendeur sait souvent quelque chose. Quand l'écart était déjà là sans que rien ne bouge, c'est négatif. C'est exactement l'idée de ChatGPT : un vrai désaccord vient d'une information nouvelle que Polymarket n'a pas encore intégrée.

## 4. Exécution réelle : acheter 0,25 / 0,5 / 1 s plus tard


Ordre a cours limite = prix vu + 1 c. Rempli seulement si le vendeur est encore la a ce prix.

| Delai | Remplis | Non remplis | Resultat des remplis | Par trade | Gain perdu vs instantané |
|---|---|---|---|---|---|
| instantané (référence) | 99 | 0 | +3002 $ | +30.3 $ | — |
| 0,25 s | 84 | 15 (dont 7 gagnants) | +2023 $ | +24.1 $ | -979 $ |
| 0,5 s | 71 | 28 (dont 13 gagnants) | +1226 $ | +17.3 $ | -1776 $ |
| 1 s | 69 | 30 (dont 15 gagnants) | +916 $ | +13.3 $ | -2086 $ |

Taille : le meilleur vendeur avait moins que les parts voulues (50 $) dans **42 / 99** cas ; ces trades font +550 $.

> **Verdict : c'est le point le plus important pour l'argent réel.** Si l'ordre arrive 0,25 s trop tard, un tiers du gain disparaît. Avec 0,5 s de retard, 60 % disparaît. Les bons désaccords se referment très vite : en réel, il faut un bot qui envoie l'ordre en moins de 0,25 s, sinon la zone ne rapporte presque plus rien.

## 2. Le modèle est-il juste ?


| Temps restant | Désaccords | Modèle moyen | Prix Polymarket moyen | **Gagnés en vrai** |
|---|---|---|---|---|
| 10-60 s | 18 | 0.41 | 0.20 | **0.17** |
| 60-120 s | 66 | 0.38 | 0.23 | **0.20** |
| 120-200 s | 131 | 0.39 | 0.26 | **0.30** |
| 200-300 s | 419 | 0.45 | 0.31 | **0.31** |

| Modèle dit | Désaccords | **Gagnés en vrai** | Prix Polymarket moyen |
|---|---|---|---|
| 0.10-0.30 | 69 | **0.13** | 0.11 |
| 0.30-0.45 | 280 | **0.23** | 0.25 |
| 0.45-0.60 | 261 | **0.36** | 0.36 |
| 0.60-0.80 | 23 | **0.65** | 0.49 |
| 0.80-1.00 | 1 | **0.00** | 0.72 |

> **Verdict : notre modèle est trop optimiste.** Quand il dit 0,30-0,45, le côté ne gagne que 23 % du temps, et le prix Polymarket (0,25) est juste. Avec moins de 2 minutes restantes, le modèle donne environ 0,40 pour 17-20 % de victoires réelles : c'est là qu'il se trompe le plus. C'est pour ça que les désaccords de 10-20 pts sont souvent faux et que l'écart de 30 pts (la zone) marche mieux : il faut une grosse marge pour couvrir l'optimisme du modèle.

## 1. Deux juges : modèle + prix Polymarket


Appris sur la 1re moitié : poids du modèle **0.68**, poids du prix Polymarket **0.66** (en echelle logit).
Précision sur la 2e moitié (Brier, plus bas = mieux) : modèle seul 0.211 · Polymarket seul 0.195 · **mélange 0.195**

| Règle | Trades | Gagnés | 1re moitié | 2e moitié | **Total** | Par trade |
|---|---|---|---|---|---|---|
| zone (référence) | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| zone + juge : proba mélangee >= prix + 0 c | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| zone + juge : proba mélangee >= prix + 3 c | 97 | 30 | +1312 $ | +1545 $ | **+2857 $** | +29.5 $ |
| zone + juge : proba mélangee >= prix + 5 c | 53 | 21 | +1121 $ | +1258 $ | **+2379 $** | +44.9 $ |
| zone + juge : proba mélangee >= prix + 10 c | 4 | 4 | +156 $ | +585 $ | **+740 $** | +185.0 $ |

> **Verdict : n'aide pas.** Le prix Polymarket seul prédit déjà aussi bien que le mélange (Brier 0,195). Le juge ne retire presque rien à +0 ou +3 c, et à +5 c il retire autant de gagnants que de perdants.

## 3. Horloge élastique (mouvements divisés par la volatilité)


| Règle | Trades | Gagnés | 1re moitié | 2e moitié | **Total** | Par trade |
|---|---|---|---|---|---|---|
| zone (référence) | 99 | 31 | +1456 $ | +1545 $ | **+3002 $** | +30.3 $ |
| Binance et perp >= 0 (brut) | 55 | 20 | +1773 $ | +952 $ | **+2725 $** | +49.5 $ |
| Binance et perp >= -0.5 écart-type (élastique) | 66 | 22 | +1666 $ | +902 $ | **+2568 $** | +38.9 $ |
| Binance et perp >= -1.0 écart-type (élastique) | 68 | 22 | +1613 $ | +849 $ | **+2462 $** | +36.2 $ |
| Binance et perp >= +0,5 écart-type (vraiment avec nous) | 28 | 14 | +1121 $ | +1204 $ | **+2325 $** | +83.0 $ |

> **Verdict : n'aide pas.** Diviser les mouvements par la volatilité ne fait pas mieux que le filtre brut. Exiger que Binance et le perp soient franchement avec nous (+0,5 écart-type) donne +83 $ par trade, mais sur 28 trades seulement.

## 6. Tendance du BTC avant l'achat


| Règle | Trades | Gagnés | 1re moitié | 2e moitié | **Total** | Par trade |
|---|---|---|---|---|---|---|
| tendance 15 min DANS notre sens | 34 | 11 | +877 $ | +249 $ | **+1126 $** | +33.1 $ |
| tendance 15 min CONTRE nous | 50 | 15 | +481 $ | +762 $ | **+1244 $** | +24.9 $ |
| tendance 60 min DANS notre sens | 46 | 17 | +1044 $ | +852 $ | **+1895 $** | +41.2 $ |
| tendance 60 min CONTRE nous | 44 | 12 | +397 $ | +558 $ | **+955 $** | +21.7 $ |
| côté Up (pour comparer) | 44 | 18 | +1380 $ | +1136 $ | **+2516 $** | +57.2 $ |
| côté Down (pour comparer) | 55 | 13 | +76 $ | +409 $ | **+486 $** | +8.8 $ |

> **Verdict : prudence.** Acheter dans le sens de la tendance de la dernière heure aide un peu (+41 $ contre +22 $ par trade), sur les deux moitiés. Mais le côté Up fait +57 $ et le côté Down +9 $ : ces 48 h étaient haussières, une partie de l'effet vient de là.

## 7. Chaque filtre : pertes évitées contre gagnants perdus


| Filtre | Trades écartes | Perdants écartes | Gagnants écartes | Pertes évitées | Gains perdus | **Net du filtre** | Net 1re moitié | Net 2e moitié |
|---|---|---|---|---|---|---|---|---|
| Binance et perp >= 0 | 44 | 33 | 11 | +1746 $ | +2023 $ | **-277 $** | +317 $ | -593 $ |
| perp >= 0 | 38 | 28 | 10 | +1481 $ | +1813 $ | **-331 $** | +368 $ | -699 $ |
| juge >= prix | 0 | 0 | 0 | +0 $ | +0 $ | **+0 $** | +0 $ | +0 $ |
| juge >= prix + 5 c | 46 | 36 | 10 | +1908 $ | +2530 $ | **-622 $** | -335 $ | -287 $ |
| pas « Polymarket baisse » | 49 | 38 | 11 | +2011 $ | +2170 $ | **-159 $** | +61 $ | -220 $ |
| pas « modèle monte » | 26 | 12 | 14 | +636 $ | +3156 $ | **-2520 $** | -1441 $ | -1080 $ |
| tendance 15 min >= 0 | 50 | 35 | 15 | +1852 $ | +3096 $ | **-1244 $** | -481 $ | -762 $ |
| tendance 60 min >= 0 | 44 | 32 | 12 | +1694 $ | +2650 $ | **-955 $** | -397 $ | -558 $ |
| élastique Binance et perp >= -0,5 | 33 | 24 | 9 | +1270 $ | +1704 $ | **-434 $** | +209 $ | -643 $ |

> **Verdict : avec les toutes dernières données, aucun filtre ne rapporte plus qu'il ne coûte**, même le filtre Binance et perp, qui était positif ce matin et qui est maintenant légèrement négatif sur la 2e moitié. Garder seulement les désaccords où le modèle a monté ferait au contraire +2 520 $ avec 26 trades. C'est la seule piste nette.
