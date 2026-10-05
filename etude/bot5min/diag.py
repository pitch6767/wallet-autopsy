import json, urllib.request
d=json.loads(urllib.request.urlopen(urllib.request.Request("https://bot95.pitch67.workers.dev/api/v1debug",headers={"User-Agent":"x"}),timeout=30).read())
print("maintenant", d["maintenant"], "cycle", d["mk"]["start"], "ws ouvert a", d["ouvert"], "=> connexion", round(d["ouvert"]-d["mk"]["start"],1), "s apres le debut du cycle")
print("livres suivis", list(d["livres"].keys()), "proba", d["proba"])
