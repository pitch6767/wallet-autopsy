# Bot95 — résumé pour ChatGPT (12.10.2026, 18:45 heure suisse)

Aucun ordre réel. H816, H821, R4, les bots actifs et les fantômes gelés sont inchangés. Aucun nouveau fantôme.

**Important : tous les chiffres ci-dessous viennent des périodes d'apprentissage et de validation.** Le test, sur le 12.10 de 12:00 à 24:00 UTC, n'a pas encore été calculé. Il sera calculé une seule fois cette nuit, à 00:40 UTC. Une confirmation sur les données à partir du 13.10 suivra le 15.10. Aucun résultat ne prouve donc encore quoi que ce soit.

## 1. Enregistrement (serveur Dublin, lecture seule)

- **Nouveaux flux :**
  - Bybit BTCUSDT : mark, index, open interest et funding (environ 8 mises à jour par seconde) ;
  - open interest Binance toutes les 5 s ;
  - Binance perp : mark, liquidations et transactions agressives. L'ancienne adresse WebSocket de Binance ne diffuse plus ces flux depuis avril ; ils passent maintenant par l'adresse `/market`.
- **Cycles tronqués, corrigé :** un plafond de 120 000 événements Polymarket par cycle coupait 10 cycles sur 362, aux heures chargées. Il est passé à 1 000 000 (version 8afb99a3762d, en ligne). Les cycles déjà coupés ne peuvent pas être récupérés.

## 2. H994–H1002, moteur de liquidations

- Protocole validé par Pitch le 12.10 à 17:03, préenregistré (commits 5ee9f5a et 8629a86).
- **Périodes :** apprentissage le 12.10 de 15:00 à 24:00 UTC, validation le 13.10, test à partir du 14.10.
- **Salve :** au moins 50 000 $ de liquidations du même côté en 5 s, Bybit et Binance réunis.
- **Contrôles ajoutés par Pitch :**
  - pression 1, 3, 5, 10 et 30 s avant chaque salve, comparée à des périodes témoins ;
  - délais réels avertissement → liquidation → BTC → Polymarket → exécution ;
  - comparaison à 164, 200, 250 et 500 ms.
- **Analyse :** prévue le 15.10 à 12:52 UTC. Pas encore de résultat.

## 3. H1003–H1046 : moteur adaptatif, sauvetage et protection des gains (une seule étude, protocole figé)

**Cerveau de règlement.** Il est appris sur l'apprentissage et colle au prix du marché :

> logit p = −0,05 − 0,003 × logit(M0) + 0,94 × logit(milieu Polymarket)

Le modèle Chainlink (M0) n'apporte rien une fois le prix connu. Avec carnet à deux côtés, il ne trouve **aucun avantage exploitable**. Les seuls « avantages » apparaissaient quand le carnet n'avait qu'un côté (billets à 0,01). Ce défaut a été corrigé avant le test (amendement A1). Une seconde façon d'entrer, sur le favori du marché, a été ajoutée pour étudier la gestion de position (amendement A2).

**Validation : 99 cycles, 78 entrées sur le favori, mise 10 $, conserver = +103 $**

| Approche | Résultat ou écart |
|---|---|
| Achat unique 50 $ | +533 $, soit la même chose ×5 |
| Renforts (T1, T2, T2p) | jamais déclenchés : aucun avantage n'apparaît |
| Couverture après détérioration (T3), vente puis inversion (T4), échelle de réaction | +54 à +80 $ |
| Gestion simultanée Up/Down (T5) et moteur adaptatif complet (T7) | environ −30 $ |
| Mode strict 5 CHF (T6, T7s) | environ −20 $, mais **plus aucune perte au-delà de 5 CHF** |

### Sauvetage (H1036–H1040), validation

- 49 positions sont devenues défavorables, c'est-à-dire que leur probabilité a reculé de 0,15. **57 % d'entre elles ont fini gagnantes.**
- Vendre, couvrir ou faire moitié-moitié ramène la perte moyenne de −9,5 $ à environ −3 $. Mais le coût est d'environ −100 $ par rapport à conserver.
- La couverture tardive (billet ≤ 0,25) coûte −13 $, ce qui n'est pas significatif.
- L'inversion complète coûte −248 $.
- **Vendre ou acheter la jambe opposée, à risque égal : résultat identique** (−56 $ contre −57 $).

