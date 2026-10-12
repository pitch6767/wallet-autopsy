# Bot95 — état complet au 10.10 11:24 (heure suisse)

**Bot :** Polymarket, marchés BTC et ETH Up/Down de 5 minutes. **Mode fantôme uniquement** (aucun argent réel ; MODE_REEL = non). Achats simulés au meilleur vendeur, limités à la quantité affichée, frais compris, 50 $ maximum par achat.

**Règlement officiel (reconstruit) :** prix à battre = moyenne Chainlink des 60 s avant le début du cycle ; prix final = moyenne Chainlink des 60 dernières secondes. Le bot calcule son prix à battre ainsi depuis le 09.10.

Colonnes : trades, gagnés, résultat net, creux maximal (pire baisse depuis un sommet), plus longue série de pertes, date de démarrage du fantôme.

## Stratégies actives — BTC (37)

| Stratégie | Depuis | Trades | Gagnés | Résultat | Creux | Pertes de suite |
|---|---|---|---|---|---|---|
| V2-D perp 120-269 s | 07.10 13:46 | 522 | 123 (24 %) | **+2 941 $** | −2 205 $ | 23 |
| desaccord 30 zone + modele monte | 08.10 09:03 | 124 | 43 (35 %) | **+2 743 $** | −363 $ | 7 |
| V2-G jury des bourses | 07.10 13:46 | 664 | 147 (22 %) | **+2 664 $** | −1 332 $ | 23 |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50 | 08.10 18:59 | 136 | 39 (29 %) | **+1 873 $** | −460 $ | 18 |
| desaccord 30 zone + Binance et perp + sortie modele -10 | 08.10 09:03 | 176 | 51 (29 %) | **+1 811 $** | −803 $ | 20 |
| desaccord 20 sans nuit | 07.10 18:03 | 412 | 98 (24 %) | **+1 756 $** | −1 840 $ | 21 |
| V2-C perp | 07.10 13:46 | 714 | 156 (22 %) | **+1 724 $** | −2 473 $ | 26 |
| desaccord 30 zone 0,15-0,35 + Binance et perp | 08.10 08:40 | 177 | 50 (28 %) | **+1 679 $** | −865 $ | 20 |
| V2-H veto complet | 07.10 13:46 | 707 | 162 (23 %) | **+1 672 $** | −2 688 $ | 27 |
| V2-F ecart qui grandit | 07.10 13:46 | 726 | 163 (22 %) | **+1 650 $** | −2 827 $ | 27 |
| desaccord 30 0,15-0,60 + perp + ecart qui grandit | 08.10 09:03 | 178 | 51 (29 %) | **+1 551 $** | −849 $ | 19 |
| desaccord 30 zone + sortie modele -10 | 08.10 09:03 | 206 | 51 (25 %) | **+1 450 $** | −575 $ | 12 |
| V2-B hors 60-89 s | 07.10 13:46 | 729 | 166 (23 %) | **+1 435 $** | −2 736 $ | 27 |
| desaccord 30 zone 0,15-0,35 | 08.10 08:40 | 207 | 55 (27 %) | **+1 368 $** | −637 $ | 12 |
| desaccord 20 Binance avec nous | 07.10 22:07 | 87 | 27 (31 %) | **+1 351 $** | −666 $ | 8 |
| desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse | 08.10 18:42 | 137 | 39 (28 %) | **+1 289 $** | −841 $ | 18 |
| desaccord 20 Binance ou perp avec nous | 07.10 21:34 | 178 | 47 (26 %) | **+1 069 $** | −879 $ | 10 |
| desaccord 20 Binance avec nous sans nuit | 07.10 22:07 | 65 | 20 (31 %) | **+855 $** | −617 $ | 8 |
| corrige : zone + Binance et perp + sortie -10 | 09.10 08:54 | 71 | 17 (24 %) | **+254 $** | −423 $ | 11 |
| desaccord 20 Poly rejoint 10 s sans nuit | 07.10 19:38 | 131 | 49 (37 %) | **+209 $** | −649 $ | 6 |
| desaccord 20 Binance ou perp avec nous sans nuit | 07.10 21:34 | 124 | 31 (25 %) | **+117 $** | −849 $ | 13 |
| corrige : V2-F ecart qui grandit | 09.10 08:54 | 226 | 76 (34 %) | **+18 $** | −1 495 $ | 10 |
| TWAP fin | 09.10 23:59 | 43 | 12 (28 %) | **−49 $** | −379 $ | 7 |
| TWAP fin anti-saut | 10.10 09:07 | 8 | 1 (12 %) | **−134 $** | −282 $ | 7 |
| TWAP fin confirme Chainlink 0,5 s | 10.10 09:49 | 6 | 0 (0 %) | **−183 $** | −183 $ | 6 |
| TWAP fin prevision Chainlink | 10.10 09:07 | 8 | 3 (38 %) | **−192 $** | −214 $ | 4 |
| TWAP fin correction spot-perp | 10.10 00:51 | 35 | 16 (46 %) | **−265 $** | −344 $ | 5 |
| corrige marge mesuree : V2-F | 09.10 23:06 | 114 | 42 (37 %) | **−282 $** | −804 $ | 8 |
| corrige : V2-F + pas les deux baissent | 09.10 08:54 | 222 | 72 (32 %) | **−360 $** | −1 910 $ | 11 |
| V2-F + plus de 120 s | 09.10 08:32 | 236 | 51 (22 %) | **−361 $** | −1 783 $ | 12 |
| TWAP fin quantiles | 10.10 09:49 | 8 | 0 (0 %) | **−372 $** | −372 $ | 8 |
| desaccord confirme perp | 07.10 13:40 | 149 | 46 (31 %) | **−416 $** | −1 093 $ | 11 |
| corrige : desaccord 20 | 09.10 08:54 | 229 | 76 (33 %) | **−449 $** | −1 657 $ | 10 |
| TWAP fin sauts | 10.10 00:51 | 33 | 8 (24 %) | **−556 $** | −601 $ | 7 |
| corrige : V2-F + garde-fou | 09.10 23:06 | 119 | 35 (29 %) | **−892 $** | −1 451 $ | 10 |
| V2-E persistant | 07.10 13:46 | 655 | 116 (18 %) | **−2 066 $** | −3 671 $ | 31 |
| V2-F + pas les deux baissent | 09.10 08:27 | 290 | 58 (20 %) | **−2 407 $** | −3 344 $ | 15 |

## Stratégies actives — ETH (14)

| Stratégie | Depuis | Trades | Gagnés | Résultat | Creux | Pertes de suite |
|---|---|---|---|---|---|---|
| desaccord confirme perp | 07.10 13:30 | 5 | 3 (60 %) | **+120 $** | −61 $ | 2 |
| V2-D perp 120-269 s | 07.10 14:35 | 2 | 0 (0 %) | **−11 $** | −11 $ | 2 |
| corrige marge mesuree : V2-F | 09.10 23:07 | 103 | 34 (33 %) | **−56 $** | −788 $ | 16 |
| corrige : zone + Binance et perp + sortie -10 | 09.10 21:01 | 24 | 5 (21 %) | **−95 $** | −164 $ | 13 |
| V2-F ecart qui grandit | 07.10 13:50 | 11 | 1 (9 %) | **−103 $** | −103 $ | 5 |
| V2-G jury des bourses | 07.10 13:50 | 10 | 0 (0 %) | **−133 $** | −133 $ | 10 |
| V2-B hors 60-89 s | 07.10 13:50 | 11 | 2 (18 %) | **−184 $** | −207 $ | 5 |
| V2-C perp | 07.10 13:50 | 11 | 1 (9 %) | **−239 $** | −239 $ | 5 |
| V2-H veto complet | 07.10 13:50 | 11 | 1 (9 %) | **−292 $** | −316 $ | 10 |
| corrige : V2-F + garde-fou | 09.10 23:07 | 101 | 32 (32 %) | **−295 $** | −812 $ | 14 |
| V2-E persistant | 07.10 13:50 | 10 | 0 (0 %) | **−329 $** | −329 $ | 10 |
| corrige : V2-F ecart qui grandit | 09.10 20:37 | 119 | 38 (32 %) | **−592 $** | −870 $ | 14 |
| corrige : desaccord 20 | 09.10 20:37 | 122 | 38 (31 %) | **−638 $** | −886 $ | 14 |
| corrige : V2-F + pas les deux baissent | 09.10 20:37 | 116 | 34 (29 %) | **−775 $** | −1 076 $ | 14 |

