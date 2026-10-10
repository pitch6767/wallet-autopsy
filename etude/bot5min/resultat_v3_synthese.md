# BOT95 V3 — synthèse des expériences 001 à 006 (hors ligne)

Étude du 10.10.2026, faite **hors ligne** sur les fichiers locaux : aucun changement du bot, aucun déploiement, rien de poussé sur git.
Détail : `resultat_v3_audit.md`, `resultat_v3_exp001.md` … `resultat_v3_exp006.md`. Scripts : `v3_commun.py`, `v3_audit.py`, `v3_exp001_premier.py`, `v3_exp002_age.py`,
`v3_exp003_logistique.py`, `v3_exp004_survie.py`, `v3_exp005_regimes.py`, `v3_exp006_routeur.py` (chacun tourne en ~35-40 s).

## 1. Audit des données

| Source | Couverture | Résolution réelle | Ce qui manque |
|---|---|---|---|
| `donnees/*/rec_BTC.json.gz` | 824 674 lignes, 07.10 08:01 → 10.10 14:35 (heure suisse) ; 841 trous > 5 s, ~590 min au total | une ligne toutes les **~0,3 s** (pas 0,25 s) | carnet Polymarket absent sur 12 % des lignes ; seulement le MEILLEUR niveau ; pas de transactions, pas de file d'attente, pas d'intérêt ouvert |
| `officiels.json` | 933 cycles BTC, 07.10 08:00 → 10.10 13:45, sans trou | — | cycles après 13:45 non réglés (exclus) |
| Cycles utilisables | **928** : apprentissage 455 (→ 08.10 22:00) · validation 433 (→ 10.10 10:25) · **inédit 40** (→ 13:45) | — | le test inédit = 3 h 20 d'une seule matinée : **trop petit pour un verdict seul** |
| `lead.json.gz` (photos) | 748 cycles (07.10 15:43 → 10.10 15:00), 732 réglés ; 42 cycles en double, 17 sans photo « après » | lignes à 100 ms, mais les prix des bourses ne changent que toutes les 0,4-0,5 s (Chainlink 0,9 s) | horodatage = réception par le bot, pas l'heure de la bourse |
| `sauvegarde/*.json` | fantômes réels, surtout 09.10 01:00 → 10.10 13:45 ; V2-F 0,01 % seulement 11 trades | — | pas de fantôme réel pour désaccord 30 / 20 60-180 s / jeton 0,35-0,65 |
| `twap_carnets.json`, `vitesse.json` | 218 et 12 signaux du 10.10 | 8 niveaux | hors périmètre / trop peu |
| Intérêt ouvert (open interest) | **absent partout** | — | — |

**Point d'audit important** : sur les mêmes cycles, le rejeu ne reproduit pas les fantômes réels (V2-D : réel +358 $ contre rejeu −1 405 $ sur 300 cycles ; V2-G : réel +416 $ contre rejeu +1 338 $ ; V2-F original : −1 738 $ contre −1 891 $, proche). Tous les chiffres ci-dessous sont des **exécutions simulées** sur les lignes enregistrées ; le délai 0 est une borne théorique (latence nulle).

## 2. Les 7 stratégies, exécution réaliste (meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, frais, 50 $ max)

| Stratégie | App. 0 s | App. 0,5 s | **Valid. 0,5 s** | Valid. 0,5 s sans top 5 | IC 90 % valid. 0,5 s | Inédit 0,5 s | Offres parties à ~0,6 s |
|---|---|---|---|---|---|---|---|
| V2-F original (O8) | +593 $ (339) | +424 $ (208) | **−1 945 $** (276) | −3 714 $ | [−4 350 ; +885] | −939 $ (24) | 33 % |
| V2-F 0,01 % (H1) | +2 350 $ (233) | +262 $ (110) | **+412 $** (142) | −1 072 $ | [−1 400 ; +2 368] | −565 $ (16) | 47 % |
| V2-D perp 120-269 s | +1 678 $ (215) | +1 649 $ (132) | **−670 $** (218) | −2 626 $ | [−3 116 ; +1 982] | −771 $ (29) | 30 % |
| V2-G jury des bourses | +234 $ (294) | −528 $ (159) | **+52 $** (247) | −1 904 $ | [−2 801 ; +2 948] | −203 $ (25) | 37 % |
| désaccord 30 | +2 623 $ (219) | +1 805 $ (127) | **+1 041 $** (200) | −2 044 $ | [−2 396 ; +4 832] | −818 $ (32) | 33 % |
| désaccord 20 60-180 s | +2 050 $ (310) | +1 884 $ (210) | **+1 316 $** (297) | −1 304 $ | [−2 057 ; +4 800] | −251 $ (29) | 25 % |
| désaccord 20 jeton 0,35-0,65 | −58 $ (61) | −60 $ (35) | **+249 $** (20) | −198 $ | [−267 ; +804] | −10 $ (1) | 43 % |

