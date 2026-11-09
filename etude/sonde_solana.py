# 09.11.2026 20 h 13 (Pitch : « fais un contrôle sérieux des stratégies, on en a trop, je veux la meilleure de toutes »). Lecture seule.
# Banc 95 h, plafond 200 $ par cycle (comme l'onglet). Doublons regroupés (mêmes trades). Jugé sur : gain, creux, jours, et 2 moitiés.
import json, urllib.request, collections, datetime as dt
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
dep = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
with urllib.request.urlopen(urllib.request.Request(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=200", headers={"user-agent": "analyse"}), timeout=180) as r: T = json.load(r)["trades"]
T.sort(key=lambda t: t["endTs"])
t0, t1 = T[0]["endTs"], T[-1]["endTs"]; mil = (t0 + t1) / 2
print("trades :", len(T), "du", dt.datetime.fromtimestamp(t0/1000, PZ), "au", dt.datetime.fromtimestamp(t1/1000, PZ))
S = collections.defaultdict(list)
for t in T: S[t["num"]].append(t)
print("lignes :", len(S))
# doublons
sig = collections.defaultdict(list)
for n, L in S.items(): sig[tuple((t["endTs"], t["side"], round(t["pnl"], 1)) for t in L)].append(n)
groupes = {min(v): sorted(v) for v in sig.values()}
print("lignes différentes (doublons regroupés) :", len(groupes), "; plus gros groupes :", sorted((len(v), k) for k, v in groupes.items())[-8:])
R = []
for n, membres in groupes.items():
    L = S[n]
    if len(L) < 40: continue
    c = p = cr = 0; jours = collections.defaultdict(float)
    for t in L: c += t["pnl"]; p = max(p, c); cr = max(cr, p - c); jours[dt.datetime.fromtimestamp(t["endTs"]/1000, PZ).strftime("%d")] += t["pnl"]
    a = sum(t["pnl"] for t in L if t["endTs"] < mil); b = c - a
    R.append(dict(n=n, k=len(membres), tr=len(L), g=c, cr=cr, a=a, b=b, jn=sum(v < 0 for v in jours.values()), jt=len(jours), pire=min(jours.values()), J=jours, mise=sum(t["mise"] for t in L)/len(L)))
print("lignes jugées (≥ 40 trades) :", len(R))
def ligne(x): return f"{x['n']:>8} (+{x['k']-1} doublons) | {x['g']:+7.0f} | creux -{x['cr']:5.0f} | gain/creux {x['g']/max(1,x['cr']):4.1f} | moitiés {x['a']:+6.0f} / {x['b']:+6.0f} | jours nég {x['jn']}/{x['jt']} | pire jour {x['pire']:+5.0f} | {x['tr']} tr, mise moy {x['mise']:.0f} | " + " ".join(f"{d}:{v:+.0f}" for d, v in sorted(x['J'].items()))
print("\n=== TOP 25 au gain ===");             [print(ligne(x)) for x in sorted(R, key=lambda x: -x["g"])[:25]]
print("\n=== TOP 25 gain / creux ===");       [print(ligne(x)) for x in sorted(R, key=lambda x: -x["g"]/max(1, x["cr"]))[:25]]
print("\n=== TOP 25 pire moitié (robustesse) ==="); [print(ligne(x)) for x in sorted(R, key=lambda x: -min(x["a"], x["b"]))[:25]]
ok = [x for x in R if x["a"] > 0 and x["b"] > 0 and x["jn"] <= 1]
print(f"\n=== lignes positives dans les 2 moitiés et au plus 1 jour négatif : {len(ok)} / {len(R)} — classées par gain/creux ===")
[print(ligne(x)) for x in sorted(ok, key=lambda x: -x["g"]/max(1, x["cr"]))[:30]]
print("\nperdantes sur 95 h :", sum(x["g"] < 0 for x in R), "/", len(R))
