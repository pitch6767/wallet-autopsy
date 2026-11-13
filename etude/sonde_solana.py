# 13.11.2026 soir : résultats depuis 11 h (Paris) — 2162 active + toutes les lignes du banc (lecture seule)
import json, urllib.request
B = "https://72-11-157-70.sslip.io/api"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.loads(r.read())
e = get(B + "/bot/banc/etat")
for k in ["version", "actives", "activesDepuis"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
g = e.get("regles", {}); print("règles :", {k: g.get(k) for k in ["vus", "doubles", "doublesF2", "sansEcart", "refuses"]})
tp = [x for x in (get(B + "/bot/banc/decisions?depuis=2026-11-01T00:00:00Z").get("tradesPaper") or []) if x.get("ouvert", "") >= "2026-11-13T10:00"]
print("\n=== onglet Trades depuis 11 h :", len(tp))
for x in tp: print(" ", json.dumps(x, ensure_ascii=False)[:300])
r = get(B + "/bot/banc?depuis=2026-11-13T10:00:00Z")
L = r.get("strategies") or []
print("\n=== banc depuis 11 h :", len(L), "lignes ; plafond", r.get("plafondCycle"))
def ligne(s): return f"{s['num']:>8} | trades {s['trades']:>3} | gagnés {s['gagnes']:>3} ({s['pctGagnes']}%) | gain {s['gain']:>9} | creux {s['creux']:>8} | mise max cycle {s['miseMaxCycle']} | {(s.get('nom') or '')[:70]}"
avec = [s for s in L if s["trades"] > 0]
print("lignes avec trades :", len(avec), "; positives :", sum(1 for s in avec if s["gain"] > 0), "; négatives :", sum(1 for s in avec if s["gain"] < 0))
print("\n-- suivies --")
for n in [2162, 700001, 700002, 700003, 700004, 700005, 700006, 700007, 4002162, 2172, 2171, 600005, 600013, 101, 105]:
    s = next((s for s in L if s["num"] == n), None); print(ligne(s) if s else f"{n:>8} | aucun signal")
print("\n-- 15 meilleures --")
for s in avec[:15]: print(ligne(s))
print("\n-- 10 pires --")
for s in avec[-10:]: print(ligne(s))
import statistics
print("\nmédiane des gains (lignes avec trades) :", statistics.median([s["gain"] for s in avec]) if avec else None)
