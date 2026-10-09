# Inertie de la moyenne de clôture — BTC, 697 cycles (07.10 08:05 → 09.10 22:35)

201083 mesures du carnet dans les 90 dernières secondes. Probabilité « moteur TWAP » calculée avec seulement ce qui était connu à l'instant.

## 1. Qui prévoit le mieux le gagnant officiel : notre moteur TWAP ou le carnet Polymarket ?

| Temps restant | Mesures | Brier moteur TWAP | Brier Polymarket (milieu) | Le meilleur |
|---|---|---|---|---|
| 60-90 s | 40618 | 0.1107 | 0.1129 | moteur TWAP |
| 40-60 s | 14072 | 0.1035 | 0.1050 | moteur TWAP |
| 20-40 s | 5990 | 0.0831 | 0.0736 | Polymarket |
| 10-20 s | 944 | 0.0765 | 0.0831 | moteur TWAP |
| 1-10 s | 165 | 0.1046 | 0.0344 | Polymarket |

Brier : plus bas = meilleur. Le milieu Polymarket n'existe pas quand un côté du carnet est vide (souvent dans les dernières secondes).

## 2. Achats simulés (un par cycle, 50 $ au meilleur vendeur limité à la quantité affichée, frais compris)

| Règle | Achats | Gagnés | Prix moyen | Résultat | Par $ | Creux | 1re moitié / 2e moitié |
|---|---|---|---|---|---|---|---|
| moteur TWAP − prix ≥ 0.10, 60 dernières secondes | 172 | 54 (31 %) | 0.21 | **+1'358 $** | +32 % | −549 $ | +1'445 $ / −87 $ |
| moteur TWAP − prix ≥ 0.15, 60 dernières secondes | 133 | 47 (35 %) | 0.21 | **+1'703 $** | +49 % | −396 $ | +1'061 $ / +642 $ |
| moteur TWAP − prix ≥ 0.20, 60 dernières secondes | 92 | 36 (39 %) | 0.22 | **+1'795 $** | +85 % | −265 $ | +966 $ / +828 $ |
| moteur TWAP − prix ≥ 0.30, 60 dernières secondes | 47 | 22 (47 %) | 0.22 | **+1'316 $** | +151 % | −153 $ | +666 $ / +650 $ |
| moteur TWAP − prix ≥ 0.10, 60-90 s avant la fin | 245 | 84 (34 %) | 0.26 | **+2'125 $** | +29 % | −576 $ | +1'393 $ / +732 $ |
| moteur TWAP − prix ≥ 0.20, 60-90 s avant la fin | 84 | 44 (52 %) | 0.28 | **+1'900 $** | +104 % | −197 $ | +997 $ / +903 $ |
| règlement « verrouillé » : moteur ≥ 0.97, prix ≤ 0.9 | 11 | 11 (100 %) | 0.70 | **+173 $** | +48 % | +0 $ | +82 $ / +90 $ |
| règlement « verrouillé » : moteur ≥ 0.99, prix ≤ 0.95 | 16 | 16 (100 %) | 0.79 | **+174 $** | +31 % | +0 $ | +85 $ / +90 $ |
| règlement « verrouillé » : moteur ≥ 0.95, prix ≤ 0.85 | 12 | 12 (100 %) | 0.67 | **+188 $** | +53 % | +0 $ | +114 $ / +75 $ |
| réaction excessive : notre côté chute de ≥ 0.10 en 3 s alors que la proba TWAP baisse 3× moins, et moteur > prix | 105 | 25 (24 %) | 0.28 | **−271 $** | -8 % | −976 $ | +333 $ / −604 $ |
| réaction excessive : notre côté chute de ≥ 0.20 en 3 s alors que la proba TWAP baisse 3× moins, et moteur > prix | 54 | 13 (24 %) | 0.32 | **−619 $** | -34 % | −927 $ | −347 $ / −272 $ |

## 3. Où le carnet et le moteur divergent le plus (60 dernières secondes, carnet entre 5 et 95 c)

Écart moyen |moteur − carnet| : 0.117 ; corrélation 0.894 (12413 mesures).