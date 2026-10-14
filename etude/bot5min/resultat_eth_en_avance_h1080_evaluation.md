# Bot95 — H1080 : ETH en avance sur BTC — évaluation (Pitch, 14.10.2026)

## Verdict

**Échantillon insuffisant, verdict reporté.** 30 cas seulement (le critère figé demande au moins 300 cas).
Sur ces 30 cas : 14 gagnés, mise 299 $, **résultat −41 $, ROI −13,8 %**, IC 90 % par cycles **[−124 ; +41] $** (ROI [−38 % ; +16 %]).
L'intervalle contient 0 : rien n'est démontré, ni dans un sens ni dans l'autre. Aucun fantôme, aucune modification du bot.

## Ce qui a été testé

Règle figée le 14.10.2026 05:20 (heure suisse), fichier `eth_en_avance_h1080.py`, **non modifiée** :
ETH Bybit (perp) bouge d'au moins 0,03 % en 300 ms (entre 30 s et 280 s du cycle, 5 s de pause entre deux signaux) alors que BTC Bybit n'a pas
bougé de 2 $ dans le même sens → achat de 10 $ du côté BTC correspondant 164 ms plus tard (vendeur entre 0,40 et 0,70, limite + 1 c),
gardé jusqu'au règlement.

Critère fixé à l'avance : au moins 300 cas sur les cycles ≥ 14.10 ; ROI > 0 et IC 90 % par cycles > 0.

## Données

- Enregistrements Dublin (branche `donnees-rapide`, export relancé le 14.10 à 16:29 UTC), cycles BTC 5 min du 14.10.2026 00:00 UTC au 14.10 15:00 UTC.
- 185 fichiers, 168 cycles avec résultat officiel connu. 15 cycles ont produit au moins un cas.
- Exécution unique : `eth_en_avance_h1080_evaluation.py` (lance la règle figée en mode `--confirmation` sur ces seuls cycles, puis calcule l'IC par
  tirage des cycles, 10 000 tirages).

## Résultats

| | Cas | Gagnés | Mise | Résultat | ROI |
|---|---|---|---|---|---|
| **Total** | **30** | **14** | **299 $** | **−41 $** | **−13,8 %** |
| ETH monte → achat Up | 12 | 9 | 120 $ | +51 $ | +42,5 % |
| ETH baisse → achat Down | 18 | 5 | 179 $ | −92 $ | −51,5 % |

IC 90 % (par cycles) du résultat total : **[−124 ; +41] $**. Prix d'achat moyen ≈ 0,56.

Le BTC suit bien ETH : dans 63 % des cas il bouge dans le même sens dans les 2 s (+9 $ en moyenne), comme vu en exploration (86 %, 7 cas).
Mais cela ne suffit pas à gagner le pari : moins de la moitié des paris (14 sur 30) sont gagnés au règlement.
La séparation Up / Down ne veut rien dire avec si peu de cas (un seul jour, un BTC en baisse ou en hausse suffit à l'expliquer) : elle n'est pas
une piste.

## Suite

À ce rythme (≈ 30 cas pour 168 cycles, soit environ 50 cas par jour), il faut **environ 6 jours de plus** pour réunir 300 cas.
Refaire la même évaluation (même règle, même script) quand ces 300 cas seront disponibles. D'ici là : pas de conclusion, pas de fantôme.
