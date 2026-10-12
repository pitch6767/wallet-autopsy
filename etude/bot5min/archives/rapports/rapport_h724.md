# Bot95 — Counterparty Intelligence Lab H724–H765 — rapport préliminaire du 11.10.2026

Hors ligne uniquement. Aucun ordre réel, aucun bot ni fantôme modifié, aucune nouvelle stratégie lancée. Période réservée (≥ 13.10) non lue. Les transactions postérieures au signal ne servent jamais de variable « avant signal ».

**Données :** 161 signaux Bot95 réglés sur 212 marchés complets, soit **37 cycles seulement**. Les 88 marchés tronqués sont exclus. Les intervalles de confiance rééchantillonnent des cycles. Séparation chronologique : 18 cycles d'apprentissage, 19 de test. Le carnet Dublin couvre 16 cycles pour le test Reverse. Tout reste **PRÉLIMINAIRE** et sera refait sur la collecte complète, en cours.

## Décisions demandées

| Question | Réponse | Niveau de preuve |
|---|---|---|
| A. Avantage directionnel observable ? | **Non** face à Bot95. Les billets qu'ils nous « vendent » rapportent +0,6 % par $ à l'acheteur, ce qui est équitable. À prix et minute égaux, ils ne vendent pas plus mal que les autres makers : +0,4 point, IC [−2,0 ; +2,8]. | moyen |
| B. D'où vient leur rentabilité ? | Pas des ventes : ils **ne vendent jamais** (0 vente sur 162 000 parts). Leurs paires Up+Down coûtent 1,048 $ et perdent environ 930 $ chacun. Tout le gain vient des **jambes résiduelles** (+2 300 à +2 900 $), donc de la gestion d'inventaire et de l'acquisition. | fort (fait) pour la structure, faible pour la cause |
| C. Leurs transactions avant le signal annoncent-elles nos pertes ? | **Non démontré.** Sur 60, 30 et 10 s : rien. Sur 3 et 1 s : écart négatif, mais le placebo atteint ce niveau 11–12 % du temps. Ces fenêtres ne sont probablement pas disponibles en direct, car l'identité arrive avec retard. | faible |
| D. L'identité apporte-t-elle plus que le flux global ? | **Non.** La log loss de test se dégrade (0,4927 → 0,5199) et 52 % des placebos font aussi bien ou mieux. | moyen |
| E. Une stratégie exploitant cette info améliore-t-elle le P&L après coûts ? | **Non.** Aucun veto ni aucune confirmation n'est significatif, et tous sont négatifs ou nuls sur le test. Reverse Bot95 perd −0,09 $ par part. | moyen |

**Conclusion, conformément à la règle fixée :** la piste « identité des wallets comme signal de trading » est **à abandonner**. Il ne reste qu'un indice faible sur 1–3 s, à revérifier sur données complètes seulement si l'identité s'avère disponible à temps.

## Ce qu'on a vraiment appris (faits)

1. **Comment ils « vendent » nos billets.** Les trois wallets sont des **acheteurs purs des deux côtés** : 100 % d'achats, 0 vente. Quand Bot95 veut acheter Up à 0,20, la contrepartie est leur offre d'achat de Down à 0,80. Le carnet crée une paire neuve (mint). Ce n'est donc ni une sortie d'inventaire ni une prise de profit : c'est **un pari passif sur le favori**.
2. **Test A (157 correspondances).**
   - 127 des 161 signaux n'ont de correspondance qu'après la seconde du signal : c'est de la description, pas une prédiction.
   - 14 signaux voient l'offre servie dans la seconde d'avant, par un autre preneur.
   - Encore achetables 250 ms après la décision : 127 signaux sur 161.
3. **Fait nouveau et important : on perd les bons signaux à la latence.**
   - Signaux encore achetables à 250 ms : 22 % de gains.
   - Signaux partis avant 250 ms : **44 % de gains**.
   - Les gagnants sont pris avant nous. Une fois exécutable, Bot95 A ≈ 0 : +0,003 $ par part, IC [−0,10 ; +0,10].
