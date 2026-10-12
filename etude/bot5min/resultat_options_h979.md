# Bot95 — H979 à H985 : options Deribit, CME, Coinbase, gamma des teneurs de marché, avance exécutable

Généré le 12.10.2026 13:19 UTC. Options Deribit : 192057 transactions (12.09 → 12.10 13:00 UTC). BTC Binance 1 s : 12.09 → 11.10. Apprentissage < 02.10, test 02.10 → 11.10 ; Dublin 11.10 → 12.10. Aucun ordre ; aucun abonnement ; période réservée non lue.

## 0. Audit des données

| Source | Disponible | Limite |
|---|---|---|
| Deribit options : transactions (instrument, côté preneur, prix, quantité, volatilité implicite) | oui, 30 jours, API publique gratuite | heure de l'échange seulement (pas de réception) ; environ 6 000 transactions par jour, soit une toutes les 14 s en moyenne |
| Deribit options : open interest par prix d'exercice, carnets d'options | **non** en historique | à enregistrer à partir de maintenant pour tester H981 |
| Deribit indice, perpétuel, DVOL | oui à Dublin depuis le 12.10 11:55 UTC | trop récent pour cette étude |
| Coinbase BTC/USD | prix et flux agressifs à Dublin depuis le 11.10 | carnet L2 non enregistré (gratuit et public, à ajouter si utile) |
| CME BTC / Micro BTC | **non** | fournisseur payant (Databento : historique à partir de 0,50 $/Go, 125 $ de crédit offert, temps réel dans les offres payantes) |
| Nasdaq, taux, dollar, or | **non** à la seconde | sources gratuites en bougies de 1 min seulement |

Transactions d'options par jour : médiane 6297, minimum 2121, maximum 15692.

## 1. H979 — Grosses transactions d'options : avance ou réaction ?

