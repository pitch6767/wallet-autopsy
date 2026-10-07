# Chasse aux failles — Polymarket crypto

## C. Remboursements maker sur les 5 min

- BTC : 80 marches, 2726136 parts echangees, frais taker 26075 $ -> remboursement maker ≈ **0.19 cents par part servie** (≈ 0.38 cents par paire Up+Down servie, soit 0.39 % d'une paire a 0,975)
- ETH : 80 marches, 305974 parts echangees, frais taker 3043 $ -> remboursement maker ≈ **0.20 cents par part servie** (≈ 0.40 cents par paire Up+Down servie, soit 0.41 % d'une paire a 0,975)

Champs recompenses/frais d'un marche 5 min (gamma) : `{"marketMakerAddress": "", "orderMinSize": 5, "makerBaseFee": 1000, "takerBaseFee": 1000, "rewardsMinSize": 50, "rewardsMaxSpread": 4.5, "spread": 0.01, "holdingRewardsEnabled": false, "feesEnabled": true, "makerRebatesFeeShareBps": 10000, "feeType": "crypto_fees_v2", "feeSchedule": {"exponent": 1, "rate": 0.07, "takerOnly": true, "rebateRate": 0.2}}`

## A/B. Echelles et fourchettes crypto ouvertes — 2100 evenements, 3 passages a 5 min d'intervalle

Net = gain garanti par dollar de paiement, frais taker 0,072·p·(1−p) compris (hypothese prudente). Positif = faille.

| Type | Evenement | Jambes (meilleur moment) | Cout | Net garanti | Taille dispo (parts) | Passages positifs |
|---|---|---|---|---|---|---|
| echelle | Bitcoin above ___ on October 9? | OUI >92000 a 0.006 + NON >94000 a 0.993 | 0.999 | **+0.000** | 5 | 3/6 |
| echelle | Hyperbeat FDV above ___ one day after launch? | OUI >2e+08 a 0.018 + NON >4e+08 a 0.98 | 0.998 | **-0.001** | 85 | 0/6 |
| echelle | Hurupay FDV above ___ one day after launch? | OUI >2e+07 a 0.042 + NON >3e+07 a 0.953 | 0.995 | **-0.001** | 5 | 0/15 |
| echelle | Ethereum above ___ on October 8? | OUI >3100 a 0.002 + NON >3200 a 0.999 | 1.001 | **-0.001** | 105 | 0/3 |
| echelle | Bitcoin above ___ on October 8? | OUI >92000 a 0.003 + NON >94000 a 0.998 | 1.001 | **-0.001** | 178 | 0/3 |
| echelle | Opensea FDV above ___ one day after launch? | OUI >3e+09 a 0.03 + NON >5e+09 a 0.967 | 0.997 | **-0.001** | 685 | 0/3 |
| echelle | Ethereum above ___ on October 10? | OUI >3000 a 0.005 + NON >3100 a 0.996 | 1.001 | **-0.002** | 5 | 0/6 |
| echelle | Hyperbeat FDV above ___ one day after launch? | OUI >3e+08 a 0.019 + NON >4e+08 a 0.98 | 0.999 | **-0.002** | 98 | 0/3 |
| echelle | Ostium FDV above ___ one day after launch? | OUI >2e+08 a 0.019 + NON >7e+08 a 0.981 | 1.000 | **-0.003** | 60 | 0/21 |
| echelle | Ostium FDV above ___ one day after launch? | OUI >3e+08 a 0.019 + NON >7e+08 a 0.981 | 1.000 | **-0.003** | 60 | 0/18 |
| echelle | Ethereum above ___ on October 9? | OUI >2900 a 0.006 + NON >3200 a 0.996 | 1.002 | **-0.003** | 5 | 0/9 |
| echelle | Ethereum above ___ on October 9? | OUI >3000 a 0.006 + NON >3200 a 0.996 | 1.002 | **-0.003** | 5 | 0/6 |
| echelle | Bitcoin above ___ on October 11? | OUI >94000 a 0.006 + NON >96000 a 0.996 | 1.002 | **-0.003** | 5 | 0/3 |
| echelle | Bitcoin above ___ on October 7? | OUI >88000 a 0.004 + NON >90000 a 0.999 | 1.003 | **-0.003** | 5 | 0/3 |
| echelle | Ethereum above ___ on October 8? | OUI >3000 a 0.004 + NON >3100 a 0.999 | 1.003 | **-0.003** | 202 | 0/6 |
| echelle | Bitcoin above ___ on October 8? | OUI >76000 a 0.99 + NON >78000 a 0.012 | 1.002 | **-0.004** | 10 | 0/27 |
| echelle | Ethereum above ___ on October 10? | OUI >3100 a 0.006 + NON >3200 a 0.997 | 1.003 | **-0.004** | 5 | 0/3 |
| echelle | Ostium FDV above ___ one day after launch? | OUI >5e+08 a 0.02 + NON >7e+08 a 0.981 | 1.001 | **-0.004** | 60 | 0/15 |
| echelle | Ethereum above ___ on October 9? | OUI >3100 a 0.007 + NON >3200 a 0.996 | 1.003 | **-0.004** | 5 | 0/3 |
| echelle | Metamask FDV above ___ one day after launch? | OUI >5e+08 a 0.043 + NON >7e+08 a 0.955 | 0.998 | **-0.004** | 291 | 0/15 |
| echelle | Ethereum above ___ on October 11? | OUI >3000 a 0.006 + NON >3200 a 0.998 | 1.004 | **-0.005** | 5 | 0/6 |
| echelle | Ethereum above ___ on October 8? | OUI >2900 a 0.007 + NON >3000 a 0.997 | 1.004 | **-0.005** | 5 | 0/9 |
| echelle | Ethereum above ___ on October 10? | OUI >2900 a 0.008 + NON >3000 a 0.996 | 1.004 | **-0.005** | 5 | 0/9 |
| echelle | Hyperbeat FDV above ___ one day after launch? | OUI >1e+08 a 0.022 + NON >4e+08 a 0.98 | 1.002 | **-0.005** | 166 | 0/9 |
| echelle | Ventuals FDV above ___ one day after launch? | OUI >5e+08 a 0.017 + NON >8e+08 a 0.986 | 1.003 | **-0.005** | 189 | 0/12 |
| echelle | Ethereum above ___ on October 11? | OUI >3100 a 0.007 + NON >3200 a 0.998 | 1.005 | **-0.006** | 509 | 0/3 |
| echelle | Hurupay FDV above ___ one day after launch? | OUI >5e+07 a 0.027 + NON >1e+08 a 0.975 | 1.002 | **-0.006** | 60 | 0/6 |
| echelle | Bitcoin above ___ on October 10? | OUI >74000 a 0.996 + NON >76000 a 0.009 | 1.005 | **-0.006** | 5 | 0/30 |
| echelle | Bitcoin above ___ on October 12? | OUI >94000 a 0.011 + NON >96000 a 0.994 | 1.005 | **-0.006** | 10 | 0/3 |
| echelle | Bitcoin above ___ on October 10? | OUI >92000 a 0.013 + NON >94000 a 0.992 | 1.005 | **-0.006** | 25 | 0/3 |
| echelle | Ethereum above ___ on October 7? | OUI >2400 a 0.998 + NON >2500 a 0.008 | 1.006 | **-0.007** | 1238 | 0/12 |
| echelle | Hurupay FDV above ___ one day after launch? | OUI >5e+06 a 0.05 + NON >1e+07 a 0.95 | 1.000 | **-0.007** | 665 | 0/21 |
| echelle | Ethereum above ___ on October 9? | OUI >2200 a 0.989 + NON >2300 a 0.016 | 1.005 | **-0.007** | 5 | 0/30 |
| echelle | Printr FDV above ___ one day after launch? | OUI >1e+08 a 0.084 + NON >1.5e+08 a 0.912 | 0.996 | **-0.007** | 11 | 0/21 |
| echelle | Bitcoin above ___ on October 9? | OUI >94000 a 0.008 + NON >96000 a 0.999 | 1.007 | **-0.008** | 935 | 0/3 |
| echelle | Ostium FDV above ___ one day after launch? | OUI >7e+08 a 0.022 + NON >1e+09 a 0.983 | 1.005 | **-0.008** | 23 | 0/12 |
| echelle | StandX FDV above ___ one day after launch? | OUI >2e+09 a 0.03 + NON >5e+09 a 0.974 | 1.004 | **-0.008** | 30 | 0/12 |
| echelle | StandX FDV above ___ one day after launch? | OUI >5e+09 a 0.03 + NON >7e+09 a 0.974 | 1.004 | **-0.008** | 45 | 0/6 |
| echelle | Ethereum above ___ on October 8? | OUI >2300 a 0.989 + NON >2400 a 0.017 | 1.006 | **-0.008** | 5 | 0/27 |
| echelle | Pacifica FDV above ___ one day after launch? | OUI >1e+09 a 0.04 + NON >2e+09 a 0.963 | 1.003 | **-0.008** | 83 | 0/6 |

Combinaisons avec un gain garanti > 0 au moins une fois : **1** sur 707.