## Description de chaque stratégie active

**desaccord 20 sans nuit** — Désaccord 20 SANS LA NUIT : exactement comme Désaccord 20, mais aucun achat entre 00h et 08h (heure suisse).

**desaccord confirme perp** — Désaccord CONFIRMÉ + PERP : pareil, et en plus le perp Bybit doit aller dans notre sens sur les 5 dernières secondes.

**V2-B hors 60-89 s** — V2-B : désaccord 20, sauf entre 60 et 89 s de la fin.

**V2-C perp** — V2-C : désaccord 20 seulement si le perp Bybit va dans notre sens sur 5 s.

**V2-D perp 120-269 s** — V2-D : désaccord 20 + perp avec nous + entre 120 et 269 s de la fin.

**V2-E persistant** — V2-E : désaccord 20 seulement s'il tient au moins 1,5 s (pas un éclair).

**V2-F ecart qui grandit** — V2-F : désaccord 20 seulement si l'écart a grandi d'au moins 3 pts sur 3 s.

**V2-F + pas les deux baissent** — V2-F SANS « LES DEUX BAISSENT » : comme V2-F, mais pas d'achat quand, sur les 3 s, le modèle ET le prix Polymarket ont baissé et que Polymarket a baissé plus fort (16 % de gagnants seulement dans l'historique).

**V2-F + plus de 120 s** — V2-F + PLUS DE 120 S : comme V2-F, mais seulement s'il reste au moins 120 secondes dans le cycle (les achats de fin de cycle perdent).

**V2-G jury des bourses** — V2-G : désaccord 20 seulement si Bybit, OKX, Binance et Coinbase vont tous dans notre sens sur 3 s ET que Polymarket a moins suivi que le modèle (en retard).

**V2-H veto complet** — V2-H : désaccord 20 sauf veto : écart qui fond, Binance contre nous, Bybit+OKX contre nous, 60-89 s, Polymarket déjà en train de corriger, vendeur < 20 parts.

**desaccord 20 Poly rejoint 10 s sans nuit** — Désaccord 20 POLY REJOINT 10 s SANS LA NUIT : comme « Poly rejoint 10 s », aucun achat entre 00h et 08h (heure suisse).

**desaccord 20 Binance avec nous** — Désaccord 20 + BINANCE AVEC NOUS : modèle ≥ meilleur vendeur + 20 pts ET Binance a bougé dans notre sens sur les 3 s avant → achat immédiat 50 $, garde jusqu'à la fin.

**desaccord 20 Binance avec nous sans nuit** — Désaccord 20 + BINANCE AVEC NOUS : modèle ≥ meilleur vendeur + 20 pts ET Binance a bougé dans notre sens sur les 3 s avant → achat immédiat 50 $, garde jusqu'à la fin. SANS LA NUIT : aucun achat entre 00h et 08h (heure suisse).

**desaccord 20 Binance ou perp avec nous** — Désaccord 20 + BINANCE OU PERP AVEC NOUS : pareil, il suffit que Binance OU le perp Bybit ait bougé dans notre sens sur 3 s.

**desaccord 20 Binance ou perp avec nous sans nuit** — Désaccord 20 + BINANCE OU PERP AVEC NOUS : pareil, il suffit que Binance OU le perp Bybit ait bougé dans notre sens sur 3 s. SANS LA NUIT : aucun achat entre 00h et 08h (heure suisse).

**desaccord 30 zone 0,15-0,35** — Désaccord 30 ZONE 0,15-0,35 : modèle ≥ meilleur vendeur + 30 pts, jeton vendu entre 0,15 et 0,35 $, plus de 60 s restantes → achat 50 $, garde jusqu'à la fin. Zone robuste trouvée le 08.10 (positive sur les 4 quarts des 48 h).

**desaccord 30 zone 0,15-0,35 + Binance et perp** — Désaccord 30 ZONE 0,15-0,35 + BINANCE ET PERP : pareil, et Binance et le perp Bybit ne vont pas contre nous sur les 3 s avant.

**desaccord 30 zone + sortie modele -10** — ZONE + SORTIE MODÈLE -10 : comme Désaccord 30 zone 0,15-0,35, mais on revend au meilleur acheteur dès que le modèle a perdu 10 pts par rapport à l'entrée.

**desaccord 30 zone + Binance et perp + sortie modele -10** — ZONE + BINANCE ET PERP + SORTIE MODÈLE -10 : zone, Binance et perp pas contre nous sur 3 s, et revente si le modèle perd 10 pts.

**desaccord 30 0,15-0,60 + perp + ecart qui grandit** — DÉSACCORD 30 LARGE + PERP + ÉCART QUI GRANDIT : écart >= 30 pts, jeton entre 0,15 et 0,60 $, plus de 60 s, perp pas contre nous sur 3 s et écart plus grand qu'il y a 3 s. Garde jusqu'à la fin.

**desaccord 30 zone + modele monte** — ZONE + LE MODÈLE A MONTÉ : zone (écart >= 30 pts, 0,15-0,35 $, > 60 s) et le désaccord vient du modèle qui a monté d'au moins 3 pts sur les 3 dernières secondes (le BTC a bougé, Polymarket pas encore). Garde jusqu'à la fin.

**desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse** — ZONE + BINANCE ET PERP + SORTIE -10 + PAS « POLYMARKET QUI BAISSE » : comme zone + Binance et perp + sortie -10, mais on n'achète pas si le désaccord vient d'un vendeur Polymarket qui a baissé son prix d'au moins 3 c en 3 s sans que le modèle monte. Revente plafonnée (jamais sous 0,05 $ ni 2 c sous le meilleur acheteur).

**desaccord 30 zone + Binance et perp + sortie modele -10 + pas Poly qui baisse + taille 25/50** — COMBINÉ : zone + Binance et perp + sortie -10 + pas « Polymarket qui baisse », et mise de 25 $ seulement si le modèle n'a pas monté d'au moins 3 pts dans les 3 s avant (50 $ sinon).

**corrige : V2-F + garde-fou** — V2-F avec le modèle corrigé (0,015 %), mais pas d'achat si le BTC est à moins de 20 $ du prix à battre ET si notre côté coûte 5 cents ou moins (le carnet sait probablement mieux que nous).

**TWAP fin** — TWAP FIN : moteur de règlement exact (prix à battre = moyenne Chainlink des 60 s avant le début ; fin = moyenne des 60 dernières secondes). Achat si sa probabilité dépasse le prix de 20 pts, entre 90 et 20 s de la fin, 50 $ au meilleur vendeur seulement, gardé jusqu'au règlement.

**TWAP fin sauts** — TWAP FIN SAUTS : comme TWAP fin, mais la probabilité suppose des mouvements avec sauts (loi de Student) au lieu d'une courbe en cloche.

**TWAP fin correction spot-perp** — TWAP FIN CORRECTION SPOT-PERP : comme TWAP fin, mais la moyenne finale prévue est corrigée de l'écart Binance/Coinbase − perp (Chainlink suit un peu plus le spot).