(entre parenthèses : nombre d'achats exécutés). À délai 0 (théorique), seule V2-F 0,01 % a un intervalle de validation qui exclut 0 : +1 889 $ [+29 ; +3 790] — il disparaît dès 0,5 s.
**À 0,5 s, aucune stratégie n'a un résultat de validation dont l'intervalle exclut 0, toutes sont négatives sans leurs 5 meilleurs trades, et toutes perdent sur l'inédit.** Sept stratégies testées en même temps : la meilleure en validation est en partie le fruit du hasard.

## 3. Tableau comparatif des expériences

| Exp. | Question | Résultat clé | Verdict |
|---|---|---|---|
| **001** qui bouge en premier | Ordre Coinbase / Binance / Bybit / OKX / Chainlink / Polymarket avant le 1er désaccord ≥ 0,20 ; Coinbase est-il un vrai indicateur avancé ? | Polymarket bouge en premier dans 64 % des photos (en partie effet de seuil : 1 c contre 5 $), Coinbase 14 %, Bybit 11 %. « Coinbase premier » en exécution réaliste : app. **+358 $** (29 achats) → valid. **−1 029 $** (45, IC [−1 811 ; −190]) → inédit −129 $ (6). Le +1 737 $ de l'ancienne étude (achat illimité au prix du signal) disparaît. Prédiction : le mouvement passé de Coinbase sur 1 s prédit Chainlink la seconde suivante (+0,13 $/$, t = 10,8 en app. ; +0,08, t = 10,9 en valid. ; −0,01 non significatif sur l'inédit, 673 pas) mais **pas Polymarket** une fois Bybit connu (coefficient négatif : Polymarket suit Bybit). | **Non, pas comme signal de trading.** Coinbase devance l'oracle Chainlink (cohérent : Chainlink agrège les prix au comptant), pas le prix Polymarket. Confirmation / divergence des bourses : instable (divergence +1 506 $ en app., −1 582 $ en valid.). |
| **002** micro-âge du désaccord | L'âge du désaccord change-t-il l'espérance ? | 80 % des signaux V2-F sont vus à la ligne même du franchissement (âge mesuré 0). V2-F 0,01 % âge 0 : +3 868 $ à délai 0, mais +672 $ à 0,5 s. Les autres tranches ont 9-78 signaux, sans motif stable (V2-F original 250-500 ms : +504 $ app., +702 $ valid., mais 18 et 26 achats). Désaccord 20 décidé plus tard : 0 s −436 $, 0,3 s −1 033 $, 0,6 s +274 $, 1,2 s +326 $, 2,1 s −854 $ (toutes périodes) — pas de pente, et les survivants ne sont que 66 → 29 %. | **Non mesurable à l'échelle utile.** La résolution (~300 ms) est trop grosse ; les tranches 0-50 / 50-100 ms demandent `rapide.js`. |
| **003** logistique pré-enregistrée | Un modèle simple (10 variables, figé sur l'apprentissage) filtre-t-il les mauvais signaux ? | Apprentissage : V2-F O8 +593 → **+2 297 $** (filtré). Validation délai 0 : −711 → +22 $ ; délai 0,5 s : −1 945 → **−1 568 $ avec une espérance pire** (−16 $ contre −7 $ par achat). Désaccord 20 : validation −228 → **−816 $** (pire). Score de Brier en validation : prix Polymarket 0,152 < logistique 0,157 < modèle du bot 0,201. | **Non.** Sur-apprentissage classique. Le prix Polymarket est la meilleure probabilité disponible ; le modèle du bot (0,08 %) est mal calibré. |
| **004** survie de l'offre | L'offre visée est-elle encore là après 0 / 0,25 / 0,5 / 1 s ? | Coût de 0 → 0,5 s (tolérance 0) : V2-F 0,01 % **−3 685 $** (+3 794 → +109), V2-G −2 250 $, V2-F original −1 491 $, désaccord 30 −955 $ ; désaccord 20 60-180 s +638 $ et V2-D +221 $ (les offres qui restent sont moins chères). 25-47 % des offres sont parties à ~0,6 s. Accepter +1 c / +2 c n'améliore rien (jamais retenu sur l'apprentissage). Photos 100 ms (désaccord 20 en direct) : déjà 14 % des offres absentes au signal, −787 $ à 0 s, −506 $ à 0,1 s, −836 $ à 0,2 s, −1 667 $ à 0,5 s. | **La latence décide de tout pour V2-F 0,01 % et V2-G.** Le gain de V2-F 0,01 % n'existe qu'à latence quasi nulle. Maker : **non mesurable** (pas de file d'attente ni de transactions). |
| **005** matrice des régimes | Une stratégie gagne-t-elle durablement dans un régime précis ? | 134 cases comparables (≥ 10 achats en app. et en valid.) : accord de signe **54 %**, Spearman **−0,17**. En retirant l'effet de la stratégie : accord **35 %**, Spearman **−0,31** (les régimes s'INVERSENT). Volatilité : Spearman −0,61. Les 10 meilleures cases d'apprentissage : 6 restent positives en validation (5 sont des cases de désaccord 30, stratégie déjà positive en validation), 9 sont négatives sur l'inédit et 1 y est vide. | **Non.** Aucun régime stable sur 3 jours. L'apprentissage (07-08.10) était beaucoup plus volatil que la validation : les cases changent de population. |
| **006** routeur | Une règle simple bat-elle une stratégie fixe ? | R0 (meilleure fixe en app., délai 0,5 s) = désaccord 20 60-180 s. Règle pré-enregistrée R* = R0 sauf cases (volatilité × jour/nuit) négatives en app. → validation **−1 332 $** contre **+1 316 $** ; différence **−2 648 $** [−5 801 ; +73], probabilité ≤ 0 = 95 %. Inédit : identique (que des heures de jour). | **Ne change pas le verdict META-ROUTER**, le renforce : filtrer par régime fait perdre. |

