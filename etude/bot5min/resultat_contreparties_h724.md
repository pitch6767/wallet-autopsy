# Bot95 — Counterparty Intelligence Lab, H724–H765 — PRÉLIMINAIRE

Généré le 11.10.2026 16:53 UTC. Marchés lus avant le 13.10 : 600 dont 5 tronqués (≥ 10 000 exécutions, exclus). Signaux Bot95 réglés : 376 ; sur des marchés complets : **353**, répartis sur **74 cycles** (les variantes du même cycle ne sont pas indépendantes : les intervalles de confiance rééchantillonnent des cycles). Séparation chronologique : apprentissage = cycles < 11.10 11:05 UTC, test = après. Cycles avec carnet Dublin (Reverse) : 31. Les trois wallets : `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c`, `0x4c9497941333332d29f1c235dd23200f3623ffad`, `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b`.

**Biais de sélection à garder en tête :** les trois wallets ont été repérés sur ces mêmes signaux (E1). Tout résultat « avec les trois wallets » est donc en partie dans l'échantillon. Le contrôle honnête est la version chronologique (wallets choisis sur la première moitié, mesurés sur la seconde) et le placebo.

## 1. H724 / Test A — Les signaux et leurs correspondances maker (livrables 1, 2, 3)

| Catégorie (sur 353 signaux) | Signaux | Lecture |
|---|---|---|
| Au moins une vente maker du côté Bot95 au prix du signal ou mieux, de −1 s à +10 s | 341 | correspondance « dans les 10 s » (c'est le chiffre 157 d'E1, recalculé) |
| … dont au même prix exact | 283 | |
| … dans la seconde de la décision (contemporaine, ordre inconnu à la seconde) | 56 | ambigu : avant ou après nous |
| … dans la seconde précédente | 27 | l'offre a été servie AVANT nous (par un autre preneur) |
| … uniquement après la seconde de décision | 270 | n'est pas une information disponible au signal |
| Offre présente au signal (carnet Dublin, quantité au prix du signal) | 353 | fait mesuré |
| Encore achetable 100 ms après | 310 | borne optimiste |
| **Encore achetable 250 ms après (exécution simulée retenue)** | 251 | délai preneur 150 ms + trajet |
| Impossible après latence (plus rien au prix) | 102 | |

Une correspondance dans les 10 s **n'est pas** un remplissage garanti : la plupart des ventes maker servent d'autres preneurs.

**Wallets réellement impliqués (livrable 3)** — top 12 par nombre de signaux servis

| Wallet | Signaux servis | Parts | dont « achète l'autre côté » | Marchés actifs | Résultat global par $ |
|---|---|---|---|---|---|
| `0x85a186d1…` | 143 | 1820 | 100 % | 592 | -1.5 % |
| `0x18c18e0c…` | 140 | 2806 | 100 % | 501 | +1.1 % |
| `0xf9b7876b…` ★ | 134 | 2263 | 100 % | 587 | +0.8 % |
| `0x322b2e7c…` | 133 | 1782 | 100 % | 592 | -1.1 % |
| `0x41e2e1cc…` | 126 | 3883 | 100 % | 595 | -0.9 % |
| `0x4c949794…` ★ | 124 | 1952 | 100 % | 594 | +1.4 % |
| `0x568b0798…` ★ | 123 | 1851 | 100 % | 595 | +1.1 % |
| `0x809f2752…` | 114 | 1276 | 0 % | 586 | +0.3 % |
| `0xaa1a4f31…` | 113 | 3014 | 100 % | 573 | -1.4 % |
| `0x32c4922d…` | 110 | 1250 | 0 % | 594 | -0.1 % |
| `0xa3338de3…` | 108 | 1237 | 0 % | 425 | +0.4 % |
| `0x1dd2a69e…` | 101 | 1041 | 0 % | 592 | +0.0 % |

Nombre total de wallets distincts : 412. ★ = les trois wallets étudiés.

## 2. Test B — Les trois wallets : inventaire, coût, profits (livrables 4, 5, 6, 7)

Méthode : inventaire reconstruit marché par marché (premier entré, premier sorti). Une vente sans stock = **split déduit** : la jambe vendue coûte son prix de vente, l'autre jambe (gardée) coûte 1 − p. Économiquement, c'est identique à **acheter le côté opposé** à 1 − p. Transferts et splits hors marché non vus (activités pas encore collectées) → les inventaires peuvent être incomplets.

