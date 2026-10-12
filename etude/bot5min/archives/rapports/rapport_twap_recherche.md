# Bot95 — TWAP fin : toutes les idées de ChatGPT testées

Rapport du 10.10.2026 à 01:00 · BTC · 692 cycles enregistrés (07.10 08:05 → 09.10 22:35) · règlement reconstruit exactement (prix à battre = moyenne Chainlink des 60 s avant le début, fin = moyenne des 60 dernières secondes ; 680 gagnants justes sur 681) · **apprentissage sur les 415 premiers cycles, test sur les 277 suivants, jamais vus** · achats simulés au meilleur vendeur, limités à la quantité affichée, frais compris · aucun changement dans le bot.

## En bref

- **Aucune idée ne bat nettement le moteur actuel pour prévoir le gagnant.** Toutes les versions sérieuses ont la même qualité de prévision (Brier 0,0423-0,0436). Les « jumeaux » et le modèle avec flux d'ordres sont **moins bons** (sur-apprentissage).
- **En résultat de trading, quatre versions font un peu mieux que le moteur sur les cycles de test** : sauts (loi de Student) +617 $, distribution empirique des erreurs +660 $, nowcast 4 bourses +632 $, correction apprise +732 $, contre +438 $ pour le moteur actuel. Mais il n'y a que 29 à 42 achats : un seul gros gain pèse 100 à 200 $. **Ces écarts sont dans le bruit — rien n'est démontré.**
- **Deux vraies informations :**
  1. Le moteur **surestime légèrement l'incertitude** de la moyenne finale (erreur réelle = 0,90 de ce qu'il prévoit) et les mouvements des 15-30 dernières secondes ont une **petite tendance à revenir** (corrélation −0,09). C'est ce que les versions « sauts » et « empirique » corrigent, d'où leur léger mieux.
  2. **L'écart entre Binance spot et le perp Bybit prédit l'erreur de la moyenne finale** (corrélation +0,23 ; Coinbase +0,14) : Chainlink suit un peu plus le spot que le perp. C'est la meilleure piste de « nowcast » trouvée. Utiliser le spot seul ne suffit pas ; l'écart doit entrer comme correction (c'est ce que fait la version « correction apprise »).
- **Flux d'ordres, liquidations, profondeur du carnet, Deribit, ETH : pas d'effet utile mesurable** sur la moyenne finale (corrélations entre −0,04 et +0,03). Les découpages donnent des chiffres variés sur de petits groupes, sans logique stable.
- **Le moteur actuel reste la référence.** Rien ne justifie de le changer aujourd'hui.

## Chaque idée commentée

- **2 et 9 — vitesse de la probabilité / prévoir ses révisions :** les achats où la probabilité « monte vite » font moins bien par dollar (+28 %) que ceux où elle est stable (+76 %), et les 3 achats où elle baissait ont perdu. Tendance cohérente mais petits groupes. À suivre.
- **3 — fiabilité de la reconstruction :** au moment des achats, le dernier prix Chainlink avait toujours moins de 2 s ; la reconstruction du prix à battre est juste à 0,19 $ près. Pas de problème de données.
- **4 et 20 — forme de la trajectoire / persistance :** pente dans notre sens +970 $ contre +302 $ ; mais en réalité, les mouvements récents ont une légère tendance à **revenir** (voir idée 5). Pas de règle à en tirer.
- **5 — sens de l'erreur :** pas de biais moyen (−0,02 écart-type) ; légère tendance au retour après un mouvement ; le moteur est un peu trop prudent (0,90).
- **6 — ETH :** aucune information utile (corrélation −0,01).
- **7 — valeur de l'attente :** pas testé ici (il faut d'abord les vrais trades TWAP fin) ; pour le corrigé, attendre 1 s perdait.
- **8 — jumeaux historiques :** le plus mauvais prédicteur (Brier 0,0475) ; beaucoup de trades et résultat négatif sur la 2e moitié. **Rejeté** avec 2,5 jours de données.
- **10 — stabilité :** les achats juste après un changement de favori ont gagné 65 % du temps (+803 $ sur 31 achats) — intéressant mais à confirmer.
- **11 — mouvement nécessaire pour inverser :** presque tous les achats sont près du seuil (|z| < 0,5 : 78 achats, +1 170 $). Normal : c'est là que le carnet et le moteur divergent.
- **12 — décomposition de la confiance :** inutile tant que ses composantes (9, 10, 14, 26) ne montrent rien de solide.
- **13, 14, 16 — trajectoires et sauts :** la version « loi de Student » (queues plus épaisses) est légèrement meilleure en prévision et en résultat. **Meilleur candidat** avec la distribution empirique.
- **15 — moment des sauts :** déjà dans la formule du moteur.
- **17 — volatilité à plusieurs horizons :** quand les 30 dernières secondes sont plus agitées que les 5 minutes, les achats gagnent plus (60 %, mais 10 achats seulement).
- **18 et 22 — volatilité pondérée et dérive :** déjà la formule du moteur.
- **19, 23, 24, 25 — flux d'ordres, liquidations, profondeur :** ces données étaient déjà enregistrées (1 fois par seconde) ; **aucun effet utile** sur la moyenne finale. Ajoutés au modèle, ils le rendent moins bon (sur-apprentissage).
- **21 — asymétrie Up/Down :** Down +913 $ contre Up +360 $ ; pas de raison de fond, probablement le hasard de la période.
- **26 — correction apprise des erreurs (modèle B) :** prévision équivalente, résultat un peu meilleur (+732 $, les deux moitiés positives). **Candidat.**
- **27 — prévoir Chainlink avec les bourses (modèle C) :** médiane des 4 bourses +632 $ ; le signal utile est l'écart spot-perp (+0,23).

