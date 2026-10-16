# Bot95 — verdict hors échantillon COMPLET (makers, FAST / SLOW / HYBRID, moteur C)

Rapport pour Pitch, 16.10.2026. Aucun ordre réel. Même verdict que celui du 15.10 (rapport_verdict_hors_echantillon_bot95.md, gardé tel quel), refait sur **toute** la période réservée maintenant que la sauvegarde des makers est réparée. Règles figées le 11.10.2026, période réservée = cycles à partir du 13.10.2026 00:00 UTC. Mêmes scripts, mêmes seuils, mêmes groupes, aucun réglage.

> En bref : **une seule ligne passe la règle figée : M8 hybride maker/preneur**, +10 647 $ simulés, IC 90 % [+738 ; +20 788], et +10 652 $ de mieux que le témoin aléatoire M0 [+929 ; +20 995]. C'est un « gain démontré » au sens de la règle, mais **fragile** : il est juste au-dessus de 0, M8 perdait avant le 13.10 (−1 266 $), on a testé une quinzaine de lignes en même temps, les remplissages sont simulés et la partie preneur repose sur un retard de 150 ms jamais mesuré. Tout le reste est **non démontré** (IC 90 % contenant 0) : M8b, FAST, HYBRID, SLOW, moteur C et tous les makers passifs. Aucun maker passif ne fait mieux que M0. Décision proposée : arrêter les makers passifs, garder M8 en observation sans argent avec une nouvelle période de confirmation fixée à l'avance, continuer d'observer FAST / HYBRID / C. C'est toi qui décides.

## 1. Données utilisées

- Cycles enregistrés à Dublin : **916 cycles du 13.10 00:00 au 16.10 07:35 UTC** (3,3 jours ; 956 attendus, 40 manquants).
- **Makers (M0 à M10) : 143 628 offres réglées, 877 cycles du 13.10 00:00 au 16.10 07:35 UTC** — toute la période réservée (la version du 15.10 s'arrêtait au 14.10 07:50, soit environ 32 h).
- Signaux réglés (FAST, SLOW, HYBRID) : 646 cycles communs avec signaux réglés (496 dans la version du 15.10). Moteur C : 227 signaux réglés, 177 trades.
- Lecture des tableaux : « résultat » = gain ou perte net en $ (frais compris), remplissages simulés en hypothèse prudente. IC 90 % = intervalle de confiance à 90 % obtenu en tirant au hasard des cycles entiers (2 000 tirages). « Creux » = pire baisse cumulée. « Sélection adverse » = où est le prix 1, 3, 5 et 10 s après notre achat, en centimes par part (négatif = le marché part contre nous). « Écart à M0 » = différence cycle par cycle avec le témoin aléatoire.

## 2. Makers : comparaison au témoin M0 (13.10 00:00 → 16.10 07:35)

| Variante | Remplissages | Parts | $ engagés | Résultat | IC 90 % | Creux | Sélection adverse +1/+3/+5/+10 s (c) | Écart à M0 [IC 90 %] | Avant le 13.10 |
|---|---|---|---|---|---|---|---|---|---|
| M0 témoin aléatoire | 1 068 | 208 647 | 52 364 $ | −5 $ | [−4 153 ; +4 405] | −3 300 $ | −1,7 / −1,7 / −1,7 / −1,6 | — | −4 028 $ |
| M1 offre au signal | 1 284 | 524 714 | 62 493 $ | −680 $ | [−11 237 ; +9 501] | −5 380 $ | −1,0 / −1,1 / −0,9 / +0,1 | −675 [−11 144 ; +10 054] | +373 $ |
| M2 marge 5 c | 5 545 | 453 917 | 150 732 $ | +2 012 $ | [−7 471 ; +12 199] | −6 224 $ | −1,2 / −1,1 / −1,0 / −0,7 | +2 017 [−8 100 ; +12 368] | +340 $ |
| M2 marge 10 c | 4 592 | 501 104 | 121 805 $ | −1 463 $ | [−11 466 ; +9 102] | −5 139 $ | −1,0 / −0,8 / −0,7 / −0,7 | −1 458 [−11 804 ; +9 332] | +612 $ |
| M4 retrait toxique | 6 251 | 478 873 | 141 121 $ | +1 303 $ | [−6 804 ; +9 383] | −5 897 $ | −0,8 / −0,8 / −0,7 / −0,5 | +1 308 [−7 669 ; +10 189] | +930 $ |
| M5 remplissage attendu | 11 179 | 714 420 | 224 510 $ | −1 136 $ | [−14 023 ; +13 358] | −8 962 $ | −1,0 / −1,1 / −1,1 / −1,2 | −1 131 [−14 753 ; +13 275] | +1 138 $ |
| **M8 hybride maker/preneur** | 1 303 (421 preneur, 882 maker) | 398 243 | 55 384 $ | **+10 647 $** | **[+738 ; +20 788]** | −2 186 $ | −0,3 / −0,2 / −0,1 / +1,0 | **+10 652 [+929 ; +20 995]** | −1 266 $ |
| M8b routeur corrigé | 1 280 (352 preneur, 928 maker) | 402 457 | 54 950 $ | +9 010 $ | [−820 ; +19 294] | −2 594 $ | −0,4 / −0,4 / −0,3 / +1,0 | +9 015 [−945 ; +19 456] | −1 517 $ |
| M3 anticipation Chainlink | 4 484 | 404 575 | 107 959 $ | +2 656 $ | [−4 862 ; +10 169] | −3 076 $ | +0,6 / +0,6 / +0,7 / +1,0 | +2 661 [−4 828 ; +9 708] | +1 039 $ |
| M10 double maker | 8 503 | 393 925 | 164 139 $ | −4 589 $ | [−11 569 ; +2 928] | −7 689 $ | −1,1 / −1,1 / −1,1 / −1,1 | −4 584 [−12 316 ; +3 699] | −207 $ |

Ce qu'on retient :

- **Aucun maker passif ne bat le hasard.** Le témoin M0 revient à zéro (−5 $) ; M1, M2, M3, M4, M5, M10 sont tous dans le bruit, et leur écart à M0 aussi. La sélection adverse reste négative pour tous les makers passifs sauf M3.
- **M8 est la seule ligne dont l'IC 90 % est entièrement au-dessus de 0.** Il est positif chaque jour (13.10 : +2 797 $, 14.10 : +2 219 $, 15.10 : +3 177 $, 16.10 jusqu'à 07:35 : +2 454 $). Le gain vient des deux modes : partie maker +7 372 $ [−1 183 ; +16 092], partie preneur +3 275 $ [−795 ; +7 483], chacune non démontrée seule. Les 5 meilleurs cycles font 6 518 $ sur 626 cycles.
- **Pourquoi rester prudent sur M8** : (1) avant le 13.10, M8 perdait −1 266 $ ; (2) une quinzaine de lignes ont été jugées en même temps (10 makers, M8 et M8b qui se ressemblent, FAST, SLOW, HYBRID, C) : à 90 %, il est attendu qu'une ligne passe par hasard ; avec un intervalle à 99 % (correction simple pour ce nombre de tests, donnée seulement pour information), M8 donne [−3 716 ; +26 004] et contient 0 ; (3) remplissages simulés ; (4) la partie preneur suppose 150 ms de retard, non mesuré ; (5) M8b, sa version « corrigée », reste juste sous le seuil.
- M6 (durées de vie 100 à 1 000 ms) : entre −2 708 $ et +5 255 $, tous les IC contiennent 0. M4a / M4b / M4c : +1 223 $, +1 876 $, +584 $, tous non démontrés.

