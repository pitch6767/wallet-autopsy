# Bot95 — H1081 : quels sous-jacents mènent le BTC ? (balayage large, lecture seule)

Généré le 14.10.2026 03:20 UTC dans GitHub Actions. Période minute 15.09–12.10, seconde 05.10–11.10 (13.10 réservé, non utilisé).
« Gain » = points de % de variance du BTC FUTUR expliqués EN PLUS du passé du BTC, mesuré sur le dernier tiers (appris sur les deux premiers).
Un gain ≤ 0 = rien de plus que le BTC lui-même. Aucun ordre.

## A. Minute — 108 séries testées, classées par gain sur la minute suivante

| nom           | source              |     n |   gain_1 |   gain_5 |   corr_1 |   corr_5 |
|:--------------|:--------------------|------:|---------:|---------:|---------:|---------:|
| BTCUSDT perp  | Binance futures 1 m | 39758 |   0.9049 |   0.2543 |   0.0315 |   0.0237 |
| SOLUSDT perp  | Binance futures 1 m | 39968 |   0.393  |  -0.0288 |   0.0424 |   0.0276 |
| XRPUSDT perp  | Binance futures 1 m | 40046 |   0.3418 |   0.1635 |   0.0415 |   0.0328 |
| ETHUSDT perp  | Binance futures 1 m | 40092 |   0.208  |   0.1079 |   0.0382 |   0.027  |
| BNBUSDT perp  | Binance futures 1 m | 40129 |   0.1819 |   0.039  |   0.0339 |   0.0229 |
| DOGEUSDT perp | Binance futures 1 m | 39980 |   0.1617 |   0.0837 |   0.0312 |   0.0264 |
| ZN=F          | Yahoo 1 m           | 27311 |   0.1518 |   0.0775 |   0.0271 |   0.0235 |
| ZB=F          | Yahoo 1 m           | 27187 |   0.1326 |   0.0789 |   0.018  |   0.0243 |
| BTC-USD       | Yahoo 1 m           | 40018 |   0.1186 |   0.0508 |   0.0249 |   0.0206 |
| GC=F          | Yahoo 1 m           | 27624 |   0.108  |   0.0793 |   0.0321 |   0.0143 |
| ETH-USD       | Yahoo 1 m           | 40250 |   0.1019 |   0.0507 |   0.0328 |   0.0246 |
| HG=F          | Yahoo 1 m           | 27415 |   0.0886 |   0.0954 |   0.0246 |   0.0198 |
| ^HSI          | Yahoo 1 m           |  6735 |   0.0656 |  -0.0731 |   0.0107 |  -0.001  |
| CL=F          | Yahoo 1 m           | 27568 |   0.0635 |   0.0523 |  -0.0207 |  -0.0187 |
| DX-Y.NYB      | Yahoo 1 m           | 26790 |   0.06   |  -0.0079 |  -0.0261 |  -0.0175 |
| COPX          | Yahoo 1 m           |  7883 |   0.0598 |   0.0134 |   0.007  |  -0.0107 |
| 6J=F          | Yahoo 1 m           | 27347 |   0.0597 |   0.0214 |   0.0229 |   0.0218 |
| SI=F          | Yahoo 1 m           | 27536 |   0.0594 |   0.0264 |   0.0277 |   0.0168 |
| GDX           | Yahoo 1 m           |  7887 |   0.0535 |  -0.0906 |   0.0092 |  -0.0113 |
| XAUTUSDT      | Binance spot 1 m    | 39202 |   0.0499 |   0.0074 |   0.0258 |   0.0139 |
| ^TNX          | Yahoo 1 m           |  8056 |   0.0493 |   0.0649 |  -0.0155 |  -0.0163 |
| GLD           | Yahoo 1 m           |  7889 |   0.0469 |  -0.0344 |   0.0119 |  -0.0101 |
| ZF=F          | Yahoo 1 m           | 27259 |   0.0456 |   0.0284 |   0.0181 |   0.0225 |
| USDJPY=X      | Yahoo 1 m           | 28312 |   0.0349 |  -0.003  |  -0.0219 |  -0.02   |
| PAXGUSDT      | Binance spot 1 m    | 39267 |   0.03   |   0.0006 |   0.0223 |   0.0135 |
| TLT           | Yahoo 1 m           |  7886 |   0.0254 |  -0.0893 |   0.0132 |   0.0127 |
| AAPL          | Yahoo 1 m           |  7892 |   0.0245 |  -0.8158 |   0.0089 |   0.0081 |
| SOXX          | Yahoo 1 m           |  7892 |   0.0182 |   0.0088 |   0.006  |  -0.0059 |
| XLF           | Yahoo 1 m           |  7888 |   0.0178 |   0.0111 |   0.0169 |   0.0117 |
| PL=F          | Yahoo 1 m           | 27343 |   0.0119 |   0.0557 |   0.0244 |   0.0129 |
| USDMXN=X      | Yahoo 1 m           | 28268 |   0.0069 |   0.0251 |  -0.0028 |  -0.0128 |
| YM=F          | Yahoo 1 m           | 27571 |   0.0057 |  -0.0461 |   0.0218 |   0.012  |
| IWM           | Yahoo 1 m           |  7886 |   0.0035 |  -0.2419 |   0.0184 |  -0.004  |
| ^VIX          | Yahoo 1 m           | 15609 |   0.0027 |  -0.0464 |  -0.0117 |  -0.0123 |
| VXX           | Yahoo 1 m           |  7873 |   0.0014 |  -0.2413 |  -0.0159 |  -0.001  |
| ^DJI          | Yahoo 1 m           |  7893 |   0.0001 |  -0.2263 |   0.0153 |   0.0027 |
| GOOGL         | Yahoo 1 m           |  7893 |  -0.0007 |  -0.0111 |   0.0069 |   0.0018 |
| COIN          | Yahoo 1 m           |  7893 |  -0.0016 |  -0.3794 |   0.0306 |   0.0185 |
| UVXY          | Yahoo 1 m           |  7875 |  -0.0029 |  -0.3893 |  -0.0149 |  -0.0005 |
| ^GDAXI        | Yahoo 1 m           | 10254 |  -0.005  |  -0.118  |   0.0175 |   0.0117 |

