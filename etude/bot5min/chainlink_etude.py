"""BOT95 — CHAINLINK : moyenne officielle 60 s contre notre reconstruction, et prévision de la prochaine valeur Chainlink à partir des bourses.
Demande de Pitch, 11.10.2026. Hors ligne, aucun bot modifié. Période réservée (≥ 13.10.2026 00:00 UTC) non lue.
Usage : python3 etude/bot5min/chainlink_etude.py dossier_des_cycles → etude/bot5min/resultat_chainlink.md"""
import gzip, json, os, sys, glob, bisect, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); SORTIE = os.path.join(ICI, "resultat_chainlink.md"); HORS_ECH = 1791849600


def main():
    fichiers = sorted(f for f in glob.glob(os.path.join(sys.argv[1], "**", "*.json.gz"), recursive=True) if int(os.path.basename(f).split(".")[0]) < HORS_ECH)
    CL = {}; TW = {}; EX = []; STRIKE = {}; n = 0
    for fn in fichiers:
        R = json.load(gzip.open(fn))
        if not R.get("cl2") and not R.get("tw"): continue
        n += 1
        for tR, flux, obs, v in R.get("cl2", []):
            e = CL.setdefault(obs, {"v": v, "t": {}}); e["t"][flux] = tR
        for tR, obs, v in R.get("tw", []): TW.setdefault(obs, (v, tR))
        for r in R.get("ex", []): EX.append(r)
        m = R.get("marche") or {}; STRIKE[R["start"]] = m.get("strike")
    EX.sort(key=lambda r: r[0]); Et = [r[0] for r in EX]
    obs = sorted(CL); vals = np.array([CL[o]["v"] for o in obs]); O = np.array(obs)
    o = []; w = o.append
    w("# Bot95 — Chainlink : moyenne officielle et prévision (PRÉLIMINAIRE)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {n} cycles avec le nouveau flux, {len(obs)} valeurs Chainlink BTC (une par seconde), {len(TW)} moyennes officielles 60 s.\n")
    # --- 1. moyenne officielle contre reconstruction
    w("## 1. Moyenne officielle 60 s contre notre reconstruction\n")
    res = {}
    for nom, (d0, d1) in {"[T−60 ; T−1]": (-60, -1), "[T−59 ; T]": (-59, 0), "[T−60 ; T]": (-60, 0)}.items():
        e = []
        for t, (v, _) in TW.items():
            lo, hi = t + d0 * 1000, t + d1 * 1000
            i, j = np.searchsorted(O, lo, "left"), np.searchsorted(O, hi, "right")
            if j - i >= (hi - lo) / 1000 + 1 - 1e-9: e.append(vals[i:j].mean() - v)
        res[nom] = e
    w("| Fenêtre reconstruite (valeurs Chainlink 1 s) | Moyennes comparées | Écart médian absolu | Écart max absolu |\n|---|---|---|---|")
    for k, e in res.items():
        a = np.abs(e) if e else []
        w(f"| {k} | {len(e)} | {np.median(a):.4f} $ | {np.max(a):.4f} $ |" if len(a) else f"| {k} | 0 | — | — |")
    # prix à battre du bot vs officiel
    d = []
    for st, s in STRIKE.items():
        tw = TW.get(st * 1000)
        if s and tw: d.append(s - tw[0])
    if d: w(f"\nPrix à battre calculé par le bot de Dublin (moyenne des valeurs reçues pendant les 60 s avant le début, par seconde de RÉCEPTION) contre la moyenne officielle à l'instant du début : "
            f"{len(d)} cycles, écart médian absolu {np.median(np.abs(d)):.2f} $, max {np.max(np.abs(d)):.2f} $.\n")
    tr = [ (t2 - t) for t, (v, t2) in TW.items() ]
    if tr: w(f"La moyenne officielle arrive à Dublin {np.median(tr):.0f} ms (médiane) après son instant de calcul.\n")
    # --- 2. prévision de la prochaine valeur Chainlink
    w("## 2. Prévoir la valeur Chainlink avant sa publication (~1,2 s de retard)\n")
    w("À l'instant d'observation s d'une valeur Chainlink, on ne la connaîtra qu'environ 1,2 s plus tard. Prévision avec ce que Dublin sait à s + δ : "
      "médiane des bourses (Bybit perp, OKX perp, Binance, Coinbase) + écart moyen bourses−Chainlink des 60 dernières valeurs DÉJÀ publiées à ce moment.\n")
    w("| Information utilisée | Valeurs prévues | Erreur médiane absolue | p90 | Témoin : dernière valeur publiée | Témoin p90 |\n|---|---|---|---|---|---|")
    pub = {ob: min(CL[ob]["t"].values()) for ob in obs}
    pubO = sorted(pub, key=lambda x: pub[x]); pubT = [pub[x] for x in pubO]
    def bourse(t):
        i = bisect.bisect_right(Et, t) - 1
        if i < 0: return None
        r = EX[i]; px = [r[k][0] for k in (1, 2, 3, 4) if r[k]]
        return float(np.median(px)) if px else None
    for delta in (0, 100, 250, 500):
        err, naif, var = [], [], {}
        for ob in obs[60:]:
            t_info = ob + delta
            X = bourse(t_info)
            if X is None: continue
            j = bisect.bisect_right(pubT, t_info)               # valeurs publiées avant t_info
            if j < 30: continue
            prev = pubO[max(0, j - 60):j]
            base = [CL[p]["v"] - (bourse(p) or np.nan) for p in prev]
            base = [b for b in base if not np.isnan(b)]
            if len(base) < 20: continue
            err.append(abs(X + np.median(base) - CL[ob]["v"])); last = pubO[j - 1]; naif.append(abs(CL[last]["v"] - CL[ob]["v"]))
            Xl = bourse(last)
            if Xl is not None:
                for beta in (0.25, 0.5, 1.0): var.setdefault(beta, []).append(abs(CL[last]["v"] + beta * (X - Xl) - CL[ob]["v"]))
        if err: w(f"| bourses à s + {delta} ms | {len(err)} | {np.median(err):.2f} $ | {np.percentile(err, 90):.2f} $ | {np.median(naif):.2f} $ | {np.percentile(naif, 90):.2f} $ |")
        for beta, e in sorted(var.items()): w(f"| dernière valeur publiée + {beta} × variation des bourses depuis son instant (s + {delta} ms) | {len(e)} | {np.median(e):.2f} $ | {np.percentile(e, 90):.2f} $ | {np.median(naif):.2f} $ | {np.percentile(naif, 90):.2f} $ |")
    w("\nLecture : si l'erreur de prévision est nettement plus petite que celle du témoin, nous connaissons la prochaine valeur Chainlink environ 1 s avant sa publication (base de M3).\n")
    w("## Limites\n- Une seule journée partielle ; chiffres indicatifs.\n- L'heure d'observation Chainlink est à la seconde.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
