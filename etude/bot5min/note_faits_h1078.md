# Bot95 — H1078 : faits utiles (14.10.2026, nuit)

1. **Accord entre stratégies** : en comptant toutes les stratégies du cycle, « aucune stratégie en face » semblait énorme (−58 % / −73 % contre +98 % / +195 %).
   C'était un PIÈGE : le compte incluait des trades faits APRÈS le nôtre. En ne comptant que les trades d'avant, plus rien de stable
   (premier du cycle, déjà une stratégie en face, ≥ 5 ou ≥ 15 déjà du même côté : signes qui changent selon les périodes). Abandon.
2. **Glissement de prix et taille** : payer au meilleur vendeur ou les petites mises (≤ 30 $) ne donnent rien de stable.
3. **Chiffres US à 14 h 30 (heure suisse)** : fenêtres 14:25–14:45 des jours ouvrés, 06–12.10 : 151 trades, −840 $ (−17 %) contre −3 % ailleurs ;
   le 09.10 (inscriptions au chômage) −2 368 $, le 12.10 (aucune publication) +1 914 $. Trop peu pour conclure, mais **l'inflation US (CPI) sort aujourd'hui
   14.10 à 14 h 30** : les résultats de cette fenêtre seront à lire à part.
4. **Téléchargement des 27 jours** : les morceaux de 7 jours tombaient en panne (mémoire du serveur GitHub) ; le script écrit maintenant chaque jour
   dès qu'il est fini, et les jours manquants sont relancés par morceaux de 3–4 jours.

5. **Sorties anticipées** (trades du bot, carnet Dublin) : vendre quand le prix a fait ×1,5, ×2 ou ×3, ou couper à −50 %, ne fait pas mieux
   que garder jusqu'au règlement de façon stable (billets ≤ 0,25 : garder −4 322 / +12 022 / +3 282 $ ; ×2 : −6 978 / +5 716 / −642 $). On garde.
6. **Temps restant à l'achat** : 120–180 s restantes positif dans les 3 périodes (+9 % / +67 % / +45 %) ; 60–120 s négatif en validation et test
   (+10 % / −28 % / −20 %) ; le reste varie. Piste seulement.

7. **Les stratégies « en forme » le restent-elles ?** Corrélation de rang entre blocs successifs (3, 6, 12, 24 h) : +0,11 / −0,05 / +0,10 / +0,14 ;
   le quart du haut bat le quart du bas au bloc suivant dans 42 à 62 % des cas seulement. Le classement est utile pour voir, faible pour prévoir.
8. **Diversification** : 97 stratégies BTC ≈ 13 paris indépendants (corrélation moyenne 0,11 ; 1er facteur 20 %).
9. **Les pertes viennent de quelques cycles** : sur 1 300 cycles (06–12.10), les 10 pires = −16 624 $ sur −29 839 $ de perte totale.
   Dans ces cycles, 29 à 43 stratégies achètent le même billet (0,18–0,36) et presque toutes perdent, souvent dans un marché calme (BTC bouge de 10 à 50 $).
   Les paquets de plus de 30 trades sur le même côté d'un cycle : −37 % (06–10.10) et −30 % (11–12.10). Mais ce nombre n'est connu qu'après coup ;
   « ne pas suivre quand ≥ 15 stratégies ont déjà acheté » n'est pas stable (pire le 06–10, mieux le 11–12). Pour l'argent réel : plafonner la mise
   totale par cycle, toutes stratégies confondues.

10. **Portefeuilles sur 9 jours** (03–06.10 pour classer, 07–11.10 pour vérifier ; 1 596 portefeuilles actifs ≥ 50 cycles dans chaque moitié) :
    corrélation des ROI 0,07. Les 20 % meilleurs : +11 % → +1,4 % ; les 20 % pires : −9,7 % → −2,0 %. Le talent ne persiste presque pas ;
    les mauvais restent un peu mauvais (cohérent avec le fantôme « anti-bête »). Copier les meilleurs : non.
11. **« Contre la foule » tout seul sur 9 jours** (flux des preneurs 30 s, achat à la première transaction suivante) : rien de stable selon le prix
    et la moitié (ex. billets 0,05–0,35 avec flux fort contre eux : +9 % puis −14 %). Comme le carnet, ça ne marche qu'en filtre d'un signal.