## 3. Preneur : FAST / SLOW / HYBRID et moteur C (13.10 → 16.10 ~07 h)

| Stratégie | Trades (remplissages) | Parts | $ engagés | Résultat | IC 90 % | par $ | Creux | Avant le 13.10 |
|---|---|---|---|---|---|---|---|---|
| FAST (exécution 164 ms après le signal) | 1 923 | 474 240 | 71 938 $ | +7 827 $ | [−2 712 ; +18 516] | +0,11 | −3 173 $ | +3 470 $ (+0,16 par $) |
| SLOW (exécution 1,164 s après) | 1 210 | 427 436 | 52 827 $ | +1 770 $ | [−8 315 ; +12 772] | +0,03 | −8 290 $ | +620 $ |
| HYBRID (FAST sinon SLOW) | 1 959 | 485 735 | 73 571 $ | +9 157 $ | [−1 671 ; +20 969] | +0,12 | −3 640 $ | +3 684 $ |
| C moteur alpha (exécution à 300 ms) | 177 | — | 8 228 $ | +1 252 $ | [−344 ; +3 029] | +0,15 | −627 $ | +765 $ [−125 ; +1 813] |

- FAST et HYBRID restent positifs et se rapprochent du seuil, mais l'IC contient toujours 0 : **non démontré**.
- SLOW redevient légèrement positif mais reste loin derrière FAST : l'avantage, s'il existe, est très court.
- Le moteur C reste stable et positif (+0,15 par $), mais petit (177 trades) et son IC contient 0 : **non démontré**.
- Totaux FAST / SLOW / HYBRID identiques entre fast_fenetre.py (section 6) et le script récapitulatif.
- Le diagnostic de fenêtre (fast_fenetre, sections 3 et 4) ne change pas : 44 % des achats arrivent moins de 150 ms après notre information, et le retard preneur de 150 ms n'est **jamais mesuré par un vrai ordre**.

## 4. Ce qui change par rapport à la version du 15.10 (32 h de makers)

