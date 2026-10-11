# Bot95 — H817 : moteur de sauvetage prédictif et progressif — PRÉLIMINAIRE (hors ligne)

Généré le 11.10.2026 19:38 UTC. Positions initiales : 70 décisions uniques exécutées (mise 20 $, 164 ms) sur 54 cycles Dublin ; apprentissage 36 / test 34 (coupure 12:30 UTC). Aucun ordre ; R4, H816 et fantômes inchangés ; période réservée non lue.

## 0. Audit des données (livrable 1)

| Donnée | Disponible | Limite |
|---|---|---|
| Carnet Polymarket (jeton Up ; Down = miroir) | oui, cycles Dublin | changements suivis à ±3 c du meilleur prix ; carnet complet toutes les 10 s → profondeur lointaine approximative |
| Transactions des deux jetons, heure ms | oui | — |
| Binance / Bybit / OKX / Coinbase, Chainlink (RTDS + PolyBolt) | oui, une valeur par 50 ms | ticks intermédiaires perdus (modèle recalculé fidèle à ±0,005 pour ~3/4 des signaux) |
| Prix à battre (strike), moyennes de règlement | oui (strike enregistré ; règlement officiel) | — |
| Annulation d'un ordre preneur pendant le retard | **impossible** (doc Polymarket : « pending and cannot be canceled ») | G2 réglé : seule l'option « envoi différé » (G4) reste |
| Retard preneur actuel | 150 ms (changelog du 04.09.2026) ; la page « order lifecycle » mentionne encore 250 ms | testé à 164, 264 et 500 ms |
| Couverture par la jambe inverse | carnet Down = miroir du carnet Up | **acheter Down à 1 − acheteur(Up) = vendre Up au même prix, mêmes frais, même profondeur** (voir §3) |
| Positions | 70 | une seule journée : faible puissance |

## 1. H817-A — Calibration de la probabilité de victoire (pendant la vie des positions)

| P_win modèle | Observations | Victoire observée | Milieu Polymarket moyen |
|---|---|---|---|
| 0.0–0.1 | 33 | 0 % | nan % |
| 0.1–0.3 | 482 | 0 % | 5 % |
| 0.3–0.5 | 4415 | 22 % | 20 % |
| 0.5–0.7 | 2369 | 77 % | 69 % |
| 0.7–0.9 | 140 | 100 % | 97 % |

Brier : modèle 0.215 ; milieu Polymarket 0.144 (plus bas = mieux ; observations corrélées dans une même position).

## 2. H817-B / J — Le carnet réagit-il en retard sur la probabilité ?

Chutes de P_win ≥ 5 points en 1 s : 184 (sur 33 cycles). Au même instant, l'acheteur avait déjà baissé de +0.0 c (médiane) pour une chute de P_win de -5.7 points.
- Vente à l'acheteur vu, exécutée 164 ms plus tard : au moins une part exécutable dans 84 % des cas (quantité médiane 261 parts).
- L'acheteur 3 s plus tard a encore baissé de +0.0 c (médiane) ; il a remonté dans 26 % des cas.

## 3. H817-D / K — Couverture par la jambe inverse

Fait de structure : le meilleur vendeur de Down est exactement 1 − meilleur acheteur de Up (mêmes ordres, appariés par Polymarket), et les frais 0,07·q·(1−q) sont identiques pour q = 1 − p. Acheter n parts de la jambe inverse verrouille donc exactement le même résultat que vendre n parts de la position, à la même profondeur. La seule différence : la couverture immobilise le capital jusqu'au règlement (ou demande une fusion). Aucun arbitrage n'existe tant que vendeur Up + vendeur Down ≥ 1 $ (vérifié : la somme des deux meilleurs vendeurs n'est jamais < 1 $ dans nos carnets puisque le vendeur Down EST le miroir de l'acheteur Up). → Les tests de couverture se confondent avec les tests de vente partielle ci-dessous.

