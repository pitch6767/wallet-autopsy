# V2-F 0,01 % — attribution exacte des signaux

928 cycles BTC réglés (07.10 08:00 → 10.10 13:45). Apprentissage 455 · validation 433 · inédit 40 (après le 10.10 10:25).

Quatre versions de la même règle V2-F, mêmes cycles :

- **O8 modèle du bot 0,08 % (V2-F original)**
- **X8 reconstruit 0,08 %**
- **X1 reconstruit 0,01 %**
- **H1 modèle du bot ramené à 0,01 % (= fantôme réel)**

Contrôle : la version X1 refait exactement la « V2-F 0,01 % » du META-ROUTER sur 928 cycles sur 928.

## 1. Recouvrement des signaux (cycles où chaque version achète)

| | O8 | X8 | X1 | H1 |
|---|---|---|---|---|
| O8 | **759** | 722 · 712 · 400 | 484 · 427 · 112 | 496 · 435 · 154 |
| X8 | 722 · 712 · 400 | **726** | 480 · 425 · 157 | 490 · 432 · 133 |
| X1 | 484 · 427 · 112 | 480 · 425 · 157 | **497** | 474 · 461 · 297 |
| H1 | 496 · 435 · 154 | 490 · 432 · 133 | 474 · 461 · 297 | **509** |

Chaque case : cycles achetés par les deux · même côté · même côté à 1 s près.

## 2. Les 47 gagnants exclusifs : d'où viennent-ils ?

47 cycles où X1 gagne alors qu'aucune des cinq autres stratégies ne gagne. Pour chacun : que fait X8 (même modèle reconstruit, 0,08 %) ? et H1 (le moteur du bot à 0,01 %) le prend-il aussi ?

| Origine | Cycles | Gain (exécution du META-ROUTER) | dont aussi pris par H1 (même côté) | V2-F original achète ce cycle |
|---|---|---|---|---|
| côté opposé chez X8 | 34 | +989 $ | 29 | 34 |
| formule : X8 (0,08 %, mêmes données) ne déclenche pas dans ce cycle | 11 | +211 $ | 8 | 0 |
| reconstruction : X8 (0,08 %) prend le même signal → la formule n'y est pour rien | 2 | +195 $ | 1 | 2 |

## 3. Ce que la formule change, à données identiques (X1 contre X8)

- Cycles achetés par les deux : 480 ; seulement à 0,01 % : 17 ; seulement à 0,08 % : 246.

À l'instant précis où X1 déclenche dans un cycle que X8 ne prend jamais :

| Raison | Cycles |
|---|---|
| à 0,08 % l'écart n'atteint pas 0,20 | 16 |
| à 0,08 % l'écart est là mais n'a pas grandi de 3 c en 3 s | 1 |

Profil médian de ces 17 signaux : probabilité 0,01 % = 0.70, la même à 0,08 % = 0.61, prix payé = 0.48, temps restant = 154 s ; incertitude due au mouvement d'ici la fin = 47.8 $, incertitude fixe 0,08 % = 66.0 $, 0,01 % = 8.2 $.

| Temps restant au signal (seulement à 0,01 %) | Cycles | Résultat (exécution sans délai) |
|---|---|---|
| 60-120 s | 5 | +64 $ |
| > 120 s | 12 | +159 $ |

## 4. Exécution réaliste : meilleur vendeur seul, quantité affichée, délai entre décision et achat

Achat sur le carnet du moment d'exécution, jamais plus cher que le prix vu à la décision.

### toutes périodes

| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s | Achats (0 s) | Gagnés | Creux (0 s) | Jackpots (0 s) |
|---|---|---|---|---|---|---|---|---|---|
| O8 modèle du bot 0,08 % (V2-F original) | **−969 $** | −1 895 $ | −2 460 $ | −2 368 $ | −2 095 $ | 758 | 22 % | −3 197 $ | 47 |
| X8 reconstruit 0,08 % | **−1 152 $** | −846 $ | −472 $ | +316 $ | +2 $ | 725 | 22 % | −2 627 $ | 58 |
| X1 reconstruit 0,01 % | **+3 798 $** | +771 $ | −413 $ | −434 $ | −986 $ | 495 | 37 % | −829 $ | 29 |
| H1 modèle du bot ramené à 0,01 % (= fantôme réel) | **+3 794 $** | +2 089 $ | +109 $ | −54 $ | −378 $ | 507 | 38 % | −985 $ | 27 |
| ↳ H1 seulement (cycles que V2-F original ne prend pas) | +289 $ | +287 $ | +222 $ | +133 $ | +174 $ | 13 | 85 % | −52 $ | 0 |
| ↳ X1 seulement (cycles que X8 ne prend pas) | +223 $ | +68 $ | +42 $ | −19 $ | −26 $ | 17 | 82 % | −52 $ | 0 |

### apprentissage

| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s | Achats (0 s) | Gagnés | Creux (0 s) | Jackpots (0 s) |
|---|---|---|---|---|---|---|---|---|---|
| O8 modèle du bot 0,08 % (V2-F original) | **+593 $** | +244 $ | +424 $ | −155 $ | +527 $ | 339 | 23 % | −1 920 $ | 26 |
| X8 reconstruit 0,08 % | **−178 $** | −1 104 $ | −622 $ | +575 $ | +110 $ | 330 | 23 % | −2 009 $ | 33 |
| X1 reconstruit 0,01 % | **+2 209 $** | +728 $ | −33 $ | +174 $ | −143 $ | 236 | 40 % | −293 $ | 16 |
| H1 modèle du bot ramené à 0,01 % (= fantôme réel) | **+2 350 $** | +1 619 $ | +262 $ | +574 $ | +3 $ | 233 | 39 % | −356 $ | 14 |
| ↳ H1 seulement (cycles que V2-F original ne prend pas) | +229 $ | +255 $ | +191 $ | +142 $ | +172 $ | 8 | 88 % | −49 $ | 0 |
| ↳ X1 seulement (cycles que X8 ne prend pas) | +131 $ | +94 $ | +66 $ | +20 $ | +22 $ | 9 | 89 % | −30 $ | 0 |

### validation

| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s | Achats (0 s) | Gagnés | Creux (0 s) | Jackpots (0 s) |
|---|---|---|---|---|---|---|---|---|---|
| O8 modèle du bot 0,08 % (V2-F original) | **−711 $** | −1 330 $ | −1 945 $ | −1 731 $ | −2 299 $ | 379 | 21 % | −2 485 $ | 21 |
| X8 reconstruit 0,08 % | **−644 $** | +694 $ | +505 $ | −13 $ | +292 $ | 356 | 21 % | −2 410 $ | 24 |
| X1 reconstruit 0,01 % | **+1 508 $** | +147 $ | −219 $ | −618 $ | −918 $ | 231 | 35 % | −658 $ | 13 |
| H1 modèle du bot ramené à 0,01 % (= fantôme réel) | **+1 889 $** | +1 030 $ | +412 $ | −325 $ | −94 $ | 243 | 38 % | −626 $ | 13 |
| ↳ H1 seulement (cycles que V2-F original ne prend pas) | +59 $ | +32 $ | +31 $ | −9 $ | +3 $ | 5 | 80 % | −52 $ | 0 |
| ↳ X1 seulement (cycles que X8 ne prend pas) | +92 $ | −26 $ | −24 $ | −39 $ | −48 $ | 8 | 75 % | −52 $ | 0 |

### inédit (après 10.10 10:25)

| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s | Achats (0 s) | Gagnés | Creux (0 s) | Jackpots (0 s) |
|---|---|---|---|---|---|---|---|---|---|
| O8 modèle du bot 0,08 % (V2-F original) | **−851 $** | −808 $ | −939 $ | −482 $ | −323 $ | 40 | 20 % | −1 054 $ | 0 |
| X8 reconstruit 0,08 % | **−330 $** | −436 $ | −354 $ | −246 $ | −400 $ | 39 | 21 % | −665 $ | 1 |
| X1 reconstruit 0,01 % | **+81 $** | −103 $ | −160 $ | +10 $ | +76 $ | 28 | 29 % | −231 $ | 0 |
| H1 modèle du bot ramené à 0,01 % (= fantôme réel) | **−445 $** | −560 $ | −565 $ | −304 $ | −287 $ | 31 | 26 % | −638 $ | 0 |
| ↳ H1 seulement (cycles que V2-F original ne prend pas) | +0 $ | +0 $ | +0 $ | +0 $ | +0 $ | 0 | 0 % | +0 $ | 0 |
| ↳ X1 seulement (cycles que X8 ne prend pas) | +0 $ | +0 $ | +0 $ | +0 $ | +0 $ | 0 | 0 % | +0 $ | 0 |

### Pourquoi le délai coûte autant (toutes périodes)

| Version | Délai | Achats à 0 s | Encore achetables après le délai | Résultat à 0 s des achats PERDUS (le prix a monté) | dont gagnants perdus | Résultat des achats faits : à 0 s → après délai |
|---|---|---|---|---|---|---|
| O8 | 0.25 s | 758 | 557 | +746 $ (201) | 55 | −1 716 $ → −1 895 $ |
| O8 | 0.5 s | 758 | 508 | +900 $ (250) | 69 | −1 869 $ → −2 460 $ |
| O8 | 1 s | 758 | 436 | +881 $ (322) | 86 | −1 850 $ → −2 368 $ |
| H1 | 0.25 s | 507 | 304 | +1 156 $ (203) | 85 | +2 638 $ → +2 089 $ |
| H1 | 0.5 s | 507 | 268 | +2 837 $ (239) | 106 | +957 $ → +109 $ |
| H1 | 1 s | 507 | 223 | +3 070 $ (284) | 124 | +724 $ → −54 $ |
| X1 | 0.25 s | 495 | 257 | +2 069 $ (238) | 96 | +1 729 $ → +771 $ |
| X1 | 0.5 s | 495 | 225 | +3 358 $ (270) | 116 | +439 $ → −413 $ |
| X1 | 1 s | 495 | 186 | +4 200 $ (309) | 134 | −403 $ → −434 $ |

## 5. Quand le moteur du bot à 0,01 % (H1) et V2-F original (O8) prennent le même cycle

- 496 cycles communs, dont 435 du même côté et 61 du côté opposé.
- Même côté : H1 déclenche en médiane +0.3 s par rapport à O8 (au même instant à 1 s près : 154 cycles).
