# Bot95 — Counterparty Intelligence Lab, H724–H765 — PRÉLIMINAIRE

Généré le 11.10.2026 14:38 UTC. Marchés lus avant le 13.10 : 300 dont 88 tronqués (≥ 10 000 exécutions, exclus). Signaux Bot95 réglés : 283 ; sur des marchés complets : **161**, répartis sur **37 cycles** (les variantes du même cycle ne sont pas indépendantes : les intervalles de confiance rééchantillonnent des cycles). Séparation chronologique : apprentissage = cycles < 11.10 09:10 UTC, test = après. Cycles avec carnet Dublin (Reverse) : 16. Les trois wallets : `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c`, `0x4c9497941333332d29f1c235dd23200f3623ffad`, `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b`.

**Biais de sélection à garder en tête :** les trois wallets ont été repérés sur ces mêmes signaux (E1). Tout résultat « avec les trois wallets » est donc en partie dans l'échantillon. Le contrôle honnête est la version chronologique (wallets choisis sur la première moitié, mesurés sur la seconde) et le placebo.

## 1. H724 / Test A — Les signaux et leurs correspondances maker (livrables 1, 2, 3)

| Catégorie (sur 161 signaux) | Signaux | Lecture |
|---|---|---|
| Au moins une vente maker du côté Bot95 au prix du signal ou mieux, de −1 s à +10 s | 157 | correspondance « dans les 10 s » (c'est le chiffre 157 d'E1, recalculé) |
| … dont au même prix exact | 122 | |
| … dans la seconde de la décision (contemporaine, ordre inconnu à la seconde) | 21 | ambigu : avant ou après nous |
| … dans la seconde précédente | 14 | l'offre a été servie AVANT nous (par un autre preneur) |
| … uniquement après la seconde de décision | 127 | n'est pas une information disponible au signal |
| Offre présente au signal (carnet Dublin, quantité au prix du signal) | 161 | fait mesuré |
| Encore achetable 100 ms après | 145 | borne optimiste |
| **Encore achetable 250 ms après (exécution simulée retenue)** | 127 | délai preneur 150 ms + trajet |
| Impossible après latence (plus rien au prix) | 34 | |

Une correspondance dans les 10 s **n'est pas** un remplissage garanti : la plupart des ventes maker servent d'autres preneurs.

**Wallets réellement impliqués (livrable 3)** — top 12 par nombre de signaux servis

| Wallet | Signaux servis | Parts | dont « achète l'autre côté » | Marchés actifs | Résultat global par $ |
|---|---|---|---|---|---|
| `0x85a186d1…` | 72 | 927 | 100 % | 210 | -2.1 % |
| `0xf9b7876b…` ★ | 68 | 1159 | 100 % | 209 | +5.9 % |
| `0x322b2e7c…` | 65 | 798 | 100 % | 210 | -1.8 % |
| `0x4c949794…` ★ | 64 | 1033 | 100 % | 212 | +5.8 % |
| `0x18c18e0c…` | 60 | 821 | 100 % | 177 | +0.7 % |
| `0x568b0798…` ★ | 59 | 903 | 100 % | 212 | +4.6 % |
| `0x41e2e1cc…` | 51 | 1462 | 100 % | 212 | -2.2 % |
| `0x809f2752…` | 50 | 547 | 0 % | 212 | +0.7 % |
| `0x1dd2a69e…` | 49 | 426 | 0 % | 212 | +0.4 % |
| `0xa3338de3…` | 49 | 542 | 0 % | 211 | +0.4 % |
| `0xaa1a4f31…` | 48 | 1105 | 100 % | 207 | -2.1 % |
| `0x5916ce25…` | 43 | 493 | 0 % | 211 | +2.1 % |

Nombre total de wallets distincts : 280. ★ = les trois wallets étudiés.

## 2. Test B — Les trois wallets : inventaire, coût, profits (livrables 4, 5, 6, 7)

Méthode : inventaire reconstruit marché par marché (premier entré, premier sorti). Une vente sans stock = **split déduit** : la jambe vendue coûte son prix de vente, l'autre jambe (gardée) coûte 1 − p. Économiquement, c'est identique à **acheter le côté opposé** à 1 − p. Transferts et splits hors marché non vus (activités pas encore collectées) → les inventaires peuvent être incomplets.

