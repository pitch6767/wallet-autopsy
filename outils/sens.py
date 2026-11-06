# 06.11.2026 — Étude H-SENS (méthode etude-fantome) sur les VRAIS trades du banc (limite +5 c, 200 $ par cycle).
# Question : qu'est-ce qui sépare les trades gagnants des perdants ? Sens du trade par rapport à la tendance du BTC sur 1 h (connue avant le cycle),
# prix payé, moment dans le cycle. Règle choisie sur l'apprentissage (04.11 15:38 → 05.11), jugée sur les jours inédits (06.11 → maintenant).
import json, sys, urllib.request, collections, datetime as dt
VPS = sys.argv[1]; DEP = "2026-11-04T14:38:10Z"; COUPE = "2026-11-06"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"cache-control": "no-store", "user-agent": "etude"}), timeout=120) as r: return json.load(r)
T = get(f"{VPS}/api/bot/banc/trades?depuis={DEP}&plafond=200")["trades"]; print("trades", len(T))
t0 = int(dt.datetime.fromisoformat(DEP.replace("Z", "+00:00")).timestamp() * 1000) - 2 * 3600_000; t1 = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000); K = {}
while t0 < t1:
    ks = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime={t0}&limit=1000")
    if not ks: break
    for k in ks: K[k[0] // 1000] = (float(k[1]), float(k[4]))
    t0 = ks[-1][0] + 300_000
noms = {}
try:
    for c in get("https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/src/catalogue.json"): noms[c["n"]] = c["nom"]
except Exception: pass
def feat(t):
    s = t["endTs"] // 1000 - 300; a, b = K.get(s - 3600), K.get(s - 300)
    if not a or not b: return None
    mv = (b[1] / a[0] - 1) * 1e4
    sens = "dans la tendance" if (mv > 0) == (t["side"] == "UP") else "contre la tendance"
    if abs(mv) < 13.8: sens = "BTC calme"
    p = t["prixSignal"]; pb = "<0,15" if p < 0.15 else "0,15-0,30" if p < 0.30 else "0,30-0,50" if p < 0.50 else ">=0,50"
    mn = (dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() - s) / 60
    mb = "min 0-1" if mn < 1 else "min 1-3" if mn < 3 else "min 3-5"
    jour = (dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)).strftime("%Y-%m-%d")
    return {"sens": sens, "prix": pb, "moment": mb, "test": jour >= COUPE}
S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0, 0.0, 0]))   # num -> clé -> [gain app, n app, gain test, n test]
for t in T:
    f = feat(t)
    if not f: continue
    for k in ("tout", "sens:" + f["sens"], "prix:" + f["prix"], "moment:" + f["moment"]):
        z = S[t["num"]][k]
        if f["test"]: z[2] += t["pnl"]; z[3] += 1
        else: z[0] += t["pnl"]; z[1] += 1
# 1) toutes stratégies confondues : quel sens gagne ?
G = collections.defaultdict(lambda: [0.0, 0, 0.0, 0])
for n, d in S.items():
    for k, z in d.items():
        if k.startswith("sens:") or k.startswith("prix:") or k.startswith("moment:"):
            for i in range(4): G[k][i] += z[i]
print("\n=== TOUTES LES STRATÉGIES ENSEMBLE (somme, apprentissage | jours inédits) ===")
for k in sorted(G): print(f"{k:28s} | appr. {G[k][0]:+10.0f} $ ({G[k][1]}) | inédit {G[k][2]:+9.0f} $ ({G[k][3]})")
# 2) règle « seulement dans la tendance » : par stratégie, comparaison inédite
print("\n=== RÈGLE « SEULEMENT DANS LA TENDANCE » — 25 meilleures stratégies (au moins 15 trades d'apprentissage) ===")
print("n° | stratégie | tout (appr. / inédit) | dans la tendance (appr. / inédit) | contre (appr. / inédit) | calme (appr. / inédit)")
L = [(n, d) for n, d in S.items() if d["tout"][1] >= 15]
for n, d in sorted(L, key=lambda x: -x[1]["tout"][0])[:25]:
    g = lambda k: f"{d[k][0]:+.0f} ({d[k][1]}) / {d[k][2]:+.0f} ({d[k][3]})"
    print(f"{n} | {noms.get(n, '')[:55]} | {g('tout')} | {g('sens:dans la tendance')} | {g('sens:contre la tendance')} | {g('sens:BTC calme')}")
# 3) meilleure règle par stratégie choisie sur l'apprentissage, jugée sur l'inédit
print("\n=== MEILLEUR FILTRE PAR STRATÉGIE (choisi sur l'apprentissage) — résultat sur les jours inédits ===")
tot_t = tot_f = 0; nb = 0
for n, d in sorted(L, key=lambda x: -x[1]["tout"][0])[:40]:
    cand = [k for k in d if k != "tout" and d[k][1] >= 8]
    if not cand: continue
    b = max(cand, key=lambda k: d[k][0])
    tot_t += d["tout"][2]; tot_f += d[b][2]; nb += 1
    print(f"{n} | {noms.get(n, '')[:50]} | filtre « {b} » | inédit sans filtre {d['tout'][2]:+.0f} ({d['tout'][3]}) | avec filtre {d[b][2]:+.0f} ({d[b][3]})")
print(f"TOTAL sur {nb} stratégies, jours inédits : sans filtre {tot_t:+.0f} $ | avec le filtre choisi {tot_f:+.0f} $")
print("\nFIN")
