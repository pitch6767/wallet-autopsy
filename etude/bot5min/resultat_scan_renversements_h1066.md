# Bot95 — H1066 : grand balayage « qu'est-ce qui précède un renversement ou une accélération ? »

13.10.2026, demande de Pitch 20:14. Exploration, aucun ordre, aucun fantôme modifié. Période réservée (≥ 13.10) non utilisée.
Scripts : `scan_h1066/`. Trois sources :
- 469 cycles Dublin (11.10 08:05 → 12.10 24:00), 1 s, ~50 mesures (Polymarket, perp, Binance, OKX, Coinbase, Bybit, Chainlink, carnets, flux, liquidations, OI).
  Découpage apprentissage / validation / test (A / V / T) comme d'habitude.
- 30 jours de Binance 1 s (12.09 → 11.10) : 8 638 fenêtres de 5 min ; exploration 20 jours (E), contrôle 10 jours (C).
- Nos petits billets (≤ 0,20) : 1 290 achats uniques (cycle, côté) de toutes les stratégies du bot, 06.10 → 12.10.

## 1. Renversements du favori (Polymarket, favori 0,65–0,95)

Le marché est calibré : 19 % / 12 % / 24 % de favoris perdants (A / V / T) pour 18 % attendus. Sur 41 mesures, aucune n'annonce
un renversement de façon stable sur les trois périodes au-delà du prix. Les « favoris qui ont reculé de leur plus haut » perdent plus en A
et T, mais pas en V. Fenêtres qui commencent à :00 et :30 de l'heure : favori perdant plus que prévu dans les 3 périodes (+1 / +4 / +21 pts),
mais 43 à 115 cas : piste seulement.

## 2. Renversements dans BTC lui-même (30 jours Binance, à distance égale du prix d'exercice)

| Mesure (sens du favori) | Exploration | Contrôle | Lecture |
|---|---|---|---|
| Volatilité 5 min / volatilité 1 h élevée | −6,9 pts | −6,9 pts | après une agitation, la volatilité retombe : moins de renversements que l'écart ne le laisse croire |
| Élan sur 10 s vers le favori | −2,9 | −4,0 | l'élan continue |
| Agresseurs Binance 30 s pour le favori | −2,7 | −4,0 | idem |
| Élan sur 30 s | −1,6 | −4,0 | idem |
| Un nombre rond (100 $) entre le prix et le prix d'exercice | −1,1 | −2,0 | léger « mur » |
| Heure, jour, minute, fenêtre précédente | ≈ 0 | ≈ 0 | rien |

Sur Polymarket (Dublin), ces mêmes mesures ne donnent rien de stable : soit le marché les intègre déjà, soit 469 cycles sont trop peu
pour voir 3 à 7 points.

## 3. Accélérations

- BTC (30 jours) : les sauts (≥ 3 σ en 10 s) arrivent 4 à 5 fois plus souvent quand la volatilité / le volume des 30 dernières secondes est
  élevé (2 % → 9–10 %), et plus souvent aux minutes :00–:02 et :30–:32 de l'heure et entre 12 et 14 h UTC. La direction suit les agresseurs
  et l'élan des 30 s (stable sur les deux périodes).
- Polymarket (Dublin) : **le déséquilibre du carnet Polymarket annonce la direction des 10 s suivantes dans les trois périodes.** Carnet
  penché vers le favori (quintile haut) contre penché contre (quintile bas) : +1,8 / +2,4 / +4,1 c d'écart sur 10 s. C'est la mesure la plus stable
  de la soirée, mais 2 à 4 c ne paient pas un aller-retour preneur (écart + 2 frais ≈ 4–5 c). Usage possible : choisir le moment d'entrée
  des stratégies existantes (entrer quand le carnet penche de notre côté).

## 4. Nos petits billets (≤ 0,20)

Gagnants contre perdants, 06.10 → 11.10 (993 billets, 137 gagnants, prix moyen 0,114, ROI +9 %) : le billet gagne quand l'élan du favori
s'est arrêté (élan 30 s ≤ 0 : 17 % gagnants, ROI +42 % ; sinon 12 %, −14 % ; favori qui a reculé : +48 % contre −20 %).
Règles figées (H1065, commit 09c82b7) puis validées sur les billets du 12.10 : **non validé** (sens inverse, seulement 24 gagnants).
Les mêmes mesures prises côté Polymarket / perp / carnet Binance vont dans le bon sens le 11.10 ET le 12.10 (regardé après coup) :
figées en H1065 bis (commit bd3836f), jugées une fois sur ≥ 13.10.

## Conclusion

Rien de démontré. Ce qui revient partout : **l'élan continue, la volatilité retombe, et le carnet Polymarket penche avant de bouger.**
Les renversements « prévisibles » ne le sont pas au-delà du prix. Pistes à confirmer sur ≥ 13.10 : H1065 bis (billets) et l'effet :00 / :30.
