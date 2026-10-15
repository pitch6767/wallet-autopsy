# Bot95 — résumé pour ChatGPT : confirmation et liquidations (15.10.2026)

Ce résumé met à jour celui du 13.10, consacré aux résultats du test.
- Aucun ordre réel.
- H816, H821, R4, les bots actifs et les fantômes gelés sont inchangés.
- Chaque calcul a été lancé **une seule fois**, avec un protocole figé avant de voir les données.

**Périodes**

| Période | Cycles de 5 min | Rôle |
|---|---|---|
| Apprentissage / validation | 216 / 109 | Avant le 12.10 12:00 UTC |
| Test | 144 | 12.10, de 12:00 à 24:00 UTC (calculé le 13.10) |
| **Confirmation** | **674** | Du 13.10 00:00 au 15.10 12:50 UTC (calculée le 15.10) |

## 1. Confirmation de H1003–H1051 : les conclusions du test tiennent

**Cerveau de règlement.** Sur 14 070 décisions, le Brier est de 0,1660 pour le cerveau contre 0,1658 pour le marché, soit +0,0003 [−0,0006 ; +0,0011]. **Le prix Polymarket reste la meilleure probabilité.**

**Favori du marché (0,60–0,85), 10 $ par entrée, 530 entrées**

| Politique | Test | Confirmation | Pertes > 6 $ |
|---|---|---|---|
| Conserver | −98 $ | **−397 $** | 177 |
| Moteur strict T7s | −35 $ | −196 $ | 0 |
| Strict 5 CHF T6 | −47 $ | −232 $ | 0 |

- **Sauvetage** (vente à −0,15) : +58 $ [−147 ; +258]. Les pertes évitées (+1 109 $) égalent les gagnants sacrifiés (−1 051 $).
- **Protection des gains :** P-HA passe de +45 $ sur le test à −78 $ sur la confirmation.
- **Récupération après −0,15 :** 46 % de victoires pour un prix de 0,486. Le marché a raison.
- **Verdict : tout reste « non démontré » ou « abandonné ».**

**Billets bon marché (H1051).** Les 11 règles de sortie sont abandonnées dans toutes les familles. Elles coupent les jackpots : la prise de gain ×2 n'en garde que 13 sur 44. La « seule exception » du test passe de +89 $ à −345 $.

**Mais le gain de « conserver » observé sur le test était un hasard :**

| Famille | Test | Confirmation |
|---|---|---|
| achats ≤ 0,10 (589 entrées) | +94 $ | **−1 074 $** |
| achats 0,11–0,25 (615 entrées) | +70 $ | **−405 $** |

## 2. Nouveau : moteur de liquidations H994–H1002

Protocole préenregistré le 12.10, séparé de l'étude H986–H993.
- **Apprentissage :** 12.10 après-midi, 108 cycles.
- **Validation :** 13.10, 279 cycles.
- **Test :** 14–15.10, 423 cycles.
- **Données :** 333 salves de liquidations de 50 000 $ ou plus en 5 s (Bybit + Binance).

**Ce qui est solide (descriptif)**
- **Les liquidations suivent le prix.** Le prix va déjà dans le sens forcé 1 à 30 s avant : +23 $ sur 5 s, juste avant la salve, contre 0 $ pour les témoins.
- **Les salves arrivent en grappes :** 52 % de chances d'une 2e salve dans les 30 s, contre 7 % sans salve.
- **Binance suit Bybit d'environ 1 s.**
- **Polymarket réagit 1,2 s après la première liquidation.** Dans 43 % des cas, c'est avant notre première exécution possible.
- **Après une salve, le règlement officiel va moins loin que le modèle M0 ne le prévoit**, avec le même signe sur les deux périodes : −0,06 [−0,12 ; −0,01] sur le test.

**Ce qui échoue**
- **Variables dérivées :** ajouter mark/index, open interest et funding **dégrade** la prévision des salves. Le ΔAUC est entièrement négatif.
- **Calibration :** les variables de liquidation n'améliorent pas le Brier du règlement (IC contenant 0).
- **Alerte avant la salve (H1000) :** sur le test, elle anticipe 29 % des salves, avec 28 s d'avance, mais **9 alertes sur 10 sont fausses**.
- **P&L, 20 $ par alerte :**
  - validation : −375 $ [−723 ; +5] ;
  - test : −375 $ [−827 ; +102].
- **Acheter après la salve :** −148 $ [−358 ; +42], pour un prix payé de 0,82. Le marché a déjà intégré le mouvement.
- **Verdict selon le critère de poursuite : on arrête.**

**Limites.**
- Le test du régime prix × open interest (H996) n'a pas produit de résultat, à cause d'un défaut technique.
- L'apprentissage ne dure que 9 heures.

## 3. Conclusions (Claude propose, Pitch décide)

1. **Aucun IC ne montre une rentabilité.** Rien n'est à mettre en réel.
2. **Le prix Polymarket est bien calibré.** Ni notre cerveau, ni les liquidations, ni le flux BTC ne le battent de façon démontrée.
3. **Ne pas couper les positions** : la confirmation le redit.
4. **Les entrées elles-mêmes perdent** sur la période longue, qu'il s'agisse des favoris de 0,60 à 0,85 ou des billets de 0,25 et moins. Le problème est à l'entrée, pas à la sortie.

**Ma question à ChatGPT :** sur un marché aussi bien calibré, quelle source d'avantage reste plausible pour un preneur qui a 164 ms de délai ?

## Fichiers

- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_liq_h994.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_reversal_h1003_confirmation.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_recuperation_h1047_confirmation.md
- https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_trailing_bas_h1051_confirmation.md
- Rapports : https://github.com/pitch6767/wallet-autopsy/tree/main/etude/bot5min/archives/rapports
