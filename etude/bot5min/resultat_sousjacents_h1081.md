# Bot95 — H1081 : quels sous-jacents mènent le BTC ? (balayage large, lecture seule)

Généré le 14.10.2026 04:37 UTC dans GitHub Actions. Période minute 15.09–12.10, seconde 05.10–11.10 (13.10 réservé, non utilisé).
« Gain » = points de % de variance du BTC FUTUR expliqués EN PLUS du passé du BTC, mesuré sur le dernier tiers (appris sur les deux premiers).
Un gain ≤ 0 = rien de plus que le BTC lui-même. « jours » = nombre de jours du test où la série améliore la prévision (contrôle anti-artefact). Aucun ordre.

## A. Minute — 156 séries testées, classées par gain sur la minute suivante

| nom           | source              |     n |   gain_1 | jours_1   |   gain_5 | jours_5   |   corr_1 |
|:--------------|:--------------------|------:|---------:|:----------|---------:|:----------|---------:|
| BTCUSDT perp  | Binance futures 1 m | 39758 |   0.9049 | 9/10      |   0.2543 | 8/10      |   0.0315 |
| SOLUSDT perp  | Binance futures 1 m | 39968 |   0.393  | 6/10      |  -0.0288 | 5/10      |   0.0424 |
| XRPUSDT perp  | Binance futures 1 m | 40046 |   0.3418 | 9/10      |   0.1635 | 8/10      |   0.0415 |
| SOLUSDT       | Binance spot 1 m    | 39979 |   0.3113 | 6/10      |  -0.0354 | 5/10      |   0.0387 |
| XRPUSDT       | Binance spot 1 m    | 40031 |   0.2998 | 9/10      |   0.1499 | 8/10      |   0.0399 |
| ETHUSDT perp  | Binance futures 1 m | 40092 |   0.208  | 6/10      |   0.1079 | 6/10      |   0.0382 |
| LINKUSDT      | Binance spot 1 m    | 40136 |   0.1852 | 7/10      |  -0.0392 | 4/10      |   0.0358 |
| BNBUSDT perp  | Binance futures 1 m | 40129 |   0.1819 | 7/10      |   0.039  | 7/10      |   0.0339 |
| ETHUSDT       | Binance spot 1 m    | 40059 |   0.1635 | 5/10      |   0.0774 | 6/10      |   0.0338 |
| DOGEUSDT perp | Binance futures 1 m | 39980 |   0.1617 | 7/10      |   0.0837 | 8/10      |   0.0312 |
| ZN=F          | Yahoo 1 m           | 27311 |   0.1518 | 8/9       |   0.0775 | 7/9       |   0.0271 |
| DOGEUSDT      | Binance spot 1 m    | 39952 |   0.1472 | 8/10      |   0.0784 | 8/10      |   0.0303 |
| UNIUSDT       | Binance spot 1 m    | 40164 |   0.1471 | 9/10      |   0.0204 | 6/10      |   0.0354 |
| ADAUSDT       | Binance spot 1 m    | 39699 |   0.1451 | 7/10      |   0.0156 | 4/10      |   0.0337 |
| SUIUSDT       | Binance spot 1 m    | 40177 |   0.1375 | 7/10      |   0.062  | 8/10      |   0.034  |
| ZB=F          | Yahoo 1 m           | 27187 |   0.1326 | 7/9       |   0.0789 | 8/9       |   0.018  |
| BNBUSDT       | Binance spot 1 m    | 40106 |   0.1314 | 8/10      |   0.0208 | 7/10      |   0.0308 |
| TAOUSDT       | Binance spot 1 m    | 39890 |   0.1309 | 7/10      |   0.0537 | 6/10      |   0.0312 |
| BTC-USD       | Yahoo 1 m           | 40018 |   0.1186 | 8/10      |   0.0508 | 7/10      |   0.0249 |
| ENAUSDT       | Binance spot 1 m    | 39912 |   0.113  | 7/10      |   0.0188 | 7/10      |   0.0346 |
| NEARUSDT      | Binance spot 1 m    | 40147 |   0.1082 | 5/10      |  -0.0355 | 4/10      |   0.0357 |
| GC=F          | Yahoo 1 m           | 27624 |   0.108  | 6/9       |   0.0793 | 7/9       |   0.0321 |
| ETH-USD       | Yahoo 1 m           | 40250 |   0.1019 | 6/10      |   0.0507 | 4/10      |   0.0328 |
| WLDUSDT       | Binance spot 1 m    | 40144 |   0.0966 | 7/10      |   0.0252 | 5/10      |   0.0307 |
| ONDOUSDT      | Binance spot 1 m    | 40057 |   0.0931 | 6/10      |   0.0669 | 5/10      |   0.027  |
| TIAUSDT       | Binance spot 1 m    | 40121 |   0.0925 | 7/10      |  -0.0288 | 6/10      |   0.0283 |
| ARBUSDT       | Binance spot 1 m    | 39791 |   0.0906 | 9/10      |  -0.0303 | 6/10      |   0.0269 |
| HG=F          | Yahoo 1 m           | 27415 |   0.0886 | 6/9       |   0.0954 | 5/9       |   0.0246 |
| AVAXUSDT      | Binance spot 1 m    | 40128 |   0.0828 | 6/10      |  -0.0028 | 6/10      |   0.0282 |
| XLMUSDT       | Binance spot 1 m    | 39479 |   0.0678 | 5/10      |  -0.0263 | 3/10      |   0.0287 |
| ^HSI          | Yahoo 1 m           |  6735 |   0.0656 | 5/7       |  -0.0731 | 4/7       |   0.0107 |
| CL=F          | Yahoo 1 m           | 27568 |   0.0635 | 6/9       |   0.0523 | 5/9       |  -0.0207 |
| INJUSDT       | Binance spot 1 m    | 40165 |   0.0605 | 6/10      |   0.0353 | 3/10      |   0.0265 |
| DX-Y.NYB      | Yahoo 1 m           | 26790 |   0.06   | 6/9       |  -0.0079 | 5/9       |  -0.0261 |
| COPX          | Yahoo 1 m           |  7883 |   0.0598 | 5/7       |   0.0134 | 5/7       |   0.007  |
| 6J=F          | Yahoo 1 m           | 27347 |   0.0597 | 7/9       |   0.0214 | 7/9       |   0.0229 |
| SI=F          | Yahoo 1 m           | 27536 |   0.0594 | 6/9       |   0.0264 | 4/9       |   0.0277 |
| GDX           | Yahoo 1 m           |  7887 |   0.0535 | 6/7       |  -0.0906 | 5/7       |   0.0092 |
| USDCUSDT      | Binance spot 1 m    | 39338 |   0.0504 | 6/10      |   0.0016 | 6/10      |  -0.0174 |
| XAUTUSDT      | Binance spot 1 m    | 39202 |   0.0499 | 3/10      |   0.0074 | 5/10      |   0.0258 |

