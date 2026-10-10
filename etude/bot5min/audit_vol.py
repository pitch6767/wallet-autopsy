"""Audit 10.10 : la volatilité du perp Bybit (souvent figé la nuit) sous-estime le bruit propre de Chainlink -> probabilités trop extrêmes ?
Comparaison, sur les mêmes mesures, du moteur actuel (volatilité perp) et d'une variante diagnostique (volatilité = max(perp, Chainlink)).
Diagnostic seulement : aucune stratégie modifiée."""
import sys
sys.path.insert(0, "etude/bot5min")
exec(open("etude/bot5min/twap_etudes.py").read().split("# ---------- A.")[0])
VCL = {}
def volcl(s):
    if s not in VCL:
        x = [sec("cl", j) for j in range(s - 300, s)]; x = [y for y in x if y]
        VCL[s] = float(np.std(np.diff(x))) if len(x) > 100 else None
    return VCL[s]
NUIT0 = 1791581760  # 10.10 00:16 heure suisse
per = lambda st: "nuit 10.10 (00:15-07:30)" if st >= NUIT0 else "07.10-09.10"
M = collections.defaultdict(list); SIGS = collections.defaultdict(list)
for st in cyc:
    c = CY[st]; fait = {"perp": False, "max": False}
    for x in c["L"]:
        if not (20 <= x["tl"] <= 90): continue
        s = int(x["t"]); vp, vc = vol(s), volcl(s)
        if not vp or not vc: continue
        # recalcul de l'écart-type avec la volatilité max(perp, Chainlink)
        sd_p = x["sd"]; v_p = sd_p ** 2 - 0.25; k = (max(vp, vc) / vp) ** 2
        sd_m = math.sqrt(max(v_p, 0) * k + 0.25); pm = phi((x["E"] - x["K"]) / sd_m)
        M[per(st)].append((x["p0"], pm, x["mid"], c["up"], vp, vc))
        for nom, p in (("perp", x["p0"]), ("max", pm)):
            if fait[nom]: continue
            for up in (True, False):
                a = ask(x, up)
                if a is None or not (0.02 <= a <= 0.98) or sz(x, up) <= 0: continue
                if (p if up else 1 - p) - a >= 0.20:
                    gm = c["up"] if up else not c["up"]; b = pnl(x, up, gm)
                    if b: SIGS[(per(st), nom)].append((b[0], b[1], gm)); fait[nom] = True
                    break
out = ["# Audit volatilité : perp Bybit contre bruit Chainlink", "",
       "| Période | Mesures | Vol. perp médiane ($/s) | Vol. Chainlink médiane ($/s) | Brier moteur actuel | Brier moteur vol. max | Brier carnet | Proba moyenne des côtés à > 90 % / gagnés réellement |", "|---|---|---|---|---|---|---|---|"]
for k, L in M.items():
    A = np.array([(a, b, m if m is not None else np.nan, y, vp, vc) for a, b, m, y, vp, vc in L], float)
    y = A[:, 3]; mm = ~np.isnan(A[:, 2])
    ext = np.maximum(A[:, 0], 1 - A[:, 0]) > 0.9; won = np.where(A[:, 0] > 0.5, y, 1 - y)
    out.append(f"| {k} | {len(A)} | {np.median(A[:, 4]):.2f} | {np.median(A[:, 5]):.2f} | {np.mean((A[:, 0] - y) ** 2):.4f} | {np.mean((A[:, 1] - y) ** 2):.4f} | {np.mean((A[mm, 2] - y[mm]) ** 2):.4f} | {np.mean(np.maximum(A[ext, 0], 1 - A[ext, 0])):.3f} / {np.mean(won[ext]):.3f} |")
out += ["", "Rejeu TWAP fin (premier signal du cycle, avantage ≥ 0,20, 90-20 s, quantité affichée, frais compris) :", "", HH]
for (k, nom), L in sorted(SIGS.items()):
    out.append(f"| {k} — moteur {'actuel (vol. perp)' if nom == 'perp' else 'vol. max(perp, Chainlink)'} | {stats(L)} |")
open("etude/bot5min/resultat_audit_vol.md", "w").write("\n".join(out)); print("\n".join(out))