Séries avec un gain > 0 à 1 min ET à 5 min : 23 sur 108.

## B. Seconde — 5 séries testées, classées par gain à 30 s

| nom      |      n |   gain_10 |   gain_30 |   gain_60 |   corr_10 |   corr_30 |
|:---------|-------:|----------:|----------:|----------:|----------:|----------:|
| EURUSDT  | 311175 |   -0.0026 |   -0.0011 |   -0.0122 |    0.0039 |    0.0027 |
| EURUSDT  | 311175 |   -0.0026 |   -0.0011 |   -0.0122 |    0.0039 |    0.0027 |
| PAXGUSDT | 312353 |   -0.0203 |   -0.013  |   -0.0008 |    0.0169 |    0.0113 |
| PAXGUSDT | 312353 |   -0.0203 |   -0.013  |   -0.0008 |    0.0169 |    0.0113 |
| XAUTUSDT | 315040 |   -0.0204 |   -0.0164 |    0.0007 |    0.0232 |    0.014  |

## Journal

```
  ok ^TNX 7999
  ok ^IRX 7999
  ok ^GSPC 7801
  ok ^NDX 7801
  ok ^DJI 7801
  ok ^RUT 7801
  ok ^N225 5312
  ok ^HSI 6556
  ok ^STOXX50E 10201
  ok ^GDAXI 10162
  ok ^FTSE 10198
  ok BTC=F 20705
  ok MBT=F 27068
  ok ETH=F 22202
  ok BTC-USD 40314
  ok ETH-USD 40316
  ok IBIT 7800
  ok FBTC 7720
  ok GBTC 7141
  ok ARKB 6913
  ok BITO 7541
  ok ETHA 7786
  ok MSTR 7800
  ok COIN 7799
  ok MARA 7800
  ok RIOT 7800
  ok CLSK 7796
  ok HUT 7711
  ok HOOD 7800
  yahoo vide SQ
  ok PYPL 7798
  ok NVDA 7800
  ok TSLA 7800
  ok AAPL 7800
  ok MSFT 7800
  ok AMZN 7800
  ok META 7800
  ok GOOGL 7800
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
  ok FXE 1715
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
A fini 269 s
B. BTC 1 s
  ok 1s PAXGUSDT
  ok 1s EURUSDT
  ok 1s XAUTUSDT
  ok 1s PAXGUSDT
  ok 1s EURUSDT
```
