# Bot95 — verdict hors échantillon (makers, FAST / SLOW / HYBRID, moteur C)

Rapport pour Pitch, 15.10.2026. Aucun ordre réel. Règles figées le 11.10.2026, période réservée = cycles à partir du 13.10.2026 00:00 UTC, jamais utilisée pour régler quoi que ce soit. Scripts lancés une seule fois avec --hors-echantillon : fast_fenetre.py et maker_h559.py, sans changer aucun seuil.

> En bref : **aucune variante ne montre un gain démontré** hors échantillon. Tous les intervalles de confiance à 90 % contiennent 0. Les makers passifs ne font pas mieux que le témoin aléatoire M0 (M5 fait même nettement pire). M8 hybride, FAST et C restent positifs mais non démontrés. Décision proposée : arrêter la piste « maker passif », continuer à observer M8, C et FAST sans argent. C'est toi qui décides.

## 1. Données utilisées

- Cycles enregistrés à Dublin : 744 cycles du 13.10 00:00 au 15.10 16:50 UTC (2,7 jours ; 778 attendus, 34 manquants).
- Signaux réglés (FAST, SLOW, HYBRID, C) : jusqu'au cycle du 15.10 14:55 UTC, 496 cycles avec signaux.
- **Makers (M0 à M10) : offres réglées seulement jusqu'au cycle du 14.10 07:50 UTC (346 cycles, environ 32 h)**. Depuis, la sauvegarde du fichier des makers échoue : le bot répond « erreur 500 » à cette demande. Le volet maker couvre donc un peu plus d'un jour, pas 2,7 jours.
- Lecture des tableaux : « résultat » = gain ou perte net en $ (frais compris), remplissages simulés en hypothèse prudente. IC 90 % = intervalle de confiance à 90 % obtenu en tirant au hasard des cycles entiers (2 000 tirages). « Creux » = pire baisse cumulée. « Sélection adverse » = où est le prix 1, 3, 5 et 10 s après notre achat, en centimes par part (négatif = le marché part contre nous).

## 2. Makers : comparaison au témoin M0 (13.10 00:00 → 14.10 07:50)

| Variante | Remplissages | Parts | $ engagés | Résultat | IC 90 % | Creux | Sélection adverse +1/+3/+5/+10 s (c) | Écart à M0 [IC 90 %] | Avant le 13.10 |
|---|---|---|---|---|---|---|---|---|---|
| M0 témoin aléatoire | 440 | 87 402 | 21 629 $ | +2 595 $ | [−772 ; +6 394] | −1 691 $ | −1,6 / −1,6 / −1,8 / −1,6 | — | −4 028 $ |
| M1 offre au signal | 530 | 215 675 | 25 740 $ | −1 673 $ | [−8 134 ; +5 540] | −5 380 $ | −0,9 / −1,3 / −0,8 / −0,1 | −4 268 [−10 914 ; +3 074] | +373 $ |
| M2 marge 5 c | 1 921 | 157 647 | 50 874 $ | +1 035 $ | [−5 196 ; +7 747] | −5 343 $ | −1,3 / −1,3 / −1,1 / −0,9 | −1 560 [−8 428 ; +5 629] | +340 $ |
| M2 marge 10 c | 1 695 | 166 868 | 39 990 $ | +273 $ | [−5 864 ; +7 279] | −5 139 $ | −0,8 / −0,6 / −0,2 / −0,3 | −2 322 [−8 840 ; +5 469] | +612 $ |
| M4 retrait toxique | 2 279 | 168 460 | 48 036 $ | +1 163 $ | [−3 588 ; +6 268] | −2 429 $ | −0,5 / −0,3 / −0,1 / −0,1 | −1 432 [−6 767 ; +4 463] | +930 $ |
| M5 remplissage attendu | 3 675 | 230 577 | 71 055 $ | −4 564 $ | [−10 602 ; +2 157] | −8 169 $ | −1,0 / −1,0 / −1,1 / −1,4 | **−7 159 [−14 088 ; −145]** | +1 138 $ |
| M8 hybride maker/preneur | 547 (184 preneur, 363 maker) | 163 664 | 22 884 $ | +5 951 $ | [−724 ; +13 004] | −2 146 $ | +0,2 / −0,0 / +0,3 / +1,1 | +3 355 [−3 448 ; +10 780] | −1 266 $ |
| M8b routeur corrigé | 538 (153 preneur, 385 maker) | 165 303 | 22 676 $ | +5 189 $ | [−1 496 ; +12 459] | −2 223 $ | −0,0 / −0,2 / +0,1 / +0,9 | +2 594 [−4 088 ; +9 905] | −1 517 $ |
| M3 anticipation Chainlink | 1 490 | 136 447 | 34 302 $ | +1 850 $ | [−2 228 ; +6 670] | −2 394 $ | +1,6 / +1,2 / +1,3 / +1,4 | −745 [−4 889 ; +3 520] | +1 039 $ |
| M10 double maker | 2 764 | 128 587 | 52 976 $ | −1 344 $ | [−4 746 ; +2 073] | −2 541 $ | −1,0 / −1,0 / −0,9 / −1,2 | −3 939 [−8 746 ; +398] | −207 $ |

Ce qu'on retient :

