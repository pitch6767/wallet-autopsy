# Modele de mouvement / mort a l'arrivee — vrais carnets du bot

## BTC — 361 desaccords (ecart >= 0,10)

- Mouvement +50 % atteint : **48 %** · gagnant a la fin : 27 % · **mort a l'arrivee : 27 %**
- Tous, garder jusqu'a la fin : 1re moitie -1201 $ (182) · 2e moitie -618 $ (179)
- Tous, revendre a +50 % (sinon garder) : 1re moitie -2087 $ (182) · 2e moitie -932 $ (179)

Taux de « mort a l'arrivee » selon chaque variable (tiers bas / milieu / haut) :

- tl : 39 % · 21 % · 22 %  (seuils 185 / 275)
- ask : 32 % · 27 % · 23 %  (seuils 0.25 / 0.34)
- fair : 26 % · 31 % · 25 %  (seuils 0.388 / 0.481)
- edge : 24 % · 24 % · 34 %  (seuils 0.11 / 0.134)
- taille : 24 % · 25 % · 33 %  (seuils 183 / 782)
- spread : 28 % · — · 11 %  (seuils 0.01 / 0.01)
- v3 : 21 % · 25 % · 36 %  (seuils 0 / 0.0675)
- perp3 : 40 % · 20 % · 25 %  (seuils -0.566 / 0)
- perp5 : 41 % · 20 % · 22 %  (seuils -0.715 / 0)
- okx3 : 38 % · 24 % · 14 %  (seuils -0.345 / 0)
- cb3 : 35 % · 23 % · 25 %  (seuils -0.547 / 0)
- bn3 : 40 % · 23 % · 9 %  (seuils -0.398 / 0)
- mkt5 : 40 % · 21 % · 20 %  (seuils -0.09 / 0)

Forme du repricing (part des desaccords qui atteignent la cible dans le delai, au meilleur acheteur executable) :

| Cible | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|
| +5c | 16 % | 27 % | 46 % | 54 % |
| +10c | 6 % | 12 % | 29 % | 39 % |
| +25% | 12 % | 22 % | 39 % | 48 % |
| +50% | 5 % | 10 % | 23 % | 31 % |
| x2 | 2 % | 3 % | 8 % | 13 % |

Morts (le meilleur acheteur ne depasse jamais entree + 1 c) : 5 s 71 % · 15 s 54 % · 30 s 42 % · 60 s 36 %

Les morts a 5 s finissent-ils perdants ? 258 trades morts a 5 s : 22 % gagnent quand meme, resultat -3334 $

