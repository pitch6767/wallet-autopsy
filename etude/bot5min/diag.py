import io, zipfile, urllib.request
u="https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/BTCUSDT-1s-2026-10-02.zip"
z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u,timeout=60).read()))
L=z.read(z.namelist()[0]).decode().splitlines()
print(len(L)); print("\n".join(L[40000:40012]))
c=[float(l.split(",")[4]) for l in L]
print("close identique a t-1 :", sum(1 for i in range(1,len(c)) if c[i]==c[i-1])/len(c))
print("close identique a t-5 :", sum(1 for i in range(5,len(c)) if c[i]==c[i-5])/len(c))
v=[float(l.split(",")[5]) for l in L]; print("secondes volume 0 :", sum(1 for x in v if x==0)/len(v))
