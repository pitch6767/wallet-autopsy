# Fiabilité de l'avantage, urgence, faux cadeaux, origine des désaccords, TWAP contrefactuel — BTC, 889 cycles

163 premiers signaux E (avantage ≥ 0,20). Apprentissage avant le 08.10 22:00 ; validation + nuit après. Seuils fixés sur l'apprentissage.

## Référence

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| tous les signaux E | 77 / 51 % / **+1 264 $** / −136 $ / 9 | 86 / 44 % / **+639 $** / −392 $ / 8 |

## Partie A — Retrait de liquidité et urgence d'exécution (idées 2-7)

### Idée 4 : au moment du signal, le prix vendeur monte-t-il d'au moins 2 c dans la seconde ?

| Groupe | Signaux | Prix vendeur +2 c en 1 s | Variation moyenne du prix en 1 s |
|---|---|---|---|
| après saut | 15 | 87 % | +24.2 c |
| après saut + retrait fort | 3 | 100 % | +39.3 c |
| avantage 20-30 pts | 109 | 53 % | +8.0 c |
| avantage 20-30 pts + retrait fort | 9 | 89 % | +20.0 c |
| avantage ≥ 30 pts | 41 | 54 % | +12.8 c |
| avantage ≥ 30 pts + retrait fort | 4 | 100 % | +39.5 c |
| pas de retrait fort | 150 | 53 % | +9.3 c |
| retrait fort (≥ 50 %) | 13 | 92 % | +26.0 c |
| régime agité | 112 | 62 % | +11.9 c |
| régime agité + retrait fort | 11 | 91 % | +21.4 c |
| régime calme | 38 | 29 % | +1.8 c |
| régime calme + retrait fort | 2 | 100 % | +51.5 c |
| sans saut | 135 | 50 % | +7.6 c |
| sans saut + retrait fort | 10 | 90 % | +22.0 c |

