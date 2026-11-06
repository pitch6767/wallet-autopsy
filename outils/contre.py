# 06.11.2026 — Étude H-CONTRE (estimation, PAS de vrais remplissages) : les achats de fin de cycle (minutes 3-5) perdent beaucoup sur les jours inédits.
# Question : prendre l'AUTRE côté de ces signaux gagnerait-il ? Prix estimé de l'autre côté = 1 − prix du signal + 0,02 (écart), frais compris,
# même mise que le vrai trade. Si c'est prometteur, le banc devra le mesurer en vrai (carnet de l'autre jeton). Aussi : gain par moment × prix.
import json, sys, urllib.request, collections, datetime as dt
VPS = sys.argv[1]; DEP = "2026-11-04T14:38:10Z"; COUPE = "2026-11-06"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"cache-control": "no-store", "user-agent": "etude"}), timeout=120) as r: return json.load(r)
T = get(f"{VPS}/api/bot/banc/trades?depuis={DEP}&plafond=200")["trades"]; print("trades", len(T))
BASES = {1, 2, 5, 6, 7, 10, 11, 14, 15, 16, 20, 28, 31, 32, 35, 101, 105, 107, 109, 112, 116, 119, 120, 121, 127, 129, 201, 207, 213, 214, 301, 1011, 1114}
G = collections.defaultdict(lambda: [0.0, 0, 0.0, 0]); C = collections.defaultdict(lambda: [0.0, 0, 0.0, 0])
for t in T:
    s = t["endTs"] / 1000 - 300; mn = (dt.datetime.fromisoformat(t["ouvert"].replace("Z", "+00:00")).timestamp() - s) / 60
    jour = (dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)).strftime("%Y-%m-%d"); te = jour >= COUPE
    p = t["prixSignal"]; pb = "<0,15" if p < 0.15 else "0,15-0,30" if p < 0.30 else "0,30-0,50" if p < 0.50 else ">=0,50"
    mb = "min 0-1" if mn < 1 else "min 1-3" if mn < 3 else "min 3-5"
    if t["num"] in BASES:   # stratégies reçues seulement (pas les versions dérivées, pour ne pas compter 400 fois le même signal)
        z = G[(mb, pb)]; z[2 if te else 0] += t["pnl"]; z[3 if te else 1] += 1
        if mb == "min 3-5":
            q = min(0.99, 1 - p + 0.02); cout = t["mise"]; parts = cout / (q + 0.07 * q * (1 - q)); g = (parts if not t["gagne"] else 0) - cout
            c = C[pb]; c[2 if te else 0] += g; c[3 if te else 1] += 1
print("\n=== STRATÉGIES REÇUES : gain par moment du cycle × prix du signal (apprentissage | jours inédits) — VRAIS trades ===")
for k in sorted(G): z = G[k]; print(f"{k[0]:8s} {k[1]:10s} | appr. {z[0]:+9.0f} $ ({z[1]}) | inédit {z[2]:+9.0f} $ ({z[3]})")
print("\n=== AUTRE CÔTÉ DES SIGNAUX DE FIN DE CYCLE (minutes 3-5) — ESTIMATION ===")
for k in sorted(C): z = C[k]; print(f"signal à {k:10s} → autre côté | appr. {z[0]:+9.0f} $ ({z[1]}) | inédit {z[2]:+9.0f} $ ({z[3]})")
print("\nFIN")
