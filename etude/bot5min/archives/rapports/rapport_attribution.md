# Bot95 — V2-F 0,01 % : d'où viennent ses gagnants exclusifs ?

> **Verdict**
> 1. **La différence vient bien de la formule**, pas d'un détail de reconstruction :
>    - sur les 47 gagnants exclusifs, 45 disparaissent quand on remet 0,08 % sur exactement les mêmes données ;
>    - 38 sont aussi pris par le moteur du bot lui-même, ramené à 0,01 %.
> 2. **Mais l'avantage tient presque entièrement à la vitesse d'exécution** :
>    - le moteur du bot à 0,01 % fait **+3 794 $** s'il achète à l'instant même du signal ;
>    - +2 089 $ avec 0,25 s de retard ;
>    - **+109 $ avec 0,5 s** ;
>    - **−54 $ avec 1 s**.
>    - Près de la moitié des signaux ne sont plus achetables après 0,5 s : le vendeur est parti ou a monté son prix. Ce sont eux qui portaient le gain (+2 837 $).
> 3. **Selon ta règle :** si notre délai réel d'exécution est de 0,5 s ou plus, **on arrête**. La seule chose qui pourrait sauver V2-F 0,01 % est un délai réel nettement sous 0,5 s. Seul un vrai ordre permettrait de le mesurer, or le test réel de 1 $ est reporté : c'est à toi de décider.

**Données**
- 928 cycles BTC réglés, du 07.10 08:00 au 10.10 13:45, carnets enregistrés 4 fois par seconde.
- Trois périodes :
  - apprentissage : 455 cycles ;
  - validation : 433 cycles ;
  - inédit : 40 cycles (après le 10.10 10:25).
- Aucun filtre n'a été construit : c'est un diagnostic seulement.

## 1. Quatre versions de la même règle V2-F

Toutes appliquent exactement la même règle :
- écart ≥ 0,20 entre la probabilité du modèle et le prix vendeur ;
- écart qui a grandi d'au moins 3 c en 3 s ;
- vendeur entre 0,03 et 0,97 ;
- premier signal du cycle.

| Version | Ce qu'elle est | Cycles achetés |
|---|---|---|
| O8 | modèle du bot tel qu'enregistré, 0,08 % = V2-F original | 759 |
| X8 | modèle reconstruit par l'étude, 0,08 % | 726 |
| X1 | modèle reconstruit, 0,01 % = la « V2-F 0,01 % » du META-ROUTER | 497 |
| H1 | modèle du bot, avec sa propre distance au prix d'exercice, seule l'incertitude passe à 0,01 % = ce que calcule le fantôme réel | 509 |

**Comment lire les comparaisons**
- **X1 contre X8 :** effet de la formule seule, sur des données identiques.
- **X8 contre O8 :** effet du détail de reconstruction.
- **H1 contre O8 :** effet de la formule dans le moteur du bot.

**Contrôle :** X1 refait exactement les signaux de la « V2-F 0,01 % » du META-ROUTER, sur les 928 cycles.

**La reconstruction est fidèle**
- O8 et X8 prennent 722 cycles en commun.
- Dans 712 de ces cycles, ils achètent le même côté.

## 2. Les 47 gagnants exclusifs : formule ou détail ?

| Origine | Cycles | Gain | Aussi pris par H1 (moteur du bot à 0,01 %) | V2-F original achète aussi ce cycle |
|---|---|---|---|---|
| **X8 (0,08 %) achète le côté OPPOSÉ** dans ce cycle | 34 | +989 $ | 29 | 34 (et perd) |
| **X8 ne déclenche pas du tout** dans ce cycle | 11 | +211 $ | 8 | 0 |
| X8 prend le même signal (détail de reconstruction) | 2 | +195 $ | 1 | 2 |

**Explication**
- À 0,01 %, le modèle est beaucoup plus tranché quand le prix est loin du prix d'exercice. L'écart dépasse donc 0,20 sur un côté à un autre moment, souvent avant l'autre version.
- Dans 34 cycles, la version 0,08 % est partie du mauvais côté, et V2-F original aussi : il a perdu ces 34 cycles.
- À données identiques, la formule ne crée que 17 cycles nouveaux (X1 seul).
  - Dans 16 d'entre eux, l'écart à 0,08 % n'atteignait pas 0,20.
  - Profil médian de ces 17 cycles :
    - probabilité 0,70 à 0,01 % contre 0,61 à 0,08 % ;
    - prix payé 0,48 ;
    - 154 s restantes.
