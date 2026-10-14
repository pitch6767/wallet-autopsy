# Bot95 — H1080 : un sous-jacent qui mène le BTC ? (Pitch, 14.10.2026 05:00)

Aucune modification du bot ni des fantômes. Exploration.

## 1. 30 jours, 1 seconde (Binance spot BTC, ETH, SOL ; 12.09 → 11.10)

Pouvoir de prévision du mouvement de BTC (part de variance expliquée sur le tiers final, modèle appris sur les deux premiers tiers) :

| Horizon | BTC seul (son passé) | + ETH et SOL (de t−10 à t−1 s, sans la dernière seconde) |
|---|---|---|
| 3 s | 1,89 % | 2,11 % |
| 10 s | 1,14 % | 1,46 % |
| 30 s | 0,39 % | 0,65 % |

ETH ou SOL qui sautent (> 4 σ en 3 s) alors que BTC ne bouge pas : BTC suit dans le même sens à 10 s dans 64 % / 56 % des cas (ETH, exploration /
contrôle) et 53 % / 57 % (SOL) ; ampleur faible (≈ 0,4 à 2 points de base, soit 3 à 16 $).

## 2. À la milliseconde, Dublin (111 cycles du 12.10 avec toutes les places)

Corrélation des variations par pas de 100 ms avec le BTC Bybit (notre déclencheur) — « en avance » = la série bouge 100 ms AVANT Bybit :

| Série | Simultané | En avance de 100 ms | En retard de 100 ms |
|---|---|---|---|
| **ETH Bybit (perp)** | 0,39 | **0,19** | 0,11 |
| **SOL Bybit (perp)** | 0,22 | **0,12** | 0,07 |
| BTC Binance perp | 0,52 | 0,16 | 0,24 |
| BTC OKX swap | 0,40 | 0,11 | 0,29 |
| BTC Binance spot | 0,28 | 0,07 | 0,28 |
| ETH Binance spot | 0,27 | 0,10 | 0,23 |
| BTC Coinbase | ≈ 0,08 | 0,02 | 0,06 |

**Les perps ETH et SOL de Bybit bougent un peu AVANT le BTC de Bybit** (environ 100 à 200 ms) ; toutes les places BTC, elles, suivent Bybit.

## 3. Test Polymarket

Saut d'ETH Bybit (≥ 0,03 % en 300 ms) sans que BTC n'ait suivi : seulement 7 cas dans les données disponibles (ETH enregistré depuis le 12.10
14:05) — BTC suit dans 86 % des cas (+14,5 $ en 2 s), ROI +27 %. Beaucoup trop peu. Règle figée (`eth_en_avance_h1080.py`) pour être jugée sur
les jours à partir du 14.10, quand ~300 cas seront réunis. Pas de fantôme (consigne : on ne touche à rien).