- **Aucun maker ne bat le hasard.** Le témoin M0 (offres posées au hasard) gagne +2 595 $ sur la période, alors qu'il perdait −4 028 $ avant : cela montre à quel point un jour et demi de résultats est dominé par la chance. Aucune variante ne fait mieux que M0 de façon démontrée.
- **M5 fait pire que M0** (écart −7 159 $, IC entièrement sous 0). Avec dix comparaisons, ce résultat limite peut en partie venir du hasard, mais il va dans le même sens que sa perte propre.
- **La sélection adverse reste négative** pour presque tous les makers (le prix repart contre nous juste après le remplissage), sauf M3 et, légèrement, M8.
- Les petits gains d'avant le 13.10 (M2, M4, M5) ne se confirment pas.
- M6 (durées de vie 100 à 1 000 ms) : entre −1 012 $ et +282 $, tous les IC contiennent 0. M4a/M4b/M4c : +2 245 $, −1 528 $, −1 104 $, tous non démontrés.

## 3. Preneur : FAST / SLOW / HYBRID et moteur C (13.10 → 15.10 ~15 h)

| Stratégie | Trades (remplissages) | Parts | $ engagés | Résultat | IC 90 % | par $ | Creux | Avant le 13.10 |
|---|---|---|---|---|---|---|---|---|
| FAST (exécution 164 ms après le signal) | 1 440 | 356 200 | 54 153 $ | +4 525 $ | [−4 780 ; +13 507] | +0,08 | −3 173 $ | +3 470 $ (+0,16 par $) |
| SLOW (exécution 1,164 s après) | 910 | 309 169 | 39 479 $ | −2 737 $ | [−9 992 ; +5 079] | −0,07 | −8 290 $ | +620 $ |
| HYBRID (FAST sinon SLOW) | 1 471 | 365 814 | 55 565 $ | +4 525 $ | [−4 535 ; +14 224] | +0,08 | −3 640 $ | +3 684 $ |
| C moteur alpha (exécution à 300 ms) | 132 | — | 6 056 $ | +734 $ | [−501 ; +1 953] | +0,12 | −627 $ | +765 $ [−125 ; +1 813] |

- FAST et HYBRID restent positifs, mais le gain par dollar est divisé par deux par rapport à avant le 13.10 et l'intervalle contient largement 0 : **non démontré**.
- SLOW perd : attendre une seconde de plus coûte cher, ce qui confirme que l'avantage, s'il existe, est très court.
- Le moteur C est stable (+765 $ avant, +734 $ après) mais petit (132 trades) et son intervalle contient 0 : **non démontré**.
- La sélection adverse n'est pas mesurée pour les ordres preneur. Le témoin M0 étant un maker, la comparaison directe n'a pas de sens ici ; pour repère, M0 fait +0,12 $ par $ engagé sur sa période.
- Tout repose sur un retard preneur de 150 ms supposé (documentation Polymarket), **jamais mesuré par un vrai ordre**. Le diagnostic de fenêtre (section 4 de fast_fenetre) montre qu'avec ce retard, une offre n'est presque jamais encore là si on décide moins de 164 ms avant sa disparition, et que 44 % des achats arrivent moins de 150 ms après notre information.

## 4. Décision proposée (tu décides)

1. **Arrêter la piste « maker passif »** (M1, M2, M3, M4 et ses variantes, M5, M6, M10) comme source de gain : rien ne fait mieux que des offres posées au hasard, le prix repart contre nous après les remplissages, et M5 fait pire que le hasard.
2. **Continuer à observer, sans argent, M8 / M8b, FAST / HYBRID et le moteur C** : résultats positifs mais non démontrés. Pas de nouveau fantôme, ceux qui tournent déjà suffisent.
3. **Avant toute suite sur M8, il faut réparer la sauvegarde des makers** (erreur 500 depuis le 14.10 08:00 UTC), sinon les fantômes tournent sans que l'on puisse lire leurs résultats.
4. **Aucun passage en réel.** La seule mesure qui peut trancher pour FAST est le vrai retard preneur, qui demande un ordre réel de test (1 $) : c'est à toi de décider si tu l'autorises.

## 5. Limites

- Volet maker : environ 32 h seulement (sauvegarde en panne), contre 2,7 jours pour FAST / C.
- Remplissages simulés (file d'attente reconstituée à partir du carnet), pas des exécutions réelles.
- Beaucoup de variantes testées en même temps : quelques sous-cohortes isolées ont un IC au-dessus de 0 (par exemple M8 « V2-F incertitude 0,01 % » +1 757 $ [+322 ; +3 520], M9 +106 $), ce qui est attendu par hasard sur près de 40 lignes. Ce n'est pas une preuve.
- Défaut repéré dans maker_h559.py et fast_fenetre.py : le groupe « M1 » y inclut aussi M10 et M11, et « M4 » (section 6 de fast_fenetre) inclut M4a/M4b/M4c. Les tableaux ci-dessus utilisent les groupes exacts (script verdict_hors_echantillon_bot95.py, lecture seule). Les lignes maker de la section 6 de fast_fenetre ne portent que sur les cycles avec signal, où tous les makers gagnent (et perdent ailleurs) : ne pas les utiliser pour juger les makers.
- Seule réparation technique faite : le fichier des makers, stocké compressé, a été décompressé à l'endroit attendu par les scripts ; le rapport de fast_fenetre (qui écrase sinon celui d'avant le 13.10) a été enregistré sous un nom séparé. Aucune règle, aucun seuil, aucune période modifiés.

Fichiers : resultat_maker_h559_hors_echantillon.md, resultat_fast_fenetre_hors_echantillon.md, resultat_verdict_hors_echantillon_bot95.md (dossier etude/bot5min).