Séries avec un gain > 0 à 1 min ET à 5 min : 47 sur 156.

## B. Seconde — 42 séries testées, classées par gain à 30 s

| nom        |      n |   gain_10 | jours_10   |   gain_30 | jours_30   |   gain_60 |   corr_10 |
|:-----------|-------:|----------:|:-----------|----------:|:-----------|----------:|----------:|
| ETHUSDT    | 410926 |    1.1724 | 3/3        |    0.6074 | 3/3        |    0.2539 |    0.1152 |
| XRPUSDT    | 363840 |    0.9293 | 2/3        |    0.5294 | 3/3        |    0.2415 |    0.1145 |
| SOLUSDT    | 382277 |    0.9334 | 3/3        |    0.4657 | 3/3        |    0.3815 |    0.1061 |
| BNBUSDT    | 391410 |    0.9091 | 3/3        |    0.4409 | 3/3        |    0.2226 |    0.1092 |
| NEARUSDT   | 392693 |    0.2779 | 2/3        |    0.3894 | 2/3        |    0.2832 |    0.0764 |
| UNIUSDT    | 355364 |    0.5753 | 2/3        |    0.3425 | 3/3        |    0.1957 |    0.0852 |
| DOGEUSDT   | 346029 |    0.6493 | 3/3        |    0.3081 | 3/3        |    0.1556 |    0.0987 |
| SUIUSDT    | 377502 |    0.3292 | 2/3        |    0.2813 | 2/3        |    0.1938 |    0.1107 |
| AAVEUSDT   | 354835 |    0.6218 | 2/3        |    0.2788 | 3/3        |    0.1441 |    0.0822 |
| HBARUSDT   | 332173 |    0.2645 | 2/3        |    0.2364 | 3/3        |    0.0817 |    0.083  |
| AVAXUSDT   | 359898 |    0.4571 | 3/3        |    0.2327 | 3/3        |    0.1029 |    0.0894 |
| LINKUSDT   | 340118 |    0.5217 | 2/3        |    0.2043 | 3/3        |    0.1265 |    0.1036 |
| ADAUSDT    | 330202 |    0.2489 | 2/3        |    0.1703 | 2/3        |    0.1003 |    0.0678 |
| LTCUSDT    | 337274 |    0.2612 | 3/3        |    0.1402 | 3/3        |    0.0182 |    0.0681 |
| BCHUSDT    | 310342 |    0.2187 | 2/3        |    0.1244 | 3/3        |    0.0009 |    0.0556 |
| FETUSDT    | 328054 |    0.033  | 2/3        |    0.1184 | 2/3        |    0.1396 |    0.0602 |
| SEIUSDT    | 323754 |    0.1644 | 2/3        |    0.0599 | 2/3        |    0.059  |    0.0774 |
| DOTUSDT    | 312383 |   -0.0134 | 1/3        |    0.0449 | 3/3        |   -0.012  |    0.0334 |
| ENAUSDT    | 337360 |    0.2071 | 2/3        |    0.0411 | 3/3        |    0.0936 |    0.0722 |
| RENDERUSDT | 317194 |    0.1116 | 3/3        |    0.0361 | 2/3        |    0.0084 |    0.0494 |
| WLDUSDT    | 356362 |   -0.2655 | 2/3        |    0.016  | 2/3        |   -0.1473 |    0.0805 |
| SHIBUSDT   | 305868 |    0.0049 | 2/3        |    0.0127 | 2/3        |    0      |    0.012  |
| TRXUSDT    | 350435 |    0.004  | 3/3        |    0.0026 | 2/3        |    0.0071 |    0.0007 |
| EURUSDT    | 311175 |   -0.0026 | 2/3        |   -0.0011 | 1/3        |   -0.0122 |    0.0039 |
| OPUSDT     | 312897 |   -0.203  | 0/3        |   -0.0013 | 2/3        |   -0.003  |    0.0437 |
| ETCUSDT    | 301349 |   -0.0133 | 1/3        |   -0.0019 | 1/3        |   -0.0008 |    0.0253 |
| ONDOUSDT   | 341719 |    0.031  | 2/3        |   -0.0038 | 1/3        |    0.0802 |    0.0916 |
| JUPUSDT    | 326957 |    0.066  | 2/3        |   -0.0045 | 1/3        |    0.0446 |    0.0597 |
| PEPEUSDT   | 317615 |   -0.0173 | 1/3        |   -0.0057 | 1/3        |   -0.0026 |    0.0152 |
| ICPUSDT    | 320471 |   -0.027  | 1/3        |   -0.0057 | 2/3        |    0.0216 |    0.0427 |
| WIFUSDT    | 307379 |   -0.02   | 1/3        |   -0.0099 | 1/3        |    0.0118 |    0.0615 |
| PAXGUSDT   | 312353 |   -0.0203 | 0/3        |   -0.013  | 0/3        |   -0.0008 |    0.0169 |
| FLOKIUSDT  | 307986 |   -0.0216 | 2/3        |   -0.0156 | 2/3        |   -0.0031 |    0.0341 |
| XAUTUSDT   | 315040 |   -0.0204 | 0/3        |   -0.0164 | 0/3        |    0.0007 |    0.0232 |
| BONKUSDT   | 302257 |   -0.0228 | 1/3        |   -0.0197 | 0/3        |    0.0048 |    0.0131 |
| XLMUSDT    | 310329 |   -0.1782 | 1/3        |   -0.0598 | 1/3        |   -0.0099 |    0.0507 |
| ATOMUSDT   | 315359 |   -0.2137 | 1/3        |   -0.0643 | 1/3        |    0.0048 |    0.0291 |
| INJUSDT    | 345151 |   -0.5031 | 1/3        |   -0.065  | 2/3        |    0.0042 |    0.0709 |
| ARBUSDT    | 318036 |    0.1679 | 3/3        |   -0.0672 | 1/3        |   -0.1268 |    0.0601 |
| APTUSDT    | 357825 |   -1.0323 | 0/3        |   -0.0968 | 1/3        |   -0.1022 |    0.0733 |

