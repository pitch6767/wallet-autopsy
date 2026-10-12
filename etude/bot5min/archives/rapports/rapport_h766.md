# Bot95 — H766 à H775 : capturer l'avantage malgré la latence — rapport préliminaire du 11.10.2026

Hors ligne uniquement. Aucun ordre réel, aucun fantôme modifié, aucun déploiement. La période réservée (≥ 13.10) n'a pas été lue.

**Données :** 157 signaux réglés sur 31 cycles enregistrés à Dublin, soit **45 décisions uniques** (une par cycle et par côté). Les intervalles de confiance rééchantillonnent des cycles. Validation chronologique : 1re moitié avant 10:55 UTC, 2e moitié après.

**Exécution preneur :** décision + 14 ms de trajet + 150 ms de retard Polymarket, soit **164 ms**. Frais compris, budget de 50 $ par signal, comme à Dublin. **Tout est PRÉLIMINAIRE.**

## Réponse courte

L'avantage **survit à la latence** sur cet échantillon : à 164 ms on garde environ 83 % du P&L théorique à 0 ms (+4 670 $ contre +5 635 $). L'espérance reste positive jusqu'à 500 ms, et la latence critique n'est pas atteinte dans la plage testée.

**Mais ce résultat est fragile :**
- la médiane par signal est de **0 $** ;
- **52 % du P&L vient des 5 meilleurs signaux** ;
- sans les 10 meilleurs, il reste +963 $ ;
- en décisions uniques (45) : +983 $, soit +21,8 $ par décision, IC 90 % [+3,9 ; +39,6].

Tout dépend donc des billets bon marché qui gagnent. Le rapport H724 trouvait ≈ 0 par part, parce qu'il misait **1 part** par signal. Ici on mise **50 $** par signal, comme Dublin, ce qui donne beaucoup plus de parts aux billets bon marché.

## H766 / H768 — Courbe P&L / latence (preneur, plafond +0)

| Délai | Signaux exécutables | P&L total | par signal (IC 90 %) | 1re / 2e moitié |
|---|---|---|---|---|
| 0 ms (mesure Dublin) | 157 | +5 635 $ | +35,9 [+15 ; +60] | +14 / +57 |
| 50 ms | 143 | +5 655 $ | +36,0 [+12 ; +62] | +14 / +58 |
| 100 ms | 135 | +4 928 $ | +31,4 [+9 ; +57] | +8 / +54 |
| **164 ms** | **128** | **+4 670 $** | **+29,7 [+6 ; +57]** | +9 / +49 |
| 250 ms | 107 | +4 127 $ | +26,3 [+5 ; +49] | +9 / +43 |
| 500 ms | 96 | +3 039 $ | +19,4 [+3 ; +37] | +8 / +30 |

- Latence critique, espérance ≤ 0 : **pas atteinte jusqu'à 500 ms**.
- La perte due à la latence se concentre sur les billets à 0,10–0,20 : −780 $ entre 0 et 164 ms.
- Sur 0,20–0,35, la quantité réapparaît après la décision : pas de perte.

## H767 — Pourquoi les offres disparaissent

Mesure sur 250 ms, sans attribution inventée.

| Cause | Signaux | Taux de gain |
|---|---|---|
| pas disparue | 93 | 33 % |
| **retirée par le vendeur (annulation)** | **46** | **63 %** |
| consommée par un autre preneur | 4 | 50 % |
| indéterminée (carnet rechargé) | 14 | 50 % |

**Fait majeur :** on ne perd pas une course contre d'autres preneurs, ce qui arrive seulement 4 fois. Les **makers retirent leurs offres** sur les meilleurs signaux (63 % de gains contre 33 %). Ils voient la même information et annulent plus vite que nos 164 ms. Or les 150 ms de retard de Polymarket sont imposés à tous les preneurs : ce n'est pas un problème de serveur.

## H769 — Prix plafond, à 164 ms

| Plafond | P&L | Gain marginal |
|---|---|---|
| +0 c | +4 670 $ | — |
| +1 c | +4 779 $ | +109 $ |
| +2 c | +5 313 $ | +643 $ |
| +3 c | +5 801 $ | +1 131 $ |

