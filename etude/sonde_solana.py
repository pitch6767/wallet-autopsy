# 13.11.2026 soir : résultats depuis 11 h (Paris) — 2162 active + toutes les lignes du banc (lecture seule, routes publiques)
import json, urllib.request, traceback, statistics
from collections import defaultdict
B = "https://72-11-157-70.sslip.io/api"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=280) as r: return json.loads(r.read())
try:
    e = get(B + "/bot/banc/etat")
    for k in ["version", "actives", "activesDepuis"]: print(k, ":", json.dumps(e.get(k), ensure_ascii=False))
    g = e.get("regles", {}); print("règles :", {k: g.get(k) for k in ["vus", "doubles", "doublesF2", "sansEcart", "refuses"]})
except Exception: traceback.print_exc()
try:
    tp = [x for x in (get(B + "/bot/banc/decisions?depuis=2026-11-01T00:00:00Z").get("tradesPaper") or []) if x.get("ouvert", "") >= "2026-11-13T10:00"]
    print("\n=== onglet Trades depuis 11 h :", len(tp))
    for x in tp: print(" ", json.dumps(x, ensure_ascii=False)[:260])
except Exception: traceback.print_exc()
try:
    T = get(B + "/bot/banc/trades?depuis=2026-11-13T10:00:00Z&plafond=100")["trades"]
    print("\n=== banc depuis 11 h :", len(T), "trades réglés")
    par = defaultdict(list)
    for t in T: par[t["num"]].append(t)
    R = []
    for n, ts in par.items():
        ts.sort(key=lambda t: t["ouvert"]); cum = pic = creux = 0
        for t in ts: cum += t["pnl"]; pic = max(pic, cum); creux = max(creux, pic - cum)
        cyc = defaultdict(float)
        for t in ts: cyc[t["endTs"]] += t["mise"]
        R.append(dict(n=n, tr=len(ts), cy=len(cyc), g=sum(t["gagne"] for t in ts), gain=cum, creux=creux, mise=sum(t["mise"] for t in ts), mx=max(cyc.values())))
    R.sort(key=lambda r: -r["gain"])
    def L(r): return f"{r['n']:>8} | trades {r['tr']:>3} | cycles {r['cy']:>3} | gagnés {r['g']:>3} | misé {r['mise']:>8.0f} | gain {r['gain']:>8.0f} | creux {r['creux']:>6.0f} | max/cycle {r['mx']:.0f}"
    print("lignes :", len(R), "; positives :", sum(r["gain"] > 0 for r in R), "; négatives :", sum(r["gain"] < 0 for r in R), "; médiane :", round(statistics.median([r["gain"] for r in R]), 1))
    print("\n-- suivies --")
    for n in [2162, 700001, 700002, 700003, 700004, 700005, 700006, 700007, 4002162, 1002162, 2002162, 3002162, 2172, 2171, 600005, 600013, 101, 105]:
        r = next((r for r in R if r["n"] == n), None); print(L(r) if r else f"{n:>8} | aucun trade")
    print("\n-- 15 meilleures --"); [print(L(r)) for r in R[:15]]
    print("\n-- 10 pires --"); [print(L(r)) for r in R[-10:]]
    print("\n-- 2162 trade par trade --")
    for t in par.get(2162, []): print(" ", t["ouvert"][11:19], t["side"], "prix", t["prix"], "mise", round(t["mise"]), "pnl", round(t["pnl"]))
    # cycles BTC depuis 11 h : combien gagnés UP/DOWN, et combien de cycles où au moins une ligne de base a tradé
    base = [t for t in T if t["num"] < 1000]
    cb = defaultdict(list)
    for t in base: cb[t["endTs"]].append(t)
    print("\ncycles avec au moins un trade de base :", len(cb), "; trades de base :", len(base), "; gagnés :", sum(t["gagne"] for t in base), "; gain total base :", round(sum(t["pnl"] for t in base)))
except Exception: traceback.print_exc()
