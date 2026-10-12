# Bot95 — H986 à H993 (première priorité) : flux forcé contre flux volontaire, cascades de liquidations, base perp/spot

Généré le 12.10.2026 14:12 UTC. Cycles Dublin : apprentissage 169, validation 85, test 71, nouveau 25. Aucun ordre ; période réservée non lue.

## 0. Audit des données Dublin pour cette série

| Donnée | Enregistrée ? | Depuis | Remarque |
|---|---|---|---|
| Liquidations Bybit BTCUSDT (agrégées, ~500 ms) | oui | 11.10 | 406 secondes avec liquidation ; 3.7 M$ de ventes forcées, 5.8 M$ d'achats forcés |
| Transactions agressives Binance spot / Bybit perp | oui | 11.10 | |
| Carnets Binance / Bybit (50 $) | oui | 11.10 | |
| Mark price, index price, open interest, funding Bybit (ticker 100 ms) | **non** | — | à enregistrer (gratuit) pour H988/H989 |
| Mark price, liquidations, transactions Binance perp | **non** | — | à enregistrer (gratuit) |
| Open interest Binance | 5 min seulement (archive) | 12.09 | trop grossier pour 5–120 s |
| Deribit : indice, perpétuel (avec OI), DVOL, transactions d'options, OI par prix d'exercice | indice/perp/DVOL depuis 12.10 11:55 ; OI par strike et transactions d'options depuis le déploiement de 14:03 UTC | — | trop récent |
| Coinbase L2, ETH / SOL | depuis le déploiement de 14:03 UTC | — | trop récent |
| IBIT (OPRA), CME, ETF | **non** | — | payant (non acheté) |


## 1. H993 — Flux contraint (liquidations du même sens) contre flux volontaire, appariés

Écart de continuation BTC (contraint − moyenne des volontaires appariés), en $, signé dans le sens de la vague ; et effet sur le règlement officiel.

| Échantillon | Vagues contraintes appariées | 5 s | 15 s | 30 s | 60 s | 120 s | Règlement : contraint − volontaire (résultat − M0) |
|---|---|---|---|---|---|---|---|
| apprentissage | 6 | -12.84 [-20.66 ; -4.58] (n=6) | -1.54 [-12.83 ; +12.70] (n=6) | +39.77 [+9.47 ; +77.55] (n=6) | +37.51 [+3.58 ; +83.44] (n=6) | +53.25 [+21.28 ; +76.86] (n=6) | — (n=4) |
| validation | 1 | — (n=1) | — (n=1) | — (n=1) | — (n=1) | — (n=1) | — (n=1) |
| test | 3 | — (n=3) | — (n=3) | — (n=3) | — (n=3) | — (n=3) | — (n=0) |
| nouveau | 1 | — (n=1) | — (n=1) | — (n=1) | — (n=1) | — (n=1) | — (n=0) |

Continuation brute (non appariée), même définition :

| Échantillon | Type | Vagues | 30 s | 120 s | Résultat − M0 |
|---|---|---|---|---|---|
| apprentissage | contrainte | 13 | +21.50 [+5.44 ; +38.34] (n=13) | +46.54 [+9.97 ; +73.61] (n=13) | +0.05 [+0.01 ; +0.09] (n=10) |
| apprentissage | volontaire | 534 | +5.14 [+3.54 ; +6.71] (n=534) | +5.79 [+2.36 ; +9.32] (n=534) | +0.08 [+0.05 ; +0.11] (n=381) |
| validation | contrainte | 1 | — (n=1) | — (n=1) | — (n=1) |
| validation | volontaire | 368 | +7.08 [+4.93 ; +9.19] (n=368) | +5.18 [+0.81 ; +9.24] (n=368) | +0.03 [-0.01 ; +0.08] (n=296) |
| test | contrainte | 4 | — (n=4) | — (n=4) | — (n=1) |
| test | volontaire | 387 | +4.45 [+2.82 ; +6.11] (n=387) | +6.09 [+1.13 ; +11.07] (n=387) | +0.05 [+0.02 ; +0.10] (n=192) |
| nouveau | contrainte | 7 | +38.83 [-15.50 ; +90.81] (n=7) | +76.68 [+47.60 ; +105.91] (n=7) | — (n=3) |
| nouveau | volontaire | 128 | +7.16 [+1.76 ; +12.40] (n=128) | +2.24 [-8.84 ; +14.00] (n=128) | +0.02 [-0.01 ; +0.08] (n=17) |

