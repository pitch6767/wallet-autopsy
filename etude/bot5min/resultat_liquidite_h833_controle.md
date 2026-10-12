# Bot95 — H833 à H835 : absorption, retrait de liquidité, autres actifs (CONTRÔLE, apprentissage seul)

Généré le 12.10.2026 10:56 UTC. Cycles Dublin : 255 (11.10 08:45 → 12.10 06:05 UTC) ; apprentissage 127 cycles (avant 11.10 19:25 UTC), test 128. Résultat officiel connu pour 255 cycles. Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 1. Couverture et qualité des données L2 (Dublin)

| Donnée | Secondes couvertes |
|---|---|
| Prix Binance spot | 97.3 % |
| Prix Bybit perp | 97.2 % |
| Prix OKX swap | 97.3 % |
| Prix Coinbase | 97.3 % |
| Chainlink | 97.3 % |
| Carnet Binance (meilleurs prix, cumuls) | 83.3 % |
| Carnet Bybit | 83.3 % |
| Photos 10 niveaux Binance (murs) | 81.7 % |

Secondes enregistrées : 76500 (21.2 h). Trous signalés par l'enregistreur : bn silence : 311, by silence : 25.

Limites : profondeur au-delà de 50 $ et au-delà de 10 niveaux non enregistrée ; liquidations Bybit agrégées seulement ; Deribit à partir du 12.10.

## 2. H833 — Absorption de liquidité

Variation BTC (Binance spot) après l'événement, signée dans le sens prévu (positif = la prévision était juste), en $. IC 90 % par cycles.

| Échantillon | Type | Sens du flux | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 60 s | 30 s en σ5 |
|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | absorption | achats | 10 | +0.0 [+0.0 ; +0.0] | +1.2 [+0.0 ; +3.5] | +1.2 [+0.0 ; +3.5] | -2.8 [-5.6 ; +0.0] | -16.3 [-46.1 ; +1.0] | -22.4 [-45.1 ; -4.2] | -4.31 |
| apprentissage | absorption | ventes | 18 | +0.0 [+0.0 ; +0.0] | +0.0 [+0.0 ; +0.0] | +0.0 [+0.0 ; +0.0] | +0.6 [-1.5 ; +2.9] | +1.5 [-7.0 ; +12.7] | -1.0 [-12.5 ; +12.6] | +0.40 |
| apprentissage | flux suivi | achats | 81 | +3.4 [+1.6 ; +5.5] | +6.1 [+2.2 ; +11.0] | +8.3 [+3.2 ; +14.9] | +8.7 [+3.2 ; +15.3] | +11.6 [+4.2 ; +20.2] | +11.5 [+4.0 ; +19.8] | +15.85 |
| apprentissage | flux suivi | ventes | 71 | +2.1 [+0.9 ; +3.3] | +2.3 [+1.1 ; +3.7] | +3.1 [+1.1 ; +5.2] | +4.4 [+2.1 ; +6.8] | +4.3 [-2.2 ; +9.4] | +8.0 [-1.5 ; +16.3] | +1.03 |

**Effet sur le règlement officiel** (événements avec 30 à 240 s restantes) : résultat − probabilité M0 au même instant, signé dans le sens prévu.

| Échantillon | Type | Événements | Écart moyen | IC 90 % par cycles |
|---|---|---|---|---|
| apprentissage | absorption | 12 | -0.177 | [-0.362 ; +0.003] |
| apprentissage | flux suivi | 101 | +0.140 | [+0.086 ; +0.200] |

## 3. H834 — Retrait de liquidité : annonce-t-il le mouvement ?

20935 instants (toutes les 3 s). Contrôles = variations passées 1/5/30 s et volatilité ; liquidité = OFI, retraits, profondeur, déséquilibres, microprix, écart, murs.

| Cible | Taux de base test | AUC contrôles seuls | AUC contrôles + liquidité | Écart (IC 90 % par cycles) |
|---|---|---|---|---|
_Contrôle : AUC non calculées (test non lu)._


## 4. H835 — Autres actifs et autres places

**(a) ETH et SOL contre BTC, Binance 1 s, 30 jours.** Corrélation simultanée ; avance = corrélation du rendement passé de l'actif sur k s avec le rendement futur de BTC sur k s ; R² hors échantillon (test 02.10 → 11.10) d'une régression BTC futur ~ BTC passé + actif passé, contre BTC passé seul.

| Actif | k | Corrélation simultanée | Avance (actif passé → BTC futur) | R² test BTC seul | R² test + actif | Gain de R² |
|---|---|---|---|---|---|---|
| ETH | 1 s | +0.678 | — | — | — | — |
| ETH | 2 s | +0.725 | — | — | — | — |
| ETH | 5 s | +0.777 | — | — | — | — |
| ETH | 10 s | +0.807 | — | — | — | — |
| ETH | 30 s | +0.840 | — | — | — | — |
| SOL | 1 s | +0.545 | — | — | — | — |
| SOL | 2 s | +0.614 | — | — | — | — |
| SOL | 5 s | +0.692 | — | — | — | — |
| SOL | 10 s | +0.735 | — | — | — | — |
| SOL | 30 s | +0.778 | — | — | — | — |

**(b) Places BTC à Dublin (50 ms, heures de réception)** : corrélation du rendement passé de la place sur Δ avec le rendement futur de Binance spot sur Δ, test.

| Place | Δ = 100 ms | 250 ms | 500 ms | 1 000 ms |
|---|---|---|---|---|
| perp | +0.314 | +0.303 | +0.290 | +0.300 |
| okx | +0.293 | +0.284 | +0.250 | +0.260 |
| cb | +0.033 | +0.062 | +0.071 | +0.116 |
| cl | +0.043 | +0.067 | +0.106 | +0.124 |

Nasdaq, or, devises, CME : non disponibles à la seconde (déclarés, non estimés). Deribit : enregistré depuis le 12.10, pour plus tard.

## 5. Modèles A / B / C / D sur les mêmes décisions

Décisions : apprentissage 466, test 738 (123 cycles).

_Contrôle : arrêt avant le test._
