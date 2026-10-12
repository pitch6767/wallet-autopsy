# Bot95 — « Désaccord 30 zone + Binance et perp + sortie modèle −10 »

Rapport du 08.10.2026, 18h · fantôme BTC lancé le 08.10 à 09:03 · 25 trades en direct · 50 $ par trade, frais Polymarket compris.

## 1. En bref

- **En direct depuis ce matin : 25 trades, 10 positifs, 15 négatifs, +609 $.**
- Le gain vient de quelques gros coups (achat vers 0,16-0,25 $, revente 1 $ à la fin) ; la plupart des trades perdent peu ou tout. C'est normal pour ce type de stratégie : on achète des « billets » sous-évalués.
- **Défaut trouvé :** quand le modèle perd 10 points, le bot revend dans un carnet presque vide — souvent à 0,02-0,04 $ la part, une fois même à 0,00 $. Sur les 12 reventes, il n'a récupéré que 176 $ au total.
- **Amélioration trouvée :** écarter les désaccords créés par **Polymarket qui baisse** (un vendeur casse son prix sans que le modèle bouge). Sur 48 h de carnets : 5 trades perdants de moins, résultat un peu meilleur, creux plus petit, les 4 quarts positifs.
> Aucun filtre ne supprime beaucoup de perdants sans perdre beaucoup de gain : cette stratégie gagne environ 1 fois sur 3, et c'est sa nature. On peut seulement retirer les perdants « évitables ».
---PAGE---
## 2. Le système en détail

**Le marché.** Polymarket ouvre toutes les 5 minutes un pari « le BTC sera-t-il plus haut ou plus bas qu'au début du cycle ? ». Deux jetons : Up et Down. Le jeton gagnant vaut 1 $ à la fin, l'autre 0 $. Le prix d'un jeton (par exemple 0,25 $) est la probabilité que le marché lui donne (25 %).
**Le modèle.** Le bot calcule sa propre probabilité à partir du prix du BTC sur les bourses (Chainlink, Binance, Bybit, OKX, Coinbase), du prix de départ à battre, du temps restant et de la volatilité. Il tient compte de la façon dont Polymarket fixe le résultat.
**Le désaccord.** Quand le modèle donne nettement plus de chances à un côté que le prix demandé par le meilleur vendeur, ce jeton est peut-être sous-évalué.
**Les 4 conditions d'achat (toutes en même temps) :**
- 1. **Écart d'au moins 30 points** : modèle − prix du meilleur vendeur ≥ 0,30 (par exemple modèle 0,55 et vendeur à 0,25).
- 2. **Jeton entre 0,15 et 0,35 $** : ni loterie (moins de 0,15, trop aléatoire), ni trop cher.
- 3. **Plus de 60 secondes restantes** dans le cycle.
- 4. **Binance et le perp Bybit ne vont pas contre nous** sur les 3 dernières secondes (s'ils montent pour Up / baissent pour Down, ou restent stables).
**L'achat.** 50 $ au meilleur vendeur, jusqu'à son prix + 1 cent. Si le vendeur n'a pas assez de jetons à ce prix, le bot achète ce qui est disponible (d'où des positions plus petites que 50 $). Un seul achat par cycle.
**La sortie.** Deux possibilités :
- **Revente** si le modèle a perdu 10 points depuis l'achat (par exemple de 0,55 à 0,45) : le désaccord n'existe plus.
- Sinon, **garde jusqu'au résultat** : 1 $ par jeton si on gagne, 0 $ sinon.
**Exemple réel (08.10, 13:13 heure suisse) :** 69 s avant la fin, le modèle donne 0,486 au côté Up, le meilleur vendeur le propose à 0,18 $ (écart 0,31) ; Binance et le perp sont stables (pas contre nous) → achat de 278 jetons Up au prix moyen de 0,19 $ (53 $). Le BTC finit au-dessus du prix de départ : 278 $ récupérés, **+225 $**.

## 3. Résultats en direct

| Trades | Positifs | Négatifs | Résultat | Meilleur | Pire |
|---|---|---|---|---|---|
| 25 | 10 | 15 | **+609 $** | +280 $ | −53 $ |