## Journal

```
  ok AMD 7800
  ok SMCI 7800
  ok PLTR 7801
  ok QQQ 7800
  ok SPY 7801
  ok IWM 7801
  ok TLT 7800
  ok HYG 7797
  ok GLD 7801
  ok SLV 7800
  ok USO 7774
  ok UUP 4153
  ok FXE 1716
  ok FXY 2747
  ok XLK 7801
  ok XLF 7801
  ok SOXX 7800
  ok ARKK 7794
  ok TQQQ 7800
  ok SQQQ 7800
  ok UVXY 7706
  ok VXX 7604
  ok KRE 7801
  ok GDX 7801
  ok COPX 7580
  ok URA 7767
  ok LIT 3089
  ok CIBR 7668
  ok BLOK 4493
  ok BKCH 1059
  ok DAPP 5359
  ok WGMI 4689
  ok CONL 7759
  ok MSTU 7729
  ok BITX 7775
liste spot fixe (ticker indisponible)
A fini 745 s
B. BTC 1 s
  ok 1s ETHUSDT
  ok 1s SOLUSDT
  ok 1s XRPUSDT
  ok 1s BNBUSDT
  ok 1s DOGEUSDT
  ok 1s ADAUSDT
  ok 1s TRXUSDT
  ok 1s LINKUSDT
  ok 1s AVAXUSDT
  ok 1s SUIUSDT
  ok 1s LTCUSDT
  ok 1s BCHUSDT
  ok 1s DOTUSDT
  ok 1s NEARUSDT
  ok 1s APTUSDT
  ok 1s UNIUSDT
  ok 1s PEPEUSDT
  ok 1s SHIBUSDT
  ok 1s WIFUSDT
  ok 1s ARBUSDT
  ok 1s OPUSDT
  ok 1s AAVEUSDT
  ok 1s ETCUSDT
  ok 1s FILUSDT
  ok 1s ATOMUSDT
  ok 1s INJUSDT
  ok 1s SEIUSDT
  ok 1s TIAUSDT
  ok 1s RENDERUSDT
  ok 1s FETUSDT
  ok 1s HBARUSDT
  ok 1s ICPUSDT
  ok 1s XLMUSDT
  ok 1s ENAUSDT
  ok 1s WLDUSDT
  ok 1s BONKUSDT
  ok 1s FLOKIUSDT
  ok 1s JUPUSDT
  ok 1s ONDOUSDT
  ok 1s PAXGUSDT
  ok 1s EURUSDT
  ok 1s XAUTUSDT
```
