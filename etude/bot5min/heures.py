"""Les desaccords dependent-ils de l'heure ? (07.10.2026) — 12 jours d'historique, BTC et ETH.
Memes episodes que combinaisons.py (premier instant ou |modele - marche| >= 0,10, achat realiste, garde jusqu'a la fin).
Resultat par heure suisse, par tranche (nuit / matin / apres-midi US / soir), par ecart, jour par jour : la tranche gagne-t-elle REGULIEREMENT ?
"""
import sys, time, statistics, collections
from datetime import datetime, timezone
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else "12"]
sys.path.insert(0, "etude/bot5min")
import combinaisons as CB

OUT = "etude/bot5min/"
H = lambda st: (datetime.fromtimestamp(st, timezone.utc).hour + 2) % 24          # heure suisse (ete)
J = lambda st: datetime.fromtimestamp(st + 7200, timezone.utc).strftime("%d.%m")
def tranche(h):
    if h < 8: return "1 nuit 00-08h (Asie)"
    if h < 15: return "2 matin 08-15h (Europe)"
    if h < 22: return "3 apres-midi 15-22h (US)"
    return "4 soir 22-24h"


def main():
    J_ = CB.JOURS
    fin = int(time.time()) // 86400 * 86400 - 300
    debut = fin + 300 - J_ * 86400
    jours = sorted({datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in range(debut - 3700, fin + 600, 3600)})
    jours = [j for j in jours if j < datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    coupe = debut + int(J_ * 2 / 3) * 86400
    D = {"btc": CB.preparer("btc", "BTCUSDT", jours, debut, fin, coupe), "eth": CB.preparer("eth", "ETHUSDT", jours, debut, fin, coupe)}
    rap = [f"# Desaccords selon l'heure — {J_} jours ({jours[1]} -> {jours[-1]}), heure suisse", "",
           "Gain par part (1 part achetee au prix d'un vrai acheteur, frais compris, garde jusqu'a la fin). Pour 50 $ par trade, multiplier par ~50 / prix.", ""]
    for A, B in (("btc", "eth"), ("eth", "btc")):
        E = CB.episodes(D, A, B, coupe)
        for e in E: e["h"] = H(e["st"]); e["tr"] = tranche(e["h"]); e["j"] = J(e["st"])
        for lab, filt in (("ecart >= 0,10 (tous)", lambda e: True), ("ecart >= 0,15", lambda e: e["ecart"] != "0.10-0.15"), ("ecart >= 0,20", lambda e: e["ecart"] == "ecart>=0.20")):
            X = [e for e in E if filt(e)]
            if not X: continue
            rap += [f"## {A.upper()} — {lab} — {len(X)} desaccords", "",
                    "| Tranche | Desaccords | Gagne | Gain/part j1-8 | **Gain/part j9-12** | Jours positifs / jours |", "|---|---|---|---|---|---|"]
            for tr in sorted({e["tr"] for e in X}):
                Y = [e for e in X if e["tr"] == tr]; a_ = [e for e in Y if not e["test"]]; b_ = [e for e in Y if e["test"]]
                pj = collections.defaultdict(float)
                for e in Y: pj[e["j"]] += e["pnl"]
                rap.append(f"| {tr} | {len(Y)} | {100 * statistics.mean(e['g'] for e in Y):.0f} % | {statistics.mean(e['pnl'] for e in a_) if a_ else float('nan'):+.3f} | **{statistics.mean(e['pnl'] for e in b_) if b_ else float('nan'):+.3f}** | {sum(1 for v in pj.values() if v > 0)} / {len(pj)} |")
            rap += ["", "Par heure : " + " · ".join(f"{h}h {statistics.mean(e['pnl'] for e in X if e['h'] == h):+.2f} ({sum(1 for e in X if e['h'] == h)})" for h in range(24) if any(e["h"] == h for e in X)), ""]
        open(OUT + "resultat_heures.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