## 4. Le défaut des reventes

Quand le modèle perd 10 points, le prix du jeton s'est déjà effondré et il ne reste presque plus d'acheteurs. Le bot vend quand même tout, en descendant dans le carnet jusqu'à des prix ridicules. Exemples : 333 jetons achetés 0,17 $ revendus pour 12,41 $ (0,04 $ pièce) ; une position revendue 0,00 $.
> **Correction proposée :** ne jamais revendre sous 0,05 $ ni à plus de 2 cents sous le meilleur acheteur. Si personne n'achète à ce prix, on garde jusqu'au résultat (on a de toute façon presque tout perdu, et on garde la petite chance de gagner).

## 5. Recherche d'amélioration (48 h de vrais carnets, rejoués seconde par seconde)

Même stratégie rejouée sur tous les cycles BTC du 06.10 18h au 08.10 18h. Attention : le rejeu suppose qu'on revend au meilleur acheteur — plus favorable que la réalité vue au point 4.

### Façons de sortir

| Sortie | Trades | Perdants | Total | Par trade | Sans top 3 | Creux max |
|---|---|---|---|---|---|---|
| revente si modèle -10 (actuel) | 99 | 64 | +4'508 $ | +46 $ | +3'667 $ | −510 $ |
| revente si modèle -10, seulement s'il reste > 60 s | 99 | 64 | +4'504 $ | +45 $ | +3'663 $ | −514 $ |
| revente si modèle -10, seulement si acheteur >= 0,05 | 99 | 64 | +4'453 $ | +45 $ | +3'612 $ | −525 $ |
| revente si modèle -10, > 60 s ET acheteur >= 0,05 | 99 | 64 | +4'453 $ | +45 $ | +3'612 $ | −525 $ |
| revente si modèle -15 | 99 | 65 | +4'456 $ | +45 $ | +3'616 $ | −585 $ |
| revente si modèle -15, > 60 s ET acheteur >= 0,05 | 99 | 65 | +4'412 $ | +45 $ | +3'571 $ | −604 $ |
| jamais de revente (garder) | 99 | 64 | +4'406 $ | +45 $ | +3'565 $ | −687 $ |

La revente apporte peu (+100 $ sur 48 h par rapport à « garder », et encore, au meilleur acheteur). Avec la correction du point 4, elle ne peut plus faire de dégâts.

### Filtres à l'entrée (chacun seul)

| Filtre ajouté | Trades | Perdants | Total | Par trade | Sans top 3 | Creux max |
|---|---|---|---|---|---|---|
| Aucun (stratégie actuelle) | 99 | 64 | +4'508 $ | +46 $ | +3'667 $ | −510 $ |
| le modèle a monte (>= 3 pts en 3 s) | 67 | 41 | +3'794 $ | +57 $ | +2'953 $ | −328 $ |
| pas « Polymarket qui baisse » | 93 | 59 | +4'635 $ | +50 $ | +3'794 $ | −437 $ |
| écart qui grandit | 92 | 59 | +4'244 $ | +46 $ | +3'403 $ | −487 $ |
| plus de 120 s restantes | 44 | 30 | +1'740 $ | +40 $ | +941 $ | −316 $ |
| plus de 90 s restantes | 68 | 48 | +2'224 $ | +33 $ | +1'404 $ | −499 $ |
| prix >= 0,18 | 77 | 53 | +2'137 $ | +28 $ | +1'462 $ | −473 $ |
| prix >= 0,20 | 58 | 41 | +1'198 $ | +21 $ | +607 $ | −420 $ |
| modèle >= 0,50 | 76 | 48 | +3'475 $ | +46 $ | +2'676 $ | −420 $ |
| écart >= 0,33 | 60 | 39 | +2'542 $ | +42 $ | +1'722 $ | −269 $ |
| vendeur assez gros pour 50 $ | 79 | 55 | +2'662 $ | +34 $ | +1'821 $ | −455 $ |
| spread 1 c | 98 | 64 | +4'311 $ | +44 $ | +3'470 $ | −510 $ |
| Polymarket monte (5 s) | 66 | 43 | +2'496 $ | +38 $ | +1'676 $ | −330 $ |
| OKX >= 0 | 97 | 63 | +4'355 $ | +45 $ | +3'514 $ | −510 $ |
| Coinbase >= 0 | 97 | 64 | +4'108 $ | +42 $ | +3'267 $ | −510 $ |
| sans nuit | 58 | 34 | +3'234 $ | +56 $ | +2'393 $ | −215 $ |