## 4. SELL — réglage choisi sur l'apprentissage : **SELL m=0.1 f=0.25** (parmi 12)

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOLD — test | +71.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +13.2 % | -17.73 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 476 % |
| SELL m=0.1 f=0.25 — test | +75.1 | +3.2 | +0.09 [-0.94 ; +1.26] | +13.8 % | -11.11 | 127.4 | -20.0 | +37.2 | +34.0 | 8 | 12 / 17 | 421 % |
| HOLD — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| SELL m=0.1 f=0.25 — apprentissage | +259.6 | -4.3 | -0.12 [-0.99 ; +0.96] | +40.0 % | -12.80 | 85.3 | -20.0 | +27.2 | +31.6 | 10 | 12 / 19 | 130 % |
| HOLD — tout | +335.8 | +0.0 | +0.00 [+0.00 ; +0.00] | +28.2 % | -17.79 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| SELL m=0.1 f=0.25 — tout | +334.7 | -1.2 | -0.02 [-0.74 ; +0.83] | +28.1 % | -12.80 | 127.4 | -20.0 | +64.4 | +65.5 | 18 | 24 / 36 | 112 % |

## 4. ÉCHELLE — réglage choisi sur l'apprentissage : **ÉCHELLE m=0.1 f=0.2** (parmi 6)

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOLD — test | +71.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +13.2 % | -17.73 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 476 % |
| ÉCHELLE m=0.1 f=0.2 — test | +73.6 | +1.8 | +0.05 [-3.56 ; +4.13] | +13.6 % | -4.93 | 102.3 | -20.0 | +119.0 | +117.2 | 11 | 722 / 786 | 357 % |
| HOLD — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| ÉCHELLE m=0.1 f=0.2 — apprentissage | +119.4 | -144.5 | -4.02 [-6.21 ; -2.03] | +18.4 % | -1.41 | 101.7 | -20.0 | +67.7 | +212.2 | 16 | 937 / 991 | 212 % |
| HOLD — tout | +335.8 | +0.0 | +0.00 [+0.00 ; +0.00] | +28.2 % | -17.79 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| ÉCHELLE m=0.1 f=0.2 — tout | +193.0 | -142.8 | -2.04 [-4.13 ; +0.17] | +16.2 % | -3.65 | 102.3 | -20.0 | +186.7 | +329.5 | 27 | 1659 / 1777 | 160 % |

## 4. BUDGET — réglage choisi sur l'apprentissage : **BUDGET d=0.2 L=0.5** (parmi 4)

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOLD — test | +71.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +13.2 % | -17.73 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 476 % |
| BUDGET d=0.2 L=0.5 — test | +92.0 | +20.1 | +0.59 [+0.00 ; +1.23] | +17.0 % | -12.07 | 134.9 | -20.0 | +20.1 | +0.0 | 0 | 2 / 2 | 372 % |
| HOLD — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| BUDGET d=0.2 L=0.5 — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| HOLD — tout | +335.8 | +0.0 | +0.00 [+0.00 ; +0.00] | +28.2 % | -17.79 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| BUDGET d=0.2 L=0.5 — tout | +356.0 | +20.1 | +0.29 [+0.00 ; +0.60] | +29.9 % | -14.80 | 134.9 | -20.0 | +20.1 | +0.0 | 0 | 2 / 2 | 111 % |

## 4. REBOND — réglage choisi sur l'apprentissage : **REBOND d=0.2 x=0.05 f=0.5** (parmi 12)

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOLD — test | +71.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +13.2 % | -17.73 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 476 % |
| REBOND d=0.2 x=0.05 f=0.5 — test | +75.9 | +4.0 | +0.12 [+0.00 ; +0.33] | +14.0 % | -15.74 | 146.3 | -20.0 | +4.0 | +0.0 | 0 | 1 / 1 | 451 % |
| HOLD — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| REBOND d=0.2 x=0.05 f=0.5 — apprentissage | +263.9 | +0.0 | +0.00 [+0.00 ; +0.00] | +40.7 % | -17.79 | 82.9 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 130 % |
| HOLD — tout | +335.8 | +0.0 | +0.00 [+0.00 ; +0.00] | +28.2 % | -17.79 | 150.3 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| REBOND d=0.2 x=0.05 f=0.5 — tout | +339.8 | +4.0 | +0.06 [+0.00 ; +0.17] | +28.5 % | -15.79 | 146.3 | -20.0 | +4.0 | +0.0 | 0 | 1 / 1 | 116 % |

