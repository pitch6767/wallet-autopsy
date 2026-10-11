# Bot95 — Chercher encore : qui nous vend nos billets, preneurs en miroir, favori (PRÉLIMINAIRE)

595 marchés complets (tronqués exclus — biais possible : ce sont les plus actifs).

## E1. Qui vend les billets que Bot95 veut acheter ?

Signaux Bot95 réglés sur des marchés lus : 353 ; signaux où au moins un maker a vendu ce côté au prix du signal ou mieux dans les 10 s : 341.

| Vendeur (maker) | Signaux servis | Parts vendues | Résultat global du portefeuille | par $ |
|---|---|---|---|---|
| `0x85a186d1a0be8593bf7eb5d323f96d932bc991b9` | 141 | 1778 | -1761 $ | -1.5 % |
| `0x18c18e0c8c3154360b4f730ec8b9d8013ceb2183` | 133 | 2704 | +1856 $ | +1.2 % |
| `0x322b2e7c44237c9fed01d534cd1c96687d52aa0c` | 133 | 1748 | -1478 $ | -1.1 % |
| `0xf9b7876ba2c35370e0bedb7f8ee772da722aa37c` | 133 | 2251 | +1209 $ | +0.8 % |
| `0x41e2e1ccf1e4940029af02259a31c6b89b9fa354` | 125 | 3734 | +8722 $ | +1.4 % |
| `0x4c9497941333332d29f1c235dd23200f3623ffad` | 123 | 1940 | +1781 $ | +1.4 % |
| `0x568b079891fcc8bef2e557fa2a8a7ecca1700b3b` | 122 | 1839 | +1279 $ | +1.1 % |
| `0x809f275254e21f720a4e6c50c28c669c721f2ef0` | 110 | 1236 | +195 $ | +0.3 % |
| `0xaa1a4f31c010d4a63fc49770d4ca2d69ea370602` | 110 | 2943 | -3389 $ | -1.4 % |
| `0x32c4922da31d9f90232ea40748846e5ccc48b175` | 107 | 1235 | -42 $ | -0.1 % |
| `0xa3338de30e72494d609f586e1e41c11a0a9a29c8` | 105 | 1212 | +174 $ | +0.4 % |
| `0x1dd2a69e73ba444ecd5d87f0073d51a670ad51c2` | 97 | 1011 | +24 $ | +0.0 % |
| `0x5916ce250c0b3e32eed3303ffb2938cab0b42a0b` | 90 | 969 | +512 $ | +1.2 % |
| `0x373b2d17d78c27bbdbcb034dae71d26b8094c855` | 85 | 1018 | +206 $ | +0.5 % |
| `0x86b14772a4da70f3e6d5eee06933ebef143efc87` | 84 | 11630 | -3284 $ | -0.6 % |

Signaux servis par des makers : gagnés 34 % (prix moyen 0.23) ; signaux NON servis : gagnés 33 % (prix moyen 0.17).

## E2. Les preneurs en miroir

| Découpage | Tranche | Exécutions | Résultat net de frais par $ |
|---|---|---|---|
| minute | 0–60 s | 156490 | -2.6 % |
| minute | 60–120 s | 134950 | -0.0 % |
| minute | 120–180 s | 140020 | -2.9 % |
| minute | 180–240 s | 160430 | +0.9 % |
| minute | 240–300 s | 123816 | -1.2 % |
| prix | 0.0–0.1 | 55822 | -4.4 % |
| prix | 0.1–0.2 | 48281 | -4.4 % |
| prix | 0.2–0.3 | 58526 | -4.1 % |
| prix | 0.3–0.4 | 59180 | -4.7 % |
| prix | 0.4–0.5 | 59240 | -3.9 % |
| prix | 0.5–0.6 | 69342 | +0.4 % |
| prix | 0.6–0.7 | 71650 | +1.8 % |
| prix | 0.7–0.8 | 68537 | -1.5 % |
| prix | 0.8–0.9 | 78033 | -1.3 % |
| prix | 0.9–1.0 | 147095 | -0.3 % |
| taille | < 10 $ | 555626 | -1.8 % |
| taille | 10–50 $ | 122218 | -1.2 % |
| taille | 50–200 $ | 32945 | -1.1 % |
| taille | ≥ 200 $ | 4917 | -0.1 % |

## E3. L'effet favori : élan ou biais permanent ?

| Côté acheté (maker) | Prix du côté sur les 30 s précédentes | Remplissages | Résultat par $ |
|---|---|---|---|
| favori | a baissé | 103473 | -2.6 % |
| favori | a monté | 466248 | +0.2 % |
| favori | stable | 110302 | +0.7 % |
| outsider | a baissé | 565025 | -2.9 % |
| outsider | a monté | 131791 | -3.6 % |
| outsider | stable | 134692 | -4.0 % |

Lecture : si le favori gagne surtout quand son prix vient de monter, c'est de l'ÉLAN (le marché sous-réagit) ; s'il gagne même stable, c'est un biais favori / outsider (les outsiders sont trop chers).

## Limites
- Une journée ; marchés les plus actifs exclus (tronqués) — à refaire sur les données complètes.