### Combinaisons qui gardent au moins 95 % du gain avec moins de perdants

| Filtres | Trades | Perdants | Total | Par trade | Sans top 3 | Creux max |
|---|---|---|---|---|---|---|
| pas « Polymarket qui baisse » + écart qui grandit | 86 | 54 | +4'371 $ | +51 $ | +3'530 $ | −413 $ |
| pas « Polymarket qui baisse » | 93 | 59 | +4'635 $ | +50 $ | +3'794 $ | −437 $ |
| pas « Polymarket qui baisse » + spread 1 c | 92 | 59 | +4'438 $ | +48 $ | +3'597 $ | −437 $ |
| OKX >= 0 | 97 | 63 | +4'355 $ | +45 $ | +3'514 $ | −510 $ |

> **Verdict :** seul « pas Polymarket qui baisse » réduit les perdants (64 → 59) tout en gardant le gain (+4 508 → +4 635 $) et en réduisant le creux (−510 → −437 $). « Sans nuit » ou « plus de 120 s » suppriment beaucoup de perdants mais aussi beaucoup de gain.

## 6. Proposition (tu décides)

- **Corriger les reventes** (plancher 0,05 $ et 2 cents sous le meilleur acheteur) sur les trois fantômes avec sortie −10. C'est une correction de défaut, pas un changement de règle.
- **Nouveau fantôme à côté :** même stratégie + « pas Polymarket qui baisse ». L'actuel reste figé pour comparer.
---PAGE---
## Annexe A — les 25 trades en direct

| # | Heure (CH) | Côté | Prix d'achat | Issue du marché | Revente | Résultat | Cumul |
|---|---|---|---|---|---|---|---|
| 1 | 08.10 07:56 | Down | 0.304 | perdu | modèle 0.586→0.474, 178.6 jetons pour 6.65 $ | −47.68 $ | −47.68 $ |
| 2 | 08.10 08:13 | Down | 0.232 | perdu | modèle 0.524→0.421, 227.3 jetons pour 18.09 $ | −34.72 $ | −82.40 $ |
| 3 | 08.10 08:33 | Down | 0.250 | gagné | — | +162.99 $ | +80.59 $ |
| 4 | 08.10 09:03 | Up | 0.164 | perdu | modèle 0.481→0.379, 140.1 jetons pour 3.91 $ | −18.99 $ | +61.60 $ |
| 5 | 08.10 09:38 | Up | 0.168 | perdu | — | −12.18 $ | +49.42 $ |
| 6 | 08.10 09:48 | Up | 0.166 | gagné | — | +12.51 $ | +61.93 $ |
| 7 | 08.10 10:27 | Up | 0.159 | perdu | modèle 0.464→0.359, 333.3 jetons pour 40.98 $ | −12.08 $ | +49.85 $ |
| 8 | 08.10 10:47 | Down | 0.230 | gagné | — | +23.87 $ | +73.72 $ |
| 9 | 08.10 10:57 | Up | 0.159 | gagné | — | +280.27 $ | +353.99 $ |
| 10 | 08.10 11:05 | Down | 0.354 | gagné | — | +34.86 $ | +388.85 $ |
| 11 | 08.10 11:16 | Up | 0.176 | perdu | modèle 0.466→0.363, 14.0 jetons pour 2.37 $ | −0.10 $ | +388.75 $ |
| 12 | 08.10 11:32 | Down | 0.168 | gagné | — | +252.48 $ | +641.23 $ |
| 13 | 08.10 11:43 | Up | 0.201 | gagné | modèle 0.504→0.379, 5.0 jetons pour 1.13 $ | +0.13 $ | +641.36 $ |
| 14 | 08.10 11:51 | Down | 0.169 | perdu | modèle 0.456→0.354, 333.3 jetons pour 12.41 $ | −43.83 $ | +597.53 $ |
| 15 | 08.10 12:13 | Up | 0.191 | gagné | — | +224.83 $ | +822.36 $ |
| 16 | 08.10 12:27 | Up | 0.169 | perdu | — | −38.30 $ | +784.06 $ |
| 17 | 08.10 12:52 | Down | 0.166 | perdu | — | −5.44 $ | +778.62 $ |
| 18 | 08.10 13:12 | Up | 0.243 | perdu | — | −52.77 $ | +725.85 $ |
| 19 | 08.10 13:21 | Down | 0.284 | perdu | — | −52.63 $ | +673.22 $ |
| 20 | 08.10 14:30 | Up | 0.336 | perdu | modèle 0.625→0.515, 156.3 jetons pour 49.08 $ | −3.37 $ | +669.85 $ |
| 21 | 08.10 14:52 | Down | 0.170 | perdu | modèle 0.462→0.347, 312.5 jetons pour 35.12 $ | −17.90 $ | +651.95 $ |
| 22 | 08.10 14:57 | Up | 0.191 | gagné | modèle 0.49→0.387, 35.0 jetons pour 4.93 $ | −1.74 $ | +650.21 $ |
| 23 | 08.10 16:15 | Up | 0.243 | perdu | modèle 0.549→0.442, 5.0 jetons pour 1.31 $ | +0.11 $ | +650.32 $ |
| 24 | 08.10 16:38 | Up | 0.164 | perdu | modèle 0.624→0.515, 5.0 jetons pour 0.00 $ (4 fois) | −53.20 $ | +597.12 $ |
| 25 | 08.10 16:52 | Down | 0.264 | gagné | — | +11.78 $ | +608.90 $ |
---PAGE---
## Annexe B — les 99 trades du rejeu 48 h

