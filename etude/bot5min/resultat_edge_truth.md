# EDGE TRUTH — V2-F « écart qui grandit » (BTC), rejeu sur les vrais carnets (07.10 08:03 → 09.10 08:12)

448 trades, 107 gagnés, +6'096 $ · « jackpot » = trade qui rapporte au moins +200 $ (34 trades). 50 $ par trade, frais compris.

## 1. Les probabilités corrigées (apprises seulement sur le passé)

Chaque trade est jugé avec ce qu'on savait au moment de l'achat (trades déjà réglés). On attend 120 trades réglés avant de décider : les **328 trades « nouveaux »** vont du 07.10 21:08 au 09.10 08:11.

| Probabilité | Annonce en moyenne | Gagne en vrai | Brier (plus bas = mieux) | AUC (gagnants vs perdants, 0,5 = hasard) |
|---|---|---|---|---|
| modèle du bot (V2-F) | 41.6 % | 22.0 % | 0.1994 | 0.654 |
| prix Polymarket payé | 19.2 % | 22.0 % | 0.1602 | 0.667 |
| B1 groupes origine × prix | 21.2 % | 22.0 % | 0.1595 | 0.660 |
| B2 régression (prix, modèle, temps, distance, volatilité, origine, côté) | 24.3 % | 22.0 % | 0.1649 | 0.640 |

### Calibration de B2 par tranche

| B2 annonce | Trades | Annonce moyenne | Gagne en vrai | Prix moyen payé | Résultat |
|---|---|---|---|---|---|
| 0.00–0.15 | 64 | 11 % | 9 % | 0.09 | −356 $ |
| 0.15–0.25 | 124 | 20 % | 17 % | 0.17 | +616 $ |
| 0.25–0.35 | 94 | 29 % | 34 % | 0.23 | +2'017 $ |
| 0.35–1.00 | 46 | 43 % | 28 % | 0.33 | −671 $ |

## 2. Les décisions comparées sur les trades nouveaux

| Décision | Trades | Gagnés | Résultat | Par $ engagé | Creux max | Pertes de suite max | Jackpots gardés | 1re moitié | 2e moitié |
|---|---|---|---|---|---|---|---|---|---|
| 1. V2-F original (tout acheter) | 328 | 72 | **+1'606 $** | +10 % | −2'568 $ | 25 | 23 / 23 | +319 $ | +1'286 $ |
| 2a. probabilité corrigée B1 (groupes) : acheter si espérance > 0 | 186 | 44 | **+1'481 $** | +16 % | −1'388 $ | 15 | 10 / 23 | +1'388 $ | +93 $ |
| 2b. probabilité corrigée B2 (régression) : acheter si espérance > 0 | 261 | 56 | **+1'671 $** | +13 % | −2'250 $ | 23 | 18 / 23 | +926 $ | +744 $ |
| 2c. B2, espérance > 2 cents par jeton | 230 | 47 | **+1'158 $** | +10 % | −1'956 $ | 18 | 16 / 23 | +707 $ | +451 $ |
| 3. B2 + mise 25 $ quand l'avantage estimé < 25 % par dollar | 261 | 56 | **+1'247 $** | +12 % | −1'940 $ | 23 | 18 / 23 | +819 $ | +428 $ |

Ce que B2 retire : 67 trades, 16 gagnés, −65 $ ; jackpots retirés 5. Par origine : les deux baissent, Poly plus 54, Poly baisse, modele stable 10, autre 1, le modele monte, Poly stable 1, modele monte ET Poly baisse 1.

## 3. Les 88 trades « les deux baissent, Polymarket plus fort »

Tous : 14 gagnés, −1'482 $. Parmi eux, **64 sont des trades nouveaux** (jugés sans voir leur résultat) : 11 gagnés, −944 $.

### 3.1 Sur les trades nouveaux (strictement sans regarder l'avenir)

