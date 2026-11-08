# 08.11.2026 : 2171 / 2172 et leurs versions (1002171, 2002171, 3002171, 600002, 600003) depuis 16 h — lecture seule /api/bot/banc/trades
import json, urllib.request, collections
with urllib.request.urlopen(urllib.request.Request("https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis=2026-11-08T15:00:00Z", headers={"user-agent": "analyse"}), timeout=120) as r: T = json.load(r)["trades"]
N = [2171, 1002171, 2002171, 3002171, 2172, 1002172, 2002172, 3002172, 12112, 1012112, 600002, 600003]
for n in N:
    X = sorted([t for t in T if t["num"] == n], key=lambda t: t["endTs"])
    print(n, "| trades", len(X), "| gagnés", sum(t["gagne"] for t in X), "| gain", round(sum(t["pnl"] for t in X)), "| mise moy", round(sum(t["mise"] for t in X) / max(1, len(X))))
A = {(t["endTs"], t["side"]): t for t in T if t["num"] == 2171}
B = {(t["endTs"], t["side"]): t for t in T if t["num"] == 600002}
print("\n2171 : cycles aussi dans 600002 :", len(A.keys() & B.keys()), "/", len(A), "; 600002 hors 2171 (viennent de 2172) :", len(B.keys() - A.keys()))
for k in sorted(A.keys() - B.keys())[:12]:
    t = A[k]; print("  2171 absent de 600002 :", t["ouvert"][11:19], t["side"], "prix", round(t["prix"], 2), "gain", round(t["pnl"]))