## Ce que je propose (tu décides)

1. **Ne rien changer à TWAP fin** : c'est la référence, il tourne depuis 23h45.
2. **Ajouter deux fantômes TWAP fin à côté**, pour les comparer sur des journées nouvelles : « TWAP fin sauts » (loi de Student) et « TWAP fin correction spot-perp » (le moteur corrigé de l'écart Binance/Coinbase − perp, appris sur le passé).
3. **Refaire tous ces tests chaque semaine** avec les nouvelles données : avec 2,5 jours, aucune de ces différences n'est démontrable.

---PAGE---

Apprentissage sur les 415 premiers cycles (jusqu'au 08.10 20:30), **test sur les 277 cycles suivants, jamais vus**. Une mesure par seconde entre 90 et 20 s de la fin (19215 mesures de test).

## 1. Qualité de prévision du gagnant officiel (test)

| Probabilité | Brier (plus bas = mieux) | Log-loss |
|---|---|---|
| moteur actuel (perp) | 0.0424 | 0.1405 |
| C : nowcast 4 bourses | 0.0424 | 0.1404 |
| C2 : prix spot (Binance + Coinbase) au lieu du perp | 0.0429 | 0.1420 |
| C3 : Binance spot seul | 0.0435 | 0.1426 |
| sauts (loi de Student) | 0.0423 | 0.1393 |
| distribution empirique des erreurs | 0.0423 | 0.1402 |
| jumeaux (60 plus proches cas passés) | 0.0475 | 0.1767 |
| B : correction apprise | 0.0436 | 0.1424 |
| B + flux d'ordres, liquidations, profondeur, Deribit, ETH | 0.0474 | 0.1558 |
| *(carnet Polymarket, sur les 7480 mesures où il existe ; moteur sur les mêmes : 0.1050)* | 0.1065 | |

## 2. Règle TWAP fin (probabilité − prix ≥ 0,20, 90-20 s, un achat par cycle, quantité affichée) — cycles de test

| Probabilité utilisée | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| moteur actuel (perp) | 41 | 44 % | 28 $ | **+438 $** | +38 % | −323 $ | 6 | 6 | +417 $ / +22 $ |
| C : nowcast 4 bourses | 29 | 38 % | 30 $ | **+632 $** | +73 % | −245 $ | 5 | 4 | +408 $ / +224 $ |
| C2 : prix spot (Binance + Coinbase) au lieu du perp | 42 | 38 % | 31 $ | **+543 $** | +41 % | −228 $ | 6 | 7 | +443 $ / +99 $ |
| C3 : Binance spot seul | 41 | 32 % | 30 $ | **+192 $** | +16 % | −371 $ | 13 | 4 | +407 $ / −215 $ |
| sauts (loi de Student) | 40 | 52 % | 29 $ | **+617 $** | +54 % | −242 $ | 4 | 5 | +477 $ / +139 $ |
| distribution empirique des erreurs | 42 | 57 % | 27 $ | **+660 $** | +58 % | −222 $ | 4 | 3 | +562 $ / +98 $ |
| jumeaux (60 plus proches cas passés) | 109 | 38 % | 40 $ | **+1'369 $** | +31 % | −511 $ | 7 | 11 | +1'571 $ / −203 $ |
| B : correction apprise | 41 | 49 % | 32 $ | **+732 $** | +56 % | −214 $ | 6 | 6 | +479 $ / +253 $ |
| B + flux d'ordres, liquidations, profondeur, Deribit, ETH | 56 | 46 % | 37 $ | **+758 $** | +37 % | −310 $ | 6 | 7 | +869 $ / −110 $ |

## 3. Les trades du moteur actuel (tous les cycles), découpés selon les idées de ChatGPT


### Idée 2/9 — vitesse : variation de la probabilité sur 3 s, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| monte vite (≥ +5 pts) | 63 | 43 % | 19 $ | **+339 $** | +28 % | −212 $ | 7 | 3 | +50 $ / +289 $ |
| stable (−5 à +5) | 43 | 37 % | 32 $ | **+1'033 $** | +76 % | −178 $ | 7 | 10 | +528 $ / +505 $ |
| baisse (≤ −5 pts) | 3 | 0 % | 31 $ | **−100 $** | -107 % | −100 $ | 3 | 0 | −53 $ / −46 $ |

### Idée 10 — stabilité de la probabilité sur 10 s

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| stable (écart-type < 0,03) | 31 | 35 % | 29 $ | **+433 $** | +49 % | −232 $ | 5 | 5 | −87 $ / +520 $ |
| agitée (≥ 0,03) | 78 | 41 % | 22 $ | **+840 $** | +48 % | −288 $ | 5 | 8 | +488 $ / +351 $ |
| a changé de favori sur 10 s | 31 | 65 % | 25 $ | **+803 $** | +103 % | −124 $ | 3 | 4 | +388 $ / +415 $ |

### Idée 11 — mouvement nécessaire pour inverser (distance en écarts-types)

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| |z| < 0,5 | 78 | 38 % | 26 $ | **+1'170 $** | +59 % | −254 $ | 6 | 12 | +248 $ / +921 $ |
| 0,5-1 | 24 | 29 % | 15 $ | **+7 $** | +2 % | −224 $ | 7 | 1 | +227 $ / −220 $ |
| 1-2 | 5 | 80 % | 37 $ | **+62 $** | +34 % | −51 $ | 1 | 0 | +82 $ / −20 $ |
| ≥ 2 | 2 | 100 % | 45 $ | **+33 $** | +37 % | +0 $ | 0 | 0 | +21 $ / +13 $ |

### Idée 4/20 — forme de la trajectoire sur 30 s (pente dans notre sens)

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| pente dans notre sens | 77 | 39 % | 24 $ | **+970 $** | +52 % | −239 $ | 7 | 10 | +512 $ / +458 $ |
| pente contre nous | 32 | 41 % | 24 $ | **+302 $** | +39 % | −256 $ | 7 | 3 | +104 $ / +198 $ |
| accélère dans notre sens | 72 | 40 % | 24 $ | **+816 $** | +47 % | −240 $ | 7 | 9 | +583 $ / +233 $ |
| ralentit / s'inverse | 37 | 38 % | 25 $ | **+456 $** | +50 % | −162 $ | 6 | 4 | +137 $ / +320 $ |

### Idée 17 — volatilité 30 s / volatilité 5 min

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| plus calme qu'avant (< 0,8) | 56 | 39 % | 21 $ | **+450 $** | +38 % | −218 $ | 6 | 6 | +183 $ / +266 $ |
| pareil (0,8-1,25) | 43 | 35 % | 27 $ | **+429 $** | +37 % | −150 $ | 5 | 4 | +174 $ / +255 $ |
| plus agitée (≥ 1,25) | 10 | 60 % | 28 $ | **+393 $** | +139 % | −69 $ | 3 | 3 | +117 $ / +277 $ |

### Idée 21 — côté acheté

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| Up | 47 | 40 % | 26 $ | **+360 $** | +29 % | −293 $ | 7 | 4 | +132 $ / +228 $ |
| Down | 62 | 39 % | 23 $ | **+913 $** | +64 % | −230 $ | 7 | 9 | +269 $ / +644 $ |

### Idée 27 — avance des bourses : Coinbase par rapport au perp, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| Coinbase dans notre sens | 13 | 38 % | 36 $ | **+27 $** | +6 % | −109 $ | 3 | 1 | +30 $ / −3 $ |
| neutre | 9 | 44 % | 32 $ | **+289 $** | +101 % | −113 $ | 3 | 3 | +195 $ / +94 $ |
| Coinbase contre nous | 87 | 39 % | 22 $ | **+957 $** | +51 % | −170 $ | 7 | 9 | +353 $ / +604 $ |

### Idée 3 — fraîcheur du dernier prix Chainlink reçu

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| < 2 s | 109 | 39 % | 24 $ | **+1'272 $** | +48 % | −323 $ | 6 | 13 | +401 $ / +871 $ |
| 2-5 s | 0 | | | | | | |
| ≥ 5 s | 0 | | | | | | |

### Écart annoncé

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| 20-30 pts | 89 | 36 % | 26 $ | **+1'150 $** | +50 % | −268 $ | 6 | 13 | +382 $ / +768 $ |
| 30-50 pts | 17 | 53 % | 18 $ | **+82 $** | +27 % | −60 $ | 2 | 0 | +36 $ / +46 $ |
| ≥ 50 pts | 3 | 67 % | 15 $ | **+40 $** | +88 % | −16 $ | 1 | 0 | +51 $ / −11 $ |

### Idées 19/23/24 — flux d'ordres agressifs Bybit sur 15 s, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| acheteurs dans notre sens (> 0,5 M$) | 16 | 56 % | 19 $ | **+550 $** | +184 % | −51 $ | 2 | 2 | +459 $ / +91 $ |
| neutre | 88 | 36 % | 26 $ | **+651 $** | +28 % | −370 $ | 6 | 11 | −113 $ / +764 $ |
| contre nous (< −0,5 M$) | 5 | 40 % | 10 $ | **+71 $** | +148 % | −7 $ | 2 | 0 | +17 $ / +54 $ |

### Idée 24 — déséquilibre du carnet Bybit à 3 points de base, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| carnet dans notre sens (> +0,2) | 40 | 35 % | 26 $ | **+37 $** | +4 % | −213 $ | 5 | 2 | +42 $ / −5 $ |
| équilibré | 42 | 36 % | 26 $ | **+887 $** | +81 % | −219 $ | 7 | 8 | +127 $ / +760 $ |
| contre nous (< −0,2) | 27 | 52 % | 19 $ | **+348 $** | +68 % | −101 $ | 2 | 3 | +284 $ / +65 $ |

### Idée 19 — liquidations sur 15 s, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| liquidations qui poussent dans notre sens | 0 | | | | | | |
| aucune / faibles | 109 | 39 % | 24 $ | **+1'272 $** | +48 % | −323 $ | 6 | 13 | +401 $ / +871 $ |
| contre nous | 0 | | | | | | |

### Idée 6 — ETH sur 15 s, dans notre sens

| Groupe | Achats | Gagnés | Mise remplie | Résultat | Par $ | Creux | Pertes de suite max | Gains ≥ +100 $ | 1re / 2e moitié du test |
|---|---|---|---|---|---|---|---|---|---|
| ETH monte dans notre sens (> 1 pb) | 41 | 37 % | 23 $ | **+115 $** | +12 % | −195 $ | 5 | 3 | −105 $ / +219 $ |
| ETH neutre | 30 | 50 % | 28 $ | **+653 $** | +78 % | −129 $ | 4 | 6 | +388 $ / +265 $ |
| ETH contre nous | 8 | 12 % | 28 $ | **+39 $** | +17 % | −133 $ | 6 | 1 | +79 $ / −40 $ |
| pas de donnée ETH | 30 | 40 % | 21 $ | **+466 $** | +74 % | −97 $ | 5 | 3 | +268 $ / +198 $ |

## 4. Idée 5 — l'erreur de la moyenne finale prévue a-t-elle un sens ?

Erreur standardisée (officiel − prévu, en écarts-types du moteur) : moyenne -0.023, écart-type 0.90 (1,00 = moteur bien calibré).
Corrélation avec le mouvement 15 s : -0.092 ; 30 s : -0.099 (positif = le mouvement continue, négatif = il revient).

Ce qui prédit l'erreur de la moyenne finale (corrélation, sur toutes les mesures) :

- flux d'ordres 5 s : -0.031 (47534 mesures)
- flux d'ordres 15 s : -0.038 (47534 mesures)
- liquidations 15 s : -0.004 (47534 mesures)
- déséquilibre carnet Bybit : +0.034 (47534 mesures)
- écart Deribit − Bybit : -0.022 (47534 mesures)
- écart Coinbase − perp : +0.142 (47534 mesures)
- écart Binance − perp : +0.226 (47534 mesures)
- mouvement 15 s : -0.092 (47534 mesures)
- ETH 15 s : -0.014 (34861 mesures)
- âge du dernier Chainlink : +0.008 (47534 mesures)