### Idée 5 : acheter tout de suite seulement si le carnet se vide, sinon attendre un peu (délais fixés d'avance)

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| A — acheter tout de suite (référence) | 77 / 51 % / **+1 264 $** / −136 $ / 9 | 86 / 44 % / **+639 $** / −392 $ / 8 |
| B — retrait fort : tout de suite ; sinon attendre 0.25 s (acheter si l'avantage est encore ≥ 0,20) | 41 / 44 % / **+752 $** / −124 $ / 4 | 62 / 45 % / **+794 $** / −287 $ / 7 |
| B — retrait fort : tout de suite ; sinon attendre 0.5 s (acheter si l'avantage est encore ≥ 0,20) | 30 / 43 % / **+330 $** / −111 $ / 2 | 57 / 39 % / **+825 $** / −238 $ / 6 |
| B — retrait fort : tout de suite ; sinon attendre 1.0 s (acheter si l'avantage est encore ≥ 0,20) | 23 / 39 % / **+150 $** / −190 $ / 3 | 46 / 37 % / **+223 $** / −218 $ / 5 |

### Idée 3 : avantage « fiable » = avantage − surestimation apprise (par régime, saut récent, âge du désaccord)

Surestimations apprises (probabilité annoncée − taux de gain réel, signaux d'apprentissage) : agité, sans saut, né < 3 s : +0.04, agité, saut, né < 3 s : +0.13, agité, sans saut, mûr : +0.05 ; global +0.04.

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| avantage fiable ≥ 0,20 | 29 / 59 % / **+947 $** / −106 $ / 6 | 43 / 37 % / **−519 $** / −522 $ / 3 |
| avantage fiable ≥ 0,10 | 77 / 51 % / **+1 264 $** / −136 $ / 9 | 86 / 44 % / **+639 $** / −392 $ / 8 |
| avantage fiable < 0,10 | 0 / — / — / — / — | 0 / — / — / — / — |

### Idée 6 : carte avantage × fiabilité × retrait (validation + nuit)

| Avantage | Fiabilité | Retrait fort | Achats / gagnés / résultat / creux / jackpots |
|---|---|---|---|
| 20-30 pts | fiable | oui | 6 / 67 % / **+120 $** / −15 $ / 2 |
| 20-30 pts | fiable | non | 55 / 49 % / **+1 107 $** / −256 $ / 4 |
| ≥ 30 pts | fiable | non | 25 / 28 % / **−588 $** / −592 $ / 2 |

## Partie B — Les faux cadeaux : les 25 signaux à 30 points d'avantage ou plus, hors apprentissage (idées 8-9)

| Heure | Côté | Prix | Proba E | Avantage | Restant | Régime | Saut récent | Âge du désaccord | Prix vendeur 3 s avant | Proba sans le dernier choc | Gagnant | Net |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 08.10 23:33 | Down | 0.64 | 0.96 | 0.32 | 76 s | agité | oui | 4.2 s | 0.64 | 0.72 | oui | +3 $ |
| 09.10 00:43 | Down | 0.40 | 0.88 | 0.48 | 65 s | agité | non | 0.3 s | 0.83 | 0.89 | non | −52 $ |
| 09.10 00:59 | Down | 0.51 | 0.90 | 0.39 | 55 s | agité | non | 3.0 s | 0.87 | 0.91 | non | −52 $ |
| 09.10 03:03 | Down | 0.17 | 0.51 | 0.34 | 63 s | agité | non | 10.8 s | 0.10 | 0.21 | oui | +16 $ |
| 09.10 03:53 | Up | 0.40 | 0.79 | 0.39 | 64 s | agité | non | 0.3 s | 0.85 | 0.78 | non | −52 $ |
| 09.10 06:19 | Down | 0.18 | 0.50 | 0.32 | 57 s | agité | non | 3.9 s | 0.23 | 0.30 | non | −26 $ |
| 09.10 08:48 | Down | 0.22 | 0.54 | 0.32 | 81 s | agité | non | 0.6 s | 0.23 | 0.20 | non | −27 $ |
| 09.10 10:08 | Up | 0.65 | 0.97 | 0.32 | 90 s | agité | non | 99.0 s | 0.71 | 0.97 | oui | +26 $ |
| 09.10 10:19 | Down | 0.62 | 0.99 | 0.37 | 53 s | agité | oui | 0.3 s | 0.45 | 0.52 | oui | +2 $ |
| 09.10 21:43 | Up | 0.28 | 0.76 | 0.48 | 86 s | agité | oui | 4.2 s | 0.28 | 0.37 | oui | +4 $ |
| 09.10 23:23 | Up | 0.50 | 1.00 | 0.50 | 63 s | calme | non | 1.2 s | 0.97 | 1.00 | non | −52 $ |
| 09.10 23:59 | Up | 0.60 | 0.90 | 0.30 | 58 s | agité | non | 3.9 s | 0.78 | 0.90 | oui | +32 $ |
| 10.10 00:23 | Down | 0.19 | 0.59 | 0.40 | 90 s | calme | non | 99.0 s | 0.24 | 0.59 | oui | +40 $ |
| 10.10 01:33 | Down | 0.20 | 0.66 | 0.46 | 77 s | calme | non | 12.0 s | 0.23 | 0.32 | non | −1 $ |
| 10.10 02:44 | Up | 0.40 | 0.98 | 0.58 | 58 s | calme | non | 0.3 s | 0.93 | 0.98 | non | −52 $ |
| 10.10 02:48 | Down | 0.40 | 0.89 | 0.49 | 62 s | calme | non | 0.3 s | 0.89 | 0.89 | non | −52 $ |
| 10.10 05:19 | Up | 0.53 | 0.97 | 0.44 | 48 s | calme | oui | 0.3 s | 0.05 | 0.00 | non | −21 $ |
| 10.10 06:29 | Down | 0.35 | 0.72 | 0.37 | 37 s | calme | oui | 0.3 s | 0.01 | 0.00 | non | −52 $ |
| 10.10 07:23 | Up | 0.18 | 0.67 | 0.49 | 90 s | calme | non | 99.0 s | 0.27 | 0.69 | non | −5 $ |
| 10.10 09:43 | Down | 0.02 | 0.57 | 0.55 | 67 s | calme | oui | 0.6 s | 0.01 | 0.04 | non | −7 $ |
| 10.10 09:53 | Down | 0.50 | 0.94 | 0.44 | 67 s | calme | non | 99.0 s | 0.88 | 0.94 | non | −52 $ |
| 10.10 09:58 | Down | 0.18 | 0.57 | 0.39 | 90 s | calme | non | 99.0 s | 0.19 | 0.57 | non | −53 $ |
| 10.10 10:13 | Down | 0.40 | 0.94 | 0.54 | 69 s | calme | non | 0.3 s | 0.92 | 0.94 | non | −52 $ |
| 10.10 10:18 | Down | 0.40 | 1.00 | 0.60 | 63 s | calme | non | 0.3 s | 0.98 | 1.00 | non | −52 $ |
| 10.10 10:23 | Down | 0.60 | 1.00 | 0.40 | 68 s | calme | non | 16.2 s | nan | 1.00 | non | −51 $ |

- Après un saut des exchanges : 6 sur 25 ; régime calme : 14 ; désaccord né il y a moins de 3 s : 12 ; prix vendeur en chute d'au moins 5 c en 3 s : 13 ; gagnants : 7 (dont jackpots : 2).
- Les 3 plus grosses pertes font −157 $ sur un total de −588 $.

### Idées 8-9, 21 : le prix Polymarket s'est-il effondré juste avant le signal ? (prix vendeur de notre côté, 3 s avant → au signal)

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| avantage 20-30 pts | 57 / 49 % / **+986 $** / −128 $ / 6 | 61 / 51 % / **+1 227 $** / −251 $ / 6 |
| avantage ≥ 30 pts | 20 / 55 % / **+278 $** / −53 $ / 3 | 25 / 28 % / **−588 $** / −592 $ / 2 |
| prix vendeur effondré d'au moins 30 c en 3 s | 1 / 100 % / **+41 $** / +0 $ / 1 | 14 / 14 % / **−523 $** / −523 $ / 0 |
| prix vendeur en baisse de 10 à 30 c en 3 s | 10 / 70 % / **+458 $** / −53 $ / 1 | 10 / 70 % / **+373 $** / −52 $ / 0 |
| prix vendeur stable ou en hausse (moins de 10 c de baisse) | 66 / 47 % / **+765 $** / −188 $ / 7 | 62 / 47 % / **+789 $** / −392 $ / 8 |
| effondré ≥ 30 c ET proba E quasi inchangée (moins de 5 pts en 3 s) | 1 / 100 % / **+41 $** / +0 $ / 1 | 11 / 0 % / **−573 $** / −573 $ / 0 |

## Partie C — D'où vient l'avantage ? (idées 10-14, sur la seconde avant le signal)

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| 1. E monte, prix stable | 20 / 30 % / **+384 $** / −118 $ / 3 | 9 / 33 % / **+32 $** / −51 $ / 2 |
| 2. E stable, prix baisse | 15 / 60 % / **+300 $** / −106 $ / 2 | 34 / 41 % / **+311 $** / −193 $ / 2 |
| 3. E monte et prix baisse | 9 / 56 % / **+119 $** / −32 $ / 1 | 3 / 67 % / **+4 $** / −26 $ / 0 |
| 4. E monte, prix monte moins vite | 30 / 57 % / **+284 $** / −53 $ / 2 | 22 / 50 % / **+147 $** / −155 $ / 3 |
| 5. E baisse, prix baisse plus vite | 1 / 100 % / **+225 $** / +0 $ / 1 | 3 / 33 % / **+6 $** / −52 $ / 0 |
| 6. petits mouvements (< 3 pts / 2 c) | 1 / 0 % / **−51 $** / −51 $ / 0 | 11 / 36 % / **+173 $** / −316 $ / 1 |
| inconnue | 1 / 100 % / **+4 $** / +0 $ / 0 | 4 / 75 % / **−35 $** / −51 $ / 0 |

Idée 12 — signaux de 30 à 50 points d'avantage seulement :

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| 1. E monte, prix stable | 8 / 25 % / **+114 $** / −55 $ / 1 | 2 / 0 % / **−28 $** / −28 $ / 0 |
| 2. E stable, prix baisse | 1 / 100 % / **+41 $** / +0 $ / 1 | 8 / 25 % / **−240 $** / −240 $ / 1 |
| 3. E monte et prix baisse | 4 / 75 % / **+100 $** / −32 $ / 1 | 1 / 0 % / **−26 $** / −26 $ / 0 |
| 4. E monte, prix monte moins vite | 5 / 80 % / **+30 $** / −7 $ / 0 | 6 / 67 % / **−47 $** / −73 $ / 1 |
| 5. E baisse, prix baisse plus vite | 0 / — / — / — / — | 0 / — / — / — / — |
| 6. petits mouvements (< 3 pts / 2 c) | 0 / — / — / — / — | 3 / 33 % / **−32 $** / −58 $ / 0 |
| inconnue | 0 / — / — / — / — | 1 / 0 % / **−51 $** / −51 $ / 0 |

### Idée 14 : origine de l'information

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| A — nouvelle valeur Chainlink dans la dernière seconde | 68 / 53 % / **+1 308 $** / −110 $ / 9 | 81 / 42 % / **+232 $** / −633 $ / 8 |
| B — mouvement des exchanges sans nouveau Chainlink | 1 / 100 % / **+3 $** / +0 $ / 0 | 0 / — / — / — / — |
| C — baisse du prix Polymarket | 1 / 100 % / **+37 $** / +0 $ / 0 | 4 / 75 % / **+233 $** / −8 $ / 0 |
| D — autre / mixte | 7 / 14 % / **−83 $** / −83 $ / 0 | 1 / 100 % / **+174 $** / +0 $ / 0 |

## Partie D — Maturité et origine (idées 16-23)

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| A — nouvelle valeur Chainlink dans la dernière seconde — mûr (désaccord né il y a ≥ 3 s) | 28 / 50 % / **+737 $** / −172 $ / 4 | 45 / 44 % / **+527 $** / −413 $ / 7 |
| A — nouvelle valeur Chainlink dans la dernière seconde — récent (< 3 s) | 40 / 55 % / **+571 $** / −55 $ / 5 | 36 / 39 % / **−295 $** / −345 $ / 1 |
| B — mouvement des exchanges sans nouveau Chainlink — mûr (désaccord né il y a ≥ 3 s) | 0 / — / — / — / — | 0 / — / — / — / — |
| B — mouvement des exchanges sans nouveau Chainlink — récent (< 3 s) | 1 / 100 % / **+3 $** / +0 $ / 0 | 0 / — / — / — / — |
| C — baisse du prix Polymarket — mûr (désaccord né il y a ≥ 3 s) | 0 / — / — / — / — | 3 / 67 % / **+230 $** / −8 $ / 0 |
| C — baisse du prix Polymarket — récent (< 3 s) | 1 / 100 % / **+37 $** / +0 $ / 0 | 1 / 100 % / **+2 $** / +0 $ / 0 |
| D — autre / mixte — mûr (désaccord né il y a ≥ 3 s) | 4 / 25 % / **−69 $** / −73 $ / 0 | 1 / 100 % / **+174 $** / +0 $ / 0 |
| D — autre / mixte — récent (< 3 s) | 3 / 0 % / **−14 $** / −14 $ / 0 | 0 / — / — / — / — |

Idée 18 — nombre de nouvelles valeurs Chainlink depuis la naissance du désaccord :

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| 0 | 47 / 51 % / **+438 $** / −104 $ / 3 | 58 / 38 % / **−1 $** / −442 $ / 3 |
| 1 | 5 / 40 % / **−3 $** / −70 $ / 1 | 5 / 60 % / **−14 $** / −79 $ / 0 |
| 2 ou plus | 25 / 52 % / **+830 $** / −185 $ / 5 | 23 / 57 % / **+654 $** / −104 $ / 5 |

## Partie E — TWAP contrefactuel (idées 24-27)

SDR = |proba E − proba E sans le mouvement des 2 dernières secondes| / avantage. Médiane d'apprentissage : 0.82.

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| SDR faible (≤ 0.82) : le signal ne dépend pas du dernier choc | 39 / 49 % / **+819 $** / −173 $ / 7 | 65 / 45 % / **+744 $** / −316 $ / 5 |
| SDR fort : le signal dépend du dernier choc | 38 / 53 % / **+445 $** / −55 $ / 2 | 21 / 43 % / **−105 $** / −149 $ / 3 |
| SDR > 1 : sans le dernier choc, il n'y aurait plus d'avantage | 29 / 52 % / **+271 $** / −55 $ / 1 | 15 / 40 % / **−133 $** / −136 $ / 1 |

Idée 27 — consensus de trois mondes (E actuel ; dernier Chainlink prolongé ; consensus des 4 exchanges), avantage ≥ 0,20 :

| Groupe | Apprentissage (achats / gagnés / résultat / creux / jackpots) | Validation + nuit |
|---|---|---|
| 1 monde(s) sur 3 voient l'avantage | 51 / 47 % / **+1 121 $** / −90 $ / 7 | 44 / 43 % / **+839 $** / −145 $ / 5 |
| 2 monde(s) sur 3 voient l'avantage | 20 / 55 % / **+84 $** / −127 $ / 1 | 16 / 62 % / **+223 $** / −198 $ / 3 |
| 3 monde(s) sur 3 voient l'avantage | 6 / 67 % / **+59 $** / −53 $ / 1 | 26 / 35 % / **−423 $** / −423 $ / 0 |