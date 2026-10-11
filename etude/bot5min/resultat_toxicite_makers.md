# Bot95 — Pourquoi les makers rentables évitent les mauvais remplissages (H695, Test B) — PRÉLIMINAIRE

Généré le 11.10.2026 14:06 UTC. 51 cycles communs (marchés lus × cycles enregistrés à Dublin). Transactions preneuses rapprochées de Dublin : 11731 / 62531 (19 %). Remplissages makers datés à la ms : 62122. Makers classés sur toute la base (≥ 20 marchés, ≥ 5 000 $) : 40 rentables (≥ +1 % par $), 48 perdants (≤ −0,5 %).

Sélection adverse = prix du côté du maker h secondes après, moins son prix (cents par part ; négatif = le marché est parti contre lui). Pondérée par les parts.

## 1. Sélection adverse : makers réels contre nos fantômes

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| makers rentables | 10849 | +0.4 | +0.3 | +0.4 | +0.4 | +0.5 | +0.8 | -0.6 |
| makers perdants | 10289 | +0.4 | +0.2 | -0.0 | -0.1 | -0.1 | +0.8 | +0.7 |
| makers autres | 40984 | +0.5 | +0.5 | +0.5 | +0.3 | +0.1 | -0.4 | -1.4 |
| nous M0 | 21 | — | — | -0.3 | -1.3 | -1.8 | +2.9 | +13.8 |
| nous M1 | 80 | — | — | -0.4 | +0.0 | -0.4 | -0.9 | +16.7 |
| nous M2 | 259 | — | — | -3.0 | -5.5 | -6.0 | -6.8 | -0.0 |
| nous M3 | 50 | — | — | +3.7 | +3.7 | -1.0 | +8.8 | +27.4 |
| nous M4 | 103 | — | — | -1.1 | -1.7 | -2.2 | -2.5 | +3.4 |
| nous M5 | 82 | — | — | -2.5 | -4.1 | -3.9 | -4.8 | +8.9 |

(nos fantômes : pas de mesure à 0,1 et 0,3 s ; la sélection adverse « règlement » est le résultat par part)

## 2. Explications candidates (tous les makers réels, puis rentables seulement)

**Au meilleur prix ou plus loin**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| au meilleur prix — tous | 59916 | +0.5 | +0.4 | +0.4 | +0.2 | +0.2 | +0.1 | -1.2 |
| au meilleur prix — rentables | 10488 | +0.4 | +0.4 | +0.4 | +0.4 | +0.4 | +0.8 | -0.8 |
| plus loin (servi par un balayage) — tous | 2206 | +0.3 | -0.2 | +0.0 | +0.5 | -0.7 | -1.8 | +2.4 |
| plus loin (servi par un balayage) — rentables | 361 | +0.1 | -0.3 | +0.4 | +1.1 | +1.9 | +0.5 | +3.9 |

**Balayage de plusieurs niveaux par le preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur sur un seul prix — tous | 34727 | +0.4 | +0.3 | +0.4 | +0.1 | +0.1 | -0.1 | -1.0 |
| preneur sur un seul prix — rentables | 5248 | +0.4 | +0.2 | +0.3 | +0.3 | +0.6 | +1.0 | -0.6 |
| balayage — tous | 27395 | +0.5 | +0.5 | +0.4 | +0.5 | +0.2 | +0.2 | -1.2 |
| balayage — rentables | 5601 | +0.5 | +0.5 | +0.6 | +0.5 | +0.4 | +0.6 | -0.6 |

