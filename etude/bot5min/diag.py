import urllib.request, json
d=json.loads(urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev/api/etat",headers={"User-Agent":"x"}),timeout=30).read())
v=d["v1"]; print("BTC entrees", v["entrees"], "refusElan", v.get("refusElan"), "pos", bool(v["pos"])); e=v["eth"]; print("ETH entrees", e["entrees"], "refusElan", e.get("refusElan"), "pos", e["pos"] and e["pos"]["cote"]); print("erreurs", d["diag"]["erreurs"][:6]); print("sources", v["sources"])
g=json.loads(urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev/api/v1debug",headers={"User-Agent":"x"}),timeout=30).read()); print("livres suivis", len(g["livres"]))
