# 12.11.2026 (Pitch : « je veux tout rejouer et avoir les trades justes ») : collecte des données de bot95 Cloudflare
# pour le trou du moteur de Dublin (03:53 → 14:03 UTC) — lecture seule. Fichier : etude/rejeu/donnees.json.gz
import json, urllib.request, urllib.parse, gzip, os, subprocess, time
def get(u):
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=90) as r: return json.loads(r.read())
        except Exception as e: err = str(e); time.sleep(2)
    return {"erreur": err}
B = "https://bot95.pitch67.workers.dev"
DEB, FIN = "2026-11-12T03:30:00", "2026-11-12T14:15:00"
cat = get(B + "/api/catalogue").get("strategies") or []
noms = sorted({x["nom"] for x in cat} | {"BY1 contre-elan calme 100 $", "TWAP fin", "TWAP fin anti-saut", "TWAP fin prevision Chainlink", "TWAP fin quantiles", "TWAP fin sauts", "V2-F incertitude 0,01 %",
  "corrige : V2-F + pas les deux baissent", "corrige : V2-F ecart qui grandit", "corrige : desaccord 20", "corrige marge mesuree : V2-F", "contrarien 5 min + 1 h"})
print("noms :", len(noms))
H = {}
for n in noms:
    d = get(B + "/api/hist?s=" + urllib.parse.quote(n + " BTC"))
    if "erreur" in d: print("erreur", n, d["erreur"]); continue
    a = [x for x in (d.get("archive") or []) if DEB <= str(x[0]) <= FIN]
    der = [x for x in (d.get("derniers") or []) if DEB <= str(x.get("heure", "")) <= FIN]
    dmin = min((x.get("heure", "") for x in (d.get("derniers") or [])), default=None)
    if a or der: H[n] = {"archive": a, "derniers": der, "derniers_depuis": dmin, "nb_derniers": len(d.get("derniers") or [])}
print("stratégies avec trades dans le trou :", len(H))
for n, v in sorted(H.items(), key=lambda kv: -len(kv[1]["archive"]))[:40]:
    print(f"  {len(v['archive']):3d} archive | {len(v['derniers']):3d} complets (depuis {v['derniers_depuis']}) | {n}")
S = {}
k0 = int(1794455400 / 60) - 2   # 03:50 UTC
apres = "sig:BTC:" + str(k0)
for _ in range(12):
    d = get(B + "/api/sig?a=BTC&n=120&apres=" + urllib.parse.quote(apres))
    ks = d.get("cles") or []
    if not ks: break
    for k, doc in zip(ks, d.get("docs") or []): S[k] = doc
    apres = ks[-1]
    if int(ks[-1].split(":")[-1]) > int(1794492900 / 60): break
print("lignes sig (minutes) :", len(S), min(S) if S else None, max(S) if S else None)
os.makedirs("etude/rejeu", exist_ok=True)
with gzip.open("etude/rejeu/donnees.json.gz", "wt") as f: json.dump({"hist": H, "sig": S, "noms": noms}, f)
print("taille", os.path.getsize("etude/rejeu/donnees.json.gz"))
subprocess.run(["git", "add", "etude/rejeu/donnees.json.gz"])
