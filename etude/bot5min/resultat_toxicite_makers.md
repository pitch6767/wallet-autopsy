# Bot95 — Pourquoi les makers rentables évitent les mauvais remplissages (H695, Test B) — PRÉLIMINAIRE

Généré le 11.10.2026 16:52 UTC. 51 cycles communs (marchés lus × cycles enregistrés à Dublin). Transactions preneuses rapprochées de Dublin : 13311 / 71747 (19 %). Remplissages makers datés à la ms : 69429. Makers classés sur toute la base (≥ 20 marchés, ≥ 5 000 $) : 59 rentables (≥ +1 % par $), 114 perdants (≤ −0,5 %).

Sélection adverse = prix du côté du maker h secondes après, moins son prix (cents par part ; négatif = le marché est parti contre lui). Pondérée par les parts.

## 1. Sélection adverse : makers réels contre nos fantômes

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| makers rentables | 12922 | +0.5 | +0.4 | +0.4 | +0.4 | +0.7 | +1.4 | +0.3 |
| makers perdants | 18621 | +0.4 | +0.3 | -0.0 | -0.5 | -0.7 | -0.8 | +0.9 |
| makers autres | 37886 | +0.5 | +0.5 | +0.7 | +0.8 | +1.0 | +0.4 | +1.0 |
| nous M0 | 113 | — | — | -1.0 | -1.6 | -1.7 | -1.3 | -4.2 |
| nous M1 | 337 | — | — | -0.7 | -1.0 | -0.4 | +0.3 | +2.1 |
| nous M10 | 271 | — | — | -0.4 | -0.2 | -0.2 | +0.8 | -3.2 |
| nous M11 | 12 | — | — | -1.3 | -0.9 | -3.1 | +1.4 | -17.5 |
| nous M2 | 771 | — | — | -2.1 | -3.1 | -3.0 | -3.2 | -2.6 |
| nous M21 | 118 | — | — | -0.9 | -0.8 | -1.2 | -0.8 | +1.6 |
| nous M3 | 225 | — | — | +3.6 | +2.8 | +1.2 | +1.6 | -0.6 |
| nous M4 | 505 | — | — | -0.9 | -0.8 | -1.2 | -1.3 | -4.5 |
| nous M4a | 360 | — | — | -1.1 | -1.5 | -1.2 | -0.5 | -4.7 |
| nous M4b | 352 | — | — | -1.2 | -1.6 | -1.5 | +0.1 | -6.3 |
| nous M4c | 341 | — | — | -1.0 | -1.7 | -1.5 | -0.9 | -9.5 |
| nous M5 | 414 | — | — | -1.9 | -2.6 | -1.8 | -2.2 | -2.9 |
| nous M6 | 1124 | — | — | -2.0 | -2.0 | -1.3 | -1.0 | -7.3 |
| nous M8 | 216 | — | — | -0.5 | -0.9 | -0.5 | +0.3 | -5.5 |
| nous M8b | 148 | — | — | -0.7 | -1.1 | -0.9 | -0.2 | -8.2 |
| nous M9 | 6 | — | — | -3.5 | +1.1 | +3.5 | +5.0 | +3.7 |

(nos fantômes : pas de mesure à 0,1 et 0,3 s ; la sélection adverse « règlement » est le résultat par part)

## 2. Explications candidates (tous les makers réels, puis rentables seulement)

**Au meilleur prix ou plus loin**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| au meilleur prix — tous | 66754 | +0.5 | +0.5 | +0.5 | +0.3 | +0.5 | +0.3 | +0.7 |
| au meilleur prix — rentables | 12395 | +0.5 | +0.4 | +0.4 | +0.4 | +0.7 | +1.5 | +0.2 |
| plus loin (servi par un balayage) — tous | 2675 | +0.2 | -0.4 | -0.0 | +0.6 | -0.5 | -1.3 | +2.7 |
| plus loin (servi par un balayage) — rentables | 527 | +0.5 | -0.5 | +0.2 | -0.0 | +0.6 | +1.0 | +3.9 |

**Balayage de plusieurs niveaux par le preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur sur un seul prix — tous | 36825 | +0.4 | +0.4 | +0.4 | +0.2 | +0.3 | -0.1 | +0.5 |
| preneur sur un seul prix — rentables | 6471 | +0.5 | +0.4 | +0.3 | +0.6 | +0.9 | +1.3 | +1.9 |
| balayage — tous | 32604 | +0.5 | +0.5 | +0.4 | +0.5 | +0.5 | +0.5 | +1.4 |
| balayage — rentables | 6451 | +0.6 | +0.4 | +0.4 | +0.1 | +0.4 | +1.6 | -3.1 |

