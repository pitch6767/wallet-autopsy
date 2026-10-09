# Exécution du modèle corrigé (marge 0,015 %, le fantôme « corrigé » en direct) — BTC, vrais carnets (07.10 08:04 → 09.10 08:05)

**Limite des données :** le bot enregistre seulement le meilleur vendeur (prix et quantité affichée) 4 fois par seconde, pas les niveaux suivants du carnet. La « liquidité multi-niveaux » ne peut donc pas être mesurée sur le passé ; seulement le meilleur prix dans le temps.

## 1. Pré-alerte (ancien modèle) → validation (corrigé)

- Opportunités validées par le corrigé : **306** (115 gagnées).
- Pré-alertes de l'ancien modèle jamais validées par le corrigé dans le cycle : **147** cycles (ce sont les faux désaccords évités).
- Validées après une pré-alerte du même côté : 221 ; délai médian **16.2 s** (moyen 31.1 s, 0 s dans 64 cas).
- Prix à la validation − prix à la pré-alerte : médiane **+0.0 c**, moyenne +0.9 c ; plus cher dans 77 cas, moins cher dans 69.

Sur les 156 validations arrivées au moins 1 s après la pré-alerte : acheter au prix de la pré-alerte aurait fait +9'747 $ contre +6'822 $ au prix de validation (50 $ remplis, pour mesurer le coût du délai seul).

## 2. Politiques d'exécution sur les mêmes 306 opportunités

Résultat par opportunité (une opportunité non remplie compte 0 $). Gagnants à prix ≤ 0,25 $ (petits prix qui paient gros) : 40.

| Politique | Remplies | Mise moyenne | Prix moyen payé | Gagnantes remplies | Petits-prix gagnants remplis | Résultat | Par $ engagé | Creux | 1re moitié | 2e moitié |
|---|---|---|---|---|---|---|---|---|---|---|
| A immédiat (quantité affichée) | 305 / 306 | 26 $ | 0.26 | 115 / 115 | 40 / 40 | **+2'403 $** | +30 % | −580 $ | +1'722 $ | +681 $ |
| A+ immédiat puis compléter à ≤ prix d'entrée pendant 5 s | 306 / 306 | 34 $ | 0.26 | 115 / 115 | 40 / 40 | **+1'626 $** | +16 % | −658 $ | +1'325 $ | +301 $ |
| A+ immédiat puis compléter à ≤ prix d'entrée pendant 15 s | 306 / 306 | 37 $ | 0.26 | 115 / 115 | 40 / 40 | **+2'148 $** | +19 % | −781 $ | +997 $ | +1'151 $ |
| A+ immédiat puis compléter à ≤ prix d'entrée pendant 30 s | 306 / 306 | 41 $ | 0.26 | 115 / 115 | 40 / 40 | **+2'452 $** | +20 % | −934 $ | +936 $ | +1'516 $ |
| W attendre 1 s, acheter si le signal tient encore | 98 / 306 | 34 $ | 0.24 | 26 / 115 | 7 / 40 | **−502 $** | -15 % | −662 $ | −270 $ | −231 $ |
| W attendre 3 s, acheter si le signal tient encore | 19 / 306 | 39 $ | 0.22 | 5 / 115 | 3 / 40 | **+23 $** | +3 % | −412 $ | +97 $ | −74 $ |
| W attendre 5 s, acheter si le signal tient encore | 28 / 306 | 28 $ | 0.24 | 7 / 115 | 2 / 40 | **−283 $** | -36 % | −382 $ | −84 $ | −200 $ |
| D limite passive −1 c pendant 20 s (rien d'immédiat) | 169 / 306 | 48 $ | 0.24 | 36 / 115 | 14 / 40 | **−221 $** | -3 % | −1'714 $ | −671 $ | +450 $ |
| D limite passive −2 c pendant 20 s (rien d'immédiat) | 157 / 306 | 48 $ | 0.25 | 32 / 115 | 13 / 40 | **−77 $** | -1 % | −1'546 $ | −489 $ | +412 $ |
| C hybride : 15 $ immédiat + limite −2 c pour le reste (20 s) | 306 / 306 | 30 $ | 0.26 | 115 / 115 | 40 / 40 | **+1'192 $** | +13 % | −908 $ | +193 $ | +999 $ |

« Prix moyen payé » = meilleur vendeur au moment de la validation pour les opportunités remplies (repère).