| Groupe | Résultat total | dont réalisé sur ventes depuis stock | Parts vendues | depuis stock | via split (≡ achat de l'autre côté) | Prix moyen de vente (stock) | Coût moyen (stock) | Ventes qui réduisent l'exposition |
|---|---|---|---|---|---|---|---|---|
| autres makers qui servent nos signaux | +29117 $ | +1000 $ | 1614665 | 54 % | 46 % | 0.546 | 0.545 | 48 % |

**Profil des trois wallets (tous marchés complets)** — achats / ventes, paires et jambes résiduelles

| Wallet | Achats (parts) | Ventes (parts) | Coût moyen d'une paire Up+Down | Parts appariées | Résultat des paires | Résultat des jambes résiduelles | Total |
|---|---|---|---|---|---|---|---|
| `0xf9b7876b…` | 259741 | 0 | 1.061 | 96891 | -5939 $ | +7149 $ | +1209 $ |
| `0x4c949794…` | 221223 | 0 | 1.066 | 79543 | -5252 $ | +7033 $ | +1781 $ |
| `0x568b0798…` | 208159 | 0 | 1.071 | 74807 | -5296 $ | +6575 $ | +1279 $ |

Taux de gain des signaux : tous 34 % (prix moyen 0.23) ; encore achetables à 250 ms 29 % (prix 0.22) ; partis avant 250 ms 48 % (prix 0.25).


**Les ventes des trois wallets au moment des signaux (de −1 s à +10 s)**

| Type de vente | Ventes | Parts | Coût moyen du stock vendu | Prix moyen | Gain réalisé/part | Billet vendu gagnant | Résultat final du wallet dans ces marchés |
|---|---|---|---|---|---|---|---|
| achat de l'autre côté (mint) | 853 | 6065 | — | 0.201 | — | 28 % | -942 $ |
Rendement de l'acheteur sur ces billets (Bot95 au même prix) : +39.4 % par $ (avant frais), contre +50.6 % sur tous les signaux.

## 3. H728 — Les trois wallets vendent-ils de moins bons billets que les autres makers ? (livrable 7)

Toutes les ventes maker (vendre X ou acheter l'autre côté) de tous les marchés complets ; rendement de l'ACHETEUR au règlement ; comparaison à prix (tranche de 0,10) × minute du cycle identiques.

- Rendement brut de l'acheteur : face aux trois wallets -1.4 % par $ ; face aux autres makers +0.8 %.
- **Écart à prix et minute identiques : -3.3 points** (IC 90 % par cycles [-5.3 ; -1.3]). Négatif = les trois wallets vendent des billets plus mauvais pour l'acheteur.

## 4. Test C — Flux observés AVANT les signaux (livrables 8, 9)

Variables calculées uniquement avec des transactions datées ≤ seconde de décision − 1 (− délai de disponibilité D). Flux net vers le côté Bot95 (+ = le groupe achète le côté Bot95 ou vend l'autre ; − = il vend notre côté). Inventaire = position nette (côté Bot95 − autre côté) depuis l'ouverture du marché.

Erreur Bot95 = gagné (1/0) − probabilité du modèle. Négatif = Bot95 surestime.

| Groupe | Fenêtre | Signaux avec flux contre nous | erreur | Signaux flux nul | erreur | Signaux flux pour nous | erreur | Écart contre − reste (IC 90 %) |
|---|---|---|---|---|---|---|---|---|
| 3 wallets (makers) | 60 s | 232 | -0.10 | 13 | -0.41 | 108 | -0.14 | +0.06 [-0.08 ; +0.19] |
| 3 wallets (makers) | 30 s | 223 | -0.09 | 26 | -0.37 | 104 | -0.14 | +0.10 [-0.03 ; +0.23] |
| 3 wallets (makers) | 10 s | 185 | -0.15 | 88 | -0.09 | 80 | -0.11 | -0.05 [-0.16 ; +0.07] |
| 3 wallets (makers) | 3 s | 113 | -0.12 | 188 | -0.13 | 52 | -0.14 | +0.01 [-0.10 ; +0.13] |
| 3 wallets (makers) | 1 s | 45 | -0.20 | 289 | -0.12 | 19 | +0.00 | -0.08 [-0.23 ; +0.09] |
| 3 wallets (makers) | inventaire | 228 | -0.11 | 0 | +nan | 125 | -0.15 | +0.04 [-0.13 ; +0.19] |
| tous les makers | 60 s | 154 | -0.10 | 0 | +nan | 199 | -0.14 | +0.04 [-0.11 ; +0.18] |
| tous les makers | 30 s | 143 | -0.15 | 0 | +nan | 210 | -0.11 | -0.03 [-0.16 ; +0.09] |
| tous les makers | 10 s | 147 | -0.07 | 1 | +0.50 | 205 | -0.17 | +0.10 [-0.01 ; +0.23] |
| tous les makers | 3 s | 150 | -0.11 | 2 | +0.08 | 201 | -0.14 | +0.03 [-0.08 ; +0.14] |
| tous les makers | 1 s | 86 | -0.21 | 138 | -0.09 | 129 | -0.11 | -0.11 [-0.22 ; -0.01] |
| tous les makers | inventaire | 154 | -0.04 | 0 | +nan | 199 | -0.20 | +0.16 [-0.00 ; +0.32] |
| tous les preneurs | 60 s | 199 | -0.14 | 0 | +nan | 154 | -0.10 | -0.04 [-0.19 ; +0.11] |
| tous les preneurs | 30 s | 210 | -0.11 | 0 | +nan | 143 | -0.15 | +0.03 [-0.09 ; +0.16] |
| tous les preneurs | 10 s | 205 | -0.17 | 1 | +0.50 | 147 | -0.07 | -0.11 [-0.22 ; +0.00] |
| tous les preneurs | 3 s | 201 | -0.14 | 2 | +0.08 | 150 | -0.11 | -0.03 [-0.13 ; +0.06] |
| tous les preneurs | 1 s | 129 | -0.11 | 138 | -0.09 | 86 | -0.21 | +0.03 [-0.07 ; +0.14] |
| tous les preneurs | inventaire | 199 | -0.20 | 0 | +nan | 154 | -0.04 | -0.16 [-0.32 ; +0.01] |

## 5. Test D — Calibration avec et sans identité des wallets (livrable 10)

Apprentissage 166 signaux / 37 cycles ; test 187 signaux / 37 cycles (chronologique, aucun signal commun).

| Modèle | Log loss test | Brier test | Log loss apprentissage |
|---|---|---|---|
| Bot95 brut | 0.6817 | 0.2421 | 0.6296 |
| Bot95 recalibré | 0.6865 | 0.2388 | 0.5669 |
| + 3 wallets (30 s + inventaire) | 0.6850 | 0.2380 | 0.5667 |
| + flux global (makers + preneurs 30 s) | 0.6943 | 0.2412 | 0.5634 |
| + les deux | 0.6893 | 0.2388 | 0.5620 |

Gain de log loss apporté par les trois wallets sur le test : +0.0015 (positif = mieux).

## 6. Test G — Placebo : trois wallets tirés au hasard (livrable 15)

- Fenêtre 3 s : écart d'erreur vrais wallets +0.006 ; placebo médiane -0.050 ; part des placebos aussi négatifs ou plus : **67 %** (173 tirages avec ≥ 5 signaux).
- Fenêtre 1 s : écart d'erreur vrais wallets -0.079 ; placebo médiane -0.130 ; part des placebos aussi négatifs ou plus : **63 %** (130 tirages avec ≥ 5 signaux).
- **Version chronologique** (wallets choisis sur l'apprentissage : `0x568b0798…`, `0x4c949794…`, `0xf9b7876b…` ; 3 en commun avec les trois) — écart d'erreur sur le TEST, flux contre nous − reste : 30 s +0.222 (n = 111) ; 10 s -0.025 (n = 84) ; 3 s +0.065 (n = 52) ; 1 s +0.019 (n = 22)

190 makers comparables (actifs sur assez de marchés) ; 200 tirages de trois wallets.

- Gain de log loss test : vrais wallets +0.0015 ; placebo médiane -0.0136, 90e centile +0.0163 ; part des placebos ≥ réel : **28 %**.
- Écart d'erreur Bot95 « flux 30 s contre nous » − reste : vrais wallets +0.097 ; placebo médiane +0.022 ; part des placebos aussi négatifs ou plus : **81 %**.

## 7. Test E — Reverse Bot95 (livrables 11, 17, 18)

A = acheter le côté Bot95 au prix achetable 250 ms après la décision (frais compris, quantité réellement présente). B = acheter le côté OPPOSÉ à son meilleur vendeur 250 ms après (carnet Dublin ; quantité au meilleur niveau ; frais preneur). C = ne rien faire. Mise : 1 part par signal (le P&L par $ est aussi donné).

| Politique | Échantillon | Exécutés | P&L total (parts) | par signal (IC 90 %) | par $ | Taux de gain | Drawdown max | Pire série de pertes | Jackpots (gain à prix ≤ 0,25) |
|---|---|---|---|---|---|---|---|---|---|
| A — côté Bot95 | tous les signaux | 251 | +15.55 | +0.062 [-0.015 ; +0.136] | +27.5 % | 29 % | 5.20 | 18 | 35 |
| B — côté opposé | tous les signaux | 157 | -35.11 | -0.224 [-0.336 ; -0.108] | -28.9 % | 56 % | 36.02 | 12 | 0 |
| C — rien | tous les signaux | 0 | 0 | 0 | — | — | 0 | 0 | 0 |
| A — côté Bot95 | cycles avec carnet Dublin (A et B exécutables) | 109 | +13.83 | +0.127 [+0.009 ; +0.249] | +57.2 % | 35 % | 3.78 | 14 | 18 |
| B — côté opposé | cycles avec carnet Dublin (A et B exécutables) | 109 | -17.22 | -0.158 [-0.288 ; -0.039] | -19.8 % | 65 % | 17.91 | 8 | 0 |
| C — rien | cycles avec carnet Dublin (A et B exécutables) | 0 | 0 | 0 | — | — | 0 | 0 | 0 |
| A — côté Bot95 | test (2e moitié) | 44 | +13.68 | +0.311 [+0.102 ; +0.519] | +146.8 % | 52 % | 2.40 | 14 | 12 |
| B — côté opposé | test (2e moitié) | 44 | -15.15 | -0.344 [-0.549 ; -0.144] | -42.4 % | 48 % | 15.15 | 8 | 0 |
| C — rien | test (2e moitié) | 0 | 0 | 0 | — | — | 0 | 0 | 0 |

Acheter le côté opposé n'est PAS vendre le billet Bot95 : on paie le vendeur opposé + frais, l'écart vendeur-acheteur est payé deux fois.

## 8. Test F — Veto et confirmation par contrepartie, contre un filtre de flux global (livrables 12, 13, 14, 18)

Règles fixées a priori (aucun seuil optimisé) : **veto** = on n'achète pas si le groupe a un flux net CONTRE notre côté sur la fenêtre ; **confirmation** = on n'achète que si le flux est POUR notre côté. Politique de base = A (côté Bot95, 250 ms).

| Filtre | Fenêtre / délai | Signaux gardés | Perdants évités | Gagnants supprimés | Jackpots supprimés | P&L marginal (parts) | IC 90 % | P&L gardé sur le test |
|---|---|---|---|---|---|---|---|---|
| veto 3 wallets | 60 s | 85 / 251 | 121 | 45 | 29 | -10.80 | [-26.71 ; +4.31] | -0.03 |
| veto 3 wallets | 30 s | 96 / 251 | 106 | 49 | 24 | -14.57 | [-30.51 ; -0.83] | +1.03 |
| veto 3 wallets | 10 s | 108 / 251 | 105 | 38 | 17 | -7.43 | [-19.91 ; +4.56] | +7.98 |
| veto 3 wallets | inv | 93 / 251 | 116 | 42 | 26 | -10.36 | [-26.71 ; +3.39] | +1.43 |
| veto 3 wallets | 30 s (D = 2 s) | 101 / 251 | 106 | 44 | 22 | -10.77 | [-25.99 ; +2.29] | +1.13 |
| veto 3 wallets | 30 s (D = 5 s) | 109 / 251 | 103 | 39 | 21 | -7.40 | [-21.81 ; +6.03] | +5.70 |
| veto flux global makers | 30 s | 163 / 251 | 66 | 22 | 13 | -1.96 | [-10.86 ; +6.35] | +11.34 |
| veto flux global preneurs | 30 s | 88 / 251 | 113 | 50 | 22 | -13.59 | [-29.25 ; +1.59] | +0.37 |
| veto flux global makers | 10 s | 162 / 251 | 61 | 28 | 12 | -8.55 | [-18.68 ; +1.04] | +5.93 |
| veto flux global preneurs | 10 s | 90 / 251 | 118 | 43 | 23 | -6.31 | [-22.34 ; +8.28] | +5.79 |
| confirmation 3 wallets | 60 s | 77 / 251 | 128 | 46 | 29 | -9.83 | [-26.56 ; +5.99] | +0.84 |
| confirmation 3 wallets | 30 s | 77 / 251 | 124 | 50 | 24 | -10.51 | [-25.00 ; +4.88] | +4.88 |
| confirmation 3 wallets | 10 s | 47 / 251 | 148 | 56 | 24 | -10.23 | [-26.88 ; +4.62] | +5.63 |
| confirmation 3 wallets | inv | 93 / 251 | 116 | 42 | 26 | -10.36 | [-26.01 ; +5.47] | +1.43 |
| confirmation 3 wallets | 30 s (D = 2 s) | 77 / 251 | 127 | 47 | 24 | -7.58 | [-22.79 ; +6.90] | +4.63 |
| confirmation 3 wallets | 30 s (D = 5 s) | 87 / 251 | 122 | 42 | 23 | -4.69 | [-20.18 ; +9.58] | +8.58 |
| confirmation flux global makers | 30 s | 163 / 251 | 66 | 22 | 13 | -1.96 | [-10.90 ; +6.54] | +11.34 |
| confirmation flux global preneurs | 30 s | 88 / 251 | 113 | 50 | 22 | -13.59 | [-30.14 ; +1.92] | +0.37 |
| confirmation flux global makers | 10 s | 161 / 251 | 61 | 29 | 12 | -9.25 | [-18.50 ; -0.18] | +5.93 |
| confirmation flux global preneurs | 10 s | 89 / 251 | 118 | 44 | 23 | -7.00 | [-24.01 ; +8.32] | +5.79 |

Référence sans filtre : P&L A total +15.55 parts ; sur le test +11.72.

## 9. H727 — Empreinte « même opérateur » (statistique seulement)

| Wallet | Exécutions maker | Taille médiane (parts) | Tailles rondes | Prix médian | Part Up | Part achats | Marchés | Résultat par $ |
|---|---|---|---|---|---|---|---|---|
| `0xf9b7876b…` | 22648 | 8.4 | 39 % | 0.58 | 51 % | 100 % | 587 | +0.8 % |
| `0x4c949794…` | 19137 | 9.0 | 40 % | 0.59 | 50 % | 100 % | 594 | +1.4 % |
| `0x568b0798…` | 17999 | 9.0 | 40 % | 0.59 | 51 % | 100 % | 595 | +1.1 % |

| Paire | Marchés communs (Jaccard) | Secondes communes d'activité | Attendu au hasard (même marchés) |
|---|---|---|---|
| 0xf9b787 / 0x4c9497 | 586 (98 %) | 6477 | 1255 |
| 0xf9b787 / 0x568b07 | 587 (99 %) | 6247 | 1196 |
| 0x4c9497 / 0x568b07 | 594 (100 %) | 6309 | 1083 |

Transferts publics, splits / merges hors marché : **non vérifiés** (activités en cours de collecte). Similarité statistique ≠ contrôle commun.

## 10. H765 — Audit de disponibilité temporelle (livrable 16)

- **Fait** : l'API Data date à la seconde. Une transaction datée de la seconde du signal peut être postérieure → exclue de toutes les variables.
- **Fait** : le flux carnet temps réel de Polymarket donne prix, taille, côté — pas l'adresse des wallets.
- **Hypothèse à mesurer** : l'identité n'arrive qu'avec la chaîne (blocs Polygon ≈ 2 s + délai de soumission) ou l'API Data (délai inconnu). Les fenêtres 1 et 3 s ne sont donc probablement PAS disponibles en direct ; les tests avec D = 2 et 5 s simulent ce retard.
- Les correspondances « dans les 10 s » de la section 1 sont presque toutes postérieures au signal : elles décrivent, elles ne prédisent pas.

## Limites
- Une seule journée, ~74 cycles : puissance statistique faible ; tout est PRÉLIMINAIRE.
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
| 07:15 | V2-F ecart qui grandit | Down | 0.27 | 0.47 | 223 | 143 | oui | +0.72 | 101 | 14 | +2.7 |
| 07:15 | V2-F incertitude 0,01  | Up | 0.29 | 0.50 | 107 | 172 | non | -0.29 | 603 | 108 | +4.0 |
| 07:15 | desaccord 20 60-180 s | Up | 0.29 | 0.50 | 107 | 172 | non | -0.29 | 603 | 108 | +4.0 |
| 07:15 | desaccord 30 | Up | 0.15 | 0.45 | 100 | 333 | non | -0.14 | 590 | 72 | +3.2 |
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
| 08:15 | V2-F ecart qui grandit | Down | 0.28 | 0.49 | 282 | 179 | oui | +0.72 | 371 | 53 | +2.7 |
| 08:15 | V2-F incertitude 0,01  | Down | 0.18 | 0.39 | 230 | 0 | oui | — | 0 | 0 | — |
| 08:15 | desaccord 30 | Down | 0.18 | 0.48 | 230 | 0 | oui | — | 0 | 0 | — |
| 08:15 | desaccord 20 jeton 0,3 | Down | 0.39 | 0.59 | 230 | 0 | oui | — | 26 | 0 | +1.9 |
| 08:15 | desaccord 20 60-180 s | Down | 0.30 | 0.50 | 95 | 167 | oui | +0.72 | 631 | 49 | +2.1 |
| 08:20 | V2-F ecart qui grandit | Down | 0.29 | 0.50 | 180 | 0 | oui | — | 25 | 0 | +7.1 |
| 08:20 | desaccord 20 60-180 s | Down | 0.29 | 0.50 | 180 | 0 | oui | — | 54 | 0 | +7.0 |
| 08:20 | V2-F incertitude 0,01  | Down | 0.22 | 0.43 | 80 | 44 | oui | +0.77 | 93 | 0 | -1.5 |
| 08:20 | desaccord 30 | Down | 0.19 | 0.49 | 70 | 263 | oui | +0.80 | 470 | 89 | +1.5 |
| 08:25 | V2-F incertitude 0,01  | Down | 0.48 | 0.68 | 276 | 0 | oui | — | 509 | 0 | -1.7 |
| 08:25 | V2-F ecart qui grandit | Up | 0.12 | 0.35 | 275 | 0 | non | — | 72 | 0 | +2.3 |
| 08:25 | desaccord 20 60-180 s | Up | 0.05 | 0.25 | 179 | 0 | non | — | 517 | 0 | -1.0 |
| 08:25 | desaccord 30 | Up | 0.03 | 0.33 | 90 | 40 | non | -0.03 | 40 | 0 | +3.3 |
| 08:30 | V2-F ecart qui grandit | Down | 0.21 | 0.42 | 294 | 238 | non | -0.22 | 154 | 26 | +1.1 |
| 08:30 | desaccord 30 | Down | 0.09 | 0.39 | 269 | 5 | non | -0.10 | 5 | 0 | +1.8 |
| 08:30 | V2-F incertitude 0,01  | Down | 0.09 | 0.29 | 269 | 5 | non | -0.10 | 5 | 0 | +1.7 |
| 08:30 | desaccord 20 60-180 s | Up | 0.15 | 0.35 | 180 | 324 | oui | +0.84 | 339 | 12 | -0.0 |
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
| 09:25 | V2-F incertitude 0,01  | Up | 0.52 | 0.73 | 278 | 40 | non | -0.54 | 35 | 0 | -1.4 |
| 09:25 | cohorte B : V2-F corri | Up | 0.52 | 0.72 | 278 | 40 | non | -0.54 | 35 | 0 | -1.4 |
| 09:25 | V2-F ecart qui grandit | Down | 0.18 | 0.38 | 276 | 278 | oui | +0.82 | 3598 | 118 | +2.6 |
| 09:25 | desaccord 20 60-180 s | Down | 0.09 | 0.38 | 180 | 515 | oui | +0.90 | 59 | 3 | -0.0 |
| 09:25 | desaccord 30 | Down | 0.07 | 0.38 | 174 | 150 | oui | +0.93 | 0 | 0 | — |
| 09:25 | cohorte A : zone + mod | Down | 0.15 | 0.47 | 155 | 0 | oui | — | 223 | 0 | -1.3 |
| 09:30 | V2-F ecart qui grandit | Up | 0.27 | 0.48 | 265 | 80 | non | -0.28 | 14 | 0 | +2.0 |
| 09:30 | desaccord 20 60-180 s | Up | 0.27 | 0.47 | 174 | 185 | non | -0.28 | 105 | 12 | +1.2 |
| 09:30 | cohorte B : V2-F corri | Up | 0.20 | 0.40 | 163 | 250 | non | -0.20 | 67 | 17 | +2.5 |
| 09:30 | V2-F incertitude 0,01  | Up | 0.19 | 0.39 | 163 | 208 | non | -0.20 | 48 | 17 | +2.4 |
| 09:30 | desaccord 30 | Up | 0.17 | 0.47 | 113 | 26 | non | -0.18 | 35 | 0 | +2.6 |
| 09:35 | V2-F incertitude 0,01  | Up | 0.42 | 0.64 | 238 | 5 | oui | +0.56 | 105 | 24 | +1.3 |
| 09:35 | cohorte B : V2-F corri | Up | 0.42 | 0.62 | 238 | 0 | oui | — | 105 | 24 | +1.3 |
| 09:35 | V2-F ecart qui grandit | Down | 0.16 | 0.38 | 230 | 312 | non | -0.17 | 264 | 20 | +3.0 |
| 09:35 | desaccord 20 60-180 s | Down | 0.10 | 0.36 | 180 | 218 | non | -0.11 | 612 | 0 | -0.0 |
| 09:35 | desaccord 30 | Down | 0.08 | 0.38 | 159 | 45 | non | -0.09 | 44 | 0 | +6.4 |
| 09:40 | V2-F incertitude 0,01  | Down | 0.57 | 0.78 | 261 | 0 | oui | — | 659 | 0 | -1.6 |
| 09:40 | V2-F ecart qui grandit | Up | 0.20 | 0.40 | 261 | 153 | non | -0.21 | 562 | 19 | +1.2 |
| 09:40 | desaccord 30 | Up | 0.11 | 0.41 | 221 | 0 | non | — | 211 | 36 | +2.0 |
| 09:40 | desaccord 20 60-180 s | Up | 0.12 | 0.39 | 180 | 390 | non | -0.13 | 308 | 51 | -0.0 |
| 09:45 | V2-F ecart qui grandit | Down | 0.21 | 0.47 | 257 | 147 | oui | +0.78 | 83 | 0 | +1.9 |
| 09:45 | desaccord 20 60-180 s | Up | 0.16 | 0.44 | 180 | 312 | non | -0.17 | 430 | 27 | -0.0 |
| 09:45 | desaccord 30 | Up | 0.13 | 0.44 | 175 | 385 | non | -0.14 | 353 | 15 | +1.5 |
| 09:45 | cohorte B : V2-F corri | Up | 0.10 | 0.31 | 173 | 401 | non | -0.11 | 291 | 24 | +2.1 |
| 09:45 | V2-F incertitude 0,01  | Up | 0.11 | 0.33 | 112 | 0 | non | — | 1735 | 0 | -1.9 |
| 09:45 | cohorte A : zone + mod | Up | 0.15 | 0.48 | 98 | 0 | non | — | 0 | 0 | — |
| 10:00 | V2-F incertitude 0,01  | Down | 0.36 | 0.67 | 184 | 0 | oui | — | 0 | 0 | +0.8 |
| 10:00 | cohorte B : V2-F corri | Down | 0.36 | 0.62 | 184 | 0 | oui | — | 0 | 0 | +0.8 |
| 10:00 | V2-F ecart qui grandit | Up | 0.20 | 0.50 | 172 | 0 | non | — | 54 | 0 | +1.5 |
| 10:00 | desaccord 30 | Up | 0.20 | 0.50 | 172 | 0 | non | — | 54 | 0 | +1.5 |
| 10:00 | desaccord 20 60-180 s | Up | 0.20 | 0.50 | 172 | 0 | non | — | 54 | 0 | +1.5 |
| 10:15 | V2-F ecart qui grandit | Up | 0.27 | 0.49 | 241 | 165 | non | -0.27 | 380 | 12 | +1.0 |
| 10:15 | cohorte B : V2-F corri | Up | 0.25 | 0.45 | 241 | 40 | non | -0.26 | 349 | 12 | +0.9 |
| 10:15 | V2-F incertitude 0,01  | Up | 0.24 | 0.45 | 241 | 25 | non | -0.25 | 215 | 12 | +0.9 |
| 10:15 | desaccord 20 60-180 s | Up | 0.28 | 0.48 | 146 | 179 | non | -0.29 | 5 | 0 | +2.2 |
| 10:15 | desaccord 30 | Up | 0.18 | 0.48 | 114 | 34 | non | -0.19 | 34 | 0 | +2.2 |
| 10:30 | V2-F ecart qui grandit | Up | 0.27 | 0.49 | 220 | 185 | non | -0.28 | 24 | 0 | +2.6 |
| 10:30 | V2-F incertitude 0,01  | Up | 0.26 | 0.46 | 219 | 65 | non | -0.27 | 24 | 0 | +1.7 |
| 10:30 | cohorte B : V2-F corri | Up | 0.26 | 0.47 | 219 | 60 | non | -0.27 | 24 | 0 | +1.7 |
| 10:30 | desaccord 30 | Up | 0.19 | 0.49 | 181 | 263 | non | -0.20 | 80 | 0 | +3.1 |
| 10:30 | desaccord 20 60-180 s | Up | 0.19 | 0.49 | 180 | 228 | non | -0.20 | 80 | 0 | +2.0 |
| 10:35 | V2-F ecart qui grandit | Down | 0.28 | 0.49 | 239 | 179 | oui | +0.72 | 79 | 5 | +1.9 |
| 10:35 | V2-F incertitude 0,01  | Down | 0.33 | 0.64 | 187 | 0 | oui | — | 57 | 0 | +1.2 |
| 10:35 | cohorte B : V2-F corri | Down | 0.33 | 0.61 | 187 | 0 | oui | — | 57 | 0 | +1.2 |
| 10:35 | desaccord 20 60-180 s | Down | 0.31 | 0.52 | 180 | 161 | oui | +0.67 | 178 | 36 | -0.3 |
| 10:35 | desaccord 30 | Up | 0.14 | 0.45 | 81 | 0 | non | — | 914 | 36 | +2.2 |
| 10:35 | cohorte A : zone + mod | Up | 0.15 | 0.47 | 76 | 89 | non | -0.16 | 1576 | 142 | -0.2 |
| 10:40 | V2-F incertitude 0,01  | Down | 0.33 | 0.54 | 148 | 152 | oui | +0.65 | 268 | 53 | +1.2 |
| 10:40 | cohorte B : V2-F corri | Down | 0.32 | 0.53 | 148 | 156 | oui | +0.67 | 138 | 36 | +2.5 |
| 10:40 | desaccord 20 60-180 s | Up | 0.29 | 0.49 | 110 | 172 | non | -0.28 | 451 | 36 | +1.5 |
| 10:40 | V2-F ecart qui grandit | Up | 0.28 | 0.49 | 109 | 179 | non | -0.28 | 449 | 36 | +1.3 |
| 10:40 | desaccord 30 | Down | 0.20 | 0.51 | 64 | 250 | oui | +0.82 | 421 | 36 | +2.8 |
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
| 11:20 | V2-F ecart qui grandit | Down | 0.27 | 0.47 | 231 | 185 | non | -0.27 | 1070 | 48 | +2.8 |
| 11:20 | cohorte B : V2-F corri | Down | 0.20 | 0.40 | 228 | 250 | non | -0.19 | 851 | 48 | +2.0 |
| 11:20 | desaccord 30 | Down | 0.15 | 0.45 | 222 | 333 | non | -0.16 | 2360 | 60 | +2.5 |
| 11:20 | V2-F incertitude 0,01  | Down | 0.14 | 0.34 | 221 | 357 | non | -0.11 | 2360 | 60 | +1.1 |
| 11:20 | desaccord 20 60-180 s | Down | 0.03 | 0.23 | 176 | 600 | non | -0.03 | 2086 | 0 | -1.5 |
| 11:25 | V2-F incertitude 0,01  | Down | 0.37 | 0.60 | 257 | 0 | non | — | 307 | 0 | -1.6 |
| 11:25 | cohorte B : V2-F corri | Down | 0.37 | 0.60 | 257 | 0 | non | — | 307 | 0 | -1.6 |
| 11:25 | V2-F ecart qui grandit | Down | 0.32 | 0.52 | 204 | 156 | non | -0.34 | 166 | 0 | +2.4 |
| 11:25 | desaccord 20 60-180 s | Up | 0.29 | 0.49 | 156 | 172 | oui | +0.70 | 1233 | 30 | +2.8 |
| 11:25 | desaccord 30 | Up | 0.13 | 0.46 | 154 | 0 | oui | — | 1304 | 54 | +3.0 |
| 11:25 | cohorte A : zone + mod | Up | 0.17 | 0.50 | 84 | 158 | oui | +0.82 | 201 | 44 | +3.3 |
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
| 12:05 | V2-F ecart qui grandit | Down | 0.24 | 0.44 | 254 | 208 | oui | +0.78 | 597 | 0 | +2.4 |
| 12:05 | desaccord 20 60-180 s | Down | 0.22 | 0.45 | 180 | 227 | oui | +0.78 | 298 | 42 | -0.0 |
| 12:05 | desaccord 30 | Down | 0.11 | 0.41 | 154 | 0 | oui | — | 2 | 0 | +2.0 |
| 12:05 | V2-F incertitude 0,01  | Down | 0.11 | 0.31 | 154 | 0 | oui | — | 2 | 0 | +1.8 |
| 12:05 | cohorte B : V2-F corri | Down | 0.11 | 0.33 | 154 | 0 | oui | — | 2 | 0 | +1.8 |
| 12:05 | cohorte A : zone + mod | Down | 0.16 | 0.49 | 154 | 0 | oui | — | 12 | 0 | +1.7 |
| 12:10 | V2-F incertitude 0,01  | Up | 0.48 | 0.70 | 230 | 0 | oui | — | 23 | 0 | -0.2 |
| 12:10 | cohorte B : V2-F corri | Up | 0.48 | 0.69 | 230 | 0 | oui | — | 23 | 0 | -0.2 |
| 12:10 | V2-F ecart qui grandit | Down | 0.20 | 0.40 | 209 | 250 | non | -0.21 | 373 | 0 | -0.9 |
| 12:10 | desaccord 20 60-180 s | Down | 0.16 | 0.39 | 180 | 312 | non | -0.17 | 195 | 0 | -0.0 |
| 12:25 | V2-F ecart qui grandit | Up | 0.21 | 0.42 | 270 | 238 | oui | +0.78 | 366 | 24 | +2.9 |
| 12:25 | desaccord 20 60-180 s | Up | 0.27 | 0.47 | 172 | 0 | oui | — | 0 | 0 | — |
| 12:25 | cohorte B : V2-F corri | Up | 0.28 | 0.48 | 172 | 0 | oui | — | 86 | 24 | +1.1 |
| 12:25 | V2-F incertitude 0,01  | Up | 0.28 | 0.49 | 172 | 0 | oui | — | 86 | 24 | +1.1 |
| 12:25 | desaccord 30 | Down | 0.15 | 0.47 | 106 | 5 | non | -0.16 | 82 | 5 | +1.6 |
| 12:30 | V2-F ecart qui grandit | Up | 0.24 | 0.44 | 271 | 208 | oui | +0.76 | 264 | 0 | +3.5 |
| 12:30 | desaccord 20 60-180 s | Up | 0.15 | 0.39 | 180 | 0 | oui | — | 649 | 0 | -0.0 |
| 12:30 | desaccord 30 | Up | 0.10 | 0.40 | 155 | 437 | oui | +0.89 | 152 | 12 | -0.4 |
| 12:30 | cohorte B : V2-F corri | Up | 0.10 | 0.32 | 155 | 437 | oui | +0.89 | 152 | 12 | -0.4 |
| 12:30 | V2-F incertitude 0,01  | Up | 0.10 | 0.30 | 155 | 437 | oui | +0.89 | 152 | 12 | -0.4 |
| 12:30 | cohorte A : zone + mod | Up | 0.20 | 0.51 | 154 | 0 | oui | — | 254 | 12 | -1.0 |
| 12:35 | V2-F ecart qui grandit | Up | 0.22 | 0.43 | 233 | 227 | oui | +0.77 | 102 | 0 | +2.8 |
| 12:35 | desaccord 20 60-180 s | Up | 0.09 | 0.34 | 180 | 556 | oui | +0.90 | 1033 | 12 | -0.0 |
| 12:35 | desaccord 30 | Up | 0.08 | 0.38 | 179 | 625 | oui | +0.92 | 853 | 12 | +1.8 |
| 12:35 | cohorte A : zone + mod | Up | 0.16 | 0.46 | 131 | 0 | oui | — | 329 | 12 | -0.9 |
| 12:35 | cohorte B : V2-F corri | Up | 0.16 | 0.36 | 131 | 0 | oui | — | 329 | 12 | -0.9 |
| 12:35 | V2-F incertitude 0,01  | Up | 0.26 | 0.49 | 130 | 7 | oui | +0.73 | 1193 | 59 | -1.5 |
| 12:40 | V2-F ecart qui grandit | Up | 0.10 | 0.30 | 262 | 0 | non | — | 49 | 24 | +1.8 |
| 12:40 | desaccord 20 60-180 s | Up | 0.08 | 0.32 | 180 | 257 | non | -0.09 | 152 | 0 | -0.0 |
| 12:40 | desaccord 30 | Up | 0.03 | 0.35 | 55 | 0 | non | — | 2762 | 0 | +1.7 |
| 12:55 | V2-F incertitude 0,01  | Up | 0.46 | 0.66 | 119 | 109 | oui | +0.52 | 520 | 48 | +2.9 |
| 12:55 | cohorte B : V2-F corri | Up | 0.35 | 0.62 | 114 | 0 | oui | — | 226 | 14 | +0.4 |
| 12:55 | V2-F ecart qui grandit | Up | 0.29 | 0.50 | 57 | 24 | oui | +0.70 | 740 | 0 | +2.9 |
| 12:55 | desaccord 30 | Up | 0.19 | 0.50 | 54 | 0 | oui | — | 71 | 0 | +2.8 |
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
| 13:25 | V2-F ecart qui grandit | Down | 0.28 | 0.49 | 273 | 0 | oui | — | 42 | 0 | +0.9 |
| 13:25 | cohorte B : V2-F corri | Down | 0.28 | 0.48 | 273 | 0 | oui | — | 42 | 0 | +0.9 |
| 13:25 | V2-F incertitude 0,01  | Up | 0.65 | 0.86 | 239 | 77 | non | -0.65 | 611 | 0 | +2.5 |
| 13:25 | desaccord 20 jeton 0,3 | Up | 0.37 | 0.58 | 222 | 135 | non | -0.37 | 1564 | 0 | +3.2 |
| 13:25 | desaccord 30 | Up | 0.28 | 0.58 | 221 | 179 | non | -0.29 | 781 | 0 | +1.9 |
| 13:25 | desaccord 20 60-180 s | Up | 0.23 | 0.55 | 180 | 0 | non | — | 100 | 0 | +1.0 |
| 13:30 | V2-F ecart qui grandit | Down | 0.26 | 0.46 | 242 | 192 | non | -0.27 | 223 | 36 | +1.7 |
| 13:30 | desaccord 20 60-180 s | Down | 0.28 | 0.48 | 146 | 179 | non | -0.28 | 48 | 15 | +3.3 |
| 13:30 | V2-F incertitude 0,01  | Down | 0.26 | 0.46 | 145 | 70 | non | -0.27 | 48 | 15 | +1.8 |
| 13:30 | cohorte B : V2-F corri | Down | 0.26 | 0.47 | 145 | 70 | non | -0.27 | 48 | 15 | +1.8 |
| 13:30 | desaccord 30 | Down | 0.19 | 0.49 | 119 | 0 | non | — | 239 | 24 | +3.0 |
| 13:35 | V2-F ecart qui grandit | Up | 0.24 | 0.47 | 267 | 208 | oui | +0.76 | 296 | 30 | +2.7 |
| 13:35 | V2-F incertitude 0,01  | Down | 0.70 | 0.93 | 248 | 0 | non | — | 350 | 48 | +2.4 |
| 13:35 | cohorte B : V2-F corri | Up | 0.32 | 0.53 | 151 | 156 | oui | +0.66 | 174 | 39 | +5.0 |
| 13:35 | desaccord 20 60-180 s | Up | 0.30 | 0.50 | 144 | 167 | oui | +0.74 | 173 | 0 | +1.5 |
| 13:35 | desaccord 30 | Up | 0.20 | 0.50 | 100 | 5 | oui | +0.79 | 5 | 0 | +2.4 |
| 13:40 | V2-F ecart qui grandit | Up | 0.23 | 0.46 | 188 | 217 | non | -0.24 | 350 | 0 | +3.1 |
| 13:40 | desaccord 20 60-180 s | Up | 0.18 | 0.42 | 180 | 122 | non | -0.19 | 494 | 0 | -0.4 |
| 13:40 | desaccord 30 | Up | 0.13 | 0.43 | 148 | 22 | non | -0.14 | 111 | 0 | +2.1 |
| 13:40 | cohorte B : V2-F corri | Up | 0.08 | 0.28 | 134 | 42 | non | -0.09 | 62 | 0 | +2.4 |
| 13:40 | V2-F incertitude 0,01  | Up | 0.06 | 0.26 | 113 | 0 | non | — | 317 | 0 | +2.6 |
| 14:05 | V2-F ecart qui grandit | Down | 0.26 | 0.46 | 189 | 192 | oui | +0.73 | 26 | 14 | +3.8 |
| 14:05 | desaccord 20 60-180 s | Down | 0.25 | 0.46 | 180 | 200 | oui | +0.74 | 106 | 12 | +3.0 |
| 14:05 | desaccord 30 | Down | 0.16 | 0.47 | 145 | 312 | oui | +0.85 | 96 | 0 | +2.4 |
| 14:05 | cohorte B : V2-F corri | Down | 0.15 | 0.35 | 145 | 333 | oui | +0.85 | 84 | 0 | +2.4 |
| 14:05 | V2-F incertitude 0,01  | Down | 0.23 | 0.53 | 136 | 120 | oui | +0.76 | 65 | 0 | -1.4 |
| 14:10 | V2-F ecart qui grandit | Down | 0.30 | 0.50 | 238 | 167 | non | -0.32 | 751 | 55 | +2.3 |
| 14:10 | V2-F incertitude 0,01  | Down | 0.30 | 0.51 | 238 | 167 | non | -0.32 | 751 | 55 | +2.3 |
| 14:10 | cohorte B : V2-F corri | Down | 0.30 | 0.51 | 238 | 167 | non | -0.32 | 751 | 55 | +2.3 |
| 14:10 | desaccord 30 | Down | 0.20 | 0.50 | 221 | 250 | non | -0.21 | 634 | 68 | +2.3 |
| 14:10 | desaccord 20 60-180 s | Down | 0.23 | 0.50 | 180 | 0 | non | — | 79 | 0 | +3.0 |
| 14:15 | V2-F incertitude 0,01  | Up | 0.37 | 0.57 | 227 | 135 | non | -0.38 | 343 | 0 | +2.5 |
| 14:15 | cohorte B : V2-F corri | Up | 0.36 | 0.57 | 226 | 139 | non | -0.38 | 343 | 0 | +2.5 |
| 14:15 | V2-F ecart qui grandit | Up | 0.33 | 0.53 | 226 | 152 | non | -0.35 | 294 | 0 | +1.9 |
| 14:15 | desaccord 20 jeton 0,3 | Up | 0.36 | 0.57 | 201 | 20 | non | -0.38 | 64 | 0 | +0.5 |
| 14:15 | desaccord 20 60-180 s | Up | 0.33 | 0.54 | 172 | 0 | non | — | 2145 | 0 | +1.3 |
| 14:15 | desaccord 30 | Up | 0.23 | 0.54 | 169 | 134 | non | -0.23 | 828 | 0 | +2.1 |
| 14:15 | cohorte A : zone + mod | Up | 0.25 | 0.62 | 85 | 0 | non | — | 70 | 0 | -0.7 |
| 14:30 | V2-F ecart qui grandit | Down | 0.23 | 0.44 | 259 | 217 | non | -0.23 | 379 | 40 | +1.9 |
| 14:30 | desaccord 20 60-180 s | Down | 0.07 | 0.32 | 180 | 262 | non | -0.07 | 251 | 0 | +6.0 |
| 14:35 | V2-F ecart qui grandit | Down | 0.27 | 0.48 | 192 | 58 | non | -0.28 | 85 | 0 | +3.2 |
| 14:35 | cohorte B : V2-F corri | Down | 0.27 | 0.47 | 192 | 58 | non | -0.28 | 85 | 0 | +3.2 |
| 14:35 | V2-F incertitude 0,01  | Down | 0.26 | 0.47 | 192 | 13 | non | -0.27 | 40 | 0 | +3.2 |
| 14:35 | desaccord 20 60-180 s | Down | 0.23 | 0.46 | 180 | 150 | non | -0.24 | 592 | 62 | -0.0 |
| 14:35 | desaccord 30 | Down | 0.09 | 0.39 | 160 | 283 | non | -0.09 | 290 | 0 | +3.5 |
| 14:40 | V2-F ecart qui grandit | Up | 0.22 | 0.43 | 261 | 227 | non | -0.21 | 363 | 12 | +1.1 |
| 14:40 | V2-F incertitude 0,01  | Up | 0.23 | 0.56 | 134 | 0 | non | — | 373 | 0 | +2.5 |
| 14:40 | cohorte B : V2-F corri | Up | 0.23 | 0.56 | 134 | 0 | non | — | 373 | 0 | +2.5 |
| 14:40 | desaccord 20 60-180 s | Up | 0.23 | 0.52 | 134 | 0 | non | — | 373 | 0 | +2.5 |
| 14:40 | cohorte A : zone + mod | Up | 0.17 | 0.48 | 73 | 0 | non | — | 0 | 0 | — |
| 14:40 | desaccord 30 | Up | 0.17 | 0.48 | 73 | 0 | non | — | 0 | 0 | — |
| 14:45 | V2-F incertitude 0,01  | Down | 0.60 | 0.80 | 187 | 51 | non | -0.62 | 98 | 0 | -0.6 |
| 14:45 | V2-F ecart qui grandit | Up | 0.20 | 0.42 | 187 | 15 | oui | +0.79 | 136 | 0 | +1.9 |
| 14:45 | desaccord 20 60-180 s | Up | 0.24 | 0.44 | 180 | 140 | oui | +0.75 | 354 | 0 | -0.0 |
| 14:45 | cohorte B : V2-F corri | Up | 0.22 | 0.42 | 128 | 24 | oui | +0.77 | 71 | 23 | +0.4 |
| 14:45 | cohorte A : zone + mod | Up | 0.22 | 0.52 | 128 | 0 | oui | — | 71 | 23 | +0.3 |
| 14:45 | desaccord 30 | Up | 0.22 | 0.52 | 128 | 0 | oui | — | 71 | 23 | +0.3 |
| 14:45 | desaccord 20 jeton 0,3 | Up | 0.35 | 0.56 | 128 | 0 | oui | — | 134 | 23 | -0.9 |
| 14:50 | V2-F ecart qui grandit | Down | 0.25 | 0.45 | 229 | 0 | non | — | 226 | 13 | +1.1 |
| 14:50 | cohorte B : V2-F corri | Down | 0.19 | 0.40 | 188 | 0 | non | — | 22 | 0 | +1.9 |
| 14:50 | V2-F incertitude 0,01  | Down | 0.19 | 0.41 | 188 | 0 | non | — | 22 | 0 | +1.8 |
| 14:50 | cohorte A : zone + mod | Down | 0.19 | 0.49 | 188 | 0 | non | — | 22 | 0 | +1.8 |
| 14:50 | desaccord 30 | Down | 0.19 | 0.49 | 188 | 0 | non | — | 22 | 0 | +1.8 |
| 14:50 | desaccord 20 60-180 s | Up | 0.27 | 0.47 | 124 | 185 | oui | +0.72 | 53 | 5 | +5.5 |
| 14:55 | V2-F incertitude 0,01  | Down | 0.55 | 0.75 | 263 | 0 | oui | — | 149 | 0 | -1.5 |
| 14:55 | cohorte B : V2-F corri | Down | 0.55 | 0.75 | 263 | 0 | oui | — | 149 | 0 | -1.5 |
| 14:55 | V2-F ecart qui grandit | Up | 0.20 | 0.41 | 262 | 250 | non | -0.21 | 892 | 42 | +2.3 |
| 14:55 | desaccord 30 | Up | 0.08 | 0.39 | 181 | 46 | non | -0.09 | 165 | 0 | +3.8 |
| 14:55 | desaccord 20 60-180 s | Up | 0.08 | 0.39 | 180 | 5 | non | -0.09 | 166 | 0 | +3.0 |
| 15:00 | V2-F ecart qui grandit | Up | 0.28 | 0.49 | 128 | 179 | non | -0.29 | 335 | 12 | +2.5 |
| 15:00 | desaccord 20 60-180 s | Up | 0.28 | 0.49 | 128 | 179 | non | -0.29 | 335 | 12 | +2.5 |
| 15:00 | cohorte B : V2-F corri | Up | 0.23 | 0.44 | 91 | 0 | non | — | 173 | 24 | +1.5 |
| 15:00 | V2-F incertitude 0,01  | Up | 0.20 | 0.41 | 90 | 0 | non | — | 0 | 0 | — |
| 15:00 | desaccord 30 | Up | 0.17 | 0.47 | 75 | 0 | non | — | 7 | 0 | +1.1 |
| 15:05 | V2-F incertitude 0,01  | Up | 0.45 | 0.67 | 265 | 0 | oui | — | 35 | 0 | +2.3 |
| 15:05 | cohorte B : V2-F corri | Up | 0.45 | 0.66 | 265 | 0 | oui | — | 35 | 0 | +2.3 |
| 15:05 | V2-F ecart qui grandit | Down | 0.20 | 0.40 | 265 | 188 | non | -0.21 | 1218 | 77 | +1.9 |
| 15:05 | desaccord 20 60-180 s | Down | 0.21 | 0.42 | 180 | 238 | non | -0.22 | 554 | 25 | +3.0 |
| 15:05 | desaccord 30 | Down | 0.21 | 0.52 | 82 | 0 | non | — | 41 | 0 | +2.3 |
| 15:15 | V2-F ecart qui grandit | Up | 0.26 | 0.48 | 221 | 192 | non | -0.27 | 88 | 0 | +2.5 |
| 15:15 | desaccord 20 60-180 s | Up | 0.26 | 0.47 | 158 | 50 | non | -0.27 | 456 | 0 | +2.9 |
| 15:15 | cohorte B : V2-F corri | Up | 0.18 | 0.38 | 155 | 69 | non | -0.19 | 407 | 21 | +2.8 |
| 15:15 | desaccord 30 | Up | 0.13 | 0.44 | 153 | 64 | non | -0.14 | 328 | 34 | +3.1 |
| 15:15 | V2-F incertitude 0,01  | Up | 0.11 | 0.51 | 105 | 0 | non | — | 296 | 48 | +0.7 |
| 15:15 | cohorte A : zone + mod | Up | 0.15 | 0.50 | 104 | 333 | non | -0.13 | 622 | 48 | +0.4 |
| 15:20 | V2-F ecart qui grandit | Down | 0.21 | 0.43 | 242 | 184 | non | -0.22 | 624 | 23 | +2.5 |
| 15:20 | desaccord 30 | Down | 0.12 | 0.42 | 198 | 20 | non | -0.13 | 38 | 0 | +2.9 |
| 15:20 | desaccord 20 60-180 s | Down | 0.21 | 0.42 | 180 | 238 | non | -0.22 | 190 | 36 | -0.2 |
| 15:20 | cohorte B : V2-F corri | Down | 0.20 | 0.41 | 171 | 0 | non | — | 121 | 24 | +0.3 |
| 15:20 | V2-F incertitude 0,01  | Down | 0.20 | 0.42 | 171 | 0 | non | — | 121 | 24 | +0.3 |
| 15:35 | V2-F ecart qui grandit | Up | 0.17 | 0.38 | 294 | 294 | oui | +0.82 | 175 | 12 | +2.8 |
| 15:35 | V2-F incertitude 0,01  | Up | 0.23 | 0.43 | 266 | 17 | oui | +0.76 | 70 | 0 | -0.6 |
| 15:35 | cohorte B : V2-F corri | Up | 0.23 | 0.43 | 266 | 17 | oui | +0.76 | 70 | 0 | -0.6 |
| 15:35 | desaccord 20 60-180 s | Down | 0.14 | 0.37 | 104 | 357 | non | -0.13 | 992 | 0 | +2.3 |
| 15:35 | desaccord 30 | Down | 0.04 | 0.35 | 67 | 15 | non | -0.04 | 3071 | 0 | -1.2 |