## 4. Verdicts honnêtes

1. **Aucune piste V3 ne survit à la validation en exécution réaliste.** Les gains d'apprentissage fondent dès qu'on ajoute 0,5 s de latence, qu'on retire les 5 meilleurs trades, ou qu'on passe à des données jamais vues.
2. **Coinbase n'est pas un indicateur avancé exploitable sur Polymarket** : il devance Chainlink d'environ une seconde, mais le prix Polymarket suit Bybit. Son résultat « premier à bouger » change de signe entre apprentissage et validation.
3. **La seule chose qui rapporte dans ces données, c'est la vitesse** : V2-F 0,01 % vaut +3 794 $ à latence nulle et ~0 $ à 0,6 s. Ce n'est pas une stratégie, c'est une course — et 14 % des offres ont déjà disparu au moment où le bot en direct les voit.
4. **Le prix Polymarket est mieux calibré que le modèle du bot** (Brier 0,152 contre 0,201) : la plupart des « désaccords » sont des erreurs du modèle, pas du marché.
5. Le test inédit (40 cycles) est négatif pour les 7 stratégies, mais il ne couvre qu'une matinée : il confirme sans prouver.

## 5. Ce qui demande les données à la milliseconde du VPS de Dublin (`bot95/rapide/rapide.js`)

- **Survie de l'offre à 50 et 100 ms** pour les 7 stratégies (aujourd'hui : 300 ms sur les lignes, 100 ms seulement pour le désaccord 20 via les photos).
- **Âge du désaccord sous 300 ms** (tranches 0-50 / 50-100 ms de l'expérience 002).
- **Premier à bouger avec l'heure de la bourse** (`tsSrc`) et non l'heure de réception, pour séparer avance réelle et latence réseau ; en particulier l'avance Coinbase → Chainlink.
- **Profondeur au-delà du meilleur niveau** au moment exact de la décision (variantes +1 c / +2 c).
- **Maker** : il faudrait en plus les transactions Polymarket et une hypothèse de file explicite ; même avec `rapide.js`, à prévoir à part.
