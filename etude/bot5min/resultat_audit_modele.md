# Audit de la formule du modele — 3677 points (cycles BTC enregistres, 11 instants par cycle)

Brier et log-loss : plus bas = meilleur. Reference : le prix Polymarket (milieu) au meme instant.

| Probabilite | Brier | Log-loss |
|---|---|---|
| **prix Polymarket (milieu)** | 0.1566 | 0.4715 |
| **probabilite enregistree du bot** | 0.1836 | 0.5482 |
| moyenne 60 s (bot), incertitude 0.00 % (0 $) | 0.1715 | 0.5412 |
| moyenne 60 s (bot), incertitude 0.01 % (8 $) | 0.1699 | 0.5084 |
| moyenne 60 s (bot), incertitude 0.02 % (17 $) | 0.1690 | 0.5029 |
| moyenne 60 s (bot), incertitude 0.04 % (33 $) | 0.1718 | 0.5144 |
| moyenne 60 s (bot), incertitude 0.08 % (66 $) | 0.1831 | 0.5473 |
| prix de fin (regle officielle), incertitude 0.00 % (0 $) | 0.1696 | 0.5074 |
| prix de fin (regle officielle), incertitude 0.01 % (8 $) | 0.1697 | 0.5080 |
| prix de fin (regle officielle), incertitude 0.02 % (17 $) | 0.1704 | 0.5109 |
| prix de fin (regle officielle), incertitude 0.04 % (33 $) | 0.1741 | 0.5228 |
| prix de fin (regle officielle), incertitude 0.08 % (66 $) | 0.1848 | 0.5521 |

## Calibration quand la formule donne 25-50 % a un cote (la zone ou nos desaccords naissent)

| Probabilite | Points | Dit en moyenne | Arrive en vrai |
|---|---|---|---|
| probabilite enregistree du bot | 3069 | 0.40 | **0.30** |
| prix Polymarket (milieu) | 1570 | 0.37 | **0.37** |
| moyenne 60 s (bot), 0.00 % | 1949 | 0.38 | **0.35** |
| moyenne 60 s (bot), 0.01 % | 2009 | 0.38 | **0.35** |
| moyenne 60 s (bot), 0.08 % | 3073 | 0.40 | **0.29** |
| prix de fin (regle officielle), 0.00 % | 2255 | 0.38 | **0.34** |
| prix de fin (regle officielle), 0.01 % | 2299 | 0.38 | **0.34** |
| prix de fin (regle officielle), 0.08 % | 3145 | 0.40 | **0.29** |