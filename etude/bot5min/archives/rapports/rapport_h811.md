# Bot95 — H811 à H815 : vérifier si annuler plus vite sauve le maker — 11.10.2026

Étude hors ligne. Aucun ordre. Aucun bot ni fantôme modifié. Aucun nouveau fantôme. La période réservée n'a pas été lue.

**Base de test : les mêmes cotations que H807.**
- 13 955 cotations, sur 82 cycles enregistrés à Dublin.
- Chaque cotation : 20 $ au meilleur acheteur, gardée 5 s, latence 14 ms.
- Les fills sont simulés selon trois hypothèses de file : prudente, centrale et optimiste.

**Avertissements, fixés à l'avance et observés à Dublin avant le fill :**
- **W1** : une transaction vendeuse consomme notre côté du carnet, à notre prix ou mieux.
- **W2** : le meilleur vendeur de notre côté baisse.
- **W3** : Binance bouge d'au moins 1 point de base contre nous en 300 ms.
- **W** : le premier des trois qui se déclenche.

**Définitions :**
- **Délai d** : temps entre l'avertissement et l'annulation effective chez Polymarket. Le trajet simple Dublin → Polymarket prend environ 14 ms, donc d = 10 ms est physiquement impossible.
- **Fill toxique** : 5 s après le fill, le prix moyen entre acheteur et vendeur est au moins 1 c sous notre prix.
- **Bon fill** : ce prix moyen est au-dessus ou égal à notre prix.

## 1. H811 — Combien de temps avant le fill arrive l'avertissement ? (file centrale)

On compte 8 770 cotations remplies : 4 212 fills toxiques et 3 397 bons fills.

| Avertissement | Fills toxiques précédés d'un avertissement | Délai médian avertissement → fill (p10 / p90) | Bons fills précédés d'un avertissement |
|---|---|---|---|
| W | **93 %** | 823 ms (65 / 3 041) | **89 %** |
| W1 | 79 % | 1 033 ms | 78 % |
| W2 | 60 % | 155 ms (13 / 1 101) | 43 % |
| W3 (Binance) | 1 % | 181 ms | 0 % |

**Fait clé :** les avertissements arrivent presque aussi souvent avant les bons fills qu'avant les mauvais. Ils ne distinguent pas les deux. Le seul avertissement sélectif est W3 (Binance), mais il est très rare (45 cas).

## 2. H814 — Quelle part des fills toxiques peut-on vraiment éviter ?

| Délai d | Fills toxiques évitables | Avertissement trop tard | Aucun avertissement | Bons fills perdus |
|---|---|---|---|---|
| 10 ms (impossible) | 91 % | 2 % | 7 % | 88 % |
| 25 ms | 88 % | 5 % | 7 % | 86 % |
| 50 ms | 85 % | 8 % | 7 % | 83 % |
| 100 ms | 81 % | 12 % | 7 % | 80 % |
| 200 ms | 75 % | 18 % | 7 % | 75 % |

Annuler sur avertissement évite 75 à 91 % des fills toxiques. Mais cela fait perdre **autant de bons fills** (75 à 88 %).

## 3. H812 / H815 — P&L net : garder ou annuler ? (tous les cycles)

| Politique | File prudente : P&L par cotation (IC 90 %) | File centrale |
|---|---|---|
| Garder | −0,75 $ [−1,46 ; −0,05] | −0,69 $ [−1,51 ; +0,16] |
| Annuler sur W à 25 ms | −0,03 $ [−0,07 ; +0,02] | −0,04 $ |
| Annuler sur W à 50 ms | −0,05 $ [−0,11 ; +0,02] | −0,05 $ |
| Annuler sur W à 100 ms | −0,04 $ | −0,05 $ |
| Annuler sur W à 200 ms | −0,07 $ | −0,08 $ |
| Annuler sur W3 seul à 50 ms | −0,68 $ (gain marginal +0,07 $ [+0,05 ; +0,10]) | gain marginal +0,07 $ |

**Lecture :**
- Annuler améliore nettement le résultat par rapport à garder (+0,69 à +0,76 $ par cotation en file prudente).
- Mais ce gain vient surtout de **l'abstention** : on ne remplit plus que 286 à 1 500 cotations sur 13 955. Le résultat net reste **≤ 0** à tous les délais réalistes, dans les deux moitiés de la journée.
- Le résultat au markout à 5 s (file centrale) va dans le même sens : −58 c par cotation si l'on garde, −1 à −8 c si l'on annule. Jamais positif.
- La file optimiste rend « annuler » positif (+0,5 $ par cotation), mais c'est l'hypothèse la moins crédible, et l'IC touche 0 sur la 2e moitié.
- W3 (Binance) seul apporte un vrai gain marginal significatif (+7 c par cotation), mais il est trop rare pour rendre le maker rentable.

## 4. H813 — Coût de la perte de priorité

Test : on annule à 50 ms, puis on repose l'ordre 500 ms plus tard, en fin de file, au meilleur prix du moment.

| File | P&L si l'on garde sa place | P&L de l'offre reposée | Coût de la priorité |
|---|---|---|---|
| Prudente | −8 437 $ | −7 439 $ | −998 $ |
| Centrale | −7 445 $ | −7 277 $ | −168 $ |
| Optimiste | −1 813 $ | +3 251 $ | −5 064 $ |

Le coût est négatif : perdre sa place dans la file ne coûte rien ici. L'offre reposée profite d'un prix plus récent, et la place d'origine était surtout exposée aux mauvais fills. **La priorité n'a pas de valeur positive pour nos cotations.**

## 5. Verdict

- **Délai d'annulation maximal économiquement acceptable : aucun.** À aucun délai, même 10 ms (physiquement impossible), le maker ne devient positif avec un IC au-dessus de 0 en file prudente ou centrale.
- Annuler vite réduit les pertes surtout parce qu'on ne remplit presque plus. Les avertissements observables précèdent autant les bons fills que les mauvais.
- **Recommandation : abandonner la piste maker pour Bot95.**
  - Les fantômes maker actuels peuvent continuer à mesurer, sans changement, jusqu'au verdict du 15.10 si tu le souhaites.
  - Aucun nouveau moteur maker n'est proposé.
- Seul résidu intéressant : un mouvement de Binance contre nous est un avertissement rare mais sélectif. Il pourrait servir de **veto pour le preneur** (Bot95 / R4), à tester hors ligne si tu le veux.
