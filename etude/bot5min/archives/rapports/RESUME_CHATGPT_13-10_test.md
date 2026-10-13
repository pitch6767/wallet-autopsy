# Bot95 — résumé pour ChatGPT : résultats du TEST (13.10.2026)

Aucun ordre réel. H816, H821, R4, les bots actifs et les fantômes gelés sont inchangés.

**Périodes, séparées**

| Période | Cycles | Rôle |
|---|---|---|
| Apprentissage | 216 | Avant le 12.10 12:00 UTC, deux premiers tiers |
| Validation | 109 | Avant le 12.10 12:00 UTC, dernier tiers |
| **Test** | **144** | 12.10, de 12:00 à 24:00 UTC, calculé **une seule fois** le 13.10 à 00:40 UTC, protocoles figés avant |
| Confirmation | — | Données à partir du 13.10 (période réservée), prévue le 15.10 |

## 1. Cerveau de règlement (H1016)

Sur le test, le Brier est de 0,1770 pour le cerveau et de 0,1772 pour le prix Polymarket. L'écart est de −0,0002, IC [−0,0021 ; +0,0015]. **Le cerveau égale le marché sans le battre.** La famille « avantage du cerveau » n'a fait aucune entrée sur le test.

## 2. H1003–H1046 : gestion de position sur le favori (0,60–0,85), 111 entrées

| Politique | Validation | Test | Pertes > 6 $ (test) |
|---|---|---|---|
| Conserver 10 $ | +25 $ | **−98 $** | 37 |
| Moteur strict T7s | −22 $ | −35 $ | 0 |
| Strict 5 CHF T6 | −25 $ | −47 $ | 0 |
| Moteur complet T7 | −28 $ | −70 $ | 5 |

- Le gain des politiques prudentes sur conserver **change de signe** : environ −47 $ en validation, +51 à +63 $ sur le test. Les IC corrigés contiennent zéro.
- **Sauvetage** (vente ou couverture à −0,15) : −1 $ contre conserver, IC [−97 ; +95]. Les pertes > 6 $ passent de 37 à 2, mais 39 gagnants sur 100 sont abîmés.
- **Protection des gains :** P-HA +45 $, IC [−10 ; +101]. Le problème visé est rare : 1 gagnant sur 22 a fini perdant.
- **Verdict : tout est « non démontré ».**

## 3. H1047–H1050 : étude séparée

**Récupération.** Après une baisse de 0,15, la victoire finale est de 43 % pour un prix de 0,46. Le 57 % de la validation était un hasard de période. **Le prix du marché est la bonne probabilité.**

**Faux sauvetages.** Les pertes évitées (+233 $) égalent les gagnants sacrifiés (−234 $).

**Trailing**, écart avec conserver :

| Règle | Validation | Test |
|---|---|---|
| Fondamental F1 | +33 $ | −63 $ |
| Marge Chainlink F2 | +19 $ | −44 $ |

**Protection sélective :** tous les IC contiennent zéro.

**Les 13 règles sont abandonnées.**

## 4. H1051 : sorties sur les billets bon marché et les stratégies des premiers jours

**Conserver (H0)**, validation → test :
- achats ≤ 0,10 : −267 → **+94 $**, avec 13 jackpots ;
- achats 0,11–0,25 : −312 → +70 $ ;
- désaccord 20, 60–180 s : −201 → +63 $.

**Les sorties qui aidaient en validation coûtent sur le test** :

| Règle (famille) | Validation | Test |
|---|---|---|
| Trailing 30 % (≤ 0,10) | +31 $ | −388 $ |
| Marge Chainlink (≤ 0,10) | +139 $ | −325 $ |
| Free-roll (0,11–0,25) | +118 $ | −185 $ |

**Cause :** elles coupent les jackpots, absents de la validation. **Les 11 règles sont abandonnées.**

## 5. H1052 : sorties sur les 10 stratégies gagnantes du 12.10

Après-midi (565 trades, 64 jackpots) : conserver fait +2 170 $.

| Règle | Résultat | Écart avec conserver |
|---|---|---|
| Verrou à 0 $ dès +10 $ | +1 055 $ | −1 115 $, IC [−2 388 ; −30] |
| Prise de gain ×2 | +263 $ | — |
| Trailing du billet | −5 $ | — |

- Le matin donnait la même chose : conserver +2 349 $, toutes les sorties −387 à −1 494 $.
- Seule exception : la stratégie perdante « désaccord 20 Binance ou perp ». Les sorties l'améliorent de +35 à +109 $, mais c'est une stratégie sur dix, choisie après coup.

## 6. Conclusions (Claude propose, Pitch décide)

1. **Ne pas couper les positions.** Sur les favoris comme sur les billets bon marché, conserver jusqu'au règlement reste la référence. Les sorties transforment des jackpots en petits gains.
2. **Pour réduire les perdantes, agir à l'entrée, pas à la sortie.**
   - Fantômes en cours depuis le 12.10 : consensus K2, K5, K9 et K5 anti-bête (veto quand les portefeuilles « bêtes » achètent contre nous dans les 10 s).
   - Premiers verdicts sur les données du 13.10, le 14.10.
3. **Alerte de retournement (H1055)**, préenregistrée, en exploration : la probabilité qu'un favori à 0,80 se retourne passe de 15 % à 27–33 %, de façon stable sur les périodes. Le signal : les portefeuilles « bêtes » achètent ce favori pendant que les « malins » le vendent. **Ce n'est pas encore testé.**
4. **Aucun IC ne démontre une rentabilité.** Rien n'est à mettre en réel.

## Fichiers

- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_reversal_h1003.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_recuperation_h1047.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_trailing_bas_h1051.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_gagnantes_jour_h1052_apres_midi.md
- Rapports : https://github.com/pitch6767/wallet-autopsy/tree/main/etude/bot5min/archives/rapports
