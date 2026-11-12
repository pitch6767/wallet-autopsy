# 12.11.2026 11 h 29 (Pitch : « stratégie 2140, analyse-moi les trades ») — même analyse que pour la 600005.
# 12.11.2026 (Pitch : « analyse profonde des trades de la stratégie du bot… les −200 sont-ils utiles ? 100 au lieu de 200 pénalise-t-il ? »)
# Lecture seule. Ligne 600005 du banc (= trades de l'onglet Trades depuis l'activation), 95 h, plafond 200 $ par cycle.
import json, urllib.request, collections, datetime as dt, statistics as st
from zoneinfo import ZoneInfo
PZ = ZoneInfo("Europe/Paris")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "analyse"}), timeout=180) as r: return json.load(r)
dep = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=95)).strftime("%Y-%m-%dT%H:%M:%SZ")
TT = get(f"https://72-11-157-70.sslip.io/api/bot/banc/trades?depuis={dep}&plafond=100")["trades"]
NUM = 2140
T = sorted([t for t in TT if t["num"] == NUM], key=lambda t: t["ouvert"])
ids1114 = {t["id"] for t in TT if t["num"] == 1114}; ids116 = {t["id"] for t in TT if t["num"] == 116}
print("ligne", NUM, "= PORTEFEUILLE 1114 + 116 ; plafond 100 $ par cycle")
for nom, ids in [("venant de la 1114", ids1114), ("venant de la 116", ids116)]:
    X = [t for t in T if t["id"] in ids]; print(f"  {nom} : {len(X)} trades, gain {sum(t['pnl'] for t in X):+.0f} $, gagnés {100*sum(t['gagne'] for t in X)/max(1,len(X)):.0f} %")
for n in (1114, 116, 600005):
    X = [t for t in TT if t["num"] == n]; print(f"  pour comparer {n} : {len(X)} trades, gain {sum(t['pnl'] for t in X):+.0f} $")
J = lambda t: dt.datetime.fromtimestamp(t["endTs"] / 1000, PZ).strftime("%d.%m")
print("période :", T[0]["ouvert"], "→", T[-1]["ouvert"], "|", len(T), "trades | gain", round(sum(t["pnl"] for t in T)), "$ | misé", round(sum(t["mise"] for t in T)), "$")
def stats(L, nom):
    if not L: print(f"{nom:28s} —"); return
    g = sum(t["pnl"] for t in L); m = sum(t["mise"] for t in L); w = sum(t["gagne"] for t in L)
    c = p = cr = 0
    for t in L: c += t["pnl"]; p = max(p, c); cr = max(cr, p - c)
    print(f"{nom:28s} {len(L):4d} tr | gagnés {100*w/len(L):3.0f} % | prix moy {st.mean(t['prix'] for t in L):.3f} | gain {g:+8.0f} $ | pour 1 $ {g/m:+.2f} | creux -{cr:.0f}")
print("\n=== par tranche de mise ===")
for nom, f in [("mise ≤ 60 $", lambda t: t["mise"] <= 60), ("mise 60–90 $", lambda t: 60 < t["mise"] <= 90), ("mise > 90 $ (≈100)", lambda t: t["mise"] > 90)]: stats([t for t in T if f(t)], nom)
print("\n=== par prix d'entrée ===")
for a, b in [(0, .06), (.06, .10), (.10, .15), (.15, .25), (.25, .40), (.40, .60), (.60, 1)]:
    stats([t for t in T if a <= t["prix"] < b], f"prix {a:.2f}–{b:.2f}")
print("\n=== les 15 plus gros gains ===")
for t in sorted(T, key=lambda t: -t["pnl"])[:15]: print(" ", t["ouvert"][:16], t["side"], "prix", round(t["prix"], 3), "mise", round(t["mise"]), "gain", round(t["pnl"]))
G = sorted([t["pnl"] for t in T if t["pnl"] > 0], reverse=True); tot = sum(t["pnl"] for t in T)
print("part du gain total faite par les 5 / 10 plus gros gains :", round(100*sum(G[:5])/tot), "% /", round(100*sum(G[:10])/tot), "%  (gain total", round(tot), ")")
print("\n=== et si on plafonnait CHAQUE trade (mise et parts réduites dans la même proportion) ===")
for cap in (100, 75, 50):
    L = []
    for t in T:
        k = min(1, cap / t["mise"]); L.append(dict(t, mise=t["mise"] * k, pnl=t["pnl"] * k))
    stats(L, f"au plus {cap} $ par trade")
print("\n=== et si on ne doublait jamais (règle x2 « carnet d'accord » et x2 du signal enlevés : mise ramenée à 50 $) ===")
stats([dict(t, mise=t["mise"] * min(1, 50 / t["mise"]), pnl=t["pnl"] * min(1, 50 / t["mise"])) for t in T], "toujours 50 $")
print("\n=== mises de 100 $ seulement si prix < X, sinon 50 $ max ===")
for X in (0.08, 0.10, 0.15, 0.20):
    L = [dict(t, mise=t["mise"] * (1 if t["prix"] < X else min(1, 50 / t["mise"])), pnl=t["pnl"] * (1 if t["prix"] < X else min(1, 50 / t["mise"]))) for t in T]
    stats(L, f"100 $ si prix < {X}")
print("\n=== par jour ===")
for d in sorted({J(t) for t in T}): stats([t for t in T if J(t) == d], d)
print("\n=== tickets à ≈100 $ : jour par jour (gagnés / joués, gain) ===")
for d in sorted({J(t) for t in T}):
    X = [t for t in T if J(t) == d and t["mise"] > 90]
    print(d, f"{sum(t['gagne'] for t in X)} / {len(X)}", round(sum(t["pnl"] for t in X)), "$")
