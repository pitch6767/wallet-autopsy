# Bot95 — H559–H564 : makers (diagnostic PRÉLIMINAIRE, non validé statistiquement)

Généré le 11.10.2026 12:48 UTC. 46 cycles avant la période réservée. Remplissages SIMULÉS selon trois bornes de file d'attente (prudente, centrale, optimiste) : aucun n'est une exécution garantie.

## 1. Décomposition de M4 (retrait sur flux toxique)

M4a, M4b, M4c gardent UNE seule des trois conditions de M4 (a : bourses −10 $ en 300 ms ; b : flux agressif net ≥ 250 000 $ contre nous en 250 ms ; c : ≥ 100 parts vendues sur nos acheteurs en 500 ms). Même prix que M2 marge 5 c ; seule la règle de retrait change.

### Comparaison directe (fantômes en parallèle sur les mêmes cycles)

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M0 temoin aleatoire | 8 | 5 / 5 / 0 | 498 | 199 $ | +114 $ [-97 ; +324] | +114 $ | +0 $ | +0.57 | -50 $ | +0.2 / -4.1 / -6.5 / +11.1 | 0 |
| M2 cotation marge 5 c | 808 | 19 / 19 / 0 | 3174 | 1195 $ | +120 $ [-224 ; +440] | +111 $ | +0 $ | +0.10 | -142 $ | -4.9 / -9.2 / -10.1 / -10.7 | 0 |
| M4 retrait toxique | 856 | 64 / 62 / 0 | 2805 | 602 $ | +206 $ [-77 ; +489] | +376 $ | +0 $ | +0.34 | -43 $ | -1.2 / -1.5 / -1.2 / -1.6 | 0 |
| M4a seul bourses -10 $ | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |
| M4b seul flux agressif | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |
| M4c seul ventes Polymarket | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |

## 2. Durée de vie des cotations (M6)

M2 marge 5 c dont chaque offre est annulée après L ms ; la suivante n'est posée qu'après confirmation de l'annulation (aller-retour mesuré). Les parts remplies pendant le trajet de l'annulation sont comptées (dernière colonne).

### Durées de vie

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 5 c | 808 | 19 / 19 / 0 | 3174 | 1195 $ | +120 $ [-224 ; +440] | +111 $ | +0 $ | +0.10 | -142 $ | -4.9 / -9.2 / -10.1 / -10.7 | 0 |
| M6 duree de vie 100 ms | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |
| M6 duree de vie 250 ms | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |
| M6 duree de vie 500 ms | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |
| M6 duree de vie 1000 ms | — | 0 / 0 / 0 | 0 | 0 $ | +0 $ [—] | +0 $ | +0 $ | +nan | +0 $ | — / — / — / — | 0 |

## 3. Début de cycle (180–300 s restantes) contre le reste

| Variante | Temps restant à la pose | Offres remplies | $ exécutés | Résultat prudent [IC 90 %] | par $ |
|---|---|---|---|---|---|
| M2 cotation marge 5 c | 180–300 s | 8 | 243 $ | +335 $ [+172 ; +499] | +1.38 |
| M2 cotation marge 5 c | 60–180 s | 3 | 150 $ | -150 $ [—] | -1.00 |
| M2 cotation marge 5 c | 0–60 s | 0 | 0 $ | +0 $ [—] | +nan |
| M4 retrait toxique | 180–300 s | 39 | 316 $ | +493 $ [+150 ; +835] | +1.56 |
| M4 retrait toxique | 60–180 s | 30 | 286 $ | -286 $ [-501 ; -71] | -1.00 |
| M4 retrait toxique | 0–60 s | 0 | 0 $ | +0 $ [—] | +nan |
| M5 remplissage attendu | 180–300 s | 18 | 221 $ | +289 $ [+145 ; +434] | +1.31 |
| M5 remplissage attendu | 60–180 s | 7 | 207 $ | -207 $ [—] | -1.00 |
| M5 remplissage attendu | 0–60 s | 0 | 0 $ | +0 $ [—] | +nan |
| M0 temoin aleatoire | 180–300 s | 1 | 50 $ | +158 $ [—] | +3.17 |
| M0 temoin aleatoire | 60–180 s | 2 | 99 $ | +5 $ [—] | +0.05 |
| M0 temoin aleatoire | 0–60 s | 2 | 50 $ | -50 $ [—] | -1.00 |

Aucune conclusion à ce stade (trop peu de remplissages).

## 4. File d'attente : trois bornes

Prudente : seules les transactions nous font avancer. Centrale : un retrait sans transaction libère la file au prorata de notre place. Optimiste : tout retrait sans transaction vient de devant nous. Les trois colonnes de résultat des tableaux ci-dessus correspondent à ces bornes.

### Autres variantes permanentes

| Variante | Offres posées | Remplies (prudent / central / optimiste) | Parts remplies prudent | $ exécutés prudent | Résultat prudent [IC 90 %] | Central | Optimiste | par $ (prudent) | Creux max (prudent) | Sélection adverse +1 / +3 / +5 / +10 s (c/part, prudent) | Parts remplies pendant l'annulation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M2 cotation marge 10 c | 829 | 23 / 23 / 0 | 3031 | 1036 $ | +117 $ [-182 ; +413] | +151 $ | +0 $ | +0.11 | -112 $ | -3.2 / -7.9 / -8.2 / -8.0 | 0 |
| M3 anticipation Chainlink | 357 | 14 / 13 / 0 | 980 | 242 $ | +22 $ [-150 ; +193] | -15 $ | +0 $ | +0.09 | -96 $ | +5.8 / +1.1 / -1.7 / +18.4 | 0 |
| M5 remplissage attendu | 184 | 42 / 32 / 0 | 1305 | 428 $ | +82 $ [-9 ; +173] | +86 $ | +0 $ | +0.19 | -7 $ | -1.3 / -4.8 / -4.0 / -4.8 | 0 |

## 5. Hybride maker / preneur (M8) contre M1 sur les mêmes signaux

- M1 (toujours maker) : 60 positions (0 preneur, 60 maker), résultat prudent +615 $ [IC 90 % -896 ; +2191], creux -787 $
- M8 hybride : 0 positions (0 preneur, 0 maker), résultat prudent +0 $ , creux +0 $

Le tournoi FAST / SLOW / HYBRID (preneur) sur les mêmes signaux est dans resultat_fast_fenetre.md, section 6.

## 6. Retard preneur
Le retard de 150 ms vient de la documentation Polymarket (changelog du 04.09.2026) et du drapeau itode=true de nos marchés ; il n'est PAS mesuré sur notre infrastructure. M8 et FAST l'utilisent comme hypothèse. Seul un ordre réel (test de 1 $, en attente de l'accord de Pitch) peut le mesurer.

## 7. Validation
Période réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais utilisée pour régler une règle. Verdict avec --hors-echantillon après plusieurs jours.
