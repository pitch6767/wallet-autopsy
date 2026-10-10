# BOT95 V3 — Expérience 006 : routeur (une seule règle simple, pré-enregistrée)

928 cycles BTC 5 min réglés (07.10 08:00 → 10.10 13:45, heure suisse). Apprentissage 455 cycles (< 08.10 22:00) · validation 433 (→ 10.10 10:25) · test inédit 40 cycles seulement (après 10.10 10:25) — le test est minuscule, aucun verdict ne peut s'y appuyer seul.

Rappel de l'étude précédente (`resultat_meta_router.md`) : hors apprentissage, R1 (choix par volatilité × tendance) − R0 (fixe) = −1 027 $ [−2 658 ; +536], R2 − R0 = −1 236 $ [−2 712 ; +215] : le routage dynamique perdait contre la meilleure stratégie fixe.

Exécution : délai 0,5 s demandé (~0,6 s réel), meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, frais, 50 $ max.

## Choix de R0 sur l'apprentissage seulement

| Stratégie | Résultat d'apprentissage (délai 0,5 s) |
|---|---|
| désaccord 20 60-180 s ← R0 | +1 884 $ |
| désaccord 30 | +1 805 $ |
| V2-D perp 120-269 s | +1 649 $ |
| V2-F original (O8) | +424 $ |
| V2-F 0,01 % (H1) | +262 $ |
| désaccord 20 jeton 0,35-0,65 | −60 $ |
| V2-G jury des bourses | −528 $ |

## Cases interdites par la règle (R0 = désaccord 20 60-180 s, seuil de volatilité = médiane d'apprentissage 4,18 $/s)

| Case | Achats app. | Espérance app. | Interdite |
|---|---|---|---|
| vol. basse · jour | 57 | +38,38 $ | non |
| vol. basse · nuit | 53 | −4,22 $ | oui |
| vol. haute · jour | 78 | +1,22 $ | non |
| vol. haute · nuit | 21 | −5,81 $ | oui |
| vol. inconnue · jour | 1 | −52,92 $ | non |

## Résultats

**apprentissage**

| Politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 fixe : désaccord 20 60-180 s | 210 | 20 % | **+1 884 $** | +8,97 $ | +938 $ | −206 $ | −1 099 $ | −2 831 $ | −1 003 $ | 1,28 | [−1 141 $ ; +5 115 $] |
| R* : R0 sauf cases interdites | 136 | 24 % | **+2 230 $** | +16,40 $ | +1 283 $ | +265 $ | −500 $ | −1 948 $ | −957 $ | 1,53 | [−352 $ ; +5 230 $] |

**validation**

| Politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 fixe : désaccord 20 60-180 s | 297 | 20 % | **+1 316 $** | +4,43 $ | +745 $ | −300 $ | −1 304 $ | −3 106 $ | −1 091 $ | 1,14 | [−1 979 $ ; +4 830 $] |
| R* : R0 sauf cases interdites | 121 | 17 % | **−1 332 $** | −11,01 $ | −1 676 $ | −2 249 $ | −2 656 $ | −3 479 $ | −1 724 $ | 0,69 | [−2 926 $ ; +310 $] |

**inédit**

| Politique | Achats | Gagnés | Résultat net | Espérance / achat | sans top 1 | sans top 3 | sans top 5 | sans top 10 | Creux max | Facteur de profit | IC 90 % (blocs 1 h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R0 fixe : désaccord 20 60-180 s | 29 | 14 % | **−251 $** | −8,66 $ | −492 $ | −740 $ | −836 $ | −809 $ | −280 $ | 0,70 | [−478 $ ; −64 $] |
| R* : R0 sauf cases interdites | 29 | 14 % | **−251 $** | −8,66 $ | −492 $ | −740 $ | −836 $ | −809 $ | −280 $ | 0,70 | [−478 $ ; −64 $] |

## R* bat-il R0 ? (différence, intervalle à 90 % par blocs d'une heure)

| Période | Différence R* − R0 | IC 90 % | Probabilité ≤ 0 |
|---|---|---|---|
| validation | −2 648 $ | [−5 801 $ ; +73 $] | 95 % |
| inédit | +0 $ | [+0 $ ; +0 $] | 100 % |
| validation + inédit | −2 648 $ | [−5 683 $ ; +48 $] | 94 % |

Inédit : les 40 cycles inédits sont tous de jour (10.10 10:25 → 13:45) ; aucune case interdite n'y tombe, R* = R0 à l'identique (différence nulle, la « probabilité ≤ 0 » de 100 % n'a pas de sens ici).

Si l'intervalle contient 0, la nouvelle règle ne change pas le verdict de l'étude META-ROUTER : pas de preuve qu'un routage par régime bat une stratégie fixe. L'expérience 005 (stabilité des régimes) explique pourquoi : les écarts entre régimes ne se répètent pas de l'apprentissage à la validation.