4. **Empreinte « même opérateur ».** Leurs profils sont presque identiques :
   - 100 % d'achats ;
   - taille médiane de 8 à 9 parts, dont 42–44 % de tailles rondes ;
   - prix médian 0,61–0,62 ;
   - 50/50 Up/Down ;
   - présents sur 99–100 % des mêmes marchés ;
   - actifs dans la même seconde 6 à 7 fois plus souvent que le hasard naïf.

   Mais un seul gros preneur remplit plusieurs acheteurs dans la même seconde, et ce point de comparaison au hasard est trop simple. **Similarité statistique, contrôle commun NON démontré.** Les transferts n'ont pas été vérifiés : les activités sont en collecte.

## Test E — Reverse Bot95 (1 part par signal, frais et 250 ms inclus)

| Politique | Exécutés | P&L par signal (IC 90 %) | par $ | Taux de gain | Drawdown max | Pire série |
|---|---|---|---|---|---|---|
| A — côté Bot95 | 127 | +0,003 [−0,096 ; +0,095] | +1,4 % | 22 % | 4,37 | 21 pertes |
| B — côté opposé | 77 | −0,093 [−0,228 ; +0,047] | −12,1 % | 69 % | 8,46 | 6 |
| A sur le test | 49 | −0,015 | −6,8 % | 20 % | 4,21 | 15 |
| B sur le test | 49 | −0,018 | −2,2 % | 80 % | 4,33 | 5 |
| C — rien | 0 | 0 | — | — | 0 | 0 |

## Test F — Veto et confirmation (règles fixées a priori)

- Aucun filtre « 3 wallets » n'a un P&L marginal significatif : les IC vont d'environ −12 à +12 parts.
- Le meilleur filtre global, le veto « tous les makers 30 s », donne +2,7 parts, IC [−0,8 ; +6,2], mais il est négatif sur le test.
- Avec un délai de disponibilité de 2 ou 5 s, le résultat reste nul.

## Trois mécanismes classés par niveau de preuve

1. **Fort :** acheteurs passifs des deux côtés. Notre billet est leur achat de l'autre côté, par mint.
2. **Moyen :** leur profit vient des jambes résiduelles et non des paires, qui coûtent plus de 1 $. Cause encore inconnue : choix du favori, sélection du flux preneur, ou biais des marchés tronqués. À refaire sur données complètes.
3. **Faible :** le flux des 1–3 s précédentes précède les erreurs de Bot95. Ce n'est pas significatif face au placebo (11–12 %), c'est probablement indisponible en direct, et sans doute dû au flux preneur anonyme plutôt qu'à l'identité.

## Trois fantômes candidats (NON lancés, ta décision)

1. **R1 « garde latence » (observation seule, sans ordre fictif nouveau).** Pour chaque signal Bot95, enregistrer la quantité encore présente à 50, 100, 150 et 250 ms. Mesurer en direct si les signaux qui disparaissent gagnent plus (constat 44 % contre 22 %). Coût nul.
2. **R2 « double achat façon trio ».**
   - Acheteur passif des deux côtés au meilleur acheteur, 9 parts.
   - Uniquement si le prix médian est entre 0,50 et 0,75 et entre 60 et 240 s du cycle.
   - Conservé jusqu'au règlement.
   - Recouvre largement M21 : je déconseille de le lancer avant le verdict M21.
3. **R3 « veto flux preneur 3 s » (anonyme, disponible en direct).** Ne pas acheter le signal Bot95 si les preneurs ont acheté net notre côté dans les 3 s précédentes. Indice faible, à tester seulement sur une période inédite.

**Ma recommandation :** abandonner l'identité des wallets comme signal. Garder éventuellement R1 (mesure pure). Ne pas lancer R2 ni R3 avant les données complètes.

Détail complet : etude/bot5min/resultat_contreparties_h724.md (tableau des 161 signaux en annexe).