- **Ce qu'elle fait surtout :** elle **retire** 246 cycles que la version 0,08 % prenait (souvent perdants), et elle **change le côté ou le moment** dans les cycles communs.

## 3. L'exécution réaliste change tout

Achat au seul meilleur vendeur, dans la quantité affichée, sur le carnet du moment de l'exécution. On ne paie jamais plus cher que le prix vu à la décision : si le prix a monté, il n'y a pas d'achat.

**Toutes périodes**

| Version | Délai 0 s | 0,25 s | 0,5 s | 1 s | 2 s |
|---|---|---|---|---|---|
| O8 V2-F original | −969 $ | −1 895 $ | −2 460 $ | −2 368 $ | −2 095 $ |
| X8 reconstruit 0,08 % | −1 152 $ | −846 $ | −472 $ | +316 $ | +2 $ |
| X1 reconstruit 0,01 % | **+3 798 $** | +771 $ | −413 $ | −434 $ | −986 $ |
| **H1 moteur du bot à 0,01 %** | **+3 794 $** | +2 089 $ | **+109 $** | **−54 $** | −378 $ |

**Pourquoi le retard coûte autant**

| Version | Délai | Signaux | Encore achetables | Achats perdus (le prix a monté) : ce qu'ils rapportaient | dont gagnants |
|---|---|---|---|---|---|
| H1 | 0,25 s | 507 | 304 | +1 156 $ (203 achats) | 85 |
| H1 | 0,5 s | 507 | 268 | **+2 837 $** (239 achats) | 106 |
| H1 | 1 s | 507 | 223 | +3 070 $ (284 achats) | 124 |
| O8 | 0,5 s | 758 | 508 | +900 $ (250 achats) | 69 |

**Ce que ça veut dire**
- **Le gain de la version 0,01 % vient de vendeurs « en retard » qui disparaissent en moins d'une demi-seconde.** C'est une course de vitesse : quelqu'un d'autre les prend, ou ils sont retirés.
- Les achats encore possibles après 0,5 s ne rapportent presque rien.
- C'est cohérent avec une mesure faite plus tôt : Polymarket bouge 2 à 3 s avant nos flux de prix.

**Par période, moteur du bot à 0,01 % (H1)**

| Période | 0 s | 0,25 s | 0,5 s | 1 s |
|---|---|---|---|---|
| apprentissage | +2 350 $ | +1 619 $ | +262 $ | +574 $ |
| validation | +1 889 $ | +1 030 $ | +412 $ | −325 $ |
| inédit (40 cycles) | **−445 $** | −560 $ | −565 $ | −304 $ |

Sur les 40 cycles inédits, la version du moteur du bot perd même sans aucun délai. La version reconstruite y fait +81 $. L'échantillon est trop petit pour conclure.

## Honnêtement

- **« Délai 0 s » est un idéal.** Le carnet est enregistré 4 fois par seconde, donc « 0 s » veut dire « au moment exact où le modèle et le carnet ont été lus ». Un vrai ordre mettra toujours un certain temps à partir et à être exécuté.
- **Les fantômes achètent tous à 0 s.** Leurs résultats affichés sont donc un plafond, pas une estimation de ce que donnerait l'argent réel.
- **V2-F original perd à tous les délais** dans ce rejeu au meilleur vendeur seul.

## Décision proposée (à toi de trancher)

1. **Ta règle s'applique :** avec 0,5 s ou plus, l'avantage disparaît, donc on arrête de privilégier V2-F 0,01 %.
2. **La seule question encore ouverte : quel est notre vrai délai ?**
   - S'il est sous 0,25 s, il reste un avantage à vérifier sur des cycles nouveaux.
   - S'il est au-dessus de 0,5 s, il n'y a plus rien.
   - Seul un vrai ordre peut le mesurer. Le test réel de 1 $ est reporté : la décision est la tienne.
3. **Le fantôme « V2-F incertitude 0,01 % » continue de tourner sans changement.** Le verdict de mardi donnera ses chiffres prospectifs. Si tu le souhaites, je peux y ajouter le même tableau des délais.