**Conditions toxiques de M4 actives au remplissage**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| aucune — tous | 40850 | +0.5 | +0.4 | +0.3 | +0.1 | +0.4 | +0.2 | +1.0 |
| aucune — rentables | 7428 | +0.5 | +0.4 | +0.4 | +0.3 | +0.8 | +0.6 | +3.3 |
| a — tous | 40 | -1.5 | -2.5 | -5.5 | -9.5 | -8.5 | -2.5 | +47.7 |
| a — rentables | 9 | +0.5 | +0.5 | +0.5 | +5.5 | +6.5 | +5.5 | +52.0 |
| b — tous | 256 | +0.8 | +0.7 | +0.1 | -0.5 | -0.7 | -0.8 | -3.2 |
| b — rentables | 57 | +4.5 | +4.3 | +1.1 | +0.0 | -0.2 | -2.5 | -3.1 |
| c — tous | 26968 | +0.5 | +0.5 | +0.6 | +0.6 | +0.6 | +0.4 | +1.4 |
| c — rentables | 5040 | +0.5 | +0.4 | +0.4 | +0.5 | +0.6 | +2.3 | -0.9 |
| ac — tous | 81 | +0.7 | -1.1 | -1.2 | -1.4 | -0.7 | -2.1 | -6.0 |
| ac — rentables | 12 | +2.0 | +0.2 | -0.6 | -0.5 | +0.6 | -1.1 | -5.5 |
| bc — tous | 1110 | +0.0 | -0.1 | -0.2 | -0.8 | -0.7 | -2.0 | -10.9 |
| bc — rentables | 342 | +0.4 | +0.4 | +0.5 | -0.2 | +1.1 | +0.3 | -0.7 |
| ab — tous | 16 | -3.5 | -17.5 | -13.5 | -19.5 | -20.5 | -19.5 | -24.3 |
| ab — rentables | 6 | -3.5 | -17.5 | -13.5 | -19.5 | -20.5 | -19.5 | -60.0 |
| abc — tous | 108 | +0.2 | -0.1 | +0.1 | +1.0 | +1.0 | -1.4 | -9.3 |
| abc — rentables | 28 | -0.2 | -0.1 | -0.8 | -0.6 | +0.1 | -2.1 | -9.4 |

**Taille de la transaction du preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur 0–10 $ — tous | 66854 | +0.5 | +0.4 | +0.5 | +0.4 | +0.4 | +0.2 | +0.3 |
| preneur 0–10 $ — rentables | 12424 | +0.5 | +0.4 | +0.4 | +0.5 | +0.7 | +1.5 | +0.3 |
| preneur 10–50 $ — tous | 2114 | +0.2 | +0.0 | +0.2 | -0.2 | +0.2 | -0.4 | +6.2 |
| preneur 10–50 $ — rentables | 363 | +0.2 | +0.1 | +0.2 | -1.1 | -0.1 | +1.0 | +0.4 |
| preneur 50–200 $ — tous | 418 | +0.3 | +0.1 | +0.2 | -0.0 | +0.1 | -0.4 | +6.3 |
| preneur 50–200 $ — rentables | 107 | +0.5 | +0.4 | +0.4 | +0.2 | +0.1 | +0.3 | -2.4 |
| preneur 200–∞ $ — tous | 43 | +0.1 | -0.2 | -1.5 | -1.5 | +1.5 | +1.5 | +8.3 |
| preneur 200–∞ $ — rentables | 28 | +0.1 | -0.1 | -1.5 | -1.5 | +1.5 | +1.5 | +8.6 |

**Part de chaque situation : makers rentables contre perdants contre nos fantômes**

- makers rentables : au meilleur prix 96 % ; balayages 50 % ; condition toxique active 43 % ; prix médian 0.20 ; moment médian 173 s
- makers perdants : au meilleur prix 96 % ; balayages 53 % ; condition toxique active 38 % ; prix médian 0.38 ; moment médian 132 s
- nos fantômes : au meilleur prix 84 % ; prix médian 0.33

## Limites
- Une journée de cycles communs ; rapprochement par seconde, prix, côté et taille (les transactions non rapprochées sont exclues).
- Les ordres posés puis annulés par ces makers sont invisibles : on ne voit que leurs remplissages.
- Rentable / perdant est mesuré sur toute la base, y compris ces cycles.
