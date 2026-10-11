# Bot95 — H807–H810 : profondeur, meilleur prix, petits flux, calme — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 17:52 UTC. 82 cycles enregistrés à Dublin ; 13955 offres fictives (apprentissage 7032 / test 6923 ; coupure 11.10 12:10 UTC). Moteur : 20 $ au meilleur acheteur, toutes les 2 s, vie 5 s, latence 14 ms, 3 bornes de file. Aucun ordre, aucun fantôme modifié.

## 1. H807 — Effet de la profondeur et de la place dans la file (tous les cycles, file centrale)

| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |
|---|---|---|---|---|---|---|
| profondeur au meilleur 0–50 parts | 3055 | 85 % | -151.5 [-272.3 ; -20.2] | -11.5 % | -1.44 / -1.70 / -1.84 / -1.59 | 78 % |
| profondeur au meilleur 50–200 parts | 4730 | 70 % | -88.8 [-192.0 ; +26.1] | -8.7 % | -1.30 / -1.59 / -1.53 / -1.52 | 73 % |
| profondeur au meilleur 200–1000 parts | 4647 | 50 % | -4.8 [-79.7 ; +77.7] | -0.6 % | -1.79 / -2.13 / -2.14 / -1.97 | 77 % |
| profondeur au meilleur 1000–∞ parts | 1523 | 37 % | -41.7 [-124.9 ; +46.9] | -7.9 % | -2.60 / -2.82 / -2.64 / -2.67 | 71 % |