| # | Heure (CH) | Côté | Prix | Modèle | Écart | Reste | Binance 3 s | Perp 3 s | Issue | Sortie | Résultat | Cumul |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 06.10 20:07 | Up | 0.17 | 0.48 | 0.32 | 126 s | +0 | +0 | perdu | fin | −52.99 $ | −52.99 $ |
| 2 | 06.10 21:13 | Up | 0.17 | 0.50 | 0.33 | 66 s | +6 | +4 | gagné | fin | +241.13 $ | +188.14 $ |
| 3 | 06.10 21:23 | Down | 0.21 | 0.53 | 0.32 | 111 s | +0 | -0 | perdu | fin | −52.84 $ | +135.30 $ |
| 4 | 06.10 22:08 | Up | 0.19 | 0.50 | 0.31 | 61 s | +0 | +0 | perdu | fin | −52.92 $ | +82.38 $ |
| 5 | 06.10 22:18 | Down | 0.18 | 0.48 | 0.30 | 96 s | -0 | -0 | perdu | revendu | −47.79 $ | +34.59 $ |
| 6 | 06.10 22:38 | Up | 0.15 | 0.46 | 0.31 | 69 s | +0 | +0 | gagné | fin | +280.27 $ | +314.86 $ |
| 7 | 06.10 22:53 | Up | 0.20 | 0.50 | 0.30 | 118 s | +0 | +0 | perdu | fin | −52.88 $ | +261.98 $ |
| 8 | 06.10 23:20 | Up | 0.24 | 0.56 | 0.32 | 249 s | +11 | +18 | gagné | fin | +155.60 $ | +417.58 $ |
| 9 | 06.10 23:27 | Down | 0.23 | 0.54 | 0.31 | 122 s | -0 | -0 | perdu | fin | −52.77 $ | +364.81 $ |
| 10 | 06.10 23:48 | Down | 0.17 | 0.47 | 0.30 | 88 s | -0 | -0 | perdu | fin | −52.99 $ | +311.82 $ |
| 11 | 07.10 00:03 | Up | 0.17 | 0.49 | 0.32 | 99 s | +8 | +6 | gagné | fin | +241.13 $ | +552.95 $ |
| 12 | 07.10 00:08 | Up | 0.17 | 0.49 | 0.32 | 78 s | +0 | +0 | gagné | fin | +241.13 $ | +794.08 $ |
| 13 | 07.10 00:18 | Up | 0.18 | 0.52 | 0.34 | 73 s | +0 | +0 | gagné | fin | +224.83 $ | +1018.91 $ |
| 14 | 07.10 00:22 | Down | 0.16 | 0.47 | 0.31 | 167 s | +0 | -0 | gagné | fin | +259.48 $ | +1278.39 $ |
| 15 | 07.10 00:26 | Up | 0.19 | 0.50 | 0.31 | 190 s | +0 | +0 | perdu | revendu | −33.26 $ | +1245.13 $ |
| 16 | 07.10 01:03 | Down | 0.20 | 0.51 | 0.31 | 95 s | +9 | +19 | gagné | fin | +197.12 $ | +1442.25 $ |
| 17 | 07.10 01:03 | Up | 0.18 | 0.49 | 0.31 | 72 s | +0 | +0 | perdu | fin | −52.95 $ | +1389.30 $ |
| 18 | 07.10 01:48 | Down | 0.16 | 0.47 | 0.31 | 99 s | +4 | +4 | perdu | fin | −53.02 $ | +1336.28 $ |
| 19 | 07.10 01:52 | Down | 0.19 | 0.49 | 0.30 | 122 s | -0 | -0 | gagné | fin | +210.24 $ | +1546.52 $ |
| 20 | 07.10 02:10 | Down | 0.16 | 0.47 | 0.31 | 280 s | +0 | +3 | perdu | revendu | −38.47 $ | +1508.05 $ |
| 21 | 07.10 02:32 | Up | 0.25 | 0.56 | 0.32 | 158 s | +0 | +0 | gagné | fin | +147.30 $ | +1655.35 $ |
| 22 | 07.10 02:57 | Down | 0.24 | 0.54 | 0.30 | 132 s | -0 | +0 | perdu | revendu | −31.29 $ | +1624.06 $ |
| 23 | 07.10 03:08 | Down | 0.15 | 0.46 | 0.31 | 111 s | -0 | -0 | perdu | fin | −53.06 $ | +1571.00 $ |
| 24 | 07.10 03:22 | Up | 0.17 | 0.49 | 0.32 | 178 s | +0 | +0 | perdu | revendu | −33.78 $ | +1537.22 $ |
| 25 | 07.10 03:48 | Down | 0.23 | 0.54 | 0.31 | 102 s | -0 | +0 | perdu | revendu | −48.73 $ | +1488.49 $ |
| 26 | 07.10 03:55 | Up | 0.26 | 0.57 | 0.31 | 268 s | +20 | +19 | perdu | revendu | −23.76 $ | +1464.73 $ |
| 27 | 07.10 04:00 | Up | 0.22 | 0.52 | 0.30 | 284 s | +0 | +0 | perdu | revendu | −16.48 $ | +1448.25 $ |
| 28 | 07.10 05:53 | Down | 0.22 | 0.52 | 0.30 | 98 s | -0 | -0 | perdu | fin | −52.81 $ | +1395.44 $ |
| 29 | 07.10 06:45 | Down | 0.26 | 0.58 | 0.32 | 261 s | +0 | +0 | perdu | revendu | −43.71 $ | +1351.73 $ |
| 30 | 07.10 07:11 | Down | 0.25 | 0.57 | 0.32 | 227 s | +0 | +0 | perdu | revendu | −26.43 $ | +1325.30 $ |
| 31 | 07.10 07:47 | Down | 0.17 | 0.48 | 0.31 | 143 s | -0 | -0 | perdu | revendu | −42.04 $ | +1283.26 $ |
| 32 | 07.10 07:51 | Down | 0.20 | 0.50 | 0.30 | 184 s | +0 | -0 | perdu | revendu | −31.85 $ | +1251.41 $ |
| 33 | 07.10 07:58 | Down | 0.17 | 0.56 | 0.39 | 63 s | +3 | +7 | perdu | fin | −52.99 $ | +1198.42 $ |
| 34 | 07.10 08:03 | Up | 0.19 | 0.51 | 0.32 | 78 s | +35 | +27 | perdu | fin | −52.92 $ | +1145.50 $ |
| 35 | 07.10 08:23 | Up | 0.16 | 0.55 | 0.39 | 75 s | +0 | +0 | gagné | fin | +259.48 $ | +1404.98 $ |
| 36 | 07.10 08:31 | Up | 0.16 | 0.48 | 0.32 | 205 s | +0 | +6 | gagné | fin | +259.48 $ | +1664.46 $ |
| 37 | 07.10 08:38 | Down | 0.17 | 0.52 | 0.35 | 102 s | +8 | +16 | perdu | fin | −52.99 $ | +1611.47 $ |
| 38 | 07.10 08:52 | Down | 0.19 | 0.53 | 0.34 | 138 s | +4 | +17 | gagné | fin | +210.24 $ | +1821.71 $ |
| 39 | 07.10 09:03 | Up | 0.21 | 0.52 | 0.31 | 103 s | +0 | +0 | perdu | revendu | −35.06 $ | +1786.65 $ |
| 40 | 07.10 09:38 | Down | 0.15 | 0.49 | 0.34 | 88 s | +11 | +17 | gagné | fin | +280.27 $ | +2066.92 $ |
| 41 | 07.10 10:23 | Down | 0.15 | 0.49 | 0.34 | 68 s | +30 | +25 | perdu | fin | −53.06 $ | +2013.86 $ |
| 42 | 07.10 11:06 | Down | 0.21 | 0.52 | 0.31 | 214 s | +10 | +32 | gagné | fin | +185.25 $ | +2199.11 $ |
| 43 | 07.10 11:23 | Up | 0.15 | 0.48 | 0.33 | 75 s | +0 | +0 | perdu | fin | −53.06 $ | +2146.05 $ |
| 44 | 07.10 11:25 | Down | 0.29 | 0.60 | 0.31 | 258 s | -0 | +0 | perdu | fin | −52.56 $ | +2093.49 $ |
| 45 | 07.10 11:32 | Down | 0.24 | 0.56 | 0.32 | 120 s | +0 | +0 | gagné | fin | +155.60 $ | +2249.09 $ |
| 46 | 07.10 11:38 | Down | 0.19 | 0.51 | 0.32 | 89 s | +0 | -0 | perdu | fin | −52.92 $ | +2196.17 $ |
| 47 | 07.10 11:41 | Up | 0.24 | 0.61 | 0.37 | 184 s | +31 | +29 | gagné | fin | +155.60 $ | +2351.77 $ |
| 48 | 07.10 11:58 | Down | 0.19 | 0.51 | 0.32 | 84 s | -0 | +2 | perdu | revendu | −45.57 $ | +2306.20 $ |
| 49 | 07.10 12:07 | Down | 0.17 | 0.48 | 0.31 | 180 s | +1 | +11 | perdu | fin | −52.99 $ | +2253.21 $ |
| 50 | 07.10 13:02 | Down | 0.16 | 0.50 | 0.34 | 139 s | +23 | +28 | gagné | fin | +259.48 $ | +2512.69 $ |
| 51 | 07.10 13:06 | Down | 0.21 | 0.54 | 0.33 | 213 s | +6 | +19 | perdu | revendu | −26.08 $ | +2486.61 $ |
| 52 | 07.10 13:28 | Up | 0.16 | 0.46 | 0.30 | 95 s | +0 | +0 | gagné | fin | +259.48 $ | +2746.09 $ |
| 53 | 07.10 14:53 | Down | 0.22 | 0.58 | 0.36 | 110 s | -0 | -0 | gagné | fin | +174.46 $ | +2920.55 $ |
| 54 | 07.10 18:26 | Up | 0.22 | 0.69 | 0.47 | 221 s | +11 | +11 | gagné | revendu | −9.97 $ | +2910.58 $ |
| 55 | 07.10 19:08 | Up | 0.15 | 0.47 | 0.32 | 108 s | +10 | +8 | perdu | fin | −53.06 $ | +2857.52 $ |
| 56 | 07.10 20:07 | Down | 0.21 | 0.54 | 0.33 | 140 s | +21 | +16 | gagné | fin | +185.25 $ | +3042.77 $ |
| 57 | 07.10 20:13 | Down | 0.17 | 0.47 | 0.30 | 75 s | +0 | +0 | perdu | fin | −52.99 $ | +2989.78 $ |
| 58 | 07.10 20:28 | Down | 0.15 | 0.51 | 0.36 | 74 s | +4 | +11 | perdu | fin | −53.06 $ | +2936.72 $ |
| 59 | 07.10 22:13 | Down | 0.16 | 0.52 | 0.35 | 94 s | +1 | +3 | perdu | fin | −53.02 $ | +2883.70 $ |
| 60 | 07.10 22:18 | Down | 0.18 | 0.49 | 0.31 | 76 s | +11 | +14 | perdu | revendu | +20.79 $ | +2904.49 $ |
| 61 | 07.10 22:18 | Up | 0.15 | 0.49 | 0.34 | 66 s | +4 | +23 | gagné | fin | +280.27 $ | +3184.76 $ |
| 62 | 07.10 22:28 | Up | 0.31 | 0.61 | 0.30 | 75 s | +0 | +0 | gagné | fin | +108.81 $ | +3293.57 $ |
| 63 | 07.10 23:48 | Up | 0.18 | 0.49 | 0.31 | 84 s | +0 | +0 | perdu | fin | −52.95 $ | +3240.62 $ |
| 64 | 08.10 00:08 | Down | 0.18 | 0.48 | 0.30 | 97 s | +4 | +4 | perdu | fin | −52.95 $ | +3187.67 $ |
| 65 | 08.10 00:13 | Down | 0.18 | 0.54 | 0.35 | 66 s | +14 | +14 | perdu | fin | −52.95 $ | +3134.72 $ |
| 66 | 08.10 00:27 | Down | 0.17 | 0.51 | 0.34 | 149 s | -0 | -0 | perdu | revendu | −50.26 $ | +3084.46 $ |
| 67 | 08.10 00:42 | Up | 0.17 | 0.52 | 0.35 | 161 s | +8 | +12 | gagné | fin | +241.13 $ | +3325.59 $ |
| 68 | 08.10 01:02 | Up | 0.15 | 0.46 | 0.31 | 158 s | +0 | +0 | perdu | fin | −53.06 $ | +3272.53 $ |
| 69 | 08.10 01:07 | Up | 0.18 | 0.48 | 0.30 | 161 s | +0 | +10 | perdu | revendu | −34.81 $ | +3237.72 $ |
| 70 | 08.10 01:13 | Up | 0.15 | 0.46 | 0.30 | 110 s | +11 | +15 | gagné | fin | +280.27 $ | +3517.99 $ |
| 71 | 08.10 01:30 | Down | 0.17 | 0.48 | 0.31 | 245 s | -0 | -0 | perdu | revendu | −28.25 $ | +3489.74 $ |
| 72 | 08.10 02:06 | Up | 0.18 | 0.51 | 0.33 | 189 s | +14 | +17 | perdu | fin | −52.95 $ | +3436.79 $ |
| 73 | 08.10 02:11 | Up | 0.18 | 0.48 | 0.30 | 216 s | +0 | +0 | perdu | revendu | −37.41 $ | +3399.38 $ |
| 74 | 08.10 02:33 | Up | 0.23 | 0.54 | 0.31 | 94 s | +0 | +0 | perdu | fin | −52.77 $ | +3346.61 $ |
| 75 | 08.10 02:38 | Up | 0.16 | 0.46 | 0.30 | 84 s | +0 | +0 | perdu | fin | −53.02 $ | +3293.59 $ |
| 76 | 08.10 04:28 | Up | 0.16 | 0.51 | 0.35 | 68 s | +2 | +12 | gagné | fin | +259.48 $ | +3553.07 $ |
| 77 | 08.10 04:38 | Down | 0.16 | 0.47 | 0.31 | 93 s | -0 | -0 | perdu | fin | −53.02 $ | +3500.05 $ |
| 78 | 08.10 06:18 | Down | 0.18 | 0.72 | 0.54 | 70 s | +57 | +72 | gagné | fin | +224.83 $ | +3724.88 $ |
| 79 | 08.10 06:42 | Up | 0.21 | 0.54 | 0.33 | 172 s | +0 | +0 | perdu | revendu | −43.98 $ | +3680.90 $ |
| 80 | 08.10 06:51 | Down | 0.32 | 0.67 | 0.35 | 218 s | +17 | +16 | perdu | revendu | −20.00 $ | +3660.90 $ |
| 81 | 08.10 07:18 | Down | 0.16 | 0.46 | 0.30 | 100 s | -0 | +3 | perdu | revendu | −32.61 $ | +3628.29 $ |
| 82 | 08.10 08:18 | Down | 0.23 | 0.54 | 0.31 | 74 s | -0 | -0 | gagné | fin | +164.62 $ | +3792.91 $ |
| 83 | 08.10 08:33 | Up | 0.20 | 0.51 | 0.31 | 88 s | +4 | +6 | perdu | revendu | −34.20 $ | +3758.71 $ |
| 84 | 08.10 08:56 | Down | 0.28 | 0.59 | 0.31 | 219 s | -0 | +0 | perdu | revendu | −45.94 $ | +3712.77 $ |
| 85 | 08.10 09:13 | Down | 0.21 | 0.51 | 0.30 | 109 s | -0 | +1 | perdu | revendu | −35.06 $ | +3677.71 $ |
| 86 | 08.10 10:03 | Up | 0.15 | 0.48 | 0.33 | 94 s | +4 | +7 | perdu | revendu | −43.76 $ | +3633.95 $ |
| 87 | 08.10 10:38 | Up | 0.17 | 0.52 | 0.35 | 101 s | +29 | +23 | perdu | fin | −52.99 $ | +3580.96 $ |
| 88 | 08.10 10:48 | Up | 0.16 | 0.48 | 0.32 | 84 s | +0 | +17 | gagné | fin | +259.48 $ | +3840.44 $ |
| 89 | 08.10 11:57 | Up | 0.15 | 0.47 | 0.32 | 145 s | +0 | +0 | gagné | fin | +280.27 $ | +4120.71 $ |
| 90 | 08.10 12:32 | Down | 0.21 | 0.51 | 0.30 | 139 s | +15 | +20 | gagné | fin | +185.25 $ | +4305.96 $ |
| 91 | 08.10 12:43 | Up | 0.15 | 0.50 | 0.35 | 82 s | +0 | +0 | gagné | revendu | +0.22 $ | +4306.18 $ |
| 92 | 08.10 13:13 | Up | 0.16 | 0.47 | 0.31 | 68 s | +0 | +0 | gagné | fin | +259.48 $ | +4565.66 $ |
| 93 | 08.10 13:27 | Up | 0.15 | 0.46 | 0.31 | 121 s | +9 | +15 | perdu | fin | −53.06 $ | +4512.60 $ |
| 94 | 08.10 13:52 | Down | 0.16 | 0.48 | 0.32 | 133 s | +13 | +15 | perdu | fin | −53.02 $ | +4459.58 $ |
| 95 | 08.10 14:12 | Up | 0.23 | 0.53 | 0.30 | 144 s | +8 | +20 | perdu | fin | −52.77 $ | +4406.81 $ |
| 96 | 08.10 14:21 | Down | 0.27 | 0.58 | 0.31 | 196 s | +4 | +5 | perdu | fin | −52.63 $ | +4354.18 $ |
| 97 | 08.10 15:30 | Up | 0.32 | 0.63 | 0.31 | 272 s | +16 | +29 | perdu | revendu | −3.37 $ | +4350.81 $ |
| 98 | 08.10 15:58 | Up | 0.19 | 0.50 | 0.31 | 118 s | +18 | +19 | gagné | fin | +210.24 $ | +4561.05 $ |
| 99 | 08.10 17:38 | Up | 0.17 | 0.63 | 0.46 | 63 s | +39 | +45 | perdu | revendu | −52.99 $ | +4508.06 $ |