| Variante | Version du 15.10 | Version complète | Ce qui change |
|---|---|---|---|
| M0 témoin | +2 595 $ [−772 ; +6 394] | −5 $ [−4 153 ; +4 405] | le gain des 32 premières heures était de la chance |
| M5 | −4 564 $, pire que M0 : −7 159 [−14 088 ; −145] | −1 136 $, écart à M0 −1 131 [−14 753 ; +13 275] | « M5 pire que le hasard » disparaît : c'était un effet de la période courte |
| M8 | +5 951 $ [−724 ; +13 004] | +10 647 $ [+738 ; +20 788] | passe juste au-dessus du seuil (+4 297 $ de plus sur les cycles après le 14.10 07:50) |
| M8b | +5 189 $ [−1 496 ; +12 459] | +9 010 $ [−820 ; +19 294] | progresse, reste sous le seuil |
| M2 5 c / M4 / M3 | +1 035 / +1 163 / +1 850 $ | +2 012 / +1 303 / +2 656 $ | toujours dans le bruit |
| M2 10 c / M1 / M10 | +273 / −1 673 / −1 344 $ | −1 463 / −680 / −4 589 $ | toujours dans le bruit |
| FAST / HYBRID | +4 525 / +4 525 $ (+0,08 par $) | +7 827 / +9 157 $ (+0,11 / +0,12 par $) | mieux, toujours non démontré |
| SLOW | −2 737 $ | +1 770 $ | toujours non démontré |
| C | +734 $ [−501 ; +1 953] | +1 252 $ [−344 ; +3 029] | toujours non démontré |

Note : les chiffres des 32 premières heures ont un peu bougé dans la sauvegarde réparée (par exemple M0 +2 779 $ au lieu de +2 595 $ sur la même tranche), car quelques offres ont été réglées après coup.

## 5. Décision proposée (tu décides)

1. **Arrêter la piste « maker passif »** (M1, M2, M3, M4 et ses variantes, M5, M6, M10) comme source de gain : sur 3,3 jours, rien ne fait mieux que des offres posées au hasard, et le prix repart contre nous après les remplissages.
2. **M8 : continuer, sans argent.** C'est le seul résultat qui passe la règle figée, mais de justesse et avec les réserves de la section 2. Proposition : fixer dès maintenant une **nouvelle période de confirmation** (par exemple les cycles à partir du 16.10 08:00 UTC, verdict après 3 jours, même règle : IC 90 % au-dessus de 0 et au-dessus de M0), sans rien régler entre-temps. Pas de nouveau fantôme : M8 / M8b tournent déjà.
3. **Continuer à observer FAST / HYBRID et le moteur C** sans argent : positifs, non démontrés.
4. **Aucun passage en réel.** M8 (partie preneur) et FAST dépendent du vrai retard preneur, qui ne se mesure qu'avec un ordre réel de test (1 $) : c'est à toi de décider si tu l'autorises.

## 6. Limites

- Remplissages simulés (file d'attente reconstituée à partir du carnet), pas des exécutions réelles.
- Beaucoup de lignes testées en même temps : un IC 90 % qui exclut 0 de peu (M8) peut être dû au hasard. Quelques sous-cohortes de M8 / M8b ont aussi un IC au-dessus de 0 dans resultat_fast_fenetre_hors_echantillon_complet.md (par exemple M8 « V2-F incertitude 0,01 % » +2 610 $ [+663 ; +4 762], « cohorte B » +1 924 $ [+117 ; +3 814]) : ce n'est pas une preuve supplémentaire, ce sont les mêmes offres découpées.
- Défaut repéré dans maker_h559.py et fast_fenetre.py (inchangés) : le groupe « M1 » y inclut aussi M10 et M11, « M8 » y inclut M8b (section 5 de maker_h559 : +19 658 $ = M8 + M8b), et « M4 » (section 6 de fast_fenetre) inclut M4a/M4b/M4c. Les tableaux ci-dessus utilisent les groupes exacts (script verdict_hors_echantillon_bot95.py, lecture seule). Les lignes maker de la section 6 de fast_fenetre ne portent que sur les cycles avec signal : ne pas les utiliser pour juger les makers.
- Changements techniques, sans effet sur les calculs : verdict_hors_echantillon_bot95.py a reçu l'option --complet (nom du fichier de sortie et texte des limites) ; fast_fenetre.py a été lancé par lance_fast_fenetre_complet.py, qui ne garde que les 10 premiers champs de chaque offre lue dans les cycles (les seuls utilisés) pour tenir en mémoire, et écrit dans un fichier séparé. Les fichiers du 15.10 sont gardés comme historique.

Fichiers (dossier etude/bot5min) : resultat_maker_h559_hors_echantillon_complet.md, resultat_fast_fenetre_hors_echantillon_complet.md, resultat_verdict_hors_echantillon_bot95_complet.md. Version du 15.10 : rapport_verdict_hors_echantillon_bot95.md.
