# 09.11.2026 18 h : point de décision de lundi soir — lecture seule des routes publiques du bot (banc avec plafond 200 $, état, chrono, calendrier)
import json, urllib.request, collections, datetime as dt
from zoneinfo import ZoneInfo
B = "https://72-11-157-70.sslip.io/api/bot/"
def get(p):
    try:
        with urllib.request.urlopen(urllib.request.Request(B + p, headers={"user-agent": "analyse"}), timeout=120) as r: return json.load(r)
    except Exception as e: print(p, repr(e)); return None
T = (get("banc/trades?depuis=2026-11-08T15:00:00Z&plafond=200") or {}).get("trades", [])
PZ = ZoneInfo("Europe/Paris"); j = lambda t: dt.datetime.fromtimestamp(t["endTs"] / 1000, PZ).strftime("%d")
G = collections.defaultdict(lambda: {"n": 0, "w": 0, "g": 0.0, "j": collections.defaultdict(float), "L": []})
for t in sorted(T, key=lambda t: t["endTs"]):
    x = G[t["num"]]; x["n"] += 1; x["w"] += t["gagne"]; x["g"] += t["pnl"]; x["j"][j(t)] += t["pnl"]; x["L"].append(t["pnl"])
def creux(L):
    c = p = m = 0
    for v in L: c += v; p = max(p, c); m = max(m, p - c)
    return m
print("trades réglés depuis le 08.11 16 h :", len(T), "; dernier :", max((t["ouvert"] for t in T), default=None))
print("\nTOP 25 (gain | trades | gagnés % | creux | par jour 08 / 09)")
for n, x in sorted(G.items(), key=lambda kv: -kv[1]["g"])[:25]:
    print(n, f"| {x['g']:+.0f} | {x['n']} | {100*x['w']/x['n']:.0f} % | -{creux(x['L']):.0f} |", {d: round(v) for d, v in sorted(x["j"].items())})
print("\nRÉFÉRENCES")
for n in [31, 32, 301, 302, 2112, 2110, 2171, 2172, 12112, 1114, 13, 1112, 313, 7, 107, 600001, 600002, 600003, 600004, 600005, 600006, 600007, 600008, 9100, 3001114, 3002171, 3012112]:
    x = G.get(n)
    print(n, "—" if not x else f"| {x['g']:+.0f} | {x['n']} | {100*x['w']/x['n']:.0f} % | -{creux(x['L']):.0f} | {dict((d, round(v)) for d, v in sorted(x['j'].items()))}")
for p in ["state", "chrono", "banc/calendrier"]:
    d = get(p)
    if d is None: continue
    if p == "state":
        c = d.get("config", {}); print("\nÉTAT : mode", c.get("mode") or d.get("mode"), "| capital", d.get("capital") or c.get("capital"), "| clés", list(d.keys())[:15])
    else: print("\n" + p.upper(), json.dumps(d, ensure_ascii=False)[:1500])
