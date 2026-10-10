# Audit volatilité : perp Bybit contre bruit Chainlink

| Période | Mesures | Vol. perp médiane ($/s) | Vol. Chainlink médiane ($/s) | Brier moteur actuel | Brier moteur vol. max | Brier carnet | Proba moyenne des côtés à > 90 % / gagnés réellement |
|---|---|---|---|---|---|---|---|
| 07.10-09.10 | 157484 | 3.97 | 2.73 | 0.0425 | 0.0425 | 0.1083 | 0.989 / 0.994 |
| nuit 10.10 (00:15-07:30) | 19673 | 1.50 | 1.05 | 0.0606 | 0.0607 | 0.0944 | 0.991 / 0.980 |

Rejeu TWAP fin (premier signal du cycle, avantage ≥ 0,20, 90-20 s, quantité affichée, frais compris) :

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 07.10-09.10 — moteur vol. max(perp, Chainlink) | 143 | 45 % | **+2'166 $** | +73 % | −215 $ | 5 |
| 07.10-09.10 — moteur actuel (vol. perp) | 143 | 45 % | **+2'166 $** | +73 % | −215 $ | 5 |
| nuit 10.10 (00:15-07:30) — moteur vol. max(perp, Chainlink) | 28 | 32 % | **−298 $** | -34 % | −367 $ | 8 |
| nuit 10.10 (00:15-07:30) — moteur actuel (vol. perp) | 28 | 36 % | **−241 $** | -29 % | −331 $ | 8 |