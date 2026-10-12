"""BOT95 — H1052 : les règles de sortie de H1051 appliquées aux stratégies GAGNANTES du jour du bot Cloudflare (Pitch, 12.10.2026 18:47 :
« Et sur les gagnantes d'aujourd'hui dans le bot ? »). Étude descriptive séparée, préenregistrée avant calcul. Hors ligne ; aucun ordre ; aucun
fantôme ni stratégie modifié.

SÉLECTION (avant tout calcul de sortie) : les 10 stratégies BTC du bot Cloudflare au meilleur résultat du 12.10 (00:00 UTC → export de 18:50),
  d'après bot95/sauvegarde (V2-F + pas les deux baissent, V2-D perp 120-269 s, V2-F + plus de 120 s, V2-C perp, V2-G jury des bourses, V2-F écart qui
  grandit, V2-B hors 60-89 s, V2-H veto complet, désaccord 20 Binance ou perp avec nous, désaccord 20 sans nuit). Attention : elles sont choisies
  parce qu'elles ont gagné aujourd'hui ; leur résultat « conserver » est donc biaisé vers le haut. Seul l'ÉCART entre une règle de sortie et la
  conservation est étudié.
ENTRÉES : chaque trade BTC du jour de ces stratégies, rejoué avec une mise normalisée de 10 $ sur le carnet Dublin, à la seconde qui suit l'heure
  du trade, côté identique, prix limite = prix du trade arrondi au centime supérieur ; exécution preneur à 164 ms (et 500 ms).
PÉRIODES : « matin » = cycles avant 12.10 12:00 UTC (calculé maintenant) ; « après-midi » = 12.10 12:00 → 24:00 UTC (calculé une seule fois
  avec le test de cette nuit, option --apres-midi). Les deux sont rapportés séparément.
RÈGLES : exactement celles de H1051 (H0, TP2, TP3, TP5, FR, TR30, TR50, TB, F1, F2, SV5, SV10), cerveau B appris sur l'apprentissage de H1003.
MESURES : par stratégie et au total : P&L (mise 10 $), écart avec H0, IC 90 % par cycles (et corrigé pour 11 comparaisons), jackpots conservés.
Usage : python3 etude/bot5min/gagnantes_jour_h1052.py dossier_cycles_dublin [--apres-midi]"""
import os, sys, math, time, json, glob, collections, datetime
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
APM = "--apres-midi" in sys.argv
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV, trailing_bas_h1051 as TB
SORTIE = os.path.join(ICI, "resultat_gagnantes_jour_h1052" + ("_apres_midi" if APM else "_matin") + ".md")
J0, MIDI, FIN = 1791763200, 1791806400, 1791849600
NOMS = ["V2-F + pas les deux baissent BTC", "V2-D perp 120-269 s BTC", "V2-F + plus de 120 s BTC", "V2-C perp BTC", "V2-G jury des bourses BTC",
        "V2-F ecart qui grandit BTC", "V2-B hors 60-89 s BTC", "V2-H veto complet BTC", "desaccord 20 Binance ou perp avec nous BTC", "desaccord 20 sans nuit BTC"]