| Groupe | Résultat total | dont réalisé sur ventes depuis stock | Parts vendues | depuis stock | via split (≡ achat de l'autre côté) | Prix moyen de vente (stock) | Coût moyen (stock) | Ventes qui réduisent l'exposition |
|---|---|---|---|---|---|---|---|---|
| autres makers qui servent nos signaux | +33722 $ | +3421 $ | 482207 | 52 % | 48 % | 0.560 | 0.546 | 47 % |

**Profil des trois wallets (tous marchés complets)** — achats / ventes, paires et jambes résiduelles

| Wallet | Achats (parts) | Ventes (parts) | Coût moyen d'une paire Up+Down | Parts appariées | Résultat des paires | Résultat des jambes résiduelles | Total |
|---|---|---|---|---|---|---|---|
| `0xf9b7876b…` | 56643 | 0 | 1.048 | 19924 | -964 $ | +2908 $ | +1944 $ |
| `0x4c949794…` | 54638 | 0 | 1.047 | 19613 | -918 $ | +2736 $ | +1818 $ |
| `0x568b0798…` | 51534 | 0 | 1.050 | 18278 | -916 $ | +2276 $ | +1360 $ |

Taux de gain des signaux : tous 27 % (prix moyen 0.22) ; encore achetables à 250 ms 22 % (prix 0.21) ; partis avant 250 ms 44 % (prix 0.24).


**Les ventes des trois wallets au moment des signaux (de −1 s à +10 s)**

| Type de vente | Ventes | Parts | Coût moyen du stock vendu | Prix moyen | Gain réalisé/part | Billet vendu gagnant | Résultat final du wallet dans ces marchés |
|---|---|---|---|---|---|---|---|
| achat de l'autre côté (mint) | 465 | 3095 | — | 0.201 | — | 20 % | -127 $ |
Rendement de l'acheteur sur ces billets (Bot95 au même prix) : +0.6 % par $ (avant frais), contre +21.5 % sur tous les signaux.

## 3. H728 — Les trois wallets vendent-ils de moins bons billets que les autres makers ? (livrable 7)

Toutes les ventes maker (vendre X ou acheter l'autre côté) de tous les marchés complets ; rendement de l'ACHETEUR au règlement ; comparaison à prix (tranche de 0,10) × minute du cycle identiques.

- Rendement brut de l'acheteur : face aux trois wallets -7.5 % par $ ; face aux autres makers +0.5 %.
- **Écart à prix et minute identiques : +0.4 points** (IC 90 % par cycles [-2.0 ; +2.8]). Négatif = les trois wallets vendent des billets plus mauvais pour l'acheteur.

## 4. Test C — Flux observés AVANT les signaux (livrables 8, 9)

Variables calculées uniquement avec des transactions datées ≤ seconde de décision − 1 (− délai de disponibilité D). Flux net vers le côté Bot95 (+ = le groupe achète le côté Bot95 ou vend l'autre ; − = il vend notre côté). Inventaire = position nette (côté Bot95 − autre côté) depuis l'ouverture du marché.

Erreur Bot95 = gagné (1/0) − probabilité du modèle. Négatif = Bot95 surestime.

| Groupe | Fenêtre | Signaux avec flux contre nous | erreur | Signaux flux nul | erreur | Signaux flux pour nous | erreur | Écart contre − reste (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| 3 wallets (makers) | 60 s | 110 | -0.20 | 6 | -0.33 | 45 | -0.15 | -0.03 [-0.22 ; +0.15] |
| 3 wallets (makers) | 30 s | 108 | -0.18 | 11 | -0.17 | 42 | -0.23 | +0.03 [-0.15 ; +0.22] |
| 3 wallets (makers) | 10 s | 89 | -0.24 | 46 | -0.09 | 26 | -0.22 | -0.10 [-0.25 ; +0.04] |
| 3 wallets (makers) | 3 s | 49 | -0.31 | 96 | -0.14 | 16 | -0.16 | -0.17 [-0.33 ; -0.02] |
| 3 wallets (makers) | 1 s | 14 | -0.41 | 140 | -0.18 | 7 | -0.04 | -0.24 [-0.37 ; -0.07] |
| 3 wallets (makers) | inventaire | 109 | -0.19 | 0 | +nan | 52 | -0.20 | +0.01 [-0.20 ; +0.21] |
| tous les makers | 60 s | 59 | -0.19 | 0 | +nan | 102 | -0.20 | +0.01 [-0.18 ; +0.20] |
| tous les makers | 30 s | 56 | -0.20 | 0 | +nan | 105 | -0.19 | -0.00 [-0.15 ; +0.16] |
| tous les makers | 10 s | 51 | -0.18 | 1 | +0.50 | 109 | -0.21 | +0.02 [-0.11 ; +0.17] |
| tous les makers | 3 s | 60 | -0.16 | 2 | +0.08 | 99 | -0.22 | +0.05 [-0.08 ; +0.18] |
| tous les makers | 1 s | 35 | -0.26 | 63 | -0.20 | 63 | -0.15 | -0.08 [-0.22 ; +0.04] |
| tous les makers | inventaire | 58 | -0.18 | 0 | +nan | 103 | -0.20 | +0.02 [-0.22 ; +0.23] |
| tous les preneurs | 60 s | 102 | -0.20 | 0 | +nan | 59 | -0.19 | -0.01 [-0.20 ; +0.17] |
| tous les preneurs | 30 s | 105 | -0.19 | 0 | +nan | 56 | -0.20 | +0.00 [-0.17 ; +0.16] |
| tous les preneurs | 10 s | 109 | -0.21 | 1 | +0.50 | 51 | -0.18 | -0.04 [-0.19 ; +0.10] |
| tous les preneurs | 3 s | 99 | -0.22 | 2 | +0.08 | 60 | -0.16 | -0.06 [-0.20 ; +0.10] |
| tous les preneurs | 1 s | 63 | -0.15 | 63 | -0.20 | 35 | -0.26 | +0.07 [-0.06 ; +0.20] |
| tous les preneurs | inventaire | 103 | -0.20 | 0 | +nan | 58 | -0.18 | -0.02 [-0.24 ; +0.21] |

## 5. Test D — Calibration avec et sans identité des wallets (livrable 10)

Apprentissage 71 signaux / 18 cycles ; test 90 signaux / 19 cycles (chronologique, aucun signal commun).

| Modèle | Log loss test | Brier test | Log loss apprentissage |
|---|---|---|---|
| Bot95 brut | 0.5966 | 0.2036 | 0.6330 |
| Bot95 recalibré | 0.4927 | 0.1568 | 0.5789 |
| + 3 wallets (30 s + inventaire) | 0.5199 | 0.1704 | 0.5736 |
| + flux global (makers + preneurs 30 s) | 0.4982 | 0.1590 | 0.5736 |
| + les deux | 0.5171 | 0.1687 | 0.5703 |

Gain de log loss apporté par les trois wallets sur le test : -0.0273 (positif = mieux).

## 6. Test G — Placebo : trois wallets tirés au hasard (livrable 15)

- Fenêtre 3 s : écart d'erreur vrais wallets -0.172 ; placebo médiane -0.023 ; part des placebos aussi négatifs ou plus : **11 %** (135 tirages avec ≥ 5 signaux).
- Fenêtre 1 s : écart d'erreur vrais wallets -0.238 ; placebo médiane -0.095 ; part des placebos aussi négatifs ou plus : **12 %** (49 tirages avec ≥ 5 signaux).
- **Version chronologique** (wallets choisis sur l'apprentissage : `0x568b0798…`, `0xf9b7876b…`, `0x4c949794…` ; 3 en commun avec les trois) — écart d'erreur sur le TEST, flux contre nous − reste : 30 s +0.068 (n = 56) ; 10 s -0.198 (n = 45) ; 3 s -0.142 (n = 28) ; 1 s -0.275 (n = 8)

199 makers comparables (actifs sur assez de marchés) ; 200 tirages de trois wallets.

- Gain de log loss test : vrais wallets -0.0273 ; placebo médiane -0.0256, 90e centile +0.0138 ; part des placebos ≥ réel : **52 %**.
- Écart d'erreur Bot95 « flux 30 s contre nous » − reste : vrais wallets +0.034 ; placebo médiane +0.002 ; part des placebos aussi négatifs ou plus : **61 %**.

## 7. Test E — Reverse Bot95 (livrables 11, 17, 18)

A = acheter le côté Bot95 au prix achetable 250 ms après la décision (frais compris, quantité réellement présente). B = acheter le côté OPPOSÉ à son meilleur vendeur 250 ms après (carnet Dublin ; quantité au meilleur niveau ; frais preneur). C = ne rien faire. Mise : 1 part par signal (le P&L par $ est aussi donné).

| Politique | Échantillon | Exécutés | P&L total (parts) | par signal (IC 90 %) | par $ | Taux de gain | Drawdown max | Pire série de pertes | Jackpots (gain à prix ≤ 0,25) |
|---|---|---|---|---|---|---|---|---|---|
| A — côté Bot95 | tous les signaux | 127 | +0.39 | +0.003 [-0.096 ; +0.095] | +1.4 % | 22 % | 4.37 | 21 | 8 |
| B — côté opposé | tous les signaux | 77 | -7.17 | -0.093 [-0.228 ; +0.047] | -12.1 % | 69 % | 8.46 | 6 | 0 |
| C — rien | tous les signaux | 0 | 0 | 0 | — | — | 0 | 0 | 0 |
| A — côté Bot95 | cycles avec carnet Dublin (A et B exécutables) | 58 | +1.30 | +0.022 [-0.121 ; +0.186] | +10.2 % | 24 % | 4.37 | 15 | 2 |
| B — côté opposé | cycles avec carnet Dublin (A et B exécutables) | 58 | -2.97 | -0.051 [-0.212 ; +0.088] | -6.4 % | 76 % | 4.33 | 5 | 0 |
| C — rien | cycles avec carnet Dublin (A et B exécutables) | 0 | 0 | 0 | — | — | 0 | 0 | 0 |
| A — côté Bot95 | test (2e moitié) | 49 | -0.73 | -0.015 [-0.150 ; +0.151] | -6.8 % | 20 % | 4.21 | 15 | 2 |
| B — côté opposé | test (2e moitié) | 49 | -0.88 | -0.018 [-0.164 ; +0.119] | -2.2 % | 80 % | 4.33 | 5 | 0 |
| C — rien | test (2e moitié) | 0 | 0 | 0 | — | — | 0 | 0 | 0 |

Acheter le côté opposé n'est PAS vendre le billet Bot95 : on paie le vendeur opposé + frais, l'écart vendeur-acheteur est payé deux fois.

## 8. Test F — Veto et confirmation par contrepartie, contre un filtre de flux global (livrables 12, 13, 14, 18)

Règles fixées a priori (aucun seuil optimisé) : **veto** = on n'achète pas si le groupe a un flux net CONTRE notre côté sur la fenêtre ; **confirmation** = on n'achète que si le flux est POUR notre côté. Politique de base = A (côté Bot95, 250 ms).

| Filtre | Fenêtre / délai | Signaux gardés | Perdants évités | Gagnants supprimés | Jackpots supprimés | P&L marginal (parts) | IC 90 % | P&L gardé sur le test |
|---|---|---|---|---|---|---|---|---|
| veto 3 wallets | 60 s | 43 / 127 | 70 | 14 | 7 | +2.84 | [-7.16 ; +11.39] | -1.39 |
| veto 3 wallets | 30 s | 46 / 127 | 63 | 18 | 8 | -0.65 | [-12.30 ; +9.71] | -2.22 |
| veto 3 wallets | 10 s | 50 / 127 | 62 | 15 | 6 | +1.04 | [-8.11 ; +9.23] | +0.18 |
| veto 3 wallets | inv | 45 / 127 | 68 | 14 | 7 | +1.28 | [-8.46 ; +9.92] | -2.22 |
| veto 3 wallets | 30 s (D = 2 s) | 47 / 127 | 63 | 17 | 7 | +0.02 | [-10.90 ; +9.77] | -1.81 |
| veto 3 wallets | 30 s (D = 5 s) | 54 / 127 | 57 | 16 | 7 | -0.50 | [-10.83 ; +8.42] | +0.11 |
| veto flux global makers | 30 s | 91 / 127 | 31 | 5 | 2 | +2.72 | [-0.75 ; +6.24] | -1.29 |
| veto flux global preneurs | 30 s | 36 / 127 | 68 | 23 | 6 | -3.11 | [-15.35 ; +7.35] | -2.21 |
| veto flux global makers | 10 s | 92 / 127 | 30 | 5 | 2 | +2.44 | [-1.32 ; +5.86] | -0.37 |
| veto flux global preneurs | 10 s | 36 / 127 | 69 | 22 | 6 | -2.14 | [-11.73 ; +7.97] | -3.13 |
| confirmation 3 wallets | 60 s | 38 / 127 | 74 | 15 | 7 | +3.17 | [-6.63 ; +12.40] | -1.14 |
| confirmation 3 wallets | 30 s | 38 / 127 | 70 | 19 | 8 | +0.00 | [-11.46 ; +10.17] | -1.73 |
| confirmation 3 wallets | 10 s | 19 / 127 | 83 | 25 | 7 | -1.37 | [-13.55 ; +9.61] | -2.04 |
| confirmation 3 wallets | inv | 45 / 127 | 68 | 14 | 7 | +1.28 | [-8.72 ; +10.17] | -2.22 |
| confirmation 3 wallets | 30 s (D = 2 s) | 37 / 127 | 71 | 19 | 8 | +0.12 | [-9.84 ; +10.23] | -1.86 |
| confirmation 3 wallets | 30 s (D = 5 s) | 43 / 127 | 66 | 18 | 8 | -0.25 | [-11.05 ; +8.81] | +0.06 |
| confirmation flux global makers | 30 s | 91 / 127 | 31 | 5 | 2 | +2.72 | [-1.00 ; +6.18] | -1.29 |
| confirmation flux global preneurs | 30 s | 36 / 127 | 68 | 23 | 6 | -3.11 | [-13.68 ; +7.18] | -2.21 |
| confirmation flux global makers | 10 s | 91 / 127 | 30 | 6 | 2 | +1.75 | [-2.45 ; +5.61] | -0.37 |
| confirmation flux global preneurs | 10 s | 35 / 127 | 69 | 23 | 6 | -2.83 | [-14.27 ; +7.13] | -3.13 |

Référence sans filtre : P&L A total +0.39 parts ; sur le test -3.51.

## 9. H727 — Empreinte « même opérateur » (statistique seulement)

| Wallet | Exécutions maker | Taille médiane (parts) | Tailles rondes | Prix médian | Part Up | Part achats | Marchés | Résultat par $ |
|---|---|---|---|---|---|---|---|---|
| `0xf9b7876b…` | 6502 | 7.9 | 42 % | 0.62 | 52 % | 100 % | 209 | +5.9 % |
| `0x4c949794…` | 6009 | 8.9 | 44 % | 0.61 | 50 % | 100 % | 212 | +5.8 % |
| `0x568b0798…` | 5652 | 8.9 | 43 % | 0.61 | 50 % | 100 % | 212 | +4.6 % |

| Paire | Marchés communs (Jaccard) | Secondes communes d'activité | Attendu au hasard (même marchés) |
|---|---|---|---|
| 0xf9b787 / 0x4c9497 | 209 (99 %) | 2187 | 344 |
| 0xf9b787 / 0x568b07 | 209 (99 %) | 2099 | 326 |
| 0x4c9497 / 0x568b07 | 212 (100 %) | 2190 | 319 |

Transferts publics, splits / merges hors marché : **non vérifiés** (activités en cours de collecte). Similarité statistique ≠ contrôle commun.

## 10. H765 — Audit de disponibilité temporelle (livrable 16)

- **Fait** : l'API Data date à la seconde. Une transaction datée de la seconde du signal peut être postérieure → exclue de toutes les variables.
- **Fait** : le flux carnet temps réel de Polymarket donne prix, taille, côté — pas l'adresse des wallets.
- **Hypothèse à mesurer** : l'identité n'arrive qu'avec la chaîne (blocs Polygon ≈ 2 s + délai de soumission) ou l'API Data (délai inconnu). Les fenêtres 1 et 3 s ne sont donc probablement PAS disponibles en direct ; les tests avec D = 2 et 5 s simulent ce retard.
- Les correspondances « dans les 10 s » de la section 1 sont presque toutes postérieures au signal : elles décrivent, elles ne prédisent pas.

## Limites
- Une seule journée, ~37 cycles : puissance statistique faible ; tout est PRÉLIMINAIRE.
- Marchés tronqués exclus (les plus actifs) ; à refaire sur la collecte complète.
- Inventaires sans transferts ni splits hors marché.
- Le choix des trois wallets est in-sample.

## Annexe — Tableau des signaux (livrable 1)

| Cycle (UTC) | Variante | Côté | Prix | Modèle | Restant | Achetable 250 ms | Gagné | P&L/part A | Ventes maker ±10 s | dont 3 wallets | Δt 1re (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 06:50 | V2-F ecart qui grandit | Up | 0.20 | 0.42 | 276 | 50 | non | -0.21 | 216 | 0 | -1.3 |
| 06:50 | V2-F incertitude 0,01  | Up | 0.19 | 0.40 | 208 | 0 | non | — | 53 | 17 | -0.0 |
| 06:50 | desaccord 30 | Up | 0.19 | 0.49 | 208 | 0 | non | — | 53 | 17 | -0.0 |
| 06:50 | desaccord 20 60-180 s | Up | 0.14 | 0.43 | 180 | 130 | non | -0.15 | 453 | 0 | -1.0 |
| 06:55 | V2-F ecart qui grandit | Down | 0.19 | 0.39 | 266 | 263 | non | -0.18 | 435 | 10 | +2.1 |
| 06:55 | desaccord 30 | Down | 0.08 | 0.39 | 194 | 253 | non | -0.09 | 235 | 0 | +6.8 |
| 06:55 | desaccord 20 60-180 s | Down | 0.07 | 0.39 | 180 | 5 | non | -0.07 | 1143 | 0 | -1.0 |
| 07:00 | V2-F incertitude 0,01  | Down | 0.37 | 0.57 | 266 | 0 | non | — | 193 | 41 | +1.6 |
| 07:00 | V2-F ecart qui grandit | Down | 0.28 | 0.50 | 177 | 179 | non | -0.21 | 387 | 20 | +2.1 |
| 07:00 | desaccord 20 60-180 s | Down | 0.28 | 0.50 | 177 | 179 | non | -0.21 | 387 | 20 | +2.1 |
| 07:00 | desaccord 30 | Down | 0.19 | 0.50 | 177 | 263 | non | -0.20 | 144 | 12 | +2.6 |
| 07:05 | V2-F ecart qui grandit | Up | 0.14 | 0.35 | 292 | 357 | non | -0.15 | 198 | 24 | +2.7 |
| 07:05 | desaccord 20 60-180 s | Up | 0.03 | 0.24 | 180 | 77 | non | -0.03 | 79 | 0 | +2.0 |
| 07:10 | V2-F ecart qui grandit | Up | 0.29 | 0.49 | 187 | 45 | non | -0.30 | 188 | 5 | +2.9 |
| 07:10 | V2-F incertitude 0,01  | Up | 0.27 | 0.48 | 183 | 185 | non | -0.28 | 141 | 5 | -0.5 |
| 07:10 | desaccord 20 60-180 s | Up | 0.28 | 0.49 | 180 | 166 | non | -0.29 | 171 | 24 | -1.0 |
| 07:10 | desaccord 30 | Up | 0.14 | 0.45 | 165 | 357 | non | -0.13 | 256 | 36 | +2.9 |
| 07:20 | V2-F ecart qui grandit | Up | 0.27 | 0.48 | 262 | 175 | non | -0.28 | 75 | 12 | +4.3 |
| 07:20 | V2-F incertitude 0,01  | Up | 0.24 | 0.45 | 260 | 208 | non | -0.25 | 150 | 19 | +2.4 |
| 07:20 | desaccord 30 | Up | 0.07 | 0.40 | 196 | 0 | non | — | 47 | 0 | +1.1 |
| 07:20 | desaccord 20 60-180 s | Up | 0.07 | 0.37 | 180 | 207 | non | -0.07 | 181 | 0 | -0.0 |
| 07:25 | V2-F ecart qui grandit | Up | 0.23 | 0.44 | 259 | 217 | non | -0.23 | 155 | 6 | +1.7 |
| 07:25 | desaccord 20 60-180 s | Up | 0.21 | 0.43 | 180 | 238 | non | -0.22 | 135 | 23 | +3.0 |
| 07:25 | desaccord 30 | Up | 0.07 | 0.37 | 169 | 714 | non | -0.07 | 241 | 0 | +3.5 |
| 07:25 | V2-F incertitude 0,01  | Up | 0.25 | 0.46 | 97 | 200 | non | -0.25 | 125 | 24 | -0.6 |
| 07:30 | V2-F ecart qui grandit | Down | 0.26 | 0.47 | 186 | 192 | oui | +0.77 | 89 | 10 | +2.7 |
| 07:30 | desaccord 20 60-180 s | Down | 0.26 | 0.47 | 176 | 192 | oui | +0.73 | 57 | 0 | +2.2 |
| 07:30 | V2-F incertitude 0,01  | Down | 0.21 | 0.42 | 111 | 52 | oui | +0.78 | 188 | 28 | +1.0 |
| 07:30 | desaccord 30 | Down | 0.18 | 0.49 | 105 | 60 | oui | +0.81 | 137 | 16 | +3.2 |
| 07:35 | V2-F ecart qui grandit | Down | 0.27 | 0.48 | 215 | 185 | oui | +0.72 | 27 | 0 | +2.8 |
| 07:35 | V2-F incertitude 0,01  | Down | 0.29 | 0.50 | 185 | 3 | oui | +0.69 | 442 | 36 | -1.0 |
| 07:35 | desaccord 30 | Down | 0.29 | 0.59 | 185 | 3 | oui | +0.69 | 442 | 36 | -1.0 |
| 07:35 | desaccord 20 60-180 s | Up | 0.06 | 0.27 | 177 | 833 | non | -0.06 | 2173 | 72 | +2.6 |
| 07:40 | V2-F ecart qui grandit | Down | 0.24 | 0.44 | 255 | 208 | oui | +0.75 | 97 | 12 | +3.1 |
| 07:40 | desaccord 20 60-180 s | Down | 0.24 | 0.44 | 180 | 208 | oui | +0.75 | 11 | 1 | +6.0 |
| 07:40 | desaccord 30 | Down | 0.14 | 0.45 | 129 | 357 | oui | +0.85 | 99 | 12 | +3.6 |
| 07:40 | V2-F incertitude 0,01  | Down | 0.07 | 0.27 | 107 | 0 | oui | — | 5 | 0 | +2.8 |
| 07:40 | desaccord 20 jeton 0,3 | Down | 0.36 | 0.58 | 107 | 0 | oui | — | 110 | 0 | -1.5 |
| 07:45 | V2-F incertitude 0,01  | Down | 0.36 | 0.57 | 205 | 0 | non | — | 5 | 0 | +1.9 |
| 07:45 | V2-F ecart qui grandit | Down | 0.29 | 0.49 | 96 | 44 | non | -0.30 | 103 | 15 | +2.8 |
| 07:45 | desaccord 20 60-180 s | Down | 0.29 | 0.49 | 96 | 44 | non | -0.30 | 103 | 15 | +2.8 |
| 07:45 | desaccord 30 | Down | 0.19 | 0.49 | 59 | 133 | non | -0.18 | 282 | 0 | +2.0 |
| 07:50 | V2-F ecart qui grandit | Down | 0.30 | 0.50 | 170 | 167 | non | -0.30 | 358 | 36 | +1.9 |
| 07:50 | V2-F incertitude 0,01  | Down | 0.30 | 0.50 | 170 | 167 | non | -0.30 | 358 | 36 | +1.9 |
| 07:50 | desaccord 20 60-180 s | Down | 0.30 | 0.50 | 170 | 167 | non | -0.30 | 358 | 36 | +1.9 |
| 07:50 | desaccord 30 | Down | 0.19 | 0.50 | 130 | 127 | non | -0.19 | 133 | 36 | +2.3 |
| 08:00 | V2-F ecart qui grandit | Down | 0.23 | 0.44 | 289 | 0 | non | — | 104 | 6 | +3.5 |
| 08:00 | desaccord 20 60-180 s | Down | 0.07 | 0.34 | 180 | 157 | non | -0.07 | 318 | 0 | +1.0 |
| 08:00 | desaccord 30 | Down | 0.07 | 0.37 | 173 | 171 | non | -0.07 | 121 | 0 | -0.4 |
| 08:00 | V2-F incertitude 0,01  | Down | 0.14 | 0.34 | 135 | 357 | non | -0.14 | 343 | 7 | +3.1 |
| 08:05 | V2-F incertitude 0,01  | Down | 0.41 | 0.66 | 108 | 0 | oui | — | 124 | 0 | -0.0 |
| 08:05 | V2-F ecart qui grandit | Up | 0.20 | 0.41 | 108 | 250 | non | -0.18 | 1460 | 168 | +2.8 |
| 08:05 | desaccord 20 60-180 s | Up | 0.20 | 0.41 | 108 | 250 | non | -0.18 | 1460 | 168 | +2.8 |
| 08:05 | desaccord 30 | Up | 0.18 | 0.48 | 108 | 278 | non | -0.17 | 1381 | 132 | +2.6 |
| 08:10 | V2-F ecart qui grandit | Down | 0.23 | 0.44 | 254 | 217 | non | -0.21 | 580 | 47 | +2.2 |
| 08:10 | desaccord 20 60-180 s | Down | 0.18 | 0.43 | 180 | 278 | non | -0.19 | 183 | 0 | -0.0 |
| 08:10 | desaccord 30 | Down | 0.12 | 0.43 | 128 | 295 | non | -0.13 | 23 | 0 | +2.6 |
| 08:20 | V2-F ecart qui grandit | Down | 0.29 | 0.50 | 180 | 0 | oui | — | 25 | 0 | +7.1 |
| 08:20 | desaccord 20 60-180 s | Down | 0.29 | 0.50 | 180 | 0 | oui | — | 54 | 0 | +7.0 |
| 08:20 | V2-F incertitude 0,01  | Down | 0.22 | 0.43 | 80 | 44 | oui | +0.77 | 93 | 0 | -1.5 |
| 08:20 | desaccord 30 | Down | 0.19 | 0.49 | 70 | 263 | oui | +0.80 | 470 | 89 | +1.5 |
| 08:50 | V2-F ecart qui grandit | Up | 0.24 | 0.45 | 261 | 0 | non | — | 8 | 0 | +1.3 |
| 08:50 | cohorte B : V2-F corri | Up | 0.21 | 0.41 | 188 | 238 | non | -0.22 | 33 | 0 | +3.2 |
| 08:50 | V2-F incertitude 0,01  | Up | 0.20 | 0.40 | 181 | 250 | non | -0.21 | 139 | 47 | +3.6 |
| 08:50 | desaccord 20 60-180 s | Up | 0.20 | 0.48 | 180 | 250 | non | -0.20 | 166 | 65 | +3.0 |
| 08:50 | desaccord 30 | Up | 0.16 | 0.46 | 159 | 150 | non | -0.17 | 0 | 0 | — |
| 08:55 | V2-F ecart qui grandit | Down | 0.29 | 0.49 | 136 | 172 | oui | +0.75 | 183 | 0 | +1.7 |
| 08:55 | desaccord 20 60-180 s | Down | 0.29 | 0.49 | 136 | 172 | oui | +0.75 | 183 | 0 | +1.7 |
| 08:55 | V2-F incertitude 0,01  | Down | 0.27 | 0.47 | 136 | 185 | oui | +0.75 | 178 | 0 | +1.6 |
| 08:55 | cohorte B : V2-F corri | Down | 0.27 | 0.47 | 136 | 185 | oui | +0.75 | 178 | 0 | +1.6 |
| 08:55 | desaccord 30 | Up | 0.20 | 0.51 | 119 | 239 | non | -0.16 | 377 | 63 | +2.5 |
| 09:10 | V2-F ecart qui grandit | Down | 0.25 | 0.46 | 239 | 200 | non | -0.24 | 595 | 10 | +2.5 |
| 09:10 | V2-F incertitude 0,01  | Down | 0.23 | 0.49 | 238 | 217 | non | -0.23 | 595 | 10 | +2.4 |
| 09:10 | cohorte B : V2-F corri | Down | 0.23 | 0.49 | 238 | 217 | non | -0.23 | 595 | 10 | +2.4 |
| 09:10 | desaccord 30 | Down | 0.14 | 0.44 | 238 | 357 | non | -0.15 | 257 | 0 | +1.7 |
| 09:10 | desaccord 20 60-180 s | Down | 0.02 | 0.22 | 180 | 1594 | non | -0.02 | 641 | 0 | -0.0 |
| 09:15 | V2-F ecart qui grandit | Up | 0.27 | 0.47 | 136 | 158 | non | -0.28 | 7 | 0 | +2.0 |
| 09:15 | desaccord 20 60-180 s | Up | 0.27 | 0.47 | 136 | 158 | non | -0.28 | 7 | 0 | +2.0 |
| 09:15 | V2-F incertitude 0,01  | Up | 0.22 | 0.42 | 116 | 25 | non | -0.23 | 94 | 0 | +1.8 |
| 09:15 | cohorte B : V2-F corri | Up | 0.22 | 0.43 | 116 | 25 | non | -0.23 | 94 | 0 | +1.8 |
| 09:15 | desaccord 30 | Up | 0.17 | 0.47 | 83 | 220 | non | -0.18 | 179 | 10 | +2.0 |
| 09:20 | V2-F ecart qui grandit | Up | 0.23 | 0.46 | 293 | 36 | oui | +0.76 | 47 | 0 | +2.2 |
| 09:20 | V2-F incertitude 0,01  | Up | 0.20 | 0.40 | 198 | 0 | oui | — | 317 | 20 | -2.0 |
| 09:20 | cohorte B : V2-F corri | Up | 0.20 | 0.42 | 198 | 0 | oui | — | 317 | 20 | -2.0 |
| 09:20 | desaccord 20 60-180 s | Down | 0.27 | 0.48 | 118 | 74 | non | -0.28 | 117 | 0 | +1.6 |
| 09:20 | desaccord 30 | Down | 0.16 | 0.47 | 76 | 8 | non | -0.16 | 48 | 0 | +7.2 |
| 09:35 | V2-F incertitude 0,01  | Up | 0.42 | 0.64 | 238 | 5 | oui | +0.56 | 105 | 24 | +1.3 |
| 09:35 | cohorte B : V2-F corri | Up | 0.42 | 0.62 | 238 | 0 | oui | — | 105 | 24 | +1.3 |
| 09:35 | V2-F ecart qui grandit | Down | 0.16 | 0.38 | 230 | 312 | non | -0.17 | 264 | 20 | +3.0 |
| 09:35 | desaccord 20 60-180 s | Down | 0.10 | 0.36 | 180 | 218 | non | -0.11 | 612 | 0 | -0.0 |
| 09:35 | desaccord 30 | Down | 0.08 | 0.38 | 159 | 45 | non | -0.09 | 44 | 0 | +6.4 |
| 09:40 | V2-F incertitude 0,01  | Down | 0.57 | 0.78 | 261 | 0 | oui | — | 659 | 0 | -1.6 |
| 09:40 | V2-F ecart qui grandit | Up | 0.20 | 0.40 | 261 | 153 | non | -0.21 | 562 | 19 | +1.2 |
| 09:40 | desaccord 30 | Up | 0.11 | 0.41 | 221 | 0 | non | — | 211 | 36 | +2.0 |
| 09:40 | desaccord 20 60-180 s | Up | 0.12 | 0.39 | 180 | 390 | non | -0.13 | 308 | 51 | -0.0 |
| 10:30 | V2-F ecart qui grandit | Up | 0.27 | 0.49 | 220 | 185 | non | -0.28 | 24 | 0 | +2.6 |
| 10:30 | V2-F incertitude 0,01  | Up | 0.26 | 0.46 | 219 | 65 | non | -0.27 | 24 | 0 | +1.7 |
| 10:30 | cohorte B : V2-F corri | Up | 0.26 | 0.47 | 219 | 60 | non | -0.27 | 24 | 0 | +1.7 |
| 10:30 | desaccord 30 | Up | 0.19 | 0.49 | 181 | 263 | non | -0.20 | 80 | 0 | +3.1 |
| 10:30 | desaccord 20 60-180 s | Up | 0.19 | 0.49 | 180 | 228 | non | -0.20 | 80 | 0 | +2.0 |
| 10:55 | V2-F ecart qui grandit | Down | 0.21 | 0.46 | 290 | 238 | non | -0.22 | 287 | 38 | -1.6 |
| 10:55 | desaccord 30 | Down | 0.15 | 0.45 | 277 | 0 | non | — | 0 | 0 | — |
| 10:55 | cohorte A : zone + mod | Down | 0.15 | 0.47 | 277 | 0 | non | — | 0 | 0 | — |
| 10:55 | cohorte B : V2-F corri | Down | 0.15 | 0.35 | 277 | 0 | non | — | 0 | 0 | — |
| 10:55 | V2-F incertitude 0,01  | Down | 0.16 | 0.51 | 277 | 0 | non | — | 6 | 0 | -0.2 |
| 10:55 | desaccord 20 60-180 s | Down | 0.07 | 0.41 | 180 | 176 | non | -0.07 | 39 | 0 | +1.9 |
| 11:00 | V2-F incertitude 0,01  | Up | 0.35 | 0.55 | 262 | 0 | oui | — | 99 | 36 | +0.1 |
| 11:00 | cohorte B : V2-F corri | Up | 0.35 | 0.56 | 262 | 0 | oui | — | 99 | 36 | +0.1 |
| 11:00 | V2-F ecart qui grandit | Down | 0.30 | 0.50 | 144 | 106 | non | -0.32 | 55 | 0 | +2.8 |
| 11:00 | desaccord 20 60-180 s | Down | 0.30 | 0.50 | 144 | 106 | non | -0.32 | 55 | 0 | +2.8 |
| 11:00 | desaccord 30 | Down | 0.13 | 0.45 | 116 | 255 | non | -0.14 | 1162 | 48 | +2.1 |
| 11:05 | V2-F ecart qui grandit | Down | 0.29 | 0.50 | 121 | 172 | oui | +0.72 | 253 | 45 | +1.4 |
| 11:05 | V2-F incertitude 0,01  | Down | 0.29 | 0.51 | 121 | 172 | oui | +0.72 | 253 | 45 | +1.4 |
| 11:05 | cohorte B : V2-F corri | Down | 0.29 | 0.51 | 121 | 172 | oui | +0.72 | 253 | 45 | +1.4 |
| 11:05 | desaccord 20 60-180 s | Down | 0.29 | 0.50 | 121 | 172 | oui | +0.72 | 253 | 45 | +1.4 |
| 11:05 | desaccord 30 | Down | 0.20 | 0.50 | 115 | 105 | oui | +0.79 | 472 | 0 | +3.0 |
| 11:10 | V2-F ecart qui grandit | Up | 0.21 | 0.41 | 191 | 238 | non | -0.21 | 543 | 11 | +1.6 |
| 11:10 | desaccord 20 60-180 s | Up | 0.19 | 0.43 | 180 | 263 | non | -0.19 | 78 | 0 | -1.0 |
| 11:10 | desaccord 30 | Up | 0.12 | 0.42 | 155 | 323 | non | -0.13 | 49 | 0 | +2.0 |
| 11:10 | cohorte B : V2-F corri | Up | 0.09 | 0.29 | 145 | 96 | non | -0.10 | 239 | 0 | +0.9 |
| 11:15 | V2-F ecart qui grandit | Down | 0.21 | 0.45 | 203 | 0 | non | — | 585 | 7 | +2.1 |
| 11:15 | cohorte B : V2-F corri | Down | 0.22 | 0.42 | 203 | 227 | non | -0.20 | 603 | 7 | +1.6 |
| 11:15 | V2-F incertitude 0,01  | Down | 0.20 | 0.40 | 202 | 250 | non | -0.19 | 597 | 7 | +1.4 |
| 11:15 | desaccord 30 | Down | 0.18 | 0.48 | 202 | 263 | non | -0.19 | 493 | 7 | +1.3 |
| 11:15 | desaccord 20 60-180 s | Down | 0.08 | 0.42 | 180 | 215 | non | -0.09 | 719 | 0 | +2.0 |
| 11:30 | V2-F ecart qui grandit | Down | 0.25 | 0.46 | 254 | 200 | oui | +0.74 | 107 | 36 | +1.9 |
| 11:30 | desaccord 20 60-180 s | Down | 0.26 | 0.46 | 180 | 192 | oui | +0.74 | 137 | 10 | +3.0 |
| 11:30 | cohorte B : V2-F corri | Down | 0.23 | 0.43 | 146 | 0 | oui | — | 123 | 0 | +1.3 |
| 11:30 | V2-F incertitude 0,01  | Down | 0.23 | 0.43 | 146 | 0 | oui | — | 123 | 0 | +1.3 |
| 11:30 | cohorte A : zone + mod | Down | 0.23 | 0.54 | 146 | 0 | oui | — | 123 | 0 | +1.2 |
| 11:30 | desaccord 30 | Down | 0.23 | 0.54 | 146 | 0 | oui | — | 123 | 0 | +1.2 |
| 11:45 | V2-F ecart qui grandit | Down | 0.26 | 0.47 | 150 | 192 | non | -0.24 | 557 | 0 | +1.6 |
| 11:45 | desaccord 20 60-180 s | Down | 0.26 | 0.47 | 150 | 192 | non | -0.24 | 557 | 0 | +1.6 |
| 11:45 | desaccord 30 | Down | 0.09 | 0.41 | 138 | 35 | non | -0.10 | 123 | 0 | +2.6 |
| 11:45 | V2-F incertitude 0,01  | Up | 0.67 | 0.89 | 130 | 75 | oui | +0.32 | 74 | 0 | +2.2 |
| 12:40 | V2-F ecart qui grandit | Up | 0.10 | 0.30 | 262 | 0 | non | — | 49 | 24 | +1.8 |
| 12:40 | desaccord 20 60-180 s | Up | 0.08 | 0.32 | 180 | 257 | non | -0.09 | 152 | 0 | -0.0 |
| 12:40 | desaccord 30 | Up | 0.03 | 0.35 | 55 | 0 | non | — | 2762 | 0 | +1.7 |
| 13:00 | V2-F incertitude 0,01  | Up | 0.34 | 0.54 | 131 | 147 | non | -0.36 | 1511 | 106 | +2.6 |
| 13:00 | cohorte B : V2-F corri | Up | 0.32 | 0.53 | 130 | 156 | non | -0.26 | 1546 | 122 | +1.5 |
| 13:00 | V2-F ecart qui grandit | Up | 0.30 | 0.51 | 129 | 167 | non | -0.26 | 1546 | 122 | +1.5 |
| 13:00 | desaccord 20 60-180 s | Up | 0.30 | 0.51 | 129 | 167 | non | -0.26 | 1546 | 122 | +1.5 |
| 13:00 | desaccord 30 | Up | 0.20 | 0.50 | 124 | 250 | non | -0.21 | 235 | 43 | +1.6 |
| 13:05 | V2-F ecart qui grandit | Up | 0.26 | 0.48 | 207 | 192 | non | -0.26 | 414 | 0 | +1.3 |
| 13:05 | desaccord 20 60-180 s | Up | 0.16 | 0.44 | 180 | 58 | non | -0.17 | 118 | 12 | +1.0 |
| 13:05 | desaccord 30 | Up | 0.12 | 0.42 | 164 | 75 | non | -0.13 | 485 | 11 | +2.4 |
| 13:10 | V2-F ecart qui grandit | Down | 0.21 | 0.43 | 293 | 238 | non | -0.21 | 371 | 48 | +0.2 |
| 13:10 | desaccord 20 60-180 s | Down | 0.21 | 0.46 | 180 | 238 | non | -0.22 | 113 | 36 | -0.0 |
| 13:10 | desaccord 30 | Down | 0.16 | 0.46 | 125 | 312 | non | -0.17 | 166 | 9 | +2.6 |
| 13:10 | cohorte B : V2-F corri | Down | 0.13 | 0.33 | 123 | 385 | non | -0.14 | 215 | 0 | +2.8 |
| 13:10 | V2-F incertitude 0,01  | Down | 0.09 | 0.29 | 114 | 0 | non | — | 639 | 60 | +3.5 |
| 13:15 | V2-F ecart qui grandit | Down | 0.29 | 0.49 | 241 | 100 | non | -0.30 | 169 | 24 | +1.7 |
| 13:15 | V2-F incertitude 0,01  | Down | 0.29 | 0.49 | 239 | 0 | non | — | 177 | 24 | +0.2 |
| 13:15 | cohorte B : V2-F corri | Down | 0.29 | 0.49 | 239 | 0 | non | — | 177 | 24 | +0.2 |
| 13:15 | desaccord 30 | Down | 0.19 | 0.49 | 187 | 167 | non | -0.20 | 74 | 28 | +1.6 |
| 13:15 | desaccord 20 60-180 s | Down | 0.17 | 0.48 | 180 | 115 | non | -0.18 | 16 | 0 | -0.0 |
| 13:20 | V2-F incertitude 0,01  | Down | 0.47 | 0.67 | 238 | 5 | oui | +0.51 | 94 | 0 | -1.1 |
| 13:20 | cohorte B : V2-F corri | Down | 0.47 | 0.68 | 238 | 5 | oui | +0.51 | 94 | 0 | -1.1 |
| 13:20 | V2-F ecart qui grandit | Up | 0.28 | 0.50 | 207 | 0 | non | — | 275 | 36 | +1.2 |
| 13:20 | desaccord 20 60-180 s | Up | 0.26 | 0.47 | 177 | 192 | non | -0.27 | 431 | 64 | +3.6 |
| 13:20 | desaccord 30 | Up | 0.17 | 0.47 | 120 | 45 | non | -0.18 | 15 | 0 | +3.0 |