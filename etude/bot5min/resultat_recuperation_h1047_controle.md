# Bot95 — Récupération, faux sauvetages, trailing fondamental, protection sélective : H1047–H1050 (CONTRÔLE)

Généré le 12.10.2026 16:34 UTC. Étude séparée (le protocole figé H1003–H1046 n'est pas modifié). Cycles : apprentissage 197, validation 99, test 0. Position : 10 $ sur le favori du marché. Aucun ordre.

Cerveau B (apprentissage, 4150 décisions) : logit p = -0.050 + -0.003 × logit(M0) + 0.943 × logit(milieu).

## 1. H1047 — Récupération contre perte définitive (au premier instant défavorable)

| Échantillon | Détérioration d | Positions | Prix récupéré plus tard | Victoire finale | Perte définitive | Milieu Polymarket moyen | Cerveau B moyen | M0 moyen | Brier milieu | Brier cerveau B | Brier M0 | Cerveau B − milieu (IC 90 %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | 0.10 | 112 | 63 % | 40 % | 60 % | 0.517 | 0.515 | 0.698 | 0.2440 | 0.2435 | 0.3550 | -0.0005 [-0.0025 ; +0.0016] |
| apprentissage | 0.15 | 104 | 56 % | 36 % | 64 % | 0.460 | 0.460 | 0.689 | 0.2325 | 0.2326 | 0.3592 | +0.0001 [-0.0020 ; +0.0022] |
| apprentissage | 0.20 | 96 | 47 % | 30 % | 70 % | 0.389 | 0.393 | 0.655 | 0.2068 | 0.2086 | 0.3585 | +0.0019 [-0.0001 ; +0.0038] |
| apprentissage | 0.30 | 89 | 34 % | 25 % | 75 % | 0.308 | 0.315 | 0.584 | 0.1803 | 0.1827 | 0.3701 | +0.0024 [+0.0006 ; +0.0043] |
| validation | 0.10 | 55 | 76 % | 69 % | 31 % | 0.547 | 0.545 | 0.728 | 0.2298 | 0.2315 | 0.2054 | +0.0017 [-0.0010 ; +0.0043] |
| validation | 0.15 | 49 | 69 % | 65 % | 35 % | 0.497 | 0.498 | 0.703 | 0.2302 | 0.2327 | 0.1969 | +0.0025 [-0.0003 ; +0.0054] |
| validation | 0.20 | 43 | 65 % | 60 % | 40 % | 0.444 | 0.447 | 0.650 | 0.2510 | 0.2525 | 0.2008 | +0.0015 [-0.0019 ; +0.0046] |
| validation | 0.30 | 31 | 48 % | 45 % | 55 % | 0.348 | 0.357 | 0.558 | 0.2296 | 0.2315 | 0.2236 | +0.0020 [-0.0024 ; +0.0061] |

**Par temps restant et perte latente liquidable (d = 0,15, toutes périodes hors apprentissage)** — récupération du prix / victoire finale / milieu moyen (n)

| Temps restant | perte -2 à +0 $ | perte -4 à -2 $ | perte -6 à -4 $ | perte < −6 $ |
|---|---|---|---|---|
| 181–240 s | — | 71 % / 61 % / 0.52 (28) | 100 % / 100 % / 0.42 (4) | — |
| 121–180 s | — | 82 % / 91 % / 0.52 (11) | 0 % / 0 % / 0.35 (1) | 0 % / 0 % / 0.26 (1) |
| 61–120 s | — | 33 % / 33 % / 0.48 (3) | — | 0 % / 0 % / 0.24 (1) |
| 1–60 s | — | — | — | — |

**Modèles (apprentissage) : AUC contre le milieu du marché seul**

| Cible | Échantillon | AUC milieu seul | AUC modèle (cerveau B, milieu, z Chainlink, temps restant, perte latente) |
|---|---|---|---|
| récupération du prix | validation | 0.637 | 0.630 |
| victoire finale | validation | 0.680 | 0.669 |

## 2. H1048 — Coût des faux sauvetages (interventions H1036 contre R0, 164 ms)

### validation (99 cycles)

| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |
|---|---|---|---|---|---|---|---|---|---|
| R1 vente totale | +92 | -190 | 28 / 63 | 0 | +9.9 | -1.5 | +0.00 | -99 | [-172 ; -29] |
| R3 couverture complète | +93 | -194 | 28 / 63 | 0 | +10.0 | -2.2 | +3.15 | -101 | [-173 ; -27] |
| R4 couverture tardive | +41 | -53 | 5 / 63 | 0 | +3.1 | +0.7 | +2.24 | -13 | [-59 ; +30] |
| R5 moitié-moitié | +92 | -192 | 28 / 63 | 0 | +10.0 | -1.9 | +0.33 | -100 | [-173 ; -29] |

## 3. H1049 — Trailing fondamental contre trailing classique et conservation (164 ms)

### validation (99 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (4) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +103 | 63 | -10.0 | -0 | +0 | 15.4 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| C1 | 60 | -47 | 23 | -4.3 | -264 | +114 | 28.8 | 15 | 10 | -150 | [-228 ; -70] | [-256 ; -37] | -133 |
| C2 | 30 | +64 | 66 | -10.0 | -85 | +46 | 20.4 | 6 | 10 | -39 | [-86 ; +14] | [-101 ; +29] | -43 |
| F1 | 24 | +85 | 54 | -9.1 | -74 | +56 | 20.0 | 7 | 10 | -18 | [-69 ; +29] | [-91 ; +46] | -33 |
| F2 | 17 | +101 | 61 | -9.6 | -21 | +19 | 16.8 | 3 | 10 | -2 | [-32 ; +21] | [-42 ; +27] | -7 |

## 4. H1050 — Protection sélective après un gain réellement liquidable (164 ms)

### validation (99 cycles)

| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé (9) | 500 ms : P&L − H0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 0 | +103 | 63 | -10.0 | -0 | +0 | 15.4 | 0 | 10 | +0 | [+nan ; +nan] | [+nan ; +nan] | +0 |
| S-V-2 | 54 | +58 | 63 | -10.0 | -85 | +40 | 20.6 | 6 | 10 | -45 | [-83 ; -5] | [-100 ; +22] | -56 |
| S-A-2 | 48 | +59 | 63 | -10.0 | -85 | +40 | 20.6 | 0 | 13 | -45 | [-82 ; -4] | [-98 ; +23] | -56 |
| S-M-2 | 54 | +58 | 63 | -10.0 | -85 | +40 | 20.6 | 15 | 10 | -45 | [-81 ; -4] | [-98 ; +21] | -56 |
| S-V-5 | 14 | +106 | 63 | -10.0 | -7 | +10 | 15.9 | 1 | 10 | +3 | [-9 ; +23] | [-12 ; +35] | +1 |
| S-A-5 | 10 | +107 | 63 | -10.0 | -6 | +10 | 15.8 | 0 | 11 | +4 | [-8 ; +24] | [-11 ; +36] | -7 |
| S-M-5 | 14 | +106 | 63 | -10.0 | -7 | +10 | 15.9 | 6 | 10 | +3 | [-9 ; +22] | [-12 ; +35] | -4 |
| S-V-8 | 0 | +103 | 63 | -10.0 | -0 | +0 | 15.4 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-A-8 | 0 | +103 | 63 | -10.0 | -0 | +0 | 15.4 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |
| S-M-8 | 0 | +103 | 63 | -10.0 | -0 | +0 | 15.4 | 0 | 10 | +0 | [+0 ; +0] | [+0 ; +0] | +0 |


## Limites
- Exécution preneur ; peu de cycles ; une seule famille d'entrée (favori) ; règles H1049/H1050 fixées a priori, sans réglage.

_Calcul : 175 s._
