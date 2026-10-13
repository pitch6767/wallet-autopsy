# Bot95 — H1052 : sorties sur les gagnantes du jour, après-midi du 12.10 (13.10.2026)

- **Préenregistrement :** étude séparée, commit 3681242.
- **Stratégies :** les 10 meilleures stratégies BTC du bot Cloudflare le 12.10. Elles ont été choisies parce qu'elles gagnaient ; leur résultat « conserver » est donc flatté. **Seul l'écart avec conserver compte.**
- **Période :** cycles du 12.10 de 12:00 à 24:00 UTC, calculés une seule fois.
- **Mise :** normalisée à 10 $, exécution preneur à 164 ms.
- Aucun ordre réel.

Détail : https://github.com/pitch6767/wallet-autopsy/blob/main/etude/bot5min/resultat_gagnantes_jour_h1052_apres_midi.md

## Total des 10 stratégies (565 trades, 64 jackpots ≥ 40 $)

| Règle | P&L | Gagnants | Jackpots gardés | Écart avec conserver | IC 90 % |
|---|---|---|---|---|---|
| **Conserver** | **+2 170 $** | 121 | 64 / 64 | — | — |
| Verrou 0 $ dès +10 $ | +1 055 $ | 156 | 64 / 64 | −1 115 $ | [−2 388 ; −30] |
| Verrou 0 $ dès +5 $ | +858 $ | 156 | 33 / 64 | −1 313 $ | [−3 102 ; +219] |
| Marge Chainlink | +783 $ | 127 | 22 / 64 | −1 387 $ | [−3 712 ; +516] |
| Prise de gain ×5 | +533 $ | 132 | 54 / 64 | −1 637 $ | [−3 904 ; −42] |
| Trailing 30 % | +399 $ | 250 | 22 / 64 | −1 772 $ | [−4 283 ; +410] |
| Prise de gain ×2 | +263 $ | 192 | 12 / 64 | −1 907 $ | [−4 141 ; +118] |
| Trailing du billet | −5 $ | 166 | 29 / 64 | −2 175 $ | [−4 682 ; −94] |

**Chaque règle de sortie détruit entre la moitié et la totalité du gain.** Elles font plus de gagnants (jusqu'à 250 contre 121) mais de plus petits : on vend les billets qui seraient devenus des jackpots.

## Par stratégie

Conserver est meilleur pour 9 des 10 stratégies.

L'exception est « désaccord 20 Binance ou perp avec nous » :
- c'est la seule stratégie perdante l'après-midi (−104 $) ;
- elle n'a eu aucun jackpot ;
- toutes les sorties l'améliorent, de +35 à +109 $ ;
- la marge Chainlink fait +86 $ (IC corrigé [+40 ; +158]) et le trailing du billet +65 $ (IC corrigé [+10 ; +143]).

**Mais ce n'est qu'une stratégie sur dix, choisie après coup. Ce n'est pas un résultat démontré.**

## Conclusion

1. Sur les stratégies qui gagnent, **les gains viennent des jackpots**. Il ne faut pas les couper.
2. Pour réduire les perdantes, la bonne piste reste le **filtre à l'entrée** (consensus K5 et suivants, en fantôme depuis le 12.10), pas la sortie.
3. Avec le matin, déjà calculé : même conclusion sur les deux demi-journées.