**Priorité hypothétique** (même offre, file devant nous = 100 % / 50 % / 0 % de l'affiché ; 0 % = premier dans la file)

| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |
|---|---|---|---|---|---|---|
| 100 % de la file devant nous | 13955 | 63 % | -69.4 [-148.9 ; +18.6] | -7.3 % | -1.52 / -1.81 / -1.82 / -1.70 | 75 % |
| 50 % de la file devant nous | 13955 | 65 % | -65.9 [-147.6 ; +24.8] | -6.7 % | -1.52 / -1.81 / -1.82 / -1.70 | 75 % |
| 0 % de la file devant nous | 13955 | 83 % | -55.6 [-148.9 ; +46.2] | -4.7 % | -1.52 / -1.81 / -1.82 / -1.70 | 72 % |

## 2. H808 — Part du temps passée au meilleur prix (description, mesurée après coup)

| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |
|---|---|---|---|---|---|---|
| au meilleur 0–25 % du temps | 2628 | 14 % | +8.4 [-10.7 ; +30.4] | +4.9 % | +3.52 / +5.17 / +5.56 / +6.53 | 61 % |
| au meilleur 25–75 % du temps | 3557 | 57 % | +82.6 [+11.1 ; +163.7] | +10.7 % | -0.55 / +1.02 / +1.41 / +1.61 | 68 % |
| au meilleur 75–99 % du temps | 1787 | 83 % | -147.8 [-269.3 ; -4.2] | -11.2 % | -1.58 / -1.97 / -1.54 / -1.75 | 80 % |
| au meilleur 99–100 % du temps | 5983 | 82 % | -170.6 [-302.0 ; -23.5] | -13.4 % | -1.95 / -2.76 / -3.01 / -2.85 | 78 % |

## 3. H809 — Régime de petites transactions récentes (10 s avant la pose)

| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |
|---|---|---|---|---|---|---|
| aucune transaction | 88 | 0 % | +0.0 [+nan ; +nan] | +nan % | +nan / +nan / +nan / +nan | nan % |
| taille moyenne < 10 $ | 8397 | 63 % | -113.0 [-170.9 ; -43.5] | -12.3 % | -1.61 / -1.86 / -1.91 / -1.86 | 73 % |
| 10–50 $ | 5431 | 64 % | -6.9 [-136.1 ; +131.6] | -0.7 % | -1.42 / -1.76 / -1.73 / -1.54 | 78 % |
| ≥ 50 $ | 39 | 64 % | +443.6 [-426.7 ; +1612.0] | +49.4 % | -0.91 / -1.06 / -0.44 / +3.16 | 70 % |

## 4. Effet de la volatilité (30 s avant la pose)

| Groupe | Offres | Remplies | P&L / offre (c) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s (c) | Fill moyen (part de l'offre) |
|---|---|---|---|---|---|---|
| volatilité 0–1 c | 773 | 45 % | +87.3 [-117.6 ; +324.0] | +17.0 % | -1.14 / -1.56 / -1.75 / -1.11 | 57 % |
| volatilité 1–2 c | 2711 | 55 % | -130.1 [-213.4 ; -36.2] | -18.4 % | -1.36 / -1.68 / -1.69 / -1.24 | 64 % |
| volatilité 2–4 c | 4511 | 62 % | -60.7 [-156.6 ; +51.3] | -6.6 % | -1.35 / -1.60 / -1.55 / -1.39 | 74 % |
| volatilité 4–∞ c | 5889 | 70 % | -65.3 [-180.5 ; +49.8] | -5.8 % | -1.71 / -1.99 / -2.00 / -2.06 | 81 % |

## 5. H810 — Politiques comparées (seuils choisis sur l'apprentissage, mesurés une fois sur le test)

Grille : volatilité < 1 / 2 / 4 c / sans ; profondeur ≥ 0 / 100 / 300 / 1 000 parts ; taille moyenne récente < 10 / 50 $ / sans (48 réglages). **Retenu sur l'apprentissage : volatilité < 1 c, profondeur ≥ 300 parts, taille récente < ∞ $.**

### TEST (cycles non vus)

| Politique | File | Offres | Remplies | P&L / offre (c, IC 90 %) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s | Drawdown ($) | P&L total ($) |
|---|---|---|---|---|---|---|---|---|
| moteur sans filtre | prudente | 6923 | 3788 | -116.4 [-210.5 ; -3.0] | -13.2 % | -1.89 / -2.03 / -2.03 / -1.87 | 11142 | -8056 |
| moteur sans filtre | centrale | 6923 | 4453 | -101.7 [-212.3 ; +34.9] | -10.1 % | -1.53 / -1.73 / -1.73 / -1.54 | 11128 | -7040 |
| moteur sans filtre | optimiste | 6923 | 6630 | -18.2 [-263.7 ; +261.3] | -1.0 % | +0.37 / +0.28 / +0.35 / +0.52 | 14625 | -1261 |
| calme + profond (H810) | prudente | 172 | 32 | +82.6 [-145.9 ; +311.0] | +26.7 % | -4.42 / -4.30 / -4.16 / -3.45 | 133 | +142 |
| calme + profond (H810) | centrale | 172 | 42 | +87.9 [-137.4 ; +323.5] | +23.3 % | -3.79 / -3.95 / -3.77 / -3.15 | 145 | +151 |
| calme + profond (H810) | optimiste | 172 | 130 | +218.0 [-210.1 ; +726.9] | +14.8 % | -0.11 / -0.45 / -0.37 / -0.45 | 168 | +375 |
| profondeur ≥ 300 seule | prudente | 2345 | 815 | -54.0 [-134.2 ; +36.4] | -9.4 % | -2.84 / -3.12 / -2.97 / -2.66 | 2331 | -1265 |
| profondeur ≥ 300 seule | centrale | 2345 | 1016 | -22.7 [-139.6 ; +124.7] | -3.3 % | -2.25 / -2.60 / -2.47 / -2.00 | 2466 | -533 |
| profondeur ≥ 300 seule | optimiste | 2345 | 2116 | +156.5 [-166.4 ; +543.9] | +8.8 % | +0.75 / +0.58 / +0.47 / +0.61 | 3789 | +3669 |
| volatilité < 2 c seule | prudente | 1519 | 648 | -67.7 [-212.4 ; +91.8] | -11.2 % | -1.63 / -1.76 / -1.61 / -1.19 | 2166 | -1029 |
| volatilité < 2 c seule | centrale | 1519 | 820 | -49.6 [-210.7 ; +130.6] | -6.9 % | -1.34 / -1.58 / -1.44 / -1.04 | 2006 | -753 |
| volatilité < 2 c seule | optimiste | 1519 | 1397 | +22.8 [-317.0 ; +401.9] | +1.3 % | +0.41 / +0.32 / +0.36 / +0.38 | 2407 | +346 |

### apprentissage

| Politique | File | Offres | Remplies | P&L / offre (c, IC 90 %) | P&L / $ immobilisé | Markout 1 / 3 / 5 / 10 s | Drawdown ($) | P&L total ($) |
|---|---|---|---|---|---|---|---|---|
| moteur sans filtre | prudente | 7032 | 3642 | -34.7 [-135.8 ; +75.1] | -4.6 % | -1.86 / -2.20 / -2.24 / -2.24 | 5514 | -2440 |
| moteur sans filtre | centrale | 7032 | 4317 | -37.7 [-148.1 ; +80.3] | -4.2 % | -1.52 / -1.90 / -1.92 / -1.87 | 5948 | -2649 |
| moteur sans filtre | optimiste | 7032 | 6423 | +142.4 [-118.5 ; +454.1] | +8.2 % | +0.24 / +0.19 / +0.24 / +0.22 | 7041 | +10016 |
| calme + profond (H810) | prudente | 127 | 30 | +238.3 [-126.4 ; +692.8] | +91.3 % | -1.78 / -1.96 / -3.51 / -1.76 | 110 | +303 |
| calme + profond (H810) | centrale | 127 | 40 | +243.6 [-205.3 ; +775.7] | +64.5 % | -1.01 / -1.19 / -2.29 / +0.13 | 179 | +309 |
| calme + profond (H810) | optimiste | 127 | 122 | +693.1 [-496.8 ; +2279.3] | +37.7 % | +0.35 / +0.21 / +0.05 / +0.45 | 455 | +880 |
| profondeur ≥ 300 seule | prudente | 2427 | 863 | +16.1 [-55.3 ; +97.8] | +3.0 % | -2.78 / -3.15 / -2.96 / -2.71 | 1274 | +390 |
| profondeur ≥ 300 seule | centrale | 2427 | 1092 | +11.4 [-66.8 ; +98.0] | +1.7 % | -2.10 / -2.55 / -2.32 / -2.10 | 1468 | +278 |
| profondeur ≥ 300 seule | optimiste | 2427 | 2171 | +253.5 [-29.0 ; +612.1] | +14.6 % | +0.56 / +0.47 / +0.91 / +0.99 | 1869 | +6153 |
| volatilité < 2 c seule | prudente | 1965 | 821 | -104.3 [-203.1 ; +5.9] | -20.7 % | -1.61 / -2.07 / -2.25 / -1.81 | 2735 | -2050 |
| volatilité < 2 c seule | centrale | 1965 | 1029 | -106.8 [-224.9 ; +40.8] | -17.0 % | -1.29 / -1.71 / -1.91 / -1.36 | 2912 | -2100 |
| volatilité < 2 c seule | optimiste | 1965 | 1722 | +235.8 [-292.9 ; +913.8] | +14.8 % | +0.38 / +0.35 / +0.56 / +0.85 | 4101 | +4633 |

## 6. Robustesse

- File prudente (test) : offres gardées par le filtre +82.56 c/offre [-141.81 ; +312.62] contre offres écartées -121.43 c/offre [-212.73 ; -5.15].
- File centrale (test) : offres gardées par le filtre +87.87 c/offre [-149.84 ; +336.94] contre offres écartées -106.52 c/offre [-221.32 ; +28.13].
- File optimiste (test) : offres gardées par le filtre +217.95 c/offre [-223.92 ; +723.53] contre offres écartées -24.23 c/offre [-259.03 ; +260.47].

Lecture : un mécanisme exploitable doit (1) rester positif sur le test, (2) avec un IC par cycles au-dessus de 0, (3) sous la file prudente aussi. Sinon, simple corrélation historique.

## Limites
- Une journée, ~80 cycles.
- Carnet suivi à ±3 c du meilleur prix ; fills datés au premier fill pour les markouts.
- Les offres fictives n'agissent pas sur le carnet ; la priorité « 0 % devant » est hypothétique (il faudrait être là avant les autres).