Les intervalles de confiance se recouvrent largement : le gain du plafond n'est pas démontré.

## H774 — Sans poursuite

On n'achète que si modèle − prix − frais ≥ 0,05, avec le modèle figé au signal.

| Politique | P&L | par signal |
|---|---|---|
| abandon immédiat | +4 670 $ | +29,7 |
| deuxième chance (500 ms, +2 c) | +4 890 $ | +31,2 |
| attente : relances 5 s au prix du signal | +5 634 $ | +35,9 |
| **attente : relances 5 s, plafond +2 c** | **+6 013 $** | **+38,3** |

**Limite :** le modèle est figé au signal. En direct, il faudrait le recalculer à chaque relance. C'est le meilleur candidat, mais il doit être testé en fantôme.

## H770 — Maker contre preneur, mêmes signaux

| Voie | P&L | par signal |
|---|---|---|
| **preneur 164 ms (Bot95 actuel)** | **+4 670 $** | **+29,7** |
| maker 10 s, file prudente / centrale | +2 531 / +2 544 $ | +16,1 / +16,2 |
| maker 60 s, file prudente / centrale | +3 201 / +3 293 $ | +20,4 / +21,0 |
| maker 60 s, file optimiste | +5 268 $ | +33,6 |

Fantôme vivant M1 sur les mêmes 78 signaux : **+2 716 $**, contre +3 970 $ pour le preneur. **Le preneur reste meilleur**, sauf si l'on suppose une file d'attente optimiste.

## Comparaison contre Bot95 actuel, M4 et M8

Sur les 16 mêmes cycles :

| Moteur | P&L prudent |
|---|---|
| Bot95 preneur 164 ms | **+3 950 $** |
| M4 | +190 $ |
| M8 | +453 $ |

## H771–H773 — Offres d'achat prépositionnées

Règle sans regard vers le futur : on garde une offre au meilleur acheteur tant que modèle − prix ≥ 0,10. L'inventaire est plafonné et les fills non désirés sont gardés jusqu'au règlement.

- Total : +220 à +265 $. IC [−7 ; +24] par cycle.
- Les fills sans signal perdent : −43 à −131 $.
- **La priorité ne paie pas.** Sur les 23 signaux couverts, l'offre prépositionnée rapporte +328 $, contre +981 $ pour une offre posée au signal. Le prix de l'offre prépositionnée est souvent dépassé quand le signal arrive.

## H775 — Décision anticipée

On recalcule le modèle de Dublin hors ligne. Il colle à 74 % des signaux à 0,005 près ; il est moins fiable pour les signaux déclenchés par Bybit/OKX.

Ajouter Binance au prix fait décider plus tôt dans seulement 2 % des cas, dont **3 décisions sur 154 au moins 164 ms plus tôt**. Sur les mêmes opportunités : −0,36 $ par signal, IC [−1,26 ; +0,20].

| Signaux | Nombre | Gagnants | Perdants | P&L |
|---|---|---|---|---|
| supplémentaires | 6 | 3 | 3 | 0 $ |
| perdus | 1 | 0 | 1 | −33 $ |

**Pas d'anticipation exploitable.**

## Recommandation (à toi de décider, rien n'est lancé)

1. **Garder le preneur.** Ni le maker ni le prépositionnement ne font mieux.
2. Un seul candidat fantôme : **« relances 5 s, plafond +2 c »**.
   - Mêmes signaux que Bot95.
   - Toutes les 500 ms pendant 5 s : achat au plus au prix du signal + 2 c.
   - Seulement si modèle **recalculé** − prix − frais ≥ 0,05.
   - Mesure pure en fantôme. À valider sur la période réservée du 15.10 avant toute décision.
3. Abandonner l'anticipation par Binance et les offres prépositionnées.

Détail : etude/bot5min/resultat_latence_h766.md. Je relance automatiquement à 18:45 UTC avec les nouveaux cycles de Dublin.
