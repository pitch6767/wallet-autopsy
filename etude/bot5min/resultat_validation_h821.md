# Bot95 — Validation H821 : H816 contre H816 + filtre H821 (CONTRÔLE DU CODE, avant le 13.10 — pas une validation)

Généré le 11.10.2026 20:03 UTC. Cycles avec décisions H816 : 53 ; décisions H816 : 64 ; retirées par le filtre (dist_sigma > -0.0905) : 17 dont 0 par donnée manquante. Mise 20 $, IC 90 % par cycles. Aucun ordre.

## 1. Résultat principal (164 ms) et sensibilité à la latence

| Délai | Politique | Décisions | Exécutées | Taux de gain | Capital engagé ($) | P&L net ($) | P&L par $ | Drawdown ($) | Pire série de pertes | Jackpots | 5 meilleures / total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 164 ms (critère) | H816 | 64 | 60 | 42 % | 1009 | +283 | +28.0 % | 119 | 5 pertes, -94 $ | 13 | 121 % |
| 164 ms (critère) | H816 + H821 | 47 | 46 | 48 % | 791 | +438 | +55.4 % | 82 | 5 pertes, -82 $ | 13 | 78 % |
| 200 ms | H816 | 64 | 58 | 41 % | 972 | +255 | +26.3 % | 124 | 5 pertes, -100 $ | 13 | 136 % |
| 200 ms | H816 + H821 | 47 | 45 | 49 % | 769 | +416 | +54.1 % | 80 | 4 pertes, -80 $ | 13 | 83 % |
| 250 ms | H816 | 64 | 53 | 38 % | 976 | +238 | +24.4 % | 163 | 5 pertes, -100 $ | 13 | 148 % |
| 250 ms | H816 + H821 | 47 | 41 | 44 % | 754 | +397 | +52.7 % | 80 | 4 pertes, -80 $ | 13 | 89 % |
| 500 ms | H816 | 64 | 47 | 34 % | 894 | +281 | +31.5 % | 112 | 6 pertes, -112 $ | 13 | 126 % |
| 500 ms | H816 + H821 | 47 | 36 | 42 % | 674 | +443 | +65.8 % | 72 | 4 pertes, -72 $ | 13 | 80 % |

## 2. Différence variante − H816 et filtre

| Délai | Perdants évités | Gagnants supprimés | Jackpots supprimés | Différence de P&L ($) | IC 90 % total ($) | IC 90 % par décision H816 ($) |
|---|---|---|---|---|---|---|
| 164 ms | 11 | 3 | 0 | +155 | [+64 ; +250] | [+1.00 ; +3.93] |
| 200 ms | 11 | 2 | 0 | +161 | [+68 ; +262] | [+1.05 ; +4.08] |
| 250 ms | 10 | 2 | 0 | +160 | [+42 ; +262] | [+0.65 ; +4.17] |
| 500 ms | 10 | 1 | 0 | +162 | [+44 ; +280] | [+0.69 ; +4.33] |

(Perdants / gagnants / jackpots comptés parmi les décisions retirées qui auraient été exécutées ; 3 retirées n'auraient pas été exécutées à 164 ms.)

## 3. Verdict selon le critère pré-enregistré

**Contrôle du code uniquement (données déjà utilisées pour choisir la règle) : aucun verdict.**

## Limites
- La règle a été choisie parmi 38 candidates, après de nombreuses recherches sur une seule journée de données ; un succès reste une confirmation partielle.
- Peu de cycles : faible puissance ; un échec n'exclut pas un petit effet, un succès peut tenir à quelques trades.
- Une donnée manquante (Chainlink, prix à battre) exclut le signal, comme dans l'étude ; leur nombre est indiqué plus haut.
