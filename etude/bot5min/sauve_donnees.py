"""Sauvegarde permanente des donnees brutes du bot (09.10.2026) : carnets enregistres (rec, 4 mesures/s, effaces apres 48 h dans le bot)
et signaux (sig, 1/s, effaces apres 4 jours), BTC. Un fichier compresse par jour (UTC) et par type dans bot95/donnees/<jour>/.
Fusion par minute : on ne perd jamais une minute deja sauvee."""
import json, gzip, os, time, urllib.request
U = "https://bot95.pitch67.workers.dev"; D = "bot95/donnees/"
def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sauve"}), timeout=120) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(5)
    raise err
def tout(kind, a, n):
    out, apres = {}, None
    while True:
        d = get(f"{U}/api/{kind}?a={a}&n={n}" + (f"&apres={apres}" if apres else ""))
        for k, doc in zip(d["cles"], d["docs"]): out[k] = doc
        if not d["cles"] or len(d["cles"]) < n: return out
        apres = d["suivant"]
for a, kind, n in (("BTC", "rec", 60), ("BTC", "sig", 120), ("ETH", "rec", 60), ("ETH", "sig", 120)):
  try:
      M = tout(kind, a, n); par_jour = {}
      for k, doc in M.items():
          minute = int(k.split(":")[2]); jour = time.strftime("%Y-%m-%d", time.gmtime(minute * 60))
          par_jour.setdefault(jour, {})[k] = doc
      for jour, docs in par_jour.items():
          os.makedirs(D + jour, exist_ok=True); f = f"{D}{jour}/{kind}_{a}.json.gz"
          old = json.load(gzip.open(f, "rt")) if os.path.exists(f) else {}
          old.update(docs)
          with gzip.open(f, "wt") as g: json.dump(old, g, separators=(",", ":"))
          print(kind, jour, len(old), "minutes", os.path.getsize(f) // 1024, "Ko")

  except Exception as e: print(a, kind, "erreur", e)