**Conditions toxiques de M4 actives au remplissage**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| aucune — tous | 36943 | +0.5 | +0.4 | +0.3 | +0.1 | +0.2 | +0.1 | -1.0 |
| aucune — rentables | 7252 | +0.5 | +0.4 | +0.4 | +0.2 | +0.3 | +0.4 | -2.2 |
| a — tous | 40 | -1.5 | -2.5 | -5.5 | -9.5 | -8.5 | -2.5 | +47.7 |
| a — rentables | 9 | +0.5 | +0.5 | +0.5 | +5.5 | +6.5 | +5.5 | +52.0 |
| b — tous | 256 | +0.8 | +0.7 | +0.1 | -0.5 | -0.7 | -0.8 | -3.2 |
| b — rentables | 4 | +0.5 | +0.5 | +0.5 | -0.5 | -1.5 | -1.5 | -5.0 |
| c — tous | 23573 | +0.5 | +0.4 | +0.6 | +0.5 | +0.2 | +0.1 | -0.4 |
| c — rentables | 3494 | +0.4 | +0.3 | +0.4 | +0.6 | +0.7 | +1.3 | +1.1 |
| ac — tous | 76 | +0.6 | -1.3 | -1.3 | -1.6 | -0.9 | -2.4 | -7.5 |
| ac — rentables | 3 | +10.0 | +11.5 | +16.5 | +17.5 | +19.9 | +23.5 | +28.0 |
| bc — tous | 1110 | +0.0 | -0.1 | -0.2 | -0.8 | -0.7 | -2.0 | -10.9 |
| bc — rentables | 56 | +0.4 | +0.7 | +1.0 | +0.4 | +1.5 | +1.0 | +1.3 |
| ab — tous | 16 | -3.5 | -17.5 | -13.5 | -19.5 | -20.5 | -19.5 | -24.3 |
| ab — rentables | 0 | — | — | — | — | — | — | — |
| abc — tous | 108 | +0.2 | -0.1 | +0.1 | +1.0 | +1.0 | -1.4 | -9.3 |
| abc — rentables | 31 | +0.0 | +0.1 | +0.2 | +0.9 | +1.3 | -1.3 | -9.1 |

**Taille de la transaction du preneur**

| Groupe | Remplissages | +0,1 s | +0,3 s | +1 s | +3 s | +5 s | +10 s | règlement |
|---|---|---|---|---|---|---|---|---|
| preneur 0–10 $ — tous | 59919 | +0.5 | +0.4 | +0.5 | +0.3 | +0.2 | +0.1 | -1.3 |
| preneur 0–10 $ — rentables | 10592 | +0.5 | +0.4 | +0.5 | +0.5 | +0.5 | +0.7 | -1.2 |
| preneur 10–50 $ — tous | 1809 | +0.1 | -0.1 | -0.2 | -1.0 | -0.2 | -0.8 | +1.3 |
| preneur 10–50 $ — rentables | 221 | -0.1 | -0.6 | -1.0 | -1.3 | -0.3 | +1.2 | +7.0 |
| preneur 50–200 $ — tous | 351 | +0.3 | -0.0 | -0.1 | -0.7 | -0.6 | -2.0 | +1.2 |
| preneur 50–200 $ — rentables | 32 | +1.2 | +1.1 | +2.3 | +3.8 | +10.4 | +10.8 | +9.1 |
| preneur 200–∞ $ — tous | 43 | +0.1 | -0.2 | -1.5 | -1.5 | +1.5 | +1.5 | +8.3 |
| preneur 200–∞ $ — rentables | 4 | -1.5 | -1.5 | -1.5 | -1.5 | +1.5 | +1.5 | +42.0 |

**Part de chaque situation : makers rentables contre perdants contre nos fantômes**

- makers rentables : au meilleur prix 97 % ; balayages 52 % ; condition toxique active 33 % ; prix médian 0.33 ; moment médian 165 s
- makers perdants : au meilleur prix 96 % ; balayages 55 % ; condition toxique active 32 % ; prix médian 0.33 ; moment médian 147 s
- nos fantômes : au meilleur prix 63 % ; prix médian 0.28

## Limites
- Une journée de cycles communs ; rapprochement par seconde, prix, côté et taille (les transactions non rapprochées sont exclues).
- Les ordres posés puis annulés par ces makers sont invisibles : on ne voit que leurs remplissages.
- Rentable / perdant est mesuré sur toute la base, y compris ces cycles.