## 5. Référence : stop naïf (pour mesurer le coût des faux sauvetages)

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| STOP naïf −0.1 | +45.2 | -290.6 | -4.15 [-9.26 ; +0.40] | +3.8 % | -8.04 | 177.0 | -20.0 | +287.9 | +578.5 | 11 | 45 / 54 | 739 % |
| STOP naïf −0.2 | +291.1 | -44.7 | -0.64 [-3.16 ; +1.45] | +24.4 % | -14.16 | 116.2 | -20.0 | +111.6 | +156.3 | 3 | 37 / 40 | 136 % |

## 6. Sensibilité à la latence et aux frais (réglages choisis sur l'apprentissage, toutes positions)

| Politique | 164 ms : vs HOLD ($) | 264 ms | 500 ms |
|---|---|---|---|
| SELL m=0.1 f=0.25 | -1.2 | +3.1 | -19.7 |
| ÉCHELLE m=0.1 f=0.2 | -142.8 | -136.2 | -138.4 |
| BUDGET d=0.2 L=0.5 | +20.1 | +0.0 | +0.0 |
| REBOND d=0.2 x=0.05 f=0.5 | +4.0 | +4.0 | +3.7 |

## 7. Sous-ensemble H816 (prix 0,20–0,50) — mêmes réglages

| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOLD — H816 | +290.2 | +0.0 | +0.00 [+0.00 ; +0.00] | +29.4 % | -15.53 | 131.4 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| SELL m=0.1 f=0.25 — H816 | +268.9 | -21.3 | -0.37 [-0.96 ; +0.29] | +27.3 % | -13.40 | 107.5 | -20.0 | +25.0 | +46.2 | 15 | 17 / 28 | 122 % |
| ÉCHELLE m=0.1 f=0.2 — H816 | +114.0 | -176.1 | -3.04 [-5.42 ; -0.42] | +11.6 % | -11.77 | 100.2 | -20.0 | +91.5 | +267.6 | 24 | 1317 / 1413 | 236 % |
| BUDGET d=0.2 L=0.5 — H816 | +290.2 | +0.0 | +0.00 [+0.00 ; +0.00] | +29.4 % | -15.53 | 131.4 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |
| REBOND d=0.2 x=0.05 f=0.5 — H816 | +290.2 | +0.0 | +0.00 [+0.00 ; +0.00] | +29.4 % | -15.53 | 131.4 | -20.0 | +0.0 | +0.0 | 0 | 0 / 0 | 118 % |

## 8. H817-G — Contrôle avant exécution (envoi différé ; un ordre preneur en retard ne peut pas être annulé)

Avant d'envoyer, on attend δ ms, on recalcule P_win et le meilleur vendeur, et on n'envoie que si P_win − vendeur − frais ≥ 0,10 ; exécution à δ + 164 ms.

| Envoi | Positions exécutées | P&L ($) | vs immédiat ($) | IC 90 % par position |
|---|---|---|---|---|
| immédiat | 70 | +335.8 | +0.0 | [+0.00 ; +0.00] |
| différé 50 ms | 58 | +322.2 | -13.6 | [-1.45 ; +1.06] |
| différé 100 ms | 54 | +291.5 | -44.3 | [-2.18 ; +0.99] |
| différé 150 ms | 52 | +350.5 | +14.7 | [-1.33 ; +1.85] |

## 9. Recommandation par module
- Voir les tableaux : un module n'est conservé que si son amélioration vs HOLD est positive sur le TEST avec un IC par cycles > 0.

## Limites
- Une journée, ~50 cycles, ~100 positions : faible puissance.
- Profondeur au-delà de ±3 c approximative.
- P_win recalculé hors ligne.