**TWAP fin confirme Chainlink 0,5 s** — TWAP FIN CONFIRMÉ CHAINLINK (règle corrigée le 10.10) : au premier signal TWAP fin du cycle (probabilité − vendeur ≥ 0,20, entre 90 et 20 s), on n'achète pas tout de suite : on attend la première NOUVELLE VALEUR Chainlink reçue au moins 0,5 s après le signal (l'ancienne version acceptait un message arrivé 30 ms après, sans changement réel), on recalcule ; si l'avantage est encore ≥ 0,20 → achat 50 $ au meilleur vendeur (quantité affichée), gardé jusqu'au règlement ; sinon le signal est abandonné (tous les signaux sont gardés sur /api/twap_confirme).

**TWAP fin anti-saut** — TWAP FIN ANTI-SAUT (10.10) : comme TWAP fin, mais un saut du prix rapide (Bybit/OKX) sur 2 s n'est pris en compte que si un autre exchange (OKX, Binance ou Coinbase) le confirme ; sinon le moteur garde le prix d'il y a 2 s. Évite les cas de 05:19 (saut de Bybit seul).

**TWAP fin prevision Chainlink** — TWAP FIN PRÉVISION CHAINLINK (10.10) : comme TWAP fin, mais les prix Chainlink encore à venir sont prévus à partir du dernier Chainlink + 0,98 × l'écart avec la médiane des 4 exchanges (Bybit, OKX, Binance, Coinbase), au lieu de prolonger le dernier prix Bybit.

**TWAP fin quantiles** — TWAP FIN QUANTILES (10.10) : même moyenne prévue que TWAP fin, mais la probabilité est lue dans la distribution réelle des erreurs passées du moteur (par tranche de temps et selon que le marché est calme ou agité), au lieu d'une courbe en cloche. Corrige l'excès de confiance en marché calme et l'excès de prudence en marché agité. Tables figées, apprises avant le 08.10 21:55.

**corrige marge mesuree : V2-F** — V2-F avec une marge d'erreur MESURÉE : écart réel entre notre prix à battre / notre Chainlink et les valeurs officielles du règlement, recalculé sur les 50 derniers cycles (12 $ au départ).