| Abandon precoce (revendre si rien n'a bouge apres k s) | 1re moitie | **2e moitie** |
|---|---|---|
| jamais (garder) | -1201 $ | **-618 $** |
| abandon a 3 s | -851 $ | **-982 $** |
| abandon a 5 s | -682 $ | **-956 $** |
| abandon a 10 s | -776 $ | **-390 $** |

### 2e moitie (jamais vue) — routeur

| Regle | Trades | Resultat |
|---|---|---|
| tout acheter, garder | 179 | -618 $ |
| ecarter si P(mort) >= 0.5 , garder | 147 | -888 $ |
| ecarter si P(mort) >= 0.6 , garder | 155 | -1158 $ |
| ecarter si P(mort) >= 0.7 , garder | 164 | -824 $ |
| routeur (garder si P(gain) >= 0.35 et > prix ; sinon revendre +50 % si P(mvt) >= 0.5) | 87 | -421 $ |
| routeur (garder si P(gain) >= 0.4 et > prix ; sinon revendre +50 % si P(mvt) >= 0.55) | 69 | -464 $ |
| routeur (garder si P(gain) >= 0.3 et > prix ; sinon revendre +50 % si P(mvt) >= 0.6) | 61 | -537 $ |

Variables les plus utilisees pour reconnaitre un « mort a l'arrivee » : edge 188 · taille 179 · tl 154 · fair 76 · ask 70 · perp3 69 · mkt5 55 · bn3 49

## ETH — 349 desaccords (ecart >= 0,10)

- Mouvement +50 % atteint : **50 %** · gagnant a la fin : 29 % · **mort a l'arrivee : 25 %**
- Tous, garder jusqu'a la fin : 1re moitie -1013 $ (176) · 2e moitie +544 $ (173)
- Tous, revendre a +50 % (sinon garder) : 1re moitie -2089 $ (176) · 2e moitie -409 $ (173)

Taux de « mort a l'arrivee » selon chaque variable (tiers bas / milieu / haut) :

- tl : 37 % · 19 % · 19 %  (seuils 182 / 272)
- ask : 38 % · 20 % · 17 %  (seuils 0.25 / 0.35)
- fair : 37 % · 22 % · 18 %  (seuils 0.392 / 0.475)
- edge : 28 % · 23 % · 25 %  (seuils 0.11 / 0.13)
- taille : 26 % · 16 % · 33 %  (seuils 35 / 94)
- spread : 25 % · — · 31 %  (seuils 0.01 / 0.01)
- v3 : 26 % · 20 % · 30 %  (seuils 0.0189 / 0.0655)
- perp3 : 26 % · 24 % · 31 %  (seuils -0.928 / 0)
- perp5 : 24 % · 25 % · 28 %  (seuils -1.08 / 0)
- okx3 : 29 % · 22 % · 29 %  (seuils -0.729 / 0)
- cb3 : 26 % · 24 % · 27 %  (seuils -0.782 / 0)
- bn3 : 23 % · 25 % · 30 %  (seuils -0.879 / 0)
- mkt5 : 26 % · 28 % · 21 %  (seuils -0.11 / -0.01)

Forme du repricing (part des desaccords qui atteignent la cible dans le delai, au meilleur acheteur executable) :

| Cible | 5 s | 10 s | 30 s | 60 s |
|---|---|---|---|---|
| +5c | 17 % | 26 % | 46 % | 56 % |
| +10c | 7 % | 13 % | 29 % | 40 % |
| +25% | 12 % | 19 % | 37 % | 49 % |
| +50% | 5 % | 9 % | 20 % | 31 % |
| x2 | 2 % | 4 % | 9 % | 15 % |

Morts (le meilleur acheteur ne depasse jamais entree + 1 c) : 5 s 71 % · 15 s 54 % · 30 s 42 % · 60 s 34 %

Les morts a 5 s finissent-ils perdants ? 247 trades morts a 5 s : 22 % gagnent quand meme, resultat -3435 $

| Abandon precoce (revendre si rien n'a bouge apres k s) | 1re moitie | **2e moitie** |
|---|---|---|
| jamais (garder) | -1013 $ | **+544 $** |
| abandon a 3 s | -906 $ | **-110 $** |
| abandon a 5 s | -1060 $ | **+423 $** |
| abandon a 10 s | -1400 $ | **+1179 $** |

### 2e moitie (jamais vue) — routeur

| Regle | Trades | Resultat |
|---|---|---|
| tout acheter, garder | 173 | +544 $ |
| ecarter si P(mort) >= 0.5 , garder | 141 | +1678 $ |
| ecarter si P(mort) >= 0.6 , garder | 155 | +1075 $ |
| ecarter si P(mort) >= 0.7 , garder | 169 | +565 $ |
| routeur (garder si P(gain) >= 0.35 et > prix ; sinon revendre +50 % si P(mvt) >= 0.5) | 76 | -692 $ |
| routeur (garder si P(gain) >= 0.4 et > prix ; sinon revendre +50 % si P(mvt) >= 0.55) | 59 | -252 $ |
| routeur (garder si P(gain) >= 0.3 et > prix ; sinon revendre +50 % si P(mvt) >= 0.6) | 52 | -303 $ |

Variables les plus utilisees pour reconnaitre un « mort a l'arrivee » : taille 176 · tl 165 · edge 135 · mkt5 83 · ask 67 · v3 60 · cb3 54 · fair 47