LATS = (164, 500); RNG = np.random.default_rng(1052); NCOMP = 11; meilleur = DP.meilleur


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y); dev = [s for s in cycles if s < RV.DEV_FIN]; TR = dev[:len(dev) * 2 // 3]
    lo, hi = (MIDI, FIN) if APM else (J0, MIDI)
    # entrées
    ENT = collections.defaultdict(list)
    for f in glob.glob(os.path.join(ICI, "..", "..", "bot95", "sauvegarde", "*_BTC.json")):
        d = json.load(open(f))
        if d.get("nom") not in NOMS: continue
        for t in (d.get("trades") or {}).values():
            if not isinstance(t, dict) or not t.get("cote") or not t.get("prix") or not t.get("heure"): continue
            st = t.get("start", 0)
            if not (lo <= st < hi) or st not in Y: continue
            ts = datetime.datetime.fromisoformat(t["heure"].replace("Z", "+00:00")).timestamp()
            k = int(math.ceil(ts - st)) - 10
            if 0 <= k <= 280: ENT[st].append((d["nom"], k, t["cote"], int(math.ceil(t["prix"] * 100 - 1e-9)) * 10, t.get("net")))
    w(f"# Bot95 — H1052 : règles de sortie sur les gagnantes du jour ({'après-midi 12:00–24:00 UTC' if APM else 'matin 00:00–12:00 UTC'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {sum(len(v) for v in ENT.values())} trades sur {len(ENT)} cycles. Mise normalisée 10 $. "
      "Stratégies choisies parce qu'elles ont gagné aujourd'hui : seul l'écart avec « conserver » compte. Aucun ordre.\n")
    def tstates(st, T):
        try: return {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T).items()}
        except Exception: return {}
    def midU(Lo):
        a, b = meilleur(Lo, "Up", "a"), meilleur(Lo, "Up", "b")
        return (a + b) / 2000 if a and b and 0 < (a + b) / 2000 < 1 else None
    Xb, yb = [], []
    for st in TR:
        T = [st * 1000 + s * 1000 for s in range(10, 291, 10)]; E = tstates(st, T)
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st)); mu = midU(E.get(t))
            if m and mu: Xb.append([L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]); yb.append(Y[st])
    bB = L.ajuster(np.array(Xb), np.array(yb), 0.1)
    RV.STRESS = {}; RV.FEE_K = 1.0; RES = collections.defaultdict(list)                 # (nom, lat, règle) -> [(st, pnl, inv)]
    for st in sorted(ENT):
        T = [st * 1000 + s * 1000 for s in range(10, 291)]
        E = tstates(st, T + [t + l for t in T for l in LATS]); p, z = [], []
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st)); mu = midU(E.get(t))
            p.append(float(L.predire(bB, np.array([[L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]]))[0]) if (m and mu) else None)
            z.append(m[1] if m else None)
        C = dict(st=st, E=E, T=T, p=p, z=z, y=Y[st])
        for nom, k, X, lim, net in ENT[st]:
            for lat in LATS:
                RV.EXEC = lat
                for rg in TB.REGLES:
                    out = TB.jouer(rg, C, k, X, lim)
                    if out: RES[(nom, lat, rg)].append((st, out[1], out[0]))
        RV.EXEC = 164
    def ligne(nom_, lab):
        H = {st: v for st, v, _ in RES.get((nom_, 164, "H0"), [])} if nom_ != "*" else None
        return H
    for nom in NOMS + ["TOUTES (somme des 10)"]:
        allx = nom.startswith("TOUTES")
        keyn = NOMS if allx else [nom]
        H = [(n_, st, v) for n_ in keyn for st, v, _ in RES.get((n_, 164, "H0"), [])]
        if not H: w(f"## {nom}\n\n_Aucun trade exécutable._\n"); continue
        Hd = {(n_, st): v for n_, st, v in H}
        jk = [x for x, v in Hd.items() if v >= 40]
        w(f"## {nom}\n\n{len(H)} trades exécutés à 164 ms ; conserver : {sum(Hd.values()):+.0f} $ ({sum(v > 0 for v in Hd.values())} gagnants, jackpots ≥ 40 $ : {len(jk)}).\n")
        w(f"| Règle | P&L ($) | Gagnants | Jackpots conservés | P&L − H0 ($) | IC 90 % | IC corrigé ({NCOMP}) | 500 ms : P&L − H0 |\n|---|---|---|---|---|---|---|---|")
        for rg in TB.REGLES:
            R_ = {(n_, st): v for n_ in keyn for st, v, _ in RES.get((n_, 164, rg), [])}
            ks = list(Hd); v = np.array([R_.get(x, Hd[x]) for x in ks]); d = v - np.array([Hd[x] for x in ks])
            g = collections.defaultdict(float)
            for x, dd in zip(ks, d): g[x[1]] += dd
            dg = np.array(list(g.values()))
            c1 = TB.ic_cy(dg) if rg != "H0" else (np.nan, np.nan); c2 = TB.ic_cy(dg, 0.10 / NCOMP) if rg != "H0" else (np.nan, np.nan)
            R5 = {(n_, st): v_ for n_ in keyn for st, v_, _ in RES.get((n_, 500, rg), [])}; H5 = {(n_, st): v_ for n_ in keyn for st, v_, _ in RES.get((n_, 500, "H0"), [])}
            d5 = sum(R5[x] - H5[x] for x in R5 if x in H5)
            w(f"| {rg} | {v.sum():+.0f} | {int((v > 0).sum())} | {sum(1 for x in jk if R_.get(x, Hd[x]) >= 0.5 * Hd[x])} / {len(jk)} | {d.sum():+.0f} | "
              f"[{c1[0]:+.0f} ; {c1[1]:+.0f}] | [{c2[0]:+.0f} ; {c2[1]:+.0f}] | {d5:+.0f} |")
        w("")
    w("Règles : H0 conserver ; TP2/TP3/TP5 prise de gain à 2/3/5 × le prix ; FR free-roll ; TR30/TR50 trailing du profit liquidable (dès 5 $) ; TB trailing "
      "du billet ; F1 trailing fondamental ; F2 marge Chainlink ; SV5/SV10 verrou de 0 $ dès 5/10 $.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
