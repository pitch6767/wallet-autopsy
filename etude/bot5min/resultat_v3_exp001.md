# BOT95 V3 — Expérience 001 : qui bouge en premier ? (FIRST MOVER)

928 cycles BTC 5 min réglés (07.10 08:00 → 10.10 13:45, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 40 cycles seulement (après 10.10 10:25) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.

Photos utilisées : 748 cycles (première photo « avant » de chaque cycle, ≥ 50 lignes), dont 732 avec résultat officiel (app. 298 · valid. 394 · inédit 40). Les photos commencent le 07.10 à 15:43 : l'apprentissage des photos est plus court que celui des lignes.

**Résolution** : lignes à 100 ms, mais les prix des bourses ne changent en médiane que toutes les 0,4-0,5 s (Chainlink 0,9 s) — voir l'audit. Les temps ci-dessous sont des multiples de 100 ms, à l'heure de RÉCEPTION par le bot : une avance de 100-400 ms peut n'être qu'une différence de latence réseau. Les fenêtres de 50 ms ne sont pas mesurables avec ces données (le programme du VPS de Dublin `bot95/rapide/rapide.js` les mesurera).

Règles (fixées avant, reprises de `lead_analyse.py`) : bourse/Chainlink « bouge » = ≥ 5 $ dans le sens du signal depuis le début de la photo ; Polymarket « bouge » = le meilleur vendeur de notre côté baisse d'au moins 1 c. **Ces deux seuils ne sont pas comparables** (1 c de Polymarket arrive bien plus souvent que 5 $ de BTC) : « Polymarket premier » est en partie un effet de seuil.

## 1. Premier à bouger, temps d'avance et ordre

| Premier à bouger | Photos | Part | Avance sur le signal (médiane, ms) | p25-p75 (ms) | Gagné (côté du signal) |
|---|---|---|---|---|---|
| Polymarket | 471 | 64 % | 8142 | 6101-9310 | 24 % |
| Coinbase | 103 | 14 % | 8688 | 6326-9418 | 19 % |
| Bybit | 78 | 11 % | 7931 | 6516-8915 | 22 % |
| personne | 44 | 6 % | — | — | 30 % |
| OKX | 16 | 2 % | 8626 | 6720-9608 | 19 % |
| Chainlink | 15 | 2 % | 8642 | 8390-9134 | 27 % |
| Binance | 5 | 1 % | 8267 | 7938-8841 | 40 % |

Ordre complet des mouvements (les 12 séquences les plus fréquentes ; « = » : même ligne de 100 ms) :

| Séquence | Photos | Gagné |
|---|---|---|
| Polymarket | 328 | 23 % |
| Polymarket → Coinbase | 56 | 20 % |
| Coinbase → Polymarket | 51 | 22 % |
| personne | 44 | 30 % |
| Coinbase | 14 | 21 % |
| Polymarket → Bybit | 9 | 33 % |
| Polymarket → Chainlink | 8 | 50 % |
| Bybit = OKX = Binance → Coinbase → Chainlink | 8 | 12 % |
| Polymarket → OKX | 5 | 40 % |
| Polymarket → Bybit = OKX | 5 | 40 % |
| Bybit → Polymarket → Coinbase | 5 | 60 % |
| Polymarket → Coinbase → Bybit = OKX | 4 | 25 % |

Décalage entre sources quand les deux ont bougé (médiane, ms ; positif = la source de la ligne bouge AVANT celle de la colonne) :

| | Bybit | OKX | Coinbase | Binance | Chainlink | Polymarket |
|---|---|---|---|---|---|---|
| Bybit | — | +0 (158) | +300 (155) | +300 (125) | +2300 (101) | -2100 (110) |
| OKX | +0 (158) | — | +100 (137) | +100 (122) | +2100 (100) | -3500 (87) |
| Coinbase | -300 (155) | -100 (137) | — | +100 (113) | +1900 (104) | -200 (202) |
| Binance | -300 (125) | -100 (122) | -100 (113) | — | +1700 (96) | -3300 (65) |
| Chainlink | -2300 (101) | -2100 (100) | -1900 (104) | -1700 (96) | — | -600 (64) |
| Polymarket | +2100 (110) | +3500 (87) | +200 (202) | +3300 (65) | +600 (64) | — |

## 2. Direction et amplitude sur les 10 s avant le signal ; confirmation ou divergence

| Source | Mouvement médian dans le sens du signal | p10 | p90 | Photos où la source va CONTRE le signal (≤ −5 $ / ≤ −1 c) |
|---|---|---|---|---|
| Bybit | -0.1 $ | -16.0 | +18.5 | 257 (35 %) |
| OKX | +0.0 $ | -15.4 | +15.1 | 231 (32 %) |
| Coinbase | -0.0 $ | -16.1 | +13.1 | 235 (32 %) |
| Binance | -0.0 $ | -15.0 | +12.1 | 234 (32 %) |
| Chainlink | -0.4 $ | -11.9 | +8.5 | 172 (23 %) |
| Polymarket | +4.0 c | -3.1 | +16.0 | 136 (19 %) |

## 3. Résultat par premier à bouger — exécution réaliste

Signal = l'achat du côté du modèle au prix vendeur vu par le bot en direct (`ask` de la photo). (A) première ligne enregistrée (≈ 0,3 s) au signal ou après : meilleur vendeur seul, quantité affichée, jamais plus cher que le prix du signal, 50 $ max. (B) photo « après » (100 ms) : balayage des 3 premiers niveaux ≤ prix du signal. Achats = achats réellement exécutés en (A). « Gagné » = part des achats gagnants.

### Par premier à bouger

**apprentissage** (298 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Polymarket (180 photos) | 134 | 24 % | **+673 $** | +5,02 $ | +226 $ | −437 $ | −1 073 $ | −2 115 $ | −1 214 $ | 1,20 | [−1 207 $ ; +2 584 $] | +716 $ | +925 $ · +836 $ · +543 $ · +709 $ · +550 $ |
| Coinbase (39 photos) | 29 | 21 % | **+358 $** | +12,34 $ | −72 $ | −619 $ | −692 $ | −702 $ | −504 $ | 1,49 | [−667 $ ; +1 648 $] | −187 $ | +356 $ · +274 $ · +337 $ · −48 $ · −269 $ |
| Bybit (47 photos) | 32 | 12 % | **−532 $** | −16,64 $ | −743 $ | −994 $ | −1 026 $ | −984 $ | −608 $ | 0,48 | [−1 064 $ ; +72 $] | −231 $ | −418 $ · −280 $ · −476 $ · −343 $ · −313 $ |
| OKX (11 photos) | 6 | 33 % | **+6 $** | +1,08 $ | −102 $ | −144 $ | −53 $ | −0 $ | −91 $ | 1,04 | [−204 $ ; +229 $] | +17 $ | +24 $ · +12 $ · +12 $ · −8 $ · +1 $ |
| Chainlink (9 photos) | 5 | 40 % | **+75 $** | +14,92 $ | −40 $ | −66 $ | −0 $ | −0 $ | −53 $ | 2,10 | [−119 $ ; +294 $] | +54 $ | +113 $ · +112 $ · +73 $ · +78 $ · +0 $ |
| Binance (2 photos) | 1 | 100 % | **+120 $** | +119,86 $ | +0 $ | +0 $ | +0 $ | +0 $ | +0 $ | ∞ | [+0 $ ; +360 $] | +120 $ | +120 $ · +120 $ · +120 $ · +120 $ · +120 $ |
| personne (10 photos) | 6 | 33 % | **+81 $** | +13,57 $ | −58 $ | −124 $ | −53 $ | +0 $ | −72 $ | 1,65 | [−90 $ ; +272 $] | +44 $ | −13 $ · +88 $ · +99 $ · +34 $ · +87 $ |

**validation** (394 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Polymarket (266 photos) | 216 | 20 % | **+193 $** | +0,89 $ | −310 $ | −1 088 $ | −1 609 $ | −2 637 $ | −1 866 $ | 1,03 | [−1 929 $ ; +2 480 $] | −36 $ | −478 $ · −237 $ · +20 $ · −113 $ · −93 $ |
| Coinbase (56 photos) | 45 | 13 % | **−1 029 $** | −22,86 $ | −1 226 $ | −1 576 $ | −1 728 $ | −1 720 $ | −1 075 $ | 0,41 | [−1 843 $ ; −206 $] | −670 $ | −597 $ · −588 $ · −682 $ · −725 $ · −569 $ |
| Bybit (30 photos) | 23 | 26 % | **+198 $** | +8,60 $ | −12 $ | −252 $ | −461 $ | −524 $ | −290 $ | 1,37 | [−426 $ ; +848 $] | −57 $ | +288 $ · +203 $ · +245 $ · +92 $ · +142 $ |
| OKX (5 photos) | 3 | 0 % | **−133 $** | −44,23 $ | −106 $ | +0 $ | +0 $ | +0 $ | −133 $ | 0,00 | [−265 $ ; −27 $] | −134 $ | −138 $ · −133 $ · −133 $ · −134 $ · −136 $ |
| Chainlink (6 photos) | 2 | 0 % | **−106 $** | −52,83 $ | −53 $ | +0 $ | +0 $ | +0 $ | −106 $ | 0,00 | [−212 $ ; +0 $] | −106 $ | −106 $ · −106 $ · −106 $ · −106 $ · −106 $ |
| Binance (3 photos) | 3 | 0 % | **−129 $** | −42,93 $ | −106 $ | +0 $ | +0 $ | +0 $ | −129 $ | 0,00 | [−265 $ ; −23 $] | −81 $ | −129 $ · −129 $ · −129 $ · −82 $ · −74 $ |
| personne (28 photos) | 25 | 20 % | **+39 $** | +1,55 $ | −202 $ | −587 $ | −748 $ | −725 $ | −241 $ | 1,05 | [−593 $ ; +775 $] | +183 $ | −50 $ · +17 $ · +0 $ · −97 $ · −149 $ |

**inédit** (40 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Polymarket (25 photos) | 21 | 14 % | **−702 $** | −33,45 $ | −757 $ | −787 $ | −776 $ | −579 $ | −757 $ | 0,11 | [−955 $ ; −461 $] | −575 $ | −592 $ · −682 $ · −659 $ · −719 $ · −559 $ |
| Coinbase (8 photos) | 6 | 17 % | **−129 $** | −21,52 $ | −187 $ | −158 $ | −53 $ | +0 $ | −187 $ | 0,31 | [−270 $ ; +6 $] | −128 $ | −127 $ · −26 $ · −113 $ · −166 $ · −107 $ |
| Bybit (1 photos) | 1 | 0 % | **−53 $** | −52,99 $ | +0 $ | +0 $ | +0 $ | +0 $ | −53 $ | 0,00 | [−106 $ ; +0 $] | −53 $ | −53 $ · −53 $ · −53 $ · −53 $ · −53 $ |
| personne (6 photos) | 4 | 50 % | **+70 $** | +17,59 $ | −69 $ | −53 $ | +0 $ | +0 $ | −73 $ | 1,96 | [−146 $ ; +378 $] | −106 $ | +87 $ · +67 $ · +67 $ · −106 $ · −106 $ |

**toutes périodes** (732 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Polymarket (471 photos) | 371 | 21 % | **+163 $** | +0,44 $ | −339 $ | −1 233 $ | −1 896 $ | −3 384 $ | −2 479 $ | 1,02 | [−2 672 $ ; +3 061 $] | +104 $ | −146 $ · −83 $ · −97 $ · −123 $ · −102 $ |
| Coinbase (103 photos) | 80 | 16 % | **−800 $** | −10,00 $ | −1 230 $ | −1 777 $ | −2 150 $ | −2 582 $ | −1 433 $ | 0,70 | [−2 215 $ ; +853 $] | −984 $ | −367 $ · −340 $ · −458 $ · −939 $ · −946 $ |
| Bybit (78 photos) | 56 | 18 % | **−388 $** | −6,92 $ | −598 $ | −1 005 $ | −1 245 $ | −1 616 $ | −659 $ | 0,76 | [−1 290 $ ; +529 $] | −341 $ | −183 $ · −131 $ · −284 $ · −304 $ · −224 $ |
| OKX (16 photos) | 9 | 22 % | **−126 $** | −14,03 $ | −235 $ | −276 $ | −212 $ | −0 $ | −186 $ | 0,55 | [−373 $ ; +133 $] | −117 $ | −114 $ · −121 $ · −121 $ · −142 $ · −135 $ |
| Chainlink (15 photos) | 7 | 29 % | **−31 $** | −4,43 $ | −145 $ | −171 $ | −106 $ | −0 $ | −159 $ | 0,82 | [−265 $ ; +222 $] | −51 $ | +7 $ · +6 $ · −33 $ · −28 $ · −106 $ |
| Binance (5 photos) | 4 | 25 % | **−9 $** | −2,24 $ | −129 $ | −53 $ | +0 $ | +0 $ | −129 $ | 0,93 | [−227 $ ; +238 $] | +39 $ | −9 $ · −9 $ · −9 $ · +37 $ · +46 $ |
| personne (44 photos) | 35 | 26 % | **+190 $** | +5,44 $ | −51 $ | −435 $ | −722 $ | −946 $ | −314 $ | 1,20 | [−556 $ ; +943 $] | +121 $ | +24 $ · +172 $ · +166 $ · −169 $ · −168 $ |

### Confirmation / divergence des 4 bourses

**apprentissage** (298 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| divergence (≥ 1 bourse contre nous) (144 photos) | 117 | 26 % | **+1 506 $** | +12,87 $ | +1 155 $ | +492 $ | −143 $ | −1 230 $ | −1 059 $ | 1,53 | [−458 $ ; +3 604 $] | +1 440 $ | +1 491 $ · +1 410 $ · +1 278 $ · +1 354 $ · +552 $ |
| confirmation forte (≥ 3 bourses avec, 0 contre) (75 photos) | 42 | 14 % | **−804 $** | −19,14 $ | −1 014 $ | −1 115 $ | −1 182 $ | −1 202 $ | −920 $ | 0,34 | [−1 299 $ ; −284 $] | −630 $ | −457 $ · −325 $ · −596 $ · −548 $ · −527 $ |
| aucune bourse ne bouge (58 photos) | 40 | 25 % | **−12 $** | −0,30 $ | −459 $ | −707 $ | −903 $ | −1 084 $ | −606 $ | 0,99 | [−799 $ ; +895 $] | +2 $ | +9 $ · −46 $ · −58 $ · −99 $ · +378 $ |
| confirmation partielle (1-2 bourses avec, 0 contre) (21 photos) | 14 | 14 % | **+91 $** | +6,48 $ | −339 $ | −347 $ | −341 $ | −210 $ | −329 $ | 1,26 | [−511 $ ; +986 $] | −279 $ | +65 $ · +122 $ · +84 $ · −166 $ · −228 $ |

**validation** (394 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| divergence (≥ 1 bourse contre nous) (186 photos) | 154 | 15 % | **−1 582 $** | −10,27 $ | −2 084 $ | −2 562 $ | −2 932 $ | −3 785 $ | −1 859 $ | 0,68 | [−3 288 $ ; +240 $] | −2 199 $ | −1 734 $ · −1 995 $ · −1 977 $ · −2 214 $ · −2 251 $ |
| aucune bourse ne bouge (123 photos) | 109 | 28 % | **+1 294 $** | +11,87 $ | +847 $ | +365 $ | −89 $ | −1 016 $ | −624 $ | 1,39 | [−259 $ ; +2 920 $] | +1 182 $ | +850 $ · +1 331 $ · +1 464 $ · +1 039 $ · +953 $ |
| confirmation partielle (1-2 bourses avec, 0 contre) (44 photos) | 29 | 10 % | **−620 $** | −21,37 $ | −784 $ | −1 013 $ | −1 011 $ | −941 $ | −731 $ | 0,39 | [−1 109 $ ; −94 $] | −522 $ | −680 $ · −609 $ · −581 $ · −577 $ · −452 $ |
| confirmation forte (≥ 3 bourses avec, 0 contre) (41 photos) | 25 | 16 % | **−59 $** | −2,34 $ | −390 $ | −720 $ | −745 $ | −715 $ | −457 $ | 0,92 | [−809 $ ; +861 $] | +638 $ | +353 $ · +300 $ · +309 $ · +588 $ · +766 $ |

**inédit** (40 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| divergence (≥ 1 bourse contre nous) (23 photos) | 18 | 17 % | **−497 $** | −27,60 $ | −555 $ | −573 $ | −562 $ | −422 $ | −511 $ | 0,13 | [−625 $ ; −383 $] | −515 $ | −536 $ · −461 $ · −505 $ · −656 $ · −569 $ |
| aucune bourse ne bouge (16 photos) | 13 | 23 % | **−265 $** | −20,37 $ | −405 $ | −475 $ | −421 $ | −158 $ | −267 $ | 0,44 | [−504 $ ; −8 $] | −294 $ | −96 $ · −181 $ · −201 $ · −335 $ · −203 $ |
| confirmation partielle (1-2 bourses avec, 0 contre) (1 photos) | 1 | 0 % | **−53 $** | −52,56 $ | +0 $ | +0 $ | +0 $ | +0 $ | −53 $ | 0,00 | [−158 $ ; +0 $] | −53 $ | −53 $ · −53 $ · −53 $ · −53 $ · −53 $ |

**toutes périodes** (732 photos) — exécution (A) lignes enregistrées, délai 0

| Groupe | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) | (A) délai 0,5 s demandé | (B) carnet photo 3 niveaux : 0 · 0,1 · 0,2 · 0,5 · 1 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| divergence (≥ 1 bourse contre nous) (353 photos) | 289 | 20 % | **−573 $** | −1,98 $ | −1 076 $ | −1 758 $ | −2 421 $ | −3 697 $ | −2 331 $ | 0,93 | [−3 248 $ ; +2 062 $] | −1 274 $ | −780 $ · −1 045 $ · −1 205 $ · −1 516 $ · −2 268 $ |
| aucune bourse ne bouge (197 photos) | 162 | 27 % | **+1 017 $** | +6,28 $ | +570 $ | −118 $ | −600 $ | −1 575 $ | −747 $ | 1,21 | [−761 $ ; +2 891 $] | +889 $ | +763 $ · +1 104 $ · +1 205 $ · +605 $ · +1 127 $ |
| confirmation forte (≥ 3 bourses avec, 0 contre) (116 photos) | 67 | 15 % | **−862 $** | −12,87 $ | −1 194 $ | −1 614 $ | −1 788 $ | −1 957 $ | −1 377 $ | 0,56 | [−1 770 $ ; +142 $] | +8 $ | −103 $ · −25 $ · −287 $ · +41 $ · +238 $ |
| confirmation partielle (1-2 bourses avec, 0 contre) (66 photos) | 44 | 11 % | **−581 $** | −13,22 $ | −1 011 $ | −1 290 $ | −1 414 $ | −1 404 $ | −1 001 $ | 0,59 | [−1 394 $ ; +413 $] | −854 $ | −668 $ · −540 $ · −549 $ · −796 $ · −733 $ |

## 4. Coinbase est-il un vrai indicateur avancé ?

### 4a. Le groupe « Coinbase premier » période par période

| Période | Photos | Coinbase premier | Gagné | Résultat (A) délai 0 | sans top 1 | sans top 3 | IC 90 % | (A) 0,5 s | Autres photos : résultat (A) 0 |
|---|---|---|---|---|---|---|---|---|---|
| apprentissage | 298 | 39 (13 %) | 21 % | **+358 $** | −72 $ | −619 $ | [−661 $ ; +1 618 $] | −187 $ | +422 $ |
| validation | 394 | 56 (14 %) | 13 % | **−1 029 $** | −1 226 $ | −1 576 $ | [−1 811 $ ; −190 $] | −670 $ | +62 $ |
| inédit | 40 | 8 (20 %) | 17 % | **−129 $** | −187 $ | −158 $ | [−310 $ ; +6 $] | −128 $ | −685 $ |

### 4b. Pouvoir prédictif, à mouvement de Bybit connu

Pas de 1 s, sans chevauchement, dans les 20 s autour de chaque signal (photos avant + après). Régression : mouvement FUTUR de la cible sur [t, t+1 s] = a + b × mouvement PASSÉ de Coinbase sur [t−1 s, t] + c × mouvement PASSÉ de Bybit sur [t−1 s, t]. Si Coinbase est un vrai indicateur avancé, b doit être positif et stable d'une période à l'autre. Échantillon biaisé : uniquement des fenêtres autour de désaccords. t de Student naïfs (observations d'une même photo non indépendantes).

| Période | Pas de 1 s | Cible | b Coinbase (t) | c Bybit (t) |
|---|---|---|---|---|
| apprentissage | 5142 | Polymarket Up, Coinbase SEUL (sans Bybit) | +3.118 (+4.8) | — |
| apprentissage | 5142 | Polymarket Up (milieu, en c pour 100 $) | -6.413 (-8.1) | +18.244 (+19.7) |
| apprentissage | 5142 | Chainlink ($ par $) | +0.132 (+10.8) | -0.003 (-0.2) |
| apprentissage | 5142 | Bybit futur ($ par $) | +0.025 (+1.7) | +0.084 (+4.8) |
| apprentissage | 5142 | Coinbase futur ($ par $) | -0.337 (-20.5) | +0.562 (+29.2) |
| validation | 6835 | Polymarket Up, Coinbase SEUL (sans Bybit) | +7.521 (+8.2) | — |
| validation | 6835 | Polymarket Up (milieu, en c pour 100 $) | -2.292 (-2.3) | +27.177 (+22.2) |
| validation | 6835 | Chainlink ($ par $) | +0.084 (+10.9) | +0.013 (+1.3) |
| validation | 6835 | Bybit futur ($ par $) | +0.016 (+1.4) | +0.052 (+3.8) |
| validation | 6835 | Coinbase futur ($ par $) | -0.330 (-26.5) | +0.543 (+35.2) |
| inédit | 673 | Polymarket Up, Coinbase SEUL (sans Bybit) | +0.127 (+0.0) | — |
| inédit | 673 | Polymarket Up (milieu, en c pour 100 $) | -2.234 (-0.5) | +14.400 (+1.7) |
| inédit | 673 | Chainlink ($ par $) | -0.012 (-0.7) | +0.044 (+1.3) |
| inédit | 673 | Bybit futur ($ par $) | +0.014 (+0.7) | -0.014 (-0.3) |
| inédit | 673 | Coinbase futur ($ par $) | -0.285 (-7.3) | +0.515 (+6.2) |

Lecture : pour Polymarket, b = de combien de centimes le milieu Up bouge dans la seconde suivante pour 100 $ de mouvement passé de Coinbase (Bybit tenu constant).