**corrige : desaccord 20** — MODÈLE CORRIGÉ — DÉSACCORD 20 : comme désaccord 20, mais avec la probabilité du modèle corrigé (marge d'incertitude 0,015 % au lieu de 0,08 %, qui gonflait les chances des outsiders).

**corrige : V2-F ecart qui grandit** — MODÈLE CORRIGÉ — V2-F : désaccord 20 qui grandit d'au moins 3 pts en 3 s, calculé avec le modèle corrigé.

**corrige : V2-F + pas les deux baissent** — MODÈLE CORRIGÉ — V2-F sans « les deux baissent, Polymarket plus fort ».

**corrige : zone + Binance et perp + sortie -10** — MODÈLE CORRIGÉ — ZONE : écart >= 30 pts, jeton 0,15-0,35 $, > 60 s, Binance et perp pas contre nous ; revente (plancher 0,05 $) si le modèle corrigé perd 10 pts.

## Détail des trades des nouveaux fantômes (BTC)

### TWAP fin — 43 trades, résultat −49 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 09.10 23:53 | Up | 0.2842 | 5 | 0.475 | 82 s | Down | −1 $ |
| 09.10 23:59 | Up | 0.6664 | 76.92 | 0.932 | 58 s | Up | +26 $ |
| 10.10 00:23 | Down | 0.1697 | 312.5 | 0.525 | 82 s | Down | +259 $ |
| 10.10 00:43 | Down | 0.528 | 98.04 | 0.728 | 79 s | Down | +46 $ |
| 10.10 00:48 | Down | 0.5479 | 94.34 | 0.73 | 87 s | Up | −52 $ |
| 10.10 00:53 | Up | 0.7442 | 18 | 0.937 | 84 s | Up | +5 $ |
| 10.10 01:03 | Up | 0.1906 | 25 | 0.408 | 76 s | Down | −5 $ |
| 10.10 01:08 | Up | 0.8019 | 63.29 | 0.994 | 76 s | Up | +13 $ |
| 10.10 01:13 | Up | 0.6468 | 9.62 | 0.834 | 73 s | Down | −6 $ |
| 10.10 01:33 | Down | 0.2115 | 6 | 0.572 | 77 s | Up | −1 $ |
| 10.10 01:58 | Down | 0.7248 | 70.42 | 0.916 | 62 s | Down | +19 $ |
| 10.10 02:03 | Up | 0.1697 | 6 | 0.371 | 71 s | Down | −1 $ |
| 10.10 02:18 | Up | 0.1487 | 38.89 | 0.343 | 75 s | Down | −6 $ |
| 10.10 02:28 | Up | 0.6074 | 84.75 | 0.808 | 81 s | Up | +33 $ |
| 10.10 02:43 | Up | 0.7924 | 5 | 0.981 | 87 s | Down | −4 $ |
| 10.10 02:48 | Down | 0.4173 | 125 | 0.803 | 62 s | Up | −52 $ |
| 10.10 03:03 | Down | 0.2428 | 217.39 | 0.459 | 89 s | Up | −53 $ |
| 10.10 03:08 | Down | 0.2428 | 5 | 0.434 | 84 s | Up | −1 $ |
| 10.10 03:59 | Up | 0.7828 | 64.94 | 0.99 | 60 s | Up | +14 $ |
| 10.10 04:08 | Up | 0.1381 | 5.33 | 0.34 | 88 s | Down | −1 $ |
| 10.10 04:13 | Down | 0.3254 | 25 | 0.61 | 65 s | Down | +17 $ |
| 10.10 04:28 | Up | 0.2115 | 50 | 0.483 | 90 s | Down | −11 $ |
| 10.10 04:49 | Up | 0.4678 | 45 | 0.655 | 56 s | Down | −21 $ |
| 10.10 04:53 | Down | 0.2011 | 263.16 | 0.398 | 89 s | Up | −53 $ |
| 10.10 05:04 | Down | 0.117 | 14 | 0.377 | 59 s | Down | +12 $ |
| 10.10 05:19 | Up | 0.0321 | 427.99 | 0.995 | 48 s | Down | −14 $ |
| 10.10 05:34 | Up | 0.2945 | 38.31 | 0.481 | 56 s | Down | −11 $ |
| 10.10 05:43 | Up | 0.2219 | 20 | 0.415 | 81 s | Down | −4 $ |
| 10.10 06:13 | Down | 0.3766 | 10 | 0.562 | 64 s | Up | −4 $ |
| 10.10 06:29 | Down | 0.3664 | 142.86 | 0.964 | 37 s | Up | −52 $ |
| 10.10 06:53 | Up | 0.4779 | 29.95 | 0.985 | 89 s | Up | +16 $ |
| 10.10 07:23 | Up | 0.1906 | 5 | 0.736 | 90 s | Down | −1 $ |
| 10.10 07:29 | Up | 0.0321 | 189 | 0.452 | 51 s | Down | −6 $ |
| 10.10 07:43 | Down | 0.1381 | 96.23 | 0.333 | 83 s | Up | −13 $ |
| 10.10 07:54 | Down | 0.2635 | 5 | 0.45 | 57 s | Up | −1 $ |
| 10.10 09:03 | Up | 0.2635 | 200 | 0.456 | 90 s | Up | +147 $ |
| 10.10 09:43 | Down | 0.0214 | 365.32 | 0.484 | 68 s | Up | −8 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.918 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.1802 | 294.12 | 0.484 | 89 s | Up | −53 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.928 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.999 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 1 | 68 s | Up | −51 $ |
| 10.10 10:38 | Down | 0.6566 | 20 | 0.848 | 65 s | Up | −13 $ |

### TWAP fin quantiles — 8 trades, résultat −372 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 09:43 | Down | 0.0214 | 365.32 | 0.575 | 68 s | Up | −8 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.935 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.1802 | 294.12 | 0.575 | 89 s | Up | −53 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.939 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.999 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 0.999 | 68 s | Up | −51 $ |
| 10.10 10:33 | Down | 0.3357 | 156.25 | 0.537 | 90 s | Up | −52 $ |
| 10.10 10:38 | Down | 0.6468 | 79.37 | 0.846 | 88 s | Up | −51 $ |

### TWAP fin anti-saut — 8 trades, résultat −134 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 09:03 | Up | 0.2635 | 200 | 0.456 | 90 s | Up | +147 $ |
| 10.10 09:43 | Down | 0.0214 | 365.32 | 0.484 | 68 s | Up | −8 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.918 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.1802 | 294.12 | 0.484 | 89 s | Up | −53 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.928 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.999 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 1 | 68 s | Up | −51 $ |
| 10.10 10:38 | Down | 0.6566 | 20 | 0.848 | 65 s | Up | −13 $ |

### TWAP fin prevision Chainlink — 8 trades, résultat −192 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 09:03 | Up | 0.1906 | 8 | 0.386 | 79 s | Up | +6 $ |
| 10.10 09:43 | Up | 0.7345 | 60 | 0.943 | 66 s | Up | +16 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.887 | 67 s | Up | −52 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.929 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.999 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 1 | 68 s | Up | −51 $ |
| 10.10 10:33 | Up | 0.7054 | 20 | 0.898 | 76 s | Up | +6 $ |
| 10.10 10:38 | Down | 0.637 | 20 | 0.823 | 65 s | Up | −13 $ |

### TWAP fin confirme Chainlink 0,5 s — 6 trades, résultat −183 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 09:43 | Down | 0.0214 | 330.32 | 0.478 | 66 s | Up | −7 $ |
| 10.10 09:53 | Down | 0.4879 | 106.38 | 0.918 | 66 s | Up | −52 $ |
| 10.10 10:13 | Down | 0.3868 | 129.53 | 0.931 | 68 s | Up | −50 $ |
| 10.10 10:18 | Down | 0.3868 | 100.11 | 0.999 | 62 s | Up | −39 $ |
| 10.10 10:23 | Down | 0.538 | 25.67 | 1 | 68 s | Up | −14 $ |
| 10.10 10:38 | Down | 0.6271 | 34 | 0.816 | 65 s | Up | −21 $ |

### TWAP fin sauts — 33 trades, résultat −556 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 00:43 | Down | 0.538 | 96.15 | 0.771 | 83 s | Down | +44 $ |
| 10.10 00:48 | Down | 0.5678 | 79.38 | 0.776 | 90 s | Up | −45 $ |
| 10.10 00:53 | Up | 0.7151 | 71.43 | 0.921 | 90 s | Up | +20 $ |
| 10.10 01:03 | Up | 0.1906 | 30 | 0.61 | 76 s | Down | −6 $ |
| 10.10 01:13 | Up | 0.6468 | 9.62 | 0.879 | 73 s | Down | −6 $ |
| 10.10 01:33 | Down | 0.2115 | 6 | 0.595 | 77 s | Up | −1 $ |
| 10.10 01:58 | Down | 0.7345 | 18.43 | 0.939 | 62 s | Down | +5 $ |
| 10.10 02:28 | Up | 0.6664 | 76.92 | 0.851 | 86 s | Up | +26 $ |
| 10.10 02:44 | Up | 0.4173 | 125 | 0.992 | 58 s | Down | −52 $ |
| 10.10 02:48 | Down | 0.4173 | 125 | 0.852 | 62 s | Up | −52 $ |
| 10.10 03:03 | Down | 0.2428 | 217.39 | 0.445 | 89 s | Up | −53 $ |
| 10.10 03:59 | Up | 0.7828 | 64.94 | 0.985 | 60 s | Up | +14 $ |
| 10.10 04:13 | Up | 0.6566 | 78.13 | 0.85 | 71 s | Down | −51 $ |
| 10.10 04:28 | Up | 0.2115 | 50 | 0.478 | 90 s | Down | −11 $ |
| 10.10 04:49 | Up | 0.528 | 98.04 | 0.712 | 57 s | Down | −52 $ |
| 10.10 05:04 | Down | 0.117 | 14 | 0.34 | 59 s | Down | +12 $ |
| 10.10 05:19 | Up | 0.0321 | 427.99 | 0.989 | 48 s | Down | −14 $ |
| 10.10 05:34 | Up | 0.2739 | 30 | 0.475 | 56 s | Down | −8 $ |
| 10.10 05:43 | Up | 0.1906 | 28 | 0.384 | 74 s | Down | −5 $ |
| 10.10 06:13 | Down | 0.3766 | 10 | 0.582 | 64 s | Up | −4 $ |
| 10.10 06:29 | Down | 0.3664 | 142.86 | 0.968 | 37 s | Up | −52 $ |
| 10.10 06:53 | Up | 0.4779 | 29.95 | 0.981 | 89 s | Up | +16 $ |
| 10.10 07:23 | Up | 0.1906 | 5 | 0.789 | 90 s | Down | −1 $ |
| 10.10 07:29 | Up | 0.0321 | 189 | 0.436 | 51 s | Down | −6 $ |
| 10.10 07:54 | Down | 0.2428 | 5 | 0.434 | 56 s | Up | −1 $ |
| 10.10 09:03 | Up | 0.2531 | 11.57 | 0.441 | 90 s | Up | +9 $ |
| 10.10 09:43 | Down | 0.0214 | 365.32 | 0.478 | 68 s | Up | −8 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.94 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.1802 | 294.12 | 0.479 | 89 s | Up | −53 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.946 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.995 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 0.998 | 68 s | Up | −51 $ |
| 10.10 10:38 | Down | 0.6762 | 20 | 0.867 | 79 s | Up | −14 $ |

### TWAP fin correction spot-perp — 35 trades, résultat −265 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 00:43 | Down | 0.528 | 98.04 | 0.712 | 79 s | Down | +46 $ |
| 10.10 00:48 | Down | 0.4678 | 22.6 | 0.653 | 70 s | Up | −11 $ |
| 10.10 00:53 | Up | 0.7442 | 18 | 0.97 | 84 s | Up | +5 $ |
| 10.10 01:03 | Down | 0.4879 | 75 | 0.722 | 76 s | Down | +38 $ |
| 10.10 01:08 | Down | 0.1592 | 5 | 0.356 | 76 s | Up | −1 $ |
| 10.10 01:13 | Up | 0.6271 | 38.46 | 0.825 | 73 s | Down | −24 $ |
| 10.10 01:33 | Down | 0.2115 | 250 | 0.404 | 69 s | Up | −53 $ |
| 10.10 01:58 | Down | 0.7345 | 18.43 | 0.924 | 62 s | Down | +5 $ |
| 10.10 02:18 | Up | 0.1802 | 60 | 0.379 | 76 s | Down | −11 $ |
| 10.10 02:23 | Up | 0.7539 | 67.57 | 0.94 | 74 s | Up | +17 $ |
| 10.10 02:28 | Up | 0.4678 | 64 | 0.653 | 76 s | Up | +34 $ |
| 10.10 02:44 | Up | 0.4173 | 125 | 0.997 | 58 s | Down | −52 $ |
| 10.10 02:48 | Down | 0.4173 | 125 | 0.815 | 62 s | Up | −52 $ |
| 10.10 03:03 | Down | 0.0959 | 147.89 | 0.299 | 84 s | Up | −14 $ |
| 10.10 03:08 | Down | 0.1906 | 5 | 0.399 | 62 s | Up | −1 $ |
| 10.10 04:13 | Down | 0.3254 | 25 | 0.518 | 65 s | Down | +17 $ |
| 10.10 04:28 | Up | 0.2115 | 50 | 0.449 | 90 s | Down | −11 $ |
| 10.10 04:48 | Down | 0.3459 | 100 | 0.54 | 64 s | Down | +65 $ |
| 10.10 05:19 | Down | 0.6271 | 30 | 0.83 | 48 s | Down | +11 $ |
| 10.10 05:33 | Down | 0.4577 | 36.56 | 0.734 | 63 s | Down | +20 $ |
| 10.10 05:43 | Up | 0.2219 | 20 | 0.418 | 81 s | Down | −4 $ |
| 10.10 06:13 | Up | 0.1487 | 8 | 0.342 | 86 s | Up | +7 $ |
| 10.10 06:29 | Up | 0.7539 | 8 | 0.943 | 37 s | Up | +2 $ |
| 10.10 06:53 | Up | 0.4779 | 29.95 | 0.997 | 89 s | Up | +16 $ |
| 10.10 07:23 | Up | 0.1906 | 5 | 0.608 | 90 s | Down | −1 $ |
| 10.10 07:54 | Down | 0.2531 | 88 | 0.443 | 57 s | Up | −22 $ |
| 10.10 09:03 | Up | 0.2219 | 15 | 0.41 | 86 s | Up | +12 $ |
| 10.10 09:43 | Up | 0.7151 | 27.85 | 0.901 | 66 s | Up | +8 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.893 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.1065 | 500 | 0.336 | 73 s | Up | −53 $ |
| 10.10 10:13 | Down | 0.4173 | 125 | 0.931 | 69 s | Up | −52 $ |
| 10.10 10:18 | Down | 0.4173 | 125 | 0.999 | 63 s | Up | −52 $ |
| 10.10 10:23 | Down | 0.6173 | 83.33 | 1 | 68 s | Up | −51 $ |
| 10.10 10:33 | Up | 0.6957 | 5 | 0.884 | 63 s | Up | +2 $ |
| 10.10 10:38 | Down | 0.6566 | 78.13 | 0.854 | 90 s | Up | −51 $ |

### TWAP fin confirme Chainlink — 13 trades, résultat −319 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 10.10 01:13 | Up | 0.6173 | 10 | 0.834 | 73 s | Down | −6 $ |
| 10.10 02:18 | Up | 0.1381 | 40 | 0.343 | 75 s | Down | −6 $ |
| 10.10 02:48 | Down | 0.4173 | 125 | 0.803 | 62 s | Up | −52 $ |
| 10.10 03:03 | Down | 0.2428 | 217.39 | 0.458 | 89 s | Up | −53 $ |
| 10.10 03:08 | Down | 0.2428 | 217.39 | 0.434 | 84 s | Up | −53 $ |
| 10.10 04:08 | Up | 0.1276 | 416.67 | 0.338 | 87 s | Down | −53 $ |
| 10.10 04:28 | Up | 0.2115 | 39.95 | 0.483 | 90 s | Down | −8 $ |
| 10.10 05:34 | Up | 0.2739 | 10 | 0.481 | 56 s | Down | −3 $ |
| 10.10 05:43 | Up | 0.2219 | 45 | 0.414 | 81 s | Down | −10 $ |
| 10.10 06:13 | Down | 0.3664 | 136.42 | 0.562 | 64 s | Up | −50 $ |
| 10.10 06:29 | Down | 0.5975 | 1.6 | 0.812 | 36 s | Up | −1 $ |
| 10.10 07:23 | Up | 0.2011 | 20 | 0.736 | 90 s | Down | −4 $ |
| 10.10 07:54 | Down | 0.2428 | 84.9 | 0.45 | 56 s | Up | −21 $ |

### corrige : V2-F + garde-fou — 119 trades, résultat −892 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 09.10 22:55 | Up | 0.6957 | 73.53 | 0.882 | 253 s | Up | +22 $ |
| 09.10 23:07 | Down | 0.2297 | 238.1 | 0.429 | 155 s | Up | −55 $ |
| 09.10 23:10 | Up | 0.498 | 104.17 | 0.682 | 255 s | Up | +52 $ |
| 09.10 23:12 | Up | 0.6074 | 84.75 | 0.813 | 178 s | Up | +33 $ |
| 09.10 23:15 | Down | 0.6021 | 86.21 | 0.784 | 249 s | Down | +34 $ |
| 09.10 23:21 | Down | 0.2324 | 52 | 0.464 | 228 s | Down | +40 $ |
| 09.10 23:25 | Down | 0.4121 | 9.75 | 0.597 | 262 s | Up | −4 $ |
| 09.10 23:30 | Down | 0.6222 | 10 | 0.812 | 277 s | Down | +4 $ |
| 09.10 23:35 | Up | 0.6074 | 84.75 | 0.801 | 283 s | Down | −51 $ |
| 09.10 23:42 | Down | 0.1802 | 33 | 0.471 | 176 s | Down | +27 $ |
| 09.10 23:48 | Down | 0.2115 | 250 | 0.45 | 116 s | Down | +197 $ |
| 09.10 23:53 | Up | 0.2945 | 20.83 | 0.483 | 113 s | Down | −6 $ |
| 09.10 23:55 | Down | 0.2739 | 6 | 0.504 | 284 s | Up | −2 $ |
| 10.10 00:05 | Up | 0.4135 | 13.33 | 0.604 | 277 s | Up | +8 $ |
| 10.10 00:11 | Up | 0.2219 | 40 | 0.412 | 239 s | Down | −9 $ |
| 10.10 00:23 | Down | 0.3452 | 156.25 | 0.527 | 106 s | Down | +102 $ |
| 10.10 00:26 | Up | 0.4577 | 13.22 | 0.688 | 230 s | Down | −6 $ |
| 10.10 00:36 | Down | 0.1276 | 100 | 0.338 | 194 s | Up | −13 $ |
| 10.10 00:42 | Up | 0.4779 | 108.7 | 0.669 | 124 s | Down | −52 $ |
| 10.10 00:47 | Up | 0.3459 | 151.52 | 0.55 | 135 s | Up | +99 $ |
| 10.10 00:52 | Up | 0.4577 | 113.64 | 0.643 | 137 s | Up | +62 $ |
| 10.10 00:56 | Up | 0.3785 | 27 | 0.662 | 187 s | Up | +17 $ |
| 10.10 01:03 | Up | 0.1842 | 13 | 0.371 | 110 s | Down | −2 $ |
| 10.10 01:08 | Down | 0.248 | 29.92 | 0.433 | 94 s | Up | −7 $ |
| 10.10 01:10 | Down | 0.4577 | 113.64 | 0.652 | 261 s | Down | +62 $ |
| 10.10 01:16 | Down | 0.3193 | 151 | 0.501 | 194 s | Up | −48 $ |
| 10.10 01:25 | Up | 0.3664 | 142.86 | 0.55 | 273 s | Down | −52 $ |
| 10.10 01:31 | Down | 0.2831 | 192.31 | 0.47 | 237 s | Up | −54 $ |
| 10.10 01:36 | Up | 0.1487 | 357.14 | 0.342 | 185 s | Down | −53 $ |
| 10.10 01:42 | Down | 0.2685 | 195 | 0.47 | 177 s | Up | −52 $ |
| 10.10 01:50 | Down | 0.2945 | 100 | 0.499 | 263 s | Down | +71 $ |
| 10.10 01:55 | Up | 0.4067 | 131.58 | 0.581 | 242 s | Down | −54 $ |
| 10.10 02:03 | Up | 0.1065 | 30.45 | 0.32 | 74 s | Down | −3 $ |
| 10.10 02:06 | Up | 0.3117 | 15 | 0.503 | 216 s | Down | −5 $ |
| 10.10 02:18 | Up | 0.1941 | 82.54 | 0.386 | 77 s | Down | −16 $ |
| 10.10 02:23 | Down | 0.1533 | 228.93 | 0.395 | 107 s | Up | −35 $ |
| 10.10 02:26 | Down | 0.7621 | 67.57 | 0.94 | 197 s | Up | −51 $ |
| 10.10 02:38 | Up | 0.32 | 166.67 | 0.5 | 120 s | Down | −53 $ |
| 10.10 02:40 | Up | 0.2842 | 185.19 | 0.481 | 280 s | Down | −53 $ |
| 10.10 02:47 | Up | 0.3048 | 172.41 | 0.537 | 176 s | Up | +120 $ |
| 10.10 02:56 | Up | 0.2842 | 185.19 | 0.48 | 218 s | Down | −53 $ |
| 10.10 03:03 | Up | 0.2324 | 227.27 | 0.52 | 117 s | Up | +174 $ |
| 10.10 03:08 | Down | 0.2821 | 192.31 | 0.464 | 85 s | Up | −54 $ |
| 10.10 03:16 | Up | 0.2635 | 70 | 0.464 | 235 s | Down | −18 $ |
| 10.10 03:33 | Up | 0.1891 | 294.12 | 0.375 | 114 s | Down | −56 $ |
| 10.10 03:58 | Down | 0.4302 | 121.95 | 0.618 | 110 s | Up | −52 $ |
| 10.10 04:01 | Up | 0.231 | 232 | 0.418 | 234 s | Up | +178 $ |
| 10.10 04:07 | Up | 0.2219 | 238.1 | 0.429 | 125 s | Down | −53 $ |
| 10.10 04:12 | Down | 0.3548 | 151.52 | 0.535 | 128 s | Down | +98 $ |
| 10.10 04:17 | Up | 0.1802 | 294.12 | 0.419 | 129 s | Down | −53 $ |
| 10.10 04:20 | Down | 0.4923 | 106.38 | 0.68 | 296 s | Down | +54 $ |
| 10.10 04:27 | Up | 0.3151 | 12 | 0.516 | 122 s | Down | −4 $ |
| 10.10 04:33 | Down | 0.2489 | 217.39 | 0.435 | 105 s | Up | −54 $ |
| 10.10 04:35 | Down | 0.6074 | 84.75 | 0.801 | 276 s | Up | −51 $ |
| 10.10 04:49 | Up | 0.3955 | 135.14 | 0.571 | 49 s | Down | −53 $ |
| 10.10 04:52 | Down | 0.2231 | 150.99 | 0.427 | 161 s | Up | −34 $ |
| 10.10 04:55 | Down | 0.3766 | 138.89 | 0.59 | 282 s | Down | +87 $ |
| 10.10 05:02 | Up | 0.3459 | 151.52 | 0.549 | 145 s | Down | −52 $ |
| 10.10 05:07 | Up | 0.3357 | 55 | 0.53 | 177 s | Down | −18 $ |
| 10.10 05:18 | Up | 0.1064 | 555.56 | 0.299 | 93 s | Down | −59 $ |
| 10.10 05:22 | Up | 0.3562 | 147.06 | 0.547 | 161 s | Down | −52 $ |
| 10.10 05:34 | Up | 0.3125 | 172.41 | 0.497 | 56 s | Down | −54 $ |
| 10.10 05:40 | Down | 0.2994 | 178.57 | 0.485 | 262 s | Down | +125 $ |
| 10.10 05:45 | Down | 0.2842 | 185.19 | 0.498 | 293 s | Up | −53 $ |
| 10.10 05:51 | Up | 0.2115 | 12 | 0.416 | 221 s | Down | −3 $ |
| 10.10 05:56 | Down | 0.3151 | 23.4 | 0.504 | 200 s | Up | −7 $ |
| 10.10 06:00 | Down | 0.3048 | 8.99 | 0.527 | 292 s | Up | −3 $ |
| 10.10 06:13 | Up | 0.2739 | 56.38 | 0.47 | 115 s | Up | +41 $ |
| 10.10 06:23 | Up | 0.1064 | 526.96 | 0.296 | 93 s | Down | −56 $ |
| 10.10 06:27 | Down | 0.1372 | 416.67 | 0.324 | 162 s | Up | −57 $ |
| 10.10 06:33 | Up | 0.1065 | 500 | 0.314 | 93 s | Down | −53 $ |
| 10.10 06:37 | Down | 0.2366 | 128.84 | 0.428 | 164 s | Up | −30 $ |
| 10.10 06:40 | Down | 0.1998 | 67 | 0.383 | 248 s | Up | −13 $ |
| 10.10 06:47 | Up | 0.263 | 208.33 | 0.447 | 126 s | Down | −55 $ |
| 10.10 06:52 | Up | 0.5851 | 77 | 0.763 | 164 s | Up | +32 $ |
| 10.10 07:02 | Up | 0.1291 | 142.85 | 0.446 | 145 s | Down | −18 $ |
| 10.10 07:05 | Up | 0.3048 | 20 | 0.492 | 294 s | Up | +14 $ |
| 10.10 07:11 | Up | 0.5975 | 16.37 | 0.895 | 218 s | Up | +7 $ |
| 10.10 07:15 | Up | 0.2321 | 238.1 | 0.418 | 255 s | Down | −55 $ |
| 10.10 07:23 | Up | 0.3216 | 94.58 | 0.508 | 109 s | Down | −30 $ |
| 10.10 07:27 | Up | 0.3664 | 142.86 | 0.554 | 178 s | Down | −52 $ |
| 10.10 07:35 | Up | 0.1802 | 10.09 | 0.371 | 271 s | Up | +8 $ |
| 10.10 07:42 | Down | 0.3034 | 140 | 0.485 | 155 s | Up | −42 $ |
| 10.10 07:46 | Up | 0.518 | 100 | 0.777 | 207 s | Down | −52 $ |
| 10.10 07:53 | Down | 0.3014 | 60 | 0.484 | 62 s | Up | −18 $ |
| 10.10 07:56 | Down | 0.4879 | 44.06 | 0.693 | 222 s | Up | −22 $ |
| 10.10 08:01 | Up | 0.2842 | 14 | 0.474 | 182 s | Down | −4 $ |
| 10.10 08:06 | Up | 0.1554 | 55 | 0.392 | 210 s | Down | −9 $ |
| 10.10 08:18 | Up | 0.2159 | 68.61 | 0.493 | 116 s | Up | +54 $ |
| 10.10 08:26 | Down | 0.2997 | 20 | 0.602 | 196 s | Up | −6 $ |
| 10.10 08:32 | Up | 0.2115 | 250 | 0.416 | 151 s | Down | −53 $ |
| 10.10 08:37 | Down | 0.1504 | 282.52 | 0.438 | 155 s | Up | −42 $ |
| 10.10 08:40 | Up | 0.538 | 10.08 | 0.756 | 277 s | Up | +5 $ |
| 10.10 08:46 | Up | 0.0782 | 30 | 0.273 | 196 s | Down | −2 $ |
| 10.10 09:01 | Down | 0.1371 | 61 | 0.329 | 220 s | Up | −8 $ |
| 10.10 09:07 | Up | 0.3715 | 70.01 | 0.606 | 149 s | Down | −26 $ |
| 10.10 09:11 | Down | 0.5835 | 8.57 | 0.867 | 191 s | Down | +4 $ |
| 10.10 09:18 | Up | 0.1792 | 219.33 | 0.377 | 103 s | Down | −39 $ |
| 10.10 09:22 | Up | 0.2009 | 277.78 | 0.387 | 175 s | Down | −56 $ |
| 10.10 09:27 | Up | 0.3329 | 161.29 | 0.519 | 158 s | Down | −54 $ |
| 10.10 09:33 | Down | 0.2731 | 200 | 0.453 | 99 s | Up | −55 $ |
| 10.10 09:43 | Down | 0.0726 | 31 | 0.489 | 66 s | Up | −2 $ |
| 10.10 09:46 | Down | 0.4888 | 55 | 0.757 | 232 s | Up | −27 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.77 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.2945 | 178.57 | 0.488 | 104 s | Up | −53 $ |
| 10.10 10:01 | Down | 0.3001 | 178.57 | 0.489 | 193 s | Up | −54 $ |
| 10.10 10:08 | Down | 0.1375 | 416.67 | 0.322 | 114 s | Up | −57 $ |
| 10.10 10:12 | Up | 0.3151 | 166.67 | 0.507 | 159 s | Up | +114 $ |
| 10.10 10:16 | Up | 0.3041 | 178.57 | 0.484 | 192 s | Up | +124 $ |
| 10.10 10:21 | Up | 0.2324 | 5 | 0.432 | 220 s | Up | +4 $ |
| 10.10 10:26 | Up | 0.3947 | 135.14 | 0.577 | 223 s | Down | −53 $ |
| 10.10 10:31 | Up | 0.2992 | 96.97 | 0.509 | 196 s | Up | +68 $ |
| 10.10 10:36 | Down | 0.397 | 100 | 0.585 | 209 s | Up | −40 $ |
| 10.10 10:41 | Down | 0.7382 | 13 | 0.921 | 227 s | Down | +3 $ |
| 10.10 10:50 | Down | 0.2842 | 185.19 | 0.483 | 285 s | Up | −53 $ |
| 10.10 10:58 | Down | 0.1118 | 10 | 0.356 | 67 s | Up | −1 $ |
| 10.10 11:00 | Down | 0.2842 | 185.19 | 0.482 | 248 s | Up | −53 $ |
| 10.10 11:07 | Down | 0.272 | 200 | 0.451 | 152 s | Up | −54 $ |
| 10.10 11:10 | Down | 0.4729 | 111.11 | 0.653 | 287 s | Up | −53 $ |

### corrige marge mesuree : V2-F — 114 trades, résultat −283 $

| Heure | Côté | Prix | Parts | Proba | Restant | Gagnant | Net |
|---|---|---|---|---|---|---|---|
| 09.10 22:56 | Up | 0.5777 | 50 | 0.777 | 229 s | Up | +21 $ |
| 09.10 23:03 | Down | 0.1332 | 166 | 0.328 | 106 s | Up | −22 $ |
| 09.10 23:07 | Down | 0.2297 | 238.1 | 0.435 | 155 s | Up | −55 $ |
| 09.10 23:10 | Up | 0.4938 | 106.38 | 0.675 | 255 s | Up | +54 $ |
| 09.10 23:12 | Up | 0.5469 | 96.15 | 0.728 | 158 s | Up | +44 $ |
| 09.10 23:16 | Down | 0.5944 | 32 | 0.799 | 195 s | Down | +13 $ |
| 09.10 23:21 | Down | 0.2324 | 52 | 0.466 | 228 s | Down | +40 $ |
| 09.10 23:25 | Down | 0.4121 | 9.75 | 0.593 | 262 s | Up | −4 $ |
| 09.10 23:38 | Up | 0.3913 | 135.14 | 0.572 | 108 s | Down | −53 $ |
| 09.10 23:42 | Down | 0.1802 | 33 | 0.472 | 176 s | Down | +27 $ |
| 09.10 23:48 | Down | 0.2115 | 250 | 0.453 | 116 s | Down | +197 $ |
| 09.10 23:53 | Up | 0.2945 | 20.83 | 0.484 | 113 s | Down | −6 $ |
| 09.10 23:55 | Down | 0.2739 | 6 | 0.504 | 284 s | Up | −2 $ |
| 10.10 00:05 | Up | 0.4135 | 13.33 | 0.603 | 277 s | Up | +8 $ |
| 10.10 00:11 | Up | 0.2219 | 40 | 0.414 | 239 s | Down | −9 $ |
| 10.10 00:23 | Down | 0.3452 | 156.25 | 0.526 | 106 s | Down | +102 $ |
| 10.10 00:26 | Up | 0.4577 | 13.22 | 0.687 | 230 s | Down | −6 $ |
| 10.10 00:36 | Down | 0.1276 | 100 | 0.34 | 194 s | Up | −13 $ |
| 10.10 00:42 | Up | 0.4779 | 108.7 | 0.668 | 124 s | Down | −52 $ |
| 10.10 00:47 | Up | 0.3459 | 151.52 | 0.55 | 135 s | Up | +99 $ |
| 10.10 00:52 | Up | 0.4577 | 113.64 | 0.644 | 137 s | Up | +62 $ |
| 10.10 00:56 | Up | 0.3785 | 27 | 0.664 | 187 s | Up | +17 $ |
| 10.10 01:03 | Down | 0.4476 | 10.28 | 0.66 | 76 s | Down | +6 $ |
| 10.10 01:08 | Down | 0.248 | 29.92 | 0.432 | 94 s | Up | −7 $ |
| 10.10 01:10 | Down | 0.4577 | 113.64 | 0.655 | 261 s | Down | +62 $ |
| 10.10 01:16 | Down | 0.3193 | 151 | 0.501 | 194 s | Up | −48 $ |
| 10.10 01:25 | Up | 0.3762 | 142.86 | 0.55 | 273 s | Down | −54 $ |
| 10.10 01:31 | Down | 0.2831 | 192.31 | 0.469 | 237 s | Up | −54 $ |
| 10.10 01:42 | Down | 0.2685 | 195 | 0.468 | 177 s | Up | −52 $ |
| 10.10 01:50 | Down | 0.2945 | 100 | 0.499 | 263 s | Down | +71 $ |
| 10.10 01:55 | Up | 0.4067 | 131.58 | 0.583 | 242 s | Down | −54 $ |
| 10.10 02:03 | Up | 0.1065 | 30.45 | 0.314 | 74 s | Down | −3 $ |
| 10.10 02:06 | Up | 0.3117 | 15 | 0.504 | 216 s | Down | −5 $ |
| 10.10 02:18 | Up | 0.1885 | 294.12 | 0.377 | 76 s | Down | −55 $ |
| 10.10 02:23 | Down | 0.1533 | 228.93 | 0.392 | 107 s | Up | −35 $ |
| 10.10 02:26 | Down | 0.7621 | 67.57 | 0.948 | 197 s | Up | −51 $ |
| 10.10 02:38 | Up | 0.32 | 166.67 | 0.5 | 120 s | Down | −53 $ |
| 10.10 02:40 | Up | 0.2842 | 185.19 | 0.48 | 280 s | Down | −53 $ |
| 10.10 02:47 | Up | 0.3048 | 172.41 | 0.54 | 176 s | Up | +120 $ |
| 10.10 02:52 | Up | 0.528 | 5 | 0.722 | 175 s | Up | +2 $ |
| 10.10 02:56 | Up | 0.2842 | 185.19 | 0.478 | 218 s | Down | −53 $ |
| 10.10 03:03 | Up | 0.2324 | 227.27 | 0.525 | 117 s | Up | +174 $ |
| 10.10 03:08 | Down | 0.2712 | 200 | 0.455 | 84 s | Up | −54 $ |
| 10.10 03:16 | Up | 0.2635 | 70 | 0.461 | 235 s | Down | −18 $ |
| 10.10 03:33 | Up | 0.1891 | 294.12 | 0.372 | 114 s | Down | −56 $ |
| 10.10 03:58 | Down | 0.4577 | 113.64 | 0.641 | 110 s | Up | −52 $ |
| 10.10 04:02 | Up | 0.4375 | 23 | 0.656 | 151 s | Up | +13 $ |
| 10.10 04:07 | Up | 0.2219 | 238.1 | 0.42 | 125 s | Down | −53 $ |
| 10.10 04:12 | Down | 0.365 | 147.06 | 0.54 | 128 s | Down | +93 $ |
| 10.10 04:17 | Up | 0.1802 | 294.12 | 0.4 | 129 s | Down | −53 $ |
| 10.10 04:20 | Down | 0.5141 | 102.04 | 0.697 | 296 s | Down | +50 $ |
| 10.10 04:27 | Up | 0.3151 | 12 | 0.519 | 122 s | Down | −4 $ |
| 10.10 04:30 | Up | 0.528 | 98.04 | 0.713 | 245 s | Up | +46 $ |
| 10.10 04:35 | Down | 0.6664 | 12.11 | 0.865 | 278 s | Up | −8 $ |
| 10.10 04:49 | Up | 0.4061 | 88.86 | 0.589 | 49 s | Down | −36 $ |
| 10.10 04:52 | Down | 0.2231 | 150.99 | 0.421 | 161 s | Up | −34 $ |
| 10.10 04:55 | Down | 0.3766 | 138.89 | 0.597 | 282 s | Down | +87 $ |
| 10.10 05:02 | Up | 0.3459 | 151.52 | 0.552 | 145 s | Down | −52 $ |
| 10.10 05:07 | Up | 0.3357 | 55 | 0.531 | 177 s | Down | −18 $ |
| 10.10 05:19 | Down | 0.5777 | 62.33 | 0.788 | 48 s | Down | +26 $ |
| 10.10 05:22 | Up | 0.3762 | 142.86 | 0.553 | 178 s | Down | −54 $ |
| 10.10 05:34 | Up | 0.3125 | 172.41 | 0.496 | 56 s | Down | −54 $ |
| 10.10 05:36 | Down | 0.6468 | 18.97 | 0.898 | 235 s | Down | +7 $ |
| 10.10 05:40 | Down | 0.2994 | 178.57 | 0.484 | 262 s | Down | +125 $ |
| 10.10 05:45 | Down | 0.2842 | 185.19 | 0.498 | 293 s | Up | −53 $ |
| 10.10 05:51 | Up | 0.2115 | 12 | 0.409 | 221 s | Down | −3 $ |
| 10.10 05:56 | Down | 0.3151 | 23.4 | 0.505 | 200 s | Up | −7 $ |
| 10.10 06:00 | Down | 0.3048 | 8.99 | 0.532 | 292 s | Up | −3 $ |
| 10.10 06:13 | Up | 0.2739 | 56.38 | 0.468 | 115 s | Up | +41 $ |
| 10.10 06:28 | Down | 0.0959 | 555.56 | 0.294 | 91 s | Up | −53 $ |
| 10.10 06:37 | Down | 0.2315 | 238.1 | 0.417 | 163 s | Up | −55 $ |
| 10.10 06:52 | Up | 0.5851 | 77 | 0.894 | 164 s | Up | +32 $ |
| 10.10 07:02 | Up | 0.1291 | 142.85 | 0.418 | 145 s | Down | −18 $ |
| 10.10 07:05 | Up | 0.2739 | 192.31 | 0.49 | 294 s | Up | +140 $ |
| 10.10 07:11 | Up | 0.5975 | 16.37 | 0.963 | 218 s | Up | +7 $ |
| 10.10 07:15 | Up | 0.2321 | 238.1 | 0.415 | 255 s | Down | −55 $ |
| 10.10 07:23 | Up | 0.3216 | 94.58 | 0.514 | 109 s | Down | −30 $ |
| 10.10 07:27 | Up | 0.3664 | 142.86 | 0.56 | 178 s | Down | −52 $ |
| 10.10 07:30 | Up | 0.791 | 64.94 | 0.971 | 241 s | Up | +14 $ |
| 10.10 07:36 | Up | 0.2635 | 200 | 0.468 | 210 s | Up | +147 $ |
| 10.10 07:42 | Down | 0.3034 | 140 | 0.483 | 155 s | Up | −42 $ |
| 10.10 07:46 | Up | 0.518 | 100 | 0.816 | 207 s | Down | −52 $ |
| 10.10 07:53 | Down | 0.2928 | 121 | 0.475 | 61 s | Up | −35 $ |
| 10.10 07:56 | Down | 0.6271 | 24 | 0.82 | 222 s | Up | −15 $ |
| 10.10 08:01 | Up | 0.2842 | 14 | 0.472 | 182 s | Down | −4 $ |
| 10.10 08:06 | Up | 0.1554 | 55 | 0.387 | 210 s | Down | −9 $ |
| 10.10 08:18 | Up | 0.2159 | 68.61 | 0.486 | 116 s | Up | +54 $ |
| 10.10 08:25 | Up | 0.6271 | 81.97 | 0.821 | 289 s | Up | +31 $ |
| 10.10 08:32 | Down | 0.7248 | 70.42 | 0.951 | 160 s | Down | +19 $ |
| 10.10 08:37 | Down | 0.1504 | 282.52 | 0.422 | 155 s | Up | −42 $ |
| 10.10 08:40 | Up | 0.538 | 10.08 | 0.841 | 277 s | Up | +5 $ |
| 10.10 08:46 | Up | 0.0965 | 208.18 | 0.368 | 186 s | Down | −20 $ |
| 10.10 09:01 | Down | 0.1371 | 61 | 0.324 | 220 s | Up | −8 $ |
| 10.10 09:07 | Up | 0.4375 | 119.05 | 0.621 | 150 s | Down | −52 $ |
| 10.10 09:11 | Down | 0.5835 | 8.57 | 0.889 | 191 s | Down | +4 $ |
| 10.10 09:20 | Down | 0.6578 | 78.13 | 0.856 | 295 s | Down | +27 $ |
| 10.10 09:27 | Up | 0.3664 | 142.86 | 0.55 | 160 s | Down | −52 $ |
| 10.10 09:33 | Down | 0.2113 | 263.16 | 0.399 | 83 s | Up | −56 $ |
| 10.10 09:43 | Down | 0.0455 | 20.47 | 0.483 | 66 s | Up | −1 $ |
| 10.10 09:46 | Down | 0.4888 | 55 | 0.77 | 232 s | Up | −27 $ |
| 10.10 09:53 | Down | 0.518 | 100 | 0.871 | 67 s | Up | −52 $ |
| 10.10 09:58 | Down | 0.2945 | 178.57 | 0.481 | 104 s | Up | −53 $ |
| 10.10 10:01 | Down | 0.3001 | 178.57 | 0.487 | 193 s | Up | −54 $ |
| 10.10 10:10 | Down | 0.7054 | 72.46 | 0.903 | 275 s | Up | −51 $ |
| 10.10 10:16 | Up | 0.2942 | 185.19 | 0.478 | 192 s | Up | +131 $ |
| 10.10 10:21 | Up | 0.2324 | 5 | 0.422 | 220 s | Up | +4 $ |
| 10.10 10:26 | Up | 0.4058 | 131.58 | 0.581 | 223 s | Down | −53 $ |
| 10.10 10:31 | Up | 0.2992 | 96.97 | 0.511 | 196 s | Up | +68 $ |
| 10.10 10:36 | Down | 0.397 | 100 | 0.65 | 209 s | Up | −40 $ |
| 10.10 10:41 | Down | 0.7382 | 13 | 0.965 | 227 s | Down | +3 $ |
| 10.10 10:50 | Down | 0.2842 | 185.19 | 0.48 | 285 s | Up | −53 $ |
| 10.10 11:00 | Down | 0.2842 | 185.19 | 0.471 | 248 s | Up | −53 $ |
| 10.10 11:07 | Down | 0.1811 | 110.33 | 0.376 | 128 s | Up | −20 $ |
| 10.10 11:10 | Down | 0.4824 | 108.7 | 0.664 | 287 s | Up | −52 $ |