| Classement par | Trades | Gagnés | Avantage moyen | Résultat |
|---|---|---|---|---|
| avantage corrigé B2 — tiers haut | 21 | 2 | +0.006 | −588 $ |
| avantage corrigé B2 — tiers milieu | 21 | 2 | -0.045 | −519 $ |
| avantage corrigé B2 — tiers bas | 22 | 7 | -0.079 | +163 $ |
| avantage annoncé par le modèle — tiers haut | 21 | 3 | +0.254 | −325 $ |
| avantage annoncé par le modèle — tiers milieu | 21 | 6 | +0.218 | +151 $ |
| avantage annoncé par le modèle — tiers bas | 22 | 2 | +0.204 | −770 $ |

AUC sur ces trades (0,5 = hasard) : B2 0.67 · modèle du bot 0.71 · prix 0.71

B2 en garde 10 (espérance > 0) : 1 gagnés, −282 $ ; il en écarte 54 : 10 gagnés, −662 $.

### 3.2 Sur les 88 (validation par 5 blocs de temps : chaque bloc jugé par un modèle appris sur les 4 autres — utilise aussi des données postérieures, donc moins strict)

| Classement par | Trades | Gagnés | Avantage moyen | Résultat |
|---|---|---|---|---|
| avantage corrigé — tiers haut | 29 | 1 | +0.015 | −1'300 $ |
| avantage corrigé — tiers milieu | 29 | 3 | -0.020 | −671 $ |
| avantage corrigé — tiers bas | 30 | 10 | -0.061 | +488 $ |

AUC : modèle corrigé 0.63 · modèle du bot 0.72 · prix 0.69

Sur les 448 trades (même validation par blocs) : AUC modèle corrigé 0.64 · modèle du bot 0.66 · prix 0.67

## 4. Moins d'incertitude fixe dans le modèle : rejeu complet de la règle V2-F avec chaque version

Chaque version du modèle refait tout le rejeu : certaines opportunités disparaissent, d'autres apparaissent (cycles différents ou autre moment).

| Version du modèle | Trades | Gagnés | Annonce moyenne | Gagne en vrai | Prix moyen | Résultat | Creux max | Pertes de suite max | Jackpots (≥ +200 $) | Cycles en commun avec l'actuel |
|---|---|---|---|---|---|---|---|---|---|---|
| modèle enregistré du bot (0,08 %, celui de V2-F) | 448 | 107 | 42 % | 24 % | 0.19 | **+6'096 $** | −2'568 $ | 25 | 34 | 448 |
| reconstruit 0,08 % (contrôle) | 431 | 102 | 42 % | 24 % | 0.19 | **+6'040 $** | −2'474 $ | 25 | 41 | 428 |
| 0,02 % | 309 | 112 | 50 % | 36 % | 0.26 | **+7'520 $** | −786 $ | 10 | 19 | 304 |
| ↳ dont cycles aussi pris par l'actuel / cycles nouveaux | 304 / 5 | 107 / 5 | | | | +7'279 $ / +240 $ | | | | |
| 0,01 % | 303 | 119 | 51 % | 39 % | 0.27 | **+8'820 $** | −512 $ | 8 | 20 | 297 |
| ↳ dont cycles aussi pris par l'actuel / cycles nouveaux | 297 / 6 | 113 / 6 | | | | +8'537 $ / +283 $ | | | | |

Par quart de la période (mêmes dates pour toutes les versions) et par jour :

| Version | Q1 | Q2 | Q3 | Q4 | Par jour |
|---|---|---|---|---|---|
| modèle enregistré du bot (0,08 %, celui de V2-F) | +2'861 $ | +999 $ | +779 $ | +1'456 $ | 07.10 +4'459 $ · 08.10 +177 $ · 09.10 +1'460 $ |
| reconstruit 0,08 % (contrôle) | +3'245 $ | +527 $ | +500 $ | +1'768 $ | 07.10 +4'049 $ · 08.10 +558 $ · 09.10 +1'434 $ |
| 0,02 % | +3'417 $ | +861 $ | +1'950 $ | +1'291 $ | 07.10 +3'491 $ · 08.10 +3'342 $ · 09.10 +687 $ |
| 0,01 % | +3'623 $ | +1'193 $ | +2'155 $ | +1'849 $ | 07.10 +3'923 $ · 08.10 +3'774 $ · 09.10 +1'123 $ |