**H992 — Achat de 20 $ du jeton dans le sens de la vague contrainte, à 164 ms au prix vu, conservé (frais compris)**

| Échantillon | Achats | Victoire | Prix payé moyen | Avantage par achat (résultat − prix − frais) | P&L ($) | IC 90 % |
|---|---|---|---|---|---|---|
| apprentissage | 9 | 100 % | 0.90 | +0.10 [+0.06 ; +0.14] (n=9) | +21 | [+10 ; +32] |
| validation | 0 | — | — | — | — | — |
| test | 0 | — | — | — | — | — |
| nouveau | 2 | 100 % | 0.92 | — (n=2) | +4 | [+nan ; +nan] |

## 2. H990 — Une salve de liquidations en déclenche-t-elle une autre ?

36 salves (≥ 50 000 $ du même côté en 5 s). Témoins : instants sans salve, |variation du prix sur 5 s| à ± 30 % de celle de la salve, même échantillon.

| Échantillon | Salves | Nouvelle salve du même côté dans 1 / 3 / 5 / 10 / 30 s | Témoins : même probabilité | Prix à 5 / 30 / 60 s (sens de la vente ou de l'achat forcé) |
|---|---|---|---|---|
| apprentissage | 16 | 25 % / 31 % / 31 % / 31 % / 50 % | 0 % / 9 % / 9 % / 9 % / 9 % | +4.43 [-4.75 ; +12.60] (n=16) / +9.11 [-9.90 ; +38.30] (n=16) / +1.37 [-21.86 ; +36.51] (n=16) |
| validation | 4 | 0 % / 0 % / 50 % / 50 % / 50 % | 0 % / 0 % / 0 % / 0 % / 0 % | — (n=4) / — (n=4) / — (n=4) |
| test | 6 | 17 % / 17 % / 17 % / 17 % / 17 % | 0 % / 3 % / 7 % / 7 % / 7 % | -8.16 [-19.97 ; +4.21] (n=6) / -24.37 [-57.77 ; +11.54] (n=6) / -15.68 [-47.22 ; +17.43] (n=6) |
| nouveau | 10 | 10 % / 20 % / 20 % / 20 % / 20 % | 0 % / 0 % / 0 % / 0 % / 8 % | +9.86 [-0.07 ; +17.44] (n=10) / +21.47 [+1.66 ; +36.28] (n=10) / +15.05 [-6.02 ; +32.20] (n=10) |

## 3. H988 (partiel) — Une base perp/spot extrême précède-t-elle les liquidations ?

| Échantillon | Instants (base |z| ≥ 2) | Salve dans les 30 s après | Taux de base (tous instants) |
|---|---|---|---|
| apprentissage | 1005 | 0.9 % | 0.9 % |
| validation | 406 | 1.7 % | 0.5 % |
| test | 327 | 0.9 % | 0.9 % |
| nouveau | 90 | 3.3 % | 4.4 % |

## 4. Non testables aujourd'hui (données absentes)
- **H986** options IBIT (OPRA payant), **H991** IBIT/CME/Deribit, **H987** gamma (OI par strike enregistré seulement depuis 14:03 UTC aujourd'hui).
- **H988 complet / H989** : mark price, index price et open interest Bybit/Binance à haute fréquence non enregistrés.

_Calcul : 84 s._