### Protection des gains (H1041–H1046), validation, favori à environ 0,71

- **Le problème visé est rare :** sur 14 positions qui ont été à +5 $ liquidables ou plus, une seule a fini perdante. Le profit abandonné moyen est de 0,19 $ par position.
- Take-profit +100 % et +200 % : jamais déclenchés.
- Trailing 10 à 40 % : −40 à −55 $.
- Trailing fondamental : −45 $.
- Free-roll : −120 $.
- Vente partielle : −29 $.
- Verrou à 5 $ : +4 $, ce qui n'est pas significatif.
- Plafond de perte à 5 CHF : −67 $.

## 4. H1047–H1050 : étude séparée

**Récupération.** Au premier instant défavorable (probabilité −0,15), la victoire finale est de 36 % en apprentissage et de 65 % en validation. Le prix Polymarket du moment vaut environ 0,46 et 0,50. **Le prix du marché est en moyenne une bonne estimation des chances.** Le 57 % vient surtout de la période, pas d'une erreur du marché. Aucun modèle ne fait mieux que le prix seul pour prévoir la récupération ou la victoire.

**Faux sauvetages.** Une intervention immédiate évite environ 92 $ de pertes. Mais elle sacrifie environ 190 $ sur 28 des 63 positions qui auraient gagné : net −100 $. Aucun jackpot n'est concerné, puisque les entrées se font à 0,60 ou plus.

**Trailing, écart avec conserver (validation)**

| Règle | Écart |
|---|---|
| Trailing sur le prix du billet | −150 $, significatif même après correction |
| Trailing sur le profit liquidable | −39 $ |
| Trailing fondamental (probabilité + marge Chainlink) | −18 $ |
| Sortie quand la marge Chainlink est contre nous à moins de 2 min | −2 $ |

**Protection sélective.** Dès +2 $ de gain : −45 $. Dès +5 $ : +3 à +4 $, non significatif. Dès +8 $ : jamais déclenchée. Vendre ou acheter l'opposé donnent le même résultat.

## 5. H1051 : trailing sur les achats très bas et les stratégies des premiers jours (étude séparée)

Les entrées sont les vrais signaux des fantômes de Dublin, plus des achats génériques entre 0,01 et 0,10 et entre 0,11 et 0,25. Tous les écarts ci-dessous sont mesurés par rapport à conserver, sur la validation, avec des IC non corrigés. **Aucun n'est démontré.**

- **La base perd** dans presque toutes les familles :
  - désaccord 30 : −133 $ ;
  - V2-F écart qui grandit : −201 $ ;
  - achats ≤ 0,10 : −432 $ ;
  - achats 0,11–0,25 : −313 $.
- **Sur les billets bon marché, sortir tôt aide souvent, contrairement aux favoris :**
  - désaccord 30 : take-profit ×2 +96 $ ;
  - V2-F incertitude 0,01 % : take-profit ×2 +119 $ ;
  - V2-F écart qui grandit : trailing 30 % +116 $ ;
  - achats ≤ 0,10 : trailing 30 % +175 $ ;
  - achats 0,11–0,25 : free-roll +147 $ et sortie sur marge Chainlink +153 $.
- **Même avec ces protections, presque toutes les familles restent en perte.** Les IC sont larges, et le verdict dépendra du test (correction pour 11 comparaisons) et de la confirmation.

## 6. Conclusion provisoire (Claude propose, Pitch décide)

1. Sur les favoris, conserver jusqu'au règlement reste le meilleur choix. Toute intervention coûte plus qu'elle ne sauve.
2. Seul le plafond strict à 5 CHF tient sa promesse, sans perte au-delà. Il coûte environ 20 à 70 $ sur 99 cycles selon la variante.
3. Sur les billets bon marché, prise de gain et trailing méritent le test et la confirmation. Mais ils ne rendent pas ces stratégies rentables sur la validation.
4. Le prix Polymarket reste la meilleure probabilité disponible. Aucun de nos modèles ne le bat.

## Fichiers

- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_reversal_h1003_controle.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_recuperation_h1047_controle.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_trailing_bas_h1051_controle.md
- Protocoles : reversal_h1003.py, recuperation_h1047.py, trailing_bas_h1051.py, liq_h994.py (même dossier).
