# TWAP fin — jackpots, attente, exécution, mises, robustesse (BTC, 693 cycles, 07.10 08:05 → 09.10 22:35)

Référence : 140 premiers signaux TWAP fin original (avantage ≥ 0,20, 90-20 s), +2'323 $. Jackpot = gain ≥ 4 × la mise ; 18 jackpots pour +1'892 $. Apprentissage avant le 08.10 20:30, validation après.

## Partie A — horloge Chainlink, âge de l'opportunité, premier signal

### Idées 2-4. Phase Chainlink au moment du signal (connue à l'instant : âge du dernier prix reçu / intervalle médian des 5 derniers)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| juste après un prix Chainlink (< 1/3 de l'intervalle) | 73 | 48 % | **+819 $** | +53 % | −169 $ | 6 |
| juste après un prix Chainlink (< 1/3 de l'intervalle) — appr. | 43 | 44 % | **+409 $** | +52 % | −169 $ | 6 |
| juste après un prix Chainlink (< 1/3 de l'intervalle) — valid. | 30 | 53 % | **+410 $** | +54 % | −156 $ | 3 |
| milieu de l'intervalle | 25 | 40 % | **+140 $** | +31 % | −111 $ | 6 |
| milieu de l'intervalle — appr. | 15 | 33 % | **+123 $** | +45 % | −74 $ | 4 |
| milieu de l'intervalle — valid. | 10 | 50 % | **+17 $** | +10 % | −74 $ | 2 |
| proche du prochain prix attendu (> 2/3) | 39 | 44 % | **+1'204 $** | +157 % | −106 $ | 4 |
| proche du prochain prix attendu (> 2/3) — appr. | 22 | 41 % | **+598 $** | +162 % | −106 $ | 4 |
| proche du prochain prix attendu (> 2/3) — valid. | 17 | 47 % | **+606 $** | +152 % | −73 $ | 2 |

| Phase | Signaux | Acheter tout de suite | Attendre le prochain Chainlink |
|---|---|---|---|
| juste après un prix Chainlink (< 1/3 de l'intervalle) | 73 | +819 $ | +595 $ |
| proche du prochain prix attendu (> 2/3) | 39 | +1'204 $ | +698 $ |
| milieu de l'intervalle | 25 | +140 $ | +375 $ |

### Idées 5-6. Âge du désaccord au moment du signal (naissance = dernier instant où l'avantage était < 0,05)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 0 prix Chainlink depuis la naissance | 52 | 40 % | **+435 $** | +45 % | −89 $ | 5 |
| 0 prix Chainlink depuis la naissance — appr. | 33 | 39 % | **+208 $** | +36 % | −89 $ | 3 |
| 0 prix Chainlink depuis la naissance — valid. | 19 | 42 % | **+227 $** | +57 % | −75 $ | 3 |
| 1 prix Chainlink depuis la naissance | 22 | 45 % | **+109 $** | +20 % | −220 $ | 2 |
| 1 prix Chainlink depuis la naissance — appr. | 11 | 45 % | **+219 $** | +95 % | −53 $ | 2 |
| 1 prix Chainlink depuis la naissance — valid. | 11 | 45 % | **−111 $** | -36 % | −187 $ | 2 |
| 2+ prix Chainlink depuis la naissance | 66 | 50 % | **+1'780 $** | +134 % | −112 $ | 3 |
| 2+ prix Chainlink depuis la naissance — appr. | 38 | 45 % | **+870 $** | +126 % | −112 $ | 3 |
| 2+ prix Chainlink depuis la naissance — valid. | 28 | 57 % | **+909 $** | +144 % | −106 $ | 2 |
| désaccord né il y a < 1 s (saut) | 38 | 53 % | **+293 $** | +38 % | −293 $ | 5 |
| désaccord né il y a < 1 s (saut) — appr. | 21 | 57 % | **+508 $** | +146 % | −8 $ | 4 |
| désaccord né il y a < 1 s (saut) — valid. | 17 | 47 % | **−216 $** | -51 % | −293 $ | 4 |
| né il y a 1-5 s | 30 | 43 % | **+385 $** | +59 % | −226 $ | 8 |
| né il y a 1-5 s — appr. | 18 | 33 % | **+138 $** | +36 % | −226 $ | 8 |
| né il y a 1-5 s — valid. | 12 | 58 % | **+247 $** | +92 % | −53 $ | 2 |
| né il y a > 5 s (montée progressive) | 72 | 43 % | **+1'645 $** | +117 % | −137 $ | 7 |
| né il y a > 5 s (montée progressive) — appr. | 43 | 40 % | **+651 $** | +86 % | −92 $ | 3 |
| né il y a > 5 s (montée progressive) — valid. | 29 | 48 % | **+994 $** | +153 % | −137 $ | 7 |

| Âge | Signaux | Acheter tout de suite | Attendre le prochain Chainlink |
|---|---|---|---|
| né il y a > 5 s (montée progressive) | 72 | +1'645 $ | +1'363 $ |
| désaccord né il y a < 1 s (saut) | 38 | +293 $ | −183 $ |
| né il y a 1-5 s | 30 | +385 $ | +482 $ |

### Idée 7. Premier franchissement du seuil contre les suivants (mesure seulement, un achat par cycle reste la règle)

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 1er franchissement | 140 | 46 % | **+2'323 $** | +82 % | −160 $ | 5 |
| 1er franchissement — appr. | 82 | 43 % | **+1'298 $** | +87 % | −118 $ | 5 |
| 1er franchissement — valid. | 58 | 50 % | **+1'026 $** | +77 % | −156 $ | 4 |
| 2e franchissement | 79 | 30 % | **+635 $** | +27 % | −410 $ | 11 |
| 2e franchissement — appr. | 50 | 24 % | **+177 $** | +13 % | −410 $ | 11 |
| 2e franchissement — valid. | 29 | 41 % | **+458 $** | +49 % | −255 $ | 6 |
| 3e et suivants | 150 | 39 % | **+3'257 $** | +77 % | −890 $ | 19 |
| 3e et suivants — appr. | 74 | 36 % | **+2'122 $** | +106 % | −519 $ | 19 |
| 3e et suivants — valid. | 76 | 42 % | **+1'135 $** | +51 % | −567 $ | 18 |

## Partie B — jackpots

### Idées 8-10. Pourquoi l'attente du prochain Chainlink abandonne-t-elle des signaux ?

| Ce qui arrive au prochain Chainlink (résultat = achat immédiat) | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| confirmé (on achète après attente) | 53 | 36 % | **+932 $** | +66 % | −186 $ | 5 |
| offre disparue | 2 | 100 % | **+246 $** | +272 % | +0 $ | 0 |
| risque A : le prix Polymarket a monté (proba stable) | 71 | 52 % | **+984 $** | +100 % | −95 $ | 4 |
| risque B : notre probabilité a baissé | 14 | 43 % | **+162 $** | +48 % | −91 $ | 4 |

Regret asymétrique (idée 10) : l'attente évite +554 $ de pertes mais fait manquer +1'945 $ de gains (achats immédiats des signaux abandonnés).

### Idée 11. ADN des jackpots : jackpots contre perdants au même prix (≤ 0,20 $), mesures connues à l'achat

| Mesure | Jackpots | Perdants bon marché | Écart significatif ? |
|---|---|---|---|
| prix | 0.134 | 0.112 | non (t = +1.7) |
| proba | 0.402 | 0.356 | oui (t = +2.1) |
| avantage | 0.268 | 0.244 | non (t = +1.3) |
| distance_z | 0.282 | 0.383 | oui (t = -2.1) |
| restant | 68.324 | 59.259 | oui (t = +2.3) |
| age_cl | 0.366 | 0.555 | non (t = -1.7) |
| var_prix_3s | -0.017 | 0.002 | non (t = -0.7) |
| var_proba_3s | 0.144 | 0.147 | non (t = -0.1) |
| quantite | 183.333 | 173.574 | non (t = +0.1) |

18 jackpots, 47 perdants à 0,20 $ ou moins.

### Idée 12. Concentration des gains

| Retirer les | Gains retirés | Part du total | Résultat restant |
|---|---|---|---|
| 1 plus gros | +401 $ | 17 % | +1'922 $ |
| 5 plus gros | +1'263 $ | 54 % | +1'060 $ |
| 10 plus gros | +2'143 $ | 92 % | +180 $ |
| 20 plus gros | +3'109 $ | 134 % | −785 $ |

## Partie C — exécution

### Idées 14-15. Capacité : la quantité affichée au meilleur vendeur suffit-elle pour 50 $ ?

- Montant réellement achetable au meilleur vendeur : médiane **10.1 $**, moyenne 20.2 $ ; 50 $ complets dans 33 signaux sur 140.
- Capital réellement engagé par la référence : 2833 $ pour 140 achats (au lieu de 7000 $ prévus).

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| 10 à 49 $ | 37 | 46 % | **+820 $** | +87 % | −129 $ | 4 |
| 10 à 49 $ — appr. | 20 | 50 % | **+537 $** | +101 % | −96 $ | 4 |
| 10 à 49 $ — valid. | 17 | 41 % | **+282 $** | +69 % | −129 $ | 4 |
| 50 $ complets | 33 | 48 % | **+1'362 $** | +83 % | −210 $ | 4 |
| 50 $ complets — appr. | 16 | 44 % | **+634 $** | +79 % | −158 $ | 3 |
| 50 $ complets — valid. | 17 | 53 % | **+728 $** | +86 % | −208 $ | 4 |
| moins de 10 $ disponibles | 70 | 44 % | **+142 $** | +59 % | −37 $ | 5 |
| moins de 10 $ disponibles — appr. | 46 | 39 % | **+127 $** | +79 % | −37 $ | 5 |
| moins de 10 $ disponibles — valid. | 24 | 54 % | **+15 $** | +19 % | −18 $ | 3 |

Idée 15 : espérance en $ (quantité × (proba − prix − frais)) moyenne 25.49 $ ; corrélation avec le résultat réel +0.18 ; somme des espérances +3'569 $ contre résultat réel +2'323 $.

### Idée 16. Budget de latence : ce qui change si l'ordre arrive plus tard

| Délai | Prix vendeur moyen | Quantité médiane | Proba moyenne (notre côté) | Offre disparue | Avantage < 0,20 | Résultat (50 $ max, quantité affichée) |
|---|---|---|---|---|---|---|
| 0 s | 0.251 | 62 | 0.512 | 0 | 0 | +2'323 $ |
| 0.25 s | 0.336 | 88 | 0.513 | 0 | 68 | +2'845 $ |
| 0.5 s | 0.358 | 129 | 0.511 | 0 | 87 | +2'486 $ |
| 1 s | 0.379 | 174 | 0.511 | 0 | 99 | +731 $ |
| 2 s | 0.376 | 220 | 0.498 | 2 | 100 | +1'633 $ |

### Idée 17. Remonter dans le carnet : les niveaux au-delà du meilleur vendeur ne sont pas dans les données enregistrées (1 niveau par côté). Le fantôme corrigé enregistre 8 niveaux à ses achats ; à ajouter au TWAP fin si tu le décides.

## Partie D — achat immédiat, fractionné ou confirmé (même budget 50 $, quantité affichée à chaque instant)

| Politique | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max | Jackpots conservés |
|---|---|---|---|---|---|---|---|
| A — 50 $ immédiats (référence) | 140 | 46 % | **+2'323 $** | +82 % | −160 $ | 5 | 100 % |
| A — 50 $ immédiats (référence) — appr. | 82 | 43 % | **+1'298 $** | +87 % | −118 $ | 5 | 52 % |
| A — 50 $ immédiats (référence) — valid. | 58 | 50 % | **+1'026 $** | +77 % | −156 $ | 4 | 48 % |
| B — 35 $ immédiats + 15 $ si confirmé | 140 | 46 % | **+2'362 $** | +81 % | −141 $ | 5 | 116 % |
| B — 35 $ immédiats + 15 $ si confirmé — appr. | 82 | 43 % | **+1'211 $** | +80 % | −126 $ | 5 | 58 % |
| B — 35 $ immédiats + 15 $ si confirmé — valid. | 58 | 50 % | **+1'151 $** | +83 % | −141 $ | 4 | 58 % |
| C — 15 $ immédiats + 35 $ si confirmé | 140 | 46 % | **+2'159 $** | +89 % | −169 $ | 5 | 119 % |
| C — 15 $ immédiats + 35 $ si confirmé — appr. | 82 | 43 % | **+903 $** | +77 % | −136 $ | 5 | 56 % |
| C — 15 $ immédiats + 35 $ si confirmé — valid. | 58 | 50 % | **+1'256 $** | +101 % | −169 $ | 4 | 63 % |
| attente complète (50 $ si confirmé) | 53 | 36 % | **+1'661 $** | +112 % | −177 $ | 5 | 93 % |
| attente complète (50 $ si confirmé) — appr. | 27 | 26 % | **+494 $** | +86 % | −112 $ | 4 | 37 % |
| attente complète (50 $ si confirmé) — valid. | 26 | 46 % | **+1'167 $** | +129 % | −177 $ | 5 | 56 % |
| D — mise selon l'avantage : 50 $ × avantage / 0,40 (max 50) | 140 | 46 % | **+1'714 $** | +81 % | −121 $ | 5 | 79 % |
| D — mise selon l'avantage : 50 $ × avantage / 0,40 (max 50) — appr. | 82 | 43 % | **+1'035 $** | +92 % | −74 $ | 5 | 43 % |
| D — mise selon l'avantage : 50 $ × avantage / 0,40 (max 50) — valid. | 58 | 50 % | **+679 $** | +69 % | −121 $ | 4 | 36 % |
| E — mise selon l'avantage prudent (proba − 10 pts) : 50 $ × (avantage − 0,10) / 0,30 | 140 | 46 % | **+1'459 $** | +81 % | −109 $ | 5 | 69 % |
| E — mise selon l'avantage prudent (proba − 10 pts) : 50 $ × (avantage − 0,10) / 0,30 — appr. | 82 | 43 % | **+938 $** | +96 % | −73 $ | 5 | 39 % |
| E — mise selon l'avantage prudent (proba − 10 pts) : 50 $ × (avantage − 0,10) / 0,30 — valid. | 58 | 50 % | **+521 $** | +63 % | −109 $ | 4 | 29 % |
| idée 20 — 90-60 s immédiat ; 60-40 s 15 + 35 confirmé ; 40-20 s rien | 127 | 48 % | **+2'503 $** | +102 % | −161 $ | 5 | 113 % |
| idée 20 — 90-60 s immédiat ; 60-40 s 15 + 35 confirmé ; 40-20 s rien — appr. | 74 | 45 % | **+1'469 $** | +115 % | −142 $ | 5 | 72 % |
| idée 20 — 90-60 s immédiat ; 60-40 s 15 + 35 confirmé ; 40-20 s rien — valid. | 53 | 53 % | **+1'034 $** | +88 % | −120 $ | 4 | 41 % |
| fenêtre 90-40 s seulement, 50 $ immédiats | 127 | 48 % | **+2'297 $** | +87 % | −156 $ | 5 | 100 % |
| fenêtre 90-40 s seulement, 50 $ immédiats — appr. | 74 | 45 % | **+1'230 $** | +92 % | −105 $ | 5 | 52 % |
| fenêtre 90-40 s seulement, 50 $ immédiats — valid. | 53 | 53 % | **+1'067 $** | +82 % | −156 $ | 4 | 48 % |

## Partie E — robustesse des probabilités

### Idées 23-24. Calibration réelle des signaux et seuil de rentabilité

| Prix payé | Achats | Proba moyenne du moteur | Gagnés réellement | Seuil de rentabilité (prix + frais) |
|---|---|---|---|---|
| 0.02-0.10 | 23 | 0.298 | 13 % | 0.062 |
| 0.10-0.20 | 38 | 0.403 | 39 % | 0.154 |
| 0.20-0.35 | 46 | 0.517 | 48 % | 0.264 |
| 0.35-0.60 | 22 | 0.703 | 68 % | 0.445 |
| 0.60-0.98 | 11 | 0.930 | 82 % | 0.682 |

Test de stress (idée 24) : si le moteur surestimait notre côté de N points, quels signaux garderaient un avantage ≥ 0,20 — et que rapportent-ils vraiment ?

| Politique | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max | Jackpots conservés |
|---|---|---|---|---|---|---|---|
| proba − 5 pts : avantage encore ≥ 0,20 | 51 | 49 % | **+841 $** | +88 % | −217 $ | 5 | 42 % |
| proba − 10 pts : avantage encore ≥ 0,20 | 30 | 57 % | **+238 $** | +41 % | −201 $ | 3 | 8 % |
| proba − 15 pts : avantage encore ≥ 0,20 | 13 | 69 % | **+118 $** | +63 % | −95 $ | 3 | 5 % |
| proba × 0,8 (correction proportionnelle, pèse sur les chers) | 26 | 54 % | **+607 $** | +149 % | −136 $ | 2 | 29 % |
| proba − 10 pts seulement entre 40 et 20 s | 128 | 48 % | **+2'306 $** | +87 % | −156 $ | 5 | 100 % |

### Idées 22, 25-26. Même avantage, prix différent

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| prix 0,15-0,35 $ | 67 | 48 % | **+1'689 $** | +122 % | −146 $ | 6 |
| prix 0,15-0,35 $ — appr. | 37 | 38 % | **+566 $** | +83 % | −146 $ | 6 |
| prix 0,15-0,35 $ — valid. | 30 | 60 % | **+1'123 $** | +161 % | −110 $ | 3 |
| prix < 0,15 $ | 40 | 20 % | **+399 $** | +77 % | −232 $ | 7 |
| prix < 0,15 $ — appr. | 28 | 25 % | **+378 $** | +106 % | −201 $ | 7 |
| prix < 0,15 $ — valid. | 12 | 8 % | **+20 $** | +13 % | −105 $ | 7 |
| prix > 0,35 $ | 33 | 73 % | **+235 $** | +25 % | −294 $ | 3 |
| prix > 0,35 $ — appr. | 17 | 82 % | **+353 $** | +78 % | −51 $ | 2 |
| prix > 0,35 $ — valid. | 16 | 62 % | **−118 $** | -25 % | −246 $ | 3 |

## Partie F — erreurs du marché (toutes les cotations, une par cycle, par côté et par case)

### Idées 27, 30. Carte : temps restant × prix × distance au seuil (|z| du moteur) — gagné − prix − frais, en points (appr. / valid.)

| Prix | Distance | 90-60 s | 60-40 s | 40-20 s |
|---|---|---|---|---|
| < 0,15 $ | proche (|z| < 1) | +0.6 / +3.3 | +4.8 / +3.2 | +4.8 / -0.9 |
| < 0,15 $ | loin (|z| ≥ 1) | -0.3 / -1.8 | -0.8 / -1.0 | -1.7 / -0.6 |
| 0,15-0,50 $ | proche (|z| < 1) | -1.4 / +0.4 | +1.0 / +1.3 | -1.8 / -7.9 |
| 0,15-0,50 $ | loin (|z| ≥ 1) | +4.4 / -7.0 | +3.0 / -1.9 | — / — |
| > 0,50 $ | proche (|z| < 1) | -3.6 / -3.9 | -5.6 / -4.8 | -3.0 / +1.9 |
| > 0,50 $ | loin (|z| ≥ 1) | -1.7 / +0.9 | -1.1 / -1.4 | +2.5 / +1.3 |

### Idées 29, 31-32. Qui a raison selon le prix et la distance (Brier, une mesure par seconde, 90-20 s)

| Groupe | Mesures | Moteur original | Sauts | Carnet |
|---|---|---|---|---|
| côté bon marché < 10 c (queues) | 9870 | 0.0371 | 0.0352 | 0.0347 |
| 10-30 c | 5871 | 0.1663 | 0.1655 | 0.1711 |
| 30-50 c (incertain) | 2476 | 0.2393 | 0.2423 | 0.2456 |
| |z| < 0,5 | 3804 | 0.2284 | 0.2271 | 0.2371 |
| |z| 0,5-1,5 | 8545 | 0.1154 | 0.1142 | 0.1124 |
| |z| ≥ 1,5 | 5868 | 0.0137 | 0.0135 | 0.0158 |

## Partie G — le marché sait-il quelque chose ? (mesures avant l'achat)

### Idées 33-34. Trajectoire du prix de notre côté sur les 10 s avant le signal

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| chute rapide (≥ 10 c en 10 s) | 22 | 50 % | **+519 $** | +113 % | −164 $ | 3 |
| chute rapide (≥ 10 c en 10 s) — appr. | 9 | 56 % | **+298 $** | +182 % | −32 $ | 3 |
| chute rapide (≥ 10 c en 10 s) — valid. | 13 | 46 % | **+221 $** | +75 % | −164 $ | 3 |
| oscillations (≥ 3 allers-retours de 2 c) | 19 | 58 % | **+269 $** | +47 % | −210 $ | 4 |
| oscillations (≥ 3 allers-retours de 2 c) — appr. | 12 | 67 % | **+374 $** | +119 % | −64 $ | 2 |
| oscillations (≥ 3 allers-retours de 2 c) — valid. | 7 | 43 % | **−105 $** | -41 % | −210 $ | 4 |
| prix stable | 47 | 38 % | **+715 $** | +101 % | −165 $ | 5 |
| prix stable — appr. | 32 | 31 % | **+552 $** | +115 % | −165 $ | 5 |
| prix stable — valid. | 15 | 53 % | **+163 $** | +71 % | −64 $ | 2 |
| remontée (≥ 5 c) | 29 | 45 % | **+379 $** | +84 % | −80 $ | 5 |
| remontée (≥ 5 c) — appr. | 16 | 38 % | **−42 $** | -25 % | −64 $ | 5 |
| remontée (≥ 5 c) — valid. | 13 | 54 % | **+421 $** | +147 % | −80 $ | 2 |

### Idées 35-37, 41. Réaction du carnet aux 3 dernières secondes, comparée à la variation de notre probabilité

| Groupe | Achats | Gagnés | Résultat | Par $ | Creux | Pertes de suite max |
|---|---|---|---|---|---|---|
| carnet CONTRE nous (milieu de notre côté −3 c ou plus) | 42 | 48 % | **+858 $** | +76 % | −149 $ | 3 |
| carnet CONTRE nous (milieu de notre côté −3 c ou plus) — appr. | 25 | 44 % | **+491 $** | +80 % | −74 $ | 3 |
| carnet CONTRE nous (milieu de notre côté −3 c ou plus) — valid. | 17 | 53 % | **+367 $** | +71 % | −149 $ | 2 |
| carnet réagit moins d'1/3 de notre hausse | 64 | 38 % | **+858 $** | +96 % | −290 $ | 8 |
| carnet réagit moins d'1/3 de notre hausse — appr. | 40 | 32 % | **+668 $** | +121 % | −234 $ | 8 |
| carnet réagit moins d'1/3 de notre hausse — valid. | 24 | 46 % | **+190 $** | +55 % | −68 $ | 4 |
| carnet suit (≥ 1/3) | 22 | 64 % | **+247 $** | +57 % | −101 $ | 2 |
| carnet suit (≥ 1/3) — appr. | 11 | 82 % | **+92 $** | +57 % | −42 $ | 1 |
| carnet suit (≥ 1/3) — valid. | 11 | 45 % | **+154 $** | +57 % | −101 $ | 2 |
| idée 37 : nouveau Chainlink en notre faveur ET carnet contre | 18 | 56 % | **+567 $** | +128 % | −96 $ | 3 |
| idée 37 : nouveau Chainlink en notre faveur ET carnet contre — appr. | 11 | 55 % | **+261 $** | +95 % | −96 $ | 3 |
| idée 37 : nouveau Chainlink en notre faveur ET carnet contre — valid. | 7 | 57 % | **+306 $** | +181 % | −26 $ | 1 |
| notre proba n'a pas monté (le désaccord vient du prix) | 6 | 33 % | **+197 $** | +77 % | −111 $ | 3 |
| notre proba n'a pas monté (le désaccord vient du prix) — appr. | 3 | 0 % | **−111 $** | -105 % | −111 $ | 3 |
| notre proba n'a pas monté (le désaccord vient du prix) — valid. | 3 | 67 % | **+308 $** | +206 % | −53 $ | 1 |

### Idée 38. Deux erreurs distinctes du modèle

- A : notre probabilité baisse de plus de 15 points dans les 5 s : 23 signaux sur 140, dont 5 gagnés quand même.
- B : le contrat perd au règlement : 76 signaux ; parmi eux, 18 avaient d'abord connu la révision A.

### Idée 42. Modèle B = moteur et carnet mélangés à parts égales (poids fixé d'avance, pas optimisé) — Brier par temps restant

| Temps restant | Moteur | Carnet | Mélange 50/50 |
|---|---|---|---|
| 60-90 s | 0.1110 | 0.1132 | 0.1104 |
| 40-60 s | 0.1034 | 0.1052 | 0.1012 |
| 20-40 s | 0.0810 | 0.0733 | 0.0724 |