Grosse transaction = notionnel ≥ 1,250,604 $ (95e centile de l'apprentissage). Mouvement BTC Binance signé dans le sens delta du preneur (positif = la transaction « avait raison »), en $. « Avant » = 10 s précédant l'heure de disponibilité. Placebo = mêmes signes, instants décalés de 2 à 10 min. IC 90 % par jours.

| Échantillon | Catégorie | Événements | 10 s AVANT | 1 s | 2 s | 5 s | 10 s | 30 s | 60 s | Placebo 10 s |
|---|---|---|---|---|---|---|---|---|---|---|
| apprentissage | toutes les grosses transactions | 6782 | +4.09 [+3.28 ; +4.81] | +0.17 [+0.08 ; +0.27] | +0.28 [+0.13 ; +0.47] | +0.33 [-0.01 ; +0.73] | +0.70 [+0.31 ; +1.06] | +0.69 [-0.41 ; +1.67] | +0.60 [-0.30 ; +1.41] | -0.00 [-0.46 ; +0.42] |
| apprentissage | courtes (< 2 j) proches de la monnaie | 533 | +5.99 [+1.82 ; +9.97] | +0.11 [-0.40 ; +0.58] | +0.93 [+0.30 ; +1.65] | +2.05 [+0.60 ; +3.80] | +1.00 [-1.35 ; +3.88] | -0.40 [-4.20 ; +3.12] | +1.04 [-4.79 ; +7.12] | +1.14 [-0.53 ; +2.93] |
| apprentissage | blocs | 3164 | +0.05 [-0.31 ; +0.41] | +0.04 [-0.08 ; +0.14] | -0.03 [-0.18 ; +0.10] | -0.02 [-0.26 ; +0.19] | +0.28 [-0.10 ; +0.63] | +0.20 [-0.79 ; +1.10] | +0.23 [-0.98 ; +1.29] | -0.71 [-1.50 ; +0.13] |
| test | toutes les grosses transactions | 3044 | +6.40 [+4.32 ; +7.81] | -0.05 [-0.23 ; +0.18] | +0.31 [-0.00 ; +0.69] | +0.06 [-0.64 ; +1.01] | +0.68 [-0.60 ; +2.36] | +1.36 [+0.52 ; +2.33] | +0.51 [-1.18 ; +2.27] | +0.22 [-0.69 ; +1.25] |
| test | courtes (< 2 j) proches de la monnaie | 193 | +15.08 [+3.62 ; +20.91] | -2.01 [-3.40 ; +0.60] | -0.84 [-4.06 ; +2.69] | -3.14 [-7.26 ; +2.34] | +1.25 [-0.29 ; +2.67] | +5.32 [+2.68 ; +8.90] | +8.63 [-1.53 ; +18.76] | -0.23 [-1.33 ; +1.64] |
| test | blocs | 1066 | -0.36 [-0.60 ; -0.07] | +0.02 [-0.15 ; +0.18] | +0.03 [-0.19 ; +0.21] | -0.09 [-0.34 ; +0.15] | -0.28 [-0.69 ; +0.15] | +0.32 [-0.06 ; +0.62] | +1.45 [+0.08 ; +2.78] | +0.62 [-0.92 ; +1.81] |

## 2. H980 — Le flux delta des options ajoute-t-il de l'information à l'OFI, au momentum et à la volatilité BTC ?

517588 instants (toutes les 5 s, 30 jours). IC corrigé : 4 cibles.

| Cible | AUC A (BTC seul) | AUC B (+ flux delta options) | ΔAUC | IC 90 % | IC corrigé |
|---|---|---|---|---|---|
| hausse BTC à 5 s | 0.6101 | 0.6098 | -0.0002 | [-0.0006 ; +0.0000] | [-0.0006 ; +0.0001] |
| hausse BTC à 10 s | 0.6146 | 0.6144 | -0.0002 | [-0.0007 ; +0.0003] | [-0.0009 ; +0.0005] |
| hausse BTC à 30 s | 0.5878 | 0.5873 | -0.0005 | [-0.0017 ; +0.0007] | [-0.0020 ; +0.0011] |
| hausse BTC à 60 s | 0.5590 | 0.5576 | -0.0015 | [-0.0028 ; +0.0001] | [-0.0032 ; +0.0003] |

Règlement (substitut Binance, 11512 décisions de test) : Brier règlement seul 0.1353, avec flux delta 0.1352, gain +0.00000 [-0.00001 ; +0.00002].

## 3. H979 / H985 — Après une grosse transaction d'options : perp, spot, Polymarket, règlement, exécution (Dublin)

190 grosses transactions d'options pendant les cycles enregistrés à Dublin (disponibilité supposée 100 ms après l'heure de l'échange).

| Mesure | Valeur (IC 90 % par cycles) |
|---|---|
| BTC spot, 10 s AVANT (signé) | +5.97 [+1.56 ; +11.58] $ |
| perp Bybit à 100 ms | +0.05 [-0.21 ; +0.29] $ |
| perp Bybit à 250 ms | +0.82 [+0.02 ; +2.04] $ |
| perp Bybit à 500 ms | +1.58 [+0.13 ; +3.94] $ |
| perp Bybit à 1000 ms | +1.77 [-0.08 ; +4.62] $ |
| perp Bybit à 2000 ms | +0.86 [-0.63 ; +2.93] $ |
| Binance spot à 100 ms | +0.15 [+0.00 ; +0.39] $ |
| Binance spot à 250 ms | +0.31 [+0.02 ; +0.72] $ |
| Binance spot à 500 ms | +0.52 [+0.02 ; +1.17] $ |
| Binance spot à 1000 ms | +0.73 [-0.05 ; +1.73] $ |
| Binance spot à 2000 ms | +0.98 [-0.14 ; +2.42] $ |
| Polymarket +1 c dans le sens, en 5 s | 47 % des cas, délai médian 750 ms |
| Règlement officiel − M0 (signé) | +0.05 [+0.01 ; +0.10] |
| Achat 20 $ du jeton dans le sens à 164 ms, conservé | -177 $ sur 125 achats [-689 ; +496], 64 gagnants |

## 4. H983 — Coinbase BTC/USD précède-t-il Binance ? (Dublin)

| Cible | Échantillon | AUC Binance seul | AUC + Coinbase | ΔAUC (IC 90 %) |
|---|---|---|---|---|
| hausse Binance à 5 s | validation | 0.614 | 0.625 | +0.011 [+0.008 ; +0.014] |
| hausse Binance à 5 s | test | 0.613 | 0.622 | +0.009 [+0.005 ; +0.013] |
| hausse Binance à 30 s | validation | 0.585 | 0.593 | +0.008 [+0.005 ; +0.010] |
| hausse Binance à 30 s | test | 0.601 | 0.601 | +0.000 [-0.003 ; +0.004] |

## 5. H981, H982, H984
- **H981 gamma des teneurs de marché** : non testable — l'open interest par prix d'exercice n'existe pas en historique gratuit. Il faudrait l'enregistrer (Deribit, gratuit, toutes les minutes) à partir de maintenant.
- **H982 CME** : non testable sans abonnement (voir l'audit).
- **H984 combinaison** : construite seulement si un instrument a une valeur individuelle démontrée (voir verdicts).

_Calcul : 215 s._
