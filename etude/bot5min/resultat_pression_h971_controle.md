# Bot95 — H971 / H972 : pression contre capacité, effondrement de liquidité (CONTRÔLE : apprentissage et validation)

Généré le 12.10.2026 12:39 UTC. Cycles Dublin : apprentissage 169, validation 85 (test inédit = à partir du 12.10 06:00 UTC). Aucun ordre ; bots, H816, H821, R4, fantômes inchangés ; période réservée non lue.

## 1. H972 — Effondrement de capacité

Mouvement BTC Binance après l'événement, en $, signé dans le sens prévu (positif = juste). IC 90 % par cycles.

| Échantillon | Type | Événements | 1 s | 3 s | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|---|---|---|---|
| apprentissage | effondrement | 17 | +1.4 [+0.4 ; +2.8] | +4.2 [+1.4 ; +7.7] | +5.1 [+1.9 ; +9.3] | +4.8 [+1.2 ; +9.6] | +9.9 [+2.1 ; +20.0] | +14.3 [+6.0 ; +23.3] |
| apprentissage | témoin | 428 | +1.6 [+1.1 ; +2.1] | +3.0 [+2.0 ; +4.2] | +3.8 [+2.5 ; +5.4] | +4.3 [+2.9 ; +6.0] | +5.1 [+3.2 ; +7.0] | +4.1 [+1.6 ; +6.8] |
| validation | effondrement | 13 | +1.6 [+0.4 ; +3.1] | +1.9 [+0.4 ; +4.0] | +1.8 [+0.3 ; +3.9] | -0.4 [-5.8 ; +4.4] | -6.9 [-17.2 ; +2.1] | -15.3 [-35.2 ; +0.8] |
| validation | témoin | 304 | +2.3 [+1.6 ; +3.1] | +3.5 [+2.8 ; +4.3] | +4.5 [+3.6 ; +5.4] | +5.6 [+4.4 ; +6.9] | +7.6 [+5.2 ; +9.9] | +6.1 [+2.9 ; +9.1] |

**Réévaluation Polymarket** (milieu du jeton prévu, en centimes, signé) et **règlement officiel** (résultat − M0, signé)

| Échantillon | Type | Polymarket 1 s | Polymarket 3 s | Polymarket 5 s | Polymarket 10 s | Polymarket 30 s | Règlement |
|---|---|---|---|---|---|---|---|
| apprentissage | effondrement | +1.67 [+0.64 ; +2.58] | +2.08 [-0.21 ; +4.77] | +2.79 [-0.07 ; +6.18] | +2.05 [-1.62 ; +6.41] | +10.73 [+1.00 ; +23.05] | +0.01 [-0.19 ; +0.22] (n=15) |
| apprentissage | témoin | +2.12 [+1.58 ; +2.74] | +3.00 [+2.25 ; +3.86] | +3.15 [+2.29 ; +4.08] | +2.37 [+1.35 ; +3.34] | +2.41 [+0.74 ; +4.03] | +0.10 [+0.07 ; +0.13] (n=315) |
| validation | effondrement | +1.73 [+0.32 ; +3.55] | +0.41 [-1.91 ; +2.91] | -0.32 [-2.73 ; +2.18] | -1.55 [-7.59 ; +4.13] | -5.49 [-12.86 ; +1.61] | -0.12 [-0.30 ; +0.03] (n=11) |
| validation | témoin | +2.34 [+1.45 ; +3.30] | +2.65 [+1.73 ; +3.62] | +2.59 [+1.58 ; +3.68] | +2.38 [+1.10 ; +3.77] | +0.88 [-1.18 ; +2.86] | +0.03 [-0.01 ; +0.07] (n=244) |

**Occasion exécutable** : achat 20 $ du jeton prévu à 164 ms au prix vu (frais compris), (a) revente 30 s après au meilleur acheteur, (b) conservation.

| Échantillon | Type | Achats | (a) P&L total, revente à 30 s | IC 90 % (total) | (b) P&L total, règlement | IC 90 % (total) |
|---|---|---|---|---|---|---|
| apprentissage | effondrement | 10 | +26 | [-5 ; +68] | -4 | [-83 ; +83] |
| apprentissage | témoin | 255 | -117 | [-266 ; +46] | +56 | [-409 ; +584] |
| validation | effondrement | 4 | -8 | [-14 ; -2] | -31 | [-80 ; +10] |
| validation | témoin | 194 | -56 | [-277 ; +218] | +314 | [-666 ; +1952] |

## 2. H971 — La pression rapportée à la capacité prévoit-elle mieux qu'OFI + momentum + volatilité ?

20851 instants (toutes les 3 s). IC corrigé : 10 comparaisons.

| Cible | Échantillon | Taux de base | AUC simple (OFI, momentum, volatilité) | AUC simple + pression/capacité | ΔAUC | IC 90 % | IC corrigé |
|---|---|---|---|---|---|---|---|
| hausse BTC à 10 s | validation | 38 % | 0.668 | 0.673 | +0.005 | [+0.001 ; +0.009] | [-0.001 ; +0.011] |
| hausse BTC à 30 s | validation | 46 % | 0.618 | 0.615 | -0.003 | [-0.009 ; +0.003] | [-0.012 ; +0.008] |
| grand mouvement à 30 s vers le haut | validation | 13 % | 0.618 | 0.629 | +0.011 | [-0.001 ; +0.025] | [-0.006 ; +0.030] |
| grand mouvement à 30 s vers le bas | validation | 13 % | 0.649 | 0.641 | -0.008 | [-0.016 ; +0.000] | [-0.019 ; +0.006] |
| milieu Polymarket Up +1 c à 10 s | validation | 45 % | 0.537 | 0.535 | -0.002 | [-0.007 ; +0.002] | [-0.008 ; +0.004] |

## 3. Règlement officiel : modèle A (règlement seul, recalibré) contre A + pression/capacité

| Échantillon | Sous-ensemble | Décisions | Brier A | Brier A + PC | Log loss A / A + PC | Précision A / A + PC | ΔBrier (A − A+PC) | IC 90 % | IC corrigé (6) |
|---|---|---|---|---|---|---|---|---|---|
| validation | toutes | 492 | 0.1150 | 0.1262 | 0.364 / 0.394 | 85 % / 83 % | -0.01117 | [-0.01997 ; -0.00291] | [-0.02373 ; +0.00039] |
| validation | proches de 50 % | 83 | 0.2456 | 0.2643 | 0.684 / 0.749 | 52 % / 54 % | -0.01876 | [-0.04489 ; +0.00674] | [-0.05992 ; +0.01551] |
| validation | marge faible | 102 | 0.2390 | 0.2517 | 0.671 / 0.717 | 57 % / 59 % | -0.01276 | [-0.03695 ; +0.00885] | [-0.05103 ; +0.01773] |

## Limites
- Carnet Binance limité à 50 $ du meilleur prix ; Bybit et OKX sans carnet profond enregistré ; liquidations agrégées seulement.
- Quelques dizaines d'heures de données ; test inédit d'environ 6 h.
- Le milieu Polymarket est reconstruit (photos 10 s + changements à ±3 c).

_Calcul : 147 s._
